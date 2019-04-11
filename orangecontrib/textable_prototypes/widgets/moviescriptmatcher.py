from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#Dictionary will include all the movies from springfieldspringfield website
testdict = {
	"Die Hard (1988)": "die-hard",
	"Watchmen (2009)": "watchmen",
	"Back to the Future (1985)": "back-to-the-future",
	"Die Hard 2": "die-hard-2",
}

#The first attribute of extract will be user's input, second is the list of all movie scripts, third is number of results determined by user
print(process.extractBests("Die Hard", testdict, limit=3, score_cutoff=70))
