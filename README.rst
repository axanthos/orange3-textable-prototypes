Orange3 Textable Prototypes - Poetica
===========================

README Widget Poetica by LOLS

The Poetica widget searches for poems on the Poetica.fr website using author names or themes, allowing Orange users to analyze poems.

The documentation is available `here <http://orange3-textable-prototypes.readthedocs.io/>`_

Features
-------
- The widget window consists of two parts: "Criteria Selection" and "Corpus".
- The "Criteria Selection" part allows you to enter information about the poems you want to analyze.
- In this part, there are two subsections that allow you to search by author name and/or theme.

- By clicking on the "Author" tab, you can choose an author from the dropdown list.
- Once you have chosen an author and clicked "Search," all poems written by that author will appear in the first box.
- You can perform the same procedure to choose poems based on their theme. In this case, you can select a theme from the list and display the corresponding poems.
- You also have the option to choose both an author and a theme. The Poetica widget will display poems by that author in the selected theme.
- After performing your search, you can select the displayed poems in the first box by clicking the "Add to Corpus" button.
- This feature allows you to add the selected poems to the corpus displayed in the second part of the window.
- From there, you can click "Send" to send the poems to another widget for further analysis.
- You can clear the displayed poems in the results by clicking the "Clear Results" button and remove the poems added to the corpus by clicking the "Clear Corpus" button.
- The "Refresh Database" button updates the widget's cache, which may take some time.

Interoperability
------
- Import data from the Poetica.fr website.
- Process imported XML-formatted texts from the website.
- Easy interface with the --Text Mining extension in Orange--?

Code Execution
-----
Poetica.py:

- The code imports necessary packages from the Orange library and other packages such as PyQt5.QtWidgets, urllib.request, inspect, re, pickle, and os.
- The class called "Poetica" is a subclass of the OWTextableBaseWidget class from the Orange library. This class represents the Poetica widget.
- Certain properties and methods handle the widget's functionality:
- Properties such as name, description, icon, priority, inputs, and outputs define the widget's metadata.
- The __init__() method initializes the widget by creating UI elements such as search areas, result and corpus lists, add and remove buttons, etc.
- The dataExtraction() method is responsible for extracting data from the Poetica.fr website. It uses the segmentation and import modules provided by the LTTL library to extract information about authors, themes, and poems from different pages of the website.
- The searchFunction() method is called when the search button is clicked. It performs a search based on the selected criteria (author and/or theme) and displays the results in the result list.
- The add() and remove() methods are used to add or remove items from the corpus list.

About Poetica:
-----
Poetica is a project developed by the LOLS group in 2023. We created this software to help Orange users analyze poems more easily.

Olivia VERBRUGGE
Leonie NUSSBAUM
Laure MARGOT
Sinem KILIC

Textable Prototypes is an open-source extension for Orange Canvas 3. It includes text analysis widgets that could not be included in the main distribution of Textable for various reasons (including introducing dependencies on third-party packages or simply because they are not