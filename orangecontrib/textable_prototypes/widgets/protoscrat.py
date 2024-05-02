from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler,
    InfoBox, SendButton,
)
from mastodon import Mastodon
from LTTL.Segment import Segment
from LTTL.Segmentation import Segmentation
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
        )

        self.infoBox = InfoBox(widget=self.controlArea)
        gui.separator(self.controlArea, height=3)

        basicURLBox = gui.widgetBox(
            widget=self.controlArea,
            box='Source',
            orientation='vertical',
            addSpace=False,
        )
        basicURLBoxLine1 = gui.widgetBox(
            widget=basicURLBox,
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

        gui.separator(widget=basicURLBox, height=3)
        gui.rubber(self.controlArea)

        self.sendButton.draw()
        self.infoBox.draw()

    def sendData(self):
        """Send data when pressing the 'Send Data' button"""

        # Return error if no userID was given
        if not self.userID:
            self.infoBox.setText("Please give a User ID.", "warning")
            self.send('Scratted posts', None)
            return

        #Clear old created Inputs
        self.clearCreatedInputs()

        dictPosts = self.fetchUserPosts(self.userID)
        self.segmentation = self.createSegmentation(dictPosts)

        #Send confirmation of how many toots were outputed
        message = f" Succesfully scrapped ! {len(self.segmentation)} segments sent to output"

        self.send("Scratted posts", self.segmentation)
        self.infoBox.setText(message)

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
        #TODO fix parsing if string is "https://rival3s.space/@macron"
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

        #Get all posts (for now just 1 request)        (limit's max = 40)
        #excludeReplies seems to miss some of them, but still it's better than nothing
        #onlyMedia and excludeReblogs seem to work, we should test a bit more
        all_posts = myMastodon.account_statuses(
        user_id,
        exclude_replies=self.excludeReplies,
        exclude_reblogs=self.excludeReblogs,
        only_media=self.onlyMedia,
        limit=n)

        print(f"Got {len(all_posts)} posts from {username_at_instance}", "\n")
        return all_posts

    def createSegmentation(self, posts_dict):
        """Takes a dictionary of posts, and create an input (in HTML) of each of their content.
        Concatenate it in a single output"""

        #TODO Certains segments sont vides, médias sans texte, n'ont rien à afficher en .content
        #-> Mettre une case dans le GUI pour exclure ou non les textes vides (les posts vides
        #restent utiles pour avoir les annotations, pour les stats..)
        #Q: Mieux vaut annotations vides (None; comme actuellement) ou pas d'annotations ?

        #Pour chaque post (un dictionnaire) dans posts (un dictionnaire de dictionnaires)
        for post in posts_dict:

            #Rentrer le texte dans LTTL
            input_seg = Input(post.content, self.captionTitle)
            # #Récupérer le numéro du texte qu'on vient de rentrer
            # str_index = input_seg[0].str_index

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

            #Add place holder text if post has no text (wip)
            #Should probably do it during segmentation!!
            if not segment.get_content:
                #segment.jsplu
                pass

            #Add annotations
            segment.annotations = {
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
            }

            #And replace it's original (we need to do it this way because LTTL)
            self.segmentation[idx] = segment

        #Debug, print chaque segment et son contenu
        for segment in self.segmentation:
            print(segment)
            print(segment.get_content(), "\n")
        print(f"Segmented {len(posts_dict)} posts.")


        self.controlArea.setDisabled(False)

        return self.segmentation

if __name__ == "__main__":
    WidgetPreview(Protoscrat).run()
