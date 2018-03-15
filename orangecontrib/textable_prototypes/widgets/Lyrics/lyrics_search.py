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

def lyrics_search():
    query_string = input("What do you want to search? ")
    page = 1
    result_number = 0
    while page<4:
        values = {'q':query_string, 'page':page}
        data = urllib.parse.urlencode(values)
        query_url = 'http://api.genius.com/search?' + data
        request = urllib.request.Request(query_url,headers={
            "Authorization" : "Bearer " + ACCESS_TOKEN, 
            "User-Agent" : USER_AGENT
            })
        response = urllib.request.urlopen(request)
        raw = response.read()
        json_obj = json.loads(raw)
        body = json_obj["response"]["hits"]

        for result in body:
            result_number += 1
            title = result["result"]["title"]
            artist = result["result"]["primary_artist"]["name"]
            path = result["result"]["path"]
            result_list[result_number] = path
            print (str(result_number) + " " + title + " - " + artist)

        page+=1
    return result_list

def html_to_text(page_url):
    page = requests.get(page_url)
    html = BeautifulSoup(page.text, "html.parser")
    [h.extract() for h in html('script')]
    lyrics = html.find("div", class_="lyrics").get_text()
    lyrics.replace('\\n', '\n')
    return lyrics

def lyrics_display(result_list):
    song_choice = input("Enter the number of the song: ")
    page_url = "http://genius.com" + result_list[int(song_choice)]
    lyrics = html_to_text(page_url)
    print(lyrics)

def main():
    lyrics_display(lyrics_search())

if __name__ == '__main__':
    main()