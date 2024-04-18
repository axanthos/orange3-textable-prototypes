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
    icon = "icons/mywidget.svg"
    priority = 1

    inputs = []
    outputs = []

    settingsHandler = VersionedSettingsHandler(
        version="0.0.1"
    )

    autoSend = settings.Setting(True)
    corpus = settings.Setting([])

    def __init__(self):
        super().__init__()

        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute="infoBox",
        )

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
