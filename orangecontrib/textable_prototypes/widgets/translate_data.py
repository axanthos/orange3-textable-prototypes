
"""TO BE DELETED EVENTUALLY !!!!!!!!!"""


import deep_translator as dt
import json
langs_dict = dt.MyMemoryTranslator(source="ace-ID",target="hr-HR").get_supported_languages(as_dict=True)
bigger_dict = dict()
bigger_dict["MyMemoryTranslator"] = langs_dict
print(bigger_dict)
with open('orangecontrib\\textable_prototypes\widgets\\translate_data.json', 'w') as f:
    json.dump(bigger_dict, f)

