
.. meta::
   :description: Orange3 Textable Prototypes documentation, CHILDES widget
   :keywords: Orange3, Textable, Prototypes, documentation, CHILDES, widget

.. _Theatre Classique:

CHILDES
=======

.. image:: figures/CHILDES.png

Import data in XML format from the `CHILDES
<https://childes.talkbank.org/data-xml/>`_ database.

Author
------

Aris Xanthos

Signals
-------

Inputs: None

Outputs:

* ``Files``

  Segmentation with a segment for each file in imported corpora

* ``Utterances`` (optional)

  Segmentation with a segment for each utterance in imported corpora

* ``Words`` (optional)

  Segmentation with a segment for each word in imported corpora

Description
-----------

This widget is designed to import one or more CHILDES corpora 
in Orange Canvas. The corpora are retrieved from
`<https://childes.talkbank.org/data-xml/>`_ and richly encoded in XML format. 
The widget outputs at least one segmentation containing a segment for each file 
in  each imported corpus. Segments in this segmentation have a number of 
annotations (depending on what is available for each corpus):[1]_

.. [1] The user is reffered to the `CHAT transcription format documentation
<https://talkbank.org/manuals/CHAT.html>`_ for the meaning and possible values
of the numerous annotations extracted by the widget.

=====================      =====
key                        example value
=====================      =====
*corpus*                   *Geneva*
*file_path*                *Geneva/020107.xml*
*lang*                     *fra*
*pid*                      *11312/c-00028161-1*
*target_child_id*          *CHI*
*target_child_age*         *P2Y01M07D*
*target_child_days*        *757*
*target_child_months*      *25*
*target_child_years*       *2*
=====================      =====

Optionally, the output may also include two more segmentations, into utterances
and into words. Both inherit the annotations above. The utterance segmentation
adds two extra annotations:

==========  ===============
key              example value
==========  ===============
*uID*            *u0*
*who*            *CHI*
==========  ===============

The word segmentation inherits all previous annotations, and adds a variable 
number of annotations (depending on the information available in the data), 
namely at most: 

===========   =========
key           example value
===========   =========
*head*        *1*
*index*       *0*
*pos*         *part*
*prefixes*    *dé*
*relation*    *OBJ*
*stem*        *faire*
*suffixes*    *PP&m*
===========   =========


Interface
~~~~~~~~~

User controls are divided into three main sections (see :ref:`figure 1 
<childes_fig1>` below): **Browse database**, **Selection**, and **Options**.

.. _childes_fig1:

.. figure:: figures/childes_interface.png
    :align: center
    :alt: Interface of the CHILDES widget

    Figure 1: **CHILDES** widget interface.

The **Browse database** section allows the user to navigate the XML section of
the CHILDES database (`<https://childes.talkbank.org/data-xml/>`_) and select
the desired corpora. It is organized like a file tree, starting from a root 
folder (denoted as "/"), and each folder may contain any number of subfolders
and/or zipped archives.

To view the contents of a folder, either double-click it or select it and
click **Open**. Button **Back** brings you back to the parent folder, and 
**Home** to the root folder.

**Add to selection** adds the highlighted archive(s) to your selection, and so 
does double-clicking an archive. If a folder is highlighted, clicking **Add to 
selection** results in adding *all* the archives contained in this folder and, 
recursively, in contained subfolders (so possibly a lot of archives), to your 
selection. Note that multiple archives/folders may be highlighted (using 
control/command-click or shift-click) and added at once to your selection.

When the current folder is the root folder ("/"), the **Home** button is 
replaced with **Refresh**. Clicking **Refresh** instructs the widget to connect
to the CHILDES website and update its own configuration to take into account
possible changes (usually additions) to the database. This operation may take
a few minutes and is only useful when the online database has changed; it has 
the additional consequence that it cancels previous selections.

TODO FROM HERE ON...

The **Options** section allows the user to define the label of the output
segmentation (**Output segmentation label**).

The **Info** section indicates the number of segments and characters in the
output segmentation, or the reasons why no segmentation is emitted (no title
selected, connection issues, etc.).

The **Send** button triggers the emission of a segmentation to the output
connection(s). When it is selected, the **Send automatically** checkbox
disables the button and the widget attempts to automatically emit a
segmentation at every modification of its interface.

Advanced interface
~~~~~~~~~~~~~~~~~~

The advanced version of **Theatre Classique**  (see :ref:`figure 2
<theatre_classique_fig2>` below)offers the same functionality as
the basic one, and it adds the possibility of selecting only the plays of a
given author/genre/title.

.. _theatre_classique_fig2:

.. figure:: figures/theatre_classique_advanced_interface.png
    :align: center
    :alt: Advanced interface of the Theatre Classique widget

    Figure 2: **Theatre Classique** widget (advanced interface).

The **Options** and **Info** sections, as well as the **Send** button and
**Send automatically**, operate in the same way as in the basic interface.

Messages
--------

Information
~~~~~~~~~~~

*<n> segments sent to output (<m> characters).*
    This confirms that the widget has operated properly.


Warnings
~~~~~~~~

*Settings were changed, please click 'Send' when ready.*
    Settings have changed but the **Send automatically** checkbox
    has not been selected, so the user is prompted to click the **Send**
    button (or equivalently check the box) in order for computation and data
    emission to proceed.

*Please select one or more titles.*
    The widget instance is not able to emit data to output because no theatre
    play has been selected.


Errors
~~~~~~

*Couldn't download data from theatre-classique website.*
    An error has prevented the widget to download the data from the
    theatre-classique (most likely related to a connection problem).
