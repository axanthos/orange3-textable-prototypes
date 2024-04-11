# TEST 1

# from mastodon import Mastodon
# import csv

# MyMastodon = Mastodon(api_base_url='https://ohai.social/')

# # Definir fonction pour avoir tous les posts d'un utilisateur
# def fetch_all_user_posts(user_id):
#     all_posts = MyMastodon.account_statuses(user_id)
#     return all_posts

# # ID utilisateur
# user_id = 112129653961427407

# # Tirer tous les posts de l'utilisateur specifie
# all_posts = fetch_all_user_posts(user_id)

# # Nom du fichier csv
# csv_file = 'user_posts.csv'

# # Ouvrir le fichier csv en mode write
# with open(csv_file, 'w', newline='', encoding='utf-8') as file:
#     writer = csv.writer(file)
    
#     # Headers pour le csv
#     writer.writerow(['Post ID', 'Content'])
    
#     # Ecrire tous les posts dans le csv par id du post et content
#     for post in all_posts:
#         post_id = post['id']
#         content = post['content']
#         writer.writerow([post_id, content])

# print(f'CSV file "{csv_file}" containing posts has been created.')

# TEST 2

from typing import List, Dict, Union
from mastodon import Mastodon
import csv

# Define type for a single post
Post = Dict[str, Union[str, int, List[str]]]

def get_public_timeline(instance_url: str, count: int) -> List[Post]:
    try:
        mastodon = Mastodon(api_base_url=instance_url)
        public_timeline = mastodon.timeline_public(limit=count)
        
        posts: List[Post] = []
        for status in public_timeline:
            post: Post = {
                "content": status['content'],
                "reblogs": status['reblogs_count'],
                "likes": status['favourites_count']
            }
            if 'media_attachments' in status:
                media_attachments = [attachment['url'] for attachment in status['media_attachments'] if attachment['type'] == 'image']
                post["images"] = media_attachments
            posts.append(post)
        
        return posts
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def main() -> None:
    instance_url: str = "https://mastodon.social"
    count: int = 100
    csv_file: str = "mastodon_posts.csv"
    fieldnames: List[str] = ["Content", "Reblogs", "Likes", "Images"]
    
    posts: List[Post] = get_public_timeline(instance_url, count)

    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for post in posts:
            data: Dict[str, Union[str, int]] = {
                "Content": post.get('content', ''),
                "Reblogs": post.get('reblogs', 0),
                "Likes": post.get('likes', 0),
                "Images": ", ".join(post.get('images', []))
            }
            writer.writerow(data)

    print(f"CSV file '{csv_file}' has been created with the extracted information.")

if __name__ == "__main__":
    main()
