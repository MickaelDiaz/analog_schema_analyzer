# Déterminer quel circuit est présent

# op amp 

def find_opamp_amplifier(components):
    amplifiers = []

    for comp in components:
        if comp["type"] == "X" and len(comp["nodes"]) == 5:
            non_inv, inv, vcc, vee, out = comp["nodes"] # on affecte le nom "" des noeuds de la netlist autour du X à des variables pour s'adapter à tout schéma
            opamp_name = comp["name"]

            # Cherche les résistances autour de l'entrée inverseuse
            r_in_inv = None
            r_feedback = None
            r_inv = None

            for r in [c for c in components if c["type"] == "R"]:
                nodes = r["nodes"]
                if inv in nodes:
                    other_node = nodes[0] if nodes[1] == inv else nodes[1] # other_node c'est le premier node si le deuxième vaut inv. Sinon other_node c'est le deuxième node
                    if other_node == out:
                        r_feedback = r
                    elif other_node == "0":
                            r_inv = r
                    else: 
                        r_in_inv = r # si la résistance plug à inv n'est pas reliée à la sortie, c'est la résistance d'entrée

            if r_in_inv and r_feedback:
                amp_info = {
                    "type": "ampli_inverseur",
                    "opamp": opamp_name,
                    "input_node": [n for n in r_in_inv["nodes"] if n != inv][0], # node de r_in, celui qui n'est pas inv
                    "output_node": out,
                    "r_in_inv": r_in_inv,
                    "r_feedback": r_feedback,
                    "inv_input": inv,
                    "non_inv_input": non_inv
                }
                amplifiers.append(amp_info)

            elif r_inv and r_feedback:
                amp_info = {
                    "type": "ampli_non_inverseur",
                    "opamp": opamp_name,
                    "input_node": non_inv, # node de r_in, celui qui n'est pas inv
                    "output_node": out,
                    "r_inv": r_inv,
                    "r_feedback": r_feedback,
                    "inv_input": inv,
                    "non_inv_input": non_inv
                }
                amplifiers.append(amp_info)

    return amplifiers

