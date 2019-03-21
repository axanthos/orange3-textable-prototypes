Specifications widget Movie Scripts
=====

1 Introduction
=====
1.1 But du projet
-----
Dans Orange3, ils existent déjà des widgets qui téléchargent les pièces de théâtre classique, les paroles des chansons, etc… 
Movie Scripts widget permettra de rajouter les scripts des films ce que facilitera le travail des étudiants et des chercheurs qui
étudient le cinéma, son histoire et/ou esthétique. 

1.2 Aperçu des etapes
----
- Premiere version de la specification: 21 mars 2019
- Remise de la specification: 28 mars 2019
- Version alpha du projet: 2 mai 2019
- Remise et presentation du projet: 30 mai 2019

1.3 Equipe et responsabilitées
----
- Leonardo Cavaliere (leonardo.cavaliere@unil.ch): specification, interface, code
- Kirill Melnikov (kirill.melnikov@unil.ch): specification, interface, code
- David Fluhmannn (david.fluhmann@unil.ch): code, documentation, tests

2. Technique
====
2.1 Dépendances
----
- Orange 3.18
- Orange Textable 3.1.0
- imsdb.com
  - met à disposition un flux RSS

2.2 Fonctionnalités minimales
-----
.. image:: images/Movie_Scripts_minimal_version.png
- Effectuer des recherches dans la base de données des scripts
- Télécharger le script choisi
- Traitement correct des exceptions (HTTPError etc.)

2.3 Fonctionnalités principales
-----
.. image:: images/Movie_Scripts_principal_version.png
- Créer un corpus, pouvoir rajouter et supprimer les scripts dans ce corpus

2.4 Fonctionnalités optionnelles
-----
.. image:: images/Movie_Scripts_optional2_version.png
- Tirer une segmentation plus petite de scripts (les scenes, les répliques) 
- Faire en sort que les résultats de recherche proposent aussi des films dont les titres ressemblent les titres recherchés
- Ajouter les filtres des recherches (par langue, par genre, etc.) si la base de données le permet
- Permettre à l’utilisateur de changer l’ordre des scripts dans le corpus

2.5 Tests
-----
TODO

3. Etapes
====
3.1 Version alpha
----
- L'interface graphique est complètement construite.
- Les fonctionnalités minimales sont prises en charge par le logiciel.
3.2 Remise et présentation
----
- Les fonctionnalités principales sont complétement prises en charge par le logiciel.
- La documentation du logiciel est complète.
