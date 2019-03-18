"""
Class Redditor
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
__author__ = "Nahuel Degonda, Olivia Edelman, Loris Rimaz"
__maintainer__ = "Nahuel Degonda, Olivia Edelman, Loris Rimaz"
__email__ = "nahuel.degonda@unil.ch, olivia.edelman@unil.ch, loris.rimaz@unil.ch"


#from Orange.widgets import widget, gui
import praw

from Orange.widgets import widget, gui, settings

from LTTL.Segmentation import Segmentation
from LTTL.Input import Input
import LTTL.Segmenter as Segmenter

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar
)


class Redditor(OWTextableBaseWidget):
    
    def __init__(self):
        super().__init__()

    pass