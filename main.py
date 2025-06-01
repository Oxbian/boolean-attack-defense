import json

import sb3_contrib
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.ppo_mask import MaskablePPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.monitor import Monitor

from construct_agent import LogicCircuitEnv

print(sb3_contrib.__version__)


# Lire les config depuis le fichier json
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)


def mask_fn(env):
    return env.get_action_mask()


def make_env():
    """
    Créer une fonction de fabrication d'environnement
    """
    env = LogicCircuitEnv(config["target_blif"], config["abc_path"])
    env = ActionMasker(env, mask_fn)
    env = Monitor(env)  # Pour logger reward et info
    return env


# Environnement vectorisé
env = make_vec_env(make_env, n_envs=1)

# Initialiser le modèle
model = MaskablePPO(
    MaskableActorCriticPolicy,
    env,
    verbose=1,
    tensorboard_log="./ppo_logs/"
)

# Entraîner
model.learn(total_timesteps=100_000)

# Sauvegarder le modèle
model.save("agent_constructeur")

# Évaluation post-entraînement
obs, info = env.reset()
done = False

while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, truncated, info = env.step(action)
    print(f"Episode terminé avec reward: {reward}")
    env.render()
