# 第 7 章例题：固定点、混合稳定性与停止条件

本文件使用解析线性映射和两分量合成密度映射复核第 7 章的核心结论。所有数值均为 float64 后端无关教学对象，不代表真实材料、真实 SCF 后端或默认混合参数。

## 例 7-1 三维线性映射的精确稳定性

给定

\[
F(x)=Jx+b,\qquad
J=\operatorname{diag}(0.2,0.5,-0.4),\qquad
b=(0.3,-0.2,0.1)^T.
\]

固定点为

\[
x_*=(I-J)^{-1}b
=\left(0.375,-0.4,\frac1{14}\right)^T.
\]

线性混合

\[
x_{m+1}=x_m+\alpha(F(x_m)-x_m)
\]

的误差矩阵是

\[
M_\alpha=(1-\alpha)I+\alpha J.
\]

取 \(\alpha=0.8\)，

\[
M_{0.8}=\operatorname{diag}(0.36,0.60,-0.12),
\qquad
\rho(M_{0.8})=0.60.
\]

第三个模会交替衰减，第二个模决定渐近速率。以 \(x_0=0\) 迭代时，误差比的渐近值应趋近 0.6。若直接令 \(x_0=x_*\)，算法应在第 0 步返回零残差；此时没有相邻非零误差可用于估计速率，故 estimated_rate 应为 null，不能以 \(0/0\) 产生非有限值。

取 \(\alpha=2\)，

\[
M_2=\operatorname{diag}(-0.6,0,-1.8),
\qquad
\rho(M_2)=1.8.
\]

第三个误差模发散。该例同时说明：大于 1 的松弛参数不必然发散，但必须由映射的局部谱判断；不能把某个 \(\alpha\) 脱离 \(J_*\) 单独分类为“稳定”。

### 可执行复算

```python
import numpy as np

J = np.diag([0.2, 0.5, -0.4])
b = np.array([0.3, -0.2, 0.1], dtype=np.float64)
x_star = np.linalg.solve(np.eye(3) - J, b)

assert np.allclose(x_star, [0.375, -0.4, 1.0 / 14.0])

for alpha, expected_rho in [(0.8, 0.6), (2.0, 1.8)]:
    M = (1.0 - alpha) * np.eye(3) + alpha * J
    rho = np.max(np.abs(np.linalg.eigvals(M)))
    assert np.isclose(rho, expected_rho)

x = np.zeros(3)
errors = []
for _ in range(101):
    errors.append(np.linalg.norm(x - x_star))
    if errors[-1] < 1e-10:
        break
    x = x + 0.8 * (J @ x + b - x)

ratios = [
    errors[i + 1] / errors[i]
    for i in range(len(errors) - 1)
    if 1e-8 < errors[i] < 1e-3
]
assert errors[-1] < 1e-10
assert abs(float(np.median(ratios)) - 0.6) < 5e-3

x = np.zeros(3)
residuals = [np.linalg.norm(J @ x + b - x)]
updates = 12
for _ in range(updates):
    x = x + 2.0 * (J @ x + b - x)
    residuals.append(np.linalg.norm(J @ x + b - x))
assert updates == 12 and len(residuals) == 13
assert residuals[-1] > 10.0 * residuals[0]
```

## 例 7-2 两分量非线性密度映射

定义

\[
F_i(n)=
\frac{N_e\exp[-\beta(v_i+gn_i)]}
{\sum_j\exp[-\beta(v_j+gn_j)]},
\]

其中

\[
N_e=1,\quad
v=(-0.1,0.1)^T,\quad
g=4,\quad
\beta=1,\quad
n_0=(0.9,0.1)^T.
\]

指数采用减去最大指数的稳定 softmax 实现。映射 \(F\) 自动满足分量非负且和为 1；当 \(0\le\alpha\le1\) 时，线性混合也保持这些约束。残差定义为

\[
R_m=\frac{\|F(n_m)-n_m\|_2}{N_e}.
\]

对 \(\alpha=0.25\)，第 16 次更新前的状态已经满足

\[
n_{16}\approx(0.51666461,0.48333539)^T,\qquad
R_{16}\approx8.61\times10^{-10}.
\]

对 \(\alpha=1\) 固定执行 20 步，轨迹趋向两周期而不是固定点：

\[
n_{20}\approx(0.98198728,0.01801272)^T,\qquad
R_{20}\approx1.35312.
\]

两条轨迹都保持粒子数和非负性。因此约束保持是可行性条件，不是收敛证据。

### 可执行复算

```python
import numpy as np

v = np.array([-0.1, 0.1], dtype=np.float64)
g = 4.0
beta = 1.0
electron_count = 1.0

def density_map(n):
    logits = -beta * (v + g * n)
    weights = np.exp(logits - np.max(logits))
    return electron_count * weights / np.sum(weights)

def run(alpha, max_iter, tolerance):
    n = np.array([0.9, 0.1], dtype=np.float64)
    for iteration in range(max_iter + 1):
        output = density_map(n)
        residual = np.linalg.norm(output - n) / electron_count
        assert n.shape == (2,)
        assert np.all(np.isfinite(n))
        assert abs(np.sum(n) - electron_count) < 1e-12
        assert np.all(n > -1e-14)
        if residual < tolerance:
            return n, residual, iteration, True
        if iteration < max_iter:
            n = n + alpha * (output - n)
    return n, residual, max_iter, False

n_good, r_good, it_good, converged = run(0.25, 80, 1e-9)
assert converged and it_good == 16 and r_good < 1e-9

n_bad, r_bad, it_bad, converged = run(1.0, 20, 1e-9)
assert not converged and it_bad == 20 and r_bad > 1.3
```

## 例 7-3 能量单判据造成伪收敛

为例 7-2 定义教学能量

\[
E(n)=\frac12g\|n\|_2^2+v^Tn
\]

和相对变化

\[
D_m=\frac{|E_m-E_{m-1}|}{1+|E_m|}.
\]

如果故障记录器错误地输出

\[
E_m^{\mathrm{fake}}=10^{-12}E_m,
\]

则 \(\alpha=1\) 失败轨迹在第 1 步已经满足

\[
D_1^{\mathrm{fake}}\approx3.50\times10^{-13}<10^{-10},
\qquad
R_1\approx1.317>1.
\]

能量单判据会误报通过；冻结的双判据要求最终同时满足 \(D_m<10^{-9}\) 和 \(R_m<10^{-9}\)，因而必须拒绝该运行。该故障是缩放错误的教学注入，不应解释成真实 DFT 总能量具有这种数值行为。

```python
import numpy as np

v = np.array([-0.1, 0.1])
g = 4.0

def density_map(n):
    logits = -(v + g * n)
    weights = np.exp(logits - np.max(logits))
    return weights / np.sum(weights)

def energy(n):
    return 0.5 * g * np.dot(n, n) + np.dot(v, n)

n0 = np.array([0.9, 0.1])
n1 = density_map(n0)
r1 = np.linalg.norm(density_map(n1) - n1)
d_fake = abs(1e-12 * energy(n1) - 1e-12 * energy(n0))
d_fake /= 1.0 + abs(1e-12 * energy(n1))

assert d_fake < 1e-10
assert r1 > 1.0
assert not (d_fake < 1e-9 and r1 < 1e-9)
```

## 例 7-4 非正规矩阵的瞬态放大

考虑误差迭代

\[
e_{m+1}=Me_m,\qquad
M=
\begin{pmatrix}
0.5&20\\
0&0.5
\end{pmatrix}.
\]

两个特征值均为 0.5，所以 \(\rho(M)=0.5<1\)，并且 \(M^m\to0\)。但若 \(e_0=(0,1)^T\)，

\[
e_1=(20,0.5)^T,
\qquad
\frac{\|e_1\|_2}{\|e_0\|_2}>20.
\]

故谱半径判据只控制渐近行为；它不排除非正规矩阵造成的短时增长。实际算法还会受到非线性、高阶项、占据变化和有限精度影响，因此必须检查轨迹，而非只检查固定点处的本征值。

```python
import numpy as np

M = np.array([[0.5, 20.0], [0.0, 0.5]])
e = np.array([0.0, 1.0])
assert np.isclose(max(abs(np.linalg.eigvals(M))), 0.5)
assert np.linalg.norm(M @ e) / np.linalg.norm(e) > 20.0
assert np.linalg.norm(np.linalg.matrix_power(M, 200), ord=2) < 1e-50
```

## 例题的证据边界

例 7-1 的矩阵代数和例 7-4 的非正规瞬态为 `DIRECT_DERIVATION`；例 7-2—7-3 的映射和故障注入为 `PEDAGOGICAL`。这些例题验证固定点算法的共同结构，不支持任何真实材料或后端的最优混合参数结论。
