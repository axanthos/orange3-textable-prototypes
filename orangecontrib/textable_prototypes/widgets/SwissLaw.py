"""
Class LyricsGenius
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

__version__ = u"0.0.3"
__author__ = "Elijah Green, Thomas Rywalski, Samantha Allendes Bravo, Antoine Vigand"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

from Orange.widgets import widget, gui, settings

from LTTL.Segmentation import Segmentation
import LTTL.Segmenter as Segmenter
from LTTL.Input import Input

from Orange.widgets.utils.widgetpreview import WidgetPreview

import inspect
import os
import pickle
import csv
import urllib
import urllib.request
import urllib.parse
import json
import requests
from urllib import request
from urllib import parse
from bs4 import BeautifulSoup

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar,
)

class SwissLaw(OWTextableBaseWidget):
    """Textable widget for importing Swiss law texts from
    https://www.fedlex.admin.ch/ (only the 21 most popular texts)
    """

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Swiss Law"
    description = "Swiss Law Documents importation"
    icon = "icons/balance-de-la-justice.png"
    priority = 10

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = []
    outputs = [("Law Documents importation", Segmentation)]

    #----------------------------------------------------------------------
    # Layout parameters...

    want_main_area = False

    #----------------------------------------------------------------------
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    # Saved settings
    autoSend = settings.Setting(False)
    myBasket = settings.Setting([])
    importedURLs = settings.Setting([])


#Note débug jeudi 20 Avril 14h14:
#J'ai changé: ligne 147 -> avant la valeur était = None (bug), j'ai remplacé None par ""
            # ligne 138 -> j'ai remis self.nbr_results = 10 (utilisé dans queryNbr2 et 3 pour values, à voir ce qu'il faut qu'on mette
            # ligne 300 -> self.updateMyDocumentsLabels() en commentaire car pas défini (doit être défini comme méthode (fonction), voir lyricsgenius avec updatemytitleslabel
            # Send ne marche pas
    def __init__(self):
        """Widget creator."""

        super().__init__()

        # ATTRIBUTS
        #database for our csv
        self.segmentation = list()
        """self.database = {
            "id": [],
            "law_text": [],
            "url_fr": [],
            "url_de": [],
            "url_it": [],
            "title": [],
            "art": [],
            "chap": [],
        }"""

        self.database = {
            "id": [],
            "law_text": [],
            "Urls": [],
            "title": [],
            "art": [],
            "chap": [],
        }

        #Path to csv
        path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )

        #Open the csv and add the content in our database
        try:
            with open(os.path.join(path, "DroitCH.csv"), "r") as file:
                reader = csv.reader(file)
                next(reader)  # skip the header row if present
                # Empty line
                self.database["id"].append("")
                self.database["law_text"].append("")
                self.database["Urls"].append(())
                self.database["title"].append("")
                self.database["art"].append("")
                self.database["chap"].append("")

                for row in reader:
                    self.database["id"].append(row[0])
                    self.database["law_text"].append(row[1])
                    self.database["Urls"].append((row[2], row[3], row[4]))
                    self.database["title"].append(row[5])
                    self.database["art"].append(row[6])
                    self.database["chap"].append(row[7])

        # Else show error message
        except IOError:
            print("Failed to open csv file.")


        self.searchResults = None
        self.inputSeg = None
        # newQuery = attribut box lineEdit (search something)
        self.newQuery = ''
        self.nbr_results = 10
        # Results box attributs
        self.documentLabels = list()
        # selections box attributs
        self.myDocuments = list()
        self.mydocumentLabels = list()
        # stock all the inputs (songs) in a list
        self.createdInputs = list()
        # list for each law document (tuples)
        self.selectedDocument = ""
        self.seg = ""
        self.language = ""
        self.addButton = None
        self.segmentations = [
            "",
            "No Segmentation"
        ]
        self.languages = [
                "",
                "FR",
                "DE",
                "IT"
            ]

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
        #----------------------------------------------------------------------
        # User interface...
        # Create the working area
        queryBox = gui.widgetBox(
            widget=self.controlArea,
            box="Select Law Document",
            orientation="vertical",
        )
        # Allows to enter specific text to the research

        # Allows to choose the law document

        queryNbr = gui.comboBox(
            widget=queryBox,
            master=self,
            value="selectedDocument",
            items=sorted(self.database["law_text"]),
            sendSelectedValue=True,
            callback=self.update_addButton,
            orientation="horizontal",
            emptyString="",
            label="Law Document :",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )

        # Allows to choose the segmentation

        self.queryNbr2 = gui.comboBox(
            widget=queryBox,
            master=self,
            value="seg",
            items=self.segmentations,
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
        queryNbr3 = gui.comboBox(
            widget=queryBox,
            master=self,
            value="language",
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

        boxbutton = gui.widgetBox(
            widget=queryBox,
            box=False,
            orientation='horizontal',
        )

        # Add Law texts button
        self.addButton = gui.button(
            widget=boxbutton,
            master=self,
            label=u'Add to corpus',
            callback=self.add,
            tooltip=(
                u"Move the selected text downward in your corpus."
            ),
        )
        self.addButton.setDisabled(True)

        # Corpus = area where confirmed law texts are moved and stocked
        mytitleBox = gui.widgetBox(
            widget=self.controlArea,
            box="Corpus",
            orientation="vertical",
        )

        self.mytitleListbox = gui.listBox(
            widget=mytitleBox,
            master=self,
            value="myDocuments",
            labels="mydocumentLabels",
            callback=lambda: self.removeButton.setDisabled(
                self.myDocuments == list()),
            tooltip="The list of titles whose content will be imported",
        )
        self.mytitleListbox.setMinimumHeight(150)
        self.mytitleListbox.setSelectionMode(3)

        boxbutton2 = gui.widgetBox(
            widget=mytitleBox,
            box=False,
            orientation='horizontal',
        )
        # Remove law texts button
        self.removeButton = gui.button(
            widget=boxbutton2,
            master=self,
            label=u'Remove the last document from corpus',
            callback=self.remove,
            tooltip=(
                u"Remove the last added text from your corpus."
            ),
        )
        self.removeButton.setDisabled(True)

        # Delete all confirmed law texts button
        self.clearmyBasket = gui.button(
            widget=boxbutton2,
            master=self,
            label=u'Clear corpus',
            callback=self.clearmyBasket,
            tooltip=(
                u"Remove all texts from your corpus."
            ),
        )
        self.clearmyBasket.setDisabled(True)

        gui.separator(widget=mytitleBox, height=3)
        gui.rubber(self.controlArea)
        #----------------------------------------------------------------------

        # Draw Info box and Send button
        self.sendButton.draw()
        self.infoBox.draw()

        # Update the selections list
        self.updateMyDocumentLabels()

        # Send data if autoSend.
        self.sendButton.sendIf()

    # Function clearing the results list
    def clearResults(self):
        """Clear the results list"""
        del self.documentLabels[:]
        self.documentLabels = self.titleLabels
        self.clearButton.setDisabled(True)
        self.addButton.setDisabled(self.documentLabels == list())

    # update AddButton function
    def update_addButton(self):
        self.addButton.setDisabled(len(self.selectedDocument) == 0)

        self.queryNbr2.clear()

        self.segmentations = list()
        self.segmentations.append("")
        self.segmentations.append("No Segmentation")

        if int(self.database["title"][self.database["law_text"].index(self.selectedDocument)]) > 0:
            self.segmentations.append("Title")

        if int(self.database["art"][self.database["law_text"].index(self.selectedDocument)]) > 0:
            self.segmentations.append("Into Article")

        if int(self.database["chap"][self.database["law_text"].index(self.selectedDocument)]) > 0:
            self.segmentations.append("Into Chapter")

        self.queryNbr2.addItems(self.segmentations)

        #self.sendButton.sendIf()
        self.updateMyDocumentLabels()



        # Add documents function
    def add(self):
        """Add document in your selection """
        segmentation_list = ["", "title", "article", "chapter"]
        if self.selectedDocument!="":
            self.myBasket.append((self.selectedDocument, segmentation_list[(self.segmentations.index(self.seg)-1)], (self.languages.index(self.language)-1)))
            self.updateMyDocumentLabels()
            self.sendButton.settingsChanged()


    # Update selections function
    def updateMyDocumentLabels(self):
        #self.mydocumentLabels = list()
        #for item in self.myBasket: (code précédent)
        if self.selectedDocument!="" and self.seg!="" and self.language!="":
            result_string = self.selectedDocument +" - "+self.seg+" - "+self.language #self.database["law_text"][item[]0] (code précédent)
            self.documentLabels.append(result_string)
            self.mydocumentLabels = self.documentLabels

            self.clearmyBasket.setDisabled(self.myBasket == list())
            self.removeButton.setDisabled(self.myDocuments == list())

            self.selectedDocument=""
            self.seg=""
            self.language=""
            self.queryNbr2.clear()

    def deleteMyDocumentLabels(self):
        self.mydocumentLabels = list()
        #for item in self.myBasket: (code précédent)
        #result_string = self.selectedDocument #self.database["law_text"][item[]0] (code précédent)
        self.documentLabels.pop()
        self.mydocumentLabels = self.documentLabels

        self.clearmyBasket.setDisabled(self.myBasket == list())
        self.removeButton.setDisabled(self.myDocuments == list())

    # fonction qui retire la selection de notre panier
    def remove(self):
        """Remove the selected text in your selection """
        self.myBasket = [
            song for idx, song in enumerate(self.myBasket)
            if idx not in self.myDocuments
        ]
        self.deleteMyDocumentLabels()
        self.sendButton.settingsChanged()


    # Clear selections function
    def clearmyBasket(self):
        """Remove all texts in your selection """
        self.documentLabels = list()
        self.mydocumentLabels = list()
        self.myBasket = list()
        self.sendButton.settingsChanged()
        self.clearmyBasket.setDisabled(True)

    def get_xml_contents(self, urls) -> str:
        xml_contents = []
        #for url in urls: #on le garde au cas ou
        response = requests.get(urls)
        xml_content = response.content.decode('utf-8')
        #xml_contents.append(xml_content)
        return xml_content

    # Function computing results then sending them to the widget output
    def sendData(self):
        """Compute result of widget processing and send to output"""
        # Skip if title list is empty:
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

        #Get the xml link
        #for item in self.myBasket:

            #essai:
        """xml_file_contents = []
                for myDocu in self.mydocumentLabels:
                    xml_file_content = self.get_xml_contents(self.database["url_fr"][self.database["law_text"].index(myDocu)])
                    xml_file_contents.append(xml_file_content)"""

        Document_list = list()
        segmentations_list = list()

        for item in self.myBasket:
            content = self.get_xml_contents(self.database["Urls"][self.database["law_text"].index(item[0])][item[2]])
            Document_list.append(content)
            segmentations_list.append(item[1])
            #annotations.append(self.database["law_text"][self.database["law_text"].index(item[0])].annotations.copy())
            #self.createdInputs.append(content)
            #self.createdInputs.set_data(-1, content)
            progressBar.advance()

        """self.send("XML-TEI data", None, self)
        self.controlArea.setDisabled(False)
        return"""

        """for script in Document_list:
            newInput = Input(script, self.captionTitle)
            self.createdInputs.append(newInput)
"""
        for script in Document_list:
            newInput = Input(script, self.captionTitle)
            self.createdInputs.append(newInput)

        # If there"s only one play, the widget"s output is the created Input.
        if len(self.createdInputs) == 1:
            self.segmentation = self.createdInputs[0]

        # Otherwise the widget"s output is a concatenation...
        else:
            self.segmentation = Segmenter.concatenate(
                self.createdInputs,
                self.captionTitle,
                import_labels_as=None
            )

        # Annotate segments...
        """for idx, segment in enumerate(self.segmentation):
            segment.annotations.update(annotations[idx])
            self.segmentation[idx] = segment"""

        # Store imported URLs as setting.
        """self.importedURLs = [
            self.searchResults[self.myBasket[0]].annotations["urls"]
        ]"""

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

        # Clear progress bar.
        progressBar.finish()
        self.controlArea.setDisabled(False)

        #print(segmentations_list[0])

        self.segmentation = Segmenter.import_xml(self.segmentation, segmentations_list[0], label=segmentations_list[0])
        #print(type(self.segmentation))
        self.send("Law Documents importation", self.segmentation, self)
        self.sendButton.resetSettingsChangedFlag()


    def clearCreatedInputs(self):
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