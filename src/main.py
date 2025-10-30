from parse import parse_netlist
from graph import build_graph, trace_signal_paths, build_transistor_signal_graph, find_all_paths, get_passive_component_in_path, is_fully_passive_path 

netlist = """R1 N005 Vin 100
C1 N005 0 47n
C2 ve1 N005 100n
R2 N005 0 680k
R3 N001 N003 12k
R4 N001 N002 220
Q1 N003 N005 ve1 PNP
Q2 N004 N003 N002 NPN
V1 0 N001 15
Q3 N008 N007 N006 NPN
R5 N004 N006 560
R6 N004 N007 10k
C3 N004 N007 10µ
C4 Vout N006 100µ
C5 N006 N007 100n
R7 N007 N008 68k
R8 N007 P001 100
R9 Vout vf 10k
R10 vf 0 20
R11 vf N009 33
C7 N009 ve1 220µ
R12 ve1 N008 220k
V2 N008 0 15
V3 Vin 0 SINE(0 0 100)
C6 P001 0 470n
R13 N006 ve1 33k
"""

components = parse_netlist(netlist)
graph = build_graph(components)
vin_nodes = trace_signal_paths(graph, start_nodes=["Vin"])
vout_nodes = trace_signal_paths(graph, start_nodes=["Vout"])
signal_graph, transistor_info, output_candidates = build_transistor_signal_graph(
    components, graph, vin_nodes, vout_nodes
)
max_stage = max(info.get("stage",-1) for info in transistor_info.values())
for name, info in transistor_info.items():
    if info.get("stage") == max_stage:
        continue  # On ignore les transistors du dernier étage

    emitter = info["E"]
    base = info["B"]
    emitter_paths = find_all_paths(graph, "Vout", emitter, max_depth=6)
    for path in emitter_paths:
        if is_fully_passive_path(path, components):
            passive_components = get_passive_component_in_path(path, components)
            comp_names = [comp["name"] for comp in passive_components]
            print(f"Contre-réaction passive détectée vers l'émetteur de {name} via {comp_names}")

    base_paths = find_all_paths(graph, "Vout", base, max_depth=6)
    for path in base_paths:
        if is_fully_passive_path(path, components):
            passive_components = get_passive_component_in_path(path, components)
            comp_names = [comp["name"] for comp in passive_components]
            print(f"Contre-réaction passive détectée vers la base de {name} via {comp_names}")



print("\n=== GRAPHE LOGIQUE DES TRANSISTORS ===")
for src, dests in signal_graph.items():
    print(f"{src} → {', '.join(dests)}")

print("\n=== INFOS PAR TRANSISTOR ===")
for name, info in transistor_info.items():
    c, b, e = info["C"], info["B"], info["E"]
    stage = info.get("stage", "N/A")
    type = info.get("type", "rien")
    print(f"{name}: C={c}, B={b}, E={e}, Stage={stage}, monté en {type}")

print("\n=== TRANSISTOR DE SORTIE ===")
if output_candidates:
    for cand in output_candidates:
        print(f"{cand['transistor']} sort vers Vout via {cand['pin']} (node: {cand['output_node']})")
else:
    print("Aucun transistor ne semble connecté à la sortie.")

