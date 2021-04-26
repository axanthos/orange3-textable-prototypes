
.. meta::
    :description: Orange3 Textable Prototypes documentation,  Text_Summarizer, widget, spaCy, Scikit-learn
    :keywords: Orange3, Textable, Prototypes, documentation, Text_Summarizer, widget, spaCy, Scikit-learn
    .. _Text_Summarizer:

Text Summarizer
=======
    
.. image:: figures/TL;DR.png

Summarizes a text segmentation by using Scikit-learn and Spacy to select the most important sentences of a segmentation.

    
Author
------

Jason Ola, Melinda Femminis, Catherine Pedroni

Signals
-------

Inputs:

* ``Text segmentation``

Outputs:

* ``Text segmentation``

Description
-----------

This widget is designed to summarize a text segmentation. It takes, as an input, a text segmentation, and summarizes it. 
There are two versions of the Text_Summarizer a basic and advanced version. The basic version allows the user to chose the desired language between english, french or portugese. It also allows the user to chose the size of the summary.
The advanced version adds the following options: the choice of the summary length based on a % of the input, meaning that the user can chose to have a summary 50% as long as the input. The other option will allow the user to visualise the most important words in a World Cloud.

Interface
~~~~~~~~~

The **basic** interface displays first a text field in which the user can set the number of sentences of the summary; a dropdown list of languages to chose from; finally two options to select : to summarize by text or by segments.

The **advanced** interface displays two more elements. 
First a percentage option that, when selected, lets the user choose the percentage with a gauge.
The second element is the world cloud letting the user visualize the most important words of the summary.

The **Info** section informs the user about the status of the widget and 
indicates the number of segments and characters in the output segmentation, or 
the reasons why no segmentation is emitted (no corpus selected, connection 
issues, etc.).

The **Send** button triggers the retrieval and emission of one or more 
segmentations to the output connection(s). When it is selected, the **Send 
automatically** checkbox disables the button and the widget attempts to 
automatically emit a segmentation at every modification of its interface.


Messages
--------

Information
~~~~~~~~~~~

*<n> files, <m> utterances and <l> words sent to output.*
    This confirms that the widget has operated properly.

Warnings
~~~~~~~~

Errors
~~~~~~

Note
~~~~