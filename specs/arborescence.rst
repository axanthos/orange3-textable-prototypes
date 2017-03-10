######################################
Specification widget Theatre-Classique
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

* permettre le choix et l'importation de multiples titres en format XML-TEI à partir des données du site Théâtre-Classique.

* créer et émettre une segmentation avec un segment (=Input) pour chaque pièce importée.

2.3 Fonctionnalités principales
===============================

.. image:: images/theatre_classique_basic_settings.png

.. image:: images/theatre_classique_advanced_settings.png

* permettre le choix et l'importation de multiples titres en format XML-TEI à partir des données du site Théâtre-Classique.

* créer et émettre une segmentation avec un segment (=Input) pour chaque pièce importée et des annotations *author*, *year* etc.

* choix possible du mode Advanced settings

* en mode Advanced settings, possibilité de sélectionner un critère de filtrage de la liste des titres (cf. image ci-dessus).

* traitement correct des exceptions (HTTPError etc.)

2.4 Fonctionnalités optionnelles
================================

* combinaison de plusieurs critères de filtrage

* filtrages plus complexes (p.ex. regex sur auteurs, intervalles d'années, etc.)

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
* Le logiciel possède des routines de test de ses fonctionnalités (principales ou optionnelles.


4. Infrastructure
=================
Le projet est disponible sur GitHub à l'adresse `https://github.com/axanthos/TextablePrototypes.git
<https://github.com/axanthos/TextablePrototypes.git>`_
