
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

In its basic version, user controls are divided into two main sections: **Sources**, which holds the **URL** subsection, and **Options**.

.. _YouGet_principal:

.. figure:: figures/YouGet_principal.png
    :align: center
    :alt: Interface of the YouGet widget

    Figure 1: **YouGet** widget interface.

Sources
*******

The **Sources** section contains all the controls related to the way **YouGet**
processes the input data. 

The user chooses a YouTube video which they would like to extract its comments. Once the video chosen, they
add its URL in the empty **URL section**. To confirm their URL, they must press on the **Add** button which
will add their URL to a list in the section below "Sources". The user can add one or more URLs to their list.
If they wish to remove an URL, they can press on the **Remove** button. If they wish to not only remove one, 
but all of their URLs, they can press on the **Clear All** button.

Options
*******

The **Options** section contains the controls to choose the **number of comments** desired in output.

The user can choose between having 1 comment (minimum requirement), 100, 1000, or an illimited amount 
of comments in output.

Once the user presses on the **Send** button, the comments will then be displayed in output in the form 
of a segmentation.

Advanced Interface
~~~~~~~~~~~~~~~~~~
In its advanced version, **YouGet** offers the same functionnalities as the basic one, but adds the 
possibility of filtering YouTube comments according to their number of **likes** or by their
**date of publication**.

Messages
--------

Information
~~~~~~~~~~~

to be added

Warnings
~~~~~~~~

*Please add a YouTube URL*
   The URL section is empty, so the user has to add at least one URL before sending.

*Settings were changed, please click 'Send' when ready.*
   Settings have changed but the **Send automatically** checkbox has not been selected, 
   so the user is prompted to click the **Send** button (or equivalently check the box) 
   in order for computation and data emission to proceed.

*Step 1/2: Processing...*
   The requested analysis is being performed.

Errors
~~~~~~~~

*Please make sure that input is well-formed XML*
   The URL section must only contain URLs.

Note
~~~~~~~~

If there is a break in WIFI connection, please press cancel and start again.
