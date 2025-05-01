"""
Class SuperTextFiles
Copyright 2020-2025 University of Lausanne
-----------------------------------------------------------------------------
This file is part of the Orange3-Textable-Prototypes package and based on the
file OWTextableTextFiles of the Orange3-Textable package.

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
__author__ = "Sarah Perreti-Poix, Borgeaud Matthias, Chétioui Orsowen, Luginbühl Colin"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

# Standard imports...
import re
import http

from PyQt5.QtWidgets import QMessageBox
from scidownl import scihub_download
import pdfplumber
from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets.settings import Setting
from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, ProgressBar,
    JSONMessage, InfoBox, SendButton, AdvancedSettings,
    addSeparatorAfterDefaultEncodings, addAutoDetectEncoding,
    normalizeCarriageReturns, getPredefinedEncodings, pluralize
)
from LTTL.Segmentation import Segmentation



class SciHubator(OWTextableBaseWidget):
    """An Orange widget that lets the user select an integer value"""

    #Version minimale
    """
    basicURLBox = gui.widgetBox(
        widget=self.controlArea,
        box=u'Source',
        orientation='vertical',
        addSpace=False,
    )
    basicURLBoxLine1 = gui.widgetBox(
        widget=basicURLBox,
        box=False,
        orientation='horizontal',
    )
    gui.lineEdit(
        widget=basicURLBoxLine1,
        master=self,
        value='URL',
        orientation='horizontal',
        label=u'DOI:',
        labelWidth=101,
        callback=self.sendButton.settingsChanged,
        tooltip=(
            u"The URL whose content will be imported."
        ),
    )
    gui.rubber(self.controlArea)

    self.exportButton = gui.button(
        widget=URLBoxCol2,
        master=self,
        label=u'Export List',
        callback=self.exportList,
        tooltip=(
            u"Open a dialog for selecting a file where the URL\n"
            u"list can be exported in JSON format."
        ),
    )
    self.importButton = gui.button(
        widget=URLBoxCol2,
        master=self,
        label=u'Import List',
        callback=self.importList,
        tooltip=(
            u"Open a dialog for selecting an URL list to\n"
            u"import (in JSON format). DOIs from this list will\n"
            u"be added to those already imported."
        ),
    )
    """

    # ----------------------------------------------------------------------
    # Widget's metadata...

    name = "Sci-Hubator"
    description = "Export a text segmentation from a DOI or URL"
    icon = "icons/lexical_hunter.svg"
    priority = 10

    # ----------------------------------------------------------------------
    # Channel definitions (NB: no input in this case)...

    outputs = [('Text data', Segmentation)]

    # ----------------------------------------------------------------------
    # GUI layout parameters...

    want_main_area = False
    resizing_enabled = False

    # ----------------------------------------------------------------------
    # Settings declaration and initializations (default values)...

    DOIs = Setting([])
    encoding = Setting('(auto-detect)')
    autoNumber = Setting(False)
    autoNumberKey = Setting(u'num')
    autoSend = settings.Setting(False)
    importDOIs = Setting(True)
    importDOIsKey = Setting(u'url')
    lastLocation = Setting('.')
    DOI = Setting(u'')

    # Ici-dessous les variables qui n'ont pas été copiées, et conçues spécialement pour SciHubator
    importAll = Setting(True)
    importAbstract = Setting(False)
    importText = Setting(False)
    importBibliography = Setting(False)

    def __init__(self):
        super().__init__()
        self.URLLabel = list()
        self.selectedURLLabel = list()
        self.newDOI = u''
        self.extractedText = u''
        self.DOI = u''
        self.DOIs = list()
        self.createdInputs = list()

        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            cancelCallback=self.cancel_manually,
            infoBoxAttribute="infoBox",
        )
        # ----------------------------------------------------------------------
        # User interface...

        # ADVANCED GUI...

        # URL box
        URLBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Sources',
            orientation='vertical',
            addSpace=False,
        )
        URLBoxLine1 = gui.widgetBox(
            widget=URLBox,
            box=False,
            orientation='horizontal',
            addSpace=True,
        )
        self.fileListbox = gui.listBox(
            widget=URLBoxLine1,
            master=self,
            value='selectedURLLabel',
            labels='URLLabel',
            callback=self.updateURLBoxButtons,
            tooltip=(
                u"The list of DOIs whose content will be imported.\n"
                u"\nIn the output segmentation, the content of each\n"
                u"URL appears in the same position as in the list.\n"
                u"\nColumn 1 shows the URL.\n"
                u"Column 2 shows the associated annotation (if any).\n"
                u"Column 3 shows the associated encoding."
            ),
        )
        URLBoxCol2 = gui.widgetBox(
            widget=URLBoxLine1,
            orientation='vertical',
        )
        self.removeButton = gui.button(
            widget=URLBoxCol2,
            master=self,
            label=u'Remove',
            callback=self.remove,
            tooltip=(
                u"Remove the selected URL from the list."
            ),
            disabled = True,
        )
        self.clearAllButton = gui.button(
            widget=URLBoxCol2,
            master=self,
            label=u'Clear All',
            callback=self.clearAll,
            tooltip=(
                u"Remove all DOIs from the list."
            ),
            disabled = True,
        )
        URLBoxLine2 = gui.widgetBox(
            widget=URLBox,
            box=False,
            orientation='vertical',
        )
        # Add URL box
        addURLBox = gui.widgetBox(
            widget=URLBoxLine2,
            box=True,
            orientation='vertical',
            addSpace=False,
        )
        gui.lineEdit(
            widget=addURLBox,
            master=self,
            value='newDOI',
            orientation='horizontal',
            label=u'DOI(s):',
            labelWidth=101,
            callback=self.updateURLBoxButtons,
            tooltip=(
                u"The DOI(s) that will be added to the list when\n"
                u"button 'Add' is clicked.\n\n"
                u"Successive DOIs must be separated with ' / ' \n"
                u"(space + slash + space). Their order in the list\n"
                u" will be the same as in this field."
            ),
        )
        advOptionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Options',
            orientation='vertical',
            addSpace=False,
        )
        gui.checkBox(
            widget=advOptionsBox,
            master=self,
            value='importAll',
            label=u'All',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Import DOIs as annotations."
            ),
        )
        gui.separator(widget=advOptionsBox, height=3)
        gui.checkBox(
            widget=advOptionsBox,
            master=self,
            value='importAbstract',
            label=u'Abstract',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Import DOIs as annotations."
            ),
        )
        gui.separator(widget=advOptionsBox, height=3)
        gui.checkBox(
            widget=advOptionsBox,
            master=self,
            value='importText',
            label=u'Top Level Sections',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Import DOIs as annotations."
            ),
        )
        gui.separator(widget=advOptionsBox, height=3)
        gui.checkBox(
            widget=advOptionsBox,
            master=self,
            value='importBibliography',
            label=u'Bibliography',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Import DOIs as annotations."
            ),
        )
        gui.separator(widget=addURLBox, height=3)
        self.addButton = gui.button(
            widget=addURLBox,
            master=self,
            label=u'Add',
            callback=self.add,
            tooltip=(
                u"Add the URL currently displayed in the 'URL'\n"
                u"text field to the list."
            ),
            disabled = True,
        )
        gui.rubber(self.controlArea)
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()
    
    def sendData(self):
        """Perform every required check and operation 
        before calling the method that does the actual 
        processing.
        """
        # Verify DOIs
        if not self.DOIContent.strip():
            self.infoBox.setText("Please enter one or many valid DOIs.", "warning")
            self.send("New segmentation", None)
            return
        
        #DOIs' validation
        doi_list = [doi.strip() for doi in self.DOIContent.split(",") if doi.strip()]
        if not doi_list: 
            self.infoBox.setText("No valid DOI detected", "warning")
            self.send("New segmentation", None)
            return 

        # If the widget creates new LTTL.Input objects (i.e.
        # if it imports new strings in Textable), make sure to
        # clear previously created Inputs with this method.
        self.clearCreatedInputs()    

        # Notify processing in infobox. Typically, there should
        # always be a "processing" step, with optional "pre-
        # processing" and "post-processing" steps before and 
        # after it. If there are no optional steps, notify 
        # "Preprocessing...".
        self.infoBox.setText("Step 1/2: Processing...", "warning")

        # Progress bar should be initialized at this point.
        self.progressBarInit()

        # Create a threaded function to do the actual processing
        # and specify its arguments (here there are none).
        threaded_function = partial(
            self.processData,
            # argument1, 
            # argument2, 
            # ...
        )


        if self.DOI == "":
            # Use mode "warning" when user needs to do some
            # action or provide some information; use mode "error"
            # when invalid parameters have been provided; 
            # for notifications that don't require user action,
            # don't use a mode. Use formulations that emphasize
            # what should be done rather than what is wrong or
            # missing.
            self.infoBox.setText("Please type DOI.", 
                                 "warning")
            # Make sure to send None and return if the widget 
            # cannot operate properly at this point.
            self.send("New segmentation", None)
            return

        # If the widget creates new LTTL.Input objects (i.e.
        # if it imports new strings in Textable), make sure to
        # clear previously created Inputs with this method.
        self.clearCreatedInputs()

        # Notify processing in infobox. Typically, there should
        # always be a "processing" step, with optional "pre-
        # processing" and "post-processing" steps before and 
        # after it. If there are no optional steps, notify 
        # "Preprocessing...".
        self.infoBox.setText("Step 1/2: Processing...", "warning")
        
        # Progress bar should be initialized at this point.
        self.progressBarInit()

        # Create a threaded function to do the actual processing
        # and specify its arguments (here there are none).
        threaded_function = partial(
            self.processData,
            # argument1, 
            # argument2, 
            # ...
        )

        # Run the threaded function...
        self.threading(threaded_function)

    def processData(self):
            """Actual processing takes place in this method,
            which is run in a worker thread so that GUI stays
            responsive and operations can be cancelled
            """
            
            # At start of processing, set progress bar to 1%.
            # Within this method, this is done using the following
            # instruction.
            self.signal_prog.emit(1, False)

            DOIs.append(self.DOIContent)
            
            # Indicate the total number of iterations that the
            # progress bar will go through (e.g. number of input
            # segments, number of selected files, etc.), then
            # set current iteration to 1.
            max_itr = int(self.numberOfSegments)
            cur_itr = 1

            # Actual processing...
            
            # For each progress bar iteration...
            for _ in range(int(self.numberOfSegments)):

                # Update progress bar manually...
                self.signal_prog.emit(int(100*cur_itr/max_itr), False)
                cur_itr += 1
                
                # Create an LTTL.Input...           
                if int(self.numberOfSegments) == 1:
                    # self.captionTitle is the name of the widget,
                    # which will become the label of the output
                    # segmentation.
                    label = self.captionTitle
                else:
                    label = None # will be set later.
                myInput = Input(self.segmentContent, label)

                # Extract the first (and single) segment in the 
                # newly created LTTL.Input and annotate it with 
                # the length of the input segmentation. 
                segment = myInput[0]
                segment.annotations["demo_annotation"]  \
                    = self.inputSegmentationLength
                # For the annotation to be saved in the LTTL.Input, 
                # the extracted and annotated segment must be re-assigned
                # to the first (and only) segment of the LTTL.Input.
                myInput[0] = segment
                
                # Add the  LTTL.Input to self.createdInputs.
                self.createdInputs.append(myInput)
                
                # Cancel operation if requested by user...
                time.sleep(0.00001) # Needed somehow!
                if self.cancel_operation:
                    self.signal_prog.emit(100, False)
                    return            

            # Update infobox and reset progress bar...
            self.signal_text.emit("Step 2/2: Post-processing...", 
                                "warning")
            self.signal_prog.emit(1, True)

            # If there's only one LTTL.Input created, it is the 
            # widget's output...
            if int(self.numberOfSegments) == 1:
                return self.createdInputs[0]

            # Otherwise the widget's output is a concatenation...        
            else:
                return Segmenter.concatenate(
                    caller=self,
                    segmentations=self.createdInputs,
                    label=self.captionTitle,
                    import_labels_as=None,
                ) 

    @OWTextableBaseWidget.task_decorator
    def task_finished(self, f):
            """All operations following the successful termination
            of self.processData
            """
            
            # Get the result value of self.processData.
            processed_data = f.result()

            # If it is not None...
            if processed_data:
                message = f"{len(processed_data)} segment@p sent to output " 
                message = pluralize(message, len(processed_data))
                numChars = 0
                for segment in processed_data:
                    segmentLength = len(Segmentation.get_data(segment.str_index))
                    numChars += segmentLength
                message += f"({numChars} character@p)."
                message = pluralize(message, numChars)
                self.infoBox.setText(message)
                self.send("New segmentation", processed_data)

    # The following method should be copied verbatim in 
    # every Textable widget.
    def setCaption(self, title):
        """Register captionTitle changes and send if needed"""
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.cancel() # Cancel current operation
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)

    def clearAll(self):
        """Remove all DOIs from DOIs attr"""
        del self.DOIs[:]
        del self.selectedURLLabel[:]
        self.sendButton.settingsChanged()
        self.URLLabel = self.URLLabel
        self.clearAllButton.setDisabled(True)

    def remove(self):
        """Remove URL from DOIs attr"""
        if self.selectedURLLabel:
            index = self.selectedURLLabel[0]
            self.DOIs.pop(index)
            del self.selectedURLLabel[:]
            self.sendButton.settingsChanged()
            self.URLLabel = self.URLLabel
        self.clearAllButton.setDisabled(not bool(self.URLLabel))

    def add(self):
        """Add DOIs to DOIs attr"""
        DOIList = re.split(r',', self.newDOI)
        print(DOIList)
        for DOI in DOIList:
            print(DOI)
            self.DOIs.append(DOI)
        if self.DOIs:
            tempSet = set(self.DOIs)
            if(len(tempSet)<len(self.DOIs)):
                QMessageBox.information(
                    None, "SciHubator", "Duplicate DOI(s) found and deleted.",
                    QMessageBox.Ok
                )
            self.DOIs = list(tempSet)
            self.URLLabel = self.DOIs
        self.URLLabel = self.URLLabel
        self.clearAllButton.setDisabled(not bool(self.DOIs))
        self.sendButton.settingsChanged()

    # def updateGUI(self):
    #     """Update GUI state"""
    #     # if self.selectedURLLabel:
    #     #     cachedLabel = self.selectedURLLabel[0]
    #     # else:
    #     #     cachedLabel = None
    #     del self.URLLabel[:]
    #     if self.DOIs:
    #         DOIs = [f for f in self.DOIs]
    #         self.URLLabel = DOIs
    #         # maxURLLen = max([len(n) for n in DOIs])
    #         # for DOI in DOIs:    #range(len(self.DOIs)):
    #             # format = u'%-' + str(maxURLLen + 2) + u's'
    #             #format % DOIs[index]
    #             # self.URLLabel.append(DOI)
    #     self.URLLabel = self.URLLabel
    #     # if cachedLabel is not None:
    #     #     self.sendButton.sendIfPreCallback = None
    #     #     self.selectedURLLabel = [cachedLabel]
    #     #     self.sendButton.sendIfPreCallback = self.updateGUI
    #     if self.newDOI:
    #         self.addButton.setDisabled(False)
    #     else:
    #         self.addButton.setDisabled(True)
    #     # if self.importDOIs:
    #     #     self.importDOIsKeyLineEdit.setDisabled(False)
    #     # else:
    #     #     self.importDOIsKeyLineEdit.setDisabled(True)
    #     self.updateURLBoxButtons()

    def updateURLBoxButtons(self):
        """Update state of File box buttons"""
        self.addButton.setDisabled(not bool(self.newDOI))
        self.removeButton.setDisabled(not bool(self.selectedURLLabel))


    # The following two methods should be copied verbatim in 
    # every Textable widget that creates LTTL.Input objects.

    def clearCreatedInputs(self):
        """Clear created inputs"""
        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]

    def onDeleteWidget(self):
        """Clear created inputs on widget deletion"""
        self.clearCreatedInputs()

if __name__ == '__main__':
        WidgetPreview(SciHubator).run()

    
    # def clearAll(self):
    #     """Remove all DOIs from DOIs attr"""
    #     del self.DOIs[:]
    #     del self.selectedURLLabel[:]
    #     self.sendButton.settingsChanged()

    # def remove(self):
    #     """Remove URL from DOIs attr"""
    #     if self.selectedURLLabel:
    #         index = self.selectedURLLabel[0]
    #         self.DOIs.pop(index)
    #         del self.selectedURLLabel[:]
    #         self.sendButton.settingsChanged()

    # def add(self):
    #     """Add DOIs to DOIs attr"""
    #     URLList = re.split(r' +/ +', self.newURL)
    #     for URL in URLList:
    #         encoding = re.sub(r"[ ]\(.+", "", self.encoding)
    #         self.DOIs.append((
    #             URL,
    #             encoding,
    #             self.newAnnotationKey,
    #             self.newAnnotationValue,
    #         ))
    #     self.sendButton.settingsChanged()
    # def updateGUI(self):
    #     """Update GUI state"""
    #     if self.displayAdvancedSettings:
    #         if self.selectedURLLabel:
    #             cachedLabel = self.selectedURLLabel[0]
    #         else:
    #             cachedLabel = None
    #         del self.URLLabel[:]
    #         if self.DOIs:
    #             DOIs = [f[0] for f in self.DOIs]
    #             encodings = [f[1] for f in self.DOIs]
    #             annotations = ['{%s: %s}' % (f[2], f[3]) for f in self.DOIs]
    #             maxURLLen = max([len(n) for n in DOIs])
    #             maxAnnoLen = max([len(a) for a in annotations])
    #             for index in range(len(self.DOIs)):
    #                 format = u'%-' + str(maxURLLen + 2) + u's'
    #                 URLLabel = format % DOIs[index]
    #                 if maxAnnoLen > 4:
    #                     if len(annotations[index]) > 4:
    #                         format = u'%-' + str(maxAnnoLen + 2) + u's'
    #                         URLLabel += format % annotations[index]
    #                     else:
    #                         URLLabel += u' ' * (maxAnnoLen + 2)
    #                 URLLabel += encodings[index]
    #                 self.URLLabel.append(URLLabel)
    #         self.URLLabel = self.URLLabel
    #         if cachedLabel is not None:
    #             self.sendButton.sendIfPreCallback = None
    #             self.selectedURLLabel = [cachedLabel]
    #             self.sendButton.sendIfPreCallback = self.updateGUI
    #         if self.newURL:
    #             if (
    #                 (self.newAnnotationKey and self.newAnnotationValue) or
    #                 (not self.newAnnotationKey and not self.newAnnotationValue)
    #             ):
    #                 self.addButton.setDisabled(False)
    #             else:
    #                 self.addButton.setDisabled(True)
    #         else:
    #             self.addButton.setDisabled(True)
    #         if self.autoNumber:
    #             self.autoNumberKeyLineEdit.setDisabled(False)
    #         else:
    #             self.autoNumberKeyLineEdit.setDisabled(True)
    #         if self.importDOIs:
    #             self.importDOIsKeyLineEdit.setDisabled(False)
    #         else:
    #             self.importDOIsKeyLineEdit.setDisabled(True)
    #         self.updateURLBoxButtons()
    #         self.advancedSettings.setVisible(True)
    #     else:
    #         self.advancedSettings.setVisible(False)

    # def updateURLBoxButtons(self):
    #     """Update state of File box buttons"""
    #     if self.selectedURLLabel:
    #         self.removeButton.setDisabled(False)
    #         if self.selectedURLLabel[0] > 0:
    #             self.moveUpButton.setDisabled(False)
    #         else:
    #             self.moveUpButton.setDisabled(True)
    #         if self.selectedURLLabel[0] < len(self.DOIs) - 1:
    #             self.moveDownButton.setDisabled(False)
    #         else:
    #             self.moveDownButton.setDisabled(True)
    #     else:
    #         self.moveUpButton.setDisabled(True)
    #         self.moveDownButton.setDisabled(True)
    #         self.removeButton.setDisabled(True)
    #     if len(self.DOIs):
    #         self.clearAllButton.setDisabled(False)
    #         self.exportButton.setDisabled(False)
    #     else:
    #         self.clearAllButton.setDisabled(True)
    #         self.exportButton.setDisabled(True)

# def checkIfDOI(string):
#     regex = re.compile(r'\d{2}\.\d{4}.+')