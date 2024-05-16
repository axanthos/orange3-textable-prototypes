from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler,
    InfoBox, SendButton,
)
from mastodon import Mastodon
from LTTL.Segment import Segment
from LTTL.Segmentation import Segmenptation
import LTTL.Segmenter as Segmenter
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
    # General
    autoSend = settings.Setting(False)
    userID = settings.Setting("macron@rivals.space")
    
    # Filters
    excludeReblogs = settings.Setting(True)
    excludeReplies = settings.Setting(True)
    excludeMedias = settings.Setting(True)
    onlyMedia = settings.Setting(True)

    URL = settings.Setting("")
    amount = settings.Setting(100)
    API = settings.Setting("")
    advancedSettings = settings.Setting(False)
    reblogsOnly = settings.Setting(False)
    minreblogs = settings.Setting(0)
    minLikes = settings.Setting(0)

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
            value='userID',
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

        self.excludeRe = gui.widgetBox(
            widget=self.controlArea,
            orientation='horizontal',
            addSpace=False,
        )

        self.exclreblogs = gui.checkBox(
            widget=self.excludeRe,
            master=self,
            value='excludeReblogs',
            label=u'Exclude reblogs',
            callback=self.updateGUI,
        )

        self.excludeRep = gui.checkBox(
            widget=self.excludeRe,
            master=self,
            value='excludeReplies',
            label=u'Exclude replies',
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

        self.reblogsBox = gui.widgetBox(
            widget=self.advSettings,
            orientation='vertical',
            addSpace=False,
        )
        

        self.reblogsOnlyCheckbox = gui.checkBox(
            widget=self.reblogsBox,
            master=self,
            value='reblogsOnly',
            label='Reblogs only',
            callback=self.updateGUI,
        )
        self.minreblogsBox = gui.spin(
            widget=self.reblogsBox,
            master=self,
            value="minreblogs",
            minv=0,
            maxv=10000,
            label="Minimum of reblogs:",
            labelWidth=135,
            orientation="horizontal",
            callback=self.sendButton.settingsChanged,
            tooltip="Select the amount of reblogs that you want",
            step=10,
        )

        self.imagesBox = gui.widgetBox(
            widget=self.reblogsBox,
            orientation='horizontal',
            addSpace=False,
        )

        self.excludeMediasCheckbox = gui.checkBox(
            widget=self.imagesBox,
            master=self,
            value='excludeMedias',
            label=u'Exclude images',
            callback=self.updateGUI,
        )
        self.onlyMediaCheckbox = gui.checkBox(
            widget=self.imagesBox,
            master=self,
            value='onlyMedia',
            label=u'Only images',
            callback=self.updateGUI,
        )

        gui.spin(
            widget=self.reblogsBox,
            master=self,
            value="minLikes",
            minv=0,
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
        
        if self.exclreblogs.isChecked():
            self.reblogsOnlyCheckbox.setDisabled(True)
            self.reblogsOnlyCheckbox.setChecked(False)
            self.minreblogsBox.setDisabled(True)
        else:
            self.reblogsOnlyCheckbox.setDisabled(False)
            self.minreblogsBox.setDisabled(False)
        
        if self.reblogsOnlyCheckbox.isChecked():
            self.exclreblogs.setDisabled(True)
            self.exclreblogs.setChecked(False)
        else:
            self.exclreblogs.setDisabled(False)

        if self.onlyMediaCheckbox.isChecked():
            self.excludeMediasCheckbox.setDisabled(True)
            self.excludeMediasCheckbox.setChecked(False)
        else:
            self.excludeMediasCheckbox.setDisabled(False)
             
        if self.excludeMediasCheckbox.isChecked():
            self.onlyMediaCheckbox.setDisabled(True)
            self.onlyMediaCheckbox.setChecked(False)
        else:
            self.onlyMediaCheckbox.setDisabled(False)


        self.infoBox = InfoBox(widget=self.controlArea)
        gui.separator(self.controlArea, height=3)

        

        gui.separator(widget=self.basicURLBox1, height=3)
        gui.separator(widget=self.basicURLBox2, height=3)
        gui.separator(widget=self.apiKey, height=3)
        gui.rubber(self.controlArea)

        self.sendButton.draw()
        self.infoBox.draw()


    def updateGUI(self):
        """Update GUI state"""

        if self.selectedSource=="User":
            self.basicURLBox1.setVisible(True)
            self.basicURLBox2.setVisible(False)
            self.URL = ""
        else: 
            self.basicURLBox1.setVisible(False)
            self.basicURLBox2.setVisible(True)
            self.userID = ""
        
        if self.advancedSettings:
            self.advSettings.setVisible(True)
        else:
            self.advSettings.setVisible(False)

        if self.exclreblogs.isChecked():
            self.reblogsOnlyCheckbox.setDisabled(True)
            self.reblogsOnlyCheckbox.setChecked(False)
            self.minreblogsBox.setDisabled(True)
        else:
            self.reblogsOnlyCheckbox.setDisabled(False)
            self.minreblogsBox.setDisabled(False)
        
        if self.reblogsOnlyCheckbox.isChecked():
            self.exclreblogs.setDisabled(True)
            self.exclreblogs.setChecked(False)
        else:
            self.exclreblogs.setDisabled(False)

        if self.onlyMediaCheckbox.isChecked():
            self.excludeMediasCheckbox.setDisabled(True)
            self.excludeMediasCheckbox.setChecked(False)
        else:
            self.excludeMediasCheckbox.setDisabled(False)
        
        if self.excludeMediasCheckbox.isChecked():
            self.onlyMediaCheckbox.setDisabled(True)
            self.onlyMediaCheckbox.setChecked(False)
        else:
            self.onlyMediaCheckbox.setDisabled(False)

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

    def fetchTimelines(self, instance, is_local, n=100):
        """
        Récupère les publications des timelines publiques locales ou fédérées d'une instance Mastodon.

        Args:
        instance (str): URL de l'instance Mastodon, par exemple "https://instance.net" ou "instance.net"
        is_local (bool): True pour récupérer à partir de la timeline locale, False pour la timeline fédérée
        n (int): Nombre de publications à récupérer

        Returns:
        all_post: Une dict contenant les publications de la timeline spécifiée

        # TODO check the timeout logic for queries that are larger than 40
        """

        # Normalisation de l'URL de l'instance pour garantir l'inclusion de "https://"
        if not instance.startswith("http://") and not instance.startswith("https://"):
            instance = f"https://{instance}"

        # Initialisation de la connexion à l'instance
        myMastodon = Mastodon(api_base_url=instance)

        # Tir de problèmes
        print(f"Getting {n} posts from the following instance:{instance}. Toot toot !")
        
        # Initialisation d'un dict vide pour contenir les objects
        all_posts = []
        # L'argument qui limite du nombre de posts !!! Pour l'instant et vu du fait de la limite à 40 l'argument du nombre de post est toujours rabotté à 40 peu importe l'input utilisateur
        remaining = n
        # A potentiellement utiliser pour créer un index dans en cas de requètes plus longues qui outrepassent la limite de 40 messages qui timeout.
        max_id = None

        # Récupération des publications par lots jusqu'à atteindre le nombre désiré `n` ou qu'il n'y ait plus de publications disponibles
        while remaining > 0:
            try:
                timeline = myMastodon.timeline('public', 
                                            local=is_local, 
                                            exclude_replies= self.excludeReplise,
                                            exclude_reblogs= self.excludeReblogs,
                                            only_media= self.onlyMedia,
                                            limit=min(remaining, 40), 
                                            max_id=max_id)
                if not timeline:
                    break
                all_posts.extend(timeline)
                remaining -= len(timeline)
                max_id = timeline[-1]['id']
            except Exception as e:
                print(f"Une erreur est survenue: {e}")
                break
        
        # Tir de problèmes
        print(f"This is the output dict: {all_posts}")
        return all_posts

    def fetchUserPosts(self, username_at_instance, n = 100):
        """Takes a string like (@)user@instance.net and returns a dictionnary of the n last posts from user"""

        #TODO loop to get n posts, instead of just one (?) request
        #TODO fix parsing if string is "https://rival3s.space/@macron"
        #TODO on peut ajouter directement ici les tris MediaOnly/ExcludeRepost/ExcludeReply cf.
        #https://mastodonpy.readthedocs.io/en/stable/_modules/mastodon/accounts.html?highlight=account_statuses
        #(ça sera plus efficace que trier en front)
        #TODO voir avec max_id min_id since_id et limit pour boucler sur n posts
        
        #Dictionary to save all fetched posts
        all_posts = {}

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

        #Get all posts (for now just 1 request)        (limit's max = 40)
        #excludeReplies seems to miss some of them, but still it's better than nothing
        #onlyMedia and excludeReblogs seem to work, we should test a bit more
        
        while True:
            posts = myMastodon.account_statuses(
            user_id,
            exclude_replies=self.excludeReplies,
            exclude_reblogs=self.excludeReblogs,
            only_media=self.onlyMedia,
            limit=n)
            
            #check if more posts
            if not posts:
                break
            
            else:
                #add posts in dictionnary
                for post in posts:
                    all_posts[post.id] = post
            
            #update last parameter to start fetching posts starting the last one        
            last_post_id = posts[-1].id
            
            posts = myMastodon.account_statuses(
                user_id,
                exclude_replies=self.excludeReplies,
                exclude_reblogs=self.excludeReblogs,
                only_media=self.onlyMedia,
                limit=n,
                since_id=last_post_id
            )

        print(f"Got {len(all_posts)} posts from {username_at_instance}", "\n")
        return all_posts

    def createSegmentation(self, posts_dict):
        """Takes a dictionary of posts, and create an input (in HTML) of each of their content.
        Concatenate it in a single output"""

        #-> Mettre une case dans le GUI pour exclure ou non les textes vides (les posts vides
        #restent utiles pour avoir les annotations, pour les stats..)
        #Q: Mieux vaut annotations vides (None; comme actuellement) ou pas d'annotations ?

        #Pour chaque post (un dictionnaire) dans posts (un dictionnaire de dictionnaires)
        for post in posts_dict:

            #Add placeholder text if post has no text
            #TODO Maybe we shouldn't do it ? we'll see

            #Rentrer le texte (ou placeholder) dans LTTL
            if not post.content:
                input_seg = Input("Placeholder !!!! this post had no text in it...", self.captionTitle)
            else:
                input_seg = Input(post.content, self.captionTitle)

            #Rajouter chaque segment dans la liste
            self.createdInputs.append(input_seg)


        # If there's only one post, the widget's output is the created Input...
        if len(self.createdInputs) == 1:
            self.segmentation = self.createdInputs[0]

        # Otherwise the widget's output is a concatenation...
        else:
            self.segmentation = Segmenter.concatenate(
                self.createdInputs,
                self.captionTitle,
                import_labels_as=None,
            )

        for idx, post in enumerate(posts_dict):

            #Create a copy of the segment
            segment = self.segmentation[idx]

            #Add annotations
            segment.annotations = {
                        "Account" : post.account.username,
                        "URL" : post.url,
                        "IsReply" : bool(post.in_reply_to_id),
                        "IsReblog" : bool(post.reblog),
                        "IsSensitive" : post.sensitive,
                        "HasMedias" : bool(post.media_attachments),
                        "Visibility" : post.visibility,
                        "Likes" : post.favourites_count,
                        "reblogs" : post.reblogs_count,
                        #"AccountDisplayName" : post.account.display_name,
                        #"ReblogId" : post.reblog.id if post.reblog else None,
                        #"PeopleMentionnedId" : post.mentions if post.mentions else None,
                        #"ReplyToPostId" : post.in_reply_to_id,
                        #"ReplyToAccountId" : post.in_reply_to_account_id,
                        #"Poll" : post.poll,
                        #"CustomEmojis" : post.emojis if post.emojis else None,
            }

            #Cut Date at seconds
            date = post.created_at
            date = date.replace(microsecond=0, tzinfo=None)
            segment.annotations["Date"] = date

            #Optionnals annotations (will only be added if it has something to say)
            if post.tags:
                tag_list = []

                #List of the name of each tag
                for tag in post.tags:
                    tag_list.append(tag.name)

                #Concatenated to a string and added to annotation
                tag_string = ", ".join(tag_list)
                segment.annotations["Hashtags"] = tag_string

            if post.spoiler_text:
                segment.annotations["SpoilerText"] = post.spoiler_text
            
            if post.application:
                segment.annotations["Application"] = post.application.name

            if post.language:
                segment.annotations["Language"] = post.language

            #And replace it's original (we need to do it this way because LTTL)
            self.segmentation[idx] = segment

        #Debug, print chaque segment et son contenu
        for segment in self.segmentation:
            print(segment)
            print(segment.get_content(), "\n")
        print(f"Segmented {len(posts_dict)} posts.")


        self.controlArea.setDisabled(False)

        return self.segmentation

    def createSegmentation(self, posts_dict):
        """Takes a dictionary of posts, and create an input (in HTML) of each of their content.
        Concatenate it in a single output"""

        #-> Mettre une case dans le GUI pour exclure ou non les textes vides (les posts vides
        #restent utiles pour avoir les annotations, pour les stats..)
        #Q: Mieux vaut annotations vides (None; comme actuellement) ou pas d'annotations ?

        #Pour chaque post (un dictionnaire) dans posts (un dictionnaire de dictionnaires)
        for post in posts_dict:

            #Add placeholder text if post has no text
            #TODO Maybe we shouldn't do it ? we'll see

            #Rentrer le texte (ou placeholder) dans LTTL
            if not post.content:
                input_seg = Input("Placeholder !!!! this post had no text in it...", self.captionTitle)
            else:
                input_seg = Input(post.content, self.captionTitle)

            #Rajouter chaque segment dans la liste
            self.createdInputs.append(input_seg)


        # If there's only one post, the widget's output is the created Input...
        if len(self.createdInputs) == 1:
            self.segmentation = self.createdInputs[0]

        # Otherwise the widget's output is a concatenation...
        else:
            self.segmentation = Segmenter.concatenate(
                self.createdInputs,
                self.captionTitle,
                import_labels_as=None,
            )

        for idx, post in enumerate(posts_dict):

            #Create a copy of the segment
            segment = self.segmentation[idx]

            #Add annotations
            segment.annotations = {
                        "Account" : post.account.username,
                        "URL" : post.url,
                        "IsReply" : bool(post.in_reply_to_id),
                        "IsReblog" : bool(post.reblog),
                        "IsSensitive" : post.sensitive,
                        "HasMedias" : bool(post.media_attachments),
                        "Visibility" : post.visibility,
                        "Likes" : post.favourites_count,
                        "Reposts" : post.reblogs_count,
                        #"AccountDisplayName" : post.account.display_name,
                        #"ReblogId" : post.reblog.id if post.reblog else None,
                        #"PeopleMentionnedId" : post.mentions if post.mentions else None,
                        #"ReplyToPostId" : post.in_reply_to_id,
                        #"ReplyToAccountId" : post.in_reply_to_account_id,
                        #"Poll" : post.poll,
                        #"CustomEmojis" : post.emojis if post.emojis else None,
            }

            #Cut Date at seconds
            date = post.created_at
            date = date.replace(microsecond=0, tzinfo=None)
            segment.annotations["Date"] = date

            #Optionnals annotations (will only be added if it has something to say)
            if post.tags:
                tag_list = []

                #List of the name of each tag
                for tag in post.tags:
                    tag_list.append(tag.name)

                #Concatenated to a string and added to annotation
                tag_string = ", ".join(tag_list)
                segment.annotations["Hashtags"] = tag_string

            if post.spoiler_text:
                segment.annotations["SpoilerText"] = post.spoiler_text
            
            if post.application:
                segment.annotations["Application"] = post.application.name

            if post.language:
                segment.annotations["Language"] = post.language

            #And replace it's original (we need to do it this way because LTTL)
            self.segmentation[idx] = segment

        #Debug, print chaque segment et son contenu
        for segment in self.segmentation:
            print(segment)
            print(segment.get_content(), "\n")
        print(f"Segmented {len(posts_dict)} posts.")


        self.controlArea.setDisabled(False)

        return self.segmentation

    #sendData method
    def sendData(self):
        """Send data when pressing the 'Send Data' button"""
            
        # Return error if no userID was given
        if self.selectedSource=="User":
            if not self.userID:
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

        dictPosts = self.fetchUserPosts(self.userID)
        self.segmentation = self.createSegmentation(dictPosts)

        #Send confirmation of how many toots were outputed
        message = f" Succesfully scrapped ! {len(self.segmentation)} segments sent to output"

        self.send("Scratted posts", self.segmentation, self)
        self.infoBox.setText(message)
        self.updateGUI()




    #Manage inputs, copy/pasted from other modules
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

if __name__ == "__main__":
    WidgetPreview(Protoscrat).run()
