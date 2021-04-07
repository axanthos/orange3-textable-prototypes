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

__version__ = u"0.0.1"
__author__ = "Caroline Rorhbach, Maryam Zoee, Victor Vermot"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

from Orange.widgets import widget, gui, settings

from Orange.widgets.utils.widgetpreview import WidgetPreview
from LTTL.Segmentation import Segmentation
import LTTL.Segmenter as Segmenter
from LTTL.Input import Input

import imdb

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar,
)

class MovieReviews(OWTextableBaseWidget):
    """An orange widget to get movie reviews from Imdb"""

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Movie Reviews"
    description = "Get movie reviews from imdb"
    icon = ""
    priority = 15

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = []
    outputs = [("Segmentation", Segmentation)]

    #----------------------------------------------------------------------
    # Handles the futur versions settings

    settingsHandler = VersionedSettingsHandler(
    version=__version__.rsplit(".", 1)[0]
    )

    # Settings
    autoSend = settings.Setting(True)
    myBasket = settings.Setting([])

    #----------------------------------------------------------------------
    # GUI layout parameters...

    want_main_area = False

    def __init__(self):
        super().__init__()

        # Search filters attributs
        self.newQuery = ''
        self.type_results = 'Title'
        self.filter_results = 'Popularity'
        self.nbr_results = '10'
        # Results box attributs
        self.titleLabels = list()
        self.selectedTitles = list()
        # selections box attributs
        self.myTitles = list()
        self.mytitleLabels = list()
        # stock all the inputs (songs) in a list
        self.createdInputs = list()

        # Mandatory declaration of the info box and the send button
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.placeholder,
            infoBoxAttribute='infoBox',
            sendIfPreCallback=None,
        )

        #----------------------------------------------------------------------
        # User interface...

        # Creation of the different working areas
        queryBox = gui.widgetBox(
            widget=self.controlArea,
            box="Search movies",
            orientation="vertical",
        )

        filterBox = gui.widgetBox(
            widget=self.controlArea,
            box="Filters",
            orientation="vertical",
        )

        searchButtonBox = gui.widgetBox(
            widget=self.controlArea,
            orientation="vertical",
        )

        resultBox = gui.widgetBox(
            widget=self.controlArea,
            box="Search results",
            orientation="vertical",
        )



        # Allows to enter specific text to the research
        gui.lineEdit(
            widget=queryBox,
            master=self,
            value='newQuery',
            orientation='horizontal',
            label=u"Search: ",
            labelWidth=120,
            tooltip=("Enter a string"),
        )

        # Allows to choose the wanted results numberp (10 by 10)
        queryType = gui.comboBox(
            widget=queryBox,
            master=self,
            value="type_results",
            items=[
                "Title",
                "Actor",
                "Genre",
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Search Type: ",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )

        queryNbr = gui.comboBox(
            widget=filterBox,
            master=self,
            value="filter_results",
            items=[
                "Popularity",
                "Alphabetical",
                "Random",
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Search by: ",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )

        # Allows to choose the wanted results numberp (10 by 10)
        queryNbr = gui.comboBox(
            widget=filterBox,
            master=self,
            value="nbr_results",
            items=[
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
        self.searchButton = gui.button(
            widget=searchButtonBox,
            master=self,
            label="Search",
            callback=None,
            tooltip="Connect to imdbpy and make a research",
        )

        self.titleListbox = gui.listBox(
            widget=resultBox,
            master=self,
            value="selectedTitles",    # setting (list)
            labels="titleLabels",      # setting (list)
            callback=None,
            tooltip="The list of titles whose content will be imported",
        )
        self.titleListbox.setMinimumHeight(150)
        self.titleListbox.setSelectionMode(3)

        boxbutton = gui.widgetBox(
            widget=resultBox,
            box=False,
            orientation='horizontal',
        )
        # Add movies button
        self.addButton = gui.button(
            widget=boxbutton,
            master=self,
            label=u'Add to corpus',
            callback=None,
            tooltip=(
                u"Move the selected song downward in your corpus."
            ),
        )
        self.addButton.setDisabled(True)

        # Clear button
        self.clearButton = gui.button(
            widget=boxbutton,
            master=self,
            label="Clear results",
            callback=None,
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
            callback=None,
            tooltip="The list of titles whose content will be imported",
        )
        self.mytitleListbox.setMinimumHeight(150)
        self.mytitleListbox.setSelectionMode(3)

        boxbutton2 = gui.widgetBox(
            widget=mytitleBox,
            box=False,
            orientation='horizontal',
        )
        # Remove movie button
        self.removeButton = gui.button(
            widget=boxbutton2,
            master=self,
            label=u'Remove from corpus',
            callback=None,
            tooltip=(
                u"Remove the selected song from your corpus."
            ),
        )
        self.removeButton.setDisabled(True)

        # Delete all confirmed movies button
        self.clearmyBasket = gui.button(
            widget=boxbutton2,
            master=self,
            label=u'Clear corpus',
            callback=None,
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

        # Send data if autoSend.
        self.sendButton.sendIf()

    def placeholder(self):
        return

if __name__ == "__main__":
    WidgetPreview(MovieReviews).run()