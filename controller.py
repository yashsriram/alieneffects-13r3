import logging

from cmdpacket import AlienwareCommandPacketManager
from usbdriver import AlienwareUSBDriver


class AlienwareController:
    # Speed capabilities
    # The higher the number, the slower the speed of blink/morph actions
    # The min speed is selected by trial and error
    #   as the lowest value that won't result in strange blink/morph behaviour.
    DEFAULT_SPEED = 200
    MIN_SPEED = 50

    # Zone codes
    LEFT_KEYBOARD = 0x0008
    MIDDLE_LEFT_KEYBOARD = 0x0004
    MIDDLE_RIGHT_KEYBOARD = 0x0002
    RIGHT_KEYBOARD = 0x0001

    ALIEN_HEAD = 0x0020
    ALIENWARE_LOGO = 0x0040
    TOUCH_PAD = 0x0080
    POWER_BUTTON = 0x0100

    # HDD_LED = 0x0200
    # WIFI_LED = 0x0400
    # CAPS_LED = 0x0080

    # Effect codes
    EFFECT_SET_COLOR = 1
    EFFECT_BLINK_COLOR = 2
    EFFECT_MORPH_COLOR = 3

    # Reset codes
    RESET_ALL_LIGHTS_OFF = 3
    RESET_ALL_LIGHTS_ON = 4

    # Zone names
    ZONE_LEFT_KEYBOARD = "LeftKeyboard"
    ZONE_MIDDLE_LEFT_KEYBOARD = "MiddleLeftKeyboard"
    ZONE_MIDDLE_RIGHT_KEYBOARD = "MiddleRightKeyboard"
    ZONE_RIGHT_KEYBOARD = "RightKeyboard"
    ZONE_ALIEN_HEAD = "AlienHead"
    ZONE_LOGO = "AlienwareLogo"
    ZONE_TOUCH_PAD = "TouchPad"
    ZONE_POWER_BUTTON = "PowerButton"

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
        self.name = "Alienware 13 R3"

        # USB VID and PID
        self.vendorId = 0x187c
        self.productId = 0x0529

        # map the zone names to their codes
        self.zoneMap = {
            self.ZONE_LEFT_KEYBOARD: self.LEFT_KEYBOARD,
            self.ZONE_MIDDLE_LEFT_KEYBOARD: self.MIDDLE_LEFT_KEYBOARD,
            self.ZONE_MIDDLE_RIGHT_KEYBOARD: self.MIDDLE_RIGHT_KEYBOARD,
            self.ZONE_RIGHT_KEYBOARD: self.RIGHT_KEYBOARD,
            self.ZONE_ALIEN_HEAD: self.ALIEN_HEAD,
            self.ZONE_LOGO: self.ALIENWARE_LOGO,
            self.ZONE_TOUCH_PAD: self.TOUCH_PAD,
            self.ZONE_POWER_BUTTON: self.POWER_BUTTON,
        }

        # zones that have special behaviour in the different power states
        self.powerZones = [
            self.ZONE_POWER_BUTTON,
        ]

        # map the reset names to their codes
        self.resetTypes = {
            self.RESET_ALL_LIGHTS_OFF: "ALL-LIGHTS-OFF",
            self.RESET_ALL_LIGHTS_ON: "ALL-LIGHTS-ON"
        }

        # map the state names to their codes
        self.stateMap = {
            self.STATE_BOOT: self.BOOT,
            self.STATE_AC_SLEEP: self.AC_SLEEP,
            self.STATE_AC_CHARGED: self.AC_CHARGED,
            self.STATE_AC_CHARGING: self.AC_CHARGING,
            self.STATE_BATTERY_SLEEP: self.BATTERY_SLEEP,
            self.STATE_BATTERY_ON: self.BATTERY_ON,
            self.STATE_BATTERY_CRITICAL: self.BATTERY_CRITICAL
        }

        self.cmdPktManager = AlienwareCommandPacketManager()

        self.driver = AlienwareUSBDriver(self.vendorId, self.productId)

    def getStatus(self):
        pkt = self.cmdPktManager.makeCmdGetStatus()
        logging.debug("writing command: {}".format(pkt))
        logging.debug("description: {}".format(self.pktToString(pkt)))
        self.driver.writePacket(pkt)
        response = self.driver.readPacket()
        isReady = response[0] == self.cmdPktManager.STATUS_READY
        if isReady:
            logging.debug('Pinged, STATUS_READY')
        else:
            logging.debug('Pinged, STATUS_BUSY')
        return isReady

    def reset(self, resetCode):
        pkt = self.cmdPktManager.makeCmdReset(resetCode)
        logging.debug("writing command: {}".format(pkt))
        logging.debug("description: {}".format(self.pktToString(pkt)))
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
            logging.debug("writing command: {}".format(cmd))
            logging.debug("description: {}".format(self.pktToString(cmd)))
            self.driver.writePacket(cmd)

    def pktToString(self, pkt_bytes):
        return self.cmdPktManager.pktToString(pkt_bytes, self)

    def getZoneName(self, pkt):
        zonesMask = (pkt[0] << 16) + (pkt[1] << 8) + pkt[2]
        zoneNames = []
        for zoneName, zoneMask in self.zoneMap.items():
            if zonesMask & zoneMask:
                zoneNames.append(zoneName)
                zonesMask &= ~zoneMask
        if zonesMask != 0:
            zoneNames.append("UNKNOWN({})".format(hex(zonesMask)))
        return ', '.join(zoneNames)

    def getStateName(self, state):
        """ Given a state number, return a string state name"""
        for state_name in self.stateMap:
            if self.stateMap[state_name] == state:
                return state_name
        return "UNKNOWN"

    def getResetTypeName(self, num):
        """ Given a reset number, return a string reset name"""
        if num in list(self.resetTypes.keys()):
            return self.resetTypes[num]
        else:
            return "UNKNOWN"
