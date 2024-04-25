"""
Class Childes
Copyright 2019 University of Lausanne
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

__version__ = "0.0.2"
__author__ = "David Fluhmann, Leonardo Cavaliere, Kirill Melnikov"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

import os
import re
import copy
import PyQt5
import urllib
import pickle
import inspect
import requests
import LTTL.Segmenter as Segmenter
from LTTL.Input import Input
from bs4 import BeautifulSoup
from urllib import request, parse
from LTTL.Segmentation import Segmentation
from Orange.widgets import Orange, widget, gui, settings
from fuzzywuzzy import fuzz, process
from _textable.widgets.TextableUtils import ProgressBar
from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton,
)

class MovieTranscripts(OWTextableBaseWidget):
    """Textable widget for importing movie scripts from the 
    springfieldspringfield.co.uk website 
    (https://www.springfieldspringfield.co.uk)
    """

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Movie Transcripts"
    description = "Import movie transcripts from www.springfieldspringfield.co.uk"
    icon = "icons/Movie_Transcripts.png"
    priority = 11

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = []
    outputs = [("Movie transcripts", Segmentation)]

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

    # Other class variables...

    cacheFilename = "cache_movie_transcripts"

    def __init__(self):
        """Widget creator."""

        super().__init__()

        # ATTRIBUTS
        # searchFunction
        self.searchResults = None
        self.inputSeg = None
        # newQuery = attribut box lineEdit (search something)
        self.newQuery = ''
        # Results box attributs
        self.titleLabels = list()
        self.selectedTitles = list()
        # selections box attributs
        self.myTitles = list()
        self.mytitleLabels = list()
        # stock all the inputs (scripts) in a list
        self.createdInputs = list()
        # stock the part of dictionary that will be used to access script's page
        self.path_storage = dict()
        # stock titles of movies
        self.movie_titles = list()
        # stock all the movies titles and link parts
        self.title_to_href = dict()

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

        # User interface...
        # Create the working area
        queryBox = gui.widgetBox(
            widget=self.controlArea,
            box="Search movie",
            orientation="vertical",
            )

        searchBox = gui.widgetBox(
            widget=queryBox,
            orientation="horizontal",
            )

        # Allows to enter specific text to the research
        #  Uses "newQuery" attribute
        gui.lineEdit(
            widget=searchBox,
            master=self,
            value='newQuery',
            orientation='horizontal',
            labelWidth=100,
            tooltip=("Enter a movie title"),
            )

        # Research button
        # Use "searchFunction" attibute
        self.searchButton = gui.button(
            widget=searchBox,
            master=self,
            label='Search',
            callback=self.searchFunction,
            tooltip='Search for the movie',
            )
        gui.separator(widget=queryBox, height=3)

        # Button that refresh all movie titles from the website
        self.refreshButton = gui.button(
            widget=queryBox,
            master=self,
            label="Refresh database",
            callback=self.refreshTitles,
            tooltip="Update SpringfieldSpringfield database"
            )

        # Box that displays search results
        self.titleListbox = gui.listBox(
            widget=queryBox,
            master=self,
            value="selectedTitles",    # setting (list)
            labels="titleLabels",      # setting (list)
            callback=lambda: self.selectButton.setDisabled(
                self.selectedTitles == list()),
            tooltip="Select the movie transcript you want to import",
            )
        self.titleListbox.doubleClicked.connect(self.Add)
        self.titleListbox.setMinimumHeight(120)
        self.titleListbox.setSelectionMode(3)

        boxbutton = gui.widgetBox(
            widget=queryBox,
            box=False,
            orientation='horizontal',
            )

        # Add button
        # Uses "Add" function
        self.selectButton = gui.button(
            widget=boxbutton,
            master=self,
            label="Add to corpus",
            callback=self.Add,
            tooltip="Add selected movie to the corpus",
            )
        self.selectButton.setDisabled(True)

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

        # Area where confirmed movies are moved and stocked
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
        self.mytitleListbox.doubleClicked.connect(self.Remove)
        self.mytitleListbox.setMinimumHeight(150)
        self.mytitleListbox.setSelectionMode(3)

        boxbutton2 = gui.widgetBox(
            widget=mytitleBox,
            box=False,
            orientation='horizontal',
            )
        # Remove movies button
        self.removeButton = gui.button(
            widget=boxbutton2,
            master=self,
            label=u'Remove from corpus',
            callback=self.Remove,
            tooltip="Remove the selected movie from your corpus.",
            )
        self.removeButton.setDisabled(True)

        # Delete all confirmed movies button
        self.clearmyBasket = gui.button(
            widget=boxbutton2,
            master=self,
            label=u'Clear corpus',
            callback=self.ClearmyCorpus,
            tooltip="Remove all movies from your corpus.",
            )
        self.clearmyBasket.setDisabled(True)

        gui.rubber(self.controlArea)

    #----------------------------------------------------------------------

        # Draw Info box and Send button
        self.sendButton.draw()
        self.searchButton.setDefault(True)
        self.infoBox.draw()

        # This initialization step needs to be done after infoBox has been
        # drawn (because we may need to display an error message).
        self.loadDatabaseCache()

        # Make sure that whatever was in the corpus last time is deleted
        self.ClearmyCorpus()

        # Send data if autoSend.
        self.sendButton.sendIf()

    def searchFunction(self):
        """Perform the search"""
        self.controlArea.setDisabled(True)

        # Search from the springfieldspringfield.co.uk
        query_string = self.newQuery
        testdict = self.title_to_href

        # Reset and clear the visible widget list
        del self.titleLabels[:]
        self.titleLabels = self.titleLabels
        del self.movie_titles[:]
        self.movie_titles = self.movie_titles

        if query_string != "":
            # Initialize progress bar.
            progressBar = ProgressBar(self, iterations=1)

            self.searchResults = process.extractBests(
                query_string, 
                testdict,
                limit=100000,
                score_cutoff=80
            )

            progressBar.finish()

            progressBar = ProgressBar(self, iterations=len(self.searchResults))

            for key, score, val in self.searchResults:
                self.titleLabels.append(val)
                self.movie_titles.append(val)
                self.path_storage[val] = key
                # 1 tick on the progress bar of the widget
                progressBar.advance()

            self.titleLabels = self.titleLabels
            self.clearButton.setDisabled(False)
            self.controlArea.setDisabled(False)

            # Clear progress bar.
            progressBar.finish()

            if self.searchResults:
                self.infoBox.setText("Search complete")
            elif self.searchResults == []:
                self.infoBox.setText("No result please try again", 'warning')

        else:
            self.infoBox.setText(
                "Please, enter a query in a search bar", 
                "warning"
            )
            self.controlArea.setDisabled(False)

    def clearResults(self):
        """Clear the results list"""
        del self.titleLabels[:]
        self.titleLabels = self.titleLabels
        del self.movie_titles[:]
        self.movie_titles = self.movie_titles
        self.clearButton.setDisabled(True)

    def loadDatabaseCache(self):
        """Load the cached database"""
        # Try to open saved file in this module's directory...

        path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )
        try:
            file = open(os.path.join(path, self.__class__.cacheFilename), "rb")
            self.title_to_href = pickle.load(file)
            file.close()

        # Else try to rebuild cache from SpringfieldSpringfield website...
        except IOError:
            self.refreshTitles()

    def refreshTitles(self):
        """Refresh the database cache"""

        basepath = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
            )
        cachedFilename = self.__class__.cacheFilename

        dialog = PyQt5.QtWidgets.QMessageBox()
        response = dialog.question(
            self,
            "springfieldspringfield",
            "Are you sure you want to refresh the database?\n"
            + "It will take several minutes",
            dialog.Yes | dialog.No
        )

        self.infoBox.setText(
            "Scraping SpringfieldSpringfield website, please wait...",
            "warning",
        )
        self.warning("Warning : it will take several minutes")
        if response == dialog.No:
            return
        else:
            try:
                self.get_all_titles()
                try:
                    path = os.path.dirname(
                        os.path.abspath(inspect.getfile(inspect.currentframe()))
                    )
                    file = open(
                        os.path.join(path, self.__class__.cacheFilename),
                        "wb",
                    )
                    pickle.dump(self.title_to_href, file)
                    file.close()
                    self.infoBox.setText(
                        "Database successfully updated",
                    )
                except IOError:
                    self.infoBox.setText(
                        "Couldn't save database to disk.",
                        "warning",
                    )
            except requests.exceptions.ConnectionError:
                self.infoBox.setText(
                    "Error while attempting to scrape the "
                    + "SpringfieldSpringfield website.",
                    "error",
                )


	# Get all movie titles from www.springfieldspringfield.co.uk
    def get_all_titles(self):
        """Get all movie titles from www.springfieldspringfield.co.uk"""
        
        '''php_query_string and http_query_string are the variable that will need to be changed
        if different database is used or if current database's structure undergoes changes'''
        php_query_string = '/movie_script.php?movie='
        http_query_string = 'https://www.springfieldspringfield.co.uk/' +   \
                            'movie_scripts.php?order='
        alphabet = ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 
                    'K', 'L', 'M', 'N', 'O', 'P', 'K', 'R', 'S', 'T', 'U', 
                    'V', 'W', 'X', 'Y', 'Z']

        # Initialize progress bar.
        progressBar = ProgressBar(
            self,
            iterations=len(alphabet)
        )
        self.controlArea.setDisabled(True)

        try:
            for lettre in alphabet:
                page_num = 1
                # 1 tick on the progress bar of the widget
                progressBar.advance()

                # This part of code is what gets all the movie titles from each
                # page of the database
                while True:
                    page_url = http_query_string + '%s&page=%i' % (
                        lettre, 
                        page_num,
                    )
                    page = urllib.request.urlopen(page_url)
                    soup = BeautifulSoup(page, 'html.parser')
                    # script_links is a variable that may need to be changed if 
                    # another database is used or current database undergoes 
                    # change
                    script_links = soup.find_all('a', class_=re.compile(r"^btn btn-dark btn-sm"))
                    
                    if not script_links:
                        break
                    links = dict()
                    for link in soup.find_all('a', class_=re.compile(r"^btn btn-dark btn-sm")):
                        links[link.text] =  \
                            link.get('href')[len(php_query_string):]
                    self.title_to_href.update(links)
                    page_num += 1

        except:
            self.infoBox.setText(
                "Couldn't download data from springfieldspringfield website.",
                "error"
            )
        # Clear progress bar.
        progressBar.finish()
        self.controlArea.setDisabled(False)
        return self.title_to_href

    # Add Movies function
    def Add(self):
        """Add movies in your selection """
        for selectedTitle in self.selectedTitles:
            movie_title = self.titleLabels[selectedTitle]
            if movie_title not in self.myBasket:
                self.myBasket.append(movie_title)
                self.mytitleLabels.append(movie_title)
                self.mytitleLabels = self.mytitleLabels
        self.clearmyBasket.setDisabled(False)
        self.sendButton.settingsChanged()

    # Remove movies function
    def Remove(self):
        """Remove the selected songs in your selection """
        self.myBasket = [
            movie for idx, movie in enumerate(self.myBasket)
            if idx not in self.myTitles
        ]
        self.updateMytitleLabels()
        self.sendButton.settingsChanged()


    def ClearmyCorpus(self):
        """Clears your selection """
        del self.mytitleLabels[:]
        del self.myBasket[:]
        self.mytitleLabels = self.mytitleLabels
        self.clearmyBasket.setDisabled(True)
        self.sendButton.settingsChanged()


    def updateMytitleLabels(self):
        """Update selections function"""
        self.mytitleLabels = list()
        for movie in self.myBasket:
            self.mytitleLabels.append(movie)
        self.mytitleLabels = self.mytitleLabels

        self.clearmyBasket.setDisabled(self.myBasket == list())
        self.removeButton.setDisabled(self.myTitles == list())


    # Create the final output with the script
    def sendData(self):
        """Send data from website springfieldspringfield"""
        # Skip if title list is empty:
        if self.myBasket == list():
            self.infoBox.setText(
                "Your corpus is empty, please add some movies first",
                "warning"
            )
            self.segmentation = None
            self.send("Movie transcripts", self.segmentation, self)
            return

        # Clear created Inputs.
        self.clearCreatedInputs()

        annotations = list()
        script_list = list()
        annotations_dict = dict()
        self.controlArea.setDisabled(True)

        # Initialize progress bar.
        progressBar = ProgressBar(self, iterations=len(self.myBasket))

        # This part of code is what fetches the actual script
        try:
            for movie in self.myBasket:
                # Each movie that is in the corpus is split into title and year
                # (rsplit makes sure to only split last occurence) which will 
                # become annotations
                b = copy.copy(movie)
                future_annotation = b.rsplit('(', 1)
                movie_title = future_annotation[0]
                movie_year = future_annotation[-1]
                movie_year = movie_year[:-1]
                annotations_dict["Movie Title"] = movie_title
                annotations_dict["Year of release"] = movie_year
                # It is important to make a copy of dictionary, otherwise each 
                # iteration will replace every element of the annotations list
                annotations.append(annotations_dict.copy())
                # link_end and page_url are the two variables that will have to
                # be changed in case scripts need to be taken from elsewhere
                link_end = self.path_storage[movie]
                page_url = "https://www.springfieldspringfield.co.uk/" +   \
                    "movie_script.php?movie=" + link_end
                page = urllib.request.urlopen(page_url)
                soup = BeautifulSoup(page, 'html.parser')

                # This is what grabs the movie script
                script = soup.find("div", {"class":"movie_script"})

                script_list.append(script.text)

                # 1 tick on the progress bar of the widget
                progressBar.advance()

        except:
            self.infoBox.setText(
                "Couldn't download data from SpringfieldSpringfield website.",
                "error"
            )
            self.controlArea.setDisabled(False)
            return

        # Store downloaded script strings in input objects...
        for script in script_list:
            newInput = Input(script, self.captionTitle)
            self.createdInputs.append(newInput)

       # If there's only one play, the widget"s output is the created Input.
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

        self.send("Movie transcripts", self.segmentation, self)
        self.sendButton.resetSettingsChangedFlag()



    def clearCreatedInputs(self):
        """Delete all Input objects that have been created."""
        del self.createdInputs[:]


    def setCaption(self, title):
        """The following method needs to be copied verbatim in
        every Textable widget that sends a segmentation"""
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.SendButton.settingsChanged()
        else:
            super().setCaption(title)



if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    myApplication = QApplication(sys.argv)
    myWidget = MovieTranscripts()
    myWidget.show()
    myApplication.exec_()
    myWidget.saveSettings()
