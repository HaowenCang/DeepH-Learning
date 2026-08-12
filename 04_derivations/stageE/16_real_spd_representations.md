# D-E02 与 D-E09：实 \(s,p,d\) 表、不可约分解与维度预算

## 1. 推导目标与完成边界

本文件完成 D-E02，并给出第 16 章所需的 D-E09 子部分：

- 从群同态、不变子空间和直和定义表示与可约性；
- 说明整数 \(\ell\) 空间的维数 \(2\ell+1\) 与不可约性边界；
- 从笛卡尔向量和对称无迹张量构造实 \(s,p,d\) 表；
- 证明 \(D^d\) 的正交性、群律和冻结 \(R_z(\pi/2)\) 锚点；
- 区分一般 \(O(3)\) 标签 \((\ell,p)\) 与轨道宇称 \((-1)^\ell\)；
- 推导多壳层维数、同型线性参数量和局部激活字节；
- 建立 D-E02/D-E09 到 T-E03/T-E07/T-E10/T-E12 的显式映射。

本文件不构造复球谐相似变换、CG 张量积、Hamiltonian 消息层或正式 DeepH 对象；这些分别属于第 17—19 章和 M8 以后授权范围。统一约定见 [阶段 E 表示约定](../../03_textbook/stageE_representation_conventions.md)。

## 2. 符号、维度与成立条件

| 符号 | 类型或维度 | 含义 |
|---|---|---|
| \(G\) | 群 | 本章具体取 \(SO(3)\) 或 \(O(3)\) |
| \(R\) | \(\mathbb R^{3\times3}\) | 主动正旋转，\(R^{\mathsf T}R=I,\det R=1\) |
| \(Q\) | \(\mathbb R^{3\times3}\) | 正交变换，\(\det Q=\pm1\) |
| \(V_\ell\) | \(\mathbb R^{2\ell+1}\) 或其复化 | 整数角动量 \(\ell\) 的不可约空间 |
| \(D^{(\ell)}(R)\) | \((2\ell+1)\times(2\ell+1)\) | 表示矩阵 |
| \(B_a\) | \(\mathbb R^{3\times3}\)，\(a=1,\ldots,5\) | 冻结实 \(d\) 基矩阵 |
| \(c\) | \(\mathbb R^5\) | 对称无迹张量的 \(B_a\) 展开系数 |
| \(m_\ell\) | 非负整数 | \(\ell\) 型不可约表示的 multiplicity |
| \(p\) | \(+1\) 或 \(-1\) | 反演宇称 |
| \(W_\ell\) | \(\mathbb R^{m_\ell^{\mathrm{out}}\times m_\ell^{\mathrm{in}}}\) | 同型副本之间的线性混合 |

所有表示矩阵比较要求相同 dtype、shape、基顺序和主动作用方向。实 \(d\) 构造依赖 \(B_a\) 的 Frobenius 正交归一；若改用其他基，必须显式引入基变换或对偶基。不可约性结论针对完整连续群 \(SO(3)\)，不能由少数采样旋转直接证明。

## 3. 群表示、直和与不可约性

### 3.1 表示同态

线性表示满足

\[
D(e)=I,
\qquad
D(g^{-1})=D(g)^{-1},
\qquad
D(g_2g_1)=D(g_2)D(g_1).
\]

最后一式确保特征空间中的矩阵复合与物理操作顺序一致。正交性或幺正性是保持内积的附加性质，不能替代同态条件。

### 3.2 不变子空间与直和

若 \(W\subseteq V\) 满足 \(D(g)W\subseteq W\)，则 \(W\) 是不变子空间。若存在非平凡真不变子空间，表示可约。对

\[
V=V_1\oplus V_2,
\]

有

\[
D(g)=D_1(g)\oplus D_2(g).
\]

相同 \(V_\ell\) 出现 \(m_\ell\) 次时可写为

\[
\mathbb R^{m_\ell}\otimes V_\ell,
\qquad
D_\ell^{(m_\ell)}(R)
=I_{m_\ell}\otimes D^{(\ell)}(R).
\]

### 3.3 整数角动量空间

复球面调和函数 \(Y_{\ell m}\) 的索引为

\[
m=-\ell,\ldots,\ell,
\]

故维数为 \(2\ell+1\)。固定 \(\ell\) 的空间在旋转下闭合。其不可约性可由角动量生成元说明：若非零复不变子空间包含某个 \(m\) 分量，升降算符 \(L_\pm\) 在不越界时连接相邻 \(m\)，从而生成同一 \(\ell\) 的整条 \(m\) 链；因此不存在非平凡真不变子空间。实 \(s,p,d\) 空间是 \(\ell=0,1,2\) 的实型基。

该论证依赖完整李代数作用和固定 \(\ell\) 空间。一个有限旋转子集可能具有额外不变子空间，不能用有限采样上的经验闭合替代连续群不可约性。

## 4. \(s\) 与 \(p\) 表

### 4.1 \(s\) 表

一维常数函数在旋转下不变，因此

\[
D^s(R)=1.
\]

群律和正交性显然成立。该表示不忠实，但仍是合法不可约表示。

### 4.2 \(p\) 表

令

\[
p(\widehat r)
=\sqrt{\frac{3}{4\pi}}
\begin{pmatrix}
\widehat r_x\\
\widehat r_y\\
\widehat r_z
\end{pmatrix}.
\]

在主动系数约定下，实 \(p\) 系数按

\[
c'=Rc
\]

变换，故

\[
D^p(R)=R.
\]

立即得到

\[
D^p(R)^{\mathsf T}D^p(R)=I_3,
\qquad
D^p(R_2R_1)=D^p(R_2)D^p(R_1).
\]

## 5. 五维对称无迹空间

### 5.1 维数与闭合

实对称 \(3\times3\) 矩阵空间维数为

\[
\frac{3(3+1)}2=6.
\]

迹映射是到 \(\mathbb R\) 的非零线性泛函，其核维数为 5：

\[
\operatorname{Sym}_0(3)
=\{T:T^{\mathsf T}=T,\operatorname{tr}T=0\}.
\]

对 \(T\in\operatorname{Sym}_0(3)\) 和 \(R\in SO(3)\)，

\[
(RTR^{\mathsf T})^{\mathsf T}
=RTR^{\mathsf T},
\]

\[
\operatorname{tr}(RTR^{\mathsf T})
=\operatorname{tr}(R^{\mathsf T}RT)
=\operatorname{tr}T=0.
\]

因此该空间在旋转下闭合。

### 5.2 冻结基与 Gram 矩阵

按顺序

\[
(xy,yz,zx,x^2-y^2,3z^2-r^2)
\]

定义

\[
\begin{aligned}
B_1&=\frac1{\sqrt2}
\begin{pmatrix}0&1&0\\1&0&0\\0&0&0\end{pmatrix},&
B_2&=\frac1{\sqrt2}
\begin{pmatrix}0&0&0\\0&0&1\\0&1&0\end{pmatrix},\\
B_3&=\frac1{\sqrt2}
\begin{pmatrix}0&0&1\\0&0&0\\1&0&0\end{pmatrix},&
B_4&=\frac1{\sqrt2}
\begin{pmatrix}1&0&0\\0&-1&0\\0&0&0\end{pmatrix},\\
B_5&=\frac1{\sqrt6}
\begin{pmatrix}-1&0&0\\0&-1&0\\0&0&2\end{pmatrix}.
\end{aligned}
\]

每个矩阵均对称无迹。对角基与非对角基的 Frobenius 内积为零，不同非对角基的非零位置不重叠，且

\[
\lVert B_1\rVert_F^2
=\frac12+\frac12=1,
\]

\[
\lVert B_4\rVert_F^2
=\frac12+\frac12=1,
\qquad
\lVert B_5\rVert_F^2
=\frac16+\frac16+\frac46=1.
\]

直接计算 \(B_4\) 与 \(B_5\) 的内积为

\[
\frac{-1+1}{\sqrt{12}}=0.
\]

故 Gram 矩阵

\[
G_{ab}=\operatorname{tr}(B_a^{\mathsf T}B_b)
\]

严格等于 \(I_5\)。

## 6. \(d\) 表的构造与证明

### 6.1 系数提取

对

\[
T=\sum_b c_bB_b,
\]

正交归一性给出

\[
c_a=\operatorname{tr}(B_a^{\mathsf T}T).
\]

旋转后

\[
T'=RTR^{\mathsf T}
=\sum_b c_b RB_bR^{\mathsf T}.
\]

因此

\[
\begin{aligned}
c'_a
&=\operatorname{tr}(B_a^{\mathsf T}T')\\
&=\sum_b
\operatorname{tr}(B_a^{\mathsf T}RB_bR^{\mathsf T})c_b.
\end{aligned}
\]

定义

\[
D^d_{ab}(R)
=\operatorname{tr}(B_a^{\mathsf T}RB_bR^{\mathsf T}),
\]

便有 \(c'=D^d(R)c\)。

### 6.2 正交性

共轭映射

\[
\mathcal C_R(T)=RTR^{\mathsf T}
\]

保持 Frobenius 内积：

\[
\begin{aligned}
\langle\mathcal C_R(S),\mathcal C_R(T)\rangle_F
&=\operatorname{tr}\!\left[
(RSR^{\mathsf T})^{\mathsf T}(RTR^{\mathsf T})
\right]\\
&=\operatorname{tr}(RS^{\mathsf T}TR^{\mathsf T})\\
&=\operatorname{tr}(S^{\mathsf T}T).
\end{aligned}
\]

由于 \(B_a\) 是正交归一基，该等距线性算子在此基中的矩阵满足

\[
D^d(R)^{\mathsf T}D^d(R)=I_5.
\]

### 6.3 群律

\[
\begin{aligned}
\mathcal C_{R_2}(\mathcal C_{R_1}(T))
&=R_2(R_1TR_1^{\mathsf T})R_2^{\mathsf T}\\
&=(R_2R_1)T(R_2R_1)^{\mathsf T}\\
&=\mathcal C_{R_2R_1}(T).
\end{aligned}
\]

在同一冻结基中取矩阵，得到

\[
D^d(R_2R_1)=D^d(R_2)D^d(R_1).
\]

这也说明若实现使用 \(R^{\mathsf T}BR\)，它计算的是 \(D^d(R^{-1})\)，在一般非对称复合测试中与目标不同。

## 7. 完整解析例与定量失败例

### 7.1 \(R_z(\pi/2)\) 锚点

取

\[
R=
\begin{pmatrix}
0&-1&0\\
1&0&0\\
0&0&1
\end{pmatrix}.
\]

由 \(Re_x=e_y\)、\(Re_y=-e_x\)、\(Re_z=e_z\)，逐项得到

\[
\begin{aligned}
RB_1R^{\mathsf T}&=-B_1,&
RB_2R^{\mathsf T}&=-B_3,\\
RB_3R^{\mathsf T}&= B_2,&
RB_4R^{\mathsf T}&=-B_4,\\
RB_5R^{\mathsf T}&= B_5.
\end{aligned}
\]

按“列为输入基、行为输出基”组装：

\[
D^d(R)=
\begin{pmatrix}
-1&0&0&0&0\\
0&0&1&0&0\\
0&-1&0&0&0\\
0&0&0&-1&0\\
0&0&0&0&1
\end{pmatrix}.
\]

直接乘法给出

\[
D^{d\mathsf T}D^d=I_5,
\qquad
\det D^d=1,
\qquad
\operatorname{tr}D^d=-1.
\]

### 7.2 系数追踪

取

\[
c=(1,2,-1,1/2,-1/4)^{\mathsf T}.
\]

矩阵乘法给出

\[
D^d(R)c
=(-1,-1,-2,-1/2,-1/4)^{\mathsf T}.
\]

直接构造 \(T=\sum_a c_aB_a\)、计算 \(RTR^{\mathsf T}\) 并用 Frobenius 投影恢复系数，得到同一结果。因此正向表示残差为 0。

### 7.3 漏归一化的定量失败

令

\[
C_1=2B_1,\qquad C_a=B_a\ (a>1).
\]

若仍错误使用正交归一投影公式

\[
\widetilde D_{ab}(R)
=\operatorname{tr}(C_a^{\mathsf T}RC_bR^{\mathsf T}),
\]

则

\[
\widetilde D(I)=
\operatorname{diag}(4,1,1,1,1).
\]

与单位矩阵的归一化 Frobenius 残差为

\[
\rho(\widetilde D(I),I)
=\frac{3}{\sqrt{20}}
\approx0.6708203932.
\]

它远大于 \(10^{-4}\)，并在单位元公理上直接失败。正确的非正交基表示需要 \(G^{-1}\) 或对偶基；失败对象是错误投影公式，而不是非正交基本身。

## 8. \(O(3)\) 宇称

### 8.1 一般标签

对 \(O(3)\)，固定 \(\ell\) 仍不足以区分反演。记不可约类型为

\[
(\ell,p),\qquad p\in\{+1,-1\}.
\]

对 \(Q\in O(3)\)，可写 \(Q=\eta R\)，其中 \(R\in SO(3)\)、\(\eta=\det Q\in\{\pm1\}\)。一种固定宇称 \(p\) 的扩张可按反演作用 \(pI\) 定义；具体数组公式必须与项目元数据一致。

### 8.2 轨道宇称与向量类型

球谐轨道满足

\[
p_{\mathrm{orbital}}=(-1)^\ell,
\]

故 \(s,p,d\) 分别是 \((0,+)\)、\((1,-)\)、\((2,+)\)。极向量为 \((1,-)\)，轴向量为 \((1,+)\)。对 \(Q=-I\)，

\[
D_{\mathrm{polar}}(Q)=-I_3,
\qquad
D_{\mathrm{axial}}(Q)=+I_3.
\]

两者在所有 \(SO(3)\) 测试上相同，因此 T-E07 必须包含行列式为 \(-1\) 的夹具。

## 9. 多壳层与同型线性映射

### 9.1 总维数

表示

\[
V=\bigoplus_{\ell=0}^{2}
\mathbb R^{m_\ell}\otimes V_\ell
\]

的总分量数为

\[
n=m_0+3m_1+5m_2.
\]

阶段 E 配置 A、B 分别给出

\[
n_A=3+3\cdot2+5\cdot2=19,
\]

\[
n_B=5+3\cdot4+5\cdot3=32.
\]

### 9.2 同型线性参数

不引入额外几何张量时，保持表示类型的线性映射为

\[
L=\bigoplus_\ell
(W_\ell\otimes I_{2\ell+1}).
\]

参数数为

\[
N_{\mathrm{param}}
=\sum_\ell
m_\ell^{\mathrm{out}}m_\ell^{\mathrm{in}}.
\]

自映射配置 A、B 分别是

\[
N_{\mathrm{param},A}=3^2+2^2+2^2=17,
\]

\[
N_{\mathrm{param},B}=5^2+4^2+3^2=50.
\]

这些是同型线性混合参数，不包括 bias、径向网络、球谐、CG 或图聚合。

### 9.3 局部字节预算

单节点连续分量数组只按裸值计算：

\[
\mathrm{bytes}_{A,\mathrm{node}}
=19\times8=152
\]

对应 float64；

\[
\mathrm{bytes}_{B,\mathrm{node}}
=32\times4=128
\]

对应 float32。固定图节点数组分别为

\[
4\times152=608\ \mathrm{bytes},
\qquad
7\times128=896\ \mathrm{bytes}.
\]

这些数字不含 edge、输出、中间 contraction、mask、身份字符串或运行时开销。完整 T-E10 的逐数组、total 和 reference peak 已由 M7-09 按冻结 kernel 重新核算，见 [代码说明](../../05_code_exercises/stageE_synthetic_equivariance/README.md)。

## 10. 失败边界

- 交换 \(d_{yz}\) 与 \(d_{zx}\) 而不同时变换表示矩阵、特征和元数据，会造成基顺序错位；
- 只比较 \(D^{\mathsf T}D=I\) 不能发现 \(D(R_2R_1)\) 的顺序错误；
- 非正交基若使用对偶基仍可构成正确表示，故“非正交必错”是错误结论；
- \(\ell\) 相同但宇称不同的通道不能无条件线性混合；
- multiplicity 相同或总维数相同不能替代 shell ID、component index 与 orbital ID；
- 复球谐相位、CG 通道和自旋双值表示尚未由本文件建立。

## 11. D-E02/D-E09 到 T-E 的显式映射

| 推导对象 | 完成位置 | 自动门控 | 正向检查 | 强制失败 | 当前证据状态 |
|---|---|---|---|---|---|
| \(D^p,D^d\) 构造、正交性与群律 | 第 4—7 节 | T-E03 | \(B_a\) Gram、shape、正交、群律、\(R_z(\pi/2)\) 锚点 | 错序、漏归一化、\(R^{\mathsf T}BR\)、行列颠倒 | 解析与定量夹具已完成；A/B 执行见 M7-09 代码说明与定点复核 |
| \(O(3)\) 宇称 | 第 8 节 | T-E07 | \(s,p,d\) 轨道宇称与极/轴向量反演 | 用正旋转结果替代反演、极/轴混淆 | 解析夹具已完成；自动矩阵见 M7-09 代码说明与定点复核 |
| multiplicity、shape 与身份 | 第 3、9 节 | T-E12 | 维数、块结构、shell/component/orbital provenance | 广播、错序、重复/缺失块、身份错位 | schema 条件已完成；故障注入见 M7-09 代码说明与定点复核 |
| D-E09 维度、参数和局部字节 | 第 9 节 | T-E10 | A/B 维数 19/32、参数 17/50、节点值字节 | 稠密参数冒充同型参数、局部字节冒充端到端 peak | 解析子预算已完成；144 点完整成本执行见 M7-09 代码说明与定点复核 |

## 12. 可独立复算的最终不变量

- \(\dim V_\ell=2\ell+1\)，故 \(s,p,d\) 维数为 1、3、5；
- 冻结 \(B_a\) 的 Gram 矩阵严格为 \(I_5\)；
- \(D^p(R)=R\)；
- \(D^d_{ab}(R)=\operatorname{tr}(B_a^{\mathsf T}RB_bR^{\mathsf T})\)；
- \(D^d(R)^{\mathsf T}D^d(R)=I_5\) 且 \(D^d(R_2R_1)=D^d(R_2)D^d(R_1)\)；
- \(R_z(\pi/2)\) 的冻结 \(D^d\) 为第 7.1 节矩阵，迹为 \(-1\)；
- 错误非正交投影在单位元处残差为 \(3/\sqrt{20}\)；
- 轨道宇称为 \(s:+\)、\(p:-\)、\(d:+\)，但一般 \(\ell=1\) 还可具有轴向 \(+\) 宇称；
- 配置 A/B 的表示维数为 19/32，同型自映射参数为 17/50；
- 本文件自身不执行 A/B 或 144 点代码扫描；完整执行证据由 [M7-09 代码说明](../../05_code_exercises/stageE_synthetic_equivariance/README.md) 和 [独立定点复核](../../08_audits/M7_stageE_code_blocking_reaudit.md) 提供。
