import imdb

ia = imdb.IMDb()

search = ia.search_movie('Matrix')
reviews = ia.get_movie_reviews(search[0].movieID)
print(reviews)
