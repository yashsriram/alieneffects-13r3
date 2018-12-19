import logging

from alieneffects.usbdriver import AlienwareUSBDriver


class AlienwareController:
    # Lower the tempo, faster the blink/morph actions
    # The min tempo is selected by trial and error
    #   as the lowest value that won't result in strange blink/morph behaviour.
    MIN_TEMPO = 50

    class Reset:
        ALL_LIGHTS_OFF = "RESET_ALL_LIGHTS_OFF"
        ALL_LIGHTS_ON = "RESET_ALL_LIGHTS_ON"

        CODES = {
            ALL_LIGHTS_OFF: 3,
            ALL_LIGHTS_ON: 4
        }

        def __init__(self):
            pass

    class Zones:
        LEFT_KEYBOARD = "LEFT_KEYBOARD"
        MIDDLE_LEFT_KEYBOARD = "MIDDLE_LEFT_KEYBOARD"
        MIDDLE_RIGHT_KEYBOARD = "MIDDLE_RIGHT_KEYBOARD"
        RIGHT_KEYBOARD = "RIGHT_KEYBOARD"
        ALIEN_HEAD = "ALIEN_HEAD"
        ALIENWARE_LOGO = "ALIENWARE_LOGO"
        TOUCH_PAD = "TOUCH_PAD"
        POWER_BUTTON = "POWER_BUTTON"

        CODES = {
            LEFT_KEYBOARD: 0x0008,
            MIDDLE_LEFT_KEYBOARD: 0x0004,
            MIDDLE_RIGHT_KEYBOARD: 0x0002,
            RIGHT_KEYBOARD: 0x0001,
            ALIEN_HEAD: 0x0020,
            ALIENWARE_LOGO: 0x0040,
            TOUCH_PAD: 0x0080,
            POWER_BUTTON: 0x0100,
        }

    class PowerStates:
        BOOT = "BOOT"
        AC_SLEEP = "AC_SLEEP"
        AC_CHARGED = "AC_CHARGED"
        AC_CHARGING = "AC_CHARGING"
        BATTERY_SLEEP = "BATTERY_SLEEP"
        BATTERY_ON = "BATTERY_ON"
        BATTERY_CRITICAL = "BATTERY_CRITICAL"

        CODES = {
            BOOT: 1,
            AC_SLEEP: 2,
            AC_CHARGED: 5,
            AC_CHARGING: 6,
            BATTERY_SLEEP: 7,
            BATTERY_ON: 8,
            BATTERY_CRITICAL: 9
        }

    class Commands:
        MORPH_COLOR = 'MORPH_COLOR'
        BLINK_COLOR = 'BLINK_COLOR'
        SET_COLOR = 'SET_COLOR'
        LOOP_SEQUENCE = 'LOOP_SEQUENCE'
        EXECUTE = 'EXECUTE'
        GET_STATUS = 'GET_STATUS'
        RESET = 'RESET'
        SAVE_NEXT = 'SAVE_NEXT'
        SAVE = 'SAVE'
        SET_TEMPO = 'SET_TEMPO'

        CODES = {
            MORPH_COLOR: 0x1,
            BLINK_COLOR: 0x2,
            SET_COLOR: 0x3,
            LOOP_SEQUENCE: 0x4,
            EXECUTE: 0x5,
            GET_STATUS: 0x6,
            RESET: 0x7,
            SAVE_NEXT: 0x8,
            SAVE: 0x9,
            SET_TEMPO: 0xe
        }

    class Status:
        BUSY = 0x11
        READY = 0x10
        UNKNOWN = 0x12

    def __init__(self):
        c = self.Commands.CODES
        self.commandParsers = {
            c[self.Commands.MORPH_COLOR]: self._parseCmdMorphColor,
            c[self.Commands.BLINK_COLOR]: self._parseCmdBlinkColor,
            c[self.Commands.SET_COLOR]: self._parseCmdSetColor,
            c[self.Commands.LOOP_SEQUENCE]: self._parseCmdLoopSequence,
            c[self.Commands.EXECUTE]: self._parseCmdExecute,
            c[self.Commands.GET_STATUS]: self._parseCmdGetStatus,
            c[self.Commands.RESET]: self._parseCmdReset,
            c[self.Commands.SAVE_NEXT]: self._parseCmdSaveNext,
            c[self.Commands.SAVE]: self._parseCmdSave,
            c[self.Commands.SET_TEMPO]: self._parseCmdSetTempo,
        }
        self.driver = AlienwareUSBDriver()

    def getStatus(self):
        pkt = self.makeGetStatusCmd()
        logging.debug("writing command: {}".format(pkt))
        logging.debug("description: {}".format(self.pktToString(pkt)))
        self.driver.writePacket(pkt)
        response = self.driver.readPacket()
        isReady = response[0] == self.Status.READY
        if isReady:
            logging.debug('Pinged, STATUS_READY')
        else:
            logging.debug('Pinged, STATUS_BUSY')
        return isReady

    def reset(self, resetCode):
        pkt = self.makeResetCmd(resetCode)
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

    # Make command packet methods
    @staticmethod
    def _validateColor(color):
        for band in color:
            if not (isinstance(band, int) and 0 <= band <= 255):
                raise RuntimeError('Invalid color')

    @classmethod
    def _validateTempo(cls, tempo):
        if not (isinstance(tempo, int) and tempo >= cls.MIN_TEMPO):
            raise RuntimeError('Invalid tempo')

    @staticmethod
    def _validateZoneCode(zoneCode):
        if not (isinstance(zoneCode, int) and zoneCode <= 0xffff):
            raise RuntimeError('Invalid zone code')

    @classmethod
    def _validateResetCode(cls, resetCode):
        if not (isinstance(resetCode, int) and resetCode in cls.Reset.CODES.values()):
            raise RuntimeError('Invalid reset code')

    @classmethod
    def _validatePowerStateCode(cls, powerStateCode):
        if not (isinstance(powerStateCode, int) and powerStateCode in cls.PowerStates.CODES.values()):
            raise RuntimeError('Invalid power state')

    @classmethod
    def makeGetStatusCmd(cls):
        pkt = [0x02, cls.Commands.CODES[cls.Commands.GET_STATUS], 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        return pkt

    @classmethod
    def makeResetCmd(cls, resetCode):
        cls._validateResetCode(resetCode)
        pkt = [0x02, cls.Commands.CODES[cls.Commands.RESET], 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        pkt[2] = resetCode & 0xff
        return pkt

    @classmethod
    def makeMorphColorCmd(cls, sequence, zoneCode, color1, color2):
        cls._validateZoneCode(zoneCode)
        cls._validateColor(color1)
        cls._validateColor(color2)
        pkt = [0x02, cls.Commands.CODES[cls.Commands.MORPH_COLOR], 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        pkt[2] = sequence & 0xff
        pkt[3:6] = [(zoneCode & 0xff0000) >> 16, (zoneCode & 0xff00) >> 8, zoneCode & 0xff]
        (red1, green1, blue1) = color1
        (red2, green2, blue2) = color2
        pkt[6:12] = [red1, green1, blue1, red2, green2, blue2]
        return pkt

    @classmethod
    def makeBlinkColorCmd(cls, sequence, zoneCode, color):
        cls._validateZoneCode(zoneCode)
        cls._validateColor(color)
        pkt = [0x02, cls.Commands.CODES[cls.Commands.BLINK_COLOR], 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        pkt[2] = sequence & 0xff
        pkt[3:6] = [(zoneCode & 0xff0000) >> 16, (zoneCode & 0xff00) >> 8, zoneCode & 0xff]
        pkt[6:9] = color
        return pkt

    @classmethod
    def makeSetColorCmd(cls, sequence, zoneCode, color):
        cls._validateZoneCode(zoneCode)
        cls._validateColor(color)
        pkt = [0x02, cls.Commands.CODES[cls.Commands.SET_COLOR], 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        pkt[2] = sequence & 0xff
        pkt[3:6] = [(zoneCode & 0xff0000) >> 16, (zoneCode & 0xff00) >> 8, zoneCode & 0xff]
        pkt[6:9] = color
        return pkt

    @classmethod
    def makeLoopSequenceCmd(cls):
        pkt = [0x02, cls.Commands.CODES[cls.Commands.LOOP_SEQUENCE], 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        return pkt

    @classmethod
    def makeSetTempoCmd(cls, tempo):
        cls._validateTempo(tempo)
        pkt = [0x02, cls.Commands.CODES[cls.Commands.SET_TEMPO], 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        pkt[2:4] = [(tempo & 0xff00) >> 8, tempo & 0xff]
        return pkt

    @classmethod
    def makeExecuteCmd(cls):
        pkt = [0x02, cls.Commands.CODES[cls.Commands.EXECUTE], 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        return pkt

    @classmethod
    def makeSaveNextCmd(cls, powerStateCode):
        cls._validatePowerStateCode(powerStateCode)
        pkt = [0x02, cls.Commands.CODES[cls.Commands.SAVE_NEXT], 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        pkt[2] = powerStateCode & 0xff
        return pkt

    @classmethod
    def makeSaveCmd(cls):
        pkt = [0x02, cls.Commands.CODES[cls.Commands.SAVE], 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        return pkt

    # Describe command packet methods
    def getZoneName(self, pkt):
        zonesMask = (pkt[0] << 16) + (pkt[1] << 8) + pkt[2]
        zoneNames = []
        for name, code in self.Zones.CODES.items():
            if zonesMask & code:
                zoneNames.append(name)
                zonesMask &= ~code
        if zonesMask != 0:
            zoneNames.append("UNKNOWN_ZONE_CODE({})".format(hex(zonesMask)))
        return ', '.join(zoneNames)

    def getPowerStateName(self, powerStateCode):
        for name, code in self.PowerStates.CODES:
            if code == powerStateCode:
                return name
        return "UNKNOWN_POWER_STATE_CODE"

    def getResetTypeName(self, resetCode):
        for name, code in self.Reset.CODES.items():
            if code == resetCode:
                return name
        return "UNKNOWN_RESET_CODE"

    def pktToString(self, pkt):
        cmd = pkt[1]
        if cmd in list(self.commandParsers.keys()):
            return self.commandParsers[cmd](pkt)
        else:
            return self._parseCmdUnknown(pkt)

    @staticmethod
    def _unpackColorPair(pkt):
        red1 = pkt[0]
        green1 = pkt[1]
        blue1 = pkt[2]
        red2 = pkt[3]
        green2 = pkt[4]
        blue2 = pkt[5]
        return (red1, green1, blue1), (red2, green2, blue2)

    @staticmethod
    def _unpackColor(pkt):
        red = pkt[0]
        green = pkt[1]
        blue = pkt[2]
        return red, green, blue

    def _parseCmdMorphColor(self, pkt):
        (red1, green1, blue1), (red2, green2, blue2) = (self._unpackColorPair(pkt[6:12]))
        msg = [
            "\n\tZONE: {}".format(self.getZoneName(pkt[3:6])),
            "SEQUENCE: {}".format(pkt[2]),
            "EFFECT: MORPH_COLOR",
            "COLORS: ({},{},{})-({},{},{})".format(red1, green1, blue1, red2, green2, blue2),
        ]
        return '\n\t'.join(msg)

    def _parseCmdBlinkColor(self, pkt):
        (red, green, blue) = self._unpackColor(pkt[6:9])
        msg = [
            "\n\tZONE: {}".format(self.getZoneName(pkt[3:6])),
            "SEQUENCE: {}".format(pkt[2]),
            "EFFECT: BLINK_COLOR",
            "COLOR: ({},{},{})".format(red, green, blue),
        ]
        return '\n\t'.join(msg)

    def _parseCmdSetColor(self, pkt):
        (red, green, blue) = self._unpackColor(pkt[6:9])
        msg = [
            "\n\tZONE: {}".format(self.getZoneName(pkt[3:6])),
            "SEQUENCE: {}".format(pkt[2]),
            "EFFECT: SET_COLOR",
            "COLOR: ({},{},{})".format(red, green, blue),
        ]
        return '\n\t'.join(msg)

    def _parseCmdLoopSequence(self, pkt):
        return "LOOP_SEQUENCE"

    def _parseCmdExecute(self, pkt):
        return "TRANSMIT_EXECUTE"

    def _parseCmdGetStatus(self, pkt):
        return "GET_STATUS"

    def _parseCmdReset(self, pkt):
        return "RESET: {}".format(self.getResetTypeName(pkt[2]))

    def _parseCmdSaveNext(self, pkt):
        return "SAVE_NEXT: STATE {}".format(self.getPowerStateName(pkt[2]))

    def _parseCmdSave(self, pkt):
        return "SAVE"

    def _parseCmdSetTempo(self, pkt):
        return "SET_TEMPO: {} ms".format((pkt[2] << 8) + pkt[3])

    def _parseCmdUnknown(self, pkt):
        return "UNKNOWN COMMAND : {} IN PACKET {}".format(pkt[1], pkt)
