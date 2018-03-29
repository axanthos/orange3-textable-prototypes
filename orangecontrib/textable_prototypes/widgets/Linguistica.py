"""
Class Linguistica
Copyright 2018 University of Lausanne
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

__version__ = u"0.0.3"
__author__ = "Aris Xanthos"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

import collections

from Orange.widgets import widget, gui, settings

from PyQt4.QtGui import QTabWidget, QWidget

from LTTL.Segmentation import Segmentation

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar
)

from lxa5crab import find_signatures, build_parser

# Constants...
LOWER_MIN_STEM_LEN = 3
MAX_MORPH_LEN = 50


class Linguistica(OWTextableBaseWidget):
    """Textable widget for unsupervised morphology learning, using the
    "Crab Nebula" algorithm from John Golsdmith's Linguistica
    """

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Linguistica"
    description = "Unupervised morphological analysis"
    icon = "icons/linguistica.svg"
    priority = 10

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = [("Word segmentation", Segmentation, "inputData")]
    outputs = [("Morphologically analyzed data", Segmentation)]

    #----------------------------------------------------------------------
    # Layout parameters...
    
    want_main_area = True

    #----------------------------------------------------------------------
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    
    autoSend = settings.Setting(False)
    minStemLen = settings.Setting(3)
    maxSuffixLen = settings.Setting(4)
    
    def __init__(self):
        """Widget creator."""

        super().__init__()

        # Other attributes...
        self.inputSeg = None

        # Next two instructions are helpers from TextableUtils. Corresponding
        # interface elements are declared here and actually drawn below (at
        # their position in the UI)...
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute="infoBox",
            sendIfPreCallback=self.updateGUI,
        )

        # User interface...

        # Options box...
        optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box="Options",
            orientation="vertical",
        )
        gui.spin(
            widget=optionsBox,
            master=self,
            value='minStemLen',
            label='Minimum length of stems: ',
            callback=self.sendButton.sendIf,
            labelWidth=180,
            tooltip=(
                'Select the minimum number of required characters in stems'
            ),
            minv=LOWER_MIN_STEM_LEN,
            maxv=MAX_MORPH_LEN,
            step=1,
        )
        gui.separator(widget=optionsBox, height=2)

        gui.rubber(self.controlArea)
        
        self.tabs = QTabWidget()
        self.wordTab = QWidget()
        self.signatureTab = QWidget()
		
        self.tabs.addTab(self.wordTab, "Words")
        self.tabs.addTab(self.signatureTab, "Signatures")
        
        wordBox = gui.widgetBox(
            widget=self.wordTab,
            box="test",
            orientation="vertical",
        )
        
        self.mainArea.layout().addWidget(self.tabs)

        # Now Info box and Send button must be drawn...
        self.sendButton.draw()
        self.infoBox.draw()
        self.infoBox.setText("Widget needs input", "warning")
        
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
            self.send("Morphologically analyzed data", None, self)
            return

        # Perform morphological analysis...
        
        # Initialize progress bar.
        self.infoBox.setText(
            u"Processing, please wait (word count)...", 
            "warning",
        )
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=100)       
        
        # Word count...
        word_counts = collections.Counter(
            [segment.get_content() for segment in self.inputSeg]
        )
        self.infoBox.setText(
            u"Processing, please wait (signature extraction)...", 
            "warning",
        )      
        progressBar.advance(5)   # 5 ticks on the progress bar...
        
        # Learn signatures...
        try:
            signatures, stems, suffixes = find_signatures(word_counts)
        except ValueError as e:
            self.infoBox.setText(e.__str__(), "warning")
            self.send("Morphologically analyzed data", None, self)
            self.controlArea.setDisabled(False)
            progressBar.finish()   # Clear progress bar.
            return
        self.infoBox.setText(
            u"Processing, please wait (word parsing)...", 
            "warning",
        )
        progressBar.advance(80)        
        
        # Parse words...
        parser = build_parser(word_counts, signatures, stems, suffixes)
        newSegments = list()
        num_analyzed_words = 0
        for segment in self.inputSeg:
            parseDict = parser[segment.get_content()]
            newSegment = segment.deepcopy()
            stem, suffix = next(iter(parseDict))
            signature = parseDict[stem, suffix]
            if signature:
                num_analyzed_words += 1
            newSegment.annotations.update(
                {
                    "stem": stem, 
                    "suffix": suffix if len(suffix) else "NULL", 
                    "signature": signature
                }
            )
            newSegments.append(newSegment)
        self.send(
            "Morphologically analyzed data", 
            Segmentation(newSegments, self.captionTitle),
            self,
        )
        progressBar.advance(15)
        
        # Set status to OK and report data size...
        message = "%i segment@p sent to output (%.2f%% analyzed)." % (
            len(self.inputSeg),
            (num_analyzed_words / len(self.inputSeg) * 100)
        )
        message = pluralize(message, len(self.inputSeg))
        self.infoBox.setText(message)
        
        # Clear progress bar.
        progressBar.finish()
        self.controlArea.setDisabled(False)
        
        self.sendButton.resetSettingsChangedFlag()             

    def updateGUI(self):
        """Update GUI state"""
        pass          

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
    import sys
    from PyQt4.QtGui import QApplication
    myApplication = QApplication(sys.argv)
    myWidget = Linguistica()
    myWidget.show()
    myApplication.exec_()
    myWidget.saveSettings()

