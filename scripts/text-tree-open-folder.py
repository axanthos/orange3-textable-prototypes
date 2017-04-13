#TexTree 2017
# coding: utf8
from __future__ import print_function
from __future__ import unicode_literals
import re
import os
import codecs
import chardet
import fnmatch

# input_path = raw_input("Add folder path : ")
input_path = os.path.normpath("/Users/mathieu/orange3-textable-prototypes-testing/test") # Path for testing
root_path = os.path.normpath(input_path)
initial_parent_path, _ = os.path.split(root_path)

inclusion_list = [""] #by default empty list
exclusion_list = [".png,",".PNG",".jpg",".JPG",".gif",".GIF",".tiff",".TIFF",".jpeg",".JPEG",".DS_Store"] # by default exclusions : img files, .DS_Store (macOS)

def walkThroughDirectory(root_path):
	print(root_path+"\n____________________\n")

	files_list = [] #output file list

	for curr_path, dirnames, filenames in os.walk(root_path):
	#curr_path is a STRING, the path to the directory.
	#dirnames is a LIST of the names of subdirectories.
	#filenames is a LIST of the names of the non directory files in curr_path
	#symlink non traités

		curr_rel_path = curr_path[len(initial_parent_path)+1:] #defines current relative path by similar initial parent path part
		curr_rel_path_list = os.path.normpath(curr_rel_path).split(os.sep) #splits current relative path by os separator

		for filename in filenames:
			prev_non_excl_check = True
			curr_non_excl_check = prev_non_excl_check #importing previous state of the "non-exclusion check" (opposite of exclusion check)

			annotations = curr_rel_path_list[:] # annotations are different subfolders browsed
			complete_annotations = annotations[:]

			for i in inclusion_list: #i = inclusionElement

				if i in filename:
					curr_non_excl_check = True

					for e in exclusion_list:
						if e in filename:
							if (e == ""):
								pass
							else:
								curr_non_excl_check = False
								curr_non_excl_check = (prev_non_excl_check and curr_non_excl_check) #any exclusion criteria will make it False (Truth Table)

					if curr_non_excl_check: # can be True only if no exclusion criteria was found in filename
						abs_file_path = os.path.join(curr_path,filename)
						complete_annotations.insert(0,abs_file_path)
						complete_annotations.append(filename)
						complete_annotations.append(str(len(complete_annotations)-3))
						files_list.append(complete_annotations)

	openFileList(files_list)

	print("\n____________________\n",len(files_list),"files matching conditions were found")

def openFileList(files_list):

	for file in files_list:
		file_path = file[0]

		encodings = getPredefinedEncodings()
		with open(file_path,'rb') as file:
			text = file.read()
			charset_dict = chardet.detect(text)
			detected_encoding = charset_dict['encoding']
			print(file_path,charset_dict)
			try:
				encodings.remove(detected_encoding)
				encodings.insert(0,detected_encoding)

			except ValueError:
				pass

			for encoding in encodings:
				try:
					ufile_text = text.decode(encoding)
				except:
					pass

			# print(ufile_text) #this will be the Segmentation for Output

def getPredefinedEncodings():
    """Return the list of predefined encodings"""
    return [
        u'ascii',
        u'iso-8859-1',
        u'iso-8859-15',
        u'utf8',
        u'windows-1252',
        u"ascii",
        u"big5",
        u"big5hkscs",
        u"cp037",
        u"cp273",
        u"German",
        u"New",
        u"cp424",
        u"cp437",
        u"cp500",
        u"cp720",
        u"cp737",
        u"cp775",
        u"cp850",
        u"cp852",
        u"cp855",
        u"cp856",
        u"cp857",
        u"cp858",
        u"cp860",
        u"cp861",
        u"cp862",
        u"cp863",
        u"cp864",
        u"cp865",
        u"cp866",
        u"cp869",
        u"cp874",
        u"cp875",
        u"cp932",
        u"cp949",
        u"cp950",
        u"cp1006",
        u"cp1026",
        u"cp1125",
        u"Ukrainian",
        u"New",
        u"cp1140",
        u"cp1250",
        u"cp1251",
        u"cp1252",
        u"cp1253",
        u"cp1254",
        u"cp1255",
        u"cp1256",
        u"cp1257",
        u"cp1258",
        u"cp65001",
        u"Windows",
        u"New",
        u"euc_jp",
        u"euc_jis_2004",
        u"euc_jisx0213",
        u"euc_kr",
        u"gb2312",
        u"gbk",
        u"gb18030",
        u"hz",
        u"iso2022_jp",
        u"iso2022_jp_1",
        u"iso2022_jp_2",
        u"iso2022_jp_2004",
        u"iso2022_jp_3",
        u"iso2022_jp_ext",
        u"iso2022_kr",
        u"latin_1",
        u"iso8859_2",
        u"iso8859_3",
        u"iso8859_4",
        u"iso8859_5",
        u"iso8859_6",
        u"iso8859_7",
        u"iso8859_8",
        u"iso8859_9",
        u"iso8859_10",
        u"iso8859_11",
        u"iso8859_13",
        u"iso8859_14",
        u"iso8859_15",
        u"iso8859_16",
        u"johab",
        u"koi8_r",
        u"koi8_t",
        u"Tajik",
        u"New",
        u"koi8_u",
        u"kz1048",
        u"Kazakh",
        u"New",
        u"mac_cyrillic",
        u"mac_greek",
        u"mac_iceland",
        u"mac_latin2",
        u"mac_roman",
        u"mac_turkish",
        u"ptcp154",
        u"shift_jis",
        u"shift_jis_2004",
        u"shift_jisx0213",
        u"utf_32",
        u"utf_32_be",
        u"utf_32_le",
        u"utf_16",
        u"utf_16_be",
        u"utf_16_le",
        u"utf_7",
        u"utf_8",
        u"utf_8_sig",
    ]

walkThroughDirectory(root_path)
