######################################
Specification widget Arborescence
######################################

1 Introduction
**************

1.1 But du projet
=================
Créer un widget pour Orange Textable (v3.0b0) permettant d’importer une arborescence complète contenant des fichiers de texte.

1.2 Aperçu des étapes
=====================
* Première version de la specification: 16 mars 2017
* Remise de la spécification: 23 mars 2017
* Version alpha du projet:  27 avril 2017
* Remise et présentation du projet:  25 mai 2017

1.3 Équipe et responsabilités
==============================

* Olivier Cavaleri (`olivier.cavaleri@unil.ch`_):

.. _olivier.cavaleri@unil.ch: mailto:olivier.cavaleri@unil.ch

    - specification
    - interface
    - code
    - documentation

* Augustin Maillefer (`augustin.maillefer@unil.ch`_):

.. _augustin.maillefer@unil.ch: mailto:augustin.maillefer@unil.ch

    - specification
    - interface
    - code
    - documentation

* Mathieu Mercapide (`mathieu.mercapide@unil.ch`_):

.. _mathieu.mercapide@unil.ch: mailto:mathieu.mercapide@unil.ch

    - specification
    - interface
    - code
    - documentation

2. Technique
************

2.1 Dépendances
===============

* Orange 3.3.12

* Orange Textable 3.0b0

2.2 Fonctionnalités minimales
=============================

.. image:: images/arborescence_folder_input.png

* permettre le choix et l'importation de multiples fichiers en format texte (.txt, .xml, .html) dans une arborescence.

* créer et émettre une segmentation avec un segment pour chaque fichier importé et une annotation par niveau dans l'arborescence (dont une contenant tout le path)

2.3 Fonctionnalités principales
=============================

.. image:: images/arborescence_folder_input.png

* permettre le choix et l'importation de multiples fichiers en format texte (.txt, .xml, .html) dans une arborescence.

* détection automatique de l'encoding (utf-8, iso 8859-1, etc...) puis tests des plus fréquents en cas d'erreur.

* créer et émettre une segmentation avec un segment pour chaque fichier importé et une annotation par niveau dans l'arborescence (dont une contenant tout le path)

* traitement correct des exceptions (UnicodeEncodeError ou UnicodeDecodeError)

2.4 Fonctionnalités optionnelles
================================

* filtrage des extensions de fichier (ex : ne sélectionner que les .txt)

* conditions d'exclusion de fichiers ()

* échantillonage (x % de fichiers)

2.5 Tests
=========

TODO

3. Etapes
*********

3.1 Version alpha
=================
* L'interface graphique est complètement construite.
* Les fonctionnalités minimales sont prises en charge par le logiciel.

3.2 Remise et présentation
==========================
* Les fonctionnalités principales sont complétement prises en charge par le logiciel.
* La documentation du logiciel est complète.
* Le logiciel possède des routines de test de ses fonctionnalités (principales ou optionnelles)

4. Infrastructure
=================
Le projet est disponible sur GitHub à l'adresse `https://github.com/mmercapi/orange3-textable-prototypes.git
<https://github.com/mmercapi/orange3-textable-prototypes.git>`_
