"""
Mon fichier pour le projet 
"""

from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview

from PyQt5.QtWidgets import QFileDialog, QMessageBox


from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler,
    InfoBox, SendButton, AdvancedSettings,
)

class AudioFile(OWTextableBaseWidget):
    

    name = "AudioFile"
    description = "Import audio files transcribe them and segment them"
    icon = "icons/mywidget.svg"
    priority = 20

    inputs =[]
    outputs = [('Text', Segmentation)] 


    want_main_area = False
    resizing_enabled = True

    displayAdvancedSettings = settings.Setting(False)

    def __init__(self):
        super().__init__()
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute='infoBox',
            #sendIfPreCallback=self.updateGUI,
        )
        self.advancedSettings = AdvancedSettings(
            widget=self.controlArea,
            master=self,
            callback=self.sendButton.settingsChanged,
        )

        # GUI EL DISAGNO 

        self.advancedSettings.draw()

        # Basic file box
        basicFileBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Source',
            orientation='vertical',
            addSpace=False,
        )
        basicFileBoxLine1 = gui.widgetBox(
            widget=basicFileBox,
            box=False,
            orientation='horizontal',
        )
        gui.lineEdit(
            widget=basicFileBoxLine1,
            master=self,
            value='file',
            orientation='horizontal',
            label=u'File path:',
            labelWidth=101,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The path of the file."
            ),
        )
        gui.separator(widget=basicFileBoxLine1, width=5)
        gui.button(
            widget=basicFileBoxLine1,
            master=self,
            label=u'Browse',
            callback=self.browse,
            tooltip=(
                u"Open a dialog for selecting file."
            ),
        )

        gui.separator(widget=basicFileBox, width=3)
        self.advancedSettings.basicWidgets.append(basicFileBox)
        self.advancedSettings.basicWidgetsAppendSeparator()
        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.adjustSizeWithTimer()
        QTimer.singleShot(0, self.sendButton.sendIf)

    def sendData(self):
            
        if (
            (self.displayAdvancedSettings and not self.files) or
            not (self.file or self.displayAdvancedSettings)
        ):
            self.infoBox.setText(u'Please select input file.', 'warning')
            self.send('Text data', None, self)
            return 

    def browse(self):
        if self.displayAdvancedSettings:
            filePathList, _ = QFileDialog.getOpenFileNames(
                self,
                u'Select Text File(s)',
                self.lastLocation,
                u'Text files (*)'
            )
            if not filePathList:
                return
            filePathList = [os.path.normpath(f) for f in filePathList]
            self.newFiles = u' / '.join(filePathList)
            self.lastLocation = os.path.dirname(filePathList[-1])
        else:
            filePath, _ = QFileDialog.getOpenFileName(
                self,
                u'Open Text File',
                self.lastLocation,
                u'Text files (*)'
            )
            if not filePath:
                return
            self.file = os.path.normpath(filePath)
            self.lastLocation = os.path.dirname(filePath)
            self.sendButton.settingsChanged()

            


if __name__ == '__main__':
    WidgetPreview(AudioFile)
