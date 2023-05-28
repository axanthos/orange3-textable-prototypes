######################################
Specification widget SwissLaw
######################################

1 Introduction
**************

1.1 But du projet
=================
Créer un widget pour Orange Textable (v3.7) permettant l'importation des principaux textes de loi Suisse à partir de
fichier XML du site `fedlex.admin.ch <https://www.fedlex.admin.ch/fr/home?news_period=last_day&news_pageNb=1&news_order=
desc&news_itemsPerPage=10>`_. SwissLaw est un widget inclus dans Orange3-Textable-Prototypes, un outil développé avec
le logiciel Orange 3 en utilisant le langage Python.

1.2 Aperçu des étapes
=====================
* Première version des spécifications: 23 mars 2023
* Remise des spécifications: 30 mars 2023
* Version alpha du projet: 27 avril 2023
* Version finale du projet: 1 juin 2023

1.3 Equipe et responsabilitées
==============================
* Mainteneur :
    - Aris Xanthos (aris.xanthos@unil.ch)

* Antoine Vigand (antoine.vigand@unil.ch)
 - specification
 - interface
 - code
 - tests
 - Github
* Elijah Green (elijah.green@unil.ch)
 - specification
 - code
 - tests
 - Github
* Samantha Allendes (samantha.allendesbravo@unil.ch)
 - specification
 - documentation
 - interface
 - code
 - Github
* Thomas Rywalski (thomas.rywalski@unil.ch)
 - specification
 - documentation
 - interface
 - code

2. Technique
************

2.1 Dépendances
===============
* Orange 3.35

* Orange Textable 3.1.11

* https://www.fedlex.admin.ch/ (29.03.2023)

2.2 Fonctionnalités minimales
=============================
.. image:: images/DroitCHVM1.png

* Permettre à l'utilisateur de récupérer un texte de loi Suisse parmi deux documents: le code des obligations et le code civil
* Ajouter l'entier du document au corpus en Français
* Avoir la possibilité d'envoyer automatiquement le corpus à l'output


2.3 Fonctionnalités principales
===============================

 .. image:: images/DroitCHVP1.png

 .. image:: images/DroitCHVP2.png

 .. image:: images/DroitCHVP3.png

* Télécharger les documents de loi suisse

* Segmenter les documents par Titre, Chapitre ou Article

* Télécharger les documents en français, italien ou allemand

* Ajouter, retirer les documents dans un panier

* Séléctionner les documents du panier qui nous intéressent

* Permettre à l'utilisateur de récupérer un texte de loi Suisse parmi une liste des 20 documents de loi les plus consultés.
* Permettre à l'utilisateur de séléctionner la langue nationale dans laquelle il souhaite récupérer le texte de loi: en
Allemand, Français ou Italien.
* Permettre à l'utilisateur de récupérer l'entier du document ou de faire une segmentation par Titre, Chapitre ou article.


2.4 Fonctionnalités optionnelles
================================
* Permettre à l'utilisateur de récupérer n'importe quel texte de loi disponible sur le site https://www.fedlex.admin.ch/

2.5 Tests
=========
TODO

2.6 Installation
============
Pour utiliser le widget SwissLaw, vous devez avoir Orange 3 et Orange3-Textable-Prototypes installés.
Suivez les instructions ci-dessous pour installer le widget :

1. Installez Orange 3 : `Guide d'installation Orange 3 <https://orangedatamining.com/download/#macos>`_
2. Installez Textable Prototypes : `Guide d'installation Textable Prototypes <https://pypi.org/project/Orange3-Textable-Prototypes/>`_

2.7 Utilisation
===========
1. Lancez Orange 3 et accéder à la section "Textable Prototypes".
2. Faites glisser et déposez le widget "Swiss Law" sur la zone de travail.
3. Configurez le widget en sélectionnant les options souhaitées.
4. Connectez le widget SwissLaw à d'autres widgets ou composants de votre flux de travail.
5. Exécutez le flux de travail pour accéder et analyser les documents de loi suisse.

3. Etapes
*********

3.1 Version alpha
=================
* L'interface graphique est complétement construite.

* La séléction de document au corpus était ajoutée.

* Le téléchargement des textes de loi en Français au format XML était fonctionnel.

3.2 Remise et présentation
==========================
* Les fonctionnalités principales sont complétement prises en charge par le logiciel.

* La documentation du logiciel est complète.

4. Infrastructure
=================
Le projet est disponible sur GitHub avec le lien suivant `SwissLaw Github
<https://github.com/axanthos/TextablePrototypes.git>`_