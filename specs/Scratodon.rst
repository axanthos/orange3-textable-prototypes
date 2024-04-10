===================
Spécification widget Scratodon (Mastodon-Scraping)
===================

1. Introduction

1.1 But du projet

    Créer un widget pour Orange Textable (v3.1.11) permettant le scraping de données de la plateforme Mastodon, afin de traiter les messages récupérés via les différents widgets disponibles sur Orange Textable.

1.2 Aperçu des étapes

    Première version des spécifications: 21 mars 2023
    Remise des spécifications: 28 mars 2024
    Version alpha du projet: 25 avril 2024
    Version finale du projet: 30 mai 2024

1.3 Equipe et responsabilitées

Mainteneur :

    Aris Xanthos (aris.xanthos@unil.ch)


Equipe de developpement :

    Olivier Oppliger (olivier.oppliger@unil.ch)

    Prototypages fonctionnalités et documentations

    Interface utilisateurs

    
    Laure Demierre (laure.demierre@unil.ch)

    Prototypages visualisations et documentations

    Interface utilisateurs


    Dimitra Savits (dimitra.savits@unil.ch)

    Recherches et documentations

    Récupération des données d'utilisateurs


    Rose Marly (rose.marly@unil.ch)

    Recherches et documentations

    Récupération des données de Timelines (locales et fédérées)



    Samuel Renteria (Samuel.Renteria@unil.ch)

    Recherches et documentations

    Liaison Mastodon - Orange 


2. Technique

2.1 Dépendances

    Orange 3.36.2 (https://orangedatamining.com/)
    Orange Textable 3.1.11 (https://orange-textable.readthedocs.io/en/latest/)
    Mastodon.py v4.2.8 (https://mastodonpy.readthedocs.io/en/stable/)

2.2 Prototypage

    .. image:: images/scratodon_example01.png
    .. image:: images/scratodon_example02.png
    .. image:: images/scratodon_example03.png

2.3 Fonctionnalités principales

    - Récupérer les messages d'un utilisateur, d'une instance ou d'une instance fédérée (dans l'ordre antéchronologique)

    - Insertion de la clé API de l'utilisateur-trice (permettant le scraping de messages privés)

    - Filtre de limitation du nombre maximum de messages à récupérer

2.4 Fonctionnalités optionnelles

    - Condition d'ajout des messages au corpus en fonctions de conditions arbitraires (Présence de médias/Interactivité)

    - Filtres: reposts, nombre d'interactions, likes et images


TODO
3. Etapes

3.1 Version alpha

    L'interface graphique est complétement construite. IN PROGRESS
    La sélection de document au corpus était ajoutée. IN PROGRESS
    Le téléchargement des messages mastodons en fonction d'un flux de source séléctionné au préalable dans l'interface  utilisateur au format XML était fonctionnel. IN PROGRESS

3.2 Remise et présentation

    Les fonctionnalités principales sont complètement prises en charge par le logiciel. TBD
    La documentation du logiciel est complète. TBD


4. Infrastructure
=========

    Le projet est disponible sur GitHub avec le lien suivant : https://github.com/Olipper/orange3-textable-prototypes
