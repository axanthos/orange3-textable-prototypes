import pickle
import requests
import urllib
from urllib import request, parse
from urllib import parse
from bs4 import BeautifulSoup
import re
import pickle
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

title_to_href = dict()

def get_all_titles(title_to_href):
	php_query_string = '/movie_script.php?movie='
	http_query_string = 'https://www.springfieldspringfield.co.uk/movie_scripts.php?order='

	# title_to_href = dict()


	for lettre in ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
				   'N', 'O', 'P', 'K', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
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

	# print(title_to_href['99 Homes (2014)'])
	print('\033[31m'+str(title_to_href.values())+'\033[0m')



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

# export_scripts(title_to_href)



def sendData(title_to_href):
#This is what will get the actual script of a single movie
	movie_names_row = input('\033[31m Entrez le nom du film et l\'année entre parenthèses, ex : 99 Homes (2014) : \033[0m')
#The first attribute of extract will be user's input, second is the list of all movie scripts, third is number of results determined by user	
	movie_names = process.extractBests(movie_names_row, title_to_href.keys(), limit=1, score_cutoff=70)
	titles = [movie_name[0] for movie_name in movie_names]
	title = titles[0]

	print(title)
	if input('\033[31m Entrez "yes" pour continuer : \033[0m') == 'yes':

		if title in title_to_href:
			print(title_to_href[title])
		else:
			print('Aucun résultat')

		page_url = "https://www.springfieldspringfield.co.uk/movie_script.php?movie=" + title_to_href[title]
		page = urllib.request.urlopen(page_url)
		soup = BeautifulSoup(page, 'html.parser')
		script = soup.find("div", {"class":"movie_script"})
		print (script.text)
	else:
		pass

get_all_titles(title_to_href)
# sendData(title_to_href)


# def addtion():
# 	x = input(int())
# 	y = input(int())

# 	print(int(x) + int(y))

# addtion()

# def soustraction():
# 	a = addtion(x)
# 	b = addtion(y)

# 	print(int(a) - int(b))
# 	exit()

# soustraction()
