def evaluate_circuit(circuit, input_cases):
    """
    Évalue un circuit sur une série de cas de test
    @param circuit: LogicCircuit
    @param input_cases: liste de tuples (inputs_dict, expected_outputs_dict)
    @return: score réel combinant validité et complexité
    """
    passed = 0
    failed = 0

    for inputs, expected in input_cases:
        try:
            result = circuit.evaluate(inputs)
            if result == expected:
                passed += 1
            else:
                failed += 1
        except Exception:
            failed += 1

    # Score de validité entre 0 et 1
    validity_score = passed / len(input_cases)

    # Complexité réduite : chaque porte non-INPUT/OUTPUT coûte 0.2 point
    complexity_penalty = len([
        n for n in circuit.graph.nodes
        if circuit.graph.nodes[n]['gate'].gate_type not in ["INPUT", "OUTPUT"]
    ]) * 0.2

    return (validity_score * 2.0) - complexity_penalty

