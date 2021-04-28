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
import spacy
import sklearn

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

AVAILABLE_MODELS = {
    "English web (small)": "en_core_web_sm",
    "French news (small)": "fr_core_news_sm",
    "Portuguese news (small)": "pt_core_news_sm",
}

# Determine which language models are installed...
INSTALLED_MODELS = list()
for model, package in AVAILABLE_MODELS.items():
    if importlib.util.find_spec(package.replace("-", ".")):
        INSTALLED_MODELS.append(model)

class TextSummarizer(OWTextableBaseWidget):
    """Textable widget for summarizing a segment in a selected language."""

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "TL;DR"
    description = "Summarize texts with spaCy models"
    icon = "icons/TL_DR_icon.svg"
    priority = 21   # TODO

    #----------------------------------------------------------------------
    # Channel definitions...
        
    inputs = [("Segmentation", Segmentation, "inputData")]
    outputs = [("Summary", Segmentation)]

    #----------------------------------------------------------------------
    # GUI layout parameters...
    
    want_main_area = False

    #----------------------------------------------------------------------
    # Settings 
    numSents = settings.Setting(5)
    language = settings.Setting("French")

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
        self.outputSeg = None

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
            value='numSents', #defined in settings
            label='Number of sentences : ',
            callback=self.sendButton.sendIf(),
            labelWidth=180,
            tooltip=(
                'Select the number of sentences wanted for the summary.'
            ),
            maxv=100,
            minv=1,
            step=1,
        )

        method_combo = gui.comboBox(
            widget=optionsBox,
            master=self,
            value="language",
            items=[
                "English",
                "French", 
                "Portuguese", 
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Language:",
            labelWidth=135,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                "Please select the text's language.\n"
            ),
        )

        gui.separator(widget=optionsBox, height=2)
        
        gui.rubber(self.controlArea)

        #----------------------------------------------------------------------
        # Draw Info box and Send button...
        
        self.sendButton.draw()
        self.infoBox.draw()
        self.infoBox.setText("Widget needs input.", "warning")
        
        # Check that there's a model and if not call noLanguageModelWarning()
        if not self.model:
            self.noLanguageModelWarning()



    #----------------------------------------------------------------------------

    def inputData(self, segmentation):
        """Process incoming data."""
        self.inputSeg = segmentation
        if self.inputSeg is None:
            self.infoBox.setText("Widget needs input.", "warning")
            return
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

        # Check that there's a model
        if not self.model:
            self.noLanguageModelWarning()
            return

        # Check that there's an input
        if self.inputSeg is None:
            self.infoBox.setText("Widget needs input.", "warning")
            return

        # Initialize progress bar.
        self.infoBox.setText(
            u"Processing, please wait...", 
            "warning",
        )

        self.controlArea.setDisabled(True)
       
        # Call main function 
        self.summarize() 

        # Segmentation go to outputs...
        self.send("Summary", self.outputSeg, self)

        # Set message to sent
        message = "%i segment@p sent to output " % len(self.outputSeg)
        message = pluralize(message, len(self.outputSeg))
        self.infoBox.setText(message)

        self.sendButton.resetSettingsChangedFlag()
        self.controlArea.setDisabled(False)


    def summarize(self):
        "Main function that summarize the text"
            
        num_segments = len(self.inputSeg)
        self.outputSeg = self.inputSeg

        #Itération sur chaque segment en entrée
        for idx in range(1, num_segments):
            texte = self.inputSeg[idx-1].get_content()
            if self.language == "French":
                nlpFR = spacy.load("fr_core_news_sm")
                docFR = nlpFR(texte)
                # corpus is an array that contains each sentence of the document separately
                corpus = [sent.text.lower() for sent in docFR.sents ]
                self.outputSeg = self.inputSeg
                return

            elif self.language == "English":
                nlpEN = spacy.load("en_core_web_sm")
                docEN = nlpEN(texte)
                # corpus is an array that contains each sentence of the document separately
                corpus = [sent.text.lower() for sent in docEN.sents ]
                elf.outputSeg = self.inputSeg
                return

            elif self.language == "Portuguese":
                nlpPT = spacy.load("pt_core_news_sm")
                docPT = nlpPT(texte)

                # corpus is an array that contains each sentence of the document separately
                corpus = [sent.text.lower() for sent in docPT.sents ]
                
                # Convert text to a matrix of token counts while removing STOP_WORDS that provides very little informations
                cv = CountVectorizer(stop_words=list(STOP_WORDS_PT))   
                X = cv.fit_transform(corpus) 
                word_list = cv.get_feature_names();    
                
                # Count unique words and how many times they appear
                word_list = cv.get_feature_names();    
                count_list = cv_fit.toarray().sum(axis=0)
                
                # Create dictionnary of word frequency
                word_frequency = dict(zip(word_list,count_list))

                # Get sorted dict of word frequency and print the top to test
                val=sorted(word_frequency.values())
                higher_word_frequencies = [word for word,freq in word_frequency.items() if freq in val[-3:]]

                # gets relative frequency of words to frequent words
                higher_frequency = val[-1]
                for word in word_frequency.keys():  
                    word_frequency[word] = (word_frequency[word]/higher_frequency)

                # Initialise a sentence dictionnary
                sentence_rank={}    

                # For each word in each sentence ... 
                for sent in docPT.sents:
                    for word in sent :    
                        # if the word appears in word_frequency dict
                        if word.text.lower() in word_frequency.keys(): 
                            # If the sentence is already in sentence_rank dict, we add points
                            if sent in sentence_rank.keys():
                                sentence_rank[sent]+=word_frequency[word.text.lower()]
                            # else we create a new key/value pair in dict    
                            else:
                                sentence_rank[sent]=word_frequency[word.text.lower()]

                # Sort sentences
                top_sentences=(sorted(sentence_rank.values())[::-1])
                # This is where we can choose how many sentences we want to keep for the summary
                top_sent=top_sentences[:3]  

                # We can now create a summary from those sentences:
                summary=[]
                for sent,strength in sentence_rank.items():  
                    if strength in top_sent:
                        summary.append(sent)
                    else:
                        continue
                    segments = list()
                    for sent in summary: 
                        input_seg = Input(sent)
                        segments.append(
                            Segment(
                                str_index=input_seg[0].str_index, 
                            )
                        )
                new_seg = Segmentation(segments)
                self.outputSeg = new_seg

                return


    #--------------------------------------------------------------
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