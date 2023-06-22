.. meta::
   :description: Orange3 Textable Prototypes documentation, Poetica
                 widget
   :keywords: Orange3, Textable, Prototypes, documentation, Poetica,
              widget

.. _Poetica:

Poetica
=============

.. image:: figures/poetica.png
A MODIFIER IMAGE CI-DESSUS

Make a corpus with selected poems.

Author
------

Sinem Kilic, Laure Margot, Leonie Nussbaum, Olivia Verbrugge

Signals
-------

Input: None

Outputs:

* ``Text data``

    A segmentation with the texts of the selected poems.

Description
-----------

This widget is designed to import one or more poems in Orange Canvas.
The poems are imported from the site `<https://poetica.fr/>`_. The output is a
segmentation containing a segment for each imported poem.
Each segment has different annotations with keys *Author*,
*Title*, *URL* and eventually *Topic*.

Interface
~~~~~~~~~

.. _Poetica_fig1:

.. figure:: figures/poetica_maquette.png
    :align: center
    :scale: 50 %
    :alt: Interface of the Poetica widget

    Figure 1: **Poetica** widget interface.

The **Poetica** widget allows the user to make a research on the Poetica's website (`<https://poetica.fr/>`_).

The **Select criterias** section allows the user to search poems by their author and/or topic.
He can add his favorite results to his basket.

The **Corpus** section is the user's basket. There he can remove elements from his corpus or clear it completely.

The **Send** button manages the emission of a segmentation to the output
connection(s). When selected, the **Send automatically** checkbox
disables the button and the widget attempts to automatically emit a
segmentation at every modification of its interface.

Messages
--------

Information
~~~~~~~~~~~

*You add a poem*
    Informs that one or more poems have been added.

*Select a poem*
    Informs the user if he hasn't selected any poems to add.

*Your corpus is empty, please add some poems first*
    Informs the user if he wants to send his results but that his basket is empty.

*Settings were changed, please click 'Send' when ready.*
    Informs the user that the settings where changed. He can send his basket to have his new selection as output.

*<n> segment sent to output (<m> characters).*
    Confirms that the widget has operated properly.


Warnings
~~~~~~~~


A MODIFIER CI-DESSOUS

*Settings were changed, please click 'Send' when ready.*
    Settings have changed but the **Send automatically** checkbox
    has not been selected, so the user is prompted to click the **Send**
    button (or equivalently check the box) in order for computation and data
    emission to proceed.

*You didn't search anything*
    The user want to make a search with no text in the query box.

*Your corpus is empty, please add some songs first*
    The corpus is empty, so the user have to add some songs before sending.

Errors
~~~~~~

*Couldn't download data from Genius website.*
    An error has prevented the widget to download the data from the
    Genius website (most likely related to a connection problem).