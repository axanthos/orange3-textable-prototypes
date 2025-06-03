from functools import partial
import time
import json
import dateparser

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, ProgressBar,
    InfoBox, SendButton, pluralize, Task
)

from LTTL.Segmentation import Segmentation
from LTTL.Input import Input


# Using the threaded version of LTTL.Segmenter to create
# a "responsive" widget.
import LTTL.SegmenterThread as Segmenter

from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview

from youtube_comment_downloader import *
# pour tester l'url
import requests

import re

import http

from PyQt5.QtWidgets import QMessageBox
from Orange.widgets.settings import Setting

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

"""
Sources that helped us code our widget "YouGet":
    - ChatGPT (including GPT-3.5 and limited GPT-4o mini): Used ChatGPT to help with 
    regex to only accept YouTube URLs ("https://chatgpt.com/
    share/6800c404-cb74-8000-afef-e321b9517c47")
    - Draw.io: Used Draw.io for the YouGet logo (https://app.diagrams.net/)
    - Widget SciHub: for sections of code where both widgets have in common
     (https://github.com/sarahperettipoix/orange3
    -textable-prototypes/blob/master/orangecontrib/textable_prototypes/widgets/SciHubatorTest.py)
"""

__version__ = '0.0.1'
__author__ = "Virgile Albasini, Sophie Ward, Lorelei Chevroulet, Vincent Joris "
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

class YouGet(OWTextableBaseWidget):
    """Demo Orange3-Textable widget"""

    name = "YouGet"
    description = "Widget that downloads comments from a youtube URL"
    icon = "icons/YouGet.svg"
    priority = 99

    # Input and output channels (remove if not needed)...
    inputs = []
    outputs = [("New segmentation", Segmentation)]

    # Copied verbatim in every Textable widget to facilitate
    # settings management.
    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    # Settings...
    # url = settings.Setting("https://www.youtube.com/watch?v=ScMzIvxBSi4")
    url = settings.Setting("")

    # widget will fetch n=0 comments -> default is all
    # n_desired_comments = 0
    # n_desired_comments = 1 # for testing


    want_main_area = False

    #---------- START: The following section of code has been borrowed from SciHub.py ----------
    # (https://github.com/sarahperettipoix/orange3-textable-prototypes/
    # blob/master/orangecontrib/textable_prototypes/widgets/SciHubatorTest.py)
    DOIs = Setting([])
    URLLabel = Setting([])
    selectedURLLabel = Setting([])
    new_url = Setting("")
    autoSend = settings.Setting(False)
    importDOIs = Setting(True)
    importDOIsKey = Setting(u'url')
    DOI = Setting(u'')
    n_desired_comments = Setting("")
    sortBy = Setting("")
    #---------- END: End of the section of code borrowed from SciHub.py ----------


    def __init__(self, *args, **kwargs):
        """
        Initializing the widget with GUI components and internal state.
        
        Part of the GUI layout and URL management logic is adapted from:
        https://github.com/sarahperettipoix/orange3-textable-prototypes/blob/master/orangecontrib/textable_prototypes/widgets/SciHubatorTest.py
        """
        super().__init__(*args, **kwargs)
        #---------- START: The following section of code has been borrowed from SciHub.py ----------
        # (https://github.com/sarahperettipoix/orange3-textable-prototypes/blob/
        # master/orangecontrib/textable_prototypes/widgets/SciHubatorTest.py)

        # self.URLLabel = list()
        # self.selectedURLLabel = list()
        # self.new_url = u''
        # self.extractedText = u''
        # self.DOI = u''
        # self.DOIs = list()
        #---------- END: End of the section of code borrowed from SciHub.py ----------

        # Attributes...
        self.inputSegmentationLength = 0

        # This attribute stores scraped comments to prevent duplicate
        # queries and make the widget both faster and less resource-intensive.
        # Comments are stored as follows:
        # 'url': list of comments on url
        self.cached_comments = {}

        # This attribute stores a per-widget number of comments desired as
        # output. This can be changed by the user at any time via the GUI.
        # n_desired_comments = 1
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
        #---------- START: The following section of code has been borrowed from SciHub.py ----------
        # (https://github.com/sarahperettipoix/orange3-textable-prototypes/blob/master/orangecontrib
        # /textable_prototypes/widgets/SciHubatorTest.py)

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
                u"The list of URLs whose comments will be imported.\n"
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
            disabled = True,
        )
        self.clearAllButton = gui.button(
            widget=URLBoxCol2,
            master=self,
            label=u'Clear All',
            callback=self.clearAll,
            tooltip=(
                u"Remove all URLs from the list."
            ),
            disabled = True,
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
            value='new_url',
            orientation='horizontal',
            label=u'URL(s):',
            labelWidth=101,
            callback=self.updateURLBoxButtons,
            tooltip=(
                u"The URL(s) that will be added to the list when\n"
                u"button 'Add' is clicked.\n\n"
                u"Successive URLs must be separated with ' , ' \n"
                u"Their order in the list will be the same as\n"
                u"in this field."
            ),
        )
        advOptionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'More Options',
            orientation='vertical',
            addSpace=False,
        )
        self.optionLine1 = gui.widgetBox(
            widget=advOptionsBox,
            orientation='horizontal',
            addSpace=False,
        )
        commentsSelector = gui.comboBox(
            widget=advOptionsBox,
            master=self,
            orientation='horizontal',
            value='n_desired_comments',
            label='Select number of comments:',
            tooltip='Default 0 is all comments.',
            items=[1, 5, 10, 100, 1000, 10000, "No limit"],
            sendSelectedValue=True,
            labelWidth=220,
        )

        self.sortByFilter = gui.widgetBox(
            widget=advOptionsBox,
            orientation='horizontal',
            addSpace=False,
        )

        sortBy = gui.comboBox(
            widget=self.sortByFilter,
            master=self,
            value='sortBy',
            label=u'Sort by:',
            tooltip= "Choose how the comment will be sorted",
            orientation='horizontal',
            sendSelectedValue=True,
            items=["Date", "Popularity"],
            labelWidth=220,
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
            disabled = True,
        )
        gui.rubber(self.controlArea)
        # So that the "Add" button is not gray
        self.updateURLBoxButtons()
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()

        #---------- END: End of the section of code borrowed from SciHub.py ----------

        # no idea why but this allows to save settings when quit and reload
        self.fileListbox.update()
        URLBoxLine1.update()
        self.DOIs = list(set(self.DOIs))
        self.URLLabel = self.DOIs
        self.selectedURLLabel = self.DOIs
        commentsSelector.update()
        self.n_desired_comments = self.n_desired_comments
        self.sortBy = self.sortBy
        self.sendButton.settingsChanged()

    def sendData(self):
        """
        Perform every required check and operation 
        before calling the method that does the actual 
        processing.
        """
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
        """
        Actual processing takes place in this method,
        which is run in a worker thread so that GUI stays
        responsive and operations can be cancelled.
        """
        # At start of processing, set progress bar to 1%.
        # Within this method, this is done using the following
        # instruction.
        self.signal_prog.emit(1, False)
        urls = [self.url]
        # Indicate the total number of iterations that the
        # progress bar will go through (e.g. number of input
        # segments, number of selected files, etc.), then
        # set current iteration to 1.
        # number of segment ça veut dire number of url
        max_itr = len(urls)
        cur_itr = 1
        urls = self.DOIs

        # Actual processing...
        # For each progress bar iteration...
        #for _ in range(int(self.numberOfSegments)):

        for url in urls:

            # Update progress bar manually...
            self.signal_prog.emit(int(100*cur_itr/max_itr), False)
            cur_itr += 1

            # If int(self.numberOfSegments) == 1:
            if len(urls) == 1:
                # self.captionTitle is the name of the widget,
                # which will become the label of the output
                # segmentation.
                label = self.captionTitle
            else:
                label = None # will be set later.

            # print('cache checks happens below')
            # # Check if we already have an entry for the url in the cached
            # # comments. If yes, we return it; if not, we scrape and cache.
            # print(
            #     f'▓▓————————▓▓ processData(): cache check'
            # # )
            # print(f'▓ cache check: url in cached comments? :\n'
            #       f'▓ ——>{url in self.cached_comments}')
            if url in self.cached_comments:
                # print(f'▓ using the cache')
                comments_ycd = self.cached_comments.get(url)
                # print(f'▓ found {len(comments_ycd)} comments')
            else:
                # print(f'▓ not using the cache')
                comments_ycd = self.scrape(url)
                # print(f'▓ found {len(comments_ycd)} comments')
                self.cached_comments[url] = comments_ycd
                # print(f'▓ saved {len(self.cached_comments[url])} comments')
            # print('▓▓————————▓▓ cache check happened! ▓▓————————▓▓')

            # Placeholder limit for testing.
            # limit = 10
            # dont know how to do infinite, so if "no limit" is selected, its value will
            # be 1 milliard
            if self.n_desired_comments == "No limit":
                limit = 10000000
            else :
                limit = int(self.n_desired_comments)

            # While we cache everything that was scraped, we only return as
            # many as the user requested.
            if limit != 0:
                # print(f'▓ desired limit is: {limit} \n'
                #       f'▓ with type: {type(limit)}')
                # comments_ycd = comments_ycd[0:limit]
                if self.sortBy == "Date":
                    comments_ycd = sorted(
                        comments_ycd,
                        key=lambda x: dateparser.parse(x["time"]),
                        reverse=False  # ou True pour plus récents d'abord
                    )
                elif self.sortBy == "Popularity":
                    comments_ycd = sorted(comments_ycd, key=lambda x: int(x["votes"]), reverse=True)
                # print(f'▓ trimmed comments to {limit} => {len(comments_ycd)} out.')

            for chose in comments_ycd:
                myInput = Input(str(chose["text"]), label)

                segment = myInput[0]
                segment.annotations["author"] = str(chose["author"])
                segment.annotations["url"] = url
                segment.annotations["likes"] = str(chose["votes"])
                # parsed_time = dateparser.parse(chose["time"])
                # segment.annotations["time"] = parsed_time.strftime('%Y-%m-%d')
                segment.annotations["time"] = str(chose["time"])
                myInput[0] = segment

                self.createdInputs.append(myInput)

            # Cancel operation if requested by user...
            time.sleep(0.00001) # Needed somehow!
            if self.cancel_operation:
                self.signal_prog.emit(100, False)
                return

        # Update infobox and reset progress bar...
        self.signal_text.emit("Step 2/2: Post-processing...",
                              "warning")
        self.signal_prog.emit(1, True)

        # If there's only one LTTL.Input created, it is the
        # widget's output...
        # if len(urls) == 1:
        if len(self.createdInputs) == 1:
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
        """
        All operations following the successful termination
        of self.processData
        """
        # Get the result value of self.processData.
        processed_data = f.result()

        # If it is not None...
        if processed_data:
            message = f"{len(processed_data)} segment@p sent to output "
            message = pluralize(message, len(processed_data))
            numChars = 0
            for segment in processed_data:
                segmentLength = len(Segmentation.get_data(segment.str_index))
                numChars += segmentLength
            message += f"({numChars} character@p)."
            message = pluralize(message, numChars)
            self.infoBox.setText(message)
            self.send("New segmentation", processed_data)

    # The following method should be copied verbatim in
    # every Textable widget.
    def setCaption(self, title):
        """
        Register captionTitle changes and send if needed
        """
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
        """
        Clear created inputs
        """
        # List of inputs/URLs
        for i in self.createdInputs:
            # Database: clearing ID of URL to clear, set value to None (= erase data)
            Segmentation.set_data(i[0].str_index, None)
        # GUI: clears contents of list
        del self.createdInputs[:]

    def onDeleteWidget(self):
        """
        Clear created inputs on widget deletion
        """
        self.clearCreatedInputs()

    def youtube_video_existe(self, urll):
        """
        This function tests the Internet connection.
        """
        # print(
        #     f'▓▓▓▓▓▓▓▓▓▓▓▓ youtube_video_existe(urll)\n'
        #     f'▓ youtube_video_existe() —— urll={urll}'
        # )
        # Mimicking a browser so there is no blockage when requesting a URL
        headers = {
            "User-Agent": "Mozilla/5.0"            
        }
        try:
            response = requests.get(urll, headers=headers, timeout=5)
            # print(f'▓ youtube_video_existe() —— headers test: {response}')
            # print('▓ youtube_video_existe() —— work done :) returning.')
            # print('▓▓▓▓▓▓▓▓▓▓▓▓ scrape() ▓▓▓▓▓▓▓▓▓▓▓▓')
            return response.status_code
        except requests.RequestException:
            # print(f'▓ youtube_video_existe() —— headers errors')
            # print('▓ youtube_video_existe() —— work done :) returning.')
            # print('▓▓▓▓▓▓▓▓▓▓▓▓ scrape() ▓▓▓▓▓▓▓▓▓▓▓▓')
            return False

    def scrape(self, url) -> list:
        """
        Sets up a virtual browser through YoutubeCommentDownloader and uses
        it to scrape all comments on a given url, returning them as a list.
        """
        # print(
        #     f'▓▓▓▓▓▓▓▓▓▓▓▓ scrape(url)'
        #     f'▓ scrape() —— url={url}'
        # )

        # Fetch the comments
        downloader = YoutubeCommentDownloader()
        comments = downloader.get_comments_from_url(url,language='en')
        every_comment = [x for x in comments]
        # Prints number of comments found
        # print(
        #     f'▓ scrape() —— returning {len(every_comment)} comment(s)'
        # )
        # print('▓ scrape() —— work done :) returning.')
        # print('▓▓▓▓▓▓▓▓▓▓▓▓ scrape() ▓▓▓▓▓▓▓▓▓▓▓▓')
        # Returns the list of all comments collected
        return every_comment
    #---------- START: The following section of code has been borrowed from SciHub.py ----------
    # (https://github.com/sarahperettipoix/orange3-textable-prototypes/
    # blob/master/orangecontrib/textable_prototypes/widgets/SciHubatorTest.py)

    def clearAll(self):
        """
        Remove all DOIs from DOIs attr
        """
        del self.DOIs[:]
        del self.selectedURLLabel[:]
        self.sendButton.settingsChanged()
        self.URLLabel = self.URLLabel
        self.clearAllButton.setDisabled(True)

    def remove(self):
        """
        Remove URL from DOIs attr
        """
        if self.selectedURLLabel:
            index = self.selectedURLLabel[0]
            self.DOIs.pop(index)
            del self.selectedURLLabel[:]
            self.sendButton.settingsChanged()
            self.URLLabel = self.URLLabel
        self.clearAllButton.setDisabled(not bool(self.URLLabel))

    def add(self):
        """
        Add Urls to URLs attr
        DOIList = re.split(r',', self.new_url)
        """
        # String of comma-separated URLs (url1, url2, ...)
        # re.split(r'\s*,\s*') splits strong on commas, allows whtiespace
        DOIList = [url.strip() for url in re.split(r'\s*,\s*', self.new_url)]

        # Saves list of added URLs
        old_urls = list(self.DOIs)
        # print("old url "+str(old_urls))

        if DOIList:
            # Create set to delete all duplicate URLs
            tempSet = DOIList
            def_set = set(tempSet)
            # Warnings
            # Invalid format
            not_an_url = False
            # Video does not exist
            not_available = False
            # Duplicate
            doublon = False
            # Numbers of each problem
            nombre_de_problemes_not_url = 0
            nombre_de_problemes_not_available = 0
            nombre_de_problemes_doublon = 0
            # print(tempSet)
            indexx = 0
            list_indexx = []

            # Loop over each new URL to validate it
            for single_url in tempSet:
                list_indexx.append(True)
                for past_url in old_urls:
                    # Mark as duplicate if it already exists in old_urls
                    if single_url == past_url:
                        doublon = True
                        # print("il y a un doublon ici")
                        list_indexx[indexx] = False
                        nombre_de_problemes_doublon += 1

                # If 1 or more URL(s) in a list are not in the form
                # of a URL from Youtube, the URL will not be added
                # Regex to only accept YouTube URL format
                # -- With the help of ChatGPT
                # ("https://chatgpt.com/share/6800c404-cb74-8000-afef-e321b9517c47") --
                if not re.match(r"^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$", 
                single_url):
                    not_an_url = True
                    # Each element is True or False depending
                    # on whether the URL passed all checks
                    if list_indexx[indexx] != False:
                        list_indexx[indexx] = False
                        nombre_de_problemes_not_url += 1

                # Check if the URL exists
                elif not youtube_video_exists(single_url):
                    not_available = True
                    # Each element is True or False depending on whether the URL passed all checks
                    if list_indexx[indexx] != False:
                        list_indexx[indexx] = False
                        nombre_de_problemes_not_available += 1

                # Check that the URL is not a duplicate and is available
                if doublon == False and not_an_url == False and not_available == False:
                    # print("la ou les url sont clean")
                    list_indexx[indexx] = True
                # If this is the case, URL is added to the list indexx
                indexx += 1

            # If an URL is a duplicate, then there is an error message
            if doublon == True:
                QMessageBox.information(
                    # The error message gives the numbers of duplicates found
                    None, "YouGet", 
                    f"Error Message:<br><br>{nombre_de_problemes_doublon} duplicate URL(s) found and deleted.",
                    QMessageBox.Ok
                )

            # If a URL is not available or misspelled
            if not_available == True:
                QMessageBox.information(
                    # The error message gives the numbers of non available URLs found
                    None, "YouGet", 
                    f"Error Message:<br><br>{nombre_de_problemes_not_available} URL(s) are not valid YouTube videos",
                    QMessageBox.Ok
                )

            # If a URL is not a URL
            if not_an_url == True:
                QMessageBox.information(
                    # The error message gives the numbers of non URLs found
                    None, "YouGet", 
                    f"Warning Message:<br><br>{nombre_de_problemes_not_url} element(s) are not YouTube URLs or please check your internet connection.",
                    QMessageBox.Ok
                )

            # Removes the False URL(s) and keeps the rest
            temp_set_liste = list(tempSet)
            filtered_list = []
            for i, keep in enumerate(list_indexx):
                if keep:
                    filtered_list.append(temp_set_liste[i])
            # Only URL(s) that pass all checks are kept and added to self.DOIs  
            self.DOIs += list(filtered_list)
            self.DOIs = list(set(self.DOIs))
            self.URLLabel = self.DOIs
            self.selectedURLLabel = self.DOIs
            self.n_desired_comments = self.n_desired_comments


        self.URLLabel = self.URLLabel
        # Update on buttons
        # Disable "Clear All" button if there are no URL(s)
        self.clearAllButton.setDisabled(not bool(self.DOIs))
        # Trigger settings changed for the send button
        self.sendButton.settingsChanged()

    def addDisabledOrNot(self):
        """
        Disables the add button if no new URL is entered
        """
        self.addButton.setDisabled(not bool(self.new_url))

    def updateURLBoxButtons(self):
        """
        Update state of the "Add" and "Remove" buttons
        """
        self.addButton.setDisabled(not bool(self.new_url))
        self.removeButton.setDisabled(not bool(self.selectedURLLabel))

    #---------- END: End of the section of code borrowed from SciHub.py ----------

    def updateGUI(self):
        """
        This method is intended to refresh or modify GUI elements based on the current
        internal state or user interactions.
        """
        pass

if __name__ == '__main__':
        WidgetPreview(YouGet).run()


def youtube_video_exists(url):
    """
    This function checks whether a YouTube video exists and is playable at a given URL.
    """
    # Mimicking a browser so there is no blockage when requesting a URL
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # Sending an HTTP GET request to the YouTube video URL
    # Grab data with the help of the internet
    try:
        response = requests.get(url, headers=headers)
        # Check for successful response
        # 200 means success, != 200 means failure
        if response.status_code != 200:
            return False

        # Extract the YouTube video content content
        html = response.text

        # Extraction du JSON "ytInitialPlayerResponse"
        initial_data_match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', html)
        # print(initial_data_match)

        # If nothing is found, return False and print Error
        if not initial_data_match:
            # print("Impossible d'extraire ytInitialPlayerResponse")
            return False

        # Parse extracted JSON into a Python dict
        data = json.loads(initial_data_match.group(1))
        # print(data)
        # Check playability status
        status = data.get("playabilityStatus", {}).get("status", "UNKNOWN")

        # Indicate the URL's playability status
        if status == "OK":
            # "OK" means that the URL is available
            return True
        else:
            # If video not playable, return False
            # print(f"Statut de lecture : {status}")
            return False

    # Catch errors during the request
    except Exception as e:
        # print(f"Erreur lors de l'analyse : {e}")
        return False