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

# TODO Ajouter d'autres annotations
# TODO Ajouter les options de recherches
# TODO Les recherches devraient filtrés les films n'ayant pas de critique avant de les afficher dans le corpus 
# TODO Le bouton 'search' devrait être disable quand y'a rien qui est recherché

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
    autoSend = settings.Setting(False)
    myBasket = settings.Setting([])

    #----------------------------------------------------------------------
    # GUI layout parameters...

    want_main_area = False

    def __init__(self):
        super().__init__()

        # Search filters attributs
        self.newQuery = ''
        self.type_results = 'Title'
        self.genre_searched = 'Comedy'
        self.filter_results = 'Popularity'
        self.nbr_results = '10'
        # Results box attributs
        self.titleLabels = list()
        self.selectedTitles = list()
        # selections box attributs
        self.myTitles = list()
        self.mytitleLabels = list()
        # stock all the inputs (movie names) in a list
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
        self.queryBox = gui.widgetBox(
            widget=self.controlArea,
            box="Query",
            orientation="horizontal",
        )

        self.genreBox = gui.widgetBox(
            widget=self.controlArea,
            box="Query",
            orientation="horizontal",
        )

        self.filterBox = gui.widgetBox(
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

        # List Box where all the searched movies are stocked
        self.titleListbox = gui.listBox(
            widget=resultBox,
            master=self,
            value="selectedTitles",
            labels="titleLabels",
            callback=lambda: self.addButton.setDisabled(
                self.selectedTitles == list()),
            tooltip="The list of titles whose content will be imported",
        )
        self.titleListbox.doubleClicked.connect(self.addToCorpus)
        self.titleListbox.setMinimumHeight(150)
        self.titleListbox.setSelectionMode(3)

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

        # Corpus where confirmed movies are moved and stocked
        self.mytitleListbox = gui.listBox(
            widget=corpusBox,
            master=self,
            value="myTitles",
            labels="mytitleLabels",
            callback=lambda: self.removeButton.setDisabled(
                self.myTitles == list()),
            tooltip="The list of titles whose content will be imported",
        )
        self.mytitleListbox.doubleClicked.connect(self.remove)
        self.mytitleListbox.setMinimumHeight(150)
        self.mytitleListbox.setSelectionMode(3)

        corpusButtonBox = gui.widgetBox(
            widget= corpusBox,
            box=False,
            orientation='horizontal',
        )

        # Allows to enter specific text to the research
        gui.lineEdit(
            widget=self.queryBox,
            master=self,
            value='newQuery',
            orientation='horizontal',
            label=u"Search: ",
            labelWidth=120,
            tooltip=("Enter a string"),
        )

        # Allows to choose a type of search
        searchType = gui.comboBox(
            widget=self.queryBox,
            master=self,
            value="type_results",
            items=[
                "Title",
                "Actor",
                "Genre",
            ],
            sendSelectedValue=True,
            callback=self.mode_changed,
            orientation="horizontal",
            label="Search Type: ",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )

        genreTypes = gui.comboBox(
            widget=self.genreBox,
            master=self,
            value="genre_searched",
            items=[
                "Comedy",
                "Action",
                "Drama",
                "Horror",
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Search Type: ",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )

        searchTypeGenre = gui.comboBox(
            widget=self.genreBox,
            master=self,
            value="type_results",
            items=[
                "Title",
                "Actor",
                "Genre",
            ],
            sendSelectedValue=True,
            callback=self.mode_changed,
            orientation="horizontal",
            label="Search Type: ",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )



        # Allows to chose a filter for the search
        self.searchFilter = gui.comboBox(
            widget=self.filterBox,
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
            widget=self.filterBox,
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
        # Uses "searchMovies" attribute
        self.searchButton = gui.button(
            widget=searchButtonBox,
            master=self,
            label="Search",
            callback=self.searchMovies,
            tooltip="Connect to imdbpy and make a research",
        )
     
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
        # Uses "clearResults" function
        self.clearButton = gui.button(
            widget=resultButtonBox,
            master=self,
            label="Clear results",
            callback=self.clearResults,
            tooltip="Clear results",
        )
        self.clearButton.setDisabled(True)
        #gui.separator(widget=queryBox, height=3)

        # Remove movie button
        self.removeButton = gui.button(
            widget=corpusButtonBox,
            master=self,
            label=u'Remove from corpus',
            callback=self.remove,
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
            callback=self.clearCorpus,
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

        #self.mode_changed()
        self.updateCorpus()

        self.mode_changed()

        # Send data if autoSend.
        self.sendButton.sendIf()


    def mode_changed(self):
        self.sendButton.settingsChanged()
        if self.type_results == "Title": # 0 = subreddit selected
            # Hide URL and full text
            self.genreBox.setVisible(False)
            self.queryBox.setVisible(True)
            self.filterBox.setVisible(True)
            self.searchFilter.setVisible(False)

        elif self.type_results == "Genre":
            # Hide subreddit
            self.queryBox.setVisible(False)
            self.genreBox.setVisible(True)
            self.filterBox.setVisible(True)
            self.searchFilter.setVisible(True)
        
        elif self.type_results == "Actor":
            self.queryBox.setVisible(True)
            self.genreBox.setVisible(False)
            self.filterBox.setVisible(True)
            self.searchFilter.setVisible(True)
        return




    def searchMovies(self):
        """Search from imdb movie database"""
        result_list = {}
        query_string = self.newQuery

        if query_string != "":
            counter = 1
            counter_max = int(self.nbr_results)
            result_id = 0

            self.controlArea.setDisabled(True)

            # Initialize progress bar
            progressBar = ProgressBar(
                self,
                iterations=counter_max
            )
            if self.type_results == 'Title':
                ia = imdb.IMDb()

                # movie name
                movie_name = query_string

                # searching the movie
                search = ia.search_movie(movie_name)
                for film in search:
                    try:
                        good_search = film['year']
                    except KeyError:
                        search.remove(film)

            elif self.type_results == 'Actor':
                ia = imdb.IMDb()
                # movie name
                actor_name = query_string
                people = ia.search_person(actor_name)
                searched_actor = people[0].personID
                first_search = ia.get_person_filmography(searched_actor)
                print(first_search)
                
                try:
                   search = first_search['data']['filmography']['actor']
                except KeyError:
                    search = first_search['data']['filmography']['actress']

                for film in search:
                    try:
                        good_search = film['year']
                    except KeyError:
                        search.remove(film)
                        
                print(search)
                #print(actor_results)
            elif self.type_results == 'Genre':
                ia = imdb.IMDb()
                result = ia.get_keyword('marvel')
                print(result)


            # Each result is stored in a dictionnary with its title
            # and year of publication if it is specified
            for result in search:
                if counter <= counter_max:
                    result_id += 1
                    year = result['year']
                    movie_id = result.movieID
                    result_list[result_id] = {'name': result,
                                            'year': year,
                                            'id': movie_id}
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
                except:
                    result_string = f'{self.searchResults[idx]["name"]}'
                    self.titleLabels.append(result_string)

            self.titleLabels = self.titleLabels
            self.clearButton.setDisabled(False)
            self.addButton.setDisabled(self.selectedTitles == list())


            # Clear progress bar.
            progressBar.finish()
            self.controlArea.setDisabled(False)

        else:
            self.infoBox.setText("Please enter a movie title", "warning")

    # Add movie to corpus
    def addToCorpus(self):
        """Add movies in your selection """
        cond_list = list()
        for selectedTitle in self.selectedTitles:
            newMovie = self.searchResults[selectedTitle+1]
            if newMovie not in self.myBasket:
                # Test if the movie has review associated, if not it refuses to add it to corpus
                try:
                    ia = imdb.IMDb()
                    movie = ia.get_movie_reviews(newMovie['id'])
                    cond_list.append(movie)
                    for movie in cond_list:
                        data = movie.get('data', "")
                        reviews_data = data.get('reviews')
                        for review in reviews_data:
                            pass
                    self.myBasket.append(newMovie)
                except:
                    self.infoBox.setText(
                    "Cannot add to corpus. One or more selected movies have no associated reviews",
                    "warning"
                    )
                    return
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

    def remove(self):
        """Remove the selected movie in the corpus """
        self.myBasket = [
            movie for idx, movie in enumerate(self.myBasket)
            if idx not in self.myTitles
        ]
        self.updateCorpus()
        self.sendButton.settingsChanged()

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

        # Clear created Inputs.
        self.clearCreatedInputs()

        self.controlArea.setDisabled(True)

        # Initialize progress bar.
        progressBar = ProgressBar(
            self,
            iterations=len(self.myBasket)
        )

        # Connect to imdb and add elements in lists
        selectedSongs = list()
        list_review = list()
        list_annotation = list()
        annotations = list()
        try:
            for item in self.myBasket:
                ia = imdb.IMDb()
                movie = ia.get_movie_reviews(item['id'])
                movie_annotations = ia.get_movie(item['id'])
                list_review.append(movie)
                list_annotation.append(movie_annotations)
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
            data = movie.get('data', "")
            reviews_data = data.get('reviews')
            for review in reviews_data:
                reviews = review.get('content')
                newInput = Input(reviews)
                self.createdInputs.append(newInput)
                new_dict = review.copy()

                # Store the annotation as dicts in a separate list
                annotations_dict = {"title": movie_annotations, "year": movie_annotations["year"]}
                annot_dict_copy = annotations_dict.copy()
                annotations.append(annot_dict_copy)
            

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
        for idx, segment in enumerate(self.segmentation):
            segment.annotations.update(annotations[idx])
            self.segmentation[idx] = segment

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
        message += " (%i character@p)." % numChars
        message = pluralize(message, numChars)
        self.infoBox.setText(message)

        self.send('Segmentation', self.segmentation, self)
        self.sendButton.resetSettingsChangedFlag()

    def clearResults(self):
        """Clear the results list"""
        del self.titleLabels[:]
        self.titleLabels = self.titleLabels
        self.clearButton.setDisabled(True)
        self.addButton.setDisabled(self.titleLabels == list())

    def clearCreatedInputs(self):
        """Delete all Input objects that have been created."""
        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]

    def clearCorpus(self):
        """Remove all movies in the corpus"""
        self.mytitleLabels = list()
        self.myBasket = list()
        self.sendButton.settingsChanged()
        self.clearmyBasket.setDisabled(True)

if __name__ == "__main__":
    WidgetPreview(MovieReviews).run()
