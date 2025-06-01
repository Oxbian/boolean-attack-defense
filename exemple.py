import json

from attacker import FaultyCircuit
from circuit import LogicCircuit, LogicGate, check_circuits

# Lire les config depuis le fichier json
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Création d’un circuit : (A AND B) → OUT
circuit = LogicCircuit()

# Création de porte logique
circuit.add_gate(LogicGate("INPUT", "A"))
circuit.add_gate(LogicGate("INPUT", "B"))
circuit.add_gate(LogicGate("AND", "AND1"))
circuit.add_gate(LogicGate("NOT", "NOT1"))
circuit.add_gate(LogicGate("OUTPUT", "OUT"))

# Ajout de connexions entre les portes logiques
circuit.connect("A", "AND1")
circuit.connect("B", "AND1")
circuit.connect("AND1", "NOT1")
circuit.connect("NOT1", "OUT")

# Évaluation
print(circuit.evaluate({"A": True, "B": False}))  # {'OUT': True}
circuit.visualize()
circuit.export_to_blif("notafter.blif", "notafter")

# Création d'un second circuit pour comparer
circuit2 = LogicCircuit()
circuit2.add_gate(LogicGate("INPUT", "A"))
circuit2.add_gate(LogicGate("INPUT", "B"))
circuit2.add_gate(LogicGate("NOT", "NOTA"))
circuit2.add_gate(LogicGate("NOT", "NOTB"))
circuit2.add_gate(LogicGate("OR", "OR1"))
circuit2.add_gate(LogicGate("OUTPUT", "OUT"))

circuit2.connect("A", "NOTA")
circuit2.connect("B", "NOTB")
circuit2.connect("NOTA", "OR1")
circuit2.connect("NOTB", "OR1")
circuit2.connect("OR1", "OUT")
print(circuit.evaluate({"A": True, "B": False}))  # {'OUT': True}
circuit2.visualize()
circuit2.export_to_blif("notfirst.blif", "notfirst")

# Création d'un troisième circuit pour comparer
circuit3 = LogicCircuit()
circuit3.add_gate(LogicGate("INPUT", "A"))
circuit3.add_gate(LogicGate("INPUT", "B"))
circuit3.add_gate(LogicGate("NOT", "NOTA"))
circuit3.add_gate(LogicGate("OR", "OR1"))
circuit3.add_gate(LogicGate("OUTPUT", "OUT"))

circuit3.connect("A", "NOTA")
circuit3.connect("B", "OR1")
circuit3.connect("NOTA", "OR1")
circuit3.connect("OR1", "OUT")
circuit3.visualize()
circuit3.export_to_blif("ortest.blif", "ortest")

# Comparaison des deux circuits avec ABC
equiv = check_circuits("notafter.blif", "notfirst.blif", config["abc_path"])
if equiv:
    print("Circuit équivalent")
else:
    print("Circuit différents")

equiv2 = check_circuits("notafter.blif", "ortest.blif", config["abc_path"])
if equiv2:
    print("Circuit équivalent")
else:
    print("Circuit différents")

# Création d'un circuit fautif
faulty_circuit = FaultyCircuit(circuit)

faulty_circuit.add_fault("AND1", "bitflip")
print(faulty_circuit.evaluate({"A": True, "B": False}))  # {'OUT': False}
faulty_circuit.visualize()
