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

        # Other attributes...
        self.inputSeg = None
        self.newQuery = ''
        self.selected_choice_artists_or_songs = None
        self.results = False
        self.types = ''
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
        # Creation de la zone de recherche
        queryBox = gui.widgetBox(
            widget=self.controlArea,
            box="Query",
            orientation="vertical",
        )
        # permet de choisir une recherche entre artistes ou chansons
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
            label="search:",
            labelWidth=120,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )
        # permet de rentrer du text pour rechercher
        gui.lineEdit(
            widget=queryBox,
            master=self,
            value='newQuery',
            label="",
            labelWidth=131,
            callback=self.updateGUI,
            tooltip=("Enter a string"),
        )
        # bouton qui lance la recherche
        gui.button(
            widget=queryBox,
            master=self,
            label="Search",
            callback=self.searchFunction,
            tooltip="Connect Genius and make a research",
        )

        # Creation de la zone de resultats
        resultsBox = gui.widgetBox(
            widget=self.controlArea,
            box="Results",
            orientation="vertical",
        )
        # Creation d une liste a puces permettant le choix du resultat
        gui.checkBox(
            widget=resultsBox,
            master=self,
            value='results',
            label='',
            labelWidth=131,
            callback=self.updateGUI,
        )
        #----------------------------------------------------------------------

        gui.rubber(self.controlArea)

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
