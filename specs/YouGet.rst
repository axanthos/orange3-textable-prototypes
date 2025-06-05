﻿#################################
Spécification widget YouGet
#################################

1 Introduction
**************

1.1 But du projet
=================
Créer un widget pour Orange Textable permettant de télécharger les commentaires d'une vidéo à partir d'une URL YouTube.

1.2 Aperçu des étapes
=====================
* Première version de la spécification: 13.03.2025
* Remise de la spécification: 20.03.2025
* Version alpha du projet: 17.04.2025
* Remise et présentation du projet:  22.05.2025

1.3 Équipe et responsabilitées
==============================
* Mainteneur :
    - Aris Xanthos (aris.xanthos@unil.ch)

* Virgile Albasini (`virgile.albasini@unil.ch`_):

.. _virgile.albasini@unil.ch: mailto:virgile.albasini@unil.ch
    	
	- Spécification
	- Code
	- Documentation
	- Maquettes

* Sophie Ward (`sophie.ward@unil.ch`_):

.. _sophie.ward@unil.ch: mailto:sophie.ward@unil.ch
	
	- Spécification
	- Code
	- Documentation
	- GitHub

* Lorelei Chevroulet(`lorelei.chevroulet@unil.ch`_):

.. _lorelei.chevroulet@unil.ch: mailto:lorelei.chevroulet@unil.ch

	- Spécification
   	- Code
	- Maquettes
	- Vérification orthographique
	
* Vincent Joris (`vincent.joris@unil.ch`_):

.. _vincent.joris@unil.ch: mailto:vincent.joris@unil.ch

	- Spécification
	- Code
	- Interface
	- Tests

2. Technique
************

2.1 Dépendances
===============

* Orange 3.38.1 ou supérieur.

* Orange Textable 3.2.2 ou supérieur.

2.2 Fonctionnalités minimales
=============================

* Input : pas d'input.

* Entrer une URL d'une vidéo YouTube pour télécharger les commentaires.
* Output : les commentaires sont sous forme de segmentation.

.. image:: images/youget_minimal.png

2.3 Fonctionnalités principales
===============================

* Fonctionnalités minimales
* Pouvoir importer une liste d'url
* Choisir le nombre de commentaires en output (minimum 1 commentaire, puis 100, puis 1000, ou un nombre de commentaires illimité).


.. image:: images/youget_principal.png

2.4 Fonctionnalités optionnelles
================================

* Avoir en output les commentaires triés par likes ou par leur date.

2.5 Tests
=========

* Vérifier que les commentaires soient exportés.

3. Etapes
*********

3.1 Version alpha
=================
* L'interface graphique est complétement construite.
* Le téléchargement des commentaires des vidéos YouTube sont fonctionnels.

3.2 Remise et présentation
==========================
* La documentation du logiciel est complète.
* Les fonctionnalités principales sont complétement prises en charge par le logiciel.


4. Infrastructure
=================
Le projet est disponible sur GitHub à l'adresse `https://github.com/axanthos/TextablePrototypes.git
<https://github.com/axanthos/orange3-textable-prototypes>`_
