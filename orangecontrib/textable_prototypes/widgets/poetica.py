"""
Class Poetica
Copyright 2022-2023 University of Lausanne
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

__version__ = u"0.0.3"
__author__ = "Olivia Verbrugge, Sinem Kilic, Leonie Nussbaum et Laure Margot"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

# Import the necessary packages...
from Orange.widgets import widget, gui, utils
from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar,
)

# Informations...
__version__ = "0.01"


# Create the poetica class...
class poetica(widget.OWWidget):
    """
    This is the poetica class
    """

    # Widget's metadata...
    name = "Poetica"
    description = "Poetica's poems importation"
#    icon = ""
    priority = 20

    # Channel definitions...
    inputs = []
    outputs = [("Poetica's poems importation", str)]

    # Gui layout parameters...
    want_main_area = False
    resizing_enabled = False

    # Define the init function...
    def __init__(self):
        """
        This is the init function
        """
        # ATTRIBUTS
        # searchFunction
        self.searchResults = None
        self.inputSeg = None
        # newQuery = attribut box lineEdit (search something)
        self.authorQuery = ''
        self.dateQuery = ''
        self.topicQuery = ''
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
        queryBox = gui.widgetBox(
            widget=self.controlArea,
            box="Search poems",
            orientation="vertical",
        )
        # Allows to choose the wanted results number (10 by 10)
        queryAuthor = gui.comboBox(
            widget=queryBox,
            master=self,
            value="name_author",
            items=[
                "ACKERMANN Louise", "AGRIPPA D’AUBIGNÉ Théodore", "ALLAIS Alphonse",
                "APOLLINAIRE Guillaume","ARAGON Louis","ARVERS Félix",
                "BANVILLE (de) Théodore","BAUDELAIRE Charles","BEAUCHEMIN Nérée",
                "BELLAY (du) Joachim","BEN SLIMA Nadia","BENJELLOUN Rhita",
                "BLANCHEMAIN Dominique","BOILEAU Nicolas","BREGAINT Christophe",
                "BRETON Jules","CALLIS-SABOT Isabelle","CENDRARS Blaise",
                "CHALINE Thomas","CHATEAUBRIAND (de) François-René","CHEDID Andrée",
                "CHENIER André","COPPÉE François","CORBIÈRE Tristan","CORNEILLE Pierre",
                "COUTÉ Gaston","CROS Charles","DAUDET Alphonse","DAVIN Sandrine",
                "DELAVIGNE Casimir","DELAVIGNE Jules","DESBORDES-VALMORE Marceline",
                "DESROSIERS Susy","DORGE Jean-Charles","DOUGLAS Chloe","DUFRENOY Adélaïde",
                "ELSKAMP Max","ELUARD Paul","FABIÉ François","FOUREST Georges",
                "GAUTIER Théophile","GEORGES Edgar","GRANEK Esther","BAUDELAIRE Charles",
                "HEREDIA (de) José-Maria","HUGO Victor","JACOB Max","JAMMES Francis",
                "JARRY Alfred","JOUY Ephraïm","KRYSINSKA Marie","LA FONTAINE (de) Jean",
                "LABÉ Louise","LACAUSSADE Auguste","LACOSTE LAREYMONDIE (de) Guillaume",
                "LAFORGUE Jules","LAMARTINE (de) Alphonse","LARRIEU Christine",
                "LECONTE DE LISLE Charles","LERMAN ENRIQUEZ Alix","LERUTAN Isaac",
                "LUEZIOR Claude","MALLARMÉ Stéphane","MATIN Jérôme","MAUNICK Edouard J.",
                "MAUPASSANT (de) Guy","MÉGRELIS Christian","MÉNARD Louis",
                "MUSSET (de) Alfred","NAIVIN Bertrand","NELLIGAN Emile","NERVAL (de) Gérard",
                "NOAILLES (de) Anna","NOORMOHAMED Nashmia","NOUVEAU Germain",
                "PEREZ Winston","PICARD Hélène","PROUST Marcel","PRUDHOMME Sully",
                "QUENEAU Raymond","RACINE Jean","RANOUX Maëlle","RATEAU Grégory",
                "REMBARD Sybille","RICHEPIN Jean","RIMBAUD Arthur","RONSARD (de) Pierre",
                "SAMAIN Albert","SAND George","SANTOS Elodie","SAUVAGE Cécile",
                "SELVE (de) Lazare","SICAUD Sabine","SIOEN Laetitia","TAILLEFER Richard",
                "TASTU Amable","TOULET Paul-Jean","VALMORE Ondine","VENTURINI Didier",
                "VERHAEREN Emile","VERLAINE Paul","VIALLEBESSET Jacques","VIAN Boris",
                "VIGNY (de) Alfred","VILLEBRAMAR Jean-Pierre","VILLON François",
                "VIVIEN Renée","VOLTAIRE","ZERDOUMI Kamal",
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Author: ",
            labelWidth=120,
            tooltip=(
                "Please select an author.\n"
            ),
        )

        queryDate=gui.comboBox(
            widget=queryBox,
            master=self,
            value="date",
            items=[ "METTRE LES DATES"
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Date: ",
            labelWidth=120,
            tooltip=(
                "Please select a date.\n"
            ),
        )

        queryTopic=gui.comboBox(
            widget=queryBox,
            master=self,
            value="topic:",
            items=["METTRE LES THEMES"
            ],
            sendSelectedValue=True,
            orientation="horizontal",
            label="Topic: ",
            labelWidth=120,
            tooltip=(
                "Please select a topic.\n"
            ),
        )

        # Refresh database button
        self.refreshButton = gui.button(
            widget=boxbutton,
            master=self,
            label=u'Refresh database',
            callback=self.refresh,
            tooltip=(
                u" Cette action risque de prendre du temps"
            ),
        )
        self.refreshButton.setDisabled(True)

        # Reasearch button
        # Uses "searchFunction" attribut
        self.searchButton = gui.button(
            widget=self.queryBox,
            master=self,
            label="Search",
            callback=self.search,
            tooltip="???",
        )
self.clearButton.setDisabled(True)
gui.separator(widget=queryBox, height=3)

        self.titleListbox = gui.listBox(
            widget=queryBox,
            master=self,
            value="selectedTitles",  # setting (list)
            labels="titleLabels",  # setting (list)
            callback=lambda: self.addButton.setDisabled(
                self.selectedTitles == list()),
            tooltip="The list of titles whose content will be imported",
        )
        self.titleListbox.setMinimumHeight(150)
        self.titleListbox.setSelectionMode(3)


if __name__ == "__main__":
    WidgetPreview(Poetica).run()
