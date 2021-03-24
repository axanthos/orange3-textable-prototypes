=============================
Spécifications widget TextSum
=============================


1. Introduction
===============

1.1 But du projet
---------------
Créer un widget pour Orange Textable (v3.1.8) permettant de résumer un ou plusieurs textes.

1.2 Aperçu des étapes
---------------
- Première version des spécifications: 25 mars 2021
- Remise des spécifications: 1er avril 2021
- Version alpha du projet: 29 avril 2021
- Version finale du projet: 3 juin 2021

1.3 Equipe et responsabilités
---------------
- Melinda Femminis

.. 

    - specification
    - code
    - tests
    - Github
    - Interface
    - documentation
    
    
- Jason Ola

.. 

    - code
    - Github
    - tests
    - documentation
    - spécifications
    - interface
    
- Catherine Pedroni

.. 

    - interface
    - spécification
    - documentation
    - tests
    - Github
    - code
    


2. Technique
=============

2.1 Dépendances
---------------
- Orange 3.24
- Orange Textable 3.1.8
- Bert Extractive Summarizer 0.7.1
- Gensim

2.2 Fonctionnalités minimales
-----------------------------

- Prendre une segmentation en entrée et proposer 2 possiblités:
    - résumer la segmentation comme un seul texte
    - résumer chaque segement séparément 
- Avoir le choix du nombre de phrases que le résumé doit contenir
- Créer une segmentation de sortie


2.3 Fonctionnalités principales
-------------------------------

- Prendre une segmentation en entrée et proposer 2 possiblités:
    - résumer la segmentation comme un seul texte
    - résumer chaque segement séparément 
- Proposer différents algorithmes de résumé
- Gestion de différentes langues
- Avoir le choix du nombre de phrases que le résumé doit contenir
- Créer une segmentation de sortie


2.4 Fonctionnalités optionnelles
--------------------------------
- Ajouter une option de visualisation dans le widget

3. Etapes
==========
3.1 Version alpha
---------------


3.2 Remise et présentation
---------------

4. Infrastructure
==================
