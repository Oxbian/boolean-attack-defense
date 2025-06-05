import copy
import os
import random
import tempfile

import networkx as nx
from circuit import LogicCircuit, LogicGate, check_circuits


class LogicCircuitOptimizer:
    """Algorithme génétique pour la construction et le renforcement de circuits
    booléens.
    Cet algorithme est capable d'ajouter, supprimer ou connecter des portes
    logiques afin de renforcer un circuit avec équivalence à un circuit cible
    face à différentes attaques réalisées par un attaquant
    """

    def __init__(self, target_filepath: str, abc_path: str, max_gates: int = 20,
                 population_size: int = 20):
        """
        Initialise l'algorithme génétique

        @param target_filepath: Chemin vers le fichier .blif du circuit cible
        @param abc_path: Chemin vers l'executable ABC
        @param max_gates: Nombre maximal de portes logiques dans le circuit
        @param population_size: Taille d'initialisation du circuit génétique
        """
        self.target_filepath = target_filepath
        self.abc_path = abc_path
        self.max_gates = max_gates
        self.population_size = population_size
        self.available_gates = ["AND", "OR",
                                "XOR", "NOT", "NAND", "NOR", "XNOR"]

    def initialize_population(self) -> list[LogicCircuit]:
        """
        Initialise la population pour l'algo génétique

        @return: Une liste de circuit logique pour tester l'algorithme
        """

        population = []
        for _ in range(self.population_size):
            # Initialisation d'un circuit logique de base
            circuit = LogicCircuit()

            circuit.add_gate(LogicGate("INPUT", "A"))
            circuit.add_gate(LogicGate("INPUT", "B"))
            circuit.add_gate(LogicGate("AND", "G1"))
            circuit.add_gate(LogicGate("OUTPUT", "OUT"))

            circuit.connect("A", "G1")
            circuit.connect("B", "G1")
            circuit.connect("G1", "OUT")
            population.append(circuit)
        return population

    def mutate(self, circuit: LogicCircuit) -> LogicCircuit:
        """Apporte des modifications sur la population

        @param LogicCircuit: Circuit logique à modifié

        @return: Circuit logique avec les modifications réalisées
        """

        new_circuit = copy.deepcopy(circuit)
        mutation_type = random.choice(
            ["add_gate", "remove_gate", "connect", "disconnect"])
        nodes = list(new_circuit.graph.nodes)

        try:
            if mutation_type == "add_gate":
                gate_type = random.choice(self.available_gates)
                new_gate = LogicGate(gate_type)
                new_circuit.add_gate(new_gate)

                # Connexion aléatoire à une source et une cible
                nodes = list(new_circuit.graph.nodes)
                inputs = [
                    n for n in nodes if new_circuit.graph.out_degree(n) > 0]
                outputs = [
                    n for n in nodes if new_circuit.graph.in_degree(n) > 0]

                if inputs:
                    src = random.choice(inputs)
                    if not nx.has_path(new_circuit.graph, new_gate.gate_id, src):
                        new_circuit.connect(src, new_gate.gate_id)

                    if outputs:
                        tgt = random.choice(outputs)
                        if not nx.has_path(new_circuit.graph, tgt, new_gate.gate_id):
                            new_circuit.connect(new_gate.gate_id, tgt)

            elif mutation_type == "remove_gate" and len(nodes) > 3:
                to_remove = random.choice(nodes)
                if new_circuit.graph.nodes[to_remove]["gate"].gate_type not in {"INPUT", "OUTPUT"}:
                    new_circuit.remove_gate(to_remove)

            elif mutation_type == "connect" and len(nodes) >= 2:
                src, tgt = random.sample(nodes, 2)

                if not nx.has_path(new_circuit.graph, tgt, src):
                    new_circuit.connect(src, tgt)

            elif mutation_type == "disconnect" and new_circuit.graph.number_of_edges() > 0:
                edges = list(new_circuit.graph.edges)
                edge = random.choice(edges)
                new_circuit.disconnect(edge[0], edge[1])
        except Exception:
            pass  # Ignore invalid mutations

        return new_circuit

    def compute_fitness(self, circuit: LogicCircuit) -> float:
        """Calcul à quel point le circuit est bon ou non
        """

        try:
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=".blif")
            os.close(tmp_fd)
            circuit.export_to_blif(tmp_path, "tmp")
            is_equivalent = check_circuits(
                tmp_path, self.target_filepath, self.abc_path)
            os.remove(tmp_path)

            if not is_equivalent:
                return 0
        except Exception:
            return 0

        return 1

    def evolve(self, generations=50):
        """
        Fais évoluer une population sur n générations
        """
        population = self.initialize_population()

        for gen in range(generations):
            scored = [(self.compute_fitness(ind), ind) for ind in population]
            scored.sort(reverse=True, key=lambda x: x[0])

            print(f"Génération {gen+1}: meilleur score = {scored[0][0]:.2f}")

            # Sélection des top_k pour les reproduires
            top_k = scored[:self.population_size // 2]
            parents = [ind for _, ind in top_k]

            # Mutation des parents
            offspring = [self.mutate(parent) for parent in parents]
            population = parents + offspring

        return scored[0][1]  # Retourne le meilleur circuit final
