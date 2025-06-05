
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

Virgile Albasini, Sophie Ward, Lorelei Chevroulet, and Vincent Joris.

Signals
-------

Inputs: 

* None

Outputs:

* The comments from a YouTube video in the form of a segmentation


Description
-----------

This widget provides a graphical interface which is designed to allow the user to enter a YouTube video's URL and
download its comments (`<https://www.youtube.com>`_).
The output is a segmentation containing the **Number of Comments** desired from the chosen YouTube video.

* Choose one or more URL(s) and place them in the **URL(s)** section in the following format: URL1, URL2, URL3, etc.
* **Add** them to the **Sources** section
* Select the **Number of Comments** you would like to download from the YouTube video
* Select whether you would like them sorted by **Date** or **Popularity**
* Press **Send** to see the comments as well as some additional information in the form of a segmentation

Interface
~~~~~~~~~~~~~~~

User controls are divided into two main sections: **Sources** and **More Options**.

**Sources** contains the **URL**, and the **Add**, **Clear All** and **Remove** button.

**More Options** contains the **Select number of comments** and the **Sort by**. 
In the **Select number of comments**,  the user can select the number of comments
they wish to see displayed, and in the **Sort by**, the user can choose to either sort the comments by **Date** or by **Popularity**.

.. _YouGet_principal:

.. figure:: figures/YouGet_principal.png
    :align: center
    :alt: Interface of the YouGet widget
    :height: 600px

    Figure 1: **YouGet** widget interface.

Sources
*******

The **Sources** section contains all the controls related to the way **YouGet** processes the input data. 

The user chooses one ore more YouTube videos which they would like to extract its comments. To confirm their URL(s), they must press on the **Add** button which
will then add their URL(s) to a list in the section above called **Sources**. The user can add one or more URLs to their list.
If they wish to remove a URL, they can select the URL they wish to delelte and press on the **Remove** button. If they wish to not only remove one, 
but all of their URLs, they can press on the **Clear All** button.

More Options
*******

The **More Options** section contains the controls to select the **number of comments** desired in output and how you would like to sort the comments, by **Date** or by **Popularity**. The user can choose between having **1 comment (minimum requirement), 5, 10, 100, 1000, 10'000 or no limit** 
of comments in output. When sorting by **Date**, the oldest comment will appear first in the list. When sorting by **Popularity**, the most liked comment will appear first. Once the user presses on the **Send** button, the comments will then be displayed in output in the form 
of a segmentation.

.. figure:: figures/YouGet_5comments.png
    :align: center
    :alt: Interface of the YouGet widget with 5 comments
    :height: 600px

    Figure 2: **YouGet** widget output with **5 comments** selected and sorted by **Date**.
.. figure:: figures/YouGet_10comments.png
    :align: center
    :alt: Interface of the YouGet widget with 10 comments
    :height: 600px
    
    Figure 3: **YouGet** widget output with **10 comments** selected and sorted by **Popularity**.

Messages
--------

Information
~~~~~~~~~~~

*f"{len(processed_data)} segment@p sent to output"*
   This confirms that the widget has operated correctly and that the segments have been sent to output.

Warnings
~~~~~~~~

*Settings were changed, please click 'Send' when ready.*
   Settings have changed but the **Send automatically** checkbox has not been selected, 
   so the user is prompted to click the **Send** button (or equivalently check the box) 
   in order for computation and data emission to proceed.

*Step 1/2: Processing...*
   The requested analysis is being performed.

Errors
~~~~~~~~

*(nb) duplicate URL(s) found and deleted*
   The system finds one or multiple duplicate URL(s) and deletes them instead of adding them.

*(nb) URL(s) are not valid YouTube videos*
   The widget detects that the URL(s) are misspelt and does not add them to the list.

*One or more elements are not YouTube URLs or please check your internet connection*
   The widget detetcs that there is an error with the process. Either in terms of the URL(s) themselves or with the internet connection. If there are multiple elements added in the **URL(s)** section and one of them is not an URL, then all of these elements will not be added to the **Sources** section. If the internet connection is interrupted during the process of adding URLs to the **Sources** section or during the loading process of the comments, there will be an error message that will appear to please check your internet connection.

Note
~~~~~~~~

Note that when starting the widget and when first adding your URL(s), the **Add** button is gray, however, it is functional. Press the **Add** button to add your URL(s) to the **Sources** section.