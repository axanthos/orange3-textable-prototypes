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
    
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    
    autoSend = settings.Setting(False)

    content_column = settings.Setting(0)
    headerEdit = settings.Setting("")
    deleteQuotes = settings.Setting(False)

    def __init__(self):
        """Widget creator."""

        super().__init__()

        # Other attributes...

        self.inputSeg = None
        self.outputSeg = None
        self.dialect = None
        self.selectedHeader = None
        self.csvSeg = list()
        # list of deleted segments
        self.contentIsNone = list()
        # list for gui
        self.headerList = list()
        self.content_column = 0
        self.headerEdit = ""

        # those are for the rename function
        self.renamedHeader = None
        self.isRenamed = False
        self.dict_keys = list()

        # preprocess
        self.deleteQuotes = False

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
        #self.header_there = False

        #----------------------------------------------------------------------
        # User interface...

        # preprocess box...
        self.preprocessBox = gui.widgetBox(
            widget=self.controlArea,
            box="Preprocess",
            orientation="vertical",
        )
        # check box...
        self.checkQuotes = gui.checkBox(
            widget=self.preprocessBox,
            master=self,
            value='deleteQuotes',
            label='delete quotation marks',
            callback=self.delete_quotes,
        )

        # main box...
        self.mainBox = gui.widgetBox(
            widget=self.controlArea,
            box="Click to select a header to modify",
            orientation="vertical",
        )

        # List of all the headers (named with numbers if None)
        self.headerListbox = gui.listBox(
            widget=self.mainBox,
            master=self,
            value="selectedHeader",
            labels="headerList",
            callback=self.update_gui,
            selectionMode=1, # can only choose one item
            tooltip="list of all your headers",
        )

        # set "rename" button (must be aside the list)
        self.renameHeader = gui.button(
            widget=self.mainBox,
            master=self,
            label="rename",
            callback=self.set_renamebox,
            tooltip="click to rename header"
        )

        # set "use as content" button (must be aside the list)
        self.iscontentHeader = gui.button(
            widget=self.mainBox,
            master=self,
            label="use as content",
            callback=self.content_changed,
            tooltip="click to select as content"
        )

        #----------------------------------------------------------------------
        # rename box...

        self.renameBox = gui.widgetBox(
            widget=self.controlArea,
            box='Rename header',
            orientation='horizontal',
            addSpace=True,
        )
        gui.separator(widget=self.renameBox, height=3)
        self.headerEditLine = gui.lineEdit(
            widget=self.renameBox,
            master=self,
            value='headerEdit',
            orientation='horizontal',
            label='New header:',
            tooltip=(
                "Rename the selected header."
            )
        )
        self.renameButton = gui.button(
            widget=self.renameBox,
            master=self,
            label="rename",
            callback=self.rename,
            tooltip="click to rename header"
        )
        self.cancelButton = gui.button(
            widget=self.renameBox,
            master=self,
            label="cancel",
            callback=self.cancel,
            tooltip="click to cancel renaming"
        )
        #----------------------------------------------------------------------
        # interface parameters...

        self.update_gui()
        self.renameBox.setVisible(False)

        gui.rubber(self.controlArea)

        # Now Info box and Send button must be drawn...
        self.sendButton.draw()
        self.infoBox.draw()
        #self.set_renamebox()
        self.infoBox.setText("Widget needs input", "warning")
        
        # Send data if autoSend.
        self.sendButton.sendIf()

    #----------------------------------------------------------------------

    def update_gui(self):
        if len(self.selectedHeader)==0:
            self.iscontentHeader.setDisabled(True)
            self.renameHeader.setDisabled(True)
        else:
            self.iscontentHeader.setDisabled(False)
            self.renameHeader.setDisabled(False)

    def content_changed(self):
        self.content_column = int(self.selectedHeader[0])
        self.treat_input()
        return

    def delete_quotes(self):
        self.treat_input()

    def set_renamebox(self):
        # take selectedHeader
        self.renamedHeader = int(self.selectedHeader[0])
        # appear rename gui
        self.renameBox.setVisible(True)
        # disable other
        self.iscontentHeader.setDisabled(True)
        self.renameHeader.setDisabled(True)
        self.headerListbox.setDisabled(True)
        self.checkQuotes.setDisabled(True)

    def rename(self):
        # rename
        for key in self.dict_keys:
            # change my header name
            if self.dict_keys.index(key) == self.renamedHeader:
                self.dict_keys[self.dict_keys.index(key)] = self.headerEdit
        # implement check value
        self.isRenamed = True
        # and treat again
        self.treat_input()

        # here we get back to normal gui
        self.renameBox.setVisible(False)
        self.headerListbox.setDisabled(False)
        self.checkQuotes.setDisabled(False)
        self.update_gui()
        # clear value
        self.headerEdit = ""

    def cancel(self):
        # here we get back to normal gui
        self.renameBox.setVisible(False)
        self.headerListbox.setDisabled(False)
        self.update_gui()
        # clear value
        self.headerEdit = ""

    def treat_input(self):
        # Check that there's an input...
        if self.inputSeg is None:
            self.infoBox.setText("Widget needs input", "warning")
            del self.headerList[:]
            self.headerList = self.headerList
            return

        # Initialize progress bar.
        self.infoBox.setText(
            u"Processing, please wait...", 
            "warning",
        )
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=len(self.inputSeg))

        # clear lists
        del self.csvSeg[:]
        del self.contentIsNone[:]

        # Process each input segment...
        for segment in self.inputSeg:
        
            # Input segment attributes...
            inputContent = segment.get_content()
            if not self.deleteQuotes == False :
                inputContent = inputContent.replace('"',"")
            inputAnnotations = segment.annotations
            inputStrIdx = segment.str_index
            inputStart = segment.start or 0
            inputEnd = segment.end or len(inputContent)
            #Call data processing
            csv_stream = io.StringIO(inputContent)
            dialect = sniffer.sniff(csv_stream.readline())
            dialect.quoting=csv.QUOTE_NONE
            csv_stream.seek(0)
            my_reader = csv.reader(csv_stream, dialect)
            position = 0
            # Process each seg in inputContent
            for seg in inputContent:
                segAnnotations = inputAnnotations.copy()
            # This  will launch if sniffer detects a header in the content.
            if sniffer.has_header(inputContent) == True:
                # go back to the start otherwise we're going to start from the
                # second row
                csv_stream.seek(0)
                # the header row is defined here.
                if self.isRenamed == False :
                    self.dict_keys = next(my_reader)
                    for key in self.dict_keys:
                    # this is position of first content
                    # TODO : separator length (if not 1)
                        position += (len(key) + 1)
                else :
                    input_keys = next(my_reader)
                    for key in input_keys:
                    # this is position of first content
                    # TODO : separator length (if not 1)
                        position += (len(key) + 1)


            # This will launch if sniffer does not detect a header 
            # in the content.
            if sniffer.has_header(inputContent) == False:
                # go back to the start otherwise we're going to start from the
                # second row. we do this here even though we don't really care
                # about the first row simply because in general we consider the
                # first row to not have any missing values
                csv_stream.seek(0)
                first_row = next(my_reader)
                n_cols = len(first_row)
                if self.isRenamed == False :
                    self.dict_keys = list()
                    for item in range(1, n_cols+1):
                        self.dict_keys.append(str(item))
                csv_stream.seek(0)


            # clear the list before appending
            del self.headerList[:]

            for key in self.dict_keys:
                # appends the headers to the gui list
                if self.dict_keys.index(key) == self.content_column:
                    self.headerList.append(str(key)+"(*content)")
                    self.headerList = self.headerList
                else :
                    self.headerList.append(str(key))
                    self.headerList = self.headerList


            for idx, row in enumerate(my_reader, start=2):
                # Get old annotations in new dictionary
                oldAnnotations = inputAnnotations.copy()
                segAnnotations = dict()
                # initiate next row starting position
                next_position = position
                for key in oldAnnotations.keys():
                    segAnnotations[key] = oldAnnotations[key]

                # This is the main part where we transform our data into
                # annotations.
                for key in self.dict_keys:
                    # segAnnotations["length"] = position
                    # segAnnotations["row"] = str(row)

                    # if column is content (first column (0) by default)
                    if self.dict_keys.index(key) == self.content_column:
                        # put value as content
                        content = row[self.dict_keys.index(key)]
                    # else we put value in annotation
                    else:
                        # only if value is not None
                        if len(row[self.dict_keys.index(key)]) != 0 :
                            segAnnotations[key] = row[self.dict_keys.index(key)]
                    # implement position and next_position depending on
                    # content column
                    if self.dict_keys.index(key) < self.content_column:
                        position += len(row[self.dict_keys.index(key)]) + 1
                        next_position += len(row[self.dict_keys.index(key)]) + 1
                    if self.dict_keys.index(key) >= self.content_column:
                        next_position += len(row[self.dict_keys.index(key)]) + 1

                if len(content) != 0:
                    self.csvSeg.append(
                        Segment(
                            str_index = inputStrIdx,
                            start = position,
                            end = position + len(content),
                            annotations = segAnnotations
                            )
                        )

                else :
                    # if no content, add idx of the row and do not append
                    # TODO : something with contentIsNone
                    self.contentIsNone.append(idx)

                # initiate new row starting position
                position = next_position
                        
            progressBar.advance()

        unSeg = len(self.csvSeg)         
        # Set status to OK and report segment analyzed...
        if len(self.contentIsNone) == 0 :
            message = "%i segment@p analyzed." % unSeg
            message = pluralize(message, unSeg)
            self.infoBox.setText(message)
        # message if one or more segments has no content and has been ignored
        elif len(self.contentIsNone) == 1 :
            message = "%i segment@p analyzed. (ignored %i segment with \
            no content)" % (unSeg, len(self.contentIsNone))
            message = pluralize(message, unSeg)
            self.infoBox.setText(message)
        else :
            message = "%i segment@p analyzed. (ignored %i segments with \
            no content)" % (unSeg, len(self.contentIsNone))
            message = pluralize(message, unSeg)
            self.infoBox.setText(message)


        # Clear progress bar.
        progressBar.finish()
        self.controlArea.setDisabled(False)

        self.sendButton.resetSettingsChangedFlag()
        self.sendButton.sendIf()

    def inputData(self, newInput):
        """Process incoming data."""
        self.inputSeg = newInput
        self.infoBox.inputChanged()

        del self.dict_keys[:]
        self.isRenamed = False

        self.sendButton.sendIf()

        self.treat_input()

    def sendData(self):
        """Compute result of widget processing and send to output"""
        
        # Check that there's an input...
        if self.inputSeg is None:
            self.infoBox.setText("Widget needs input", "warning")
            del self.headerList[:]
            self.headerList = self.headerList
            self.send("CSV Segmentation", None, self)
            return

        # Initialize progress bar.
        self.infoBox.setText(
            u"Processing, please wait...", 
            "warning",
        )
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(self, iterations=len(self.inputSeg))


        # Treat...
        for segment in self.csvSeg:
            
            pass
                        
            progressBar.advance()

                 
        # Set status to OK and report data size...
        outputSeg = Segmentation(self.csvSeg, label=self.captionTitle)
        if len(self.contentIsNone) == 0 :
            message = "%i segment@p sent to output." % len(outputSeg)
            message = pluralize(message, len(outputSeg))
            self.infoBox.setText(message)
        # message if one or more segments has no content and has been ignored
        elif len(self.contentIsNone) == 1:
            message = "%i segment@p sent to output. (ignored %i segment with \
            no content)" % (len(outputSeg), len(self.contentIsNone))
            message = pluralize(message, len(outputSeg))
            self.infoBox.setText(message)
        else :
            message = "%i segment@p sent to output. (ignored %i segments with \
            no content)" % (len(outputSeg), len(self.contentIsNone))
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