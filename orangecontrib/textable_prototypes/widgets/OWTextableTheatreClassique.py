"""
Class OWTextableTheatreClassique
Copyright 2016 University of Lausanne
-----------------------------------------------------------------------------
This file is part of the Orange-Textable-Prototypes package v0.1.

Orange-Textable-Prototypes v0.1 is free software: you can redistribute it 
and/or modify it under the terms of the GNU General Public License as published 
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Orange-Textable-Prototypes v0.1 is distributed in the hope that it will be 
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Orange-Textable-Prototypes v0.1. If not, see 
<http://www.gnu.org/licenses/>.
"""

__version__ = u'0.2.1'
__author__ = "Aris Xanthos"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

"""
<name>Theatre Classique</name>
<description>Import XML-TEI data from theatre-classique website</description>
<icon>icons/Theatre_Classique.png</icon>
<priority>10</priority>
"""

import Orange
from OWWidget import *
import OWGUI

from LTTL.Segmentation import Segmentation
from LTTL.Input import Input
import LTTL.Segmenter as Segmenter
import LTTL.Processor as Processor

from _textable.widgets.TextableUtils import *   # Provides several utilities.

import urllib2
import re
import inspect
import os
import pickle


class OWTextableTheatreClassique(OWWidget):
    """Orange widget for importing XML-TEI data from the Theatre-classique
    website (http://www.theatre-classique.fr)
    """

    # Widget settings declaration...
    settingsList = [
        u'autoSend',
        u'label',
        u'uuid',
        u'selectedTitles',
        u'filterCriterion',
        u'filterValue',
        u'importedURLs',
        u'displayAdvancedSettings',
    ]

    def __init__(self, parent=None, signalManager=None):
        """Widget creator."""

        # Standard call to creator of base class (OWWidget).
        OWWidget.__init__(            
            self,
            parent,
            signalManager,
            wantMainArea=0,
            wantStateInfoWidget=0,
        )


        # Channel definitions...
        self.inputs = []
        self.outputs = [('Text data', Segmentation)]

        # Settings initializations...
        self.autoSend = True
        self.label = u'xml_tei_data'
        self.filterCriterion = u'author'
        self.filterValue = u'(all)'
        self.titleLabels = list()
        self.selectedTitles = list()
        self.importedURLs = list()
        self.displayAdvancedSettings = False

        # Always end Textable widget settings with the following 3 lines...
        self.uuid = None
        self.loadSettings()
        self.uuid = getWidgetUuid(self)

        # Other attributes...
        self.segmentation = None
        self.createdInputs = list()
        self.titleSeg = None
        self.filteredTitleSeg = None
        self.filterValues = dict()
        self.base_url =     \
          u'http://www.theatre-classique.fr/pages/programmes/PageEdition.php'
        self.document_base_url =     \
          u'http://www.theatre-classique.fr/pages/'

        # Next two instructions are helpers from TextableUtils. Corresponding
        # interface elements are declared here and actually drawn below (at
        # their position in the UI)...
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute=u'infoBox',
            sendIfPreCallback=self.updateGUI,
        )

        # The AdvancedSettings class, also from TextableUtils, facilitates
        # the management of basic vs. advanced interface. An object from this 
        # class (here assigned to self.advancedSettings) contains two lists 
        # (basicWidgets and advanceWidgets), to which the corresponding
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
        filterBox = OWGUI.widgetBox(
            widget=self.controlArea,
            box=u'Filter',
            orientation=u'vertical',
        )
        filterCriterionCombo = OWGUI.comboBox(
            widget=filterBox,
            master=self,
            value=u'filterCriterion',
            items=[u'author', u'year', u'genre'],
            sendSelectedValue=True,
            orientation=u'horizontal',
            label=u'Criterion:',
            labelWidth=120,
            callback=self.updateFilterValueList,
            tooltip=(
                u"Please select a criterion for searching the title list\n"
            ),
        )
        filterCriterionCombo.setMinimumWidth(120)
        OWGUI.separator(widget=filterBox, height=3)
        self.filterValueCombo = OWGUI.comboBox(
            widget=filterBox,
            master=self,
            value=u'filterValue',
            sendSelectedValue=True,
            orientation=u'horizontal',
            label=u'Value:',
            labelWidth=120,
            callback=self.updateTitleList,
            tooltip=(u"Please select a value for the chosen criterion."),
        )
        OWGUI.separator(widget=filterBox, height=3)
        
        # The following lines add filterBox (and a vertical separator) to the
        # advanced interface...
        self.advancedSettings.advancedWidgets.append(filterBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # Title box
        titleBox = OWGUI.widgetBox(
            widget=self.controlArea,
            box=u'Titles',
            orientation=u'vertical',
        )
        self.titleListbox = OWGUI.listBox(
            widget=titleBox,
            master=self,
            value=u'selectedTitles',    # setting (list)
            labels=u'titleLabels',      # setting (list)
            callback=self.sendButton.settingsChanged,
            tooltip=u"The list of titles whose content will be imported",
        )
        self.titleListbox.setMinimumHeight(150)
        self.titleListbox.setSelectionMode(3)
        OWGUI.separator(widget=titleBox, height=3)
        OWGUI.button(
            widget=titleBox,
            master=self,
            label=u'Refresh',
            callback=self.refreshTitleSeg,
            tooltip=u"Connect to Theatre-classique website and refresh list.",
        )
        OWGUI.separator(widget=titleBox, height=3)

        OWGUI.separator(widget=self.controlArea, height=3)

        OWGUI.rubber(self.controlArea)

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
                u'Please select one or more titles.', 
                'warning'
            )
            self.send(u'Text data', None, self)
            return

        # Clear created Inputs.
        self.clearCreatedInputs()
        
        # Initialize progress bar.
        progressBar = OWGUI.ProgressBar(
            self, 
            iterations=len(self.selectedTitles)
        )       
        
        # Attempt to connect to Theatre-classique and retrieve plays...
        xml_contents = list()
        annotations = list()
        try:
            for title in self.selectedTitles:
                response = urllib2.urlopen(
                    self.document_base_url + 
                    self.filteredTitleSeg[title].annotations[u'url']
                )
                xml_contents.append(unicode(response.read(), u'utf8'))
                annotations.append(
                    self.filteredTitleSeg[title].annotations.copy()
                )
                progressBar.advance()   # 1 tick on the progress bar...

        # If an error occurs (e.g. http error, or memory error)...
        except:

            # Set Info box and widget to 'error' state.
            self.infoBox.setText(
                u"Couldn't download data from theatre-classique website.", 
                'error'
            )

            # Reset output channel.
            self.send(u'Text data', None, self)
            return
            
        # Store downloaded XML in input objects...
        for xml_content_idx in xrange(len(xml_contents)):
            newInput = Input(xml_contents[xml_content_idx], self.captionTitle)
            self.createdInputs.append(newInput)
            
        # If there's only one play, the widget's output is the created Input.
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
            
        # Store imported URLs as setting.
        self.importedURLs = [
            self.filteredTitleSeg[self.selectedTitles[0]].annotations[u'url']
        ]
        
        # Set status to OK and report data size...
        message = u'%i segment@p sent to output ' % len(self.segmentation)
        message = pluralize(message, len(self.segmentation))
        numChars = 0
        for segment in self.segmentation:
            segmentLength = len(Segmentation.get_data(segment.str_index))
            numChars += segmentLength
        message += u'(%i character@p).' % numChars
        message = pluralize(message, numChars)
        self.infoBox.setText(message)
        progressBar.finish()

        # Clear progress bar.
        progressBar.finish()
        
        # Send token...
        self.send(u'Text data', self.segmentation, self)
        self.sendButton.resetSettingsChangedFlag()        
        
    def getTitleSeg(self):
        """Get title segmentation, either saved locally or online"""
        
        # Try to open saved file in this module's directory...
        path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )
        try:
            file = open(os.path.join(path, "cached_title_list"),'rb')
            self.titleSeg = pickle.load(file)
            file.close()
        # Else try to load list from Theatre-classique and build new seg...
        except IOError:
            self.titleSeg = self.getTitleListFromTheatreClassique()

        # Build author, year and genre lists...
        if self.titleSeg is not None:
            self.filterValues[u'author'] = Processor.count_in_context(
                units={
                    u'segmentation': self.titleSeg, 
                    u'annotation_key': u'author'
                }
            ).col_ids
            self.filterValues[u'author'].sort()
            self.filterValues[u'year'] = Processor.count_in_context(
                units={
                    u'segmentation': self.titleSeg, 
                    u'annotation_key': u'year'
                }
            ).col_ids
            self.filterValues[u'year'].sort(key=lambda v: int(v))
            self.filterValues[u'genre'] = Processor.count_in_context(
                units={
                    u'segmentation': self.titleSeg, 
                    u'annotation_key': u'genre'
                }
            ).col_ids
            self.filterValues[u'genre'].sort()

        # Sort the segmentation alphabetically based on titles (nasty hack!)...
        self.titleSeg.buffer.sort(key=lambda s: s.annotations[u'title'])
        
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
            u'Fetching data from Theatre-classique website, please wait'
        )
        
        # Attempt to connect to Theatre-classique...
        try:
            response = urllib2.urlopen(self.base_url)
            base_html = unicode(response.read(), 'iso-8859-1')
            self.infoBox.customMessage(
                u'Done fetching data from Theatre-classique website.'
            )

        # If unable to connect (somehow)...
        except:

            # Set Info box and widget to 'warning' state.
            self.infoBox.noDataSent(
                warning=u"Couldn't access theatre-classique website."
            )

            # Empty title list box.
            self.titleLabels = list()

            # Reset output channel.
            self.send(u'Text data', None, self)
            return None
            
        # Otherwise store HTML content in LTTL Input object.
        base_html_seg = Input(base_html)

        # Remove accents from the data...
        recoded_seg = Segmenter.recode(base_html_seg, remove_accents=True)

        # Extract table containing titles from HTML.
        table_seg = Segmenter.import_xml(
            segmentation=recoded_seg,
            element=u'table',
            conditions={u'id': re.compile(ur'^table_AA$')},
        )

        # Extract table lines.
        line_seg = Segmenter.import_xml(
            segmentation=table_seg,
            element=u'tr',
        )

        # Compile the regex that will be used to parse each line.
        field_regex = re.compile(
            ur"^\s*<td>\s*<a.+?>(.+?)</a>\s*</td>\s*"
            ur"<td>(.+?)</td>\s*"
            ur"<td.+?>\s*<a.+?>\s*(\d+?)\s*</a>\s*</td>\s*"
            ur"<td.+?>\s*(.+?)\s*</td>\s*"
            ur"<td.+?>\s*<a\s+.+?t=\.{2}/(.+?)'>\s*HTML"
        )

        # Parse each line and store the resulting segmentation in an attribute.
        titleSeg = Segmenter.tokenize(
            segmentation=line_seg,
            regexes=[
                (field_regex, u'tokenize', {u'author': u'&1'}),
                (field_regex, u'tokenize', {u'title': u'&2'}),
                (field_regex, u'tokenize', {u'year': u'&3'}),
                (field_regex, u'tokenize', {u'genre': u'&4'}),
                (field_regex, u'tokenize', {u'url': u'&5'}),
            ],
            import_annotations=False,
            merge_duplicates=True,
        )

        # Try to save list in this module's directory for future reference...
        path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )
        try:
            file = open(os.path.join(path, u"cached_title_list"), u'wb')
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
            self.filterValueCombo.addItem(u'(all)')
            for filterValue in self.filterValues[self.filterCriterion]:
                self.filterValueCombo.addItem(filterValue)

        # Reset filterValue if needed...
        if self.filterValue not in [
            unicode(self.filterValueCombo.itemText(i)) 
            for i in xrange(self.filterValueCombo.count())
        ]:
            self.filterValue = u'(all)'
        else:
            self.filterValue = self.filterValue
        
        self.updateTitleList()

    def updateTitleList(self):
        """Update the list of titles"""
        
        # If titleSeg has not been loaded for some reason, skip.
        if self.titleSeg is None:
            return
        
        # In Advanced settings mode, get list of selected titles...
        if self.displayAdvancedSettings and self.filterValue != u'(all)':
            self.filteredTitleSeg, _ = Segmenter.select(
                segmentation=self.titleSeg,
                regex=re.compile(ur'^%s$' % self.filterValue),
                annotation_key=self.filterCriterion,
            )
        else:
            self.filteredTitleSeg = self.titleSeg
        
        # Populate titleLabels list with the titles...
        self.titleLabels = sorted(
            [s.annotations[u'title'] for s in self.filteredTitleSeg]
        )
        
        # Add specification (author, year and genre, depending on criterion)...
        titleLabels = self.titleLabels[:]
        for idx, titleLabel in enumerate(titleLabels):
            specs = list()
            if (
                self.displayAdvancedSettings == False or
                self.filterCriterion != 'author' or 
                self.filterValue == u'(all)'
            ):
                specs.append(
                    self.filteredTitleSeg[idx].annotations[u'author']
                )
            if (
                self.displayAdvancedSettings == False or
                self.filterCriterion != 'year' or 
                self.filterValue == u'(all)'
            ):
                specs.append(
                    self.filteredTitleSeg[idx].annotations[u'year']
                )
            if (
                self.displayAdvancedSettings == False or
                self.filterCriterion != 'genre' or 
                self.filterValue == u'(all)'
            ):
                specs.append(
                    self.filteredTitleSeg[idx].annotations[u'genre']
                )
            titleLabels[idx] = titleLabel + " (%s)" % "; ".join(specs)
        self.titleLabels = titleLabels
        
        # Reset selectedTitles if needed...
        if not set(self.importedURLs).issubset(
            set(u.annotations[u'url'] for u in self.filteredTitleSeg)
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

    # The following methods need to be copied (without any change) in
    # every Textable widget...

    def adjustSizeWithTimer(self):
        qApp.processEvents()
        QTimer.singleShot(50, self.adjustSize)

    def setCaption(self, title):
        if 'captionTitle' in dir(self) and title != 'Orange Widget':
            OWWidget.setCaption(self, title)
            self.sendButton.settingsChanged()
        else:
            OWWidget.setCaption(self, title)

    def getSettings(self, *args, **kwargs):
        """Read settings, taking into account version number (overriden)"""
        settings = OWWidget.getSettings(self, *args, **kwargs)
        settings["settingsDataVersion"] = __version__.split('.')[:2]
        return settings

    def setSettings(self, settings):
        """Write settings, taking into account version number (overriden)"""
        if settings.get("settingsDataVersion", None) \
                == __version__.split('.')[:2]:
            settings = settings.copy()
            del settings["settingsDataVersion"]
            OWWidget.setSettings(self, settings)


if __name__ == '__main__':
    myApplication = QApplication(sys.argv)
    myWidget = OWTextableTheatreClassique()
    myWidget.show()
    myApplication.exec_()
