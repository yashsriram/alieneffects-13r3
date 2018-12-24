import logging
import os

# user who used sudo
SUDO_USER = os.getenv('SUDO_USER')
if SUDO_USER is None:
    print('You need to use sudo.')
    exit(-1)

# config file
CONFIG_FILE_DEFAULT_PATH = os.path.join(os.path.expanduser('~' + SUDO_USER), '.alieneffects-13r3.json')

# log file
USER_HOME = os.path.expanduser('~' + SUDO_USER)
LOG_FILE_PATH = os.path.join(USER_HOME, '.alieneffects-13r3.log')
logging.basicConfig(filename=LOG_FILE_PATH,
                    level=logging.ERROR,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%dth %H:%M:%S:')
