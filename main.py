import json

from attacker import FaultyCircuit
from circuit import LogicCircuit, LogicGate, check_circuits

# Lire les config depuis le fichier json
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Utilisation du constructeur pour créer le circuit
