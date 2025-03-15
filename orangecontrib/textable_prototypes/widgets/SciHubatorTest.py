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
            u"import (in JSON format). URLs from this list will\n"
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
    URL = Setting(u'')
    selected_int = Setting(50)

    # Ici-dessous les variables qui n'ont pas été copiées, et conçues spécialement pour SciHubator
    importAll = Setting(True)
    importAbstract = Setting(False)
    importText = Setting(False)
    importBibliography = Setting(False)

    def __init__(self):
        super().__init__()
        self.URLLabel = list()
        self.selectedURLLabel = list()
        self.newURL = u''
        self.newAnnotationKey = u''
        self.newAnnotationValue = u''

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
                u"The list of URLs whose content will be imported.\n"
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
        )
        self.clearAllButton = gui.button(
            widget=URLBoxCol2,
            master=self,
            label=u'Clear All',
            callback=self.clearAll,
            tooltip=(
                u"Remove all URLs from the list."
            ),
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
            value='newURL',
            orientation='horizontal',
            label=u'DOI(s):',
            labelWidth=101,
            callback=self.updateGUI,
            tooltip=(
                u"The URL(s) that will be added to the list when\n"
                u"button 'Add' is clicked.\n\n"
                u"Successive URLs must be separated with ' / ' \n"
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
                u"Import URLs as annotations."
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
                u"Import URLs as annotations."
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
                u"Import URLs as annotations."
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
                u"Import URLs as annotations."
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
        )
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()

    def int_changed(self):
        """Send the entered number on "Number" output"""
        self.send("Text data", None)

    def importList(self):
        """Display a FileDialog and import URL list"""
        filePath, _ = QFileDialog.getOpenFileName(
            self,
            u'Import URL List',
            self.lastLocation,
            u'Text files (*)'
        )
        if not filePath:
            return

        self.file = os.path.normpath(filePath)
        self.lastLocation = os.path.dirname(filePath)
        self.error()
        try:
            fileHandle = codecs.open(filePath, encoding='utf8')
            fileContent = fileHandle.read()
            fileHandle.close()
        except IOError:
            QMessageBox.warning(
                None,
                'Textable',
                "Couldn't open file.",
                QMessageBox.Ok
            )
            return
        try:
            json_data = json.loads(fileContent)
            temp_URLs = list()
            for entry in json_data:
                URL = entry.get('url', '')
                encoding = entry.get('encoding', '')
                annotationKey = entry.get('annotation_key', '')
                annotationValue = entry.get('annotation_value', '')
                if URL == '' or encoding == '':
                    QMessageBox.warning(
                        None,
                        'Textable',
                        "Selected JSON file doesn't have the right keys "
                        "and/or values.",
                        QMessageBox.Ok
                    )
                    return
                temp_URLs.append((
                    URL,
                    encoding,
                    annotationKey,
                    annotationValue,
                ))
            self.URLs.extend(temp_URLs)
            if temp_URLs:
                self.sendButton.settingsChanged()
        except ValueError:
            QMessageBox.warning(
                None,
                'Textable',
                "Selected file is not in JSON format.",
                QMessageBox.Ok
            )
            return

    def exportList(self):
        """Display a FileDialog and export URL list"""
        toDump = list()
        for URL in self.URLs:
            toDump.append({
                'url': URL[0],
                'encoding': URL[1],
            })
            if URL[2] and URL[3]:
                toDump[-1]['annotation_key'] = URL[2]
                toDump[-1]['annotation_value'] = URL[3]
        filePath, _ = QFileDialog.getSaveFileName(
            self,
            u'Export URL List',
            self.lastLocation,
        )

        if filePath:
            self.lastLocation = os.path.dirname(filePath)
            outputFile = codecs.open(
                filePath,
                encoding='utf8',
                mode='w',
                errors='xmlcharrefreplace',
            )
            outputFile.write(
                normalizeCarriageReturns(
                    json.dumps(toDump, sort_keys=True, indent=4)
                )
            )
            outputFile.close()
            QMessageBox.information(
                None,
                'Textable',
                'URL list correctly exported',
                QMessageBox.Ok
            )
    def moveUp(self):
        """Move URL upward in URLs listbox"""
        if self.selectedURLLabel:
            index = self.selectedURLLabel[0]
            if index > 0:
                temp = self.URLs[index-1]
                self.URLs[index-1] = self.URLs[index]
                self.URLs[index] = temp
                self.selectedURLLabel = [index-1]
                self.sendButton.settingsChanged()

    def moveDown(self):
        """Move URL downward in URLs listbox"""
        if self.selectedURLLabel:
            index = self.selectedURLLabel[0]
            if index < len(self.URLs) - 1:
                temp = self.URLs[index+1]
                self.URLs[index+1] = self.URLs[index]
                self.URLs[index] = temp
                self.selectedURLLabel = [index+1]
                self.sendButton.settingsChanged()

    def clearAll(self):
        """Remove all URLs from URLs attr"""
        del self.URLs[:]
        del self.selectedURLLabel[:]
        self.sendButton.settingsChanged()

    def remove(self):
        """Remove URL from URLs attr"""
        if self.selectedURLLabel:
            index = self.selectedURLLabel[0]
            self.URLs.pop(index)
            del self.selectedURLLabel[:]
            self.sendButton.settingsChanged()

    def add(self):
        """Add URLs to URLs attr"""
        URLList = re.split(r' +/ +', self.newURL)
        for URL in URLList:
            encoding = re.sub(r"[ ]\(.+", "", self.encoding)
            self.URLs.append((
                URL,
                encoding,
                self.newAnnotationKey,
                self.newAnnotationValue,
            ))
        self.sendButton.settingsChanged()
    def updateGUI(self):
        """Update GUI state"""
        if self.displayAdvancedSettings:
            if self.selectedURLLabel:
                cachedLabel = self.selectedURLLabel[0]
            else:
                cachedLabel = None
            del self.URLLabel[:]
            if self.URLs:
                URLs = [f[0] for f in self.URLs]
                encodings = [f[1] for f in self.URLs]
                annotations = ['{%s: %s}' % (f[2], f[3]) for f in self.URLs]
                maxURLLen = max([len(n) for n in URLs])
                maxAnnoLen = max([len(a) for a in annotations])
                for index in range(len(self.URLs)):
                    format = u'%-' + str(maxURLLen + 2) + u's'
                    URLLabel = format % URLs[index]
                    if maxAnnoLen > 4:
                        if len(annotations[index]) > 4:
                            format = u'%-' + str(maxAnnoLen + 2) + u's'
                            URLLabel += format % annotations[index]
                        else:
                            URLLabel += u' ' * (maxAnnoLen + 2)
                    URLLabel += encodings[index]
                    self.URLLabel.append(URLLabel)
            self.URLLabel = self.URLLabel
            if cachedLabel is not None:
                self.sendButton.sendIfPreCallback = None
                self.selectedURLLabel = [cachedLabel]
                self.sendButton.sendIfPreCallback = self.updateGUI
            if self.newURL:
                if (
                    (self.newAnnotationKey and self.newAnnotationValue) or
                    (not self.newAnnotationKey and not self.newAnnotationValue)
                ):
                    self.addButton.setDisabled(False)
                else:
                    self.addButton.setDisabled(True)
            else:
                self.addButton.setDisabled(True)
            if self.autoNumber:
                self.autoNumberKeyLineEdit.setDisabled(False)
            else:
                self.autoNumberKeyLineEdit.setDisabled(True)
            if self.importURLs:
                self.importURLsKeyLineEdit.setDisabled(False)
            else:
                self.importURLsKeyLineEdit.setDisabled(True)
            self.updateURLBoxButtons()
            self.advancedSettings.setVisible(True)
        else:
            self.advancedSettings.setVisible(False)

    def updateURLBoxButtons(self):
        """Update state of File box buttons"""
        if self.selectedURLLabel:
            self.removeButton.setDisabled(False)
            if self.selectedURLLabel[0] > 0:
                self.moveUpButton.setDisabled(False)
            else:
                self.moveUpButton.setDisabled(True)
            if self.selectedURLLabel[0] < len(self.URLs) - 1:
                self.moveDownButton.setDisabled(False)
            else:
                self.moveDownButton.setDisabled(True)
        else:
            self.moveUpButton.setDisabled(True)
            self.moveDownButton.setDisabled(True)
            self.removeButton.setDisabled(True)
        if len(self.URLs):
            self.clearAllButton.setDisabled(False)
            self.exportButton.setDisabled(False)
        else:
            self.clearAllButton.setDisabled(True)
            self.exportButton.setDisabled(True)

