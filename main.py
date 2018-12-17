from theme import AlienwareTheme
import logging
import argparse

logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(levelname)s:%(message)s')

# arguments
parser = argparse.ArgumentParser()
# required args
parser.add_argument('--THEME_FILE', required=True)
args = parser.parse_args()

theme = AlienwareTheme(args.THEME_FILE)
theme.apply()
