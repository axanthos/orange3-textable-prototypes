##############################
Specification widget Redditor
##############################

1 Introduction
**************

1.1 But du projet
=================
Créer un widget pour Orange Textable (v3.1.0) créant une interface visuelle pour télécharger et transformer des données textuelles de Reddit.

1.2 Aperçu des etapes
=====================
* Premiere version de la specification: 21 mars 2019
* Remise de la specification: 28 mars 2019
* Version alpha du projet:  2 mai 2019
* Remise et presentation du projet:  30 mai 2019

1.3 Equipe et responsabilitées
==============================

* Olivia Edelman (olivia.edelman@unil.ch):
    - Specification
    - Code
    - Documentation
    - Verification orthographe

.. _olivia.edelman@unil.ch: mailto:olivia.edelman@unil.ch


* Nahuel Degonda (nahuel.degonda@unil.ch):
    - Specification
    - Maquettes
    - Code
    - Verification orthographe

.. _nahuel.degonda@unil.ch: mailto:nahuel.degonda@unil.ch


* Loris Rimaz (loris.rimaz@unil.ch):
    - Specification
    - Maquettes
    - Code
    - Debuggage

.. _loris.rimaz@unil.ch: mailto:loris.rimaz@unil.ch

2. Technique
************

2.1 Dépendances
===============
* Orange 3.18
* Orange Textable 3.1.0
* Praw 6.0.0

2.2 Fonctionnalités minimales
=============================
.. image:: https://zupimages.net/up/19/12/510f.png

* Permettre de chercher des posts selon deux méthodes:
    - La recherche par subreddit (filtre par défaut: hot, on retourne le premier post trouvé)
    - La recherche par lien
* Permettre de récupérer le titre et le contenu du post ainsi que tous ses commentaires
* Créer et émettre une segmentation contenant un segment pour le post ainsi qu'un segment par commentaires
* Traitement correct des exceptions

2.3 Fonctionnalités principales
===============================
.. image:: https://zupimages.net/up/19/12/u9et.png

* Permettre de récupérer plusieurs posts avec la recherche par subreddit (et ainsi créer un annotation sur chaque post)
* Permettre de changer le filtre des posts sur les subreddits (new, hot, controversial, rising et top)

2.4 Fonctionnalités optionnelles
================================
* Permettre de rechercher plusieurs posts avec une liste de liens
* Permettre de retourner une liste de posts avec la recherche par subreddit
* Permettre de filter les commentaires (par upvotes, etc)


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

4. Infrastructure
=================
Le projet est disponible sur GitHub à l'adresse `https://github.com/DigitalDW/orange3-textable-prototypes
<https://github.com/DigitalDW/orange3-textable-prototypes>`_
