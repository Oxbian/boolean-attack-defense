import json

from construct_agent import LogicCircuitOptimizer

# Charger la configuration
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Initialiser et exécuter l'optimiseur
optimizer = LogicCircuitOptimizer(
    target_filepath=config["target_blif"],
    abc_path=config["abc_path"],
    max_gates=20,
    population_size=20
)

best_circuit = optimizer.evolve(generations=50)

# Affichage
print("\nMeilleur circuit robuste obtenu :")
best_circuit.visualize()

# Sauvegarde
best_circuit.export_to_blif(
    "best_robust_circuit.blif", model_name="robust_final")
print("Circuit enregistré dans 'best_robust_circuit.blif'")
