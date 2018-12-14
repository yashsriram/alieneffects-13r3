import apis
import logging

logging.basicConfig(level=logging.DEBUG)
apis.setAlienheadBacklight([0, 255, 0])
apis.setKeyboardBacklight([0, 0, 255])
apis.setTouchpadBacklight([0, 255, 0])
apis.setAlienwareLogoBacklight([255, 0, 255])
# apis.turnOffEverything()
