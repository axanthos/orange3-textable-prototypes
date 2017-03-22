#Arborescence 2017
# coding: utf8
from __future__ import print_function
from __future__ import unicode_literals
import HTMLParser
import re
import os
import codecs

directory = "/Users/mathieu/Downloads/doctissimo/forum.doctissimo.fr/animaux"
output_path = "/Users/mathieu/Downloads/doctissimo/posts_text/animaux_doctissimo_posts.txt"
regexTitle = ""
forbidden_names = ["liste","top","image"]

# regex_post = re.compile('<table class="main" cellspacing="0" cellpadding="4">(.+)</div><div id="(.+?)" class="post_content"><div>(.+?)(<div class="clear"></div></p></div>)?',re.DOTALL)
regex_post = re.compile('<div id="(.+?)" class="post_content"><div>(.+?)<div class="clear',re.DOTALL)
html_parser = HTMLParser.HTMLParser()

for dirName, subdirList, fileList in os.walk(directory):

	for fname in fileList:
		check = 0
		if ".htm" in fname:
			
			for i in forbidden_names:
				if i in fname:
					check = 1
				if i in dirName:
					check = 1

			if check == 0 :
				path = (dirName+"/"+fname)
				print("\n"+path+"\n")
				output = codecs.open(output_path,'a', encoding='utf-8')
				with open(path,'r') as file:
					html = file.read()			
		
					
					post = regex_post.search(html)
					if post:
						try:
							post_text = (post.group(2))

						except AttributeError:
							pass

						try:
							post_text = post_text.decode('utf-8')
						
						except UnicodeDecodeError:
							post_text = post_text.decode('windows-1252').encode('utf-8')

						clnd_post_text = re.sub('<img(.+?)/>', '', post_text)
						clnd_post_text = re.sub(u'!!*|</></>|<>|<tr>|</tr>|=>|--*|==*|< class(.+?)>|<i>|<>|<ul>|<li>|</li>|</ul>|<img(.+?)/>|<br /><br />|<br />|&nbsp;|<span(.+?)</span>|</span>|<a(.+?)</a>|[/URL][/img]|<div align="center">|div|<b>Reprise du message précédent :</b|</b>|<b>">|<u>|</u>|</>|</p>|<p>|<td>|</td>|<table>|</table>|<table class="citation"><tr class="md_without_border">|< class="container">|<b>|< align="left">|<h1>|<a>|</a>|>< class="container"><b class="s1">|(- )*','',post_text)
						clnd_post_text = html_parser.unescape(clnd_post_text)
						print(clnd_post_text)
						output.write(clnd_post_text+"\n\n")
				output.close
				

