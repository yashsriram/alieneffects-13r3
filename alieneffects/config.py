import json
import os
from alieneffects.constants import CONFIG_FILE_DEFAULT_PATH


class AlienwareConfig:
    class Keys:
        THEMES_DIRECTORY = 'THEMES_DIRECTORY'

    def __init__(self, path=CONFIG_FILE_DEFAULT_PATH):
        self.config = {
            self.Keys.THEMES_DIRECTORY: os.path.expanduser('~'),
        }
        # Read themes directory from config file, if it exists
        try:
            with open(path) as configFile:
                userConfig = json.loads(''.join(configFile.readlines()))
                self.config[self.Keys.THEMES_DIRECTORY] = userConfig[self.Keys.THEMES_DIRECTORY]
        except:
            pass

    def __getitem__(self, item):
        return self.config[item]
