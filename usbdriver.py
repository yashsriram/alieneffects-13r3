import logging

import usb
from usb import USBError


class AlienwareUSBDriver(object):
    """Provides low level acquire-release, read-write access to an USB controller"""

    OUT_BM_REQUEST_TYPE = 0x21
    OUT_B_REQUEST = 0x09  # bRequest = Set Configuration
    OUT_W_VALUE = 0x202  # configuration
    OUT_W_INDEX = 0x0  # must be 0 as per USB

    IN_BM_REQUEST_TYPE = 0xa1
    IN_B_REQUEST = 0x01  # bRequest = Clear Feature
    IN_W_VALUE = 0x101
    IN_W_INDEX = 0x0

    def __init__(self, vendorId, productId, packetLength):
        self._vendorId = vendorId
        self._productId = productId
        self._packetLength = packetLength
        self._control_taken = False
        self._device = None

    def acquire(self):
        """ Acquire control from libusb of the AlienFX controller."""
        if self._control_taken:
            return
        self._device = usb.core.find(idVendor=self._vendorId, idProduct=self._productId)

        if self._device is None:
            msg = "ERROR: No AlienFX USB controller found; tried "
            msg += "VID {}".format(self._vendorId)
            msg += ", PID {}".format(self._productId)
            logging.error(msg)

        try:
            self._device.detach_kernel_driver(0)
        except USBError as exc:
            logging.error(
                "Cant detach kernel driver. Error : {}".format(exc.strerror))

        try:
            self._device.set_configuration()
        except USBError as exc:
            logging.error(
                "Cant set configuration. Error : {}".format(exc.strerror))

        try:
            usb.util.claim_interface(self._device, 0)
        except USBError as exc:
            logging.error(
                "Cant claim interface. Error : {}".format(exc.strerror))

        self._control_taken = True
        logging.debug("USB device acquired, VID={}, PID={}".format(hex(self._vendorId), hex(self._productId)))

    def release(self):
        """ Release control to libusb of the AlienFX controller."""
        if not self._control_taken:
            return

        try:
            usb.util.release_interface(self._device, 0)
        except USBError as exc:
            logging.error(
                "Cant release interface. Error : {}".format(exc.strerror))

        try:
            self._device.attach_kernel_driver(0)
        except USBError as exc:
            logging.error("Cant re-attach. Error : {}".format(exc.strerror))

        self._control_taken = False
        logging.debug("USB device released, VID={}, PID={}".format(hex(self._vendorId), hex(self._productId)))

    def writePacket(self, pkt):
        """ Write the given packet over USB"""
        if not self._control_taken:
            return

        try:
            numBytesSent = self._device.ctrl_transfer(
                self.OUT_BM_REQUEST_TYPE,
                self.OUT_B_REQUEST, self.OUT_W_VALUE,
                self.OUT_W_INDEX, pkt, 0)
            logging.debug("number of bytes sent: {}".format(numBytesSent))
            if len(pkt) != numBytesSent:
                logging.error("writePacket: intended to send {} of {} bytes but sent {} bytes"
                              .format(pkt, len(pkt), numBytesSent))
        except USBError as exc:
            logging.error("writePacket: {}".format(exc))

    def readPacket(self):
        """ Read a packet over USB return it"""
        if not self._control_taken:
            logging.error("readPacket: control not taken...")
            return

        try:
            pkt = self._device.ctrl_transfer(
                self.IN_BM_REQUEST_TYPE,
                self.IN_B_REQUEST, self.IN_W_VALUE,
                self.IN_W_INDEX, self._packetLength, 0)
            logging.debug("read: {}".format(pkt))
            return pkt
        except USBError as exc:
            logging.error("read_packet: {}".format(exc))
