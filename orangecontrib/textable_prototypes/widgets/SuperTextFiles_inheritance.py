"""
Class SuperTextFiles
Copyright 2020 University of Lausanne
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
__author__ = "Loïc Aubrays, Fàbio Torres Cabral"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

import copy

from chardet.universaldetector import UniversalDetector

from LTTL.Segmentation import Segmentation
from LTTL.Input import Input
import LTTL.Segmenter as Segmenter

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, ProgressBar,
    JSONMessage, InfoBox, SendButton, AdvancedSettings,
    addSeparatorAfterDefaultEncodings, addAutoDetectEncoding,
    getPredefinedEncodings, normalizeCarriageReturns, pluralize
)
from _textable.widgets.OWTextableTextFiles import OWTextableTextFiles

from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview


class SuperTextFiles(OWTextableTextFiles):
    """Textable widget to import PDF files and if necessary make an Optical
    Character Recognition (OCR) based on OWTextableTextFiles."""

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Super Text Files"
    description = "Import data from raw text and PDF files"
    icon = "icons/supertextfiles.svg"
    priority = 25 # TODO

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = [
        ('Message', JSONMessage, "inputMessage", widget.Single)
    ]
    outputs = [('Text data', Segmentation)]


    #----------------------------------------------------------------------
    # Layout parameters...
    
    want_main_area = False

    #----------------------------------------------------------------------
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    # controlArea is a QVBoxLayout

    def clearLayout(layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    clearLayout(child.layout())

    def __init__(self, *args, **kwargs):
        """Widget creator."""
        super().__init__(*args, **kwargs)

        # Other attributes...
        self.pdfPassword = u''

        # GUI elements of TextFiles
        advancedWidgets = self.advancedSettings.advancedWidgets
        fileBox = advancedWidgets[0].children()[3]
        addFileBox = fileBox.children()[1]

        gui.separator(widget=addFileBox, width=3)
        # Field for PDF password
        password_field = gui.lineEdit(
            widget=addFileBox,
            master=self,
            value='pdfPassword',
            orientation='horizontal',
            label=u'PDF password:',
            labelWidth=101,
            callback=self.updateGUI,
            tooltip=(
                u"This field lets you specify a password\n"
                u"if the PDF file needs one."
            ),
        )


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    appl = QApplication(sys.argv)
    ow = SuperTextFiles()
    ow.show()
    appl.exec_()
    ow.saveSettings()
