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

__version__ = u"0.0.4"
__author__ = "Aris Xanthos"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

import importlib.util
import sys
import os
import subprocess

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

import spacy

# Global variables...
RELEVANT_KEYS = [
   'dep_', 'ent_iob_', 'ent_type_', 'head', 'is_alpha', 'is_bracket', 
   'is_digit', 'is_left_punct', 'is_lower', 'is_oov', 'is_punct', 'is_quote', 
   'is_right_punct', 'is_sent_start', 'is_space', 'is_stop', 'is_title', 
   'is_upper', 'label_', 'lang_', 'lemma_', 'like_email', 'like_num', 
   'like_url', 'lower_', 'norm_', 'pos_', 'sentiment', 'shape_', 
   'tag_', 'whitespace_',
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
    outputs = [
        ("Tokenized text", Segmentation, widget.Default),
        ("Named entities", Segmentation),      
        ("Noun chunks", Segmentation),
        ("Sentences", Segmentation),
    ]

    #----------------------------------------------------------------------
    # Layout parameters...
    
    want_main_area = False

    #----------------------------------------------------------------------
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    
    maxLen = settings.Setting("1000000")
    annotatePOSTags = settings.Setting(False)
    annotateDependencies = settings.Setting(False)
    annotateEntities = settings.Setting(False)
    segmentEntities = settings.Setting(False)
    segmentChunks = settings.Setting(False)
    segmentSentences = settings.Setting(False)
    autoSend = settings.Setting(False)
    model = settings.Setting("en_core_web_sm")
    
    def __init__(self):
        """Widget creator."""

        super().__init__()

        # Other attributes...
        self.inputSeg = None
        self.nlp = None
        self.selectedModels = list()
        self.downloadableModelLabels = list()
        self.loadedComponents = list()       
        self.mustLoad = True

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

        annotationsBox = gui.widgetBox(
            widget=optionsBox, 
            box="Additional token annotations:",
        )
        
        annotationsBoxLine1 = gui.widgetBox(
            widget=annotationsBox,
            orientation="horizontal",
            box=None,
        )
        
        gui.checkBox(
            widget=annotationsBoxLine1,
            master=self,
            value='annotatePOSTags',
            label='part-of-speech tags',
            callback=self.updateDisabledComponents,
            tooltip=("Annotate output tokens with part-of-speech tags."),
        )
        
        self.annotatePOSTagsReloadLabel = gui.label(
            annotationsBoxLine1,
            master=self,
            label="(reload needed)",
        )
        self.annotatePOSTagsReloadLabel.setStyleSheet(
            "font-style: oblique; color: gray"
        )
 
        annotationsBoxLine2 = gui.widgetBox(
            widget=annotationsBox,
            orientation="horizontal",
            box=None,
        )
        
        gui.checkBox(
            widget=annotationsBoxLine2,
            master=self,
            value='annotateDependencies',
            label='syntactic dependencies',
            callback=self.updateDisabledComponents,
            tooltip=("Annotate output tokens with syntactic dependencies."),
        )

        self.annotateDependenciesReloadLabel = gui.label(
            annotationsBoxLine2,
            master=self,
            label="(reload needed)",
        )
        self.annotateDependenciesReloadLabel.setStyleSheet(
            "font-style: oblique; color: gray"
        )

        annotationsBoxLine3 = gui.widgetBox(
            widget=annotationsBox,
            orientation="horizontal",
            box=None,
        )
        
        gui.checkBox(
            widget=annotationsBoxLine3,
            master=self,
            value='annotateEntities',
            label='named entities',
            callback=self.updateDisabledComponents,
            tooltip=("Annotate output tokens with named entities."),
        )

        self.annotateEntitiesReloadLabel = gui.label(
            annotationsBoxLine3,
            master=self,
            label="(reload needed)",
        )
        self.annotateEntitiesReloadLabel.setStyleSheet(
            "font-style: oblique; color: gray"
        )

        segmentationsBox = gui.widgetBox(
            widget=optionsBox, 
            box="Additional segmentations:",
        )
        
        segmentationsBoxLine1 = gui.widgetBox(
            widget=segmentationsBox,
            orientation="horizontal",
            box=None,
        )
        
        gui.checkBox(
            widget=segmentationsBoxLine1,
            master=self,
            value='segmentEntities',
            label='named entities',
            callback=self.updateDisabledComponents,
            tooltip="Output named entity segmentation on separate channel.",
        )
        
        self.segmentEntitiesReloadLabel = gui.label(
            segmentationsBoxLine1,
            master=self,
            label="(reload needed)",
        )
        self.segmentEntitiesReloadLabel.setStyleSheet(
            "font-style: oblique; color: gray"
        )
 
        segmentationsBoxLine2 = gui.widgetBox(
            widget=segmentationsBox,
            orientation="horizontal",
            box=None,
        )
        
        gui.checkBox(
            widget=segmentationsBoxLine2,
            master=self,
            value='segmentChunks',
            label='noun chunks',
            callback=self.updateDisabledComponents,
            tooltip="Output noun chunk segmentation on separate channel.",
        )

        self.segmentChunksReloadLabel = gui.label(
            segmentationsBoxLine2,
            master=self,
            label="(reload needed)",
        )
        self.segmentChunksReloadLabel.setStyleSheet(
            "font-style: oblique; color: gray"
        )

        segmentationsBoxLine3 = gui.widgetBox(
            widget=segmentationsBox,
            orientation="horizontal",
            box=None,
        )
        
        gui.checkBox(
            widget=segmentationsBoxLine3,
            master=self,
            value='segmentSentences',
            label='sentences',
            callback=self.updateDisabledComponents,
            tooltip="Output sentence segmentation on separate channel.",
        )

        self.segmentSentencesReloadLabel = gui.label(
            segmentationsBoxLine3,
            master=self,
            label="(reload needed)",
        )
        self.segmentSentencesReloadLabel.setStyleSheet(
            "font-style: oblique; color: gray"
        )

        self.updateReloadNeededLabels()

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
                "If you're not using the parser or NER, or have lots of \n"
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
        self.infoBox.setText("Widget needs input.", "warning")

    def inputData(self, newInput):
        """Process incoming data."""
        self.inputSeg = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()
                  
    def modelComboboxChanged(self):
        """Respond to model change in UI (Options tab)."""
        self.mustLoad = True
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

    def updateDisabledComponents(self):
        """Load components if needed."""
        self.updateReloadNeededLabels()
        self.sendButton.settingsChanged()

    def updateReloadNeededLabels(self):
        """Update the labels that indicate whether model reload is needed."""
        self.annotatePOSTagsReloadLabel.setVisible(
            self.annotatePOSTags and ("tagger" not in self.loadedComponents)
        )
        self.annotateDependenciesReloadLabel.setVisible(
            self.annotateDependencies and ("parser" not in self.loadedComponents)
        )
        self.annotateEntitiesReloadLabel.setVisible(
            self.annotateEntities and ("ner" not in self.loadedComponents)
        )
        self.segmentSentencesReloadLabel.setVisible(
            self.segmentSentences and "parser" not in self.loadedComponents
        )
        self.segmentChunksReloadLabel.setVisible(
            self.segmentChunks and (
                ("tagger" not in self.loadedComponents)
                or ("parser" not in self.loadedComponents)
            )
        )
        self.segmentEntitiesReloadLabel.setVisible(
            self.segmentEntities and "ner" not in self.loadedComponents
        )

    def getComponentStatus(self):
        """Returns the list of disabled/enabled component based on UI state."""
        disabledComponents = list()
        enabledComponents = list()
        if self.annotatePOSTags or self.segmentChunks:
            enabledComponents.append("tagger")
        else:
            disabledComponents.append("tagger")
        if self.annotateDependencies or self.segmentChunks or self.segmentSentences:
            enabledComponents.append("parser")
        else:
            disabledComponents.append("parser")
        if self.annotateEntities or self.segmentEntities:
            enabledComponents.append("ner")
        else:
            disabledComponents.append("ner")
        return disabledComponents, enabledComponents
    
    def loadModel(self):
        """(Re-)load language model if needed."""
        # Initialize progress bar.
        self.infoBox.setText(
            u"Loading language model, please wait...", 
            "warning",
        )
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=1)       
        disabled, enabled = self.getComponentStatus()
        self.nlp = spacy.load(
            AVAILABLE_MODELS[self.model], 
            disable=disabled,
        )
        self.loadedComponents = enabled
        self.updateReloadNeededLabels()
        self.mustLoad = False
        progressBar.advance()
        progressBar.finish()
        self.controlArea.setDisabled(False)

    def sendData(self):
        """Compute result of widget processing and send to output."""

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
            self.infoBox.setText("Widget needs input.", "warning")
            for channel in [c[0] for c in self.outputs]:
                self.send(channel, None, self)
            return

        # Check max length and adjust if needed...
        inputLength = sum(len(s.get_content()) for s in self.inputSeg)
        if self.maxLen != "no limit":
            maxNumChar = int(self.maxLen.split()[0]) * 1000000
            if inputLength > maxNumChar:
                self.infoBox.setText(
                    "Input exceeds max number of characters set by user.", 
                    "warning",
                )
                for channel in [c[0] for c in self.outputs]:
                    self.send(channel, None, self)
                return
        else:
            if inputLength > self.nlp.max_length:
                maxNumChar = inputLength          
        
        # Load components if needed...
        disabled, enabled = self.getComponentStatus()
        if self.mustLoad or not(
            self.nlp and set(enabled) <= set(self.loadedComponents)
        ):
            self.loadModel()
        self.nlp.max_length = maxNumChar
        
        # Initialize progress bar.
        self.infoBox.setText(
            u"Processing, please wait...", 
            "warning",
        )
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=len(self.inputSeg))       

        tokenSegments = list()
        entitySegments = list()
        chunkSegments = list()
        sentenceSegments = list()
        
        # Process each input segment...
        for segment in self.inputSeg:
        
            # NLP analysis...
            disabled, _ = self.getComponentStatus()
            disabled = [c for c in disabled if c in set(self.loadedComponents)]
            with self.nlp.disable_pipes(*disabled):
                doc = self.nlp(segment.get_content())

            # Get token segments...
            tokenSegments.extend(spacyItemsToSegments(doc, segment))

            # Get named entity segments...
            if self.segmentEntities:
                entitySegments.extend(spacyItemsToSegments(doc.ents, segment))

            # Get noun chunk segments...
            if self.segmentChunks:
                chunkSegments.extend(
                    spacyItemsToSegments(doc.noun_chunks, segment), 
                )

            # Get sentences segments...
            if self.segmentSentences:
                sentenceSegments.extend(
                    spacyItemsToSegments(doc.sents, segment), 
                )

            progressBar.advance()

        # Build segmentations and send them to output...                   
        tokenSeg = Segmentation(tokenSegments, self.captionTitle + "_tokens")
        self.send("Tokenized text", tokenSeg, self)
        if self.segmentChunks:
            chunkSeg = Segmentation(
                chunkSegments, 
                self.captionTitle + "_chunks",
            )
            self.send("Noun chunks", chunkSeg, self)
        if self.segmentEntities:
            entitySeg = Segmentation(
                entitySegments, 
                self.captionTitle + "_entities",
            )
            self.send("Named entities", entitySeg, self)
        if self.segmentSentences:
            sentenceSeg = Segmentation(
                sentenceSegments, 
                self.captionTitle + "_sentences",
            )
            self.send("Sentences", sentenceSeg, self)

        # Set status to OK and report data size...
        message = "%i token@p" % len(tokenSeg)
        message = pluralize(message, len(tokenSeg))
        if self.segmentChunks:
            message += ", %i chunk@p" % len(chunkSeg)
            message = pluralize(message, len(chunkSeg))
        if self.segmentEntities:
            message += ", %i " % len(entitySeg)
            message += "entity" if len(entitySeg) == 1 else "entities"
        if self.segmentSentences:
            message += ", %i sentence@p" % len(sentenceSeg)
            message = pluralize(message, len(sentenceSeg))
        message += " sent to output."
        last_comma_idx = message.rfind(",")
        if last_comma_idx > -1:
            message = message[:last_comma_idx] + " and" +    \
                message[last_comma_idx+1:]
        self.infoBox.setText(message)
        
        # Clear progress bar.
        progressBar.finish()
        self.controlArea.setDisabled(False)
                
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


def spacyItemsToSegments(items, parentSegment):
    """Convert spaCy items (tokens or spans) to Textable segments."""
    parentStrIndex = parentSegment.str_index
    parentAnnotations = parentSegment.annotations
    parentStart = parentSegment.start or 0
    segments = list()
    for item in items:
        annotations = parentAnnotations.copy()
        annotations.update(
            {
                k: getattr(item, k) for k in RELEVANT_KEYS
                if hasattr(item, k)
                and getattr(item, k) is not None 
                and getattr(item, k) is not ""
                
            }
        )
        if str(type(item)).endswith("Token'>"):
            startPos = parentStart + item.idx
            endPos = startPos + len(item) 
        else:
            startPos = parentStart + item.start_char
            endPos = parentStart + item.end_char 
        segments.append(
            Segment(
                str_index=parentStrIndex,
                start=startPos,
                end=endPos,
                annotations=annotations,
            )
        )
    return segments

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
    WidgetPreview(SpaCy).run(
        inputData=Input(
            "a simple example is better than a thousand words in New York"
        )
    )
