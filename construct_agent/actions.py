import random
from circuit import LogicGate

def add_random_gate(circuit):
    gate_type = random.choice(["AND", "OR", "XOR", "NOT", "NAND", "NOR", "XNOR"])
    gate = LogicGate(gate_type)
    circuit.add_gate(gate)
    nodes = list(circuit.graph.nodes)
    if len(nodes) >= 2:
        from_id = random.choice(nodes)
        circuit.connect(from_id, gate.gate_id)
        to_id = random.choice(nodes)
        circuit.connect(gate.gate_id, to_id)

def remove_random_gate(circuit):
    candidates = [n for n in circuit.graph.nodes if circuit.graph.nodes[n]['gate'].gate_type not in ["INPUT", "OUTPUT"]]
    if len(candidates) > 1:
        circuit.remove_gate(random.choice(candidates))

def add_random_connection(circuit):
    nodes = list(circuit.graph.nodes)
    if len(nodes) >= 2:
        from_id, to_id = random.sample(nodes, 2)
        try:
            circuit.connect(from_id, to_id)
        except:
            pass

def remove_random_connection(circuit):
    if circuit.graph.number_of_edges() > 2:
        edges = list(circuit.graph.edges)
        from_id, to_id = random.choice(edges)
        circuit.disconnect(from_id, to_id)

def change_random_gate(circuit):
    candidates = [n for n in circuit.graph.nodes if circuit.graph.nodes[n]['gate'].gate_type not in ["INPUT", "OUTPUT"]]
    if candidates:
        gate_id = random.choice(candidates)
        new_type = random.choice(["AND", "OR", "XOR", "NOT", "NAND", "NOR", "XNOR"])
        circuit.graph.nodes[gate_id]['gate'].gate_type = new_type
