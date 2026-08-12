# 第 20 章 自旋、时间反演与复表示接口

## 20.1 本章范围与 M8 边界

### 20.1.1 为什么阶段 E 需要高级物理接口

前五章已经建立空间旋转、\(O(3)\) 宇称、复球谐、CG 耦合和 Hamiltonian 轨道块。本章补上三类不能由纯整数角动量接口自动推出的对象：半整数自旋的 \(SU(2)\) 表示、反幺正时间反演，以及时间反演约束下的复 Hamiltonian。

目标是使后续实现能够回答以下问题：数组是整数角动量还是半整数角动量表示；时间反演是否需要 unitary part \(J\)；复共轭作用在哪些轴；\(H(\boldsymbol k)\) 与 \(H(-\boldsymbol k)\) 如何配对；Kramers 结论需要哪些物理条件。只写“考虑自旋”或“满足时间反演”不能替代这些合同。

### 20.1.2 本章不冻结 SOC、磁性或正式实践对象

本章使用确定性 \(2\times2\) 和小型 Kronecker 合成矩阵，不安装 DeepH/e3nn，不下载正式数据，不生成 DFT 标签，也不选择材料、赝势、基组、DFT/数据后端或软件版本。SOC、磁性、双群与非共线对象是否进入首个实践，属于 M8 集中决策。

因此，“本章可验证”只表示理论接口和合成夹具完备，不表示实际 DeepH 对象已经支持相同 schema，更不表示首个材料必须包含 SOC。

### 20.1.3 复数、共轭与反幺正算符的先修

线性算符满足

\[
U(a\psi+b\phi)=aU\psi+bU\phi,
\]

反线性算符满足

\[
\Theta(a\psi+b\phi)
=a^*\Theta\psi+b^*\Theta\phi.
\]

反幺正算符还保持内积模，并满足

\[
\langle\Theta\psi\mid\Theta\phi\rangle
=\langle\phi\mid\psi\rangle.
\]

在固定基中可写为

\[
\Theta=JK,
\]

其中 \(K\) 是逐 component 复共轭，\(J\) 是幺正矩阵。由于 \(KJ=J^*K\)，有

\[
\boxed{\Theta^2=JJ^*}.
\]

这不是普通矩阵平方 \(J^2\) 的一般替代式。实现必须同时测试反线性与 \(JJ^*\)，只测试 shape 或范数不充分。

## 20.2 \(SO(3)\)、\(SU(2)\) 与双值表示

### 20.2.1 \(SU(2)\) 到 \(SO(3)\) 的双覆盖

Pauli 矩阵取

\[
\sigma_x=
\begin{pmatrix}0&1\\1&0\end{pmatrix},
\quad
\sigma_y=
\begin{pmatrix}0&-i\\i&0\end{pmatrix},
\quad
\sigma_z=
\begin{pmatrix}1&0\\0&-1\end{pmatrix}.
\]

对单位轴 \(\widehat n\) 和主动转角 \(\theta\)，自旋 \(1/2\) 的固定 lift 为

\[
U_{1/2}(\widehat n,\theta)
:=\exp\!\left(-\frac{i\theta}{2}\widehat n\cdot\boldsymbol\sigma\right)
=\cos\frac\theta2 I_2
-i\sin\frac\theta2\widehat n\cdot\boldsymbol\sigma.
\]

它通过操作恒等式

\[
U_{1/2}(\boldsymbol\sigma\cdot v)U_{1/2}^\dagger
=\boldsymbol\sigma\cdot(Rv)
\]

映射到唯一 \(R\in SO(3)\)。\(U\) 与 \(-U\) 给出同一 \(R\)，所以映射是二对一。实际数组必须记录 lift 或等价的规范四元数，不能只由 \(R\) 猜测未记录的自旋相位链。

### 20.2.2 整数与半整数角动量

角动量 \(j\) 的 irrep 维数为

\[
2j+1.
\]

整数 \(j\) 给出 \(SO(3)\) 的单值线性表示；半整数 \(j\) 给出 \(SU(2)\) 的线性表示，若只视作 \(SO(3)\) 对象则是投影表示。第 16—19 章的 \(\ell=0,1,2\) 轨道表示均为整数角动量；本章的纯自旋通道是 \(j=1/2\)、维数 2。

一个表示标签至少应记录 `angular_kind=orbital|spin|total`、\(j\)、dimension、dtype、component 顺序、basis family、lift identity 和版本。把半整数自旋通道仅标成普通 \(\ell=0\) multiplicity 会丢失 \(2\pi\) 旋转和时间反演平方信息。

### 20.2.3 \(2\pi\) 旋转、态矢量符号与可观测量

对任意轴，空间矢量旋转满足

\[
R(2\pi)=I_3,
\]

而自旋 \(1/2\) lift 满足

\[
U_{1/2}(2\pi)=-I_2,
\qquad
U_{1/2}(4\pi)=+I_2.
\]

单个态矢量的整体负号不改变射线和期望值，但相对相位、连续旋转路径及与其他通道的干涉仍要求表示合同一致。代码不能把 \(-I_2\) 改写成 \(+I_2\) 后又声称逐步群作用完全相同；正确说法是两者对同一 \(SO(3)\) 元素代表不同 \(SU(2)\) lift，而物理射线可相同。

### 20.2.4 轨道表示与自旋表示的张量积

在轨道 component 为外轴、自旋 component \((m_s=+1/2,-1/2)\) 为内轴的 C-order 约定下，旋转表示为

\[
D_{\ell\otimes1/2}(R,U)
=D^{(\ell)}(R)\otimes U_{1/2}.
\]

shape 为

\[
\bigl(2(2\ell+1),2(2\ell+1)\bigr).
\]

例如 \(p\otimes\tfrac12\) 的维数为 6。该未耦合基可以再经 CG 变换到总角动量 \(j=\ell\pm1/2\)，但本章不冻结正式 SOC 数据采用未耦合还是耦合基；两种 schema 的选择留到 M8。任何转换都必须携带 CG 版本、输入快轴和 component provenance。

## 20.3 复表示与 Hamiltonian

### 20.3.1 复基中的幺正 \(D(R)\)

复球谐 coefficient、半整数自旋和两者的张量积都使用幺正表示：

\[
D^\dagger D=I,
\qquad
D(g_2g_1)=D(g_2)D(g_1).
\]

复共轭 \(D^*\)、转置 \(D^{\mathsf T}\) 和共轭转置 \(D^\dagger\) 是不同对象。第 17 章函数点值按 \(D^*\) 变换，coefficient 按 \(D\) 变换；本章态系数和 Hamiltonian 轨道/自旋轴继续使用 coefficient 作用。

### 20.3.2 \(H'=DHD^\dagger\) 和 Hermiticity

同一节点或同一 \(\boldsymbol k\) 上的 Hamiltonian 满足

\[
H'=DHD^\dagger.
\]

不同 receiver/sender 空间的块仍使用第 19 章公式

\[
H'_{ij}=D_iH_{ij}D_j^\dagger.
\]

若 \(H=H^\dagger\)，则

\[
(DHD^\dagger)^\dagger=DHD^\dagger.
\]

普通转置不能替代 \(\dagger\)。自旋扩维后，左右轨道、自旋和 shell 顺序必须同时进入 block provenance；只在最末轴追加长度 2 而不更新实际轨道身份不是完整 schema。

### 20.3.3 实—复基相似变换与轨道顺序

若 \(K_{\mathrm{orb}}\) 是第 17 章冻结的实轨道 coefficient 到复球谐 coefficient 映射，则自旋扩维基变换为

\[
K_{\mathrm{tot}}=K_{\mathrm{orb}}\otimes I_2.
\]

因此

\[
H_{\mathrm c}=K_{\mathrm{tot}}H_{\mathrm r}K_{\mathrm{tot}}^\dagger,
\qquad
D_{\mathrm c}=K_{\mathrm{tot}}D_{\mathrm r}K_{\mathrm{tot}}^\dagger.
\]

实/复路线比较必须固定 orbital-major/spin-minor 顺序。若使用 spin-major 顺序，必须给出显式置换并同步 H、D、J、mask 与 provenance；不能仅因 shape 相同而直接比较。

## 20.4 时间反演的反幺正性

### 20.4.1 复共轭 \(K\) 与反线性

在固定基中

\[
K\psi=\psi^*.
\]

对任意复标量 \(a\)，

\[
K(a\psi)=a^*K\psi.
\]

特别地，

\[
\Theta(i\psi)=-i\Theta\psi.
\]

这是区分反幺正与普通幺正矩阵乘法的最小故障夹具。只使用纯实向量会隐藏漏共轭错误。

### 20.4.2 无自旋 \(\Theta=K\) 和 \(\Theta^2=+I\)

统一约定中的无自旋主线使用实轨道基，故

\[
\Theta_0=K,
\qquad
\Theta_0^2=+I.
\]

这里“\(\Theta=K\)”是基依赖陈述，不是任意复轨道基中的绝对公式。在 DLMF-CS 复 \(|\ell,m\rangle\) coefficient 基中，定义

\[
(J_\ell)_{m',m}
=(-1)^m\delta_{m',-m},
\qquad
m,m'=-\ell,\ldots,\ell,
\]

则

\[
\Theta_\ell=J_\ell K,
\qquad
J_\ell J_\ell^*=+I
\]

对整数 \(\ell\) 成立。它与实轨道基中的 \(K\) 通过冻结基变换相容。若 coefficient 基变换为 \(c_{\mathrm c}=K_{\mathrm{orb}}c_{\mathrm r}\)，反幺正 unitary part 的变换是

\[
\boxed{
J_{\mathrm c}
=K_{\mathrm{orb}}J_{\mathrm r}K_{\mathrm{orb}}^{\mathsf T}
},
\]

而不是普通线性算符的 \(K_{\mathrm{orb}}J_{\mathrm r}K_{\mathrm{orb}}^\dagger\)。转置来自 \(c_{\mathrm r}^*=K_{\mathrm{orb}}^{\mathsf T}c_{\mathrm c}^*\)。

这里的 \((-1)^m\) 与常见 \((-1)^{\ell-m}\) 只差整个 \(\ell\) 通道的相位 \((-1)^\ell\)；本项目选前者，是为了与第 17 章冻结的 \(K_\ell\) 精确满足 \(J_{\ell,\mathrm c}=K_\ell K_\ell^{\mathsf T}\)，而不只满足相位等价。

### 20.4.3 自旋 \(1/2\) 的 \(J=i\sigma_y\) 与 \(\Theta=JK\)

按与上述 Pauli 矩阵一致的 component \((m_s=+1/2,-1/2)\) 顺序，固定

\[
J_s=i\sigma_y
=
\begin{pmatrix}
0&1\\
-1&0
\end{pmatrix},
\qquad
\Theta_s=J_sK.
\]

由于 \(J_s\) 为实矩阵且 \(J_s^2=-I\)，

\[
\boxed{\Theta_s^2=J_sJ_s^*=-I}.
\]

在实轨道 \(\otimes\) 自旋基中，\(J_{\mathrm{tot}}=I_{\mathrm{orb}}\otimes J_s\)。在复 \(|\ell,m\rangle\otimes|1/2,m_s\rangle\) 基中，

\[
J_{\mathrm{tot}}=J_\ell\otimes J_s,
\qquad
J_{\mathrm{tot}}J_{\mathrm{tot}}^*=-I.
\]

### 20.4.4 全局相位自由与代码固定矩阵

若

\[
\Theta'=e^{i\varphi}\Theta,
\]

则反线性使

\[
(\Theta')^2
=e^{i\varphi}e^{-i\varphi}\Theta^2
=\Theta^2.
\]

所以整体相位是物理自由。材料和代码仍固定上述实矩阵 \(J_s\)，以获得唯一字节对象和定向测试。另一个只差整体相位的 \(J\) 不应被宣称为物理错误，但若没有同步版本/元数据，就属于项目规范不一致。\(J=I\) 或 \(J=\sigma_x\) 则给 \(\Theta^2=+I\)，不是自旋 \(1/2\) 的等价相位选择。

代码版本固定为 `stageE-time-reversal-v1`。规范 UTF-8/无空白 JSON 中，spin-half payload

`["stageE-time-reversal-v1","spin-half",[0.5,-0.5],"complex128","J=i*sigma_y",[[[0,0],[1,0]],[[-1,0],[0,0]]]]`

的 SHA-256 为 `F8B5E9591B791A2DBD9B262736718C8B391B75DE6CE720335D1AD5B8F1AFF444`。实无自旋与复 \(\ell=1\) payload/hash 见 D-E08 第 4.4 节。schema 必须把数学对象 hash、实际 dtype 和实际数组字节 hash 分列。

## 20.5 时间反演约束

### 20.5.1 \(H(-\boldsymbol k)=JH(\boldsymbol k)^*J^\dagger\)

若基和 Bloch 相位约定已固定，时间反演把 \(\boldsymbol k\) 映到 \(-\boldsymbol k\)。时间反演不变 Hamiltonian 满足

\[
\boxed{
H(-\boldsymbol k)
=JH(\boldsymbol k)^*J^\dagger
}.
\]

若使用非正交基，overlap 也应满足相同类型的配对式

\[
S(-\boldsymbol k)=JS(\boldsymbol k)^*J^\dagger.
\]

两侧必须使用同一规范 \(\boldsymbol k\) 与 \(-\boldsymbol k\) 配对、同一 reciprocal representative、basis/shell/component 顺序和 provenance。只比较排序后的本征值不能验证矩阵接口。

### 20.5.2 时间反演不变、磁性破缺和外场条件

一般 \(2\times2\) Hermitian 自旋块可写为

\[
H(\boldsymbol k)=\varepsilon(\boldsymbol k)I
+\boldsymbol b(\boldsymbol k)\cdot\boldsymbol\sigma,
\]

其中 \(\varepsilon\) 和 \(\boldsymbol b\) 为实函数。固定 \(J_s\) 满足

\[
J_s\sigma_a^*J_s^\dagger=-\sigma_a,
\qquad a=x,y,z.
\]

因此时间反演约束等价于

\[
\varepsilon(-\boldsymbol k)=\varepsilon(\boldsymbol k),
\qquad
\boldsymbol b(-\boldsymbol k)=-\boldsymbol b(\boldsymbol k).
\]

均匀 Zeeman 或交换场 \(\boldsymbol M\cdot\boldsymbol\sigma\) 若在 \(\boldsymbol k\to-\boldsymbol k\) 下保持同号，则破坏该约束。不能把破缺样例通过事后把 \(\boldsymbol M\) 人工反号伪装成同一物理输入的时间反演对称。

### 20.5.3 \(\Theta^2=-I\) 与 Kramers 条件

设 \(H\) 时间反演不变、\(H\psi=E\psi\)，则

\[
H(\Theta\psi)=E(\Theta\psi).
\]

若 \(\Theta^2=-I\)，则 \(\Theta\psi\) 不能与 \(\psi\) 成比例；更强地，反幺正内积恒等式给出

\[
\langle\psi\mid\Theta\psi\rangle=0.
\]

因此两者是正交同能态。对有限系统或同一 Hilbert 空间中的时间反演不变 Hamiltonian，这给出 Kramers 成对。对 Bloch Hamiltonian，\(\Theta\) 一般把 \(\boldsymbol k\) 态映到 \(-\boldsymbol k\) 态；只有在时间反演不变动量满足

\[
-\boldsymbol k=\boldsymbol k+\boldsymbol G
\]

时，才能直接推出同一 \(\boldsymbol k\) 的 Kramers 简并。

### 20.5.4 仅有代数恒等式不足以证明物理简并

验证 \(JJ^*=-I\) 只说明反幺正平方的表示类型。Kramers 结论还要求：

- \(H\) 的定义域由 \(\Theta\) 保持；
- Hamiltonian 实际满足时间反演约束；
- 讨论 Bloch 态时正确处理 \(\boldsymbol k\leftrightarrow-\boldsymbol k\)；
- 没有把外磁场、磁序或其他破缺项当成不变输入；
- 数值离散和 basis/provenance 没有错配。

因此，一个 \(J\) 单元测试通过不能证明任意材料或任意预测 Hamiltonian 具有 Kramers 简并。

## 20.6 宇称、旋转与时间反演的组合

### 20.6.1 空间反演与自旋轴向量

空间反演 \(P\) 下，位置和动量是极向量：

\[
\boldsymbol r\mapsto-\boldsymbol r,
\qquad
\boldsymbol p\mapsto-\boldsymbol p.
\]

轨道角动量和自旋是轴向量：

\[
\boldsymbol L=\boldsymbol r\times\boldsymbol p\mapsto\boldsymbol L,
\qquad
\boldsymbol S\mapsto\boldsymbol S.
\]

时间反演则满足

\[
\boldsymbol r\mapsto\boldsymbol r,
\quad
\boldsymbol p\mapsto-\boldsymbol p,
\quad
\boldsymbol L\mapsto-\boldsymbol L,
\quad
\boldsymbol S\mapsto-\boldsymbol S.
\]

所以“自旋不因空间反演变号”与“自旋因时间反演变号”必须分开。仅测 \(SO(3)\) 正旋转无法发现这类错误。

### 20.6.2 复合对称作用和次序

时间反演与纯空间旋转相容。在固定 coefficient 基中，这一条件写为

\[
\boxed{
JD(R)^*J^\dagger=D(R)
}.
\]

对轨道—自旋张量积，J 和 D 必须使用相同的 orbital/spin 轴顺序与同一 SU(2) lift。该等式同时检验共轭、J、复表示和 component provenance；只分别验证 \(D^\dagger D=I\) 与 \(JJ^*=\pm I\) 不足。

复合反幺正算符仍需显式记录次序。若 \(P\) 与 \(\Theta\) 对易且 \(P^2=I\)，则

\[
(P\Theta)^2=P^2\Theta^2.
\]

在有反演且时间反演的自旋 \(1/2\) 系统中，\(P\Theta\) 可把 \(\boldsymbol k\) 映回同一 \(\boldsymbol k\)，并在满足全部条件时支持每个 \(\boldsymbol k\) 的成对结构。但若 \(P\) 与 \(\Theta\) 不对易、basis 中含额外平移或磁性空间群操作，上式必须重新推导，不能套用。

### 20.6.3 双群和更高阶磁性范围的保留接口

包含半整数自旋时，空间群操作通常需要双群 lift；包含反幺正磁性操作时，还可能需要磁群/共表示。阶段 E 只登记以下最小字段：空间操作、\(SU(2)\) lift、是否反幺正、unitary part \(J\)、复共轭标志、平移、basis/component 顺序和 group-element identity。

本章不构造特定材料的双群表、磁性空间群、非共线自旋 texture 或 SOC 轨道投影。它们是否成为实践目标、使用何种软件对象和数据后端，由 M8 决定。

## 20.7 合成验证

### 20.7.1 \(\Theta^2=\pm I\) 的逐向量复算

固定复向量 \(\psi\ne0\)。无自旋实基中

\[
K(K\psi)=\psi.
\]

自旋 \(1/2\) 中

\[
J_s\bigl(J_s\psi^*\bigr)^*
=J_sJ_s^*\psi
=-\psi.
\]

还必须验证

\[
\Theta(i\psi)+i\Theta\psi=0.
\]

这些测试应使用非零实部和虚部，报告 dtype、shape、norm、最大残差和固定 \(J\) hash；只测标准实基向量不能覆盖反线性。

### 20.7.2 合成 \(2\times2\) 自旋 Hamiltonian

取一维合成模型

\[
H(k)
=\bigl(2+0.3\cos k\bigr)I
+\sin k\,\sigma_x
+0.4\sin k\,\sigma_z.
\]

标量项为偶函数，Pauli 系数为奇函数，所以

\[
H(-k)=J_sH(k)^*J_s^\dagger.
\]

在 \(k=0,\pi\) 处，\(\sin k=0\)，Hamiltonian 与 \(I_2\) 成正比并显式二重简并。这个夹具只证明合成接口，不支持对真实材料的能带简并判断。

### 20.7.3 漏共轭、错 \(J\) 和磁性破缺反例

T-E11 至少实际执行：

- 把 \(JK\) 错写成线性 \(J\)，用 \(\Theta(i\psi)=-i\Theta\psi\) 定向检出；
- 使用 \(J=I\) 或 \(\sigma_x\)，使 \(JJ^*=+I\)；
- 在 Hamiltonian 配对中漏掉 \(^*\)；
- 把 \(-k\) 行与错误 k 点或错误 basis row 配对；
- 对 \(H_B=B\sigma_z\)、\(B\ne0\) 仍宣称时间反演通过。

对 \(H_B=\sigma_z\)，归一化残差

\[
\rho\!\left(H_B,J_sH_B^*J_s^\dagger\right)=2,
\]

是固定定向失败。整体相位不同但元数据同步的 \(J\) 不应作为物理失败；它只在违反项目固定规范时报告 schema 不一致。

### 20.7.4 D-E08/D-E09 与 T-E11/T-E12

[解析推导](../../../04_derivations/stageE/20_spin_time_reversal_complex.md) 完成 D-E08，并给出 D-E09 的自旋扩维局部子对象。Q20/A20 提供 10 组配对题解。M7-09 已在 [Stage E 代码与复现说明](../../../05_code_exercises/stageE_synthetic_equivariance/README.md) 中执行 T-E11 的 \(\Theta^2\)、反线性、Hamiltonian 配对与磁性破缺，以及 T-E12 的 dtype/rank/shape、basis/J/version、k-pair/provenance 和授权边界故障矩阵；独立放行证据见 [`M7_stageE_code_blocking_reaudit.md`](../../../08_audits/M7_stageE_code_blocking_reaudit.md)。本章解析结果本身仍不能冒充这些 A/B 代码与独立审计证据。

## 20.8 与 DeepH 和 M8 的接口

### 20.8.1 论文级 SOC 方法对象与证据边界

DH-02 支持的本章联系限于：含 SOC 的复 Hamiltonian 可以成为等变学习目标，空间与自旋表示需要一致处理。该论文级方法范围不等于当前工作区已获得软件、数据、训练权重或正式 schema，也不支持把本章教学矩阵当作 DeepH-E3 原生数组接口。

### 20.8.2 M8 高级物理范围的候选分支

进入 M8 时应集中比较至少三类范围：无自旋/非磁基线；时间反演保持的自旋/SOC 路线；磁性或时间反演破缺路线。比较字段包括科学目标、数据/DFT 后端能力、软件对象、复矩阵与自旋 schema、验证复杂度、计算资源、时间预算和失败风险。

本章不在三者中预选。尤其不能因为已经写出 \(J_s\) 和 Kramers 证明，就隐含决定首个材料必须含重元素、SOC 或磁性。

### 20.8.3 本章完成不授权 DeepH 安装或正式数据动作

M7-07 通过只允许进入阶段 E 的统一推导、合成代码、自学材料和总审计。M8 前仍禁止安装 DeepH/e3nn、下载正式训练数据、生成 DFT 标签或选择材料/后端/实践版本。M8 方案由用户冻结后，M9 外部安装、数据下载或复现实验前仍需再次明确授权。

### 20.8.4 章节门控和阶段 E 总审计入口

章节门控要求：来源逐项定位；正文与三级提纲一致；D-E08/D-E09 子对象具备条件、维度、正反例和最终不变量；至少两个正确例与两个失败例；Q20/A20 10/10；严格 Pandoc/MathML、链接和控制字符通过；新的独立内容审计问题为 0。

历史门控顺序为 M7-08 统一推导审计、M7-09 代码审计、M7-10 自学材料审计和 M7-11 阶段总审计；这些门控均已通过，M7 已完成。当前仍须通过 D-011 指定的 `gpt-5.6-sol`/`max` M3—M7 全量独立总审计后，才可进入 M8 决策冻结。

本章由此冻结了 \(SO(3)\)/\(SU(2)\) 双覆盖、半整数自旋表示、复 Hamiltonian、反幺正时间反演、\(\Theta^2=\pm I\)、Bloch k-pair 和 Kramers 成立条件。最关键的边界是：\(J\) 的代数恒等式、Hamiltonian 的对称约束、材料是否具有该对称性以及实践是否纳入 SOC/磁性，是四个不同层级，不能互相替代。
