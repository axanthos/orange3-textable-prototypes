
import pickle
import requests
import urllib
from urllib import request
from urllib import parse
from bs4 import BeautifulSoup

all_titles_page = 'https://www.imsdb.com/all%20scripts/'
page = urllib.request.urlopen(all_titles_page)
soup = BeautifulSoup(page, 'html.parser')
for link in soup.find_all('a'):
    print(link.get('href'))