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

import re
# Standard imports...
import time
import tempfile
import pdfplumber
import os
import requests
import LTTL.SegmenterThread as Segmenter

from functools import partial
from scidownl import scihub_download
from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget,
    InfoBox, SendButton, pluralize
)
from LTTL.Segmenter import tokenize
from LTTL.Segmentation import Segmentation
from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview
from LTTL.Input import Input
from Orange.widgets.settings import Setting
from PyQt5.QtWidgets import QMessageBox

class SciHubator(OWTextableBaseWidget):
    """
    Orange widget for importing and segmenting text from DOIs using Sci-Hub.

    Attributes :
        URLLabel (list) : List of labels for the DOIs.
        selectedURLLabel (list) : List of selected labels from the URL list.
        newDOI (str) : DOI entered by the user for addition.
        extractedText (str) : Extracted text from the downladed PDF
        DOI (str) : Single DOI value.
        DOIs (list) : List of DOIs added by the user
        createdInputs (list) : List of created LTTL.Inputs
    """

    #Version minimale

    # ----------------------------------------------------------------------
    # Widget's metadata...

    name = "Sci-Hubator"
    description = "Export a text segmentation from a DOI or URL"
    icon = "icons/scihubator.svg"
    priority = 10

    # ----------------------------------------------------------------------
    # Channel definitions (NB: no input in this case)...

    outputs = [('Segmentation', Segmentation)]

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
    """importAll = Setting(True)"""
    """importAbstract = Setting(False)"""
    """importText = Setting(False)"""
    """importBibliography = Setting(False)"""
    importAllorBib = Setting(0)

    def __init__(self):
        """
        Initializes the SciHubator widget, including the GUI components and settings
        """
        super().__init__()
        self.URLLabel = self.DOIs[:]
        print(self.URLLabel)
        self.selectedURLLabel = list()
        self.newDOI = u''
        self.extractedText = u''
        self.DOI = u''
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
                u"DOI appears in the same position as in the list.\n"
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
                u"Remove the selected DOI from the list."
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
                u"Successive DOIs must be separated with ' , '. \n"
                u"Their order in the list\n"
                u" will be the same as in this field."
            ),
        )
        advOptionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Options',
            orientation='vertical',
            addSpace=False,
        )
        gui.separator(widget=advOptionsBox, height=3)
        gui.radioButtonsInBox(
            widget=advOptionsBox,
            master=self,
            value='importAllorBib',
            btnLabels=['All in one Segment', 'Bibliography'],
            label=u'Choose what to import',
            callback=self.sendButton.settingsChanged,
            tooltips=["Import all article's content in one segment", "Import only bibliography (if found)"]
        )
        gui.separator(widget=addURLBox, height=3)
        self.addButton = gui.button(
            widget=addURLBox,
            master=self,
            label=u'Add',
            callback=self.add,
            tooltip=(
                u"Add the DOI(s) currently displayed in the 'DOI'\n"
                u"text field to the list."
            ),
            disabled = True,
        )
        gui.rubber(self.controlArea)
        self.URLLabel = self.URLLabel
        self.updateURLBoxButtons()
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()

    def sendData(self):
        """
        Trigger the data processing workflow from user-provided DOIs.

        This method:
            - Validates the presence of at least one DOI.
            - Displays a warning if no DOI is provided.
            - Clears any previously created inputs.
            - Updates the UI to indicate the start of preprocessing.
            - Launches the processing asynchronously using a background thread
        """
        # Verify checkboxes
        if not (self.importAll or self.importBibliography): #or self.importText
            self.infoBox.setText("Please select one or more checkboxes.", "warning")
            self.send("Segmentation", None)
            return
        # Verify DOIs
        if not self.DOIs:
            self.infoBox.setText("Please enter one or many valid DOIs.", "warning")
            self.send("Segmentation", None)
            return

        self.clearCreatedInputs()

        # Notify processing in infobox. Typically, there should
        # always be a "processing" step, with optional "pre-
        # processing" and "post-processing" steps before and
        # after it. If there are no optional steps, notify
        # "Preprocessing...".
        self.infoBox.setText(f"Step 1/3: Pre-processing...", "warning")

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
        """
        Download and process academic articles from DOIs using Sci-Hub.

        This method handles the full pipeline for downloading PDFs via Sci-Hub,
        extracting their text content, and converting them into LTTL-compatible
        input segmentations.

        Steps:
            1. Verifies Sci-Hub accessibility.
            2. Downloads PDFs for each DOI.
            3. Extracts text from each PDF using pdfplumber.
            4. Wraps extracted text into LTTL.Inputs with DOI annotations.
            5. Concatenates inputs if multiple DOIs are processed.

        Returns :
            Segmentation: A single or concatenated segmentation(s) ready for output.

        Raises:
            Emits error messages and halts processing if:
            - Sci-Hub is unreachable.
            - A download fails.
            - A PDF cannot be parsed.
        """

        # At start of processing, set progress bar to 1%.
        # Within this method, this is done using the following
        # instruction.
        self.signal_prog.emit(1, False)

        # DOIList.append(self.DOIContent)

        # Indicate the total number of iterations that the
        # progress bar will go through (e.g. number of input
        # segments, number of selected files, etc.), then
        # set current iteration to 1.
        max_itr = len(self.DOIs)
        cur_itr = 1

        # Permet de tester la connexion à Sci-Hub
        if not test_scihub_accessible():
            self.sendNoneToOutputs()
            self.infoBox.setText("SciHub inaccessible - verify your connexion", 'error')
            return
        # Actual processing...

        # For each progress bar iteration...
        tempdir = tempfile.TemporaryDirectory()
        for DOI in self.DOIs:

            # Update progress bar manually...
            self.signal_prog.emit(int(100 * cur_itr / max_itr), False)
            cur_itr += 1

            # code ajouté ici
            paper = DOI
            paper_type = "doi"
            out = f"{tempdir.name}/{self.DOIs.index(DOI)}"
            try:
                scihub_download(paper, paper_type=paper_type, out=out)
            except Exception as ex:
                print(ex)
                self.sendNoneToOutputs()
                self.infoBox.setText("An error occurred when downloading", 'error')
                return
            # Cancel operation if requested by user...
            time.sleep(0.00001)  # Needed somehow!
            if self.cancel_operation:
                self.signal_prog.emit(100, False)
                return

        # Update infobox and reset progress bar...
        self.signal_text.emit(f"Step 2/3: Processing...",
                              "warning")
        cur_itr = 0
        cur_itr_p3 = 0
        self.signal_prog.emit(0, True)
        empty_re = False
        for DOI in self.DOIs:
            DOIText = ""
            if os.path.exists(f"{tempdir.name}/{self.DOIs.index(DOI)}.pdf"):
                try:
                    with pdfplumber.open(f"{tempdir.name}/{self.DOIs.index(DOI)}.pdf") as pdf:
                        for page in pdf.pages:
                            self.signal_prog.emit(int(100 * cur_itr / max_itr), False)
                            cur_itr += (1 / len(pdf.pages))
                            DOIText += page.extract_text()
                except Exception as e:
                    self.sendNoneToOutputs()
                    self.infoBox.setText(f"Error occurred when reading PDF: {str(e)}", 'error')
                    return
            else:
                self.sendNoneToOutputs()
                self.infoBox.setText("Download failed. Please, verify DOI or connexion", 'error')
                return
            ########

            # Create an LTTL.Input...
            if len(self.DOIs) == 1:
                # self.captionTitle is the name of the widget,
                # which will become the label of the output
                # segmentation.
                label = self.captionTitle
            else:
                label = None  # will be set later.

            myInput = Input(DOIText, label)

            self.signal_text.emit("Step 3/3: Post-processing...",
                                  "warning")
            max_itr = (2*int(importAllorBib))
            if self.importAllorBib == 0:
                cur_itr_p3 += 1 * len(self.DOIs)
                # Extract the first (and single) segment in the
                # newly created LTTL.Input and annotate it with
                # the length of the input segmentation.
                segment = myInput[0]
                segment.annotations["DOI"] \
                    = DOI
                # For the annotation to be saved in the LTTL.Input,
                # the extracted and annotated segment must be re-assigned
                # to the first (and only) segment of the LTTL.Input.
                myInput[0] = segment
                # Add the  LTTL.Input to self.createdInputs.
                self.createdInputs.append(myInput)
            if self.importAllorBib == 1:
                cur_itr_p3 += 1 * len(self.DOIs)
                ma_regex = re.compile(r'(?<=\n)\n?(([Bb]iblio|[Rr][eé]f)\w*\W*\n)(.|\n)*')
                regexes = [(ma_regex, 'tokenize')]
                self.signal_prog.emit(int(100 * cur_itr_p3 / max_itr), False)
                new_segmentation = tokenize(myInput, regexes)
                if (len(new_segmentation) == 0):
                    empty_re = True
                    new_input = Input(f"Empty search Bib for DOI: {DOI}", "Empty Bibliography section")
                else:
                    new_input = Input(new_segmentation.to_string(), "Bibliographies")
                    segment = new_input[0]
                    segment.annotations["part"] = "Bibliography"
                    segment.annotations["DOI"] = DOI
                    new_input[0] = segment
                self.createdInputs.append(new_input)

            # Cancel operation if requested by user...
            time.sleep(0.00001)  # Needed somehow!
            if self.cancel_operation:
                self.signal_prog.emit(100, False)
                return
        tempdir.cleanup()


        # If there's only one LTTL.Input created, it is the
        # widget's output...
        print(empty_re)
        if empty_re:
            QMessageBox.warning(
                None, "SciHubator", "Not all sections were segmented",
                QMessageBox.Ok
            )
        if len(self.DOIs) == 1:
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
        """
        Handle the output after asynchronous DOI processing is complete.

        This method :
            - Retrieves the result of the processing task.
            - Calculates the number of segments and total characters.
            - Displays an informative message to the user.
            - Sends the processed data to the output.

        Args :
            f (Future): A Future object containing the result from `processData`.

        """

        # Get the result value of self.processData.
        processed_data = f.result()

        # If it is not None...
        if processed_data:
            message = f"{len(processed_data)} segment@p sent to output "
            message = pluralize(message, len(processed_data))
            self.infoBox.setText(message)
            self.send("Segmentation", processed_data)

    # The following method should be copied verbatim in
    # every Textable widget.
    def setCaption(self, title):
        """
        Set or update the widget's caption title.

        If the caption has changed, it triggers cancellation of ongoing tasks
        and marks the settings as changed to prompt UI updates.

        Args :
            title (str): The new caption/title to be displayed on the widget.
        """
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.cancel() # Cancel current operation
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)

    def clearAll(self):
        """
        Clear all stored DOIs and reset related UI elements.

        This method empties the DOI list and selection,
        disables the 'Clear All' button, and updates the interface state.
        """
        del self.DOIs[:]
        del self.selectedURLLabel[:]
        self.sendButton.settingsChanged()
        self.URLLabel = self.DOIs
        self.clearAllButton.setDisabled(True)
        self.removeButton.setDisabled(True)

    def remove(self):
        """
        Remove the selected DOI from the list.

        Removes the DOI corresponding to the currently selected index in the GUI,
        updates the list of DOIs and labels, and disables the clear button if the
        list is empty.
        """
        if self.selectedURLLabel:
            index = self.selectedURLLabel[0]
            self.DOIs.pop(index)
            del self.selectedURLLabel[:]
            self.sendButton.settingsChanged()
            self.URLLabel = self.URLLabel
        self.clearAllButton.setDisabled(not bool(self.URLLabel))

    def add(self):
        """
        Add new DOI(s) from the input field to the list.

        Parses the input string for comma-separated DOIs, adds them to the internal list,
        removes duplicates if any, updates the display labels, and enables relevant UI buttons.
        Shows a message box if duplicates are found and removed.
        """
        DOIList = [x.strip() for x in self.newDOI.strip().split(',')]
        print(DOIList)
        #--> Pas besoin de la boucle DOIList non?? <--
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

    def updateURLBoxButtons(self):
        """Update state of File box buttons"""
        self.addButton.setDisabled(not bool(self.newDOI))
        self.removeButton.setDisabled(not bool(self.selectedURLLabel))
        self.clearAllButton.setDisabled(not bool(self.URLLabel))


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
def test_scihub_accessible():
    """
    Test the internet connection and/or sci-hub's accessibility.
    """
    try:
        response = requests.get("https://sci-hub.se", timeout=10)
        return response.status_code == 200
    except:
        return False

if __name__ == '__main__':
        WidgetPreview(SciHubator).run()
