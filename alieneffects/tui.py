import curses
import logging
import os

import npyscreen as nps

from alieneffects.config import AlienwareConfig
from alieneffects.controller import AlienwareController as AC
from alieneffects.theme import AlienwareTheme


class BoxedTitleFileName(nps.BoxTitle):
    _contained_widget = nps.FilenameCombo


class SelectOneManyTimes(nps.SelectOne):
    def handle_input(self, _input):
        retvalue = super().handle_input(_input)
        if _input == curses.ascii.NL:
            self.parent.apply_theme_callback()
        return retvalue


class BoxedSelectOne(nps.BoxTitle):
    _contained_widget = SelectOneManyTimes

    def when_cursor_moved(self):
        self.parent.browse_theme_callback(self.entry_widget.values[self.entry_widget.cursor_line])


class ThemeDetailView(nps.MultiLine):
    def display_value(self, val):
        # todo override this or do something else to improve theme detail view
        return val


class BoxedThemeDetailView(nps.BoxTitle):
    _contained_widget = ThemeDetailView


# noinspection PyAttributeOutsideInit
class ThemeMasterDetailView(nps.Form):

    def create(self):
        new_handlers = {
            'q': self.exit_application,
        }
        self.add_handlers(new_handlers)

        usableY, usableX = self.useable_space()

        config = AlienwareConfig()
        self.directoryField = self.add(BoxedTitleFileName,
                                       name='Themes directory',
                                       rely=1,
                                       width=int(usableX * 0.4),
                                       value=config[config.Keys.THEMES_DIRECTORY],
                                       contained_widget_arguments={
                                           'value_changed_callback': self.change_dir_callback
                                       })
        self.listField = self.add(BoxedSelectOne,
                                  name='List of themes in directory',
                                  rely=5,
                                  width=int(usableX * 0.4),
                                  contained_widget_arguments={
                                      'scroll_exit': True,
                                      'value_changed_callback': self.apply_theme_callback,
                                      'check_cursor_move': True
                                  })
        self.detailField = self.add(BoxedThemeDetailView,
                                    name='Theme detail',
                                    relx=int(usableX * 0.5),
                                    rely=1,
                                    values=[])

    def activate(self):
        self.edit()
        self.parentApp.setNextForm(None)

    def change_dir_callback(self, **kwargs):
        themesDirectory = self.directoryField.value
        themes = []
        if os.path.isdir(themesDirectory):
            with os.scandir(themesDirectory) as entries:
                for entry in entries:
                    if entry.is_file():
                        themes.append(entry.name)
            self.listField.values = themes
        else:
            self.listField.values = ['** Not a directory **']

    def browse_theme_callback(self, themeFilename):
        directoryPath = self.directoryField.value
        try:
            themeFilePath = os.path.join(directoryPath, themeFilename)
            theme = AlienwareTheme(themeFilePath)
            desciption, tempo, duration, zoneCodeSequenceMap = theme.validate()
            self.show_theme_in_detailed_view(desciption, tempo, duration, zoneCodeSequenceMap)
        except Exception as e:
            logging.error(
                'Exception occurred while opening theme "{}" in "{}" directory'.format(themeFilename, directoryPath))
            logging.error('Description {}'.format(e))
            self.show_error_in_detailed_view('{} file doesn\'t seem to be a good theme file'.format(themeFilename))

    def apply_theme_callback(self, **kwargs):
        if len(self.listField.value) == 0:
            return
        directoryPath = self.directoryField.value
        themeFilename = self.listField.values[self.listField.value[0]]
        try:
            themeFilePath = os.path.join(directoryPath, themeFilename)
            theme = AlienwareTheme(themeFilePath)
            theme.apply()
        except Exception as e:
            logging.error(
                'Exception occurred while applying theme "{}" in "{}" directory'.format(themeFilename, directoryPath))
            logging.error('Description {}'.format(e))
            self.show_error_in_detailed_view('{} file doesn\'t seem to be a good theme file'.format(themeFilename))

    def show_error_in_detailed_view(self, message):
        self.detailField.values = [message]
        self.detailField.display()

    def show_theme_in_detailed_view(self, desciption, tempo, duration, sequences):
        sequenceDescriptions = []
        for zoneCode, sequence in sequences.items():
            zoneName = 'Unknown'
            for name, code in AC.Zones.CODES.items():
                if code == zoneCode:
                    zoneName = name
                    break
            sequenceDescriptions.append(zoneName)
            for effect in sequence:
                sequenceDescriptions.append('\t\t\t\t\t\t\t\t{}'.format(effect['EFFECT']))
            sequenceDescriptions.append('')

        self.detailField.values = ['Description = {}'.format(desciption),
                                   'Tempo = {}ms'.format(tempo),
                                   'Duration = {}ms'.format(duration),
                                   'Sequences'] + sequenceDescriptions
        self.detailField.display()

    @staticmethod
    def exit_application(keyCode):
        exit(0)


class CustomTheme(nps.npysThemes.TransparentThemeDarkText):
    default_colors = {
        'DEFAULT': 'YELLOW_ON_DEFAULT',
        'FORMDEFAULT': 'WHITE_ON_DEFAULT',
        'NO_EDIT': 'BLUE_ON_DEFAULT',
        'STANDOUT': 'CYAN_ON_DEFAULT',
        'CURSOR': 'WHITE_BLACK',
        'CURSOR_INVERSE': 'BLACK_WHITE',
        'LABEL': 'MAGENTA_ON_DEFAULT',
        'LABELBOLD': 'BLACK_ON_DEFAULT',
        'CONTROL': 'CYAN_ON_DEFAULT',
        'WARNING': 'RED_BLACK',
        'CRITICAL': 'BLACK_RED',
        'GOOD': 'GREEN_BLACK',
        'GOODHL': 'GREEN_BLACK',
        'VERYGOOD': 'BLACK_GREEN',
        'CAUTION': 'YELLOW_BLACK',
        'CAUTIONHL': 'BLACK_YELLOW',
    }


class AlienwareTUI(nps.StandardApp):
    def onStart(self):
        nps.setTheme(CustomTheme)
        self.addForm(
            'MAIN',
            ThemeMasterDetailView,
            name='Alien effects',
        )
