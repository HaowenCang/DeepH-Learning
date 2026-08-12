# 第 3 章例题：两轨道非正交广义本征问题

## 例 3.1　闭式广义谱与 \(S\)-归一化

考虑 `PEDAGOGICAL` 模型

\[
H=\begin{pmatrix}1&0\\0&2\end{pmatrix},
\qquad
S=\begin{pmatrix}1&1/2\\1/2&1\end{pmatrix}.
\]

两矩阵均为实对称矩阵。\(S\) 的特征值为 \(1/2,3/2\)，故 \(S\succ0\)，且 \(\kappa_2(S)=3\)。广义特征方程为

\[
\begin{aligned}
0&=\det(H-ES)\\
&=\det\begin{pmatrix}1-E&-E/2\\-E/2&2-E\end{pmatrix}\\
&=2-3E+\frac34E^2.
\end{aligned}
\]

因此

\[
E_\pm=2\pm\frac{2}{\sqrt3}
\approx 0.8452994616, 3.1547005384.
\]

一组按 \(C^\mathsf TSC=I\) 归一化的实本征矢为

\[
C\approx
\begin{pmatrix}
-0.8164965809&-0.8164965809\\
-0.2988584907& 1.1153550717
\end{pmatrix}.
\]

每列整体符号任意，因此复算时允许整列变号；必须保持的是广义残差和 \(S\)-正交性，而不是未固定符号的逐元素相等。

若错误地忽略 \(S\)，普通本征问题只给出 \(1,2\)。它与正确广义谱不同，说明 \(S\) 不是可选的数值修正项，而是非正交坐标中的度量。

## 例 3.2　Cholesky 与对称正交化

对该 \(S\)，下三角 Cholesky 因子为

\[
L=\begin{pmatrix}1&0\\1/2&\sqrt3/2\end{pmatrix},
\qquad S=LL^\mathsf T.
\]

令 \(y=L^\mathsf Tc\)，则标准 Hermitian 矩阵为

\[
\widetilde H_{\mathrm C}=L^{-1}HL^{-\mathsf T}
=\begin{pmatrix}
1&-1/\sqrt3\\
-1/\sqrt3&3
\end{pmatrix}.
\]

它的普通本征值仍为 \(2\pm2/\sqrt3\)。变量映射必须包含回代 \(c=L^{-\mathsf T}y\)；只对矩阵做约化而忘记回代，不能得到原基中的系数。

对称逆平方根的数值值为

\[
S^{-1/2}\approx
\begin{pmatrix}
1.1153550717&-0.2988584907\\
-0.2988584907&1.1153550717
\end{pmatrix},
\]

从而

\[
\widetilde H_{\mathrm S}=S^{-1/2}HS^{-1/2}
\approx
\begin{pmatrix}
1.4226497308&-1\\
-1&2.5773502692
\end{pmatrix}.
\]

其普通谱也相同。两种约化矩阵并不逐元素相等，因为它们采用不同的正交坐标；谱和映射回原空间后的态才是应比较的对象。

## 例 3.3　一致基变换与不一致失败样例

取可逆但非幺正矩阵

\[
A=\begin{pmatrix}1&1/2\\0&1\end{pmatrix}.
\]

一致变换给出

\[
H'=A^\mathsf THA
=\begin{pmatrix}1&1/2\\1/2&9/4\end{pmatrix},
\qquad
S'=A^\mathsf TSA
=\begin{pmatrix}1&1\\1&7/4\end{pmatrix}.
\]

矩阵束 \((H',S')\) 的广义谱仍为 \(2\pm2/\sqrt3\)。若只变换 \(H\) 而仍与原 \(S\) 配对，则广义谱变为 \(1,8/3\)；这构成一个可执行的失败样例。

## 例 3.4　非法与病态重叠矩阵

以下两个输入说明不同失败类别：

\[
S_{\mathrm{sing}}=
\begin{pmatrix}1&1\\1&1\end{pmatrix},
\qquad
S_{\mathrm{indef}}=
\begin{pmatrix}1&1.2\\1.2&1\end{pmatrix}.
\]

\(S_{\mathrm{sing}}\) 的特征值为 \(0,2\)，表示线性相关基；\(S_{\mathrm{indef}}\) 的特征值为 \(-0.2,2.2\)，不可能作为正定 Gram 矩阵。两者都应被标准 Hermitian-definite 求解路径拒绝，而不是添加任意小常数后继续并把结果冒充原问题。

若改取

\[
S_\varepsilon=\begin{pmatrix}1&1-\varepsilon\\1-\varepsilon&1\end{pmatrix},
\qquad 0<\varepsilon\ll1,
\]

则它仍正定，但 \(\kappa_2(S_\varepsilon)=(2-\varepsilon)/\varepsilon\) 很大。此时应报告条件数、残差和 \(S\)-正交误差；不能只因求解器返回有限数值便称输入良态。

## 例 3.5　后向扰动与谱隙界的确定性复核

仍取例 3.1 的 \(H,S\)，选择未经求解器优化的向量并作 \(S\)-归一化：

\[
\widehat c=\frac1{\sqrt{39}}\begin{pmatrix}5\\2\end{pmatrix},
\qquad
\widehat E=\mathcal R(\widehat c)=\frac{11}{13}.
\]

未归一化残差为

\[
q=H\widehat c-\widehat E S\widehat c
=\frac1{\sqrt{39}}
\begin{pmatrix}-1/13\\5/26\end{pmatrix},
\qquad
\widehat c^\mathsf Tq=0.
\]

按正文 3.5.2 构造 \(u=\widehat c/\|\widehat c\|_2\)、\(p=-q/\|\widehat c\|_2\) 和

\[
\Delta H=pu^\mathsf T+up^\mathsf T.
\]

数值复算给出

\[
\Delta H\approx
\begin{pmatrix}
0.0265251989&-0.0278514589\\
-0.0278514589&-0.0265251989
\end{pmatrix},
\]

且 \(\Delta H=\Delta H^\mathsf T\)、\((H+\Delta H)\widehat c=\widehat E S\widehat c\)。本例有

\[
\|\Delta H\|_2=\frac1{26}
\le2\frac{\|q\|_2}{\|\widehat c\|_2}
=\frac1{13}.
\]

在对称正交坐标中，\(\rho=S^{-1/2}q\) 的范数为 \(0.0444115592\)。最近本征值误差与其余谱分离量分别为

\[
|\widehat E-E_-|\approx0.0008543845,
\qquad
\operatorname{sep}_-(\widehat E)\approx2.3085466922.
\]

因此本征值包含界 \(|\widehat E-E_-|\le\|\rho\|_2\) 成立；正交坐标中的实际角度与界为

\[
\sin\angle(y,u_-)
\approx0.0192343275
\le
\frac{\|\rho\|_2}{\operatorname{sep}_-(\widehat E)}
\approx0.0192378865.
\]

该模型是 `PEDAGOGICAL`；扰动构造和不等式检验是正文 `DIRECT_DERIVATION` 的确定性实例，不外推为真实基组误差统计。

## 确定性复现

固定环境为 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0。PowerShell 复现命令如下：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
@'
import numpy as np
from scipy.linalg import cholesky, eigh, eigvalsh

np.set_printoptions(precision=10, suppress=True)
H = np.array([[1.0, 0.0], [0.0, 2.0]])
S = np.array([[1.0, 0.5], [0.5, 1.0]])
E, C = eigh(H, S)
L = cholesky(S, lower=True)
left = np.linalg.solve(L, H)
HC = np.linalg.solve(L, left.T).T
s, U = np.linalg.eigh(S)
Smhalf = (U * s**-0.5) @ U.T
HS = Smhalf @ H @ Smhalf
A = np.array([[1.0, 0.5], [0.0, 1.0]])
Hp, Sp = A.T @ H @ A, A.T @ S @ A

def solve_definite(H_in, S_in):
    if not np.allclose(H_in, H_in.T.conj(), atol=1e-13):
        raise ValueError('H must be Hermitian')
    if np.min(eigvalsh(S_in)) <= 0.0:
        raise ValueError('S must be positive definite')
    return eigh(H_in, S_in)

assert np.max(np.abs(E - np.array([2-2/np.sqrt(3), 2+2/np.sqrt(3)]))) < 1e-12
assert np.linalg.norm(H @ C - S @ C @ np.diag(E)) < 1e-12
assert np.linalg.norm(C.T @ S @ C - np.eye(2)) < 1e-12
assert np.max(np.abs(eigvalsh(HC) - E)) < 1e-12
assert np.max(np.abs(eigvalsh(HS) - E)) < 1e-12
assert np.max(np.abs(eigvalsh(Hp, Sp) - E)) < 1e-12
assert np.max(np.abs(eigvalsh(Hp, S) - E)) > 1e-1

chat = np.array([1.0, 0.4])
chat /= np.sqrt(chat @ S @ chat)
theta = (chat @ H @ chat) / (chat @ S @ chat)
q = H @ chat - theta * S @ chat
u = chat / np.linalg.norm(chat)
p = -q / np.linalg.norm(chat)
alpha = float(u @ p)
DeltaH = np.outer(p, u) + np.outer(u, p) - alpha * np.outer(u, u)
Shalf = (U * s**0.5) @ U.T
rho = Smhalf @ q
y = Shalf @ chat
j = int(np.argmin(np.abs(E - theta)))
uj = Shalf @ C[:, j]
sep = float(np.min(np.abs(np.delete(E, j) - theta)))
sin_angle = float(np.sqrt(max(0.0, 1.0 - abs(y @ uj)**2)))
coeff_error = min(np.linalg.norm(chat-C[:, j]), np.linalg.norm(chat+C[:, j])) / np.linalg.norm(C[:, j])

assert np.linalg.norm(DeltaH - DeltaH.T) < 1e-14
assert np.linalg.norm((H + DeltaH) @ chat - theta * S @ chat) < 1e-14
assert np.linalg.norm(DeltaH, 2) <= 2*np.linalg.norm(q)/np.linalg.norm(chat) + 1e-14
assert np.linalg.norm(rho) <= np.linalg.norm(q)/np.sqrt(np.min(s)) + 1e-14
assert abs(theta - E[j]) <= np.linalg.norm(rho) + 1e-14
assert sin_angle <= np.linalg.norm(rho)/sep + 1e-14
assert coeff_error <= np.sqrt(2*np.linalg.cond(S))*np.linalg.norm(rho)/sep + 1e-14

for S_bad in (
    np.array([[1.0, 1.0], [1.0, 1.0]]),
    np.array([[1.0, 1.2], [1.2, 1.0]]),
):
    try:
        solve_definite(H, S_bad)
    except ValueError as exc:
        assert 'positive definite' in str(exc)
    else:
        raise AssertionError('invalid S was not rejected')

print({
    'eigenvalues': E.tolist(),
    'cond_S': float(np.linalg.cond(S)),
    'backward_cancel': float(np.linalg.norm((H+DeltaH)@chat-theta*S@chat)),
    'rho_norm': float(np.linalg.norm(rho)),
    'sin_angle': sin_angle,
})
'@ | & $py -
```

这些断言同时复核一致/不一致基变换、Hermitian 后向扰动、谱隙界和非法 \(S\) 的显式拒绝。它们不是在验证新物理现象，而是在检验推导条件是否被代码正确执行。
