Movie Transcripts
=================

.. image:: figures/Movie_Transcripts.png

Make a corpus of movie transcripts

Authors
-------
Leonardo Cavaliere, David Flühmann, Kirill Melnikov


Signals
-------
Input: None

Outputs:

* ``Text data``

    A segmentation with the transcripts of the selected movies.

Description
-----------

This widget is designed to import one or more movie transcripts in Orange Canvas.
The transcripts are retrieved from `<https://www.springfieldspringfield.co.uk/>`_. The output is a
segmentation containing a segment for each imported movie.

Interface
~~~~~~~~~

.. image:: figures/movie_transcripts_search.png

Figure 1: **Movie transcripts** widget interface

The **Movie transcripts** widget simply lets the user make a search on the `SpringfieldSpringfield <https://www.springfieldspringfield.co.uk/>`_ website.

The **Search** button searches the database for entries matching user's input.

The **Refresh database** button downloads the newest collection of all the movie titles available on the website and stores them in cache. 

The **Corpus** section is a container where the user's transcripts are stored. The user can add or remove transcripts to and from their corpus or clear the corpus entirely.

The **Send** button triggers the emission of a segmentation to the output connection(s). When selected, the Send automatically checkbox disables the button and the widget attempts to automatically emit a segmentation at every modification of its interface.

Messages
--------

Information
~~~~~~~~~~~

*<n> segments sent to output (<m> characters).*
    This confirms that the widget has operated properly.

*Database successfully updated*
    This confirms that the Refresh button worked properly.


Warnings
~~~~~~~~

*Settings were changed, please click 'Send' when ready.*
    Settings have changed but the **Send automatically** checkbox
    has not been selected, so the user is prompted to click the **Send**
    button (or equivalently check the box) in order for computation and data
    emission to proceed.

*Please, enter a query in the search bar*
    The user attempted to make a search with no text in the query box.

*Your corpus is empty, please add some movies first*
    The corpus is empty, no movies have been selected for downloading.

Errors
~~~~~~

*Couldn't download data from SpringfieldSpringfield website.*
    An error has prevented the widget from downloading the data from the
    SpringfieldSpringfield website (most likely related to a connection problem).

*Couldn't save database on disk*
    An error has prevented the widget from saving the downloaded database on
    the user's hard drive.

