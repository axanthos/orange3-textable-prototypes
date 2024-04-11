### SCRAPODON | Table de référence
---

CONVENTIONS 

Pour ce qui est de l'interface utilisateur, nommer les différents bacs pour faciliter la formulation de l'interface.

API[KEY:STR] - Comme défini 

MODE[KEY:MODE] - Comme défini 

TARGET[KEY:STR] - Comme défini

QUERY ATTRIBUTES [EXCLUDE-REPOSTS:BOOL,ONLY-REPOSTS:BOOL,EXCLUDE-IMAGES:BOOL,ONLY-REPOSTS:BOOL] 

ADDITION THRESHOLDS[T-REPOSTS:INT,T-LIKE:INT] 

---

DONNEE TYPE

[TARGET:STR,CONTENT:STR,hasREPOSTS:BOOL,nREPOSTS:INT,hasLIKES:BOOL,nLIKES:INT,nREPOSTS:INT,hasIMAGE,refIMAGE:STR]


Q!!: Serait il intéressant d'appondre une fonction de cache avec un historique des dernières recherches dirigées dans ? Histoire de conserver dans la mémoire du widget lui même différentes recherches ? Si oui, CSV / Dict, quel moyen utiliser pour rendre l'objet facile.

---

PARAMETRES TYPES T

Parameters:
        m (string): Stands for 'mode', defines which mode the query will use
        aPI (string): Stands for 'API', defines the key used for private message access.
        tAR (string): Stands for 'Target', defines the key used to identify the target, type specified by m the 'mode'
        rE (string): Stands for 'Exclude reposts', defines
        rO (string): Stands for 'Reposts only', defines
        rON (string): Stands for 'Reposts threshold', defines 
        iEX (string): Stands for 'Exclude Images', defines
        iWI (string): Stands for 'With Images, defines
        tL (string): Stands for 'Threshold Likes', defines a numerical value of the key pair value nLIKES, under which the given post will not be added to the output segmentation.
        

Q: Si vous pouvez expliciter les fonctions des différents paramètes histoire de ne plus avoir d'ambiguité. Si vous le faite en logique formelle, vous êtes des crèmes.s

## TODO [SAMUEL] [ROSE] [OLIVIER] [LAURE] [DIMETRA]
---

FRONT END

- [ ] Version finale de l'interface ratifiée [EN COURS 11.04.24]
- [ ] Implémentation fonctionelle des éléments d'interface dans le code [OLIVIER][LAURE]

BACK END

REGLAGES

- [ ] Sélection fonctionnelle du mode d'interaction [SAMUEL]
- [ ] CACHE et étapes intermédiaires [ROSE]

    POPULATION DE LA DICT

    - [ ] RUNTIME et TIMEOUT [DIMITRA]


    ENVOI DE LA SEGMENTATION

    - [ ] TBD


GROSSE QUESTION A RESOUDRE:

Les choix tels que je les ai décrits ici partent du principe d'une récupération d'un modèle de donnée standardisé depuis l'api mastodon, modulée par des réglages au niveau de l'envoi de la segmentation, sommes nous bien d'accord sur ce point ?







