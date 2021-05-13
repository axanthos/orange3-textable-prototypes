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
import sys
import importlib.util
import sys
import os
import subprocess
import platform
import spacy
from sklearn.feature_extraction.text import CountVectorizer

from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview

from AnyQt.QtGui import (
    QTabWidget, QWidget, QHBoxLayout, QMessageBox, QIntValidator
)

from LTTL.Segmentation import Segmentation
from LTTL.Segment import Segment
import LTTL.Segmenter
from LTTL.Input import Input


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
    priority = 21 

    #----------------------------------------------------------------------
    # Channel definitions...
        
    inputs = [("Segmentation", Segmentation, "inputData")]
    outputs = [("Summary", Segmentation)]

    #----------------------------------------------------------------------
    # GUI layout parameters...
    
    want_main_area = False

    #----------------------------------------------------------------------
    # Settings - defines set values when opening widget

    numSents = settings.Setting(5)
    language = settings.Setting("French")
    typeSeg =  settings.Setting("Summarize each segments individually")
    percentage = settings.Setting(20)
    method = settings.Setting("Number of sentences")

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

        lenghtBox = gui.widgetBox(
            widget=self.controlArea,
            box="Summary's lenght options",
            orientation="vertical",
        )
        gui.spin(
            widget=lenghtBox,
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
        optionsPercentage = gui.spin(
            widget=lenghtBox,
            master=self,
            value='percentage',
            label='Length in %',
            callback=self.sendButton.sendIf(),
            labelWidth=180,
            tooltip=(
                'Select the length of the summary in percentage of the input text.'
            ),
            maxv= 99,
            minv=1,
            step=1,
        )
        lenght_method = gui.comboBox(
            widget=lenghtBox,
            master=self,
            value="method",
            items=[
                "Number of sentences",
                "Percentage of text lenght", 
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Method:",
            labelWidth=135,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                "How do you want to choose the summary's lenght ?"
            ),
        )

        optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box="More options",
            orientation="vertical",
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
        method_segment = gui.comboBox(
            widget= optionsBox,
            master=self,
            value= "typeSeg",
            items = [
                "Summarize all segments as one",
                "Summarize each segments individually",
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label= "Segmentation",
            labelWidth=135,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                "Please select the method. \n"
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

    def checkNumSentWarning(self, doc):
        """Warns user if the summary's sentences' number is bigger than the input's sentences' number."""
        if self.method == "Number of sentences":
            count = 0
            for sent in doc.sents:
                count += 1
            print(count)    
            if self.numSents > count:
                print(count)
                self.infoBox.setText("The summary's sentences' number needs to be smaller than the input's sentences' number.", "warning")



    ################################################################
    # Triggered when send button is clicked
    ################################################################

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
       
       # Load the appropriate model according to user choice
        if self.language == "French":
            cv = self.loadModelFR()
        elif self.language == "English":
            cv = self.loadModelEN()
        elif self.language == "Portuguese":
            cv = self.loadModelPT()


        # Type of segmentation (per segment or per segmentation)
        segments = list()
        if self.typeSeg == "Summarize each segments individually":
            # Process each segment separately, then create segmentation 
            for segment in self.inputSeg: 
                content = segment.get_content() 
                resume = self.summarize(cv, content)
                segments.append(
                    Segment(
                        str_index=resume[0].str_index,   
                    )
                )
        elif self.typeSeg == "Summarize all segments as one":
            merged_seg = " ".join([segment.get_content() for segment in self.inputSeg])
            resume = self.summarize(cv, merged_seg)
            segments.append(
                    Segment(
                        str_index=resume[0].str_index,   
                    )
                )
        # Create segmentation from segment() and assign it to the output
        self.outputSeg = Segmentation(segments)

        # 
        # Segmentation go to outputs...
        self.send("Summary", self.outputSeg, self)

        # Set message to sent
        message = "%i segment@p sent to output " % len(self.outputSeg)
        message = pluralize(message, len(self.outputSeg))
        self.infoBox.setText(message)

        self.sendButton.resetSettingsChangedFlag()
        self.controlArea.setDisabled(False)




    ################################################################
    # Main function
    ################################################################

    def summarize(self, cv, content):
        "Main function that summarize the text"

        doc = self.nlp(content)

        # Check if the sentence number is right
        if self.checkNumSentWarning(doc):
            return

        corpus = [sent.text.lower() for sent in doc.sents]
        cv_fit = cv.fit_transform(corpus) 

        # Count unique words and how many times they appear
        word_list = cv.get_feature_names();    
        count_list = cv_fit.toarray().sum(axis=0)
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
        for sent in doc.sents:
            count = 0
            for word in sent :
                count += 1
                # if the word appears in word_frequency dict
                if word.text.lower() in word_frequency.keys(): 
                    # If the sentence is already in sentence_rank dict, we add points
                    if sent in sentence_rank.keys():
                        sentence_rank[sent]+=word_frequency[word.text.lower()]
                    # else we create a new key/value pair in dict    
                    else:
                        sentence_rank[sent]=word_frequency[word.text.lower()]
                        
            # Normalize: divide score of current sentence by number of words 
            if sentence_rank.get(sent, None) != None: 
                sentence_rank[sent] = (sentence_rank.get(sent) / count)
                        

        # Sort sentences
        top_sentences=(sorted(sentence_rank.values())[::-1])
        # This is where we can choose how many sentences we want to keep for the summary
        top_sent=top_sentences[:self.numSents]

        summary = list()
        for sent,strength in sentence_rank.items():  
            if strength in top_sent:
                summary.append(sent)
            else:
                continue
        
        #Summary contains spacy.tokens.span.Span that must be converted to string
        summary_str = [str(i) for i in summary]

        # Join all sentence in a single string
        resume = " ".join(summary_str)

        # Create ouput segmentation from summary
        return Input(resume)
        
        



    ################################################################
    # loadmodelEN(), loadmodelFR() and loadmodelPT() load choosen model
    ################################################################

    def loadModelEN(self):
        """(Re-)load language model if needed."""
        # Initialize progress bar.
        self.infoBox.setText(
            u"Loading english language model, please wait...", 
            "warning",
        )
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=1)       
        self.nlp = spacy.load(
            "en_core_web_sm"
        )

        # Get the list of stop_words that will not be counted
        from spacy.lang.en.stop_words import STOP_WORDS
        cv = CountVectorizer(stop_words=list(STOP_WORDS))

        # Advance and finish progress bar + make buttons available
        progressBar.advance()
        progressBar.finish()
        self.controlArea.setDisabled(False)

        return cv

    def loadModelFR(self):
        """(Re-)load language model if needed."""
        # Initialize progress bar.
        self.infoBox.setText(
            u"Loading french language model, please wait...", 
            "warning",
        )
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=1)       
        self.nlp = spacy.load(
            "fr_core_news_sm"
        )

        # Get the list of stop_words that will not be counted
        from spacy.lang.fr.stop_words import STOP_WORDS
        cv = CountVectorizer(stop_words=list(STOP_WORDS))

        # Advance and finish progress bar + make buttons available
        progressBar.advance()
        progressBar.finish()
        self.controlArea.setDisabled(False)

        return cv
        
    def loadModelPT(self):
        """(Re-)load language model if needed."""
        # Initialize progress bar.
        self.infoBox.setText(
            u"Loading portuguese language model, please wait...", 
            "warning",
        )
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=1)       
        self.nlp = spacy.load(
            "pt_core_web_sm"
        )

        # Advance and finish progress bar + make buttons available
        from spacy.lang.pt.stop_words import STOP_WORDS
        cv = CountVectorizer(stop_words=list(STOP_WORDS))

        # Advance and finish progress bar + make buttons available
        progressBar.advance()
        progressBar.finish()
        self.controlArea.setDisabled(False)

        return cv


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
