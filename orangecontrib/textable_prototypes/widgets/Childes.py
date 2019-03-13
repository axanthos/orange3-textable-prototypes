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

__version__ = u"0.0.1"
__author__ = "Aris Xanthos"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"


import os
import pickle

import requests
from bs4 import BeautifulSoup

from Orange.widgets import widget, gui, settings

from LTTL.Segmentation import Segmentation
from LTTL.Input import Input
import LTTL.Segmenter as Segmenter

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar
)


class Childes(OWTextableBaseWidget):
    """Textable widget for importing data in XML format from the CHILDES
    database (https://childes.talkbank.org/data-xml/).
    """

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "CHILDES"
    description = "Import XML data from the CHILDES database"
    icon = "icons/CHILDES.svg"
    priority = 12

    #----------------------------------------------------------------------
    # Channel definitions (NB: no input in this case)...

    inputs = []
    outputs = [("XML data", Segmentation)]

    #----------------------------------------------------------------------
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    autoSend = settings.Setting(False)
    displayedFolder = settings.Setting(None)
    selectedItem = settings.Setting(None)

    #----------------------------------------------------------------------
    # Other class variables...
    
    base_url = "https://childes.talkbank.org/data-xml/"

    want_main_area = False

    def __init__(self):
        """Widget creator."""

        super().__init__()

        # Other (non-setting) attributes...
        self.segmentation = None
        self.displayedFolderLabels = ["Bates", "Bernstein", "Bliss"]

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

        # Browse database box
        browseBox = gui.widgetBox(
            widget=self.controlArea,
            box="Browse database",
            orientation="vertical",
            addSpace=False,
        )

        upwardNavBox = gui.widgetBox(
            widget=browseBox,
            box=False,
            orientation="horizontal",
        )
        gui.button(
            widget=upwardNavBox,
            master=self,
            label="Home",
            callback=self.homeRefreshPressed,
            tooltip="Return to database root.",
            # tooltip="Connect to CHILDES website and refresh corpus list.",
        )
        gui.button(
            widget=upwardNavBox,
            master=self,
            label="Back",
            callback=self.backPressed,
            tooltip="View parent folder.",
        )

        gui.separator(widget=browseBox, height=3)

        self.displayedFolderListbox = gui.listBox(
            widget=browseBox,
            master=self,
            value="selectedItem",    # setting (list)
            labels="displayedFolderLabels",
            callback=self.corpusSelected,
            tooltip="Select a folder to open or a corpus to import.",
        )
        self.displayedFolderListbox.setMinimumHeight(150)
        self.displayedFolderListbox.setSelectionMode(1)
        self.displayedFolderLabels = self.displayedFolderLabels

        downwardNavBox = gui.widgetBox(
            widget=browseBox,
            box=False,
            orientation="horizontal",
        )
        gui.button(
            widget=downwardNavBox,
            master=self,
            label="Open",
            callback=self.openPressed,
            tooltip="View selected folder's contents.",
        )
        gui.button(
            widget=downwardNavBox,
            master=self,
            label="Import",
            callback=self.importPressed,
            tooltip="View selected item's contents.",
        )

        gui.separator(widget=browseBox, height=3)

        gui.rubber(self.controlArea)

        # Now Info box and Send button must be drawn...
        self.sendButton.draw()
        self.infoBox.draw()

        # This initialization step needs to be done after infoBox has been
        # drawn (because getTitleSeg may need to display an error message).
        #self.getTitleSeg()

        # Send data if autoSend.
        self.sendButton.sendIf()

        self.setMinimumWidth(350)
        self.adjustSizeWithTimer()

    def sendData(self):
        """Compute result of widget processing and send to output"""
        pass

    def homeRefreshPressed(self):
        """Refresh title segmentation from website"""
        pass

    def backPressed(self):
        """Refresh title segmentation from website"""
        pass

    def corpusSelected(self):
        """Refresh title segmentation from website"""
        pass

    def openPressed(self):
        """Refresh title segmentation from website"""
        pass

    def importPressed(self):
        """Refresh title segmentation from website"""
        pass

    # The following method need to be copied (without any change) in
    # every Textable widget...

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
    myWidget = Childes()
    myWidget.show()
    myApplication.exec_()
    myWidget.saveSettings()
