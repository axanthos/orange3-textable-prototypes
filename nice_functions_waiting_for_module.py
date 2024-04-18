"""
Function to fetch user post
Can probably be recycled to fetch timelines (local/federated)
Will be integrated to the main Scraptodon.py module file

Funtion to segment (and later, annotate) posts from dict
Will also be integrated
"""

from mastodon import Mastodon
from LTTL.Segment import Segment
from LTTL.Segmentation import Segmentation
from LTTL.Input import Input

def fetch_user_posts(username_at_instance):
    "Takes a string like ' (@)user@instance.net ' and returns a dictionnary of all posts from user"
    #TODO fix parsing if string is "https://rivals.space/@macron"
    #Delete the first "@", if given
    if username_at_instance[0] == "@":
        username_at_instance = username_at_instance[1:]

    #Get user and instance frome input, format it in domain
    user, instance = username_at_instance.split("@")
    domain = f"https://{instance}/"

    #Initialize connexion to instance
    myMastodon = Mastodon(api_base_url=domain)
    print(user, instance, domain, myMastodon) #Debug

    #Get ID from user
    user_id = myMastodon.account_lookup(user).id
    print(user_id)

    all_posts = myMastodon.account_statuses(user_id)
    return all_posts

def createSegmentation(posts):
    """
    Takes a dictionary of posts, and create an input (in HTML) of each of their content.
    Concatenate it in a single output
    """
    segments = []
    #TODO for later: annotate (like, username, hasPhoto...) each post (easy and useful)
    #TODO Certains segments sont vides, images sans texte, qui n'ont rien à afficher en .content
    # -> Mettre une case dans le GUI pour exclure ou non les textes vides
    # (les posts vides restent utiles pour avoir les valeurs de stats..)
    #Annotations vides ou pas d'annotations ?
    for post in posts:
        input_seg = Input(post.content)
        str_index = input_seg[0].str_index
        segments.append(
            Segment(
                str_index=str_index,
                annotations={
                    "Account" : post.account.username,
                    "AccountDisplayName" : post.account.display_name,
                    "Date" : post.created_at, #TODO Format
                    "URL" : post.url,
                    "IsAReply" : bool(post.in_reply_to_id),
                    "IsAReblog" : bool(post.reblog),
                    "IsSensitive" : post.sensitive,
                    "HasMedias" : bool(post.media_attachments), #Rajouter types de médias ?
                    "HasContentWarning" : bool(post.spoiler_text),
                    "ReblogId" : post.reblog.id if post.reblog else None,
                    "PeopleMentionnedId" : post.mentions if post.mentions else None, #TODO id
                    "ReplyToPostId" : post.in_reply_to_id,
                    "ReplyToAccountId" : post.in_reply_to_account_id,
                    "SpoilerText" : post.spoiler_text,
                    "Visibility" : post.visibility,
                    "Application" : post.application.get("name") if post.application else None, #TODO tester
                    "Likes" : post.favourites_count,
                    "Repost" : post.reblogs_count,
                    "Language" : post.language,
                    "Tags" : post.tags if post.tags else None, #TODO tester
                    "Poll" : post.poll, #TODO Format (ou enlever ?)
                    "CustomEmojis" : post.emojis if post.emojis else None, #TODO tester
                    },
                )
            )
    segmentation = Segmentation(segments)

    for segment in segmentation:
        print(segment)
        print(segment.get_content())
    print(f"found {len(posts)} posts on this account")

if __name__ == "__main__":
    posts = fetch_user_posts("@macron@rivals.space")
    createSegmentation(posts)
