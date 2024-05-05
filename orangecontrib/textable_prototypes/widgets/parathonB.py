__version__ = u"0.0.1"
__authors__ = "Zakari Rabet, Joël Huck, Matthieu Perring, Lara Lambelet"
__maintainer__ = "Zakari Rabet, Joël Huck, Matthieu Perring, Lara Lambelet"
__email__ = "rabet.zakari@gmail.ch, joel.huck@unil.ch, lara.lambelet.1@unil.ch, matthieu.perring@unil.ch"

# Standard imports...
import re, json, csv, os, platform, codecs, inspect


from Orange.widgets import widget, gui, settings
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets.utils.widgetpreview import WidgetPreview
from enum import Enum
from pathlib import Path
from LTTL.Segmentation import Segmentation
from LTTL.Segment import Segment
from LTTL.Segmenter import bypass
from PyQt5.QtWidgets import QMessageBox
from PyQt4.QtGui import QTabWidget, QWidget, QHBoxLayout
from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler,
    JSONMessage, InfoBox, SendButton, AdvancedSettings,
    ProgressBar, pluralize
)

__version__ = "0.0.1"


class Parathon(OWTextableBaseWidget):
    """An Orange widget that lets extract paratextual elements from a text"""
        
    #----------------------------------------------------------------------
    # Widget's metadata...
    name = "Parathon"
    description = "Extract paratextual elements"
    icon = "icons/parathon.svg"
    priority = 12
        
    #----------------------------------------------------------------------    
    # Input and output channels...
    inputs = [
        ('Segmentation', Segmentation, 'inputData',)]
    outputs = [('Segmented data', Segmentation)]

    #----------------------------------------------------------------------
    # Settings...
    
    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    
    want_main_area = False
    
    autoSend = settings.Setting(False)
    displayAdvancedSettings = settings.Setting(False)
    
    
    selectedDictionaries = settings.Setting([])
    selectedSubDictionaries = settings.Setting([])
    subDict = settings.Setting(0)
    

    def __init__(self):
        super().__init__()
        
        # Other attributes...
        self.defaultDict = {}   
        self.dictLabels = []
        self.selectedSubDictionaries = []
        self.subDictLabels = []
        self.subDictUniqueLabels = set()
        self.f2fDictLabels = []
        self.cmcDictLabels = []
        
        
        #-------------------------------------------------------------------
        # GUI...

        self.inputsegmentation = None
        self.newInput = None
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute="infoBox",
            sendIfPreCallback=None
        )
        
        # Advanced settings...
        self.advancedSettings = AdvancedSettings(
            widget=self.controlArea,
            master=self,
            callback=self.showAdvancedSettings,
        )
        
        self.advancedSettings.draw()
        

        # Global box
        self.globalBox = gui.widgetBox(
            widget=self.controlArea,
            box=False,
            orientation='horizontal',
            )
    
        # Dictionaries box
        self.dictBox = gui.widgetBox(
            widget=self.globalBox,
            box="Dictionaries",
            orientation="vertical",
            )
        self.dictListBox = gui.listBox(
            widget=self.dictBox,
            master=self,
            value="selectedDictionaries",
            labels="dictLabels",
            callback=self.getSubDictList,
            tooltip="The list of dictionaries containing the regex to apply",
            )
        
        self.dictBox.setMinimumHeight(40)
        self.dictBox.setMinimumWidth(50)
        self.dictListBox.setSelectionMode(2)
        self.selectedDictionaries = self.selectedDictionaries
        gui.separator(widget=self.dictBox, height=3)
        
        # Create a button box for the two next buttons
        selectionBox = gui.widgetBox(
            widget=self.dictBox,
            box=False,
            orientation='horizontal',
        )
        
        # SelectAll Button
        self.selectAll = gui.button(
            widget=selectionBox,
            master=self,
            label="Select All",
            callback=self.selectAll,
            tooltip="Select every dictionary of the list.",
        )

        # DeselectAll Button
        self.deselectAll = gui.button(
            widget=selectionBox,
            master=self,
            label="Deselect All",
            callback=self.deselectAll,
            tooltip="Deselect every dictionary from the list.",
        )
        
        # Create a button box for the refresh button
        refreshBox = gui.widgetBox(
            widget=self.dictBox,
            box=False,
            orientation='horizontal',
        )
        
        # Reload button
        self.refreshDict = gui.button(
            widget=refreshBox,
            master=self,
            label="Reload",
            callback=self.getDictList,
            tooltip="Refresh dictionary List",
            )

        #-------------------------------------------------------------------
        # Advanced settings box
        self.advancedBox = gui.widgetBox(
            widget=self.globalBox,
            box="Selection Mode",
            orientation="vertical",
        )
        
        # Radio Button
        self.cmcButtons = gui.radioButtonsInBox(
            widget=self.advancedBox,
            master=self,
            box=False,
            btnLabels=['CMC', 'F2F'],
            callback=self.processRadioButton,
            value='subDict',
        )
        
        self.cmcButtons.setMinimumHeight(80)
        self.cmcButtons.setMinimumWidth(40)
        
        self.subDictBox = gui.widgetBox(
            widget=self.advancedBox,
            box=False,
            orientation="vertical",
            )
        
        self.subDictListBox = gui.listBox(
            widget=self.subDictBox,
            master=self,
            value="selectedSubDictionaries",
            labels="subDictLabels",
            callback=self.sendButton.settingsChanged,
            tooltip="The list of sub dictionaries containing the regex to apply",
            )
        self.selectedSubDictionaries = self.selectedSubDictionaries
        
        self.subDictListBox.setSelectionMode(2)
        
        # Create a button box for the two next buttons
        subSelectionBox = gui.widgetBox(
            widget=self.advancedBox,
            box=False,
            orientation='horizontal',
        )
        
        # SelectAll Sub Button
        self.selectAll = gui.button(
            widget=subSelectionBox,
            master=self,
            label="Select All",
            callback=self.subSelectAll,
            tooltip="Select every dictionary of the list.",
        )

        # DeselectAll Sub Button
        self.deselectAll = gui.button(
            widget=subSelectionBox,
            master=self,
            label="Deselect All",
            callback=self.subDeselectAll,
            tooltip="Deselect every dictionary from the list.",
        )
        # GUI separator...
        gui.separator(widget=self.globalBox)
        
        self.advancedSettings.advancedWidgets.append(self.advancedBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()
        
        self.getDictList()
        
        self.sendButton.draw()
        self.infoBox.draw()
        
        self.advancedSettings.setVisible(self.displayAdvancedSettings)
    
    def print(self):
        print(self.selectedSubDictionaries)

    def showAdvancedSettings(self):
        self.advancedSettings.setVisible(self.displayAdvancedSettings)
    
    def inputData(self, Segmentation, language=None, mode=None):
        # Process incoming segmentation
        self.inputsegmentation = Segmentation
        self.language = language
        self.mode = mode
        self.infoBox.inputChanged()
        self.sendButton.sendIf()
        

    # Function for the detection of paralinguistic cues
    def parathonFunction(self, segmentation, AS_SelectionStatus, dicts, f2fList,
                         cmcList, progress_callback):
   
        # Dictionnaire où sera stocké les regex à utiliser selon les choix de CMC ou f2f
        cue_dictionary = {}

        # Si les deux listes sont vides alors cela veut dire que 
        #if not f2fList and not cmcList:
        current_path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )
        if AS_SelectionStatus == False or AS_SelectionStatus and not cmcList and not f2fList:
            # Looper chaque dictionnaire choisi
            print("in the loop")
            for dict in dicts:
                #Ouvrir le dictionnaire qui est sous format json
                f = open(os.path.join(current_path, 'dictionaries', dict+'.json'), 
                    encoding='utf-8')
                data = json.load(f)
                # Aller chercher les keys du dictionnaire
                keys = list(data)
                print("Number of keys " + str(len(keys)))
                # Combiner ces dictionnaires dans cue_dictionary
                for key in keys:
                    cue_dictionary[key] = data[key]
                print(len(list(cue_dictionary)))
        elif AS_SelectionStatus==True and f2fList or cmcList:
            # Looper chaque dictionnaire choisi
            print("in the advanced loop")
            for dict in dicts:
                #Ouvrir le dictionnaire qui est sous format json
                f = open(os.path.join(current_path, 'dictionaries', dict+'.json'), 
                    encoding='utf-8')
                data = json.load(f)
                # Aller chercher les keys du dictionnaire
                keys = list(data)
                # On va chercher la liste qui n'est pas vide (f2f ou CMC) et on déclare la variable selection et la variable index
                if f2fList:
                    selection = f2fList
                    index = 0
                if cmcList:
                    selection = cmcList
                    index = 1
            # Une fois ces deux variables déclarées on utilise leur valeur
            # Pour chaque CMC ou f2f choisi on va aller prendre les regex associées dans chaque dictionnaire puis l'ajouter à un nouveau dictionnaire (--> cue_dictionary)
                for element in selection:
                    for key in keys : 
                        regex1 = re.escape(element)+r"\W"
                        regex2 = re.escape(element)+r"\Z"
                        if re.search(regex1, str(data[key][index])) or re.search(regex2, str(data[key][index])):
                            cue_dictionary[key] = data[key]

        # Initialize list of output segments.
        segments = list()

        # Iterate over input segments...
        for segment in segmentation:
        
            # Get string index and annotations for this segment.
            str_index = segment.str_index
            annotations = segment.annotations
        
            # Here we split the text into tokens. Emojis count as tokens. Some punctuation
            # is included as a word character so we may take into account,
            # for example, *corrections and _whatsapp formatting_.
            tokens = re.findall(r"[\w'*_~]+|[.,!?;:)\*]+|\s+|[\U00010000-\U0010ffff]|.",
                                segment.get_content(), flags=re.UNICODE)
            position = segment.start or 0
            for token in tokens:
                start = position
                position = position + len(token)
                end = position

                matches_for_token = list()
                for key in cue_dictionary:
                    # Some of the regexes require flags.
                    # This part allows us to use those flags.
                    try:
                        if cue_dictionary[key][3]:
                            if re.search(key, token, flags=eval(cue_dictionary[key][3])):
                                matches_for_token.append([token, cue_dictionary[key], start, end])
                    except IndexError:
                        if re.search(key, token):
                            matches_for_token.append([token, cue_dictionary[key], start, end])
                # Append properties to lists for later
                f2f_properties = list()
                cmc_properties_main = list()
                cmc_properties_sub = list()
                if len(matches_for_token) > 1:
                    for match in matches_for_token:
                        f2f_properties.append(match[1][0])
                        cmc_properties_main.append(match[1][1])
                        cmc_properties_sub.append(match[1][2])
                elif len(matches_for_token) == 1:
                    f2f_properties.append(matches_for_token[0][1][0])
                    cmc_properties_main.append(matches_for_token[0][1][1])
                    cmc_properties_sub.append(matches_for_token[0][1][2])
                    
                # Create segment for token and append to output segments...
                if f2f_properties:
                    my_annotations = annotations.copy()
                    my_annotations.update({
                        "f2f": ", ".join(sorted(set(f2f_properties))),
                        "cmc_main": ", ".join(sorted(set(cmc_properties_main))),
                        "cmc_sub": ", ".join(sorted(set(cmc_properties_sub))),
                    })
                    segments.append(
                        Segment(
                            str_index=str_index, 
                            start=start, 
                            end=end, 
                            annotations=my_annotations,
                        )
                    )
                
            # Advance progress bar.
            progress_callback()
        
        # Create and return output segmentation.
        return Segmentation(segments, self.captionTitle)
    
    def sendData(self):
        
        # True si advanced setting coché et False sinon
        AS_SelectionStatus = self.displayAdvancedSettings
        print("\nAdvanced Settings is selected : " + str(AS_SelectionStatus))

        current_path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )
        print(current_path)
        f = open(os.path.join(current_path, 'codeToType.json'), 
                    encoding='utf-8')
        codeToType = json.load(f)
        print(codeToType)
        codeToTypeInverse = dict((v, k) for k, v in codeToType.items())
        print(codeToTypeInverse)
        # Dictionnaires sélectionnés
        selectedDictsLabels = [self.dictLabels[item] for item in self.selectedDictionaries]
        print("Length of selected labels : " + str(len(selectedDictsLabels)))
        print(selectedDictsLabels)
        print("Selected dictionnaries " + str(selectedDictsLabels))
        #selectedDictsLabels [codeToType[item] for item in ]

        # Sous-Dictionnaires (les CMTs ou f2fs) sélectionnés
        if AS_SelectionStatus == True:
            selectedSubDictsLabelsWhole = [list(self.subDictUniqueLabels)[item] for item in self.selectedSubDictionaries]
            selectedSubDictsLabels = [codeToTypeInverse[item] for item in selectedSubDictsLabelsWhole]
            print("Selected subDicts = " + str(selectedSubDictsLabels))

        if AS_SelectionStatus == True and len(selectedSubDictsLabels)==0:
            selectedDictsLabels = []
            print("NO DICTS")

        # Determine ici le mode de sélection coché
        if isinstance(self.subDict, int) and AS_SelectionStatus==True:
            selectedMode = ['CMC', 'F2F'][self.subDict]
            # Assigner les valeurs de CMTs ou f2fs à des listes
            if selectedMode == "CMC":
                cmcList = selectedSubDictsLabels
                f2fList = []
            
            if selectedMode == "F2F":
                cmcList = []
                f2fList = selectedSubDictsLabels
        else:
            cmcList = []
            f2fList = []
            print("The selected sublists " + str(cmcList), str(f2fList))
            print("Neither CMC or F2F are selected")

        # Preprocess and send data
        if not self.inputsegmentation:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Segmented data', None, self)
            return
        # if advancedSettings: # renommer selon le code
            # return
            
        if not self.selectedDictionaries:
            self.infoBox.setText(u'Please select at least 1 dictionary', 
                                 'warning')
            self.send('Segmented data', None, self)
            return


        self.infoBox.setText(u"Processing, please wait...", "warning")
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(
            self,
            iterations=len(self.inputsegmentation)
        )
        
        # On va chercher l'input et on lui applique la fonction parathon
        parathonResult = self.parathonFunction(self.inputsegmentation,
                                               AS_SelectionStatus,
                                               selectedDictsLabels, f2fList,
                                               cmcList, progressBar.advance)

        # Remplacer cette ligne de code par celle qui transforme parathonResult en segmentation (?) pour être envoyé comme output
        #bypassed_data = bypass(self.inputsegmentation, label=self.captionTitle)

        self.segmentation = parathonResult
        progressBar.finish()        
        
        self.controlArea.setDisabled(False)
        message = u'%i segment@p sent to output.' % len(self.segmentation)
        message = pluralize(message, len(self.segmentation))
        self.infoBox.setText(message)
        # Send token...
        self.send('Segmented data', self.segmentation, self)
        #self.send('Segmented data', parathonResult, self)
        
        self.sendButton.resetSettingsChangedFlag()
        
    
    def getDictList(self):        
        # Setting the path of the file and retrieving file dictionary names
        actualFolderPath = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )
        folderPath = os.path.join(actualFolderPath, "dictionaries")
        
        self.defaultDict = {} # nom du fichier et contenu du fichier
        for file in os.listdir(folderPath):
            if file.endswith(".json"):
                # Gets json file name and substracts .json extension
                fileName = os.path.splitext(os.path.basename(file))[0]
                self.defaultDict.update({fileName: ''})
                
                # Open json files and stores their content
                try:
                    filePath = os.path.join(folderPath, file)
                    fileOpened = codecs.open(filePath, encoding='utf-8')
                    fileLoaded = json.load(fileOpened)
                    self.defaultDict[fileName] = fileLoaded
                except IOError:
                    QMessageBox.warning(
                        None,
                        'Parathon',
                        "Couldn't open file.",
                        QMessageBox.Ok
                    )
        
        # Sorts defaultDict and display the right titles in the listBox            
        self.dictLabels = sorted(self.defaultDict.keys())
    

    

    def getSubDictList(self):
        # Sets lists to contain sub labels
        self.cmcDictLabels = []
        self.f2fDictLabels = []
        # Gets all sub labels and stoxks them in the right list
        for key in self.selectedDictionaries:
            subDictLabelsList = self.defaultDict[self.dictLabels[key]].values()
            for subDictLabel in subDictLabelsList:
                self.f2fDictLabels.append(subDictLabel[0])
                self.cmcDictLabels.append(subDictLabel[1])
        self.processRadioButton()
    


    # Displays the right sub labels according to the selected dictionnaries
    def processRadioButton(self):  
        self.subDictLabels = []
        tempList = []
        self.subDictUniqueLabels = set()
        # Defines dictionaries to link sub labels code to their type
        current_path = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )
        print(current_path)
        f = open(os.path.join(current_path, 'codeToType.json'), 
                    encoding='utf-8')
        codeToType = json.load(f)
        
        
        if self.subDict == 0:
            for elem in self.cmcDictLabels:
                if ',' in elem:
                    tempElems = elem.split(', ')
                    for item in tempElems:
                        tempList.append(codeToType[item])
                else:
                    tempList.append(codeToType[elem])
            self.subDictUniqueLabels.update(tempList)
        elif self.subDict == 1:
            for elem in self.f2fDictLabels:
                if ',' in elem:
                    tempElems = elem.split(', ')
                    for item in tempElems:
                        tempList.append(codeToType[item])
                else:
                    tempList.append(codeToType[elem])
            self.subDictUniqueLabels.update(tempList)
        else:
            print(self.subDict)
            QMessageBox.warning(
                        None,
                        'Parathon',
                        "Unvalid interaction.",
                        QMessageBox.Ok
                    )
        self.subDictLabels = list(self.subDictUniqueLabels)
        self.selectedSubDictionaries = list(range(len(self.subDictLabels)))
        self.sendButton.settingsChanged() 
    
    def selectAll(self):
        self.selectedDictionaries = list(range(len(self.dictLabels)))
        self.getSubDictList()
  
    def subSelectAll(self):
        self.selectedSubDictionaries = list(range(len(self.subDictLabels)))
    
    def deselectAll(self):
        self.selectedDictionaries = []
        self.getSubDictList()
    
    def subDeselectAll(self):
        self.selectedSubDictionaries = []
    
    def setCaption(self, title):
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)
        

        
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from LTTL.Input import Input
    
    myApplication = QApplication(sys.argv)
    myWidget = Parathon()
    #myWidget.inputData(Input('03/02/2021, 19:30 - sorcha: *LMAO'))
    myWidget.inputData(Input('a simple example :) ;)'))
    myWidget.show()
    myApplication.exec_()
    myWidget.saveSettings()
    #WidgetPreview(Parathon).run()
    