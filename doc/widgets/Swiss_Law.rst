.. meta::
   :description: Orange3 Textable Prototypes documentation, Swiss Law
                 widget
   :keywords: Orange3, Textable, Prototypes, documentation, Swiss, Law,
              widget

######################################
Documentation Swiss Law widget
######################################

.. image:: figures/SwissLaw.png
    :align: center
    :scale: 20 %
    :alt: Swiss Law Icon

Make a corpus with Swiss law documents.

1 Introduction
**************

1.1 Author
===========

Antoine Vigand, Elijah Green, Samantha Allendes et Thomas Rywalski

1.2 Signals
=============

Input: None

Outputs:

* ``Text data``

    The selected Swiss law documents with the requested segmentation.

1.3 Description
================

Create a widget for Orange Textable (v3.7) to import the main Swiss legal texts from
XML file from the site `fedlex.admin.ch <https://www.fedlex.admin.ch/fr/home?news_period=last_day&news_pageNb=1&news_order=
desc&news_itemsPerPage=10>`_. SwissLaw is a widget included in Orange3-Textable-Prototypes, a tool developed with
Orange 3 software using the Python language.

1.4 Interface
==============

.. figure:: figures/SwissLaw3.png
    :align: center
    :scale: 50 %
    :alt: Interface of the Swiss Law widget

    Figure 1: **Swiss Law** widget interface.

2. Technique
************

2.1 Installation
=================
To use the SwissLaw widget, you need to have Orange 3 and Orange3-Textable-Prototypes installed.
Follow the instructions below to install the widget:

1. Install Orange 3: `Orange 3 Installation Guide <https://orangedatamining.com/download/#macos>`_
2. Install Textable Prototypes: `Textable Prototypes installation guide <https://pypi.org/project/Orange3-Textable-Prototypes/>`_

2.2 Using Widget
=================
1. Launch Orange 3 and go to the "Textable Prototypes" section.
2. Drag and drop the "Swiss Law" widget onto the work area.
3. Configure the widget by selecting the desired options.
    3a. Select the desired legal document. The **Select Law Document** section allows the user to choose a law document, a segmentation and a language.
		.. image:: images/SwissLaw1.png

	3b. Click on "Add to corpus" to add the item to the corpus, the **Corpus** section allows the user to clear or remove selected document from
the corpus.
		.. image:: images/SwissLaw2.png

	3c. Click on "send" to send the segmentation. The **Send** button triggers the emission of a segmentation to the output
    connection(s). When selected, the **Send automatically** checkbox
    disables the button and the widget attempts to automatically emit a
    segmentation at every modification of its interface.
		.. image:: images/SwissLaw3.png

4. Connect the SwissLaw widget to other widgets or components in your workflow.
5. Run the workflow to access and analyse SwissLaw documents.

2.3 Messages
=============

2.3.1 Information
~~~~~~~~~~~

*<n> segments sent to output (<m> characters).*
    This confirms that the widget has operated properly.


2.3.2 Warnings
~~~~~~~~

*Settings were changed, please click 'Send' when ready.*
    Settings have changed but the **Send automatically** checkbox
    has not been selected, so the user is prompted to click the **Send**
    button (or equivalently check the box) in order for computation and data
    emission to proceed.

*Your corpus is empty, please add some law texts first.*
    The corpus is empty, so the user have to add some law documents before sending.
