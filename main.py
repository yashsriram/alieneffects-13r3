import apis
import logging
from controller import AlienwareController

logging.basicConfig(level=logging.DEBUG)
# apis.setAlienheadBacklight([0, 255, 0])
# apis.setKeyboardBacklight([0, 0, 255])
# apis.setTouchpadBacklight((0, 0, 255))
# apis.setAlienwareLogoBacklight([255, 0, 255], )
# apis.turnOffEverything()
apis.setAlienwareLogoBacklight(AlienwareController.EFFECT_BLINK_COLOR, (0, 255, 0), color2=(255, 0, 0))
