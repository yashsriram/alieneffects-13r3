import logging

import usb
from usb import USBError


class AlienwareUSBDriver(object):
    """ Provides low level acquire/release and read/write access to an AlienFX
    USB controller.
    """

    OUT_BM_REQUEST_TYPE = 0x21
    OUT_B_REQUEST = 0x09  # bRequest = Set Configuration
    OUT_W_VALUE = 0x202  # configuration
    OUT_W_INDEX = 0x0  # must be 0 as per USB

    IN_BM_REQUEST_TYPE = 0xa1
    IN_B_REQUEST = 0x01  # bRequest = Clear Feature
    IN_W_VALUE = 0x101
    IN_W_INDEX = 0x0

    def __init__(self, controller):
        self._control_taken = False
        self._controller = controller
        self._device = None

    def write_packet(self, pkt):
        """ Write the given packet over USB to the AlienFX controller."""
        if not self._control_taken:
            return
        try:
            self._device.ctrl_transfer(
                self.OUT_BM_REQUEST_TYPE,
                self.OUT_B_REQUEST, self.OUT_W_VALUE,
                self.OUT_W_INDEX, pkt, 0)
        except USBError as exc:
            logging.error("write_packet: {}".format(exc))

    def read_packet(self):
        """ Read a packet over USB from the AlienFX controller and return it."""
        if not self._control_taken:
            logging.error("read_packet: control not taken...")
            return
        try:
            pkt = self._device.ctrl_transfer(
                self.IN_BM_REQUEST_TYPE,
                self.IN_B_REQUEST, self.IN_W_VALUE,
                self.IN_W_INDEX, self._controller.cmdPacket.PACKET_LENGTH, 0)
            return pkt
        except USBError as exc:
            logging.error("read_packet: {}".format(exc))

    def acquire(self):
        """ Acquire control from libusb of the AlienFX controller."""
        if self._control_taken:
            return
        self._device = usb.core.find(
            idVendor=self._controller.vendorId,
            idProduct=self._controller.productId)
        if self._device is None:
            msg = "ERROR: No AlienFX USB controller found; tried "
            msg += "VID {}".format(self._controller.vendorId)
            msg += ", PID {}".format(self._controller.productId)
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
        logging.debug("USB device acquired, VID={}, PID={}".format(
            hex(self._controller.vendorId), hex(self._controller.productId)))

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
        logging.debug("USB device released, VID={}, PID={}".format(
            hex(self._controller.vendorId), hex(self._controller.productId)))
