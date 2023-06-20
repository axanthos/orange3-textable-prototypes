import pickle

database = {
    "author": {
        "https://www.poetica.fr/poeme-726/louise-ackermann-a-alfred-de-musset/": "Louise Ackermann",
        "https://www.poetica.fr/poeme-3961/louise-ackermann-a-une-artiste/": "Louise Ackermann",
        "https://www.poetica.fr/poeme-623/arthur-rimbaud-a-la-musique/": "Arthur Rimbaud",
        "https://www.poetica.fr/poeme-1990/arthur-rimbaud-accroupissements/": "Arthur Rimbaud",
        "https://www.poetica.fr/poeme-1910/voltaire-a-la-marquise-du-chatelet/": "Voltaire",
        "https://www.poetica.fr/poeme-1911/voltaire-a-m-le-duc-de-la-feuillade/": "Voltaire",
    },
    "content": {
        "https://www.poetica.fr/poeme-726/louise-ackermann-a-alfred-de-musset/": "Louise Ackermann",
        "https://www.poetica.fr/poeme-3961/louise-ackermann-a-une-artiste/": "Louise Ackermann",
        "https://www.poetica.fr/poeme-623/arthur-rimbaud-a-la-musique/": "Arthur Rimbaud",
        "https://www.poetica.fr/poeme-1990/arthur-rimbaud-accroupissements/": "Arthur Rimbaud",
        "https://www.poetica.fr/poeme-1910/voltaire-a-la-marquise-du-chatelet/": "Voltaire",
        "https://www.poetica.fr/poeme-1911/voltaire-a-m-le-duc-de-la-feuillade/": "Voltaire",
    },
print('Poem dictionary')
print(database)

# save dictionary to person_data.pkl file
with open('database_data.pkl', 'rb') as fp:
    pickle.dump(database, fp)
    print('dictionary saved successfully to file')
    pickle.load(database)
}

pickle.dump(mydict, open('pickle_file_name.p', 'wb'))