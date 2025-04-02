
.. meta::
   :description: Orange3 Textable Prototypes documentation, YouGet widget
   :keywords: Orange3, Textable, Prototypes, documentation, YouGet, widget

.. _YouGet:

YouGet
=======

.. image:: figures/YouGet.svg

Import YouTube video comments (`<https://www.youtube.com>`_).

Author
------

Virgile Albasini, Sophie Ward, Lorelei Chevroulet, et Vincent Joris

Signals
-------

Inputs: 

* Enter a YouTube video's URL to download comments
* Import a URL list
* Choose the amount of comments you would like to download (minimum 1 comment, then 100, then 1000, or no limit)

Outputs:

* The comments from a YouTube video in the form of a segmentation

Optional 

* Have the comments in output ordered by likes or by their date


Description
-----------

This widget provides a graphical interface which permits the user to enter an YouTube video's URL and
download its comments (`<https://www.youtube.com>`_).
The output is a segmentation containing the comments of the chosen YouTube video. 

* Choose an URL
* Choose the number of comments you would like to download
* See the comments in the form of a segmentation

**YouGet**'s interface is available in two versions, depending on whether or not the Advanced Settings is
selected.

Basic Interface
~~~~~~~~~~~~~~~

User controls are divided into two sections: **Sources** and **Options**.

.. _YouGet_principal:

.. figure:: figures/YouGet_principal.png
    :align: center
    :alt: Interface of the YouGet widget

    Figure 1: **YouGet** widget interface.

Sources
*******

The **Sources** section contains all the controls related to the way YouGet
processes the input data. 

The user adds the YouTube video's URL of their choice in the **URL**'s section and presses
on the **add** button to add their URL to the list. The user can add one or more URLs to their list which will then appear
in the empty section above. If they wish to remove an URL, they can press on the **Remove** 
button. If they wish to not only remove one, but all of their URLs, they can press on the 
**Clear All** button.

Options
*******

The **Options** section contains the controls to choose how many comments is desired in output.

The user can choose the **number of comments** they would like have in output. They can choose between 
having 1 comment (minimum requirement), 100, 100, or an illimited amount of comments in output.

Once the user presses on the **Send** button, the comments will then be displayed in output in the form 
of a segmentation.


Messages
--------

Information
~~~~~~~~~~~

*<n> tokens, <m> noun chunks, <l> entities and <k> sentences sent to output.*
    This confirms that the widget has operated properly.

Warnings
~~~~~~~~

*Settings were changed, please click 'Send' when ready.*
    Settings have changed but the **Send automatically** checkbox
    has not been selected, so the user is prompted to click the **Send**
    button (or equivalently check the box) in order for computation and data
    emission to proceed.

*Widget needs input.*
    The widget instance needs data to be sent to its input channel in order
    to process it.

*Please download a language model first.*
    At least one language model needs to be installed before the widget can
    operate.

*Loading language model, please wait...*
    A language model is currently being downloaded and installed.

*Processing, please wait...*
    The requested NLP analysis is being performed.

*Input exceeds max number of characters set by user.*
    The number of characters in the widget's input is larger than the maximum
    number of characters allowed based user-defined settings; either decrease
