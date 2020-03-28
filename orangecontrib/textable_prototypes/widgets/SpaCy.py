"""
Class SpaCy
Copyright 2020 University of Lausanne
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


from Orange.widgets import gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview

from AnyQt.QtGui import QTabWidget, QWidget, QHBoxLayout

from LTTL.Segmentation import Segmentation
from LTTL.Segment import Segment
import LTTL.Segmenter

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar
)

import spacy

# Global variables...
RELEVANT_KEYS = [
   'dep_', 'ent_iob_', 'ent_type_', 'head', 'is_alpha', 'is_bracket', 
   'is_digit', 'is_left_punct', 'is_lower', 'is_oov', 'is_punct', 'is_quote', 
   'is_right_punct', 'is_sent_start', 'is_space', 'is_stop', 'is_title', 
   'is_upper', 'lang_', 'lemma_', 'like_email', 'like_num', 'like_url', 
   'lower_', 'norm_', 'pos_', 'sentiment', 'shape_', 'tag_', 'whitespace_',
]
AVAILABLE_MODELS = [
    "en_core_web_sm",
    "fr_core_news_sm",
]
INSTALLED_MODELS = list()   # TODO: determine installed models automatically.

# Temporary code to ensure that 2 models are downloaded for dev purposes...
for model in AVAILABLE_MODELS:
    try:
        spacy.load(model)
    except OSError:
        spacy.cli.download(model, "--user")
INSTALLED_MODELS = AVAILABLE_MODELS


class SpaCy(OWTextableBaseWidget):
    """Textable widget for NLP using spaCy."""

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "spaCy"
    description = "Natural language processing using spaCy"
    icon = "icons/spacy.svg"
    priority = 21   # TODO

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = [("Text data", Segmentation, "inputData")]
    outputs = [("Linguistically analyzed data", Segmentation)]

    #----------------------------------------------------------------------
    # Layout parameters...
    
    want_main_area = False

    #----------------------------------------------------------------------
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    
    autoSend = settings.Setting(False)
    model = settings.Setting("fr_core_news_sm")
    
    def __init__(self):
        """Widget creator."""

        super().__init__()

        # Other attributes...
        self.inputSeg = None
        self.nlp = None

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

        # User interface...

        # Tabs...
        self.tabs = QTabWidget()
        self.optionsTab = QWidget()
        self.modelManagerTab = QWidget()		
        self.tabs.addTab(self.optionsTab, "Options")
        self.tabs.addTab(self.modelManagerTab, "Model manager")
        
        # Options tab...
        OptionsTabBox = QHBoxLayout()
        
        optionsBox = gui.widgetBox(widget=self.optionsTab)

        self.modelComboBox = gui.comboBox(
            widget=optionsBox,
            master=self,
            value='model',
            label='Model: ',
            tooltip='Select the spaCy language model you want to use.',
            items=INSTALLED_MODELS,
            sendSelectedValue=True,
            callback=self.modelChanged,
        )
        
        OptionsTabBox.addWidget(optionsBox)
        self.optionsTab.setLayout(OptionsTabBox)

        # Model manager tab...
        modelManagerTabBox = QHBoxLayout()

        modelManagerBox = gui.widgetBox(widget=self.modelManagerTab)
        
        # TODO: Model manager UI
        
        modelManagerTabBox.addWidget(modelManagerBox)
        self.modelManagerTab.setLayout(modelManagerTabBox)

        self.controlArea.layout().addWidget(self.tabs)

        gui.rubber(self.controlArea)

        # Now Info box and Send button must be drawn...
        self.sendButton.draw()
        self.infoBox.draw()
        self.infoBox.setText("Widget needs input", "warning")

        # Load spaCy language model...
        self.modelChanged()
        
        # Send data if autoSend.
        self.sendButton.sendIf()

    def inputData(self, newInput):
        """Process incoming data."""
        self.inputSeg = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def modelChanged(self):
        """Respond to model change in UI."""
        self.nlp = spacy.load(self.model)
        self.sendButton.settingsChanged()        

    def sendData(self):
        """Compute result of widget processing and send to output"""

        # Check that there's an input...
        if self.inputSeg is None:
            self.infoBox.setText("Widget needs input", "warning")
            self.send("Linguistically analyzed data", None, self)
            return

        # Initialize progress bar.
        self.infoBox.setText(
            u"Processing, please wait...", 
            "warning",
        )
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=len(self.inputSeg))       
        
        tokenizedSegments = list()

        # Process each input segment...
        for segment in self.inputSeg:
        
            # Input segment attributes...
            inputContent = segment.get_content()
            inputAnnotations = segment.annotations
            inputString = segment.str_index
            inputStart = segment.start or 0
            inputEnd = segment.end or len(inputContent)

            # NLP analysis...
            doc = self.nlp(inputContent)

            # Process each token in input segment...
            for token in doc:
                tokenAnnotations = inputAnnotations.copy()
                tokenAnnotations.update(
                    {
                        k: getattr(token, k) for k in RELEVANT_KEYS
                        if getattr(token, k) is not None
                    }
                )
                tokenStart = inputStart+token.idx
                tokenizedSegments.append(
                    Segment(
                        str_index=inputString,
                        start=tokenStart,
                        end=tokenStart+len(token),
                        annotations=tokenAnnotations,
                    )
                )

            progressBar.advance()

        outputSeg = Segmentation(tokenizedSegments, self.captionTitle)
                 
        # Set status to OK and report data size...
        message = "%i segment@p sent to output." % len(outputSeg)
        message = pluralize(message, len(outputSeg))
        self.infoBox.setText(message)
        
        print(outputSeg.to_string())
        
        # Clear progress bar.
        progressBar.finish()
        self.controlArea.setDisabled(False)
        
        # Send data to output...
        self.send("Linguistically analyzed data", outputSeg, self)
        
        self.sendButton.resetSettingsChangedFlag()             

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
    WidgetPreview(SpaCy).run(inputData=Input("a simple example"))
