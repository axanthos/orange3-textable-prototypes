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
__author__ = "Noémie Carette", "Saara Jones", "Sorcha Walsh"
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

import csv


class ExtractCSV(OWTextableBaseWidget):
    """Textable widget for NLP using spaCy."""

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "ExtractCSV"
    description = "Extract tabulated data as a Textable Segmentation"
    icon = "icons/spacy.svg"
    priority = 21   # TODO

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = [("Text data", Segmentation, "inputData")]
    outputs = [("CSV Data", Segmentation)]

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
        self.dialect = None

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

        # User interface will go here
        
        
        # Send data if autoSend.
        self.sendButton.sendIf()

    def inputData(self, newInput):
        """Process incoming data."""
        self.inputSeg = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()
  

    def sendData(self):
        """Compute result of widget processing and send to output"""

        # Check that there's an input...
        if self.inputSeg is None:
            self.infoBox.setText("Widget needs input", "warning")
            self.send("CSV data", None, self)
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



            progressBar.advance()

                 
        # Set status to OK and report data size...
        message = "Did something"
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
