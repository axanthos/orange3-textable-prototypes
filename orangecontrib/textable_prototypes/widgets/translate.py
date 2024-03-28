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

from PyQt5.QtWidgets import QPlainTextEdit

from Orange.widgets import gui, settings

from langdetect import detect

class Translate(OWTextableBaseWidget):
    """Orange widget for standard text preprocessing"""

    name = "Translate"
    description = "Text translator"
    icon = "icons/Context_54.png"
    priority = 2001

    inputs = [('Segmentation', Segmentation, "inputData",)]
    outputs = [('Preprocessed data', Segmentation)]

    # Settings...
    textFieldContent = settings.Setting(u''.encode('utf-8'))
    encoding = settings.Setting(u'utf-8')

    want_main_area = False

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    # Settings...
    copyAnnotations = settings.Setting(True)
    enableAPI = settings.Setting(False)
    inputLanguage = settings.Setting('chosenInputLanguage')
    outputLanguage = settings.Setting('chosenOutputLanguage')
    translator = settings.Setting('chosenTranslator')
    removeAccents = settings.Setting(False)
    labelKey = settings.Setting(u'Entrez votre API key')

    want_main_area = False

    def __init__(self, *args, **kwargs):
        """Initialize a widget"""
        super().__init__(*args, **kwargs)

        # Other attributes...
        self.createdInputIndices = list()
        self.segmentation = None
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute='infoBox',
            #sendIfPreCallback=self.updateGUI,
        )

        # GUI...

        # Options box
        """ optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Options',
            orientation='vertical',
            addSpace=True,
        )
        self.preprocessingBoxLine1 = gui.widgetBox(
            widget=optionsBox,
            orientation='horizontal',
        ) """
        """ gui.checkBox(
            widget=self.preprocessingBoxLine1,
            master=self,
            value='applyCaseTransform',
            label=u'Transform case:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Apply systematic case conversion."
            ),
        ) """
        """ self.caseTransformCombo = gui.comboBox(
            widget=self.preprocessingBoxLine1,
            master=self,
            value='caseTransform',
            items=[u'to lower', u'to upper'],
            sendSelectedValue=True,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Case conversion mode: to lowercase or uppercase."
            ),
        )
        self.caseTransformCombo.setMinimumWidth(120)
        gui.separator(widget=optionsBox, height=3) """
        """ gui.checkBox(
            widget=optionsBox,
            master=self,
            value='removeAccents',
            label=u'Remove accents',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Replace accented characters with non-accented ones."
            ),
        ) """
        """ gui.separator(widget=optionsBox, height=3)
        gui.checkBox(
            widget=optionsBox,
            master=self,
            value='copyAnnotations',
            label=u'Copy annotations',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Copy all annotations from input to output segments."
            ),
        ) """
        """ gui.separator(widget=optionsBox, height=2)

        gui.rubber(self.controlArea) """

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
        self.outputLanguage = gui.comboBox(
            widget=self.testBox2,
            master=self,
            value='outputLanguage',
            items=[u'Anglais', u'Portuguais', u'Français', u'Allemand', u'Russe'],
            sendSelectedValue=True,
            callback=self.sendButton.settingsChanged,
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
        self.adjustSizeWithTimer()

    def inputData(self, newInput):
        """Process incoming data."""
        self.segmentation = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def sendData(self):
        """Preprocess and send data"""
        if not self.segmentation:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Preprocessed data', None, self)
            return
        if not self.segmentation.is_non_overlapping():
            self.infoBox.setText(
                message=u'Please make sure that input segments are not ' +
                        u'overlapping.',
                state='error'
            )
            self.send('Preprocessed data', None, self)
            return

        self.clearCreatedInputIndices()
        previousNumInputs = len(Segmentation.data)
        self.infoBox.setText(u"Processing, please wait...", "warning")
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(
            self,
            iterations=len(self.segmentation)
        )
        preprocessed_data, _ = Segmenter.recode(
            self.segmentation,
            case=case,
            remove_accents=self.removeAccents,
            label=self.captionTitle,
            copy_annotations=self.copyAnnotations,
            progress_callback=progressBar.advance,
        )
        progressBar.finish()
        self.controlArea.setDisabled(False)
        newNumInputs = len(Segmentation.data)
        self.createdInputIndices = range(previousNumInputs, newNumInputs)
        message = u'%i segment@p sent to output.' % len(preprocessed_data)
        message = pluralize(message, len(preprocessed_data))
        self.infoBox.setText(message)
        self.send('Preprocessed data', preprocessed_data, self)
        self.sendButton.resetSettingsChangedFlag()

    def clearCreatedInputIndices(self):
        for i in self.createdInputIndices:
            Segmentation.set_data(i, None)

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
        text = self.segmentation[0].get_content()
        self.detectedInputLanguage = detect(text)
    
    def translate(self):
        #change segmentation
        return Input("Ce texte a été traduit (ou pas (encore))")
    

if __name__ == '__main__':
    from LTTL.Input import Input
    input1 = Input("Mary said hello to John and Mike.")
    input2 = Input("Lucy told Johnny to say hello in return.")
    input = Segmenter.concatenate([input1, input2])
    WidgetPreview(Translate).run(inputData=input)
