.. meta::
   :description: Orange3 Textable Prototypes documentation, TextTree 
                 widget
   :keywords: Orange3, Textable, Prototypes, documentation, TextTree,
              widget

.. _Text Tree:

Text Tree
=================

.. image:: figures/textTree.png

Allow to import a complete tree of text files (.txt, .xml, .csv, .html, .rtf by default)

Author
------

Mathieu Mercapide,
Augustin Maillefer
& Olivier Cavaleri

Signals
-------

Inputs: None

Outputs:

* ``Text data``

  Segmentation covering the content of files filtered in a tree of files

Description
-----------

This widget is designed to import one, some or all the files contained in a selected folder.
The output is a segmentation containing a segment for each imported file. 
Each segment has annotations with keys : folder name (depth_0), depth level (depth_1, depth_2, ...), file depth level, file encoding and confidence, file name and file path 
  
The interface of **Text Tree** is available in two versions, according 
to whether or not the **Advanced Settings** checkbox is selected.

Basic interface
~~~~~~~~~~~~~~~

In its basic version (see :ref:`figure 1 <text_tree_fig1>` below), the 
**Text Tree** widget lets the user browse at once all the files contained
in the selected folder.

.. _text_tree_fig1:

.. figure:: figures/TextTree_Basic.png
    :align: center
    :alt: Basic interface of the Text Tree widget

    Figure 1: **Text Tree** widget (basic interface).

The **Options** section allows the user to browse on his computer to find
desired folder (**Output segmentation label**). 
Default filter : the files with extensions .txt, .html, .xml, .csv, .rtf will be opened.

The **Info** section indicates the number of segments (files) in the 
output segmentation, or the reasons why no segmentation is emitted (no title 
selected).

The **Send** button triggers the emission of a segmentation to the output
connection(s). When it is selected, the **Send automatically** checkbox
disables the button and the widget attempts to automatically emit a
segmentation at every modification of its interface.

Advanced interface
~~~~~~~~~~~~~~~~~~

The advanced version of **Text Tree**  (see :ref:`figure 2 
<text_tree_fig2>` below) offers the same functionality as
the basic one, and it adds the possibility of filtering (include or exclude files by filenames) 
and execute a sampling (0 - 100 %).

.. _text_tree_fig2:

.. figure:: figures/text_tree_advanced_interface.PNG
    :align: center
    :alt: Advanced interface of the Text Tree widget
    
    Figure 2: **Text Tree** widget (advanced interface).

The **Options** section allows the user to browse on his computer to find the desired folders (the samme way as in the basic interface), but with the options to include or excludes types or names of files and to input a level of sampling in %. With the **Add button** the selection will be added to the list.
Exclusion : exclusion in the files list from the basic browse (default filter). Each exclusion should be separated by a comma.
Inclusion : inclusion of a new files filter (default filter replaced). Each inclusion should be separeted by a comma.
The encoding's annotation of a file with encoding's error will simply be omitted.
Sampling : the sampling operation selects the input proportion (rounded-up number) of files randomly. Ex : 50% of 9 files will select 5 random files from the file list.

The **Info** section, as well as the **Send** button and 
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

*Please select one (or more) folders.*
    The widget instance is not able to emit data to output because no folder
    has been selected.

    
Errors
~~~~~~

*No added errors*

