import controller
import logging

logging.basicConfig(level=logging.DEBUG)
controller = controller.AlienwareController()
try:
    # Make controller ready
    controller.driver.acquire()

    controller.ping()
    controller.reset('all-lights-on')
    controller.waitControllerReady()

    color = [0x0, 0x0, 0x0]

    cmds = [
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
