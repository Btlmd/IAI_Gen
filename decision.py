from collections import Counter
from math import log2
from igraph import Graph, EdgeSeq
import random
from math import inf, isinf
import plotly.graph_objects as go
import time
import json
from attrdict import AttrDict
import pathlib
import os
from copy import deepcopy

epsilon = -inf

class Tree:
    def __init__(self, init_set=None, from_val=None):
        if init_set is None:
            init_set = []  # (trait: dict, class: str)
        self.set = init_set
        self.tag = None
        self.from_val = from_val
        self.which = None
        self.children = []
        self.gain = 0

    def __or__(self, other):
        return self, other, "given"

    def __len__(self):
        return len(self.set)

    def __matmul__(self, other):
        return self, other, "split"

    def max_class(self):
        cls = Counter(map(lambda x: x[1], self.set))
        return cls.most_common(1)[0][0]

    def set_gain(self, gain):
        self.gain = gain

    def set_tag(self, A):
        self.tag = A

    def set_from(self, A):
        self.from_val = A

    def set_which(self, A):
        self.which = A

    def cls_cnt(self):
        return len(Counter(map(lambda x: x[1], self.set)))

    def split_with(self, A):
        classes = {}
        for trait, cls in self.set:
            if trait[A] not in classes:
                classes[trait[A]] = [(trait, cls)]
            else:
                classes[trait[A]] += [(trait, cls)]

        for i in A.values:
            if i not in classes:
                classes[i] = []
        return classes

    def add_children(self, ch):
        self.children = ch

    def to_graph(self, base: Graph = None, this=None) -> Graph:
        if base is None:
            base = Graph(directed=True)
            this = base.add_vertex(which=self.which, tag=self.tag, gain=self.gain)
        for ch in self.children:
            v = base.add_vertex(which=ch.which, tag=ch.tag, gain=ch.gain)
            base.add_edge(this, v, case=ch.from_val)
            ch.to_graph(base, v)
        base.vs["name"] = range(len(base.vs))
        return base

class Trait(str):
    values = []

def H(_D):
    if type(_D) == tuple:
        D, A, mode = _D
        if mode == "given":
            total = len(D)
            classes = D.split_with(A)
            classes = [Tree(init_set=objs) for _, objs in classes.items()]
            entropy = map(H, classes)
            h = 0
            for c, e in zip(map(lambda x: len(x) / total, classes), entropy):
                h += c * e
            return h
        elif mode == "split":
            total = len(D)
            cnt = map(lambda x: len(x[1]) / total, D.split_with(A).items())
            h = 0
            for p in cnt:
                if p == 0:
                    continue
                h += -p * log2(p)
            return h

    assert type(_D) == Tree
    D = _D
    total = len(D)
    D = map(lambda x: x[1], D.set)
    cnt = Counter(D)
    cnt = map(lambda x: x[1] / total, cnt.items())
    h = 0
    for p in cnt:
        h += -p * log2(p)
    return h


def generate(D: Tree, A: list, algo: str = "ID3"):
    class_cnt = D.cls_cnt()
    if class_cnt == 1:
        D.set_tag(D.max_class())
        return D
    if len(A) == 0:
        D.set_tag(D.max_class())
        return D

    if algo == "ID3":
        gains = [(H(D) - H(D | a), a) for a in A]
    elif algo == "C4.5":
        gains = [((H(D) - H(D | a)) / H(D @ a), a) for a in A]
    else:
        raise NotImplemented

    A_gs = sorted(gains, key=lambda x: x[0], reverse=True)
    global infos
    infos += [A_gs]

    # D.set_gain(A_gs)
    A_g = A_gs[0]

    if A_g[0] < epsilon:
        D.set_tag(D.max_class())
        return D

    A_g = A_g[1]
    D.set_which(A_g)

    division = [Tree(init_set=objs, from_val=val) for val, objs in D.split_with(A_g).items()]
    D.add_children(division)
    A.remove(A_g)
    for d in division:
        if len(d):
            generate(d, A, algo)
        else:
            d.set_tag(D.max_class())


def draw(G: Graph):
    print(G)
    lay = G.layout('tree', root=[G.vs.find(name=0).index])
    position = {k: (lay[k][0], lay[k][1]) for k in range(len(G.vs))}
    Y = [lay[k][1] for k in range(len(G.vs))]
    M = max(Y)

    es = EdgeSeq(G)
    E = [(e.tuple, e["case"]) for e in G.es]

    L = len(position)

    fig = go.Figure()
    border = dict(color='rgb(0,0,0)', width=6)
    edge_line = dict(color='rgb(0,0,0)', width=6)

    Xe = []
    Ye = []
    MdpX = []
    MdpY = []
    from_vals = []

    for edge, from_val in E:
        Xe += [position[edge[0]][0], position[edge[1]][0], None]
        Ye += [2 * M - position[edge[0]][1], 2 * M - position[edge[1]][1], None]
        MdpX += [sum(Xe[-3: -1]) / 2]
        MdpY += [sum(Ye[-3: -1]) / 2]
        from_vals += [from_val]
    fig.add_trace(go.Scatter(x=Xe,
                             y=Ye,
                             mode='lines',
                             line=edge_line,
                             hoverinfo='none',
                             text="edge"
                             ))

    fig.add_trace(go.Scatter(
        x=MdpX, y=MdpY, mode="markers+text", marker=dict(symbol='circle',
                                         size=45,
                                         color='#FFF',
                                         line=border
                                         ), text=from_vals, opacity=0.7
    ))

    Xn = [position[k][0] for k in range(0, L)]
    Yn = [2 * M - position[k][1] for k in range(0, L)]
    fig.add_trace(go.Scatter(x=Xn,
                             y=Yn,
                             mode='markers',
                             name='bla',
                             marker=dict(symbol='square',
                                         size=64,
                                         color='#FFF',
                                         line=border
                                         ),
                             hoverinfo='text',
                             opacity=1,
                             # text="text"
                             ))

    def make_annotations(pos, font_size=10, font_color='rgb(0,0,0)'):
        L = len(pos)
        annotations = []
        for k in range(L):
            caption = G.vs[k]["tag"] if G.vs[k]["tag"] else G.vs[k]["which"]
            # if G.vs[k]["gain"]:
            #     caption += f' {G.vs[k]["gain"]}'
            # print(caption)
            annotations.append(
                dict(
                    text=caption,
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
        text='决策树',
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
        annotations=make_annotations(position, font_size=32),
        font_size=12,
        showlegend=False,
        xaxis=axis,
        yaxis=axis,
        margin=dict(l=80, r=80, b=80, t=150),
        # hovermode='closest',
        plot_bgcolor='rgb(248,248,248)',
        font={"size": 32}
    )
    save_path = pathlib.Path(settings.save_path)
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    if save_path.is_file():
        raise RuntimeError(f"{save_path} should be a directory")
    fig.write_image(save_path / (f"decision_tree_{sd}.jpg"), height=1000,
                    width=1000)


if __name__ == "__main__":
    with open("settings.json", "r") as f:
        settings = json.load(f)
        assert "decision" in settings
        settings = AttrDict(settings["decision"])

    sd = int(time.time())
    # sd = 1655139803
    print("Current seed", sd)
    random.seed(sd)

    infos = []

    traits = []
    subclass_cnt = []
    for j in range(settings.trait_cnt):
        tr = Trait(f"A{j + 1}")
        tr.values = list(range(1, random.choice(settings.subclass_range) + 1))
        traits += [tr]
        subclass_cnt += [tr.values[-1]]

    pool = []
    for i in range(settings.set_size):
        trait = {}
        for tr in traits:
            trait[tr] = random.choice(tr.values)
        pool += [(trait, random.randint(1, settings.class_cnt))]

    root = Tree(init_set=pool)
    _traits = deepcopy(traits)
    generate(root, _traits, algo=settings.algo)
    # print(root.to_graph())
    draw(root.to_graph())

    generating_process = '\n\n'.join(map(str, infos))

    bar = ["ID"] + traits + ["Class"]
    spl = "|-" * len(bar) + "|"
    content = [f"|{idx}|" + "|".join(map(lambda x: str(x[1]), trs.items())) + f"|{cls}|" for idx, (trs, cls) in enumerate(pool)]
    training_set = f"|{'|'.join(bar)}|" + "\n" + spl + "\n" + '\n'.join(content)

    template = f"""
## Decision Tree

### Training Set

{training_set}

### Generating Process
{generating_process}

### Generated Tree
![decision_tree](../img/decision_tree_{sd}.jpg)
    
"""
    with open(f"doc/decision_tree_{sd}.md", "w", encoding="utf-8") as f:
        f.write(template)


