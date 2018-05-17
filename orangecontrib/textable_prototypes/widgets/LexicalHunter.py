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

from PyQt4.QtGui import QPlainTextEdit, QFileDialog, QMessageBox

import PyQt4.QtCore as QtCore

import os
import codecs
import re
from os import listdir
from os.path import isfile, join
import platform

from unicodedata import normalize

# Global variables with exemple list
defaultDict = {
    "Exemple-FR" : ["Je","suis","une","liste","de","mots"],
    "Example-EN" : ["I","am","a","word","list"],
    "Beispiel-DE" : ["Ich","bin","ein","Wort","Liste"],
    "Esempio-IT" : ["Sono","una","lista","di","parole"]
}

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

    savedDict = settings.Setting({})
    selectedFields = settings.Setting([])
    autoSend = settings.Setting(False)
    labelName = settings.Setting("Topic")

    def __init__(self):
        """Widget creator."""

        super().__init__()

        # Other attributes...
        self.inputSeg = None
        self.outputSeg = None
        self.titleLabels = []
        # Put the saved dictionarys, if exist, in the global variable defaultDict
        if self.savedDict :
            defaultDict.clear()
            defaultDict.update(self.savedDict)

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
            value="selectedFields",    # setting (list)
            labels="titleLabels",   # setting (list)
            callback=self.sendButton.settingsChanged,
            tooltip="The list of lexical list that you want\
                to use for annotation",
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

        self.titleEdit = gui.lineEdit(
            widget=self.controlArea,
            master=self,
            value="labelName",
            label="Annotation key : ",
            orientation="horizontal",
        )

        gui.rubber(self.controlArea)

        # Now Info box and Send button must be drawn...
        self.sendButton.draw()
        self.infoBox.draw()

        # Show the lists in the box
        self.setTitleList()
        # Send data if autoSend.
        self.sendButton.sendIf()

    def getDefaultLists(self):
        """ DEPRECATED
        Gets default lexical lists stored in txt files """
        # Seting the path of the files...
        __location__ = os.path.realpath(
            os.path.join(
                os.getcwd(),
                os.path.dirname(__file__)
            )
        )
        if platform.system() == "Windows":
            __location__ += r"\lexicalfields"
        else:
            __location__ += r"/lexicalfields"

        # Initiations
        self.myContent = {}

        # For each txt file in the directory...
        for file in os.listdir(__location__):
            if file.endswith(".txt"):
                # Gets txt file name and substracts .txt extension
                fileName = os.path.join(__location__, file);

                if platform.system() == "Windows":
                    listLexicName = fileName.split('\\')

                else:
                    listLexicName = fileName.split('/')

                lexicName = listLexicName[-1]
                lexicName = re.sub('\.txt$', '', lexicName)


                # Trying to open the files and store their content in
                # a dictionnary then store all of theses in a list
                try:
                    fileHandle = codecs.open(fileName, encoding='utf-8')
                    fileContent = fileHandle.read()
                    fileHandle.close()
                    defaultDict[lexicName] = fileContent.split('\n')
                except IOError:
                    QMessageBox.warning(
                        None,
                        'Textable',
                        "Couldn't open file.",
                        QMessageBox.Ok
                    )
                    return


    def setTitleList(self):
        """Creates a list with each key of the default dictionnaries to display
        them on the list box Be careful, the order really matter for the
        selectedFields variable !"""
        self.titleLabels = defaultDict.keys()
        # save the dictionnary used to display the list as a setting
        self.savedDict.clear()
        self.savedDict.update(defaultDict)

    def editList(self):
        """ Edit the list of lexical word. Nothing to do now"""
        self.widgetEdit = WidgetEditList(self)
        self.widgetEdit.show()
        self.setTitleList()

    def hideEditWidget(self):
        self.widgetEdit.hide()

    def inputData(self, newInput):
        """Process incoming data."""
        ######### traiter inputSeg comme le segement d entree ##########
        self.inputSeg = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def sendData(self):
        """Compute result of widget processing and send to output"""

        # An input is needed
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
        if len(self.selectedFields) == 0:
            self.infoBox.setText(
                "Please select one or more lexical lists.",
                "warning"
            )
            self.send("Segmentation with annotations", None, self)
            return

        # A annotation key must have been defined
        if self.labelName == "":
            self.infoBox.setText(
                "A annoatation key is needed.",
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
        """
            main I/O function, filters the inputSeg with the selected
            lexical fields and outputs a copy of the input this Segmentation
            with segments labelised according to the topic they belong in
        """

        # initiations...
        out = list()
        selectedListsNames = list()

        # first we select the topics according to the ones the user chose
        if self.titleLabels:
            selectedListsNames = [list(self.titleLabels)[idx] for idx
                                    in self.selectedFields]

        # we can then associate the topics with their respective lists
        selectedLists = {key:value for key, value in defaultDict.items()
                        if key in selectedListsNames}

        # if we have an input, we can select the segments of the input and
        # label them according to the lists they are found in
        if self.inputSeg is not None:
            for filter_list in selectedLists:
                work_list = [i for i in selectedLists[filter_list] if i]
                if work_list:
                    out.append(
                        Segmenter.select(
                            self.inputSeg,
                            self.listToRegex(work_list),
                            label=filter_list,
                        )[0]
                    )

        # lastly we define the output as a segmentation that is a copy of
        # the input, with the segments that we found labeled accordingly
        self.outputSeg = Segmenter.concatenate(
            [Segmenter.bypass(self.inputSeg, label="__None__")] + out,
            merge_duplicates=True,
            label=self.captionTitle,
            import_labels_as=self.labelName,
        )

    def updateGUI(self):
        """Update GUI state"""

        if len(self.titleLabels) > 0:
            self.selectedFields = self.selectedFields

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

    #An eventually useful function, set aside for the moment
    def listToRegex(self,list):
        """
        Takes a list and turns it into a
        regex that matches any elements within it
        """

        regexString = "^("+"|".join(list)+")$"
        exitRegex = re.compile(regexString, re.IGNORECASE)

        return exitRegex


class WidgetEditList(OWTextableBaseWidget):
    """Textable widget for modifing the lexical content of the list
    """

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Edit Lexical List"
    description = "Edit words contained in lists (lexical fields)"
    icon = "icons/lexical_hunter.svg"

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = [("Word segmentation", Segmentation, "inputData")]
    outputs = [("Segmentation with annotations", Segmentation)]

    #----------------------------------------------------------------------
    # Layout parameters...

    want_main_area = True

    #----------------------------------------------------------------------
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    textFieldContent = settings.Setting(u''.encode('utf-8'))
    encoding = settings.Setting(u'utf-8')
    selectedFields = []
    listTitle = ""
    listWord = ""

    titleList = settings.Setting([])
    baseLocation = settings.Setting('.')

    def __init__(self, caller):
        """Widget creator."""

        super().__init__()
        # Variable to communicate with the base widjet by calling
        # self.creator.vriable_name

        self.caller = caller
        # Other attributes...
        self.inputSeg = None
        self.outputSeg = None

        # Next two instructions are helpers from TextableUtils. Corresponding
        # interface elements are declared here and actually drawn below (at
        # their position in the UI)...
        self.infoBox = InfoBox(widget=self.controlArea)
        # Temporary dictionary so that the user can cancel changes
        self.tempDict = defaultDict.copy()

        # User interface...

        # CONTROL AREA #
        # Options box for the structure
        titleListBox = gui.widgetBox(
            widget=self.controlArea,
            box="Lists",
            orientation="horizontal",
        )
        # SAVE AREA
        # (After the control one but need to be first for the savechange button)
        SaveBox = gui.widgetBox(
            widget=self.controlArea,
            box=None,
            orientation="horizontal",
        )
        self.SaveChanges = gui.button(
            widget=SaveBox,
            master=self,
            label="Save changes",
            callback=self.saveChanges,
            width=130,
        )
        self.CancelChanges = gui.button(
            widget=SaveBox,
            master=self,
            label="Cancel",
            callback=self.closeWindow,
            width=130,
        )
        # END OF SAVE AREA

        # List of Lexical list that the user can select
        self.titleLabelsList = gui.listBox(
            widget=titleListBox,
            master=self,
            value="selectedFields",    # setting (list)
            labels="titleList",   # setting (list)
            tooltip="The list of lexical list that you want to use for annotation",
            callback=self.updateGUI,
        )
        self.titleLabelsList.setMinimumHeight(300)
        self.titleLabelsList.setMinimumWidth(150)
        self.titleLabelsList.setSelectionMode(1)

        # a box for vertical align of the button
        controlBox = gui.widgetBox(
            widget=titleListBox,
            box=None,
            orientation="vertical",
        )
        # Actions on list
        self.EditList = gui.button(
            widget=controlBox,
            master=self,
            label="Edit",
            callback=self.setEditContent,
            width=130,
            autoDefault=False,
        )
        self.ImportList = gui.button(
            widget=controlBox,
            master=self,
            label="Import",
            callback=self.importLexic,
            width=130,
            autoDefault=False,
        )
        self.ExportList = gui.button(
            widget=controlBox,
            master=self,
            label="Export All",
            callback=self.exportAllLexics,
            width=130,
        )
        self.ExportSelectedList = gui.button(
            widget=controlBox,
            master=self,
            label="Export Selected",
            callback=self.exportOneLexic,
            width=130,
        )
        self.NewList = gui.button(
            widget=controlBox,
            master=self,
            label="New",
            callback=self.newLexicalField,
            width=130,
        )
        self.ClearList = gui.button(
            widget=controlBox,
            master=self,
            label="Clear all",
            callback=self.clearList,
            width=130,
        )
        self.RemoveSelectedList = gui.button(
            widget=controlBox,
            master=self,
            label="Remove Selected",
            callback=self.deleteSelectedList,
            width=130,
        )

        # MAIN AREA (edit list) #
        # structure ...
        listEditBox = gui.widgetBox(
            widget=self.mainArea,
            box="Edit",
            orientation="vertical",
        )
        listEditBox.setMinimumWidth(300)
        # Edit the titile of the list
        self.titleEdit = gui.lineEdit(
            widget=listEditBox,
            master=self,
            value="listTitle",
            label="List name",
            orientation="vertical",
        )

        # structure ...
        editBox = gui.widgetBox(
            widget=listEditBox,
            box="List content",
            orientation="vertical",
            margin=0,
            spacing=0,
        )

        # Editable text Field. Each line gonna be a enter of
        # the lexical list selected
        self.editor = QPlainTextEdit()
        editBox.layout().addWidget(self.editor)
        self.editor.textChanged.connect(self.dontforgettosaveChange)
        self.editor.setMinimumHeight(300)

        # For saving the chang on the list edit
        self.CommitList = gui.button(
            widget=listEditBox,
            master=self,
            label="Commit",
            callback=self.saveEdit,
            width=100,
        )

        gui.rubber(self.controlArea)

        self.setTitleList()
        self.updateGUI()

        # Now Info box and Send button must be drawn...
        self.infoBox.draw()

    def setEditContent(self):
        """Sets the lexical field informations when the user wants to edit it"""
        # Getting selected list title
        self.listTitle = list(self.titleList)[self.selectedFields[0]]
        # Converting words list to string
        self.editContent = '\n'.join(self.tempDict[self.listTitle])
        # Setting editor content with words list (converted to string)
        self.editor.setPlainText(self.editContent)
        # Getting old title (to delete it later if the users wants to)
        self.oldTitle = self.listTitle

        self.updateGUI()

    def setTitleList(self):
        """Displays the lexical fields titles in the edit widget view"""
        self.titleList = self.tempDict.keys()

    def clearList(self):
        """Clears the list of lexical fields"""
        confBox = QMessageBox(QMessageBox.Question, "Textable", "Do you really want to delete all the lexic lists?", QMessageBox.Yes | QMessageBox.No)
        
        # Getting the answer of the user
        result = confBox.exec_()
        if result == QMessageBox.Yes:
            # Reset textfields values
            self.titleEdit.setText("")
            self.editor.setPlainText("")
            # Deleting all lexical fields
            self.tempDict.clear()
            self.setTitleList()
        else:
            pass

    def deleteSelectedList(self):
        """Deletes selected lexical field"""
        confBox = QMessageBox(QMessageBox.Question, "Textable", "Do you really want to delete this list?", QMessageBox.Yes | QMessageBox.No)
        
        # Getting the answer of the user
        result = confBox.exec_()
        if result == QMessageBox.Yes:
            # Getting selected list title
            self.listToDelete = list(self.titleList)[self.selectedFields[0]]
            # Reset textfields values
            self.titleEdit.setText("")
            self.editor.setPlainText("")
            # Deleting selected list
            self.tempDict.pop(self.listToDelete, None)
            self.titleList = self.tempDict.keys()
        else:
            pass

    def newLexicalField(self):
        """Sets a new entry in the lexical fields dictionnary"""
        newDict = "New lexical field"
        i = 1
        while newDict in self.tempDict.keys():
            newDict = "New lexical field %i" %i
            i += 1

        self.tempDict[newDict] = ""
        self.setTitleList()

    def saveEdit(self):
        """Saves the modifications made by the user on the list"""
        # Getting textfields values
        self.val = self.editor.toPlainText()
        self.newTitle = self.titleEdit.text()

        # Reset textfields values
        self.titleEdit.setText("")
        self.editor.setPlainText("")

        wordList = self.val.split("\n")

        self.tempDict[self.newTitle] = wordList
        # Deleting old key and value
        if self.newTitle != self.oldTitle:
            del self.tempDict[self.oldTitle]

        self.titleList = self.tempDict.keys()

        self.updateGUI()

    def saveChanges(self):
        """Saves changes made by the user"""
        defaultDict.clear()
        defaultDict.update(self.tempDict)
        self.hide()
        self.caller.setTitleList()

    def closeWindow(self):
        """Cancels changes made by the user"""
        self.hide()

    def importLexic(self):
        """Lets the user import a lexical field from a text file"""

        # Opening a file browser
        filePath = QFileDialog.getOpenFileName(
            self,
            u'Import lexical field file',
            self.baseLocation,
            u'Text files (*)'
        )
        if not filePath:
            return
        self.file = os.path.normpath(filePath)
        self.baseLocation = os.path.dirname(filePath)
        # Gets txt file name and substracts .txt extension
        fileName = os.path.join(self.baseLocation, self.file);

        # Cutting the path to get the name
        if platform.system() == "Windows":
            listLexicName = fileName.split('\\')

        else:
            listLexicName = fileName.split('/')

        # Getting file name
        lexicName = listLexicName[-1]
        lexicName = re.sub('\.txt$', '', lexicName)


        # Trying to open the files and store their content in a dictionnary
        # then store all of theses in a list
        try:
            fileHandle = open(fileName, encoding='utf-8')
            self.tempDict[lexicName] = fileHandle.readlines()
            fileHandle.close()
            self.setTitleList()
        except IOError:
            QMessageBox.warning(
                None,
                'Textable',
                "Couldn't open file.",
                QMessageBox.Ok
            )
            return

    def exportOneLexic(self):
        """Lets the user export the selected lexic to a text file"""
        # Opening file browser
        filePath = QFileDialog.getSaveFileName(
            self,
            u'Export Selected Lexic',
            self.baseLocation,
        )

        # Setting content to save
        exportTitle = list(self.titleList)[self.selectedFields[0]]
        exportContent = self.tempDict[exportTitle]

        # Saving lexic content
        if filePath:
            outputFile = open(
                filePath,
                encoding='utf8',
                mode='w+',
                errors='xmlcharrefreplace',
            )

            outputFile.write('\n'.join(exportContent))
            outputFile.close()
            QMessageBox.information(
                None,
                'Textable',
                'Lexic file correctly exported',
                QMessageBox.Ok
            )

    def exportAllLexics(self):
        """Lets the user export all the lexics"""
        # Opening file browser
        filePath = QFileDialog.getExistingDirectory(
            self,
            u'Export Selected Lexic',
            self.baseLocation
        )

        if filePath:
            for name in self.tempDict:
                exportName = name.replace(" ", "_")
                if platform.system() == "Windows":
                    fullName = r"{}\{}.txt".format(filePath, exportName)
                else:
                    fullName = r"{}/{}.txt".format(filePath, exportName)

                outputFile = open(
                    fullName,
                    encoding='utf8',
                    mode='w+',
                    errors='xmlcharrefreplace',
                )
                outputFile.write('\n'.join(self.tempDict[name]))
                outputFile.close()
            QMessageBox.information(
                None,
                'Textable',
                'Lexic files correctly exported',
                QMessageBox.Ok
            )

    def dontforgettosaveChange(self):
        """
        Diplay a warning message when the user edit the textfield of the list
        """
        self.infoBox.setText("Don't forget to save your changes after \
            commiting your list", "warning")

    def inputData(self, newInput):
        """Process incoming data."""
        pass

    def updateGUI(self):
        if self.titleEdit.text() != "":
            # Disabled elements
            self.SaveChanges.setDisabled(True)
            self.CancelChanges.setDisabled(True)
            self.EditList.setDisabled(True)
            self.ImportList.setDisabled(True)
            self.ExportList.setDisabled(True)
            self.ExportSelectedList.setDisabled(True)
            self.NewList.setDisabled(True)
            self.ClearList.setDisabled(True)
            self.RemoveSelectedList.setDisabled(True)

            # Enabled elements
            self.CommitList.setDisabled(False)
            self.editor.setDisabled(False)
            self.titleEdit.setDisabled(False)

        if self.titleEdit.text() == "":
            # Enabled elements
            self.SaveChanges.setDisabled(False)
            self.CancelChanges.setDisabled(False)
            self.EditList.setDisabled(False)
            self.ImportList.setDisabled(False)
            self.ExportList.setDisabled(False)
            self.ExportSelectedList.setDisabled(False)
            self.NewList.setDisabled(False)
            self.ClearList.setDisabled(False)
            self.RemoveSelectedList.setDisabled(False)

            # Disabled elements
            self.CommitList.setDisabled(True)
            self.editor.setDisabled(True)
            self.titleEdit.setDisabled(True)

        if not self.selectedFields:
            # Disabled elements if a list isn't selected
            self.RemoveSelectedList.setDisabled(True)
            self.ExportSelectedList.setDisabled(True)
            self.EditList.setDisabled(True)


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
