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
__maintainer__ = "Bony Maxime, Cappelle Simon, Pitteloud Robin"
__email__ = "maxime.bony@unil.ch, simon.cappelle@unil.ch, robin.pitteloud@unil.ch"

from Orange.widgets import widget, gui, settings

from LTTL.Segmentation import Segmentation
from LTTL.Input import Input
import LTTL.Segmenter as Segmenter

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton
)

# Constants...
# Champs lexicaux #fichier texte ?
List1={"Amour":["aimer","coeur","j'aime","embrasser"]}
List2={"Colere":["rage","colere","sourciles froncés"]}
List3={"Joie":["vin","biere","wisky","TICT"]}

DEFAULTLIST=[List1,List2,List3]

class LexicalHunter(OWTextableBaseWidget):
    """Textable widget for identifying lexical fields in segments
    """

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Lexical Hunter"
    description = "Identify words contained in lists (lexical fields)"
    icon = "icons/lexical_hunter.svg"
    priority = 10

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = [("Word segmentation", Segmentation, "inputData")]
    outputs = [("Segmentation with annotations", Segmentation)]

    #----------------------------------------------------------------------
    # Layout parameters...

    want_main_area = False

    #----------------------------------------------------------------------
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    lexicalDict = settings.Setting({})
    selectedTitles = settings.Setting([])
    titleLabels = settings.Setting([])
    autoSend = settings.Setting(False)

    def __init__(self):
        """Widget creator."""

        super().__init__()

        # Other attributes...
        self.inputSeg = None
        self.outputSeg = None
        self.defaultDict = {}

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

        # User interface...

        # Options box...
        titleLabelsList = gui.widgetBox(
            widget=self.controlArea,
            box="Click to select the lexical lists",
            orientation="vertical",
        )
        # List of Lexical list that the user can select
        self.titleListbox = gui.listBox(
            widget=titleLabelsList,
            master=self,
            ########## selectedTitles retourne un tabeau de int suivant la position dans selectedTitles des listes selectionnees ########
            value="selectedTitles",    # setting (list)
            labels="titleLabels",   # setting (list)
            callback=self.sendButton.settingsChanged,
            tooltip="The list of lexical list that you want to use for annotation",
        )
        self.titleListbox.setMinimumHeight(150)
        self.titleListbox.setSelectionMode(2)

        # Edit a list ...
        self.OptionList = gui.button(
            widget=titleLabelsList,
            master=self,
            label="Edit lists",
            callback=self.editList,
            width=100,
        )

        ###### START NOTA BENNE ######

        # Utiliser self.labelControl.setText(str(Ma_variable)) pour afficher une variable dans le widget
        self.labelControl = gui.widgetLabel(self.controlArea, "[J'affiche des variables pour les controler]")

        #A definire plus tard
        #gui.separator(widget=optionsBox, height=3)

        ##### END NOTA BENNE ######

        gui.rubber(self.controlArea)

        # Now Info box and Send button must be drawn...
        self.sendButton.draw()
        self.infoBox.draw()

        self.creatDefaultDict() # Constants...
        self.setTitleList()
        # Send data if autoSend.
        self.sendButton.sendIf()

    def creatDefaultDict(self):
        """ Creat the default dictionnaries from a list of default lexical list
        the key must be the title of default lexical liste
        the value is the content of the default lexical liste"""

        for lexiclist in DEFAULTLIST :
            self.defaultDict.update(lexiclist)

    def setTitleList(self):
        """Creat a list with each key of the default dictionnaries to display them on the list box
        Be carfull, the order really metter for the selectedTitles variable !"""

        self.titleLabels = self.defaultDict.keys()

    def editList():
        """ Edit the list of lexical word. Nothing to do now"""

    def inputData(self, newInput):
        """Process incoming data."""
        ######### traiter inputSeg comme le segement d entree ##########
        self.inputSeg = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()
        ######## pour tester ! ########
        #self.InputSeg = "test tes2 amour et biere"

    def sendData(self):
        """Compute result of widget processing and send to output"""
        #self.labelControl.setText("selectedTitles = " + str(self.selectedTitles))

        # A input is needed
        if self.inputSeg == None:
            self.infoBox.setText(
                "A segmentation input is needed",
                "warning"
            )
            self.send("Segmentation with annotations", None, self)
            return

        # Skip if no list is selected
        if self.titleLabels == None:
            self.infoBox.setText(
                "You need to define at least one lexical list",
                "error"
            )
            self.send("Segmentation with annotations", None, self)
            return

        # A list must have been selected
        if len(self.selectedTitles) == 0:
            self.infoBox.setText(
                "Please select one or more lexical lists.",
                "warning"
            )
            self.send("Segmentation with annotations", None, self)
            return

        self.huntTheLexic()

        # Set status to OK and report data size...
        message = "%i segment@p sent to output " % len(self.outputSeg)
        message = pluralize(message, len(self.outputSeg))

        # Segmentation go to outputs...
        self.send("Segmentation with annotations", self.outputSeg, self)
        self.infoBox.setText(message)
        self.sendButton.resetSettingsChangedFlag()

    ######## NOTRE FONCTION PRINCIPALE !!! #######
    def huntTheLexic(self):
        """ Je traite le segement (inputSeg) pour en retourner un output (outputSeg) de ouf """
        self.outputSeg = self.inputSeg #lourd!

    def updateGUI(self):
        """Update GUI state"""

        if len(self.titleLabels) > 0:
            self.selectedTitles = self.selectedTitles

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
    myWidget = LexicalHunter()
    myWidget.show()
    myApplication.exec_()
    myWidget.saveSettings()
