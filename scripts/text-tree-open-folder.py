#Arborescence 2017
# coding: utf8
from __future__ import print_function
from __future__ import unicode_literals
import HTMLParser
import re
import os
import codecs
import fnmatch

root_path = os.path.normpath("/Users/mathieu/orange3-textable-prototypes-testing/test")
initial_parent_path, _ = os.path.split(root_path)

inclusion_list = [""] #by default empty list
exclusion_list = [".png,",".PNG",".jpg",".JPG",".gif",".GIF",".tiff",".TIFF",".jpeg",".JPEG",".DS_Store"] # by default exclusions : img files, .DS_Store (macOS)

def goThroughDirectory(root_path):
	output_files_list = []
	print(root_path+"\n____________________\n")

	# countAll=0
	countFiles=0

	for curr_path, dirnames, filenames in os.walk(root_path):
	#curr_path is a STRING, the path to the directory.
	#dirnames is a LIST of the names of subdirectories.
	#filenames is a LIST of the names of the non directory files in curr_path
	#symlink non traités

		curr_rel_path = curr_path[len(initial_parent_path)+1:] #defines current relative path by similar initial parent path part
		curr_rel_path_list = os.path.normpath(curr_rel_path).split(os.sep) #splits current relative path by os separator

		prev_non_excl_check = True
		for filename in filenames:
			curr_non_excl_check = prev_non_excl_check #importing previous state of the "non-exclusion check" (opposite of exclusion check)

			annotations = curr_rel_path_list[:] # annotations are different subfolders browsed

			complete_annotations = annotations[:]
			complete_annotations.append(filename)
			complete_annotations.append(str(len(complete_annotations)-1))

			for i in inclusion_list: #i = inclusionElement
				for e in exclusion_list:
					if i in filename:
						if e in filename:
							if (e == ""):
								pass
							else:
								curr_non_excl_check = False
								curr_non_excl_check = (prev_non_excl_check and curr_non_excl_check) #any exclusion criteria will make it False

			if curr_non_excl_check: # can be True only if no exclusion criteria was found in filename
				countFiles +=1
				# print(complete_annotations)
				abs_file_path = os.path.join(curr_path,filename)
				print(complete_annotations)

	print("\n_____\n",countFiles,"files matching conditions were found")

def openFile(file_path):
	with open(file_path,'r') as file:
		text = file.read()

		try:
			file_text = text.decode('utf-8')

		except UnicodeDecodeError:
			file_text = text.decode('windows-1252').encode('utf-8')

		print(file_text)

goThroughDirectory(root_path)
