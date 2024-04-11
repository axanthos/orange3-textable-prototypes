from typing import List, Dict, Union
from mastodon import Mastodon
import csv

# Define type for a single post
Post = Dict[str, Union[str, int, bool]]

def get_public_timeline(instance_url: str, count: int) -> List[Post]:
    try:
        mastodon = Mastodon(api_base_url=instance_url)
        public_timeline = mastodon.timeline_public(limit=count)
        
        posts: List[Post] = []
        for status in public_timeline:
            post: Post = {
                "TARGET": status['account']['acct'],  # Username of the author
                "CONTENT": status['content'],
                "hasREPOSTS": status['reblogs_count'] > 0,  # Check if there are reposts
                "nREPOSTS": status['reblogs_count'],
                "hasLIKES": status['favourites_count'] > 0,  # Check if there are likes
                "nLIKES": status['favourites_count'],
                "hasIMAGE": 'media_attachments' in status and any(attachment['type'] == 'image' for attachment in status['media_attachments']),  # Check if there are images
                "refIMAGE": next((attachment['url'] for attachment in status['media_attachments'] if attachment['type'] == 'image'), '')  # Reference to the first image URL if available
            }
            posts.append(post)
        
        return posts
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def main() -> None:
    instance_url: str = "https://mastodon.social"
    count: int = 5
    
    posts: List[Post] = get_public_timeline(instance_url, count)
    
    # Store posts in a dictionary
    posts_dict: Dict[int, Post] = {i+1: post for i, post in enumerate(posts)}

    print(posts_dict)

if __name__ == "__main__":
    main()
