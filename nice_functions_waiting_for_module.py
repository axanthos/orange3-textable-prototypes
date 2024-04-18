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
    #TODO fix parsing if string is "https://etc..."
    #Delete the first "@", if given
    if username_at_instance[0] == "@":
        username_at_instance = username_at_instance[1:]

    #Get user and instance frome input, format it in domain
    user, instance = username_at_instance.split("@")
    domain = f"https://{instance}/"

    #Initialize connexion to instance
    MyMastodon = Mastodon(api_base_url=domain)
    print(user, instance, domain, MyMastodon) #Debug

    #Get ID from user
    user_id = MyMastodon.account_lookup(user).id
    print(user_id)

    all_posts = MyMastodon.account_statuses(user_id)
    return all_posts

def createSegmentation(posts):
    """
    Takes a dictionary of posts, and create an input (in HTML) of each of their content.
    Concatenate it in a single output
    """
    segments = []
    #TODO for later: annotate (like, username, hasPhoto...) each post (easy and useful)
    #TODO Certains segments sont vides, probablements des rts, qui n'ont rien à afficher en .content
    # --> les supprimer de posts (selon un filtre) ou prendre le content du post partagé
    for post in posts:
        input_seg = Input(post.content)
        str_index = input_seg[0].str_index
        segments.append(
            Segment(
                str_index=str_index,
                annotations={"Visibility": post.visibility},
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
