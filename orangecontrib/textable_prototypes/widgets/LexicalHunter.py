"""
Class LexicalHunter
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
__author__ = "Bony Maxime, Cappelle Simon, Pitteloud Robin"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

# Standard imports...
from Orange.widgets import widget, gui
from Orange.widgets.settings import Setting


class LexicalHunter(OWTextableBaseWidget):
    """Textable widget for identifying lexical fields in segments
    """

    #----------------------------------------------------------------------
    # Widget"s metadata...

    name = "Lexical Hunter"
    description = "Identify words contained in lists (lexical fields)"
    icon = "icons/lexical_hunter.svg"
    priority = 10

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = []
    outputs = []
    
    #----------------------------------------------------------------------
    # GUI layout parameters...

    want_main_area = False
    resizing_enabled = False

    #----------------------------------------------------------------------
    # Settings...
    
    def __init__(self):
        """Widget creator."""
        pass

            
if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication
    myApplication = QApplication(sys.argv)
    myWidget = TheatreClassique()
    myWidget.show()
    myApplication.exec_()
    myWidget.saveSettings()
