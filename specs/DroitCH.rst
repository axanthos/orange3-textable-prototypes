#################################
Specification Widget Addic7ed
#################################

1 Introduction
**************

1.1 But du projet
=================
Le but du projet est de créer un widget dans Orange Textable capable de récupérer des textes du droit Suisse disponible sur le site https://www.fedlex.admin.ch/


1.2 Etapes du projet
====================
* Première version des spécifications: 23 mars 2023
* Remise des spécifications: 30 mars 2023
* Version alpha du projet: 27 avril 2023
* Version finale du projet: 1 juin 2023

1.3 Equipe et responsabilités
=============================
* Samantha Allendes (samantha.allendesbravo@unil.ch)
 - specification
 - documentation
 - interface
 - code 
 - tests 
 - Github
* Elijah Green (elijah.green@unil.ch)
 - specification
 - documentation
 - interface
 - code 
 - tests 
 - Github
* Thomas Rywalski (thomas.rywalski@unil.ch)
 - specification
 - documentation
 - interface
 - code 
 - tests 
 - Github
* Antoine Vigand (antoine.vigand@unil.ch)
 - specification
 - documentation
 - interface
 - code 
 - tests 
 - Github
 
2 Technique 
***********
 
2.1 Dépendances
===============
- Orange 3.24
- Orange Textable 3.1.8
- https://www.fedlex.admin.ch/ 29.03.2023
  
2.2 Fonctionnalités minimales
=============================
- Permettre à l'utilisateur de récupérer un texte de loi Suisse parmi deux documents:
	-le code des obligations
	-le code civil
- Pouvoir faire une segmentation du document par titre ou Chapitre du texte légal
- Ajouter les résultats de la recherche au corpus


.. image:: images/DroitCHVM1.png
  
2.3 Fonctionnalités principales
===============================
- Permettre à l'utilisateur de récupérer un texte de loi Suisse parmi une liste des 20 documents de loi les plus consultés
- Permettre à l'utilisateur de séléctionner la langue nationale dans laquelle il souhaite récupérer le texte de loi:
	-Allemand
	-Français
	-Italien
- Pouvoir faire une segmentation du document par Titre, Chapitre ou article du texte légal
- Pouvoir ajouter ou supprimer des éléments du corpus
- Avoir la possibilité d'envoyer automatiquement le corpus à l'output


 .. image:: images/DroitCHVP1.png


 .. image:: images/DroitCHVP2.png



2.4 Fonctionnalités optionnels
==========================
- Permettre à l'utilisateur de récupérer n'importe quel texte de loi disponible sur le site https://www.fedlex.admin.ch/


 .. image:: images/DroitCHVOp.png



2.5 Tests
=========
TODO
  

3. Etapes
*********
  
3.1 Version Alpha
=================
* L'interface graphique est complètement construite.
* Les fonctionnalités minimales sont prises en charge par le logiciel.

3.2 Remise et présentation
===============
* Les fonctionnalités principales sont complétement prises en charge par le logiciel.
* La documentation du logiciel est complète.
* Le logiciel possède des routines de test de ses fonctionnalités (principales ou optionnelles).
  
4 Infrastructures
*****************
Le projet est disponible sur GitHub à l'adresse <https://github.com/axanthos/TextablePrototypes.git>
