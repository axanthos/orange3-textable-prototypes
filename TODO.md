### SCRAPODON | Table de référence
---

CONVENTIONS 

Pour ce qui est de l'interface utilisateur, nommer les différents bacs pour faciliter la formulation de l'interface.

API[KEY:STR] - Comme défini 

MODE[KEY:MODE] - Comme défini 

TARGET[KEY:STR] - Comme défini

QUERY ATTRIBUTES [EXCLUDE-REPOSTS:BOOL,ONLY-REPOSTS:BOOL,EXCLUDE-IMAGES:BOOL,ONLY-REPOSTS:BOOL] 

ADDITION THRESHOLDS[T-REPOSTS:INT,T-LIKE:INT] 

Q: Faut il regrouper les discriminants existentiels et les numériques sachant qu'il existe des dépendances mutuelles entre les types, le tout par souci de lisibilité et d'ergonomie ? Et quand nous parlons des reposts à exclure ou à uniquement inclure. Il s'agit alors bien d'exclure et d'inclure uniqement des documents ayant ces caractéristiques ou s'agit il d'ajouter leurs contenus également ?

---

DONNEE TYPE

[TARGET:STR,CONTENT:STR,hasREPOSTS:BOOL,nREPOSTS:INT,hasLIKES:BOOL,nLIKES:INT,nREPOSTS:INT,hasIMAGE,refIMAGE:STR]

Il s'agit ici de formuler le dict qui stockera l'information fournie par l'api sous ses différentes formes. TARGET est ici l'utilisateur/serveur/fédération, conservé par souci de réutilisabilité. L'on résout alors le problème de la classifictioncar il devient possible d'effectuer les opérations logiques nécessaires à la discrimination de l'information transmise à la ségmentation sans regex. S'agit d'un processus en deux temps, POPULATION de la DICT et ENVOI de la segmentation.

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










