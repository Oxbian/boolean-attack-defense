from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env

from construct_agent import LogicCircuitEnv

# Créer l'environnement Gym (permet de pouvoir changer d'algo facilement)
env = LogicCircuitEnv()

# Vérifie la compatibilité de l'algo (ici DQN) avec l'environnement Gym
check_env(env)

# Entraîner l'agent avec l'algorithme DQN
model = DQN(
    "MlpPolicy",
    env,
    verbose=1,
    exploration_initial_eps=1.0,
    exploration_final_eps=0.1,
    exploration_fraction=0.3,
)
model.learn(total_timesteps=100_000)


# Sauvegarder le modèle entraîné
model.save("agent_constructeur_rl")
