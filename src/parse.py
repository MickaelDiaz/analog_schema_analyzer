# Permet d'analyser la netlist, déterminer nom, noeuds, valeurs, type de composant

def parse_netlist(netlist_text):
    components = []
    for line in netlist_text.split('\n'): # découpe la string en lignes
        line = line.strip() # enlève les espaces avant et après la ligne
        if not line or line.startswith("*"):  # ignorer les commentaires
            continue
        tokens = line.split() # la ligne est divisée en fonction des espaces et regroupée dans une liste appelée tokens
        comp_name = tokens[0] # premier de la liste c'est le nom
        comp_type = comp_name[0].upper() # premier caractère du nom mis en majuscule

        if comp_type in "RCL":
            name = comp_name
            nodes = tokens[1:-1] # tokens de 1 à l'avant dernier (car nombre de nodes variable)
            value = tokens[-1] # dernière valeur des tokens
            components.append({ # append pour rajouter des éléments à la liste
                "type": comp_type,
                "name": name,
                "nodes": nodes,
                "value": value
            })

        elif comp_type in "XQD":
            name = comp_name
            nodes = tokens[1:-1]
            model = tokens[-1]
            if model in ["NPN", "N", "2N2222", "2N3904"]:
                model = "N"
            elif model in ["PNP", "P", "2N2907", "2N3906"]:
                model = "P"
            components.append({
                "type": comp_type,
                "name": name,
                "nodes": nodes,
                "model": model
            })
        
        elif comp_type in "V":
            name = comp_name
            nodes = tokens[1:-2]
            value = tokens[-2:]
            components.append({
                "type": comp_type,
                "name": name,
                "nodes": nodes,
                "value": value
            })
        
        else:
            print(f"Composant non reconnu : {line}")
    return components