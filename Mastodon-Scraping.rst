Specification widget SwissLaw
1 Introduction
1.1 But du projet

Créer un widget pour Orange Textable (v3.7) permettant l'importation des principaux textes de loi Suisse à partir de fichier XML du site fedlex.admin.ch. SwissLaw est un widget inclus dans Orange3-Textable-Prototypes, un outil développé avec le logiciel Orange 3 en utilisant le langage Python.
1.2 Aperçu des étapes

    Première version des spécifications: 14 mars 2023
    Remise des spécifications: 21 mars 2024
    Version alpha du projet: 27 avril 2024
    Version finale du projet: 1 juin 2024

1.3 Equipe et responsabilitées

    Mainteneur :
            Aris Xanthos (aris.xanthos@unil.ch)

    Olivier Oppliger (olivier.oppliger@unil.ch)

    Tache 1

    Tache 2 

    Tache 3 

    Dimitra Savits (dimitra.savits@unil.ch)

    Tache 1

    Tache 2 

    Tache 3 

    Rose Marly (rose.marly@unil.ch)

    Tache 1

    Tache 2 

    Tache 3 

    Samuel Renteria (Samuel.Renteria@unil.ch)

    Tache 1

    Tache 2 

    Tache 3 

    Laure Demierre (laure.demierre@unil.ch)

    Tache 1

    Tache 2 

    Tache 3 



2. Technique
2.1 Dépendances

    Orange 3.35
    Orange Textable 3.1.11
    Mastodon.py (Ajouter un lien Hypertexte)

2.2 Fonctionnalités minimales

(Schéma)

    - Récupérer les messages d'un utilisateur de manière structurée

2.3 Fonctionnalités principales

    - Récupérer les messages d'une instance de manière structurée

    - Récupérer les messages d'une instance fédérées de manière structurée



2.4 Fonctionnalités optionnelles

    - Permettre à l'utilisateur de nettoyer le texte en enlevant les balises xml sans devoir passer par le widget extract XML  |A DEFINIR 

    - Condition d'ajout des messages au corpus en fonctions de conditions arbitraires (Présence de médias/Interactivité)

2.5 Tests

TODO
3. Etapes
3.1 Version alpha

    L'interface graphique est complétement construite. OBJECTIFS OK
    La sélection de document au corpus était ajoutée. OBJECTIFS OK
    Le téléchargement des messages mastodons en fonction d'un flux de source séléctionné au préalable dans l'interface utilisateur au format XML était fonctionnel. DEFINIR 

3.2 Remise et présentation

    Les fonctionnalités principales sont complètement prises en charge par le logiciel. TBD
    La documentation du logiciel est complète. TBD

4. Infrastructure

Le projet est disponible sur GitHub avec le lien suivant https://github.com/Olipper/ScrapingMastoAPI