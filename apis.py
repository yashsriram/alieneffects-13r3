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

        controller.reset(AC.Reset.CODES[AC.Reset.ALL_LIGHTS_OFF])
        controller.waitUntilControllerReady()
    except Exception as e:
        print(e)
    finally:
        controller.driver.release()


def setKeyboardBacklight(effect, color1, speed=200, color2=(0, 0, 0)):
    masterSet(AC.Zones.CODES[AC.Zones.LEFT_KEYBOARD]
              | AC.Zones.CODES[AC.Zones.MIDDLE_LEFT_KEYBOARD]
              | AC.Zones.CODES[AC.Zones.MIDDLE_RIGHT_KEYBOARD]
              | AC.Zones.CODES[AC.Zones.RIGHT_KEYBOARD], effect, color1, speed, color2)


def setTouchpadBacklight(effect, color1, speed=200, color2=(0, 0, 0)):
    masterSet(AC.Zones.CODES[AC.Zones.TOUCH_PAD], effect, color1, speed, color2)


def setAlienheadBacklight(effect, color1, speed=200, color2=(0, 0, 0)):
    masterSet(AC.Zones.CODES[AC.Zones.ALIEN_HEAD], effect, color1, speed, color2)


def setAlienwareLogoBacklight(effect, color1, speed=200, color2=(0, 0, 0)):
    masterSet(AC.Zones.CODES[AC.Zones.ALIENWARE_LOGO], effect, color1, speed, color2)


def masterSet(zonesCode, effect, color1, speed=200, color2=(0, 0, 0)):
    controller = AC()
    try:
        if effect == EFFECT_SET_COLOR:
            commands = [
                controller.makeSetColourCmd(1, zonesCode, color1),
                controller.makeLoopSequenceCmd(),
            ]
        elif effect == EFFECT_BLINK_COLOR:
            commands = [
                controller.makeSetTempoCmd(speed),
                controller.makeBlinkColourCmd(1, zonesCode, color1),
                controller.makeLoopSequenceCmd(),
            ]
        elif effect == EFFECT_MORPH_COLOR:
            commands = [
                controller.makeSetTempoCmd(speed),
                controller.makeMorphColourCmd(1, zonesCode, color1, color2),
                controller.makeLoopSequenceCmd(),
            ]
        else:
            raise RuntimeError('Invalid effect code')

        controller.driver.acquire()

        controller.reset(AC.Reset.CODES[AC.Reset.ALL_LIGHTS_ON])
        controller.waitUntilControllerReady()

        commands += [
            controller.makeExecuteCmd(),
        ]
        controller.sendCommands(commands)

        controller.waitUntilControllerReady()
    except Exception as e:
        logging.error('Exception occurred', exc_info=True)
    finally:
        controller.driver.release()
