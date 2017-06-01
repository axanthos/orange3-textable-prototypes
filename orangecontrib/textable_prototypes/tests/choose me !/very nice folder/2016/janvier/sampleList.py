import random
import math
# Initialisation de la liste qui normalement sera creee par l'iteration a travers tous les fichiers du dossier source
#Il reste a prendre la liste depuis le Widget
myList = [["Un", "1"],["Deux", "2"],["Trois", "3"],["Quatre", "4"]]

# Initialisation d'un parametre qui decidera de l'echantillonage
#Il reste a importer la variable inseree dans Widget

m = 0.5


# Solution A On melange la liste pour prendre ensuite les "m" premiers

random.shuffle(myList)


#On definit le nombre de fichiers voulus selon le parametre d'echantillonage "m", arrondi au superieur
nOfFiles = int(math.ceil(len(myList)*m))
print(type(nOfFiles))
#On prend les "nOfFiles" premiers fichiers de la liste
selectedFiles = myList[:nOfFiles]


print (selectedFiles)




# Solution B on fait un tirage sans remise avec une formule directe