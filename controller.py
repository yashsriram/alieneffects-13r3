import logging

from usbdriver import AlienwareUSBDriver
from cmdpacket import AlienwareCmdPacket
from themefile import AlienwareThemeFile
from functools import reduce


class AlienwareController:
    """
    Provides facilities to communicate with an AlienFX controller.
    This class provides methods to send commands to an AlienFX controller, and receive status from the controller.
    """

    # Speed capabilities. The higher the number, the slower the speed of
    # blink/morph actions. The min speed is selected by trial and error as
    # the lowest value that will not result in strange blink/morph behaviour.
    DEFAULT_SPEED = 200
    MIN_SPEED = 50

    # Zone codes
    LEFT_KEYBOARD = 0x0008
    MIDDLE_LEFT_KEYBOARD = 0x0004
    MIDDLE_RIGHT_KEYBOARD = 0x0002
    RIGHT_KEYBOARD = 0x0001
    # External 'Alien Head'
    ALIEN_HEAD = 0x0020
    # 'Alienware' below screen
    LOGO = 0x0040
    # Windows the next 3 as a single 'Zone 8'
    HDD_LED = 0x0200
    WIFI_LED = 0x0400
    CAPS_LED = 0x0080
    TOUCH_PAD = 0x0080
    POWER_BUTTON = 0x0100

    # Reset codes
    RESET_ALL_LIGHTS_OFF = 3
    RESET_ALL_LIGHTS_ON = 4

    # State codes
    BOOT = 1
    AC_SLEEP = 2
    AC_CHARGED = 5
    AC_CHARGING = 6
    BATTERY_SLEEP = 7
    BATTERY_ON = 8
    BATTERY_CRITICAL = 9

    # Zone names
    ZONE_LEFT_KEYBOARD = "Left Keyboard"
    ZONE_MIDDLE_LEFT_KEYBOARD = "Middle-left Keyboard"
    ZONE_MIDDLE_RIGHT_KEYBOARD = "Middle-right Keyboard"
    ZONE_RIGHT_KEYBOARD = "Right Keyboard"
    ZONE_RIGHT_SPEAKER = "Right Speaker"
    ZONE_LEFT_SPEAKER = "Left Speaker"
    ZONE_ALIEN_HEAD = "Alien Head"
    ZONE_LOGO = "Logo"
    ZONE_TOUCH_PAD = "Touchpad"
    ZONE_MEDIA_BAR = "Media Bar"
    ZONE_STATUS_LEDS = "Status LEDs"
    ZONE_POWER_BUTTON = "Power Button"
    ZONE_HDD_LEDS = "HDD LEDs"
    ZONE_RIGHT_DISPLAY = "Right Display"  # LED-bar display right side, as built in the AW17R4
    ZONE_LEFT_DISPLAY = "Left Display"  # LED-bar display left side, as built in the AW17R4

    # State names
    STATE_BOOT = "Boot"
    STATE_AC_SLEEP = "AC Sleep"
    STATE_AC_CHARGED = "AC Charged"
    STATE_AC_CHARGING = "AC Charging"
    STATE_BATTERY_SLEEP = "Battery Sleep"
    STATE_BATTERY_ON = "Battery On"
    STATE_BATTERY_CRITICAL = "Battery Critical"

    ALIENFX_CONTROLLER_TYPE = "old"  # Default controllertype=old. Note that modern controllers are using 8 bits per color. older ones just 4

    def __init__(self):
        self.name = "Alienware m13xR3"

        # USB VID and PID
        self.vendorId = 0x187c
        self.productId = 0x0529

        # map the zone names to their codes
        self.zone_map = {
            self.ZONE_LEFT_KEYBOARD: self.LEFT_KEYBOARD,
            self.ZONE_MIDDLE_LEFT_KEYBOARD: self.MIDDLE_LEFT_KEYBOARD,
            self.ZONE_MIDDLE_RIGHT_KEYBOARD: self.MIDDLE_RIGHT_KEYBOARD,
            self.ZONE_RIGHT_KEYBOARD: self.RIGHT_KEYBOARD,
            self.ZONE_ALIEN_HEAD: self.ALIEN_HEAD,
            self.ZONE_LOGO: self.LOGO,
            self.ZONE_TOUCH_PAD: self.TOUCH_PAD,
            self.ZONE_POWER_BUTTON: self.POWER_BUTTON,
        }

        # zones that have special behaviour in the different power states
        self.power_zones = [
            self.ZONE_POWER_BUTTON,
        ]

        # map the reset names to their codes
        self.reset_types = {
            self.RESET_ALL_LIGHTS_OFF: "all-lights-off",
            self.RESET_ALL_LIGHTS_ON: "all-lights-on"
        }

        # map the state names to their codes
        self.state_map = {
            self.STATE_BOOT: self.BOOT,
            self.STATE_AC_SLEEP: self.AC_SLEEP,
            self.STATE_AC_CHARGED: self.AC_CHARGED,
            self.STATE_AC_CHARGING: self.AC_CHARGING,
            self.STATE_BATTERY_SLEEP: self.BATTERY_SLEEP,
            self.STATE_BATTERY_ON: self.BATTERY_ON,
            self.STATE_BATTERY_CRITICAL: self.BATTERY_CRITICAL
        }

        self.cmdPacket = AlienwareCmdPacket()

        self.driver = AlienwareUSBDriver(self)

    def getZoneName(self, pkt):
        """ Given 3 bytes of a command packet, return a string zone
            name corresponding to it
        """
        zone_mask = (pkt[0] << 16) + (pkt[1] << 8) + pkt[2]
        zone_name = ""
        for zone in self.zone_map:
            bit_mask = self.zone_map[zone]
            if zone_mask & bit_mask:
                if zone_name != "":
                    zone_name += ","
                zone_name += zone
                zone_mask &= ~bit_mask
        if zone_mask != 0:
            if zone_name != "":
                zone_name += ","
            zone_name += "UNKNOWN({})".format(hex(zone_mask))
        return zone_name

    def getStateName(self, state):
        """ Given a state number, return a string state name """
        for state_name in self.state_map:
            if self.state_map[state_name] == state:
                return state_name
        return "UNKNOWN"

    def getResetTypeName(self, num):
        """ Given a reset number, return a string reset name """
        if num in list(self.reset_types.keys()):
            return self.reset_types[num]
        else:
            return "UNKNOWN"

    def ping(self):
        """ Send a get-status command to the controller."""
        pkt = self.cmdPacket.makeCmdGetStatus()
        logging.debug("SENDING: {}".format(self.pktToString(pkt)))
        self.driver.write_packet(pkt)
        if self.driver.read_packet() == self.cmdPacket.STATUS_READY:
            logging.debug('Pinged. Status READY')
        else:
            logging.debug('Pinged. Status NOT READY')

    def reset(self, reset_type):
        """ Send a "reset" packet to the AlienFX controller."""
        reset_code = self.getResetCode(reset_type)
        pkt = self.cmdPacket.makeCmdReset(reset_code)
        logging.debug("SENDING: {}".format(self.pktToString(pkt)))
        self.driver.write_packet(pkt)
        logging.debug('Reset done')

    def waitControllerReady(self):
        """ Keep sending a "get status" packet to the AlienFX controller and 
        return only when the controller is ready
        """
        ready = False
        errcount = 0
        while not ready:
            pkt = self.cmdPacket.makeCmdGetStatus()
            logging.debug("SENDING: {}".format(self.pktToString(pkt)))
            self.driver.write_packet(pkt)
            try:
                resp = self.driver.read_packet()
                ready = (resp[0] == self.cmdPacket.STATUS_READY)
            except TypeError:
                errcount += 1
                logging.debug("No Status received yet... Failed tries=" + str(errcount))
            if errcount > 50:
                logging.error("Controller status could not be retrieved. Is the device already in use?")
                exit(-1)
        logging.debug('Controller Ready')

    def pktToString(self, pkt_bytes):
        """ Return a human readable string representation of an AlienFX
        command packet.
        """
        return self.cmdPacket.pktToString(pkt_bytes, self)

    def getNoZoneCode(self):
        """ Return a zone code corresponding to all non-visible zones."""
        zone_codes = [self.zone_map[x] for x in self.zone_map]
        return ~reduce(lambda x, y: x | y, zone_codes, 0)

    def getZoneCodes(self, zone_names):
        """ Given zone names, return the zone codes they refer to.
        """
        zones = 0
        for zone in zone_names:
            if zone in self.zone_map:
                zones |= self.zone_map[zone]
        return zones

    def getResetCode(self, reset_name):
        """ Given the name of a reset action, return its code. """
        for reset in self.reset_types:
            if reset_name == self.reset_types[reset]:
                return reset
        logging.warning("Unknown reset type: {}".format(reset_name))
        return 0

    def makeLoopCommands(self, themefile, zones, block, loop_items):
        """ Given loop-items from the theme file, return a list of loop
        commands.
        """
        loop_cmds = []
        pkt = self.cmdPacket
        for item in loop_items:
            item_type = themefile.get_action_type(item)
            item_colours = themefile.get_action_colours(item)
            if item_type == AlienwareThemeFile.KW_ACTION_TYPE_FIXED:
                if len(item_colours) != 1:
                    logging.warning("fixed must have exactly one colour value")
                    continue
                loop_cmds.append(
                    pkt.makeCmdSetColour(block, zones, item_colours[0]))
            elif item_type == AlienwareThemeFile.KW_ACTION_TYPE_BLINK:
                if len(item_colours) != 1:
                    logging.warning("blink must have exactly one colour value")
                    continue
                loop_cmds.append(
                    pkt.makeCmdSetBlinkColour(block, zones, item_colours[0]))
            elif item_type == AlienwareThemeFile.KW_ACTION_TYPE_MORPH:
                if len(item_colours) != 2:
                    logging.warning("morph must have exactly two colour values")
                    continue
                loop_cmds.append(
                    pkt.makeCmdSetMorphColour(
                        block, zones, item_colours[0], item_colours[1]))
            else:
                logging.warning("unknown loop item type: {}".format(item_type))
        return loop_cmds

    def makeZoneCommands(self, themefile, state_name, boot=False):
        """ Given a theme file, return a list of zone commands.
        
        If 'boot' is True, then the colour commands created are not saved with
        SAVE_NEXT commands. Also, the final command is one to set the colour
        of all non-visible zones to black.
        """
        zone_cmds = []
        block = 1
        pkt = self.cmdPacket
        state = self.state_map[state_name]
        state_items = themefile.get_state_items(state_name)
        for item in state_items:
            zone_codes = self.getZoneCodes(themefile.get_zone_names(item))
            loop_items = themefile.get_loop_items(item)
            loop_cmds = self.makeLoopCommands(
                themefile, zone_codes, block, loop_items)
            if (loop_cmds):
                block += 1
                for loop_cmd in loop_cmds:
                    if not boot:
                        zone_cmds.append(pkt.makeCmdSaveNext(state))
                    zone_cmds.append(loop_cmd)
                if not boot:
                    zone_cmds.append(pkt.makeCmdSaveNext(state))
                zone_cmds.append(pkt.makeCmdLoopBlockEnd())
        if zone_cmds:
            if not boot:
                zone_cmds.append(pkt.makeCmdSave())
        if boot:
            zone_cmds.append(
                pkt.makeCmdSetColour(
                    block, self.getNoZoneCode(), (0, 0, 0)))
            zone_cmds.append(pkt.makeCmdLoopBlockEnd())
        return zone_cmds

    def sendCommands(self, cmds):
        """ Send the given commands to the controller. """
        for cmd in cmds:
            logging.debug("SENDING: {}".format(self.pktToString(cmd)))
            self.driver.write_packet(cmd)

    def setTheme(self, themefile):
        """ Send the given theme settings to the controller. This should result
        in the lights changing to the theme settings immediately.
        """
        try:
            self.driver.acquire()
            bootCommands = []

            # prepare the controller
            self.ping()
            self.reset("all-lights-on")
            self.waitControllerReady()

            for state_name in self.state_map:
                commands = self.makeZoneCommands(themefile, state_name)
                # Boot block commands are saved for sending again later.
                # The second time, they are sent without SAVE_NEXT commands.
                if state_name == self.STATE_BOOT:
                    bootCommands = self.makeZoneCommands(themefile, state_name, boot=True)
                self.sendCommands(commands)

            self.sendCommands([self.cmdPacket.makeCmdSetSpeed(themefile.get_speed())])
            # send the boot block commands again
            self.sendCommands(bootCommands)
            cmd = self.cmdPacket.makeCmdTransmitExecute()
            self.sendCommands([cmd])
        finally:
            self.driver.release()
