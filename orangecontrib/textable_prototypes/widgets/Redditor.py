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

class Redditor(OWTextableBaseWidget):
    """An Orange widget to scrape Reddit"""

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Redditor"
    description = "Scrap on Reddit"
    icon = "icons/mywidget.svg"
    priority = 20

    #----------------------------------------------------------------------
    # Channel definitions...

    # inputs = []
    outputs = [("Segmentation", Segmentation)]

    #----------------------------------------------------------------------
    # GUI layout parameters...

    want_main_area = False
    resizing_enabled = True

    # Settings
    mode = Setting("Subreddit")
    subreddit = Setting(u'')
    URL = Setting(u'')
    fullText = Setting(u'')
    sortBy = Setting("Hot")
    sortByFT = Setting("Relevance")
    postedAt = Setting("All")
    amount = Setting(1)
    includeTitle = Setting(True)
    includeContent = Setting(True)
    includeComments = Setting(True)
    labelsPanier = Setting(list())
    segmentations = Setting(list())

    # Praw instance
    reddit = praw.Reddit(
        client_id="aHeP3Ub7aILvsg",
        client_secret=None,
        username="RedditorApp",
        password="RedditorProg2019",
        user_agent="Redditor by /u/RedditorApp"
    )

    # Segment list
    segments = list()

    def __init__(self):
        super().__init__()

        self.indicesPanier = list()

        #----------------------------------------------------------------------
        # User interface...
        self.infoBox = InfoBox(
            widget=self.controlArea,

        )

        sourceBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Source',
            orientation='vertical',
            addSpace=False,
        )

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

        """
        modeRadio = gui.radioButtons(
            widget=self.modeBox,
            master=self,
            value='mode',
            label="Mode",
            orientation='horizontal',
            callback=self.mode_changed,
            btnLabels=["SubReddit", "Post"],
        )
        """

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
            label=u'Search on reddit:',
            labelWidth=120,
        )

        """
        Filter box
        """

        self.filterBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Filters',
            orientation='vertical',
            addSpace=False,
        )

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
            tooltip="Select the amount of posts that you want",
        )

        '''
        Include Box
        '''

        self.includeBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Include',
            orientation='horizontal',
            addSpace=False,
        )

        # TODO: replace checkboxes

        gui.checkBox(
            widget=self.includeBox,
            master=self,
            value='includeTitle',
            label=u'Title',
            callback=self.mode_changed,  
        )

        gui.checkBox(
            widget=self.includeBox,
            master=self,
            value='includeContent',
            label=u'Content',
            callback=self.mode_changed,
        )
        
        gui.checkBox(
            widget=self.includeBox,
            master=self,
            value='includeComments',
            label=u'Comments',
            callback=self.mode_changed,
        )

        gui.rubber(self.controlArea)


       
        '''
        Panier
        '''

        panierBox = gui.widgetBox(
            widget=self.controlArea,
            orientation='vertical',
            box=u'Selection',
            addSpace=False,
        )

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
        
        # Remove listing button
        self.removeButton = gui.button(
            widget=removalBox,
            master=self,
            label="Remove from selection",
            callback=self.removePressed,
            tooltip="Remove the selected corpus.",
        )

        self.removeButton.setDisabled(True)

        # Delete all corpus button
        self.clearButton = gui.button(
            widget=removalBox,
            master=self,
            label="Clear selection",
            callback=self.clearPressed,
            tooltip="Remove all corpora from selection.",
        )

        self.fetchButton = gui.button(
            widget=self.includeBox,
            master=self,
            label=u'Get content',
            callback=self.get_content,
        )

        """
        Send button
        """

        self.sendBox = gui.widgetBox(
            widget=self.controlArea,
            orientation='vertical',
            addSpace=False,
        )

        self.sendButton = SendButton(
            widget=self.sendBox,
            master=self,
            callback=self.send_data,
            infoBoxAttribute='infoBox',
        )

       
        # self.label = gui.widgetLabel(self.controlArea, "Chose a mode")

        # Send button...
        # self.sendButton.draw()

        # Info box...
        self.infoBox.draw()
        self.sendButton.draw()

        self.mode_changed()

    def mode_changed(self):
        """Reimplemented from OWWidget."""
        if self.mode == "Subreddit": # 0 = subreddit selected
            # cacher URL et Full text
            self.urlBox.setVisible(False)
            self.fullTextBox.setVisible(False)
            self.fullTextFilter.setVisible(False)

            # montrer subreddit
            self.subredditBox.setVisible(True)
            self.filterBox.setVisible(True)
            self.subredditFilter.setVisible(True)

            self.checkSubredditSortMode()
        elif self.mode == "URL": # self.mode ==1 => post selected
            # cacher subreddit et Full text
            self.subredditBox.setVisible(False)
            self.fullTextBox.setVisible(False)
            self.filterBox.setVisible(False)

            # montrer URL
            self.urlBox.setVisible(True)
        elif self.mode == "Full text":
            # cacher subreddit
            self.subredditBox.setVisible(False)
            self.urlBox.setVisible(False)
            self.subredditFilter.setVisible(False)

            # montrer Full text
            self.fullTextBox.setVisible(True)
            self.filterBox.setVisible(True)
            self.fullTextFilter.setVisible(True)

            self.checkSearchSortMode()

        # Clear the channel by sending None.
        # TODO: pas sûr que ce soit utile. Je pense qu'un return suffit
        # self.send("Segmentation", None)
        return

    """
    def update_send_button(self):
        # self.mode == 0 => subreddit selected, self.mode == 1 => post selected
        if ((self.mode == "Subreddit" and len(self.subreddit) > 0) or
            (self.mode == "URL" and len(self.URL) > 0) or
            (self.mode == "Full text" and len(self.URL) > 0)):
            self.sendButton.setDisabled(False)
        else:
            self.sendButton.setDisabled(True)
    """

    def get_content(self):
        if ((self.mode == "Subreddit" and len(self.subreddit) > 0) or
            (self.mode == "URL" and len(self.URL) > 0) or
            (self.mode == "Full text" and len(self.fullText) > 0)):
            tmp = self.postedAt
            if tmp == "All":
                varTimeFilter = "all"
            elif tmp == "Past day":
                varTimeFilter = "day"
            elif tmp == "Past hour":
                varTimeFilter = "hour"
            elif tmp == "Past week":
                varTimeFilter = "week"
            elif tmp == "Past month":
                varTimeFilter = "month"
            elif tmp == "Past year":
                varTimeFilter = "year"
            # Differenciate method depending of user selection
            if self.mode == "Subreddit":
                # Get the subreddit based on subreddit name
                try:
                    subreddit = self.reddit.subreddit(self.subreddit)
                    # Set list of posts "posts" according to filter
                    # Initiate lists without time filters applicable first
                    modeTri = self.sortBy
                    if modeTri == "Hot":
                        posts = subreddit.hot(limit=self.amount)
                    elif modeTri == "New":
                        posts = subreddit.new(limit=self.amount)
                    elif modeTri == "Rising":
                        posts = subreddit.rising(limit=self.amount)
                    # Initiate lists with time filters
                    elif modeTri == "Controversial":
                        posts = subreddit.controversial(limit=self.amount, time_filter=varTimeFilter)
                    elif modeTri == "Top":
                        posts = subreddit.top(limit=self.amount, time_filter=varTimeFilter)
                    # Loop on the posts found
                    for post in posts:
                		# On crée les segments appropriés
                        self.create_post_segments(post)
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
                    post = self.reddit.submission(url=self.URL)
                	# On crée les segments appropriés
                    self.create_post_segments(post)
                except prawcore.exceptions.NotFound:
                    self.infoBox.setText(
                        "No match forURL.",
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
                userSearch = self.fullText
                reddit = self.reddit.subreddit("all")

                modeTri = self.sortByFT
                if modeTri == "Relevance":
                    posts = reddit.search(
                        userSearch,
                        sort="relevance",
                        limit=self.amount,
                        time_filter=varTimeFilter,
                    )
                elif modeTri == "Top":
                    posts = reddit.search(
                        userSearch,
                        sort="top",
                        limit=self.amount,
                        time_filter=varTimeFilter,
                    )
                elif modeTri == "Comments":
                    posts = reddit.search(
                        userSearch,
                        sort="comments",
                        limit=self.amount,
                        time_filter=varTimeFilter,
                    )
                elif modeTri == "New":
                    posts = reddit.search(
                        userSearch,
                        sort="new",
                        limit=self.amount,
                    )
            
                for post in posts:
                    # On crée les segments appropriés
                    self.create_post_segments(post)

            if len(self.segments) > 0:
                # self.send("Segmentation", Segmentation(self.segments))
                # self.infoBox.setText("{} segments sent to output !".format(len(self.segments)))
                self.segmentations.append(Segmentation(self.segments))
                self.add_to_list(Segmentation(self.segments))
                self.segments = []
                return
            else:
                self.infoBox.setText(
                    "There is nothing! Maybe you should include at least one item",
                    "warning"
                )
                # self.send("Segmentation", Segmentation(self.segments))
                return
        else:
            self.infoBox.setText(
                "Please fill in the input box.",
                "warning"
            )
            return

    def create_post_segments(self, post):
        # Si "Title" est coché, on crée le segment correspondant
        if self.includeTitle is True:
            self.create_title_segment(post)
        # Si "Content" est coché ou si aucune case ne l'est, on crée le segment correspondant
        # et vérifie que "Content" est bien coché
        if self.includeContent is True or (self.includeTitle is not True and self.includeComments is not True):
            self.includeContent = True
            self.create_content_segment(post)
        # Si "Comments" est coché, on crée les segments correspondants
        if self.includeComments is True:
            self.create_comments_segments(post)
            return
        
    def create_title_segment(self, post):
        annotations = dict()
        #annotations["Title"] = post.title
        annotations["Id"] = post.id
        annotations["Parent"] = post.id
        annotations["Author"] = post.author
        annotations["Posted"] = post.created_utc 
        annotations["Score"] = post.score
        annotations["Upvotes"] = post.ups
        annotations["Downvotes"] = post.downs
        text = Input(post.title)

        self.segments.append(
            Segment(
                str_index=text[0].str_index,
                start=text[0].start,
                end=text[0].end,
                annotations=annotations
            )
        )
        return
   

    def create_content_segment(self, post):
        annotations = dict()
        annotations["Title"] = post.title
        annotations["Id"] = post.id
        annotations["Parent"] = post.id
        annotations["author"] = post.author
        annotations["Pasted"] = post.created_utc
        annotations["Score"] = post.score
        annotations["Upvotes"] = post.ups
        annotations["Downvotes"] = post.downs

        # TODO: add these annotations:
        # author, created_utc (ou created ?) et score

        text = Input(post.selftext)

        self.segments.append(
            Segment(
                str_index=text[0].str_index,
                start=text[0].start,
                end=text[0].end,
                annotations=annotations
            )
        )
        return
    
    def create_comments_segments(self, post):
        post.comments.replace_more(limit=0)
        comments = post.comments.list()

        # On crée un segment pour chaque commentaire
        for comment in comments:
            annotations = dict()
            annotations["Title"] = post.title
            annotations["Id"] = comment.id
            annotations["author"] = post.author
            annotations["Posted"] = post.created_utc 
            annotations["Score"] = post.score
            annotations["Upvotes"] = post.ups
            annotations["Downvotes"] = post.downs

            # TODO: add these annotations:
            # author, created_utc (ou created ?) et score

            parentId= comment.parent_id.split("_")
            annotations["Parent"] = parentId[1]
            annotations["Parent_type"] = parentId[0][1]

            text = Input(comment.body)

            self.segments.append(
                Segment(
                    str_index=text[0].str_index,
                    start=text[0].start,
                    end=text[0].end,
                    annotations=annotations
                )
            )
        return
    
    def checkSubredditSortMode(self):
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
        # labelsPanierRemove = list()

        for idx in sorted(self.indicesPanier, reverse=True):
            del labelsPanier[idx]
            del self.segmentations[idx]
        
        self.labelsPanier = labelsPanier
            
    
    def clearPressed(self):
        self.labelsPanier = list()
        self.segmentations = list()
    
    def add_to_list(self, segmentation):
        labelsPanier = self.labelsPanier

        if self.mode == "Subreddit":
            valeur = self.subreddit
            sortBy = self.sortBy
            if sortBy == "Top" or sortBy == "Controversial":
                time = self.postedAt
            else:
                time = "[not specified]"
            amount = self.amount
        elif self.mode == "URL":
            valeur = self.URL
            sortBy = "[not specified]"
            time = "[not specified]"
            amount = 1
        elif self.mode == "Full text":
            valeur = self.fullText
            sortBy = self.sortByFT
            time = self.postedAt
            amount = self.amount
        
        if self.includeTitle:
            title = "Title|"
        else:
            title = ""
        if self.includeContent:
            content = "Content|"
        else:
            content = ""
        if self.includeComments:
            comments = "Comments"
        else:
            comments = ""
    
        labelsPanier.append("* Mode: {}; Value: {}; Settings: {}, {}, {}; Includes: {}{}{}; Segments: {}".format(
                self.mode,
                valeur,
                sortBy,
                time,
                amount,
                title,
                content,
                comments,
                len(self.segments)
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
        print(self.segmentations)
        final_amount = 0
        for segmentation in self.segmentations:
            for _ in segmentation:
                final_amount += 1
        self.infoBox.setText("{} segments sent to output !".format(final_amount))
        self.send("Segmentation", self.segmentations)
    
    """
    def send_data(self):
        self.label.setText("Envoyé! Mode is: {}".format(self.mode))
    """


 
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


