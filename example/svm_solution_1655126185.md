## 二元SVM 解答
求解该 SVM，就是在约束
$$
\begin{cases} 
\phi=\sum\limits_{i=1}^{3}\alpha_iy_i=0  \\
\alpha_i\geq0,\ i\in\{1,\cdots,3\}
\end{cases}
$$
下，求解最值问题
$$
\min_{\alpha\in \mathbb{R}^{3}} \frac{1}{2} \sum_{i=1}^{3}\sum_{j=1}^{3}\alpha_i\alpha_jy_iy_jK(x_i,x_j)-\sum_{i=1}^{3}\alpha_i
$$
令
$$
\begin{aligned}
f&=\frac{1}{2} \sum_{i=1}^{3}\sum_{j=1}^{3}\alpha_i\alpha_jy_iy_jK(x_i,x_j)-\sum_{i=1}^{3}\alpha_i\\
&=10 \alpha_{1}^{2} - 2 \alpha_{1} \alpha_{2} - 8 \alpha_{1} \alpha_{3} - \alpha_{1} + \alpha_{2}^{2} + 8 \alpha_{2} \alpha_{3} - \alpha_{2} + 16 \alpha_{3}^{2} - \alpha_{3}
\end{aligned}
$$
由 $Lagrange$ 乘子法，先求解驻点,有
$$
\nabla f \ // \ \nabla\phi
$$
其中
$$
\nabla f=\left[\begin{matrix}20 \alpha_{1} - 2 \alpha_{2} - 8 \alpha_{3} - 1\\- 2 \alpha_{1} + 2 \alpha_{2} + 8 \alpha_{3} - 1\\- 8 \alpha_{1} + 8 \alpha_{2} + 32 \alpha_{3} - 1\end{matrix}\right],\ \nabla \phi=\left[\begin{matrix}1\\1\\-1\end{matrix}\right]
$$
结合 $\phi=0$，得到方程租
$$
\begin{aligned}
22 \alpha_{1} - 4 \alpha_{2} - 16 \alpha_{3}&=0 \\
- 10 \alpha_{1} + 10 \alpha_{2} + 40 \alpha_{3} - 2&=0 \\
\alpha_{1} + \alpha_{2} - \alpha_{3}&=0 \\
\end{aligned}
$$
解得
$$
 \left\{ \alpha_{1} : \frac{2}{45}, \  \alpha_{2} : \frac{1}{75}, \  \alpha_{3} : \frac{13}{225}\right\} 
$$ 
 此时 $f$ 的值为 $-13/225$。

再来看边界的情况。



**Case 1**  令 $\alpha_{1}=0$，化简得
$$
f_{\alpha_{1}}=\alpha_{2}^{2} + 8 \alpha_{2} \alpha_{3} - \alpha_{2} + 16 \alpha_{3}^{2} - \alpha_{3}
$$
 令 $\nabla f=\textbf{0}$ ，有
$$
\begin{aligned}
\alpha_{2} - \alpha_{3}&=0 \\
- 10 \alpha_{2} - 40 \alpha_{3} + 2&=0 \\
\end{aligned}
$$
解得
$$
 \left\{ \alpha_{2} : \frac{1}{25}, \  \alpha_{3} : \frac{1}{25}\right\} 
$$ 
 此时 $f_{\alpha_{1}}$ 的值为 $-1/25$。




**Case 2**  令 $\alpha_{2}=0$，化简得
$$
f_{\alpha_{2}}=10 \alpha_{1}^{2} - 8 \alpha_{1} \alpha_{3} - \alpha_{1} + 16 \alpha_{3}^{2} - \alpha_{3}
$$
 令 $\nabla f=\textbf{0}$ ，有
$$
\begin{aligned}
\alpha_{1} - \alpha_{3}&=0 \\
- 12 \alpha_{1} - 24 \alpha_{3} + 2&=0 \\
\end{aligned}
$$
解得
$$
 \left\{ \alpha_{1} : \frac{1}{18}, \  \alpha_{3} : \frac{1}{18}\right\} 
$$ 
 此时 $f_{\alpha_{2}}$ 的值为 $-1/18$。




**Case 3**  令 $\alpha_{3}=0$，化简得
$$
f_{\alpha_{3}}=10 \alpha_{1}^{2} - 2 \alpha_{1} \alpha_{2} - \alpha_{1} + \alpha_{2}^{2} - \alpha_{2}
$$
 令 $\nabla f=\textbf{0}$ ，有
$$
\begin{aligned}
\alpha_{1} + \alpha_{2}&=0 \\
- 22 \alpha_{1} + 4 \alpha_{2}&=0 \\
\end{aligned}
$$
解得
$$
 \left\{ \alpha_{1} : 0, \  \alpha_{2} : 0\right\} 
$$ 
 此时 $f_{\alpha_{3}}$ 的值为 $0$。




   - 取
$$
\left\{ \alpha_{1} : \frac{2}{45}, \  \alpha_{2} : \frac{1}{75}, \  \alpha_{3} : \frac{13}{225}\right\}
$$
时，决策函数为
$$
g(\vec{x})=\text{sign}\left(\frac{2}{45}K\left(\left[\begin{matrix}-4 & 2\end{matrix}\right], \vec{x}\right)+\frac{1}{75}K\left(\left[\begin{matrix}1 & 1\end{matrix}\right], \vec{x}\right)- \frac{13}{225}K\left(\left[\begin{matrix}-4 & -4\end{matrix}\right], \vec{x}\right)+\frac{3}{5}\right)
$$

对于 $\left[\begin{matrix}-2 & 1\end{matrix}\right]$ ，符号函数内的计算结果为 $4/5$，

此时 $\left[\begin{matrix}-2 & 1\end{matrix}\right]$ 为正类

