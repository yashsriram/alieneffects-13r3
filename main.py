import apis
from controller import AlienwareController
import logging

logging.basicConfig(level=logging.DEBUG)


# apis.setAlienheadBacklight(AlienwareController.EFFECT_MORPH_COLOR, (0, 255, 255), speed=500, color2=(255, 0, 0))
# apis.setAlienwareLogoBacklight(AlienwareController.EFFECT_MORPH_COLOR, (0, 255, 0), speed=300, color2=(255, 0, 0))
# apis.setTouchpadBacklight(AlienwareController.EFFECT_MORPH_COLOR, (0, 255, 255), speed=400, color2=(255, 0, 0))
# apis.setKeyboardBacklight(AlienwareController.EFFECT_BLINK_COLOR, (0, 255, 255), speed=400, color2=(255, 0, 0))
# apis.turnOffEverything()


def masterSet(color1=(255, 0, 255), speed=200, color2=(0, 255, 0)):
    controller = AlienwareController()
    try:

        if speed < AlienwareController.MIN_SPEED:
            raise RuntimeError('Too much speed')

        commands = [
            controller.cmdPacket.makeCmdSetSpeed(speed),
            controller.cmdPacket.makeCmdSetColour(0, 0x0070, (0, 255, 255)),
            controller.cmdPacket.makeCmdSetMorphColour(1, 0x0080, color1, color2),
            controller.cmdPacket.makeCmdLoopBlockEnd(),
            controller.cmdPacket.makeCmdLoopBlockEnd(),
            controller.cmdPacket.makeCmdSetSpeed(speed - 100),
            controller.cmdPacket.makeCmdSetMorphColour(1, 0x0080, color2, (255, 0, 0)),
            controller.cmdPacket.makeCmdLoopBlockEnd(),
            # controller.cmdPacket.makeCmdSetColour(1, 0x0080, (0, 0, 0)),
            controller.cmdPacket.makeCmdSetBlinkColour(2, 0x000f, color2),
        ]

        controller.driver.acquire()

        controller.reset(controller.RESET_ALL_LIGHTS_OFF)
        controller.waitUntilControllerReady()

        commands += [
            controller.cmdPacket.makeCmdLoopBlockEnd(),
            controller.cmdPacket.makeCmdTransmitExecute(),
        ]
        controller.sendCommands(commands)

        controller.waitUntilControllerReady()
    except Exception as e:
        logging.error('Exception occurred', exc_info=True)
    finally:
        controller.driver.release()


masterSet()
