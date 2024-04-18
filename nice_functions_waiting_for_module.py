"""
Function to fetch posts from a user
Can probably be recycled to fetch timelines (local/federated)
Will be integrated to the main Scraptodon.py module file

Funtion to segment and annotate each post from a dict of posts
Will also be integrated to the module
"""

from mastodon import Mastodon
from LTTL.Segment import Segment
from LTTL.Segmentation import Segmentation
from LTTL.Input import Input

def fetchUserPosts(username_at_instance, n = 100):
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

def createSegmentation(posts_dict):
    """Takes a dictionary of posts, and create an input (in HTML) of each of their content.
    Concatenate it in a single output"""

    #TODO for later: annotate (like, username, hasPhoto...) each post (easy and useful)
    #TODO Certains segments sont vides, RT et images sans texte, n'ont rien à afficher en .content
    #-> Mettre une case dans le GUI pour exclure ou non les textes vides (les posts vides
    #restent utiles pour avoir les annotations, pour les stats..)
    #Q: Mieux vaut annotations vides (None; comme actuellement) ou pas d'annotations ?

    #Initialisation de notre liste de segments
    segments = []

    #Pour chaque post (un dictionnaire) dans posts (un dictionnaire de dictionnaires)
    for post in posts_dict:

        #Rentrer le texte dans LTTL
        input_seg = Input(post.content)
        #Récupérer le numéro du texte qu'on vient de rentrer
        str_index = input_seg[0].str_index

        #Rajouter chaque segment dans la liste
        segments.append(
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
    segmentation = Segmentation(segments)

    #Debug, print chaque segment et son contenu
    for segment in segmentation:
        print(segment)
        print(segment.get_content(), "\n")
    print(f"Segmented {len(posts_dict)} posts.")

if __name__ == "__main__":
    posts = fetchUserPosts("@macron@rivals.space")
    #Le compte parodique de Macron a seulement 60~ posts, c'est pratique pour tester
    createSegmentation(posts)
