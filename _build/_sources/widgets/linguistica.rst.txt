.. meta::
   :description: Orange3 Textable Prototypes documentation, Linguistica 
                 widget
   :keywords: Orange3, Textable, Prototypes, documentation, Linguistica,
              widget

.. _Linguistica:

Linguistica
===========

.. image:: figures/linguistica.png

Unsupervised morphological analysis.

Author
------

Aris Xanthos

Signals
-------

Input:

* ``Word segmentation``

    A Textable segmentation containing words

Outputs:

* ``Morphologically analyzed data``

    A Textable segmentation containing the same words annotated with the discovered morphological structure (stem, suffix, and signature)

Description
-----------

This widget takes a word segmentation as input and applies part of John
Goldsmith's "Crab Nebula" algorithm to it. The algorithm seeks to discover 
morphological structure in an unsupervised fashion, i.e. without using 
language-dependent linguistic resources. 

In particular, the widget tries to divide each word into stem and a suffix, 
in a way that the resulting components can be regularly combined with other 
stems and suffixes (thus forming a structure known as a "signature"). 

Interface
~~~~~~~~~

The widget's interface displays a single control (see 
:ref:`figure 1 <linguistica_fig1>` below): the user can set the minimum
length allowed for a stem (4 characters is the default value).

.. _linguistica_fig1:

.. figure:: figures/linguistica_interface_words.png
    :align: center
    :alt: Interface of the Linguistica widget (Words)

    Figure 1: **Linguistica** widget interface (**Words** tab).

The right hand side of the interface contains two tabs that can be used to
explore the discovered morphology. The **Words** tab displays the list of
input words ordered by decreasing frequency. When a word is selected in this
list, the possible parses are displayed in the **Parse(s)** section, along
with a probability estimate (NB: at this point the estimation is excessively 
biased toward parses involving the "NULL" suffix, i.e. the empty string). 
When a parse is selected, the stems and suffixes that belong to the 
corresponding signature are displayed in the **Stem(s)** and **Suffixe(s)** 
lists. The signature's identifier (an integer) is also indicated. 

.. _linguistica_fig2:

.. figure:: figures/linguistica_interface_signatures.png
    :align: center
    :alt: Interface of the Linguistica widget (Signatures)

    Figure 2: **Linguistica** widget interface (**Signatures** tab).

The **Signatures** tab displays the list of discovered signatures, along
with their identifier. When a signature is selected, the corresponding words, 
stems and suffixes are displayed in the other lists.

The **Info** section indicates that the input has been correctly processed, or 
the reason why no output is emitted (no input, etc.). It also indicates the 
proportion of tokens that have been assigned to a signature (with the exception
of the signature #0, which always contains all the stems that have only been
found to occur with the NULL suffix).

The **Send** button triggers the computation and emission of the annotated
word segmentation. When it is selected, the checkbox to the left of the button
disables the button and the widget attempts to automatically emit results at every modification of its interface.

Messages
--------

Information
~~~~~~~~~~~

*<n> segments sent to output (<p>% analyzed).*
    This confirms that the widget has operated properly.


Warnings
~~~~~~~~

*Unable to find any stems in data.*
    The morphology learning algorithm has not been able to discover any 
    relevant structure.

*Unable to find any stems in data. Please check that they are segmented into words.*
    The morphology learning algorithm has not been able to discover any 
    relevant structure, and a likely explanation is that the input has 
    not been segmented before being transmitted to this widget. If so, 
    please segment it into words (for example using Textable's **Segment**
    widget).

*Settings were changed, please click 'Send' when ready.*
    Settings have changed but the **Send automatically** checkbox
    has not been selected, so the user is prompted to click the **Send**
    button (or equivalently check the box) in order for computation and data
    emission to proceed.

*Widget needs input*
    A Textable segmentation containing words should be input
    in the widget.

    
