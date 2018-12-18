import logging
import os

import npyscreen as nps

from theme import AlienwareTheme


class ThemeDetailView(nps.GridColTitles):
    def custom_print_cell(self, actual_cell, cell_display_value):
        pass


class BoxedTitleFileName(nps.BoxTitle):
    _contained_widget = nps.FilenameCombo


class BoxedSelectOne(nps.BoxTitle):
    _contained_widget = nps.SelectOne

    def when_cursor_moved(self):
        self.parent.browse_theme_callback(self.entry_widget.values[self.entry_widget.cursor_line])


# noinspection PyAttributeOutsideInit
class ThemeMasterDetailView(nps.Form):

    def create(self):
        new_handlers = {
            'q': self.exit_application,
        }
        self.add_handlers(new_handlers)

        usableY, usableX = self.useable_space()
        self.directoryField = self.add(BoxedTitleFileName,
                                       name='Themes directory',
                                       width=int(usableX * 0.4),
                                       value='/home/pandu/alienfx-13r3/themes',
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
        self.detailField = self.add(ThemeDetailView,
                                    name='Theme detail',
                                    relx=int(usableX * 0.5),
                                    rely=1,
                                    values=[],
                                    editable=False)
        # todo remove
        self.logField = self.add(nps.TitleFixedText,
                                 name='log',
                                 value='log will come here',
                                 editable=False,
                                 relx=int(usableX * 0.5),
                                 rely=1)

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

    def browse_theme_callback(self, themeFilename):
        directoryPath = self.directoryField.value
        try:
            themeFilePath = os.path.join(directoryPath, themeFilename)
            theme = AlienwareTheme(themeFilePath)
            validatedTempo, validatedDuration, validatedZoneCodeSequenceMap = theme.validate()
            self.set_detailed_field(validatedTempo, validatedDuration, validatedZoneCodeSequenceMap)
        except Exception as e:
            logging.error(
                'Exception occurred while opening theme "{}" in "{}" directory'.format(themeFilename, directoryPath))
            logging.error('Description {}'.format(e))

    def set_detailed_field(self, tempo, duration, sequences):
        self.detailField.values = [
            ['Tempo = {}ms'.format(tempo)],
            ['Duration = {}ms'.format(duration)],
            ['Sequences = {}'.format(sequences)]
        ]
        self.detailField.display()

    def debug_log(self, msg):
        self.logField.value = msg
        self.logField.display()

    @staticmethod
    def exit_application(keyCode):
        exit(0)


class AlienwareTUI(nps.StandardApp):
    def onStart(self):
        nps.setTheme(nps.Themes.ElegantTheme)
        self.addForm(
            'MAIN',
            ThemeMasterDetailView,
            name='Alien effects',
        )
