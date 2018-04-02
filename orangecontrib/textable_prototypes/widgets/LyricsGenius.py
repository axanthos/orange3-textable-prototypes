"""
Class LyricsGenius
Copyright 2018 University of Lausanne
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
__author__ = "Cyrille Gay Crosier, Rafael Bruni Baschino, Basile Maillard"
__maintainer__ = "Aris Xanthos"
__email__ = "cyrille.gay-crosier@unil.ch, rafael.brunibaschino@unil.ch, basile.maillard@unil.ch"

from Orange.widgets import widget, gui, settings

from LTTL.Segmentation import Segmentation
import LTTL.Segmenter as Segmenter

import urllib
import urllib.request
import urllib.parse
import json
import requests
from urllib import request
from urllib import parse

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton
)

class LyricsGenius(OWTextableBaseWidget):
    """Textable widget for importing JSON data from the website Genius
    (https://genius.com/)
    """

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "LyricsGenius"
    description = "Lyrics importation"
    icon = "icons/LyricsGenius.svg"
    priority = 10

    #----------------------------------------------------------------------
    # Channel definitions...

    outputs = [("Lyrics imporation", Segmentation)]

    #----------------------------------------------------------------------
    # Layout parameters...

    want_main_area = False

    #----------------------------------------------------------------------
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    autoSend = settings.Setting(False)

    def __init__(self):
        """Widget creator."""

        super().__init__()

        # ATTRIBUTS
        # test de l'interface creer une recherche definie dans la fonction
        # searchFunction
        self.searchResults = None
        self.inputSeg = None
        # newQuery = attribut box lineEdit (rechercher qqch)
        self.newQuery = ''
        # types = attribut box choix entre artistes et chansons
        self.types = ''
        # attributs de la box de resultats
        self.titleLabels = list()
        self.selectedTitles = list()

        # stock tous les inputs (chansons) dans une liste
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
            sendIfPreCallback=self.updateGUI,
        )
        #----------------------------------------------------------------------
        # User interface...
        # Creation de la zone de travail
        queryBox = gui.widgetBox(
            widget=self.controlArea,
            box="Query",
            orientation="vertical",
        )
        # permet de choisir une recherche entre artistes ou chansons
        # utilise l attribut "types"
        query = gui.comboBox(
            widget=queryBox,
            master=self,
            value="types",
            items=[
                "artists",
                "songs",
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Make a search by:",
            labelWidth=120,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )
        # permet de rentrer du text pour rechercher
        # utilise l attribut "newQuery"
        gui.lineEdit(
            widget=queryBox,
            master=self,
            value='newQuery',
            orientation='horizontal',
            label=u"You searching for?",
            labelWidth=120,
            callback=self.updateGUI,
            tooltip=("Enter a string"),
        )
        # bouton qui lance la recherche
        # utilise la fonction "searchFunction"
        gui.button(
            widget=queryBox,
            master=self,
            label="Search",
            callback=self.searchFunction,
            tooltip="Connect Genius and make a research",
        )

        # Creation d une liste permettant le choix du resultat
        # utilise l attribut "selectedTitles"
        titleBox = gui.widgetBox(
            widget=self.controlArea,
            box="Titles",
            orientation="vertical",
        )
        self.titleListbox = gui.listBox(
            widget=titleBox,
            master=self,
            value="selectedTitles",    # setting (list)
            labels="titleLabels",      # setting (list)
            callback=self.sendButton.settingsChanged,
            tooltip="The list of titles whose content will be imported",
        )
        self.titleListbox.setMinimumHeight(150)
        self.titleListbox.setSelectionMode(3)
        gui.separator(widget=titleBox, height=3)
        gui.rubber(self.controlArea)

        # bouton qui nettoye les resultats
        # utilise la fonction "clearResults"
        gui.button(
            widget=queryBox,
            master=self,
            label="Clear",
            callback=self.clearResults,
            tooltip="Clear results",
        )
        #----------------------------------------------------------------------

        # Now Info box and Send button must be drawn...
        self.sendButton.draw()
        self.infoBox.draw()

        # Send data if autoSend.
        self.sendButton.sendIf()

    def inputData(self, newInput):
        """Process incoming data."""
        self.inputSeg = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    # Fonction qui recherche sur Genius les chanson par rapport
    # au choix de l utilisasteur
    def searchFunction(self):
        """Search from website Genius"""
        result_list = {}
        query_string = self.newQuery
        page = 1
        result_id = 0
        result_artist = []

        values = {'q':query_string, 'page':page}
        data = urllib.parse.urlencode(values)
        query_url = 'http://api.genius.com/search?' + data
        json_obj = self.url_request(query_url)
        body = json_obj["response"]["hits"]

        for result in body:
            # Chaque resultat est stocke dans un dict avec titre, nom d'artiste, id d'artiste et path pour l'url des paroles
            result_id += 1
            title = result["result"]["title"]
            artist = result["result"]["primary_artist"]["name"]
            artist_id = result["result"]["primary_artist"]["id"]
            path = result["result"]["path"]
            result_list[result_id] = {'artist': artist, 'artist_id':artist_id, 'path':path, 'title':title}

        self.searchResults = result_list
        """
        # Liste de résultats factice pour test hors-ligne
        self.searchResults = {
            "id1":{"title":'Les lacs', "artist":'Sardou', "artist_id":10, "path":'path/sardou/lacs'},
            "id2":{"title":'Je vole', "artist":'Sardou', "artist_id":10, "path":'path/sardou/vole'}
            }
        """
        del self.titleLabels[:]
        for id in self.searchResults:
            result_string = self.searchResults[id]["title"] + " - " + self.searchResults[id]["artist"]
            self.titleLabels.append(result_string)

        self.titleLabels = self.titleLabels

    def url_request(self, url):
        """Opens a URL and returns it as a JSON object"""
        ACCESS_TOKEN = "PNlSRMxGK1NqOUBelK32gLirqAtWxPzTey9pReIjzNiVKbHBrn3o59d5Zx7Yej8g"
        USER_AGENT = "CompuServe Classic/1.22"

        request = urllib.request.Request(url,headers={
            "Authorization" : "Bearer " + ACCESS_TOKEN,
            "User-Agent" : USER_AGENT
            })
        response = urllib.request.urlopen(request)
        raw = response.read().decode('utf-8')
        json_obj = json.loads(raw)
        return json_obj

    # Fonction qui vide la liste des resultats
    def clearResults(self):
        """Clear the results list"""
        del self.titleLabels[:]
        self.titleLabels = self.titleLabels
    
    def sendData(self):
        """Compute result of widget processing and send to output"""

        # Check that there's an input...
        if self.inputSeg is None:
            self.send("Improted lyrics", None, self)
            return

        # For now, just send a copy of input to output (will be replaced with
        # actual processing)...
        self.send(
            "Improted lyrics",
            Segmenter.bypass(self.inputSeg, self.captionTitle),
            self,
        )
        self.infoBox.setText(
            "Lyrics importation not yet implemented...",
            "error",
        )

        # Set status to OK and report data size...
        # message = "%i segment@p sent to output." % len(self.segmentation)
        # message = pluralize(message, len(self.segmentation))
        # self.infoBox.setText(message)

        self.sendButton.resetSettingsChangedFlag()

    def updateGUI(self):
        """Update GUI state"""
        pass

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
    import sys
    from PyQt4.QtGui import QApplication
    myApplication = QApplication(sys.argv)
    myWidget = LyricsGenius()
    myWidget.show()
    myApplication.exec_()
    myWidget.saveSettings()
