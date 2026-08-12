# 第 4 章例题：有限周期 Fourier 对与相位规范

## 例 4.1　单轨道复跃迁链

取晶格常数 \(a=1\)，只保留

\[
H(0)=\varepsilon,
\qquad
H(1)=t e^{i\varphi},
\qquad
H(-1)=t e^{-i\varphi},
\]

其中 \(\varepsilon,t,\varphi\in\mathbb R\)。实空间关系 \(H(1)^*=H(-1)\) 保证 Hermiticity。按本教材正号正变换，

\[
\begin{aligned}
H(k)
&=\varepsilon+t e^{i(k+\varphi)}+t e^{-i(k+\varphi)}\\
&=\varepsilon+2t\cos(k+\varphi)\in\mathbb R.
\end{aligned}
\]

若删去 \(H(-1)\)，则 \(H(k)=\varepsilon+t e^{i(k+\varphi)}\) 一般为复数，不再是一维 Hermitian 矩阵。该失败不是“有限采样误差”，而是实空间共轭配对被破坏。

## 例 4.2　\(N=8\) 的闭合离散 Fourier 对

在有限循环晶格上把 \(-1\) 存为索引 \(N-1=7\)，取

\[
\varepsilon=0.7,
\qquad t=0.3,
\qquad\varphi=0.4,
\qquad k_m=\frac{2\pi m}{8}.
\]

正变换和逆变换分别为

\[
H(k_m)=\sum_{n=0}^{7}e^{ik_mn}H(n),
\qquad
H(n)=\frac18\sum_{m=0}^{7}e^{-ik_mn}H(k_m).
\]

确定性复算的最大重建误差为 \(4.1\times10^{-16}\)。若错误地在逆变换中也使用正号，最大块误差约为 \(0.233651\)，远高于浮点误差；该错误实际交换了正负平移信息。

## 例 4.3　Cell-phase 与轨道中心规范

在某个固定 \(k=1.1\) 处，取合成 Hermitian-definite 矩阵束

\[
H=\begin{pmatrix}
1&0.4+0.2i\\
0.4-0.2i&2
\end{pmatrix},
\qquad
S=\begin{pmatrix}1&0.2\\0.2&1\end{pmatrix}.
\]

令轨道中心 \(\tau_1=0\)、\(\tau_2=0.37\)，

\[
U(k)=\operatorname{diag}(1,e^{ik\tau_2}).
\]

同步变换

\[
\bar H=U^\dagger HU,
\qquad
\bar S=U^\dagger SU
\]

前后的广义谱均为

\[
0.91976160,\qquad 2.03857173.
\]

若只变换 \(H\) 而仍与原 \(S\) 配对，错误谱为

\[
0.88407490,\qquad 2.12086103,
\]

最大差约 \(8.23\times10^{-2}\)。因此“相位规范不改变物理量”的前提是基、矩阵和系数同步变换。

## 例 4.4　\(\mathbf k+\mathbf G\) 的规范边界

对 cell-phase Bloch 和，\(e^{i\mathbf G\cdot\mathbf R}=1\) 直接给出

\[
|\phi_{a,\mathbf k+\mathbf G}\rangle
=|\phi_{a\mathbf k}\rangle.
\]

对含中心相位的基，

\[
|\bar\phi_{a,\mathbf k+\mathbf G}\rangle
=e^{i\mathbf G\cdot\boldsymbol\tau_a}
|\bar\phi_{a\mathbf k}\rangle.
\]

因此能量可以严格倒格周期。对固定的同一抽象态，轨道系数先按

\[
D_G=\operatorname{diag}(e^{i\mathbf G\cdot\boldsymbol\tau_a})
\]

对齐基规范；数值本征矢还允许每条非简并带具有任意整体相位。简并处允许简并子空间内的幺正混合，只能比较投影算符或先对齐整个子空间，不能要求逐带逐元素相等。

## 确定性复现

固定环境为 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
@'
import numpy as np
from scipy.linalg import eigvalsh

N = 8
R = np.arange(N)
k_grid = 2*np.pi*np.arange(N)/N
eps, t, phi = 0.7, 0.3, 0.4
blocks = np.zeros(N, dtype=complex)
blocks[0] = eps
blocks[1] = t*np.exp(1j*phi)
blocks[-1] = blocks[1].conjugate()

hk = np.array([
    np.sum(np.exp(1j*k*R)*blocks)
    for k in k_grid
])
recovered = np.array([
    np.sum(np.exp(-1j*k_grid*r)*hk)/N
    for r in R
])
wrong_inverse = np.array([
    np.sum(np.exp(1j*k_grid*r)*hk)/N
    for r in R
])
broken = blocks.copy()
broken[-1] = 0.0
hk_broken = np.array([
    np.sum(np.exp(1j*k*R)*broken)
    for k in k_grid
])

assert np.max(np.abs(recovered-blocks)) < 1e-12
assert np.max(np.abs(hk.imag)) < 2e-12
assert np.max(np.abs(wrong_inverse-blocks)) > 1e-2
assert np.max(np.abs(hk_broken.imag)) > 1e-2

H = np.array([[1, 0.4+0.2j], [0.4-0.2j, 2]], dtype=complex)
S = np.array([[1, 0.2], [0.2, 1]], dtype=complex)
k = 1.1
tau = np.array([0.0, 0.37])
U = np.diag(np.exp(1j*k*tau))
Hbar = U.conj().T @ H @ U
Sbar = U.conj().T @ S @ U
E = eigvalsh(H, S)
Ebar = eigvalsh(Hbar, Sbar)
Ewrong = eigvalsh(Hbar, S)

assert np.max(np.abs(Hbar-Hbar.conj().T)) < 1e-13
assert np.max(np.abs(Sbar-Sbar.conj().T)) < 1e-13
assert np.max(np.abs(Ebar-E)) < 1e-12
assert np.max(np.abs(Ewrong-E)) > 1e-2

G = 2*np.pi
Dg = np.diag(np.exp(1j*G*tau))
UkG = np.diag(np.exp(1j*(k+G)*tau))
Hbar_kG = UkG.conj().T @ H @ UkG
Sbar_kG = UkG.conj().T @ S @ UkG
assert np.max(np.abs(np.exp(1j*G*R)-1.0)) < 1e-12
assert np.max(np.abs(UkG-U@Dg)) < 1e-12
assert np.max(np.abs(Hbar_kG-Dg.conj().T@Hbar@Dg)) < 1e-12
assert np.max(np.abs(Sbar_kG-Dg.conj().T@Sbar@Dg)) < 1e-12
assert np.max(np.abs(eigvalsh(Hbar_kG, Sbar_kG)-E)) < 1e-12
print({
    'fourier_error': float(np.max(np.abs(recovered-blocks))),
    'wrong_sign_error': float(np.max(np.abs(wrong_inverse-blocks))),
    'missing_pair_imag': float(np.max(np.abs(hk_broken.imag))),
    'gauge_spectrum_error': float(np.max(np.abs(Ebar-E))),
    'one_sided_gauge_error': float(np.max(np.abs(Ewrong-E))),
    'k_plus_G_gauge_error': float(np.max(np.abs(Hbar_kG-Dg.conj().T@Hbar@Dg))),
})
'@ | & $py -
```

所有负例均通过显式断言进入验收；仅打印错误而不检查阈值不算通过。
