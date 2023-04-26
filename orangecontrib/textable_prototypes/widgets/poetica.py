"""
Class Poetica
Copyright 2023 University of Lausanne
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
__author__ = "Sinem Kilic, Laure Margot, Leonie Nussbaum, Olivia Verbrugge"
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
from urllib.request import urlopen
from urllib import request
from urllib import parse
from bs4 import BeautifulSoup

import inspect
import re
import pickle
import os

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar,
)

class Poetica(OWTextableBaseWidget):
    """Textable widget for importing XML data from the website Poetica
    (https://poetica.fr/)
    """

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Poetica"
    description = "Poems importation from poetica.fr"
    icon = "icons/Poetica.svg"
    priority = 10

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = []
    outputs = [("Poems importation", Segmentation)]

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
        # authorQuery = attribut box lineEdit (search something)
        self.authorQuery = ''
        self.dateQuery = ''
        self.topicQuery = ''
        # Results box attributs
        self.poemLabels = list()
        self.selectedPoems = list()
        # Corpus box attributs
        self.corpusItems = list()
        self.corpusItemsLabels = list()
        # Stocks all the inputs (poems) in a list
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
            box="Search poems",
            orientation="vertical",
        )

        # Import the poem's database.
        i = self.openDatabase()

        # Store the list of authors...
        self.authors_list = list()
        self.authors_list.append("None")
        previous_author = ""
        for key, value in i["author"].items():
            if i["author"][key] != previous_author:
                self.authors_list.append(i["author"][key])
            previous_author = i["author"][key]

        # Allows to select an author in a list
        #  Uses "authorQuery" attribut
        gui.comboBox(
            widget=queryBox,
            master=self,
            value='authorQuery',
            items=self.authors_list,
            orientation='horizontal',
            label=u"Author Query: ",
            labelWidth=120,
            tooltip=("Select an author"),
        )

        # Allows to select a date in a list
        #  Uses "dateQuery" attribut
        gui.comboBox(
            widget=queryBox,
            master=self,
            value='dateQuery',
            items=[
                "1700",
            ],
            orientation='horizontal',
            label=u"Date Query: ",
            labelWidth=120,
            tooltip=("Select date"),
        )

        # Allows to select a topic in a list
        #  Uses "topicQuery" attribut
        gui.comboBox(
            widget=queryBox,
            master=self,
            value='topicQuery',
            items=[
                "amour",
                "amitié"
            ],
            orientation='horizontal',
            label=u"Topic Query: ",
            labelWidth=120,
            tooltip=("Select topic"),
        )

        # Research button
        # Uses "searchFunction" attribut
        self.searchButton = gui.button(
            widget=queryBox,
            master=self,
            label="Search",
            callback=self.searchFunction,
            tooltip="Connecter Poetica et effectuer une recherche",
        )

        # Refresh Button
        self.refreshButton = gui.button(
            widget=queryBox,
            master=self,
            label="Refresh database",
            #callback=self.searchFunction,
            tooltip="Attention ! Cela peut prendre un peu de temps…",
        )

        self.poemLabelsBox = gui.listBox(
            widget=queryBox,
            master=self,
            value="selectedPoems",    # setting (list)
            labels="poemLabels",      # setting (list)
            callback=lambda: self.addButton.setDisabled(
                self.selectedPoems == list()),
            tooltip="The list of poems whose content will be imported",
        )
        self.poemLabelsBox.setMinimumHeight(150)
        self.poemLabelsBox.setSelectionMode(3)

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

        self.mypoemLabelsBox = gui.listBox(
            widget=mytitleBox,
            master=self,
            value="corpusItems",
            labels="corpusItemsLabels",
            callback=lambda: self.removeButton.setDisabled(
                self.corpusItems == list()),
            tooltip="The list of titles whose content will be imported",
        )
        self.mypoemLabelsBox.setMinimumHeight(150)
        self.mypoemLabelsBox.setSelectionMode(3)

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
        self.updatecorpusItemsLabels()

        # Send data if autoSend.
        self.sendButton.sendIf()

    def dataExtraction(self):

        database = {
            "title": {},
            "author": {},
            "poem": {},
        }

        # Acceder a la page d'accueil de poetica...
        try:
            poetica_url = 'https://www.poetica.fr/'
            url_accueil = urlopen(poetica_url)
            page_accueil = url_accueil.read()
            # print(page_accueil)
            print("Valid poetica's URL")
            page_accueil = page_accueil.decode("utf-8")
            # url_accueil.close()

            # Extraire la liste d'auteurs...
            base_seg = Input(page_accueil)
            condition = dict()
            condition["id"] = re.compile(r"^menu-poemes-par-auteur$")
            xml_auteurs = Segmenter.import_xml(
                segmentation=base_seg,
                element="<ul>",
                conditions=condition,
            )

            # Recuperer le lien url vers la page de chaque auteur...
            xml_par_auteur = Segmenter.import_xml(
                segmentation=xml_auteurs,
                element="<a>",
            )

            # Acceder a la page de chaque auteur...
            for auteur in xml_par_auteur:
                try:
                    url_page_auteur = auteur.annotations["href"]
                    url_auteur = urlopen(url_page_auteur)
                    page_auteur = url_auteur.read()
                    print("Valid author's URL")
                    page_auteur = page_auteur.decode("utf-8")

                    # Recuperer le nom de l'auteur.
                    nom_auteur = auteur.get_content()
                    # print(nom_auteur)

                    # print(xml_par_auteur.to_string())
                    # nom_auteur = auteur.get_content()

                    # Extraire la liste de poemes...
                    seg_auteurs = Input(page_auteur)
                    condition_auteur = dict()
                    condition_auteur["class"] = re.compile(r"^entry-header$")
                    xml_poemes = Segmenter.import_xml(
                        segmentation=seg_auteurs,
                        element="<header>",
                        conditions=condition_auteur,
                    )

                    # Recuperer le lien url vers la page de chaque poeme...
                    xml_par_poeme = Segmenter.import_xml(
                        segmentation=xml_poemes,
                        element="<a>",
                    )

                    # Acceder a la page de chaque poeme...
                    for poeme in xml_par_poeme:
                        try:
                            url_page_poeme = poeme.annotations["href"]
                            url_poeme = urlopen(url_page_poeme)
                            page_poeme = url_poeme.read()
                            print("Valid poem's URL")
                            page_poeme = page_poeme.decode("utf-8")

                            # Recuperer le nom du poeme.
                            nom_poeme = poeme.get_content()
                            # print(nom_poeme)

                            # Extraire les poeme et ses donnees...
                            seg_poemes = Input(page_poeme)
                            condition_poeme = dict()
                            condition_poeme["class"] = re.compile(r"^entry-content$")
                            xml_contenu_poeme = Segmenter.import_xml(
                                segmentation=seg_poemes,
                                element="<div>",
                                conditions=condition_poeme,
                            )

                            # Recuperer le poeme avec ses propres balises.
                            poeme_balises = xml_contenu_poeme[0].get_content()

                            # Recuperer et associer la date de parution du poeme si elle est connue...

                            # N'afficher que le contenu du poeme...
                            poeme = re.sub(r"((</?p.*?>)|(<br />))|(<em>.*</em>)|(</p>)", "", poeme_balises)
                            poeme = re.sub(r".+$", "", poeme)
                            # print(poeme)
                            database["title"][url_page_poeme] = nom_poeme
                            database["author"][url_page_poeme] = nom_auteur
                            database["poem"][url_page_poeme] = poeme

                        # Avertir si l'url ne fonctionne pas...
                        except IOError:
                            print("Invalid poem's URL")

                # Avertir si l'url ne fonctionne pas...
                except IOError:
                    print("Invalid author's URL")

        # Avertir si l'url ne fonctionne pas...
        except IOError:
            print("Invalid poetica's URL")

        # print(database)

        # Definir un path pour situer par la suite le chemin d'acces pour la sauvegarde...
        path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )

        # Sauvegarder les dictionnaires avec pickle...
        try:
            file = open(os.path.join(path, "poetica_cache.p"), "wb")
            pickle.dump(database, file)
            print('The dictionary has successfully been saved to the file')
            file.close()
        except IOError:
            print("Can't save the dictionary")


    def openDatabase(self):

        # Definir un path pour situer par la suite le chemin d'acces pour la sauvegarde...
        path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )

        # Ouvrir les dictionnaires avec pickle...
        try:
            file = open(os.path.join(path, "poetica_cache.p"), "rb")
            new_database = pickle.load(file)
            # print(new_database)
            print("Dictionary correctly loaded")
            file.close()
        except IOError:
            print("Can't load the dictionary")

        return new_database


    def searchFunction(self):
        author_query = self.authorQuery
        if str(author_query) != "":
            index = int(self.authorQuery)
            self.infoBox.setText(f"You search {self.authors_list[index]}. Select a poem", "warning")
            #            for key, value in i["author"].items():
            #                if self.i["author"][key] == self.authors_list[index]:
            #                else :
            #                    pass
            self.poemLabelsBox.addItem("a")
        else:
            self.infoBox.setText(f"You didn't search anything !",
                                 "warning")

    # Search function which contacts the Genius API
    def searchFunctionGenius(self):
        """Search from website Genius"""

        result_list = {}
        query_string = self.authorQuery

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
            del self.poemLabels[:]

            # Update the results list with the search results
            # in order to display them
            for idx in self.searchResults:
                result_string = self.searchResults[idx]["title"] + " - " + \
                                self.searchResults[idx]["artist"]
                self.poemLabels.append(result_string)

            self.poemLabels = self.poemLabels
            self.clearButton.setDisabled(False)
            self.addButton.setDisabled(self.selectedPoems == list())


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
        del self.poemLabels[:]
        self.poemLabels = self.poemLabels
        self.clearButton.setDisabled(True)
        self.addButton.setDisabled(self.poemLabels == list())


    # Add songs function
    def add(self):
        """Add songs in your selection """
        for selectedTitle in self.selectedPoems:
            songData = self.searchResults[selectedTitle+1]
            if songData not in self.myBasket:
                self.myBasket.append(songData)
        self.updatecorpusItemsLabels()
        self.sendButton.settingsChanged()


    # Update selections function
    def updatecorpusItemsLabels(self):
        self.corpusItemsLabels = list()
        for songData in self.myBasket:
            result_string = songData["title"] + " - " + songData["artist"]
            self.corpusItemsLabels.append(result_string)
        self.corpusItemsLabels = self.corpusItemsLabels

        self.clearmyBasket.setDisabled(self.myBasket == list())
        self.removeButton.setDisabled(self.corpusItems == list())


    # fonction qui retire la selection de notre panier
    def remove(self):
        """Remove the selected songs in your selection """
        self.myBasket = [
            song for idx, song in enumerate(self.myBasket)
            if idx not in self.corpusItems
        ]
        self.updatecorpusItemsLabels()
        self.sendButton.settingsChanged()


    # Clear selections function
    def clearmyBasket(self):
        """Remove all songs in your selection """
        self.corpusItemsLabels = list()
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
    WidgetPreview(Poetica).run()
