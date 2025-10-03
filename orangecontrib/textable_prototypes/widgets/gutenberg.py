"""
Class Gutenberg
Copyright 2021-2025 University of Lausanne
-----------------------------------------------------------------------------
This file is part of the Orange3-Textable-Prototypes package.

Orange3-Textable-Prototypes is free software: you can redistribute it
and/or modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Orange3-Textable-Prototypes is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Orange-Textable-Prototypes. If not, see
<http://www.gnu.org/licenses/>.
"""

__version__ = u"0.0.2"
__author__ = "Florian Rieder, Paul Zignani"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

from ntpath import join
import os
from pathlib import Path

# Orange
from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview

# LTTL
from LTTL.Segmentation import Segmentation
import LTTL.Segmenter as Segmenter
from LTTL.Input import Input

# gutenbergpy
import gutenbergpy.textget
from gutenbergpy.gutenbergcache import GutenbergCache

# regex
import re

# Textable
from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar,
)

class Gutenberg(OWTextableBaseWidget):
    """Textable widget for importing clean texts from Gutenberg
    (https://www.gutenberg.org/)
    """

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Gutenberg"
    description = "Gutenberg caching and importation"
    icon = "icons/gutenberg.png"
    priority = 21

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = []
    outputs = [("Gutenberg importation", Segmentation)]

    #----------------------------------------------------------------------
    # Layout parameters...

    want_main_area = False

    #----------------------------------------------------------------------
    # Settings...

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    # Saved settings
    autoSend = settings.Setting(False)
    myBasket = settings.Setting([])

    def __init__(self):
        """Widget creator."""

        super().__init__()

        # ATTRIBUTS
        # searchFunction
        self.searchResults = None
        self.inputSeg = None
        # newQuery = attribut box lineEdit (search something)
        self.titleQuery = ''
        self.authorQuery = ''
        self.langQuery = 'Any'
        self.nbr_results = 200
        # Results box attributs
        self.titleLabels = list()
        self.selectedTitles = list()
        # selections box attributs
        self.myTitles = list()
        self.mytitleLabels = list()
        # stock all the inputs (texts) in a list
        self.createdInputs = list()

        # Next two instructions are helpers from TextableUtils. Corresponding
        # interface elements are declared here and actually drawn below (at
        # their position in the UI)...
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute="infoBox",
        )
        #----------------------------------------------------------------------
        # User interface...
        # Create the working area
        self.cacheGenerationButton = gui.button(
            widget=self.controlArea,
            master=self,
            label="Generate cache",
            callback=self.generate_cache,
            tooltip="Generate the gutenberg cache, this might take a while...",
        )

        self.queryBox = gui.widgetBox(
            widget=self.controlArea,
            box="Search books",
            orientation="vertical",
        )


        # Allows to enter specific text to the research
        #  Uses "newQuery" attribut
        gui.lineEdit(
            widget=self.queryBox,
            master=self,
            value='titleQuery',
            orientation='horizontal',
            label=u"Title: ",
            labelWidth=120,
            tooltip=("Enter a string"),
        )

        gui.lineEdit(
            widget=self.queryBox,
            master=self,
            value='authorQuery',
            orientation='horizontal',
            label=u"Author: ",
            labelWidth=120,
            tooltip=("Enter a string"),
        )

        #ComboBox for selecting the text language
        queryLang = gui.comboBox(
            widget=self.queryBox,
            master=self,
            value='langQuery',
            items=["Any","Afrikaans","Aleut","Arabic",
                "Arapaho","Bodo","Breton","Bulgarian",
                "Caló","Catalan","Cebuano","Chinese",
                "Czech","Danish","Dutch","English",
                "Esperanto","Estonian","Farsi","Finnish",
                "French","Frisian","Friulian","Gaelic, Scottish",
                "Galician","Gamilaraay","German","Greek",
                "Greek, Ancient","Hebrew","Hungarian","Icelandic",
                "Iloko","Interlingua","Inuktitut","Irish",
                "Italian","Japanese","Kashubian","Khasi",
                "Korean","Latin","Lithuanian","Maori",
                "Mayan Languages","Middle English","Nahuatl",
                "Napoletano-Calabrese","Navajo","North American Indian",
                "Norwegian","Occitan","Ojibwa","Old English",
                "Polish","Portuguese","Romanian","Russian",
                "Sanskrit","Serbian","Slovenian","Spanish",
                "Swedish","Tagabawa","Tagalog","Telugu",
                "Welsh","Yiddish"
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Language",
            labelWidth=120,
            tooltip=(
                "Please select the desired language.\n"
            ),
        )

        #dict to get the language code
        self.lang_dict = {
            "Any":"", "Afrikaans":"af","Aleut":"ale",
            "Arabic":"ar","Arapaho":"arp","Bodo":"brx",
            "Breton":"br","Bulgarian":"bg","Caló":"rmr",
            "Catalan":"ca","Cebuano":"ceb","Chinese":"zh",
            "Czech":"cs","Danish":"da","Dutch":"nl",
            "English":"en","Esperanto":"eo","Estonian":"et",
            "Farsi":"fa","Finnish":"fi","French":"fr",
            "Frisian":"fy","Friulian":"fur","Gaelic, Scottish":"gla",
            "Galician":"gl","Gamilaraay":"kld","German":"de",
            "Greek":"el","Greek, Ancient":"grc","Hebrew":"he",
            "Hungarian":"hu","Icelandic":"is","Iloko":"ilo",
            "Interlingua":"ia","Inuktitut":"iu","Irish":"ga",
            "Italian":"it","Japanese":"ja","Kashubian":"csb",
            "Khasi":"kha","Korean":"ko","Latin":"la",
            "Lithuanian":"lt","Maori":"mi","Mayan Languages":"myn",
            "Middle English":"enm","Nahuatl":"nah","Napoletano-Calabrese":"nap",
            "Navajo":"nav","North American Indian":"nai","Norwegian":"no",
            "Occitan":"oc","Ojibwa":"oji","Old English":"ang",
            "Polish":"pl","Portuguese":"pt","Romanian":"ro",
            "Russian":"ru","Sanskrit":"sa","Serbian":"sr",
            "Slovenian":"sl","Spanish":"es","Swedish":"sv",
            "Tagabawa":"bgs","Tagalog":"tl","Telugu":"te",
            "Welsh":"cy","Yiddish":"yi"
            }
        # Allows to choose the wanted results numberp (10 by 10)
        queryNbr = gui.comboBox(
            widget=self.queryBox,
            master=self,
            value="nbr_results",
            items=[
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                "70",
                "80",
                "90",
                "100",
                "200",
                "300",
                "400",
                "500",
                "1000"
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Number of results: ",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )

        # Reasearch button
        # Uses "searchFunction" attribut
        self.searchButton = gui.button(
            widget=self.queryBox,
            master=self,
            label="Search",
            callback=self.search,
            tooltip="Connect Genius and make a research",
        )
        self.titleListbox = gui.listBox(
            widget=self.queryBox,
            master=self,
            value="selectedTitles",    # setting (list)
            labels="titleLabels",      # setting (list)
            callback=lambda: self.addButton.setDisabled(
                self.selectedTitles == list()),
            tooltip="The list of titles whose content will be imported",
        )
        self.titleListbox.setMinimumHeight(150)
        self.titleListbox.setSelectionMode(3)

        boxbutton = gui.widgetBox(
            widget=self.queryBox,
            box=False,
            orientation='horizontal',
        )
        # Add text button
        self.addButton = gui.button(
            widget=boxbutton,
            master=self,
            label=u'Add to corpus',
            callback=self.add,
            tooltip=(
                u"Move the selected book downward in your corpus."
            ),
        )
        self.addButton.setDisabled(True)

        # Clear button
        # Uses "clearResults" function
        self.clearButton = gui.button(
            widget=boxbutton,
            master=self,
            label="Clear results",
            callback=self.clearResults,
            tooltip="Clear results",
        )
        self.clearButton.setDisabled(True)
        gui.separator(widget=self.queryBox, height=3)

        # area where confirmed texts are moved and stocked
        mytitleBox = gui.widgetBox(
            widget=self.controlArea,
            box="Corpus",
            orientation="vertical",
        )

        self.mytitleListbox = gui.listBox(
            widget=mytitleBox,
            master=self,
            value="myTitles",
            labels="mytitleLabels",
            callback=lambda: self.removeButton.setDisabled(
                self.myTitles == list()),
            tooltip="The list of books which will be imported",
        )
        self.mytitleListbox.setMinimumHeight(150)
        self.mytitleListbox.setSelectionMode(3)

        boxbutton2 = gui.widgetBox(
            widget=mytitleBox,
            box=False,
            orientation='horizontal',
        )
        # Remove text button
        self.removeButton = gui.button(
            widget=boxbutton2,
            master=self,
            label=u'Remove from corpus',
            callback=self.remove,
            tooltip=(
                u"Remove the selected book from your corpus."
            ),
        )
        self.removeButton.setDisabled(True)

        # Delete all confirmed texts button
        self.clearmyBasketButton = gui.button(
            widget=boxbutton2,
            master=self,
            label=u'Clear corpus',
            callback=self.clearmyBasket,
            tooltip=(
                u"Remove all books from your corpus."
            ),
        )
        self.clearmyBasketButton.setDisabled(True)

        gui.separator(widget=mytitleBox, height=3)
        gui.rubber(self.controlArea)
        #----------------------------------------------------------------------

        # Draw Info box and Send button
        self.sendButton.draw()
        self.searchButton.setDefault(True)
        self.infoBox.draw()

        # Update the selections list
        self.updateMytitleLabels()

        # Send data if autoSend.
        self.sendButton.sendIf()

        # checks if the cache exists
        self.check_cache()


    def check_cache(self):
        """changes layout according to the cache existens
        """
        # disables the search button if cache does not exists
        if not GutenbergCache.exists():
            # disables the search button if not
            self.queryBox.setDisabled(True)
            self.infoBox.setText(
                "Cache must be generated before first launch, it can take up to 10min",
                "warning"
            )
        # disables the the cache generation button if it does exists
        else:
            self.cacheGenerationButton.setDisabled(True)

    def generate_cache(self):
        """generates the cache
        """
        if not GutenbergCache.exists():
            try:
                self.infoBox.setText(
                    "The cache is being generated. This can take up to 10min.",
                    "warning"
                )
                GutenbergCache.create(
                    refresh=True,
                    download=True,
                    unpack=True,
                    parse=True,
                    deleteTemp=True
                )
                self.infoBox.setText(
                    "Cache generated!"
                )
                self.cacheGenerationButton.setDisabled(True)
                self.queryBox.setEnabled(True)
            except Exception as exc:
                print(exc)
                self.infoBox.setText(
                    "An error occurred while building the cache",
                    "error"
                )
        else:
            self.infoBox.setText(
                "The cache already exists."
            )

    def search(self):
        """
            Parse a query string and do a search in the Gutenberg cache
        """
        query_string = self.titleQuery
        query_author = self.authorQuery
        language = self.lang_dict[self.langQuery]

        # informs the user that he didn't change anything
        if self.langQuery == 'Any' and query_string == '' and self.authorQuery == '':
            self.infoBox.setText("You can't search only by language, if it's set to Any",
                                 "warning")

        else:    
            # Recode author to name, first_name
            if len(query_author.split()) == 2:
                if "," not in query_author:
                    query_author = "%, ".join(query_author.split()[::-1])

            # parse query and lookup in gutenbergcache
            cache = GutenbergCache.get_cache()

            # searches the database
            try:
                query_results = cache.native_query(
                    sql_query="""
                    /* Creates a new table with one author per book
                    by selecting the greatest author id */

                    WITH unique_book_author AS
                    (SELECT * FROM book_authors  
                    WHERE authorid IN (SELECT MAX(authorid) FROM book_authors GROUP BY bookid))

                    /* Selects title, author, gutenberg id and language */

                    SELECT titles.name, authors.name, books.gutenbergbookid, languages.name
                    FROM titles

                    /* Merges every needed table into one on shared attributes */

                    INNER JOIN books ON books.id = titles.bookid
                    INNER JOIN unique_book_author ON  books.id = unique_book_author.bookid 
                    INNER JOIN authors ON authors.id = unique_book_author.authorid
                    INNER JOIN languages ON books.languageid = languages.id

                    /* Matches users query using % wildcard for more permissive query */

                    WHERE upper(titles.name) LIKE "%{title}%"
                    AND upper(authors.name) LIKE "%{author}%"
                    AND languages.name LIKE "%{lang}%"
                    LIMIT {limit}
                    """.format(
                        title=query_string, author=query_author,lang=language, limit=self.nbr_results)
                )
            except Exception as exc:
                print(exc)
                self.infoBox.setText(
                    "An error occurred while interrogating the cache.",
                    "error"
                )
                return
            # get the results
            Results = list(query_results)

            self.searchResults = list()

            # creates better results
            for result in Results:
                result = list(result)
                # replaces all newlines types
                result[0] = re.sub(r'[\n\r]+', r', ', result[0])
                # recodes athor from: name, first_name to: fisrt_name name
                result[1] = " ".join(result[1].split(", ")[::-1])
                # gets the key from the lang_dict for the coresponding language abbreviation
                result[3] = [key for key,value in self.lang_dict.items() if value == result[3]][0]

                self.searchResults.append(result)

            # display info message
            n_results = len(self.searchResults)
            self.infoBox.setText("{n} result{s} have been found".format(
                    n=n_results,
                    s= "s" if n_results > 0 else ""
                )
            )

            self.clearResults()
            # Update the results list with the search results
            # in order to display them
            for idx in self.searchResults:

                result_string = "{title} — {author} — {lang}".format(
                        title = idx[0], author = idx[1], lang = idx[3])
                self.titleLabels.append(result_string)

                self.titleLabels = self.titleLabels
                self.clearButton.setDisabled(False)
                self.addButton.setDisabled(self.selectedTitles == list())

                self.controlArea.setDisabled(False)



    # Function clearing the results list
    def clearResults(self):
        """Clear the results list"""
        del self.titleLabels[:]
        self.titleLabels = self.titleLabels
        self.clearButton.setDisabled(True)
        self.addButton.setDisabled(self.titleLabels == list())


    # Add texts function
    def add(self):
        """Add texts in your selection """
        for selectedTitle in self.selectedTitles:
            titleData = self.searchResults[selectedTitle]
            if titleData not in self.myBasket:
                self.myBasket.append(titleData)

        self.updateMytitleLabels()
        self.sendButton.settingsChanged()

    # Update selections function
    def updateMytitleLabels(self):
        """Update the selections list"""
        self.mytitleLabels = list()

        for titleData in self.myBasket:

            result_string = "{title} — {author} — {lang}".format(
                    title = titleData[0], author = titleData[1], lang = titleData[3])
            self.mytitleLabels.append(result_string)

        self.mytitleLabels = self.mytitleLabels
        self.clearmyBasketButton.setDisabled(self.myBasket == list())
        self.removeButton.setDisabled(self.myTitles == list())


    def remove(self):
        """Remove the selected books in the user's basket """
        self.myBasket = [
            title for idx, title in enumerate(self.myBasket)
            if idx not in self.myTitles
        ]
        self.updateMytitleLabels()
        self.sendButton.settingsChanged()


    # Clear selections function
    def clearmyBasket(self):
        """Remove all texts in your selection """
        self.mytitleLabels = list()
        self.myBasket = list()
        self.sendButton.settingsChanged()
        self.clearmyBasketButton.setDisabled(True)


    # Function computing results then sending them to the widget output
    def sendData(self):
        """Compute result of widget processing and send to output"""
        # Skip if title list is empty:
        if self.myBasket == list():
            self.infoBox.setText(
                "Your corpus is empty, please add some books first",
                "warning"
            )
            return


        # Clear created Inputs.
        self.clearCreatedInputs()

        self.controlArea.setDisabled(True)

        # Initialize progress bar.
        progressBar = ProgressBar(
            self,
            iterations=len(self.myBasket),
        )

        text_content = list()
        annotations = list()

        try:
            # Retrieve selected texts from gutenberg
            for text in self.myBasket:

                gutenberg_id = text[2]

                # Get the text with Gutenbergpy
                gutenberg_text = gutenbergpy.textget.strip_headers(
                    gutenbergpy.textget.get_text_by_id(gutenberg_id)
                ).decode("utf-8")

                text_content.append(gutenberg_text)
                # populate the annotation list
                annotations.append([text[0], text[1], text[3]])
                progressBar.advance()

        # If an error occurs (e.g. http error, or memory error)...
        except Exception as exc:
            # Set Info box and widget to "error" state.
            self.infoBox.setText(
                "Couldn't download data from Gutenberg",
                "error"
            )
            self.controlArea.setDisabled(False)
            print(exc)
            return

        # Store downloaded text strings in input objects...
        for text in text_content:
            newInput = Input(text, self.captionTitle)
            self.createdInputs.append(newInput)

        # If there's only one text, the widget's output is the created Input.
        if len(self.createdInputs) == 1:
            self.segmentation = self.createdInputs[0]

        # Otherwise the widget"s output is a concatenation.
        else:
            self.segmentation = Segmenter.concatenate(
                self.createdInputs,
                self.captionTitle,
                import_labels_as=None,
            )

        # Annotate segments with book metadata
        for idx, segment in enumerate(self.segmentation):
            segment.annotations.update({"title": annotations[idx][0]})
            segment.annotations.update({"author": annotations[idx][1]})
            segment.annotations.update({"language": annotations[idx][2]})
            self.segmentation[idx] = segment

        # Clear progress bar.
        progressBar.finish()

        self.controlArea.setDisabled(False)

        # Set status to OK and report data size...
        message = "%i segment@p sent to output " % len(self.segmentation)
        message = pluralize(message, len(self.segmentation))
        numChars = 0
        for segment in self.segmentation:
            segmentLength = len(Segmentation.get_data(segment.str_index))
            numChars += segmentLength
        message += "(%i character@p)." % numChars
        message = pluralize(message, numChars)
        self.infoBox.setText(message)

        self.send("Gutenberg importation", self.segmentation)
        self.sendButton.resetSettingsChangedFlag()


    def clearCreatedInputs(self):
        """Delete all Input objects that have been created."""
        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]


    # The following method needs to be copied verbatim in
    # every Textable widget that sends a segmentation...
    def setCaption(self, title):
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)


if __name__ == "__main__":
    WidgetPreview(Gutenberg).run()
