
"""TO BE DELETED EVENTUALLY !!!!!!!!!"""


from deep_translator import (GoogleTranslator,
                             ChatGptTranslator,
                             MicrosoftTranslator,
                             PonsTranslator,
                             LingueeTranslator,
                             MyMemoryTranslator,
                             YandexTranslator,
                             PapagoTranslator,
                             DeeplTranslator,
                             QcriTranslator,
                             single_detection,
                             batch_detection)
import json

langs_dict = dict()
#google translator:
google_dict = {
    "name": "Google Translate",
    "api": False,
    "lang": GoogleTranslator().get_supported_languages(as_dict=True)
}
langs_dict["GoogleTranslator"] = google_dict

#MyMemory Translator
mymemory_dict = {
    "name": "MyMemory Translator",
    "api": False,
    "lang": MyMemoryTranslator(source="auto", target="hr-HR").get_supported_languages(as_dict=True)
}
langs_dict["MyMemory"] = mymemory_dict

#DeepL Translator
deepl_dict = {
    "name": "DeepL Translator",
    "api": True,
    "lang": DeeplTranslator(api_key="4411c800-3281-42ff-8940-acccfb640a72:fx").get_supported_languages(as_dict=True)
}
langs_dict["DeepL"] = deepl_dict

#Qcri Translator
qcri_dict = {
    "name": "Qcri Translator",
    "api": True,
    "lang": QcriTranslator(api_key="29007d2cbaa9a744cfbf42611b27a75c").get_supported_languages(as_dict=True)
}
langs_dict["Qcri"] = qcri_dict

#Linguee Translator
linguee_dict = {
    "name": "Linguee Translator",
    "api": False,
    "lang": LingueeTranslator(source="english", target="german").get_supported_languages(as_dict=True)
}
langs_dict["Linguee"] = linguee_dict

#Pons Translator
pons_dict = {
    "name": "Pons Translator",
    "api": False,
    "lang": PonsTranslator(source='english', target='french').get_supported_languages(as_dict=True)
}
langs_dict["Pons"] = pons_dict
print(pons_dict)



with open('orangecontrib\\textable_prototypes\widgets\\translate_data.json', 'w') as f:
    json.dump(langs_dict, f)

