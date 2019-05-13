__version__ = u"0.0.2"
__author__ = "David Fluhmann, Leonardo Cavaliere, Kirill Melnikov"
__maintainer__ = "Aris Xanthos"
__email__ = "david.fluhmann@unil.ch, leonardo.cavaliere@unil.ch, kirill.melnikov@unil.ch"

from Orange.widgets import widget, gui, settings

from LTTL.Segmentation import Segmentation
import LTTL.Segmenter as Segmenter
from LTTL.Input import Input

import urllib
import urllib.request
import urllib.parse
import json
import pickle
import requests
import inspect
import os
from urllib import request, parse
from bs4 import BeautifulSoup
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process



from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, 
)

class MovieScripts(OWTextableBaseWidget):
    """Textable widget for importing movie scripts from the website IMSDB.com
    (https://www.imsdb.com)
    """

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Movie Scripts"
    description = "Movie Script Importation"
    icon = "icons/Movie_Scripts.png"
    priority = 11

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = []
    outputs = [("Movie Scripts importation", Segmentation)]

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

    # Other class variables...

    cacheFilename = "cache_springfield"

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
        self.path_storage = list()
        # stock all the movies titles
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

        # Allows to enter specific text to the research
        #  Uses "newQuery" attribute
        gui.lineEdit(
            widget=queryBox,
            master=self,
            value='newQuery',
            orientation='horizontal',
            label=u"Movie title: ",
            labelWidth=100,
            tooltip=("Enter a string"),
        )

        # Button that refresh all movie titles from the website
        self.refreshButton = gui.button(
            widget = queryBox,
            master = self,
            label = "Refresh DataBase",
            callback = self.refreshTitles,
            tooltip = "update SpringfieldSpringfield DataBase"
            )


        # Research button 
        # Use "searchFunction" attibute
        self.searchButton = gui.button(
        	widget=queryBox,
        	master=self,
        	label='Search',
        	callback=self.searchFunction,
        	tooltip='Search for the movie',
        	)

        # Reasearch button
        # Uses "searchFunction" attribute
        self.titleListbox = gui.listBox(
            widget=queryBox,
            master=self,
            value="selectedTitles",    # setting (list)
            labels="titleLabels",      # setting (list)
            callback=lambda: self.selectButton.setDisabled(
                self.selectedTitles == list()),
            tooltip="Select the movie you want to get the script of",
        )
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
            label="Add",
            callback=None,
            tooltip="Select",
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
        gui.separator(widget=queryBox, height=3)

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
            label=u'Remove',
            callback=None,
            tooltip="Remove the selected song from your corpus.",
        )
        self.removeButton.setDisabled(True)

        # Delete all confirmed movies button
        self.clearmyBasket = gui.button(
            widget=boxbutton2,
            master=self,
            label=u'Clear corpus',
            callback=None,
            tooltip=
                "Remove all movies from your corpus.",
        )
        self.clearmyBasket.setDisabled(True)

        gui.rubber(self.controlArea)

    #----------------------------------------------------------------------

        # Draw Info box and Send button
        self.sendButton.draw()
        # self.searchButton.setDefault(True)
        self.infoBox.draw()
		
        # This initialization step needs to be done after infoBox has been
        # drawn (because we may need to display an error message).
        self.loadDatabaseCache()


        # Send data if autoSend.
        # self.sendButton.sendIf()



    def searchFunction(self):
        #Search from the springfieldspringfield.co.uk

        result_list = dict()
        query_string = self.newQuery
        testdict = self.title_to_href
        # Reset and clear the visible widget list
        del self.titleLabels[:]
		
        if query_string != "":
            searchResults = process.extractBests(query_string, testdict, limit = 100000, score_cutoff=70)
            for key,score,val in searchResults:
                self.titleLabels.append(val)
                self.path_storage.append(key)
		
            self.titleLabels = self.titleLabels
            self.clearButton.setDisabled(False)
            self.controlArea.setDisabled(False)
            self.infoBox.setText("Search complete")
            self.searchResults = result_list
        else:
            self.infoBox.setText("You didn't search anything", "warning")



    def clearResults(self):
        """Clear the results list"""
        del self.titleLabels[:]
        self.titleLabels = self.titleLabels
        self.clearButton.setDisabled(True)
		
    def loadDatabaseCache(self):
        """Load the cached database"""
        # Try to open saved file in this module"s directory...
        path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )
        try:
            file = open(os.path.join(path, self.__class__.cacheFilename),"rb")
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
        if os.path.exists(cachedFilename) and list(os.walk('.'))[0]:
            dialog = AnyQt.QtGui.QMessageBox()
            response = dialog.question(
                self,
                "springfieldspringfield", 
                "Keep previously saved files?", 
                dialog.Yes | dialog.No
            )

        self.infoBox.setText(
            "Scraping springfieldspringfield website, please wait...", 
            "warning",
        )     
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
                "Error while attempting to scrape the SpringfieldSpringfield website.", 
                "error",)


	# Get all movie titles from www.springfieldspringfield.co.uk
    def get_all_titles(self):
        php_query_string = '/movie_script.php?movie='
        http_query_string = 'https://www.springfieldspringfield.co.uk/movie_scripts.php?order='

        try:
            for lettre in ['0']:#, 'A']:, 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                       #'N', 'O', 'P', 'K', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
                page_num = 1

                while True:
                    page_url = http_query_string + '%s&page=%i' % (lettre, page_num)
                    page = urllib.request.urlopen(page_url)
                    soup = BeautifulSoup(page, 'html.parser')
                    script_links = soup.findAll('a', attrs={'class': re.compile("^script-list-item")})
                    if not script_links:
                        break
                    links = dict()
                    for link in soup.findAll('a', attrs={'class': re.compile("^script-list-item")}):
                        links[link.text] = link.get('href')[len(php_query_string):]
                    self.title_to_href.update(links)

                    print(page_num)
                    page_num += 1

        except:
            self.infoBox.setText(
                "Couldn't download data from springfieldspringfield website.", 
                "error"
            )
        return(self.title_to_href)


    # Create the final output with the script
    def sendData(self):
        """Send data from website springfieldspringfield"""

        #link_title = process.extractBests(self.selectedTitles, testdict, limit=1)
        # Clear created Inputs.
        self.clearCreatedInputs()

        link_end = self.path_storage[self.selectedTitles[0]]

        self.controlArea.setDisabled(True)
        try:
            page_url = "https://www.springfieldspringfield.co.uk/movie_script.php?movie=" + link_end
            page = urllib.request.urlopen(page_url)
            soup = BeautifulSoup(page, 'html.parser')
            script = soup.find("div", {"class":"movie_script"})
            new_input = Input(script.text)
            self.createdInputs.append(new_input)
            self.segmentation = self.createdInputs[0]
            print(self.createdInputs[0])
            self.infoBox.setText(
                "Script downloaded!",
            )
        except:
            self.infoBox.setText(
                "Couldn't download data from SpringfieldSpringfield website.",
                "error"
            )
        self.controlArea.setDisabled(False)
        self.send("Movie Scripts importation", self.segmentation, self)



    def clearCreatedInputs(self):
        """Delete all Input objects that have been created."""
        del self.createdInputs[:]

	# The following method needs to be copied verbatim in
	# every Textable widget that sends a segmentation...
    def setCaption(self, title):
    	if 'captionTitle' in dir(self):
    		changed = title != self.captionTitle
    		super().setCaption(title)
    		if changed:
    			self.SendButton.settingsChanged()
    	else:
    		super().setCaption(title)



if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication
    myApplication = QApplication(sys.argv)
    myWidget = MovieScripts()
    myWidget.show()
    myApplication.exec_()
    myWidget.saveSettings()
