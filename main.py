import json

import gymnasium
from gymnasium.wrappers import TimeLimit
from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env

from construct_agent import LogicCircuitEnv

# Lire les config depuis le fichier json
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Adapter avec TimeLimit si tu veux limiter la durée des épisodes
env = LogicCircuitEnv(config["target_blif"], config["abc_path"])
env = TimeLimit(env, max_episode_steps=100)  # Facultatif

# Vérifie que l'environnement est bien formé
check_env(env, warn=True)

# Entrainement du modèle DQN
model = DQN(
    "MlpPolicy",
    env,
    verbose=1,
    learning_rate=1e-3,
    buffer_size=50000,
    learning_starts=1000,
    batch_size=32,
    tau=1.0,
    gamma=0.99,
    train_freq=1,
    target_update_interval=100,
)

model.learn(total_timesteps=100_000)
model.save("agent_contruscteur")

obs, _ = env.reset()
done = False

while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, truncated, info = env.step(action)
    env.render()
