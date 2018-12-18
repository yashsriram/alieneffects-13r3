from theme import AlienwareTheme
import logging
import argparse

from tui import AlienwareTUI

logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%dth %H:%M:%S:')

# argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--THEME_FILE')
args = parser.parse_args()

if args.THEME_FILE:
    theme = AlienwareTheme(args.THEME_FILE)
    theme.apply()
else:
    # default behaviour is to open TUI
    AlienwareTUI().run()
