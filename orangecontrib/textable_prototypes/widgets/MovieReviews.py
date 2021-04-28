"""
Class MovieReviews
Copyright 2020-2021 University of Lausanne
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

# TODO Bouger les boutons de 'clear' et de 'add' sous les listbox
# TODO Annoter les segments output

__version__ = u"0.0.1"
__author__ = "Caroline Rohrbach, Maryam Zoee, Victor Vermot"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

from Orange.widgets import widget, gui, settings

from Orange.widgets.utils.widgetpreview import WidgetPreview
from LTTL.Segmentation import Segmentation
import LTTL.Segmenter as Segmenter
from LTTL.Input import Input

import imdb

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar,
)

class MovieReviews(OWTextableBaseWidget):
    """An orange widget to get movie reviews from Imdb"""

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Movie Reviews"
    description = "Get movie reviews from imdb"
    icon = ""
    priority = 15

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = []
    outputs = [("Segmentation", Segmentation)]

    #----------------------------------------------------------------------
    # Handles the futur versions settings

    settingsHandler = VersionedSettingsHandler(
    version=__version__.rsplit(".", 1)[0]
    )

    # Settings
    autoSend = settings.Setting(True)
    myBasket = settings.Setting([])

    #----------------------------------------------------------------------
    # GUI layout parameters...

    want_main_area = False

    def __init__(self):
        super().__init__()

        # Search filters attributs
        self.newQuery = ''
        self.type_results = 'Title'
        self.filter_results = 'Popularity'
        self.nbr_results = '10'
        # Results box attributs
        self.titleLabels = list()
        self.selectedTitles = list()
        # selections box attributs
        self.myTitles = list()
        self.mytitleLabels = list()
        self.createdInputs = list()


        # Mandatory declaration of the info box and the send button
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute='infoBox',
            sendIfPreCallback=None,
        )

        #----------------------------------------------------------------------
        # User interface...

        # Creation of the different working areas
        queryBox = gui.widgetBox(
            widget=self.controlArea,
            box="Search movies",
            orientation="horizontal",
        )

        filterBox = gui.widgetBox(
            widget=self.controlArea,
            box="Filters",
            orientation="horizontal",
        )

        searchButtonBox = gui.widgetBox(
            widget=self.controlArea,
            orientation="vertical",
        )

        resultBox = gui.widgetBox(
            widget=self.controlArea,
            box="Search results",
            orientation="vertical",
        )

        resultButtonBox = gui.widgetBox(
            widget=resultBox,
            box=False,
            orientation='horizontal',
        )

        corpusBox = gui.widgetBox(
            widget=self.controlArea,
            box="Corpus",
            orientation="vertical",
        )

        corpusButtonBox = gui.widgetBox(
            widget=corpusBox,
            box=False,
            orientation='horizontal',
        )



        # Allows to enter specific text to the research
        gui.lineEdit(
            widget=queryBox,
            master=self,
            value='newQuery',
            orientation='horizontal',
            label=u"Search: ",
            labelWidth=120,
            tooltip=("Enter a string"),
        )

        # Allows to choose a type of search
        searchType = gui.comboBox(
            widget=queryBox,
            master=self,
            value="type_results",
            items=[
                "Title",
                "Actor",
                "Genre",
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Search Type: ",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )
        # Allows to chose a filter for the search
        searchFilter = gui.comboBox(
            widget=filterBox,
            master=self,
            value="filter_results",
            items=[
                "Popularity",
                "Alphabetical",
                "Random",
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Search by: ",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )

        # Allows to choose the wanted results numberp (10 by 10)
        searchNbr = gui.comboBox(
            widget=filterBox,
            master=self,
            value="nbr_results",
            items=[
                "10",
                "20",
                "30",
                "40",
                "50",
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
        self.searchButton = gui.button(
            widget=searchButtonBox,
            master=self,
            label="Search",
            callback=self.searchMovies,
            tooltip="Connect to imdbpy and make a research",
        )

        # List Box where all the searched movies are stocked
        self.titleListbox = gui.listBox(
            widget=resultBox,
            master=self,
            value="selectedTitles",
            labels="titleLabels",
            callback=None,
            tooltip="The list of titles whose content will be imported",
        )
        self.titleListbox.setMinimumHeight(150)
        self.titleListbox.setSelectionMode(3)

        
        # Add movies button
        self.addButton = gui.button(
            widget=resultButtonBox,
            master=self,
            label=u'Add to corpus',
            callback=self.addToCorpus,
            tooltip=(
                u"Move the selected movie downward in your corpus."
            ),
        )
        self.addButton.setDisabled(True)

        # Clear button
        self.clearButton = gui.button(
            widget=resultButtonBox,
            master=self,
            label="Clear results",
            callback=self.clearResults,
            tooltip="Clear results",
        )
        self.clearButton.setDisabled(True)
        #gui.separator(widget=queryBox, height=3)

        # Corpus where confirmed movies are moved and stocked
        self.mytitleListbox = gui.listBox(
            widget=corpusBox,
            master=self,
            value="myTitles",
            labels="mytitleLabels",
            callback=None,
            tooltip="The list of titles whose content will be imported",
        )
        self.mytitleListbox.setMinimumHeight(150)
        self.mytitleListbox.setSelectionMode(3)


        # Remove movie button
        self.removeButton = gui.button(
            widget=corpusButtonBox,
            master=self,
            label=u'Remove from corpus',
            callback=None,
            tooltip=(
                u"Remove the selected movie from your corpus."
            ),
        )
        self.removeButton.setDisabled(True)

        # Delete all confirmed movies button
        self.clearmyBasket = gui.button(
            widget=corpusButtonBox,
            master=self,
            label=u'Clear corpus',
            callback=None,
            tooltip=(
                u"Remove all movies from your corpus."
            ),
        )
        self.clearmyBasket.setDisabled(True)

        gui.separator(widget=corpusBox, height=3)
        gui.rubber(self.controlArea)
        #----------------------------------------------------------------------

        # Draw Info box and Send button
        self.sendButton.draw()
        self.searchButton.setDefault(True)
        self.infoBox.draw()

        # Send data if autoSend.
        self.sendButton.sendIf()

    def placeholder(self):
        return

    def searchMovies(self):
        """Search from imdb movie database"""
        result_list = {}
        query_string = self.newQuery

        if query_string != "":
            counter = 1
            counter_max = int(self.nbr_results)
            result_id = 0
            result_artist = []

            self.controlArea.setDisabled(True)

            # Initialize progress bar
            progressBar = ProgressBar(
                self,
                iterations=counter_max
            )

            ia = imdb.IMDb()
            
            # movie name
            name = query_string

            # searching the movie
            search = ia.search_movie(name)
            print(search)

            # Each result is stored in a dictionnary with its title
            # and year of publication if it is specified
            for result in search:
                if counter <= counter_max:
                    #print(counter)
                    #print(counter_max)
                    try:
                        result_id += 1
                        year = result['year']
                        movie_id = result.movieID
                        result_list[result_id] = {'name': result,
                                                'year': year,
                                                'id': movie_id}
                    except KeyError:
                        result_id += 1
                        result_list[result_id] = {'name': result,}

                    counter += 1
                else:
                    break

            # 1 tick on the progress bar of the widget
            progressBar.advance()
            # Stored the results list in the "result_list" variable
            self.searchResults = result_list

            # Reset and clear the visible widget list
            del self.titleLabels[:]

            # Update the results list with the search results
            # in order to display them
            for idx in self.searchResults:
                try:
                    result_string = f'{self.searchResults[idx]["name"]} - {self.searchResults[idx]["year"]}'
                    self.titleLabels.append(result_string)
                except KeyError: 
                    result_string = f'{self.searchResults[idx]["name"]}'
                    self.titleLabels.append(result_string)

            self.titleLabels = self.titleLabels
            self.clearButton.setDisabled(False)
            self.addButton.setDisabled(False)


            # Clear progress bar.
            progressBar.finish()
            self.controlArea.setDisabled(False)

        else:
            self.infoBox.setText("Please enter a movie title", "warning")

    # Add movie to corpus
    def addToCorpus(self):
        """Add movies in your selection """
        for selectedTitle in self.selectedTitles:
            newMovie = self.searchResults[selectedTitle+1]
            if newMovie not in self.myBasket:
                self.myBasket.append(newMovie)
        self.updateCorpus()
        self.sendButton.settingsChanged()

    # Make the movie appear in the corpus Listbox
    def updateCorpus(self):
        """Update the corpus box list in order to view the movies added"""
        self.mytitleLabels = list()
        for newMovie in self.myBasket:
            try: 
                result_string = f'{newMovie["name"]} - {newMovie["year"]}'
                self.mytitleLabels.append(result_string)
            except KeyError:
                result_string = newMovie["name"]
                self.mytitleLabels.append(result_string)
        self.mytitleLabels = self.mytitleLabels

        self.clearmyBasket.setDisabled(self.myBasket == list())
        self.removeButton.setDisabled(self.myTitles == list())


     # Remove movies function
    def sendData(self):
        """Compute result of widget processing and send to output"""
        # Skip if title list is empty:
        if self.myBasket == list():
            self.infoBox.setText(
                "Your corpus is empty, please add some movies first",
                "warning"
            )
            return
        
        def clearResults(self):
             """Clear the results list"""
            del self.titleLabels[:]
            self.titleLabels = self.titleLabels
            del self.selectedTitle[:]
            self.selectedTitle= self.selectedTitle
            self.clearButton.setDisabled(True)


        # Clear created Inputs.
        self.clearCreatedInputs()

        self.controlArea.setDisabled(True)

        # Initialize progress bar.
        progressBar = ProgressBar(
            self,
            iterations=len(self.myBasket)
        )

        # Attempt to connect to Genius and retrieve lyrics...
        selectedSongs = list()
        list_review = list()
        try:
            for item in self.myBasket:
                ia = imdb.IMDb()
                movie = ia.get_movie_reviews(item['id'])
                list_review.append(movie)
                # 1 tick on the progress bar of the widget
                progressBar.advance()

        # If an error occurs (e.g. http error, or memory error)...
        except:
            # Set Info box and widget to "error" state.
            self.infoBox.setText(
                "Couldn't download data from imdb",
                "error"
            )
            self.controlArea.setDisabled(False)
            return

        # Store movie critics strings in input objects...
        for movie in list_review:
            #for key, value in movie.items():
            data = movie.get('data', "")
            reviews_data = data.get('reviews')
            for review in reviews_data:
                reviews = review.get('content')
                newInput = Input(reviews)
                self.createdInputs.append(newInput)

        # If there's only one item, the widget's output is the created Input.
        if len(self.createdInputs) == 1:
            self.segmentation = self.createdInputs[0]

        # Otherwise the widget's output is a concatenation...
        else:
            self.segmentation = Segmenter.concatenate(
                self.createdInputs,
                import_labels_as=None,
            )

        # Annotate segments...
        """
        for idx, segment in enumerate(self.segmentation):
            segment.annotations.update(annotations[idx])
            self.segmentation[idx] = segment
        """

        # Clear progress bar.
        progressBar.finish()

        self.controlArea.setDisabled(False)

        # Set status to OK and report data size...
        message = f"{len(self.segmentation)} segment@p sent to output"
        message = pluralize(message, len(self.segmentation))
        numChars = 0
        for segment in self.segmentation:
            segmentLength = len(Segmentation.get_data(segment.str_index))
            numChars += segmentLength
        message += "(%i character@p)." % numChars
        message = pluralize(message, numChars)
        self.infoBox.setText(message)

        self.send('Segmentation', self.segmentation, self)
        self.sendButton.resetSettingsChangedFlag()

    def clearCreatedInputs(self):
        """Delete all Input objects that have been created."""
        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]


if __name__ == "__main__":
    WidgetPreview(MovieReviews).run()
