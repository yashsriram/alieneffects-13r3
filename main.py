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

    color = [0xF, 0xF, 0x0]

    cmds = [
        controller.cmdPacket.makeCmdSetColour(1, 0x0021, color),
        controller.cmdPacket.makeCmdLoopBlockEnd(),
        controller.cmdPacket.makeCmdTransmitExecute(),
    ]
    # send commands
    controller.sendCommands(cmds)

except Exception as e:
    print(e)
finally:
    controller.driver.release()
