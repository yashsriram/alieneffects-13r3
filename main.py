import apis
from controller import AlienwareController
import logging

logging.basicConfig(level=logging.DEBUG)

# apis.setAlienheadBacklight(AlienwareController.EFFECT_MORPH_COLOR, (0, 255, 255), speed=500, color2=(255, 0, 0))
# apis.setAlienwareLogoBacklight(AlienwareController.EFFECT_MORPH_COLOR, (0, 255, 0), speed=300, color2=(255, 0, 0))
apis.setTouchpadBacklight(AlienwareController.EFFECT_SET_COLOR, (0, 0, 0), speed=400, color2=(255, 0, 0))
apis.setKeyboardBacklight(AlienwareController.EFFECT_MORPH_COLOR, (0, 255, 255), speed=400, color2=(255, 0, 0))

# controller = AlienwareController()
# try:
#     commands = [
#         controller.cmdPacket.makeCmdSetSpeed(200),
#         controller.cmdPacket.makeCmdSetColour(0, 0x00FF, (0, 255, 0)),
#         controller.cmdPacket.makeCmdLoopBlockEnd(),
#     ]
#
#     controller.driver.acquire()
#
#     controller.reset(controller.RESET_ALL_LIGHTS_ON)
#     controller.waitUntilControllerReady()
#
#     commands += [
#         controller.cmdPacket.makeCmdTransmitExecute(),
#     ]
#     controller.sendCommands(commands)
#
#     controller.waitUntilControllerReady()
# except Exception as e:
#     logging.error('Exception occurred', exc_info=True)
# finally:
#     controller.driver.release()

# apis.turnOffEverything()
