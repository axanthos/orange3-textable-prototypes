"""
Class TheatreClassique
Copyright 2017 University of Lausanne
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

__version__ = u"0.1.1"
__author__ = "Aris Xanthos"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"


from Orange.widgets import widget, gui, settings

from LTTL.Segmentation import Segmentation
from LTTL.Input import Input
import LTTL.Segmenter as Segmenter
import LTTL.Processor as Processor

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, AdvancedSettings
)
from Orange.widgets import widget, gui, settings

import urllib
import re
import inspect
import os
import pickle


class TheatreClassique(OWTextableBaseWidget):
    """Textable widget for importing XML-TEI data from the Theatre-classique
    website (http://www.theatre-classique.fr)
    """

    #----------------------------------------------------------------------
    # Widget"s metadata...

    name = "Theatre Classique"
    description = "Import XML-TEI data from theatre-classique website"
    icon = "icons/theatre_classique.svg"
    priority = 10

    #----------------------------------------------------------------------
    # Channel definitions (NB: no input in this case)...

    inputs = []
    outputs = [("XML-TEI data", Segmentation)]

    #----------------------------------------------------------------------
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    
    autoSend = settings.Setting(False)
    label = settings.Setting("xml_tei_data")
    selectedTitles = settings.Setting([])
    titleLabels = settings.Setting([])
    filterCriterion = settings.Setting("author")
    filterValue = settings.Setting("(all)")
    importedURLs = settings.Setting([])
    displayAdvancedSettings = settings.Setting(False) 

    want_main_area = False
    
    def __init__(self):
        """Widget creator."""

        super().__init__()

        # Other attributes...
        self.segmentation = None
        self.createdInputs = list()
        self.titleSeg = None
        self.filteredTitleSeg = None
        self.filterValues = dict()
        self.base_url =     \
          u"http://www.theatre-classique.fr/pages/programmes/PageEdition.php"
        self.document_base_url =     \
          u"http://www.theatre-classique.fr/pages/"

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

        # The AdvancedSettings class, also from TextableUtils, facilitates
        # the management of basic vs. advanced interface. An object from this 
        # class (here assigned to self.advancedSettings) contains two lists 
        # (basicWidgets and advancedWidgets), to which the corresponding
        # widgetBoxes must be added.
        self.advancedSettings = AdvancedSettings(
            widget=self.controlArea,
            master=self,
            callback=self.updateFilterValueList,
        )

        # User interface...

        # Advanced settings checkbox (basic/advanced interface will appear 
        # immediately after it...
        self.advancedSettings.draw()

        # Filter box (advanced settings only)
        filterBox = gui.widgetBox(
            widget=self.controlArea,
            box="Filter",
            orientation="vertical",
        )
        filterCriterionCombo = gui.comboBox(
            widget=filterBox,
            master=self,
            value="filterCriterion",
            items=["author", "year", "genre"],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Criterion:",
            labelWidth=120,
            callback=self.updateFilterValueList,
            tooltip=(
                "Please select a criterion for searching the title list\n"
            ),
        )
        filterCriterionCombo.setMinimumWidth(120)
        gui.separator(widget=filterBox, height=3)
        self.filterValueCombo = gui.comboBox(
            widget=filterBox,
            master=self,
            value="filterValue",
            sendSelectedValue=True,
            orientation="horizontal",
            label="Value:",
            labelWidth=120,
            callback=self.updateTitleList,
            tooltip=("Please select a value for the chosen criterion."),
        )
        gui.separator(widget=filterBox, height=3)
        
        # The following lines add filterBox (and a vertical separator) to the
        # advanced interface...
        self.advancedSettings.advancedWidgets.append(filterBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # Title box
        titleBox = gui.widgetBox(
            widget=self.controlArea,
            box="Titles",
            orientation="vertical",
        )
        self.titleListbox = gui.listBox(
            widget=titleBox,
            master=self,
            value="selectedTitles",    # setting (list)
            labels="titleLabels",      # setting (list)
            callback=self.sendButton.settingsChanged,
            tooltip="The list of titles whose content will be imported",
        )
        self.titleListbox.setMinimumHeight(150)
        self.titleListbox.setSelectionMode(3)
        gui.separator(widget=titleBox, height=3)
        gui.button(
            widget=titleBox,
            master=self,
            label="Refresh",
            callback=self.refreshTitleSeg,
            tooltip="Connect to Theatre-classique website and refresh list.",
        )
        gui.separator(widget=titleBox, height=3)

        gui.separator(widget=self.controlArea, height=3)

        gui.rubber(self.controlArea)

        # Now Info box and Send button must be drawn...
        self.sendButton.draw()
        self.infoBox.draw()
        
        # This initialization step needs to be done after infoBox has been 
        # drawn (because getTitleSeg may need to display an error message).
        self.getTitleSeg()

        # Send data if autoSend.
        self.sendButton.sendIf()

        self.setMinimumWidth(350)
        self.adjustSizeWithTimer()

    def sendData(self):
        """Compute result of widget processing and send to output"""

        # Skip if title list is empty:
        if self.titleLabels == list():
            return
        
        # Check that something has been selected...
        if len(self.selectedTitles) == 0:
            self.infoBox.setText(
                "Please select one or more titles.", 
                "warning"
            )
            self.send("XML-TEI data", None, self)
            return

        # Clear created Inputs.
        self.clearCreatedInputs()
        
        # Initialize progress bar.
        progressBar = gui.ProgressBar(
            self, 
            iterations=len(self.selectedTitles)
        )       
        
        # Attempt to connect to Theatre-classique and retrieve plays...
        xml_contents = list()
        annotations = list()
        try:
            for title in self.selectedTitles:
                response = urllib.request.urlopen(
                    self.document_base_url + 
                    self.filteredTitleSeg[title].annotations["url"]
                )
                xml_contents.append(response.read().decode('utf-8'))
                annotations.append(
                    self.filteredTitleSeg[title].annotations.copy()
                )
                progressBar.advance()   # 1 tick on the progress bar...

        # If an error occurs (e.g. http error, or memory error)...
        except:

            # Set Info box and widget to "error" state.
            self.infoBox.setText(
                "Couldn't download data from theatre-classique website.", 
                "error"
            )

            # Reset output channel.
            self.send("XML-TEI data", None, self)
            return
            
        # Store downloaded XML in input objects...
        for xml_content_idx in range(len(xml_contents)):
            newInput = Input(xml_contents[xml_content_idx], self.captionTitle)
            self.createdInputs.append(newInput)
            
        # If there"s only one play, the widget"s output is the created Input.
        if len(self.createdInputs) == 1:
            self.segmentation = self.createdInputs[0]
            
        # Otherwise the widget"s output is a concatenation...
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
            
        # Store imported URLs as setting.
        self.importedURLs = [
            self.filteredTitleSeg[self.selectedTitles[0]].annotations["url"]
        ]
        
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
        progressBar.finish()

        # Clear progress bar.
        progressBar.finish()
        
        # Send token...
        self.send("XML-TEI data", self.segmentation, self)
        self.sendButton.resetSettingsChangedFlag()        
        
    def getTitleSeg(self):
        """Get title segmentation, either saved locally or online"""
        
        # Try to open saved file in this module"s directory...
        path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )
        try:
            file = open(os.path.join(path, "cached_title_list"),"rb")
            self.titleSeg = pickle.load(file)
            file.close()
        # Else try to load list from Theatre-classique and build new seg...
        except IOError:
            self.titleSeg = self.getTitleListFromTheatreClassique()

        # Build author, year and genre lists...
        if self.titleSeg is not None:
            self.filterValues["author"] = Processor.count_in_context(
                units={
                    "segmentation": self.titleSeg, 
                    "annotation_key": "author"
                }
            ).col_ids
            self.filterValues["author"].sort()
            self.filterValues["year"] = Processor.count_in_context(
                units={
                    "segmentation": self.titleSeg, 
                    "annotation_key": "year"
                }
            ).col_ids
            self.filterValues["year"].sort(key=lambda v: int(v))
            self.filterValues["genre"] = Processor.count_in_context(
                units={
                    "segmentation": self.titleSeg, 
                    "annotation_key": "genre"
                }
            ).col_ids
            self.filterValues["genre"].sort()

        # Sort the segmentation alphabetically based on titles (nasty hack!)...
        self.titleSeg.buffer.sort(key=lambda s: s.annotations["title"])
        
        # Update title and filter value lists (only at init and on manual
        # refresh, therefore separate from self.updateGUI).
        self.updateFilterValueList()
                    
    def refreshTitleSeg(self):
        """Refresh title segmentation from website"""
        self.titleSeg = self.getTitleListFromTheatreClassique()
        # Update title and filter value lists (only at init and on manual
        # refresh, therefore separate from self.updateGUI).
        self.updateFilterValueList()
        
    def getTitleListFromTheatreClassique(self):
        """Fetch titles from the Theatre-classique website"""

        self.infoBox.customMessage(
            "Fetching data from Theatre-classique website, please wait"
        )
        
        # Attempt to connect to Theatre-classique...
        try:
            response = urllib.request.urlopen(self.base_url)
            base_html = response.read().decode('iso-8859-1')
            self.infoBox.customMessage(
                "Done fetching data from Theatre-classique website."
            )

        # If unable to connect (somehow)...
        except:

            # Set Info box and widget to "warning" state.
            self.infoBox.noDataSent(
                warning="Couldn't access theatre-classique website."
            )

            # Empty title list box.
            self.titleLabels = list()

            # Reset output channel.
            self.send("XML-TEI data", None, self)
            return None
            
        # Otherwise store HTML content in LTTL Input object.
        base_html_seg = Input(base_html)

        # Remove accents from the data...
        recoded_seg = Segmenter.recode(base_html_seg, remove_accents=True)

        # Extract table containing titles from HTML.
        table_seg = Segmenter.import_xml(
            segmentation=recoded_seg,
            element="table",
            conditions={"id": re.compile(r"^table_AA$")},
        )

        # Extract table lines.
        line_seg = Segmenter.import_xml(
            segmentation=table_seg,
            element="tr",
        )

        # Compile the regex that will be used to parse each line.
        field_regex = re.compile(
            r"^\s*<td>\s*<a.+?>(.+?)</a>\s*</td>\s*"
            r"<td>(.+?)</td>\s*"
            r"<td.+?>\s*<a.+?>\s*(\d+?)\s*</a>\s*</td>\s*"
            r"<td.+?>\s*(.+?)\s*</td>\s*"
            r"<td.+?>\s*<a\s+.+?t=\.{2}/(.+?)'>\s*HTML"
        )

        # Parse each line and store the resulting segmentation in an attribute.
        titleSeg = Segmenter.tokenize(
            segmentation=line_seg,
            regexes=[
                (field_regex, "tokenize", {"author": "&1"}),
                (field_regex, "tokenize", {"title": "&2"}),
                (field_regex, "tokenize", {"year": "&3"}),
                (field_regex, "tokenize", {"genre": "&4"}),
                (field_regex, "tokenize", {"url": "&5"}),
            ],
            import_annotations=False,
            merge_duplicates=True,
        )

        # Try to save list in this module"s directory for future reference...
        path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )
        try:
            file = open(os.path.join(path, "cached_title_list"), "wb")
            pickle.dump(titleSeg, file, -1) 
            file.close()         
        except IOError:
            pass

        # Remove warning (if any)...
        self.error(0)
        self.warning(0)
        
        return titleSeg

    def updateFilterValueList(self):
        """Update the list of filter values"""
        
        # In Advanced settings mode, populate filter value list...
        if self.titleSeg is not None and self.displayAdvancedSettings:
            self.filterValueCombo.clear()
            self.filterValueCombo.addItem("(all)")
            for filterValue in self.filterValues[self.filterCriterion]:
                self.filterValueCombo.addItem(filterValue)

        # Reset filterValue if needed...
        if self.filterValue not in [
            self.filterValueCombo.itemText(i) 
            for i in range(self.filterValueCombo.count())
        ]:
            self.filterValue = "(all)"
        else:
            self.filterValue = self.filterValue
        
        self.updateTitleList()

    def updateTitleList(self):
        """Update the list of titles"""
        
        # If titleSeg has not been loaded for some reason, skip.
        if self.titleSeg is None:
            return
        
        # In Advanced settings mode, get list of selected titles...
        if self.displayAdvancedSettings and self.filterValue != "(all)":
            self.filteredTitleSeg, _ = Segmenter.select(
                segmentation=self.titleSeg,
                regex=re.compile(r"^%s$" % self.filterValue),
                annotation_key=self.filterCriterion,
            )
        else:
            self.filteredTitleSeg = self.titleSeg
        
        # Populate titleLabels list with the titles...
        self.titleLabels = sorted(
            [s.annotations["title"] for s in self.filteredTitleSeg]
        )
        
        # Add specification (author, year and genre, depending on criterion)...
        titleLabels = self.titleLabels[:]
        for idx, titleLabel in enumerate(titleLabels):
            specs = list()
            if (
                self.displayAdvancedSettings == False or
                self.filterCriterion != "author" or 
                self.filterValue == "(all)"
            ):
                specs.append(
                    self.filteredTitleSeg[idx].annotations["author"]
                )
            if (
                self.displayAdvancedSettings == False or
                self.filterCriterion != "year" or 
                self.filterValue == "(all)"
            ):
                specs.append(
                    self.filteredTitleSeg[idx].annotations["year"]
                )
            if (
                self.displayAdvancedSettings == False or
                self.filterCriterion != "genre" or 
                self.filterValue == "(all)"
            ):
                specs.append(
                    self.filteredTitleSeg[idx].annotations["genre"]
                )
            titleLabels[idx] = titleLabel + " (%s)" % "; ".join(specs)
        self.titleLabels = titleLabels
        
        # Reset selectedTitles if needed...
        if not set(self.importedURLs).issubset(
            set(u.annotations["url"] for u in self.filteredTitleSeg)
        ):
            self.selectedTitles = list()
        else:
            self.selectedTitles = self.selectedTitles

        self.sendButton.settingsChanged()

    def updateGUI(self):
        """Update GUI state"""
        if self.displayAdvancedSettings:
            self.advancedSettings.setVisible(True)
        else:
            self.advancedSettings.setVisible(False)
            
        if len(self.titleLabels) > 0:
            self.selectedTitles = self.selectedTitles
            
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
    myWidget = TheatreClassique()
    myWidget.show()
    myApplication.exec_()
    myWidget.saveSettings()

