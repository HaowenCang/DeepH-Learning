# D-E08 与 D-E09 子对象：自旋、反幺正时间反演与成本

## 1. 目标、范围与未授权对象

本文件完成 D-E08：

- \(SU(2)\) 自旋 \(1/2\) lift 与 \(2\pi\) 符号；
- 固定基中的反幺正作用 \(\Theta=JK\)；
- 无自旋实基、复轨道 coefficient 基和自旋基之间的接口；
- 时间反演 Hamiltonian 配对、Kramers 条件及破缺边界；
- D-E09 的自旋扩维解析成本子对象。

所有数值对象均为确定性合成矩阵。本文件不安装 DeepH/e3nn，不选择 SOC/磁性实践，不下载数据，不生成 DFT 标签；T-E11/T-E12 的正式 A/B 执行证据见 [M7-09 代码说明](../../05_code_exercises/stageE_synthetic_equivariance/README.md) 与 [独立定点复核](../../08_audits/M7_stageE_code_blocking_reaudit.md)。

## 2. 符号、维度、dtype、基与身份

| 符号 | rank/shape | dtype 与基 | 身份/provenance |
|---|---|---|---|
| \(R\) | rank 2，\((3,3)\) | `float64`/`float32`，主动列向量 \(SO(3)\) | rotation/quaternion ID、seed、dtype、validator |
| \(U_{1/2}\) | rank 2，\((2,2)\) | `complex128`/`complex64`，\(m_s=(+1/2,-1/2)\) | 与 \(R\) 同一 lift identity；轴角/四元数符号与版本 |
| \(D^{(\ell)}\) | rank 2，\((2\ell+1,2\ell+1)\) | DLMF-CS coefficient 基或冻结实轨道基 | \(\ell\)、component 顺序、K/hash |
| \(D_{\ell\otimes s}\) | rank 2，\((2(2\ell+1),2(2\ell+1))\) | `complex*`，orbital-major/spin-minor | orbital/spin component pair、Kronecker 顺序、lift ID |
| \(J_0\) | 反幺正 unitary part 为 \(I_P\) | 实轨道 basis；\(\Theta=K\) | `spinless-real`、basis/version/hash |
| \(J_\ell\) | rank 2，\((2\ell+1,2\ell+1)\) | 复 coefficient 基，\((J_\ell)_{m',m}=(-1)^m\delta_{m',-m}\) | \(m\) 升序、K/hash、整体相位规范 |
| \(J_s\) | rank 2，\((2,2)\) | `complex*`，固定实矩阵 \(i\sigma_y\) | `spin-half`、\(m_s\) 顺序、version/hash |
| \(\psi\) | rank 1，\((d,)\) | 与 J 相同 complex dtype/basis | state/fixture ID；有限且非零 |
| \(H(k)\) | rank 3 批对象 \((N_k,d,d)\)，单点 rank 2 | complex Hermitian coefficient 基 | k row、partner row、reciprocal representative、basis/shell/component、mask |
| \(S(k)\) | 与 \(H(k)\) 相同 | 可选 complex Hermitian overlap | 与 H 同一 k/basis/provenance 行 |

所有 validator 必须严格检查 rank、shape、dtype、有限性和完整身份，不允许把 `float` J、错误 component 轴或广播后的 k row 静默接受。旋转、时间反演和 k-pair 不改变 structure ID、实际轨道身份或离散 basis 标签。

## 3. \(SU(2)\) lift 与整数/半整数边界

### 3.1 自旋 \(1/2\) 指数

Pauli 代数给

\[
(\widehat n\cdot\boldsymbol\sigma)^2=I_2.
\]

因此幂级数的偶次项和奇次项分别求和为

\[
U_{1/2}(\widehat n,\theta)
=\exp\!\left(-\frac{i\theta}{2}\widehat n\cdot\boldsymbol\sigma\right)
=\cos\frac\theta2 I_2
-i\sin\frac\theta2\widehat n\cdot\boldsymbol\sigma.
\]

直接得到

\[
U_{1/2}(2\pi)=-I_2,
\qquad
U_{1/2}(4\pi)=I_2.
\]

### 3.2 双覆盖的操作定义

对任意实向量 \(v\)，定义 R 为满足

\[
U(\boldsymbol\sigma\cdot v)U^\dagger
=\boldsymbol\sigma\cdot(Rv)
\]

的实矩阵。Pauli 迹正交性给

\[
R_{ab}
=\frac12\operatorname{tr}
\left(\sigma_aU\sigma_bU^\dagger\right).
\]

把 U 换成 \(-U\) 时右侧不变，故两者给同一 R。T-E11 只使用由 T-E01 已验证的 R/lift 对；不得从任意近似 R 反解未记录 lift 后再比较连续自旋路径。

### 3.3 轨道—自旋张量积

冻结 component 次序为 orbital-major/spin-minor：

\[
D_{\ell\otimes s}=D^{(\ell)}\otimes U_{1/2}.
\]

输入/输出维数均为 \(2(2\ell+1)\)。成立条件是两个因子来自同一空间旋转/lift、dtype/basis 一致、Kronecker 快轴固定。最终群律为

\[
D_{\ell\otimes s}(g_2g_1)
=D_{\ell\otimes s}(g_2)D_{\ell\otimes s}(g_1).
\]

若只把 R 作用到轨道轴、遗漏 U，自旋 component 的空间旋转语义即不完整；若交换 Kronecker 轴却不施加置换，shape 仍相同但 component provenance 错误。

## 4. 反幺正作用、平方和基变换

### 4.1 反线性与平方

定义

\[
\Theta\psi:=J\psi^*.
\]

则

\[
\Theta(a\psi+b\phi)
=a^*\Theta\psi+b^*\Theta\phi,
\]

以及

\[
\Theta^2\psi
=J(J\psi^*)^*
=JJ^*\psi.
\]

所以无自旋实基 \(J_0=I\) 给 \(+I\)，自旋 \(1/2\) 的

\[
J_s=
\begin{pmatrix}0&1\\-1&0\end{pmatrix}
\]

给 \(-I\)。测试必须同时执行

\[
\rho(\Theta^2\psi,\pm\psi)
\]

和反线性残差

\[
\rho(\Theta(i\psi),-i\Theta\psi).
\]

### 4.2 复轨道基中的 \(J_\ell\)

在整数 \(\ell\)、\(m=-\ell,\ldots,\ell\) 升序中，冻结

\[
(J_\ell)_{m',m}=(-1)^m\delta_{m',-m}.
\]

两次作用的非零项要求 \(m''=m\)，相位为

\[
(-1)^m(-1)^{-m}=1,
\]

故

\[
J_\ell J_\ell^*=I_{2\ell+1}.
\]

对自旋扩维复轨道基，

\[
J_{\ell\otimes s}=J_\ell\otimes J_s,
\]

所以

\[
J_{\ell\otimes s}J_{\ell\otimes s}^*
=(+I)\otimes(-I)=-I.
\]

### 4.3 反幺正 unitary part 的基变换

设 coefficient 基变换

\[
c_{\mathrm c}=Kc_{\mathrm r}.
\]

若 \(\Theta_{\mathrm r}c_{\mathrm r}=J_{\mathrm r}c_{\mathrm r}^*\)，则

\[
\begin{aligned}
\Theta_{\mathrm c}c_{\mathrm c}
&=KJ_{\mathrm r}(K^\dagger c_{\mathrm c})^*\\
&=KJ_{\mathrm r}K^{\mathsf T}c_{\mathrm c}^*.
\end{aligned}
\]

因此

\[
\boxed{J_{\mathrm c}=KJ_{\mathrm r}K^{\mathsf T}}.
\]

对 \(\ell=1\)、\(J_{\mathrm r}=I_3\) 和第 17 章 K1，得到

\[
J_1=K_1K_1^{\mathsf T}
=
\begin{pmatrix}
0&0&-1\\
0&1&0\\
-1&0&0
\end{pmatrix}.
\]

若误用 \(K_1K_1^\dagger=I_3\)，归一化残差为 \(1.1547005384\)。这是 D-E08 的定向基变换失败，不得用整体相位自由掩盖，因为 I 与 J1 并非整体相位关系。

### 4.4 规范 payload 与 hash

规范 payload 使用 UTF-8、无空白 JSON；复数矩阵元素编码为 `[real,imag]`。版本统一为 `stageE-time-reversal-v1`：

| 对象 | payload | SHA-256 |
|---|---|---|
| spinless real | `["stageE-time-reversal-v1","spinless-real","real-orbital","complex","Theta=K","Theta2=+I"]` | `56342DB661DA6F8D9CC8C3BF6E241DCB9817F42E63A33CAD9AF9364BCC8DF6EC` |
| spin half | `["stageE-time-reversal-v1","spin-half",[0.5,-0.5],"complex128","J=i*sigma_y",[[[0,0],[1,0]],[[-1,0],[0,0]]]]` | `F8B5E9591B791A2DBD9B262736718C8B391B75DE6CE720335D1AD5B8F1AFF444` |
| orbital l1 | `["stageE-time-reversal-v1","orbital-l1",[-1,0,1],"complex128","J=K1@K1.T",[[[0,0],[0,0],[-1,0]],[[0,0],[1,0],[0,0]],[[-1,0],[0,0],[0,0]]]]` | `230AA31FC0201B4F2D7F8981A3244049C280F75CB2C753F38F9CE9D86A250980` |

`complex64` 执行可由同一精确整数矩阵转换 dtype，但摘要必须记录实际 dtype；不能把 `complex128` payload hash 冒充实际数组字节 hash。

## 5. Hamiltonian 时间反演约束

### 5.1 从 \([H,\Theta]=0\) 到 k-pair

时间反演把 Bloch k 映为 \(-k\)。在固定 basis/Bloch 规范下，

\[
H(-k)\Theta\psi_k
=\Theta H(k)\psi_k.
\]

代入 \(\Theta=JK\) 并比较任意 \(\psi_k\) 的系数，得到

\[
\boxed{H(-k)=JH(k)^*J^\dagger}.
\]

若有非正交 overlap，同理得到

\[
S(-k)=JS(k)^*J^\dagger.
\]

成立条件包括：H/S Hermitian；J 与 basis 顺序相同；k 与 -k 的 reciprocal representative 规范唯一；partner row、structure、shell、actual orbital、mask 和 provenance 完整；破缺场未被错误标成不变输入。

### 5.2 Pauli 分解

任意 \(2\times2\) Hermitian 矩阵写为

\[
H(k)=\varepsilon(k)I+\sum_{a=x,y,z}b_a(k)\sigma_a,
\]

其中系数实。直接相乘得

\[
J_s\sigma_a^*J_s^\dagger=-\sigma_a.
\]

因此时间反演不变当且仅当

\[
\varepsilon(-k)=\varepsilon(k),
\qquad
b_a(-k)=-b_a(k).
\]

该条件把 scalar 偶函数、spin vector 奇函数和 k-pair 身份分开，适合作为 T-E11 的逐字段 oracle。

### 5.3 固定数值正例

取

\[
H(k)=\bigl(2+0.3\cos k\bigr)I
+\sin k\,\sigma_x
+0.4\sin k\,\sigma_z.
\]

在 \(k=0.7\) 时

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
\end{pmatrix},
\]

全精度 `complex128` 配对残差为 0。本征值约 \(1.53560897,2.92329634\)，一般 k 不简并。

### 5.4 固定破缺反例

取 \(H_B=\sigma_z\)。时间反演像为 \(-\sigma_z\)，所以

\[
\rho\!\left(H_B,J_sH_B^*J_s^\dagger\right)=2.
\]

若错误 J=I，平方符号变为 +I；若漏共轭但夹具 H 恰为实，Hamiltonian 单项可能偶然不能暴露错误，所以还必须用复向量反线性夹具和含 \(\sigma_y\) 的复矩阵变异。T-E11 必须按对象分层报告，不允许一个失败被另一个测试的偶然通过遮蔽。

## 6. Kramers 条件与 Bloch 定义域

### 6.1 同能映射

若 H 时间反演不变且

\[
H\psi=E\psi,
\]

由于 E 为实数和反线性，

\[
H(\Theta\psi)=\Theta(H\psi)=E\Theta\psi.
\]

### 6.2 正交性

反幺正内积恒等式对 \(\phi=\psi\)、\(\chi=\Theta\psi\) 给

\[
\langle\Theta\psi\mid\Theta^2\psi\rangle
=\langle\Theta\psi\mid\psi\rangle.
\]

若 \(\Theta^2=-I\)，左侧又等于

\[
-\langle\Theta\psi\mid\psi\rangle.
\]

故

\[
\langle\Theta\psi\mid\psi\rangle=0,
\qquad
\langle\psi\mid\Theta\psi\rangle=0.
\]

### 6.3 TRIM 条件

Bloch 态通常满足

\[
\Theta:\mathcal H_k\to\mathcal H_{-k}.
\]

只有当

\[
-k=k+G
\]

且 reciprocal/basis 识别已正确回拉时，\(\psi_k\) 与 \(\Theta\psi_k\) 才属于同一 k fiber 并直接构成 Kramers 对。一般 k 只保证 k 与 -k 的谱成对，不保证同一 k 的两个本征值相等。

### 6.4 适用条件清单

D-E08 的 Kramers 最终结论只在以下条件共同成立时使用：

1. \(\Theta\) 是同一 Hilbert 对象上的反幺正算符；
2. \(\Theta^2=-I\)；
3. H 的定义域由 \(\Theta\) 保持且 H 时间反演不变；
4. Bloch 情形位于 TRIM，或结论明确写成 k/-k 跨 fiber 配对；
5. 没有外磁场、磁序或被保留为同号的时间反演奇项；
6. 数值 basis/k-pair/provenance 完整相容。

仅有 \(JJ^*=-I\) 不足以推出第 3—6 项。

## 7. 宇称、复合与保留边界

时间反演与旋转的 coefficient 表示满足

\[
\boxed{JD(R)^*J^\dagger=D(R)}.
\]

对 spin half，这可由 \(J_s\sigma_a^*J_s^\dagger=-\sigma_a\) 与反幺正对指数中 i 的共轭直接得到；对复轨道基，则由 \(D_c=KD_rK^\dagger\)、\(J_c=KJ_rK^T\) 和实基 \(D_r^*=D_r\) 得到。对轨道—自旋张量积，J、D 的 Kronecker 轴和 lift identity 必须一致。

空间反演下自旋是轴向量而不变，时间反演下自旋变号。若 P 与 \(\Theta\) 对易且 \(P^2=I\)，则

\[
(P\Theta)^2=P^2\Theta^2.
\]

在这些明确条件下，P 与 \(\Theta\) 都把 k 反号，复合 PΘ 可保持 k。但含非平凡平移、磁性群或不对易内部作用时必须重新推导。D-E08 不构造材料双群/磁群表，只冻结 operation identity、SU(2) lift、antiunitary flag、J/version、conjugation flag、translation 和 basis provenance 字段。

## 8. 固定逐向量正例与失败矩阵

取

\[
\psi=\frac1{\sqrt3}(1,1+i)^{\mathsf T}.
\]

直接得到

\[
\Theta\psi
=\frac1{\sqrt3}(1-i,-1)^{\mathsf T},
\quad
\Theta^2\psi=-\psi,
\quad
\langle\psi\mid\Theta\psi\rangle=0.
\]

正确反线性残差为 0。错误线性映射 \(L(\psi)=J_s\psi\) 给

\[
\lVert L(i\psi)+iL(\psi)\rVert_2=2.
\]

最低失败矩阵为：

| 变异 | 必须失败的对象 | 定量锚点/原因 |
|---|---|---|
| 漏 \(^*\)，把 Θ 当线性 J | anti-linearity | 固定 ψ 残差 2 |
| \(J=I\) 或 \(\sigma_x\) | Θ² sign | 得 +I 而非 -I |
| \(J_c=KJ_rK^\dagger\) | basis route | l=1 残差 1.1547005384 |
| k partner 行错配 | H time-reversal | 完整 partner/provenance 不同即拒绝 |
| H 配对漏复共轭 | complex H oracle | 含 σy/复轨道夹具稳定失败 |
| \(H_B=\sigma_z\) 仍标记 invariant | physical symmetry condition | 残差 2 |
| 一般 k 强求同 k 简并 | Kramers domain | 例 20-5 两本征值不同 |
| 整体相位同步的 J 被判物理错误 | phase false positive | Θ² 与 H 约束不变；仅规范元数据可不一致 |
| spin-major/orbital-major 静默互换 | component provenance | shape 相同但 pair identity 错 |
| 正式数据/DeepH/e3nn 依赖出现 | authorization | M8/M9 边界硬拒绝 |

## 9. D-E09 自旋扩维解析成本子对象

设无自旋轨道维数为 P。显式自旋扩维后

\[
d_{\mathrm{spin}}=2P,
\qquad
n_{\mathrm{entry}}=(2P)^2=4P^2.
\]

若无自旋 dense block 为 `float64`，持久字节为 \(8P^2\)；自旋 dense block 为 `complex128`，持久字节为

\[
16(2P)^2=64P^2,
\]

是前者 8 倍，其中 4 倍来自元素数，2 倍来自 dtype bytes。若比较同为 complex128，则只保留 4 倍元素因子。

把 dense 双侧作用作为两个一般矩阵乘法，n×n 块的 complex MAC 为

\[
2n^3.
\]

从 n=P 到 n=2P 时 MAC 数因子为 8；complex MAC 的实 FLOP 展开必须另报，不能套用 T-E10 实 reference kernel 的 2 FLOP/MAC。Kronecker、Hermiticity、稀疏性或 shell block kernel 可降低实际成本，但只有实现存在时才能按其操作图计数。

本节不是 T-E10 的 144 点执行证据。M7-09 已在 [代码说明](../../05_code_exercises/stageE_synthetic_equivariance/README.md) 中对实际数组逐名称给出 shape/dtype/nbytes、total/reference peak，并分离 H、J、partner map、临时 conjugate 和输出；wall-time 仍不得进入确定性 hash。

## 10. T-E11/T-E12 映射

| D-E08 子对象 | T-E 入口 | 正向证据 | 强制失败 |
|---|---|---|---|
| SU(2) lift/2π | T-E11/T-E12 | U 幺正、U→R、2π=-I、4π=I、lift identity | 只存 R、错半角、component/lift 漂移 |
| antiunitary/Θ² | T-E11 | 复向量反线性、\(JJ^*=\pm I\) | 漏共轭、J=I/σx、错误 dtype/shape |
| basis route | T-E11/T-E12 | \(J_c=KJ_rK^T\)、K/hash/顺序 | 错用 K†、m/spin 轴错位、版本/hash 错 |
| rotation/TR composition | T-E11/T-E12 | \(JD(R)^*J^\dagger=D(R)\)，轨道—自旋 Kronecker 轴一致 | 漏共轭、J/D 轴错位、lift identity 漂移 |
| H(k) pairing | T-E11/T-E12 | Hermitian、k/-k、H/S、basis/provenance | 漏 *、partner 错行、mask/轨道错位、Zeeman 误判 |
| Kramers | T-E11 | 同能、正交、TRIM | 只凭 Θ²、一般 k 强求同 k 简并、破缺 H |
| D-E09 cost | T-E10/T-E12 | 维数/entry/bytes 因子、实际数组口径 | “自旋只翻倍”、complex MAC 当实 MAC、漏数组 |

## 11. 最终可复算不变量与定义域

| 对象 | 最终不变量 | 定义域 |
|---|---|---|
| SU(2) | \(U^\dagger U=I\)，Uσ·vU†=σ·Rv，U(2π)=-I | 合法单位轴/角或已验证 lift；固定 component/lift identity |
| antiunitary | \(\Theta(a\psi+b\phi)=a^*\Theta\psi+b^*\Theta\phi\)；\(\Theta^2=JJ^*\) | 有限 complex \(\psi\)、幺正 J、固定 basis/dtype |
| integer orbital | \(J_\ell J_\ell^*=+I\)，\(J_c=KJ_rK^T\) | 整数 l、m 升序、冻结 K/hash/相位 |
| spin half | \(J_sJ_s^*=-I\) | spin order (+1/2,-1/2)、固定 stageE-time-reversal-v1 |
| rotation/TR | \(JD(R)^*J^\dagger=D(R)\) | J/D 同一 coefficient 基、component 顺序和 SU(2) lift identity |
| Hamiltonian | \(H(-k)=JH(k)^*J^\dagger\) | TR invariant H、正确 k partner、basis/mask/provenance 完整 |
| Kramers | HΘψ=EΘψ 且 <ψ|Θψ>=0 | Θ²=-I、H TR invariant；Bloch 同 k 简并还需 TRIM |
| D-E09 | dimension 2P、entries 4P²、指定 dtype bytes | dense 解析对象；不得外推实际稀疏/库成本 |

D-E08 因而只在表示、反幺正、Hamiltonian 对称性和 Bloch 定义域四层合同同时满足时支持 Kramers 结论。任何一层的代数通过都不能替代其余层；M8 高级物理选择和 M9 外部执行授权继续保持未决。
