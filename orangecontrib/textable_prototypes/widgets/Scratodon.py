from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler,
    InfoBox, SendButton, ProgressBar,
)
from mastodon import Mastodon
from LTTL.Segment import Segment
from LTTL.Segmentation import Segmentation
import LTTL.Segmenter as Segmenter
from LTTL.Input import Input
import time
from urllib.parse import urlparse

class Scratodon(OWTextableBaseWidget):
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
        version="1.0"
    )

    # Saved settings
    # General
    autoSend = settings.Setting(False)

    selectedSource = settings.Setting("User")
    userID = settings.Setting("gargron@mastodon.social")
    URL = settings.Setting("mastodon.social")
    amount = settings.Setting(100)

    # Filters
    filterReblogs = settings.Setting("Keep")
    filterReplies = settings.Setting("Keep")
    filterMedias = settings.Setting("Keep")

    minReblogs = settings.Setting(0)
    minLikes = settings.Setting(0)

    def __init__(self):
        super().__init__()

        #Attributs initilizations...
        self.segmentation = Input("")
        self.createdInputs = list()

        # GUI
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute="infoBox",
            sendIfPreCallback=self.updateGUI,
        )


        #Boite des sources
        queryBox = gui.widgetBox(
            widget=self.controlArea,
            box="Source",
            orientation="vertical",
        )

        #Combo Box du choix de source
        gui.comboBox(
            widget=queryBox,
            master=self,
            value="selectedSource",
            items=["User", "Federated", "Local"],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Source Type:",
            labelWidth=100,
            tooltip=(
                "User's posts or one of the timelines."
            ),
            callback=self.sendButton.settingsChanged,
        )

        # Sous-Boite pour contenir le user ID
        self.UserIDBox = gui.widgetBox(
            widget=queryBox,
            orientation='vertical',
            addSpace=False,
            )
        
        #Ecarter un peu plus la sous-boite de l'élément précédent
        Spacer1 = gui.widgetBox(
            widget=self.UserIDBox,
            box=False,
            orientation='horizontal',
            )

        #Champ pour donner le user ID
        gui.lineEdit(
            widget=self.UserIDBox,
            master=self,
            value='userID',
            orientation='horizontal',
            label='User ID:',
            labelWidth=50,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                "The full username (ex: gargron@mastodon.social) of the wanted user."
                ),
            )
        
        #Sous-boite pour l'URL, analogue à celle du user ID
        self.URLBox = gui.widgetBox(
            widget=queryBox,
            orientation='vertical',
            addSpace=False,
            )
        
        #Ecarter
        Spacer2 = gui.widgetBox(
            widget=self.URLBox,
            box=False,
            orientation='horizontal',
            )

        #Champ pour rentrer l'URL
        gui.lineEdit(
            widget=self.URLBox,
            master=self,
            value='URL',
            orientation='horizontal',
            label='URL:',
            labelWidth=50,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                "The domain (ex: mastodon.social) of the wanted instance."
                ),
            )
        
        #Champ pour le nombre de posts
        gui.spin(
            widget=queryBox,
            master=self,
            value="amount",
            minv=1,
            maxv=1000000,
            label="Max amount of posts:",
            labelWidth=150,
            orientation="horizontal",
            callback=self.sendButton.settingsChanged,
            tooltip="Amount of posts that will get fetched. \n!! Actual amount of posts may be lower, because of the filters.\n(~5 minutes of wait every 12k posts)",
            step=10,
        )

        #Boite des filtres
        filtersBox = gui.widgetBox(
            widget=self.controlArea,
            box="Filters",
            orientation="vertical",
        )

        #Qui contient la sous-boite des types
        typesBox = gui.widgetBox(
            widget=filtersBox,
            box="Type of posts",
            orientation="vertical",
        )

        #Les 3 comboBox pour filter
        gui.comboBox(
            widget=typesBox,
            master=self,
            value="filterReblogs",
            items=["Remove", "Keep", "Keep Only"],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Reblogs:",
            labelWidth=125,
            tooltip=(
                "What to do with posts that are reblogs (They won't have any text anyway)."
            ),
            callback=self.sendButton.settingsChanged,
        )

        gui.comboBox(
            widget=typesBox,
            master=self,
            value="filterReplies",
            items=["Remove", "Keep", "Keep Only"],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Replies:",
            labelWidth=125,
            tooltip=(
                "What to do with posts that are replies."
            ),
            callback=self.sendButton.settingsChanged,
        )

        gui.comboBox(
            widget=typesBox,
            master=self,
            value="filterMedias",
            items=["Remove", "Keep", "Keep Only"],
            sendSelectedValue=True,
            orientation="horizontal",
            label="With medias:",
            labelWidth=125,
            tooltip=(
                "What to do with posts that have medias."
            ),
            callback=self.sendButton.settingsChanged,
        )

        #La sous-boite des interactions
        interactionsBox = gui.widgetBox(
            widget=filtersBox,
            box="Interactions",
            orientation="vertical",
        )

        #Nombre minimum de reblogs
        gui.spin(
            widget=interactionsBox,
            master=self,
            value="minReblogs",
            minv=0,
            maxv=1000000,
            label="Minimum of reblogs:",
            labelWidth=150,
            orientation="horizontal",
            callback=self.sendButton.settingsChanged,
            tooltip="Amount of reblogs that a post should have",
            step=5,
        )

        #Nombre minimum de likes
        gui.spin(
            widget=interactionsBox,
            master=self,
            value="minLikes",
            minv=0,
            maxv=1000000,
            label="Minimum of likes:",
            labelWidth=150,
            orientation="horizontal",
            callback=self.sendButton.settingsChanged,
            tooltip="Amount of likes that a post should have",
            step=5,
        )

        self.infoBox = InfoBox(widget=self.controlArea)

        self.sendButton.draw()
        self.infoBox.draw()
        self.updateGUI()

    #Our methods
    def updateGUI(self):
        """Update GUI state"""

        if self.selectedSource=="User":
            self.UserIDBox.setVisible(True)
            self.URLBox.setVisible(False)
        else: 
            self.UserIDBox.setVisible(False)
            self.URLBox.setVisible(True)


    def fetchUserPosts(self, username_at_instance, n=100, exclude_replies=False, exclude_reblogs=False, only_media=False):
        """Takes a string like (@)user@instance.net or a URL and returns a dictionary of the n last posts from user"""

        # If url input
        if isinstance(username_at_instance, str) and username_at_instance.startswith("http"):
            parsed_url = urlparse(username_at_instance)
            path_parts = parsed_url.path.split("/")
            if len(path_parts) > 1 and path_parts[1].startswith("@"):
                username_at_instance = path_parts[1][1:] + "@" + parsed_url.netloc

        # Delete the first "@", if given
        if isinstance(username_at_instance, str) and username_at_instance[0] == "@":
            username_at_instance = username_at_instance[1:]

        # Initialize progress bar...
        progressBar = ProgressBar(
            self,
            iterations=int(n/40)+1
        )
        
        try:
            user, instance = username_at_instance.split("@")
        except Exception as e:
                print(f"Une erreur est survenue: {e}")
                #Return an error
                self.infoBox.setText("Can't find any '@', please check your User ID", "warning")
                self.send('Scratted posts', None)

                #And free the user
                self.controlArea.setDisabled(False)
                return

        domain = f"https://{instance}/"
        
        myMastodon = Mastodon(api_base_url=domain)

        print(f"Trying to get {n} posts from @{user} on {domain}", "\n")

        try:
            user_id = myMastodon.account_lookup(user).id
        except Exception as e:
            #Return an error
            self.infoBox.setText("Can't find this account, please check your User ID", "warning")
            self.send('Scratted posts', None)

            #And free the user
            self.controlArea.setDisabled(False)
            return            

        print(f"{username_at_instance}'s id is: {user_id}", "\n")

        # Initialisation d'un dict vide pour contenir les objects
        all_posts = []
        # Créer un index pour requetes de plus de 40 posts
        max_id = None

        # Récupération des publications par lots jusqu'à atteindre le
        # nombre désiré `n` ou qu'il n'y ait plus de publications disponibles
        while len(all_posts) < n:
            posts = myMastodon.account_statuses(
                    user_id,
                    exclude_replies=exclude_replies,
                    exclude_reblogs=exclude_reblogs,
                    only_media=only_media,
                    max_id=max_id,
                    limit=min(40, n - len(all_posts)))

            all_posts.extend(posts)
            
            try:
                max_id = posts[-1].id - 1
            #If fetching all the account isn't enough, tell the user
            except:
                print(f"Got ALL posts from this user, only {len(all_posts)}")
                return all_posts

            print(f"Fetched {len(all_posts)} posts so far.")
            progressBar.advance()

        print(f"Got {len(all_posts)} posts from {username_at_instance}", "\n")
        return all_posts

    def fetchTimelines(self, instance, n=100, only_media=False):
        """
        Récupère les publications des timelines publiques locales ou fédérées d'une instance Mastodon.

        Args:
        instance (str): URL de l'instance Mastodon, par exemple "https://instance.net" ou "instance.net"
        is_local (bool): True pour récupérer à partir de la timeline locale, False pour la timeline fédérée
        n (int): Nombre de publications à récupérer

        Returns:
        all_post: Une dict contenant les publications de la timeline spécifiée
        """

        # Transformer la logique de sélection Local/Fédéré d'une string (GUI) en Bool (Utilisé par le script)

        if self.selectedSource == "Local":
            is_local = True
        else:
            is_local = False

        # Normalisation de l'URL de l'instance pour garantir l'inclusion de "https://"
        if not self.URL.startswith("http://") and not self.URL.startswith("https://"):
            instance = f"https://{self.URL}"

        # Initialize progress bar...
        progressBar = ProgressBar(
            self,
            iterations=int(n/40)+1
        )

        # Initialisation de la connexion à l'instance
        myMastodon = Mastodon(api_base_url=instance)
        
        # Initialisation d'un dict vide pour contenir les objects
        all_posts = []
        # Argument qui limite le nombre de posts
        remaining = n
        # Créer un index pour requetes de plus de 40 posts
        max_id = None

        # Récupération des publications par lots jusqu'à atteindre le nombre désiré `n` ou qu'il n'y ait plus de publications disponibles
        while remaining > 0:
            try:
                timeline = myMastodon.timeline('public', 
                                            local=is_local,
                                            max_id=max_id,
                                            only_media=only_media,
                                            limit=min(remaining, n))
                if not timeline:
                    break

                all_posts.extend(timeline)
                remaining -= 40
                max_id = timeline[-1]['id']
                limit=min(remaining, n)

                print(f"Fetched {len(all_posts)} posts so far.")
                progressBar.advance()

            except Exception as e:
                print(f"Une erreur est survenue: {e}")
                #Return an error
                self.infoBox.setText("Can't find this instance, please check your URL", "warning")
                self.send('Scratted posts', None)

                #And free the user
                self.controlArea.setDisabled(False)
                return

        print(f"Got {len(all_posts)} posts from timeline of {instance}", "\n")
        return all_posts

    def filterPosts(self, all_posts):
        """Set an empty dictionary, where the segmentation will be filtered"""
        filtered_posts = []
        for post in all_posts:
            if self.filterReblogs=="Remove" and bool(post.reblog):
                continue
            if self.filterReblogs=="Keep Only" and not bool(post.reblog):
                continue
            if self.filterReplies=="Remove" and bool(post.in_reply_to_id):
                continue
            if self.filterReplies=="Keep Only" and not bool(post.in_reply_to_id):
                continue
            if self.filterMedias=="Remove" and bool(post.media_attachments):
                continue
            if self.filterMedias=="Keep Only" and not bool(post.media_attachments):
                continue
            if post.reblogs_count < self.minReblogs:
                continue
            if post.favourites_count < self.minLikes:
                continue

            filtered_posts.append(post)

        if not filtered_posts:
            #Return an error
            self.infoBox.setText("Filters too strong, no posts were kept", "warning")
            self.send('Scratted posts', None)

            #And free the user
            self.controlArea.setDisabled(False)
            return
        return filtered_posts
    
    def createSegmentation(self, posts_dict):
        """Takes a dictionary of posts, and create an input (in HTML) of each of their content.
        Concatenate it in a single output"""

        #Pour chaque post (un dictionnaire) dans posts (un dictionnaire de dictionnaires)
        for post in posts_dict:

            #Rentrer le texte (ou placeholder) dans LTTL
            if not post.content:
                if post.reblog:
                    input_seg = Input("CantFetchTextFromReblogs", self.captionTitle)
                else:
                    input_seg = Input("OnlyMediaInThisPost", self.captionTitle)
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
            
            if getattr(post, 'application', None):
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
        if self.selectedSource == "User" and not self.userID:
            self.infoBox.setText("Please give a User ID.", "warning")
            self.send('Scratted posts', None)
            return

        if self.selectedSource in ["Federated", "Local"] and not self.URL:
            self.infoBox.setText("Please give a URL.", "warning")
            self.send('Scratted posts', None)
            return

        # Clear old created Inputs
        self.clearCreatedInputs()
        self.controlArea.setDisabled(True)

        #Initialiser filtres
        excludeReblogs = False
        excludeReplies = False
        onlyMedia = False

        #Transform filters to bool
        if self.filterReblogs=="Remove":
            excludeReblogs = True
        if self.filterReplies=="Remove":
            excludeReplies = True
        if self.filterMedias=="Keep Only":
            onlyMedia = True

        if self.selectedSource == "User":
            dictPosts = self.fetchUserPosts(self.userID, self.amount, excludeReplies, excludeReblogs, onlyMedia)
        else:
            dictPosts = self.fetchTimelines(self.URL, self.amount, onlyMedia)

        filteredPosts = self.filterPosts(dictPosts)
        self.segmentation = self.createSegmentation(filteredPosts)

        # Send confirmation of how many toots were outputted
        message = f"Successfully scrapped! {len(self.segmentation)} segments sent to output"
        self.send("Scratted posts", self.segmentation)
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
    WidgetPreview(Scratodon).run()
