import controller
import logging

logging.basicConfig(level=logging.DEBUG)
controller = controller.AlienwareController()
try:
    # Make controller ready
    controller.driver.acquire()

    # controller.getStatus()
    controller.reset('all-lights-off')
    controller.waitUntilControllerReady()

    color1 = [0, 0, 255]
    color2 = [0, 0, 0]

    cmds = [
        controller.cmdPacket.makeCmdSetColour(1, 0x0080, color1),
        controller.cmdPacket.makeCmdLoopBlockEnd(),
        controller.cmdPacket.makeCmdTransmitExecute(),
    ]
    # send commands
    controller.sendCommands(cmds)

except Exception as e:
    print(e)
finally:
    controller.driver.release()
