from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler,
    InfoBox, SendButton,
)
from mastodon import Mastodon
from LTTL.Segment import Segment
from LTTL.Segmentation import Segmentation
from LTTL.Input import Input

class Protoscrat(OWTextableBaseWidget):
    """An Orange widget that uses MastoAPI to pull annotated posts"""

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Scratodon"
    description = "MastoAPI calls"
    icon = "icons/Scratodon_logo_dark.png"
    priority = 1

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = []
    outputs = [("Scratted posts", Segmentation)]

    #----------------------------------------------------------------------
    # GUI parameters...

    want_main_area = False

    #----------------------------------------------------------------------
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version="0.0.1"
    )

    # Saved settings
    autoSend = settings.Setting(True)
    UserID = settings.Setting("")
    URL = settings.Setting("")
    amount = settings.Setting(100)
    excludeReposts = settings.Setting(False)
    API = settings.Setting("")
    advancedSettings = settings.Setting(False)
    repostsOnly = settings.Setting(False)
    minReposts = settings.Setting(10)
    excludeImages = settings.Setting(False)
    withImages = settings.Setting(False)
    minLikes = settings.Setting(10)
    #mode = settings.ContextSetting(u'No context')

    def __init__(self):
        super().__init__()

        #Attributs initilizations...
        self.segmentation = Input("")
        self.createdInputs = list()
        self.sources = ["User", "Federated", "Local"]
        self.selectedSource = "User"

        # GUI
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute="infoBox",
            sendIfPreCallback=self.updateGUI,
        )

        queryBox = gui.widgetBox(
            widget=self.controlArea,
            box="Select A Source",
            orientation="vertical",
        )

        gui.comboBox(
            widget=queryBox,
            master=self,
            value="selectedSource",
            items=self.sources,
            sendSelectedValue=True,
            orientation="horizontal",
            label="Source:",
            emptyString="",
            labelWidth=120,
            tooltip=(
                "Please select the desired source.\n"
            ),
            callback=self.sendButton.settingsChanged,
        )

        self.basicURLBox1 = gui.widgetBox(
            widget=self.controlArea,
            box='Source',
            orientation='vertical',
            addSpace=False,
            )
        basicURLBoxLine1 = gui.widgetBox(
            widget=self.basicURLBox1,
            box=False,
            orientation='horizontal',
            )
        gui.lineEdit(
            widget=basicURLBoxLine1,
            master=self,
            value='UserID',
            orientation='horizontal',
            label='User ID:',
            labelWidth=101,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                "The username '@user@instance.com' whose content will be imported."
                ),
            )
        
        self.basicURLBox2 = gui.widgetBox(
            widget=self.controlArea,
            box='Source',
            orientation='vertical',
            addSpace=False,
            )
        basicURLBoxLine2 = gui.widgetBox(
            widget=self.basicURLBox2,
            box=False,
            orientation='horizontal',
            )
        gui.lineEdit(
            widget=basicURLBoxLine2,
            master=self,
            value='URL',
            orientation='horizontal',
            label='URL:',
            labelWidth=101,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                "The URL whose content will be imported."
                ),
            )
        
        if self.selectedSource == "User":
            self.basicURLBox1.setVisible(True)
            self.basicURLBox2.setVisible(False)
        else:
            self.basicURLBox1.setVisible(False)
            self.basicURLBox2.setVisible(True)
        
        gui.spin(
            widget=self.controlArea,
            master=self,
            value="amount",
            minv=1,
            maxv=10000,
            label="Max amount of posts:",
            labelWidth=135,
            orientation="horizontal",
            callback=self.sendButton.settingsChanged,
            tooltip="Select the amount of posts that you want",
            step=10,
        )

        self.exclReposts = gui.checkBox(
            widget=self.controlArea,
            master=self,
            value='excludeReposts',
            label=u'Exclude reposts',
            callback=self.updateGUI,
        )

        self.apiKey = gui.lineEdit(
            widget=self.controlArea,
            master=self,
            value='API',
            orientation='horizontal',
            label='API key (optional):',
            labelWidth=101,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                "Your API key, optional."
                ),
            )

        gui.checkBox(
            widget=self.controlArea,
            master=self,
            value='advancedSettings',
            label=u'Advanced settings',
            callback=self.updateGUI,
        )

        self.advSettings = gui.widgetBox(
            widget=self.controlArea,
            orientation='horizontal',
            addSpace=False,
        )

        self.repostsBox = gui.widgetBox(
            widget=self.advSettings,
            orientation='vertical',
            addSpace=False,
        )
        

        self.repostsOnlyCheckbox = gui.checkBox(
            widget=self.repostsBox,
            master=self,
            value='repostsOnly',
            label=u'Reposts only',
            callback=self.updateGUI,
        )
        self.minRepostsBox = gui.spin(
            widget=self.repostsBox,
            master=self,
            value="minReposts",
            minv=1,
            maxv=10000,
            label="Minimum of reposts:",
            labelWidth=135,
            orientation="horizontal",
            callback=self.sendButton.settingsChanged,
            tooltip="Select the amount of reposts that you want",
            step=10,
        )

        self.imagesBox = gui.widgetBox(
            widget=self.repostsBox,
            orientation='horizontal',
            addSpace=False,
        )

        self.excludeImagesCheckbox = gui.checkBox(
            widget=self.imagesBox,
            master=self,
            value='excludeImages',
            label=u'Exclude images',
            callback=self.updateGUI,
        )
        self.withImagesCheckbox = gui.checkBox(
            widget=self.imagesBox,
            master=self,
            value='withImages',
            label=u'With images',
            callback=self.updateGUI,
        )

        gui.spin(
            widget=self.repostsBox,
            master=self,
            value="minLikes",
            minv=1,
            maxv=10000,
            label="Minimum of likes:",
            labelWidth=135,
            orientation="horizontal",
            callback=self.sendButton.settingsChanged,
            tooltip="Select the amount of likes that a post should have",
            step=10,
        )

        if self.advancedSettings:
            self.advSettings.setVisible(True)
        else:
            self.advSettings.setVisible(False)
        
        if self.exclReposts.isChecked():
            self.repostsOnlyCheckbox.setDisabled(True)
            self.repostsOnlyCheckbox.setChecked(False)
            self.minRepostsBox.setDisabled(True)
        else:
            self.repostsOnlyCheckbox.setDisabled(False)
            self.minRepostsBox.setDisabled(False)
        
        if self.repostsOnlyCheckbox.isChecked():
            self.exclReposts.setDisabled(True)
            self.exclReposts.setChecked(False)
        else:
            self.exclReposts.setDisabled(False)

        if self.withImagesCheckbox.isChecked():
            self.excludeImagesCheckbox.setDisabled(True)
            self.excludeImagesCheckbox.setChecked(False)
        else:
            self.excludeImagesCheckbox.setDisabled(False)
             
        if self.excludeImagesCheckbox.isChecked():
            self.withImagesCheckbox.setDisabled(True)
            self.withImagesCheckbox.setChecked(False)
        else:
            self.withImagesCheckbox.setDisabled(False)


        self.infoBox = InfoBox(widget=self.controlArea)
        gui.separator(self.controlArea, height=3)

        

        gui.separator(widget=self.basicURLBox1, height=3)
        gui.separator(widget=self.basicURLBox2, height=3)
        gui.separator(widget=self.apiKey, height=3)
        gui.rubber(self.controlArea)

        self.sendButton.draw()
        self.infoBox.draw()


    def sendData(self):
        """Send data when pressing the 'Send Data' button"""
            
        # Return error if no UserID was given
        if self.selectedSource=="User":
            if not self.UserID:
                self.infoBox.setText("Please give a User ID.", "warning")
                self.send('Scratted posts', None)
                return
        if self.selectedSource=="Federated":
            if not self.URL:
                self.infoBox.setText("Please give a URL.", "warning")
                self.send('Scratted posts', None)
                return
        if self.selectedSource=="Local":
            if not self.URL:
                self.infoBox.setText("Please give a URL.", "warning")
                self.send('Scratted posts', None)
                return

        #Clear old created Inputs
        self.clearCreatedInputs()

        dictPosts = self.fetchUserPosts(self.UserID)
        self.segmentation = self.createSegmentation(dictPosts)

        #Send confirmation of how many toots were outputed
        message = f" Succesfully scrapped ! {len(self.segmentation)} segments sent to output"

        self.send("Scratted posts", self.segmentation, self)
        self.infoBox.setText(message)
        self.updateGUI()
    
    def updateGUI(self):
        """Update GUI state"""

        if self.selectedSource=="User":
            self.basicURLBox1.setVisible(True)
            self.basicURLBox2.setVisible(False)
            self.URL = ""
        else: 
            self.basicURLBox1.setVisible(False)
            self.basicURLBox2.setVisible(True)
            self.UserID = ""
        
        if self.advancedSettings:
            self.advSettings.setVisible(True)
        else:
            self.advSettings.setVisible(False)

        if self.exclReposts.isChecked():
            self.repostsOnlyCheckbox.setDisabled(True)
            self.repostsOnlyCheckbox.setChecked(False)
            self.minRepostsBox.setDisabled(True)
        else:
            self.repostsOnlyCheckbox.setDisabled(False)
            self.minRepostsBox.setDisabled(False)
        
        if self.repostsOnlyCheckbox.isChecked():
            self.exclReposts.setDisabled(True)
            self.exclReposts.setChecked(False)
        else:
            self.exclReposts.setDisabled(False)

        if self.withImagesCheckbox.isChecked():
            self.excludeImagesCheckbox.setDisabled(True)
            self.excludeImagesCheckbox.setChecked(False)
        else:
            self.excludeImagesCheckbox.setDisabled(False)
        
        if self.excludeImagesCheckbox.isChecked():
            self.withImagesCheckbox.setDisabled(True)
            self.withImagesCheckbox.setChecked(False)
        else:
            self.withImagesCheckbox.setDisabled(False)

    def clearCreatedInputs(self):
        """Delete all Input objects that have been created"""

        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]

    def setCaption(self, title):
        """This method needs to be copied verbatim in every Textable widget that sends a segmentation"""

        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)

    def fetchUserPosts(self, username_at_instance, n = 100):
        """Takes a string like (@)user@instance.net and returns a dictionnary of all posts from user"""

        #TODO loop to get n posts, instead of just one (?) request
        #TODO fix parsing if string is "https://rivals.space/@macron"
        #TODO on peut ajouter directement ici les tris MediaOnly/ExcludeRepost/ExcludeReply cf.
        #https://mastodonpy.readthedocs.io/en/stable/_modules/mastodon/accounts.html?highlight=account_statuses
        #(ça sera plus efficace que trier en front)
        #TODO voir avec max_id min_id since_id et limit pour boucler sur n posts

        #Delete the first "@", if given (my parsing is ugly, I (Rose) will do better later)
        if username_at_instance[0] == "@":
            username_at_instance = username_at_instance[1:]

        #Get user and instance frome input, format it in domain
        user, instance = username_at_instance.split("@")
        domain = f"https://{instance}/"

        #Initialize connexion to instance
        myMastodon = Mastodon(api_base_url=domain)
        print(f"Trying to get {n} posts from @{user} on {domain}", "\n") #Debug

        #Get ID from user
        user_id = myMastodon.account_lookup(user).id
        print(f"{username_at_instance}'s id is: {user_id}", "\n")

        #Get all posts (for now just 1 request, 20 or 40 if we add limit=n (strange ??))
        all_posts = myMastodon.account_statuses(user_id, limit=n)

        print(f"Got {len(all_posts)} posts from {username_at_instance}", "\n")
        return all_posts

    def createSegmentation(self, posts_dict):
        """Takes a dictionary of posts, and create an input (in HTML) of each of their content.
        Concatenate it in a single output"""

        #TODO for later: annotate (like, username, hasPhoto...) each post (easy and useful)
        #TODO Certains segments sont vides, RT et images sans texte, n'ont rien à afficher en .content
        #-> Mettre une case dans le GUI pour exclure ou non les textes vides (les posts vides
        #restent utiles pour avoir les annotations, pour les stats..)
        #Q: Mieux vaut annotations vides (None; comme actuellement) ou pas d'annotations ?

        #Pour chaque post (un dictionnaire) dans posts (un dictionnaire de dictionnaires)
        for post in posts_dict:

            #Rentrer le texte dans LTTL
            input_seg = Input(post.content)
            #Récupérer le numéro du texte qu'on vient de rentrer
            str_index = input_seg[0].str_index

            #Rajouter chaque segment dans la liste
            self.createdInputs.append(
                Segment(
                    str_index=str_index,
                    annotations={
                        "Account" : post.account.username,
                        "AccountDisplayName" : post.account.display_name,
                        "Date" : post.created_at, #TODO Format
                        "URL" : post.url,
                        "IsReply" : bool(post.in_reply_to_id),
                        "IsReblog" : bool(post.reblog),
                        "IsSensitive" : post.sensitive,
                        "HasMedias" : bool(post.media_attachments), #Rajouter types de médias ?
                        "HasContentWarning" : bool(post.spoiler_text),
                        "ReblogId" : post.reblog.id if post.reblog else None,
                        "PeopleMentionnedId" : post.mentions if post.mentions else None, #TODO get id of accounts (or username ?)
                        "ReplyToPostId" : post.in_reply_to_id,
                        "ReplyToAccountId" : post.in_reply_to_account_id,
                        "SpoilerText" : post.spoiler_text,
                        "Visibility" : post.visibility,
                        "Application" : post.application.name if post.application else None,
                        "Likes" : post.favourites_count,
                        "Reposts" : post.reblogs_count,
                        "Language" : post.language,
                        "Tags" : post.tags if post.tags else None, #TODO tester
                        "Poll" : post.poll, #TODO Format (ou enlever ?)
                        "CustomEmojis" : post.emojis if post.emojis else None, #TODO tester
                        },
                    )
                )
        #Segmenter selon notre liste de segments
        self.segmentation = Segmentation(self.createdInputs)
        #Debug, print chaque segment et son contenu
        for segment in self.segmentation:
            print(segment)
            print(segment.get_content(), "\n")
        print(f"Segmented {len(posts_dict)} posts.")
        return self.segmentation

if __name__ == "__main__":
    WidgetPreview(Protoscrat).run()
