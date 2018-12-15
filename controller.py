import logging

from cmdpktmanager import AlienwareCommandPacketManager
from usbdriver import AlienwareUSBDriver


class AlienwareController:
    # Lower the tempo, faster the blink/morph actions
    # The min tempo is selected by trial and error
    #   as the lowest value that won't result in strange blink/morph behaviour.
    DEFAULT_TEMPO = 200
    MIN_TEMPO = 50

    # Reset type names
    RESET_ALL_LIGHTS_OFF = "RESET_ALL_LIGHTS_OFF"
    RESET_ALL_LIGHTS_ON = "RESET_ALL_LIGHTS_ON"

    RESET_TYPE_CODES = {
        RESET_ALL_LIGHTS_OFF: 3,
        RESET_ALL_LIGHTS_ON: 4
    }

    # Zone names
    LEFT_KEYBOARD = "LEFT_KEYBOARD"
    MIDDLE_LEFT_KEYBOARD = "MIDDLE_LEFT_KEYBOARD"
    MIDDLE_RIGHT_KEYBOARD = "MIDDLE_RIGHT_KEYBOARD"
    RIGHT_KEYBOARD = "RIGHT_KEYBOARD"
    ALIEN_HEAD = "ALIEN_HEAD"
    ALIENWARE_LOGO = "ALIENWARE_LOGO"
    TOUCH_PAD = "TOUCH_PAD"
    POWER_BUTTON = "POWER_BUTTON"

    ZONE_CODES = {
        LEFT_KEYBOARD: 0x0008,
        MIDDLE_LEFT_KEYBOARD: 0x0004,
        MIDDLE_RIGHT_KEYBOARD: 0x0002,
        RIGHT_KEYBOARD: 0x0001,
        ALIEN_HEAD: 0x0020,
        ALIENWARE_LOGO: 0x0040,
        TOUCH_PAD: 0x0080,
        POWER_BUTTON: 0x0100,
    }

    # Power state names
    BOOT = "BOOT"
    AC_SLEEP = "AC_SLEEP"
    AC_CHARGED = "AC_CHARGED"
    AC_CHARGING = "AC_CHARGING"
    BATTERY_SLEEP = "BATTERY_SLEEP"
    BATTERY_ON = "BATTERY_ON"
    BATTERY_CRITICAL = "BATTERY_CRITICAL"

    POWER_STATE_CODES = {
        BOOT: 1,
        AC_SLEEP: 2,
        AC_CHARGED: 5,
        AC_CHARGING: 6,
        BATTERY_SLEEP: 7,
        BATTERY_ON: 8,
        BATTERY_CRITICAL: 9
    }

    def __init__(self):
        self.cmdPktManager = AlienwareCommandPacketManager()
        self.driver = AlienwareUSBDriver()

    def getStatus(self):
        pkt = self.cmdPktManager.makeGetStatusCmd()
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
        pkt = self.cmdPktManager.makeResetCmd(resetCode)
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
        for zoneName, zoneMask in self.ZONE_CODES.items():
            if zonesMask & zoneMask:
                zoneNames.append(zoneName)
                zonesMask &= ~zoneMask
        if zonesMask != 0:
            zoneNames.append("UNKNOWN_ZONE_CODE({})".format(hex(zonesMask)))
        return ', '.join(zoneNames)

    def getPowerStateName(self, powerStateCode):
        """ Given a power state code, return a string state name"""
        for name, code in self.POWER_STATE_CODES:
            if code == powerStateCode:
                return name
        return "UNKNOWN_POWER_STATE_CODE"

    def getResetTypeName(self, resetCode):
        """ Given a reset number, return a string reset name"""
        for name, code in self.RESET_TYPE_CODES.items():
            if code == resetCode:
                return name
        return "UNKNOWN_RESET_CODE"
