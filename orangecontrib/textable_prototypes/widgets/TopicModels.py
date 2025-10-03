"""
Class TopicModels
Copyright 2017-2025 University of Lausanne
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

__version__ = u"0.1.8"
__author__ = "Aris Xanthos"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"


import Orange.data
from Orange.widgets import widget, gui, settings
from Orange.widgets.unsupervised.owcorrespondence import correspondence
from Orange.widgets.utils.widgetpreview import WidgetPreview

import LTTL
from LTTL.Table import Table, PivotCrosstab

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, # pluralize,
    InfoBox, SendButton, ProgressBar
)

from gensim import corpora, models
from gensim.matutils import corpus2dense

import numpy as np


MAX_NUM_DISPLAYED_TERMS = 6


class TopicModels(OWTextableBaseWidget):
    """Textable widget for building topic models based on a term-document matrix
    """

    #----------------------------------------------------------------------
    # Widget"s metadata...

    name = "Topic Models"
    description = "Build topic models based on term-document matrices"
    icon = "icons/topic_models.svg"
    priority = 32

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = [("Textable Crosstab", PivotCrosstab, "input_data")]
    outputs = [
        ("Term-topic Textable table", PivotCrosstab, widget.Default),
        ("Document-topic Textable table", PivotCrosstab),
        ("Term-topic Orange table", Orange.data.Table, widget.Default),
        ("Document-topic Orange table", Orange.data.Table),        
    ]

    #----------------------------------------------------------------------
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    
    autoSend = settings.Setting(False)
    method = settings.Setting("Latent semantic indexing")
    numTopics = settings.Setting(10)

    want_main_area = False
    
    def __init__(self):
        """Widget creator."""
        super().__init__()

        # Other attributes...
        self.inputTable = None
        self.listEntries = list()

        # Next two instructions are helpers from TextableUtils. Corresponding
        # interface elements are declared here and actually drawn below (at
        # their position in the UI)...
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.send_data,
            infoBoxAttribute="infoBox",
            sendIfPreCallback=self.updateGUI,
        )

        # User interface...

        # Filter box (advanced settings only)
        optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box="Options",
            orientation="vertical",
        )
        method_combo = gui.comboBox(
            widget=optionsBox,
            master=self,
            value="method",
            items=[
                "Latent Dirichlet allocation",
                "Latent semantic indexing", 
                "Correspondence analysis", 
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Method:",
            labelWidth=120,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                "Please select the desired topic modelling method.\n"
            ),
        )
        method_combo.setMinimumWidth(120)
        gui.separator(widget=optionsBox, height=3)
        self.numTopicsSpin = gui.spin(
            widget=optionsBox,
            master=self,
            value='numTopics',
            minv=1,
            maxv=999,
            orientation='horizontal',
            label=u'Number of topics:',
            labelWidth=120,
            callback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"Please select the desired number of topics in output tables."
            ),
        )
        gui.separator(widget=optionsBox, height=3)
        gui.listBox(
            widget=optionsBox,
            master=self,
            labels='listEntries',
            tooltip=(
                u"TODO"
            ),
        )

        gui.separator(widget=self.controlArea, height=3)

        gui.rubber(self.controlArea)

        # Now Info box and Send button must be drawn...
        self.sendButton.draw()
        self.infoBox.draw()
        self.infoBox.setText("Widget needs input", "warning")
        
        # Send data if autoSend.
        self.sendButton.sendIf()

        self.setMinimumWidth(350)
        self.adjustSizeWithTimer()

    def input_data(self, newInput):
        """Process incoming data."""
        self.inputTable = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def send_data(self):
        """Compute result of widget processing and send to output"""

        # Check that there's a table in input...
        if self.inputTable is None:
            self.infoBox.setText(
                "Widget needs input.", 
                "warning"
            )
            self.send("Term-topic Textable table", None)
            self.send("Document-topic Textable table", None)
            self.send("Term-topic Orange table", None)
            self.send("Document-topic Orange table", None)
            self.listEntries = list()
            return

        # Initialize progress bar.
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(
            self, 
            iterations=1    # TODO
        )       
                
        # Convert input table to gensim dictionary.  
        dictionary, corpus = pivot_crosstab_to_gensim(self.inputTable)
        
        # Apply topic modelling...
        
        # Case 1: LDA...
        if self.method == "Latent Dirichlet allocation":
            
            model = models.LdaModel(
                corpus, 
                id2word=dictionary, 
                num_topics=self.numTopics,
            )
            
            import pyLDAvis
            import pyLDAvis.gensim
            viz = pyLDAvis.gensim.prepare(model, corpus, dictionary)
            pyLDAvis.save_html(viz, r"D:\Documents\output.html")
            
            # Create segment-topic PivotCrosstab table.
            values = dict()
            terms = list()
            for topic in range(self.numTopics):
                topic_terms = model.get_topic_terms(
                    topic, 
                    len(self.inputTable.col_ids),
                )
                for term, score in topic_terms:
                    values[(dictionary[term], topic)] = score
                terms.append(
                    list(
                        dictionary[t] 
                        for t, s in topic_terms[:MAX_NUM_DISPLAYED_TERMS]
                    )
                )
            segmentTopicTable = PivotCrosstab(
                row_ids=self.inputTable.col_ids[:],
                col_ids=list(range(self.numTopics)),
                values=values,
                header_row_id='__topic__',
                header_row_type='continuous',
                header_col_id='__unit__',
                header_col_type='string',
                col_type=dict(
                    (col_id, 'continuous') for col_id in range(self.numTopics)
                ),
            )

            # Fill listbox...
            newListEntries = list()
            for topicNum in range(self.numTopics):
                displayedTerms = ", ".join(terms[topicNum])
                if len(self.inputTable.col_ids) > MAX_NUM_DISPLAYED_TERMS:
                    displayedTerms += ", ..."
                listEntry = "%i. %s" % (
                    topicNum+1,
                    displayedTerms,
                )
                newListEntries.append(listEntry)
            self.listEntries = newListEntries

            # Create context-topic PivotCrosstab table...
            corpus_lda = model[corpus]
            values = dict()
            for row_idx, row in enumerate(self.inputTable.row_ids):
                lda_doc = corpus_lda[row_idx]
                for topic, score in lda_doc:
                    values[(row, topic)] = score 
            contextTopicTable = PivotCrosstab(
                row_ids=self.inputTable.row_ids[:],
                col_ids=list(range(self.numTopics)),
                values=values,
                header_row_id='__topic__',
                header_row_type='continuous',
                header_col_id='__context__',
                header_col_type='string',
                col_type=dict(
                    (col_id, 'continuous') for col_id in range(self.numTopics)
                ),
                missing=0,
            )  
                
        # Case 2: LSI...
        if self.method == "Latent semantic indexing":
            
            model = models.LsiModel(
                corpus, 
                id2word=dictionary, 
                num_topics=self.numTopics,
            )
            
            # Create segment-topic PivotCrosstab table.
            segmentTopicTable = PivotCrosstab.from_numpy(
                row_ids=self.inputTable.col_ids[:],
                col_ids=list(range(self.numTopics)),
                np_array=model.projection.u,
                header_row_id='__topic__',
                header_row_type='continuous',
                header_col_id='__unit__',
                header_col_type='string',
                col_type=dict(
                    (col_id, 'continuous') for col_id in range(self.numTopics)
                ),
            )

            # Fill listbox...
            colIds = np.array(self.inputTable.col_ids)
            newListEntries = list()
            # Subtask: compute total inertia, i.e. sum of eigenvalues of
            # doc-term matrix multiplied by its transposed...
            rect_matrix = self.inputTable.to_numpy()
            matrix_dims = self.inputTable.to_numpy().shape
            if matrix_dims[0] > matrix_dims[1]:
                square_matrix = np.dot(np.transpose(rect_matrix), rect_matrix)
            else:
                square_matrix = np.dot(rect_matrix, np.transpose(rect_matrix))
            total_inertia = sum(np.linalg.eigvals(square_matrix))
            for topicNum in range(self.numTopics):
                # Proportion of inertia is SQUARE of singular value divided by
                # total inertia, because n-th singular value = square root of
                # n-th eigenvalue (cf. compute total inertia above)...
                propInertia = model.projection.s[topicNum] ** 2 / total_inertia 
                scores = model.projection.u[:,topicNum]
                sortedTerms = colIds[scores.argsort()[::-1]]
                if len(colIds) > MAX_NUM_DISPLAYED_TERMS:
                    displayedTerms = ", ".join(
                        sortedTerms[:MAX_NUM_DISPLAYED_TERMS//2]
                    )
                    displayedTerms += ", ..., "
                    displayedTerms += ", ".join(
                        sortedTerms[-MAX_NUM_DISPLAYED_TERMS//2:]
                    )
                else:
                    displayedTerms = ", ".join(sortedTerms)
                listEntry = "%i. (%.2f%%) %s" % (
                    topicNum+1,
                    propInertia*100, 
                    displayedTerms,
                )
                newListEntries.append(listEntry)
            self.listEntries = newListEntries

            # Create context-topic PivotCrosstab table...
            contextTopicMatrix = corpus2dense(
                model[corpus], len(model.projection.s)
            ).T / model.projection.s
            values = dict()
            for row_idx, row in enumerate(contextTopicMatrix):
                for topic, val in enumerate(row):
                    values[(self.inputTable.row_ids[row_idx], topic)] = val
            contextTopicTable = PivotCrosstab(
                row_ids=self.inputTable.row_ids[:],
                col_ids=list(range(self.numTopics)),
                values=values,
                header_row_id='__topic__',
                header_row_type='continuous',
                header_col_id='__context__',
                header_col_type='string',
                col_type=dict(
                    (col_id, 'continuous') for col_id in range(self.numTopics)
                ),
                missing=0,
            )            
                
        # Case 2: Correspondence analysis...
        elif self.method == "Correspondence analysis":
        
            ca = correspondence(self.inputTable.to_numpy())

            # Create segment-topic PivotCrosstab table.
            segmentTopicTable = PivotCrosstab.from_numpy(
                row_ids=self.inputTable.col_ids[:],
                col_ids=list(range(self.numTopics)),
                np_array=ca.col_factors[:, range(self.numTopics)],
                header_row_id='__topic__',
                header_row_type='continuous',
                header_col_id='__unit__',
                header_col_type='string',
                col_type=dict(
                    (col_id, 'continuous') for col_id in range(self.numTopics)
                ),
            )

            # Fill listbox...
            colIds = np.array(self.inputTable.col_ids)
            newListEntries = list()
            total_inertia = sum(ca.inertia_of_axis())
            for topicNum in range(self.numTopics):
                propInertia = ca.inertia_of_axis()[topicNum] / total_inertia
                scores = np.array(ca.col_factors[:,topicNum])
                sortedTerms = colIds[scores.argsort()[::-1]]
                if len(colIds) > MAX_NUM_DISPLAYED_TERMS:
                    displayedTerms = ", ".join(
                        sortedTerms[:MAX_NUM_DISPLAYED_TERMS//2]
                    )
                    displayedTerms += ", ..., "
                    displayedTerms += ", ".join(
                        sortedTerms[-MAX_NUM_DISPLAYED_TERMS//2:]
                    )
                else:
                    displayedTerms = ", ".join(sortedTerms)
                listEntry = "%i. (%.2f%%) %s" % (
                    topicNum+1,
                    propInertia*100,
                    displayedTerms,
                )
                newListEntries.append(listEntry)
            self.listEntries = newListEntries

            # Create context-topic PivotCrosstab table.
            contextTopicTable = PivotCrosstab.from_numpy(
                row_ids=self.inputTable.row_ids[:],
                col_ids=list(range(self.numTopics)),
                np_array=ca.row_factors[:, range(self.numTopics)],
                header_row_id='__topic__',
                header_row_type='continuous',
                header_col_id='__unit__',
                header_col_type='string',
                col_type=dict(
                    (col_id, 'continuous') for col_id in range(self.numTopics)
                ),
            )
            
        # Set status to OK and report...
        self.infoBox.setText("Tables correctly sent to output.")

        # Clear progress bar.
        progressBar.finish()
        self.controlArea.setDisabled(False)        
        
        # Send tokens...
        self.send("Term-topic Textable table", segmentTopicTable)
        self.send("Document-topic Textable table", contextTopicTable)
        self.send(
            "Term-topic Orange table", 
            segmentTopicTable.to_orange_table(),
            )
        self.send(
            "Document-topic Orange table", 
            contextTopicTable.to_orange_table(),
        )
        
        self.sendButton.resetSettingsChangedFlag()        
        
    def updateGUI(self):
        """Update GUI state"""
        if self.inputTable is not None:
            if (
                self.method == "Latent semantic indexing" or
                self.method == "Correspondence analysis"
            ):
                maxNumTopics = min(
                    len(self.inputTable.row_ids),
                    len(self.inputTable.col_ids),              
                )
                self.numTopicsSpin.setRange(1, maxNumTopics-1)
            else:
                self.numTopicsSpin.setRange(1, 999)
        else:
            self.numTopicsSpin.setRange(1, 999)

                
  
def pivot_crosstab_to_gensim(table, callback=None):
    """Convert a Textable pivot crosstab to gensim dictionary and corpus"""

    # Create token2id and id2token mappings...
    token2id = dict(
        (table.col_ids[idx], idx) for idx in range(len(table.col_ids))
    )
    id2token = dict(
        (idx, table.col_ids[idx]) for idx in range(len(table.col_ids))
    )

    # Compute document frequency and store it in dict...
    dfs = dict()
    for token in token2id:
        dfs[token2id[token]] = len(
            [v for v in table.values if v[1] == token]
        )
    
    # Compute number of documents.
    num_docs = len(table.row_ids)
    
    # Compute total frequency.
    num_pos = sum(table.values.values())

    # Compute number of non-zero frequencies.
    num_nnz = len(table.values)

    # Create and populate gensim dictionary...
    dictionary = corpora.Dictionary()
    dictionary.token2id.update(token2id)
    dictionary.id2token.update(id2token)
    dictionary.dfs.update(dfs)
    dictionary.num_docs = num_docs
    dictionary.num_pos = num_pos
    dictionary.num_nnz = num_nnz
    
    # Create and populate gensim corpus...
    corpus_dict = dict()
    for k in table.values:
        try:
            corpus_dict[k[0]].append((token2id[k[1]], table.values[k]))
        except KeyError:
            corpus_dict[k[0]] = [(token2id[k[1]], table.values[k])]
    corpus = [corpus_dict[row_id] for row_id in table.row_ids]

    # Return dictionary and corpus.
    return dictionary, corpus

    
if __name__ == "__main__":
    WidgetPreview(TopicModels).run()
