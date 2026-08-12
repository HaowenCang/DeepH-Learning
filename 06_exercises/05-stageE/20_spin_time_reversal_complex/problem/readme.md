# 第 20 章练习

## Q20-01 \(SU(2)\) lift 与 \(2\pi\) 旋转

从

\[
U_{1/2}(\widehat n,\theta)
=\cos(\theta/2)I-i\sin(\theta/2)\widehat n\cdot\boldsymbol\sigma
\]

推出 \(U(2\pi)\)、\(U(4\pi)\)，并解释为何这不与三维空间 \(R(2\pi)=I_3\) 矛盾。说明代码至少应记录哪个 lift 身份，才能检验连续复合。

## Q20-02 轨道—自旋张量积的维度与顺序

对 p 轨道 \((p_x,p_y,p_z)\) 与自旋 \((m_s=+1/2,-1/2)\)，写出 orbital-major/spin-minor 的六个 component、旋转矩阵 shape 和公式。若实现采用 spin-major 顺序，应怎样转换？说明为何 shape 相同不足以证明正确。

## Q20-03 反线性与 \(\Theta^2\)

取

\[
J_s=\begin{pmatrix}0&1\\-1&0\end{pmatrix},
\qquad
\Theta\psi=J_s\psi^*.
\]

证明 \(\Theta(a\psi+b\phi)=a^*\Theta\psi+b^*\Theta\phi\) 和 \(\Theta^2=-I\)。给出一个含非零虚部的向量，用于区分正确反线性实现和错误线性 \(J_s\psi\)。

## Q20-04 实—复轨道基中的时间反演

在实 p 基中无自旋时间反演为 K。若 \(c_c=K_1c_r\)，推出复基 unitary part 的正确公式，并写出 \(m=(-1,0,1)\) 顺序的 \(J_1\)。解释为什么普通线性相似变换 \(K_1IK_1^\dagger\) 错误。

## Q20-05 Hamiltonian k-pair 约束

从固定基中的 \(\Theta=JK\) 写出时间反演不变 Bloch Hamiltonian 和 overlap 的 k-pair 公式。列出至少六个必须同步的 schema/provenance 字段，并说明为什么只比较 k 与 -k 的排序后本征值不足。

## Q20-06 Pauli 分解与磁性破缺

对

\[
H(k)=\varepsilon(k)I+\boldsymbol b(k)\cdot\boldsymbol\sigma
\]

推出时间反演不变时 \(\varepsilon\) 和 \(\boldsymbol b\) 的 k 奇偶性。计算 \(H_B=\sigma_z\) 相对其时间反演像的归一化 Frobenius 残差，并解释其物理含义。

## Q20-07 Kramers 正交性与 TRIM

设 \(H\) 时间反演不变且 \(\Theta^2=-I\)。证明 \(\psi\) 与 \(\Theta\psi\) 同能且正交。随后说明在 Bloch Hamiltonian 中，为什么一般 k 只得到 k/-k 谱配对，而同一 k 的 Kramers 简并还需要 \(-k=k+G\)。

## Q20-08 宇称、时间反演与复合作用

分别写出 P 和 Θ 对 \(r,p,L,S\) 的作用。若 P 与 Θ 对易且 \(P^2=I\)，计算 \((P\Theta)^2\)。列出至少两种不能直接套用该结果、必须重新推导的情形。

## Q20-09 自旋扩维的解析成本

无自旋 dense 轨道维数为 P。计算加入显式自旋后的维数、方块元素数、`float64` spinless 与 `complex128` spinful 的持久字节比，以及一般 dense 双侧作用的 MAC 数比例。说明这些因子为什么不能直接外推为真实软件 wall-time。

## Q20-10 端到端门控与授权边界

为阶段 E 的自旋/时间反演对象写出从输入 validator 到最终结论的检查顺序。必须覆盖 SU(2) lift、反线性、\(\Theta^2\)、basis J 变换、H/S k-pair、Kramers 条件、失败矩阵、成本和 provenance，并明确 M8/M9 授权边界。把每一部分映射到 D-E08/D-E09 与 T-E11/T-E12。
