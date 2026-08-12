# 第 10 章例题：衰减、截断与表示依赖

本文件使用合成矩阵解释 T-C10 及其边界。索引距离不是实际原子距离，数值 cutoff 不构成真实材料建议。

## 例 10-1 指数与代数矩阵的截断三联表

令 \(N=64\)、\(R_{ij}=|i-j|\)，并定义

\[
A_{\exp}=e^{-R/2},
\qquad
A_{\mathrm{alg}}=(1+R)^{-1}.
\]

对 \(R_c=(2,4,8,16)\) 直接复算非零比例、相对 Frobenius 误差和

\[
y=A\mathbf1/N
\]

的相对作用量误差。指数族的误差随 cutoff 快速下降，而代数族保留明显长尾；同一非零比例不决定相同矩阵或作用量误差。

```python
import numpy as np

size = 64
index = np.arange(size)
distance = np.abs(index[:, None] - index[None, :])
matrices = {
    "exponential": np.exp(-distance / 2.0),
    "algebraic": 1.0 / (1.0 + distance),
}

records = {}
for name, matrix in matrices.items():
    records[name] = []
    exact_action = matrix @ np.ones(size) / size
    for cutoff in [2, 4, 8, 16]:
        truncated = matrix * (distance <= cutoff)
        sparsity = np.count_nonzero(truncated) / truncated.size
        matrix_error = np.linalg.norm(matrix - truncated, ord="fro")
        matrix_error /= np.linalg.norm(matrix, ord="fro")
        truncated_action = truncated @ np.ones(size) / size
        action_error = np.linalg.norm(exact_action - truncated_action)
        action_error /= np.linalg.norm(exact_action)
        records[name].append((cutoff, sparsity, matrix_error, action_error))

        assert np.isclose(
            sparsity, np.count_nonzero(truncated) / truncated.size, atol=1e-14
        )
        assert np.isclose(
            matrix_error,
            np.linalg.norm(matrix - truncated, ord="fro")
            / np.linalg.norm(matrix, ord="fro"),
            atol=1e-14,
        )

assert records["exponential"][-1][2] < 3e-4
assert records["algebraic"][-1][2] > 0.1
```

## 例 10-2 短窗指数拟合不能代表代数尾

指数族在每个固定距离 \(r\) 的元素均值满足

\[
\log\overline{|A_{\exp}(r)|}=-r/2.
\]

距离 4—12 的线性拟合斜率因而恰为 \(-0.5\)。对代数族，只在距离 1—8 拟合指数并外推到 16—31，冻结相对 2-范数残差约为 0.843。有限窗口能画出近似直线，不足以识别渐近函数族。

```python
import numpy as np

size = 64
index = np.arange(size)
distance = np.abs(index[:, None] - index[None, :])
exponential = np.exp(-distance / 2.0)
algebraic = 1.0 / (1.0 + distance)

fit_distance = np.arange(4, 13)
fit_mean = np.array([
    np.mean(np.abs(exponential[distance == value]))
    for value in fit_distance
])
slope, intercept = np.polyfit(fit_distance, np.log(fit_mean), 1)
assert abs(slope + 0.5) < 1e-12

short_distance = np.arange(1, 9)
short_mean = np.array([
    np.mean(np.abs(algebraic[distance == value]))
    for value in short_distance
])
fit = np.polyfit(short_distance, np.log(short_mean), 1)

far_distance = np.arange(16, 32)
far_true = np.array([
    np.mean(np.abs(algebraic[distance == value]))
    for value in far_distance
])
far_prediction = np.exp(np.polyval(fit, far_distance))
extrapolation_error = np.linalg.norm(far_prediction - far_true)
extrapolation_error /= np.linalg.norm(far_true)
assert extrapolation_error > 0.8
```

## 例 10-3 稀疏性不是 unitary 不变量

取对角 Hamiltonian

\[
H=\operatorname{diag}(-2,-1,0,1,2,3)
\]

及离散 Fourier unitary \(U\)。矩阵

\[
H'=U^\dagger HU
\]

与 \(H\) 等谱，但因一个对角元恰为零，\(H\) 只有 5 个非零元素；\(H'\) 在本例中有 36 个非零元素。稀疏性是表示性质，不是谱性质。

```python
import numpy as np

dimension = 6
H = np.diag([-2.0, -1.0, 0.0, 1.0, 2.0, 3.0])
j = np.arange(dimension)
U = np.exp(2j * np.pi * j[:, None] * j[None, :] / dimension)
U /= np.sqrt(dimension)
H_rotated = U.conj().T @ H @ U

assert np.linalg.norm(U.conj().T @ U - np.eye(dimension), ord="fro") < 1e-12
assert np.max(
    np.abs(np.linalg.eigvalsh(H_rotated) - np.linalg.eigvalsh(H))
) < 1e-12
assert np.count_nonzero(np.abs(H) > 1e-12) == 5
assert np.count_nonzero(np.abs(H_rotated) > 1e-12) == dimension**2
```

## 例 10-4 截断误差与 \(\mathbf k\) 采样误差是不同轴

一维标量实空间模型

\[
H(R)=e^{-|R|/2},
\qquad R\in\mathbb Z
\]

的 Bloch 和为

\[
H(k)=\sum_R H(R)e^{ikR}.
\]

固定 \(R_c=2\) 后，无论把 \(k\) 网格从 64 加密到 4096，\(k=0\) 处缺失的远程和都不变；加密采样不能恢复被截断的 \(R\) 块。

```python
import numpy as np

full_radius = 200
R = np.arange(-full_radius, full_radius + 1)
blocks = np.exp(-np.abs(R) / 2.0)
full_at_zero = np.sum(blocks)

cutoff = 2
truncated_at_zero = np.sum(blocks[np.abs(R) <= cutoff])
missing = abs(full_at_zero - truncated_at_zero)
assert missing > 0.0

for mesh_size in [64, 256, 4096]:
    k = 2.0 * np.pi * np.arange(mesh_size) / mesh_size
    truncated_bands = np.array([
        np.sum(
            blocks[np.abs(R) <= cutoff]
            * np.exp(1j * point * R[np.abs(R) <= cutoff])
        ).real
        for point in k
    ])
    assert np.isclose(truncated_bands[0], truncated_at_zero)
    assert abs(full_at_zero - truncated_bands[0]) == missing
```

## 例题证据边界

例 10-1、10-2 和 10-4 为 PEDAGOGICAL；例 10-3 的 unitary 等谱为 DIRECT_DERIVATION。它们验证概念差异和失败机制，不支持真实体系采用 \(R_c=2,4,8,16\) 或任何统一指数率。
