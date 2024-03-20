from mastodon import Mastodon
import csv

MyMastodon = Mastodon(api_base_url='https://ohai.social/')

# Definir fonction pour avoir tous les posts d'un utilisateur
def fetch_all_user_posts(user_id):
    all_posts = MyMastodon.account_statuses(user_id)
    return all_posts

# ID utilisateur
user_id = 112129653961427407

# Tirer tous les posts de l'utilisateur specifie
all_posts = fetch_all_user_posts(user_id)

# Nom du fichier csv
csv_file = 'user_posts.csv'

# Ouvrir le fichier csv en mode write
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Headers pour le csv
    writer.writerow(['Post ID', 'Content'])
    
    # Ecrire tous les posts dans le csv par id du post et content
    for post in all_posts:
        post_id = post['id']
        content = post['content']
        writer.writerow([post_id, content])

print(f'CSV file "{csv_file}" containing posts has been created.')