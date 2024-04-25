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

    name = "Translate"
    description = "Text translator"
    icon = "icons/Context_54.png"
    priority = 2001

    inputs = [('Segmentation', Segmentation, "inputData")]
    outputs = [('Translated data', Segmentation)]

    want_main_area = False

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    # Settings...
    #enableAPI = settings.Setting(False)
    #inputLanguage = settings.Setting('chosenInputLanguage')
    outputLanguageKey = settings.Setting('french')
    outputLanguage = settings.Setting('fr-FR')
    
    #translator = settings.Setting('chosenTranslator')
    #labelKey = settings.Setting(u'Entrez votre API key')

    want_main_area = False

    def __init__(self, *args, **kwargs):
        """Initialize a widget"""
        super().__init__(*args, **kwargs)

        # Other attributes...
        self.inputSegmentation = None
        self.outputSegmentation = None
        self.createdInputs = list()
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute='infoBox',
        )

        # Path to pkl
        path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )

        # Open the pkl and add the content in our database
        try:
            with open(os.path.join(path, "translate_data.json"), "r") as file:
                self.available_languages_dict = json.load(file)
        # Else show error message
        except IOError:
            print("Failed to open pkl file.")

        
        # Input language
        
        """ optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Input language',
            orientation='vertical',
            addSpace=True,
        )
        self.testBox1 = gui.widgetBox(
            widget=optionsBox,
            orientation='horizontal',
        )
        self.inputLanguage = gui.comboBox(
            widget=self.testBox1,
            master=self,
            value='inputLanguage',
            items=[u'Anglais', u'Portuguais', u'Français', u'Allemand', u'Russe'],
            sendSelectedValue=True,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Choose language input."
            ),
        ) """

        # Output language
        optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Output language',
            orientation='vertical',
            addSpace=True,
        )
        self.testBox2 = gui.widgetBox(
            widget=optionsBox,
            orientation='horizontal',
        )
        self.outputLanguageBox = gui.comboBox(
            widget=self.testBox2,
            master=self,
            value='outputLanguageKey',
            items=list(self.available_languages_dict["MyMemoryTranslator"].keys()),
            sendSelectedValue=True,
            callback=self.outputLanguageChanged, 
            tooltip=(
                u"Choose language output."
            ),
        )



        # Translation service
        """ optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Translation service',
            orientation='vertical',
            addSpace=True,
        )
        self.testBox3 = gui.widgetBox(
            widget=optionsBox,
            orientation='horizontal',
        )
        self.chooseTranslator = gui.comboBox(
            widget=self.testBox3,
            master=self,
            value='translator',
            items=[u'Google Traduction', u'DeepL', u'LibrTranslate', u'PONS'],
            sendSelectedValue=True,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Choose the translation service."
            ),
        )
        self.chooseTranslator.setMinimumWidth(120)
        self.outputLanguage.setMinimumWidth(120)
        self.inputLanguage.setMinimumWidth(120)
        gui.separator(widget=optionsBox, height=3)

        gui.rubber(self.controlArea) """

        # Text Field API key
        """ optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'',
            orientation='vertical',
            addSpace=True,
        )
        self.testBox4 = gui.widgetBox(
            widget=optionsBox,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=self.testBox4,
            master=self,
            value='enableAPI',
            label=u'API Key :',
            labelWidth=80,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"API."
            ),
        )
        self.labelKeyLineEdit = gui.lineEdit(
            widget=self.testBox4,
            master=self,
            value='labelKey',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Spot to put API key if needed"
            ),
        ) """

        # Space in between
        gui.rubber(self.controlArea)

        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.sendButton.sendIf()

    
    def outputLanguageChanged(self):
        """ Method for change in Output Language """
        self.outputLanguage = self.available_languages_dict["MyMemoryTranslator"][self.outputLanguageKey]
        print(self.outputLanguage)
        self.sendButton.settingsChanged()


    def inputData(self, newInput):
        """Process incoming data."""
        print(f"this is input datat print : {len(newInput)}")
        self.inputSegmentation = newInput
        self.detectInputLanguage()
        self.infoBox.inputChanged()
        self.sendButton.sendIf()
        print("input data ok")

        

    def sendData(self):
        """Compute result of widget processing and send to output"""

        # Check that something has been selected...
        print("this is input segmentation :")
        print(self.inputSegmentation)
        if not self.inputSegmentation:
            self.infoBox.setText(
                "Widget needs input.",
                "warning"
            )
            self.send("Translated data", None, self)
            return        

        """if self.detectedInputLanguage not in self.available_languages_dict["MyMemoryTranslator"].items():
            self.infoBox.setText(u'This language is not supported', 'error')
            self.send('Preprocessed data', None, self)
            return"""

        # Clear created Inputs.
        self.clearCreatedInputs()

        # Initialize progress bar.
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(
            self,
            iterations=len(self.inputSegmentation)
        )

       
        #annotations = list()
        #try:
        for segment in self.inputSegmentation:
            #pas pour test
            self.createdInputs.append(Input(self.translate(segment.get_content()), self.captionTitle))
            """annotations.append(
                self.inputSegmentation[segment].annotations.copy()
            )"""
            progressBar.advance()   # 1 tick on the progress bar...
                
        # If an error occurs (e.g. http error, or memory error)...
            """         except:
            # Set Info box and widget to "error" state.
            self.infoBox.setText(
                "Couldn't translate input",
                "error"
            ) 

            # Reset output channel.
            self.send("Translated data", None, self)
            self.controlArea.setDisabled(False)
            return"""
        # Store downloaded XML in input objects...
        """for segmentation_content_idx in range(len(segmentation_contents)):
            newInput = Input(segmentation_contents[segmentation_content_idx])
            self.createdInputs.append(newInput)"""

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

        # Annotate segments...
        """for idx, segment in enumerate(self.outputSegmentation):
            segment.annotations.update(annotations[idx])
            self.outputSegmentation[idx] = segment"""        

        # Set status to OK and report data size...
        message = "%i segment@p sent to output " % len(self.outputSegmentation)
        message = pluralize(message, len(self.outputSegmentation))
        numChars = 0
        for segment in self.outputSegmentation:
            segmentLength = len(Segmentation.get_data(segment.str_index))
            numChars += segmentLength
        message += "(%i character@p)." % numChars
        message = pluralize(message, numChars)
        self.infoBox.setText(message)
        progressBar.finish()

        # Clear progress bar.
        progressBar.finish()
        self.controlArea.setDisabled(False)

        # Send token...
        self.send("Translated data", self.outputSegmentation, self)
        self.sendButton.resetSettingsChangedFlag()

    def clearCreatedInputs(self):
        """
        Delete all Input objects that have been created
        """

        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]

    def updateGUI(self):
        """Update GUI state"""
        """ if self.importLabels:
            self.labelKeyLineEdit.setDisabled(False)
        else:
            self.labelKeyLineEdit.setDisabled(True) """
        """ if self.autoNumber:
            self.autoNumberKeyLineEdit.setDisabled(False)
        else:
            self.autoNumberKeyLineEdit.setDisabled(True) """
        if self.enableAPI:
            self.caseTransformCombo1.setDisabled(False)
        else:
            self.caseTransformCombo1.setDisabled(True)

    def setCaption(self, title):
        """
        This method needs to be copied verbatim in every Textable widget that sends a segmentation
        """

        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)

    def onDeleteWidget(self):
        self.clearCreatedInputs()

    def detectInputLanguage(self):
        #detect the language
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
    from LTTL.Input import Input
    input1 = Input("Mary said hello to John and Mike.")
    input2 = Input("Lucy told Johnny to say hello in return.")
    input = Segmenter.concatenate([input1, input2])
    WidgetPreview(Translate).run(inputData=input)
