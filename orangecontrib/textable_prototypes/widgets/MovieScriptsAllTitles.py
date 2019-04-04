import pickle
import requests
import urllib
from urllib import request, parse
from urllib import parse
from bs4 import BeautifulSoup
import re
import pickle

php_query_string = '/movie_script.php?movie='
http_query_string = 'https://www.springfieldspringfield.co.uk/movie_scripts.php?order='

title_to_href = dict()


for lettre in ['0']:#, 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
			   #'N', 'O', 'P', 'K', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
	page_num = 1
	while True:
		page_url = http_query_string + '%s&page=%i' % (lettre, page_num)
		page = urllib.request.urlopen(page_url)
		soup = BeautifulSoup(page, 'html.parser')
		script_links = soup.findAll('a', attrs={'class': re.compile("^script-list-item")})
		if not script_links:
			break
		links = dict()
		for link in soup.findAll('a', attrs={'class': re.compile("^script-list-item")}):
			links[link.text] = link.get('href')[len(php_query_string):]
		title_to_href.update(links)

		print(page_num)
		page_num += 1

print(title_to_href)



def export_scripts(title_to_href):
	try:
		name_file = input('Entrez le nom du fichier à exporter: ')
		exported_file = open(name_file, 'w', encoding='utf8')
		exported_file.write(str(title_to_href))
		exported_file.close()

		'{:*^20}'.format('title_to_href')

	except IOError:
		print('Impossible de lire le fichier')

	return

export_scripts(title_to_href)



############################

# for link in soup.findAll('a', attrs={'class': re.compile("^script-list-item")}):
#     links[link.text] = link.get('href')
#     # links.append(link.get('.text'))
 
# print(links)
# # print(links.values())


###to go in the page wich containes the script###

# script_list = []

# movie_script_url = 'https://www.springfieldspringfield.co.uk' + list(links.values())[0]
# print(movie_script_url)
# page_movie_script = urllib.request.urlopen(movie_script_url)
# soup_movie_script = BeautifulSoup(page_movie_script, 'html.parser')

# for script in soup.find_all('div', attrs={'class': re.compile('scrolling-script')}):
# 	script.append(script.get('scrolling-script-container'))
# print(script_list)




# https://www.springfieldspringfield.co.uk/movie_scripts.php?order=A&page=1
# https://www.springfieldspringfield.co.uk/movie_scripts.php?order=B&page=1
# https://www.springfieldspringfield.co.uk/movie_script.php?movie=a-2nd-hand-lover



