import matplotlib.pyplot as plt
import networkx as nx

from .colors import bcolors
from .logic_gate import LogicGate


class LogicCircuit:
    """Classe pour le circuit booléen, basé sur les graphes orientée acyclique.
    Les arrêtes vont dans le sens de l'information, des entrées (inputs) vers la
    sortie (output), car les noeuds sans prédécesseurs sont évalués en premiers
    (souvent les inputs)"""

    def __init__(self):
        """Initialisation du circuit booléen, créer un graphe orientée
        acyclique"""
        self.graph = nx.DiGraph()

    def add_gate(self, gate: LogicGate):
        """Ajoute une porte logique au circuit
        @param gate: Porte logique à ajouté au circuit
        """
        self.graph.add_node(gate.gate_id, gate=gate)

    def connect(self, from_id: str, to_id: str):
        """Connecte deux noeuds / portes logiques, ex: C a pour entrée A et B
        @param from_id: Identifiant de la porte d'origine, ex: A -> C, B->C,
        donc A ou B
        @param to_id: Identifiant de la porte de destination, ex: C
        """

        # Vérification de l'existance des noeuds
        if not self.graph.has_node(from_id) or not self.graph.has_node(to_id):
            raise ValueError(
                f"{bcolors.WARNING}Identifiant de la porte logique non existant")

        self.graph.add_edge(from_id, to_id)

    def remove_gate(self, gate_id: str) -> bool:
        """Supprimer une porte logique du graphe
        @param gate_id: Identifiant de la porte à supprimé

        @return: Booléen indiquant la réussite de la suppression ou non
        """

        # Vérification de l'existence du noeud
        if not self.graph.has_node(gate_id):
            raise ValueError(
                f"{bcolors.WARNING}Identifiant de la porte à supprimé non présent dans le graphe")

        # Sauvegarde du graphe avant la suppression pour pouvoir backup
        bk = self.graph.copy()
        self.graph.remove_node(gate_id)

        if not self.is_valid():
            self.graph = bk
            return False

        return True

    def disconnect(self, from_id: str, to_id: str):
        """Déconnecter deux portes logiques, ex: C a pour entrée A et B
        @param from_id: Identifiant de la porte d'origine, ex: A -> C, B->C,
        donc A ou B
        @param to_id: Identifiant de la porte de destination, ex: C
        """
        self.graph.remove_edge(from_id, to_id)

    def is_valid(self) -> bool:
        """Vérification que le circuit est correct
        Input et output bien liées, chaque porte à assez d'entrées

        @return: Booléen de la validité du graphe
        """

        for node in self.graph.nodes:
            gate = self.graph.nodes[node]["gate"]
            preds = list(self.graph.predecessors(node))

            # Vérification que les noeuds ont bien assez d'entrées
            if gate.gate_type in {"NOT", "OUTPUT"} and len(preds) != 1:
                return False
            if gate.gate_type in {"AND", "OR", "XOR", "NAND", "NOR", "XNOR"} and len(preds) < 2:
                return False

            # Vérifie que chaque OUTPUT est atteignable depuis au moins un INPUT
            inputs = [n for n in self.graph.nodes if self.graph.nodes[n]
                      ["gate"].gate_type == "INPUT"]
            outputs = [n for n in self.graph.nodes if self.graph.nodes[n]
                       ["gate"].gate_type == "OUTPUT"]

            for output in outputs:
                reachable = any(nx.has_path(self.graph, src, output)
                                for src in inputs)
                if not reachable:
                    return False
        return True

    def evaluate(self, input_values: dict[str, bool]) -> dict[str, bool]:
        """Calcul le résultat du circuit booléen
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

        # Retourne uniquement les sorties
        outputs = {
            gate_id: val
            for gate_id, val in values.items()
            if self.graph.nodes[gate_id]["gate"].gate_type == "OUTPUT"
        }
        return outputs

    def visualize(self):
        """Affiche graphiquement le circuit"""

        labels = {}
        node_colors = []

        for node in self.graph.nodes:
            gate = self.graph.nodes[node]["gate"]
            labels[node] = f"{gate.gate_id} : {gate.gate_type}"

            # Colorations des noeuds selon leur type
            if gate.gate_type == "INPUT":
                node_colors.append("green")
            elif gate.gate_type == "OUTPUT":
                node_colors.append("yellow")
            else:
                node_colors.append("lightblue")

        nx.draw(self.graph, labels=labels, with_labels=True,
                node_size=1500, node_color=node_colors)

        plt.title("Visualisation du circuit logique")
        plt.show()
