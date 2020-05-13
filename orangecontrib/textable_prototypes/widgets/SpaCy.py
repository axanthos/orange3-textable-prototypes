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

__version__ = u"0.0.2"
__author__ = "Aris Xanthos"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

import importlib.util
import sys
import os
import subprocess

from Orange.widgets import gui, settings
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

# Global variables...
RELEVANT_KEYS = [
   'dep_', 'ent_iob_', 'ent_type_', 'head', 'is_alpha', 'is_bracket', 
   'is_digit', 'is_left_punct', 'is_lower', 'is_oov', 'is_punct', 'is_quote', 
   'is_right_punct', 'is_sent_start', 'is_space', 'is_stop', 'is_title', 
   'is_upper', 'lang_', 'lemma_', 'like_email', 'like_num', 'like_url', 
   'lower_', 'norm_', 'pos_', 'sentiment', 'shape_', 'tag_', 'whitespace_',
]
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
MODEL_VERSION_NUM = "2.2.5"
DOWNLOAD_URL = "https://github.com/explosion/spacy-models/releases/download/"

# Determine which language models are installed...
INSTALLED_MODELS = list()
DOWNLOADABLE_MODELS = list()
for model, package in AVAILABLE_MODELS.items():
    if importlib.util.find_spec(package.replace("-", ".")):
        INSTALLED_MODELS.append(model)
    else:
        DOWNLOADABLE_MODELS.append(model)


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
    
    maxLen = settings.Setting(1000000)

    autoSend = settings.Setting(False)
    if INSTALLED_MODELS:
        model = settings.Setting(INSTALLED_MODELS[0])
    else:
        model = settings.Setting("")
    
    def __init__(self):
        """Widget creator."""

        super().__init__()

        # Other attributes...
        self.inputSeg = None
        self.nlp = None
        self.selectedModels = list()
        self.downloadableModelLabels = list()

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
            items=INSTALLED_MODELS[:],
            sendSelectedValue=True,
            callback=self.modelComboboxChanged,
        )

        gui.separator(widget=optionsBox, height=3)

        gui.comboBox(
            widget=optionsBox,
            master=self,
            value='maxLen',
            items=["1 million"] + ["%i millions" % l for l in range(2, 10)]   \
                  + ["no limit"],
            sendSelectedValue=True,
            label=u'Max number of input characters:',
            tooltip=(
                "The spaCy parser and NER models require roughly 1GB of\n"
                "temporary memory per 100'000 characters in the input.\n"
                "This means long texts may cause memory allocation errors.\n"
                "If you're not using the parser or NER, or half lots of \n"
                "RAM, it's probably safe to increase the default limit of\n"
                "1 million characters."
            ),
        )
        gui.rubber(optionsBox)

        OptionsTabBox.addWidget(optionsBox)
        self.optionsTab.setLayout(OptionsTabBox)

        # Model manager tab...
        modelManagerTabBox = QHBoxLayout()

        modelManagerBox = gui.widgetBox(widget=self.modelManagerTab)
               
        gui.label(modelManagerBox, self, label="Available models:")
        
        self.downloadableModelsListbox = gui.listBox(
            widget=modelManagerBox,
            master=self,
            value="selectedModels",
            labels="downloadableModelLabels",
            callback=self.downloadableModelsListboxChanged,
            tooltip="Select language models then click Download.",
        )
        self.downloadableModelsListbox.setSelectionMode(3)
        self.downloadableModelLabels = DOWNLOADABLE_MODELS[:]
        self.downloadableModelLabels = self.downloadableModelLabels
        
        self.downloadButton = gui.button(
            widget=modelManagerBox,
            master=self,
            label="Download",
            callback=self.downloadModels,
            tooltip="Download the selected language models.",
        )
        self.downloadButton.setDisabled(True)
        
        modelManagerTabBox.addWidget(modelManagerBox)
        self.modelManagerTab.setLayout(modelManagerTabBox)

        self.controlArea.layout().addWidget(self.tabs)

        gui.rubber(self.controlArea)

        # Now Info box and Send button must be drawn...
        self.sendButton.draw()
        self.infoBox.draw()
        self.infoBox.setText("Widget needs input", "warning")

        # Load spaCy language model...
        if self.model:
            self.modelComboboxChanged()
            # Send data if autoSend.
            self.sendButton.sendIf()
        else:
            self.infoBox.setText(
                "Please download a language model.",
                "warning",
            )
            self.tabs.setCurrentIndex(1)

    def inputData(self, newInput):
        """Process incoming data."""
        self.inputSeg = newInput
        if self.model:
            self.infoBox.inputChanged()
            self.sendButton.sendIf()
        else:
            self.infoBox.setText(
                "Please download a language model.",
                "warning",
            )
            self.tabs.setCurrentIndex(1)
                  
    def modelComboboxChanged(self):
        """Respond to model change in UI (Options tab)."""
        self.infoBox.setText(
            u"Loading language model, please wait...", 
            "warning",
        )
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=1)       
        self.nlp = spacy.load(AVAILABLE_MODELS[self.model])
        self.nlp.max_length = self.maxLen
        progressBar.finish()
        self.controlArea.setDisabled(False)
        self.sendButton.settingsChanged()              

    def downloadableModelsListboxChanged(self):
        """Respond to model change in UI (Model manager tab)."""
        self.downloadButton.setDisabled(len(self.selectedModels) == 0)        

    def downloadModels(self):
        """Respond to Download button (Model manager tab)."""
        global INSTALLED_MODELS

        # Ask for confirmation...
        num_models = len(self.selectedModels)
        message = "Your are about to download %i language model@p. " +   \
                  "This may take up to several minutes depending on your " +  \
                  "internet connection. Do you want to proceed?"
        message = message % num_models
        buttonReply = QMessageBox.question(
            self, 
            "Textable", 
            pluralize(message, num_models),
            QMessageBox.Ok | QMessageBox.Cancel
        )
        if buttonReply == QMessageBox.Cancel:
            return
            
        # Download models...
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=num_models)       
        for model_idx in reversed(self.selectedModels):
            model = self.downloadableModelLabels[model_idx]
            download_spacy_model(AVAILABLE_MODELS[model])
            del self.downloadableModelLabels[model_idx]
            progressBar.advance()
            
        # Update GUI...
        self.downloadableModelLabels = self.downloadableModelLabels
        self.selectedModels = list()
        progressBar.finish()
        self.controlArea.setDisabled(False)
        message = "Downloaded %i language model@p, please restart " +   \
                  "Orange for changes to take effect."
        message = message % num_models
        QMessageBox.information(
            None,
            "Textable",
            pluralize(message, num_models),
            QMessageBox.Ok
        )

    def sendData(self):
        """Compute result of widget processing and send to output"""

        # Check that there's a model...
        if not self.model:
            self.infoBox.setText(
                "Please download a language model first.",
                "warning",
            )
            self.tabs.setCurrentIndex(1)
            return
            
        # Check that there's an input...
        if self.inputSeg is None:
            self.infoBox.setText("Widget needs input", "warning")
            self.send("Linguistically analyzed data", None, self)
            return

        # Check max length and adjust if needed...
        inputLength = sum(len(s.get_content()) for s in self.inputSeg)
        if self.maxLen != "no limit":
            self.nlp.max_length = int(self.maxLen.split()[0]) * 1000000
            if inputLength > self.nlp.max_length:
                self.infoBox.setText(
                    "Input exceeds max number of characters set by user.", 
                    "warning",
                )
                self.send("Linguistically analyzed data", None, self)
                return
        else:
            if inputLength > self.nlp.max_length:
                self.nlp.max_length = inputLength          

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
                        and getattr(token, k) is not ""
                        
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


# This is really a hack: Orange is normally run with pythonw.exe, but spaCy's
# functions for downloading a model only work with python.exe (somehow!), so
# the following function is reimplemented here to use python.exe anyway.
def download_spacy_model(model):
    """Reimplemented (and simplified) from spacy.cli.download."""
    global DOWNLOAD_URL
    global MODEL_VERSION_NUM
    dl_tpl = "{m}-{v}/{m}-{v}.tar.gz#egg={m}=={v}"
    download_url = DOWNLOAD_URL + dl_tpl.format(m=model, v=MODEL_VERSION_NUM)
    pip_args = ["--no-cache-dir", "--user"]
    executable = sys.executable.replace("pythonw", "python") # <== hack!
    cmd = [executable, "-m", "pip", "install"] + pip_args + [download_url]
    subprocess.run(cmd, env=os.environ.copy())

            
if __name__ == "__main__":
    from LTTL.Input import Input
    WidgetPreview(SpaCy).run(inputData=Input("a simple example"))
