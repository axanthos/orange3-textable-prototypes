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
from Orange.widgets.utils.widgetpreview import WidgetPreview

from LTTL.Segmentation import Segmentation
import LTTL.Segmenter as Segmenter
from LTTL.Input import Input

from urllib.request import urlopen
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
        # Query criterias
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
            box="Select criteria",
            orientation="vertical",
        )

        # Import the poem's database.
        self.db = self.openDatabase()

        # Store the list of authors...
        self.authors_list = list()
        self.authors_list.append("Select an author")
        previous_author = ""
        for key, value in self.db["author"].items():
            if self.db["author"][key] != previous_author:
                self.authors_list.append(self.db["author"][key])
            previous_author = self.db["author"][key]

        # Allows to select an author in a list
        #  Uses "authorQuery" attribut
        gui.comboBox(
            widget=queryBox,
            master=self,
            value='authorQuery',
            items=self.authors_list,
            orientation='horizontal',
            label=u"Author : ",
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
            label=u"Date : ",
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
            label=u"Topic : ",
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
        # Add poems button
        self.addButton = gui.button(
            widget=boxbutton,
            master=self,
            label=u'Add to corpus',
            callback=self.add,
            tooltip=(
                u"Move the selected poem downward in your corpus."
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

        # area where confirmed poems are moved and stocked
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
        # Remove poems button
        self.removeButton = gui.button(
            widget=boxbutton2,
            master=self,
            label=u'Remove from corpus',
            callback=self.remove,
            tooltip=(
                u"Remove the selected poem from your corpus."
            ),
        )
        self.removeButton.setDisabled(True)

        # Delete all confirmed poems button
        self.clearmyBasket = gui.button(
            widget=boxbutton2,
            master=self,
            label=u'Clear corpus',
            callback=self.clearmyBasket,
            tooltip=(
                u"Remove all poems from your corpus."
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

    # Function to extract data...
    def dataExtraction(self):

        database = {
            "title": {},
            "author": {},
            "poem": {},
        }

        # Go to poetica's homepage...
        try:
            poetica_url = 'https://www.poetica.fr/'
            url_accueil = urlopen(poetica_url)
            page_accueil = url_accueil.read()
            print("Valid poetica's URL")
            page_accueil = page_accueil.decode("utf-8")
            # url_accueil.close()

            # Extract list of authors...
            base_seg = Input(page_accueil)
            condition = dict()
            condition["id"] = re.compile(r"^menu-poemes-par-auteur$")
            xml_auteurs = Segmenter.import_xml(
                segmentation=base_seg,
                element="<ul>",
                conditions=condition,
            )

            # Retrieve the url link to each author's page...
            xml_par_auteur = Segmenter.import_xml(
                segmentation=xml_auteurs,
                element="<a>",
            )

            # Go to each author's page...
            for auteur in xml_par_auteur:
                try:
                    url_page_auteur = auteur.annotations["href"]
                    url_auteur = urlopen(url_page_auteur)
                    page_auteur = url_auteur.read()
                    print("Valid author's URL")
                    page_auteur = page_auteur.decode("utf-8")

                    # Recover the author's name.
                    nom_auteur = auteur.get_content()

                    # Extract the list of poems...
                    seg_auteurs = Input(page_auteur)
                    condition_auteur = dict()
                    condition_auteur["class"] = re.compile(r"^entry-header$")
                    xml_poemes = Segmenter.import_xml(
                        segmentation=seg_auteurs,
                        element="<header>",
                        conditions=condition_auteur,
                    )

                    # Retrieve the url link to each poem's page...
                    xml_par_poeme = Segmenter.import_xml(
                        segmentation=xml_poemes,
                        element="<a>",
                    )

                    # Go to each poem's page...
                    for poeme in xml_par_poeme:
                        try:
                            url_page_poeme = poeme.annotations["href"]
                            url_poeme = urlopen(url_page_poeme)
                            page_poeme = url_poeme.read()
                            print("Valid poem's URL")
                            page_poeme = page_poeme.decode("utf-8")

                            # Recover the poem's name.
                            nom_poeme = poeme.get_content()

                            # Extract the poem and its data...
                            seg_poemes = Input(page_poeme)
                            condition_poeme = dict()
                            condition_poeme["class"] = re.compile(r"^entry-content$")
                            xml_contenu_poeme = Segmenter.import_xml(
                                segmentation=seg_poemes,
                                element="<div>",
                                conditions=condition_poeme,
                            )

                            # Retrieve the poem with its own tags.
                            poeme_balises = xml_contenu_poeme[0].get_content()

                            # Recuperer et associer la date de parution du poeme si elle est connue...

                            # Display only the contents of the poem...
                            poeme = re.sub(r"((</?p.*?>)|(<br />))|(<em>.*</em>)|(</p>)", "", poeme_balises)
                            poeme = re.sub(r".+$", "", poeme)
                            database["title"][url_page_poeme] = nom_poeme
                            database["author"][url_page_poeme] = nom_auteur
                            database["poem"][url_page_poeme] = poeme

                        # Warn if the url doesn't work...
                        except IOError:
                            print("Invalid poem's URL")

                # Warn if the url doesn't work...
                except IOError:
                    print("Invalid author's URL")

        # Warn if the url doesn't work...
        except IOError:
            print("Invalid poetica's URL")

        # Define a path to later locate the access path for the backup...
        path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )

        # Back up dictionaries with pickle...
        try:
            file = open(os.path.join(path, "poetica_cache.p"), "wb")
            pickle.dump(database, file)
            print('The dictionary has successfully been saved to the file')
            file.close()
        except IOError:
            print("Can't save the dictionary")

    # Function to open the database...
    def openDatabase(self):

        # Define a path to later locate the access path for the backup...
        path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )

        # Open dictionaries with pickle...
        try:
            file = open(os.path.join(path, "poetica_cache.p"), "rb")
            new_database = pickle.load(file)
            print("Dictionary correctly loaded")
            file.close()
        except IOError:
            print("Can't load the dictionary")

        # Return the stored dictionary.
        return new_database


    # Search button's features...
    def searchFunction(self):
        author_query = self.authorQuery
        # If the selection isn't empty...
        if str(author_query) != "":
            index = int(self.authorQuery)
            # Display a message.
            self.infoBox.setText(f"You search {self.authors_list[index]}. Select a poem", "warning")
            self.poemLabels = list()
            # For each author in the authors dictionnary.
            for key, value in self.db["author"].items():
                # If the dictionnary's author is equal to the selected author.
                if self.db["author"][key] == self.authors_list[index]:
                    # Store the poem's title...
                    self.poemLabels.append(self.db["title"][key])
            self.poemLabels = self.poemLabels
            self.clearButton.setDisabled(len(self.poemLabels) == 0)
        # If the selection is empty...
        else:
            self.infoBox.setText(f"You didn't select anything !",
                                 "warning")

    # Add button's features...
    def add(self):
        # If there is a selected poem...
        if self.selectedPoems:
            self.infoBox.setText(f"You add a poem", "warning")
            for poem_idx in self.selectedPoems:
                # Check if the poem is already in the basket or not...
                if self.poemLabels[poem_idx] in self.corpusItemsLabels:
                    self.infoBox.setText(f"The poem '{self.poemLabels[poem_idx]}' is already in your basket", "warning")
                else:
                    # Add the poem to the list "corpusItemsLabels"...
                    self.corpusItemsLabels.append(self.poemLabels[poem_idx])
            self.corpusItemsLabels = self.corpusItemsLabels
            # Make the "clear" button usable.
            self.clearmyBasket.setDisabled(len(self.corpusItemsLabels) == 0)
        else:
            self.infoBox.setText(f"Select a poem", "warning")


    # Function clearing the results list
    def clearResults(self):
        """Clear the results list"""
        del self.poemLabels[:]
        self.poemLabels = self.poemLabels
        self.clearButton.setDisabled(True)
        self.addButton.setDisabled(self.poemLabels == list())


    # Update selections function
    def updatecorpusItemsLabels(self):
        self.corpusItemsLabels = list()
        for poemData in self.myBasket:
            result_string = poemData["title"] + " - " + poemData["artist"]
            self.corpusItemsLabels.append(result_string)
        self.corpusItemsLabels = self.corpusItemsLabels

        self.clearmyBasket.setDisabled(self.myBasket == list())
        self.removeButton.setDisabled(self.corpusItems == list())


    # fonction qui retire la selection de notre panier
    def remove(self):
        """Remove the selected poems in your selection """
        self.myBasket = [
            poem for idx, poem in enumerate(self.myBasket)
            if idx not in self.corpusItems
        ]
        self.updatecorpusItemsLabels()
        self.sendButton.settingsChanged()


    # Clear selections function
    def clearmyBasket(self):
        """Remove all poems in your selection """
        self.corpusItemsLabels = list()
        self.myBasket = list()
        self.sendButton.settingsChanged()
        self.clearmyBasket.setDisabled(True)

    # Function computing results then sending them to the widget output
    def sendData(self):
        """Compute result of widget processing and send to output"""
        # Skip if title list is empty:
        if self.corpusItemsLabels == list():
            self.infoBox.setText(
                "Your corpus is empty, please add some poems first",
                "warning"
            )
            return

        # Clear created Inputs.
        self.clearCreatedInputs()

        self.controlArea.setDisabled(True)

        # Initialize progress bar.
        progressBar = ProgressBar(
            self,
            iterations=len(self.corpusItemsLabels)
        )

        # Attempt to connect to Genius and retrieve lyrics...
        selectedSongs = list()
        song_content = list()
        annotations = list()
        try:
            for song in self.corpusItemsLabels:
                # song is a dict {'idx1':{'title':'song1'...},
                # 'idx2':{'title':'song2'...}}
                # page_url = "http://genius.com" + song['path']
                # lyrics = self.html_to_text(page_url)
                song_content.append(song)
                # annotations.append(song.copy())
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
        for poem in poem_content:
            newInput = Input(poem, self.captionTitle)
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
        # for idx, segment in enumerate(self.segmentation):
        #    segment.annotations.update(annotations[idx])
        #    self.segmentation[idx] = segment

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

        self.send("Poems importation", self.segmentation, self)
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
