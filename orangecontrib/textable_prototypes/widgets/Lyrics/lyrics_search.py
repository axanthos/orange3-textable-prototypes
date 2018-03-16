#------- REPARE ERROR MAC -------
#   $ sudo pip3 install requests
#   $ pip3 install Beautifulsoup4
#   $ python3 MacOS_if_SSLError.px
#--------- HOPE IT WORKS ---------

import urllib
import urllib.request
import urllib.parse
import json
import requests
import sys
from bs4 import BeautifulSoup

result_list = {}
ACCESS_TOKEN = "PNlSRMxGK1NqOUBelK32gLirqAtWxPzTey9pReIjzNiVKbHBrn3o59d5Zx7Yej8g"
USER_AGENT = "CompuServe Classic/1.22"

def main():
    lyrics_search()

def lyrics_search():
    """Searches a list of songs with keywords"""
    search_type = input("Songs (1) or artists search (2)? ")
    query_string = input("What do you want to search? ")
    page = 1
    result_number = 0
    result_artist = []

    while page<2:
        values = {'q':query_string, 'page':page}
        data = urllib.parse.urlencode(values)
        query_url = 'http://api.genius.com/search?' + data
        json_obj = url_request(query_url)
        body = json_obj["response"]["hits"]

        if int(search_type) == 1:
            for result in body:
                result_number += 1
                title = result["result"]["title"]
                artist = result["result"]["primary_artist"]["name"]
                artist_id = result["result"]["primary_artist"]["id"]
                path = result["result"]["path"]
                result_list[result_number] = {'artist': artist, 'artist_id':artist_id, 'path':path, 'title':title}
                print (str(result_number) + " " + title + " - " + artist)
        elif int(search_type) == 2:
            for result in body:
                artist = result["result"]["primary_artist"]["name"]
                artist_id = result["result"]["primary_artist"]["id"]
                if artist not in result_artist:
                    result_artist.append(artist)
                    result_number = len(result_artist)
                    result_list[result_number] = {'artist': artist, 'artist_id':artist_id}
                    print(str(result_number) + " " + artist)

        page+=1

    if int(search_type) == 1:
        lyrics_display(result_list)
    elif int(search_type) == 2:
        artist_display(result_list) 

def artist_display(result_list):
    """Displays the most popular songs of an artist"""
    artist_nbr = input("Enter the number of the artist: ")
    results_per_page = input("Enter the number of songs to display: ")
    artist_nbr = int(artist_nbr)
    artist_id = result_list[artist_nbr]['artist_id']
    artist_url = "http://api.genius.com/artists/" + str(artist_id) + "/songs?sort=popularity&per_page=" + results_per_page
    json_obj = url_request(artist_url)
    body = json_obj["response"]["songs"]
    result_number = 0

    for result in body:
        result_number += 1
        title = result["title"]
        artist = result["primary_artist"]["name"]
        path = result["path"]
        result_list[result_number] = {'artist': artist, 'path':path, 'title':title}
        print (str(result_number) + " " + title + " - " + artist)

    lyrics_display(result_list)

def lyrics_display(result_list):
    """Displays the lyrics of the song chosen by the user in the search results"""
    song_choice = input("Enter the number of the song: ")
    song_choice = int(song_choice)
    result_choice = result_list[song_choice]
    page_url = "http://genius.com" + result_choice['path']
    lyrics = html_to_text(page_url)
    song_info = result_choice['artist'] + " - " + result_choice['title']
    print(song_info)
    print(lyrics)

def url_request(url):
    """Opens a URL and returns it as a JSON object"""
    request = urllib.request.Request(url,headers={
            "Authorization" : "Bearer " + ACCESS_TOKEN,
            "User-Agent" : USER_AGENT
            })
    response = urllib.request.urlopen(request)
    raw = response.read()
    json_obj = json.loads(raw)
    return json_obj

def html_to_text(page_url):
    """Extracts the lyrics (as a string) of the html page"""
    page = requests.get(page_url)
    html = BeautifulSoup(page.text, "html.parser")
    [h.extract() for h in html('script')]
    lyrics = html.find("div", class_="lyrics").get_text()
    lyrics.replace('\\n', '\n')
    return lyrics

if __name__ == '__main__':
    main()