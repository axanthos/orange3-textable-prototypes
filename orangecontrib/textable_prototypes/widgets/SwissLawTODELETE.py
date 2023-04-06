import csv

with open('DroitCH.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)  # skip the header row if present
    for row in reader:
        print(row[2])


def gather_every_law_name():
    list_law_names = []
    with open('DroitCH.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) # skip header row if present
        for row in reader:
            list_law_names.append(row[1])
    return dict_law_names
    #print(list_law_names)

gather_every_law_name()

