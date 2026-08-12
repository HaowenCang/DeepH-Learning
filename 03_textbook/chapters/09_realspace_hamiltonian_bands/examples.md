# 第 9 章例题：双轨道实空间矩阵到能带

## 例 9.1　合成矩阵块与高对称点

取一维晶格常数 \(a=1\)，固定以下 `PEDAGOGICAL` 矩阵块：

\[
H(0)=\begin{pmatrix}0.2&0.3\\0.3&1.2\end{pmatrix},
\quad
H(1)=\begin{pmatrix}-0.4&0.10\\0.05&-0.2\end{pmatrix},
\]

\[
H(2)=\begin{pmatrix}-0.06&0.02i\\0.01&-0.03\end{pmatrix},
\qquad
H(-R)=H(R)^\dagger,
\]

以及

\[
S(0)=I,
\quad
S(1)=\begin{pmatrix}0.08&0.02\\0.01&0.05\end{pmatrix},
\quad
S(2)=\begin{pmatrix}0.01&0.005i\\0.002&0.008\end{pmatrix},
\]

并令 \(S(-R)=S(R)^\dagger\)。在 \(k=0\) 处，

\[
H(0_k)=\begin{pmatrix}-0.72&0.46+0.02i\\0.46-0.02i&0.74\end{pmatrix},
\]

\[
S(0_k)=\begin{pmatrix}1.18&0.032+0.005i\\0.032-0.005i&1.116\end{pmatrix},
\]

广义本征值约为 \(-0.73728885,0.76771829\)。在 \(k=\pi\) 处，谱约为 \(0.96124921,1.75714114\)。

## 例 9.2　全路径广义本征与逆变换

在 129 个均匀点上，\(S(k)\) 的最小特征值不低于 \(0.8479\)。两条能带范围分别约为

\[
[-0.73753,0.96167],
\qquad
[0.76757,1.75769].
\]

全路径最大 \(H\) 与 \(S\) 反 Hermitian Frobenius 残差分别低于 \(1.7\times10^{-16}\) 与 \(1.7\times10^{-17}\)，最大逐本征对归一化 2-范数残差低于 \(6.4\times10^{-16}\)，最大 \(S\)-正交 Frobenius 残差低于 \(1.3\times10^{-15}\)。在 \(N=64\) 完整循环网格上对 \(H(k),S(k)\) 作逆变换，全部已知 \(R=0,\pm1,\pm2\) 块的最大误差低于 \(4\times10^{-15}\)。

## 例 9.3　截断与采样不是同一误差

删除 \(R=\pm2\) 的 \(H,S\) 块但保留 \(R=0,\pm1\)，最大能带差约为 \(0.16136\)。该截断按正负平移成对执行，因此 Hermiticity 仍保持；能带差来自模型本身改变。

把截断模型的网格从 64 点增加到 128 点，只会更密地采样截断后的矩阵函数，最大差仍保持在同一非零尺度。增加 \(k\) 点不能恢复已经删除的 \(R=\pm2\) 信息。

## 例 9.4　三类失败

- 忽略 \(S(k)\)：与正确广义谱的最大差约 \(0.180\)；
- 只删除 \(H(-2)\) 而保留 \(H(2)\)：\(H(k)\) 出现显著反 Hermitian 部分；
- 对两轨道施加 \(U(k)=\operatorname{diag}(1,e^{0.37ik})\) 时只变换 \(H(k)\)：广义谱改变。

这三类失败分别对应遗漏度量、破坏实空间共轭配对和不一致基规范，不能统一归因于“数值噪声”。

## 确定性复现

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
@'
import numpy as np
from scipy.linalg import eigh

H = {
  0: np.array([[0.2,0.3],[0.3,1.2]], complex),
  1: np.array([[-0.4,0.10],[0.05,-0.2]], complex),
  2: np.array([[-0.06,0.02j],[0.01,-0.03]], complex),
}
H[-1], H[-2] = H[1].conj().T, H[2].conj().T
S = {
  0: np.eye(2, dtype=complex),
  1: np.array([[0.08,0.02],[0.01,0.05]], complex),
  2: np.array([[0.01,0.005j],[0.002,0.008]], complex),
}
S[-1], S[-2] = S[1].conj().T, S[2].conj().T

def assemble(blocks, k):
    return sum(np.exp(1j*k*r)*b for r,b in blocks.items())

def bands(Hb, Sb, grid):
    out=[]
    for k in grid:
        hk, sk = assemble(Hb,k), assemble(Sb,k)
        out.append(eigh(hk,sk)[0])
    return np.array(out)

grid = np.linspace(-np.pi, np.pi, 129, endpoint=False)
min_s = np.inf
max_h_herm, max_s_herm = 0.0, 0.0
max_norm_res, max_orth = 0.0, 0.0
E=[]
for k in grid:
    hk, sk = assemble(H,k), assemble(S,k)
    e,c = eigh(hk,sk)
    E.append(e)
    max_h_herm = max(max_h_herm, np.linalg.norm(hk-hk.conj().T, ord='fro'))
    max_s_herm = max(max_s_herm, np.linalg.norm(sk-sk.conj().T, ord='fro'))
    min_s = min(min_s, np.linalg.eigvalsh(sk).min())
    for n in range(len(e)):
        cn = c[:,n]
        numerator = np.linalg.norm(hk@cn-e[n]*sk@cn, ord=2)
        denominator = (np.linalg.norm(hk, ord=2)
                       + abs(e[n])*np.linalg.norm(sk, ord=2))*np.linalg.norm(cn, ord=2)
        max_norm_res = max(max_norm_res, numerator/denominator)
    max_orth = max(max_orth, np.linalg.norm(c.conj().T@sk@c-np.eye(2), ord='fro'))
E=np.array(E)
assert max_h_herm < 1e-12
assert max_s_herm < 1e-12
assert min_s > 0.84
assert max_norm_res < 1e-12
assert max_orth < 2e-14

N=64
kgrid=2*np.pi*np.arange(N)/N
hk=np.array([assemble(H,k) for k in kgrid])
sk=np.array([assemble(S,k) for k in kgrid])
for r,b in H.items():
    rec=np.sum(np.exp(-1j*kgrid*r)[:,None,None]*hk,axis=0)/N
    assert np.max(np.abs(rec-b)) < 5e-14
for r,b in S.items():
    rec=np.sum(np.exp(-1j*kgrid*r)[:,None,None]*sk,axis=0)/N
    assert np.max(np.abs(rec-b)) < 5e-14

Htr={r:b for r,b in H.items() if abs(r)<=1}
Str={r:b for r,b in S.items() if abs(r)<=1}
for n in (64,128):
    g=2*np.pi*np.arange(n)/n
    trunc_error=np.max(np.abs(bands(H,S,g)-bands(Htr,Str,g)))
    assert trunc_error > 0.1

ignore_s=max(
    np.max(np.abs(eigh(assemble(H,k),assemble(S,k))[0]
                  -np.linalg.eigvalsh(assemble(H,k))))
    for k in grid
)
assert ignore_s > 0.1

Hbroken=dict(H)
del Hbroken[-2]
herm_failure=max(
    np.linalg.norm(assemble(Hbroken,k)-assemble(Hbroken,k).conj().T)
    for k in grid
)
assert herm_failure > 1e-2

k=2.5
hk0,sk0=assemble(H,k),assemble(S,k)
U=np.diag(np.exp(1j*k*np.array([0.0,0.37])))
hbar=U.conj().T@hk0@U
sbar=U.conj().T@sk0@U
e0=eigh(hk0,sk0)[0]
assert np.max(np.abs(eigh(hbar,sbar)[0]-e0)) < 1e-12
assert np.max(np.abs(eigh(hbar,sk0)[0]-e0)) > 1e-3

print({
 'max_H_antihermitian_fro': float(max_h_herm),
 'max_S_antihermitian_fro': float(max_s_herm),
 'min_S_eigenvalue': float(min_s),
 'max_normalized_eigenpair_residual': float(max_norm_res),
 'max_S_orthogonality': float(max_orth),
 'band_ranges': [E.min(axis=0).tolist(),E.max(axis=0).tolist()],
 'truncation_error_128': float(trunc_error),
 'ignore_S_error': float(ignore_s),
 'missing_pair_hermiticity': float(herm_failure),
})
'@ | & $py -
```

该复现使用固定用户态依赖，不包含正式数据或 DeepH 安装。
