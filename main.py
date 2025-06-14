import json

from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.ppo_mask import MaskablePPO

from construct_agent import LogicCircuitEnv
from gymnasium.wrappers import RecordVideo, RecordEpisodeStatistics


# Lire les config depuis le fichier json
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)


def mask_fn(env):
    return env.get_action_mask()


# Environnement
env = LogicCircuitEnv(config["target_blif"], config["abc_path"], render_mode='rgb_array')
env = ActionMasker(env, mask_fn)

# Enregistrer une vidéo de l'évolution
env = RecordVideo(env, video_folder="videos-evolution/", episode_trigger=lambda
                  x: x % 100 == 0, name_prefix="circuit_evolution")

# Initialiser le modèle
model = MaskablePPO(MaskableActorCriticPolicy, env, verbose=1)

# Entraînement du modèle
model.learn(total_timesteps=1_000_000)

# Sauvegarder le modèle
model.save("agent_constructeur")
env.close()

# Vérification modèle charge bien
del model

model = MaskablePPO.load("agent_constructeur")

# Évaluation post-entraînement
obs, _ = env.reset()
done = False

while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, truncated, info = env.step(action)
    print(f"Episode terminé avec reward: {reward}")
