from igraph import Graph, EdgeSeq
import random
from math import inf, isinf
import plotly.graph_objects as go
import time
import json
from attrdict import AttrDict
import pathlib
import os
from tqdm import tqdm

with open("settings.json", "r") as f:
    settings = json.load(f)
    assert "tree" in settings
    settings = AttrDict(settings["tree"])

sd = settings["seed"] if "seed" in settings else int(time.time())
print("Current random seed", sd)
random.seed(sd)

clipped = []
Xpos = {}

def adj(graph: Graph, node: int):
    ret = []
    for idx, val in enumerate(graph.get_adjacency()[node]):
        if val == 1:
            ret += [idx]

    ret = sorted(ret, key=lambda x: Xpos[x])
    return ret


def children(anc, adjs):
    ret = list(filter(lambda x: not ((x, True) in anc or (x, False) in anc), adjs))
    if settings.debug:
        print("ancestor", anc)
        print("adj", adjs)
    return ret


def alpha_beta(g: Graph, node: int, anc: list, is_max: bool = True):
    global clipped
    glob_clip = False
    for ch in children(anc, adj(g, node)):
        if glob_clip:
            clipped += [(node, ch)]
            continue
        rw = alpha_beta(g, ch, anc + [(node, is_max)], not is_max)
        if settings.debug:
            print(rw, anc)
        if is_max:  # Max
            if isinf(G.vs[node]["reward"]):
                G.vs[node]["reward"] = rw
            else:
                G.vs[node]["reward"] = max(G.vs[node]["reward"], rw)
            clip = False
            for nd, tp in anc:
                if tp == False and not isinf(G.vs[nd]["reward"]) and G.vs[node]["reward"] >= G.vs[nd]["reward"]:
                    clip = True
                    break
        else:  # Min
            if isinf(G.vs[node]["reward"]):
                G.vs[node]["reward"] = rw
            else:
                G.vs[node]["reward"] = min(G.vs[node]["reward"], rw)
            clip = False
            for nd, tp in anc:
                if tp == True and not isinf(G.vs[nd]["reward"]) and G.vs[node]["reward"] <= G.vs[nd]["reward"]:
                    clip = True
                    break
        if clip:
            glob_clip = True
    return g.vs[node]["reward"]

def leaves(graph: Graph):
    l_c = 0
    for v in range(1, len(graph.vs)):
        if graph.vs[v].degree() == 1:
            l_c += 1
    return l_c

def conditional_gen():
    while True:
        deletions = 0
        n_vertices = int((settings.max_ch ** settings.layers - 1) / (settings.max_ch - 1))
        _G = Graph.Tree(n_vertices, settings.max_ch)

        def cascade_del(_del, graph: Graph, node: int) -> Graph:
            assert node
            graph = graph - node
            _del += 1
            paths = graph.shortest_paths(0)[0]
            tbd = []
            for idx, p in enumerate(paths):
                if isinf(p):
                    tbd += [idx]
            graph = graph - tbd
            _del += len(tbd)
            return _del, graph

        print("Shaping...")
        l_count = leaves(_G)
        bar = tqdm(total=l_count-settings.max_leaves)
        while l_count > settings.max_leaves:
            rml = random.randint(settings.max_ch, len(_G.vs) - 1)
            deletions, _G = cascade_del(deletions, _G, rml)
            now_l_count = leaves(_G)
            bar.update(l_count-now_l_count)
            l_count = now_l_count
            if settings.debug:
                print(l_count, len(_G.vs))
        bar.close()
        n_vertices -= deletions
        assert n_vertices == len(_G.vs)

        return _G, n_vertices

def avg_br(g: Graph):
    dgs = 0
    for i in range(len(g.vs)):
        if i == 0:
            dgs += g.vs[i].degree()
        elif g.vs[i].degree() != 1:
            dgs += g.vs[i].degree() - 1
    return dgs / (len(G.vs) - leaves(G))


while True:
    G, n_vertices = conditional_gen()
    best_points = []
    best_clipped = []
    succ = False
    print("Average Branch", avg_br(G))
    print("Assigning...")
    time.sleep(0.1)
    for trial in tqdm(range(200)):
        points = []
        clipped = []
        Xpos = {}
        for i in range(n_vertices):
            if G.vs[i].degree() == 1 and i != 0:
                points += [random.randint(-10, 10)]
            else:
                points += [inf]

        G.vs["reward"] = points
        G.vs["name"] = range(len(G.vs))

        layout = G.layout('tree', root=[G.vs.find(name=0).index])
        Xpos = {k: layout[k][1] for k in range(n_vertices)}
        alpha_beta(G, 0, [], True)
        # print(len(clipped))
        if len(clipped) > len(best_clipped):
            best_points = G.vs["reward"]
            best_clipped = clipped
    if len(best_clipped) >= settings.min_clip:
        clipped = best_clipped
        points = best_points
        G.vs["reward"] = best_points
        if settings.debug:
            print(clipped)
        break
    else:
        print("No available assignment sample, retry")

print(f"{n_vertices} Nodes")
if settings.show_clip_count:
    print(f"{len(clipped)} Clips")

if settings.debug:
    print(G.vs["reward"])

print("Plotting...")


def draw(tp):
    lay = layout
    position = {k: (lay[k][0], lay[k][1]) for k in range(n_vertices)}
    Y = [lay[k][1] for k in range(n_vertices)]
    M = max(Y)

    es = EdgeSeq(G)
    E = [e.tuple for e in G.es]

    L = len(position)

    fig = go.Figure()
    border = dict(color='rgb(0,0,0)', width=6)
    edge_line = dict(color='rgb(0,0,0)', width=6)
    cut_line = {**edge_line, "dash": "dash", "color": "rgb(255,0,0)"}
    if tp:
        Xr, Yr, Xe, Ye = [], [], [], []
        for edge in E:
            # if isinf(G.vs[edge[0]]["reward"]) or isinf(G.vs[edge[1]]["reward"]):
            if edge in clipped or tuple(reversed(edge)) in clipped:
                if edge[0] == 0 or edge[1] == 0:
                    print("Fatal!", sd)
                Xe += [position[edge[0]][0], position[edge[1]][0], None]
                Ye += [2 * M - position[edge[0]][1], 2 * M - position[edge[1]][1], None]
            else:
                Xr += [position[edge[0]][0], position[edge[1]][0], None]
                Yr += [2 * M - position[edge[0]][1], 2 * M - position[edge[1]][1], None]
        if settings.debug:
            print(Xr, Yr, Xe, Ye)
        fig.add_trace(go.Scatter(x=Xr,
                                 y=Yr,
                                 mode='lines',
                                 line=edge_line,
                                 hoverinfo='none'
                                 ))
        fig.add_trace(go.Scatter(x=Xe,
                                 y=Ye,
                                 mode='lines',
                                 line=cut_line,
                                 hoverinfo='none'
                                 ))
    else:
        Xe = []
        Ye = []
        for edge in E:
            Xe += [position[edge[0]][0], position[edge[1]][0], None]
            Ye += [2 * M - position[edge[0]][1], 2 * M - position[edge[1]][1], None]
        fig.add_trace(go.Scatter(x=Xe,
                                 y=Ye,
                                 mode='lines',
                                 line=edge_line,
                                 hoverinfo='none'
                                 ))

    # plot nodes
    if settings.distinguish_max_min:
        Xmax = []
        Xmin = []
        Ymax = []
        Ymin = []
        for k in range(0, L):
            path = G.get_shortest_paths(0, k)[0]
            # print(len(path))
            if len(path) % 2 == 1:
                Xmax += [position[k][0]]
                Ymax += [2 * M - position[k][1]]
            else:
                Xmin += [position[k][0]]
                Ymin += [2 * M - position[k][1]]
        fig.add_trace(go.Scatter(x=Xmax,
                                 y=Ymax,
                                 mode='markers',
                                 name='bla',
                                 marker=dict(symbol='square',
                                             size=64,
                                             color='#FFF',
                                             line=border
                                             ),
                                 hoverinfo='text',
                                 opacity=1
                                 ))
        fig.add_trace(go.Scatter(x=Xmin,
                                 y=Ymin,
                                 mode='markers',
                                 name='bla',
                                 marker=dict(symbol='circle',
                                             size=64,
                                             color='#FFF',
                                             line=border
                                             ),
                                 hoverinfo='text',
                                 opacity=1
                                 ))
    else:
        Xn = [position[k][0] for k in range(0, L)]
        Yn = [2 * M - position[k][1] for k in range(0, L)]
        fig.add_trace(go.Scatter(x=Xn,
                                 y=Yn,
                                 mode='markers',
                                 name='bla',
                                 marker=dict(symbol='circle',
                                             size=64,
                                             color='#FFF',
                                             line=border
                                             ),
                                 hoverinfo='text',
                                 opacity=1
                                 ))

    def make_annotations(pos, font_size=10, font_color='rgb(0,0,0)', ans=False):
        L = len(pos)
        annotations = []
        for k in range(L):
            if ans and not isinf(G.vs[k]["reward"]):
                annotations.append(
                    dict(
                        text=f'{G.vs[k]["reward"]}, {k}' if settings.debug else G.vs[k]["reward"],
                        x=pos[k][0], y=2 * M - position[k][1],
                        xref='x1', yref='y1',
                        font=dict(color=font_color, size=font_size),
                        showarrow=False)
                )
            elif G.degree()[k] == 1 and k != 0:
                annotations.append(
                    dict(
                        text=G.vs[k]["reward"],
                        x=pos[k][0], y=2 * M - position[k][1],
                        xref='x1', yref='y1',
                        font=dict(color=font_color, size=font_size),
                        showarrow=False)
                )
        return annotations

    axis = dict(showline=False,
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                )

    fig.update_layout(title=dict(
        text='剪完啦！' if tp else '让我剪剪！',
        x=0.5,
        # y = 0.90,
        xanchor='center',
        yanchor='top',
        # pad = dict(
        #            t = 0
        #           ),
        font=dict(
            size=64,
        )
    ),
        annotations=make_annotations(position, font_size=32, ans=tp),
        font_size=12,
        showlegend=False,
        xaxis=axis,
        yaxis=axis,
        margin=dict(l=80, r=80, b=80, t=150),
        # hovermode='closest',
        plot_bgcolor='rgb(248,248,248)',
        font={"size": 60}
    )
    save_path = pathlib.Path(settings.save_path)
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    if save_path.is_file():
        raise RuntimeError(f"{save_path} should be a directory")
    fig.write_image(save_path / (f"done_{sd}.jpg" if tp else f"todo_{sd}.jpg"), height=200 + 150 * settings.layers,
                    width=500 + 100 * leaves(G))


draw(True)
draw(False)
