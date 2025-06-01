import os
import tempfile

import gymnasium as gym
import numpy as np
# from attacker import FaultyCircuit
from circuit import LogicCircuit, LogicGate, check_circuits

# import construct_agent as ca


class LogicCircuitEnv(gym.Env):
    """Environnement Gym pour la construction de circuits booléens.
    L'agent peut ajouter, supprimer ou connecter des portes pour tenter de
    rendre un circuit équivalent en fonctionnalités à un circuit cible,
    même en présence de fautes injectées par un attaquant.
    """

    def __init__(self, target_filepath: str, abc_path: str):
        """
        Initialise l'environnement de construction de circuits

        @param target_circuit_path: Chemin vers le fichier .blif du circuit cible
        @param abc_path: Chemin vers l'exécutable ABC
        """
        super().__init__()

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
        self.action_space = gym.spaces.Discrete(
            4 * len(self.available_gates) * self.max_gates * self.max_gates)

        # Définition d'une matrice max_gates * (nombre type + connexions) pour
        # enregistrer l'état du circuit
        self.observation_space = gym.spaces.Box(
            low=0, high=1, shape=(self.max_gates, self.max_gates *
                                  len(self.available_gates)), dtype=np.int8)

        self.circuit = None

    def reset(self, seed=None, options=None):
        """
        Réinitialise l'environnement pour un nouvel épisode

        @return: Observation initiale, informations supplémentaires
        """
        super().reset(seed=seed)
        self.circuit = LogicCircuit()

        # Ajout de base : deux inputs et une sortie
        self.circuit.add_gate(LogicGate("INPUT", "A"))
        self.circuit.add_gate(LogicGate("INPUT", "B"))
        self.circuit.add_gate(LogicGate("OUTPUT", "OUT"))

        # self.faulty_circuit = FaultyCircuit(self.circuit)
        # self.faulty_circuit.add_fault("OUT", "bitflip")

        return self._get_obs(), {}

    def step(self, action):
        """
        Applique une action de modification sur le circuit

        @param action: Tuple (action_type, gate_type_or_source, source, target)
        @return: Observation, récompense, bool de fin d'épisode, bool de troncature, infos
        """
        done = False
        truncated = False
        reward = -0.1

        self.id_to_index = {gate_id: i for i, gate_id in enumerate(
            sorted(self.circuit.graph.nodes))}
        self.index_to_id = {i: gate_id for gate_id,
                            i in self.id_to_index.items()}

        try:
            action_type, action_gate_type, action_id1, action_id2 = action
            source_id = self.index_to_id.get(action_id1, f"G{action_id1}")
            target_id = self.index_to_id.get(action_id2, f"G{action_id2}")

            if action_type == 0:  # Ajouter une porte logique au circuit
                gate_type = self._int_to_gate_type(action_gate_type)
                self.circuit.add_gate(LogicGate(gate_type))
            elif action_type == 1:  # Supprimer une porte logique
                is_removed = self.circuit.remove_gate(source_id)

                if is_removed is False:
                    reward = -1
            elif action_type == 2:  # Connecter deux portes logiques
                self.circuit.connect(source_id, target_id)
            elif action_type == 3:  # Déconnecter deux portes logiques
                self.circuit.disconnect(source_id, target_id)

            if self.circuit.is_valid():
                tmp_fd, tmp_path = tempfile.mkstemp(suffix=".blif")
                os.close(tmp_fd)
                self.circuit.export_to_blif(tmp_path, "tmp")
                # Sauvegarder le circuit + comparer avec le circuit de base
                if check_circuits(tmp_path, self.target_filepath,
                                  self.abc_path):
                    reward = 10
                    done = True
                else:
                    reward = -0.1
        except Exception:
            reward = -2

        print(f"Action RL: {action}, reward: {reward:.2f}")
        return self._get_obs(), reward, done, truncated, {}

    def _get_obs(self):
        """
        Retourne une observation sous forme de matrice d'adjacence + types des
        portes

        @return: numpy array représentant l'état
        """
        obs = np.zeros((self.max_gates, self.max_gates *
                        len(self.available_gates)), dtype=np.int8)
        nodes = list(self.circuit.graph.nodes)

        for i, gate_id in enumerate(nodes[:20]):
            gate = self.circuit.graph.nodes[gate_id]["gate"]

            # One-hot type
            type_idx = self._gate_type_to_int(gate.gate_type)

            # Vérification d'erreur
            if type_idx is None:
                return obs

            obs[i][type_idx] = 1

            # Connexions sortantes (adjacency vector)
            successors = list(self.circuit.graph.successors(gate_id))

            for succ in successors:
                if succ in nodes[:20]:
                    succ_idx = nodes.index(succ)
                    obs[i][8 + succ_idx] = 1

        return obs

    def render(self):
        """
        Affiche le circuit courant
        """
        self.circuit.visualize()

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

    def decode_action(self, action):
        """
        Décodeur d'actions
        """
        a_type = action // (len(self.available_gates) * self.max_gates *
                            self.max_gates)
        rem = action % (len(self.available_gates) * self.max_gates *
                        self.max_gates)
        gate = rem // (self.max_gates ** 2)
        rem = rem % (self.max_gates ** 2)
        src = rem // self.max_gates
        tgt = rem % self.max_gates
        return (a_type, gate, src, tgt)
