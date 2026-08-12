# 第 19 章 等变图网络与 Hamiltonian 轨道块

本章把第 15—18 章的群作用、实/复 \(s,p,d\) 表、球谐和 CG intertwiner 接到阶段 D 的周期有向多重图，形成最小等变消息层和 Hamiltonian 轨道块输出合同。目标不是复刻某个软件 API，而是使每一层的表示类型、离散身份、矩阵左右作用和失败判据均可独立复算。

本章只使用解析矩阵和合成图。DeepH-E3 论文用于限定论文级任务联系，不授权安装 DeepH/e3nn、下载正式数据、生成 DFT 标签或选择材料、后端和软件版本。

## 19.1 从普通 MPNN 到表示型消息

### 19.1.1 阶段 D 普通标量特征的能力边界

阶段 D 的普通 MPNN 以标量节点/边特征、共享消息函数和 receiver 求和验证节点置换等变性。若所有连续特征都按 \((0,+1)\) 处理，它能表达旋转不变量，但不能仅凭“使用三维坐标”自动输出按 \(p,d\) 轨道基旋转的张量。

Hamiltonian 块在主动旋转下满足

\[
H_{ij}(RX)=D_i(R)H_{ij}(X)D_j(R)^\dagger.
\]

这要求输出同时携带左、右轨道表示。仅训练旋转增强数据、仅让标量损失变小或仅验证节点置换，都不能推出该协变式。

### 19.1.2 节点/边特征的 \((\ell,p)\)、multiplicity 和 shape

固定类型 \((\ell,p)\) 的节点特征写为

\[
x_i^{(\ell,p)}
\in\mathbb F^{n_{\ell,p}\times(2\ell+1)},
\]

其中 \(\mathbb F=\mathbb R\) 或 \(\mathbb C\) 由基约定决定，\(n_{\ell,p}\) 是 multiplicity。旋转作用于最后的 component 轴：

\[
x_i'^{(\ell,p)}
=x_i^{(\ell,p)}D^{(\ell)}(R)^{\mathsf T}
\]

（数组按 multiplicity 行存储），等价的列向量写法为 \(x'_{\mu}=D^{(\ell)}x_\mu\)。

边方向球谐的类型为 \((\ell_f,(-1)^{\ell_f})\)。边还携带标量距离、完整离散键、receiver/sender、周期 shift、mask 和 provenance。shape 相同但 \((\ell,p)\)、component 顺序或 edge-row 不同的数组不能相加。

### 19.1.3 平移、旋转、反演和节点置换的不同作用

- 全局平移不改变相对位移、距离或表示型内部 component；
- 主动旋转使笛卡尔位移按 \(d_{\mathrm{col}}'=Rd_{\mathrm{col}}\) 变换，并使 \((\ell,p)\) component 按 \(D^{(\ell)}\) 变换；
- 反演使方向变号，并按显式宇称 \(p\) 作用；
- 节点置换重排节点轴、receiver/sender 和输出索引，但不作用于 component 基；
- 旋转与反演不得改变 structure ID、端点、整数 shift 或完整 edge key。

这些作用可复合但不可互相替代。尤其 \(SO(3)\) 通过不能证明 \(O(3)\) 宇称正确，节点置换通过也不能证明轨道 component 作用正确。

## 19.2 最小等变消息层

### 19.2.1 径向标量函数

阶段 D 周期边

\[
e=(i,j,n)
\]

中 \(i\) 是 receiver，\(j\) 是 sender，位移为

\[
d_{ijn}=(f_j+n-f_i)A,
\qquad
r_{ijn}=\lVert d_{ijn}\rVert_2.
\]

径向权重只依赖 \(r\) 和其他已声明偶标量：

\[
w_{\alpha}(r):(0,+1).
\]

它在旋转和反演下不变。若门值携带伪标量宇称，必须按第 18 章更新输出类型，不能继续称为径向偶标量。

### 19.2.2 单位边方向的球谐

对非零边定义列方向

\[
\widehat d_{ijn}
=\frac{d_{ijn}^{\mathsf T}}{r_{ijn}}.
\]

方向必须通过第 17 章单向量无量纲合同：显式有限正尺度 \(s\)，

\[
\zeta_d=\lVert d\rVert_2/s,
\]

float64/32 分别在 \(\zeta_d\le10^{-12}\)/\(10^{-5}\) 时拒绝，等号拒绝。不得给零方向任意填轴。

先把复球谐函数点值记为

\[
y^{\mathrm{pv}}_{\ell}(\widehat d)
\in\mathbb C^{2\ell+1},
\]

其中 component 按 \(m=-\ell,\ldots,\ell\) 升序排列。点值满足

\[
y^{\mathrm{pv}}_{\ell}(R\widehat d)
=D^{(\ell)}(R)^*y^{\mathrm{pv}}_{\ell}(\widehat d).
\]

规范 CG 的输入轴是 coefficient 表示，不是函数点值表示。本章因此显式定义边 coefficient filter

\[
\boxed{
z^{\mathrm{cf}}_{\ell}(\widehat d)
=\overline{y^{\mathrm{pv}}_{\ell}(\widehat d)}
},
\qquad
z^{\mathrm{cf}}_{\ell}(R\widehat d)
=D^{(\ell)}(R)z^{\mathrm{cf}}_{\ell}(\widehat d).
\]

它的 shape 为 \((2\ell+1,)\)、dtype 为 `complex128` 或 `complex64`、宇称为 \((-1)^\ell\)，basis family 为 `dlmf-cs-pointvalue-conjugate`。component 顺序、dtype 和 edge 行都不得在共轭时改变。版本为 `stageE-edge-filter-v1`；规范 UTF-8/无空白 JSON payload 与 SHA-256 为：

| \(\ell\) | payload | SHA-256 |
|---:|---|---|
| 0 | `["stageE-edge-filter-v1","dlmf-cs-pointvalue-conjugate",0,[0],"complex","z=conjugate(y)"]` | `549A79B3656BAA8736315F6D12F195013301C0FCDFE97BFDF3C73ECD85F58692` |
| 1 | `["stageE-edge-filter-v1","dlmf-cs-pointvalue-conjugate",1,[-1,0,1],"complex","z=conjugate(y)"]` | `55144ADBD95056208733AB51FF2EFB16789A95A855234641A4521C41FB577D06` |
| 2 | `["stageE-edge-filter-v1","dlmf-cs-pointvalue-conjugate",2,[-2,-1,0,1,2],"complex","z=conjugate(y)"]` | `1A940F1CDCBC62B99BA56D6AA5E50619FB96C85FB0DDCC86913405CBACA97295` |

每个 \(z^{\mathrm{cf}}_{e,\ell m}\) 必须携带原 edge row、完整 edge key/ID、方向定义、\(\ell\)、basis family、版本和对应 hash。实笛卡尔滤波可以通过冻结的 \(K_\ell\) 变换得到等价实数组，但不得因此省略复点值到 coefficient 的接口。

### 19.2.3 节点特征与边球谐的 CG 张量积

一条输入路径

\[
(\ell_{\mathrm{in}},p_{\mathrm{in}})
\otimes
(\ell_f,p_f)
\to
(L,p_{\mathrm{out}})
\]

要求

\[
|\ell_{\mathrm{in}}-\ell_f|
\le L\le
\ell_{\mathrm{in}}+\ell_f,
\qquad
p_{\mathrm{out}}=p_{\mathrm{in}}p_f.
\]

消息分量为

\[
m_{e,\alpha,LM}
=
w_\alpha(r_e)
\sum_{m,m_f}
C^{LM}_{\ell_{\mathrm{in}}m,\ell_fm_f}
x_{j,\mu m}
z^{\mathrm{cf}}_{e,\ell_fm_f}.
\]

CG 表、输入快轴、相位、component 顺序和路径身份必须使用第 18 章规范。CG contraction 的两个输入现在都按 \(D\) 变换；它只收缩表示 component，不收缩 edge 或 multiplicity 身份。

### 19.2.4 receiver 聚合和同型通道线性混合

对固定输出类型求和：

\[
a_{i,\alpha,LM}
=
\sum_{e:\operatorname{receiver}(e)=i}
m_{e,\alpha,LM}.
\]

求和不混合 component，且在节点置换下与 receiver 重标记相容。随后只能在同一 \((L,p)\) 的 multiplicity 轴线性混合：

\[
h_{i,\nu,LM}
=
\sum_\alpha W_{\nu\alpha}^{(L,p)}a_{i,\alpha,LM}.
\]

权重对所有 \(M\) 共享。空入边的 sum 输出定义为零；若另用 mean/max，必须沿用阶段 D 已冻结的零度处理，不能产生 NaN 或任意哨兵。

### 19.2.5 标量门控与逐层表示契约

类型保持门值必须是偶标量 \(g:(0,+1)\)：

\[
\widetilde h^{(L,p)}=g\,h^{(L,p)}.
\]

伪标量门值会把宇称变为 \(-p\)，普通 \(1+s_-\) 没有确定宇称并必须拒绝。每层输出 schema 至少记录 \((L,p)\)、multiplicity、dtype、shape、component 顺序、edge/node 身份、mask、CG/球谐版本和容差。

## 19.3 逐层等变证明

### 19.3.1 边方向与球谐的协变

旋转不改变 \(r_e\)，所以 \(w(r_e)\) 不变；方向按 \(R\widehat d_e\) 变换。第 17 章给出点值作用 \(y^{\mathrm{pv}}(R\widehat d)=D^*y^{\mathrm{pv}}(\widehat d)\)。逐元素共轭并使用 \(D^*\) 的共轭为 \(D\)，得到

\[
z^{\mathrm{cf}}(R\widehat d)
=\overline{y^{\mathrm{pv}}(R\widehat d)}
=D\,\overline{y^{\mathrm{pv}}(\widehat d)}
=Dz^{\mathrm{cf}}(\widehat d).
\]

周期 shift 是离散晶格坐标，不随笛卡尔旋转改变。若直接把 \(y^{\mathrm{pv}}\) 输入 coefficient CG，第一输入按 \(D\)、第二输入按 \(D^*\)，下一节的 intertwiner 前提不成立。

### 19.3.2 CG intertwiner

第 18 章给出

\[
C(D^{(\ell_{\mathrm{in}})}\otimes D^{(\ell_f)})
=D^{(L)}C.
\]

所以每条合法 CG 路径按输出 \(D^{(L)}\) 变换。这里第二输入明确是 \(z^{\mathrm{cf}}\)，而不是 \(y^{\mathrm{pv}}\)。只满足 \(M=m+m_f\)、只测实基或只测 z 轴都不足以证明一般轴复基等变。

### 19.3.3 求和聚合与节点置换

同一 receiver 的消息共享 \(D^{(L)}\)，故

\[
\sum_eD^{(L)}m_e
=
D^{(L)}\sum_em_e.
\]

节点置换只改变索引名称和边端点；共享消息函数与 sum 聚合给出节点置换等变。若先按纯数值排序并丢失 edge key，再聚合相同 shape 数组，数学求和仍可运行但身份合同已破坏。

### 19.3.4 端到端复合及失败非线性

径向偶标量、球谐、CG intertwiner、同型混合、sum 聚合和偶标量门控逐层等变，因此其复合等变。逐分量高阶非线性一般不与 \(D^{(L)}\) 对易；第 18 章向量平方例给出绝对残差 \(8\)。架构名称、训练增强或少量旋转近似通过不能替代逐层残差。

## 19.4 Hamiltonian 轨道块

### 19.4.1 \(H_{ij}(RX)=D_iH_{ij}(X)D_j^\dagger\)

令原子 \(i,j\) 的轨道系数列分别按

\[
c_i'=D_i(R)c_i,
\qquad
c_j'=D_j(R)c_j
\]

变换。保持双线性矩阵元一致得到

\[
\boxed{
H_{ij}(RX)
=D_i(R)H_{ij}(X)D_j(R)^\dagger
}.
\]

左作用属于 receiver/bra 轨道，右作用属于 sender/ket 轨道。只左乘、左右交换或右侧漏 \(\dagger\) 都是定向错误。

### 19.4.2 \(s-s,s-p,p-p,p-d,d-d\) 的 shape 与左右作用

单壳层块 shape 为：

| block | shape | rotated block |
|---|---:|---|
| \(s-s\) | \(1\times1\) | \(H\) |
| \(s-p\) | \(1\times3\) | \(H D_p^\dagger\) |
| \(p-s\) | \(3\times1\) | \(D_p H\) |
| \(p-p\) | \(3\times3\) | \(D_pHD_p^\dagger\) |
| \(p-d\) | \(3\times5\) | \(D_pHD_d^\dagger\) |
| \(d-d\) | \(5\times5\) | \(D_dHD_d^\dagger\) |

非方块同样有明确左右作用。将 \(s-p\) 当成 \(p-s\) 或靠转置“修 shape”会交换 bra/ket 语义。

### 19.4.3 多壳层块对角表示和轨道顺序

若原子 \(i\) 具有多个 shell/multiplicity，

\[
D_i(R)
=
\bigoplus_{\alpha\in i}D^{(\ell_\alpha)}(R).
\]

轨道顺序必须与阶段 B/D 轨道表、component mask 和 provenance 一致。两个同为 \(p\) 的 shell 是两个 multiplicity 身份，不能因表示矩阵相同而折叠。完整 shell mask 必须全真或全假；padding 在矩阵乘法前切除。

### 19.4.4 实基转置、复基共轭转置与相似变换

实 \(s,p,d\) 表为正交矩阵，右侧使用转置：

\[
H_{\mathrm r}'=D_{i,\mathrm r}H_{\mathrm r}D_{j,\mathrm r}^{\mathsf T}.
\]

复球谐基必须用共轭转置：

\[
H_{\mathrm c}'=D_{i,\mathrm c}H_{\mathrm c}D_{j,\mathrm c}^\dagger.
\]

两基由第 17 章块对角 \(K_i,K_j\) 联系：

\[
H_{\mathrm c}=K_iH_{\mathrm r}K_j^\dagger.
\]

变换 Hamiltonian、表示、mask 和 provenance 必须使用同一 shell-pair 轴映射。只把转置改成共轭而不变基，或只变 \(H\) 不变 \(D\)，都不是合法相似变换。

## 19.5 周期边、Hermiticity 与 provenance

### 19.5.1 完整边键在旋转下保持不变

完整键固定为

\[
(\text{stageD-edge-v1},
\text{structure ID},
i,j,n_x,n_y,n_z).
\]

旋转只作用于笛卡尔位移和表示型特征；structure ID、receiver \(i\)、sender \(j\) 和整数 shift \(n\) 不变。不同周期镜像即使距离相同仍是不同边。

### 19.5.2 逆边、周期 shift 和 Hermitian 共轭

\((i,j,n)\) 的逆边是

\[
(j,i,-n).
\]

对 Hermitian 单粒子算符，

\[
\boxed{
H_{ji,-n}=H_{ij,n}^\dagger
}.
\]

非零位移块不要求自身 Hermitian。旋转后

\[
\begin{aligned}
H_{ji,-n}'&=D_jH_{ji,-n}D_i^\dagger\\
&=D_jH_{ij,n}^\dagger D_i^\dagger\\
&=(D_iH_{ij,n}D_j^\dagger)^\dagger,
\end{aligned}
\]

所以旋转协变与逆边 Hermiticity 相容。缺逆边不能靠事后重厄米化静默掩盖。

### 19.5.3 prediction—mask—轨道身份—边键统一行映射

每条预测行必须共同携带：

- 完整 edge key 与 edge ID；
- block shape、receiver/sender shell/multiplicity；
- 左右局部 component 和实际轨道身份；
- prediction、target（若有）、continuous mask；
- basis family、component 顺序、单位和 schema 版本；
- 旋转/换胞/节点置换的可逆行映射。

任何排序、batch 拼接、逆边生成或基变换都必须同步全部字段。允许 prediction 多一行、几何独立滚动或 provenance 单独排序会使数值无法追溯，即使 loss 仍可计算。

### 19.5.4 concat/padded batch 中的表示维

concat batch 在节点/边轴拼接，并用 graph ID、count 和 offset 定位；表示 component 轴不得拼进 feature/multiplicity 轴。padded batch 对每个 \((\ell,p)\) 使用明确

\[
(B,N_{\max},n_{\ell,p},2\ell+1)
\]

或边级对应 shape，并用 prefix mask 切除 inactive 区。inactive NaN/极大值必须在任何球谐、CG、矩阵乘法或 loss 前切除；active 非有限值必须拒绝。重复 structure ID 可存在于不同 batch 槽位，定位依赖槽位/graph ID 而非假设全局唯一。

## 19.6 局部坐标路线

### 19.6.1 局部架中的不变预测与全局回拉

设 \(F_i,F_j\in SO(3)\) 的列为局部架轴，且在全局旋转下

\[
F_i(RX)=RF_i(X).
\]

令 \(U_i=D_i(F_i)\)。局部块和回拉为

\[
\overline H_{ij}
=U_i^\dagger H_{ij}U_j,
\]

\[
H_{ij}=U_i\overline H_{ij}U_j^\dagger.
\]

若局部预测 \(\overline H_{ij}\) 对全局旋转不变，则 \(U_i'=D_i(R)U_i\)，从而回拉自动给出 \(D_i(R)H_{ij}D_j(R)^\dagger\)。

### 19.6.2 轴选择、符号和取向规则

阶段 E 只接受由两个有限向量 \(u,v\) 和有限正尺度 \(s\) 构造的唯一右手架：

\[
e_1=\widehat u,\quad
\widetilde e_2=\widehat v-(e_1^{\mathsf T}\widehat v)e_1,\quad
e_2=\widetilde e_2/\lVert\widetilde e_2\rVert,\quad
e_3=e_1\times e_2.
\]

不得在退化时选择任意全局后备轴；否则 \(F(RX)=RF(X)\) 可失败。输出必须验证 \(F^{\mathsf T}F=I\)、\(\det F=+1\) 和有限性。

### 19.6.3 零方向、共线与近简并不连续

零长度指标

\[
\zeta_u=\lVert u\rVert/s,\qquad
\zeta_v=\lVert v\rVert/s
\]

在 float64/32 中分别满足 \(\zeta\le10^{-12}\)/\(10^{-5}\) 时拒绝。归一化后

\[
\eta=\lVert\widehat u\times\widehat v\rVert
\]

在 float64/32 中分别满足 \(\eta\le10^{-8}\)/\(10^{-4}\) 时拒绝，等号拒绝。阈值两侧夹具和扰动序列完全沿用统一表示约定，不得事后放宽。

### 19.6.4 局部坐标与显式等变的可比条件

两路线比较必须固定相同图、轨道表、目标块、训练/测试划分、dtype、容差、参数/路径预算、成本口径和下游评价。局部架只在其定义域内有协变保证；显式等变层也仍可能因错误 CG、mask 或身份映射失败。现有来源不足以支持任一路线普遍更准确或更高效。

## 19.7 数值验证和复杂度

### 19.7.1 随机旋转下逐层/端到端残差

每层使用归一化残差

\[
\rho(A,B)
=
\frac{\lVert A-B\rVert_F}
{\max(1,\lVert A\rVert_F,\lVert B\rVert_F)}.
\]

float64/32 阈值分别为 \(5\times10^{-12}\)/\(5\times10^{-6}\)，等号接受。T-E06 比较 Hamiltonian 块、逆边与 provenance；T-E08 比较消息逐层及端到端；T-E09 比较局部架接受域与回拉。

### 19.7.2 float32/64、尺度与通道数扫描

正式 T-E10 使用统一约定的 144 点网格：

\[
\text{dtype}\{64,32\}
\times\text{seed}\{20260809,20260810\}
\times n_R\{1,8,64,257\}
\times m\{1,2,4\}
\times\alpha\{10^{-3},1,10^3\}.
\]

scan mode 与 config A/B 互斥，seed 映射到固定图 \(G_A:(4,8)\)、\(G_B:(7,18)\)，不得观察结果后删点。

### 19.7.3 张量积路径、参数量、FLOP 和激活内存

参数只来自径向/同型 multiplicity 权重，不来自固定 CG 系数。每条路径应从实际 contraction shape 计数 MAC；统一 reference kernel 每 MAC=2 FLOP，receiver 聚合加法另报。数组按名称报告 shape/dtype/nbytes，并区分完整物化 total 与参考流式 peak。complex MAC 必须明确实 FLOP 展开，不能照搬实 kernel 口径。

### 19.7.4 数学等变、浮点误差、拟合误差的分离

数学等变残差检验实现是否遵守表示合同；float dtype 和尺度影响舍入；拟合误差衡量预测与合成 target 的差异。三者必须分字段报告。可选 wall-time 受硬件、线程和调度影响，只能按冻结 warm-up/测量协议单独报告，不能进入确定性 stdout hash。

## 19.8 例题、失败样例与代码门控

### 19.8.1 非对称 \(s,p,d\) 合成 Hamiltonian

取 receiver 含 \(s+p\)（维数 4），sender 含 \(p+d\)（维数 8），构造非方块

\[
H_{ij}\in\mathbb R^{4\times8}.
\]

表示为

\[
D_i=1\oplus R,\qquad
D_j=R\oplus D^d(R),
\]

正确旋转是 \(D_iH_{ij}D_j^{\mathsf T}\)。非对称 shape 可同时暴露左右交换、只左乘和错误转置。固定数值见例题文件与 D-E05。

### 19.8.2 只左乘、漏共轭和轨道错位反例

强制故障至少包括：

- 只计算 \(D_iH\)；
- 复基右侧使用普通转置而非 \(\dagger\)；
- receiver/sender 表示交换；
- 同 shape 的两个 \(p\) shell 行错位；
- 旋转时改变 edge key 或独立排序 provenance；
- 逆边未取共轭转置。

### 19.8.3 高阶逐分量非线性与局部架退化

T-E08 必须在一般轴复基中同时执行 \(z^{\mathrm{cf}}(R\widehat d)=Dz^{\mathrm{cf}}(\widehat d)\) 正例，以及把按 \(D^*\) 变换的 \(y^{\mathrm{pv}}\) 直接送入 coefficient CG 的定向失败；还需注入逐分量高阶非线性。T-E12 拒绝 filter version/hash、\(m\) 顺序、basis family 或 edge-row provenance 错配。T-E09 执行零长度、阈值等号、正/负近共线扰动、任意后备轴和错误回拉方向。只在一个非退化架上成功不能替代退化域合同。

### 19.8.4 D-E05—D-E07/D-E09 与 T-E06/T-E08—T-E10/T-E12

[解析推导](../../../04_derivations/stageE/19_equivariant_graph_hamiltonian.md) 完成 D-E05 Hamiltonian 块、D-E06 最小消息层、D-E07 局部架比较，并登记 D-E09 成本子对象。Q19/A19 提供 10 组配对题解。正式合成代码、A/B、144 点扫描和故障矩阵已由 M7-09 执行，见 [代码说明](../../../05_code_exercises/stageE_synthetic_equivariance/README.md) 与 [定点复核](../../../08_audits/M7_stageE_code_blocking_reaudit.md)。

## 19.9 DeepH-E3 论文接口与授权边界

### 19.9.1 论文级对象映射

DH-02 支持的本章联系限于：目标是局域轨道 Hamiltonian 表示，轨道块在旋转下有确定左右作用，等变方法可把群约束写入模型对象。本章的数组 schema、阈值、合成图、CG hash 和测试故障属于项目教学冻结，不应冒充论文原生接口。

### 19.9.2 不选择软件版本、数据、材料或 DFT 后端

本章不确定 DeepH/DeepH-E3 仓库 commit、e3nn 版本、训练数据格式、DFT 软件、赝势/基组、材料体系、SOC/磁性范围、硬件或训练预算。这些选择集中保留到 M8；M8 冻结后，M9 外部安装/下载/复现实验仍需再次明确授权。

### 19.9.3 章节门控和 M8 保留决策

章节通过要求教材、推导、例题、10 道练习与参考答案、来源定位、严格 Pandoc/MathML、链接/控制字符和独立内容审计均清零。通过只授权继续第 20 章和阶段 E 内部合成材料，不授权 M8/M9 外部动作。

## 19.10 章节小结

最小等变消息层由径向偶标量、复球谐点值的显式 coefficient filter \(z^{\mathrm{cf}}=\overline{y^{\mathrm{pv}}}\)、CG intertwiner、receiver 求和、同型 multiplicity 混合和偶标量门控组成。点值按 \(D^*\) 变换，coefficient filter 按 \(D\) 变换，两者不能直接互换。Hamiltonian 块不是普通标量标签，而按 receiver/bra 左表示和 sender/ket 右共轭表示双侧变换；该关系必须与完整周期边键、逆边 Hermiticity、轨道身份、mask 和 batch 行映射同步。

局部坐标路线可在唯一、协变、右手且非退化的局部架定义域内给出同一全局协变式，但零方向、共线、近简并和任意后备轴会破坏保证。显式等变与局部坐标的比较只有在对象、数据、精度和成本口径相同且分别执行失败门控时才有意义。
