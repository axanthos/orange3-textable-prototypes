from __future__ import unicode_literals

"""
Class OWTextableTextTree
Copyright 2012-2016 LangTech Sarl (info@langtech.ch)
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

__version__ = '0.0.2'

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
        version=__version__.rsplit(".", 1)[0]
    )

    # Settings...
    autoSend = settings.Setting(True)
    folders = settings.Setting([])
    encoding = settings.Setting('iso-8859-1')
    operation = settings.Setting('nothing')
    sampling =settings.Setting(100)
    autoNumber = settings.Setting(False)
    autoNumberKey = settings.Setting(u'num')
    importFilenames = settings.Setting(True)
    importFolderName = settings.Setting(True)
    importFolderNameKey = settings.Setting(u'folderName')
    importFileNameKey = settings.Setting(u'filename')
    FolderDepth1Key = settings.Setting(u'depth 1')
    FolderDepth2Key = settings.Setting(u'depth 2')
    FolderDepth2Key = settings.Setting(u'depth 3')
    FolderDepth2Key = settings.Setting(u'depth 4')
    FolderDepthLvl = settings.Setting(u'depth level')

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
        self.selectedfolderLabels = list()
        self.rootFolderPath = u''
        self.inclusionsUser = u''
        self.exclusionsUser = u''
        self.newAnnotationKey = u''
        self.newAnnotationValue = u''
        self.folders = list() # self.folders is a list of dictionaries with each dictionaries being a a folder
        self.inclusionList = [".txt",".html",".xml",".csv"] #by default empty list

        # self.exclusionList = [".png,",".PNG",".jpg",".JPG",".gif",".GIF",".tiff",".TIFF",".jpeg",".JPEG",".DS_Store"] # by default exclusions : img files, .DS_Store (macOS)
        self.exclusionList = [] # by default null
        self.infoBox = InfoBox(widget=self.controlArea)
        # self.fileList = list() #output file list

        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute='infoBox',
            sendIfPreCallback=self.updateGUI,
        )
        self.advancedSettings = AdvancedSettings(
            widget=self.controlArea,
            master=self,
            callback=self.sendButton.settingsChanged,
        )

        # GUI...

        # Advanced settings checkbox...
        self.advancedSettings.draw()

        # BASIC GUI...

        # Basic folder box
        basicfolderBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Source',
            orientation='vertical',
            addSpace=False,
        )
        basicfolderBoxLine1 = gui.widgetBox(
            widget=basicfolderBox,
            box=False,
            orientation='horizontal',
        )
        gui.lineEdit(
            widget=basicfolderBoxLine1,
            master=self,
            value='rootFolderPath',
            orientation='horizontal',
            label=u'Folder path:',
            labelWidth=101,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The path of the folder."
            ),
        )
        gui.separator(widget=basicfolderBoxLine1, width=5)
        gui.button(
            widget=basicfolderBoxLine1,
            master=self,
            label=u'Browse',
            callback=self.browse,
            tooltip=(
                u"Open a dialog for selecting a top folder."
            ),
        )
        #gui.separator(widget=basicfolderBox, width=3)
        #gui.comboBox(
#            widget=basicfolderBox,
#            master=self,
#            value='encoding',
#            items=getPredefinedEncodings(),
#            sendSelectedValue=True,
#            orientation='horizontal',
#            label=u'Encoding:',
#            labelWidth=101,
#            callback=self.sendButton.settingsChanged,
#            tooltip=(
#                u"Select input folder(s) encoding."
#            ),
#        )
        gui.separator(widget=basicfolderBox, width=3)
        self.advancedSettings.basicWidgets.append(basicfolderBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        # ADVANCED GUI...

        # folder box
        folderBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Sources',
            orientation='vertical',
            addSpace=False,
        )
        folderBoxLine1 = gui.widgetBox(
            widget=folderBox,
            box=False,
            orientation='horizontal',
            addSpace=True,
        )
        self.folderListbox = gui.listBox(
            widget=folderBoxLine1,
            master=self,
            value='selectedfolderLabels',
            labels='folderLabels',
            callback=self.updatefolderBoxButtons,
            tooltip=(
                u"The list of folders whose content will be imported.\n"
                u"\nIn the output segmentation, the content of each\n"
                u"folder appears in the same position as in the list.\n"
                u"\nColumn 1 shows the folder's name.\n"
                u"Column 2 shows the folder's annotation (if any).\n"
                u"Column 3 shows the folder's encoding."
            ),
        )
        font = QFont()
        font.setFamily('Courier')
        font.setStyleHint(QFont.Courier)
        font.setPixelSize(12)
        self.folderListbox.setFont(font)
        folderBoxCol2 = gui.widgetBox(
            widget=folderBoxLine1,
            orientation='vertical',
        )
        self.moveUpButton = gui.button(
            widget=folderBoxCol2,
            master=self,
            label=u'Move Up',
            callback=self.moveUp,
            tooltip=(
                u"Move the selected folder upward in the list."
            ),
        )
        self.moveDownButton = gui.button(
            widget=folderBoxCol2,
            master=self,
            label=u'Move Down',
            callback=self.moveDown,
            tooltip=(
                u"Move the selected folder downward in the list."
            ),
        )
        self.removeButton = gui.button(
            widget=folderBoxCol2,
            master=self,
            label=u'Remove',
            callback=self.remove,
            tooltip=(
                u"Remove the selected folder from the list."
            ),
        )
        self.clearAllButton = gui.button(
            widget=folderBoxCol2,
            master=self,
            label=u'Clear All',
            callback=self.clearAll,
            tooltip=(
                u"Remove all folders from the list."
            ),
        )
        self.exportButton = gui.button(
            widget=folderBoxCol2,
            master=self,
            label=u'Export List',
            callback=self.exportList,
            tooltip=(
                u"Open a dialog for selecting a folder where the folder\n"
                u"list can be exported in JSON format."
            ),
        )
        self.importButton = gui.button(
            widget=folderBoxCol2,
            master=self,
            label=u'Import List',
            callback=self.importList,
            tooltip=(
                u"Open a dialog for selecting a folder list to\n"
                u"import (in JSON format). folders from this list\n"
                u"will be added to those already imported."
            ),
        )
        folderBoxLine2 = gui.widgetBox(
            widget=folderBox,
            box=False,
            orientation='vertical',
        )
        # Add folder box
        addfolderBox = gui.widgetBox(
            widget=folderBoxLine2,
            box=True,
            orientation='vertical',
        )
        addfolderBoxLine1 = gui.widgetBox(
            widget=addfolderBox,
            orientation='horizontal',
        )
        # Folder path input
        gui.lineEdit(
            widget=addfolderBoxLine1,
            master=self,
            value='rootFolderPath',
            orientation='horizontal',
            label=u'Folder path:',
            labelWidth=101,
            callback=self.updateGUI,
            tooltip=(
                u"The paths of the folders that will be added to the\n"
                u"list when button 'Add' is clicked.\n\n"
                u"Successive paths must be separated with ' / ' \n"
                u"(whitespace + slash + whitespace). Their order in\n"
                u"the list will be the same as in this field."
            ),
        )
        gui.separator(widget=addfolderBoxLine1, width=5)
        # Button Browse
        gui.button(
            widget=addfolderBoxLine1,
            master=self,
            label=u'Browse',
            callback=self.browse,
            tooltip=(
                u"Open a dialog for selecting a top folder.\n\n"
                u"Selected folder paths will appear in the field to\n"
                u"the left of this button afterwards, ready to be\n"
                u"added to the list when button 'Add' is clicked."
            ),
        )
        gui.separator(widget=addfolderBox, width=10)

        # Filter choice to include only certain files or to exclude files
        # ------------
        # self.applyInclusion = False  à mettre dans le init
        # gui.checkbox()
        # callback = lambda t=self.applyInclusion : includeLineEdit.setDisabled(not t)
        # includeLineEdit = gui.lineEdit()
        # ------------

        # Filter box to input include only
        gui.separator(widget=addfolderBox, width=3)
        includeBoxLine1 = gui.widgetBox(
            widget=addfolderBox,
            box=False,
            orientation='horizontal',
        )

        # Include only box
        gui.checkBox(
            widget=includeBoxLine1,
            master=self,
            value='applyInclusion',
            label=u'Include only',
            labelWidth=100,
            callback = lambda: includeLineEdit.setDisabled(not self.applyInclusion),
            tooltip=(
                u"Choose the inclusion"
            ),
        )
        includeLineEdit = gui.lineEdit(
            widget=includeBoxLine1,
            master=self,
            value='inclusionsUser',
            orientation='horizontal',
            label=u'',
            disabled = True,
            labelWidth=101,
            tooltip=(
                u"This field lets you specify a custom filter\n"
                u"to select the folders to be\n"
                u"added to the list."
            ),
        )

        # Filter box to exclude only
        gui.separator(widget=addfolderBox, width=3)
        excludeBoxLine1 = gui.widgetBox(
            widget=addfolderBox,
            box=False,
            orientation='horizontal',
        )
        # Exclude only box
        gui.checkBox(
            widget=excludeBoxLine1,
            master=self,
            value='applyExclusion',
            label=u'Exclude',
            labelWidth=100,
            disabled = False,
            callback = lambda: includeLineEdit2.setDisabled(not self.applyExclusion),
            tooltip=(
                u"Exclude the inclusion"
            ),
        )
        includeLineEdit2=gui.lineEdit(
            widget=excludeBoxLine1,
            master=self,
            value='exclusionsUser',
            orientation='horizontal',
            label=u'',
            disabled = True,
            labelWidth=101,
            tooltip=(
                u"This field lets you specify a custom filter\n"
                u"to select the folders to be\n"
                u"added to the list."
            ),
        )

        # Sampling box to input the level of sampling
        gui.separator(widget=addfolderBox, width=3)
        samplingBoxLine1 = gui.widgetBox(
            widget=addfolderBox,
            box=False,
            orientation='horizontal',
        )
        # Check box for sampling
        gui.checkBox(
            widget=samplingBoxLine1,
            master=self,
            value='applySampling',
            label=u'Sampling',
            labelWidth=100,
            disabled = False,
            callback = lambda: samplingSpin.setDisabled(not self.applySampling),
            tooltip=(
                u"Choose the sampling level"
            ),
        )
        # Box to input the level of samplig, spin minv = 10 and maxv = 100

        # self.importFilenamesKeyLineEdit = gui.spin(

        samplingSpin = gui.spin(
            widget=samplingBoxLine1,
            master=self,
            value='samplingRate',
            minv = 10,
            maxv = 100,
            labelWidth=50,
            orientation='horizontal',
            tooltip=(
                u"sampling level"
            ),
        )
        gui.separator(widget=addfolderBox, width=3)
        self.addButton = gui.button(
            widget=addfolderBox,
            master=self,
            label=u'Add',
            callback=self.add,
            tooltip=(
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
            widget=self.controlArea,
            box=u'Options',
            orientation='vertical',
            addSpace=False,
        )
        optionsBoxLine1 = gui.widgetBox(
            widget=optionsBox,
            box=False,
            orientation='horizontal',
        )
#        gui.checkBox(
#           widget=optionsBoxLine1,
#            master=self,
#           value='importFilenames',
#            label=u'Import folder names with key:',
#           labelWidth=180,
#            callback=self.sendButton.settingsChanged,
#            tooltip=(
#                u"Import folder names as annotations."
#           ),
#        )
#        self.importFilenamesKeyLineEdit = gui.lineEdit(
#            widget=optionsBoxLine1,
#            master=self,
#            value='importFilenamesKey',
#            orientation='horizontal',
#            callback=self.sendButton.settingsChanged,
#            tooltip=(
#                u"Annotation key for importing folder names."
#            ),
#        )
        gui.separator(widget=optionsBox, width=3)
        optionsBoxLine2 = gui.widgetBox(
            widget=optionsBox,
            box=False,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=optionsBoxLine2,
            master=self,
            value='autoNumber',
            label=u'Auto-number with key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotate folders with increasing numeric indices."
            ),
        )
        self.autoNumberKeyLineEdit = gui.lineEdit(
            widget=optionsBoxLine2,
            master=self,
            value='autoNumberKey',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotation key for folder auto-numbering."
            ),
        )
        gui.separator(widget=optionsBox, width=3)
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
            json_data = json.loads(message.content)
            temp_folders = list()
            for entry in json_data:
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
                temp_folders.append((
                    name,
                    path,
                    depth,
                    options,

                ))
            self.folders.extend(temp_folders)
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
        if (
            (self.displayAdvancedSettings and not self.folders) or
            not (self.rootFolderPath or self.displayAdvancedSettings)
        ):
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

        fileContents = list()
        annotations = list()
        counter = 1

        if self.displayAdvancedSettings:
            myFolders = self.folders
        else:
            myFolders = [[self.rootFolderPath]]

        progressBar = gui.ProgressBar(
            self,
            iterations=len(myFolders)
        )

        # Walk through each folder and open each files successively...

        for myFolder in myFolders:
            # self.rootFolderPath = myFolder[0]

            # OLD VERSION Try to open the file

            # with open(file_path,'rb') as opened_file:
            #     fileContent = ""
            #     i = 0
            #
            #     text = opened_file.read()
            #     charset_dict = chardet.detect(text)
            #     detected_encoding = charset_dict['encoding']
            #
            #     #Chunking is necessary when opening large files
            #     chunks = list()
            #     for chunk in iter(lambda: opened_file.read(CHUNK_LENGTH), ""):
            #         chunks.append('\n'.join(chunk.splitlines()))
            #         i += CHUNK_LENGTH
            #         if i % (CHUNK_NUM * CHUNK_LENGTH) == 0:
            #             fileContent += "".join(chunks)
            #             chunks = list()
            #
            #     if len(chunks):
            #         fileContent += "".join(chunks)
            #     del chunks
            #
            #     try:
            #         encodings.remove(detected_encoding)
            #         encodings.insert(0,detected_encoding)
            #
            #     except ValueError:
            #         pass
            #
            #     for encoding in encodings:
            #         try:
            #             self.segmentation_text = text.decode(encoding)
            #         except:
            #             pass
            #
            #     self.fileContent.append(self.segmentation_text)
            #
            # # Normalize text (canonical decomposition then composition)...
            #     fileContent = normalize('NFC', fileContent)
            #     fileContents.append(fileContent)
            fileContents = self.fileContents

            # Annotations...
            myFolders = self.folders
            for myFolder in myFolders:
                myFiles = myFolder['fileList']

                for myFile in myFiles:
                    # print(myFile)
                    annotation = dict()

                    if self.importFileNameKey:
                        folderName = myFile[-2]
                        annotation[self.importFileNameKey] = folderName

                    if self.importFolderNameKey:
                        folderName = myFile[1]
                        annotation[self.importFolderNameKey] = folderName

                    if self.FolderDepth1Key:
                        folderDepth1 = myFile[2]
                        annotation[self.FolderDepth1Key] = folderDepth1

                    if self.FolderDepth2Key:
                        folderDepth2 = myFile[3]
                        annotation[self.FolderDepth2Key] = folderDepth2

                    if self.FolderDepthLvl:
                        FolderDepthLvl = myFile[-1]
                        annotation[self.FolderDepthLvl] = FolderDepthLvl

                    annotations.append(annotation)
                # progressBar.advance()

            # Create an LTTL.Input for each files...

                if len(fileContents) == 1:
                    label = self.captionTitle
                else:
                    label = None
                for index in range(len(fileContents)):
                    myInput = Input(fileContents[index], label)
                    segment = myInput[0]
                    segment.annotations.update(annotations[index])
                    myInput[0] = segment
                    self.createdInputs.append(myInput)

                # If there's only one file, the widget's output is the created Input.
                if len(fileContents) == 1:
                    self.segmentation = self.createdInputs[0]

                # Otherwise the widget's output is a concatenation...
                else:
                    self.segmentation = Segmenter.concatenate(
                        segmentations=self.createdInputs,
                        label=self.captionTitle,
                        copy_annotations=True,
                        import_labels_as=None,
                        sort=False,
                        auto_number_as=None,
                        merge_duplicates=False,
                        progress_callback=None,
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
                progressBar.finish()

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
            folderHandle = codecs.open(folderPath, encoding='utf8')
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
            json_data = json.loads(folderContent)
            temp_folders = list()
            for entry in json_data:
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
                temp_folders.append((
                    path,
                    encoding,
                    annotationKey,
                    annotationValue,
                ))
            self.folders.extend(temp_folders)
            if temp_folders:
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
        folderPath =QFileDialog.getSaveFileName(
            self,
            u'Export folder List',
            self.lastLocation,
        )

        if folderPath:
            self.lastLocation = os.path.dirname(folderPath)
            outputfolder = codecs.open(
                folderPath,
                encoding='utf8',
                mode='w',
                errors='xmlcharrefreplace',
            )
            outputfolder.write(
                normalizeCarriageReturns(
                    json.dumps(toDump, sort_keys=True, indent=4)
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
        print("getFileList")
        initialRootParentPath, _ = os.path.split(self.rootFolderPath) #initial parent path is selected's folder parent folder
        fileListExt = list() # list of files matching default extension
        depthList = list()

        for curr_path, dirnames, filenames in os.walk(self.rootFolderPath):
    	#curr_path is a STRING, the path to the directory.
    	#dirnames is a LIST of the names of subdirectories.
    	#filenames is a LIST of the names of the files in curr_path
    	#symlink non traités

            curr_rel_path = curr_path[len(initialRootParentPath)+1:] #defines current relative path by similar initial parent path part
            curr_rel_path_list = os.path.normpath(curr_rel_path).split(os.sep) #splits current relative path by os separator

            for filename in filenames:
                file = dict()
                # file = {"absoluteFilePath","foldername","filename","depth1","depth2","depth3","depth4","depth5","depth lvl"}
                # prev_non_excl_check = False
                # curr_non_excl_check = prev_non_excl_check #importing previous state of the "non-exclusion check" (opposite of exclusion check)

                annotations = curr_rel_path_list[:] # annotations are different subfolders browsed
                annotationsByLvl = annotations[:]
                # print(annotationsByLvl)

                curr_depth = (len(annotationsByLvl))

                depthList.append(curr_depth)

                file['absoluteFilePath'] = os.path.join(curr_path,filename)
                file['fileName'] = filename
                file['depthLvl'] = curr_depth

                file['folderName'] = annotationsByLvl[0]

                try:
                    file['depth1'] = annotationsByLvl[1]
                except IndexError:
                    file['depth1'] = "0"

                try:
                    file['depth2'] = annotationsByLvl[2]
                except IndexError:
                    file['depth2'] = "0"

                try:
                    file['depth3'] = annotationsByLvl[3]
                except IndexError:
                    file['depth3'] = "0"

                try:
                    file['depth4'] = annotationsByLvl[4]
                except IndexError:
                    file['depth4'] = "0"

                for extension in self.inclusionList: #i = inclusionElement
                    if filename.endswith(extension):
                        fileListExt.append(file)

        # apply inclusion filter
        if self.applyInclusion:
            fileListIncl = [file for file in fileListExt
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
            self.openFileList()
        else:
            self.maxDepth = 0

    # TODO document
    def match(self, file, patternList):
        for pattern in patternList:
            if pattern in file:
                return True
        return False

    def openFileList(self):
        self.fileContents = list()
        for file in self.fileList:
            fileContent = ""
            try:
                file_path = file['absoluteFilePath']
            except TypeError:
                pass

            encodings = getPredefinedEncodings()
            with open(file_path,'rb') as opened_file:
                fileContent = opened_file.read()
                charset_dict = chardet.detect(fileContent)
                detected_encoding = charset_dict['encoding']

                # i = 0
                # chunks = list()
                #
                # for chunk in iter(lambda: opened_file.read(CHUNK_LENGTH), ""):
                #     chunks.append('\n'.join(chunk.splitlines()))
                #     i += CHUNK_LENGTH
                #     if i % (CHUNK_NUM * CHUNK_LENGTH) == 0:
                #         fileContent += "".join(str(chunks)
                #         chunk = list()
                #
                # if len(chunks):
                #     fileContent += "".join(str(chunks))
                # del chunks

                try:
                    encodings.remove(detected_encoding)
                    encodings.insert(0,detected_encoding)

                except ValueError:
                    pass

                for encoding in encodings:
                    try:
                        self.fileContent = fileContent.decode(encoding)
                    except:
                        pass


                # fileContent = normalize('NFC', str(fileContent))
                # fileContents.append(fileContent)

                self.fileContents.append(self.fileContent)

        del self.fileContents[-1]
        # print(self.fileContents)

    def browse(self):
        """Display a QFileDialog and select a folder"""

        rootFolderPath = QFileDialog.getExistingDirectory(    #Use QFileDialog.getExistingDirectory
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
            self.add()

        self.updateGUI()

    def moveUp(self):
        """Move folder upward in folders listbox"""
        if self.selectedfolderLabels:
            index = self.selectedfolderLabels[0]
            if index > 0:
                temp = self.folders[index - 1]
                self.folders[index - 1] = self.folders[index]
                self.folders[index] = temp
                self.selectedfolderLabels.listBox.item(index - 1).setSelected(1)
                self.sendButton.settingsChanged()

    def moveDown(self):
        """Move folder downward in folders listbox"""
        if self.selectedfolderLabels:
            index = self.selectedfolderLabels[0]
            if index < len(self.folders) - 1:
                temp = self.folders[index + 1]
                self.folders[index + 1] = self.folders[index]
                self.folders[index] = temp
                self.selectedfolderLabels.listBox.item(index + 1).setSelected(1)
                self.sendButton.settingsChanged()

    def clearAll(self):
        """Remove all folders from folders attr"""
        del self.folders[:]
        del self.selectedfolderLabels[:]
        self.sendButton.settingsChanged()

    def remove(self):
        """Remove folder from folders attr"""
        if self.selectedfolderLabels:
            index = self.selectedfolderLabels[0]
            self.folders.pop(index)
            del self.selectedfolderLabels[:]
            self.sendButton.settingsChanged()

    def add(self):
        """Add folders to folders attr"""

        rootFolderPathList = re.split(r' +/ +', self.rootFolderPath) #self.rootFolderPath = name

        # identify sequences separated by a "," and suppress the white spaces
        self.inclusionsUserAsList = [x.strip() for x in self.inclusionsUser.split(",") if x.strip()]
        self.exclusionsUserAsList = [x.strip() for x in self.exclusionsUser.split(",") if x.strip()]

        self.getFileList()
        # display the list of files
        print("Files: ", list(map(lambda f: f['fileName'], self.fileList)))

        sampleFileList = self.sampleFileList()
        # display the list of sampled files
        print("Files after sampling: ", list(map(lambda f: f['fileName'], sampleFileList)))

        self.folders.append(
            {
            'rootPath' : self.rootFolderPath,
            'maxDepth' : self.maxDepth,
            'inclusionsUser' : self.inclusionsUser,
            'exclusionsUser' : self.exclusionsUser,
            'samplingRate' : self.samplingRate,
            'fileList' : sampleFileList,
            }
        )
        # print(self.folders)
        self.sendButton.settingsChanged()

        # for folderDict in self.folders:
        #     fileList = folderDict['fileList']

    def sampleFileList(self):

        # Utilisation de la variable fileList
        # On fait une copie pour eviter de modifier self.fileList avec shuffle plus bas
        myList = list(self.fileList)

        # Initialisation d'un parametre qui decidera de l'echantillonage
        samplePercentage = self.samplingRate / 100.0
        print(samplePercentage)

        # On melange la liste pour prendre ensuite les "samplePercentage" premiers
        random.shuffle(myList)

        # On definit le nombre de fichiers voulus selon le parametre d'echantillonage "samplePercentage", arrondi au superieur
        nOfFiles = int(math.ceil(len(myList) * samplePercentage))
        # On prend les "nOfFiles" premiers fichiers de la liste melangee
        return myList[:nOfFiles]

    def updateGUI(self):
        """Update GUI state"""
        if self.displayAdvancedSettings:
            if self.selectedfolderLabels:
                cachedLabel = self.selectedfolderLabels[0]
            else:
                cachedLabel = None
            del self.folderLabels[:]

            if self.folders:
                folderRootPathsList = [f['rootPath'] for f in self.folders]
                maxDepthList = ['%s' % f['maxDepth'] for f in self.folders]
                inclusionsUserList = [f['inclusionsUser'] for f in self.folders]
                # print(inclusionsUserList)
                exclusionsUserList = [f['exclusionsUser'] for f in self.folders]
                samplingRatesList = ['%s' % f['samplingRate'] for f in self.folders]
                folderNamesList = [os.path.basename(p) for p in folderRootPathsList]
                maxFolderNameLen = max([len(n) for n in folderNamesList])

                for index in range(len(self.folders)):
                    format = u'%-' + str(maxFolderNameLen + 2) + u's'
                    # folderLabel = format % folderNamesList[index],
                    folderLabel = format % folderNamesList[index]
                    # print(inclusionsUserList[index])
                    folderLabel += "[d]:{"+maxDepthList[index]+"} "
                    folderLabel += "[i]:{"+inclusionsUserList[index]+"} "
                    folderLabel += "[e]:{"+exclusionsUserList[index]+"} "
                    folderLabel += "[s]:{"+samplingRatesList[index]+"%}"
                    self.folderLabels.append(folderLabel)

            self.folderLabels = self.folderLabels
            if cachedLabel is not None:
                self.sendButton.sendIfPreCallback = None
                self.selectedfolderLabels.listBox.item(
                    cachedLabel
                ).setSelected(1)
                self.sendButton.sendIfPreCallback = self.updateGUI
            if self.rootFolderPath:
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
            # if self.importFilenames:
            #     self.importFilenamesKeyLineEdit.setDisabled(False)
            # else:
            #     self.importFilenamesKeyLineEdit.setDisabled(True)
            self.updatefolderBoxButtons()
            self.advancedSettings.setVisible(True)
        else:
            self.advancedSettings.setVisible(False)

    def updatefolderBoxButtons(self):
        """Update state of folder box buttons"""
        if self.selectedfolderLabels:
            self.removeButton.setDisabled(False)
            if self.selectedfolderLabels[0] > 0:
                self.moveUpButton.setDisabled(False)
            else:
                self.moveUpButton.setDisabled(True)
            if self.selectedfolderLabels[0] < len(self.folders) - 1:
                self.moveDownButton.setDisabled(False)
            else:
                self.moveDownButton.setDisabled(True)
        else:
            self.moveUpButton.setDisabled(True)
            self.moveDownButton.setDisabled(True)
            self.removeButton.setDisabled(True)
        if len(self.folders):
            self.clearAllButton.setDisabled(False)
            self.exportButton.setDisabled(False)
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
