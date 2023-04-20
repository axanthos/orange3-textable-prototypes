import csv
from urllib.request import urlopen
import requests
from LTTL.Input import Input
import LTTL.Segmenter as Segmenter

documents = [(2,0,0),
             (3,0,0),
             (7,0,0)
             ]

# for urls in segment:
#     try:
#         url = urls
#         url_ouverte = urlopen(url)
#         url_lue = url.read()
#         url_lue = url_lue.decode("utf-8")

def get_csv_elements(doc_ids):
    language = ["url_fr", "url_de", "url_it"]
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
#print(xml_contents)

created_inputs = []
for item in xml_contents:
    created_inputs.append(Input(item))

output_seg = Segmenter.concatenate(created_inputs, import_labels_as=None)
print(output_seg.to_string())