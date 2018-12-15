import logging

import usb
from usb import USBError


class AlienwareUSBDriver:
    """Provides low level acquire, control transfer and release APIs"""

    VENDOR_ID = 0x187c
    PRODUCT_ID = 0x0529

    OUT_BM_REQUEST_TYPE = 0x21
    OUT_B_REQUEST = 0x09
    OUT_W_VALUE = 0x202
    OUT_W_INDEX = 0x0

    IN_BM_REQUEST_TYPE = 0xa1
    IN_B_REQUEST = 0x01
    IN_W_VALUE = 0x101
    IN_W_INDEX = 0x0

    PACKET_LENGTH = 12

    def __init__(self):
        self._control_taken = False
        self._device = None

    def acquire(self):
        """ Acquire control of the USB controller."""
        if self._control_taken:
            return

        self._device = usb.core.find(idVendor=AlienwareUSBDriver.VENDOR_ID, idProduct=AlienwareUSBDriver.PRODUCT_ID)

        if self._device is None:
            logging.error("ERROR: No AlienFX USB controller found; tried VID {}, PID {}"
                          .format(AlienwareUSBDriver.VENDOR_ID, AlienwareUSBDriver.PRODUCT_ID))

        try:
            self._device.detach_kernel_driver(0)
        except USBError as exc:
            logging.error("Cant detach kernel driver. Error : {}".format(exc.strerror))

        try:
            self._device.set_configuration()
        except USBError as exc:
            logging.error("Cant set configuration. Error : {}".format(exc.strerror))

        try:
            usb.util.claim_interface(self._device, 0)
        except USBError as exc:
            logging.error("Cant claim interface. Error : {}".format(exc.strerror))

        self._control_taken = True
        logging.debug("USB device acquired, VID={}, PID={}".format(hex(AlienwareUSBDriver.VENDOR_ID),
                                                                   hex(AlienwareUSBDriver.PRODUCT_ID)))

    def release(self):
        """ Release control of the USB controller."""
        if not self._control_taken:
            return

        try:
            usb.util.release_interface(self._device, 0)
        except USBError as exc:
            logging.error("Cant release interface. Error : {}".format(exc.strerror))

        try:
            self._device.attach_kernel_driver(0)
        except USBError as exc:
            logging.error("Cant re-attach. Error : {}".format(exc.strerror))

        self._control_taken = False
        logging.debug("USB device released, VID={}, PID={}".format(hex(AlienwareUSBDriver.VENDOR_ID),
                                                                   hex(AlienwareUSBDriver.PRODUCT_ID)))

    def writePacket(self, pkt):
        """ Write the given packet over USB"""
        if not self._control_taken:
            return

        try:
            numBytesSent = self._device.ctrl_transfer(
                self.OUT_BM_REQUEST_TYPE, self.OUT_B_REQUEST,
                self.OUT_W_VALUE, self.OUT_W_INDEX,
                pkt, 0)

            logging.debug("wrote: {}, {} bytes".format(pkt, len(pkt)))
            if len(pkt) != numBytesSent:
                logging.error("writePacket: intended to write {} of {} bytes but wrote {} bytes"
                              .format(pkt, len(pkt), numBytesSent))

            return numBytesSent
        except USBError as exc:
            logging.error("writePacket: {}".format(exc))

    def readPacket(self):
        """ Read a packet over USB return it"""
        if not self._control_taken:
            logging.error("readPacket: control not taken...")
            return

        try:
            pkt = self._device.ctrl_transfer(
                self.IN_BM_REQUEST_TYPE, self.IN_B_REQUEST,
                self.IN_W_VALUE, self.IN_W_INDEX,
                AlienwareUSBDriver.PACKET_LENGTH, 0)

            logging.debug("read: {}, {} bytes".format(pkt, len(pkt)))
            if len(pkt) != AlienwareUSBDriver.PACKET_LENGTH:
                logging.error("readPacket: intended to read {} of {} bytes but read {} bytes"
                              .format(pkt, AlienwareUSBDriver.PACKET_LENGTH, len(pkt)))

            return pkt
        except USBError as exc:
            logging.error("read_packet: {}".format(exc))
