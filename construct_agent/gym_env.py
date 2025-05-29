import gymnasium as gym
from gymnasium import spaces
import numpy as np
from circuit import LogicCircuit, LogicGate
from construct_agent.actions import *
from construct_agent.reward import evaluate_circuit

class LogicCircuitEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.input_cases = [
            ({"A": True, "B": False}, {"OUT": False}),
            ({"A": True, "B": True}, {"OUT": True})
        ]

        self.actions = [
            add_random_gate,
            remove_random_gate,
            add_random_connection,
            remove_random_connection,
            change_random_gate
        ]
        self.action_space = spaces.Discrete(len(self.actions))
        self.observation_space = spaces.Box(low=0, high=10, shape=(10,), dtype=np.float32)

        self.circuit = None

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.circuit = LogicCircuit()

        # Création d'un circuit simple (A AND B -> OUT)
        g1 = LogicGate("INPUT", "A")
        g2 = LogicGate("INPUT", "B")
        g3 = LogicGate("AND", "AND1")
        g4 = LogicGate("OUTPUT", "OUT")

        for g in [g1, g2, g3, g4]:
            self.circuit.add_gate(g)

        self.circuit.connect("A", "AND1")
        self.circuit.connect("B", "AND1")
        self.circuit.connect("AND1", "OUT")

        obs = self._encode_state()
        info = {}
        return obs, info

    def step(self, action_index):
        action_fn = self.actions[action_index]
        try:
            action_fn(self.circuit)
        except Exception:
            pass

        reward = evaluate_circuit(self.circuit, self.input_cases)
        obs = self._encode_state()

        terminated = False
        truncated = False
        info = {}
        print(f"Action RL: {action_fn}, reward: {reward:.2f}")
        return obs, reward, terminated, truncated, info

    def _encode_state(self):
        types = [self.circuit.graph.nodes[n]['gate'].gate_type for n in self.circuit.graph.nodes]
        gates = ["INPUT", "OUTPUT", "AND", "OR", "NOT", "XOR", "NAND", "NOR", "XNOR", "OTHER"]
        counts = [types.count(g) for g in gates]
        return np.array(counts, dtype=np.float32)
