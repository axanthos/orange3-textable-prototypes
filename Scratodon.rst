Spécification widget Scratodon (Mastodon-Scraping)

1 Introduction
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

    Prototypages et documentations

    Interface utilisateurs 

    Tache 3 

    Dimitra Savits (dimitra.savits@unil.ch)

    Recherches et documentations

    Récupération des données

    Tache 3 

    Rose Marly (rose.marly@unil.ch)

    Recherches et documentations

    Récupération des données

    Tache 3 

    Samuel Renteria (Samuel.Renteria@unil.ch)

    Recherches et documentations

    Liaison Mastodon - Orange 

    Tache 3 

    Laure Demierre (laure.demierre@unil.ch)

    Prototypages et documentations

    Interface utilisateurs

    Tache 3 



2. Technique
2.1 Dépendances

    Orange 3.36.2
    Orange Textable 3.1.11
    Mastodon.py (https://mastodon.social/explore)

2.2 Fonctionnalités minimales

(Schéma)

    - Récupérer les messages d'un utilisateur de manière structurée

2.3 Fonctionnalités principales

    - Récupérer les messages d'une instance de manière structurée

    - Récupérer les messages d'une instance fédérées de manière structurée

    - Filtres de temps de traitement et limitation de messages récupérés

2.4 Fonctionnalités optionnelles

    - Condition d'ajout des messages au corpus en fonctions de conditions arbitraires (Présence de médias/Interactivité)
    - Filtres: nombre d'interactions, likes, reposts et images

2.5 Tests

TODO
3. Etapes
3.1 Version alpha

    L'interface graphique est complétement construite. OBJECTIFS OK
    La sélection de document au corpus était ajoutée. OBJECTIFS OK
    Le téléchargement des messages mastodons en fonction d'un flux de source séléctionné au préalable dans l'interface  utilisateur au format XML était fonctionnel. DEFINIR 

3.2 Remise et présentation

    Les fonctionnalités principales sont complètement prises en charge par le logiciel. TBD
    La documentation du logiciel est complète. TBD

4. Infrastructure

Le projet est disponible sur GitHub avec le lien suivant : https://github.com/Olipper/orange3-textable-prototypes
