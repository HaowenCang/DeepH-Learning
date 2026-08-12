# 第 20 章例题与失败样例

## 例 20-1：绕 z 轴的自旋 \(1/2\) lift

取 \(\theta=\pi/2\)。按与标准 Pauli 矩阵一致的 \((m_s=+1/2,-1/2)\) 顺序，

\[
U_z(\pi/2)
=
\begin{pmatrix}
e^{-i\pi/4}&0\\
0&e^{i\pi/4}
\end{pmatrix}
=
\begin{pmatrix}
0.70710678-0.70710678i&0\\
0&0.70710678+0.70710678i
\end{pmatrix}.
\]

直接相乘给

\[
U_z(\pi/2)^4=-I_2,
\qquad
U_z(\pi/2)^8=I_2.
\]

对应的三维旋转在四次作用后已经是 \(I_3\)。因此测试若只比较三维向量，会漏掉 \(SU(2)\) lift 的符号链。

## 例 20-2：\(p\otimes1/2\) 的维度与轴顺序

实 p 轨道顺序为 \((p_x,p_y,p_z)\)，自旋顺序为 \((+1/2,-1/2)\)。orbital-major/spin-minor 的 6 个 component 为

\[
(p_x\uparrow,p_x\downarrow,
p_y\uparrow,p_y\downarrow,
p_z\uparrow,p_z\downarrow).
\]

旋转表示为

\[
D_{p\otimes s}=R\otimes U_{1/2}\in\mathbb C^{6\times6}.
\]

若改用 spin-major 顺序，所需矩阵是显式置换后的 \(P(R\otimes U)P^{\mathsf T}\)。直接把同一个 \(6\times6\) 数组解释成另一种顺序会产生 shape 合法但身份错误的结果。

## 例 20-3：固定复向量上的反幺正平方与正交性

取归一化自旋向量

\[
\psi=\frac1{\sqrt3}
\begin{pmatrix}1\\1+i\end{pmatrix},
\qquad
J_s=
\begin{pmatrix}0&1\\-1&0\end{pmatrix}.
\]

则

\[
\Theta\psi=J_s\psi^*
=\frac1{\sqrt3}
\begin{pmatrix}1-i\\-1\end{pmatrix},
\]

\[
\Theta^2\psi=-\psi,
\qquad
\langle\psi\mid\Theta\psi\rangle=0.
\]

该向量同时含实部和虚部，可检出漏共轭；只用 \((1,0)^{\mathsf T}\) 只能检查部分矩阵列。

## 例 20-4：整数 \(\ell=1\) 的复轨道时间反演矩阵

在 \(m=(-1,0,1)\) 顺序和本项目固定相位下，

\[
J_1=
\begin{pmatrix}
0&0&-1\\
0&1&0\\
-1&0&0
\end{pmatrix}.
\]

它满足

\[
J_1J_1^*=I_3.
\]

由第 17 章冻结的 \(K_1\) 从实 p 基变换得到

\[
J_1=K_1I_3K_1^{\mathsf T}.
\]

若错误使用普通线性相似变换 \(K_1I_3K_1^\dagger=I_3\)，与正确 \(J_1\) 的归一化 Frobenius 残差为

\[
1.1547005384.
\]

因此反幺正 unitary part 的基变换必须使用转置，而不是共轭转置。

## 例 20-5：固定 \(2\times2\) 时间反演不变 Hamiltonian

取

\[
H(k)=\bigl(2+0.3\cos k\bigr)I
+\sin k\,\sigma_x
+0.4\sin k\,\sigma_z.
\]

在 \(k=0.7\) 时，

\[
H(k)=
\begin{pmatrix}
2.48713973&0.64421769\\
0.64421769&1.97176558
\end{pmatrix},
\]

\[
H(-k)=
\begin{pmatrix}
1.97176558&-0.64421769\\
-0.64421769&2.48713973
\end{pmatrix}.
\]

全精度 `complex128` 直接给

\[
\rho\!\left(H(-k),J_sH(k)^*J_s^\dagger\right)=0.
\]

\(H(k)\) 的两个本征值约为 \(1.53560897\) 和 \(2.92329634\)。它们在一般 k 不要求简并，因为时间反演把 k 映到 \(-k\)。

## 例 20-6：TRIM 上的 Kramers 成对

对例 20-5，在 \(k=0\) 时

\[
H(0)=2.3I_2,
\]

在 \(k=\pi\) 时

\[
H(\pi)=1.7I_2.
\]

这两个 k 满足 \(-k=k+G\)，Pauli 奇函数项为零，因此出现二重简并。若只在 \(k=0.7\) 上要求同一矩阵的两本征值相等，会把 Bloch k-pair 条件误用为逐 k 简并。

## 例 20-7：Zeeman 项的定向破缺

取

\[
H_B=\sigma_z.
\]

固定时间反演给

\[
J_sH_B^*J_s^\dagger=-\sigma_z.
\]

归一化 Frobenius 残差为

\[
\rho(H_B,-H_B)=2.
\]

它远高于 float64/32 门限。这不是实现误差，而是把外场保持同号时的物理时间反演破缺。测试应将其标成预期拒绝，不能用“模型不够精确”解释。

## 例 20-8：漏共轭和错误 \(J\) 的不同失败

把正确反幺正作用记为

\[
\Theta(\psi)=J_s\psi^*.
\]

若错误实现为线性映射 \(L(\psi)=J_s\psi\)，对例 20-3 的归一化向量有

\[
\lVert L(i\psi)+iL(\psi)\rVert_2=2,
\]

而正确 \(\Theta\) 的同一残差为 0。另一方面，若使用 \(J_{\mathrm{wrong}}=I_2\)，反线性仍可通过，但

\[
J_{\mathrm{wrong}}J_{\mathrm{wrong}}^*=+I_2
\]

而不是 \(-I_2\)。T-E11 必须把反线性与平方符号分成两个测试对象。

## 例 20-9：整体相位自由不改变 \(\Theta^2\)

取

\[
J'_s=e^{i\pi/3}J_s.
\]

则

\[
J'_s(J'_s)^*
=e^{i\pi/3}e^{-i\pi/3}J_sJ_s^*
=-I_2.
\]

所以 \(J'_sK\) 与 \(J_sK\) 物理等价。项目代码仍要求固定实矩阵 \(J_s\)；若输入 \(J'_s\) 却声明固定版本，应报告规范/哈希不一致，而不是宣称 Kramers 数学被破坏。

## 例 20-10：空间反演和时间反演对自旋的作用不同

设 \(\boldsymbol S=(S_x,S_y,S_z)\)。空间反演下自旋是轴向量：

\[
P\boldsymbol SP^{-1}=+\boldsymbol S.
\]

时间反演下

\[
\Theta\boldsymbol S\Theta^{-1}=-\boldsymbol S.
\]

把自旋按极向量处理会在 P 下错误变号；把 P 的结果照搬到时间反演又会漏掉负号。这两个故障都可能通过纯 \(SO(3)\) 随机旋转，所以必须由 T-E07/T-E11 分别检查。

## 例 20-11：自旋扩维的解析成本因子

设 spinless 轨道维数为 \(P\)。加入显式自旋后维数为 \(2P\)，稠密方块元素数从 \(P^2\) 变为

\[
(2P)^2=4P^2.
\]

若 spinless 基准为 `float64`、自旋块为 `complex128`，仅持久数组字节从 \(8P^2\) 变为 \(16\cdot4P^2=64P^2\)，即 8 倍。这个因子同时包含 4 倍元素数和 2 倍单元素字节，不能把它概括成“自旋只使成本翻倍”。稀疏性、Hermiticity、块结构或专用 kernel 可以改变实际成本，留待明确实现后计数。

## 例 20-12：代数通过但 Hamiltonian 不对称

固定 \(J_s\) 总能满足 \(J_sJ_s^*=-I\)。现在仍取 \(H_B=\sigma_z\)。如果只运行 \(J\) 的平方测试，结果会通过；但 Hamiltonian 配对残差为 2，Kramers 的时间反演不变前提不成立。

这说明 T-E11 至少需要三层证据：反幺正作用本身、Hamiltonian 对称关系、满足条件时的谱/正交结论。任何单层通过都不能替代其余两层。
