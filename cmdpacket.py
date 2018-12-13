class AlienwareCmdPacket(object):
    """Provides facilities to parse and create packets

    This class provides methods to parse binary packets into human readable
    strings. It also provides methods to create binary packets.

    As this is for newer alienfx controllers which are setting 8-bits per color (256 values from 0-255 each) we have to convert the color.json-values as they are 4-bits (16 values from 0-15)

    """

    # Command codes
    CMD_SET_MORPH_COLOUR = 0x1
    CMD_SET_BLINK_COLOUR = 0x2
    CMD_SET_COLOUR = 0x3
    CMD_LOOP_BLOCK_END = 0x4
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

    command_parsers = {}

    def __init__(self):
        self.command_parsers = {
            self.CMD_SET_MORPH_COLOUR: self._parseCmdSetMorphColour,
            self.CMD_SET_BLINK_COLOUR: self._parseCmdSetBlinkColour,
            self.CMD_SET_COLOUR: self._parseCmdSetColour,
            self.CMD_LOOP_BLOCK_END: self._parseCmdLoopBlockEnd,
            self.CMD_TRANSMIT_EXECUTE: self._parseCmdTransmitExecute,
            self.CMD_GET_STATUS: self._parseCmdGetStatus,
            self.CMD_RESET: self._parseCmdReset,
            self.CMD_SAVE_NEXT: self._parseCmdSaveNext,
            self.CMD_SAVE: self._parseCmdSave,
            self.CMD_SET_SPEED: self._parseCmdSetSpeed
        }

    def pktToString(self, pkt_bytes, controller):
        """ Return a human readable string representation of a command packet.
        """
        if len(pkt_bytes) != self.PACKET_LENGTH:
            print(len(pkt_bytes), self.PACKET_LENGTH)
            return "BAD PACKET: {}".format(pkt_bytes)
        else:
            cmd = pkt_bytes[1]
            args = {"pkt": pkt_bytes, "controller": controller}
            if cmd in list(self.command_parsers.keys()):
                return self.command_parsers[cmd](args)
            else:
                return self._parseCmdUnknown(args)

    @staticmethod
    def _unpackColourPair(pkt):
        """ Unpack two colour values from the given packet and return them as a
        list of two tuples (each colour is a 3-member tuple)

        TODO: i think this ist still bullshit for the newer controller
        """
        red1 = hex(pkt[0] >> 4)
        green1 = hex(pkt[0] & 0xf)
        blue1 = hex(pkt[1] >> 4)
        red2 = hex(pkt[1] & 0xf)
        green2 = hex(pkt[2] >> 4)
        blue2 = hex(pkt[2] & 0xf)
        return [(red1, green1, blue1), (red2, green2, blue2)]

    @staticmethod
    def _unpackColour(pkt):
        """ Unpack a colour value from the given packet and return it as a
        3-member tuple

        TODO: This mist still be bullshit too
        """
        red = hex(pkt[0] >> 4)
        green = hex(pkt[0] & 0xf)
        blue = hex(pkt[1] >> 4)
        return red, green, blue

    @classmethod
    def _parseCmdSetMorphColour(cls, args):
        """ Parse a packet containing the "set morph colour" command and
        return it as a human readable string.
        """
        pkt = args["pkt"]
        controller = args["controller"]
        [(red1, green1, blue1), (red2, green2, blue2)] = (
            cls._unpackColourPair(pkt[6:9]))
        msg = "SET_MORPH_COLOUR: "
        msg += "BLOCK: {}".format(pkt[2])
        msg += ", ZONE: {}".format(controller.getZoneName(pkt[3:6]))
        msg += ", ({},{},{})-({},{},{})".format(
            red1, green1, blue1, red2, green2, blue2)
        return msg

    @classmethod
    def _parseCmdSetBlinkColour(cls, args):
        """ Parse a packet containing the "set blink colour" command and
        return it as a human readable string.
        """
        pkt = args["pkt"]
        controller = args["controller"]
        (red, green, blue) = cls._unpackColour(pkt[6:8])
        msg = "SET_BLINK_COLOUR: "
        msg += "BLOCK: {}".format(pkt[2])
        msg += ", ZONE: {}".format(controller.getZoneName(pkt[3:6]))
        msg += ", ({},{},{})".format(red, green, blue)
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
        msg += "BLOCK: {}".format(pkt[2])
        msg += ", ZONE: {}".format(controller.getZoneName(pkt[3:6]))
        msg += ", ({},{},{})".format(red, green, blue)
        return msg

    @classmethod
    def _parseCmdLoopBlockEnd(cls, args):
        """ Parse a packet containing the "loop block end" command and
        return it as a human readable string.
        """
        return "LOOP_BLOCK_END"

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
        """ Return a string reporting an unknown command packet.
        """
        pkt = args["pkt"]
        return "UNKNOWN COMMAND : {} IN PACKET {}".format(pkt[1], pkt)

    @staticmethod
    def _packColourPair(colour1, colour2):
        """ Pack two colours into a list of bytes and return the list. Each
        colour is a 3-member tuple
        """
        (red1, green1, blue1) = colour1
        (red2, green2, blue2) = colour2
        # pkt = []
        # pkt.append(((red1&0xf)<<4) + (green1&0xf))
        # pkt.append(((blue1&0xf)<<4) + (red2&0xf))
        # pkt.append(((green2&0xf)<<4) + (blue2&0xf))
        pkt = []
        red8_1 = red1 / float(15) * 255
        green8_1 = green1 / float(15) * 255
        blue8_1 = blue1 / float(15) * 255
        red8_2 = red2 / float(15) * 255
        green8_2 = green2 / float(15) * 255
        blue8_2 = blue2 / float(15) * 255
        pkt.append(int(red8_1))
        pkt.append(int(green8_1))
        pkt.append(int(blue8_1))
        pkt.append(int(red8_2))
        pkt.append(int(green8_2))
        pkt.append(int(blue8_2))
        return pkt

    @staticmethod
    def _packColour(colour):
        """ Pack a colour into a list of bytes and return the list. The
        colour is a 3-member tuple
        """
        (red, green, blue) = colour
        # pkt = [255, 0, 255] # DEBUG should set every color to pink (100% red, 0% green, 100% blue)
        red8 = red / float(15) * 255
        green8 = green / float(15) * 255
        blue8 = blue / float(15) * 255
        pkt = [int(red8), int(green8), int(blue8)]
        return pkt

    @classmethod
    def makeCmdGetStatus(cls):
        """ Return a command packet for the "get status" command with the
        given parameters.
        """
        pkt = [0x02, cls.CMD_GET_STATUS, 0, 0, 0, 0, 0, 0, 0]
        return pkt

    @classmethod
    def makeCmdReset(cls, reset_type):
        """ Return a command packet for the "reset" command with the
        given parameters.
        """
        pkt = [0x02, cls.CMD_RESET, 0, 0, 0, 0, 0, 0, 0]
        pkt[2] = reset_type & 0xff
        return pkt

    @classmethod
    def makeCmdSetMorphColour(cls, block, zone, colour1, colour2):
        """ Return a command packet for the "set morph colour" command with the
        given parameters.
        """
        pkt = [0x02, cls.CMD_SET_MORPH_COLOUR, 0, 0, 0, 0, 0, 0, 0]
        pkt[2] = block & 0xff
        pkt[3:6] = [(zone & 0xff0000) >> 16, (zone & 0xff00) >> 8, zone & 0xff]
        pkt[6:9] = cls._packColourPair(colour1, colour2)
        return pkt

    @classmethod
    def makeCmdSetBlinkColour(cls, block, zone, colour):
        """ Return a command packet for the "set blink colour" command with the
        given parameters.
        """
        pkt = [0x02, cls.CMD_SET_BLINK_COLOUR, 0, 0, 0, 0, 0, 0, 0]
        pkt[2] = block & 0xff
        pkt[3:6] = [(zone & 0xff0000) >> 16, (zone & 0xff00) >> 8, zone & 0xff]
        pkt[6:8] = cls._packColour(colour)
        return pkt

    @classmethod
    def makeCmdSetColour(cls, block, zone, colour):
        """ Return a command packet for the "set colour" command with the
        given parameters.
        """
        pkt = [0x02, cls.CMD_SET_COLOUR, 0, 0, 0, 0, 0, 0, 0]
        pkt[2] = block & 0xff
        pkt[3:6] = [(zone & 0xff0000) >> 16, (zone & 0xff00) >> 8, zone & 0xff]
        pkt[6:8] = cls._packColour(colour)
        return pkt

    @classmethod
    def makeCmdLoopBlockEnd(cls):
        """ Return a command packet for the "loop block end" command with the
        given parameters.
        """
        pkt = [0x02, cls.CMD_LOOP_BLOCK_END, 0, 0, 0, 0, 0, 0, 0]
        return pkt

    @classmethod
    def makeCmdSetSpeed(cls, speed):
        """ Return a command packet for the "set speed" command with the
        given parameters.
        """
        pkt = [0x02, cls.CMD_SET_SPEED, 0, 0, 0, 0, 0, 0, 0]
        pkt[2:4] = [(speed & 0xff00) >> 8, speed & 0xff]
        return pkt

    @classmethod
    def makeCmdTransmitExecute(cls):
        """ Return a command packet for the "transmit execute" command with the
        given parameters.
        """
        pkt = [0x02, cls.CMD_TRANSMIT_EXECUTE, 0, 0, 0, 0, 0, 0, 0]
        return pkt

    @classmethod
    def makeCmdSaveNext(cls, state):
        """ Return a command packet for the "save next" command with the
        given parameters.
        """
        pkt = [0x02, cls.CMD_SAVE_NEXT, 0, 0, 0, 0, 0, 0, 0]
        pkt[2] = state & 0xff
        return pkt

    @classmethod
    def makeCmdSave(cls):
        """ Return a command packet for the "save" command with the
        given parameters.
        """
        pkt = [0x02, cls.CMD_SAVE, 0, 0, 0, 0, 0, 0, 0]
        return pkt
