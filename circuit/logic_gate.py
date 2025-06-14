import uuid


class LogicGate:
    """Classe pour définir une porte logique"""

    def __init__(self, gate_type: str, gate_id: str | None = None):
        """Initialisation de la porte logique
        @param gate_type: String du type de porte logique, input pour les portes
        d'entrée du circuit, output pour la porte de sortie du circuit
        @param gate_id: Identifiant pour la porte logique
        """
        assert gate_type in {"AND", "OR", "NOT", "NAND",
                             "NOR", "XOR", "XNOR", "INPUT", "OUTPUT"}

        self.gate_type = gate_type
        self.gate_id = gate_id or str(uuid.uuid4())

    def __repr__(self):
        """Méthode pour l'affichage de la porte et de ses informations
        @return: Chaine formattée avec le type et l'id de la porte
        """
        return f"{self.gate_type}({self.gate_id[:4]})"

    def compute(self, inputs: list[bool]) -> bool:
        """Calcul la porte logique à partir de ses entrées
        @param inputs: Liste de booléen pour entrant dans la porte logique

        @return: Booléen résultat de l'opération de la porte logique
        """

        if self.gate_type == "AND":
            return inputs[0] and inputs[1]
        elif self.gate_type == "OR":
            return inputs[0] or inputs[1]
        elif self.gate_type == "NOT":
            return not inputs[0]
        elif self.gate_type == "NAND":
            return not (inputs[0] and inputs[1])
        elif self.gate_type == "NOR":
            return not (inputs[0] or inputs[1])
        elif self.gate_type == "XOR":
            return inputs[0] ^ inputs[1]
        elif self.gate_type == "XNOR":
            return not (inputs[0] ^ inputs[1])
        elif self.gate_type == "INPUT":
            raise ValueError("INPUT gate has no compute logic")
        elif self.gate_type == "OUTPUT":
            raise ValueError("OUTPUT gate has no compute logic")
