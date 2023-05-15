"""Extraction des données de Poetica"""


# Importer les packages necessaires...
import inspect
import os
import pickle
import re
import LTTL.Segmenter as Segmenter
from LTTL.Input import Input
from urllib.request import urlopen


def main():
    """Programme principal"""

    database = {
        "title": {},
        "author": {},
        #"date": {},
        "topic": {},
        #"poem": {},
    }

    # Acceder a la page d'accueil de poetica...
    try:
        poetica_url = 'https://www.poetica.fr/'
        url_accueil = urlopen(poetica_url)
        page_accueil = url_accueil.read()
        #print(page_accueil)
        print("Valid poetica's URL")
        page_accueil = page_accueil.decode("utf-8")
        #url_accueil.close()

        # Extraire la liste d'auteurs...
        base_seg = Input(page_accueil)
        condition = dict()
        condition["id"]=re.compile(r"^menu-poemes-par-auteur$")
        xml_auteurs = Segmenter.import_xml(
            segmentation=base_seg,
            element="<ul>",
            conditions=condition,
        )

        # Extraire la liste des themes...
        seg_themes = Input(page_accueil)
        condition_themes = dict()
        condition_themes["id"] = re.compile(r"^menu-poemes-par-theme$")
        xml_themes = Segmenter.import_xml(
            segmentation=seg_themes,
            element="<ul>",
            conditions=condition_themes,
        )

        # Recuperer le lien url vers la page de chaque auteur...
        xml_par_auteur = Segmenter.import_xml(
            segmentation=xml_auteurs,
            element="<a>",
        )

        # Recuperer le lien url vers la page de chaque theme...
        xml_par_theme = Segmenter.import_xml(
            segmentation=xml_themes,
            element="<a>",
        )

        # Acceder a la page de chaque auteur...
        for auteur in xml_par_auteur:
            try:
                url_page_auteur = auteur.annotations["href"]
                url_auteur = urlopen(url_page_auteur)
                page_auteur = url_auteur.read()
                print("Valid author's URL")
                page_auteur = page_auteur.decode("utf-8")

                # Recuperer le nom de l'auteur.
                nom_auteur = auteur.get_content()
                #print(nom_auteur)

        #print(xml_par_auteur.to_string())
        #nom_auteur = auteur.get_content()
            

                # Extraire la liste de poemes...
                seg_auteurs = Input(page_auteur)
                condition_auteur = dict()
                condition_auteur["class"]=re.compile(r"^entry-header$")
                xml_poemes = Segmenter.import_xml(
                    segmentation=seg_auteurs,
                    element="<header>",
                    conditions=condition_auteur,
                )

                # Recuperer le lien url vers la page de chaque poeme...
                xml_par_poeme = Segmenter.import_xml(
                    segmentation=xml_poemes,
                    element="<a>",
                )

                # Acceder a la page de chaque poeme...
                for poeme in xml_par_poeme:
                    try:
                        url_page_poeme = poeme.annotations["href"]
                        url_poeme = urlopen(url_page_poeme)
                        page_poeme = url_poeme.read()
                        print("Valid poem's URL")
                        page_poeme = page_poeme.decode("utf-8")

                        # Recuperer le nom du poeme.
                        nom_poeme = poeme.get_content()
                        #print(nom_poeme)
                
                        # Extraire les poeme et ses donnees...
                        #seg_poemes = Input(page_poeme)
                        #condition_poeme = dict()
                        #condition_poeme["class"]=re.compile(r"^entry-content$")
                        #xml_contenu_poeme = Segmenter.import_xml(
                        #    segmentation=seg_poemes,
                        #    element="<div>",
                        #    conditions=condition_poeme,
                        #)

                        # Recuperer le poeme avec ses propres balises.
                        #poeme_balises = xml_contenu_poeme[0].get_content()

                        # Recuperer et associer la date de parution du poeme si elle est connue...
                        #regex_date = re.compile(r"(1|2)\d{3}")
                        #date_poeme_intermediaire = regex_date.search(poeme_balises)
                        #if date_poeme_intermediaire == None:
                        #    date_poeme = str(date_poeme_intermediaire)
                        #else:
                        #    date_poeme = str(date_poeme_intermediaire.group())
                        #print(date_poeme)

                        # N'afficher que le contenu du poeme...
                        #poeme = re.sub(r"((</?p.*?>)|(<br />))|(<em>.*</em>)|(</p>)", "", poeme_balises)
                        #poeme = re.sub(r".+$", "", poeme)
                        #print(poeme)
                        database["title"][url_page_poeme] = nom_poeme
                        database["author"][url_page_poeme] = nom_auteur
                        #database["date"][url_page_poeme] = date_poeme
                        #database["poem"][url_page_poeme] = poeme

                    # Avertir si l'url ne fonctionne pas...
                    except IOError:
                        print("Invalid poem's URL")

            # Avertir si l'url ne fonctionne pas...
            except IOError:
                print("Invalid author's URL")

        # Acceder a la page de chaque theme...
        for theme in xml_par_theme:
            try:
                url_page_theme = theme.annotations["href"]
                url_theme = urlopen(url_page_theme)
                page_theme = url_theme.read()
                print("Valid topic's URL")
                page_theme = page_theme.decode("utf-8")

                # Recuperer le nom de l'auteur.
                nom_theme = theme.get_content()
                # print(nom_auteur)

                # print(xml_par_auteur.to_string())
                # nom_auteur = auteur.get_content()

                # Extraire la liste de poemes...
                seg_themes = Input(page_theme)
                condition_themes = dict()
                condition_themes["class"] = re.compile(r"^entry-header$")
                xml_poemes_themes = Segmenter.import_xml(
                    segmentation=seg_themes,
                    element="<header>",
                    conditions=condition_themes,
                )

                # Recuperer le lien url vers la page de chaque poeme...
                xml_par_theme = Segmenter.import_xml(
                    segmentation=xml_poemes_themes,
                    element="<a>",
                )

                # Acceder a la page de chaque poeme...
                for poeme_theme in xml_par_theme:
                    try:
                        url_page_poeme_theme = poeme_theme.annotations["href"]
                        #url_poeme_theme = urlopen(url_page_poeme_theme)
                        #page_poeme_theme = url_poeme_theme.read()
                        #print("Valid poem's URL")
                        #page_poeme_theme = page_poeme_theme.decode("utf-8")

                        database["topic"][url_page_poeme_theme] = nom_theme
                        # database["poem"][url_page_poeme] = poeme
                        print(nom_theme)
                        print(database["topic"])

                    # Avertir si l'url ne fonctionne pas...
                    except IOError:
                        print("Invalid poem's URL")

            # Avertir si l'url ne fonctionne pas...
            except IOError:
                print("Invalid topic's URL")

    # Avertir si l'url ne fonctionne pas...
    except IOError:
        print("Invalid poetica's URL")

    #print(database)

    path = os.path.dirname(
        os.path.abspath(inspect.getfile(inspect.currentframe()))
    )
    try:
        file = open(os.path.join(path, "poetica_cache.p"), "wb")
        pickle.dump(database, file)
        print('The dictionary has successfully been saved to the file')
        file.close()
    except IOError:
        print("Can't save the dictionary")

    try:
        file = open(os.path.join(path, "poetica_cache.p"), "rb")
        new_database = pickle.load(file)
        #print(new_database)
        print("Dictionary correctly loaded")
        print(new_database)
        file.close()
    except IOError:
        print("Can't load the dictionary")

    #print(new_database)
    #print(new_database["author"])
    #for key_author, value_author in new_database["author"].items():
    #    print(f"Key : {key_author} and Value : {value_author}")
    #    for key_title, value_title in new_database["title"].items():
    #        for key_poem, value_poem in new_database["poem"].items():
    #            if key_title == key_author and key_title == key_poem:
    #                print(f"The poem '{value_title}' has been written by {value_author} : {value_poem}")

if __name__=="__main__":
    main()
