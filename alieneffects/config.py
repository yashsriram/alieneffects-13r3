import json
import os


class AlienwareConfig:
    class Keys:
        THEMES_DIRECTORY = 'THEMES_DIRECTORY'

    def __init__(self, path=os.path.join(os.path.expanduser('~' + os.getenv('SUDO_USER')), '.alieneffects-13r3.json')):
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
