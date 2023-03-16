############################
Specification widget Poetica
############################

1 Introduction
**************

1.1 But du projet
=================

Créer un widget pour Orange Textable (v3.1.8) permettant de rechercher
des poèmes par le nom de leur auteur, leur année de publication ou par
différents thèmes.


1.2 Aperçu des etapes
=====================

* Première version des spécifications: 16 mars 2023
* Remise des spécifications: 23 mars 2023
* Version alpha du projet:
* Version finale du projet:


1.3 Equipe et responsabilités
==============================

* Olivia Verbrugge :
    - code
    - extraction des données
* Sinem Kilic :
    - maquette
    - code
* Leonie Nussbaum :
    - code
    - documentation
    - GitHub
* Laure Margot :
    - specification
    - code


2. Technique
************

2.1 Dépendances
===============

* Orange 3.30

* Orange Textable 3.1.8

* poetica *.*


2.2 Fonctionnalités minimales
=============================

.. image:: images/charnet_minimal.png

* Première box : afficher la liste des auteurs établie par Poetica. Les auteurs sont triés par ordre alphabétique.

* Deuxième box : afficher la liste des dates établie par Poetica. Les dates sont triées par décénies, de manière croissante.

* Troisième box : afficher la liste des thèmes établie par Poetica. Les thèmes sont triés par ordre alphabétique.

* Bouton search permet de sortir tous les différents poèmes par auteur, date ou thème.

NB :
    * Si aucun champ n'est rempli, tous les poèmes sortent.
    * Si un champ est rempli, les poèmes sortis sont ceux correspoondant au champ rempli.
    * Si plusieurs champs sont remplis, la recherche est affinée et les poèmes sortent spécifiquement.





2.3 Fonctionnalités principales
===============================

.. image:: images/charnet_principal.png

* Première box : afficher la liste des auteurs établie par Poetica. Les auteurs sont triés par ordre alphabétique.

* Deuxième box : afficher la liste des dates établie par Poetica. Les dates sont triées par décénies, de manière croissante.

* Troisième box : afficher la liste des thèmes établie par Poetica. Les thèmes sont triés par ordre alphabétique.

* Bouton search permet de sortir tous les différents poèmes par auteur, date ou thème.


2.4 Fonctionnalités optionnelles
================================

* A voir...


2.5 Tests
=========

TODO


3. Etapes
*********

3.1 Version alpha
=================

* L'interface graphique pour les fonctionnalités minimales est complètement construite.
* Les fonctionnalités minimales sont prises en charge par le logiciel et ont été testées.


3.2 Remise et présentation
==========================

* L'interface graphique est complètement construite.
* Les fonctionnalités principales sont complétement prises en charge par le logiciel.
* La documentation du logiciel est complète.
* Les fonctionnalités principales (et, le cas échéant, optionnelles) sont implémentées et ont été testées.


4. Infrastructure
=================

Le projet est disponible sur GitHub à l'adresse `https://github.com/axanthos/orange3-textable-prototypes.git
<https://github.com/axanthos/orange3-textable-prototypes.git>`_