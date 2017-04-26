from __future__ import unicode_literals

"""
Class OWTextableTextfolders
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
    importfoldernames = settings.Setting(True)
    importfoldernamesKey = settings.Setting(u'foldername')
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
        self.newFolderPath = u''
        self.inclusionCondition = u''
        self.exclusionCondition = u''
        self.newAnnotationKey = u''
        self.newAnnotationValue = u''
        self.infoBox = InfoBox(widget=self.controlArea)
        # self.files_list = list() #output file list

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
            value='folder',
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
            value='newFolderPath',
            orientation='horizontal',
            label=u'Folder path(s):',
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
            value='inclusionCondition',
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
            value='exclusionCondition',
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
#           value='importfoldernames',
#            label=u'Import folder names with key:',
#           labelWidth=180,
#            callback=self.sendButton.settingsChanged,
#            tooltip=(
#                u"Import folder names as annotations."
#           ),
#        )
#        self.importfoldernamesKeyLineEdit = gui.lineEdit(
#            widget=optionsBoxLine1,
#            master=self,
#            value='importfoldernamesKey',
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
            not (self.folder or self.displayAdvancedSettings)
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
            myFolders = self.files_list
        else:
            myFolders = [[self.folder]]

        progressBar = gui.ProgressBar(
            self,
            iterations=len(myFolders)
        )

        # Walk through each folder and open each files successively...

        for myFolder in myFolders:
            self.newFolderPath = myFolder[0]
            self.walkThroughDirectory()
            # OLD VERSION Try to open the file
            # try:
            #     file_path = myFile[0]
            # except TypeError:
            #     pass
            #
            # encodings = getPredefinedEncodings()
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
            #     # print(self.segmentation_text) #this will be the Segmentation for Output
            #     self.fileContent.append(self.segmentation_text)
            #
            # # Normalize text (canonical decomposition then composition)...
            #     fileContent = normalize('NFC', fileContent)
            #     fileContents.append(fileContent)
            # print(self.fileContents)
            fileContents = self.fileContents
            # Annotations...
            # annotation = dict()
            # annotations.append(annotation)
            # progressBar.advance()

        # Create an LTTL.Input for each files...
            # print(self.fileContents)

            if len(fileContents) == 1:
                label = self.captionTitle
            else:
                label = None
            for index in range(len(fileContents)):
                print(str(index))
                myInput = Input(fileContents[index], label)
                segment = myInput[0]
                # segment.annotations.update(annotations[index])
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
            print(self.segmentation.to_string())
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
        self.folder = os.path.normpath(folderPath)
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
        for myFolder in self.folders:
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

    def walkThroughDirectory(self):
        inclusion_list = [""] #by default empty list
        exclusion_list = [".png,",".PNG",".jpg",".JPG",".gif",".GIF",".tiff",".TIFF",".jpeg",".JPEG",".DS_Store"] # by default exclusions : img files, .DS_Store (macOS)

        root_path = os.path.normpath(self.newFolderPath)
        initial_parent_path, _ = os.path.split(root_path)
        print(root_path+"\n____________________\n")

        self.files_list = [] #output file list
        depth_list = list()

        for curr_path, dirnames, filenames in os.walk(root_path):
    	#curr_path is a STRING, the path to the directory.
    	#dirnames is a LIST of the names of subdirectories.
    	#filenames is a LIST of the names of the non directory files in curr_path
    	#symlink non traités

            curr_rel_path = curr_path[len(initial_parent_path)+1:] #defines current relative path by similar initial parent path part
            curr_rel_path_list = os.path.normpath(curr_rel_path).split(os.sep) #splits current relative path by os separator


            for filename in filenames:
                prev_non_excl_check = True
                curr_non_excl_check = prev_non_excl_check #importing previous state of the "non-exclusion check" (opposite of exclusion check)

                annotations = curr_rel_path_list[:] # annotations are different subfolders browsed
                complete_annotations = annotations[:]
                max_depth = 0

                for i in inclusion_list: #i = inclusionElement

                    if i in filename:
                        curr_non_excl_check = True

                        for e in exclusion_list:
                            if e in filename:
                                if (e == ""):
                                    pass
                                else:
                                    curr_non_excl_check = False
                                    curr_non_excl_check = (prev_non_excl_check and curr_non_excl_check) #any exclusion criteria will make it False (Truth Table)

                        if curr_non_excl_check: # can be True only if no exclusion criteria was found in filename
                            abs_file_path = os.path.join(curr_path,filename)
                            complete_annotations.insert(0,abs_file_path)
                            complete_annotations.append(filename)
                            curr_depth = (len(complete_annotations)-3)
                            depth_list.append(curr_depth)
                            complete_annotations.append(curr_depth)
                            self.files_list.append(complete_annotations)

        if self.files_list:
            max_depth = max(depth_list)
            self.files_list.append(max_depth)
            self.openFileList()
        else:
            print("No file matching condition was found")

    def openFileList(self):
        self.fileContents = list()
        for file in self.files_list:
            fileContent = ""
            try:
                file_path = file[0]
            except TypeError:
                pass

            encodings = getPredefinedEncodings()
            with open(file_path,'rb') as opened_file:
                fileContent = opened_file.read()
                charset_dict = chardet.detect(fileContent)
                detected_encoding = charset_dict['encoding']

                # for chunk in iter(lambda: opened_file.read(CHUNK_LENGTH), ""):
                #     chunks.append('\n'.join(chunk.splitlines()))
                #     i += CHUNK_LENGTH
                #     if i % (CHUNK_NUM * CHUNK_LENGTH) == 0:
                #         fileContent += "".join(chunks)
                #         chunks = list()
                #
                # if len(chunks):
                #     fileContent += "".join(chunks)
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

                # print(self.segmentation_text) #this will be the Segmentation for Output

                # fileContent = normalize('NFC', str(fileContent))
                # fileContents.append(fileContent)

                self.fileContents.append(self.fileContent)

        del self.fileContents[-1]

        # print(self.fileContents)

    def browse(self):
        """Display a folderDialog and select a folder"""
        if self.displayAdvancedSettings:
            folderPathList = QFileDialog.getExistingDirectory(    #Use QFileDialog.getExistingDirectory
                self,
                u'Select Folder(s)',
                self.lastLocation,
            )
            if not folderPathList:
                return
            folderPathList = [os.path.normpath(f) for f in folderPathList]
            self.newFolderPath = u''.join(folderPathList)
            # self.walkThroughDirectory()
            self.lastLocation = os.path.dirname(folderPathList[-1])
            self.updateGUI()
        else:
            folderPath = QFileDialog.getExistingDirectory(    #Use QFileDialog.getExistingDirectory
                self,
                u'Select Folder(s)',
                self.lastLocation,
            )
            if not folderPath:
                return
            self.newFolderPath = u''.join(folderPath)
            self.walkThroughDirectory()
            self.folder = os.path.normpath(folderPath)
            self.lastLocation = os.path.dirname(folderPath)
            self.updateGUI()
            self.sendButton.settingsChanged()

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
        folderPathList = re.split(r' +/ +', self.newFolderPath) #self.newFolderPath = name

        self.depth = str(1)
        self.inclusionsUser = ["marc"]
        self.exclusionsUser = ["image","table"]
        self.samplingRate = 100

        for folderPath in folderPathList:
            self.folders.append((
                self.folder,
                self.depth,
                self.inclusionsUser,
                self.exclusionsUser,
                self.samplingRate,
                folderPath,
                # self.newAnnotationKey,
                # self.newAnnotationValue,
            ))
        self.sendButton.settingsChanged()
        print(folderPathList)

    def updateGUI(self):
        """Update GUI state"""
        if self.displayAdvancedSettings:
            if self.selectedfolderLabels:
                cachedLabel = self.selectedfolderLabels[0]
            else:
                cachedLabel = None
            del self.folderLabels[:]
            print(self.folders)
            if self.folders:
                folderPaths = [f[0] for f in self.folders]
                foldernames = [os.path.basename(p) for p in folderPaths]
                encodings = [f[1] for f in self.folders]
                depth = ['%s' % f[2] for f in self.folders]
                annotations = ['%s' % f[3] for f in self.folders]
                maxfoldernameLen = max([len(n) for n in foldernames])
                maxAnnoLen = max([len(a) for a in annotations])

                for index in range(len(self.folders)):
                    format = u'%-' + str(maxfoldernameLen + 2) + u's'
                    folderLabel = format % foldernames[index]
                    if maxAnnoLen > 4:
                        if len(annotations[index]) > 4:
                            format = u'%-' + str(maxAnnoLen + 2) + u's'
                            folderLabel += format % annotations[index]
                        else:
                            folderLabel += u' ' * (maxAnnoLen + 2)
                    folderLabel += encodings[index]
                    self.folderLabels.append(folderLabel)
            self.folderLabels = self.folderLabels
            if cachedLabel is not None:
                self.sendButton.sendIfPreCallback = None
                self.selectedfolderLabels.listBox.item(
                    cachedLabel
                ).setSelected(1)
                self.sendButton.sendIfPreCallback = self.updateGUI
            if self.newFolderPath:
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
            if self.importfoldernames:
                self.importfoldernamesKeyLineEdit.setDisabled(False)
            else:
                self.importfoldernamesKeyLineEdit.setDisabled(True)
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
