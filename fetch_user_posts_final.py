"""
Function to fetch user post
Can probably be recycled to fetch timelines (local/federated)
Will be integrated to the main Scraptodon.py module file
"""

from mastodon import Mastodon
import csv

def fetch_user_posts(username_at_instance):
    "Takes a string like ' (@)user@instance.net ' and returns a dictionnary of all posts from the user"
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

if __name__ == "__main__":
    print(fetch_user_posts("macron@rivals.space")) 
