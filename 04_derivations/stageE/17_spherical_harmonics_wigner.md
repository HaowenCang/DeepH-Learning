# D-E03 与 D-E09：复球谐、Wigner \(D\) 和复—实相似变换

## 1. 推导目标与边界

本文件完成 D-E03，并给出第 17 章所需的 D-E09 子部分：

- 固定 DLMF/Condon--Shortley 球谐、\(m\) 递增顺序和主动函数作用；
- 从操作性定义推导 Wigner \(D\) 的幺正性、逆和群律；
- 构造 \(\ell=1,2\) 的函数值映射 \(C_\ell\) 与系数映射 \(K_\ell=C_\ell^*\)；
- 推导复 Wigner 表与实 \(p,d\) 表的相似变换；
- 区分复球谐点值的 \(D^*\) 与展开系数的 \(D\)；
- 给出 \(z\) 轴解析例、点值例和未同步 \(m\) 逆序的定量失败；
- 记录实/复数组局部存储字节，并映射到 T-E04/T-E07/T-E10/T-E12。

本文件不采用某个未冻结的 Euler 角软件接口，不构造第 18 章 CG 表，也不在推导内部执行 A/B 或 144 点扫描；这些 M7-09 证据见 [代码说明](../../05_code_exercises/stageE_synthetic_equivariance/README.md) 和 [独立定点复核](../../08_audits/M7_stageE_code_blocking_reaudit.md)。统一约定见 [阶段 E 表示约定](../../03_textbook/stageE_representation_conventions.md)。

## 2. 符号、维度与适用条件

| 符号 | 类型或维度 | 含义 |
|---|---|---|
| \(\widehat r\) | \(\mathbb R^3\)，\(\lVert\widehat r\rVert=1\) | 单位球面方向 |
| \(Y_{\ell m}\) | 复球面函数 | DLMF/Condon--Shortley 基函数 |
| \(y_\ell(\widehat r)\) | \(\mathbb C^{2\ell+1}\) | 按 \(m=-\ell,\ldots,\ell\) 排列的点值列 |
| \(D^{(\ell)}(R)\) | \(\mathbb C^{(2\ell+1)\times(2\ell+1)}\) | 复 Wigner 表示矩阵 |
| \(r_1,r_2\) | \(\mathbb R^3,\mathbb R^5\) | 冻结实 \(p,d\) 函数值列 |
| \(C_1,C_2\) | \(\mathbb C^{3\times3},\mathbb C^{5\times5}\) | 函数值关系 \(y_\ell=C_\ell r_\ell\) |
| \(K_\ell=C_\ell^*\) | 同维幺正矩阵 | 实系数到复系数的映射 |
| \(c_{\mathrm r},c_{\mathrm c}\) | 实或复系数列 | 同一函数在实基与复基中的展开系数 |

所有向量和矩阵必须具有严格 rank/shape、有限元素、声明的复/实 dtype 和冻结索引顺序。球谐方向只对非零位移定义。相位或顺序改变若同步作用于点值、系数、表示、CG 和 provenance，可构成合法基变换；只改变其中一个接口必须失败。

## 3. 球谐规范

### 3.1 正交归一与共轭

采用 DLMF 14.30.1：

\[
Y_{\ell,m}(\theta,\phi)
=
\left[
\frac{(\ell-m)!(2\ell+1)}
{4\pi(\ell+m)!}
\right]^{1/2}
e^{im\phi}
\mathsf P_\ell^m(\cos\theta).
\]

这里 \(\mathsf P_\ell^m\) 是 DLMF 的 Ferrers 函数，相关相位已经包含在该定义链中；不能把另一教材对 associated Legendre 函数的相位约定直接叠加。

采用

\[
\int_{S^2}
Y_{\ell m}(\widehat r)^*
Y_{\ell' m'}(\widehat r)\,d\Omega
=\delta_{\ell\ell'}\delta_{mm'}
\]

和

\[
Y_{\ell,-m}
=(-1)^mY_{\ell m}^*.
\]

后式同时编码 Condon--Shortley 相位。若删除 \((-1)^m\)，低阶 \(p,d\) 恒等式和后续 CG 相位都会改变。

### 3.2 索引

固定 \(\ell\) 的数组索引

\[
j=m+\ell
\]

把 \(m=-\ell,\ldots,\ell\) 映到零基 \(j=0,\ldots,2\ell\)。任何逆序或软件特有顺序必须用显式置换矩阵表示。

## 4. 主动函数作用与 Wigner \(D\)

### 4.1 操作性定义

\[
[U(R)f](\widehat r)
=f(R^{-1}\widehat r).
\]

在固定 \(\ell\) 子空间中，

\[
U(R)Y_{\ell m}
=\sum_{m'}Y_{\ell m'}D^{(\ell)}_{m'm}(R).
\]

因此列是输入 \(m\)，行是输出 \(m'\)，且展开系数按 \(c'=Dc\) 变换。

### 4.2 群律

\[
\begin{aligned}
[U(R_2)U(R_1)f](\widehat r)
&=[U(R_1)f](R_2^{-1}\widehat r)\\
&=f(R_1^{-1}R_2^{-1}\widehat r)\\
&=f((R_2R_1)^{-1}\widehat r)\\
&=[U(R_2R_1)f](\widehat r).
\end{aligned}
\]

在同一基中取矩阵：

\[
D(R_2R_1)=D(R_2)D(R_1).
\]

### 4.3 幺正性

旋转保持球面测度，故

\[
\langle U(R)f,U(R)g\rangle
=\langle f,g\rangle.
\]

对正交归一基取矩阵得到

\[
D(R)^\dagger D(R)=I,
\qquad
D(R^{-1})=D(R)^\dagger.
\]

## 5. \(z\) 轴解析矩阵

绕 \(z\) 轴主动旋转 \(\alpha\) 时，

\[
R_z(\alpha)^{-1}
\]

把方位角变为 \(\phi-\alpha\)。由于 \(Y_{\ell m}\) 的方位依赖为 \(e^{im\phi}\)，

\[
U(R_z(\alpha))Y_{\ell m}
=e^{-im\alpha}Y_{\ell m}.
\]

因此

\[
D^{(\ell)}(R_z(\alpha))
=\operatorname{diag}_{m=-\ell}^{\ell}
(e^{-im\alpha}).
\]

在 \(\alpha=\pi/2\) 时：

\[
D^{(1)}
=\operatorname{diag}(i,1,-i),
\]

\[
D^{(2)}
=\operatorname{diag}(-1,i,1,-i,-1).
\]

## 6. \(\ell=1\) 复—实变换

### 6.1 函数值映射

由低阶恒等式

\[
y_1=C_1r_1,
\]

\[
C_1=
\begin{pmatrix}
s&-is&0\\
0&0&1\\
-s&-is&0
\end{pmatrix},
\qquad
s=\frac1{\sqrt2}.
\]

行范数均为 1，第一与第三行内积为

\[
s(-s)+(-is)^*(-is)
=-\frac12+\frac12=0,
\]

且中间行与其余行正交。因此 \(C_1\) 幺正。

### 6.2 系数映射

把实基函数写成行向量 \(\Phi_{\mathrm r}\)，复基函数写成 \(\Phi_{\mathrm c}\)。函数恒等式等价于

\[
\Phi_{\mathrm c}
=\Phi_{\mathrm r}C_1^{\mathsf T}.
\]

同一函数满足

\[
\Phi_{\mathrm r}c_{\mathrm r}
=\Phi_{\mathrm c}c_{\mathrm c}
=\Phi_{\mathrm r}C_1^{\mathsf T}c_{\mathrm c}.
\]

故

\[
c_{\mathrm r}=C_1^{\mathsf T}c_{\mathrm c},
\]

\[
c_{\mathrm c}
=(C_1^{\mathsf T})^{-1}c_{\mathrm r}
=C_1^*c_{\mathrm r}.
\]

定义 \(K_1=C_1^*\)。

### 6.3 相似变换

由

\[
c_{\mathrm c}'=K_1c_{\mathrm r}'
=K_1D^p c_{\mathrm r}
\]

和

\[
c_{\mathrm c}'=D^{(1)}c_{\mathrm c}
=D^{(1)}K_1c_{\mathrm r},
\]

对所有 \(c_{\mathrm r}\) 得

\[
D^{(1)}=K_1D^pK_1^\dagger,
\]

\[
D^p=K_1^\dagger D^{(1)}K_1.
\]

对第 5 节的 \(\pi/2\) 矩阵，右式严格给出 \(R_z(\pi/2)\)。

## 7. \(\ell=2\) 复—实变换

### 7.1 函数值矩阵

在冻结顺序中，

\[
C_2=
\begin{pmatrix}
-is&0&0&s&0\\
0&-is&s&0&0\\
0&0&0&0&1\\
0&-is&-s&0&0\\
is&0&0&s&0
\end{pmatrix}.
\]

各行的非零位置按两两正交组合成对，直接得到

\[
C_2C_2^\dagger=C_2^\dagger C_2=I_5.
\]

### 7.2 系数矩阵与相似变换

\[
K_2=C_2^*,
\qquad
c_{\mathrm c}=K_2c_{\mathrm r},
\]

\[
D^{(2)}=K_2D^dK_2^\dagger,
\qquad
D^d=K_2^\dagger D^{(2)}K_2.
\]

代入第 5 节 \(D^{(2)}(R_z(\pi/2))\)，得到

\[
D^d=
\begin{pmatrix}
-1&0&0&0&0\\
0&0&1&0&0\\
0&-1&0&0&0\\
0&0&0&-1&0\\
0&0&0&0&1
\end{pmatrix}.
\]

这与第 16 章的张量共轭公式逐项一致。

### 7.3 非 \(z\) 轴工作例

对

\[
R_x(\pi/2)=
\begin{pmatrix}
1&0&0\\
0&0&-1\\
0&1&0
\end{pmatrix},
\]

由 \(D^p=R\) 与第 16 章 \(B_a\) 共轭先得到实表

\[
D^d_{\mathrm r}(R_x)=
\begin{pmatrix}
0&0&-1&0&0\\
0&-1&0&0&0\\
1&0&0&0&0\\
0&0&0&1/2&-\sqrt3/2\\
0&0&0&-\sqrt3/2&-1/2
\end{pmatrix}.
\]

再按系数基变换：

\[
D^{(1)}_{\mathrm c}(R_x)
=K_1R_xK_1^\dagger
=
\begin{pmatrix}
1/2&-i/\sqrt2&-1/2\\
-i/\sqrt2&0&-i/\sqrt2\\
-1/2&-i/\sqrt2&1/2
\end{pmatrix},
\]

\[
D^{(2)}_{\mathrm c}(R_x)
=K_2D^d_{\mathrm r}(R_x)K_2^\dagger
=
\begin{pmatrix}
1/4&-i/2&-\sqrt6/4&i/2&1/4\\
-i/2&-1/2&0&-1/2&i/2\\
-\sqrt6/4&0&-1/2&0&-\sqrt6/4\\
i/2&-1/2&0&-1/2&-i/2\\
1/4&i/2&-\sqrt6/4&-i/2&1/4
\end{pmatrix}.
\]

\(R_x(\pi/2)^4=I_3\)，故群律要求

\[
D^{(1)}_{\mathrm c}(R_x)^4=I_3,
\qquad
D^{(2)}_{\mathrm c}(R_x)^4=I_5.
\]

反向相似变换严格恢复 \(R_x\) 和 \(D^d_{\mathrm r}(R_x)\)，从而把非 \(z\) 轴矩阵、群律与实—复双路线交叉验证。

## 8. 点值协变

### 8.1 复点值

操作性定义对每个输入 \(m\) 给出

\[
Y_{\ell m}(R^{-1}\widehat r)
=\sum_{m'}Y_{\ell m'}(\widehat r)D_{m'm}(R).
\]

把输入 \(m\) 作为点值列的行索引，得到

\[
y_\ell(R^{-1}\widehat r)
=D(R)^{\mathsf T}y_\ell(\widehat r).
\]

令 \(\widehat r\leftarrow R\widehat r\)：

\[
y_\ell(R\widehat r)
=D(R)^{-\mathsf T}y_\ell(\widehat r)
=D(R)^*y_\ell(\widehat r).
\]

最后一步使用幺正性。

### 8.2 实点值

由 \(y_\ell=C_\ell r_\ell\) 与复相似变换，

\[
\begin{aligned}
C_\ell r_\ell(R\widehat r)
&=D_{\mathrm c}(R)^*C_\ell r_\ell(\widehat r)\\
&=C_\ell D_{\mathrm r}(R)r_\ell(\widehat r),
\end{aligned}
\]

故

\[
r_\ell(R\widehat r)
=D_{\mathrm r}(R)r_\ell(\widehat r).
\]

### 8.3 解析点值例

取

\[
\widehat r=(1,2,2)^{\mathsf T}/3,
\qquad
R=R_z(\pi/2),
\qquad
\kappa=\sqrt{\frac{3}{4\pi}}.
\]

直接代入 \(\ell=1\) 恒等式：

\[
y_1(\widehat r)
=\kappa
\begin{pmatrix}
(1-2i)/(3\sqrt2)\\
2/3\\
-(1+2i)/(3\sqrt2)
\end{pmatrix}.
\]

用 \(D^{(1)}(R)^*=\operatorname{diag}(-i,1,i)\) 作用，得到

\[
\kappa
\begin{pmatrix}
(-2-i)/(3\sqrt2)\\
2/3\\
(2-i)/(3\sqrt2)
\end{pmatrix},
\]

这与直接计算 \(y_1(R\widehat r)\) 一致。

## 9. 宇称、方向与零长度

\[
Y_{\ell m}(-\widehat r)
=(-1)^\ell Y_{\ell m}(\widehat r).
\]

因此球谐方向特征具有轨道型宇称 \((-1)^\ell\)。方向输入为有限位移 \(d\)、显式特征长度 \(s\) 和 dtype，其中 \(s\) 必须有限且严格为正。定义

\[
\zeta_d=\frac{\lVert d\rVert_2}{s}.
\]

float64/float32 分别使用

\[
\tau_{0,64}=10^{-12},
\qquad
\tau_{0,32}=10^{-5}.
\]

仅当

\[
\zeta_d>\tau_0
\]

时才接受；\(\zeta_d=\tau_0\) 必须拒绝。接受后定义

\[
\widehat d=d/\lVert d\rVert.
\]

冻结阈值夹具为

\[
d_\varepsilon=(\varepsilon s,0,0),
\qquad
\varepsilon\in\{0,\tfrac12\tau_0,\tau_0,2\tau_0\}.
\]

前三项拒绝，最后一项接受。\(d\) 与 \(s\) 同时按同一正尺度缩放时 \(\zeta_d\) 不变。非有限 \(d/s\)、\(s\le0\)、错误 rank/shape 必须先拒绝。这里是统一局部架合同的单向量零长度子规则，不引入第二向量或共线指标 \(\eta\)。任意后备轴会把未定义对象替换为依赖实验室坐标的对象，不能作为等变修复。

## 10. 定量失败例

### 10.1 未同步 \(m\) 逆序

令 \(J\) 反转 \(m=-1,0,1\) 的顺序，错误地只改系数接口：

\[
K_{\mathrm{wrong}}=JK_1.
\]

若仍使用规范顺序

\[
D^{(1)}=\operatorname{diag}(i,1,-i),
\]

则

\[
\begin{aligned}
D_{\mathrm{wrong}}
&=K_{\mathrm{wrong}}^\dagger
D^{(1)}K_{\mathrm{wrong}}\\
&=R_z(\pi/2)^{\mathsf T}.
\end{aligned}
\]

相对正确 \(R\) 的归一化 Frobenius 残差为

\[
\rho(R,R^{\mathsf T})
=\frac{2\sqrt2}{\sqrt3}
=2\sqrt{\frac23}
\approx1.632993162.
\]

### 10.2 漏复共轭

对第 8.3 节点值，错误关系 \(y(R\widehat r)=Dy(\widehat r)\) 与正确 \(D^*y\) 不同。该错误在纯实矩阵或 \(m=0\) 分量上可能偶然通过，因此夹具必须同时含非零 \(m=\pm1\) 复分量。

### 10.3 相位变化的正确分类

若以对角幺正矩阵 \(P_\ell\) 改变整个复基，

\[
\widetilde D=P_\ell^{-1}DP_\ell,
\qquad
\widetilde K=P_\ell^{-1}K,
\]

并同步变换点值、系数、CG 与元数据，则只是合法基变换。只翻某个函数定义而不更新这些对象，才是项目规范不一致或 intertwiner 错误。不得把所有相位自由一概判为数学错误。

## 11. D-E09 存储子预算

相同分量数下：

| dtype | 每个实元素 | 每个复元素 | 复/实裸值字节比 |
|---|---:|---:|---:|
| float64 / complex128 | 8 bytes | 16 bytes | 2 |
| float32 / complex64 | 4 bytes | 8 bytes | 2 |

单个 \(\ell=1\) 副本在 float64/complex128 中分别为 24/48 bytes；单个 \(\ell=2\) 副本为 40/80 bytes。若把配置 A 的 19 个实分量全部复化，单节点裸值从 152 增至 304 bytes；配置 B 从 128 增至 256 bytes。

这只是显式数组元素字节。共轭对称压缩、实视图、库临时量、球谐求值、CG contraction、图数组和 reference peak 未计入。M7-09 已按冻结实际数组在 [代码说明](../../05_code_exercises/stageE_synthetic_equivariance/README.md) 中重新报告；不能把本节乘 2 关系外推为完整运行内存或 FLOP 比。

## 12. Hamiltonian 基变换的块、mask、edge 与 provenance 契约

### 12.1 完整 shell 前提

对每个节点按冻结 shell/multiplicity 顺序构造

\[
K_i=\bigoplus_{\alpha\in\mathcal S_i^{\mathrm{active}}}
K_{\ell_\alpha}.
\]

一个 \(\ell\) shell 必须有完整 \(2\ell+1\) 个活动分量。令其 component mask 为 \(M_\alpha\)，则只允许

\[
M_\alpha=(1,\ldots,1)
\quad\text{或}\quad
M_\alpha=(0,\ldots,0).
\]

全假 shell 是 padding，在稠密矩阵作用前切除；部分真、部分假的 shell 必须拒绝。对 shell-pair Hamiltonian 子块，只有行 shell 与列 shell 的完整笛卡尔积都有效时才执行

\[
H_{\alpha\beta,\mathrm c}
=K_{\ell_\alpha}
H_{\alpha\beta,\mathrm r}
K_{\ell_\beta}^\dagger.
\]

禁止先把缺失或 padding 分量填零，再让稠密 \(K_\ell\) 混合有效与无效槽位。

### 12.2 离散 edge 不变量

纯轨道基变换不作用于结构几何或离散边。每行完整键

\[
(\text{stageD-edge-v1},\text{structure ID},
\text{receiver},\text{sender},n_x,n_y,n_z)
\]

和 edge 行序必须逐项不变。Hamiltonian、行/列表示矩阵、component mask 与 provenance 使用同一个 edge-row 和 shell-pair 轴映射；任何单独排序都必须带可逆映射并同步全部对象。

### 12.3 provenance 最小字段

每个变换后复分量至少记录：

| 字段 | 合同 |
|---|---|
| structure/atom/edge identity | 保留结构 ID、两端原子 ID 和完整 edge key |
| shell identity | shell ID、multiplicity ID、\(\ell\)、宇称 |
| source basis | real-spd-v1 与冻结实分量顺序 |
| target basis | complex-dlmf-cs-v1 与递增 \(m\) |
| component identity | 目标 \(m\)，不得沿用单个实 orbital component ID |
| transform identity | stageE-K-coeff-v1、\(\ell\)、规范载荷 SHA-256 |
| source span | 该复分量所线性组合的完整实 component ID 集合 |

### 12.4 规范载荷与哈希

载荷采用 UTF-8 ASCII JSON、数组顺序固定、separators 为逗号与冒号且不含空格。\(K_1\) 的规范载荷为

~~~json
["stageE-K-coeff-v1",1,["px","py","pz"],[-1,0,1],[["1/sqrt2","i/sqrt2","0"],["0","0","1"],["-1/sqrt2","i/sqrt2","0"]]]
~~~

其 SHA-256 为

\[
\text{347E352605A3F4F3CCB078B6CEDF5C755FDC6AA3527EA41A8EA3E93D076972A2}.
\]

\(K_2\) 的规范载荷为

~~~json
["stageE-K-coeff-v1",2,["dxy","dyz","dzx","dx2-y2","d3z2-r2"],[-2,-1,0,1,2],[["i/sqrt2","0","0","1/sqrt2","0"],["0","i/sqrt2","1/sqrt2","0","0"],["0","0","0","0","1"],["0","i/sqrt2","-1/sqrt2","0","0"],["-i/sqrt2","0","0","1/sqrt2","0"]]]
~~~

其 SHA-256 为

\[
\text{5E783D9CDFE025238977F9E92D64D8B46E9A0E79EB8C9DEBA1AF116AAAFC7B82}.
\]

哈希标识符追踪的是符号系数、两侧顺序与版本，不依赖某次浮点序列化。实现仍须把符号矩阵转换为声明 dtype，并执行幺正性和数值哈希之外的语义检查。

## 13. D-E03/D-E09 到 T-E 的显式映射

| 推导对象 | 完成位置 | 自动门控 | 正向检查 | 强制失败 | 当前证据状态 |
|---|---|---|---|---|---|
| DLMF 相位、\(m\) 顺序与 \(C_1,C_2\) | 第 3、6、7 节 | T-E04 | 低阶函数恒等式、幺正、往返 | 漏 Condon--Shortley、逆序、错实轨道顺序 | 解析矩阵已完成；A/B 执行见 M7-09 代码说明与定点复核 |
| Wigner \(D\) 与群律 | 第 4—5 节 | T-E04 | 幺正、逆、非交换复合、\(z\) 轴锚点 | 主动/被动、Euler 轴序、共轭方向 | 操作性定义与解析锚点完成；一般旋转代码见 M7-09 代码说明与定点复核 |
| 复—实相似变换 | 第 6—7 节 | T-E03、T-E04 | \(KDK^\dagger\)、实 \(p,d\) 双路线、\(R_z/R_x\) 锚点一致 | 函数 \(C\) 与系数 \(K\) 混用 | 两轴解析变换完成；随机矩阵测试见 M7-09 代码说明与定点复核 |
| 点值、方向 validator 与宇称 | 第 8—9 节 | T-E04、T-E07、T-E12 | \(y(Rr)=D^*y(r)\)、\(\zeta_d=\lVert d\rVert/s\)、\((-1)^\ell\) | 漏共轭、阈值等号、非法 \(s\)、零长度、错宇称 | 固定点与阈值两侧合同完成；失败矩阵见 M7-09 代码说明与定点复核 |
| schema 与定向失败 | 第 2、10 节 | T-E12 | dtype/rank/shape/顺序/finite/provenance | 静默广播、未同步重排或相位 | 契约完成；故障注入见 M7-09 代码说明与定点复核 |
| Hamiltonian 基变换接口 | 第 12 节 | T-E06、T-E12 | 完整 shell 块、全真/全假 mask、edge key/row 不变、K 版本/hash 与复 component provenance | 部分 mask、穿透 padding、改 edge key、伪装实 component ID | 块与身份合同完成；代码故障注入见 M7-09 代码说明与定点复核 |
| D-E09 实/复局部字节 | 第 11 节 | T-E10 | 元素 nbytes 与局部数组 | 局部乘 2 冒充端到端 total/peak | 子预算完成；144 点完整成本见 M7-09 代码说明与定点复核 |

## 14. 可独立复算的最终不变量

- \(D^{(\ell)}(R_z(\alpha))=\operatorname{diag}_{m=-\ell}^{\ell}(e^{-im\alpha})\)；
- \(C_1,C_2,K_1,K_2\) 均幺正，且 \(K_\ell=C_\ell^*\)；
- \(D_{\mathrm c}=K_\ell D_{\mathrm r}K_\ell^\dagger\)；
- 复点值按 \(y(R\widehat r)=D(R)^*y(\widehat r)\)，系数按 \(c'=D(R)c\)；
- \(R_z(\pi/2)\) 通过相似变换恢复第 16 章冻结 \(D^p,D^d\)；
- \(R_x(\pi/2)\) 的复 \(D^{(1)},D^{(2)}\) 为第 7.3 节矩阵，四次幂分别为单位矩阵；
- 未同步 \(m\) 逆序的实矩阵残差为 \(2\sqrt{2/3}\)；
- \(Y_{\ell m}(-\widehat r)=(-1)^\ell Y_{\ell m}(\widehat r)\)；
- 基变换只在完整活动 shell-pair 内执行，padding 在作用前切除，完整 edge key 与 edge 行序不变；
- stageE-K-coeff-v1 的 \(\ell=1,2\) 规范载荷哈希分别为 347E3526...6972A2 与 5E783D9C...FC7B82；
- 相同分量数的显式 complex128/64 数组裸值字节是 float64/32 的两倍；
- 本文件没有执行 A/B、144 点或任何正式软件/数据验证。
