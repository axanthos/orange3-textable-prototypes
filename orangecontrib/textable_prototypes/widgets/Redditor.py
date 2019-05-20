"""
Class Redditor
Copyright 2019 University of Lausanne
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

__version__ = u"0.0.1"
__author__ = "Nahuel Degonda, Olivia Edelman, Loris Rimaz"
__maintainer__ = "Nahuel Degonda, Olivia Edelman, Loris Rimaz"
__email__ = "nahuel.degonda@unil.ch, olivia.edelman@unil.ch, loris.rimaz@unil.ch"

# Standard imports...
import praw
import prawcore

from Orange.widgets import widget, gui
from Orange.widgets.settings import Setting

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar
)

from LTTL.Segmentation import Segmentation
import LTTL.Segmenter as Segmenter
from LTTL.Segment import Segment
from LTTL.Input import Input

from datetime import datetime

import re

class Redditor(OWTextableBaseWidget):
    """An Orange widget to scrape Reddit"""

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Redditor"
    description = "Scrap on Reddit"
    icon = "icons/Reddit-alien.png"
    priority = 20

    #----------------------------------------------------------------------
    # Channel definitions...

    # inputs = []
    outputs = [("Segmentation", Segmentation)]

    #----------------------------------------------------------------------
    # GUI layout parameters...

    want_main_area = False
    resizing_enabled = True

    #----------------------------------------------------------------------
    # Query settings...

    mode = Setting("Subreddit")
    subreddit = Setting(u'')
    URL = Setting(u'')
    fullText = Setting(u'')

    # Filters settings...

    sortBy = Setting("Hot")
    sortByFT = Setting("Relevance")
    postedAt = Setting("All")
    amount = Setting(1)

    # Include settings...

    includeComments = Setting(True)
    includeImage = Setting(False)

    # resultBox settings...

    labelsPanier = Setting(list())

    # Data settings...

    queryList = Setting(list())
    annotList = Setting(list())

    #----------------------------------------------------------------------
    # Praw instance

    reddit = praw.Reddit(
        client_id="aHeP3Ub7aILvsg",
        client_secret=None,
        username="RedditorApp",
        password="RedditorProg2019",
        user_agent="Redditor by /u/RedditorApp"
    )

    #----------------------------------------------------------------------
    # Temporary inputs and data lists

    createdInputs = list()
    listeTempAnnot = list()
    listeTempPosts = list()

    def __init__(self):
        """Init of the module: UI and variables definition"""
        super().__init__()

        # queryBox indexes
        self.indicesPanier = list()

        #----------------------------------------------------------------------
        # User interface...

        self.infoBox = InfoBox(
            widget=self.controlArea,
        )

        #-------------------------#
        #    Main widget boxes    #
        #-------------------------#

        sourceBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Source',
            orientation='vertical',
            addSpace=False,
        )

        self.filterBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Filters',
            orientation='vertical',
            addSpace=False,
        )

        self.includeOuterBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Include',
            orientation='vertical',
            addSpace=False,
        )

        panierBox = gui.widgetBox(
            widget=self.controlArea,
            orientation='vertical',
            box=u'Selection',
            addSpace=False,
        )

        #-------------------#
        #    Send button    #
        #-------------------#

        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.send_data,
            infoBoxAttribute='infoBox',
        )

        #------------------------#
        #   Query box elements   #
        #------------------------#

        self.choiceBox = gui.comboBox(
            widget=sourceBox,
            master=self, 
            value='mode', 
            label="Mode:",
            callback=self.mode_changed,
            tooltip= "Choose mode",
            orientation='horizontal',
            sendSelectedValue=True,
            items=["Subreddit", "URL", "Full text"],
            labelWidth=120,
        )

        self.modeBox = gui.widgetBox(
            widget=sourceBox,
            orientation='horizontal',
            addSpace=False,
        )

        self.urlBox = gui.widgetBox(
            widget=sourceBox,
            orientation='horizontal',
            addSpace=False,
        )

        gui.lineEdit(
            widget=self.urlBox,
            master=self,
            value='URL',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            label=u'Search with URL:',
            labelWidth=120,
        )

        self.subredditBox = gui.widgetBox(
            widget=sourceBox,
            orientation='horizontal',
            addSpace=False,
        )

        gui.lineEdit(
            widget=self.subredditBox,
            master=self,
            value='subreddit',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            label=u'reddit.com/r/...:',
            labelWidth=120,
        
        )
        self.fullTextBox = gui.widgetBox(
            widget=sourceBox,
            orientation='horizontal',
            addSpace=False,
        )
        
        gui.lineEdit(
            widget=self.fullTextBox,
            master=self,
            value='fullText',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            label=u'Search on reddit:',
            labelWidth=120,
        )

        #----------------------------#
        #    Filters box elements    #
        #----------------------------#

        self.subredditFilter = gui.widgetBox(
            widget=self.filterBox,
            orientation='horizontal',
            addSpace=False,
        )

        gui.comboBox(
            widget=self.subredditFilter,
            master=self,
            value='sortBy',
            label=u'Sort by:',
            tooltip= "Choose mode to sort your posts",
            orientation='horizontal',
            sendSelectedValue=True,
            callback=self.checkSubredditSortMode,
            items=["Hot", "New", "Controversial", "Top", "Rising"],
            labelWidth=120,
        )

        self.fullTextFilter = gui.widgetBox(
            widget=self.filterBox,
            orientation='horizontal',
            addSpace=False,
        )

        gui.comboBox(
            widget=self.fullTextFilter,
            master=self, 
            value='sortByFT', 
            label="Sort by:",
            tooltip= "Choose mode",
            orientation='horizontal',
            sendSelectedValue=True,
            callback=self.checkSearchSortMode,
            items=["Relevance", "Top", "New", "Comments"],
            labelWidth=120,
        )

        self.timeBox = gui.widgetBox(
            widget=self.filterBox,
            orientation='horizontal',
            addSpace=False,
        )

        gui.comboBox(
            widget=self.timeBox,
            master=self,
            value='postedAt',
            label=u'Time:',
            tooltip= "Choose mode to sort your posts",
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            sendSelectedValue=True,
            items=["All", "Past day", "Past hour", "Past month", "Past year"],
            labelWidth=120,
        )

        gui.spin(
            widget=self.filterBox,
            master=self,
            value="amount",
            minv=1,
            maxv=200,
            label="Amount of posts:",
            labelWidth=120,
            orientation="horizontal",
            callback=self.sendButton.settingsChanged,
            tooltip="Select the amount of posts that you want",
        )

        #-------------------------#
        #   Include box elements   #
        #-------------------------#

        self.includeBox = gui.widgetBox(
            widget=self.includeOuterBox,
            orientation='horizontal',
            addSpace=False,
        )

        gui.checkBox(
            widget=self.includeBox,
            master=self,
            value='includeImage',
            label=u'Include images',
            callback=self.mode_changed,
        )

        gui.checkBox(
            widget=self.includeBox,
            master=self,
            value='includeComments',
            label=u'Include comments',
            callback=self.mode_changed,
        )

        self.requestsBox = gui.widgetBox(
            widget=self.includeOuterBox,
            orientation='horizontal',
            addSpace=False,
        )

        self.refreshButton = gui.button(
            widget=self.requestsBox,
            master=self,
            label=u'Refresh the Data',
            callback=self.refresh_content,
        )

        if len(self.labelsPanier) == 0:
            self.refreshButton.setDisabled(True)
        

        self.fetchButton = gui.button(
            widget=self.requestsBox,
            master=self,
            label=u'Add Request',
            callback=self.confirm_settings,
        )

        #--------------------------#
        #   Results box elements   #
        #--------------------------#

        panier = gui.listBox(
            widget=panierBox,
            master=self,
            value="indicesPanier", 
            labels="labelsPanier",
            callback=lambda: self.removeButton.setDisabled(
                self.indicesPanier == list()
            ),
            tooltip="List of imported corpora.",
        )
        panier.setMinimumHeight(120)
        panier.setSelectionMode(3)

        self.update_list(self.labelsPanier)

        removalBox = gui.widgetBox(
            widget=panierBox,
            orientation='horizontal',
            addSpace=False,
        )
        
        self.removeButton = gui.button(
            widget=removalBox,
            master=self,
            label="Remove from selection",
            callback=self.removePressed,
            tooltip="Remove the selected corpus.",
        )

        self.removeButton.setDisabled(True)

        self.clearButton = gui.button(
            widget=removalBox,
            master=self,
            label="Clear selection",
            callback=self.clearPressed,
            tooltip="Remove all corpora from selection.",
        )

        #------------------------#
        #   End of definitions   #
        #------------------------#

        gui.separator(widget=self.controlArea, height=3) # Spacer
        gui.rubber(self.controlArea)

        # Info box...
        
        self.sendButton.draw()
        self.infoBox.draw()

        self.mode_changed()

    def mode_changed(self):
        self.sendButton.settingsChanged()
        """Allows to update the interface depeding on query mode"""
        if self.mode == "Subreddit": # 0 = subreddit selected
            # Hide URL and full text
            self.urlBox.setVisible(False)
            self.fullTextBox.setVisible(False)
            self.fullTextFilter.setVisible(False)

            # Show subreddit
            self.subredditBox.setVisible(True)
            self.filterBox.setVisible(True)
            self.subredditFilter.setVisible(True)

            self.checkSubredditSortMode()
        elif self.mode == "URL": # self.mode ==1 => post selected
            # Hide subreddit and full text
            self.subredditBox.setVisible(False)
            self.fullTextBox.setVisible(False)
            self.filterBox.setVisible(False)

            # Show URL
            self.urlBox.setVisible(True)
        elif self.mode == "Full text":
            # Hide subreddit
            self.subredditBox.setVisible(False)
            self.urlBox.setVisible(False)
            self.subredditFilter.setVisible(False)

            # Show full text
            self.fullTextBox.setVisible(True)
            self.filterBox.setVisible(True)
            self.fullTextFilter.setVisible(True)

            self.checkSearchSortMode()

        return

 
    def get_content(self, m, pA, sI, uI, ftI, sTF, ftTF, iI, iC, a):
        """Fetches the content on Reddit based on the filters selected by the user
        
        
        Parameters:
        m (string): Stands for 'method', defines which method the query will use
        pA (string): Stands for 'posted at', defines the time scale of the query
        sI (string): Stands for 'SubReddit input', defines the SubReddit name that will be queried
        uI (string): Stands for 'URL input', defines the URL of the SubReddit post that will be queried
        ftI (string): Stands for 'full text input', defines the query parameter for a full text query
        sTF (string): Stands for 'SubReddit time filters', defines the manner of filters for a SubReddit query in 'sort by'
        ftTF (string): Stands for 'full text time filters', defines the manner of filters for a full text query
        iI (string): Stands for 'include image', defines if the images should be included
        iC (string): Stands for 'include comments', defines if comments should be included
        a (int): Stands for 'amount', amount of posts to be fetched

        """
        self.sendButton.settingsChanged()
        self.controlArea.setDisabled(True)
        if ((m == "Subreddit" and len(sI) > 0) or
            (m == "URL" and len(uI) > 0) or
            (m == "Full text" and len(ftI) > 0)):
            if pA == "All":
                varTimeFilter = "all"
            elif pA == "Past day":
                varTimeFilter = "day"
            elif pA == "Past hour":
                varTimeFilter = "hour"
            elif pA == "Past week":
                varTimeFilter = "week"
            elif pA == "Past month":
                varTimeFilter = "month"
            elif pA == "Past year":
                varTimeFilter = "year"

            # Differenciate method depending of user selection
            if self.mode == "Subreddit":
                # Get the subreddit based on subreddit name
                try:
                    subreddit = self.reddit.subreddit(sI)
                    # Set list of posts "posts" according to filter
                    # Initiate lists without time filters applicable first
                    if sTF == "Hot":
                        posts = subreddit.hot(limit=a)
                    elif sTF == "New":
                        posts = subreddit.new(limit=a)
                    elif sTF == "Rising":
                        posts = subreddit.rising(limit=a)
                    # Initiate lists with time filters
                    elif sTF == "Controversial":
                        posts = subreddit.controversial(limit=a, time_filter=varTimeFilter)
                    elif sTF == "Top":
                        posts = subreddit.top(limit=a, time_filter=varTimeFilter)
                    # Loop on the posts found
                    for post in posts:
                		# Creation of corresponding segments
                        self.create_post_segments(post, iI, iC)
                except prawcore.exceptions.Redirect:
                    self.infoBox.setText(
                        "Error in redirect, please make sure the subreddit name is correct.",
                        "error"
                    )
                    return
                except prawcore.exceptions.NotFound:
                    self.infoBox.setText(
                        "Subreddit not found.",
                        "error"
                    )
                    return
            elif self.mode == "URL":
                # Get post based on URL
                try:
                    # Set list of posts "posts" according to filter
                    # Initiate lists without time filters applicable first
                    post = self.reddit.submission(url=uI)
                	# Creation of corresponding segment
                    self.create_post_segments(post, iI, iC)
                except prawcore.exceptions.NotFound:
                    self.infoBox.setText(
                        "No match for URL.",
                        "error"
                    )
                    return
                except praw.exceptions.ClientException:
                    self.infoBox.setText(
                        "URL not found.",
                        "error"
                    )
                    return
            elif self.mode == "Full text":
                userSearch = ftI
                reddit = self.reddit.subreddit("all")

                if ftTF == "Relevance":
                    posts = reddit.search(
                        userSearch,
                        sort="relevance",
                        limit=a,
                        time_filter=varTimeFilter,
                    )
                elif ftTF == "Top":
                    posts = reddit.search(
                        userSearch,
                        sort="top",
                        limit=a,
                        time_filter=varTimeFilter,
                    )
                elif ftTF == "Comments":
                    posts = reddit.search(
                        userSearch,
                        sort="comments",
                        limit=a,
                        time_filter=varTimeFilter,
                    )
                elif ftTF == "New":
                    posts = reddit.search(
                        userSearch,
                        sort="new",
                        limit=a,
                    )
            
                for post in posts:
                    # Creation of corresponding segment
                    self.create_post_segments(post, iI, iC)

            if len(self.listeTempPosts) > 0:
                # self.send("Segmentation", Segmentation(self.createdInputs))
                # self.infoBox.setText("{} segments sent to output !".format(len(self.createdInputs)))
                self.queryList.append(self.listeTempPosts)
                self.annotList.append(self.listeTempAnnot)
                self.add_to_list(
                    m = m,
                    pA = pA,
                    sI = sI,
                    uI = uI,
                    ftI = ftI,
                    sTF = sTF,
                    ftTF = ftTF,
                    iI = iI,
                    iC = iC,
                    a = a
                )
                self.refreshButton.setDisabled(False)
                self.listeTempPosts = list()
                self.listeTempAnnot = list()
            else:
                self.infoBox.setText(
                    "The posts found only contained images. Try to include images or comments.",
                    "warning"
                )
                # self.send("Segmentation", Segmentation(self.createdInputs))

        else:
            self.infoBox.setText(
                "Please fill in the input box.",
                "warning"
            )

        self.controlArea.setDisabled(False)
        return

    def refresh_content(self):
        modeReg = re.compile(r"(?<=Mode: ).+?(?=; Value)")
        valueReg = re.compile(r"(?<=Value: ).+?(?=; Settings)")
        settingsReg = re.compile(r"(?<=Settings: ).+?(?=; Include)")
        includeImageReg = re.compile(r"(?<=Include image: )\w+(?=; Include)")
        includeCommentsReg = re.compile(r"(?<=Include comments: )\w+(?=; Segments)")
        labels = self.labelsPanier
        self.clearPressed()
        for label in labels:
            mode = re.search(modeReg, label).group(0)
            value = re.search(valueReg, label).group(0)
            settings = re.search(settingsReg, label).group(0).split(", ")
            incIma = re.search(includeImageReg, label).group(0)
            incCom = re.search(includeCommentsReg, label).group(0)
            subIn = ""
            urlIn = ""
            ftxtIn = ""
            if mode == "Subreddit":
                subIn = value
            elif mode == "URL":
                urlIn = value
            elif mode == "Full text":
                ftxtIn = value

            if settings[1] == "[not specified]":
                settings[1] = "All"
            
            self.get_content(
                m = mode,
                pA = settings[1],
                sI = subIn,
                uI = urlIn,
                ftI = ftxtIn,
                sTF = settings[0],
                ftTF = settings[0],
                iI = incIma,
                iC = incCom,
                a = int(settings[2])
            )
     
    def confirm_settings(self):
        """sets all the values for filters entered by user"""
        mode = self.mode
        timeFilt = self.postedAt
        subInput = self.subreddit
        urlInput = self.URL
        ftInput = self.fullText
        subTimeFilter = self.sortBy
        ftTimeFiler = self.sortByFT
        image = self.includeImage
        comments = self.includeComments
        amount = self.amount
        self.get_content(
            m = mode,
            pA = timeFilt,
            sI = subInput,
            uI = urlInput,
            ftI = ftInput,
            sTF = subTimeFilter,
            ftTF = ftTimeFiler,
            iI = image,
            iC = comments,
            a = amount
        )


    # creation of segments from posts
    def create_post_segments(self, post, includeImage, includeComments):
        self.create_content_segment(post, includeImage)
        # if "Comments" is checked, we create the corresponding segments
        if includeComments:
            self.create_comments_segments(post)
            return

    # creation of segments for posts
    def create_content_segment(self, post, includeImage = False):
        annotations = dict()
        annotations["Title"] = post.title
        annotations["Id"] = post.id
        annotations["Parent"] = post.id
        annotations["Author"] = post.author
        annotations["Score"] = post.score
        annotations["Parent_type"] = "0"

        # Time annotations
        time = post.created_utc
        ts = int(time)
        date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        annotations["Posted_Unix"] = time
        annotations["Posted_at"] = date

        # TODO: add these annotations:
        # author, created_utc (ou created ?) et score
        content = post.selftext
        if content == "":
            content = "[image]"

        if not (includeImage == False and content == "[image]"):
            self.listeTempPosts.append(content)
            self.listeTempAnnot.append(annotations)
        
        return

    def create_comments_segments(self, post):
        post.comments.replace_more(limit=0)
        comments = post.comments.list()

        # Creation of a segment for each comment
        for comment in comments:
            annotations = dict()
            annotations["Title"] = post.title
            annotations["Id"] = comment.id
            annotations["Author"] = comment.author
            annotations["Score"] = comment.score

            # Time annotations
            time = comment.created_utc
            ts = int(time)
            date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            annotations["Posted_Unix"] = time
            annotations["Posted_at"] = date

            # TODO: add these annotations:
            # author, created_utc (ou created ?) et score

            parentId= comment.parent_id.split("_")
            annotations["Parent"] = parentId[1]
            annotations["Parent_type"] = parentId[0][1]

            self.listeTempPosts.append(comment.body)
            self.listeTempAnnot.append(annotations)
        return
    
    def checkSubredditSortMode(self):
        self.sendButton.settingsChanged()
        if self.sortBy == "Hot":
            self.timeBox.setDisabled(True)
        elif self.sortBy == "New":
            self.timeBox.setDisabled(True)
        elif self.sortBy == "Controversial":
            self.timeBox.setDisabled(False)
        elif self.sortBy == "Top":
            self.timeBox.setDisabled(False)
        elif self.sortBy == "Rising":
            self.timeBox.setDisabled(True)
    
    def checkSearchSortMode(self):
        self.sendButton.settingsChanged()
        if self.sortByFT == "Relevance":
            self.timeBox.setDisabled(False)
        elif self.sortByFT == "New":
            self.timeBox.setDisabled(True)
        elif self.sortByFT == "Top":
            self.timeBox.setDisabled(False)
        elif self.sortByFT == "Comments":
            self.timeBox.setDisabled(False)

    def removePressed(self):
        labelsPanier = self.labelsPanier

        for idx in sorted(self.indicesPanier, reverse=True):
            del labelsPanier[idx]
            del self.queryList[idx]
            del self.annotList[idx]
        
        self.labelsPanier = labelsPanier
        self.sendButton.settingsChanged()
            
    
    def clearPressed(self):
        self.labelsPanier = list()
        self.queryList = list()
        self.annotList = list()
        self.sendButton.settingsChanged()
        self.refreshButton.setDisabled(True)
    
    def add_to_list(self, m, pA, sI, uI, ftI, sTF, ftTF, iI, iC, a):
        labelsPanier = self.labelsPanier

        if m == "Subreddit":
            valeur = sI
            sortBy = sTF
            if sortBy == "Top" or sortBy == "Controversial":
                time = pA
            else:
                time = "[not specified]"
            amount = a
        elif m == "URL":
            valeur = uI
            sortBy = "[not specified]"
            time = "[not specified]"
            amount = 1
        elif m == "Full text":
            valeur = ftI
            sortBy = ftTF
            time = pA
            amount = a
        
        if iI:
            image = "True"
        else:
            image = "False"

        if iC:
            comments = "True"
        else:
            comments = "False"
    
        labelsPanier.append("* Mode: {}; Value: {}; Settings: {}, {}, {}; Include image: {}; Include comments: {}; Segments: {}".format(
                m,
                valeur,
                sortBy,
                time,
                amount,
                image,
                comments,
                len(self.queryList[len(self.queryList)-1])
            )
        )

        self.update_list(labelsPanier)
 
    def update_list(self, listOfLabels):
        try:
            self.labelsPanier = listOfLabels
        except TypeError:
            self.infoBox.setText(
                "Error !",
                "error"
            )
            return

    def change_button(self):
        self.removeButton.setDisabled(False)
    
    def send_data(self):
        self.controlArea.setDisabled(True)
        self.clearCreatedInputs()
        segmentation = None

        for query in self.queryList:
            for text in query:
                newInput = Input(text)
                self.createdInputs.append(newInput)

        if len(self.createdInputs) == 1:
            segmentation = self.createdInputs[0]

        # Otherwise the widget's output is a concatenation...
        else:
            segmentation = Segmenter.concatenate(
                self.createdInputs,
                import_labels_as=None,
            )

        # Annotate segments...
        annotations = list()
        for elem in self.annotList:
            for dic in elem:
                annotations.append(dic)
        
        for idx, segment in enumerate(segmentation):
            segment.annotations.update(annotations[idx])
            segmentation[idx] = segment

        num_chars = 0
        for segment in segmentation:
            num_chars += len(Segmentation.get_data(segment.str_index))
        self.infoBox.setText("{} segments sent to output ({} characters)".format(
            len(segmentation),
            num_chars,
            )
        )
        
        self.send("Segmentation", segmentation)

        self.controlArea.setDisabled(False)

        self.sendButton.resetSettingsChangedFlag()
    
    def clearCreatedInputs(self):
        """Delete all Input objects that have been created."""
        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]

    def onDeleteWidget(self):
        """Free memory when widget is deleted (overriden method)"""
        self.clearCreatedInputs()



 
# The following code lets you execute the code outside of Orange (to view the
# resulting interface)...
if __name__ == "__main__":
    from PyQt4.QtGui import QApplication
    import sys
    my_app = QApplication(list(sys.argv))
    my_widget = Redditor()
    my_widget.show()
    my_widget.raise_()
    my_app.exec_()
    my_widget.saveSettings()

