# 第 16 章 群、表示、不可约表示与 \(s,p,d\) 轨道

## 16.1 群与表示的最小语言

### 16.1.1 本章对象与先修接口

第 15 章已经固定主动旋转、复合顺序和几何对象的变换。本章回答后续等变模型必须先回答的数组问题：一个旋转 \(R\) 在标量、向量、五维 \(d\) 轨道、多壳层节点特征和 Hamiltonian 两端轨道空间上分别由什么矩阵表示。

阶段 E 统一使用列向量和主动旋转，

\[
r'=Rr,
\qquad
D(R_2R_1)=D(R_2)D(R_1).
\]

本章的主对象及维度为

| 对象 | 空间 | 冻结顺序 |
|---|---|---|
| \(s\) 轨道 | \(\mathbb R^1\) | \((s)\) |
| \(p\) 轨道 | \(\mathbb R^3\) | \((p_x,p_y,p_z)\) |
| \(d\) 轨道 | \(\mathbb R^5\) | \((d_{xy},d_{yz},d_{zx},d_{x^2-y^2},d_{3z^2-r^2})\) |
| 多壳层节点 | \(\bigoplus_\ell \mathbb R^{m_\ell}\otimes\mathbb R^{2\ell+1}\) | 壳层表与每壳层内部顺序共同冻结 |

完整推导见 [D-E02/D-E09 子推导](../../../04_derivations/stageE/16_real_spd_representations.md)，例题见 [examples.md](examples.md)，练习和参考解答分别见[问题](../../../06_exercises/05-stageE/16_groups_representations/problem/readme.md)与[解答](../../../06_exercises/05-stageE/16_groups_representations/solution/readme.md)。

### 16.1.2 群、群作用与线性表示

群 \(G\) 具有单位元 \(e\)、逆元和结合的乘法。群作用 \(\alpha:G\times X\to X\) 满足

\[
\alpha(e,x)=x,
\qquad
\alpha(g_2,\alpha(g_1,x))
=\alpha(g_2g_1,x).
\]

当 \(X=V\) 是向量空间，且每个作用均为可逆线性映射时，得到表示

\[
D:G\to GL(V),
\qquad
D(e)=I,
\qquad
D(g_2g_1)=D(g_2)D(g_1).
\]

表示是群到矩阵群的同态。群元素、几何旋转矩阵和特征空间中的表示矩阵是三个不同层级；只有在标准三维极向量表示中才有 \(D(R)=R\)。

### 16.1.3 忠实性不是等变性的必要条件

表示的核为

\[
\ker D=\{g\in G:D(g)=I\}.
\]

若核只含单位元，则表示忠实。标量表示 \(D^{(0)}(R)=1\) 把所有旋转都映到 1，显然不忠实，但标量不变映射仍可严格等变。等变性要求输入、输出表示和映射之间满足 intertwiner 关系，不要求每个表示单独区分所有群元素。

## 16.2 子空间、直和与不可约性

### 16.2.1 不变子空间与可约表示

子空间 \(W\subseteq V\) 对表示 \(D\) 不变，当

\[
D(g)W\subseteq W
\quad\text{对所有 }g\in G.
\]

若 \(V\) 除 \(\{0\}\) 和自身外没有不变子空间，则该表示不可约；否则可约。例如标量与向量的直和

\[
D(R)=
\begin{pmatrix}
1&0\\
0&R
\end{pmatrix}
\]

是四维可约表示，因为一维标量子空间和三维向量子空间分别闭合。

### 16.2.2 直和、块对角矩阵与 multiplicity

若 \(V=V_1\oplus V_2\)，则

\[
D_{V_1\oplus V_2}(g)
=D_1(g)\oplus D_2(g).
\]

同一不可约表示出现 \(m_\ell\) 次时，

\[
V_\ell^{(m_\ell)}
\cong \mathbb R^{m_\ell}\otimes V_\ell,
\qquad
D_\ell^{(m_\ell)}(R)
=I_{m_\ell}\otimes D^{(\ell)}(R).
\]

这里 multiplicity 轴标识同型通道，表示轴标识 \(2\ell+1\) 个分量。两轴不能在没有元数据变换的情况下静默交换。

### 16.2.3 Schur 引理的使用边界

在有限维复不可约表示上，若线性映射 \(L\) 与所有 \(D(g)\) 交换，则 \(L\) 是标量倍数的单位矩阵。对本章的实 \(SO(3)\) 整数角动量表示，\(\ell=0,1,2\) 也具有相应的实型结论；但有 multiplicity 时，同型副本之间允许任意线性混合：

\[
L_\ell=W_\ell\otimes I_{2\ell+1}.
\]

因此，“高阶通道只能乘一个标量”只对单副本成立。不同 \(\ell\) 或不同宇称的通道不能由不含额外几何对象的同型线性层直接混合。

## 16.3 \(SO(3)\) 的整数角动量表示

### 16.3.1 \(\ell\)、\(m\) 与维数

对整数角动量，

\[
\ell=0,1,2,\ldots,
\qquad
m=-\ell,-\ell+1,\ldots,\ell,
\]

故不可约空间维数为

\[
\dim V_\ell=2\ell+1.
\]

\(\ell=0,1,2\) 分别对应 1、3、5 维。复球谐基中的 \(m\) 顺序固定为递增顺序；实 \(s,p,d\) 基则使用本章明确给出的笛卡尔顺序。

### 16.3.2 幺正性、正交性与群律

复球谐基中的 \(D^{(\ell)}(R)\) 为幺正矩阵，

\[
D^{(\ell)}(R)^\dagger D^{(\ell)}(R)=I.
\]

本章的实 \(s,p,d\) 基通过幺正基变换获得，因此表示矩阵为实正交矩阵，

\[
D^{(\ell)}(R)^{\mathsf T}D^{(\ell)}(R)=I.
\]

正交性只说明单个矩阵保持内积；群律还要求不同旋转的复合顺序正确。两者必须分别验证。

### 16.3.3 \(SO(3)\) 与 \(SU(2)\) 的边界

整数 \(\ell\) 表示是 \(SO(3)\) 的单值表示。半整数自旋是 \(SU(2)\) 的表示，并在 \(2\pi\) 旋转下出现符号；该对象留到第 20 章。本章不得把三维 \(p\) 轨道表示与二维自旋 \(1/2\) 表示混为一谈。

## 16.4 实 \(s,p,d\) 表

### 16.4.1 \(s\) 标量

\(s\) 轨道张成一维平凡表示：

\[
D^s(R)=D^{(0)}(R)=(1).
\]

它在所有正旋转下不变。这里的不变指表示分量不变，不代表包含该轨道的任意 Hamiltonian 子块逐元素不变。

### 16.4.2 \(p\) 轨道

按单位球面归一化函数

\[
p_a(\widehat r)
=\sqrt{\frac{3}{4\pi}}\,\widehat r_a
\]

和顺序 \((p_x,p_y,p_z)\)，系数向量按标准极向量表示变换：

\[
D^p(R)=R.
\]

例如

\[
R_z(\pi/2)=
\begin{pmatrix}
0&-1&0\\
1&0&0\\
0&0&1
\end{pmatrix}
\]

把 \(p_x\) 系数列变为 \(p_y\)，把 \(p_y\) 系数列变为 \(-p_x\)。

### 16.4.3 对称无迹二阶张量的五维空间

实对称 \(3\times3\) 矩阵有 6 个独立分量，迹为零提供一个独立线性约束，故

\[
\dim\operatorname{Sym}_0(3)=6-1=5.
\]

若 \(T=T^{\mathsf T}\) 且 \(\operatorname{tr}T=0\)，则

\[
T'=RTR^{\mathsf T}
\]

仍对称且无迹。因此该五维空间在 \(SO(3)\) 下闭合，承载 \(\ell=2\) 表示。

### 16.4.4 正交归一 \(B_a\) 基

令 \(e_x,e_y,e_z\) 为标准基，按冻结顺序定义

\[
\begin{aligned}
B_{xy}&=(e_xe_y^{\mathsf T}+e_ye_x^{\mathsf T})/\sqrt2,\\
B_{yz}&=(e_ye_z^{\mathsf T}+e_ze_y^{\mathsf T})/\sqrt2,\\
B_{zx}&=(e_ze_x^{\mathsf T}+e_xe_z^{\mathsf T})/\sqrt2,\\
B_{x^2-y^2}&=(e_xe_x^{\mathsf T}-e_ye_y^{\mathsf T})/\sqrt2,\\
B_{3z^2-r^2}&=(-e_xe_x^{\mathsf T}-e_ye_y^{\mathsf T}+2e_ze_z^{\mathsf T})/\sqrt6.
\end{aligned}
\]

它们满足

\[
B_a^{\mathsf T}=B_a,
\qquad
\operatorname{tr}B_a=0,
\qquad
\operatorname{tr}(B_a^{\mathsf T}B_b)=\delta_{ab}.
\]

任意 \(T\in\operatorname{Sym}_0(3)\) 唯一写成

\[
T=\sum_{b=1}^{5}c_bB_b,
\qquad
c_b=\operatorname{tr}(B_b^{\mathsf T}T).
\]

### 16.4.5 \(d\) 表的构造

旋转后的基张量 \(RB_bR^{\mathsf T}\) 仍在五维空间中，其在 \(B_a\) 上的系数定义

\[
D^d_{ab}(R)
=\operatorname{tr}\!\left(
B_a^{\mathsf T}RB_bR^{\mathsf T}
\right).
\]

于是

\[
RB_bR^{\mathsf T}
=\sum_a B_aD^d_{ab}(R),
\qquad
c'=D^d(R)c.
\]

由于共轭作用保持 Frobenius 内积，\(D^d(R)\) 正交；由于

\[
R_2(R_1B_bR_1^{\mathsf T})R_2^{\mathsf T}
=(R_2R_1)B_b(R_2R_1)^{\mathsf T},
\]

它满足

\[
D^d(R_2R_1)=D^d(R_2)D^d(R_1).
\]

### 16.4.6 \(R_z(\pi/2)\) 的五维锚点

对冻结顺序，直接作用给出

\[
B_{xy}\mapsto-B_{xy},\quad
B_{yz}\mapsto-B_{zx},\quad
B_{zx}\mapsto B_{yz},
\]

\[
B_{x^2-y^2}\mapsto-B_{x^2-y^2},\quad
B_{3z^2-r^2}\mapsto B_{3z^2-r^2}.
\]

因此

\[
D^d(R_z(\pi/2))=
\begin{pmatrix}
-1&0&0&0&0\\
0&0&1&0&0\\
0&-1&0&0&0\\
0&0&0&-1&0\\
0&0&0&0&1
\end{pmatrix}.
\]

该矩阵的列对应输入基，行对应输出基。把行列含义颠倒会得到转置矩阵，并在非对称复合夹具中失败。

### 16.4.7 迹与字符

共轭作用保持每个张量的迹为零。表示矩阵的迹

\[
\chi^{(\ell)}(R)=\operatorname{tr}D^{(\ell)}(R)
\]

是字符，并在共轭旋转 \(SRS^{-1}\) 下不变。对转角为 \(\theta\) 的 \(SO(3)\) 旋转，

\[
\chi^{(\ell)}(\theta)
=\sum_{m=-\ell}^{\ell}e^{-im\theta}
=1+2\sum_{m=1}^{\ell}\cos(m\theta).
\]

因此

\[
\chi^{(1)}(\theta)=1+2\cos\theta,
\qquad
\chi^{(2)}(\theta)=1+2\cos\theta+2\cos2\theta.
\]

字符是有用的弱检查，但相同迹不能证明两个完整矩阵相同。

## 16.5 从 \(SO(3)\) 到 \(O(3)\)

### 16.5.1 一般 \((\ell,p)\) 标签与轨道宇称

\(O(3)\) 的表示除 \(\ell\) 外还需记录反演宇称 \(p=\pm1\)。一般特征可具有任意允许的 \((\ell,p)\) 标签；对由球谐轨道获得的主线 \(s,p,d\) 基，宇称专门为

\[
p_{\mathrm{orbital}}=(-1)^\ell.
\]

故

\[
s:(0,+1),\qquad
p:(1,-1),\qquad
d:(2,+1).
\]

不能把“所有 \(\ell=1\) 对象都具有奇宇称”当作一般结论。

### 16.5.2 极向量与轴向量

极向量的标签为 \((1,-1)\)，轴向量为 \((1,+1)\)。它们在 \(SO(3)\) 下都按 \(R\) 变换，但对空间反演 \(Q=-I\)：

\[
v_{\mathrm{polar}}'=-v_{\mathrm{polar}},
\qquad
a_{\mathrm{axial}}'=+a_{\mathrm{axial}}.
\]

因此，正旋转上的数值矩阵相同不能推出 \(O(3)\) 表示同型。

### 16.5.3 允许与禁止的同型混合

不含额外奇偶对象的 \(O(3)\)-等变线性层只可在线性同型通道之间混合，即 \(\ell\) 与 \(p\) 都相同。把 \((1,-1)\) 与 \((1,+1)\) 直接相加会在反演下产生不一致。若存在明确带宇称的几何张量积，输出宇称按输入宇称相乘，并由第 18 章的 CG 路径处理；这不同于无条件线性混合。

## 16.6 多壳层轨道表示

### 16.6.1 块对角节点表示

设节点有 \(m_0\) 个 \(s\) 壳、\(m_1\) 个 \(p\) 壳和 \(m_2\) 个 \(d\) 壳。总维数为

\[
n_{\mathrm{orb}}
=m_0+3m_1+5m_2.
\]

若序列化顺序按壳层表固定，则节点表示是相应块的直和：

\[
D_i(R)
=\bigoplus_{\alpha\in\text{shell table}_i}
D^{(\ell_\alpha)}(R).
\]

相同元素的两个不同径向 \(p\) 壳具有相同三维表示，但仍是不同 multiplicity 槽位；不能仅凭 \(\ell=1\) 合并身份。

### 16.6.2 轨道表、mask 与 provenance

每个有效分量至少需要

\[
(\text{structure ID},\text{atom ID},\text{shell ID},
\ell,p,\text{component index},\text{orbital ID}).
\]

表示矩阵、特征、预测、mask 和实际轨道身份必须共享同一行映射。padding 槽位不参与表示作用或损失；重排壳层时应显式使用置换矩阵并同步 provenance，而不是只重排数值数组。

### 16.6.3 维度、参数量与字节

同型线性层从 multiplicity \(m_\ell^{\mathrm{in}}\) 到 \(m_\ell^{\mathrm{out}}\) 的形式为

\[
W_\ell\otimes I_{2\ell+1},
\]

其自由参数数为

\[
\sum_\ell
m_\ell^{\mathrm{out}}m_\ell^{\mathrm{in}},
\]

而不是把完整分量空间当作稠密矩阵。阶段 E 配置 A 的 \((m_0,m_1,m_2)=(3,2,2)\) 给出维数 19；配置 B 的 \((5,4,3)\) 给出维数 32。自映射同型混合参数分别为

\[
3^2+2^2+2^2=17,
\qquad
5^2+4^2+3^2=50.
\]

每节点裸特征字节分别为 \(19\times8=152\) bytes 和 \(32\times4=128\) bytes。这里只核算表示布局；图消息、球谐、CG 中间量和完整 T-E10 total/peak 已由 M7-09 的冻结实现单独核算，见 [代码说明](../../../05_code_exercises/stageE_synthetic_equivariance/README.md)，不得将这些局部数字冒充端到端成本。

## 16.7 例题、失败样例与验证

### 16.7.1 例题入口

[examples.md](examples.md) 给出八个完整对象：

1. 平凡表示不忠实但可用于不变输出；
2. 标量与向量直和；
3. \(p\) 表的 \(R_z(\pi/2)\)；
4. \(d\) 表的 \(R_z(\pi/2)\)；
5. 对称无迹张量的系数追踪；
6. 多壳层维数与块对角表示；
7. 极向量、轴向量与轨道宇称；
8. 非正交基上错误使用 Frobenius 投影的失败。

### 16.7.2 数值门控

至少检查：

- 每个 \(B_a\) 的对称、无迹和两两 Frobenius 正交归一；
- \(D^p,D^d\) 的 dtype、shape、有限性、正交性与群律；
- \(R_z(\pi/2)\) 的冻结五维锚点；
- \(O(3)\) 反演下的宇称；
- 壳层表、multiplicity、mask 和 orbital provenance；
- float64/float32 归一化残差阈值；
- 错序、漏归一化、错误 \(R^{\mathsf T}BR\)、错误宇称和静默广播的失败样例。

### 16.7.3 常见失败

把 \(d\) 名称顺序相同误当作函数相位相同，会造成合法矩阵之间出现隐含置换或符号。用非正交基时仍以 \(\operatorname{tr}(B_a^{\mathsf T}T)\) 直接当作展开系数，会在单位旋转下就得到 \(D(I)\ne I\)。只验证单个矩阵正交不能发现复合顺序错误；只验证 \(SO(3)\) 不能发现宇称错误；只比较总维数不能发现壳层身份错位。

### 16.7.4 推导、练习与测试映射

D-E02 与本章 D-E09 子对象位于 [解析推导](../../../04_derivations/stageE/16_real_spd_representations.md)。Q16-01—Q16-10 与 A16-01—A16-10 覆盖群语言、不可约性、\(p/d\) 构造、宇称、多壳层和数值审计。T-E03 负责 \(p/d\) 正交性与群律，T-E07 负责宇称，T-E12 负责 schema 与失败矩阵；实际 A/B 代码证据见 [Stage E 代码说明](../../../05_code_exercises/stageE_synthetic_equivariance/README.md) 与 [M7-09 定点复核](../../../08_audits/M7_stageE_code_blocking_reaudit.md)。

## 16.8 与后续章节的接口

### 16.8.1 复球谐与 Wigner \(D\)

本章以笛卡尔张量直接构造实 \(p,d\) 表。第 17 章将从 DLMF 复球谐与 Wigner \(D\) 出发，构造复—实幺正变换并证明两条路线得到相似的表示矩阵。

### 16.8.2 CG 耦合

直和只并列表示，不能生成不同 \(\ell\) 的耦合。第 18 章将通过 Clebsch--Gordan intertwiner 分解张量积，并区分合法整通道相位自由与局部系数错误。

### 16.8.3 Hamiltonian 轨道块

第 19 章使用本章冻结的多壳层块对角表示验证

\[
H_{ij}(RX)
=D_i(R)H_{ij}(X)D_j(R)^\dagger.
\]

实基中 \(\dagger\) 为转置；转到复基后必须保留共轭。两端维数、轨道顺序和 provenance 由本章接口提供。

### 16.8.4 章节门控与授权边界

本章完成必须同时满足：

- 群作用、表示、不可约性、直和和 multiplicity 的定义及边界明确；
- \(s,p,d\) 的维数、顺序、归一化、正交性和群律可独立复算；
- 一般 \((\ell,p)\) 与轨道宇称 \((-1)^\ell\) 不混淆；
- 多壳层维度、参数量、字节和 provenance 均有正例与失败例；
- D-E02/D-E09 子推导、八个例题、10 道题解和数值复算一致；
- 严格 Markdown/MathML、链接、控制字符和独立内容审计全部通过。

本章不安装 DeepH/e3nn，不使用正式数据或 DFT 标签，不选择材料体系、DFT/数据后端、DeepH 软件对象、实践版本或 SOC 实践范围。

### 16.8.5 章节小结

表示把抽象群复合转化为对象空间中的矩阵复合；不可约分量给出不能再由同一群作用分解的基本类型，multiplicity 则记录同型副本。实 \(s,p,d\) 表分别由一维标量、三维极向量和五维对称无迹张量承载，且所有基顺序、归一化和列/行语义均已固定。

\(SO(3)\) 的 \(\ell\) 标签不足以确定反演行为；一般 \(O(3)\) 特征还需宇称 \(p\)，而轨道型 \(s,p,d\) 专门满足 \((-1)^\ell\)。这些表示和多壳层身份是球谐相似变换、CG 耦合与 Hamiltonian 左右作用的输入契约，任一顺序或 provenance 漂移都会使后续数值等变比较失去语义。
