sarah's note: search for TODO for all missing and needing of correction areas

.. meta::
   :description: Orange3 Textable Prototypes documentation, SciHubator widget
   :keywords: Orange3, Textable, Prototypes, documentation, SciHubator, widget

.. _SciHubator:

SciHubator
==============

.. image:: figures/TODO.png 
 
Download pdf files from `Sci-HUB <https://www.sci-hub.se/>`_ and extract textual content into segmentations

Authors
-------
Sarah Perreti-Poix, Borgeaud Matthias, Chétioui Orsowen, Luginbühl Colin

Signals
-------

Inputs: ``None``

  None


Outputs: ``Text data``

  Segmentation covering the content of downloaded pdf files

Requirements 
------------

* Orange 3.38.1
* Orange Textable 3.2.2
* from functools import partial
* import time
* from scidownl import scihub_download
* import tempfile
* import pdfplumber
* import os
* import requests
 
Description
-----------

This widget is designed to download pdf files from the SciHub project and outputs its content
into an annotated text segmentation.


Basic interface
~~~~~~~~~~~~~~~

In its basic version (see :ref:`figure 1 <scihubator_basicinterface>` below), 
the **SciHubator** widget is limited to the import of a single DOI.
The interface contains a **Source** section enabling the user to type the DOI.

.. _SciHubator_basicinterface:

.. figure:: specs/images/scihubator_minimal.png
    :align: center
    :alt: Basic interface of the SciHubator widget

    Figure 1: **SciHubator** widget (basic interface).

Note that pdfplumber might not work properly with none latin alphabets
and serif typefaces. TODO

The **Send** button triggers the emission of a segmentation to the output
connection(s). When it is selected, the **Send automatically** checkbox
disables the button and the widget attempts to automatically emit a
segmentation at every modification of its interface.

The text below the **Send** button indicates the number TODO of characters in the single
segment contained in the output segmentation, or the reasons why no
segmentation is emitted (no input data, encoding issue, etc.).

Advanced interface TODO
~~~~~~~~~~~~~~~~~~

The advanced version of **SciHubator** allows the user to type several DOIs
in a determined order; each outputed text file can moreover be segmented into
specific segmentations (introduction, mais corpus and bibliography) with specific
annotations. The emitted segmentation contains a segment
for each imported file.

.. _scihubator_advancedinterface:

.. figure:: figures/scihubator_advancedinterface.png
    :align: center
    :alt: Advanced interface of the Super Text files widget
    :scale: 80%
    
    Figure 2: **SciHubator** widget (advanced interface).

The advanced interface (see :ref:`figure 2 <scihubator_advancedinterface>` 
above) presents similarities with that of the **URLs** and **Segment**
widgets. The **Sources** section allows the user to select the input
DOI(s). The list
of imported files appears at the top of the window; the columns of this list
indicate (a) the name of each file, (b) the corresponding annotation (if any),
and (c) the encoding with which each is associated.

The first buttons on the right of the imported files' list enable the user to
modify the order in which they appear in the output segmentation (**Move Up**
and **Move Down**), to delete a file from the list (**Remove**) or to
completely empty it (**Clear All**). Except for **Clear All**, all these
buttons require the user to previously select an entry from the list.

The **Send** button triggers the emission of a segmentation to the output
connection(s). When it is selected, the **Send automatically** checkbox
disables the button and the widget attempts to automatically emit a
segmentation at every modification of its interface.

The text below the **Send** button indicates the length of the output segmentation in
characters, or the reasons why no segmentation is emitted (no selected file,
encoding issue, etc.). In the example, the two segments corresponding to the
imported files thus total up to 1'262'145 characters.

Messages
--------

Information
~~~~~~~~~~~

*Data correctly sent to output: <n> segments (<m> characters).*
    This confirms that the widget has operated properly.

*Settings were* (or *Input has*) *changed, please click 'Send' when ready.*
    Settings and/or input have changed but the **Send automatically** checkbox
    has not been selected, so the user is prompted to click the **Send**
    button (or equivalently check the box) in order for computation and data
    emission to proceed.

*No data sent to output yet: no file selected.*
    The widget instance is not able to emit data to output because no input 
    file has been selected.

*No data sent to output yet, see 'Widget state' below.*
    A problem with the instance's parameters and/or input data prevents it
    from operating properly, and additional diagnostic information can be
    found in the **Widget state** box at the bottom of the instance's
    interface (see `Warnings`_ and `Errors`_ below).

Warnings
~~~~~~~~

*No label was provided.*
    A label must be entered in the **Output segmentation label** field in
    order for computation and data emission to proceed.

Errors
~~~~~~

    
