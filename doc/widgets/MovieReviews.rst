Movie Reviews
=================

.. image:: figures/moviereviews.png

Retrieving the IMDB movie reviews 

Authors
-------
Caroline Roxana Rohrbach, Maryam Zoee, Victor Vermot-Petit-Outhenin


Signals
-------
Input: None

Outputs:

* ``Text data``

    A segmentation with the reviews of the selected movies.

Description
-----------

This widget is designed for searching any movie by its title or actors and the output is 25 reviews of the film. 
The widget will use the imdbpy library to import the movies’ data.


Interface
~~~~~~~~~

.. figure:: figures/Movie_Reviews_interface.png
    :align: center
    :scale: 50 %
    :alt: Interface of the MovieReviews widget

Figure 1: **Movie Reviews** widget interface - search by Title

The **Movie Reviews** widget lets the user make a search on the IMDB library.

The **Search** button searches the database for entries matching user's input.

The **Corpus** section is a container where the user's movie selections are stored. The user can add or remove the movies to and from their corpus or clear the corpus entirely.

The **Send** button triggers the emission of a segmentation to the output connection(s). When selected, the Send automatically checkbox disables the button and the widget attempts to automatically emit a segmentation at every modification of its interface.


Messages
--------

Information
~~~~~~~~~~~

*<n> segments sent to output (<m> characters).*
    This confirms that the widget has operated properly.


Warnings
~~~~~~~~


*Please enter a movie title*
    The user attempted to make a search with no text in the query box.

*Cannot add to corpus. One or more selected movies have no associated reviews*
    The movies with no reviews will not be added to the corpus.
    
*Your corpus is empty, please add some movies first*
    The corpus is empty, no movies have been selected for downloading the reviews.

*Please enter a valid actor or actress name
    The entered word is not an actor/actress name as found on the imdb website

Errors
~~~~~~

*Couldn't download data from imdb*
    An error has prevented the widget from downloading the data from the imdb website (probably because of a connection problem).



