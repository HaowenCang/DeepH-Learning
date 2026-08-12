# D-E01 与 D-E09：群作用、几何等变和残差预算

## 1. 推导目标

本文件完成 D-E01，并给出第 15 章所需的 D-E09 子部分：

- 从主动作用推导复合顺序，并从基矩阵等式推导被动换基及其复合顺序；
- 从输入/输出表示推导不变与等变关系；
- 推导向量、二阶张量、轴向量和周期边位移的变换；
- 桥接行晶格存储与列向量旋转；
- 给出可独立复算的归一化残差、精度条件和强制失败判据。

约定来源为 [阶段 E 统一表示约定](../../03_textbook/stageE_representation_conventions.md)。

## 2. 符号、维度与适用条件

| 符号 | 类型或维度 | 本文件中的含义 |
|---|---|---|
| \(G,g\) | 群及其元素 | 抽象群作用；具体几何作用取旋转或正交变换 |
| \(R\) | \(\mathbb R^{3\times3}\)，\(R^{\mathsf T}R=I\)，\(\det R=1\) | 列向量上的主动正旋转 |
| \(Q\) | \(\mathbb R^{3\times3}\)，\(Q^{\mathsf T}Q=I\)，\(\det Q=\pm1\) | 含反射的正交变换 |
| \(t\) | \(\mathbb R^3\) | 欧氏变换的平移；相对位移中消去 |
| \(u,v,w,d\) | \(\mathbb R^3\) 列向量 | 极向量、叉积输入或周期边位移 |
| \(T\) | \(\mathbb R^{3\times3}\) | 二阶笛卡尔张量 |
| \(A\) | \(\mathbb R^{3\times3}\)，晶格矢量按行存储 | 有效周期晶格；几何旋转使用 \(A'=AR^{\mathsf T}\) |
| \(f_i,f_j\) | \(\mathbb R^{1\times3}\) 行向量 | 规范分数坐标 |
| \(n\) | \(\mathbb Z^{1\times3}\) 行向量 | 周期镜像 shift 与完整边键的一部分 |
| \(\rho_{\mathrm{in/out}}(g)\) | 输入/输出空间上的可逆线性算子 | 群表示；维度分别由输入/输出对象决定 |
| \(F\) | \(V_{\mathrm{in}}\to V_{\mathrm{out}}\) | 待验证的不变或等变映射 |
| \(D_i,D_j\) | \(\mathbb C^{d_i\times d_i}\)、\(\mathbb C^{d_j\times d_j}\) | 轨道表示接口 |
| \(H_{ij}\) | \(\mathbb C^{d_i\times d_j}\) | Hamiltonian 子块接口；本文件不构造具体 \(s,p,d\) 表 |
| \(\rho(A,B)\) | 非负实标量 | 第 10 节的归一化 Frobenius 残差；与群表示按参数个数区分 |

所有参与数值残差的数组必须具有相同 shape、有限元素和已声明 dtype；NaN、无穷、非法旋转、无效晶格或身份错位应先拒绝。第 3—9 节完成 D-E01 的几何子空间推导，第 10—12 节只完成 D-E09 的残差、精度解释与成本报告接口。Hamiltonian 的具体 \(D_i,D_j\)、轨道顺序和 CG contraction 位于第 16—19 章及 M7-08；实际 A/B/144 点执行证据位于 [M7-09 代码说明](../../05_code_exercises/stageE_synthetic_equivariance/README.md) 和 [独立定点复核](../../08_audits/M7_stageE_code_blocking_reaudit.md)，不得由本文件的接口式代替。

## 3. 群作用与复合

设 \(G\) 为群，\(\rho:G\to GL(V)\) 为线性表示。按定义

\[
\rho(e)=I,\qquad
\rho(g^{-1})=\rho(g)^{-1},\qquad
\rho(g_2g_1)=\rho(g_2)\rho(g_1).
\]

对主动旋转 \(R\) 和列向量 \(v\)：

\[
\rho(R)v=Rv.
\]

先 \(R_1\) 后 \(R_2\)：

\[
\rho(R_2)\rho(R_1)v
=R_2R_1v
=\rho(R_2R_1)v.
\]

因此总矩阵必须是 \(R_2R_1\)。这不是记号偏好，而由函数复合次序决定。

### 3.1 被动换基的对象与逐步推导

被动换基不旋转物理向量，只改变用于报告同一向量坐标的基。令旧基矩阵

\[
E_{\mathrm{old}}=(e_1\ e_2\ e_3)\in\mathbb R^{3\times3}
\]

以基向量为列；假定 \(E_{\mathrm{old}}\) 是右手正交 Cartesian 基。令 \(R\in SO(3)\) 是以旧基分量表示的新基定向，并定义

\[
E_{\mathrm{new}}=E_{\mathrm{old}}R.
\]

物理向量 \(v_{\mathrm{phys}}\) 不变，因而它在两套基中的坐标满足

\[
v_{\mathrm{phys}}
=E_{\mathrm{old}}[v]_{\mathrm{old}}
=E_{\mathrm{new}}[v]_{\mathrm{new}}
=E_{\mathrm{old}}R[v]_{\mathrm{new}}.
\]

左乘 \(E_{\mathrm{old}}^{-1}=E_{\mathrm{old}}^{\mathsf T}\)，得到

\[
[v]_{\mathrm{old}}=R[v]_{\mathrm{new}},
\qquad
[v]_{\mathrm{new}}=R^{\mathsf T}[v]_{\mathrm{old}}.
\]

这里 \(R^{\mathsf T}\) 回答的是“同一物理向量在旋转后的新基中有什么坐标”；主动式 \(v'=Rv\) 回答的是“固定基中被旋转后的物理向量有什么坐标”。两式的对象身份不同，不能仅因矩阵互为转置而互换。

若第一次新基相对旧基的右因子为 \(R_1\)，第二次新基相对当前基的右因子为 \(R_2\)，则

\[
E_1=E_0R_1,
\qquad
E_2=E_1R_2=E_0R_1R_2,
\]

并且

\[
[v]_1=R_1^{\mathsf T}[v]_0,
\qquad
[v]_2=R_2^{\mathsf T}[v]_1
=R_2^{\mathsf T}R_1^{\mathsf T}[v]_0
=(R_1R_2)^{\mathsf T}[v]_0.
\]

因此连续被动换基的坐标算符按 \(R_2^{\mathsf T}R_1^{\mathsf T}\) 复合；这与固定基中先主动旋转 \(R_1\)、再主动旋转 \(R_2\) 所得的 \(R_2R_1\) 不是同一对象链。

### 3.2 被动换基解析正例与误用失败

取旧基为标准 Cartesian 基 \(E_0=I_3\)，所有数组为 C-order `float64`，\(R=R_z(\pi/2)\) 的 shape 为严格 \((3,3)\)，坐标的 shape 为严格 \((3,)\)：

\[
R=
\begin{pmatrix}
0&-1&0\\
1&0&0\\
0&0&1
\end{pmatrix},
\qquad
[v]_0=e_x=(1,0,0)^{\mathsf T}.
\]

新基为 \(E_1=E_0R=R\)，同一物理向量在新基中的正确坐标为

\[
[v]_1=R^{\mathsf T}e_x=(0,-1,0)^{\mathsf T},
\]

且回构给出

\[
E_1[v]_1=R(0,-1,0)^{\mathsf T}=e_x=v_{\mathrm{phys}}.
\]

若把被动坐标式误用为主动旋转，错误地把 \(R^{\mathsf T}e_x=-e_y\) 与正确主动目标 \(Re_x=e_y\) 等同，则

\[
\rho(Re_x,R^{\mathsf T}e_x)
=\frac{\lVert e_y-(-e_y)\rVert_2}
{\max(1,\lVert e_y\rVert_2,\lVert-e_y\rVert_2)}
=2.
\]

该正例只在物理向量身份保持不变、基矩阵右乘 \(R\)、旧/新基均为同一三维 Euclidean 空间中的右手正交 Cartesian 基时成立。若基不正交，应使用一般逆矩阵而不能把逆静默替换为转置；非法 dtype、rank、shape 或非有限值必须在坐标运算前拒绝。

## 4. 等变映射的复合一致性

设输入表示 \(\rho_{\mathrm{in}}\)、输出表示 \(\rho_{\mathrm{out}}\)，并假设

\[
F(\rho_{\mathrm{in}}(g)x)
=\rho_{\mathrm{out}}(g)F(x).
\]

对 \(g_1,g_2\)：

\[
\begin{aligned}
F(\rho_{\mathrm{in}}(g_2g_1)x)
&=F(\rho_{\mathrm{in}}(g_2)\rho_{\mathrm{in}}(g_1)x)\\
&=\rho_{\mathrm{out}}(g_2)
F(\rho_{\mathrm{in}}(g_1)x)\\
&=\rho_{\mathrm{out}}(g_2)
\rho_{\mathrm{out}}(g_1)F(x)\\
&=\rho_{\mathrm{out}}(g_2g_1)F(x).
\end{aligned}
\]

若输出表示为平凡表示 \(\rho_{\mathrm{out}}(g)=I\)，即得不变性。反之，输出是向量或张量时不能要求数值数组不变。

## 5. 行晶格桥接

阶段 B 的行晶格满足

\[
r_{\mathrm{row}}=fA.
\]

把对应列向量写成

\[
r_{\mathrm{col}}=A^{\mathsf T}f_{\mathrm{col}}.
\]

主动旋转后

\[
r'_{\mathrm{col}}
=R A^{\mathsf T}f_{\mathrm{col}}.
\]

转置：

\[
r'_{\mathrm{row}}
=f_{\mathrm{row}}AR^{\mathsf T}.
\]

故

\[
A'=AR^{\mathsf T}.
\]

这同时保证每一行晶格矢量 \(a_\mu\) 的列形式变为 \(Ra_\mu\)。

## 6. 向量与二阶张量

对极向量

\[
u'=Qu,\qquad v'=Qv.
\]

外积

\[
T=uv^{\mathsf T}
\]

变为

\[
T'=u'v'^{\mathsf T}
=Quv^{\mathsf T}Q^{\mathsf T}
=QTQ^{\mathsf T}.
\]

迹不变：

\[
\operatorname{tr}(T')
=\operatorname{tr}(QTQ^{\mathsf T})
=\operatorname{tr}(Q^{\mathsf T}QT)
=\operatorname{tr}(T).
\]

Frobenius 范数不变：

\[
\begin{aligned}
\lVert T'\rVert_F^2
&=\operatorname{tr}(T'^{\mathsf T}T')\\
&=\operatorname{tr}(QT^{\mathsf T}Q^{\mathsf T}QTQ^{\mathsf T})\\
&=\operatorname{tr}(QT^{\mathsf T}TQ^{\mathsf T})\\
&=\operatorname{tr}(T^{\mathsf T}T).
\end{aligned}
\]

## 7. 叉积与宇称

Levi--Civita 张量满足

\[
\varepsilon_{abc}Q_{bj}Q_{ck}
=\det(Q)Q_{ai}\varepsilon_{ijk}.
\]

因此

\[
\begin{aligned}
[(Qu)\times(Qv)]_a
&=\varepsilon_{abc}Q_{bj}u_jQ_{ck}v_k\\
&=\det(Q)Q_{ai}\varepsilon_{ijk}u_jv_k\\
&=[\det(Q)Q(u\times v)]_a.
\end{aligned}
\]

当 \(\det Q=-1\) 时，多出的符号说明叉积是轴向量。标量三重积

\[
\chi=u\cdot(v\times w)
\]

满足

\[
\chi'=\det(Q)\chi.
\]

## 8. 周期边位移

行形式边位移

\[
d_{ijn,\mathrm{row}}
=(f_j+n-f_i)A.
\]

主动旋转只替换

\[
A'=AR^{\mathsf T},
\]

故

\[
d'_{ijn,\mathrm{row}}
=(f_j+n-f_i)AR^{\mathsf T}
=d_{ijn,\mathrm{row}}R^{\mathsf T}.
\]

由于 \(f_i,f_j,n\) 未变，完整键 \((i,j,n)\) 未变。正交性给出

\[
\lVert d'_{ijn}\rVert_2=\lVert d_{ijn}\rVert_2.
\]

若实现旋转时更换 \(n\)，它执行的是另一个离散边变换，不再是本推导的纯空间旋转。

## 9. 完整解析数值例与定量失败例

取

\[
R=
\begin{pmatrix}
0&-1&0\\
1&0&0\\
0&0&1
\end{pmatrix},
\quad
u=(1,2,-1)^{\mathsf T},
\quad
v=(2,-1,3)^{\mathsf T}.
\]

逐步作用得到

\[
Ru=(-2,1,-1)^{\mathsf T},
\qquad
Rv=(1,2,3)^{\mathsf T}.
\]

点积的两条计算链为

\[
u^{\mathsf T}v=-3,
\qquad
(Ru)^{\mathsf T}(Rv)=-3.
\]

距离回归锚点必须直接复算平方而非复用结论：

\[
u-v=(-1,3,-4)^{\mathsf T},
\qquad
\lVert u-v\rVert_2^2=1+9+16=26,
\]

\[
Ru-Rv=(-3,-1,-4)^{\mathsf T},
\qquad
\lVert Ru-Rv\rVert_2^2=9+1+16=26.
\]

故正确距离为 \(\sqrt{26}\)，正确不变关系的归一化残差在精确算术中为 0。

定量失败例取 \(x=(1,2,4)^{\mathsf T}\) 和 \(R_z(\pi/3)\)。正确主动目标 \(a=R_z(\pi/3)x\)，错误转置结果 \(b=R_z(\pi/3)^{\mathsf T}x\)。两者范数均为 \(\sqrt{21}\)，但

\[
\lVert a-b\rVert_2=\sqrt{15},
\qquad
\rho(a,b)=\frac{\sqrt{15}}{\sqrt{21}}
=\sqrt{\frac57}
\approx0.8451542547.
\]

该残差远大于定向错误下界 \(10^{-4}\)，因此同时提供解析失败证据和可执行数值锚点。

## 10. 归一化残差

定义

\[
\rho(A,B)
=\frac{\lVert A-B\rVert_F}
{\max(1,\lVert A\rVert_F,\lVert B\rVert_F)}.
\]

该量无量纲，并满足：

- 若 \(A=B\)，则 \(\rho=0\)；
- 若同时缩放 \(A,B\) 且范数大于 1，残差近似尺度不变；
- 若两者均很小，分母固定为 1，避免除以近零；
- NaN 或无穷输入必须在计算前拒绝，不能依赖比较表达式自然失败。

设数值算法由 \(k\) 次稳定矩阵乘加构成，单位舍入误差为 \(u\)。在条件良好且没有灾难性消去时，预期残差通常为 \(O(ku)\)，但这不是严格统一上界；具体阈值必须通过 dtype、运算规模和冻结夹具验证。阶段 E 固定：

\[
\tau_{64}=5\times10^{-12},
\qquad
\tau_{32}=5\times10^{-6}.
\]

阈值远高于单次机器 epsilon，以容纳多次 contraction，又远低于定向错误下界 \(10^{-4}\)。

## 11. 群律和协变测试矩阵

对每个固定 seed 和 dtype：

1. 检查 \(R^{\mathsf T}R\approx I\)；
2. 检查 \(\det R\approx1\)；
3. 检查 \(R^{-1}\approx R^{\mathsf T}\)；
4. 检查 \(D(R_2R_1)\approx D(R_2)D(R_1)\)；
5. 检查 \(F(Rx)\approx D_{\mathrm{out}}(R)F(x)\)；
6. 对反射检查宇称；
7. 对错误转置、错复合顺序、只左乘和错宇称运行强制失败。

必须使用非对称输入。若 \(x=0\)、\(T=\lambda I\) 或两个旋转同轴，某些错误实现会偶然给出零残差。

## 12. D-E01/D-E09 到 T-E 的显式映射与证据边界

| 推导对象 | 本文件完成位置 | 对应自动门控 | 正向对象与强制失败 | 当前证据状态 |
|---|---|---|---|---|
| D-E01 主动/被动、合法旋转、逆与复合 | 第 3、9、11 节，尤其第 3.1—3.2 节 | T-E01 | 主动 \(R_2R_1\)；被动 \(R_2^{\mathsf T}R_1^{\mathsf T}\)；正交性、\(\det R=1\)；对象混用、错误顺序、反射误入 \(SO(3)\) | 主动与被动对象、复合、解析正反例均已给出；A/B 执行见 M7-09 代码说明与定点复核 |
| D-E01 标量、极向量与二阶张量 | 第 3.1—3.2、4、6、9、11 节 | T-E02 | 点积/距离不变、主动 \(v'=Rv\)、被动 \([v]_{new}=R^{\mathsf T}[v]_{old}\)、\(T'=RTR^{\mathsf T}\)；只左乘或对象混用 | 被动回构与失败残差 2、平方距离 26 锚点已给出；自动失败矩阵见 M7-09 代码说明与定点复核 |
| D-E01 轴向量与 \(O(3)\) 宇称 | 第 7、11 节 | T-E07 | \((Qu)\times(Qv)=\det(Q)Q(u\times v)\)；把轴向量按极向量处理 | 解析推导已完成；A/B 与反演执行见 M7-09 代码说明与定点复核 |
| D-E01 周期几何接口 | 第 5、8 节 | T-E02、T-E07 | 保持 \((i,j,n)\)，旋转位移；旋转时改写 shift 必须失败 | 解析关系已完成；与阶段 D schema 的代码联测见 M7-09 代码说明与定点复核 |
| D-E09 残差与 dtype 误差预算 | 第 9—10 节 | T-E10 | 归一化残差、float64/32 阈值、尺度轴；NaN、误差口径或方向错误 | 只完成公式和边界，不宣称扫描已执行 |
| D-E09 规模与成本报告接口 | 本节后半 | T-E10 | A/B 与 144 点网格，MAC/FLOP、聚合、逐数组/total/peak、wall-time 分离 | 完整对象在统一约定中冻结；M7-08 汇总完整推导，实现和执行证据见 M7-09 代码说明与定点复核 |

旋转样本数增加提高随机覆盖率，但不改变单次群作用的数学定义。通道数增加会改变 contraction 数量和舍入累积。输入尺度可暴露绝对/相对残差混用。三者应按工作包冻结网格扫描，但本文件没有执行该扫描。

成本报告至少区分：

- 由 shape 直接复算的 MAC/FLOP；
- 命名数组的 dtype、shape、逐数组 nbytes、total 和参考 peak；
- 与确定性摘要分离的可选 wall-time；
- 数学残差与模型拟合误差。

不得用一次 wall-time、单个随机旋转或一个标量不变量替代完整等变门控。

## 13. 可独立复算的不变量

- \(R_z(\pi/2)e_x=e_y\)，而 \(R_z(\pi/2)^{\mathsf T}e_x=-e_y\)；
- 被动换基 \(E_1=R_z(\pi/2)\) 时，同一物理向量 \(e_x\) 的新坐标为 \(-e_y\)，且 \(E_1(-e_y)=e_x\)；把该坐标式误作主动旋转的归一化残差为 2；
- 行晶格主动旋转为 \(A'=AR^{\mathsf T}\)；
- 第 9 节冻结输入的距离平方在旋转前后均为 26，距离为 \(\sqrt{26}\)；
- \((Qu)\times(Qv)=\det(Q)Q(u\times v)\)；
- \(T'=QTQ^{\mathsf T}\) 保持迹和 Frobenius 范数；
- 周期旋转保持 \((i,j,n)\) 并把列位移变为 \(Rd\)；
- float64/32 协变阈值分别为 \(5\times10^{-12}\)、\(5\times10^{-6}\)；
- 定向错误夹具残差不得低于 \(10^{-4}\)。
