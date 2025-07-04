import os
import tempfile

import gymnasium as gym
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from circuit import LogicCircuit, LogicGate, check_circuits
import networkx as nx


class LogicCircuitEnv(gym.Env):
    """Environnement Gym pour la construction de circuits booléens.
    L'agent peut ajouter, supprimer ou connecter des portes pour tenter de
    rendre un circuit équivalent en fonctionnalités à un circuit cible,
    même en présence de fautes injectées par un attaquant.
    """

    def __init__(self, target_filepath: str, abc_path: str,
                 render_mode: str | None = None):
        """
        Initialise l'environnement de construction de circuits

        @param target_circuit_path: Chemin vers le fichier .blif du circuit cible
        @param abc_path: Chemin vers l'exécutable ABC
        """
        # Informations pour l'environnement Gymnasium
        super().__init__()
        self.metadata['render_modes'] = ['rgb_array', 'human']
        self.render_mode = render_mode
        
        # Nombre d'étapes avant truncated (permet d'optimiser l'enregistrement
        # des vidéos de rendu)
        self.max_steps = 500
        self.current_steps = 0

        self.target_filepath = target_filepath
        self.abc_path = abc_path

        self.circuit = LogicCircuit()
        self.faulty_circuit = None

        self.available_gates = ["AND", "OR",
                                "XOR", "NOT", "NAND", "NOR", "XNOR"]

        # Explication du action_space:
        # le 1er est le type de l'action, 0: ajouter une porte, 1: supprimer
        # une porte, 2: ajouter une connexion, 3: supprimer une connexion
        # le 2nd est le choix de la porte (utile que pour l'action d'ajout)
        # le 3e et 4e c'est l'id encodée de la porte (0 à max gates)

        self.max_gates = 20

        # Définition d'un nombre d'actions possibles max car l'action space
        # doit être constant mais le nombre d'action possible est dynamique,
        # d'où l'utilisation du masque
        self.max_actions = 4 * len(self.available_gates) * \
            self.max_gates * self.max_gates

        self.action_space = gym.spaces.Discrete(self.max_actions)

        # Définition d'une matrice max_gates * (nombre type + connexions) pour
        # enregistrer l'état du circuit
        self.observation_space = gym.spaces.Box(
            low=0,
            high=1,
            shape=(self.calculate_flat_dim(),),
            dtype=np.float32
        )

        self.circuit = None
        self.valid_actions = []



    def reset(self, seed: str | None = None, options: None = None):
        """
        Réinitialise l'environnement pour un nouvel épisode

        @return: Observation initiale, informations supplémentaires
        """
        super().reset(seed=seed)
        self.current_steps = 0
        self.circuit = LogicCircuit()

        # Ajout de base : deux inputs et une sortie, une porte AND
        self.circuit.add_gate(LogicGate("INPUT", "A"))
        self.circuit.add_gate(LogicGate("INPUT", "B"))
        self.circuit.add_gate(LogicGate("AND", "G1"))
        self.circuit.add_gate(LogicGate("OUTPUT", "OUT"))

        self.circuit.connect("A", "G1")
        self.circuit.connect("B", "G1")
        self.circuit.connect("G1", "OUT")

        # Ajout d'une faute pour le circuit afin de l'aider à s'améliorer
        # self.faulty_circuit = FaultyCircuit(self.circuit)
        # self.faulty_circuit.add_fault("OUT", "bitflip")

        obs = self._get_obs()
        info = {"action_mask": self.get_action_mask()}
        return obs, info

    def step(self, action):
        """
        Applique une action de modification sur le circuit

        @param action: Tuple (action_type, gate_type_or_source, source, target)

        @return: Observation, récompense, bool de fin d'épisode, bool de troncature, infos
        """
        done = False
        truncated = False
        self.current_steps += 1
        reward = -0.1

        # Indexation de noeuds du graph
        self.id_to_index = {gate_id: i for i, gate_id in enumerate(
            sorted(self.circuit.graph.nodes))}
        self.index_to_id = {i: gate_id for gate_id,
                            i in self.id_to_index.items()}

        try:
            actual_action = self.valid_actions[action]
            action_type, action_gate_type, action_id1, action_id2 = actual_action
            source_id = self.index_to_id.get(action_id1, f"G{action_id1}")
            target_id = self.index_to_id.get(action_id2, f"G{action_id2}")

            if action_type == 0:  # Ajouter une porte logique au circuit
                if len(self.circuit.graph.nodes) < self.max_gates:
                    gate_type = self._int_to_gate_type(action_gate_type)
                    self.circuit.add_gate(LogicGate(gate_type))
                    reward = 1
                else:
                    reward = -0.25

            elif action_type == 1:  # Supprimer une porte logique
                is_removed = self.circuit.remove_gate(source_id)
                reward = 1
                if is_removed is False:
                    reward = -1

            elif action_type == 2:  # Connecter deux portes logiques
                self.circuit.connect(source_id, target_id)
                reward = 1

            elif action_type == 3:  # Déconnecter deux portes logiques
                self.circuit.disconnect(source_id, target_id)
                reward = 1

            if self.circuit.is_valid():
                # Sauvegarder le circuit + comparer avec les fonctionnalités
                # avec le circuit de base
                tmp_fd, tmp_path = tempfile.mkstemp(suffix=".blif")
                os.close(tmp_fd)
                self.circuit.export_to_blif(tmp_path, "tmp")

                if check_circuits(tmp_path, self.target_filepath,
                                  self.abc_path):
                    reward = 10
                    done = True
                else:
                    reward = 5

                os.remove(tmp_path)

        except Exception:
            reward = -2

        print(f"Action RL: {action}, reward: {reward:.2f}, current_steps: {
              self.current_steps}")
        info = {"action_mask": self.get_action_mask()}

        # Optimisation pour le rendu vidéo, sinon le cache est trop grand et ça
        # ralenti l'entrainement
        if self.current_steps >= self.max_steps:
            truncated = True

        return self._get_obs(), reward, done, truncated, info

    def _get_obs(self):
        """
        Retourne une observation sous forme de vecteur applati 1D contenant la
        structure du circuit (matrice adjacence, types de portes logiques)

        @return: numpy array représentant l'état
        """

        # Création de vecteur qui contiendront les informations sur le circuit
        # - Les types des différentes portes logiques
        # - Une matrice d'adjacence des portes logiques pour comprendre les
        # connexions
        # - Le type de la porte logique (entrée, sortie etc)

        types = np.zeros((self.max_gates, len(
            self.available_gates)), dtype=np.int8)
        adj = np.zeros((self.max_gates, self.max_gates), dtype=np.int8)
        is_input = np.zeros((self.max_gates,), dtype=np.int8)
        is_output = np.zeros((self.max_gates,), dtype=np.int8)
        fanin = np.zeros((self.max_gates,), dtype=np.int8)
        fanout = np.zeros((self.max_gates,), dtype=np.int8)
        nodes = list(self.circuit.graph.nodes)

        # Remplissage des vecteurs avec les informations
        for i, gate_id in enumerate(nodes[:self.max_gates]):
            gate = self.circuit.graph.nodes[gate_id]["gate"]
            type_idx = self._gate_type_to_int(gate.gate_type)
            if type_idx is not None:
                types[i][type_idx] = 1

            preds = list(self.circuit.graph.predecessors(gate_id))
            succs = list(self.circuit.graph.successors(gate_id))

            for j, other_id in enumerate(nodes[:self.max_gates]):
                if self.circuit.graph.has_edge(gate_id, other_id):
                    adj[i][j] = 1

            if gate.gate_type == "INPUT":
                is_input[i] = 1
            if gate.gate_type == "OUTPUT":
                is_output[i] = 1

            fanin[i] = len(preds)
            fanout[i] = len(succs)

        # Applitassage des vecteurs pour avoir un espace d'observation en 1D
        flat_obs = np.concatenate([
            types.flatten(),
            adj.flatten(),
            is_input.flatten(),
            is_output.flatten(),
            fanin.flatten(),
            fanout.flatten(),
        ])
        return flat_obs

    def get_action_mask(self):
        """
        Génère un masque d'actions valides effectuables
        """
        self.valid_actions = self._compute_valid_actions()
        mask = np.zeros(self.max_actions, dtype=bool)

        for i in range(len(self.valid_actions)):
            mask[i] = True

        return mask

    def _compute_valid_actions(self):
        """
        Génère la liste des actions valides par l'algorithme de RL
        """
        actions = []
        nodes = list(self.circuit.graph.nodes)
        max_id = min(self.max_gates, len(nodes))

        for gate_type in range(len(self.available_gates)):
            actions.append((0, gate_type, 0, 0))

        for i in range(max_id):
            actions.append((1, 0, i, 0))

        for i in range(max_id):
            for j in range(max_id):
                if i != j:
                    actions.append((2, 0, i, j))

        for i in range(max_id):
            for j in range(max_id):
                if i != j:
                    actions.append((3, 0, i, j))

        return actions

    def render(self):
        """
        Génère la frame selon le render_mode, human affiche le plot, rgb_array
        pour la vidéo
        """

        if self.render_mode is None:
            return

        fig = plt.figure()
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        labels = {}
        node_colors = []

        for node in self.circuit.graph.nodes:
            gate = self.circuit.graph.nodes[node]["gate"]
            labels[node] = f"{gate.gate_type}"

            # Colorations des noeuds selon leur type
            if gate.gate_type == "INPUT":
                node_colors.append("green")
            elif gate.gate_type == "OUTPUT":
                node_colors.append("yellow")
            else:
                node_colors.append("lightblue")

        nx.draw(self.circuit.graph, ax=ax, labels=labels, with_labels=True,
                node_size=1500, node_color=node_colors)

        if self.render_mode == "human":
            self.plt.pause(0.001)
            self.plt.draw()
            return

        elif self.render_mode == "rgb_array":
            canvas.draw()
            buf = np.asarray(fig.canvas.buffer_rgba())
            img = buf[:, :, :3].copy()
            plt.close(fig)
            return img

    def _int_to_gate_type(self, value: int) -> str:
        """
        Convertit un entier en type de porte logique

        @param value: Indice de la porte
        @return: Nom de type de porte logique
        """
        return self.available_gates[value % len(self.available_gates)]

    def _gate_type_to_int(self, gate_type: str):
        """
        Convertit un type de porte logique en entier

        @param gate_type: Type de la porte logique
        @return: Indice de la porte
        """
        if gate_type in self.available_gates:
            return self.available_gates.index(gate_type)

        return None

    def calculate_flat_dim(self) -> int:
        """
        Fonction pour calculer la taille du dict applatis pour l'observation

        @return: Taille applatis nécessaires
        """

        dim_gate_types = self.max_gates * len(self.available_gates)
        dim_adjacency = self.max_gates * self.max_gates
        dim_inputs_outputs = self.max_gates * 2  # is_input + is_output
        dim_fan = self.max_gates * 2  # fanin + fanout

        return dim_gate_types + dim_adjacency + dim_inputs_outputs + dim_fan
