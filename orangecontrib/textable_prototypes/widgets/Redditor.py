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

from Orange.widgets.settings import Setting
from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar
)


class Redditor(OWTextableBaseWidget):
    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Redditor"
    description = "Scrap on Reddit"
    priority = 20

    outputs = [("Operation result", Segmentation)]
    
    mode = Setting("Subreddit")
    subreddit = Setting(u'')
    URL = Setting(u'')

    want_main_area = False

    def __init__(self):
        super().__init__()

        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.fct,
            infoBoxAttribute="infoBox",
        )

        # Basic URL box
        basicBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Source',
            orientation='vertical',
            addSpace=False,
        )

        gui.comboBox(
            widget=basicBox,
            master=self,
            value='mode',
            items=["Subreddit", "URL"],
            sendSelectedValue=True,
            orientation='horizontal',
            label=u'Mode:',
            callback=self.fct,
            tooltip=(
                u"Select URL's encoding."
            ),
        )

        gui.lineEdit(
            widget=basicBox,
            master=self,
            value='URL',
            orientation='horizontal',
            label=u'URL:',
            labelWidth=101,
            callback=self.fct,
            tooltip=(
                u"The URL whose content will be imported."
            ),
        )

        gui.lineEdit(
            widget=basicBox,
            master=self,
            value='subreddit',
            orientation='horizontal',
            label=u'reddit.com/r/...:',
            labelWidth=101,
            callback=self.fct,
            tooltip=(
                u"The URL whose content will be imported."
            ),
        )

        self.sendButton.draw()
        self.infoBox.draw()

        gui.rubber(self.controlArea)
        self.adjustSizeWithTimer()

    def fct(self):
        pass


if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication
    myApplication = QApplication(sys.argv)
    myWidget = Redditor()
    myWidget.show()
    myApplication.exec_()
    myWidget.saveSettings()
