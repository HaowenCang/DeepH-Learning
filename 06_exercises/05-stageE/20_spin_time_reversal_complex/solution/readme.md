# 第 20 章参考解答

## A20-01 \(SU(2)\) lift 与 \(2\pi\) 旋转

代入半角公式：

\[
U(2\pi)=\cos\pi I-i\sin\pi\,\widehat n\cdot\sigma=-I_2,
\]

\[
U(4\pi)=\cos2\pi I-i\sin2\pi\,\widehat n\cdot\sigma=I_2.
\]

SU(2) 到 SO(3) 是双覆盖，U 与 -U 对同一 v 的共轭作用

\[
U(\sigma\cdot v)U^\dagger
\]

相同，因此都映到同一 R。态射线不受整体负号影响，但连续 lift 和相对相位需要保留。数组应记录同一 rotation/quaternion ID、规范四元数或等价 SU(2) lift ID、component 顺序、dtype 和版本；只存 R 不能恢复唯一 lift。

## A20-02 轨道—自旋张量积的维度与顺序

component 为

\[
(p_x\uparrow,p_x\downarrow,
p_y\uparrow,p_y\downarrow,
p_z\uparrow,p_z\downarrow).
\]

表示为

\[
D_{p\otimes s}=R\otimes U_{1/2}\in\mathbb C^{6\times6}.
\]

spin-major 顺序需要显式置换 P：

\[
D_{\mathrm{spin-major}}=P(R\otimes U)P^{\mathsf T}.
\]

H、J、mask、actual orbital/spin pair 和 provenance 都必须同步施加 P。两种顺序的数组均为 \(6\times6\)，所以 rank/shape 检查无法发现静默轴互换。

## A20-03 反线性与 \(\Theta^2\)

由逐元素共轭，

\[
\Theta(a\psi+b\phi)
=J_s(a\psi+b\phi)^*
=a^*\Theta\psi+b^*\Theta\phi.
\]

两次作用为

\[
\Theta^2\psi
=J_s(J_s\psi^*)^*
=J_sJ_s^*\psi
=-\psi.
\]

可取

\[
\psi=(1,1+i)^{\mathsf T}/\sqrt3.
\]

正确实现满足 \(\Theta(i\psi)+i\Theta\psi=0\)。错误线性 \(L(\psi)=J_s\psi\) 给

\[
\lVert L(i\psi)+iL(\psi)\rVert_2=2.
\]

因此反线性和平方符号应分开测试。

## A20-04 实—复轨道基中的时间反演

由

\[
c_c=K_1c_r,
\qquad
c_r^*=K_1^{\mathsf T}c_c^*,
\]

得到

\[
J_c=K_1J_rK_1^{\mathsf T}.
\]

实 p 基中 \(J_r=I_3\)，故

\[
J_1=K_1K_1^{\mathsf T}
=
\begin{pmatrix}
0&0&-1\\
0&1&0\\
-1&0&0
\end{pmatrix}.
\]

它满足 \(J_1J_1^*=I_3\)。误用 \(K_1IK_1^\dagger=I_3\) 把反幺正 unitary part 当普通线性算符；与正确 J1 的归一化残差为 1.1547005384。

## A20-05 Hamiltonian k-pair 约束

时间反演不变要求

\[
H(-k)=JH(k)^*J^\dagger,
\qquad
S(-k)=JS(k)^*J^\dagger.
\]

至少同步：structure ID、k row、-k partner row、reciprocal representative、basis family、shell 顺序、actual orbital/spin identity、component 顺序、J version/hash、dtype、mask 和 H/S provenance。只比较本征值会丢掉基矢、相位、矩阵元和行映射；许多不同矩阵同谱，因此同谱不是矩阵级时间反演接口的充分证据。

## A20-06 Pauli 分解与磁性破缺

固定 Js 满足

\[
J_s\sigma_a^*J_s^\dagger=-\sigma_a.
\]

所以

\[
\varepsilon(-k)=\varepsilon(k),
\qquad
\boldsymbol b(-k)=-\boldsymbol b(k).
\]

对 \(H_B=\sigma_z\)，时间反演像为 \(-\sigma_z\)，且两者 Frobenius 范数均为 \(\sqrt2\)，故

\[
\rho(H_B,-H_B)
=\frac{\lVert2\sigma_z\rVert_F}{\sqrt2}
=2.
\]

这表示保持同号的 Zeeman/交换场破坏时间反演，不是浮点误差。

## A20-07 Kramers 正交性与 TRIM

由 H 与 Θ 相容，

\[
H(\Theta\psi)=\Theta(H\psi)=E\Theta\psi.
\]

反幺正内积恒等式给

\[
\langle\Theta\psi\mid\Theta^2\psi\rangle
=\langle\Theta\psi\mid\psi\rangle.
\]

代入 \(\Theta^2=-I\)，左右相差负号，因此

\[
\langle\Theta\psi\mid\psi\rangle=0.
\]

Bloch 情形中 Θ 把 \(\mathcal H_k\) 映到 \(\mathcal H_{-k}\)。一般 k 的同能伙伴位于另一个 fiber；只有 \(-k=k+G\) 且 reciprocal/basis 回拉正确时，才是同一 k 的正交 Kramers 对。

## A20-08 宇称、时间反演与复合作用

作用表为

\[
P:(r,p,L,S)\mapsto(-r,-p,+L,+S),
\]

\[
\Theta:(r,p,L,S)\mapsto(+r,-p,-L,-S).
\]

若 \([P,\Theta]=0\)、\(P^2=I\)，则

\[
(P\Theta)^2=P\Theta P\Theta=P^2\Theta^2.
\]

不能直接套用的情形包括：P 与 Θ 不对易；空间操作含非平凡平移/非共形操作；磁性空间群含额外反幺正元素；basis 中 P 交换子晶格并带 k 依赖相位；项目尚未冻结的双群/共表示。此时应从实际作用和次序重新计算平方。

## A20-09 自旋扩维的解析成本

维数

\[
P\to2P.
\]

dense 方块元素数

\[
P^2\to4P^2.
\]

`float64` spinless 字节为 \(8P^2\)，`complex128` spinful 字节为

\[
16(2P)^2=64P^2,
\]

所以比值为 8。一般 dense 双侧作用按两个 n×n matmul 计 \(2n^3\) MAC，n 翻倍使 MAC 数变为 8 倍；complex MAC 的实 FLOP 展开还应另报。

真实 wall-time 还取决于稀疏性、shell block、Hermiticity、Kronecker kernel、内存调度、硬件和库实现。解析因子只能用于检查指定 dense 对象，不能代替 M7-09 的实际数组/FLOP/bytes 或跨硬件性能结论。

## A20-10 端到端门控与授权边界

检查顺序应为：

1. 严格验证 R/U、J、ψ、H/S、k/partner、dtype/rank/shape/有限性和完整 provenance；
2. 验证 SU(2) lift 的幺正、U→R、2π=-I、4π=I 与同一 lift identity；
3. 验证 \(\Theta(a\psi+b\phi)\) 的反线性和 \(\Theta^2=JJ^*=\pm I\)；
4. 按 \(J_c=KJ_rK^{\mathsf T}\) 检查 basis route、component 顺序和 `stageE-time-reversal-v1` payload/hash；
5. 检查 H/S Hermiticity与 \(H(-k)=JH(k)^*J^\dagger\)、\(S(-k)=JS(k)^*J^\dagger\)；
6. 只有 H 时间反演不变且 \(\Theta^2=-I\) 时检查同能/正交；同 k 简并还需 TRIM；
7. 实际执行漏共轭、错误 J、错误 K†、k 错行、spin/orbital 轴错位、Zeeman 破缺和一般 k 误判；
8. 分列维数、entries、dtype bytes、complex MAC/FLOP 与实际数组口径；
9. 输出逐对象残差、最坏 ID、样本数、seed/dtype、失败 rejected/total 和授权扫描；
10. 保持 M8 前不安装 DeepH/e3nn、不下载正式数据、不生成 DFT 标签、不选择材料/后端/软件/SOC-磁性实践；M8 冻结后 M9 外部动作仍需明确授权。

D-E08 对应 T-E11，并与 T-E12 共享 schema/失败矩阵；D-E09 子对象对应 T-E10/T-E12。章内解析结果不等于 M7-09 已执行。M7-07 通过只允许继续阶段 E 内部建设，不授权 M8/M9 外部动作。
