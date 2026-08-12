# D-E04：Clebsch--Gordan 选择定则、低阶分解与 intertwiner

## 1. 目标、范围与依赖

本推导完成阶段 E 的 D-E04，并给出 D-E06 中张量积/门控子对象以及 D-E09 的局部维数与 contraction 成本边界。目标是：

- 从张量积群作用推出三角条件、\(M=m_1+m_2\) 与 intertwiner；
- 给出 DLMF/Condon--Shortley 规范 CG 系数的可复算有限和；
- 构造完整 \(1\otimes1=0\oplus1\oplus2\) 表；
- 区分正交、完整性、规范表一致性和等变性；
- 证明整条输出通道相位自由合法，而局部相位、错轴和交换相位遗漏失败；
- 连接实笛卡尔 trace/反对称/对称无迹分解；
- 冻结 multiplicity、宇称、mask、provenance 和测试映射。

依赖第 15 章的主动群作用、第 16 章实 \(s,p,d\) 表、第 17 章 \(K_1,K_2\) 与 Wigner \(D\)，以及 [阶段 E 统一表示约定](../../03_textbook/stageE_representation_conventions.md)。本文件不实现第 19 章完整消息层，也不替代 [M7-09 代码说明](../../05_code_exercises/stageE_synthetic_equivariance/README.md) 与 [独立定点复核](../../08_audits/M7_stageE_code_blocking_reaudit.md) 中的 T-E05/T-E08/T-E10 执行证据。

## 2. 符号、维度和冻结索引

| 对象 | shape | dtype | 顺序/条件 |
|---|---:|---|---|
| \(x^{(\ell_1)}\) | \((2\ell_1+1,)\) | complex64/128 | \(m_1=-\ell_1,\ldots,\ell_1\) |
| \(y^{(\ell_2)}\) | \((2\ell_2+1,)\) | complex64/128 | \(m_2=-\ell_2,\ldots,\ell_2\) |
| \(q=x\otimes y\) | \(((2\ell_1+1)(2\ell_2+1),)\) | 同输入提升规则 | \(m_2\) 快轴 |
| \(C\) | \((n_{\mathrm{out}},n_{\mathrm{prod}})\) | float64 规范表 | 行 \((L,M)\)，列 \((m_1,m_2)\) |
| \(z=Cq\) | \((n_{\mathrm{out}},)\) | complex64/128 | \(L\) 递增、每块 \(M\) 递增 |
| \(D_{\mathrm{prod}}\) | \((n_{\mathrm{prod}},n_{\mathrm{prod}})\) | complex64/128 | \(D^{(\ell_1)}\otimes D^{(\ell_2)}\) |
| \(D_{\mathrm{out}}\) | \((n_{\mathrm{out}},n_{\mathrm{out}})\) | complex64/128 | \(\bigoplus_LD^{(L)}\) |

完整分解时

\[
n_{\mathrm{prod}}=n_{\mathrm{out}}
=(2\ell_1+1)(2\ell_2+1).
\]

列索引冻结为

\[
a(m_1,m_2)
=(m_1+\ell_1)(2\ell_2+1)+(m_2+\ell_2).
\]

行偏移定义为

\[
b(L,M)
=
\sum_{J=|\ell_1-\ell_2|}^{L-1}(2J+1)+(M+L).
\]

当 \(L=|\ell_1-\ell_2|\) 时空和为零。所有数组必须具有严格 rank/shape、有限元素、声明 dtype 和完整 irrep shell；部分 component mask 不得进入稠密 contraction。

## 3. 张量积群作用

由

\[
x'=D_1x,\qquad y'=D_2y
\]

和 Kronecker 积恒等式

\[
(D_1x)\otimes(D_2y)
=(D_1\otimes D_2)(x\otimes y)
\]

得到

\[
q'=D_{\mathrm{prod}}q,
\qquad
D_{\mathrm{prod}}=D^{(\ell_1)}\otimes D^{(\ell_2)}.
\]

维数为

\[
n_{\mathrm{prod}}=(2\ell_1+1)(2\ell_2+1).
\]

若 \(C\) 是从乘积坐标到耦合坐标的矩阵，

\[
z=Cq,
\]

希望 \(z\) 按输出块表示变换：

\[
z'=D_{\mathrm{out}}z.
\]

另一方面

\[
z'=Cq'=CD_{\mathrm{prod}}q.
\]

对任意 \(q\) 相等当且仅当

\[
CD_{\mathrm{prod}}=D_{\mathrm{out}}C.
\]

这就是 intertwiner 恒等式。

## 4. 选择定则

### 4.1 \(M=m_1+m_2\)

绕 \(z\) 轴旋转时

\[
D^{(\ell)}_{mm}(R_z(\alpha))=e^{-im\alpha}.
\]

对一个系数非零的项，intertwiner 要求

\[
e^{-i(m_1+m_2)\alpha}
=e^{-iM\alpha}
\]

对任意 \(\alpha\) 成立，因此

\[
M=m_1+m_2.
\]

这只是必要条件。任何对角行相位矩阵都与 \(R_z\) 表示对易，因此一般轴测试仍然不可省略。

### 4.2 三角条件

最高权重法给出乘积中的最大 \(M=\ell_1+\ell_2\)，故最大输出 \(L_{\max}=\ell_1+\ell_2\)。反复取与已构造最高权重态正交的下一最高权重态，得到

\[
L=\ell_1+\ell_2,\ell_1+\ell_2-1,\ldots,|\ell_1-\ell_2|.
\]

维数求和验证没有遗漏：

\[
\sum_{L=|\ell_1-\ell_2|}^{\ell_1+\ell_2}(2L+1)
=(2\ell_1+1)(2\ell_2+1).
\]

设 \(\ell_1\ge\ell_2\)，则左侧为

\[
\sum_{L=\ell_1-\ell_2}^{\ell_1+\ell_2}(2L+1)
=(2\ell_2+1)(2\ell_1+1).
\]

### 4.3 \(O(3)\) 宇称

若反演分别作用为 \(p_1I\) 与 \(p_2I\)，则乘积空间上为

\[
(p_1I)\otimes(p_2I)=p_1p_2I.
\]

所以每个输出 \(L\) 具有

\[
p_{\mathrm{out}}=p_1p_2.
\]

该结论不含 \((-1)^L\)。\((-1)^\ell\) 只适用于轨道型球谐自身；一般表示型特征必须显式携带 \(p\)。

## 5. CG--\(3j\) 关系与可复算有限和

规范关系为

\[
C^{LM}_{\ell_1m_1,\ell_2m_2}
=
(-1)^{\ell_1-\ell_2+M}\sqrt{2L+1}
\begin{pmatrix}
\ell_1&\ell_2&L\\
m_1&m_2&-M
\end{pmatrix}.
\]

对本阶段整数角动量，Wigner \(3j\) 可由 Racah 有限和复算。定义

\[
\Delta(j_1,j_2,j_3)
=
\frac{
(j_1+j_2-j_3)!
(j_1-j_2+j_3)!
(-j_1+j_2+j_3)!
}{
(j_1+j_2+j_3+1)!
}.
\]

若 \(m_1+m_2+m_3=0\)，则

\[
\begin{aligned}
\begin{pmatrix}
j_1&j_2&j_3\\
m_1&m_2&m_3
\end{pmatrix}
={}&
(-1)^{j_1-j_2-m_3}
\sqrt{\Delta(j_1,j_2,j_3)}
\\
&\times
\sqrt{
(j_1+m_1)!(j_1-m_1)!
(j_2+m_2)!(j_2-m_2)!
(j_3+m_3)!(j_3-m_3)!
}
\\
&\times
\sum_z
\frac{(-1)^z}{
z!
(j_1+j_2-j_3-z)!
(j_1-m_1-z)!
(j_2+m_2-z)!
}
\\
&\times
\frac1{
(j_3-j_2+m_1+z)!
(j_3-j_1-m_2+z)!
}.
\end{aligned}
\]

求和只遍历使所有阶乘参数为非负整数的 \(z\)。若磁量子数和、三角条件或 \(|m_i|\le j_i\) 失败，值为零。实现必须用整数逻辑确定求和上下界，不能依赖浮点“接近整数”判断。

## 6. 正交、完整性与交换

规范系数满足输出正交关系

\[
\sum_{m_1,m_2}
C^{LM}_{\ell_1m_1,\ell_2m_2}
C^{L'M'}_{\ell_1m_1,\ell_2m_2}
=
\delta_{LL'}\delta_{MM'},
\]

以及乘积基完备性

\[
\sum_{L,M}
C^{LM}_{\ell_1m_1,\ell_2m_2}
C^{LM}_{\ell_1m_1',\ell_2m_2'}
=
\delta_{m_1m_1'}\delta_{m_2m_2'}.
\]

矩阵形式为

\[
CC^{\mathsf T}=I,
\qquad
C^{\mathsf T}C=I.
\]

输入交换关系为

\[
C^{LM}_{\ell_2m_2,\ell_1m_1}
=
(-1)^{\ell_1+\ell_2-L}
C^{LM}_{\ell_1m_1,\ell_2m_2}.
\]

交换实现必须同时：

1. 交换输入类型、multiplicity 和 component 轴；
2. 将 Kronecker 列应用 perfect-shuffle 置换；
3. 对每个 \(L\) 施加上述交换相位；
4. 同步 provenance 中的输入方向。

只改变数组 shape 或只转置最后两轴不足以满足合同。

## 7. 构造 \(1\otimes1\) 全表

### 7.1 \(L=2\) 最高权重链

最高权重态唯一：

\[
|2,2\rangle=|1,1\rangle|1,1\rangle.
\]

用总降算符

\[
J_-=J_{1,-}+J_{2,-}
\]

以及

\[
J_-|L,M\rangle
=
\sqrt{(L+M)(L-M+1)}|L,M-1\rangle
\]

得到

\[
|2,1\rangle
=\frac1{\sqrt2}
\left(
|1,1\rangle|1,0\rangle
+|1,0\rangle|1,1\rangle
\right),
\]

\[
|2,0\rangle
=\frac1{\sqrt6}
\left(
|1,1\rangle|1,-1\rangle
+2|1,0\rangle|1,0\rangle
+|1,-1\rangle|1,1\rangle
\right).
\]

继续下降得到 \(M=-1,-2\) 行。

### 7.2 \(L=1\) 反对称链

在 \(M=1\) 二维子空间中，与 \(|2,1\rangle\) 正交并满足冻结锚点的态为

\[
|1,1\rangle_{\mathrm{coupled}}
=
\frac1{\sqrt2}
\left(
|1,1\rangle|1,0\rangle
-|1,0\rangle|1,1\rangle
\right).
\]

下降得到

\[
|1,0\rangle_{\mathrm{coupled}}
=
\frac1{\sqrt2}
\left(
|1,1\rangle|1,-1\rangle
-|1,-1\rangle|1,1\rangle
\right),
\]

\[
|1,-1\rangle_{\mathrm{coupled}}
=
\frac1{\sqrt2}
\left(
|1,0\rangle|1,-1\rangle
-|1,-1\rangle|1,0\rangle
\right).
\]

三行在输入交换下变号。

### 7.3 \(L=0\) 标量

\(M=0\) 三维子空间中与 \(L=2,M=0\) 和 \(L=1,M=0\) 正交，并满足

\[
C^{00}_{1\,1,1\,-1}=+\frac1{\sqrt3}
\]

的单位向量为

\[
|0,0\rangle
=
\frac1{\sqrt3}
\left(
|1,1\rangle|1,-1\rangle
-|1,0\rangle|1,0\rangle
+|1,-1\rangle|1,1\rangle
\right).
\]

### 7.4 稀疏表与确定性序列化

输入列和输出行顺序沿用第 2 节。规范表的所有非零值为：

| 行 \((L,M)\) | 列 \((m_1,m_2)\) 与值 |
|---|---|
| \((0,0)\) | \((-1,1):1/\sqrt3,(0,0):-1/\sqrt3,(1,-1):1/\sqrt3\) |
| \((1,-1)\) | \((-1,0):-1/\sqrt2,(0,-1):1/\sqrt2\) |
| \((1,0)\) | \((-1,1):-1/\sqrt2,(1,-1):1/\sqrt2\) |
| \((1,1)\) | \((0,1):-1/\sqrt2,(1,0):1/\sqrt2\) |
| \((2,-2)\) | \((-1,-1):1\) |
| \((2,-1)\) | \((-1,0):1/\sqrt2,(0,-1):1/\sqrt2\) |
| \((2,0)\) | \((-1,1):1/\sqrt6,(0,0):\sqrt{2/3},(1,-1):1/\sqrt6\) |
| \((2,1)\) | \((0,1):1/\sqrt2,(1,0):1/\sqrt2\) |
| \((2,2)\) | \((1,1):1\) |

M7-09 已从规范版本、索引数组和精确符号表达构造可追溯 hash，见 [代码说明](../../05_code_exercises/stageE_synthetic_equivariance/README.md)；不得对 float 字节直接跨平台宣称同一规范身份。规范身份与运行数组 hash 应分字段记录。

### 7.5 \(1\otimes2\) 三个规范锚点

把第 5 节 Racah 有限和用于 \((\ell_1,\ell_2)=(1,2)\)，三个最高 \(M=L\) 行为

\[
\begin{aligned}
|1,1\rangle
&=
\sqrt{\frac35}|-1,2\rangle
-\sqrt{\frac3{10}}|0,1\rangle
+\frac1{\sqrt{10}}|1,0\rangle,\\
|2,2\rangle
&=
-\sqrt{\frac23}|0,2\rangle
+\frac1{\sqrt3}|1,1\rangle,\\
|3,3\rangle
&=|1,2\rangle.
\end{aligned}
\]

三行分别固定 \(L=1,2,3\) 的 DLMF 相位。由有限和生成全部 15 行后，

\[
\lVert CC^{\mathsf T}-I_{15}\rVert_F,
\quad
\lVert C^{\mathsf T}C-I_{15}\rVert_F
\]

在 float64 中均应处于 \(10^{-15}\) 量级。对轴 \((1,2,3)/\sqrt{14}\)、角度 \(0.7\) 的固定一般轴旋转，规范表的归一化 intertwiner 残差为

\[
2.64\times10^{-16}.
\]

保持 CG 列不变却反转 Kronecker 输入轴时，残差为 \(0.9192367498522585\)。交换到 \(2\otimes1\) 时必须使用

\[
(-1)^{1+2-L}=(-1)^{3-L};
\]

遗漏 \(L=2\) 的负号给出最大规范系数误差 \(1.6329931618554523\)。这些数值作为 T-E05 章内回归锚点，正式代码仍须从冻结公式生成并验证全表。

## 8. \(1\otimes1\) 的实笛卡尔分解

### 8.1 标量通道

第 17 章冻结

\[
x_{\mathrm{c}}=K_1u,\qquad y_{\mathrm{c}}=K_1v.
\]

把 \(L=0\) CG 行作用于 \(K_1\otimes K_1\)，得到

\[
C^{(0)}(K_1\otimes K_1)
=-\frac1{\sqrt3}
\begin{pmatrix}
1&0&0&0&1&0&0&0&1
\end{pmatrix}.
\]

因此

\[
z_{00}=-\frac{u\cdot v}{\sqrt3}.
\]

### 8.2 反对称通道

令 \(C^{(1)}\) 为三条 \(L=1\) 行。直接矩阵乘法给出

\[
K_1^\dagger C^{(1)}(K_1\otimes K_1)(u\otimes v)
=-\frac{i}{\sqrt2}(u\times v).
\]

叉积是轴向量。对两个极向量 \(p_1=p_2=-1\)，输出宇称为 \(+1\)，与 \(SO(3)\) 标签 \(L=1\) 独立。

### 8.3 对称无迹通道

定义

\[
Q(u,v)
=
\frac12(uv^{\mathsf T}+vu^{\mathsf T})
-\frac{u\cdot v}{3}I.
\]

显然

\[
Q^{\mathsf T}=Q,\qquad\operatorname{tr}Q=0.
\]

旋转后

\[
\begin{aligned}
Q(Ru,Rv)
&=
\frac12(Ruv^{\mathsf T}R^{\mathsf T}
+Rvu^{\mathsf T}R^{\mathsf T})
-\frac{u\cdot v}{3}I\\
&=RQ(u,v)R^{\mathsf T}.
\end{aligned}
\]

用第 16 章正交基 \(B_a\) 取

\[
q_a=\operatorname{tr}(B_a^{\mathsf T}Q),
\]

则 \(q\) 按实 \(D^d(R)\) 变换。令 \(T_B\) 的第 \(a\) 行是 \(\operatorname{vec}(B_a)^{\mathsf T}\)，直接代入正文的 \(C^{(2)},K_1,K_2,B_a\) 可逐元素验证矩阵恒等式

\[
C^{(2)}(K_1\otimes K_1)=K_2T_B.
\]

因此对任意实 \(u,v\)，冻结规范下的精确等式是

\[
\boxed{
C^{(2)}
\left[(K_1u)\otimes(K_1v)\right]
=K_2q
}.
\]

比例严格为 \(+1\)，没有待拟合相位。T-E05 必须直接比较两端；错误比例 \(\sqrt2\)、局部 \(M\) 相位或未同步的 \(K_2\) 顺序必须失败。若重新定义整个 \(L=2\) 输出基相位，必须同步变换 \(C^{(2)}\)、基映射、规范元数据和全部下游对象，不能在每个测试样例上临时拟合。

### 8.4 维数直和

任意 \(3\times3\) 张量可唯一分解为

\[
uv^{\mathsf T}
=
\frac{u\cdot v}{3}I
+\frac12(uv^{\mathsf T}-vu^{\mathsf T})
+Q(u,v).
\]

三个子空间维数分别为 \(1,3,5\)，两两正交且总维数 \(9\)。

## 9. 相位自由和失败分类

### 9.1 整通道相位

令

\[
S=\bigoplus_L e^{i\phi_L}I_{2L+1},
\qquad
\widetilde C=SC.
\]

因为

\[
SD_{\mathrm{out}}=D_{\mathrm{out}}S,
\]

所以

\[
\widetilde C D_{\mathrm{prod}}
=SCD_{\mathrm{prod}}
=SD_{\mathrm{out}}C
=D_{\mathrm{out}}SC
=D_{\mathrm{out}}\widetilde C.
\]

同时 \(S\) 幺正，故 \(\widetilde C\widetilde C^\dagger=I\)。这严格证明整通道相位不破坏等变性。

### 9.2 部分 \(M\) 相位

若 \(S_L\) 在一个 \(L\) 块内不同 \(M\) 使用不同相位，则一般有

\[
[S_L,D^{(L)}(R)]\ne0.
\]

只有在 \(D^{(L)}(R)\) 与 \(S_L\) 偶然同时对角时才可能漏检。因此 T-E05 必须含一般轴旋转。

### 9.3 单系数变异

单独改变 \(C\) 的一个非零元素通常使：

\[
CC^\dagger\ne I,
\qquad
C^\dagger C\ne I,
\qquad
CD_{\mathrm{prod}}\ne D_{\mathrm{out}}C.
\]

规范表逐项比较是最直接的定位器；正交和 intertwiner 是独立语义门控。

### 9.4 删通道

取选择矩阵 \(P\) 保留部分输出，\(\widehat C=PC\)。若所保留的是完整 \(L\) 块，则

\[
\widehat C D_{\mathrm{prod}}
=\widehat D_{\mathrm{out}}\widehat C
\]

仍可成立，但

\[
\widehat C^\dagger\widehat C\ne I
\]

于完整输入空间。故它是等变路径裁剪，不是完整分解。测试合同必须区分两种目标。

## 10. multiplicity、路径与同型混合

令输入具有 multiplicity：

\[
x_{\mu_1m_1},
\qquad
y_{\mu_2m_2}.
\]

每个输入副本对形成

\[
z_{\mu_1\mu_2,LM}
=
\sum_{m_1,m_2}
C^{LM}_{\ell_1m_1,\ell_2m_2}
x_{\mu_1m_1}y_{\mu_2m_2}.
\]

CG 只收缩 \(m_1,m_2\)，不收缩 \(\mu_1,\mu_2\)。对固定 \((L,p)\)，随后可用

\[
\widetilde z_{\nu M}
=
\sum_{\mu_1,\mu_2}
W^{(L,p)}_{\nu,\mu_1\mu_2}
z_{\mu_1\mu_2,LM}
\]

混合路径。权重对所有 \(M\) 共享，因此

\[
W^{(L,p)}D^{(L)}=D^{(L)}W^{(L,p)}
\]

在不同轴上自然成立。若每个 \(M\) 使用不同任意权重，通常破坏等变性。

## 11. 标量门控与失败非线性

\(0\otimes\ell=\ell\) 的规范系数只描述 \(SO(3)\) 角动量部分：

\[
C^{\ell M}_{0\,0,\ell m}=\delta_{Mm}.
\]

对 \(O(3)\)，门值还带宇称 \(p_g\)。若 \(g_+:(0,+1)\) 为偶标量，

\[
z_M=gx_M,
\]

则

\[
z'_M
=g\sum_mD^{(\ell)}_{Mm}x_m
=\sum_mD^{(\ell)}_{Mm}(gx_m).
\]

则在正旋转和反演下都保持输入类型 \((\ell,p_x)\)。一般 \(g:(0,p_g)\) 门控的输出类型是

\[
(\ell,p_gp_x).
\]

因此伪标量 \(g_-:(0,-1)\) 会翻转输出宇称，不能称为类型保持门控。

对偶标量 \(s_+\)，任意普通函数 \(\sigma(s_+)\) 仍为偶标量。对伪标量 \(s_-\)，只有满足

\[
\sigma(-s_-)=+\sigma(s_-)
\]

的偶函数输出 \((0,+1)\)，或满足

\[
\sigma(-s_-)=-\sigma(s_-)
\]

的奇函数输出 \((0,-1)\)。例如 \(s_-^2\) 是偶标量，\(s_-^3\) 是伪标量，而

\[
\sigma_{\mathrm{bad}}(s_-)=1+s_-
\]

在反演后成为 \(1-s_-\)，一般无确定宇称，必须拒绝。

对逐分量非线性 \(f\)，一般

\[
f(Dx)\ne Df(x).
\]

教材例 18-10 用 \(u=(1,2,0)^{\mathsf T}\)、\(R_z(\pi/2)\) 和逐分量平方得到差 \((8,0,0)^{\mathsf T}\)，为 T-E08 的强制失败锚点之一。T-E07/T-E08/T-E12 还必须实际执行偶标量门控的反演正例、伪标量奇函数的宇称更新，以及 \(1+s_-\) 无确定宇称的拒绝例。

## 12. mask、padding、edge identity 与 provenance

CG contraction 的最小输入单元是两个完整 irrep shell。对每个 shell：

- component 数必须恰为 \(2\ell+1\)；
- component mask 必须全真或全假；
- inactive padding 必须在 contraction 前切除；
- active 元素必须有限，dtype/shape 与元数据一致。

图消息中的离散边身份

\[
(\text{stageD-edge-v1},
\text{structure ID},
\text{receiver},
\text{sender},
n_x,n_y,n_z)
\]

在旋转和纯表示耦合下不变。CG 输出、径向权重、球谐方向、receiver 聚合和 provenance 必须共享同一 edge-row 映射。

路径 provenance 最少包含：

| 字段 | 条件 |
|---|---|
| input A | node/edge identity、\((\ell_1,p_1,\mu_1)\)、component 顺序 |
| input B | node/edge identity、\((\ell_2,p_2,\mu_2)\)、component 顺序 |
| output | \((L,p_1p_2,\nu)\)、\(M\) 递增 |
| CG identity | DLMF/Condon--Shortley、表版本/hash、快轴、输入交换方向 |
| path | allowed/kept、径向权重或同型混合权重身份 |
| tensor | dtype、shape、mask、有限值状态、容差 |

只保留数值数组而丢弃路径身份，不能证明错轴、交换或 edge-row 污染未发生。

## 13. 局部成本子预算

对一个 \(1\otimes1\) 输入副本对，若先物化

\[
q=x\otimes y,
\]

形成 \(q\) 需要 9 次分量乘法。随后稀疏 \(Cq\) 的非零 CG 项数为

\[
3+2+2+2+1+2+3+2+1=18.
\]

因此显式“先乘积、后投影”操作图需要：

\[
9\ \text{次乘积形成}
+18\ \text{次系数缩放}
+9\ \text{次同输出累加}.
\]

最后一项来自各输出行的 \((k_{\mathrm{row}}-1)\) 求和，总数为 \(18-9=9\)。若实际 kernel 从零初始化每个输出，并把每个非零项的“系数缩放后累加”记为一个 FMA/MAC，则可报告 18 MAC，但必须另行报告前面的 9 次乘积形成。对 \(n_1n_2\) 个输入副本对，相应为

\[
9n_1n_2\ \text{乘积形成},
\qquad
18n_1n_2\ \text{MAC}.
\]

这是实标量操作图的 CG 局部子预算。complex64/128 的复乘、实系数缩放和复加必须在实现中另行展开成唯一实 FLOP 口径；不得直接把一个复 MAC 当成两个实 FLOP。本节不包含：

- 球谐生成；
- 径向网络；
- 同型通道混合；
- receiver 聚合；
- mask/index 操作；
- 图数组和临时量；
- 反向传播；
- wall-time。

T-E10 仍按统一约定对其冻结的同型逐边线性 reference kernel 以每 MAC=2 FLOP、聚合加法分列、逐数组/total/reference peak bytes 和 144 点网格报告。该 kernel 与本节 CG 子操作图不是同一个成本对象；不得把 18 MAC 外推成完整消息层成本。

## 14. 可执行验证合同

### 14.1 T-E05

对 \(0\otimes\ell\)、\(1\otimes1\) 和代码实际使用的 \(1\otimes2\) 部分，执行：

1. shape、dtype、有限值、索引和零模式；
2. 三角条件与 \(M=m_1+m_2\)；
3. DLMF 规范表逐项一致；
4. \(1\otimes1\) 三个相位锚点；
5. 输入交换相位；
6. \(CC^\dagger=I\) 与 \(C^\dagger C=I\)；
7. 冻结旋转集的 intertwiner 残差；
8. 整通道相位变异只触发 canonical-table fail；
9. 部分 \(M\)、单系数、错轴、漏交换相位实际拒绝；
10. \(1\otimes2\) 三个最高行锚点、固定一般轴和 \(1\otimes2\leftrightarrow2\otimes1\) 交换；
11. 实 STF 路线直接满足 \(z^{(2)}=K_2q\)，不拟合比例/相位；
12. float64/32 阈值分别为 \(5\times10^{-12}\)/\(5\times10^{-6}\)。

### 14.2 T-E08

把 CG contraction 接入最小消息对象链：

\[
\text{node irrep}
\to
\text{edge spherical harmonic}
\to
\text{CG path}
\to
\text{radial scalar}
\to
\text{same-type mixing}
\to
\text{receiver aggregation}
\to
\text{scalar gate}.
\]

逐层和端到端比较旋转前后输出。强制失败包括高阶逐分量非线性、错误 CG 通道、边方向或 edge-row 错位、partial mask、padding 穿透和伪标量 \(1+s_-\) 无确定宇称。偶标量门控反演正例及合法伪标量奇/偶函数的输出宇称须由 T-E07/T-E08 同步验证。

### 14.3 T-E10

本章只提供维数和 CG 局部 MAC。正式 T-E10 必须执行统一约定的 144 点网格、固定图 \(G_A/G_B\)、PCG64 draw order、完整 kernel、MAC/FLOP、聚合加法、逐数组/total/reference peak 和独立 wall-time 口径。

## 15. D-E/T-E/C-E 映射

| 对象 | 本文件位置 | 后续测试 | 正确证据 | 强制失败 |
|---|---|---|---|---|
| D-E04 选择定则 | 第 4—6 节 | T-E05 | 三角、\(M\) 和交换关系 | 非允许 \(L,M\) 非零、漏交换相位 |
| D-E04 \(1\otimes1\)/\(1\otimes2\) | 第 7—9 节 | T-E05 | 全表、三锚点、\(1\otimes2\) 三最高行、正交、一般轴/交换 intertwiner、\(z^{(2)}=K_2q\) | 单系数、部分 \(M\)、错轴、错误比例/临时相位拟合 |
| D-E04 实/复交叉 | 第 8 节 | T-E04/T-E05 | dot/cross/STF 与 \(K_1,K_2\) | 未同步基/相位 |
| D-E06 张量积路径 | 第 10—12 节 | T-E07/T-E08/T-E12 | 类型、宇称门控、mask、edge、provenance | padding、identity、高阶非线性、伪标量 \(1+s_-\) |
| D-E09 局部成本 | 第 13—14 节 | T-E10 | 9 次乘积形成、18 非零项缩放/零初始化 MAC、9 次真实累加及排除项 | 漏乘积形成、复 MAC 冒充两个实 FLOP或局部预算冒充完整成本 |
| C-E05 自学能力 | 全文 | M7-10 | 规范相位自由与错误相位区分 | 只背锚点或选择定则 |

## 16. 推导结论

张量积的群作用由 Kronecker 积给出，CG 矩阵通过 intertwiner 将其分块为允许的 \(L\) 通道。完整分解同时需要规范表、正交、完备和一般轴 intertwiner 四类证据。\(1\otimes1\) 的九维空间精确分成标量、轴向反对称和对称无迹三个子空间；宇称由输入相乘决定。整通道相位是合法基自由，局部相位、错轴、遗漏交换相位和不完整身份映射才是实现错误。
