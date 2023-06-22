Orange3 Textable Prototypes - Poetica
===========================
# README
## Poetica Widget by LOLS

Le widget Poetica_LOLS recherche des poèmes dans le site de Poetica.fr via le nom des auteurs ou des thèmes pour permettre aux utilisateurs de Orange d'analyser les poèmes.

Le documentation est disponible sur .....

# Fonctionnalités
-------
- Dans la fenêtre du widget, vous avez deux parties : - Select criteria et - Corpus.
- La partie de "Select criteria" vous permet d'introduire les informations sur les poèmes dont vous voulez analyser,
- Dans cette partie, vous avez tout d'abord deux sections qui vous permettent de faire la recherche par le nom d'auteur et/ou par le thème.
- En cliquant sur l'onglet d'Author, vous pouvez choisir un auteur dans la liste déroulante.
- Une fois que vous avez choisi un auteur et cliqué sur "Search", vous aurez dans le premier box, tous les poèmes écrits par cet auteur choisi.
- Vous pouvez effectuer la même demarche pour choisir des poèmes en fonction de leur thème. Alors dans ce cas là, vous pouvez seulement choisir un thème dans liste puis les afficher.
- Vous avez également la possibilité de choisir un auteur et un thème et le widget Poetica va vous afficher les poèmes de cet auteur dans le thème choisi.
- Une fois que vous avez fait votre recherche, vous pouvez sélectionner les poèmes affichés dans le premier box en cliquant sur le bouton " Add to corpus".
- Cette fonctionne permet d'ajouter les poèmes sélectionnés au corpus, donc la deuxième partie de la fenêtre.
- À partir de là, vous pouvez cliquer sur "Send" et envoyer les poèmes à un autre widget à la sortie afin de réaliser des analyses que vous voulez.
- Vous pouvez en cliquant sur le bouton de "Clear result" de supprimer tous les poèmes affiché dans le box et supprimer également les poèmes que vous avez ajoutés dans le corpus en cliquant sur le bouton de "clear corpus".
- Le "refresh database" est une fonction qui efface toute la data dans le cas des changements sur le site.

# Interopérabilité
------
- Importez des données à partir du site web Poetica.fr,
- Traitez les textes de format XML importés à partir du site,
- Interface facile avec l'extension --Text Mining d'Orange--?

_ Execution du code
-----
 Poetice.py :

- Le code importe les packages nécessaires provenant de la bibliothèque Orange et d'autres packages tels que PyQt5.QtWidgets, urllib.request, inspect, re, pickle et os.
- La classe appelée "Poetica" est un sous-classe de la classe OWTextableBaseWidget de la bibliothèque Orange. Cette classe représente le widget Poetica.
- Certains propriétés et méthodes pour gérer le fonctionnement du widget :
  - Les propriétés telles que le nom, la description, l'icône, la priorité, les entrées et les sorties définissent les métadonnées du widget.
  - La méthode __init__() initialise le widget en créant les éléments de l'interface utilisateur, tels que les zones de recherche, les listes de résultats et de corpus, les boutons d'ajout et de suppression, etc.
  - La méthode dataExtraction() est responsable de l'extraction des données à partir du site web Poetica.fr. Elle utilise les modules de segmentation et d'importation fournis par la bibliothèque LTTL pour extraire les informations sur les auteurs, les thèmes et les poèmes à partir de différentes pages du site web.
  - La méthode searchFunction() est appelée lorsque le bouton de recherche est cliqué. Elle effectue une recherche en fonction des critères sélectionnés (auteur et/ou thème) et affiche les résultats dans la liste des résultats.
  - Les méthodes add() et remove() sont utilisées pour ajouter ou supprimer des éléments de la liste de corpus.

***
À propos de Poetica;

Poetica est un projet développé par le groupe LOLS en 2023. Nous avons créé ce logiciel dans le but d'aider les utilisateurs à faire des analyses sur les poèmes plus facilement.


Olivia VERBRUGGE
Leonie NUSSBAUM
Laure MARGOT
Sinem KILIC


Textable Prototypes is an open-source add-on for Orange Canvas 3. It
collects text analysis widgets that couldn't be included in the core
Textable distribution for various reasons (notably because they introduce
dependencies to third-party packages, or simply because they're not yet
production-ready), but that may still be found useful by Orange
Canvas/Textable users.


The project is brought to the community by the `department of language and
information sciences (SLI) <http://www.unil.ch/sli>`_ at the `University of
Lausanne <http://www.unil.ch>`_. It is hosted at 
`<https://github.com/axanthos/orange3-textable-prototypes>`_, and the 
documentation can be found at 
`<http://orange3-textable-prototypes.readthedocs.io/>`_.