
# import pickle
# import requests
# import urllib
# from urllib import request
# from urllib import parse
# from bs4 import BeautifulSoup

# all_titles_page = 'https://www.imsdb.com/all%20scripts/'
# page = urllib.request.urlopen(all_titles_page)
# soup = BeautifulSoup(page, 'html.parser')
# for link in soup.find_all('a'):
#     print(link.get('href'))

##############################################################

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
from urllib import request
from urllib import parse
from bs4 import BeautifulSoup
import re

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
        # stock all the inputs (songs) in a list
        self.createdInputs = list()
        self.sendData = ''
        self.newQuery = ''

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
        #  Uses "newQuery" attribut
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
        # Use "sendData" attibute
        self.searchButton = gui.button(
        	widget=queryBox,
        	master=self,
        	label='search',
        	callback=self.get_all_titles,
        	tooltip='Search for the movie',
        	)
        self.searchButton.setDisabled(False)

        # Reasearch button
        # Uses "searchFunction" attribut
        self.titleListbox = gui.listBox(
            widget=queryBox,
            master=self,
            value="selectedTitles",    # setting (list)
            labels="titleLabels",      # setting (list)
            callback=lambda: self.addButton.setDisabled(
                self.selectedTitles == list()),
            tooltip="The list of titles whose content will be imported",
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
            # callback=self.clearResults,
            tooltip="Select",
        )
        self.selectButton.setDisabled(True)

        # Clear button
        # Uses "clearResults" function
        self.clearButton = gui.button(
            widget=boxbutton,
            master=self,
            label="Clear results",
            # callback=self.clearResults,
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


    # Get all movie titles from www.springfieldspringfield.co.uk
    def get_all_titles(self):
        php_query_string = '/movie_script.php?movie='
        http_query_string = 'https://www.springfieldspringfield.co.uk/movie_scripts.php?order='

        title_to_href = dict()


        for lettre in ['0']:#, 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
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
                title_to_href.update(links)

                print(page_num)
                page_num += 1

        # print(title_to_href)

        '''ne fonctionne pas --> à voir pq...'''
        self.titleLabels.append(title_to_href) 


    # Export file with all titles in a list
    def export_scripts(title_to_href):
        try:
            name_file = input('Entrez le nom du fichier à exporter: ')
            exported_file = open(name_file, 'w', encoding='utf8')
            exported_file.write(str(title_to_href))
            exported_file.close()

            '{:*^20}'.format('title_to_href')

        except IOError:
            print('Impossible de lire le fichier')

        return

    # export_scripts(title_to_href)


    # Creat the final output with the script
    def sendData(self, title_to_href):
        """Send data from website springfieldspringfield"""

        #This is what will get the actual script of a single movie
        movie_names_row = input('\033[31m Entrez le nom du film et l\'année entre parenthèses, ex : 99 Homes (2014) : \033[0m')
        #The first attribute of extract will be user's input, second is the list of all movie scripts, third is number of results determined by user    
        movie_names = process.extractBests(movie_names_row, title_to_href.keys(), limit=1, score_cutoff=70)
        titles = [movie_name[0] for movie_name in movie_names]
        title = titles[0]

        print(title)
        if input('\033[31m Entrez "yes" pour continuer : \033[0m') == 'yes':

            if title in title_to_href:
                print(title_to_href[title])
            else:
                print('Aucun résultat')

            page_url = "https://www.springfieldspringfield.co.uk/movie_script.php?movie=" + title_to_href[title]
            page = urllib.request.urlopen(page_url)
            soup = BeautifulSoup(page, 'html.parser')
            script = soup.find("div", {"class":"movie_script"})
            print (script.text)
        else:
            pass

        self.searchButton.setDisabled(False)

    # def searchFunction(self):
    #     result_list = {"1": "a", "1": "a", "1": "a", "1": "a",}
    #     query_string = self.newQuery

    #     if query_string != "":
    #         page = 1
    #         page_max = int(self.nbr_results)/10
    #         result_id = 0
    #         result_artist = []

    #         self.controlArea.setDisabled(True)

    #         # Initialize progress bar.
    #         progressBar = ProgressBar(
    #             self,
    #             iterations=page_max
    #         )

    #         # Each result is stored in a dictionnary with its title,
    #         # artist's name, artist's ID and URL path
    #         for result in body:
    #             result_id += 1
    #             title = result["result"]["title"]
    #             artist = result["result"]["primary_artist"]["name"]
    #             artist_id = result["result"]["primary_artist"]["id"]
    #             path = result["result"]["path"]
    #             result_list[result_id] = {'artist': artist,
    #                                           'artist_id':artist_id,
    #                                           'path':path, 'title':title}
    #             page += 1

    #             # 1 tick on the progress bar of the widget
    #             progressBar.advance()
    #         # Stored the results list in the "result_list" variable
    #         self.searchResults = result_list

    #         # Reset and clear the visible widget list
    #         del self.titleLabels[:]

    #         # Update the results list with the search results
    #         # in order to display them
    #         for idx in self.searchResults:
    #             result_string = self.searchResults[idx]["title"] + " - " + \
    #                             self.searchResults[idx]["artist"]
    #             self.titleLabels.append(result_string)

    #         self.titleLabels = self.titleLabels
    #         self.clearButton.setDisabled(False)
    #         self.addButton.setDisabled(self.selectedTitles == list())


    #         # Clear progress bar.
    #         progressBar.finish()
    #         self.controlArea.setDisabled(False)

    #     else:
    #         self.infoBox.setText("You didn't search anything", "warning")


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