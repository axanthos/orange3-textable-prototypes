"""
AUDIOFILE
"""
import os 
import subprocess
from Orange.widgets import widget, gui, settings
from Orange.widgets.settings import Setting
from Orange.widgets.utils.widgetpreview import WidgetPreview

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from LTTL.Segmentation import Segmentation
from LTTL.Input import Input
from LTTL.Segment import Segment 
import LTTL.Segmenter as Segmenter


from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, AdvancedSettings, ProgressBar
)

import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import filetype 
import tempfile
import re 

class AudioFile(OWTextableBaseWidget):
    
    # Widget info
    name = "AudioFile_rebecca"
    description = "Import an audio file, transcribe it and segment it"
    icon = "icons/audioFile.png"
    priority = 20

    inputs =[]
    outputs = [("Text data", Segmentation)] 

    outputs = [('Text data', Segmentation)] 

    # Settings
    language = settings.Setting("French")
    want_main_area = False
    resizing_enabled = True
    displayAdvancedSettings = settings.Setting(False)
    file = settings.Setting(u"")
    lastLocation = settings.Setting(".")
    #Advanced settings 
    selected_vol = settings.Setting(14)
    selected_dur = settings.Setting(500)
    selected_seg = settings.Setting(False)

    dict_languages = {
            "English":"en-US",
            "French": "fr-FR",
            "German": "de-DE",
            "Italian": "it-IT",
            "Japanese": "ja",
            "Mandarin Chinese": "zh-CN",
            "Portugese": "pt-PT",
            "Russian": "ru",
            "Spanish": "es-ES",
    }

    def __init__(self):
        super().__init__()
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute="infoBox",
            #sendIfPreCallback = self.updateGUI,
        )
        self.advancedSettings = AdvancedSettings(
            widget=self.controlArea,
            master=self,
            callback=self.showAdvancedSettings,
        )

        # Initiates output segmentation
        self.segmentation = Input(text=u"")
        self.createdInputs = list()

        self.advancedSettings.draw()

        # Basic file box
        basicFileBox = gui.widgetBox(
            widget=self.controlArea,
            box=u"File selection",
            orientation="vertical",
            addSpace=False,
        )
        basicFileBoxLine1 = gui.widgetBox(
            widget=basicFileBox,
            box=False,
            orientation="horizontal",
        )
        gui.lineEdit(
            widget=basicFileBoxLine1,
            master=self,
            value="file",
            orientation="horizontal",
            label=u"File path :",
            labelWidth=101,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The path of the file."
            ),
        )

        

        languageComboBox = gui.comboBox(
            widget=basicFileBox,
            master= self,
            value="language",
            # Displays the keys of the above dict of the multiple languages
            items=[(language) for language in AudioFile.dict_languages],
            sendSelectedValue=True,
            orientation=u"horizontal",
            label="Input language :",
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
            label=u"Browse",
            callback=self.browse,
            tooltip=(
                u"Open a dialog for selecting file."
            ),
        )

        OptionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u"Segmentation at pauses",
            orientation="vertical",
            addSpace=False,
        )

        OptionBoxLine1 = gui.widgetBox(
            widget=OptionsBox,
            box=False,
            orientation="horizontal",
        )
        gui.spin(
            widget=OptionsBox,  
            master=self,                
            value="selected_vol",       
            label="Maximum volume (in dBFS) : ",
            callback=self.sendButton.settingsChanged,
            tooltip="Select a value between 1 and 50",
            minv=1,
            maxv=50,
            step=1,
        )

        gui.spin(
            widget=OptionsBox,
            master=self, 
            value="selected_dur",
            label="Minimum duration (in milliseconds) : ",
            callback=self.sendButton.settingsChanged,
            tooltip="Select a value between 1 and 1000",
            minv=1,
            maxv=1000,
            step=1,
        )

        gui.checkBox(
            widget=OptionsBox,
            master=self,
            value="selected_seg",
            label="Segment the audio file with the parameters",
            box=None,
            callback=self.sendButton.settingsChanged,
            tooltip="Leave this box unchecked if you want one and only segment."
        )

        gui.separator(widget=OptionsBox, width=3)
        self.advancedSettings.advancedWidgets.append(OptionsBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()
        # Adding space between control area and send button
        gui.rubber(self.controlArea)
        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.advancedSettings.setVisible(self.displayAdvancedSettings)

    def get_large_audio_transcription(self, path, language, set_silence_len=500, set_silence_threshold=14):
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
                                  silence_thresh=sound.dBFS-set_silence_threshold,
                                  # keep the silence for 1 second, adjustable as well
                                  keep_silence=500,
                                  )
        # Initiates ouput variable
        whole_text = ""
        segments = list()
        #Initiate alert message and progress bar
        progressBar = ProgressBar(
                    self,
                    iterations=len(chunks)
        )

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
                        # A COMPLETER POUR LE CHOIX DE LA LANGUE
                        # Il faut aller chercher la valeur de la langue choisie dans le dictionnaire
                        text = r.recognize_google(audio_listened, language=AudioFile.dict_languages[self.language])
                    except sr.UnknownValueError as e:
                        print("Error : ", str(e))
                    else:
                        if self.selected_seg:
                            segmented_text = f"{text.capitalize()}. "
                            print(chunk_filename, " : ", segmented_text)
                            segments.append(segmented_text)
                        else:
                            text = f"{text.capitalize()}. "
                            print(chunk_filename, " : ", text)
                            whole_text += text
                        self.infoBox.setText(u"Processing, please wait...", "warning")
                        progressBar.advance()
        # return the text for all chunks detected
        progressBar.finish()
        if self.selected_seg:
            return segments
        else:
            return whole_text

    def sendData(self):
            
        if not self.file:
            self.infoBox.setText(u"Please select input file.", "warning")
            self.send('Text data', None, self)
            return 

        # Clear created Inputs.
        self.clearCreatedInputs()
        # gets transcription
        transcription = self.get_large_audio_transcription(self.file, language=self.language, set_silence_len=self.selected_dur, set_silence_threshold=self.selected_vol)
        
        # Regex to get the name of the input file
        title = self.file
        regex = re.compile("[^(/\\)]+[mp3|wav]$")
        match = re.findall(regex, title)

        if self.selected_seg:
            for chunk in transcription:
                new_input = Input(chunk, label=match)
                self.createdInputs.append(new_input)
        else:
            new_input = Input(transcription, label=match)
            self.createdInputs.append(new_input)
        # Concatenates the segmentations in the output segmentation
        self.segmentation = Segmenter.concatenate(segmentations=self.createdInputs, label=self.captionTitle, copy_annotations=False, import_labels_as="")
        
        #Sending segments length
        message = " Succesfully transcripted ! % i segment@p sent to output" % len(self.segmentation)
        message = pluralize(message, len(self.segmentation))

        # Send token...
        self.send("Text data", self.segmentation, self)
        self.infoBox.setText(message)
        self.sendButton.resetSettingsChangedFlag()

    def setCaption(self, title):
        if "captionTitle" in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)

    def browse(self):
        audioPath, _ = QFileDialog.getOpenFileName(
            self,
            u"open Text File",
            self.lastLocation,
            u"Audio Files(*)"
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

        subprocess.call(
            ['/usr/local/bin/ffmpeg', '-i',
             file,
             destination])
        return destination

    def clearCreatedInputs(self):
        """Delete all Input objects that have been created."""
        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]

    def onDeleteWidget(self):
        """Free memory when widget is deleted (overriden method)"""
        self.clearCreatedInputs()


if __name__ == '__main__':
    WidgetPreview(AudioFile).run()
    # import sys
    # from PyQt5.QtWidgets import QApplication
    # myApplication = QApplication(sys.argv)
    # myWidget = AudioFile()
    # myWidget.show()
    # myApplication.exec_()
    # myWidget.saveSettings()