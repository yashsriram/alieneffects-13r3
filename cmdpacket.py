class AlienwareCommandPacketManager(object):
    """Provides facilities to create and parse command packets"""

    # Command codes
    CMD_SET_MORPH_COLOUR = 0x1
    CMD_SET_BLINK_COLOUR = 0x2
    CMD_SET_COLOUR = 0x3
    CMD_LOOP_SEQUENCE = 0x4
    CMD_TRANSMIT_EXECUTE = 0x5
    CMD_GET_STATUS = 0x6
    CMD_RESET = 0x7
    CMD_SAVE_NEXT = 0x8
    CMD_SAVE = 0x9
    CMD_SET_SPEED = 0xe

    # Status codes
    STATUS_BUSY = 0x11
    STATUS_READY = 0x10
    STATUS_UNKNOWN_COMMAND = 0x12

    PACKET_LENGTH = 12

    def __init__(self):
        self.commandParsers = {
            self.CMD_SET_MORPH_COLOUR: self._parseCmdSetMorphColour,
            self.CMD_SET_BLINK_COLOUR: self._parseCmdSetBlinkColour,
            self.CMD_SET_COLOUR: self._parseCmdSetColour,
            self.CMD_LOOP_SEQUENCE: self._parseCmdLoopSequence,
            self.CMD_TRANSMIT_EXECUTE: self._parseCmdTransmitExecute,
            self.CMD_GET_STATUS: self._parseCmdGetStatus,
            self.CMD_RESET: self._parseCmdReset,
            self.CMD_SAVE_NEXT: self._parseCmdSaveNext,
            self.CMD_SAVE: self._parseCmdSave,
            self.CMD_SET_SPEED: self._parseCmdSetSpeed
        }

    def pktToString(self, pkt, controller):
        """ Return a human readable string representation of a command packet"""
        try:
            cmd = pkt[1]
            args = {"pkt": pkt, "controller": controller}
            if cmd in list(self.commandParsers.keys()):
                return self.commandParsers[cmd](args)
            else:
                return self._parseCmdUnknown(args)
        except Exception as e:
            print(e)

    @staticmethod
    def _unpackColourPair(pkt):
        red1 = pkt[0]
        green1 = pkt[1]
        blue1 = pkt[2]
        red2 = pkt[3]
        green2 = pkt[4]
        blue2 = pkt[5]
        return (red1, green1, blue1), (red2, green2, blue2)

    @staticmethod
    def _unpackColour(pkt):
        red = pkt[0]
        green = pkt[1]
        blue = pkt[2]
        return red, green, blue

    @classmethod
    def _parseCmdSetMorphColour(cls, args):
        """ Parse a packet containing the "set morph colour" command and
        return it as a human readable string.
        """
        pkt = args["pkt"]
        controller = args["controller"]
        (red1, green1, blue1), (red2, green2, blue2) = (cls._unpackColourPair(pkt[6:12]))
        msg = "SET_MORPH_COLOUR: "
        msg += "SEQUENCE: {}".format(pkt[2])
        msg += ", ZONE: {}".format(controller.getZoneName(pkt[3:6]))
        msg += ", COLORS: ({},{},{})-({},{},{})".format(
            red1, green1, blue1, red2, green2, blue2)
        return msg

    @classmethod
    def _parseCmdSetBlinkColour(cls, args):
        """ Parse a packet containing the "set blink colour" command and
        return it as a human readable string.
        """
        pkt = args["pkt"]
        controller = args["controller"]
        (red, green, blue) = cls._unpackColour(pkt[6:9])
        msg = "SET_BLINK_COLOUR: "
        msg += "SEQUENCE: {}".format(pkt[2])
        msg += ", ZONE: {}".format(controller.getZoneName(pkt[3:6]))
        msg += ", COLOR: ({},{},{})".format(red, green, blue)
        return msg

    @classmethod
    def _parseCmdSetColour(cls, args):
        """ Parse a packet containing the "set colour" command and
        return it as a human readable string.
        """
        pkt = args["pkt"]
        controller = args["controller"]
        (red, green, blue) = cls._unpackColour(pkt[6:8])
        msg = "SET_COLOUR: "
        msg += "SEQUENCE: {}".format(pkt[2])
        msg += ", ZONE: {}".format(controller.getZoneName(pkt[3:6]))
        msg += ", COLOR: ({},{},{})".format(red, green, blue)
        return msg

    @classmethod
    def _parseCmdLoopSequence(cls, args):
        """ Parse a packet containing the "loop sequence" command and
        return it as a human readable string.
        """
        return "LOOP_SEQUENCE"

    @classmethod
    def _parseCmdTransmitExecute(cls, args):
        """ Parse a packet containing the "transmit execute" command and
        return it as a human readable string.
        """
        return "TRANSMIT_EXECUTE"

    @classmethod
    def _parseCmdGetStatus(cls, args):
        """ Parse a packet containing the "get status" command and
        return it as a human readable string.
        """
        return "GET_STATUS"

    @classmethod
    def _parseCmdReset(cls, args):
        """ Parse a packet containing the "reset" command and
        return it as a human readable string.
        """
        pkt = args["pkt"]
        controller = args["controller"]
        return "RESET: {}".format(controller.getResetTypeName(pkt[2]))

    @classmethod
    def _parseCmdSaveNext(cls, args):
        """ Parse a packet containing the "save next" command and
        return it as a human readable string.
        """
        pkt = args["pkt"]
        controller = args["controller"]
        return "SAVE_NEXT: STATE {}".format(controller.getStateName(pkt[2]))

    @classmethod
    def _parseCmdSave(cls, args):
        """ Parse a packet containing the "save" command and
        return it as a human readable string.
        """
        return "SAVE"

    @classmethod
    def _parseCmdSetSpeed(cls, args):
        """ Parse a packet containing the "set speed" command and
        return it as a human readable string.
        """
        pkt = args["pkt"]
        return "SET_SPEED: {}".format(hex((pkt[2] << 8) + pkt[3]))

    @classmethod
    def _parseCmdUnknown(cls, args):
        """ Return a string description an unknown command packet"""
        pkt = args["pkt"]
        return "UNKNOWN COMMAND : {} IN PACKET {}".format(pkt[1], pkt)

    @staticmethod
    def validateColourPair(colour1, colour2):
        for band in colour1:
            if not (isinstance(band, int) and 0 <= band <= 255):
                raise RuntimeError('Invalid color')
        for band in colour2:
            if not (isinstance(band, int) and 0 <= band <= 255):
                raise RuntimeError('Invalid color')
        (red1, green1, blue1) = colour1
        (red2, green2, blue2) = colour2
        pkt = [red1, green1, blue1, red2, green2, blue2]
        return pkt

    @staticmethod
    def validateColor(colour):
        for band in colour:
            if not (isinstance(band, int) and 0 <= band <= 255):
                raise RuntimeError('Invalid color')
        return colour

    @classmethod
    def makeCmdGetStatus(cls):
        pkt = [0x02, cls.CMD_GET_STATUS, 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        return pkt

    @classmethod
    def makeCmdReset(cls, reset_type):
        pkt = [0x02, cls.CMD_RESET, 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        pkt[2] = reset_type & 0xff
        return pkt

    @classmethod
    def makeCmdSetMorphColour(cls, sequence, zone, colour1, colour2):
        pkt = [0x02, cls.CMD_SET_MORPH_COLOUR, 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        pkt[2] = sequence & 0xff
        pkt[3:6] = [(zone & 0xff0000) >> 16, (zone & 0xff00) >> 8, zone & 0xff]
        pkt[6:12] = cls.validateColourPair(colour1, colour2)
        return pkt

    @classmethod
    def makeCmdSetBlinkColour(cls, sequence, zone, colour):
        pkt = [0x02, cls.CMD_SET_BLINK_COLOUR, 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        pkt[2] = sequence & 0xff
        pkt[3:6] = [(zone & 0xff0000) >> 16, (zone & 0xff00) >> 8, zone & 0xff]
        pkt[6:9] = cls.validateColor(colour)
        return pkt

    @classmethod
    def makeCmdSetColour(cls, sequence, zone, colour):
        pkt = [0x02, cls.CMD_SET_COLOUR, 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        pkt[2] = sequence & 0xff
        pkt[3:6] = [(zone & 0xff0000) >> 16, (zone & 0xff00) >> 8, zone & 0xff]
        pkt[6:9] = cls.validateColor(colour)
        return pkt

    @classmethod
    def makeCmdLoopSequence(cls):
        pkt = [0x02, cls.CMD_LOOP_SEQUENCE, 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        return pkt

    @classmethod
    def makeCmdSetSpeed(cls, speed):
        pkt = [0x02, cls.CMD_SET_SPEED, 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        pkt[2:4] = [(speed & 0xff00) >> 8, speed & 0xff]
        return pkt

    @classmethod
    def makeCmdTransmitExecute(cls):
        pkt = [0x02, cls.CMD_TRANSMIT_EXECUTE, 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        return pkt

    @classmethod
    def makeCmdSaveNext(cls, state):
        pkt = [0x02, cls.CMD_SAVE_NEXT, 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        pkt[2] = state & 0xff
        return pkt

    @classmethod
    def makeCmdSave(cls):
        pkt = [0x02, cls.CMD_SAVE, 0,
               0, 0, 0,
               0, 0, 0,
               0, 0, 0]
        return pkt
