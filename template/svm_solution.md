## 二元SVM 解答
求解该 SVM，就是在约束
$$
\begin{cases} 
\phi=\sum\limits_{i=1}^{[n]}\alpha_iy_i=0  \\
\alpha_i\geq0,\ i\in\{1,\cdots,[n]\}
\end{cases}
$$
下，求解最值问题
$$
\min_{\alpha\in \mathbb{R}^{[n]}} \frac{1}{2} \sum_{i=1}^{[n]}\sum_{j=1}^{[n]}\alpha_i\alpha_jy_iy_jK(x_i,x_j)-\sum_{i=1}^{[n]}\alpha_i
$$
令
$$
\begin{aligned}
f&=\frac{1}{2} \sum_{i=1}^{[n]}\sum_{j=1}^{[n]}\alpha_i\alpha_jy_iy_jK(x_i,x_j)-\sum_{i=1}^{[n]}\alpha_i\\
&=[f_simplified]
\end{aligned}
$$
由 $Lagrange$ 乘子法，先求解驻点,有
$$
\nabla f \ // \ \nabla\phi
$$
其中
$$
\nabla f=[df],\ \nabla \phi=[dphi]
$$
结合 $\phi=0$，得到方程租
$$
\begin{aligned}
[lagrange_eqs]
\end{aligned}
$$
[solutions_for_lag_eqs]

再来看边界的情况。

[begin_case]

**Case [case_number]**  令 $[cons_v]=0$，化简得
$$
f_{[cons_v]}=[f_after_cons]
$$
 令 $\nabla f=\textbf{0}$ ，有
$$
\begin{aligned}
[grad_eqs]
\end{aligned}
$$
[solutions_for_grad_eqs]

[end_case]

[endings]
