##########################################
Specification widget EighteenCenturyPoetry
##########################################

1 Introduction
**************

1.1 But du projet
=================
Créer un widget pour Orange Textable (v1.5.2) permettant l'importation de poésies en format XML-TEI à partir du site `EighteenCenturyPoetry
<http://http://www.eighteenthcenturypoetry.org>`_.

1.2 Aperçu des etapes
=====================
* Premiere version de la specification: 17 mars 2016
* Remise de la specification: 24 mars 2016
* Version alpha du projet:  28 avril 2016
* Remise et presentation du projet:  26 mai 2016

1.3 Equipe et responsabilitées
==============================

* Frank Dat Tai Pham (`FrankDatTai.Pham@unil.ch`_):

.. _FrankDatTai.Pham@unil.ch: mailto:FrankDatTai.Pham@unil.ch

    - specification
    - interface
    - code
    - tests
    - documentation
    - GitHub

* Adriano Matos Barbosa (`adriano.MatosBarbosa@unil.ch`_):

.. _adriano.MatosBarbosa@unil.ch: mailto:adriano.MatosBarbosa@unil.ch

    - specification
    - interface
    - code
    - tests
    - documentation
    - GitHub

2. Technique
************

2.1 Dépendances
===============

* Orange 2.7

* Orange Textable 1.5.2

2.3 Fonctionnalités principales
===============================

.. image:: images/ECP_settings.png

* permettre le choix et l'importation de multiples titres en format XML-TEI à partir des données du site EighteenCenturyPoetry.

* créer et émettre une segmentation avec un segment (=Input) pour chaque poésie importée et des annotations *author*, *year* etc.

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
