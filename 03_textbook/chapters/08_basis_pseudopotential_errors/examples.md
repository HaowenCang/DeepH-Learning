# 第 8 章例题：多轴收敛、广义谱与表示损失

本文件实现 T-C05—T-C08 的冻结合成对象。所有数组均为教学数据；分辨率、采样、基、矩阵和投影窗口不对应真实材料或后端设置。

## 例 8-1 多层级收敛与局部假平台

令参考值 \(q_*=1\)，分辨率为

\[
p=(8,16,32,64,128).
\]

正序列

\[
q^+=(1.12,1.03,1.008,1.002,1.0005)
\]

的最后三个参考误差为

\[
(8\times10^{-3},2\times10^{-3},5\times10^{-4}),
\]

最后两个相邻差为 \(6\times10^{-3}\) 与 \(1.5\times10^{-3}\)。三项冻结条件均通过。

负序列

\[
q^-=(1.12,1.03,1.0020,1.0015,1.0080)
\]

在 32/64 两层之间只有 \(5\times10^{-4}\) 的小差，但 128 层参考误差反而为 \(8\times10^{-3}>5\times10^{-3}\)。因此单独选择局部最平的一对会误报收敛。

```python
import numpy as np

resolution = np.array([8, 16, 32, 64, 128])
reference = 1.0
positive = np.array([1.12, 1.03, 1.008, 1.002, 1.0005])
negative = np.array([1.12, 1.03, 1.0020, 1.0015, 1.0080])

positive_error = np.abs(positive - reference)
positive_delta = np.abs(np.diff(positive))
assert np.all(positive_error[-3:] < 1e-2)
assert positive_error[-1] < 1e-3
assert np.all(positive_delta[-2:] < 1e-2)

negative_error = np.abs(negative - reference)
negative_delta = np.abs(np.diff(negative))
assert negative_delta[2] < 1e-3
assert negative_error[-1] > 5e-3
assert resolution.shape == positive.shape == negative.shape
```

## 例 8-2 \(\mathbf k\) 采样已收敛但基偏置仍存在

对周期函数

\[
f(k)=e^{\cos k}
\]

在 \(N_k\) 个等距点上取均值。精确周期平均为修正 Bessel 函数

\[
q_*=I_0(1).
\]

对 \(N_k=16,32,64\)，采样误差已到浮点精度；若另有固定基误差

\[
\delta_b=10^{-2},
\]

则 \(q_{N_k}+\delta_b\) 的总误差仍约为 \(10^{-2}\)。相邻采样差为零不能消除另一个误差轴。

```python
import numpy as np
from scipy.special import iv

reference = iv(0, 1)
sizes = [4, 8, 16, 32, 64]
values = []
for size in sizes:
    k = 2.0 * np.pi * np.arange(size) / size
    values.append(np.mean(np.exp(np.cos(k))))

values = np.array(values)
sampling_error = np.abs(values - reference)
assert np.all(sampling_error[-3:] < 1e-12)

basis_bias = 1e-2
biased = values + basis_bias
total_error = np.abs(biased - reference)
assert abs(values[-1] - values[-2]) < 1e-12
assert total_error[-1] > 5e-3
```

## 例 8-3 忽略 overlap 会改变谱

从

\[
S=\operatorname{diag}(1,2,1.5,2.3),
\qquad
H=\operatorname{diag}(-1.2,-0.2,1.2,4.6)
\]

出发，广义谱为

\[
(-1.2,-0.1,0.8,2.0).
\]

用固定可逆复矩阵 \(A\) 作一致合同变换

\[
H'=A^\dagger HA,\qquad S'=A^\dagger SA.
\]

正确求解 \(H'c=ES'c\) 保持广义谱；把同一 \(H'\) 错当普通本征问题则得到约

\[
(-1.794,-0.156,1.436,2.967),
\]

最大谱差约 0.967。错误不是数值容差造成，而是删除了物理内积矩阵。

```python
import numpy as np
from scipy.linalg import eigh

S = np.diag([1.0, 2.0, 1.5, 2.3])
H = np.diag([-1.2, -0.2, 1.2, 4.6])
reference = np.array([-1.2, -0.1, 0.8, 2.0])

A = np.diag([1.2, 0.9, 1.1, 0.8]).astype(np.complex128)
A[0, 1] = 0.2 + 0.1j
A[1, 2] = -0.15j
A[2, 3] = 0.1

H_prime = A.conj().T @ H @ A
S_prime = A.conj().T @ S @ A
values, vectors = eigh(H_prime, S_prime)

assert np.min(np.linalg.eigvalsh(S_prime)) > 0.0
assert np.max(np.abs(values - reference)) < 1e-11

for energy, vector in zip(values, vectors.T):
    numerator = np.linalg.norm(H_prime @ vector - energy * S_prime @ vector)
    denominator = (
        np.linalg.norm(H_prime, 2)
        + abs(energy) * np.linalg.norm(S_prime, 2)
    ) * np.linalg.norm(vector)
    assert numerator / denominator < 1e-12

wrong_values = np.linalg.eigvalsh(H_prime)
assert np.max(np.abs(wrong_values - reference)) > 1e-1
```

## 例 8-4 子空间丢失与等谱矩阵差

用固定 seed 生成 \(d\) 维 unitary \(Q\)，并定义

\[
H=Q\operatorname{diag}(\operatorname{linspace}(-3,3,d))Q^\dagger.
\]

取 \(B\) 为 \(Q\) 的 \(p\) 个中间列，

\[
H_p=B^\dagger HB,\qquad H_r=BH_pB^\dagger.
\]

在两组冻结配置中，\(\|H-H_r\|_F/\|H\|_F\) 分别约为 0.960 和 0.983，明确表明小目标子空间没有保留完整矩阵。

再用只旋转标准基前两维的 unitary \(U\) 构造

\[
H_2=U^\dagger HU.
\]

\(H_2\) 与 \(H\) 等谱，但固定坐标中的相对矩阵差分别约为 0.233 和 0.175，均大于 0.15。故“谱相同即矩阵标签相同”必须被拒绝。

```python
import numpy as np

def canonical_qr(matrix):
    q_matrix, r_matrix = np.linalg.qr(matrix)
    diagonal = np.diag(r_matrix)
    phases = np.where(np.abs(diagonal) > 0, diagonal / np.abs(diagonal), 1.0)
    q_canonical = q_matrix @ np.diag(phases)
    r_canonical = np.diag(np.conj(phases)) @ r_matrix
    reconstruction_error = np.linalg.norm(
        q_canonical @ r_canonical - matrix, ord="fro"
    ) / np.linalg.norm(matrix, ord="fro")
    assert reconstruction_error < 1e-12
    assert np.max(np.abs(np.imag(np.diag(r_canonical)))) < 1e-12
    assert np.min(np.real(np.diag(r_canonical))) > -1e-14
    return q_canonical

for seed, dimension in [(20260805, 12), (20260806, 16)]:
    rng = np.random.default_rng(seed)
    gaussian = (
        rng.normal(size=(dimension, dimension))
        + 1j * rng.normal(size=(dimension, dimension))
    )
    Q = canonical_qr(gaussian)
    H = Q @ np.diag(np.linspace(-3.0, 3.0, dimension)) @ Q.conj().T

    target_dimension = max(5, dimension // 3)
    offset = (dimension - target_dimension) // 2
    B = Q[:, offset : offset + target_dimension]
    H_projected = B.conj().T @ H @ B
    H_reconstructed = B @ H_projected @ B.conj().T

    assert np.linalg.norm(
        B.conj().T @ B - np.eye(target_dimension), ord="fro"
    ) < 1e-12
    idempotent_residual = np.linalg.norm(
        H_reconstructed
        - B @ (B.conj().T @ H_reconstructed @ B) @ B.conj().T,
        ord="fro",
    ) / max(np.linalg.norm(H_reconstructed, ord="fro"), 1e-15)
    assert idempotent_residual < 1e-12

    loss = np.linalg.norm(H - H_reconstructed, ord="fro")
    loss /= np.linalg.norm(H, ord="fro")
    assert loss > 0.9

    angle = 0.37
    U = np.eye(dimension, dtype=np.complex128)
    U[:2, :2] = [
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)],
    ]
    H_rotated = U.conj().T @ H @ U
    spectral_difference = np.max(
        np.abs(np.linalg.eigvalsh(H_rotated) - np.linalg.eigvalsh(H))
    )
    matrix_difference = np.linalg.norm(H_rotated - H, ord="fro")
    matrix_difference /= np.linalg.norm(H, ord="fro")

    assert spectral_difference < 1e-12
    assert matrix_difference > 0.15
```

## 例题证据边界

例 8-1、8-2 和例 8-4 的数据族为 PEDAGOGICAL；例 8-3 的合同变换与广义谱不变性、例 8-4 的 unitary 等谱关系为 DIRECT_DERIVATION。任何数值都不能转写为真实 cutoff、\(\mathbf k\) 网格、轨道数或投影窗口建议。
