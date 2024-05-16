"""
Class OWTextablePreprocess
Copyright 2012-2019 LangTech Sarl (info@langtech.ch)
-----------------------------------------------------------------------------
This file is part of the Orange3-Textable package.

Orange3-Textable is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Orange3-Textable is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Orange3-Textable. If not, see <http://www.gnu.org/licenses/>.
"""

__version__ = '0.0.1'


import LTTL.Segmenter as Segmenter
from LTTL.Segmentation import Segmentation
from LTTL.Input import Input
from Orange.widgets.utils.widgetpreview import WidgetPreview
from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, ProgressBar,
    InfoBox, SendButton, pluralize
)
#from PyQt5.QtWidgets import QPlainTextEdit
from Orange.widgets import gui, settings
from langdetect import detect
import deep_translator as dt
import json
import os
import inspect


class Translate(OWTextableBaseWidget):
    """Orange widget for standard text preprocessing"""

    name = "Preprocess"
    description = "Basic text preprocessing"
    icon = "icons/Preprocess.png"
    priority = 2001

    inputs = [('Segmentation', Segmentation, "inputData",)]
    outputs = [('Preprocessed data', Segmentation)]

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    # Settings...
    copyAnnotations = settings.Setting(True)
    applyCaseTransform = settings.Setting(False)
    caseTransform = settings.Setting('to lower')
    removeAccents = settings.Setting(False)
    outputLanguageKey = settings.Setting('french')
    outputLanguage = settings.Setting('fr-FR')

    want_main_area = False

    def __init__(self, *args, **kwargs):
        """Initialize a Preprocess widget"""
        super().__init__(*args, **kwargs)

        # Other attributes...
        self.createdInputs = list()
        self.inputSegmentation = None
        self.outputSegmentation = None
        self.infoBox = InfoBox(widget=self.controlArea)
        self.detectedInputLanguage = "en-GB"
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute='infoBox',
        )

        # Path to json
        path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )

        # Open the jspon and add the content in our database
        try:
            with open(os.path.join(path, "translate_data.json"), "r") as file:
                self.available_languages_dict = json.load(file)
        # Else show error message
        except IOError:
            print("Failed to open json file.")

        # GUI...

        # Options box
        optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Output language',
            orientation='vertical',
            addSpace=True,
        )
        self.textBox2 = gui.widgetBox(
            widget=optionsBox,
            orientation='horizontal',
        )
        self.outputLanguageBox = gui.comboBox(
            widget=self.textBox2,
            master=self,
            value='outputLanguageKey',
            sendSelectedValue=True,
            items=list(self.available_languages_dict["MyMemoryTranslator"].keys()),
            callback=self.outputLanguageChanged,
            tooltip=(
                u"Choose language output."
            ),
        )

        gui.rubber(self.controlArea)

        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.sendButton.sendIf()
        self.adjustSizeWithTimer()

    def outputLanguageChanged(self):
        """ Method for change in Output Language """
        self.outputLanguage = self.available_languages_dict["MyMemoryTranslator"][self.outputLanguageKey]
        print(self.outputLanguage)
        self.sendButton.settingsChanged()

    def inputData(self, newInput):
        """Process incoming data."""
        self.inputSegmentation = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def sendData(self):
        """Preprocess and send data"""
        if not self.inputSegmentation:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Preprocessed data', None, self)
            return


        self.clearCreatedInputIndices()
        previousNumInputs = len(Segmentation.data)
        self.infoBox.setText(u"Processing, please wait...", "warning")
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(
            self,
            iterations=len(self.inputSegmentation)
        )

        self.detectInputLanguage()


        for segment in self.inputSegmentation:
            #pas pour test
            self.createdInputs.append(Input(self.translate(segment.get_content()), self.captionTitle))
            """annotations.append(
                self.inputSegmentation[segment].annotations.copy()
            )"""
            progressBar.advance()   # 1 tick osn the progress bar...

        # If there's only one play, the widget's output is the created Input...
        if len(self.createdInputs) == 1:
            self.outputSegmentation = self.createdInputs[0]

        # Otherwise the widget's output is a concatenation...
        else:
            self.outputSegmentation = Segmenter.concatenate(
                self.createdInputs,
                self.captionTitle,
                import_labels_as=None,
            )

        progressBar.finish()
        self.controlArea.setDisabled(False)

        message = u'%i segment@p sent to output.' % len(self.outputSegmentation)
        message = pluralize(message, len(self.outputSegmentation))

        numChars = 0
        for segment in self.outputSegmentation:
            segmentLength = len(Segmentation.get_data(segment.str_index))
            numChars += segmentLength
        message += "(%i character@p)." % numChars
        message = pluralize(message, numChars)
        self.infoBox.setText(message)
        self.send('Preprocessed data', self.outputSegmentation, self)
        self.sendButton.resetSettingsChangedFlag()

    def clearCreatedInputIndices(self):
        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]

    def setCaption(self, title):
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)

    def onDeleteWidget(self):
        self.clearCreatedInputIndices()

    def detectInputLanguage(self):
        #detect the language
        print(f"HEEEEEERE {self.inputSegmentation[0].get_content()}")
        text = self.inputSegmentation[0].get_content()
        #self.detectedInputLanguage = detect(text)
        lang_detect_language = detect(text)
        for language in self.available_languages_dict["MyMemoryTranslator"].values():
            if lang_detect_language in language:
                self.detectedInputLanguage = language
                print(f"lang_detect: {lang_detect_language}")
                print(f"langue: {language}")
                return
        self.infoBox.setText(
                "Language not recognized",
                "warning"
            )
        return

    def translate(self, untranslated_text):
        print(self.detectedInputLanguage)
        print(self.outputLanguage)
        #try:
        translated_text = dt.MyMemoryTranslator(source=self.detectedInputLanguage, target=self.outputLanguage).translate(untranslated_text)
        return translated_text
        #except:
         #   print("Translation process did not work")


if __name__ == '__main__':
    """ import sys
    from PyQt5.QtWidgets import QApplication
    appl = QApplication(sys.argv)
    ow = OWTextablePreprocess()
    ow.show()
    appl.exec_()
    ow.saveSettings() """
    from LTTL.Input import Input
    input1 = Input("Mary said hello to John and Mike.")
    input2 = Input("Lucy told Johnny to say hello in return.")
    input = Segmenter.concatenate([input1, input2])
    WidgetPreview(Translate).run(inputData=input)
