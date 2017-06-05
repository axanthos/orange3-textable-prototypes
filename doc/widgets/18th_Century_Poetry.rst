.. meta::
   :description: Orange3 Textable Prototypes documentation, 18th Century
                 Poetry widget
   :keywords: Orange3, Textable, Prototypes, documentation, 18th Century,
              Poetry widget

.. _18th Century Poetry:

18th Century Poetry
===================

.. image:: logo.png

Import poems from the `Eighteenth Century Poetry
<http://eighteenthcenturypoetry.org/>`_ website (in TEI-XML).

Author
------

Adriano Matos Barbosa & Frank Pham

Signals
-------

Inputs: None

Outputs:

* ``Text data``

  Segmentation covering the content of imported TEI-XML-encoded poems

Description
-----------

This widget is designed to import one or more poems in Orange Canvas. The
poems are retrieved from `<http://eighteenthcenturypoetry.org/>`_ and
abundantly encoded in TEI-XML format. The output is a segmentation containing
a segment for each imported poem. Each segment has 5 annotations with keys
*author*, *title*, *genre*, and *url*.

The Interface of **18th Century Poetry** is available in two versions,
according to whether or not the **Advanced Settings** checkbox is
selected.


Basic interface
~~~~~~~~~~~~~~~

In its basic version (see :ref:`figure 1 <18thCenturyPoetry_fig1>` below),
the **18th Century Poetry** widget simply lets the user select one or more
poems in the catalogue of a large number of entries downloadable from the
`18th Century Poetry <http://eighteenthcenturypoetry.org/>`_ website. To
select multiple files use either control/command-click or shift-click.

.. _18thCenturyPoetry_fig1:

.. figure:: figures/18thCenturyPoetry_Basic.png
    :align: center
    :alt: Basic interface of the 18th Century Poetryy widget

    Figure 1: **18th Century Poetry** widget (basic interface).

The  **Refresh** button allows the user to refresh the list of poems in
case the `18th Century Poetry <http://eighteenthcenturypoetry.org/>`_
database has been updated.

The **Send** button triggers the emission of a segmentation to the output
connection(s). When it is selected, the **Send automatically** checkbox
disables the button and the widget attempts to automatically emit a
segmentation at every modification of its interface.


Advanced interface
~~~~~~~~~~~~~~~~~~

The advanced version of **18th Century Poetry**  (see :ref:`figure 2
<18thCenturyPoetry_fig2>` below)offers the same functionality as
the basic one, and it adds the possibility of filtering the poems
according to the authors and the genres.

.. _18thCenturyPoetry_fig2:

.. figure:: figures/18thCenturyPoetry_Advanced.png
    :align: center
    :alt: Advanced interface of the 18th Century Poetry widget

    Figure 2: **18th Century Poetry** widget (advanced interface).

The **Criterion** drop down menu allows the user to select the filters
such as the authors or the genres.

The **Value** drop down menu allows the user to select the values
according to the first selected filter.


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
    The widget instance is not able to emit data to output because no poem
    has been selected.


Errors
~~~~~~

*Couldn't download data from 18th Century Poetry website.*
    An error has prevented the widget to download the data from the
    18th Century Poetry (most likely related to a connection problem).
