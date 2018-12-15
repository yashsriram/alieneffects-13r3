from controller import AlienwareController as AC
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

# Effect codes
EFFECT_SET_COLOR = 1
EFFECT_BLINK_COLOR = 2
EFFECT_MORPH_COLOR = 3


def turnOffEverything():
    controller = AC()
    try:
        controller.driver.acquire()

        controller.reset(AC.RESET_TYPE_CODES[AC.RESET_ALL_LIGHTS_OFF])
        controller.waitUntilControllerReady()
    except Exception as e:
        print(e)
    finally:
        controller.driver.release()


def setKeyboardBacklight(effect, color1, speed=200, color2=(0, 0, 0)):
    masterSet(AC.ZONE_CODES[AC.LEFT_KEYBOARD]
              | AC.ZONE_CODES[AC.MIDDLE_LEFT_KEYBOARD]
              | AC.ZONE_CODES[AC.MIDDLE_RIGHT_KEYBOARD]
              | AC.ZONE_CODES[AC.RIGHT_KEYBOARD], effect, color1, speed, color2)


def setTouchpadBacklight(effect, color1, speed=200, color2=(0, 0, 0)):
    masterSet(AC.ZONE_CODES[AC.TOUCH_PAD], effect, color1, speed, color2)


def setAlienheadBacklight(effect, color1, speed=200, color2=(0, 0, 0)):
    masterSet(AC.ZONE_CODES[AC.ALIEN_HEAD], effect, color1, speed, color2)


def setAlienwareLogoBacklight(effect, color1, speed=200, color2=(0, 0, 0)):
    masterSet(AC.ZONE_CODES[AC.ALIENWARE_LOGO], effect, color1, speed, color2)


def masterSet(zonesCode, effect, color1, speed=200, color2=(0, 0, 0)):
    controller = AC()
    try:
        if zonesCode > 0xffff:
            raise RuntimeError('Invalid zones code')

        if speed < AC.MIN_TEMPO:
            raise RuntimeError('Too much speed')

        if effect == EFFECT_SET_COLOR:
            commands = [
                controller.cmdPktManager.makeSetColourCmd(1, zonesCode, color1),
                controller.cmdPktManager.makeLoopSequenceCmd(),
            ]
        elif effect == EFFECT_BLINK_COLOR:
            commands = [
                controller.cmdPktManager.makeSetTempoCmd(speed),
                controller.cmdPktManager.makeBlinkColourCmd(1, zonesCode, color1),
                controller.cmdPktManager.makeLoopSequenceCmd(),
            ]
        elif effect == EFFECT_MORPH_COLOR:
            commands = [
                controller.cmdPktManager.makeSetTempoCmd(speed),
                controller.cmdPktManager.makeMorphColourCmd(1, zonesCode, color1, color2),
                controller.cmdPktManager.makeLoopSequenceCmd(),
            ]
        else:
            raise RuntimeError('Invalid effect code')

        controller.driver.acquire()

        controller.reset(AC.RESET_TYPE_CODES[AC.RESET_ALL_LIGHTS_ON])
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
