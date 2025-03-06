# Standard imports...
import re
import http
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

__version__ = "0.01"


class SciHubator(widget.OWWidget):
    """An Orange widget that lets the user select an integer value"""

    # ----------------------------------------------------------------------
    # Widget's metadata...

    name = "Sci-Hubator"
    description = "Export a text segmentation from a DOI or URL"
    icon = "icons/lexical_hunter.svg"
    priority = 10

    # ----------------------------------------------------------------------
    # Channel definitions (NB: no input in this case)...

    inputs = []
    outputs = [('Text data', Segmentation)]

    # ----------------------------------------------------------------------
    # GUI layout parameters...

    want_main_area = False
    resizing_enabled = False

    # ----------------------------------------------------------------------
    # Settings declaration and initializations (default values)...

    URLs = Setting([])
    encoding = Setting('(auto-detect)')
    autoNumber = Setting(False)
    autoNumberKey = Setting(u'num')
    autoSend = settings.Setting(False)
    importURLs = Setting(True)
    importURLsKey = Setting(u'url')
    lastLocation = Setting('.')
    displayAdvancedSettings = Setting(False)
    URL = Setting(u'')
    selected_int = Setting(50)

    # Ici-dessous les variables qui n'ont pas été copiées, et conçues spécialement pour SciHubator
    importAll = Setting(True)
    importAbstract = Setting(False)
    importText = Setting(False)
    importBibliography = Setting(False)

    def __init__(self):
        super().__init__()

        self.advancedSettings = AdvancedSettings(
            widget=self.controlArea,
            master=self,
            callback=self.int_changed,
        )
        self.advancedSettings.draw()

        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.int_changed,
            infoBoxAttribute='infoBox',
            sendIfPreCallback=self.int_changed,
        )
        # ----------------------------------------------------------------------
        # User interface...

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
            label=u'DOI/URL:',
            labelWidth=101,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The URL whose content will be imported."
            ),
        )
        gui.separator(widget=basicURLBox, height=3)
        optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Options',
            orientation='vertical',
            addSpace=False,
        )
        gui.checkBox(
            widget=optionsBox,
            master=self,
            value='importAll',
            label=u'All',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Import URLs as annotations."
            ),
        )
        iBox = gui.indentedBox(
            widget=optionsBox,
        )
        gui.separator(widget=optionsBox, height=3)
        gui.checkBox(
            widget=iBox,
            master=self,
            value='importAbstract',
            label=u'Abstract',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Import URLs as annotations."
            ),
        )
        gui.separator(widget=optionsBox, height=3)
        gui.checkBox(
            widget=iBox,
            master=self,
            value='importText',
            label=u'Text',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Import URLs as annotations."
            ),
        )
        gui.separator(widget=optionsBox, height=3)
        gui.checkBox(
            widget=iBox,
            master=self,
            value='importBibliography',
            label=u'Bibliography',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Import URLs as annotations."
            ),
        )
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()

    def int_changed(self):
        """Send the entered number on "Number" output"""
        self.send("Text data", None)
