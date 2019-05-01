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
from urllib import request, parse
from bs4 import BeautifulSoup
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process



from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar,
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
        self.titleLabels = list()
        self.selectedTitles = list()
        # selections box attributs
        self.myTitles = list()
        self.mytitleLabels = list()
        # stock all the inputs (scripts) in a list
        self.createdInputs = list()
        self.path_storage = list()
        

        # Next two instructions are helpers from TextableUtils. Corresponding
        # interface elements are declared here and actually drawn below (at
        # their position in the UI)...
        self.infoBox = InfoBox(widget=self.controlArea)
        #self.sendButton = SendButton(
        #   widget=self.controlArea,
        #    master=self,
        #    callback=self.sendData,
        #    infoBoxAttribute="infoBox",
        #)
		

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

        # Allows to choose the wanted results numberp (10 by 10)
        queryNbr = gui.comboBox(
            widget=queryBox,
            master=self,
            value="nbr_results",
            items=[
                "5",
                "10",
                "20",
                "30",
                "40",
                "50",
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Number of results: ",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
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

        # select button
        # Uses "select" function
        self.selectButton = gui.button(
            widget=boxbutton,
            master=self,
            label="Select",
            callback=self.sendData,
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

        gui.rubber(self.controlArea)

    #----------------------------------------------------------------------

        # Draw Info box and Send button
        # self.sendButton.draw()
        # self.searchButton.setDefault(True)
        self.infoBox.draw()

        # Send data if autoSend.
        # self.sendButton.sendIf()



    title_to_href = dict()

    def searchFunction(self, title_to_href):
        #Search from the springfieldspringfield.co.uk

        result_list = dict()
        query_string = self.newQuery
        testdict = MovieScripts.get_all_titles(title_to_href)
        # Reset and clear the visible widget list
        del self.titleLabels[:]
		
        if query_string != "":
            searchResults = process.extractBests(query_string, testdict, limit=5, score_cutoff=70)
            for key,score,val in searchResults:
                self.titleLabels.append(val)
                self.path_storage.append(key)
		
            self.titleLabels = self.titleLabels
            self.clearButton.setDisabled(False)
            self.controlArea.setDisabled(False)
            self.infoBox.setText("Search complete")

        else:
            self.infoBox.setText("You didn't search anything", "warning")

        progressBar.finish()

    def clearResults(self):
        """Clear the results list"""
        del self.titleLabels[:]
        self.titleLabels = self.titleLabels
        self.clearButton.setDisabled(True)
    
	# Get all movie titles from www.springfieldspringfield.co.uk
    def get_all_titles(title_to_href):
        title_to_href = dict()
        php_query_string = '/movie_script.php?movie='
        http_query_string = 'https://www.springfieldspringfield.co.uk/movie_scripts.php?order='

        for lettre in ['0']:#, 'A']:, 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                   #'N', 'O', 'P', 'K', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            page_num = 1

            # Initialize progress bar.
            progressBar = ProgressBar(
                self,
                iterations=page_num,
            )

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
                title_to_href.update(links)

                print(page_num)
                page_num += 1

                progressBar.advance()

        # print(title_to_href['99 Homes (2014)'])
        return(title_to_href)
        print(title_to_href)

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
            new_input = script.text
            self.createdInputs.append(new_input)
            self.segmentation = self.createdInputs[0]
            print(self.createdInputs[0])
            del self.path_storage[:]
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
