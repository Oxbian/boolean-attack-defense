import subprocess


def check_circuits(circuit_a_filepath: str, circuit_b_filepath: str, abc_path:
                   str) -> bool:
    """Vérifie si deux circuits sont identiques grâce au vérificateur formel ABC
    @param circuit_a_filepath: Chemin vers le fichier .blif du circuit a
    @param circuit_b_filepath: Chemin vers le fichier .blif du circuit b

    @return: Booléen indiquant si les circuits sont formellement identiques ou
    non
    """

    cmd = f"read {circuit_a_filepath}\nread {circuit_b_filepath}\ncec {circuit_a_filepath} {circuit_b_filepath}\n"

    process = subprocess.Popen([abc_path], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
    output, error = process.communicate(cmd)

    # print(f"output: {output}, err: {error}")
    if error != "" or "NOT EQUIVALENT" in output:
        return False

    return True
