import os
import subprocess


def check_circuits(circuit_a_filepath: str, circuit_b_filepath: str, abc_path:
                   str) -> bool:
    """Vérifie si deux circuits sont identiques grâce au vérificateur formel ABC
    @param circuit_a_filepath: Chemin vers le fichier .blif du circuit a
    @param circuit_b_filepath: Chemin vers le fichier .blif du circuit b

    @return: Booléen indiquant si les circuits sont formellement identiques ou
    non
    """

    # Vérification existance des fichiers
    if not os.path.exists(circuit_a_filepath) or not os.path.exists(circuit_b_filepath):
        return False

    cmd = f"read {circuit_a_filepath}\nread {circuit_b_filepath}\ncec {
        circuit_a_filepath} {circuit_b_filepath}\n"

    process = subprocess.Popen([abc_path], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
    try:
        output, error = process.communicate(cmd, timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        return False

    # DEBUG:
    # print(f"output: {output}, err: {error}")
    if error != "" or "NOT EQUIVALENT" in output:
        return False

    return True
