from itertools import islice
from youtube_comment_downloader import *
downloader = YoutubeCommentDownloader()
comments = downloader.get_comments_from_url('https://www.youtube.com/watch?v=ScMzIvxBSi4', sort_by=SORT_BY_POPULAR)
#for comment in islice(comments, 10):
#    print(comment)

newlist = [x for x in comments]
print(newlist)