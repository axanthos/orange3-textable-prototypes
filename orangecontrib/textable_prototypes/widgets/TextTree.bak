from __future__ import unicode_literals

"""
Class OWTextableTextTree
Copyright 2012-2017 LangTech Sarl (info@langtech.ch)
-----------------------------------------------------------------------------
This folder is part of the Orange-Textable package v3.0.
Orange-Textable v3.0 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Orange-Textable v3.0 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Orange-Textable v3.0. If not, see <http://www.gnu.org/licenses/>.
"""

__version__ = '0.1.0'

import codecs, io, os, re, json, chardet
from unicodedata import normalize
import random
import math

from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QFileDialog, QMessageBox
from PyQt4.QtGui import QFont

from LTTL.Segmentation import Segmentation
from LTTL.Input import Input
import LTTL.Segmenter as Segmenter

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler,
    JSONMessage, InfoBox, SendButton, AdvancedSettings,
    getPredefinedEncodings, normalizeCarriageReturns, pluralize
)

from Orange.widgets import widget, gui, settings

CHUNK_LENGTH = 1000000
CHUNK_NUM = 100


class OWTextableTextTree(OWTextableBaseWidget):
    """Orange widget for loading text folders"""

    name = "Text Tree"
    description = "Import data from raw text trees"

    icon = "icons/Textfolders.png"

    icon = "icons/textTree.svg"

    priority = 2

    # Input and output channels...
    inputs = [
        ('Message', JSONMessage, "inputMessage", widget.Single)
    ]
    outputs = [('Text data', Segmentation)]

    settingsHandler = VersionedSettingsHandler(
        version = __version__.rsplit(".", 1)[0]
    )

    # Settings...
    autoSend = settings.Setting(True)
    folders = settings.Setting([])
    encoding = settings.Setting('iso-8859-1')
    operation = settings.Setting('nothing')
    sampling = settings.Setting(100)
    autoNumber = settings.Setting(False)
    autoNumberKey = settings.Setting(u'num')
    importFilenames = settings.Setting(True)
    importFolderName = settings.Setting(True)

    lastLocation = settings.Setting('.')
    displayAdvancedSettings = settings.Setting(False)
    folder = settings.Setting(u'')

    want_main_area = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Other attributes...
        self.segmentation = None
        self.operation = "no"
        self.applyInclusion = False
        self.applyExclusion = False
        self.applySampling = True
        self.samplingRate = 100
        self.createdInputs = list()
        self.folderLabels = list()
        self.selectedFolderLabels = list()
        self.rootFolderPath = u''
        self.inclusionsUser = u''
        self.exclusionsUser = u''
        self.newAnnotationKey = u''
        self.newAnnotationValue = u''

        # self.folder is a dictionary whose keys are :'rootPath', 'maxDepth','inclusionsUser','exclusionsUser', ...
        # ... 'samplingRate' and 'fileList'
        self.folder = dict()

        # self.folders is a list of previously defined "self.folder" dictionaries
        self.folders = list()

        # self.inclusionList is the default inclusion list (used in minimal mode, ...
        # ... and in advanced mode when no inclusion has been selected)
        self.inclusionList = [".txt", ".html", ".xml", ".csv", ".rtf"]

        # self.inclusionList is the default null inclusion list (used in minimal mode, ...
        # ... and in advanced mode when no inclusion has been selected)
        self.exclusionList = []

        self.infoBox = InfoBox(widget = self.controlArea)

        self.sendButton = SendButton(
            widget = self.controlArea,
            master = self,
            callback = self.sendData,
            infoBoxAttribute = 'infoBox',
            sendIfPreCallback = self.updateGUI,
        )
        self.advancedSettings = AdvancedSettings(
            widget = self.controlArea,
            master = self,
            callback = self.sendButton.settingsChanged,
        )

        # GUI...

        # Advanced settings checkbox...
        self.advancedSettings.draw()

        # BASIC GUI...

        # Basic folder box
        basicFolderBox = gui.widgetBox(
            widget = self.controlArea,
            box = u'Source',
            orientation = 'vertical',
            addSpace = False,
        )
        basicFolderBoxLine1 = gui.widgetBox(
            widget = basicFolderBox,
            box = False,
            orientation = 'horizontal',
        )
        gui.lineEdit(
            widget = basicFolderBoxLine1,
            master = self,
            value = 'rootFolderPath',
            orientation = 'horizontal',
            label = u'Folder path:',
            labelWidth = 101,
            callback = self.add,
            tooltip = (
                u"The path of the folder."
            ),
        )
        gui.separator(widget = basicFolderBoxLine1, width = 5)
        gui.button(
            widget = basicFolderBoxLine1,
            master = self,
            label = u'Browse',
            callback = self.browse,
            tooltip = (
                u"Open a dialog for selecting a top folder."
            ),
        )

        gui.separator(widget = basicFolderBox, width = 3)
        self.advancedSettings.basicWidgets.append(basicFolderBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        # ADVANCED GUI...

        # folder box
        folderBox = gui.widgetBox(
            widget = self.controlArea,
            box = u'Sources',
            orientation = 'vertical',
            addSpace = False,
        )
        folderBoxLine1 = gui.widgetBox(
            widget = folderBox,
            box = False,
            orientation = 'horizontal',
            addSpace = True,
        )
        self.folderListbox = gui.listBox(
            widget = folderBoxLine1,
            master = self,
            value = 'selectedFolderLabels',
            labels = 'folderLabels',
            callback = self.updatefolderBoxButtons,
            tooltip = (
                u"The list of folders whose content will be imported.\n"
                u"\nIn the output segmentation, the content of each\n"
                u"folder appears in the same position as in the list.\n"
                u"\nColumn 1 shows the folder's name.\n"
                u"Column 2 shows the folder's depth.\n"
                u"Column 3 shows the inclusions filter.\n"
                u"Column 4 shows the exclusions filter.\n"
                u"Column 5 shows the folder's level of sampling."
            ),
        )
        font = QFont()
        font.setFamily('Courier')
        font.setStyleHint(QFont.Courier)
        font.setPixelSize(12)
        self.folderListbox.setFont(font)
        folderBoxCol2 = gui.widgetBox(
            widget = folderBoxLine1,
            orientation = 'vertical',
        )
        self.moveUpButton = gui.button(
            widget = folderBoxCol2,
            master = self,
            label = u'Move Up',
            callback = self.moveUp,
            tooltip = (
                u"Move the selected folder upward in the list."
            ),
        )
        self.moveDownButton = gui.button(
            widget = folderBoxCol2,
            master = self,
            label = u'Move Down',
            callback = self.moveDown,
            tooltip = (
                u"Move the selected folder downward in the list."
            ),
        )
        self.removeButton = gui.button(
            widget = folderBoxCol2,
            master = self,
            label = u'Remove',
            callback = self.remove,
            tooltip = (
                u"Remove the selected folder from the list."
            ),
        )
        self.clearAllButton = gui.button(
            widget = folderBoxCol2,
            master = self,
            label = u'Clear All',
            callback = self.clearAll,
            tooltip = (
                u"Remove all folders from the list."
            ),
        )
        self.exportButton = gui.button(
            widget = folderBoxCol2,
            master = self,
            label = u'',
            callback = self.exportList,
            disabled = True,
            tooltip = (
                u"Open a dialog for selecting a folder where the folder\n"
                u"list can be exported in JSON format."
            ),
        )
        self.importButton = gui.button(
            widget = folderBoxCol2,
            master = self,
            label = u'',
            callback = self.importList,
            disabled = True,
            tooltip = (
                u"Open a dialog for selecting a folder list to\n"
                u"import (in JSON format). folders from this list\n"
                u"will be added to those already imported."
            ),
        )
        folderBoxLine2 = gui.widgetBox(
            widget = folderBox,
            box = False,
            orientation = 'vertical',
        )
        # Add folder box
        addFolderBox = gui.widgetBox(
            widget = folderBoxLine2,
            box = True,
            orientation = 'vertical',
        )
        addFolderBoxLine1 = gui.widgetBox(
            widget = addFolderBox,
            orientation = 'horizontal',
        )
        # Folder path input
        gui.lineEdit(
            widget = addFolderBoxLine1,
            master = self,
            value = 'rootFolderPath',
            orientation = 'horizontal',
            label = u'Folder path:',
            labelWidth = 101,
            callback = self.updateGUI,
            tooltip = (
                u"The paths of the folders that will be added to the\n"
                u"list when button 'Add' is clicked.\n\n"
                u"Successive paths must be separated with ' / ' \n"
                u"(whitespace + slash + whitespace). Their order in\n"
                u"the list will be the same as in this field."
            ),
        )
        gui.separator(widget = addFolderBoxLine1, width = 5)
        # Button Browse
        gui.button(
            widget = addFolderBoxLine1,
            master = self,
            label = u'Browse',
            callback = self.browse,
            tooltip = (
                u"Open a dialog for selecting a top folder.\n\n"
                u"Selected folder paths will appear in the field to\n"
                u"the left of this button afterwards, ready to be\n"
                u"added to the list when button 'Add' is clicked."
            ),
        )
        gui.separator(widget = addFolderBox, width = 10)

        # Filter box to input include
        gui.separator(widget = addFolderBox, width = 3)
        includeBoxLine1 = gui.widgetBox(
            widget = addFolderBox,
            box = False,
            orientation = 'horizontal',
        )

        # Include box
        gui.checkBox(
            widget = includeBoxLine1,
            master = self,
            value = 'applyInclusion',
            label = u'Include',
            labelWidth = 100,
            callback = lambda: includeLineEdit.setDisabled(not self.applyInclusion),
            tooltip = (
                u"Choose the inclusion(s)"
            ),
        )
        includeLineEdit = gui.lineEdit(
            widget = includeBoxLine1,
            master = self,
            value = 'inclusionsUser',
            orientation = 'horizontal',
            label = u'',
            disabled = True,
            labelWidth = 101,
            tooltip = (
                u"This field lets you specify a custom filter\n"
                u"to select the folders to be\n"
                u"added to the list."
            ),
        )

        # Filter box to exclude
        gui.separator(widget = addFolderBox, width = 3)
        excludeBoxLine1 = gui.widgetBox(
            widget = addFolderBox,
            box = False,
            orientation = 'horizontal',
        )
        # Exclude box
        gui.checkBox(
            widget = excludeBoxLine1,
            master = self,
            value = 'applyExclusion',
            label = u'Exclude',
            labelWidth = 100,
            disabled = False,
            callback = lambda: includeLineEdit2.setDisabled(not self.applyExclusion),
            tooltip = (
                u"Exclude the inclusion(s)"
            ),
        )
        includeLineEdit2 = gui.lineEdit(
            widget = excludeBoxLine1,
            master = self,
            value = 'exclusionsUser',
            orientation = 'horizontal',
            label = u'',
            disabled = True,
            labelWidth = 101,
            tooltip = (
                u"This field lets you specify a custom filter\n"
                u"to select the folders to be\n"
                u"added to the list."
            ),
        )

        # Sampling box to input the level of sampling
        gui.separator(widget = addFolderBox, width = 3)
        samplingBoxLine1 = gui.widgetBox(
            widget = addFolderBox,
            box = False,
            orientation = 'horizontal',
        )
        # Check box for sampling
        gui.checkBox(
            widget = samplingBoxLine1,
            master = self,
            value = 'applySampling',
            label = u'Sampling',
            labelWidth = 100,
            disabled = False,
            callback = lambda: samplingSpin.setDisabled(not self.applySampling),
            tooltip = (
                u"Choose the sampling level"
            ),
        )

        samplingSpin = gui.spin(
            widget = samplingBoxLine1,
            master = self,
            value = 'samplingRate',
            minv = 10,
            maxv = 100,
            labelWidth = 50,
            orientation = 'horizontal',
            tooltip = (
                u"sampling level"
            ),
        )
        gui.separator(widget = addFolderBox, width = 3)
        self.addButton = gui.button(
            widget = addFolderBox,
            master = self,
            label = u'Add',
            callback = self.add,
            tooltip = (
                u"Add the folder(s) currently displayed in the\n"
                u"'folders' text field to the list.\n\n"
                u"Each of these folders will be associated with the\n"
                u"specified encoding and annotation (if any).\n\n"
                u"Other folders may be selected afterwards and\n"
                u"assigned a different encoding and annotation."
            ),
        )
        self.advancedSettings.advancedWidgets.append(folderBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # Options box...
        optionsBox = gui.widgetBox(
            widget = self.controlArea,
            box = u'Options',
            orientation = 'vertical',
            addSpace = False,
        )
        optionsBoxLine1 = gui.widgetBox(
            widget = optionsBox,
            box = False,
            orientation = 'horizontal',
        )

        gui.separator(widget = optionsBox, width = 3)
        optionsBoxLine2 = gui.widgetBox(
            widget = optionsBox,
            box = False,
            orientation = 'horizontal',
        )
        gui.checkBox(
            widget = optionsBoxLine2,
            master = self,
            value = 'autoNumber',
            label = u'Auto-number with key:',
            labelWidth = 180,
            callback = self.sendButton.settingsChanged,
            tooltip = (
                u"Annotate folders with increasing numeric indices."
            ),
        )
        self.autoNumberKeyLineEdit = gui.lineEdit(
            widget = optionsBoxLine2,
            master = self,
            value = 'autoNumberKey',
            orientation = 'horizontal',
            callback = self.sendButton.settingsChanged,
            tooltip = (
                u"Annotation key for folder auto-numbering."
            ),
        )
        gui.separator(widget = optionsBox, width = 3)
        self.advancedSettings.advancedWidgets.append(optionsBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        gui.rubber(self.controlArea)

        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.adjustSizeWithTimer()
        QTimer.singleShot(0, self.sendButton.sendIf)

    def inputMessage(self, message):
        """Handle JSON message on input connection"""
        if not message:
            return
        self.displayAdvancedSettings = True
        self.advancedSettings.setVisible(True)
        self.clearAll()
        self.infoBox.inputChanged()
        try:
            jsonData = json.loads(message.content)
            tempFolders = list()
            for entry in jsonData:
                path = entry.get('path', '')
                encoding = entry.get('encoding', '')
                annotationKey = entry.get('annotation_key', '')
                annotationValue = entry.get('annotation_value', '')
                if path == '' or encoding == '':
                    self.infoBox.setText(
                        u"Please verify keys and values of incoming "
                        u"JSON message.",
                        'error'
                    )
                    self.send('Text data', None, self)
                    return
                depth = "0"
                options = "[i]:{unicorn}"
                tempFolders.append((
                    name,
                    path,
                    depth,
                    options,

                ))
            self.folders.extend(tempFolders)
            self.sendButton.settingsChanged()
        except ValueError:
            self.infoBox.setText(
                u"Please make sure that incoming message is valid JSON.",
                'error'
            )
            self.send('Text data', None, self)
            return

    def sendData(self):

        """Load folders, create and send segmentation"""

        # Check that there's something on input...
        if (self.displayAdvancedSettings and not self.folders) or not (
                    self.rootFolderPath or self.displayAdvancedSettings):
            self.infoBox.setText(u'Please select input folder.', 'warning')
            self.send('Text data', None, self)
            return

        # Check that autoNumberKey is not empty (if necessary)...
        if self.displayAdvancedSettings and self.autoNumber:
            if self.autoNumberKey:
                autoNumberKey = self.autoNumberKey
            else:
                self.infoBox.setText(
                    u'Please enter an annotation key for auto-numbering.',
                    'warning'
                )
                self.send('Text data', None, self)
                return
        else:
            autoNumberKey = None

        # Clear created Inputs...
        self.clearCreatedInputs()
        annotations = list()
        counter = 1

        if self.displayAdvancedSettings:
            myFolders = self.folders
        else:
            myFolders = [self.folder]

        # Annotations...
        allFileListContent = list()
        for myFolder in myFolders:

            myFiles = myFolder['fileList']

            for myFile in myFiles:

                annotation = dict()
                annotation['file name'] = myFile['fileName']
                annotation['file depth level'] = myFile['depthLvl']
                annotation['file path'] = myFile['absoluteFilePath']
                try:
                    annotation['file encoding, confidence'] = myFile['encoding'] + ", " + str(
                        myFile['encodingConfidence'])
                except TypeError:
                    annotation['file encoding, confidence'] = "unknown"

                depths = [k for k in myFile.keys() if k.startswith('depth_')]
                for depth in depths:
                    annotation[depth] = myFile[depth]

                annotations.append(annotation)
                allFileListContent.append(myFile['fileContent'])

        # Create an LTTL.Input for each files...

        if len(allFileListContent) == 1:
            label = self.captionTitle
        else:
            label = None
        for index in range(len(allFileListContent)):
            myInput = Input(allFileListContent[index], label)
            segment = myInput[0]
            segment.annotations.update(annotations[index])
            myInput[0] = segment
            self.createdInputs.append(myInput)

        # If there's only one file, the widget's output is the created Input.
        if len(allFileListContent) == 1:
            self.segmentation = self.createdInputs[0]
        # Otherwise the widget's output is a concatenation...
        else:
            self.segmentation = Segmenter.concatenate(
                segmentations = self.createdInputs,
                label = self.captionTitle,
                copy_annotations = True,
                import_labels_as = None,
                sort = False,
                auto_number_as = None,
                merge_duplicates = False,
                progress_callback = None,
            )
        message = u'%i segment@p sent to output ' % len(self.segmentation)
        message = pluralize(message, len(self.segmentation))
        numChars = 0
        for segment in self.segmentation:
            segmentLength = len(Segmentation.get_data(segment.str_index))
            numChars += segmentLength
        message += u'(%i character@p).' % numChars
        message = pluralize(message, numChars)
        self.infoBox.setText(message)

        self.send('Text data', self.segmentation, self)
        self.sendButton.resetSettingsChangedFlag()

    def clearCreatedInputs(self):
        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]

    def importList(self):
        """Display a folderDialog and import folder list"""
        folderPath = QFileDialog.getOpenFileName(
            self,
            u'Import folder List',
            self.lastLocation,
            u'Text folders (*)'
        )
        if not folderPath:
            return
        self.rootFolderPath = os.path.normpath(folderPath)
        self.lastLocation = os.path.dirname(folderPath)
        self.error()
        try:
            folderHandle = codecs.open(folderPath, encoding = 'utf8')
            folderContent = folderHandle.read()
            folderHandle.close()
        except IOError:
            QMessageBox.warning(
                None,
                'Textable',
                "Couldn't open folder.",
                QMessageBox.Ok
            )
            return
        try:
            jsonData = json.loads(folderContent)
            tempFolders = list()
            for entry in jsonData:
                path = entry.get('path', '')
                encoding = entry.get('encoding', '')
                annotationKey = entry.get('annotation_key', '')
                annotationValue = entry.get('annotation_value', '')
                if path == '' or encoding == '':
                    QMessageBox.warning(
                        None,
                        'Textable',
                        "Selected JSON folder doesn't have the right keys "
                        "and/or values.",
                        QMessageBox.Ok
                    )
                    return
                tempFolders.append((
                    path,
                    encoding,
                    annotationKey,
                    annotationValue,
                ))
            self.folders.extend(tempFolders)
            if tempFolders:
                self.sendButton.settingsChanged()
        except ValueError:
            QMessageBox.warning(
                None,
                'Textable',
                "JSON parsing error.",
                QMessageBox.Ok
            )
            return

    def exportList(self):
        """Display a folderDialog and export folder list"""
        toDump = list()
        myFolders = self.folders
        for myFolder in myFolders:
            toDump.append({
                'path': myFolder[0],
                'encoding': myFolder[1],
            })
            if myFolder[2] and myFolder[3]:
                toDump[-1]['annotation_key'] = myFolder[2]
                toDump[-1]['annotation_value'] = myFolder[3]
        folderPath = QFileDialog.getSaveFileName(
            self,
            u'Export folder List',
            self.lastLocation,
        )

        if folderPath:
            self.lastLocation = os.path.dirname(folderPath)
            outputfolder = codecs.open(
                folderPath,
                encoding = 'utf8',
                mode = 'w',
                errors = 'xmlcharrefreplace',
            )
            outputfolder.write(
                normalizeCarriageReturns(
                    json.dumps(toDump, sort_keys = True, indent = 4)
                )
            )
            outputfolder.close()
            QMessageBox.information(
                None,
                'Textable',
                'folder list correctly exported',
                QMessageBox.Ok
            )

    def getFileList(self):

        initialRootParentPath, _ = os.path.split(

            # self.rootFolderPath is the initially selected's folder parent
            self.rootFolderPath)
        fileList = list()

        # fileListExt is a list of files matching default extension
        fileListExt = list()
        depthList = list()

        progressBarZero = gui.ProgressBar(self, iterations = 1)

        # Using os.walk to walk through directories :
        # Variables descriptions :
            # currPath is a STRING, the path to the directory.
            # dirNames is a LIST of the names of subdirectories.
            # fileNames is a LIST of the names of the files in currPath
            # symlink are not considered in this analysis

        for currPath, dirNames, fileNames in os.walk(self.rootFolderPath):

            currRelPath = currPath[len(
                initialRootParentPath) + 1:]  # defines current relative path by similar initial parent path part
            currRelPathList = os.path.normpath(currRelPath).split(
                os.sep)  # splits current relative path by os separator

            for fileName in fileNames:

                # file dict is a dictionary of the file's informations will get following keys :
                # file = {
                # "absoluteFilePath",
                # "fileName",
                # "depth_0",
                # "depth_X"
                # depthLvl",
                # "fileContent"
                # }

                # 'fileContent','encoding' and 'encodingConfidence' keys are defined when function "openFileList" is called

                file = dict()

                # Initial annotations correspond different subfolders browsed by each depth level (used for depth_X annot.)
                annotations = currRelPathList[:]

                currDepth = len(annotations) - 1
                depthList.append(currDepth)

                file['absoluteFilePath'] = os.path.join(currPath, fileName)
                file['fileName'] = fileName
                file['depthLvl'] = currDepth

                file['depth_0'] = annotations[0]

                # Created an annotation by depth level, corresponding to folder names
                for i in range(1, currDepth + 1):
                    file['depth_' + str(i)] = annotations[i]

                # Apply default file extension filter
                for extension in self.inclusionList:
                    if fileName.endswith(extension):

                        # FileListExt = file list created with default inclusion criteria (text extensions from inclusionList)
                        fileListExt.append(
                            file)

                fileList.append(file)

        # apply inclusion filter
        if self.applyInclusion:
            fileListIncl = [file for file in fileList
                            # match in inclusion list
                            if self.match(file['fileName'], self.inclusionsUserAsList)]
        else:
            fileListIncl = fileListExt

        # apply exclusion filter
        if self.applyExclusion:
            fileListExcl = [file for file in fileListIncl
                            # no match in exclusion list
                            if not self.match(file['fileName'], self.exclusionsUserAsList)]
        else:
            fileListExcl = fileListIncl

        # output file list
        self.fileList = fileListExcl

        if self.fileList:
            self.maxDepth = max(depthList)
            self.fileList = self.sampleFileList()
            self.openFileList()
        else:
            self.maxDepth = 0

        progressBarZero.finish()

    # Test if file contains one of the patterns in patternList
    def match(self, file, patternList):
        for pattern in patternList:
            if pattern in file:
                return True
        return False

    def openFileList(self):

        tempFileList = list()

        progressBarOpen = gui.ProgressBar(
            self,
            iterations = len(self.fileList)
        )

        for file in self.fileList:
            fileContent = ""
            try:
                filePath = file['absoluteFilePath']
            except TypeError:
                pass

            encodings = getPredefinedEncodings()
            try:
                with open(filePath, 'rb') as openedFile:
                    fileContent = openedFile.read()
                    charsetDict = chardet.detect(fileContent)
                    detectedEncoding = charsetDict['encoding']
                    detectedConfidence = charsetDict['confidence']

                    # Chunking functionnality should be added here

                    try:
                        encodings.remove(detectedEncoding)
                        encodings.insert(0, detectedEncoding)

                    except ValueError:
                        pass

                    for encoding in encodings:
                        try:
                            self.fileContent = fileContent.decode(encoding)
                        except:
                            pass

                file['encoding'] = detectedEncoding
                file['fileContent'] = self.fileContent
                file['encodingConfidence'] = detectedConfidence
                progressBarOpen.advance()
                tempFileList.append(file)

            except IOError:
                if len(myFiles) > 1:
                    message = u"Couldn't open file '%s'." % filePath
                else:
                    message = u"Couldn't open file."
                self.infoBox.setText(message, 'error')
                self.send('Text data', None, self)
                return

        self.fileList = tempFileList

        self.folder = {
            'rootPath': self.rootFolderPath,
            'maxDepth': self.maxDepth,
            'inclusionsUser': self.inclusionsUser,
            'exclusionsUser': self.exclusionsUser,
            'samplingRate': self.samplingRate,
            'fileList': self.fileList
        }
        progressBarOpen.finish()

    def browse(self):
        """Display a QFileDialog and select a folder"""

        rootFolderPath = QFileDialog.getExistingDirectory(
            self,
            u'Select Folder(s)',
            self.lastLocation,
        )
        if not rootFolderPath:
            return

        rootFolderPath = os.path.normpath(rootFolderPath)
        self.rootFolderPath = rootFolderPath
        self.lastLocation = rootFolderPath

        if self.displayAdvancedSettings:
            pass
        else:
            self.getFileList()
            self.folder = {
                'rootPath': self.rootFolderPath,
                'maxDepth': self.maxDepth,
                'fileList': self.fileList,
            }
            self.sendButton.settingsChanged()

        self.updateGUI()

    def moveUp(self):
        """Move folder upward in folders listbox"""
        if self.selectedFolderLabels:
            index = self.selectedFolderLabels[0]
            if index > 0:
                temp = self.folders[index - 1]
                self.folders[index - 1] = self.folders[index]
                self.folders[index] = temp
                self.selectedFolderLabels.listBox.item(index - 1).setSelected(1)
                self.sendButton.settingsChanged()

    def moveDown(self):
        """Move folder downward in folders listbox"""
        if self.selectedFolderLabels:
            index = self.selectedFolderLabels[0]
            if index < len(self.folders) - 1:
                temp = self.folders[index + 1]
                self.folders[index + 1] = self.folders[index]
                self.folders[index] = temp
                self.selectedFolderLabels.listBox.item(index + 1).setSelected(1)
                self.sendButton.settingsChanged()

    def clearAll(self):
        """Remove all folders from folders attr"""
        del self.folders[:]
        del self.selectedFolderLabels[:]
        self.sendButton.settingsChanged()

    def remove(self):
        """Remove folder from folders attr"""
        if self.selectedFolderLabels:
            index = self.selectedFolderLabels[0]
            self.folders.pop(index)
            del self.selectedFolderLabels[:]
            self.sendButton.settingsChanged()

    def add(self):
        """Add folders to folders attr"""

        # Identify sequences separated by a comma (,) and deletes existing whitespaces
        self.inclusionsUserAsList = [x.strip() for x in self.inclusionsUser.split(",") if x.strip()]
        self.exclusionsUserAsList = [x.strip() for x in self.exclusionsUser.split(",") if x.strip()]

        # Calling the GetFileList function returns a self.fileList list of all files corresponding to either defaults
        # or optional settings
        self.getFileList()

        self.folders.append(self.folder)

        self.sendButton.settingsChanged()

    def sampleFileList(self):

        myList = list(self.fileList)

        # Sampling rate from input allows calculation of the sampling percentage
        samplePercentage = self.samplingRate / 100.0

        # The initial list is shuffled so that files from all folders can be picked randomly
        random.shuffle(myList)

        # Files are picked randomly from the previously shuffled list
        nOfFiles = int(math.ceil(len(myList) * samplePercentage))
        return myList[:nOfFiles]

    def updateGUI(self):
        """Update GUI state"""
        if self.displayAdvancedSettings:
            if self.selectedFolderLabels:
                cachedLabel = self.selectedFolderLabels[0]
            else:
                cachedLabel = None

            del self.folderLabels[:]
            folderLabels = []

            if self.folders:
                folderRootPathsList = [f['rootPath'] for f in self.folders]
                maxDepthList = ['%s' % f['maxDepth'] for f in self.folders]
                inclusionsUserList = [f['inclusionsUser'] for f in self.folders]
                exclusionsUserList = [f['exclusionsUser'] for f in self.folders]
                samplingRatesList = ['%s' % f['samplingRate'] for f in self.folders]
                folderNamesList = [os.path.basename(p) for p in folderRootPathsList]
                maxFolderNameLen = max([len(n) for n in folderNamesList])

                for index in range(len(self.folders)):
                    format = u'%-' + str(maxFolderNameLen + 2) + u's'
                    folderLabel = format % folderNamesList[index]
                    folderLabel += "[d]:{" + maxDepthList[index] + "} "
                    folderLabel += "[i]:{" + inclusionsUserList[index] + "} "
                    folderLabel += "[e]:{" + exclusionsUserList[index] + "} "
                    folderLabel += "[s]:{" + samplingRatesList[index] + "%}"
                    folderLabels.append(folderLabel)

            self.folderLabels = folderLabels

            if cachedLabel is not None:
                self.sendButton.sendIfPreCallback = None
                self.selectedFolderLabels.listBox.item(
                    cachedLabel
                ).setSelected(1)
                self.sendButton.sendIfPreCallback = self.updateGUI
            if self.rootFolderPath:
                if (self.newAnnotationKey and self.newAnnotationValue) or (
                    not self.newAnnotationKey and not self.newAnnotationValue):
                    self.addButton.setDisabled(False)
                else:
                    self.addButton.setDisabled(True)
            else:
                self.addButton.setDisabled(True)
            if self.autoNumber:
                self.autoNumberKeyLineEdit.setDisabled(False)
            else:
                self.autoNumberKeyLineEdit.setDisabled(True)

            self.updatefolderBoxButtons()
            self.advancedSettings.setVisible(True)
        else:
            self.advancedSettings.setVisible(False)

    def updatefolderBoxButtons(self):
        """Update state of folder box buttons"""
        if self.selectedFolderLabels:
            self.removeButton.setDisabled(False)
            if self.selectedFolderLabels[0] > 0:
                self.moveUpButton.setDisabled(False)
            else:
                self.moveUpButton.setDisabled(True)
            if self.selectedFolderLabels[0] < len(self.folders) - 1:
                self.moveDownButton.setDisabled(False)
            else:
                self.moveDownButton.setDisabled(True)
        else:
            self.moveUpButton.setDisabled(True)
            self.moveDownButton.setDisabled(True)
            self.removeButton.setDisabled(True)
        if len(self.folders):
            self.clearAllButton.setDisabled(False)
            self.exportButton.setDisabled(True)
        else:
            self.clearAllButton.setDisabled(True)
            self.exportButton.setDisabled(True)

    def setCaption(self, title):
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)

    def onDeleteWidget(self):
        self.clearCreatedInputs()


if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import QApplication

    appl = QApplication(sys.argv)
    ow = OWTextableTextTree()
    ow.show()
    appl.exec_()
    ow.saveSettings()
