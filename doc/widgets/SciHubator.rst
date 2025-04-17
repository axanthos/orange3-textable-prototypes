sarah's note: searh for TODO for all missing and needing of correction areas

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

Requirements ???? TODO
-------------------------

from functools import partial
import time
from scidownl import scihub_download
import tempfile
import pdfplumber
import os
import requests


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

.. figure:: figures/scihubator_basicinterface.png
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

The advanced version of **SciHubator** allows the user to import several DOIs
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
buttons require the user to previously select an entry from the list. **Import
List** enables the user to import a file list in JSON format (see sections
*JSON im-/export format* and *File list* in Textable documentation) and to add 
it to the previously selected sources. In the opposite **Export List** enables 
the user to export the source list in a JSON
file.

The remainder of the **Sources** section allows the user to add new files to
the list. The easiest way to do so is to first click on the **Browse** button,
which opens a file selection dialog. After having selected one or more files
in this dialog  and validated the choice by clicking on **Open**, the files
appear in the **File paths** field and can be added to the list by clicking on
the **Add** button. It is also possible to type the complete paths of the
files directly in the text field, separating the paths corresponding to the
successive files with the string " \ " (space + slash + space).

Before adding one or more files to the list by clicking on **Add**, it is
possible to select their encoding (**Encoding**), and to assign an annotation
by specifying its key in the **Annotation key** field and the corresponding
value in the **Annotation value** field. These three parameters (encoding,
key, value) will be applied to each file appearing in the **File paths** field
at the moment of their addition to the list with **Add**.

The **PDF Password** field allows password-protected files to be passed to the widget. Insert the password in the field and proceed as usual.

The **OCR Language(s)** field is needed by the OCR processes. By default,
it contains English abbreviated by `eng`. Multilingual files are supported
by complete the field with the languages separated by `+`. For example,
`eng+fra+ita`. See all `installable Tesseract data files
<https://tesseract-ocr.github.io/tessdoc/Data-Files.html>`_. If nothing is
indicated in this field, the language is assumed to be `eng`.

**Force OCR** enables the OCR processes of the widget while also extracting textual content. Enable this if textual and image content are both present in the file (or if extraction of
textual content gives really bad results).

The **Options** section allows the user to specify the label affected to the
output segmentation. The **Import filenames with key** checkbox enables the
program to create for each imported file an
annotation whose value is the file name (as displayed in the list) and whose
key is specified by the user in the text field on the right of the checkbox.
Similarly the button **Auto-number with key** enables the program to
automatically number the imported files and to associate the number to the
annotation key specified in the text field on the right.


The **Send** button triggers the emission of a segmentation to the output
connection(s). When it is selected, the **Send automatically** checkbox
disables the button and the widget attempts to automatically emit a
segmentation at every modification of its interface.

The text below the **Send** button indicates the length of the output segmentation in
characters, or the reasons why no segmentation is emitted (no selected file,
encoding issue, etc.). In the example, the two segments corresponding to the
imported files thus total up to 1'262'145 characters.

.. _text_files_remote_control_ref:

Remote control
~~~~~~~~~~~~~~

**Super Text Files** is one the widgets that can be controlled by means of the
**Message** widget. Indeed, it can receive in input a message consisting
of a file list in JSON format (see sections *JSON im-/export format* and 
*File list* in Textable documentation), in which case the list
of files specified in this message replaces previously imported sources (if
any). Note that removing the incoming connection from the **Message** instance
will not, by itself, remove the list of files imported in this way from the
**Super Text Files** instance's interface; conversely, this list of files can be
modified using buttons **Move up/down**, **Remove**, etc. even if the incoming
connection from the **Message** instance has not been removed. Finally, note
that if a **Super Text Files** instance has the basic version of its interface
activated when an incoming connection is created from an instance of
**Message**, it automatically switches to the advanced interface.

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
    
*No annotation key was provided for auto-numbering.*
    The **Auto-number with key** checkbox has been selected and an annotation
    key must be specified in the text field on the right in order for
    computation and data emission to proceed.
    
*JSON message on input connection doesn't have the right keys and/or values.*
    The widget instance has received a JSON message on its ``Message`` input
    channel and the keys and/or values specified in this message do not match
    those that are expected for this particular widget type (see sections
    *JSON im-/export format* and *File list* in Textable documentation).

*JSON parsing error.*
    The widget instance has received data on its ``Message`` input channel and
    the data couldn't be correctly parsed. Please use a JSON validator to 
    check the data's well-formedness.

Errors
~~~~~~

*Couldn't open file* or *Couldn't open file '<filepath>'.*
    A file couldn't be opened and read, typically because the specified path
    is wrong.

*Encoding error* or *Encoding error: file '<filepath>'.*
    A file couldn't be read with the specified encoding (it must be in another
    encoding).

*Please make sure all Tesseract parameter files for language(s) '<languages>' have been installed..*
    One or more Tesseract language packages are probably missing.
    
*Tesseract is not installed or it's not in your path.*
    Add the directory where the tesseract-OCR binaries are located to the Environment Path variables, probably ``C:\Program Files\Tesseract-OCR``
    
