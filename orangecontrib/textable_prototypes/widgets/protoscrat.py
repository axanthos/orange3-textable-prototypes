from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler,
    InfoBox, SendButton,
)

from LTTL.Segmentation import Segmentation

class Protoscrat(OWTextableBaseWidget):
    """Button"""

    name = "Scratodon"
    description = "Button test"
    icon = "icons/Scratodon_logo_dark.png"
    priority = 1

    inputs = []
    outputs = []

    settingsHandler = VersionedSettingsHandler(
        version="0.0.1"
    )

    autoSend = settings.Setting(True)
    corpus = settings.Setting([])
    want_main_area = False
    UserID=""

    def __init__(self):
        super().__init__()

        


        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute="infoBox",
        )


        self.infoBox = InfoBox(widget=self.controlArea)
        gui.separator(self.controlArea, height=3)

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
            value='UserID',
            orientation='horizontal',
            label=u'User ID:',
            labelWidth=101,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The URL whose content will be imported."
            ),
        )
        gui.separator(widget=basicURLBox, height=3)

        
      
        gui.rubber(self.controlArea)

        self.sendButton.draw()
        self.infoBox.draw()




    def sendData(self):
        if self.corpus == list():
            self.infoBox.setText(
                "Your corpus is empty, please add datas first",
                "Warning"
            )
            return

        self.controlArea.setDisabled(True)

        self.infoBox.setText("Sending data...")

        self.send("Datas importation", None, self)

        self.controlArea.setDisabled(False)
        self.infoBox.setText("Data sent successfully.")

if __name__ == "__main__":
    WidgetPreview(Protoscrat).run()