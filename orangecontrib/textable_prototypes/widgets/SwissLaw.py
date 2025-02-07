"""
Class Swiss Law
Copyright 2018-2025 University of Lausanne
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
__author__ = "Elijah Green, Thomas Rywalski, Samantha Allendes Bravo, Antoine Vigand"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

from Orange.widgets import gui, settings
from LTTL.Segmentation import Segmentation
import LTTL.Segmenter as Segmenter
from LTTL.Input import Input

from Orange.widgets.utils.widgetpreview import WidgetPreview

import inspect
import os
import csv
import requests


from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar,
)


class SwissLaw(OWTextableBaseWidget):
    """Textable widget for importing Swiss law texts from
    https://www.fedlex.admin.ch/ (only the 21 most popular texts)
    """

    # ----------------------------------------------------------------------
    # Widget's metadata...

    name = "Swiss Law"
    description = "Swiss Law Documents importation"
    icon = "icons/SwissLaw.png"
    priority = 20

    # ----------------------------------------------------------------------
    # Channel definitions...

    inputs = []
    outputs = [("Law Documents importation", Segmentation)]

    # ----------------------------------------------------------------------
    # Layout parameters...

    want_main_area = False

    # ----------------------------------------------------------------------
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    # Saved settings
    autoSend = settings.Setting(False)
    myBasket = settings.Setting([])
    importedURLs = settings.Setting([])

    def __init__(self):
        """Widget creator."""

        super().__init__()

        # ATTRIBUTS
        self.segmentation = list()

        # Database for our csv
        self.database = {
            "id": [],
            "law_text": [],
            "Urls": [],
            "title": [],
            "art": [],
            "chap": [],
        }

        # Path to csv
        path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )

        # Open the csv and add the content in our database
        try:
            with open(os.path.join(path, "SwissLaw.csv"), "r") as file:
                reader = csv.reader(file)
                next(reader)  # skip the header row if present
                for row in reader:
                    self.database["id"].append(row[0])
                    self.database["law_text"].append(row[1])
                    self.database["Urls"].append((row[2], row[3], row[4]))
                    self.database["title"].append(row[5])
                    self.database["chap"].append(row[6])
                    self.database["art"].append(row[7])

        # Else show error message
        except IOError:
            print("Failed to open csv file.")

        # Dict stocking the documents (avoid re-download)
        self.cached = dict()
        # Stock all the documents names and parameters
        self.documents = sorted(self.database["law_text"])
        self.selectedDocument = self.documents[0]
        self.segLevels = list()
        self.selectedSegLevel = "No segmentation"
        self.languages = ["FR", "DE", "IT"]
        self.selectedLanguage = "FR"
        # Selections box attributs
        self.corpusSelectedItems = list()
        self.corpusLabels = list()
        # Stock all the inputs (law documents) in a list
        self.createdInputs = list()

        # Next two instructions are helpers from TextableUtils. Corresponding
        # interface elements are declared here and actually drawn below (at
        # their position in the UI)...
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute="infoBox",
        )
        # ----------------------------------------------------------------------
        # User interface...
        # Create the working area
        queryBox = gui.widgetBox(
            widget=self.controlArea,
            box="Select Law Document",
            orientation="vertical",
        )

        # Allows to choose the law document
        gui.comboBox(
            widget=queryBox,
            master=self,
            value="selectedDocument",
            items=self.documents,
            sendSelectedValue=True,
            callback=self.updateSegLevelsComboBox,
            orientation="horizontal",
            label="Law Document :",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )
        self.selectedDocument = self.selectedDocument

        # Allows to choose the segmentation
        self.segLevelComboBox = gui.comboBox(
            widget=queryBox,
            master=self,
            value="selectedSegLevel",
            sendSelectedValue=True,
            orientation="horizontal",
            label="Segmentation",
            emptyString="",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )

        # Allows to choose the language
        gui.comboBox(
            widget=queryBox,
            master=self,
            value="selectedLanguage",
            items=self.languages,
            sendSelectedValue=True,
            orientation="horizontal",
            label="Language",
            emptyString="",
            labelWidth=120,
            tooltip=(
                "Please select the desired Language.\n"
            ),
        )

        # Add Law texts button
        self.addButton = gui.button(
            widget=queryBox,
            master=self,
            label=u'Add to corpus',
            callback=self.add,
            tooltip=(
                u"Move the selected text downward in your corpus."
            ),
        )

        # Corpus = area where confirmed law texts are moved and stocked
        corpusBox = gui.widgetBox(
            widget=self.controlArea,
            box="Corpus",
            orientation="vertical",
        )

        self.corpusListbox = gui.listBox(
            widget=corpusBox,
            master=self,
            value="corpusSelectedItems",
            labels="corpusLabels",
            callback=self.updateRemoveButton,
            tooltip="The list of titles whose content will be imported",
        )
        self.corpusListbox.setMinimumHeight(150)
        self.corpusListbox.setSelectionMode(3)

        # Buttons in the corpus area
        buttonBox = gui.widgetBox(
            widget=corpusBox,
            box=False,
            orientation='horizontal',
        )
        # Remove law texts button
        self.removeButton = gui.button(
            widget=buttonBox,
            master=self,
            label=u'Remove the selected document from corpus',
            callback=self.remove,
            tooltip=(
                u"Remove the selected text from your corpus."
            ),
        )
        self.removeButton.setDisabled(True)

        # Delete all confirmed law texts button
        self.clearCorpusButton = gui.button(
            widget=buttonBox,
            master=self,
            label=u'Clear corpus',
            callback=self.clearCorpus,
            tooltip=(
                u"Remove all texts from your corpus."
            ),
        )
        self.clearCorpusButton.setDisabled(self.corpusLabels == list()),

        gui.separator(widget=corpusBox, height=3)
        gui.rubber(self.controlArea)
        # ----------------------------------------------------------------------

        # Draw Info box and Send button
        self.sendButton.draw()
        self.infoBox.draw()

        # Update the selections list
        self.updateMyDocumentLabels()

        # Send data if autoSend.
        self.sendButton.sendIf()

        self.updateSegLevelsComboBox()

    def updateRemoveButton(self):
        """Update the remove button if a law text is selected in the corpus"""
        self.removeButton.setDisabled(self.corpusSelectedItems == list())

    # Function clearing the results list
    def clearResults(self):
        """Clear the results list"""
        del self.corpusLabels[:]
        self.corpusLabels = self.titleLabels
        self.clearButton.setDisabled(True)
        self.addButton.setDisabled(self.corpusLabels == list())

    def updateSegLevelsComboBox(self):
        """Update available segmentation"""
        self.segLevelComboBox.clear()
        self.segLevels = list()
        self.segLevels.append("No Segmentation")

        # Check if the selected law text has title, article or chapter
        if int(self.database["title"][self.database["law_text"].index(self.selectedDocument)]) > 0:
            self.segLevels.append("Into title")

        if int(self.database["chap"][self.database["law_text"].index(self.selectedDocument)]) > 0:
            self.segLevels.append("Into chapter")

        if int(self.database["art"][self.database["law_text"].index(self.selectedDocument)]) > 0:
            self.segLevels.append("Into article")

        self.selectedSegLevel = self.segLevels[0]
        self.segLevelComboBox.addItems(self.segLevels)

    # Add documents to corpus function
    def add(self):
        """Add document in your selection """
        if (self.selectedDocument, self.selectedSegLevel, self.selectedLanguage) not in self.myBasket:
            self.myBasket.append((self.selectedDocument, self.selectedSegLevel, self.selectedLanguage))
        else:
            pass

        self.updateMyDocumentLabels()
        self.sendButton.settingsChanged()

        self.selectedDocument = self.documents[0]
        self.updateSegLevelsComboBox()
        self.selectedLanguage = "FR"

    def updateMyDocumentLabels(self):
        """Update selections"""
        self.corpusLabels = list()
        for item in self.myBasket:
            result_string = item[0] + " - " + item[1] + " - " + item[2]
            self.corpusLabels.append(result_string)

        self.corpusLabels = self.corpusLabels

        self.clearCorpusButton.setDisabled(self.corpusLabels == list())
        self.removeButton.setDisabled(self.corpusSelectedItems == list())

        self.segLevelComboBox.clear()

    # Function to remove selected law text from the corpus
    def remove(self):
        """Remove the selected text in your selection """
        self.myBasket = [
            text_law for idx, text_law in enumerate(self.myBasket)
            if idx not in self.corpusSelectedItems
        ]
        self.updateMyDocumentLabels()
        self.sendButton.settingsChanged()

        self.selectedDocument = self.documents[0]
        self.updateSegLevelsComboBox()
        self.selectedLanguage = "FR"

    # Clear selections (all corpus) function
    def clearCorpus(self):
        """Remove all texts in your selection """
        self.corpusLabels = list()
        self.corpusLabels = list()
        self.myBasket = list()
        self.sendButton.settingsChanged()
        self.clearCorpusButton.setDisabled(True)

        self.selectedDocument = self.documents[0]
        self.updateSegLevelsComboBox()
        self.selectedLanguage = "FR"

    def get_xml_contents(self, urls) -> str:
        """Download xml law text based on the url"""
        response = requests.get(urls)
        xml_content = response.content.decode('utf-8')
        return xml_content

    # Function computing results then sending them to the widget output
    def sendData(self):
        """Compute result of widget processing and send to output"""
        # Skip if document list is empty:
        if self.myBasket == list():
            self.infoBox.setText(
                "Your corpus is empty, please add some law texts first",
                "warning"
            )
            return

        # Clear created Inputs.
        self.clearCreatedInputs()

        self.controlArea.setDisabled(True)

        # Initialize progress bar.
        progressBar = ProgressBar(
            self,
            iterations=len(self.myBasket)
        )

        # Lists to stock the necessary information
        documents = list()
        annotations = list()
        segmentation_levels = list()

        # Get the xml law text...
        for item in self.myBasket:

            # ...from the self.cached dict if already downloaded
            if self.database["Urls"][self.database["law_text"].index(item[0])][self.languages.index(item[2])]\
                    in self.cached:
                content = self.cached[self.database["Urls"][self.database["law_text"].index(item[0])][self.languages.index(item[2])]]
            # ...with the get_xml_function if not already downloaded
            else:
                content = self.get_xml_contents(
                    self.database["Urls"][self.database["law_text"].index(item[0])][self.languages.index(item[2])]
                )
                self.cached[self.database["Urls"][self.database["law_text"].index(item[0])][self.languages.index(item[2])]] = content

            documents.append(content)

            # Get the desired segmentation
            segmentation_levels.append(item[1].replace("Into ", ""))

            # Add segment annotations
            annotations.append({"Document": item[0], "Language": item[2]})
            progressBar.advance()

        # Segment the text with the desired segmentation (using import_xml)
        segmentations = []

        for doc_idx, document in enumerate(documents):
            newInput = Input(document, self.captionTitle)
            self.createdInputs.append(newInput)

            if segmentation_levels[doc_idx] == "No Segmentation":
                current_segmentation = newInput
            else:
                current_segmentation = Segmenter.import_xml(newInput, segmentation_levels[doc_idx])
            # Annotate segments...
            for idx, segment in enumerate(current_segmentation):
                segment.annotations.update(annotations[doc_idx])
                current_segmentation[idx] = segment
            segmentations.append(current_segmentation)

        # If there's only one document, the widget's output is the created Input.
        if len(self.createdInputs) == 1:
            self.segmentation = segmentations[0]

        # Otherwise the widget's output is a concatenation...
        else:
            self.segmentation = Segmenter.concatenate(
                segmentations,
                self.captionTitle,
                import_labels_as=None
            )

        # Clear progress bar.
        progressBar.finish()

        self.controlArea.setDisabled(False)

        # Set status to OK and report data size...
        message = "%i segment@p sent to output " % len(self.segmentation)
        message = pluralize(message, len(self.segmentation))
        numChars = 0
        for segment in self.segmentation:
            segmentLength = len(Segmentation.get_data(segment.str_index))
            numChars += segmentLength
        message += "(%i character@p)." % numChars
        message = pluralize(message, numChars)
        self.infoBox.setText(message)

        # Final send
        self.send("Law Documents importation", self.segmentation)
        self.sendButton.resetSettingsChangedFlag()

    def clearCreatedInputs(self):
        """Clear created inputs"""
        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]

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
    WidgetPreview(SwissLaw).run()
