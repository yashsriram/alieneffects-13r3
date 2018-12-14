import apis
from controller import AlienwareController

# apis.setAlienheadBacklight([0, 255, 0])
# apis.setKeyboardBacklight([0, 0, 255])
# apis.setTouchpadBacklight((0, 0, 255))
# apis.setAlienwareLogoBacklight([255, 0, 255], )
# apis.turnOffEverything()
# apis.setAlienheadBacklight(AlienwareController.EFFECT_MORPH_COLOR, (0, 255, 255), speed=500, color2=(255, 0, 0))
# apis.setAlienwareLogoBacklight(AlienwareController.EFFECT_MORPH_COLOR, (0, 255, 0), speed=300, color2=(255, 0, 0))
# apis.setTouchpadBacklight(AlienwareController.EFFECT_MORPH_COLOR, (0, 255, 255), speed=400, color2=(255, 0, 0))
apis.setKeyboardBacklight(AlienwareController.EFFECT_BLINK_COLOR, (0, 255, 255), speed=400, color2=(255, 0, 0))
