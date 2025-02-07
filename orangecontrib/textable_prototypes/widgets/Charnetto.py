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

__version__ = u"0.0.1"
__author__ = "Aris Xanthos"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

import importlib.util
import sys

from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview

from AnyQt.QtGui import (
    QTabWidget, QWidget, QHBoxLayout, QMessageBox, QInputDialog
)

from LTTL.Segmentation import Segmentation
from LTTL.Segment import Segment
import LTTL.Segmenter

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar
)

from orangecontrib.textable_prototypes.widgets import SpaCy as spacy_widget

import charnetto
import spacy


class Charnetto(OWTextableBaseWidget):
    """Textable widget for building character networks with Charnetto."""

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Charnetto"
    description = "Build character networks with the Charnetto package"
    icon = "icons/charnetto.svg"
    priority = 20

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = [("Text data", Segmentation, "inputData")]
    outputs = [("Character segmentation", Segmentation)]

    #----------------------------------------------------------------------
    # Layout parameters...
    
    want_main_area = False

    #----------------------------------------------------------------------
    # Settings...
    
    sourceType = settings.Setting("Plain text")
    minFreq = settings.Setting(1)
    model = settings.Setting("")

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
        if spacy_widget.INSTALLED_MODELS:
            self.model = spacy_widget.INSTALLED_MODELS[0]
            self.mustInstall = False
        else:
            self.model = ""
            self.mustInstall = True
        self.editsWereMade = False

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

        # Sample box...
        self.optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box="Options",
            orientation="vertical",
        )
        # self.sourceTypeCombo = gui.comboBox(
            # widget=self.optionsBox,
            # master=self,
            # value="sourceType",
            # sendSelectedValue=True,
            # items=["Plain text", "IMSDB-formatted script"],
            # orientation="horizontal",
            # label="Source type:",
            # labelWidth=120,
            # callback=self.changeSourceType,
            # tooltip=(
                # "TODO\n"
                # "TODO\n"
                # "TODO\n"
            # ),
        # )

        self.spacyModelCombo = gui.comboBox(
            widget=self.optionsBox,
            master=self,
            value="model",
            sendSelectedValue=True,
            items=spacy_widget.INSTALLED_MODELS,
            orientation="horizontal",
            label="SpaCy model:",
            labelWidth=120,
            callback=self.loadModel,
            tooltip=("Choose spaCy model for named entity recognition."),
        )


        # gui.separator(widget=self.optionsBox, height=3)

        # minFreqSpin = gui.spin(
            # widget=self.optionsBox,
            # master=self,
            # value='minFreq',
            # minv=1,
            # maxv=1000,
            # orientation='horizontal',
            # label="Minimum frequency:",
            # labelWidth=120,
            # callback=self.sendButton.settingsChanged,
            # keyboardTracking=False,
            # tooltip=(
                # "TODO\n"
                # "TODO\n"
                # "TODO\n"
            # ),
        # )
        
        # gui.separator(widget=self.optionsBox, height=3)

        # Character box...
        self.characterBox = gui.widgetBox(
            widget=self.controlArea,
            box="Edit character list",
            orientation="vertical",
        )

        characterListbox = gui.listBox(
            widget=self.characterBox,
            master=self,
            value="selectedCharacters",
            labels="characters",
            callback=self.updateButtons,
            tooltip="List of identified characters",
        )
        # TODO set min height

        self.characterButtonBox = gui.widgetBox(
            widget=self.characterBox,
            orientation="horizontal",
        )

        self.newButton = gui.button(
            widget=self.characterButtonBox,
            master=self,
            label="New",
            callback=self.newCharacter,
            tooltip="Add a new entry to the character list.",
        )
        
        self.editButton = gui.button(
            widget=self.characterButtonBox,
            master=self,
            label="Edit",
            callback=self.editCharacters,
            tooltip="Add the selected character list entry.",
        )
        
        self.deleteButton = gui.button(
            widget=self.characterButtonBox,
            master=self,
            label="Delete",
            callback=self.deleteCharacter,
            tooltip="Delete the selected character list entry.",
        )

        self.resetButton = gui.button(
            widget=self.characterButtonBox,
            master=self,
            label="Reset",
            callback=self.resetCharacters,
            tooltip="Revert all changes made to character list.",
        )

        self.updateButtons()
        
        gui.rubber(self.controlArea)

        #----------------------------------------------------------------------
        # Draw Info box and Send button...
        
        self.sendButton.draw()
        self.infoBox.draw()
        self.infoBox.setText("Widget needs input.", "warning")
        
        # Check that there's a model...
        if self.mustInstall:
            self.noLanguageModelWarning()
        else:
            self.loadModel()

    def inputData(self, newInput):
        """Process incoming data."""
        if self.mustInstall:
            return
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
        # Sanity checks...
        if not self.model or not self.inputSeg:
            return
        
        # Init UI...
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=4)
        
        # Get input strings...
        strings = [segment.get_content() for segment in self.inputSeg]
        progressBar.advance()
        
        # Extract character tokens...
        # if self.sourceType == "Plain text":
            # self.char_df = charnetto.extract_spacy_df(strings, self.nlp)
        # elif self.sourceType == "IMSDB-formatted script":
            # self.char_df = charnetto.extract_movie_df(" ".join(strings))
        self.char_df = charnetto.extract_spacy_df(strings, self.nlp)
        
        # TODO deal with \n in names
        progressBar.advance()
        
        # Unify spaCy tags to match those of flair...  
        self.char_df = charnetto.unify_tags(self.char_df)
        progressBar.advance()
        
        # Collapse characters whose name is the prefix of another.
        self.char_list = charnetto.concatenate_parents(self.char_df, min_occ = 1)

        # Build char list and reset UI.
        self.characters = [", ".join(char) for char in self.char_list]
        progressBar.advance()
        progressBar.finish()
        self.controlArea.setDisabled(False)
        
        # Cache character list for resetting if needed.
        self.cachedCaracters = self.characters[:]
    
    def loadModel(self):
        """(Re-)load language model if needed."""
        # Display warning, disable UI and initialize progress bar...
        self.infoBox.setText(
            u"Loading language model, please wait...", 
            "warning",
        )
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=1)

        # Load model and reset UI.
        self.nlp = spacy.load(spacy_widget.AVAILABLE_MODELS[self.model])
        progressBar.advance()
        progressBar.finish()
        self.controlArea.setDisabled(False)
        
        # Update char list if there's an input...
        if self.inputSeg:
            self.updateCharacterList()
        
        self.sendButton.settingsChanged()

    def noLanguageModelWarning(self):
        """"Warn user that a spaCy model must be installed and disable GUI."""
        self.infoBox.setText(
            "Please first use the spaCy widget to download a language "
            "model, then create a new copy of the Charnetto widget.",
            "warning",
        )
        self.controlArea.setDisabled(True)

    def changeSourceType(self):
        """"Deal with user-requested source type change."""
        self.spacyModelCombo.setDisabled(self.sourceType ==
            "IMSDB-formatted script")
            
        # Update char list if there's an input...
        if self.inputSeg:
            self.updateCharacterList()
        
        self.sendButton.settingsChanged()

    def newCharacter(self):
        """"Add new character to list."""
        new_value, ok = QInputDialog.getText(self, "New character", 
            "Enter new line:")
        if ok and self.checkInputValidity(new_value):
            self.editsWereMade = True
            self.characters.append(str(new_value))
            self.characters = self.characters
            self.sendButton.settingsChanged()

    def editCharacters(self):
        """"Deal with user requested edition of character in list."""
        selected_idx = self.selectedCharacters[0]
        old_value = self.characters[selected_idx]
        new_value, ok = QInputDialog.getText(self, "Edit character", 
            "Enter new value for this line:", text=old_value)
        if ok and self.checkInputValidity(new_value):
            if new_value != old_value:
                self.editsWereMade = True
                self.characters[selected_idx] = str(new_value)
                self.characters = self.characters
                self.sendButton.settingsChanged()

    def deleteCharacter(self):
        """"Deal with user requested deletion of character in list."""
        selected_idx = self.selectedCharacters[0]
        old_value = self.characters[selected_idx]
        answer = QMessageBox.question(self, "Delete character",
            f"Do you really want to delete line '{old_value}'")
        if answer == QMessageBox.Yes:
            self.editsWereMade = True
            del self.characters[selected_idx]
            self.characters = self.characters
            self.sendButton.settingsChanged()

    def resetCharacters(self):
        """"Revert all edits to character list."""
        self.characters = self.cachedCaracters[:]
        self.editsWereMade = False
        self.resetButton.setDisabled(not self.editsWereMade)
        self.sendButton.settingsChanged()

    def checkInputValidity(self, value):
        """"Check validity of user-submitted character list entry."""
        if value == "":
            QMessageBox.warning(self, "Invalid input",
                "Please submit a nonempty string value.")
            return False
        if [item for item in value.split(", ") if item == ""]:
            QMessageBox.warning(self, "Invalid input",
                "Please make sure your entry consists in nonempty strings "
                "separated by \", \".")
            return False
        return True

    def updateButtons(self):
        """Enable/disable buttons depending on selection in list."""
        self.editButton.setDisabled(len(self.selectedCharacters) == 0)
        self.deleteButton.setDisabled(len(self.selectedCharacters) == 0)
        self.resetButton.setDisabled(not self.editsWereMade)

    def sendNoneToOutputs(self):
        """Send None token to all output channels."""
        for channel in [c.name for c in self.outputs]:
            self.send(channel, None)
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
        startPositions = [0]
        endPositions = list()
        numSegments = len(self.inputSeg)
        for idx in range(1, numSegments):
            prevSegLen = len(self.inputSeg[idx-1].get_content())
            startPositions.append(startPositions[-1] + prevSegLen + 1)
            endPositions.append(startPositions[-1] - 1)
        endPositions.append(startPositions[-1] + 
                            len(self.inputSeg[-1].get_content()) + 1)

        # Get or update character aliases...
        find_pairs = sys.modules['charnetto.find_pairs']
        characters = [entry.split(", ") for entry in self.characters]
        find_pairs.map_names(self.char_df, characters)

        # Initializations...
        charSegments = list()
        currentSegmentIdx = 0
                
        # For each character token in Charnetto's output...
        for index, charToken in self.char_df.iterrows():
        
            # Skip non-PER named entities.
            if charToken["tag"] != "PER":
                continue

            # Get index of containing segment...
            while charToken["end_pos"] > endPositions[currentSegmentIdx]:
                currentSegmentIdx += 1
                
            # Create segment for char with its actual coordinates...
            strIndex = self.inputSeg[currentSegmentIdx].str_index
            start = charToken["start_pos"]-startPositions[currentSegmentIdx]
            end = charToken["end_pos"]-startPositions[currentSegmentIdx]
            annotations = {"id": charToken["alias"]}
            charSegments.append(Segment(strIndex, start, end, annotations))
            
            progressBar.advance()

        # Send output...
        outputSegmentation = Segmentation(charSegments, 
                                           label=self.captionTitle)
        self.send("Character segmentation", outputSegmentation)
        print(outputSegmentation.to_string())

        # Set status to OK and report data size...
        message = "%i segment@p sent to output." % len(outputSegmentation)
        message = pluralize(message, len(outputSegmentation))
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
    input1 = Input("Mary said hello to John and Mike.")
    input2 = Input("Lucy told Johnny to say hello in return.")
    input = LTTL.Segmenter.concatenate([input1, input2])
    WidgetPreview(Charnetto).run(inputData=input)
