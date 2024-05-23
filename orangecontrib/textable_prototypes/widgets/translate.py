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

__version__ = '0.0.5'


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
    icon = "icons/Translator.svg"
    priority = 2001

    inputs = [('Segmentation', Segmentation, "inputData")]
    outputs = [('Translated data', Segmentation)]

    want_main_area = False

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    # Settings...
    enableAPI = settings.Setting(False)
    inputLanguageKey = settings.Setting('french')
    inputLanguage = settings.Setting('fr-FR')
    outputLanguageKey = settings.Setting('french')
    outputLanguage = settings.Setting('fr-FR')
    
    translator = settings.Setting('GoogleTranslator')
    labelKey = settings.Setting('')

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
            print("Failed to open json file.")

        
        # Input language
        
        optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Input language',
            orientation='vertical',
            addSpace=True,
        )
        self.testBox1 = gui.widgetBox(
            widget=optionsBox,
            orientation='horizontal',
        )
       
        self.vacheALait()
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
            items=self.available_languages,
            sendSelectedValue=True,
            callback=self.outputLanguageChanged, 
            tooltip=(
                u"Choose language output."
            ),
        )

        # Translation service
        optionsBox = gui.widgetBox(
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
            items=self.available_translators,
            sendSelectedValue=True,
            callback=self.translatorChanged,
            tooltip=(
                u"Choose the translation service."
            ),
        )


        optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'',
            orientation='vertical',
            addSpace=True,
        )
        self.testBox5 = gui.widgetBox(
            widget=optionsBox,
            orientation='horizontal',
        )
        gui.button(
            widget=self.testBox5,
            master=self,
            label=u'Reset',
            callback=self.resetAll,
            tooltip=("Reset all"),
        )

        #self.chooseTranslator.setMinimumWidth(120)
        #self.outputLanguage.setMinimumWidth(120)
        #self.inputLanguage.setMinimumWidth(120)
        gui.separator(widget=optionsBox, height=3)

        gui.rubber(self.controlArea)

        # Text Field API key
        self.translator_need_API = list()
        for translator in self.available_languages_dict.keys():
            if self.available_languages_dict[translator]["api"]:
                self.translator_need_API.append(translator)
        print("self.translator_need_api:")
        print(self.translator_need_API)

        optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'API :',
            orientation='vertical',
            addSpace=True,
        )
        self.apiBox = gui.widgetBox(
            widget=optionsBox,
            orientation='horizontal',
        )

        self.apiKeyEdit = gui.lineEdit(
            widget=self.apiBox,
            master=self,
            value='labelKey',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Spot to put API key if needed"
            ),
        )

        self.apiKeyEdit.setDisabled(True)

        # Space in between
        gui.rubber(self.controlArea)

        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.sendButton.sendIf()

    
    def inputLanguageChanged(self):
        """ Method for change in Input Language """
        translators_available_for_lang = []
        output_available_for_lang = []
        for translator in self.available_languages_dict.keys():
            for lang in self.available_languages_dict[translator]["lang"].keys():
                print(self.inputLanguageKey)
                print(lang)
                if self.inputLanguageKey == lang:
                    translators_available_for_lang.append(translator)
        for translator in translators_available_for_lang:
            for lang in self.available_languages_dict[translator]["lang"].keys():
                output_available_for_lang.append(lang)

        print(translators_available_for_lang)
        self.chooseTranslator.clear()
        for lang in translators_available_for_lang:
            self.chooseTranslator.addItem(lang)
        self.available_translators = translators_available_for_lang
        self.available_translators = self.available_translators
        self.outputLanguageBox.clear()
        output_available_for_lang = list(set(output_available_for_lang))
        output_available_for_lang.sort()
        for lang in output_available_for_lang:
            self.outputLanguageBox.addItem(lang)
        print(self.available_translators)
        self.sendButton.settingsChanged()


    def outputLanguageChanged(self):
        """ Method for change in Output Language """
        self.outputLanguage = self.available_languages
        print(self.outputLanguage)
        self.sendButton.settingsChanged()

    def translatorChanged(self):
        """Method for change in translator"""
        #self.translator = self.available_translators
        print(self.translator)
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

    def vacheALait(self):
        self.available_languages = list()
        self.available_translators = list()
        for translator in self.available_languages_dict.keys():
            self.available_translators.append(translator)
            for lang in self.available_languages_dict[translator]["lang"].keys():
                self.available_languages.append(lang)
        self.available_languages = list(set(self.available_languages))
        self.available_languages.sort()


    def resetAll(self):
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


    def detectInputLanguage(self):
        #detect the language
        text = self.inputSegmentation[0].get_content()
        #self.detectedInputLanguage = detect(text)
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
        #print(self.detectedInputLanguage)
        print(self.translator)  
        #try:
        dict = self.available_languages_dict[self.translator]["lang"]
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
    

if __name__ == '__main__':
    from LTTL.Input import Input
    input1 = Input("Mary said hello to John and Mike.")
    input2 = Input("Lucy told Johnny to say hello in return.")
    input = Segmenter.concatenate([input1, input2])
    WidgetPreview(Translate).run(inputData=input)
