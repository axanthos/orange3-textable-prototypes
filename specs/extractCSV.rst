################################
Specification widget extractCSV
################################

1 Introduction
**************

1.1 But du projet
=================

Créer un widget pour Orange Textable (v3.24.1) permettant d’importer divers données tabulées (ex: CSV, données WhatsApp…) sous forme de segmentation Textable.


1.2 Aperçu des etapes
=====================

* Première version des spécifications: 26 mars 2020
* Remise des spécifications: 2 avril 2020
* Version alpha du projet:  30 avril 2020
* Version finale du projet:  28 mai 2020


1.3 Equipe et responsabilités
==============================

* Aris Xanthos :

	- superviseur

* Sorcha Walsh

	- idéation du projet
	- mise en place de l'environnement de programmation

* Saara Jones



* Noémie Carette

	- rédaction du cahier de spécification
	- création des maquettes d'interface

**TODO : responsabilités**


2. Technique
************

2.1 Dépendances
===============

* Orange 3.24.1

* Orange Textable 3.1.5


2.2 Fonctionnalités minimales
=============================


* Prendre en input un fichier tabulaire (traité avec Sniffer) et le convertir en segmentation Textable.


2.3 Fonctionnalités principales
===============================

.. image:: extractXML_auto.png


* Accès au mode automatique (par défaut) qui convertit en segmentation sans intervention de l'utilisateur.


2.4 Fonctionnalités optionnelles
================================

.. image:: extractXML_manuel.png

* Permettre le passage en mode manuel où l'utilisateur pourra personnaliser les headers:
	
	- vue de la liste des headers pré-interprétés
	- possibilité d'en changer le nom avec le bouton rename
	- possibilité de choisir lequel de ces headers deviendra le contenu de la segmentation résultante (par défaut, le premier)


2.5 Tests
=========

TODO


3. Etapes
*********

3.1 Version alpha
=================

* L'interface graphique est complètement construite.
* Les fonctionnalités minimales sont prises en charge par le logiciel et ont été testées.


3.2 Remise et présentation
==========================

* Les fonctionnalités principales sont complétement prises en charge par le logiciel.
* La documentation du logiciel est complète.
* Les fonctionnalités principales (et, le cas échéant, optionnelles) sont implémentées et ont été testées.
