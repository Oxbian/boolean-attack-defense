# Boolean circuit attack & defense
---

Le but de ce projet est de créer deux modèles d'apprentissage par renforcement
qui auront pour objectif de faire un circuit booléen le plus efficace et
résistant possible aux attaques, en utilisant possiblement des techniques
d'offuscation.

Pour cela deux modèles seront créer:
- Le constructeur, qui devra créer un circuit robuste
- L'attaquant, qui devra faire des attaques sur le circuit booléen

## Installation

> [!CAUTION]
> Recommandation d'utiliser un environnement virtuel

Pour créer l'environnement virtuel:

```bash
python3 -m venv .venv
```

Puis pour installer les dépendances dans l'environnement virtuel:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Pour l'utilisation du programme:

```bash
.venv/bin/python3 main.py
```

La vérification formelle de l'égalité de deux circuits se faisant avec l'utilitaire
[abc](https://github.com/berkeley-abc/abc), son installation est nécessaire.

## Utilisation

Les différents programmes ont besoin d'avoir accès à un fichier de configuration
`config.json` contenant le chemin vers l'executable ABC.  
  
Le programme `main.py` à besoin d'un circuit de comparaison afin d'entrainer le
modèle, ce circuit doit être défini dans le fichier de configuration
`config.json`.  
Des circuits peuvent être générer grâce au programme `exemple.py`, qui permet 
de comprendre le fonctionnement de ce projet, ainsi que de vérifier le
fonctionnement de l'outil de vérification formelle ABC.

## Démonstration

**Évolution de la création de circuits booléens par le constructeur :**

