import control
import logging

logging.basicConfig(level=logging.DEBUG)
controller = control.AlienwareController()
try:
    # Make controller ready
    controller.driver.acquire()

    controller.ping()
    controller.reset('all-lights-on')
    controller.waitControllerReady()

    color = [0x1, 0x0, 0x1]

    cmds = [
        # controller.cmdPacket.make_cmd_set_speed(500),
        # controller.cmdPacket.make_cmd_set_colour(1, control.AlienwareController.LEFT_KEYBOARD, color),
        # controller.cmdPacket.make_cmd_set_colour(1, control.AlienwareController.MIDDLE_LEFT_KEYBOARD, color),
        # controller.cmdPacket.make_cmd_set_colour(1, control.AlienwareController.MIDDLE_RIGHT_KEYBOARD, color),
        # controller.cmdPacket.make_cmd_set_colour(1, control.AlienwareController.RIGHT_KEYBOARD, color),
        # controller.cmdPacket.make_cmd_set_colour(1, control.AlienwareController.ALIEN_HEAD, color),
        # controller.cmdPacket.make_cmd_set_colour(1, control.AlienwareController.LOGO, color),
        controller.cmdPacket.make_cmd_set_colour(1, 0x0080, color),
        controller.cmdPacket.make_cmd_loop_block_end(),
        controller.cmdPacket.make_cmd_transmit_execute(),
    ]
    # send commands
    controller.sendCommands(cmds)

except Exception as e:
    print(e)
finally:
    controller.driver.release()
