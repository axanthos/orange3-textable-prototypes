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
import random

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
        #self.genre_searched = 'Comedy'
        self.filter_results = 'Popularity'
        self.nbr_results = '10'
        # Results box attributs
        self.titleLabels = list()
        self.selectedTitles = list()
        # selections box attributs
        self.myTitles = list()
        self.mytitleLabels = list()

        # stocks the imdbpy instance
        self.ia = imdb.IMDb()
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
            box="Query options",
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
                #"Genre",
            ],
            sendSelectedValue=True,
            callback=self.mode_changed,
            orientation="horizontal",
            label="Search by: ",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )
        """genreTypes = gui.comboBox(
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
        """
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
                "Year",
                "Alphabetical",
                "Random",
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Sort by: ",
            labelWidth=120,
            tooltip=(
                "Please select the desired search.\n"
            ),
        )

        # Allows to choose the wanted results numberp (10 by 10)
        self.searchNbr = gui.comboBox(
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
            label="Results' number: ",
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
            # Hide Genre box
            self.genreBox.setVisible(False)
            self.queryBox.setVisible(True)
            self.filterBox.setVisible(True)
            #self.searchFilter.setVisible(False)
            self.searchFilter.setDisabled(True)
            self.searchNbr.setVisible(True)
        elif self.type_results == "Genre":
            # Hide Title
            self.queryBox.setVisible(False)
            self.genreBox.setVisible(True)
            self.filterBox.setVisible(True)
            #self.searchFilter.setVisible(True)
            self.searchFilter.setDisabled(False)
            self.searchNbr.setVisible(True)
        elif self.type_results == "Actor":
            # searchFilter disabled
            self.queryBox.setVisible(True)
            self.genreBox.setVisible(False)
            self.filterBox.setVisible(True)
            #self.searchFilter.setVisible(True)
            self.searchFilter.setDisabled(False)
            self.searchNbr.setVisible(True)
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
            filtered_results = list()
            if self.type_results == 'Title':

                # movie name
                movie_name = query_string

                # searching the movie
                search = self.ia.search_movie(movie_name)
                for film in search:
                    if 'year' in film:
                        filtered_results.append(film)

            elif self.type_results == 'Actor':
                actor_name = query_string
                people = self.ia.search_person(actor_name)
                searched_actor = people[0].personID
                first_search = self.ia.get_person_filmography(searched_actor)

                # Checks if the user input is a valid actor/actress
                if 'actor' in first_search['data']['filmography']:
                    search = first_search['data']['filmography']['actor']
                elif 'actress' in first_search['data']['filmography']:
                    search = first_search['data']['filmography']['actress']
                else:
                    search = list()
                    self.infoBox.setText("Please enter a valid actor or actress name", "warning")

                # Checks if the movie has a year associated and stores it in a list
                filtered_results = [film for film in search if 'year' in film]

            if self.filter_results == 'Random':
                random.shuffle(filtered_results)

            elif self.filter_results == 'Alphabetical':
                alpha_dict = dict()
                for result in filtered_results:
                    my_id = result.movieID
                    alpha_dict[str(result)] = my_id
                    print(alpha_dict)
                sorted_dict = sorted(alpha_dict.keys(), key=lambda x:x.lower())
                print(sorted_dict)
                filtered_results = list()
                for i in sorted_dict:
                    value = alpha_dict[i]
                    print(value)
                    print(self.ia.get_movie(value))
                    filtered_results.append(self.ia.get_movie(value))

            # Each result is stored in a dictionnary with its title
            # and year of publication if it is specified

            for result in filtered_results:
                if counter <= counter_max:
                    try:
                        result_id += 1
                        year = result['year']
                        movie_id = result.movieID
                        result_list[result_id] = {'name': result,
                                                'year': year,
                                                'id': movie_id}
                    except KeyError:
                        continue
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
                result_string = f'{self.searchResults[idx]["name"]} - {self.searchResults[idx]["year"]}'
                self.titleLabels.append(result_string)

            self.titleLabels = self.titleLabels
            self.clearButton.setDisabled(False)
            self.addButton.setDisabled(self.selectedTitles == list())


            # Clear progress bar.
            progressBar.finish()
            self.controlArea.setDisabled(False)

        else:
            self.infoBox.setText("Please type something in the search bar", "warning")
    

    # Add movie to corpus
    def addToCorpus(self):
        """Add movies in your selection """
        cond_list = list()
        for selectedTitle in self.selectedTitles:
            newMovie = self.searchResults[selectedTitle+1]
            if newMovie not in self.myBasket:
                # Test if the movie has review associated, if not it refuses to add it to corpus
                movie = self.ia.get_movie_reviews(newMovie['id'])
                cond_list.append(movie)
                for movie in cond_list:
                    data = movie.get('data', "")
                    if 'reviews' in data:
                        self.myBasket.append(newMovie)
                    else:
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
            result_string = f'{newMovie["name"]} - {newMovie["year"]}'
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
        list_review = list()
        list_annotation = list()
        annotations = list()
        try:
            for item in self.myBasket:
                movie = self.ia.get_movie_reviews(item['id'])
                movie_annotations = self.ia.get_movie(item['id'])
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
        for item in list_annotation:
            print(item)
            # Store the annotation as dicts in a separate list
            annotations_dict = {"title": item, "year": item["year"]}
            annot_dict_copy = annotations_dict.copy()
            for i in range(25):
                annotations.append(annot_dict_copy)
        print(annotations)
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
