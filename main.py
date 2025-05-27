from circuit import LogicCircuit, LogicGate

# Création d’un circuit : (A AND B) → OUT
circuit = LogicCircuit()

# Création de porte logique
g1 = LogicGate("INPUT", "A")
g2 = LogicGate("INPUT", "B")
g3 = LogicGate("AND", "AND1")
g4 = LogicGate("OUTPUT", "OUT")

# Ajout au circuit
for g in [g1, g2, g3, g4]:
    circuit.add_gate(g)

# Ajout de connexions entre les portes logiques
circuit.connect("A", "AND1")
circuit.connect("B", "AND1")
circuit.connect("AND1", "OUT")

# Évaluation
print(circuit.evaluate({"A": True, "B": False}))  # {'OUT': False}
circuit.visualize()
