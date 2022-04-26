"""
Mon fichier pour le projet 
"""
import os 
from Orange.widgets import widget, gui, settings
from Orange.widgets.settings import Setting
from Orange.widgets.utils.widgetpreview import WidgetPreview

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from LTTL.Segmentation import Segmentation


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


    #selected_int = Setting(50)
    language = settings.Setting(0)
    want_main_area = False
    resizing_enabled = True

    displayAdvancedSettings = settings.Setting(False)
    file = settings.Setting(u'')
    selected_int = Setting(0)
    lastLocation = settings.Setting('.')
    selected_vol = settings.Setting(50)
    selected_dur = settings.Setting(50)
  
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
            callback=self.showAdvancedSettings,
        )


        self.advancedSettings.draw()

        # Basic file box
        basicFileBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'File selection',
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
        languageComboBox = gui.comboBox(
            widget=basicFileBox,
            master=self,
            value="language",
            items=[
                "French",
                "English",
            ],
            sendSelectedValue=True,
            orientation=u"horizontal",
            label="Input language:",
            labelWidth=101,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Select the language of the input text."
            ),
        )
        gui.separator(widget=basicFileBoxLine1, width=3)
        gui.button(
            widget=basicFileBoxLine1,
            master=self,
            label=u'Browse',
            callback=self.browse,
            tooltip=(
                u"Open a dialog for selecting file."
            ),
        )

        OptionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Segmentation at pauses',
            orientation='vertical',
            addSpace=False,
        )

        OptionBoxLine1 = gui.widgetBox(
            widget=OptionsBox,
            box=False,
            orientation='horizontal',
        )
        gui.spin(
            widget=OptionsBox,  
            master=self,                
            value='selected_vol',       
            label='Maximum Volume: ',
            callback=self.sendButton.settingsChanged,
            tooltip='Select a value between 1 and 100',
            minv=1,                     
            maxv=100,                   
            step=1,
        )

        gui.spin(
            widget=OptionsBox,
            master=self, 
            value='selected_dur',
            label='Minimum Duration: ',
            callback=self.sendButton.settingsChanged,
            tooltip='Select a value between 1 and 100',
            minv=1,
            maxv=100,
            step=1,
        )

        gui.separator(widget=OptionsBox, width=3)
        self.advancedSettings.advancedWidgets.append(OptionsBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        gui.rubber(self.controlArea)
        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.advancedSettings.setVisible(self.displayAdvancedSettings)

    # def int_changed(self):
    #     """Send the entered number on "Number" output"""
    #     self.send("Integer", self.selected_int)

    def sendData(self):
            
        if (
            (self.displayAdvancedSettings and not self.files) or
            not (self.file or self.displayAdvancedSettings)
        ):
            self.infoBox.setText(u'Please select input file.', 'warning')
            self.send('Text data', None, self)
            return 

    def browse(self):
        audioPath = QFileDialog.getOpenFileName(
            self,
            u'open Text File',
            self.lastLocation,
            u'Audio Files(*)')
        self.file = os.path.normpath(audioPath)
        self.lastLocation = os.path.dirname(audioPath)
        self.updateGUI()
        self.sendButton.settingsChanged()

    def showAdvancedSettings(self):

        self.advancedSettings.setVisible(self.displayAdvancedSettings)


if __name__ == '__main__':
    WidgetPreview(AudioFile).run()
    # import sys
    # from PyQt5.QtWidgets import QApplication
    # myApplication = QApplication(sys.argv)
    # myWidget = AudioFile()
    # myWidget.show()
    # myApplication.exec_()
    # myWidget.saveSettings()

