import logging

from usbdriver import AlienwareUSBDriver
from cmdpacket import AlienwareCmdPacket
from functools import reduce


class AlienwareController:

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

    ALIEN_HEAD = 0x0020
    LOGO = 0x0040
    TOUCH_PAD = 0x0080
    POWER_BUTTON = 0x0100

    # HDD_LED = 0x0200
    # WIFI_LED = 0x0400
    # CAPS_LED = 0x0080

    # Reset codes
    RESET_ALL_LIGHTS_OFF = 3
    RESET_ALL_LIGHTS_ON = 4

    # Zone names
    ZONE_LEFT_KEYBOARD = "Left Keyboard"
    ZONE_MIDDLE_LEFT_KEYBOARD = "Middle-left Keyboard"
    ZONE_MIDDLE_RIGHT_KEYBOARD = "Middle-right Keyboard"
    ZONE_RIGHT_KEYBOARD = "Right Keyboard"
    ZONE_ALIEN_HEAD = "Alien Head"
    ZONE_LOGO = "Logo"
    ZONE_TOUCH_PAD = "Touchpad"
    ZONE_POWER_BUTTON = "Power Button"

    # State names
    STATE_BOOT = "Boot"
    STATE_AC_SLEEP = "AC Sleep"
    STATE_AC_CHARGED = "AC Charged"
    STATE_AC_CHARGING = "AC Charging"
    STATE_BATTERY_SLEEP = "Battery Sleep"
    STATE_BATTERY_ON = "Battery On"
    STATE_BATTERY_CRITICAL = "Battery Critical"

    # State codes
    BOOT = 1
    AC_SLEEP = 2
    AC_CHARGED = 5
    AC_CHARGING = 6
    BATTERY_SLEEP = 7
    BATTERY_ON = 8
    BATTERY_CRITICAL = 9

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

        self.driver = AlienwareUSBDriver(self.vendorId, self.productId, self.cmdPacket.PACKET_LENGTH)

    def getStatus(self):
        pkt = self.cmdPacket.makeCmdGetStatus()
        logging.debug("writing command: {}".format(self.pktToString(pkt)))
        self.driver.writePacket(pkt)
        response = self.driver.readPacket()
        isReady = response[0] == self.cmdPacket.STATUS_READY
        if isReady:
            logging.debug('Pinged, STATUS_READY')
        else:
            logging.debug('Pinged, STATUS_BUSY')
        return isReady

    def reset(self, reset_type):
        reset_code = self.getResetCode(reset_type)
        pkt = self.cmdPacket.makeCmdReset(reset_code)
        logging.debug("writing command: {}".format(self.pktToString(pkt)))
        self.driver.writePacket(pkt)

    def waitUntilControllerReady(self):
        isReady = False
        errCount = 0
        while not isReady:
            try:
                isReady = self.getStatus()
            except TypeError:
                errCount += 1
                logging.debug("No Status received yet... Num failed tries={}".format(errCount))

            if errCount > 50:
                logging.error("Controller status could not be retrieved. Is the device already in use?")
                exit(-1)
        logging.debug('Controller Ready')

    def sendCommands(self, cmds):
        for cmd in cmds:
            logging.debug("writing command: {}".format(self.pktToString(cmd)))
            self.driver.writePacket(cmd)

    def pktToString(self, pkt_bytes):
        return self.cmdPacket.pktToString(pkt_bytes, self)

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
