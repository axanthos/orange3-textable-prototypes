"""
Class Scratodon
Copyright 2024 University of Lausanne
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
__author__ = "N/D"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

# Standard imports...
from mastodon import Mastodon

from Orange.widgets import widget, gui
from Orange.widgets.settings import Setting

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar
)

from LTTL.Segmentation import Segmentation
import LTTL.Segmenter as Segmenter
from LTTL.Segment import Segment
from LTTL.Input import Input

from datetime import datetime

import re

class Scratodon(OWTextableBaseWidget):
    """An Orange widget to scrape Mastodon"""

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Scratodon"
    description = "Scrape Mastodon Data"
    # icon = "icons/Scrat.png"
    priority = 14

    #----------------------------------------------------------------------
    # Channel definitions...

    # inputs = []
    outputs = [("Segmentation", Segmentation)]

    #----------------------------------------------------------------------
    # GUI layout parameters...

    want_main_area = False
    resizing_enabled = True

    #----------------------------------------------------------------------
    # DEFAULT - Query settings...

    mode = Setting("Federated")
    Federated = Setting(u'')
    Instance = Setting(u'')
    User = Setting(u'')

    # DEFAULT - Filters settings...

    amount = Setting(S)

    # Include settings...

    includeImage = Setting(False)

    # resultBox settings...

    labelsPanier = Setting(list())

    # Data settings...

    queryList = Setting(list())
    annotList = Setting(list())

    #----------------------------------------------------------------------

    def __init__(self):
        """Init of the module: UI and variables definition"""
        super().__init__()

        # queryBox indexes
        self.indicesPanier = list()

        #----------------------------------------------------------------------
        # User interface...

        self.infoBox = InfoBox(
            widget=self.controlArea,
        )

        #-------------------------#
        #    Main widget boxes    #
        #-------------------------#

        

        #-------------------#
        #    Send button    #
        #-------------------#

    

        #--------------------------#
        #  API input box elements  # 
        #--------------------------#



        #--------------------------------#
        #   MODE SELECTOR box elements   #
        #--------------------------------#



        #----------------------------------#
        #   TARGET SELECTOR box elements   #
        #----------------------------------#



        #--------------------------------------------#
        #   QUERY ATTRIBUTES SELECTOR box elements   #
        #--------------------------------------------#



        #--------------------------------------#
        #   ADDITION THRESHROLD box elements   #
        #--------------------------------------#

        

        #------------------------#
        #   End of definitions   #
        #------------------------#

        gui.separator(widget=self.controlArea, height=3) # Spacer
        gui.rubber(self.controlArea)

        # Info box...
        
        self.sendButton.draw()
        self.infoBox.draw()

        self.mode_changed()
        self.sendButton.settingsChanged()

        # Send data if autoSend...
        self.sendButton.sendIf()

    def mode_changed(self):
        self.sendButton.settingsChanged()
        """Allows to update the interface depeding on query mode"""

        return

 
    def get_content(self,):
        """Fetches the content on MASTODON based on the filters selected by the user
        
        
        Parameters:
        
        """
        

    def confirm_settings(self):
        """Sets all the values for filters entered by user"""
        

    def create_post_segments(self, post, includeImage, includeComments):
        """ Creation of segments from posts"""


    def onDeleteWidget(self):
        """Free memory when widget is deleted (overriden method)"""
        self.clearCreatedInputs()
 

# The following code lets you execute the code (to view the
# resulting interface)...
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    my_app = QApplication(list(sys.argv))
    my_widget = Scratodon()
    my_widget.show()
    my_widget.raise_()
    my_app.exec_()
    my_widget.saveSettings()
