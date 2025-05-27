# Boolean circuit attack & defense
---

Le but de ce projet est de créer deux modèles d'apprentissage par renforcement
qui auront pour objectif de faire un circuit booléen le plus efficace et
résistant possible aux attaques.

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
