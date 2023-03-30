"""
Class Poetica
Copyright 2022-2023 University of Lausanne
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

__version__ = u"0.0.3"
__author__ = "Olivia Verbrugge, Sinem Kilic, Leonie Nussbaum et Laure Margot"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

# Import the necessary packages...
from Orange.widgets import widget, gui, utils
from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar,
)

# Informations...
__version__ = "0.01"


# Create the poetica class...
class poetica(widget.OWWidget):
    """
    This is the poetica class
    """

    # Widget's metadata...
    name = "Poetica"
    description = "Poetica's poems importation"
#    icon = ""
    priority = 20

    # Channel definitions...
    inputs = []
    outputs = [("Poetica's poems importation", str)]

    # Gui layout parameters...
    want_main_area = False
    resizing_enabled = False

    # Define the init function...
    def __init__(self):
        """
        This is the init function
        """
        # ATTRIBUTS
        # searchFunction
        self.searchResults = None
        self.inputSeg = None
        # newQuery = attribut box lineEdit (search something)
        self.authorQuery = ''
        self.dateQuery = '1910-1920'
        self.queryTopic = ''
        self.nbr_results = 200

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





if __name__ == "__main__" :
#    ...
