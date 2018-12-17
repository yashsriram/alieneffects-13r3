from theme import AlienwareTheme
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

theme = AlienwareTheme("themes/moon.json")
theme.apply()
