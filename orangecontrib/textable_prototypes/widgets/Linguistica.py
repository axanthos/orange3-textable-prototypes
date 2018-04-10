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

from PyQt4.QtGui import QTabWidget, QWidget, QFont

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
        self.morphology = dict()
        self.selectedMainWord = None
        self.mainWords = list()
        self.selectedParse = None
        self.parses = list()
        self.selectedStemForParse = None
        self.stemsForParse = list()
        self.selectedSuffixForParse = None
        self.suffixesForParse = list()

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

        # A) Control area...
        
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
        
        # B) Main area...
        
        font = QFont()
        font.setFamily('Courier')
        font.setStyleHint(QFont.Courier)
        font.setPixelSize(12)

        # Tabs...
        self.tabs = QTabWidget()
        self.wordTab = QWidget()
        self.signatureTab = QWidget()		
        self.tabs.addTab(self.wordTab, "Words")
        self.tabs.addTab(self.signatureTab, "Signatures")
        
        # Words tab...
        wordBox = gui.widgetBox(
            widget=self.wordTab,
            orientation="horizontal",
            margin=5,
        )
        
        self.mainWordListbox = gui.listBox(
            widget=wordBox,
            master=self,
            value="selectedMainWord", 
            labels="mainWords",
            callback=self.mainWordSelected,
            tooltip="Select a word to display its possible parses.",
        )
        self.mainWordListbox.setMinimumHeight(260)
        self.mainWordListbox.setMaximumHeight(260)
        self.mainWordListbox.setFont(font)

        gui.separator(widget=wordBox, height=3)

        parsesBox = gui.widgetBox(widget=wordBox)
        
        gui.label(
            widget=parsesBox, 
            master=self,
            label="Parse(s):",
        )
        
        self.parsesListbox = gui.listBox(
            widget=parsesBox,
            master=self,
            value="selectedParse", 
            labels="parses",
            callback=self.parseSelected,
            tooltip="Select a parse to display the corresponding signature.",
        )
        self.parsesListbox.setMaximumHeight(55)
        self.parsesListbox.setFont(font)
        
        self.sigForParseBox = gui.widgetBox(
            widget=parsesBox,
            box="Signature",
        )
        
        gui.label(
            widget=self.sigForParseBox, 
            master=self,
            label="Stem(s):",
        )
        
        self.stemsForParseListbox = gui.listBox(
            widget=self.sigForParseBox,
            master=self,
            value="selectedStemForParse", 
            labels="stemsForParse",
            callback=None,
            tooltip="TODO.",
        )
        self.stemsForParseListbox.setMaximumHeight(50)
        
        gui.label(
            widget=self.sigForParseBox, 
            master=self,
            label="Suffixes(s):",
        )
        
        self.suffixesForParseListbox = gui.listBox(
            widget=self.sigForParseBox,
            master=self,
            value="selectedSuffixForParse", 
            labels="suffixesForParse",
            callback=None,
            tooltip="TODO.",
        )
        self.suffixesForParseListbox.setMaximumHeight(50)
        
        gui.rubber(parsesBox)

        self.mainArea.layout().addWidget(self.tabs)

        # Now Info box and Send button must be drawn...
        self.sendButton.draw()
        self.infoBox.draw()
        self.infoBox.setText("Widget needs input", "warning")

        self.setMinimumWidth(602)
        self.setMinimumHeight(317)
        self.adjustSizeWithTimer()
        
        # Send data if autoSend.
        self.sendButton.sendIf()

    def inputData(self, newInput):
        """Process incoming data."""
        self.inputSeg = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()
        
    def mainWordSelected(self):
        """Display possible parses for selected word."""

        self.sigForParseBox.setTitle(" Signature ")

        # Return if no selected word...
        if len(self.selectedMainWord) == 0:
            self.parses = list()
            return
        
        # Get selected word's parses...
        words = list(self.morphology["wordCounts"].keys())
        words.sort(key=self.morphology["wordCounts"].get, reverse=True)
        parses = self.morphology["parser"][
            words[self.selectedMainWord[0]]
        ]
        
        # Display parses...
        self.parses = [
            '{score:.2f} {stem} + {suffix}'.format(
                score=parse.score,
                stem=parse.stem,
                suffix=parse.suffix if parse.suffix else "NULL",
            )
            for parse in parses
        ]

    def parseSelected(self):
        """Display selected parse's signature."""
        # Return if no selected parse...
        if len(self.selectedParse) == 0:
            self.stemsForParse = list()
            self.suffixesForParse = list()
            return
        
        # Get selected parse's signature...
        words = list(self.morphology["wordCounts"].keys())
        words.sort(key=self.morphology["wordCounts"].get, reverse=True)
        parses = self.morphology["parser"][
            words[self.selectedMainWord[0]]
        ]
        parse = parses[self.selectedParse[0]]
        sigNum = parse.signature
        
        # Display stems and suffixes in parse's signature...
        if sigNum > 0:
            self.sigForParseBox.setTitle(" Signature {} ".format(sigNum))
            signatures = list(self.morphology["signatures"].keys())
            self.suffixesForParse = [
                suffix or "NULL" for suffix in signatures[sigNum-1]
            ]
            self.stemsForParse =    \
                self.morphology["signatures"][signatures[sigNum-1]]
        else:
            self.sigForParseBox.setTitle(" Signature ")
            self.suffixesForParse = list()
            self.stemsForParse = list()

    def sendData(self):
        """Compute result of widget processing and send to output"""

        # Clear morphology...
        self.morphology = dict()
        
        # Check that there's an input...
        if self.inputSeg is None:
            self.infoBox.setText("Widget needs input", "warning")
            self.send("Morphologically analyzed data", None, self)
            self.updateGUI()
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
        wordCounts = collections.Counter(
            [segment.get_content() for segment in self.inputSeg]
        )
        self.morphology["wordCounts"] = wordCounts
        self.infoBox.setText(
            u"Processing, please wait (signature extraction)...", 
            "warning",
        )      
        progressBar.advance(5)   # 5 ticks on the progress bar...
        
        # Learn signatures...
        try:
            signatures, stems, suffixes = find_signatures(wordCounts)
            self.morphology["signatures"] = signatures
            self.morphology["stems"] = stems
            self.morphology["suffixes"] = suffixes
        except ValueError as e:
            self.infoBox.setText(e.__str__(), "warning")
            self.send("Morphologically analyzed data", None, self)
            self.controlArea.setDisabled(False)
            progressBar.finish()   # Clear progress bar.
            self.morphology = dict()
            self.updateGUI()
            return
        self.infoBox.setText(
            u"Processing, please wait (word parsing)...", 
            "warning",
        )
        progressBar.advance(80)        
        
        # Parse words...
        parser = build_parser(wordCounts, signatures, stems, suffixes)
        self.morphology["parser"] = parser
        newSegments = list()
        num_analyzed_words = 0
        for segment in self.inputSeg:
            parses = parser[segment.get_content()]
            newSegment = segment.deepcopy()
            if parses[0].signature:
                num_analyzed_words += 1
            newSegment.annotations.update(
                {
                    "stem": parses[0].stem, 
                    "suffix": parses[0].suffix  \
                                if len(parses[0].suffix) else "NULL", 
                    "signature": parses[0].signature
                }
            )
            newSegments.append(newSegment)
        self.send(
            "Morphologically analyzed data", 
            Segmentation(newSegments, self.captionTitle),
            self,
        )
        self.updateGUI()
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
        
        # Empty lists...
        self.mainWords = list()
        self.parses = list()
        self.stemsForParse = list()
        self.suffixesForParse = list()
        self.sigForParseBox.setTitle(" Signature ")
        
        # Fill main lists if necessary...
        if len(self.morphology):
        
            # Main word list...
            words = list(self.morphology["wordCounts"].keys())
            words.sort(key=self.morphology["wordCounts"].get, reverse=True)
            max_count = self.morphology["wordCounts"][words[0]]
            padding = len(str(max_count))+1
            self.mainWords = [
                '{num: {width}} {word}'.format(
                    num=self.morphology["wordCounts"][word],
                    width=padding,
                    word=word,
                )
                for word in words
            ]
            
            # self.mainWords = list()
            # self.selectedParse = None
            # self.parses = list()
            # self.selectedStemForParse = None
            # self.stemsForParse = list()
            # self.selectedSuffixForParse = None
            # self.suffixesForParse = list()

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

