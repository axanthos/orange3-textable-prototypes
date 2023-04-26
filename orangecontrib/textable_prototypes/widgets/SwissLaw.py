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
    autoSend = settings.Setting(True)
    myBasket = settings.Setting([])

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
        self.database = {
            "id": [],
            "law_text": [],
            "url_fr": [],
            "url_de": [],
            "url_it": [],
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
                for row in reader:
                    self.database["id"].append(row[0])
                    self.database["law_text"].append(row[1])
                    self.database["url_fr"].append(row[2])
                    self.database["url_de"].append(row[3])
                    self.database["url_it"].append(row[4])
                    self.database["title"].append(row[5])
                    self.database["art"].append(row[6])
                    self.database["chap"].append(row[7])

        # Else show error message
        except IOError:
            print("Failed to open csv file.")

        # searchFunction
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
            box="Search Law Document",
            orientation="vertical",
        )
        # Allows to enter specific text to the research

        # Allows to choose the law document

        
        if len(self.selectedDocument) > 0:
            self.addButton.label=u'Add 1 item to corpus'

        queryNbr = gui.comboBox(
            widget=queryBox,
            master=self,
            value="selectedDocument",
            items=self.database["law_text"],
            sendSelectedValue=True,
            callback=self.update_addButton,
            orientation="horizontal",
            label="Law Document :",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )

        # Allows to choose the segmentation
        queryNbr2 = gui.comboBox(
            widget=queryBox,
            master=self,
            value="nbr_results",
            items=[
                "No Segmentation",
                "Into Title",
                "Into Chapter",
                "Into Article",
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Segmentation",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )

        # Allows to choose the language
        queryNbr3 = gui.comboBox(
            widget=queryBox,
            master=self,
            value="nbr_results",
            items=[
                "FR",
                "DE",
                "IT",
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Language",
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
            label=u'Remove from corpus',
            callback=self.remove,
            tooltip=(
                u"Remove the selected text from your corpus."
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
        #self.updateMyDocumentsLabels()

        # Send data if autoSend.
        self.sendButton.sendIf()


    # Search function which contacts the Genius API
    def searchFunction(self):
        """Search from website Genius"""

        result_list = {}
        query_string = self.newQuery

        if query_string != "":
            page = 1
            page_max = int(self.nbr_results)/10
            result_id = 0
            result_artist = []

            self.controlArea.setDisabled(True)

            # Initialize progress bar.
            progressBar = ProgressBar(
                self,
                iterations=page_max
            )

            while page <= page_max:
                values = {'q':query_string, 'page':page}
                data = urllib.parse.urlencode(values)
                query_url = 'http://api.genius.com/search?' + data
                json_obj = self.url_request(query_url)
                body = json_obj["response"]["hits"]

                # Each result is stored in a dictionnary with its title,
                # artist's name, artist's ID and URL path
                for result in body:
                    result_id += 1
                    title = result["result"]["title"]
                    artist = result["result"]["primary_artist"]["name"]
                    artist_id = result["result"]["primary_artist"]["id"]
                    path = result["result"]["path"]
                    result_list[result_id] = {'artist': artist,
                                              'artist_id':artist_id,
                                              'path':path, 'title':title}
                page += 1

                # 1 tick on the progress bar of the widget
                progressBar.advance()
            # Stored the results list in the "result_list" variable
            self.searchResults = result_list

            # Reset and clear the visible widget list
            del self.documentLabels[:]

            # Update the results list with the search results
            # in order to display them
            for idx in self.searchResults:
                result_string = self.searchResults[idx]["title"] + " - " + \
                                self.searchResults[idx]["artist"]
                self.documentLabels.append(result_string)

            self.documentLabels = self.documentLabels
            self.clearButton.setDisabled(False)
            self.addButton.setDisabled(self.selectedDocument == list())


            # Clear progress bar.
            progressBar.finish()
            self.controlArea.setDisabled(False)

        else:
            self.infoBox.setText("You didn't search anything", "warning")


    # Function contacting the Genius API and returning JSON objects
    def url_request(self, url):
        """Opens a URL and returns it as a JSON object"""

        # Token to use the Genius API. DO NOT CHANGE.
        ACCESS_TOKEN = "PNlSRMxGK1NqOUBelK32gLirqAtWxPzTey" \
                       "9pReIjzNiVKbHBrn3o59d5Zx7Yej8g"
        USER_AGENT = "CompuServe Classic/1.22"

        request = urllib.request.Request(url, headers={
            "Authorization" : "Bearer " + ACCESS_TOKEN,
            "User-Agent" : USER_AGENT
            })
        response = urllib.request.urlopen(request)
        raw = response.read().decode('utf-8')
        json_obj = json.loads(raw)
        # retourne un objet json
        return json_obj

    # Function converting HTML to string
    def html_to_text(self, page_url):
        """Extracts the lyrics (as a string) of the html page"""

        page = requests.get(page_url)
        html = BeautifulSoup(page.text, "html.parser")
        [h.extract() for h in html('script')]
        lyrics = html.find("div", class_="lyrics").get_text()
        lyrics.replace('\\n', '\n')
        # return a string
        return lyrics


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

    # Add documents function
    def add(self):
        """Add document in your selection """
        self.myBasket.append((self.selectedDocument,0,0))
        self.updateMyDocumentLabels()
        self.sendButton.settingsChanged()


    # Update selections function
    def updateMyDocumentLabels(self):
        self.mydocumentLabels = list()
        #for item in self.myBasket: (code précédent)
        result_string = self.selectedDocument #self.database["law_text"][item[]0] (code précédent)
        self.documentLabels.append(result_string)
        self.mydocumentLabels = self.documentLabels

        self.clearmyBasket.setDisabled(self.myBasket == list())
        self.removeButton.setDisabled(self.myDocuments == list())

    def deleteMyDocumentLabels(self):
        self.mydocumentLabels = list()
        #for item in self.myBasket: (code précédent)
        result_string = self.selectedDocument #self.database["law_text"][item[]0] (code précédent)
        self.documentLabels.remove(result_string)
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

    def get_xml_contents(self, urls):
        xml_contents = []
        for url in urls:
            response = requests.get(url)
            xml_content = response.content.decode('utf-8')
            xml_contents.append(xml_content)
        return xml_contents

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
        for item in self.myBasket:

            #essai:
            #content = self.get_xml_contents(self.database["url_fr"][self.database["law_text"].index(self.selectedDocument)])

            content = self.get_xml_contents(self.database["url_fr"][item[0]])
            self.created_inputs.append(Input(item))
            progressBar.advance()

        # If there"s only one play, the widget"s output is the created Input.
        if len(self.createdInputs) == 1:
            self.segmentation = self.createdInputs[0]

        # Otherwise the widget"s output is a concatenation...
        else:
            self.segmentation = Segmenter.concatenate(
                self.createdInputs,
                self.captionTitle,
                import_labels_as=None,
            )

        # Annotate segments...
        #for idx, segment in enumerate(self.segmentation):
            #segment.annotations.update(annotations[idx])
            #self.segmentation[idx] = segment

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

        self.send("Lyrics importation", self.segmentation, self)
        self.sendButton.resetSettingsChangedFlag()


    def clearCreatedInputs(self):
        """Delete all Input objects that have been created."""
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