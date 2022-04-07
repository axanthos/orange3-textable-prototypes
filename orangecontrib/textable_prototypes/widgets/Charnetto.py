"""
Class Charnetto
Copyright 2022 University of Lausanne
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

__version__ = u"0.0.2"
__author__ = "Aris Xanthos"
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

import charnetto
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

class Charnetto(OWTextableBaseWidget):
    """Textable widget for building character networks with Charnetto."""

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Charnetto"
    description = "Build character networks with the Charnet package"
    icon = "icons/charnetto.svg"
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
    
    # TODO

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
        self.mustLoad = True
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

        self.characterListbox = gui.listBox(
            widget=self.controlArea,
            master=self,
            value="selectedCharacters",
            labels="characters",
            callback=None,
            tooltip="List of identified characters",
        )
        
        gui.rubber(self.controlArea)

        #----------------------------------------------------------------------
        # Draw Info box and Send button...
        
        self.sendButton.draw()
        self.infoBox.draw()
        self.infoBox.setText("Widget needs input.", "warning")
        
        # Check that there's a model...
        if not self.model:
            self.noLanguageModelWarning()

    def inputData(self, newInput):
        """Process incoming data."""
        self.inputSeg = newInput
        if self.inputSeg is None:
            self.infoBox.setText("Widget needs input.", "warning")
            self.sendNoneToOutputs()
            self.characters = list()
            return
        self.updateCharacterList()
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def updateCharacterList(self):
        """Update character list based on Charnetto output."""
        if self.mustLoad:
            self.loadModel()
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=4)
        strings = [segment.get_content() for segment in self.inputSeg]
        progressBar.advance()
        self.char_df = charnetto.extract_spacy_df(strings, self.nlp) # TODO progress
        print(self.char_df)
        progressBar.advance()
        self.char_df = charnetto.unify_tags(self.char_df)
        progressBar.advance()
        self.char_list = charnetto.concatenate_parents(self.char_df, min_occ = 1)
        self.characters = [", ".join(char) for char in self.char_list]
        progressBar.advance()
        progressBar.finish()
        self.controlArea.setDisabled(False)
    
    def loadModel(self):
        """(Re-)load language model if needed."""
        # Initialize progress bar.
        self.infoBox.setText(
            u"Loading language model, please wait...", 
            "warning",
        )
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=1)       
        self.nlp = spacy.load(
            #AVAILABLE_MODELS[self.model],
            "en_core_web_sm",
        )
        self.mustLoad = False
        progressBar.advance()
        progressBar.finish()
        self.controlArea.setDisabled(False)

    def noLanguageModelWarning(self):
        """"Warn user that a spaCy model must be installed and disable GUI."""
        self.infoBox.setText(
            "Please use the spaCy widget to download a language "
            "model first.",
            "warning",
        )
        self.controlArea.setDisabled(True)

    def sendNoneToOutputs(self):
        """Send None token to all output channels."""
        for channel in [c.name for c in self.outputs]:
            self.send(channel, None, self)
        return

    def sendData(self):
        """Compute result of widget processing and send to output."""

        # Check that there's a model...
        if not self.model:
            self.noLanguageModelWarning()
            self.sendNoneToOutputs()
            return

        # Check that there's an input...
        if self.inputSeg is None:
            self.infoBox.setText("Widget needs input.", "warning")
            self.sendNoneToOutputs()
            return
       
        # Initialize progress bar.
        self.infoBox.setText(
            u"Processing, please wait...", 
            "warning",
        )

        # Disable control area and initialize progress bar...
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=len(self.char_df))       

        # Get start and end pos of concatenated input segments...
        start_positions = [0]
        end_positions = list()
        num_segments = len(self.inputSeg)
        for idx in range(1, num_segments):
            prev_seg_len = len(self.inputSeg[idx-1].get_content())
            start_positions.append(start_positions[-1] + prev_seg_len + 1)
            end_positions.append(start_positions[-1] - 1)
        end_positions.append(start_positions[-1] + 
                             len(self.inputSeg[-1].get_content()) + 1)

        # Initializations...
        char_segments = list()
        current_segment_idx = 0

        # For each character token in Charnetto's output...
        for index, char_token in self.char_df.iterrows():

            # Get index of containing segment...
            while char_token["end_pos"] > end_positions[current_segment_idx]:
                current_segment_idx += 1
                
            # Create segment for char with its actual coordinates...
            str_index = self.inputSeg[current_segment_idx].str_index
            start = char_token["start_pos"]-start_positions[current_segment_idx]
            end = char_token["end_pos"]-start_positions[current_segment_idx]
            char_segments.append(Segment(str_index, start, end))
            
            progressBar.advance()

        # Send output...
        output_segmentation = Segmentation(char_segments, 
                                           label=self.captionTitle)
        self.send("Character segmentation", output_segmentation, self)
        print(output_segmentation.to_string())

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
    input1 = Input("Mary said hello to John.")
    input2 = Input("Lucy told Johnny to say hello in return.")
    input = LTTL.Segmenter.concatenate([input1, input2])
    WidgetPreview(Charnetto).run(inputData=input)
