"""
Class Text Summarizer
Copyright 2021 University of Lausanne
-----------------------------------------------------------------------------
This file is part of the Orange3-Textable-Prototypes package.
Orange3-Textable-Prototypes is free software: you can redistribute it 
and/or modify it under the terms of the GNU General Public License as published 
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Orange3-Textable-Prototypes is distributed in the hope that it will be 
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Orange-Textable-Prototypes. If not, see 
<http://www.gnu.org/licenses/>.
"""

__version__ = u"0.0.1"
__author__ = "Melinda Femminis, Catherine Pedroni, Jason Ola"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"
import importlib.util
import sys
import os
import subprocess
import platform

from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview

from AnyQt.QtGui import (
    QTabWidget, QWidget, QHBoxLayout, QMessageBox, QIntValidator
)

from LTTL.Segmentation import Segmentation
from LTTL.Segment import Segment
import LTTL.Segmenter

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar
)

import spacy

AVAILABLE_MODELS = {
    "Dutch news (small)": "nl_core_news_sm",
    "English web (small)": "en_core_web_sm",
    "English web (medium)": "en_core_web_md",
    "English web (large)": "en_core_web_lg",
    "French news (small)": "fr_core_news_sm",
    "French news (medium)": "fr_core_news_md",
    "German news (small)": "de_core_news_sm",
    "German news (medium)": "de_core_news_md",
    "Greek news (small)": "el_core_news_sm",
    "Greek news (medium)": "el_core_news_md",
    "Italian news (small)": "it_core_news_sm",
    "Lithuanian news (small)": "lt_core_news_sm",
    "Norwegian news (small)": "nb_core_news_sm",
    "Portuguese news (small)": "pt_core_news_sm",
    "Spanish news (small)": "es_core_news_sm",
    "Spanish news (medium)": "es_core_news_md",
}

# Determine which language models are installed...
INSTALLED_MODELS = list()
for model, package in AVAILABLE_MODELS.items():
    if importlib.util.find_spec(package.replace("-", ".")):
        INSTALLED_MODELS.append(model)

class TextSummarizer(OWTextableBaseWidget):
    """Textable widget for summarizing Text segmentation with spaCy models."""

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Text Summarizer"
    description = "Summarize texts with spaCy models"
    icon = "icons/TL_DR_icon.svg"
    priority = 21   # TODO

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = [("Text data", Segmentation, "inputData")]
    outputs = [("Character segmentation", Segmentation)]

    #----------------------------------------------------------------------
    # Layout parameters...
    
    want_main_area = False

    #----------------------------------------------------------------------
    # Settings...
    # Define variables in widgets (the ones weirdly in "")
    
    # Set number of sentences to keep default
    numSentences = settings.Setting(10)
    # Set language selection
    language = settings.Setting("English")

    #----------------------------------------------------------------------
    # The following lines need to be copied verbatim in every Textable widget...
    
    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    
    def __init__(self):
        """Widget creator."""

        super().__init__()

        #----------------------------------------------------------------------
        # Other (non settings) attributes...
        
        self.inputSeg = None
        self.selectedCharacters = list()
        self.characters = list()
        self.nlp = None
        if INSTALLED_MODELS:
            self.model = INSTALLED_MODELS[0]
        else:
            self.model = ""

        #----------------------------------------------------------------------
        # Next two instructions are helpers from TextableUtils. Corresponding
        # interface elements are declared here and actually drawn below (at
        # their position in the UI)...
        
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute="infoBox",
            sendIfPreCallback=None,
        )

        #----------------------------------------------------------------------
        # User interface...

        optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box="Options",
            orientation="vertical",
        )
        gui.spin(
            widget=optionsBox,
            master=self,
            value='numSentences', #defined in settings
            label='Number of sentences : ',
            callback=self.sendButton.sendIf,
            labelWidth=180,
            tooltip=(
                'Select the number of sentences'
            ),
            maxv=1000,
            minv=1,
            step=1,
        )
        self.choiceBox = gui.comboBox(
            widget=optionsBox,
            master=self, 
            value='language', #defined in settings
            label="Language : ",
            callback=self.lang_changed,# defined in methods down
            tooltip= "Choose mode",
            orientation='horizontal',
            sendSelectedValue=True,
            items=["English", "French", "Portuguese"],
            labelWidth=135,
        )
        gui.separator(widget=optionsBox, height=2)

        #self.characterListbox.setSelectionMode(0)
        
        gui.rubber(self.controlArea)

        #----------------------------------------------------------------------
        # Draw Info box and Send button...
        
        self.sendButton.draw()
        self.infoBox.draw()
        self.infoBox.setText("Widget needs input.", "warning")
        
        # Check that there's a model...
        if not self.model:
            self.noLanguageModelWarning()

    # New defined method for callback before
    def lang_changed(self):
        pass #refer to redditor mode_changed method

    # didnt touch code below it is still copypaste from charnet
    def inputData(self, newInput):
        """Process incoming data."""
        self.inputSeg = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def noLanguageModelWarning(self):
        """"Warn user that a spaCy model must be installed and disable GUI."""
        self.infoBox.setText(
            "Please use the spaCy widget to download a language "
            "model first.",
            "warning",
        )
        self.controlArea.setDisabled(True)

    def sendData(self):
        """Compute result of widget processing and send to output."""

        # Check that there's a model...
        if not self.model:
            self.noLanguageModelWarning()
            return

        # Check that there's an input...
        if self.inputSeg is None:
            self.infoBox.setText("Widget needs input.", "warning")
            for channel in [c.name for c in self.outputs]:
                self.send(channel, None, self)
            return
       
        # Initialize progress bar.
        self.infoBox.setText(
            u"Processing, please wait...", 
            "warning",
        )
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=len(self.inputSeg))       

        # Process each input segment...
        for segment in self.inputSeg:

            # TODO...
            
            progressBar.advance()

        # Send output...
        output_segmentation = LTTL.Segmenter.bypass(self.inputSeg)
        self.send("Character segmentation", output_segmentation, self)

        # Set status to OK and report data size...
        message = "%i segment@p sent to output." % len(output_segmentation)
        message = pluralize(message, len(output_segmentation))
        self.infoBox.setText(message)
        
        # Clear progress bar.
        progressBar.finish()
        self.controlArea.setDisabled(False)
                
        self.sendButton.resetSettingsChangedFlag()             

    #----------------------------------------------------------------------
    # The following method needs to be copied verbatim in
    # every Textable widget that sends a segmentation...
    
    def setCaption(self, title):
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)

            
if __name__ == "__main__":
    from LTTL.Input import Input
    WidgetPreview(TextSummarizer).run(inputData=Input("Mary said hello to John."))