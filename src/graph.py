
from collections import defaultdict, deque

# Graphe réprésenté comme un dictionnaire où chaque clé est un node et sa valeur est l'ensemble des nodes connectés
def build_graph(components):
    graph = defaultdict(set) # dictionnaire avec valeur par défaut un set (ensemble vide)
    for comp in components:
        if comp["type"] in ("R", "C", "V", "I", "L", "D"):  # passifs
            nodes = comp["nodes"]
            if len(nodes) >= 2:  # Vérification sécurité
                n1, n2 = nodes[0], nodes[1]
                graph[n1].add(n2) # même si n1 n'existait pas, il est créé comme un set vide. Cela ajoute n2 au set n1
                graph[n2].add(n1) 
    return graph


# Parcours en largeur (BFS) : parcours d'un graph à partir du noeud source, tous les successeurs, tous les successeur des successeurs etc.
# Alors que parcours en profondeur (DFS) continue l'exploration jusu'au cul de sac pour chaque branche.
def trace_signal_paths(graph, start_nodes):
    max_depth = 2
    exclude_nodes = {"Vee", "Vcc", "0"}
    visited = set(start_nodes) # initiation nodes visités (ceux de départ)
    queue = deque([(node, 0) for node in start_nodes]) # File d'attente double ended queue, pour des opérations aux deux extrémités. On a chaque noeud associé au début à la profondeur 0

    while queue:
        node, depth = queue.popleft() # on retire le noeud le plus à gauche (FIFO) qu'on stocke dans "node" 
        if depth >= max_depth:
            continue
        for neighbor in graph[node]: # d'après le dictionnaire graph, il retrouve les valeurs associées à ce node, donc ses voisins
            if neighbor not in visited and neighbor not in exclude_nodes:
                visited.add(neighbor)
                queue.append((neighbor, depth+1))

    return visited

def build_transistor_signal_graph(components, graph, vin_nodes, vout_nodes):
    transistor_info = {
        comp["name"]: {"C": c, "B": b, "E": e}
        for comp in components if comp["type"] == "Q"
        for c, b, e in [comp["nodes"]]
    } # le nom du transistor (clé) est défini par un sous dictionnaires de ses broches dans le dictionnaire

    signal_graph = defaultdict(set) 

    visited_transistors = set()
    queue = deque()

    # Transistors d’entrée (base connectée à vin)
    for name, info in transistor_info.items(): # info permet d'itérer les items du dictionnaire
        if info["B"] in vin_nodes:
            queue.append(name)
            visited_transistors.add(name)
            transistor_info[name]["stage"] = 0 # définition de l'étage du transistor

    while queue:
        current = queue.popleft()
        current_stage = transistor_info[current]["stage"]
        c, e = transistor_info[current]["C"], transistor_info[current]["E"]
        reachable = { # dictionnaire, clés : type de config et valeurs : nodes
            "émetteur commun": trace_signal_paths(graph, [c]),
            "collecteur commun": trace_signal_paths(graph, [e]),
        }

        for name, info in transistor_info.items(): # pour chaque transistor (name) et dedans pour chaque broche (info)
            if name == current:
                continue
            for config_type, reachable_nodes in reachable.items():
                if info["B"] in reachable_nodes:
                    signal_graph[current].add(name)
                if "type" not in transistor_info[current]: # si il n'y a pas encore de type inscrit (ex si les nodes du collecteur n'ont pas trouvé de base, sueleemnt à ce moment là on pourra mettre en collecteur commun) 
                    transistor_info[current]["type"] = config_type
                if name not in visited_transistors:
                    transistor_info[name]["stage"] = current_stage + 1
                    queue.append(name)
                    visited_transistors.add(name)
    
    max_stage = max(info.get("stage", -1) for info in transistor_info.values()) 
    # .values permet d'obtenir une liste des valeurs du dictionnaire donc le sous dictionnaire (stage et pattes). 
    # info.get("stage") permet d'obtenir la valeur de la clé "stage" du sous dico (-1 si il trouve pas pour éviter les erreurs)
    candidates = []
    for name, info in transistor_info.items(): # items sort une liste de tuples clé-valeur
        if info.get("stage") == max_stage:
            c, e = info["C"], info["E"]
            reachable_from_c = trace_signal_paths(graph, [c])
            reachable_from_e = trace_signal_paths(graph, [e])
            if vout_nodes & reachable_from_c:
                candidates.append({"transistor": name, "output_node": c, "pin": "C"})
                transistor_info[name]["type"] = "émetteur commun" 
            elif vout_nodes & reachable_from_e:
                candidates.append({"transistor": name, "output_node": e, "pin": "E"})
                transistor_info[name]["type"] = "collecteur commun" 

    return signal_graph, transistor_info, candidates

# enregistrement des chemins (path) entre un node de début (start) et de fin (target)
def find_all_paths(graph, start, target, max_depth=5):
    queue = deque([(start, [start])]) # dequeue avec une liste de paire node-path
    paths = [] # liste des chemins
    while queue:
        (node, path) = queue.popleft()
        if node == target: # une fois qu'on atteint le node de target, on rajoute le path à la liste
            paths.append(path)
        elif len(path) <= max_depth:
            for neighbor in graph[node]: # pour chaque sommet (node) adjacent (contenus dans le graph du node)
                if neighbor not in path and neighbor != "0": # si le node n'est pas de la chein on le rajoute
                    queue.append((neighbor, path + [neighbor])) 
    return paths

def get_passive_component_in_path(path, components):
    path_components = []
    for i in range(len(path) - 1):
        n1, n2 = path[i], path[i+1]
        for comp in components:
            if set(comp["nodes"]) == {n1, n2} or (n1 in comp["nodes"] and n2 in comp["nodes"]):
                if comp["type"] not in ("Q", "V", "I", "D", "X"):
                    path_components.append(comp)
                break  # On a trouvé le composant pour cette paire de nœuds
    return path_components

def is_fully_passive_path(path, components):
    for i in range(len(path) - 1):
        n1, n2 = path[i], path[i+1]
        for comp in components:
            if n1 in comp["nodes"] and n2 in comp["nodes"]:
                if comp["type"] in ("Q", "V", "I", "D", "X"):
                    return False
                break  # On a trouvé le composant, on peut sortir
    return True



