from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env
from construct_agent.gym_env import LogicCircuitEnv

# Créer l'environnement Gym
env = LogicCircuitEnv()
check_env(env)  # Vérifie la compatibilité avec Gym

# Entraîner l'agent avec DQN
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
