"""
Class Gutenberg
Copyright 2018-2021 University of Lausanne
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

__version__ = u"0.0.0"
__author__ = "Florian Rieder, Paul Zignani"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

import os
from pathlib import Path

# Orange
from Orange.widgets import widget, gui, settings

# LTTL
from LTTL.Segmentation import Segmentation
import LTTL.Segmenter as Segmenter
from LTTL.Input import Input

# gutenbergpy
import gutenbergpy.textget
from gutenbergpy.gutenbergcache import GutenbergCache

# chardet
import chardet

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
    priority = 10

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
        # stock all the inputs (songs) in a list
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
        queryBox = gui.widgetBox(
            widget=self.controlArea,
            box="Search books",
            orientation="vertical",
        )

        self.cacheGenerationButton = gui.button(
            widget=queryBox,
            master=self,
            label="Generate cache",
            callback=self.generate_cache,
            tooltip="Generate the gutenberg cache, this might take a while...",
        )

        # Allows to enter specific text to the research
        #  Uses "newQuery" attribut
        gui.lineEdit(
            widget=queryBox,
            master=self,
            value='titleQuery',
            orientation='horizontal',
            label=u"Title: ",
            labelWidth=120,
            tooltip=("Enter a string"),
        )

        gui.lineEdit(
            widget=queryBox,
            master=self,
            value='authorQuery',
            orientation='horizontal',
            label=u"Author: ",
            labelWidth=120,
            tooltip=("Enter a string"),
        )

        queryLang = gui.comboBox(
            widget=queryBox,
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
        # Allows to choose the wanted results numberp (10 by 10)
        queryNbr = gui.comboBox(
            widget=queryBox,
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
            widget=queryBox,
            master=self,
            label="Search",
            callback=self.search,
            tooltip="Connect Genius and make a research",
        )
        self.titleListbox = gui.listBox(
            widget=queryBox,
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
            widget=queryBox,
            box=False,
            orientation='horizontal',
        )
        # Add songs button
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
        gui.separator(widget=queryBox, height=3)

        # area where confirmed songs are moved and stocked
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
        # Remove songs button
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


    def generate_cache(self):
        print(self.cacheExists())
        if not self.cacheExists():
            try:
                self.infoBox.setText(
                    "The cache is being generated. This can take up to 10mn."
                )
                GutenbergCache.create(
                    refresh=True,
                    download=True,
                    unpack=True,
                    parse=True,
                    deleteTemp=True
                )
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

        lang_dict = {
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

        if query_string:
            # parse query and lookup in gutenbergcache
            cache = GutenbergCache.get_cache()

            try:
                query_results = cache.native_query(
                    sql_query="""
                    SELECT titles.name, authors.name, books.gutenbergbookid
                    FROM titles
                    INNER JOIN books ON books.id = titles.bookid
                    INNER JOIN book_authors ON  books.id = book_authors.bookid 
                    INNER JOIN authors ON authors.id = book_authors.authorid
                    INNER JOIN languages ON books.languageid = languages.id
                    WHERE upper(titles.name) LIKE "%{title}%"
                    AND upper(authors.name) LIKE "%{author}%"
                    AND languages.name LIKE "%{lang}%"
                    LIMIT {limit}
                    """.format(title=query_string, author=self.authorQuery, lang=lang_dict[self.langQuery],limit=self.nbr_results)
                )
            except Exception as exc:
                print(exc)
                self.infoBox.setText(
                    "An error occurred while interrogating the cache.",
                    "error"
                )
                return
            # get the results
            self.searchResults = list(query_results)

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
                
                result_string = "%s - %s" % (idx[0], idx[1])
                self.titleLabels.append(result_string)

                self.titleLabels = self.titleLabels
                self.clearButton.setDisabled(False)
                self.addButton.setDisabled(self.selectedTitles == list())

                self.controlArea.setDisabled(False)

        else:
            self.infoBox.setText("You didn't search anything", "warning")


    # Function clearing the results list
    def clearResults(self):
        """Clear the results list"""
        del self.titleLabels[:]
        self.titleLabels = self.titleLabels
        self.clearButton.setDisabled(True)
        self.addButton.setDisabled(self.titleLabels == list())


    # Add texts function
    def add(self):
        """Add songs in your selection """
        for selectedTitle in self.selectedTitles:
            titleData = self.searchResults[selectedTitle]
            if titleData not in self.myBasket:
                self.myBasket.append(titleData)

        self.updateMytitleLabels()
        self.sendButton.settingsChanged()

    # Update selections function
    def updateMytitleLabels(self):
        self.mytitleLabels = list()
        for titleData in self.myBasket:
            result_string = "%s - %s" % (titleData[0] ,titleData[1])
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
        """Remove all songs in your selection """
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

        selectedTexts = list()
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
                annotations.append([text[0], text[1]])
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

        # If there"s only one play, the widget"s output is the created Input.
        if len(self.createdInputs) == 1:
            self.segmentation = self.createdInputs[0]

        # Otherwise the widget"s output is a concatenation...
        else:
            self.segmentation = Segmenter.concatenate(
                self.createdInputs,
                self.captionTitle,
                import_labels_as=None,
            )

        # TODO: add author, language, etc
        # Annotate segments with book metadata
        for idx, segment in enumerate(self.segmentation):
            segment.annotations.update({"title": annotations[idx][0]})
            segment.annotations.update({"authors": annotations[idx][1]})
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

        self.send("Gutenberg importation", self.segmentation, self)
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

    def cacheExists(self):
        # OOH THIS IS UGLY
        # get the root directory of the package
        root = Path(__file__).parent.parent.parent.parent.parent
        # check if the cache database exists
        return os.path.isfile("gutenbergindex.db")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    myApplication = QApplication(sys.argv)
    myWidget = Gutenberg()
    myWidget.show()
    myApplication.exec_()
    myWidget.saveSettings()
