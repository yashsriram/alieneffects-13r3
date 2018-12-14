from controller import AlienwareController


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


def setKeyboardBacklight(color):
    controller = AlienwareController()
    try:
        controller.driver.acquire()

        controller.reset(controller.RESET_ALL_LIGHTS_ON)
        controller.waitUntilControllerReady()

        commands = [
            controller.cmdPacket.makeCmdSetColour(1,
                                                  AlienwareController.LEFT_KEYBOARD
                                                  | AlienwareController.MIDDLE_LEFT_KEYBOARD
                                                  | AlienwareController.MIDDLE_RIGHT_KEYBOARD
                                                  | AlienwareController.RIGHT_KEYBOARD
                                                  , color),
            controller.cmdPacket.makeCmdLoopBlockEnd(),
            controller.cmdPacket.makeCmdTransmitExecute(),
        ]
        controller.sendCommands(commands)

        controller.waitUntilControllerReady()
    except Exception as e:
        print(e)
    finally:
        controller.driver.release()


def setTouchpadBacklight(color):
    controller = AlienwareController()
    try:
        controller.driver.acquire()

        controller.reset(controller.RESET_ALL_LIGHTS_ON)
        controller.waitUntilControllerReady()

        commands = [
            controller.cmdPacket.makeCmdSetColour(1,
                                                  AlienwareController.TOUCH_PAD,
                                                  color),
            controller.cmdPacket.makeCmdLoopBlockEnd(),
            controller.cmdPacket.makeCmdTransmitExecute(),
        ]
        controller.sendCommands(commands)

        controller.waitUntilControllerReady()
    except Exception as e:
        print(e)
    finally:
        controller.driver.release()


def setAlienheadBacklight(color):
    controller = AlienwareController()
    try:
        controller.driver.acquire()

        controller.reset(controller.RESET_ALL_LIGHTS_ON)
        controller.waitUntilControllerReady()

        commands = [
            controller.cmdPacket.makeCmdSetColour(1,
                                                  AlienwareController.ALIEN_HEAD,
                                                  color),
            controller.cmdPacket.makeCmdLoopBlockEnd(),
            controller.cmdPacket.makeCmdTransmitExecute(),
        ]
        controller.sendCommands(commands)

        controller.waitUntilControllerReady()
    except Exception as e:
        print(e)
    finally:
        controller.driver.release()


def setAlienwareLogoBacklight(effect, color1, speed=200, color2=(0, 0, 0)):
    controller = AlienwareController()
    try:
        controller.driver.acquire()

        controller.reset(controller.RESET_ALL_LIGHTS_ON)
        controller.waitUntilControllerReady()

        if speed < AlienwareController.MIN_SPEED:
            raise RuntimeError('Too much speed')

        if effect == AlienwareController.EFFECT_SET_COLOR:
            commands = [controller.cmdPacket.makeCmdSetColour(1, AlienwareController.ALIENWARE_LOGO, color1)]
        elif effect == AlienwareController.EFFECT_BLINK_COLOR:
            commands = [
                controller.cmdPacket.makeCmdSetSpeed(speed),
                controller.cmdPacket.makeCmdSetBlinkColour(1, AlienwareController.ALIENWARE_LOGO, color1)
            ]
        elif effect == AlienwareController.EFFECT_MORPH_COLOR:
            commands = [
                controller.cmdPacket.makeCmdSetSpeed(speed),
                controller.cmdPacket.makeCmdSetMorphColour(1, AlienwareController.ALIENWARE_LOGO, color1, color2)
            ]
        else:
            raise RuntimeError('Invalid effect code')

        commands += [
            controller.cmdPacket.makeCmdLoopBlockEnd(),
            controller.cmdPacket.makeCmdTransmitExecute(),
        ]
        controller.sendCommands(commands)

        controller.waitUntilControllerReady()
    except Exception as e:
        print(e)
    finally:
        controller.driver.release()
