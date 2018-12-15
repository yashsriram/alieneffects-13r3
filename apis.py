from controller import AlienwareController
import logging

logging.basicConfig(level=logging.DEBUG)


def turnOffEverything():
    controller = AlienwareController()
    try:
        controller.driver.acquire()

        controller.reset(controller.RESET_ALL_LIGHTS_OFF)
        controller.waitUntilControllerReady()
    except Exception as e:
        print(e)
    finally:
        controller.driver.release()


def setKeyboardBacklight(effect, color1, speed=200, color2=(0, 0, 0)):
    masterSet(AlienwareController.LEFT_KEYBOARD
              | AlienwareController.MIDDLE_LEFT_KEYBOARD
              | AlienwareController.MIDDLE_RIGHT_KEYBOARD
              | AlienwareController.RIGHT_KEYBOARD, effect, color1, speed, color2)


def setTouchpadBacklight(effect, color1, speed=200, color2=(0, 0, 0)):
    masterSet(AlienwareController.TOUCH_PAD, effect, color1, speed, color2)


def setAlienheadBacklight(effect, color1, speed=200, color2=(0, 0, 0)):
    masterSet(AlienwareController.ALIEN_HEAD, effect, color1, speed, color2)


def setAlienwareLogoBacklight(effect, color1, speed=200, color2=(0, 0, 0)):
    masterSet(AlienwareController.ALIENWARE_LOGO, effect, color1, speed, color2)


def masterSet(zonesCode, effect, color1, speed=200, color2=(0, 0, 0)):
    controller = AlienwareController()
    try:
        if zonesCode > 0xffff:
            raise RuntimeError('Invalid zones code')

        if speed < AlienwareController.MIN_SPEED:
            raise RuntimeError('Too much speed')

        if effect == AlienwareController.EFFECT_SET_COLOR:
            commands = [
                controller.cmdPktManager.makeSetColourCmd(1, zonesCode, color1),
                controller.cmdPktManager.makeLoopSequenceCmd(),
            ]
        elif effect == AlienwareController.EFFECT_BLINK_COLOR:
            commands = [
                controller.cmdPktManager.makeSetTempoCmd(speed),
                controller.cmdPktManager.makeBlinkColourCmd(1, zonesCode, color1),
                controller.cmdPktManager.makeLoopSequenceCmd(),
            ]
        elif effect == AlienwareController.EFFECT_MORPH_COLOR:
            commands = [
                controller.cmdPktManager.makeSetTempoCmd(speed),
                controller.cmdPktManager.makeMorphColourCmd(1, zonesCode, color1, color2),
                controller.cmdPktManager.makeLoopSequenceCmd(),
            ]
        else:
            raise RuntimeError('Invalid effect code')

        controller.driver.acquire()

        controller.reset(controller.RESET_ALL_LIGHTS_ON)
        controller.waitUntilControllerReady()

        commands += [
            controller.cmdPktManager.makeExecuteCmd(),
        ]
        controller.sendCommands(commands)

        controller.waitUntilControllerReady()
    except Exception as e:
        logging.error('Exception occurred', exc_info=True)
    finally:
        controller.driver.release()
