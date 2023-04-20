import csv
from urllib.request import urlopen
import requests
from LTTL.input import input
import LTTL.segmenter as segmenter

documents = [(2,0,0),
             (3,0,0)]

with open('DroitCH.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)  # skip the header row if present
    for row in reader:
        print(row[2])


def gather_every_law_name():
    list_law_names = []
    with open('DroitCH.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip header row if present
        for row in reader:
            list_law_names.append(row[1])
    #return list_law_names
    print(list_law_names)

gather_every_law_name()

# for urls in segment:
#     try:
#         url = urls
#         url_ouverte = urlopen(url)
#         url_lue = url.read()
#         url_lue = url_lue.decode("utf-8")

def get_single_csv_element(doc_id, lg_id = 0, seg_id = 0 ):
    col = lg_id + 2
    with open('DroitCH.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for i, row_data in enumerate(csv_reader):
            if i == doc_id:
                return row_data[col]
    return None

element = get_single_csv_element(7, 0)
print(element)


def get_csv_elements(doc_ids):
    results = []
    with open('DroitCH.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for doc_id, seg_id, lg_id in doc_ids:
            col = int(lg_id) + 2
            for i, row_data in enumerate(csv_reader):
                if i == int(doc_id):
                    results.append(row_data[col])
                    break
            csv_file.seek(0)
    return results

elements2 = get_csv_elements(documents)
print(elements2)
print(type(elements2))

def get_xml_content(url):
    response = requests.get(url)
    xml_content = response.content.decode('utf-8')
    return xml_content

#xml_content = get_xml_content(element)
#print(xml_content)

def get_xml_contents(urls):
    xml_contents = []
    for url in urls:
        response = requests.get(url)
        xml_content = response.content.decode('utf-8')
        xml_contents.append(xml_content)
    return xml_contents

xml_contents = get_xml_contents(elements2)
print(xml_contents)

