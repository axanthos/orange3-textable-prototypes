"""
Class Linguistica
Copyright 2018-2019 University of Lausanne
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

__version__ = u"0.0.6"
__author__ = "Aris Xanthos"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

import collections
import itertools

from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview

from PyQt4.QtGui import QTabWidget, QWidget, QFont, QHBoxLayout

from LTTL.Segmentation import Segmentation

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar
)

import lxa5crab

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
    priority = 21

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
        self.selectedMainSignature = None
        self.mainSignatures = list()
        self.wordsForSig = list()
        self.stemsForSig = list()
        self.suffixesForSig = list()

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
        wordTabBox = QHBoxLayout()
        wordBox = gui.widgetBox(
            widget=self.wordTab,
            orientation="horizontal",
            margin=5,
        )
        
        wordBoxRight = gui.widgetBox(widget=wordBox)
        
        self.mainWordListbox = gui.listBox(
            widget=wordBoxRight,
            master=self,
            value="selectedMainWord", 
            labels="mainWords",
            callback=self.mainWordSelected,
            tooltip="Select a word to display its possible parses.",
        )
        self.mainWordListbox.setFont(font)

        gui.separator(widget=wordBox, width=3)

        wordBoxLeft = gui.widgetBox(widget=wordBox)
        
        gui.label(
            widget=wordBoxLeft, 
            master=self,
            label="Parse(s):",
        )
        
        self.parsesListbox = gui.listBox(
            widget=wordBoxLeft,
            master=self,
            value="selectedParse", 
            labels="parses",
            callback=self.parseSelected,
            tooltip="Select a parse to display the corresponding signature.",
        )
        self.parsesListbox.setFont(font)
        
        self.sigForParseBox = gui.widgetBox(
            widget=wordBoxLeft,
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
            labels="stemsForParse",
            tooltip="Stems associated with the parse selected above.",
        )
        
        gui.separator(widget=self.sigForParseBox, height=2)

        gui.label(
            widget=self.sigForParseBox, 
            master=self,
            label="Suffixes(s):",
        )
        
        self.suffixesForParseListbox = gui.listBox(
            widget=self.sigForParseBox,
            master=self,
            labels="suffixesForParse",
            tooltip="Suffixes associated with the parse selected above.",
        )
        
        wordTabBox.addWidget(wordBox)
        self.wordTab.setLayout(wordTabBox)

        # Signature tab...
        signatureTabBox = QHBoxLayout()

        signatureBox = gui.widgetBox(
            widget=self.signatureTab,
            orientation="horizontal",
            margin=5,
        )
        
        signatureBoxRight = gui.widgetBox(widget=signatureBox)

        self.mainSignatureListbox = gui.listBox(
            widget=signatureBoxRight,
            master=self,
            value="selectedMainSignature", 
            labels="mainSignatures",
            callback=self.mainSignatureSelected,
            tooltip="Select a signature to display its contents.",
        )
        self.mainSignatureListbox.setFont(font)

        gui.separator(widget=signatureBox, width=3)

        signatureBoxLeft = gui.widgetBox(widget=signatureBox)
        
        gui.label(
            widget=signatureBoxLeft, 
            master=self,
            label="Words:",
        )
        
        self.wordsForSigListbox = gui.listBox(
            widget=signatureBoxLeft,
            master=self,
            labels="wordsForSig",
            tooltip="Words associated with the selected signature.",
        )
        self.wordsForSigListbox.setFont(font)
        
        gui.label(
            widget=signatureBoxLeft, 
            master=self,
            label="Stem(s):",
        )
        
        self.stemsForSigListbox = gui.listBox(
            widget=signatureBoxLeft,
            master=self,
            labels="stemsForSig",
            tooltip="Stems associated with the selected signature.",
        )
        self.stemsForSigListbox.setFont(font)
        
        gui.label(
            widget=signatureBoxLeft, 
            master=self,
            label="Suffixes(s):",
        )
        
        self.suffixesForSigListbox = gui.listBox(
            widget=signatureBoxLeft,
            master=self,
            labels="suffixesForSig",
            tooltip="Suffixes associated with the selected signature.",
        )
        self.suffixesForSigListbox.setFont(font)

        signatureTabBox.addWidget(signatureBox)
        self.signatureTab.setLayout(signatureTabBox)

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
        
    def mainSignatureSelected(self):
        """Display selected signature and generated words."""
        # Return if no selected signature...
        if len(self.selectedMainSignature) == 0:
            self.wordsForSig = list()
            return
        
        # Get generated words (by decreasing frequency)...
        sigs = self.morphology["signatures"]
        if self.selectedMainSignature[0] == 0:
            words = sorted([
                w for w in self.morphology["wordCounts"].keys() 
                if self.morphology["parser"][w][0].signature == 0
            ])          
        else:
            su = list(sigs.keys())[self.selectedMainSignature[0]-1]
            words = ["".join(pair) for pair in itertools.product(sigs[su], su)]
        words.sort(key=self.morphology["wordCounts"].get, reverse=True)

        # Display generated words...
        max_count = self.morphology["wordCounts"][words[0]]
        padding = len(str(max_count))+1
        self.wordsForSig = [
            '{num: {width}} {word}'.format(
                num=self.morphology["wordCounts"][word],
                width=padding,
                word=word,
            )
            for word in words
        ]
        
        # Display stems and suffixes in signature...
        if self.selectedMainSignature[0] > 0:
            suffixes = list(sigs.keys())[self.selectedMainSignature[0]-1]
            self.suffixesForSig = [suffix or "NULL" for suffix in suffixes]
            self.stemsForSig = sigs[suffixes]
        else:
            self.suffixesForSig = ["NULL"]
            self.stemsForSig = sorted(words[:])

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
        self.selectedParse = [0]
        self.parseSelected()

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
            self.sigForParseBox.setTitle(" Signature 0 ")
            self.suffixesForParse = ["NULL"]
            self.stemsForParse = sorted([
                w for w in words 
                if self.morphology["parser"][w][0].signature == 0
            ])

    def sendData(self):
        """Compute result of widget processing and send to output"""

        # Clear morphology...
        self.morphology = dict()
        
        # Check that there's an input...
        if self.inputSeg is None:
            self.infoBox.setText("Widget needs input", "warning")
            self.send("Morphologically analyzed data", None)
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
            lxa5crab.crab_nebula.MIN_STEM_LEN = self.minStemLen
            signatures, stems, suffixes = lxa5crab.find_signatures(wordCounts)
            self.morphology["signatures"] = signatures
            self.morphology["stems"] = stems
            self.morphology["suffixes"] = suffixes
        except ValueError as e:
            self.infoBox.setText(e.__str__(), "warning")
            self.send("Morphologically analyzed data", None)
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
        parser = lxa5crab.build_parser(wordCounts, signatures, stems, suffixes)
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
        self.mainSignatures = list()
        self.wordsForSig = list()
        self.stemsForSig = list()
        self.suffixesForSig = list()
        
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
            
            # Main signature list...
            sigs = [["NULL"]] + list(self.morphology["signatures"].keys())
            padding = len(str(len(sigs)))+1
            self.mainSignatures = [
                '{num: {width}} {sig}'.format(
                    num=idx,
                    width=padding,
                    sig=", ".join(
                        [suff or "NULL" for suff in sig]
                    )
                )
                for idx, sig in enumerate(sigs)
            ]
            

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
    #import sys
    #from PyQt5.QtWidgets import QApplication
    #myApplication = QApplication(sys.argv)
    #myWidget = Linguistica()
    #myWidget.show()
    #myApplication.exec_()
    #myWidget.saveSettings()
    from LTTL.Input import Input
    import LTTL.Segmenter as Segmenter
    import re
    example=Input("rosa rosa rosam rosae rosae rosa rosae rosae rosas rosarum rosis rosis")
    segments = Segmenter.tokenize(example, [(re.compile(r"\w+"), "tokenize")])
    WidgetPreview(Linguistica).run(inputData=Input(segments))
