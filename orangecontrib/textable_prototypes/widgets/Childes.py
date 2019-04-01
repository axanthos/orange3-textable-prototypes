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

__version__ = u"0.0.2"
__author__ = "Aris Xanthos"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"


import os
import io
import re
import pickle
import inspect
import zipfile

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

    importedCorpora = settings.Setting(list())
    outputUtterances = settings.Setting(False)
    autoSend = settings.Setting(False)

    #----------------------------------------------------------------------
    # Other class variables...
    
    base_url = "https://childes.talkbank.org/data-xml/"
    cache_filename = "cache_childes"

    want_main_area = False

    def __init__(self):
        """Widget creator."""

        super().__init__()

        # Other (non-setting) attributes...
        self.segmentation = None
        self.createdInputs = list()
        self.displayedFolderLabels = list()
        self.currentFolder = self.__class__.base_url
        self.database = None
        self.selectedInDisplayedFolder = list()
        self.selectedInSelection = list()
        self.selectionLabels = list()
        

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
        self.homeRefreshButton = gui.button(
            widget=upwardNavBox,
            master=self,
            label="Home",
            callback=self.homeRefreshPressed,
            tooltip="Return to database root.",
            # tooltip="Connect to CHILDES website and refresh corpus list.",
        )
        self.backButton = gui.button(
            widget=upwardNavBox,
            master=self,
            label="Back",
            callback=self.backPressed,
            tooltip="View parent folder.",
        )

        gui.separator(widget=browseBox, height=3)

        self.currentFolderLabel = gui.label(
            widget=browseBox,
            master=self,
            label="Current folder: /",
            tooltip="This is the currently displayed folder.",
        )

        gui.separator(widget=browseBox, height=3)

        displayedFolderListbox = gui.listBox(
            widget=browseBox,
            master=self,
            value="selectedInDisplayedFolder", 
            labels="displayedFolderLabels",
            callback=self.corpusSelected,
            tooltip="Select an item to open or import.",
        )
        displayedFolderListbox.setMinimumHeight(120)
        displayedFolderListbox.setSelectionMode(3)
        displayedFolderListbox.doubleClicked.connect(
            self.displayedFoldersDoubleClicked
        )

        gui.separator(widget=browseBox, height=3)

        downwardNavBox = gui.widgetBox(
            widget=browseBox,
            box=False,
            orientation="horizontal",
        )
        self.openButton = gui.button(
            widget=downwardNavBox,
            master=self,
            label="Open",
            callback=self.openPressed,
            tooltip="View selected folder's contents.",
        )
        self.addButton = gui.button(
            widget=downwardNavBox,
            master=self,
            label="Add to selection",
            callback=self.addPressed,
            tooltip="Add selected items contents to selection.",
        )

        gui.separator(widget=browseBox, height=3)

        # Selection box...
        selectionBox = gui.widgetBox(
            widget=self.controlArea,
            box="Selection",
            orientation="vertical",
            addSpace=False,
        )

        selectionListbox = gui.listBox(
            widget=selectionBox,
            master=self,
            value="selectedInSelection",
            labels="selectionLabels",
            callback=lambda: self.removeButton.setDisabled( # TODO move
                self.selectedInSelection == list()),
            tooltip="The list of corpora whose content will be imported",
        )
        selectionListbox.setMinimumHeight(120)
        selectionListbox.setSelectionMode(3)
        selectionListbox.doubleClicked.connect(self.selectionDoubleClicked)

        removalBox = gui.widgetBox(
            widget=selectionBox,
            box=False,
            orientation="horizontal",
        )
        # Remove songs button
        self.removeButton = gui.button(
            widget=removalBox,
            master=self,
            label="Remove from selection",
            callback=self.removePressed,
            tooltip="Remove the selected corpus.",
        )

        # Delete all confirmed songs button
        self.clearButton = gui.button(
            widget=removalBox,
            master=self,
            label="Clear selection",
            callback=self.clearPressed,
            tooltip="Remove all corpora from selection.",
        )

        gui.separator(widget=selectionBox, height=3)

        # Options box...
        optionBox = gui.widgetBox(
            widget=self.controlArea,
            box="Options",
            orientation="vertical",
            addSpace=False,
        )
        
        gui.checkBox(
            widget=optionBox,
            master=self,
            value='outputUtterances',
            label=u'Output utterance segmentation',
            callback=self.outputUtterancesClicked,
            tooltip=u"TODO",
        )

        gui.separator(widget=optionBox, height=3)

        gui.rubber(self.controlArea)
        
        # Now Info box and Send button must be drawn...
        self.sendButton.draw()
        self.infoBox.draw()

        # This initialization step needs to be done after infoBox has been
        # drawn (because we may need to display an error message).
        self.loadDatabaseCache()

        self.updateSelection()

        # Send data if autoSend.
        self.sendButton.sendIf()

        self.setMinimumWidth(350)
        self.adjustSizeWithTimer()

    def sendData(self):
        """Compute result of widget processing and send to output"""
        if not self.importedCorpora:
            self.infoBox.setText(
                "Please select a corpus to import.",
                "warning"
            )
            self.send("XML data", None, self)
            return
       
        # Clear created Inputs and initialize progress bar...
        self.clearCreatedInputs()
        self.infoBox.setText(
            "Downloading data from CHILDES website, please wait...", 
            "warning",
        )     
        progressBar = ProgressBar(self, iterations=len(self.importedCorpora))
        self.controlArea.setDisabled(True)
        
        annotations = list()

        # Iterate over corpora...
        for importedCorpus in self.importedCorpora:
        
            corpus = importedCorpus.split("/")[-1]
            
            # Download requested zip file...
            try:    # TODO Test errors
                response = requests.get(importedCorpus)
                
            # If an error occurs (e.g. http error)...
            except:

                # Set Info box and widget to "error" state.
                self.infoBox.setText(
                    "Couldn't download corpus %s from CHILDES website."
                        % corpus,
                    "error"
                )

                # Reset output channel.
                self.send("XML data", None, self)
                progressBar.finish()
                self.controlArea.setDisabled(False)
                return
            
            # Create Input for each zipped file and store annotations...
            myZip = zipfile.ZipFile(io.BytesIO(response.content))
            for file in myZip.infolist():
                newInput = Input(
                    myZip.read(file).decode('utf-8'), 
                    self.captionTitle
                )
                self.createdInputs.append(newInput)
                chatSeg = Segmenter.import_xml(newInput, "CHAT")
                annotations.append(dict())
                annotations[-1]["file_path"] = file.filename
                for key in ["Corpus", "Lang", "PID"]:
                    try:
                        annotations[-1][key.lower()] =  \
                            chatSeg[0].annotations[key]
                    except KeyError:
                        pass
                participantListSeg = Segmenter.import_xml(
                    newInput, "Participants"
                )
                recodedInput, _ = Segmenter.recode(
                    participantListSeg, [
                        (re.compile("/>"), "> </participant>")
                    ]
                )
                participantSeg = Segmenter.import_xml(
                    recodedInput, "participant"
                )
                targetChildData = list()
                for participant in participantSeg:
                    if participant.annotations["role"] != "Target_Child":
                        continue
                    targetChildData.append(dict())
                    if "age" in participant.annotations:
                        targetChildData[-1]["target_child_age"] =   \
                            participant.annotations["age"]
                    if "id" in participant.annotations:
                        targetChildData[-1]["target_child_id"] =   \
                            participant.annotations["id"]
                    if "sex" in participant.annotations:
                        targetChildData[-1]["target_child_sex"] =   \
                            participant.annotations["sex"]
                if len(targetChildData) == 1:
                    annotations[-1].update(targetChildData[0])
                    
            progressBar.advance()

        # If there's only one file, the widget's output is the created Input...
        if len(self.createdInputs) == 1:
            self.segmentation = self.createdInputs[0]

        # Otherwise the widget's output is a concatenation...
        else:
            self.segmentation = Segmenter.concatenate(
                self.createdInputs,
                self.captionTitle,
                import_labels_as=None,
            )

        # Annotate segments...
        for idx, segment in enumerate(self.segmentation):
            segment.annotations.update(annotations[idx])
            self.segmentation[idx] = segment

        # Set status to OK and report data size...
        message = "%i segment@p sent to output " % len(self.segmentation)
        message = pluralize(message, len(self.segmentation))
        numChars = 0
        for segment in self.segmentation:
            segmentLength = len(Segmentation.get_data(segment.str_index))
            numChars += segmentLength
        message += "(%i character@p)." % numChars
        message = pluralize(message, numChars)
        self.infoBox.setText(message)

        # Terminate progress bar...
        progressBar.finish()
        self.controlArea.setDisabled(False)

        # Send token...
        self.send("XML data", self.segmentation, self)

        self.sendButton.resetSettingsChangedFlag()

    def homeRefreshPressed(self):
        """Refresh database file tree"""
        if self.currentFolder != self.__class__.base_url:
            self.currentFolder = self.__class__.base_url
            self.updateDisplayedFolders()
        else:
            self.refreshDatabaseCache()

    def backPressed(self):
        """Display parent folder's contents"""
        self.currentFolder = "/".join(self.currentFolder[:-1].split("/")[:-1])
        self.currentFolder += "/"
        self.updateDisplayedFolders()        

    def corpusSelected(self):
        """Import selected corpus"""
        self.updateBrowseBoxButtons()

    def openPressed(self):
        """Display selected folder's contents"""
        if len(self.selectedInDisplayedFolder) == 1:
            self.currentFolder += self.displayedFolderLabels[
                self.selectedInDisplayedFolder[0]
            ]
            self.updateDisplayedFolders()

    def addPressed(self):
        """Import selected corpora"""
        corpora = list()
        for item in self.selectedInDisplayedFolder:
            label = self.displayedFolderLabels[item]
            self.getZipsFromItem(label, self.currentFolder, corpora)
        self.importedCorpora += corpora
        self.importedCorpora = sorted(list(set((self.importedCorpora))))
        self.addButton.setDisabled(True)
        self.updateSelection()
        self.sendButton.settingsChanged()

    def getZipsFromItem(self, label, folder, zipList):
        """Get selected zip files or those contained in selected folders"""
        if label.endswith(".zip"):
            zipList.append(folder + label)
            return
        else:
            newFolder = self.getFolderContent(folder + label)
            for label in newFolder.keys():
                if label.endswith(".zip"):
                    label = newFolder[label]
                label = label[len(self.__class__.base_url):]
                self.getZipsFromItem(label, folder, zipList)
                
    def displayedFoldersDoubleClicked(self):
        """Reroute to 'openPressed' or 'addPressed' as needed"""
        if self.displayedFolderLabels[
            self.selectedInDisplayedFolder[0]
        ].endswith(".zip"):
            self.addPressed()
        else:
            self.openPressed()

    def removePressed(self):
        """Remove selected items"""
        for idx in sorted(self.selectedInSelection, reverse=True):
            del self.importedCorpora[idx]            
        self.updateSelection()
        self.sendButton.settingsChanged()      

    def clearPressed(self):
        """Empty the selection"""
        self.importedCorpora = list()
        self.updateSelection()
        self.sendButton.settingsChanged()      

    def selectionDoubleClicked(self):
        """Reroute to removePressed"""
        self.removePressed()

    def outputUtterancesClicked(self):
        """Handle 'output utterances' checkbox"""
        pass
        
    def refreshDatabaseCache(self):
        """Refresh the database cache"""
        self.infoBox.setText(
            "Scraping CHILDES website, please wait...", 
            "warning",
        )     
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=1)
        
        # Scrape website...
        self.database = dict()
        self.importedCorpora = list()
        try:
            self.recursivelyScrapeUrl(
                self.__class__.base_url, 
                self.database,
            )
            # Dump cache to file...
            path = os.path.dirname(
                os.path.abspath(inspect.getfile(inspect.currentframe()))
            )
            try:
                file = open(
                    os.path.join(path, self.__class__.cache_filename),
                    "wb",
                )
                pickle.dump(self.database, file)
                file.close()
            except IOError:
                self.infoBox.setText(
                    "Couldn't save database to disk.", 
                    "warning",
                )
            self.sendButton.settingsChanged()
        except requests.exceptions.ConnectionError:
            self.infoBox.setText(
                "Error while attempting to scrape the CHILDES website.", 
                "error",
            )
            self.send("XML data", None, self)
              
        progressBar.advance()
        progressBar.finish()
        self.currentFolder = self.__class__.base_url
        self.updateDisplayedFolders()
        self.updateSelection()
        self.controlArea.setDisabled(False)

    def recursivelyScrapeUrl(self, url, urls):
        """Scrape the CHILDES website recursively"""
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        links = soup.find_all('a')
        if links is None or len(links) == 0:
            return
        else:
            urls[url] = dict()
            for link in links:
                new_url = url+link["href"]
                if(
                    link["href"].endswith("/") 
                    and len(link["href"]) > 1
                    and not link["href"].startswith("/data-xml/")
                ):
                    self.recursivelyScrapeUrl(new_url, urls[url])
                elif link["href"].endswith(".zip"):
                    urls[url][link["href"]] = new_url
            if len(urls[url]) == 0:
                del urls[url]
        
    def loadDatabaseCache(self):
        """Load the cached database"""
        # Try to open saved file in this module"s directory...
        path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )
        try:
            file = open(os.path.join(path, self.__class__.cache_filename),"rb")
            self.database = pickle.load(file)
            file.close()
            self.currentFolder = self.__class__.base_url
            self.updateDisplayedFolders()
        # Else try to rebuild cache from CHILDES website...
        except IOError:
            self.refreshDatabaseCache()

    def updateDisplayedFolders(self):
        """Refresh state of displayed folder listbox"""
        # If database couldn't be loaded...
        if not self.database:
            self.currentFolderLabel.setText(
                "No database loaded, please click 'Refresh'."
            )
            self.homeRefreshButton.setDisabled(False)
            self.homeRefreshButton.setText("Refresh")
            self.backButton.setDisabled(True)
            self.openButton.setDisabled(True)
            self.addButton.setDisabled(True)
            return
        
        # Current folder label...
        currentFolder = self.currentFolder[len(self.__class__.base_url)-1:]
        self.currentFolderLabel.setText("Current folder: " + currentFolder)
        
        # Populate listbox...
        folderContent = self.getFolderContent(self.currentFolder)
        displayedFolderLabels = list()
        for item in folderContent.keys():
            if item.endswith(".zip"):
                displayedFolderLabels.append(item)
            else:
                displayedFolderLabels.append(item.split("/")[-2] + "/")
        self.displayedFolderLabels = displayedFolderLabels
        
        # Buttons.
        self.updateBrowseBoxButtons()
            
    def getFolderContent(self, folder):
        folderContent = self.database[self.__class__.base_url]
        folder = folder[len(self.__class__.base_url)-1:]
        steps = folder[:-1].split("/")[1:]
        for idx, _ in enumerate(steps):
            path = self.__class__.base_url + "/".join(steps[:idx+1]) + "/"
            folderContent = folderContent[path]
        return folderContent

    def updateBrowseBoxButtons(self):
        """Refresh state of Browse box buttons"""
        currentFolder = self.currentFolder[len(self.__class__.base_url)-1:]
        if currentFolder == "/": # TODO change tooltip
            self.homeRefreshButton.setText("Refresh")
        else:
            self.homeRefreshButton.setText("Home")
        self.backButton.setDisabled(currentFolder == "/")
        self.openButton.setDisabled(
            len(self.selectedInDisplayedFolder) != 1 or 
            self.displayedFolderLabels[
                self.selectedInDisplayedFolder[0]
            ].endswith(".zip")
        )
        self.addButton.setDisabled(not self.selectedInDisplayedFolder) 

    def updateSelection(self):
        """Refresh state of selection listbox"""
        self.selectionLabels = [
            corpus[len(self.__class__.base_url)-1:]
            for corpus in self.importedCorpora
        ]
        self.updateRemovalButtons()

    def updateRemovalButtons(self):
        """Refresh state of Browse box buttons"""
        self.removeButton.setDisabled(not self.selectedInSelection)
        self.clearButton.setDisabled(not self.importedCorpora)

    def clearCreatedInputs(self):
        """Delete all Input objects that have been created."""
        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]

    def onDeleteWidget(self):
        """Free memory when widget is deleted (overriden method)"""
        self.clearCreatedInputs()

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
