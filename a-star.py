import random
from igraph import Graph, plot
import argparse
import time

def generate_random_dag(node_names, seed=None):
    if seed is not None:
        random.seed(seed)
    
    g = Graph(directed=True)
    g.add_vertices(len(node_names))
    
    node_index = {name: i for i, name in enumerate(node_names)}
    
    # 确保至少有一条边从 S 出发
    possible_targets = [i for i in range(len(node_names)) if i != node_index["T"] and i != node_index["S"]]
    source = node_index["S"]
    target = random.choice(possible_targets)
    g.add_edges([(source, target)])
    print(f"Add edge from {node_names[source]} to {node_names[target]}")
    
    # 确保至少有一条边指向 T
    possible_sources = [i for i in range(len(node_names)) if i != node_index["T"] and i != node_index["S"]]
    target = node_index["T"]
    source = random.choice(possible_sources)
    g.add_edges([(source, target)])
    
    # 确保每个节点（除了 S 和 T）至少有一条入边和一条出边
    for i in range(len(node_names)):
        if i == node_index["S"] or i == node_index["T"]:
            continue
        # 添加至少一条入边
        possible_sources = [j for j in range(len(node_names)) if j != i and j != node_index["S"] and j != node_index["T"]]
        while len(g.incident(i, mode="in")) == 0:
            source = random.choice(possible_sources)
            if not g.are_adjacent(source, i) and not g.are_adjacent(i, source):
                g.add_edges([(source, i)])
        
        # 添加至少一条出边
        possible_targets = [j for j in range(len(node_names)) if j != i and j != node_index["S"] and j != node_index["T"]]
        while len(g.incident(i, mode="out")) == 0:
            target = random.choice(possible_targets)
            if not g.are_adjacent(i, target) and not g.are_adjacent(target, i):
                g.add_edges([(i, target)])
    
    # 添加随机边，确保无环，且没有边指向 S，也没有边从 T 指出，没有边从 S 到 T
    for i in range(len(node_names)):
        for j in range(i + 1, len(node_names)):
            if random.random() > 0.7:
                if i == node_index["T"] or j == node_index["S"] or (i == node_index["S"] and j == node_index["T"]):
                    continue
                if not g.are_adjacent(i, j) and not g.are_adjacent(j, i):
                    g.add_edges([(i, j)] if i < j else [(j, i)])
    
    # 检查有无最小环（两条边构成的），如果有，仅保留其中一条边
    for edge in g.es:
        source, target = edge.tuple
        if g.are_adjacent(target, source):
            if source == "S" or target == "T":
                continue
            g.delete_edges(edge)
    
    return g

def add_weights(g, node_names, seed=None, monotonic=False):
    if seed is not None:
        random.seed(seed)
    
    num_nodes = g.vcount()
    node_index = {name: i for i, name in enumerate(node_names)}

    h_values = {node_name: random.randint(1, 10) for node_name in node_names if node_name != "T" and node_name != "S"}
    h_values["S"] = 10
    h_values["T"] = 0
    new_h_values = [float("inf") for _ in range(num_nodes)]
    for key, value in h_values.items():
        new_h_values[node_index[key]] = value
    g.vs["h"] = new_h_values

    if not monotonic:
        edge_weights = [random.randint(1, 10) for _ in range(g.ecount())]
        g.es["weight"] = edge_weights
    else:
        for edge in g.es:
            source, target = edge.tuple
            edge["weight"] = random.randint(1, max(2, g.vs[source]["h"] - g.vs[target]["h"] + 1))

    g.vs["name"] = node_names

    return g

# ========================================================================
# 使用修改A*算法求解最短路径
# ========================================================================

def modified_a_star(g, start, goal):
    # 初始化
    g.vs["f"] = float("inf")
    g.vs["g"] = float("inf")
    g.vs["parent"] = None
    
    start_index = g.vs.find(name=start).index
    goal_index = g.vs.find(name=goal).index
    
    g.vs[start_index]["f"] = g.vs[start_index]["h"]
    g.vs[start_index]["g"] = 0
    
    open_set = [start_index]
    closed_set = []
    f_m = 0

    print_str = "|Nest|Open set \\ Nest|Closed set|f_m\n"
    print_str += "|-|-|-|-|\n"
    # print_str += "|S(0+"+str(g.vs[start_index]["h"])+")|||" + str(f_m) + "|\n"
    
    while open_set:
        nest = [x for x in open_set if g.vs[x]["f"] < f_m]
        nest = sorted(nest, key=lambda x: g.vs[x]["g"])
        open_set = sorted(open_set, key=lambda x: g.vs[x]["f"])
        if len(nest) > 0:
            current_index = min(nest, key=lambda x: g.vs[x]["g"])
        else:
            current_index = min(open_set, key=lambda x: g.vs[x]["f"])
            f_m = g.vs[current_index]["f"]
        current_node = g.vs[current_index]

        print_str += "|"
        for node_index in nest:
            if node_index == current_index:
                print_str += "<u>" + g.vs[node_index]["name"] + "(" + str(g.vs[node_index]["g"]) + "+" + str(g.vs[node_index]["h"]) + ")</u>"
            else:
                print_str += g.vs[node_index]["name"] + "(" + str(g.vs[node_index]["g"]) + "+" + str(g.vs[node_index]["h"]) + ")"
        print_str += "|"
        for node_index in open_set:
            if node_index not in nest:
                if node_index == current_index:
                    print_str += "<u>" + g.vs[node_index]["name"] + "(" + str(g.vs[node_index]["g"]) + "+" + str(g.vs[node_index]["h"]) + ")</u>"
                else:
                    print_str += g.vs[node_index]["name"] + "(" + str(g.vs[node_index]["g"]) + "+" + str(g.vs[node_index]["h"]) + ")"
        print_str += "|"
        
        if current_index == goal_index:
            # 找到最短路径
            path = []
            while current_node is not None:
                path.append(current_node["name"])
                current_node = current_node["parent"]
            path.reverse()
            print_str += "||\n"
            return path, print_str
        
        open_set.remove(current_index)
        closed_set.append(current_index)
        
        for node_index in closed_set:
            print_str += g.vs[node_index]["name"] + "(" + str(g.vs[node_index]["g"]) + "+" + str(g.vs[node_index]["h"]) + ")"
        print_str += "|" + str(f_m) + "|\n"
        
        for neighbor_index in g.neighbors(current_index, mode="out"):
            neighbor = g.vs[neighbor_index]
            tentative_g = g.vs[current_index]["g"] + g.es[g.get_eid(current_index, neighbor_index)]["weight"]
            
            if tentative_g < neighbor["g"]:
                neighbor["parent"] = current_node
                neighbor["g"] = tentative_g
                neighbor["f"] = neighbor["g"] + neighbor["h"]
                
                if neighbor_index not in open_set:
                    open_set.append(neighbor_index)
                if neighbor_index in closed_set:
                    closed_set.remove(neighbor_index)
    
    return None, print_str

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--monotonic", action="store_true", help="Use monotonic heuristic")
    args = parser.parse_args()

    node_names = ["S", "A", "B", "C", "D", "E", "T"]

    if args.seed is not None:
        seed = args.seed
    else:
        seed = int(time.time())
    print(f"Random seed: {seed}")
    dag = generate_random_dag(node_names, seed=seed)
    dag = add_weights(dag, node_names, seed=seed, monotonic=args.monotonic)

    print("Nodes with weights (h):")
    for i in range(dag.vcount()):
        print(f"Node {dag.vs[i]['name']}: h={dag.vs[i]['h']}")

    print("\nEdges with weights:")
    for edge in dag.es:
        source, target = edge.tuple
        print(f"Edge {dag.vs[source]['name']} -> {dag.vs[target]['name']}: weight={edge['weight']}")

    layout = dag.layout("fr")
    plot(
        dag,
        layout=layout,
        vertex_label=[f"{dag.vs[i]['name']}\n(h={dag.vs[i]['h']})" for i in range(dag.vcount())],
        edge_label=dag.es["weight"],
        bbox=(600, 600),
        margin=50,
        target=f"./img/a_star_{seed}.png"
    )

    start = "S"
    goal = "T"
    path, print_str = modified_a_star(dag, start, goal)
    print_str += f"\nShortest path from {start} to {goal}: {path}"

    with open(f"./img/a_star_{seed}_sol.md", "w") as f:
        f.write(print_str)