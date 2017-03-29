"""
Class TopicModels
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

__version__ = u"0.1.0"
__author__ = "Aris Xanthos"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"


import Orange.data
from Orange.widgets import widget, gui, settings

# import LTTL.Processor as Processor
import LTTL
from LTTL.Table import PivotCrosstab

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, # pluralize,
    InfoBox, SendButton
)


class TopicModels(OWTextableBaseWidget):
    """Textable widget for building topic models based on a term-document matrix
    """

    #----------------------------------------------------------------------
    # Widget"s metadata...

    name = "Topic Models"
    description = "Build topic models based on term-document matrices"
    icon = "icons/topic_models.svg"
    priority = 10

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = [("Textable Crosstab", LTTL.Table.PivotCrosstab, "input_data")]
    outputs = [
        ("Term-topic Textable table", LTTL.Table.PivotCrosstab, widget.Default),
        ("Document-topic Textable table", LTTL.Table.PivotCrosstab),
        ("Term-topic Orange table", Orange.data.Table, widget.Default),
        ("Document-topic Orange table", Orange.data.Table),        
    ]

    #----------------------------------------------------------------------
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    
    autoSend = settings.Setting(False)
    method = settings.Setting("Latent semantic indexing")
    numTopics = settings.Setting(10)

    want_main_area = False
    
    def __init__(self):
        """Widget creator."""
        super().__init__()

        # Other attributes...
        self.inputTable = None

        # Next two instructions are helpers from TextableUtils. Corresponding
        # interface elements are declared here and actually drawn below (at
        # their position in the UI)...
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.send_data,
            infoBoxAttribute="infoBox",
            sendIfPreCallback=self.updateGUI,
        )

        # User interface...

        # Filter box (advanced settings only)
        optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box="Options",
            orientation="vertical",
        )
        method_combo = gui.comboBox(
            widget=optionsBox,
            master=self,
            value="method",
            items=["Latent semantic indexing", "Latent Dirichlet allocation"],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Method:",
            labelWidth=120,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                "Please select the desired topic modelling method.\n"
            ),
        )
        method_combo.setMinimumWidth(120)
        gui.separator(widget=optionsBox, height=3)
        self.numTopics_spin = gui.spin(
            widget=optionsBox,
            master=self,
            value='numTopics',
            minv=1,
            maxv=999,
            orientation='horizontal',
            label=u'Number of topics:',
            labelWidth=120,
            callback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"Please select the desired number of topics in output tables."
            ),
        )
        gui.separator(widget=optionsBox, height=3)

        gui.separator(widget=self.controlArea, height=3)

        gui.rubber(self.controlArea)

        # Now Info box and Send button must be drawn...
        self.sendButton.draw()
        self.infoBox.draw()
        self.infoBox.setText("Widget needs input", "warning")
        
        # Send data if autoSend.
        self.sendButton.sendIf()

#        self.setMinimumWidth(350)
        self.adjustSizeWithTimer()

    def input_data(self, newInput):
        """Process incoming data."""
        self.inputTable = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def send_data(self):
        """Compute result of widget processing and send to output"""

        # Check that there's a table in input...
        if self.inputTable is None:
            self.infoBox.setText(
                "Widget needs input.", 
                "warning"
            )
            self.send("Term-topic Textable table", None)
            self.send("Document-topic Textable table", None)
            self.send("Term-topic Orange table", None)
            self.send("Document-topic Orange table", None)
            return

        # Initialize progress bar.
        progressBar = gui.ProgressBar(
            self, 
            iterations=1    # TODO
        )       
                
        # Set status to OK and report...
        self.infoBox.setText("Tables correctly NOT sent to output ;)")
        progressBar.finish()

        # Clear progress bar.
        progressBar.finish()
        
        # Send token... TODO
        # self.send("XML-TEI data", self.segmentation, self)
        self.sendButton.resetSettingsChangedFlag()        
        
    def updateGUI(self):
        """Update GUI state"""
        pass
            
            
if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication
    myApplication = QApplication(sys.argv)
    myWidget = TopicModels()
    myWidget.show()
    myApplication.exec_()
    myWidget.saveSettings()


