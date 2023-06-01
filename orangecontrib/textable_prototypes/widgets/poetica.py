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

# Import the useful packages...
from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar,
)

from LTTL.Segmentation import Segmentation
import LTTL.Segmenter as Segmenter
from LTTL.Input import Input

from PyQt5.QtWidgets import QMessageBox

from urllib.request import urlopen

import inspect
import re
import pickle
import os

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
    corpus = settings.Setting([])

    def __init__(self):
        """
        Widget creator
        """

        super().__init__()

        # ATTRIBUTS
        # searchFunction...
        self.searchResults = None
        self.inputSeg = None
        # Query criterias...
        self.authorQuery = 'Select an author'
        self.topicQuery = 'Select a topic'
        # Results box attributs...
        self.results = list()
        self.resultLabels = list()
        self.resultSelectedItems = list()
        # Corpus box attributs...
        self.corpusSelectedItems = list()
        self.corpusLabels = list()
        # Stocks all the inputs (poems) in a list.
        self.createdInputs = list()
        # Cache dictionnary.
        self.cache = dict()

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
        # Create the working area...
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
        for author in sorted(set(self.db["author"].values())):
            self.authors_list.append(author)

        # Store the list of topics...
        self.topics_list = list()
        self.sorted_topics_list = list()
        self.final_topics_list = list()
        self.final_topics_list.append("Select a topic")
        for topic in sorted(set(self.db["topic"].values())):
            self.final_topics_list.append(topic)

        # Allows to select an author in a list...
        # Uses "authorQuery" attribut...
        gui.comboBox(
            widget=queryBox,
            master=self,
            value='authorQuery',
            items=self.authors_list,
            orientation='horizontal',
            label=u"Author : ",
            labelWidth=120,
            tooltip=("Select an author"),
            sendSelectedValue=True,

        )

        # Allows to select a topic in a list...
        # Uses "topicQuery" attribut...
        gui.comboBox(
            widget=queryBox,
            master=self,
            value='topicQuery',
            items=self.final_topics_list,
            orientation='horizontal',
            label=u"Topic : ",
            labelWidth=120,
            tooltip=("Select topic"),
            sendSelectedValue=True,

        )

        # Research button...
        # Uses "searchFunction" attribut...
        self.searchButton = gui.button(
            widget=queryBox,
            master=self,
            label="Search",
            callback=self.searchFunction,
            tooltip="Connecter Poetica et effectuer une recherche",
        )

        # Refresh Button...
        self.refreshButton = gui.button(
            widget=queryBox,
            master=self,
            label="Refresh database",
            callback=self.alertMessage,
            tooltip="Attention ! Cela peut prendre un peu de temps…",
        )

        # Basket of found items...
        self.resultBox = gui.listBox(
            widget=queryBox,
            master=self,
            value="resultSelectedItems",    # setting (list)
            labels="resultLabels",      # setting (list)
            callback=lambda: self.addButton.setDisabled(
                self.resultSelectedItems == list()),
            tooltip="The list of poems whose content will be imported",
        )
        self.resultBox.setMinimumHeight(150)
        self.resultBox.setSelectionMode(3)

        boxbutton = gui.widgetBox(
            widget=queryBox,
            box=False,
            orientation='horizontal',
        )

        # Add poems button...
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

        # Clear button...
        # Uses "clearResults" function...
        self.clearResultsButton = gui.button(
            widget=boxbutton,
            master=self,
            label="Clear results",
            callback=self.clearResults,
            tooltip="Clear results",
        )
        self.clearResultsButton.setDisabled(True)
        gui.separator(widget=queryBox, height=3)

        # area where confirmed poems are moved and stocked...
        mytitleBox = gui.widgetBox(
            widget=self.controlArea,
            box="Corpus",
            orientation="vertical",
        )

        # Basket of selected items...
        self.corpusBox = gui.listBox(
            widget=mytitleBox,
            master=self,
            value="corpusSelectedItems",
            labels="corpusLabels",
            callback=lambda: self.removeButton.setDisabled(
                self.corpusSelectedItems == list()),
            tooltip="The list of titles whose content will be imported",
        )
        self.corpusBox.setMinimumHeight(150)
        self.corpusBox.setSelectionMode(3)

        boxbutton2 = gui.widgetBox(
            widget=mytitleBox,
            box=False,
            orientation='horizontal',
        )
        # Remove poems button...
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

        # Delete all button...
        self.clearCorpusButton = gui.button(
            widget=boxbutton2,
            master=self,
            label=u'Clear corpus',
            callback=self.clearCorpus,
            tooltip=(
                u"Remove all poems from your corpus."
            ),
        )
        self.clearCorpusButton.setDisabled(True)

        gui.separator(widget=mytitleBox, height=3)
        gui.rubber(self.controlArea)

        #----------------------------------------------------------------------

        # Draw Info box and Send button...
        self.sendButton.draw()
        self.searchButton.setDefault(True)
        self.infoBox.draw()

        self.updateCorpusLabels()
        self.updateResultLabels()

    def alertMessage(self):
        """
        Confirmation request message to refresh the database
        """
        QMessageBox.information(
            None,
            'Poetica',
            'Are you sure you want to refresh the database ? This may take some time.',
            QMessageBox.Ok
        )

    def dataExtraction(self):
        """
        Function to extract data
        """

        database = {
            "title": {},
            "author": {},
            "topic": {},
        }

        # Go to Poetica's homepage...
        try:
            poetica_url = 'https://www.poetica.fr/'
            url_accueil = urlopen(poetica_url)
            page_accueil = url_accueil.read()
            print("Valid poetica's URL")
            page_accueil = page_accueil.decode("utf-8")

            # Extract the list of authors...
            base_seg = Input(page_accueil)
            condition = dict()
            condition["id"] = re.compile(r"^menu-poemes-par-auteur$")
            xml_auteurs = Segmenter.import_xml(
                segmentation=base_seg,
                element="<ul>",
                conditions=condition,
            )

            # Extract the list of topics...
            seg_themes = Input(page_accueil)
            condition_themes = dict()
            condition_themes["id"] = re.compile(r"^menu-poemes-par-theme$")
            xml_themes = Segmenter.import_xml(
                segmentation=seg_themes,
                element="<ul>",
                conditions=condition_themes,
            )

            # Recover the url ink to each author's page...
            xml_par_auteur = Segmenter.import_xml(
                segmentation=xml_auteurs,
                element="<a>",
            )

            # Recover the url ink to each topic's page...
            xml_par_theme = Segmenter.import_xml(
                segmentation=xml_themes,
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

                    # Extract the list poems...
                    seg_auteurs = Input(page_auteur)
                    condition_auteur = dict()
                    condition_auteur["class"] = re.compile(r"^entry-header$")
                    xml_poemes = Segmenter.import_xml(
                        segmentation=seg_auteurs,
                        element="<header>",
                        conditions=condition_auteur,
                    )

                    # Recover the url link to each poem's page...
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

                            # Recuperer le nom du poeme.
                            nom_poeme = poeme.get_content()

                            database["title"][url_page_poeme] = nom_poeme
                            database["author"][url_page_poeme] = nom_auteur

                        # Warn if the url doesn't work...
                        except IOError:
                            print("Invalid poem's URL")

                # Warn if the url doesn't work...
                except IOError:
                    print("Invalid author's URL")

            # Go to each topic's page...
            for theme in xml_par_theme:
                try:
                    url_page_theme = theme.annotations["href"]
                    url_theme = urlopen(url_page_theme)
                    page_theme = url_theme.read()
                    print("Valid topic's URL")
                    page_theme = page_theme.decode("utf-8")

                    # Recover the topic's name.
                    nom_theme = theme.get_content()

                    # Extract the list of poems...
                    seg_themes = Input(page_theme)
                    condition_themes = dict()
                    condition_themes["class"] = re.compile(r"^entry-header$")
                    xml_poemes_themes = Segmenter.import_xml(
                        segmentation=seg_themes,
                        element="<header>",
                        conditions=condition_themes,
                    )

                    # Recover the url link to each poem's page...
                    xml_par_theme = Segmenter.import_xml(
                        segmentation=xml_poemes_themes,
                        element="<a>",
                    )

                    # Go to each poem's page...
                    for poeme_theme in xml_par_theme:
                        try:
                            url_page_poeme_theme = poeme_theme.annotations["href"]

                            database["topic"][url_page_poeme_theme] = nom_theme

                        # Warn if the url doesn't work...
                        except IOError:
                            print("Invalid poem's URL")

                # Warn if the url doesn't work...
                except IOError:
                    print("Invalid topic's URL")

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

    def openDatabase(self):
        """
        Function to open the database
        """

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

    def searchFunction(self):
        """
        Search button's features
        """

        # If the selection is empty...
        if self.authorQuery == "Select an author" and self.topicQuery == "Select a topic":
            self.infoBox.setText(f"You didn't select anything !", "warning")
            return

        all_urls = self.db["author"].keys()

        selected_urls = list()
        # If an author has been selected...
        if self.authorQuery != "Select an author":
            for url in all_urls:
                if self.db["author"][url] == self.authorQuery:
                    selected_urls.append(url)
            all_urls = selected_urls

        # If a topic has been selected...
        if self.topicQuery != "Select a topic":
            selected_urls = list()
            for url in all_urls:
                try:
                    if self.topicQuery in self.db["topic"][url]:
                        selected_urls.append(url)
                except KeyError:
                    pass

        # Show results found in the first basket...
        self.results = selected_urls[:]
        self.updateResultLabels()

    def updateResultLabels(self):
        """
        TO DO
        """

        self.resultLabels = list()
        for url in self.results :
            self.resultLabels.append(f"{self.db['title'][url]} ({self.db['author'][url]})")
        self.resultLabels = self.resultLabels
        self.clearResultsButton.setDisabled(len(self.resultLabels) == 0)
        self.addButton.setDisabled(self.resultLabels == list())

    def add(self):
        """
        Add button's features
        """

        # If there is a selected poem...
        if self.resultSelectedItems:
            self.infoBox.setText(f"You add a poem", "warning")
            for poem_idx in self.resultSelectedItems:
                # Check if the poem is already in the basket or not...
                print(self.results[poem_idx], self.corpus)
                if self.results[poem_idx] in self.corpus:
                    pass
                else:
                    # Add the poem to the list "corpusLabels"...
                    self.corpus.append(self.results[poem_idx])
            self.updateCorpusLabels()
        else:
            self.infoBox.setText(f"Select a poem", "warning")

    def updateCorpusLabels(self):
        """
        TO DO
        """

        self.corpusLabels = list()
        for url in self.corpus :
            self.corpusLabels.append(f"{self.db['title'][url]} ({self.db['author'][url]})")
        self.corpusLabels = self.corpusLabels
        self.clearCorpusButton.setDisabled(len(self.corpusLabels) == 0)
        self.sendButton.settingsChanged()

        # Send data if autoSend.
        self.sendButton.sendIf()

    def clearResults(self):
        """
        Clear the results list
        """

        self.results = list()
        self.updateResultLabels()

    def remove(self):
        """
        Remove the selected poems in the selection
        """

        self.corpus = [
            poem for idx, poem in enumerate(self.corpus)
            if idx not in self.corpusSelectedItems
        ]
        self.updateCorpusLabels()

    # Clear selections function
    def clearCorpus(self):
        """
        Clear the selected poems list in the basket
        """

        self.corpus = list()
        self.updateCorpusLabels()

    def sendData(self):
        """
        Compute result of widget processing and send to output
        """

        # Skip if title list is empty...
        if self.corpus == list():
            self.infoBox.setText(
                "Your corpus is empty, please add some poems first",
                "warning"
            )
            return

        # Clear created Inputs.
        self.clearCreatedInputs()

        self.controlArea.setDisabled(True)

        # Initialize progress bar...
        progressBar = ProgressBar(
            self,
            iterations=len(self.corpus)
        )

        # Attempt to connect to Poetica and retrieve poems...
        poem_content = list()

        annotations_list_authors = list()
        annotations_list_tiles = list()
        annotations_list_urls = list()
        annotations_list_topics = list()

        annotations_author = dict()
        annotations_title = dict()
        annotations_url = dict()
        annotations_topic = dict()

        #try:
        for url in self.corpus:
            # If the poem is already in the cache...
            if url in self.cache:
                poem_content.append(self.cache[url])

            # If the poem isn't already in the cache...
            else:
                try:
                    url_poeme = urlopen(url)
                    page_poeme = url_poeme.read()
                    print("Valid poem's URL")
                    page_poeme = page_poeme.decode("utf-8")

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

                    # N'afficher que le contenu du poeme...
                    poeme = re.sub(r"((</?p.*?>)|(<br />))|(<em>.*</em>)|(</p>)", "", poeme_balises)
                    poeme = re.sub(r".+$", "", poeme)
                    # print(poeme)
                    poem_content.append(poeme)
                    self.cache[url] = poeme

                # Avertir si l'url ne fonctionne pas...
                except IOError:
                    print("Invalid poem's URL")

            # Annotate the poem...
            annotations_author["Author"] = self.db["author"][url]
            annotations_title["Title"] = self.db["title"][url]
            annotations_url["URL"] = url
            try:
                annotations_topic["Topic"] = self.db["topic"][url]
            except KeyError:
                pass

            # if self.topicQuery != "Select a topic":
            #     annotations_topic["Topic"] = self.topicQuery
            # else:
            #     if key in self.db["topic"] :
            #         annotations_topic["Topic"] = self.db["topic"][key]
            #     else :
            #         annotations_topic["Topic"] = "None"

            annotations_list_authors.append(annotations_author.copy())
            annotations_list_tiles.append(annotations_title.copy())
            annotations_list_urls.append(annotations_url.copy())
            annotations_list_topics.append(annotations_topic.copy())

            # 1 tick on the progress bar of the widget
            progressBar.advance()

        # If an error occurs (e.g. http error, or memory error)...
        # except:
        #     # Set Info box and widget to "error" state.
        #     self.infoBox.setText(
        #         "Couldn't download data from Poetica's website.",
        #         "error"
        #     )
        #     self.controlArea.setDisabled(False)
        #     return

        # Store downloaded poems strings in input objects...
        for poem in poem_content:
            newInput = Input(poem, self.captionTitle)
            self.createdInputs.append(newInput)

        # If there's only one play, the widget's output is the created Input...
        if len(self.createdInputs) == 1:
            self.segmentation = self.createdInputs[0]

        # Otherwise the widget's output is a concatenation...
        else:
            self.segmentation = Segmenter.concatenate(
                self.createdInputs,
                self.captionTitle,
                import_labels_as=None,
            )

        # Annotate segments...
        for idx, segment in enumerate(self.segmentation):
            segment.annotations.update(annotations_list_authors[idx])
            segment.annotations.update(annotations_list_tiles[idx])
            segment.annotations.update(annotations_list_urls[idx])
            segment.annotations.update(annotations_list_topics[idx])
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

        self.send("Poems importation", self.segmentation, self)
        self.sendButton.resetSettingsChangedFlag()


    def clearCreatedInputs(self):
        """
        Delete all Input objects that have been created
        """

        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]

    def setCaption(self, title):
        """
        This method needs to be copied verbatim in every Textable widget that sends a segmentation
        """

        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)


if __name__ == "__main__":
    WidgetPreview(Poetica).run()
