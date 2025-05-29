import matplotlib.pyplot as plt
import networkx as nx
from circuit import LogicCircuit, LogicGate, bcolors


class FaultyCircuit(LogicCircuit):
    """Classe pour définir un circuit booléen avec des fautes,
    capable des mêmes fonctionnalités que le circuit booléen classique
    """

    def __init__(self, circuit):
        """Initialise le circuit booléen fautif avec un circuit booléen déjà
        construit"""
        self.graph = circuit.graph
        self.faults = {}

    def add_fault(self, gate_id: str, fault_type: str, stuck_value: bool = None):
        """Ajouter une faute au circuit sur la porte logique spécifié
        Il existe deux types de fautes:
        - le bitflip "bitflip", qui va inverser la sortie de la porte logique
        - le stuck-at-default "stuck", qui va fixer la sortie

        @param gate_id: Identifiant de la porte logique à mettre en faute
        @param fault_type: Type de faute
        @param value: Valeur a mettre pour la faute de type stuck
        """
        if not self.graph.has_node(gate_id):
            raise ValueError(
                f"{bcolors.WARNING}Identifiant de la porte logique non existant")

        assert fault_type in {"bitflip", "stuck"}

        self.faults[gate_id] = (fault_type, stuck_value)

    def remove_fault(self, gate_id: str):
        """Supprime une faute du circuit sur la porte logique spécifiée
        @param gate_id: Identifiant de la porte logique où la faute doit être
        retirée
        """
        if not self.graph.has_node(gate_id):
            raise ValueError(
                f"{bcolors.WARNING}Identifiant de la porte logique non existant")

        del self.faults[gate_id]

    def clear_faults(self):
        """Supprime toutes les fautes du circuit"""
        self.faults = {}

    def evaluate(self, input_values: dict[str, bool]) -> dict[str, bool]:
        """Calcul le résultat du circuit booléen fautif
        @param input_values: Dictionnaire indiquant les valeurs logiques des inputs

        @return: Dictionnaire contenant les résultats logiques des outputs
        """

        # Stocke les résultats intermédiaires
        values = {}

        # Tri topologique pour respecter l'ordre logique (chaque noeud est
        # évalué après ses prédécesseurs, donc les inputs en premiers)
        order = list(nx.topological_sort(self.graph))

        for gate_id in order:
            # Récupération du noeud et de ses prédecesseurs
            gate: LogicGate = self.graph.nodes[gate_id]["gate"]
            preds = list(self.graph.predecessors(gate_id))

            if gate.gate_type == "INPUT":
                if gate_id not in input_values:
                    raise ValueError(
                        f"{bcolors.WARNING}Pas d'input pour la porte logique: {gate_id}")
                values[gate_id] = input_values[gate_id]

            elif gate.gate_type == "OUTPUT":
                # OUTPUT: on transmet juste la valeur du seul prédécesseur
                if len(preds) != 1:
                    raise ValueError(
                        f"{bcolors.WARNING}Porte logique OUTPUT doit avoir un seul prédécesseur")
                values[gate_id] = values[preds[0]]

            else:
                input_vals = [values[pred] for pred in preds]
                values[gate_id] = gate.compute(input_vals)

            if gate_id in self.faults:
                ftype, fval = self.faults[gate_id]
                if ftype == "bitflip":
                    values[gate_id] = not values[gate_id]
                elif ftype == "stuck":
                    values[gate_id] = fval

        # Retourne uniquement les sorties
        outputs = {
            gate_id: val
            for gate_id, val in values.items()
            if self.graph.nodes[gate_id]["gate"].gate_type == "OUTPUT"
        }
        return outputs

    def visualize(self):
        """Affiche graphiquement le circuit avec les fautes en rouge"""

        labels = {}
        node_colors = []

        for node in self.graph.nodes:
            gate = self.graph.nodes[node]["gate"]
            labels[node] = f"{gate.gate_id} : {gate.gate_type}"

            # Couleur rouge si le nœud a une faute, bleu sinon
            if node in self.faults:
                node_colors.append("red")
            elif gate.gate_type == "INPUT":
                node_colors.append("green")
            elif gate.gate_type == "OUTPUT":
                node_colors.append("yellow")
            else:
                node_colors.append("lightblue")

        # Ou shell_layout, graphviz_layout, etc.
        nx.draw(self.graph, labels=labels, with_labels=True,
                node_size=1500, node_color=node_colors)

        plt.title("Visualisation du circuit logique (nœuds fautifs en rouge)")
        plt.axis("off")
        plt.show()
