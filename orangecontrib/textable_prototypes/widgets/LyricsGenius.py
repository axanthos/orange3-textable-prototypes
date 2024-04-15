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
__author__ = "Cyrille Gay Crosier, Rafael Bruni Baschino, Basile Maillard"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

from Orange.widgets import widget, gui, settings

from LTTL.Segmentation import Segmentation
import LTTL.Segmenter as Segmenter
from LTTL.Input import Input

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

import re

class LyricsGenius(OWTextableBaseWidget):
    """Textable widget for importing JSON data from the website Genius
    (https://genius.com/)
    """

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Lyrics Genius"
    description = "Lyrics importation"
    icon = "icons/LyricsGenius.svg"
    priority = 10

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = []
    outputs = [("Lyrics importation", Segmentation)]

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

    def __init__(self):
        """Widget creator."""

        super().__init__()

        # ATTRIBUTS
        # searchFunction
        self.searchResults = None
        self.inputSeg = None
        # newQuery = attribut box lineEdit (search something)
        self.newQuery = ''
        self.nbr_results = 10
        # Results box attributs
        self.documentLabels = list()
        self.selectedTitles = list()
        # selections box attributs
        self.titleLabels = list()
        self.myTitles = list()
        self.mytitleLabels = list()
        # stock all the inputs (songs) in a list
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
        #----------------------------------------------------------------------
        # User interface...
        # Create the working area
        queryBox = gui.widgetBox(
            widget=self.controlArea,
            box="Search songs",
            orientation="vertical",
        )
        # Allows to enter specific text to the research
        #  Uses "newQuery" attribut
        gui.lineEdit(
            widget=queryBox,
            master=self,
            value='newQuery',
            orientation='horizontal',
            label=u"Query: ",
            labelWidth=120,
            tooltip=("Enter a string"),
        )

        # Allows to choose the wanted results numberp (10 by 10)
        queryNbr = gui.comboBox(
            widget=queryBox,
            master=self,
            value="nbr_results",
            items=[
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                "70",
                "80",
                "90",
                "100",
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Number of results: ",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )

        # Reasearch button
        # Uses "searchFunction" attribut
        self.searchButton = gui.button(
            widget=queryBox,
            master=self,
            label="Search",
            callback=self.searchFunction,
            tooltip="Connect Genius and make a research",
        )
        self.titleListbox = gui.listBox(
            widget=queryBox,
            master=self,
            value="selectedTitles",    # setting (list)
            labels="titleLabels",      # setting (list)
            callback=lambda: self.addButton.setDisabled(
                self.selectedTitles == list()),
            tooltip="The list of titles whose content will be imported",
        )
        self.titleListbox.setMinimumHeight(150)
        self.titleListbox.setSelectionMode(3)

        boxbutton = gui.widgetBox(
            widget=queryBox,
            box=False,
            orientation='horizontal',
        )
        # Add songs button
        self.addButton = gui.button(
            widget=boxbutton,
            master=self,
            label=u'Add to corpus',
            callback=self.add,
            tooltip=(
                u"Move the selected song downward in your corpus."
            ),
        )
        self.addButton.setDisabled(True)

        # Clear button
        # Uses "clearResults" function
        self.clearButton = gui.button(
            widget=boxbutton,
            master=self,
            label="Clear results",
            callback=self.clearResults,
            tooltip="Clear results",
        )
        self.clearButton.setDisabled(True)
        gui.separator(widget=queryBox, height=3)

        # area where confirmed songs are moved and stocked
        mytitleBox = gui.widgetBox(
            widget=self.controlArea,
            box="Corpus",
            orientation="vertical",
        )

        self.mytitleListbox = gui.listBox(
            widget=mytitleBox,
            master=self,
            value="myTitles",
            labels="mytitleLabels",
            callback=lambda: self.removeButton.setDisabled(
                self.myTitles == list()),
            tooltip="The list of titles whose content will be imported",
        )
        self.mytitleListbox.setMinimumHeight(150)
        self.mytitleListbox.setSelectionMode(3)

        boxbutton2 = gui.widgetBox(
            widget=mytitleBox,
            box=False,
            orientation='horizontal',
        )
        # Remove songs button
        self.removeButton = gui.button(
            widget=boxbutton2,
            master=self,
            label=u'Remove from corpus',
            callback=self.remove,
            tooltip=(
                u"Remove the selected song from your corpus."
            ),
        )
        self.removeButton.setDisabled(True)

        # Delete all confirmed songs button
        self.clearmyBasket = gui.button(
            widget=boxbutton2,
            master=self,
            label=u'Clear corpus',
            callback=self.clearmyBasket,
            tooltip=(
                u"Remove all songs from your corpus."
            ),
        )
        self.clearmyBasket.setDisabled(True)

        gui.separator(widget=mytitleBox, height=3)
        gui.rubber(self.controlArea)
        #----------------------------------------------------------------------

        # Draw Info box and Send button
        self.sendButton.draw()
        self.searchButton.setDefault(True)
        self.infoBox.draw()

        # Update the selections list
        self.updateMytitleLabels()

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
            del self.titleLabels[:]

            # Update the results list with the search results
            # in order to display them
            for idx in self.searchResults:
                result_string = self.searchResults[idx]["title"] + " - " + \
                                self.searchResults[idx]["artist"]
                self.titleLabels.append(result_string)

            self.titleLabels = self.titleLabels
            self.clearButton.setDisabled(False)
            self.addButton.setDisabled(self.selectedTitles == list())


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
        lyrics = ""
        for element in html.find_all("div", class_=re.compile(r"^Lyrics__Container")):
            lyrics_part = element.get_text()
            lyrics = lyrics + lyrics_part
        lyrics = re.sub(r"(?<=\S)(\[|\(|[A-Z])", r" \1", lyrics)
        # return a string
        return lyrics
        


    # Function clearing the results list
    def clearResults(self):
        """Clear the results list"""
        del self.titleLabels[:]
        self.titleLabels = self.titleLabels
        self.clearButton.setDisabled(True)
        self.addButton.setDisabled(self.titleLabels == list())


    # Add songs function
    def add(self):
        """Add songs in your selection """
        for selectedTitle in self.selectedTitles:
            songData = self.searchResults[selectedTitle+1]
            if songData not in self.myBasket:
                self.myBasket.append(songData)
        self.updateMytitleLabels()
        self.sendButton.settingsChanged()


    # Update selections function
    def updateMytitleLabels(self):
        self.mytitleLabels = list()
        for songData in self.myBasket:
            result_string = songData["title"] + " - " + songData["artist"]
            self.mytitleLabels.append(result_string)
        self.mytitleLabels = self.mytitleLabels

        self.clearmyBasket.setDisabled(self.myBasket == list())
        self.removeButton.setDisabled(self.myTitles == list())


    # fonction qui retire la selection de notre panier
    def remove(self):
        """Remove the selected songs in your selection """
        self.myBasket = [
            song for idx, song in enumerate(self.myBasket)
            if idx not in self.myTitles
        ]
        self.updateMytitleLabels()
        self.sendButton.settingsChanged()


    # Clear selections function
    def clearmyBasket(self):
        """Remove all songs in your selection """
        self.mytitleLabels = list()
        self.myBasket = list()
        self.sendButton.settingsChanged()
        self.clearmyBasket.setDisabled(True)


    # Function computing results then sending them to the widget output
    def sendData(self):
        """Compute result of widget processing and send to output"""
        # Skip if title list is empty:
        if self.myBasket == list():
            self.infoBox.setText(
                "Your corpus is empty, please add some songs first",
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

        # Attempt to connect to Genius and retrieve lyrics...
        selectedSongs = list()
        song_content = list()
        annotations = list()
        try:
            for song in self.myBasket:
                # song is a dict {'idx1':{'title':'song1'...},
                # 'idx2':{'title':'song2'...}}
                page_url = "http://genius.com" + song['path']
                lyrics = self.html_to_text(page_url)
                song_content.append(lyrics)
                annotations.append(song.copy())
                # 1 tick on the progress bar of the widget
                progressBar.advance()

        # If an error occurs (e.g. http error, or memory error)...
        except:
            # Set Info box and widget to "error" state.
            self.infoBox.setText(
                "Couldn't download data from Genius website.",
                "error"
            )
            self.controlArea.setDisabled(False)
            return

        # Store downloaded lyrics strings in input objects...
        for song in song_content:
            newInput = Input(song, self.captionTitle)
            self.createdInputs.append(newInput)

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
        for idx, segment in enumerate(self.segmentation):
            segment.annotations.update(annotations[idx])
            self.segmentation[idx] = segment

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
    WidgetPreview(LyricsGenius).run()
