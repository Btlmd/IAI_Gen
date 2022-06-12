# IAI Gen
复习得是不是有点烦躁？练习题太少？这里提供批量生成人智导练习题的工具

```bash
pip install -r requirements.txt
```

## A* 算法

TODO

## Alpha-Beta 剪枝

随机生成一道 Alpha-Beta 剪枝题目及其解答。

```bash
python tree.py
```
运行后会根据 `settings.json` 中的配置，将题目和解答生成到 `img` 目录下。其中，`todo_**.jpg` 是题目，`done_**.jpg` 是解答，`**` 是生成是使用的随机数种子。

运行时，输出节点数和剪枝数。如果剪枝数太少，直接重新生成即可。

运行过程中输出
```bash
tree.py:93: RuntimeWarning: Couldn't reach some vertices at src/paths/unweighted.c:368
  path = graph.get_shortest_paths(0, nd)[0]
```
是预期内的行为。

## 决策树

TODO

## SVM

TODO

## 神经网络设计

TOOD

## 一套人智导期末试卷

TODO
