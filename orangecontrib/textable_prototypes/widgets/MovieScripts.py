"""
Class Movie Scripts
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
        self.sendData =

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
            label=u"Film title: ",
            labelWidth=120,
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

        # Reasearch button
        # Uses "searchFunction" attribut
        self.searchButton = gui.button(
            widget=queryBox,
            master=self,
            label="Search",
            callback=self.searchFunction,
            tooltip="Search for a script",
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
        self.sendButton.draw()
        self.searchButton.setDefault(True)
        self.infoBox.draw()


        # Send data if autoSend.
        self.sendButton.sendIf()


    # Search function which contacts the IMSBD RSS feeds
    def searchFunction(self):
        """Search from website IMSDB.com"""
        #Instead of searching for a title from the website, have a cache of all title which widget will access
        quote_page = 'https://www.imsdb.com/all%20scripts/'
        page = urllib.urlopen(quote_page)
        soup = BeautifulSoup(page, 'html.parser')
        for link in soup.find_all('a'):
            MovieScripts.sendButton.sendData(link.get('href'))


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

    ######################################################

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

print(title_to_href)



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

export_scripts(title_to_href)

#This is what will get the actual script of a single movie 
page_url = "https://www.springfieldspringfield.co.uk/movie_script.php?movie=five-minutes-of-heaven"
page = urllib.request.urlopen(page_url)
soup = BeautifulSoup(page, 'html.parser')
script = soup.find("div", {"class":"movie_script"})
print (script.text)

##################################################


if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication
    myApplication = QApplication(sys.argv)
    myWidget = MovieScripts()
    myWidget.show()
    myApplication.exec_()
    myWidget.saveSettings()
