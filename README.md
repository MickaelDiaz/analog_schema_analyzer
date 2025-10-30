# 🛠️ Analyseur de Netlist de Circuits Électroniques

Ce projet est un outil en Python conçu pour analyser une **netlist** (une description textuelle des composants et de leurs interconnexions dans un circuit) afin de déterminer les chemins de signal, identifier les étages d'amplification à transistors, et détecter des configurations courantes comme les amplificateurs à AOP ou les contre-réactions.

---

## 🏗️ Structure et Fonctionnement du Code

Le projet est organisé en plusieurs modules Python, chacun ayant une responsabilité spécifique :

### 1. `parse.py` : Analyse de la Netlist

Ce module est responsable de la lecture et de l'interprétation de la netlist fournie (une liste de composants avec leurs connexions et valeurs).

|**Fonction**|**Rôle**|
|---|---|
|`parse_netlist(netlist_text)`|Analyse la chaîne de caractères de la netlist et convertit chaque ligne en un dictionnaire structuré. Il identifie le **type** (`R`, `C`, `Q`, `V`, `X`, etc.), le **nom**, les **nœuds** de connexion et la **valeur/modèle** de chaque composant.|

### 2. `graph.py` : Construction et Analyse du Graphe

Ce module contient les algorithmes de graphe essentiels pour l'analyse du circuit.

|**Fonction**|**Rôle**|
|---|---|
|`build_graph(components)`|Construit une **représentation graphique** du circuit. Les nœuds du graphe sont les nœuds du circuit, et les arêtes représentent une connexion physique par un composant.|
|`trace_signal_paths(graph, start_nodes)`|Utilise un **parcours en largeur (BFS)** pour trouver les nœuds qui sont connectés aux nœuds de départ (par exemple, "Vin") dans un rayon limité (profondeur maximale de 2) sans passer par les rails d'alimentation ou la masse.|
|`build_transistor_signal_graph(...)`|Le cœur de l'analyse : il crée un graphe logique des transistors. Il **détecte les étages** de l'amplificateur en partant des nœuds d'entrée (`Vin`) et **détermine la configuration** (`émetteur commun`, `collecteur commun`) en fonction de la connexion des bases. Il identifie aussi le **transistor de sortie** (celui qui sort vers `Vout`).|
|`find_all_paths(graph, start, target, max_depth)`|Recherche tous les chemins possibles entre deux nœuds, utilisés notamment pour détecter les boucles de contre-réaction.|
|`is_fully_passive_path(...)` / `get_passive_component_in_path(...)`|Vérifie si un chemin est composé **uniquement de composants passifs** (R, C, L) et liste ces composants.|

### 3. `analyzer.py` : Détection de Circuits Spécifiques

Ce module se concentre sur l'identification de structures de circuit bien connues.

|**Fonction**|**Rôle**|
|---|---|
|`find_opamp_amplifier(components)`|Cherche les amplificateurs opérationnels (`X`) et analyse les résistances connectées à leurs bornes inverseuses et de sortie pour identifier des configurations d'**amplificateur inverseur** ou **non-inverseur**.|

### 4. `main.py` : Le Script Principal

Ce script orchestre l'ensemble du processus en utilisant les fonctions des autres modules pour analyser la netlist et afficher les résultats.

---

## 🏃 Étapes d'Analyse

Le processus d'analyse suit une séquence logique dans `main.py` :

1. **Parsing** : La netlist est lue et convertie en une liste de dictionnaires de composants via `parse_netlist()`.
    
2. **Construction du Graphe Physique** : `build_graph()` crée la carte des interconnexions du circuit.
    
3. **Identification des Zones de Signal** : `trace_signal_paths()` identifie les nœuds proches de l'entrée (`Vin`) et de la sortie (`Vout`).
    
4. **Analyse des Transistors** :
    
    - `build_transistor_signal_graph()` crée un **graphe logique** où les nœuds sont les transistors.
        
    - Il **assigne un étage** à chaque transistor en partant de l'entrée (Stage 0).
        
    - Il **détermine la configuration** (ex: `émetteur commun`) et **identifie le transistor de sortie**.
        
5. **Détection de Contre-réaction** :
    
    - Pour les transistors qui ne sont pas du dernier étage, le script recherche des chemins passifs (R et C) entre `Vout` et la base ou l'émetteur du transistor.
        
    - Si un tel chemin est trouvé, il est signalé comme une **contre-réaction passive**.
        
6. **Affichage des Résultats** : Les informations clés (graphe logique, détails des transistors, contre-réactions, transistor de sortie) sont imprimées dans la console.
    

---

## 💡 Exemple de Détection (Dans `op_amp_det`)

Le script `op_amp_det` illustre comment utiliser l'analyseur pour des circuits spécifiques, en l'occurrence, l'amplificateur opérationnel (AOP) :

1. Il parse une netlist contenant un AOP (`XU2`) et des résistances (`R1`, `R2`). 1
    
2. `find_opamp_amplifier()` est appelé pour détecter la configuration de l'AOP.
    
3. Dans l'exemple fourni, il détecte un **Amplificateur inverseur** et affiche son **gain théorique** calculé à partir des valeurs des résistances de contre-réaction (`R2`) et d'entrée (`R1`), selon la formule : Gain $= -R_{feedback}/R_{in}$. 2
