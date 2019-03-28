import pickle
import requests
from urllib import request
from urllib import parse
from bs4 import BeautifulSoup

all_titles_page = 'https://www.imsdb.com/all%20scripts/'
page = urllib.urlopen(all_titles_page)
soup = BeautifulSoup(page, 'html.parser')
soup.find_all('p')[0].get_text()
