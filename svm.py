from sympy import *
from math import inf
import json
from attrdict import AttrDict
import time
import random
import pathlib
import os
from IPython import embed


def dot(lhs: Array, rhs: Array):
    assert len(lhs) == len(rhs)
    return Matrix(lhs.reshape(len(lhs), 1)).T.dot(Matrix(rhs.reshape(len(rhs), 1)))


def is_valid(stag):
    if type(stag) == list:
        if len(stag) == 0:
            return False
        stag = stag[0]

    for variable, value in stag.items():
        if value < 0:
            return False
    return True


def min_solutions(s: list):
    min_v = inf
    min_s = []
    for vars, value in s:
        if value.evalf() < min_v:
            min_v = value.evalf()
            min_s = [vars]
        elif value.evalf() == min_v:
            min_s += [vars]
    return min_s, min_v


class Template:
    def __get_case(self):
        flag1, flag2, repl = "[begin_case]", "[end_case]", "[cases]"
        left = self.template.rfind(flag1)
        right = self.template.rfind(flag2)
        if left != -1:
            self.case_template = self.template[left + len(flag1): right]
            self.render_result = self.template[:left] + repl + self.template[right + len(flag2):]
        else:
            self.render_result = self.template
        self.case = []

    def __init__(self, file_path, save_path):
        with open(file_path, "r", encoding="utf-8") as tf:
            self.template = tf.read()
            self.render_result = ""
            self.tmp = ""
            self.case = []
            self.__get_case()
        self.save_path = save_path

    def render(self, name, value):
        if type(value) == list:
            value = "\n".join(value)

        if self.tmp:
            self.tmp = self.tmp.replace(f"[{name}]", str(value))
        self.render_result = self.render_result.replace(f"[{name}]", str(value))

    def save(self):
        self.render("cases", "\n".join(self.case))
        with open(self.save_path, "w", encoding="utf-8") as f:
            f.write(self.render_result)

    def begin(self):
        self.tmp = self.case_template

    def commit(self):
        self.case += [self.tmp]
        self.tmp = ""

    def __call__(self, *args, **kwargs):
        self.render(*args, **kwargs)


class MultipleRender:
    def __init__(self, temps):
        self.templates = temps

    def __call__(self, *args, **kwargs):
        for t in self.templates:
            t.render(*args, **kwargs)

    def save(self):
        for t in self.templates:
            t.save()


if __name__ == "__main__":
    with open("settings.json", "r") as f:
        settings = json.load(f)
        assert "svm" in settings
        settings = AttrDict(settings["svm"])

    save_path = pathlib.Path('doc')
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    if save_path.is_file():
        raise RuntimeError(f"{save_path} should be a directory")

    if settings.random:
        # sd = int(time.time())
        sd = 1655128848
        print("Current random seed", sd)
        random.seed(sd)
        problem = Template("template/svm_problem.md", f"doc/svm_problem_{sd}.md")
        solution = Template("template/svm_solution.md", f"doc/svm_solution_{sd}.md")
        R = MultipleRender([problem, solution])
        train = []
        labels = []
        if random.randint(0, 1) == 1:
            labels = [1, 1, -1]
        else:
            labels = [1, -1, -1]

        for label in labels:
            train += [{
                "x": Array([
                    random.randint(-settings.range, settings.range),
                    random.randint(-settings.range, settings.range)
                ]),
                "y": label
            }]

        K = random.choice(settings.kernels)
        # print(K["repr"])
        exec(K["repr"])
        R('kernel', K['str'])
        assert kernel

        sample = Array([
            random.randint(-settings.range, settings.range),
            random.randint(-settings.range, settings.range)
        ])
    else:
        problem = Template("template/svm_problem.md", "doc/p.md")
        solution = Template("template/svm_solution.md", "doc/s.md")
        R = MultipleRender([problem, solution])


        def kernel(lhs: Array, rhs: Array):
            assert len(lhs) == len(rhs)
            return dot(lhs, rhs)


        K = {
            "str": "x^Ty"
        }

        train = [
            {"x": Array([0, 0]), "y": 1},
            {"x": Array([1, 1]), "y": -1},
            {"x": Array([-1, -1]), "y": -1},
        ]

        sample = Array([0, 1])
        R('kernel', K['str'])

    R("n", len(train))

    R("positive_vectors",
      "\ ,".join([
          f"x_{rank + 1}={latex(ex['x'])}"
          for rank, ex in filter(lambda ob: ob[1]["y"] > 0, enumerate(train))
      ]))

    R("negative_vectors",
      "\ ,".join([
          f"x_{rank + 1}={latex(ex['x'])}"
          for rank, ex in filter(lambda ob: ob[1]["y"] < 0, enumerate(train))
      ]))

    R("sample_point", latex(sample))

    # R("kernel", "(1+x^Ty)^2")

    assert len(train) == 3

    rng1 = range(1, len(train) + 1)
    rng0 = range(len(train))

    var = []
    eval_string = ""
    for i in rng1:
        var += [f'alpha{i}']
    eval_string = ' '.join(var)
    var = symbols(eval_string)

    f = Integer(0)
    for alpha_i in var:
        f -= alpha_i

    for i in rng0:
        for j in rng0:
            f += Rational(1, 2) * var[i] * var[j] * train[i]["y"] * train[j]["y"] * kernel(train[i]["x"], train[j]["x"])

    f = f.simplify()
    R("f_simplified", latex(f))

    con = Integer(0)
    for i in rng0:
        con += var[i] * train[i]["y"]

    # nabla phi
    dc = []
    for i in rng0:
        dc += [train[i]["y"]]

    R("dphi", latex(Matrix(dc)))

    # nabla f
    df = []
    for i in rng0:
        df += [diff(f, var[i])]

    R("df", latex(Matrix(df)))

    # lagrange method
    lag_eqs = [df[0] / dc[0] - df[1] / dc[1],
               df[1] / dc[1] - df[2] / dc[2],
               con]
    stagnation = solve(lag_eqs, var, dict=True)
    R("lagrange_eqs", [latex(eq) + r"&=0 \\" for eq in lag_eqs])

    solutions = []

    if is_valid(stagnation):
        stagnation = stagnation[0]
        solutions += [(stagnation, f.subs(stagnation))]
        R("solutions_for_lag_eqs", f"解得\n$$\n {latex(stagnation)} \n$$ \n 此时 $f$ 的值为 ${f.subs(stagnation)}$。")
    else:
        if len(stagnation):
            R("solutions_for_lag_eqs", f"""解得 \n$$\n {latex(stagnation[0])} \n$$ \n解不满足约束条件。""")
        else:
            R("solutions_for_lag_eqs", "无解。")

    # border situations
    for idx, border in enumerate(var):
        solution.begin()
        pf = f.subs(border, 0).simplify()
        pcon = con.subs(border, 0).simplify()
        left_var = list(set(var).intersection(pf.atoms()))
        solution("case_number", str(idx + 1))
        solution("cons_v", latex(border))
        solution("f_after_cons", latex(pf))

        dpf = [pcon, pf.diff(left_var[0]) / pcon.diff(left_var[0]) - pf.diff(left_var[1]) / pcon.diff(left_var[1])]

        # print("dpf", dpf)
        solution("grad_eqs", [latex(eq) + r"&=0 \\" for eq in dpf])
        stagnation = solve(dpf, left_var)

        # print(stagnation)

        if is_valid(stagnation):
            solutions += [({**stagnation, border: 0}, pf.subs(stagnation))]
            solution("solutions_for_grad_eqs",
                     f"解得\n$$\n {latex(stagnation)} \n$$ \n 此时 $f_{{{latex(border)}}}$ 的值为 ${pf.subs(stagnation)}$。")
        else:
            if stagnation:
                R("solutions_for_grad_eqs", f"""解得 \n$$\n {latex(stagnation)} \n$$ \n 解不满足约束条件。""")
            else:
                R("solutions_for_grad_eqs", "无解。")
        solution.commit()

    # print_latex(solutions)
    # solutions = sorted(solutions)

    def eq(s1, s2):
        if s1[1] != s2[1]:
            return False

        for ik, iv in s1[0].items():
            if s2[0][ik] != iv:
                return False
        return True

    # embed()

    while True:
        for ss1 in solutions:
            for ss2 in solutions:
                if eq(ss1, ss2) and ss1 is not ss2:
                    solutions.remove(ss1)
                    continue
        break

    # embed()

    var_choice, min_value = min_solutions(solutions)

    result = ""

    for vars in var_choice:
        result += "\n   - 取\n$$\n"
        result += latex(vars)
        result += "\n$$\n时，决策函数为\n$$\ng(\\vec{x})=\\text{sign}\\left("
        b_asterisk = inf
        x_j = None

        for v, val in vars.items():
            if val != 0:
                b_asterisk = train[int(str(v)[-1:]) - 1]["y"]
                x_j = train[int(str(v)[-1:]) - 1]["x"]
                break
        for idx, (v, val) in enumerate(vars.items()):
            if val == 0:
                continue
            if val * train[int(str(v)[-1:]) - 1]["y"] > 0 and idx != 0:
                result += "+"
            result += latex(val * train[int(str(v)[-1:]) - 1]["y"])
            result += r"K\left("
            result += latex(train[int(str(v)[-1:]) - 1]["x"])
            result += r", \vec{x}\right)"
            b_asterisk -= val * train[int(str(v)[-1:]) - 1]["y"] * kernel(x_j, train[int(str(v)[-1:]) - 1]["x"])

        if b_asterisk != 0:
            if b_asterisk > 0:
                result += "+"
            result += latex(b_asterisk)
        result += "\\right)\n$$\n"

        judgement = b_asterisk
        for v, val in vars.items():
            judgement += val * train[int(str(v)[-1:]) - 1]["y"] * kernel(sample, train[int(str(v)[-1:]) - 1]["x"])

        result += f"\n对于 ${latex(sample)}$ ，符号函数内的计算结果为 ${judgement}$，\n\n"

        if judgement > 0:
            result += "此时 $" + latex(sample) + "$ 为正类"
        elif judgement < 0:
            result += "此时 $" + latex(sample) + "$ 为负类"
        else:
            result += "此时无法给 $" + latex(sample) + "$ 分类"

        result += "\n"

    R("endings", result)
    R.save()
