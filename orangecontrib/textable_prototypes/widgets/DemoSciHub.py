"""
Class DemoTextableWidget
Copyright 2025 University of Lausanne
-----------------------------------------------------------------------------
This file is part of the Orange3-Textable-Prototypes package.

Orange3-Textable-Prototypes is free software: you can redistribute 
it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

Orange3-Textable-Prototypes is distributed in the hope that it will 
be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Orange3-Textable-Prototypes. If not, see
 <http://www.gnu.org/licenses/>.
"""

__version__ = u"0.0.1"
__author__ = "Sarah Perreti-Poix, Borgeaud Matthias, Chétioui Orsowen, Luginbühl Colin"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"


from functools import partial
import time
from scidownl import scihub_download
import tempfile
import pdfplumber
import os
import requests

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, ProgressBar,
    InfoBox, SendButton, pluralize, Task
)

from LTTL.Segmentation import Segmentation
#from LTTL.Input import Input

# Using the threaded version of LTTL.Segmenter to create
# a "responsive" widget.
import LTTL.SegmenterThread as Segmenter

from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview
from LTTL.Input import Input


class DemoSciHUB(OWTextableBaseWidget):
    """Demo Orange3-Textable widget"""

    name = "Demo Scihub"
    description = "Export a text segmentation from a DOI or URL"
    icon = "icons/someIcon.svg"
    priority = 99

    # Input and output channels (remove if not needed)...
    #inputs = [("Segmentation", Segmentation, "inputData")]
    outputs = [("New segmentation", Segmentation)]

    # Copied verbatim in every Textable widget to facilitate 
    # settings management.
    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    # Settings...
    DOIContent = settings.Setting("")
    #numberOfSegments = settings.Setting("10")

    want_main_area = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inputSegmentationLength = 0
        # The following attribute is required by every widget
        # that imports new strings into Textable.
        self.createdInputs = list()

        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            cancelCallback=self.cancel_manually,
            infoBoxAttribute="infoBox",
        )

        # GUI...
        # Top-level GUI boxes are created using method
        # create_widgetbox(), so that they are automatically
        # enabled/disabled when processes are running.
        sourceBox = self.create_widgetbox(
            box=u'Options',
            orientation='vertical',
            addSpace=False,
        )

        # GUI elements can be assigned to variables or even
        # attributes (e.g. self.DOIContentLineEdit) if
        # they must be referred to elsewhere, e.g., to enable
        # or disable them, etc. It is not the case below.
        gui.lineEdit(
            widget=sourceBox,
            master=self,
            value="DOIContent",
            orientation="horizontal",
            label="DOI:",
            labelWidth=130,
            # self.sendButton.settingsChanged should be used in 
            # in cases where using a GUI element should result
            # in sending data to output. If it should result in
            # other operations being done, use a custom method 
            # instead, and at the end of it, if data should be
            # sent to output, call self.sendButton.settingsChanged(). 
            # If using the GUI element should not result in   
            # anything at that moment, delete the "callback" 
            # parameter.
            callback=self.sendButton.settingsChanged,
            tooltip=(
                "A string that defines the content "
                "each segment."
            ),
        )

        # Stretchable vertical spacing between "options"
        # and Send button etc.
        gui.rubber(self.controlArea)

        # Draw send button & Info box...
        self.sendButton.draw()
        self.infoBox.draw()
        
        # Send data if needed. 
        self.sendButton.settingsChanged()

    def sendData(self):
        """Perform every required check and operation 
        before calling the method that does the actual 
        processing.
        """

        if self.DOIContent == "":
            # Use mode "warning" when user needs to do some
            # action or provide some information; use mode "error"
            # when invalid parameters have been provided; 
            # for notifications that don't require user action,
            # don't use a mode. Use formulations that emphasize
            # what should be done rather than what is wrong or
            # missing.
            self.infoBox.setText("Please type valid DOI.",
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

        DOIList = self.DOIContent.split(",")
        #DOIList.append(self.DOIContent)
        
        # Indicate the total number of iterations that the
        # progress bar will go through (e.g. number of input
        # segments, number of selected files, etc.), then
        # set current iteration to 1.
        max_itr = len(DOIList)
        cur_itr = 1

        # Permet de tester la connexion à Sci-Hub
        if not test_scihub_accessible():
            self.sendNoneToOutputs()
            self.infoBox.setText("SciHub inaccessible - verify your connexion", 'error')
            return
        # Actual processing...

        # For each progress bar iteration...
        tempdir = tempfile.TemporaryDirectory()
        for DOI in DOIList:

            # Update progress bar manually...
            self.signal_prog.emit(int(100*cur_itr/max_itr), False)
            cur_itr += 1

            # code ajouté ici
            paper = DOI
            paper_type = "doi"
            out = f"{tempdir.name}/{DOIList.index(DOI)}"
            try:
                scihub_download(paper, paper_type=paper_type, out=out)
            except Exception as ex:
                print(ex)
                self.sendNoneToOutputs()
                self.infoBox.setText(ex, 'error')

        # Update infobox and reset progress bar...
        self.signal_text.emit("Step 2/2: Post-processing...", 
                              "warning")
        cur_itr = 0
        self.signal_prog.emit(0, True)
        for DOI in DOIList:
            DOIText = ""
            if os.path.exists(f"{tempdir.name}/{DOIList.index(DOI)}.pdf"):
                try:
                    with pdfplumber.open(f"{tempdir.name}/{DOIList.index(DOI)}.pdf") as pdf:
                        for page in pdf.pages:
                            self.signal_prog.emit(int(100 * cur_itr / max_itr), False)
                            cur_itr += (1 / len(pdf.pages))
                            DOIText += page.extract_text()
                except Exception as e:
                    self.sendNoneToOutputs()
                    self.infoBox.setText(f"Error occurred when reading PDF: {str(e)}", 'error')
                    return
            else:
                print("Bonjour")
                self.sendNoneToOutputs()
                self.infoBox.setText("Download failed. Please, verify DOI or connexion", 'error')
                return
            ########

            # Create an LTTL.Input...
            if len(DOIList) == 1:
                # self.captionTitle is the name of the widget,
                # which will become the label of the output
                # segmentation.
                label = self.captionTitle
            else:
                label = None  # will be set later.
            print(DOIText)
            myInput = Input(DOIText, label)

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

            # Cancel operation if requested by user...
            time.sleep(0.00001)  # Needed somehow!
            if self.cancel_operation:
                self.signal_prog.emit(100, False)
                return
        tempdir.cleanup()


        # If there's only one LTTL.Input created, it is the 
        # widget's output...
        if len(DOIList) == 1:
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
            message = "text sent to output "
            message = pluralize(message, len(processed_data))
            """numChars = 0
            for segment in processed_data:
                segmentLength = len(Segmentation.get_data(segment.str_index))
                numChars += segmentLength
            message += f"({numChars} character@p)."
            message = pluralize(message, numChars)"""
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
    try:
        response = requests.get("https://sci-hub.se", timeout=10)
        return response.status_code == 200
    except:
        return False

if __name__ == '__main__':
        WidgetPreview(DemoSciHub).run()
