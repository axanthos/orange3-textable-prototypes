"""
Class OWTextablePreprocess
Copyright 2024-2025 LangTech Sarl (info@langtech.ch)
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

__version__ = '0.0.6'


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

class Transletto(OWTextableBaseWidget):
    """Orange widget for standard text translation"""

    # Widget metadata
    name = "Transletto"
    description = "Text translator"
    icon = "icons/Translator.svg"
    priority = 37

    # Input and output signals
    inputs = [('Segmentation', Segmentation, "inputData")]
    outputs = [('Translated data', Segmentation)]

    want_main_area = False

    # Settings handler
    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    # Settings...
    enableAPI = settings.Setting(False)
    inputLanguageKey = settings.Setting('English')
    outputLanguageKey = settings.Setting('French')
    autoSend = settings.Setting(False)
    translator = settings.Setting('GoogleTranslator')
    labelKey = settings.Setting('')

    want_main_area = False

    def __init__(self, *args, **kwargs):
        """Initialize a widget"""
        
        super().__init__(*args, **kwargs)

        # Initialize attributes...
        self.inputSegmentation = None
        self.outputSegmentation = None
        self.defaultLanguage = "English"
        self.createdInputs = list()
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute='infoBox',
        )

        # Path to the JSON file containing available languages and translators
        path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )

        # Load the available languages and translators from the JSON file
        try:
            with open(os.path.join(path, "translate_data.json"), "r") as file:
                self.available_languages_dict = json.load(file)
        # Else show error message
        except IOError:
            print("Failed to open json file.")

        
        # GUI elements for input language selection        
        optionsBoxInput = gui.widgetBox(
            widget=self.controlArea,
            box=u'Input language',
            orientation='vertical',
            addSpace=True,
        )
        self.testBox1 = gui.widgetBox(
            widget=optionsBoxInput,
            orientation='horizontal',
        )

        #Générer les listes des Traducteurs et Languages à être affichés au départ
        self.GenerateTranslatorLanguageList()
        
        self.inputLanguage = gui.comboBox(
            widget=self.testBox1,
            master=self,
            value='inputLanguageKey',
            items=self.available_languages,
            sendSelectedValue=True,
            callback=self.inputLanguageChanged,
            tooltip=(
                u"Choose language input."
            ),
        )
        gui.button(
            widget=self.testBox1,
            master=self,
            label=u'Auto-detect',
            callback=self.detectInputLanguage,
            tooltip=("Auto-detect language"),
        )

        # GUI elements for output language selection
        optionsBoxOutput = gui.widgetBox(
            widget=self.controlArea,
            box=u'Output language',
            orientation='vertical',
            addSpace=True,
        )
        self.testBox2 = gui.widgetBox(
            widget=optionsBoxOutput,
            orientation='horizontal',
        )
        self.outputLanguageBox = gui.comboBox(
            widget=self.testBox2,
            master=self,
            value='outputLanguageKey',
            items=self.available_languages,
            sendSelectedValue=True,
            callback=self.outputLanguageChanged, 
            tooltip=(
                u"Choose language output."
            ),
        )

        # GUI elements for translation service selection
        optionsBoxTranslator = gui.widgetBox(
            widget=self.controlArea,
            box=u'Translation service',
            orientation='vertical',
            addSpace=True,
        )
        self.testBox3 = gui.widgetBox(
            widget=optionsBoxTranslator,
            orientation='horizontal',
        )
        self.chooseTranslator = gui.comboBox(
            widget=self.testBox3,
            master=self,
            value='translator',
            items=self.available_translators,
            sendSelectedValue=True,
            callback=self.translatorChanged,
            tooltip=(
                u"Choose the translation service."
            ),
        )

        # Reset button
        optionsBoxReset = gui.widgetBox(
            widget=self.controlArea,
            box=u'',
            orientation='vertical',
            addSpace=True,
        )
        self.testBox5 = gui.widgetBox(
            widget=optionsBoxReset,
            orientation='horizontal',
        )
        gui.button(
            widget=self.testBox5,
            master=self,
            label=u'Reset',
            callback=self.resetAll,
            tooltip=("Reset all"),
        )

        gui.separator(widget=optionsBoxReset, height=3)
        gui.rubber(self.controlArea)

        # API key input field
        self.translator_need_API = list()
        for translator in self.available_languages_dict.keys():
            if self.available_languages_dict[translator]["api"]:
                self.translator_need_API.append(translator)
        print("self.translator_need_api:")
        print(self.translator_need_API)

        """ optionsBoxAPI = gui.widgetBox(
            widget=self.controlArea,
            box=u'API key :',
            orientation='vertical',
            addSpace=True,
        ) """
        self.apiBox = gui.widgetBox(
            widget=optionsBoxTranslator,
            orientation='horizontal',
        )
        self.apiKeyEdit = gui.lineEdit(
            widget=self.apiBox,
            master=self,
            value='labelKey',
            label='API Key: ',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Spot to put API key if needed"
            ),
        )
        self.apiKeyEdit.setDisabled(True)

        # Space and send button
        gui.rubber(self.controlArea)
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        #Send automatically
        self.sendButton.sendIf()

    
    def inputLanguageChanged(self):
        """ Method for change in Input Language """
        self.update(boxUpdated="input")
        self.sendButton.settingsChanged()


    def outputLanguageChanged(self):
        """ Method for change in Output Language """
        self.update(boxUpdated="output")
        self.sendButton.settingsChanged()

    def translatorChanged(self):
        """Method for change in translator"""
        print(self.translator)
        self.update(boxUpdated="translator")
        self.sendButton.settingsChanged()
        if self.translator in self.translator_need_API:
            self.apiKeyEdit.setDisabled(False)
        else:
            self.apiKeyEdit.setDisabled(True)
            

    def inputData(self, newInput):
        """Process incoming data."""
        self.inputSegmentation = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()
        print("input data ok")
       

    def sendData(self):
        """Compute result of widget processing and send to output"""
        print("this is input segmentation :")
        print(self.inputSegmentation)
        if not self.inputSegmentation:
            self.infoBox.setText(
                "Widget needs input.",
                "warning"
            )
            self.send("Translated data", None)
            return        

        # Clear created Inputs.
        self.clearCreatedInputs()

        # Initialize progress bar.
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(
            self,
            iterations=len(self.inputSegmentation)
        )

        # Make translation, print error if translation not available
        try:
            for segment in self.inputSegmentation:
                self.createdInputs.append(Input(self.translate(segment.get_content()), self.captionTitle))
                progressBar.advance()   # 1 tick on the progress bar...
       
                
            # If there's only one input, the widget's output is the created Input...
            if len(self.createdInputs) == 1:
                self.outputSegmentation = self.createdInputs[0]

            # Otherwise the widget's output is a concatenation...
            else:
                self.outputSegmentation = Segmenter.concatenate(
                    self.createdInputs,
                    self.captionTitle,
                    import_labels_as=None,
                )
     

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

            self.controlArea.setDisabled(False)

            # Send token...
            self.send("Translated data", self.outputSegmentation)
            self.sendButton.resetSettingsChangedFlag()

        except:
            #Print error if widget fails to translate
            self.infoBox.setText(
                'Translation failed. Please try changing the translation service or languages.',
                'error'
            )
            self.controlArea.setDisabled(False)

    def clearCreatedInputs(self):
        """Delete all Input objects that have been created"""
        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]

    def setCaption(self, title):
        """This method needs to be copied verbatim in every Textable widget that sends a segmentation"""
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)

    def onDeleteWidget(self):
        self.clearCreatedInputs()

    def GenerateTranslatorLanguageList(self):
        """Generate lists of available translators and languages"""
        self.available_languages = list()
        self.available_translators = list()
        for translator in self.available_languages_dict.keys():
            self.available_translators.append(translator)
            for lang in self.available_languages_dict[translator]["lang"].keys():
                self.available_languages.append(lang)
        self.available_languages = list(set(self.available_languages))
        self.available_languages.sort()


    def resetAll(self):
        """Reset widget settings"""
        self.inputLanguage.clear()
        self.chooseTranslator.clear()
        self.outputLanguageBox.clear()

        #Get all translators and available languages:
        self.available_languages = list()
        self.available_translators = list()
        for translator in self.available_languages_dict.keys():
            self.available_translators.append(translator)
            for lang in self.available_languages_dict[translator]["lang"].keys():
                self.available_languages.append(lang)
        self.available_languages = list(set(self.available_languages))
        self.available_languages.sort()

        for translator in self.available_translators:
            self.chooseTranslator.addItem(translator)
        
        for lang in self.available_languages:
            self.inputLanguage.addItem(lang)
            self.outputLanguageBox.addItem(lang)  

        self.inputLanguageKey = self.defaultLanguage
        self.outputLanguageKey = self.defaultLanguage   

    def update(self, boxUpdated):
        """Update values when a box is changed"""
        if boxUpdated != "input":
            previousInput = self.inputLanguageKey
            self.inputLanguage.clear()
        if boxUpdated != "translator":
            previousTranslator = self.translator
            self.chooseTranslator.clear()
        if boxUpdated != "output":
            previousOutput = self.outputLanguageKey
            self.outputLanguageBox.clear()


        #Get all translators:
        if boxUpdated != "translator":
            self.available_translators = list()
            for translator in self.available_languages_dict.keys():
                for lang in self.available_languages_dict[translator]["lang"].keys():
                    if boxUpdated == "input":
                        if self.inputLanguageKey == lang:
                            self.available_translators.append(translator)
                    elif boxUpdated == "output":
                        if self.outputLanguageKey == lang:
                            self.available_translators.append(translator)
            self.available_translators = list(set(self.available_translators))

        #Get all input languages
        #if boxUpdated != "input":
        self.available_languages = list()
        for translator in self.available_languages_dict.keys():
            if translator == self.translator:
                for lang in self.available_languages_dict[translator]["lang"].keys():
                    self.available_languages.append(lang)
        self.available_languages = list(set(self.available_languages))
        self.available_languages.sort()
        
        
        if boxUpdated != "input":
            for lang in self.available_languages:
                self.inputLanguage.addItem(lang)
            if previousInput in self.available_languages:
                self.inputLanguageKey = previousInput
        if boxUpdated != "translator":
            for translator in self.available_translators:
                self.chooseTranslator.addItem(translator)
            if previousTranslator in self.available_translators:
                self.translator = previousTranslator
        if boxUpdated != "output":
            for lang in self.available_languages:
                self.outputLanguageBox.addItem(lang)
            if previousOutput in self.available_languages:
                self.outputLanguageKey = previousOutput
        
        
        self.sendButton.settingsChanged()


    def detectInputLanguage(self):
        """Auto-detect input language"""
        #detect the language
        text = self.inputSegmentation[0].get_content()
        lang_detect_language = detect(text)
        for key, value in self.available_languages_dict["GoogleTranslator"]["lang"].items():
            if lang_detect_language == value:
                self.detectedInputLanguage = key
                print(f"lang_detect: {lang_detect_language}")
                self.inputLanguageKey = self.detectedInputLanguage
                self.inputLanguageChanged()
                self.sendButton.settingsChanged()
                return
        self.infoBox.setText(
                "Language not recognized",
                "warning"
            )
        return

    def translate(self, untranslated_text):        
        """Translate a text from one language to another"""

        dict = self.available_languages_dict[self.translator]["lang"]
        print(dict[self.inputLanguageKey])

        if self.translator == "GoogleTranslator":
            translated_text = dt.GoogleTranslator(source=dict[self.inputLanguageKey], target=dict[self.outputLanguageKey]).translate(untranslated_text)
        if self.translator == "MyMemory":
            translated_text = dt.MyMemoryTranslator(source=dict[self.inputLanguageKey], target=dict[self.outputLanguageKey]).translate(untranslated_text)
        if self.translator == "DeepL":
            translated_text = dt.DeeplTranslator(source=dict[self.inputLanguageKey], target=dict[self.outputLanguageKey], api_key=self.labelKey).translate(untranslated_text)
        if self.translator == "Qcri":
            translated_text = dt.QcriTranslator(source=dict[self.inputLanguageKey], target=dict[self.outputLanguageKey], api_key=self.labelKey).translate(untranslated_text)
        if self.translator == "Linguee":
            translated_text = dt.LingueeTranslator(source=dict[self.inputLanguageKey], target=dict[self.outputLanguageKey]).translate(untranslated_text)
        if self.translator == "Pons":
            translated_text = dt.PonsTranslator(source=dict[self.inputLanguageKey], target=dict[self.outputLanguageKey]).translate(untranslated_text)
        return translated_text


    
# Widget Preview for testing
if __name__ == '__main__':
    from LTTL.Input import Input
    input1 = Input("Mary said hello to John and Mike.")
    input2 = Input("Lucy told Johnny to say hello in return.")
    input = Segmenter.concatenate([input1, input2])
    WidgetPreview(Transletto).run(inputData=input)
