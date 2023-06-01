Orange3 Textable Prototypes - Poetica
===========================

README Widget Poetica par LOLS

Le widget Poetica recherche des poèmes sur le site Poetica.fr en utilisant les noms des auteurs ou les thèmes, permettant ainsi aux utilisateurs d'Orange d'analyser des poèmes.

La documentation est disponible `ici <http://orange3-textable-prototypes.readthedocs.io/>`_

Fonctionnalités
-------
- La fenêtre du widget se compose de deux parties : "Sélection des critères" et "Corpus".
- La partie "Sélection des critères" vous permet de saisir les informations sur les poèmes que vous souhaitez analyser.
- Dans cette partie, il y a deux sous-sections qui vous permettent de rechercher par nom d'auteur et/ou par thème.

- En cliquant sur l'onglet "Auteur", vous pouvez choisir un auteur dans la liste déroulante.
- Une fois que vous avez choisi un auteur et cliqué sur "Rechercher", tous les poèmes écrits par cet auteur apparaîtront dans la première boîte.
- Vous pouvez effectuer la même procédure pour choisir des poèmes en fonction de leur thème. Dans ce cas, vous pouvez sélectionner un thème dans la liste et afficher les poèmes correspondants.
- Vous avez également la possibilité de choisir à la fois un auteur et un thème. Le widget Poetica affichera les poèmes de cet auteur dans le thème sélectionné.
- Après avoir effectué votre recherche, vous pouvez sélectionner les poèmes affichés dans la première boîte en cliquant sur le bouton "Ajouter au corpus".
- Cette fonctionnalité vous permet d'ajouter les poèmes sélectionnés au corpus affiché dans la deuxième partie de la fenêtre.
- À partir de là, vous pouvez cliquer sur "Envoyer" pour envoyer les poèmes à un autre widget pour une analyse plus approfondie.
- Vous pouvez effacer les poèmes affichés dans les résultats en cliquant sur le bouton "Effacer les résultats" et supprimer les poèmes ajoutés au corpus en cliquant sur le bouton "Effacer le corpus".
- Le bouton "Actualiser la base de données" permet de mettre à jour le cache du widget, cette opération peut prendre du temps.

Interopérabilité
------
- Importez des données à partir du site web Poetica.fr.
- Traitez les textes au format XML importés à partir du site.
- Interface facile avec l'extension --Text Mining d'Orange--?

Exécution du code
-----
Poetica.py :

- Le code importe les packages nécessaires provenant de la bibliothèque Orange et d'autres packages tels que PyQt5.QtWidgets, urllib.request, inspect, re, pickle et os.
- La classe appelée "Poetica" est une sous-classe de la classe OWTextableBaseWidget de la bibliothèque Orange. Cette classe représente le widget Poetica.
- Certaines propriétés et méthodes permettent de gérer le fonctionnement du widget :
- Les propriétés telles que le nom, la description, l'icône, la priorité, les entrées et les sorties définissent les métadonnées du widget.
- La méthode __init__() initialise le widget en créant les éléments de l'interface utilisateur, tels que les zones de recherche, les listes de résultats etde corpus, les boutons d'ajout et de suppression, etc.
- La méthode dataExtraction() est responsable de l'extraction des données à partir du site web Poetica.fr. Elle utilise les modules de segmentation et d'importation fournis par la bibliothèque LTTL pour extraire les informations sur les auteurs, les thèmes et les poèmes à partir de différentes pages du site web.
- La méthode searchFunction() est appelée lorsque le bouton de recherche est cliqué. Elle effectue une recherche en fonction des critères sélectionnés (auteur et/ou thème) et affiche les résultats dans la liste des résultats.
- Les méthodes add() et remove() sont utilisées pour ajouter ou supprimer des éléments de la liste de corpus.

À propos de Poetica :
-----
Poetica est un projet développé par le groupe LOLS en 2023. Nous avons créé ce logiciel dans le but d'aider les utilisateurs d'Orange à analyser les poèmes plus facilement.

Olivia VERBRUGGE
Leonie NUSSBAUM
Laure MARGOT
Sinem KILIC

Textable Prototypes est une extension open-source pour Orange Canvas 3. Elle regroupe des widgets d'analyse de texte qui n'ont pas pu être inclus dans la distribution principale de Textable pour diverses raisons (notamment parce qu'ils introduisent des dépendances à des packages tiers ou simplement parce qu'ils ne sont pas encore prêts pour la production), mais qui peuvent toujours être utiles aux utilisateurs d'Orange Canvas/Textable.

Le projet est proposé à la communauté par le `département des sciences du langage et de l'information (SLI) <http://www.unil.ch/sli>`_ de l'`Université de Lausanne <http://www.unil.ch>`_. Il est hébergé sur
`<https://github.com/axanthos/orange3-textable-prototypes>`_, et la documentation peut être consultée sur
`<http://orange3-textable-prototypes.readthedocs.io/>`_.