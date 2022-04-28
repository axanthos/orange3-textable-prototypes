"""
Mon fichier pour le projet 
"""
import os 
from Orange.widgets import widget, gui, settings
from Orange.widgets.settings import Setting
from Orange.widgets.utils.widgetpreview import WidgetPreview

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from LTTL.Segmentation import Segmentation
from LTTL.Input import Input


from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler,
    InfoBox, SendButton, AdvancedSettings, ProgressBar
)

import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import filetype 
import tempfile

class AudioFile(OWTextableBaseWidget):
    

    name = "AudioFile_Rebecca"
    description = "Import audio files transcribe them and segment them"
    icon = "icons/audioFile.png"
    priority = 20

    inputs =[]
    outputs = [('Text', Segmentation)] 


    #selected_int = Setting(50)
    language = settings.Setting('fr-FR')
    want_main_area = False
    resizing_enabled = True

    displayAdvancedSettings = settings.Setting(False)
    file = settings.Setting(u'')
    selected_int = Setting(0)
    lastLocation = settings.Setting('.')
    selected_vol = settings.Setting(14)
    selected_dur = settings.Setting(500)
  
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

        # Initiates output segmentation
        self.segmentation = Input(text=u'')

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
                "fr-FR",
                "en-US",
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
            label='Maximum Volume (in dBFS): ',
            callback=self.sendButton.settingsChanged,
            tooltip='Select a value between 1 and 50',
            minv=1,                     
            maxv=50,                   
            step=1,
        )

        gui.spin(
            widget=OptionsBox,
            master=self, 
            value='selected_dur',
            label='Minimum Duration (in milliseconds): ',
            callback=self.sendButton.settingsChanged,
            tooltip='Select a value between 1 and 1000',
            minv=1,
            maxv=1000,
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

    def get_large_audio_transcription(self, path, set_silence_len=500, set_silence_threshold=14, language="en-US"):
        """
        Splitting the large audio file into chunks
        and apply speech recognition on each of these chunks
        """
        r = sr.Recognizer()
        # Check type of the audio file and change it to wav if mp3
        audio_type = self.detect_format(path)

        if audio_type == "mp3":
            path = self.to_wav(path)

        # open the audio file using pydub
        sound = AudioSegment.from_wav(path)
        # split audio sound where silence is 700 milliseconds or more and get chunks
        chunks = split_on_silence(sound,
                                  # experiment with this value for your target audio file
                                  min_silence_len=set_silence_len,
                                  # adjust this per requirement
                                  silence_thresh=sound.dBFS - set_silence_threshold,
                                  # keep the silence for 1 second, adjustable as well
                                  keep_silence=500,
                                  )

        whole_text = ""
        # create a temporary folder to handle the chunks, will be deleted upon completion of the task
        with tempfile.TemporaryDirectory() as tempDict:
            # process each chunk
            for i, audio_chunk in enumerate(chunks, start=1):
                # export audio chunk and save it in
                # the `folder_name` directory.
                chunk_filename = os.path.join(tempDict, f"chunk{i}.wav")
                audio_chunk.export(chunk_filename, format="wav")
                # recognize the chunk
                with sr.AudioFile(chunk_filename) as source:
                    audio_listened = r.record(source)
                    # try converting it to text
                    try:
                        text = r.recognize_google(audio_listened, language=language)
                    except sr.UnknownValueError as e:
                        print("Error:", str(e))
                    else:
                        text = f"{text.capitalize()}. "
                        print(chunk_filename, ":", text)
                        whole_text += text
        # return the text for all chunks detected
        return whole_text

    def sendData(self):
            
        if (
            (self.displayAdvancedSettings and not self.file) or
            not (self.file or self.displayAdvancedSettings)
        ):
            self.infoBox.setText(u'Please select input file.', 'warning')
            self.send('Text data', None, self)
            return 
        else:
            #Initiate alert message and progress bar
            self.infoBox.setText(u"Processing, please wait...", "warning")
            progressBar = ProgressBar(
            self,
            iterations=2
            )
            # gets transcription
            transcription = self.get_large_audio_transcription(self.file, set_silence_len=self.selected_dur, set_silence_threshold=self.selected_vol, language=self.language)
            #updates segmentation for output
            # TODO: regex that detects '\' before and '.wav' after for name
            self.segmentation.update(transcription, label=self.file)
            
            # Send token...
            self.send('Text', self.segmentation, self)
            message = "Succesfully transcripted!"
            self.infoBox.setText(message)
            self.sendButton.resetSettingsChangedFlag()
            progressBar.finish()

    def browse(self):
        audioPath, _ = QFileDialog.getOpenFileName(
            self,
            u'open Text File',
            self.lastLocation,
            u'Audio Files(*)'
        )
        if not audioPath:
            return
        self.file = os.path.normpath(audioPath)
        self.lastLocation = os.path.dirname(audioPath)
        self.sendButton.settingsChanged()

    def showAdvancedSettings(self):

        self.advancedSettings.setVisible(self.displayAdvancedSettings)

    def detect_format(self, file):
        """A function that detects the format of a file"""
        file_type = filetype.guess(file)
        return file_type.extension

    def to_wav(self, file):
        """A function to convert mp3 files to wav files"""

        # files
        source = file
        destination = file.replace(".mp3", ".wav")

        # convert wav to mp3
        sound = AudioSegment.from_mp3(source)
        sound.export(destination, format="wav")



if __name__ == '__main__':
    WidgetPreview(AudioFile).run()
    # import sys
    # from PyQt5.QtWidgets import QApplication
    # myApplication = QApplication(sys.argv)
    # myWidget = AudioFile()
    # myWidget.show()
    # myApplication.exec_()
    # myWidget.saveSettings()

