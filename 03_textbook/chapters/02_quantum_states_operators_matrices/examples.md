# 第 2 章例题：二能级系统中的一致与不一致基变换

## 1. 原始表示

取正交基中的 Hermitian 矩阵和归一化态

\[
H=\begin{pmatrix}1&2\\2&-1\end{pmatrix},
\qquad
c=\frac1{\sqrt2}\begin{pmatrix}1\\i\end{pmatrix},
\qquad S=I_2.
\]

特征多项式为 \(\det(H-EI)=E^2-5\)，故本征值为 \(E_\pm=\pm\sqrt5\)。态的期望值为

\[
c^\dagger Hc
=\frac12(1,-i)
\begin{pmatrix}1+2i\\2-i\end{pmatrix}=0.
\]

## 2. 单轨道相位翻转

令

\[
A_\mathrm p=\begin{pmatrix}1&0\\0&-1\end{pmatrix}.
\]

因为 \(A_\mathrm p\) 幺正，

\[
H_\mathrm p=A_\mathrm p^\dagger H A_\mathrm p
=\begin{pmatrix}1&-2\\-2&-1\end{pmatrix},
\quad
c_\mathrm p=A_\mathrm p^{-1}c
=\frac1{\sqrt2}\begin{pmatrix}1\\-i\end{pmatrix},
\quad S_\mathrm p=I_2.
\]

非对角元改变符号，但特征多项式仍为 \(E^2-5\)，且 \(c_\mathrm p^\dagger H_\mathrm p c_\mathrm p=0\)。这说明矩阵元素变化不等于物理问题变化。

## 3. 轨道重排

令

\[
A_\mathrm r=\begin{pmatrix}0&1\\1&0\end{pmatrix}.
\]

则

\[
H_\mathrm r=A_\mathrm r^\dagger H A_\mathrm r
=\begin{pmatrix}-1&2\\2&1\end{pmatrix},
\qquad
c_\mathrm r=A_\mathrm r^{-1}c
=\frac1{\sqrt2}\begin{pmatrix}i\\1\end{pmatrix}.
\]

谱和期望值仍分别为 \(\{-\sqrt5,+\sqrt5\}\) 与 0。若只重排矩阵的行而不重排列，所得矩阵通常不再 Hermitian；若只重排矩阵而不重排系数，期望值对应另一个态。

## 4. 非幺正基变换

取

\[
A=\begin{pmatrix}1&\tfrac12\\0&1\end{pmatrix},
\qquad
A^{-1}=\begin{pmatrix}1&-\tfrac12\\0&1\end{pmatrix}.
\]

新基不是正交基，因为

\[
S'=A^\dagger A
=\begin{pmatrix}1&\tfrac12\\[2pt]\tfrac12&\tfrac54\end{pmatrix}\ne I_2.
\]

同步变换给出

\[
H'=A^\dagger H A
=\begin{pmatrix}1&\tfrac52\\[2pt]\tfrac52&\tfrac54\end{pmatrix},
\qquad
c'=A^{-1}c
=\frac1{\sqrt2}\begin{pmatrix}1-\tfrac i2\\ i\end{pmatrix}.
\]

直接计算可验证

\[
c'^\dagger S'c'=1,
\qquad
c'^\dagger H'c'=0.
\]

广义特征方程满足

\[
\det(H'-ES')=|\det A|^2\det(H-EI)=E^2-5,
\]

所以广义本征值仍为 \(\pm\sqrt5\)。

## 5. 确定性失败样例

若错误地忽略 \(S'\)，直接求 \(H'x=Ex\)，则

\[
\det(H'-EI)=E^2-\frac94E-5,
\]

普通本征值为

\[
E_{\mathrm{wrong},\pm}
=\frac{9\pm\sqrt{401}}8
\approx 3.6281,-1.3781,
\]

明显不同于 \(\pm\sqrt5\approx\pm2.2361\)。失败原因不是非幺正基变换改变了物理谱，而是把非正交基中的矩阵 \(H'\) 错当成正交基矩阵，遗漏了 \(S'\)。

## 6. 验收结论

本例同时验证：

- 相位翻转和重排会改变矩阵元素，但一致变换保持谱与期望值；
- 一般可逆基变换保持矩阵对 \((H,S)\) 的广义谱；
- 非幺正变换后只求 \(H'\) 的普通谱是可确定复现的错误；
- 基变换必须同步作用于基、系数、Hamiltonian 和 overlap。
