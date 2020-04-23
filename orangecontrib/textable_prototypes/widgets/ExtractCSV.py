"""
Class ExtractCSV
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
__author__ = "Noémie Carette", "Saara Jones", "Sorcha Walsh"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"


from Orange.widgets import gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview

from PyQt5.QtCore import QTimer

from LTTL.Segmentation import Segmentation
from LTTL.Segment import Segment
import LTTL.Segmenter

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar
)

import io
import csv

""" Global variables"""
sniffer = csv.Sniffer()

class ExtractCSV(OWTextableBaseWidget):
    """Textable widget for to extract CSV usign the CSV module and Sniffer."""

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "ExtractCSV"
    description = "Extract tabulated data as a Textable Segmentation"
    icon = "icons/extractcsv.png"
    priority = 21   # TODO

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = [("CSV Data", Segmentation, "inputData")]
    outputs = [("CSV Segmentation", Segmentation)]

    #----------------------------------------------------------------------
    # Layout parameters...
    
    want_main_area = False
    
    #----------------------------------------------------------------------
    # Query settings...

    selected_mode = settings.Setting("automatic")
    #----------------------------------------------------------------------
    
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    
    autoSend = settings.Setting(False)
    model = settings.Setting("fr_core_news_sm")
    
    def __init__(self):
        """Widget creator."""

        super().__init__()

        # Other attributes...
        self.inputSeg = None
        self.outputSeg = None
        self.dialect = None

        # Next two instructions are helpers from TextableUtils. Corresponding
        # interface elements are declared here and actually drawn below (at
        # their position in the UI)...
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute="infoBox",
            sendIfPreCallback=None,
        )

         # User interface...

        #-------------------------#
        #    Main widget box      #
        #-------------------------#
        self.selectBox = gui.widgetBox(
            widget=self.controlArea,
            box = "Select",
            orientation='vertical',
            addSpace=False,
        )
        
        # changing mode combobox 
        self.modeCombo = gui.comboBox(
            widget=self.selectBox,
            master=self, 
            value='selected_mode',
            sendSelectedValue=True,
            items=['automatic', 'manual'],
            orientation='horizontal',
            label="Mode:",
            callback=self.mode_changed,
            tooltip= "Choose mode",   
        )

        #-------------------------#
        #       Manual box        #
        #-------------------------#
        # manual box...
        self.manualBox = gui.widgetBox(
            widget=self.controlArea,
            box="Click to select a header to modify",
            orientation="vertical",
        )

        # List of all the headers (named with numbers if None)
        self.headerListbox = gui.listBox(
            widget=self.manualBox,
            master=self,
            value=None,
            labels=None,
            callback=None,
            selectionMode=1, # can only choose one item
            tooltip="List of all the headers you can rename and\
                change which one is the content",
        )

        # set "rename" button (must be aside the list)
        self.renameHeader = gui.button(
            widget=self.manualBox,
            master=self,
            label="rename",
            callback=None,
        )

        # set "use as content" button (must be aside the list)
        self.iscontentHeader = gui.button(
            widget=self.manualBox,
            master=self,
            label="use as content",
            callback=None,
        )

        gui.rubber(self.controlArea)

        # Now Info box and Send button must be drawn...
        self.sendButton.draw()
        self.infoBox.draw()

        self.mode_changed()

        self.infoBox.setText("Widget needs input", "warning")

        # Send data if autoSend.
        self.sendButton.sendIf()

        # adjust size
        # self.adjustSizeWithTimer()
        # QTimer.singleShot(0, self.sendButton.sendIf)
    
    def mode_changed(self):
        self.sendButton.settingsChanged()
        """Allows to update the interface depending on query mode"""
        if self.selected_mode == "automatic": # automatic selected
            # Hide manual options
            self.manualBox.setVisible(False)

        elif self.selected_mode == "manual": # manual selected
            # Show manual options
            self.manualBox.setVisible(True)

        return
                
    def inputData(self, newInput):
        """Process incoming data."""
        self.inputSeg = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()
  

    def sendData(self):
        """Compute result of widget processing and send to output"""
        
        # Check that there's an input...
        if self.inputSeg is None:
            self.infoBox.setText("Widget needs input", "warning")
            self.send("CSV Segmentation", None, self)
            return

        # Initialize progress bar.
        self.infoBox.setText(
            u"Processing, please wait...", 
            "warning",
        )
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=len(self.inputSeg))

        csvSeg = list()
        # Process each input segment...
        for segment in self.inputSeg:
        
            # Input segment attributes...
            inputContent = segment.get_content()
            inputAnnotations = segment.annotations
            inputStrIdx = segment.str_index
            inputStart = segment.start or 0
            inputEnd = segment.end or len(inputContent)
            #Call data processing
            csv_stream = io.StringIO(inputContent)
            dialect = sniffer.sniff(csv_stream.readline())
            csv_stream.seek(0)
            my_reader = csv.reader(csv_stream, dialect)
            # By default, content_column is set to 0. The content retrieved will be from the first column.
            # TODO: Maybe turn this into a setting?
            content_column = 0
            position = 0
            # Process each seg in inputContent
            for seg in inputContent:
            	segAnnotations = inputAnnotations.copy()
            		
            # This  will launch if sniffer detects a header in the content.
            if sniffer.has_header(inputContent) == True:
                # go back to the start otherwise we're going to start from the second row
                csv_stream.seek(0)
                # the header row is defined here.
                dict_keys = next(my_reader)
                for key in dict_keys:
                    position += len(key)
                for row in my_reader:
                    # Get old annotations in new dictionary
                    oldAnnotations = inputAnnotations.copy()
                    segAnnotations = dict()
                    for key in oldAnnotations.keys():
                        segAnnotations[key] = oldAnnotations[key]
                    # This is the main part where we transform our data into annotations.
                    for key in dict_keys:
                        segAnnotations["length"] = position
                        segAnnotations["row"] = str(row)
                        segAnnotations[key] = row[dict_keys.index(key)]
                        position += len(row[dict_keys.index(key)])
                        # By default, content_column is set to 0. The content retrieved will be from the first column.
                        content = segAnnotations[dict_keys[content_column]]
                    csvSeg.append(
                        Segment(
                            str_index = inputStrIdx,
                            start = position,
                            end = position + len(content),
                            annotations = segAnnotations
                            )
                        )

            progressBar.advance()

                 
        # Set status to OK and report data size...
        outputSeg = Segmentation(csvSeg)
        message = "%i segment@p sent to output." % len(outputSeg)
        message = pluralize(message, len(outputSeg))
        self.infoBox.setText(message)

        # Clear progress bar.
        progressBar.finish()
        self.controlArea.setDisabled(False)
        
        # Send data to output...
        self.send("CSV Segmentation", outputSeg, self)
        
        self.sendButton.resetSettingsChangedFlag()             

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
    from LTTL.Input import Input
    WidgetPreview(ExtractCSV).run(inputData=Input("a simple example"))
