# 阶段 E 综合问题：参考解答

本解答与 C-E01—C-E12 一一对应。长数组的规范序列化值由[阶段 E 合成代码](../../../../05_code_exercises/stageE_synthetic_equivariance/stagee_models.py)生成，并以完整 SHA-256 锚定；公式、shape、basis、身份和失败机制仍在正文中明确给出，不能用 hash 代替语义核验。

## A-E01 主动/被动与群复合

主动作用给出

\[
r_1=R_1r=(-2,1,3)^\mathsf T,
\qquad
r_2=R_2r_1=(-2,-3,1)^\mathsf T,
\]

且

\[
R_2R_1=
\begin{pmatrix}
0&-1&0\\0&0&-1\\1&0&0
\end{pmatrix}.
\]

任意不可约表示必须满足 \(D^{(\ell)}(R_2R_1)=D^{(\ell)}(R_2)D^{(\ell)}(R_1)\)。若只是将坐标轴被动旋转 \(R_1\)，同一物理向量的新分量为

\[
r_{\mathrm{new}}=R_1^\mathsf Tr=(2,-1,3)^\mathsf T.
\]

错误顺序得到 \(R_1R_2r=(3,1,2)^\mathsf T\)，错误转置得到 \((2,-1,3)^\mathsf T\)。正交性只说明长度保持，不说明两个非交换旋转的先后相同，也不允许把被动分量变化当作主动对象变化。

## A-E02 标量、极向量、轴向量与二阶张量

由于 \(\det Q=-1\)，极向量和轴向量分别满足

\[
v'=Qv=(-1,2,3)^\mathsf T,
\qquad
a'=(\det Q)Qa=(4,-5,-6)^\mathsf T.
\]

对由一个 polar 与一个 axial 构成的二阶对象，\(T'=v'a'^\mathsf T=(\det Q)QTQ^\mathsf T\)，所以它是奇宇称的 rank-2 对象。偶标量保持 \(s_+'=2\)，伪标量变为 \(s_-'=3\)。轨道型表示的宇称为 \((-1)^\ell\)，但 polar/axial 的区别不能只由 \(SO(3)\) 三维矩阵判断。

\(v\cdot a\) 是伪标量；两个 polar 向量的叉积是 axial；`1+s_-` 没有确定宇称，不能作为单一 \((0,+)\) 门值。偶标量本身以及由同宇称对象形成的偶标量组合可用于保持目标通道宇称的门控。对所有 \(R\in SO(3)\)，\(\det R=+1\)，polar 与 axial 都按 \(R\) 变换，因此必须加入 \(\det Q=-1\) 的测试才能区分。

## A-E03 从 STF 基构造实 \(s,p,d\) 表

对题面 \(R_1\)，按冻结 d 基顺序得到

\[
D^d(R_1)=
\begin{pmatrix}
-1&0&0&0&0\\
0&0&1&0&0\\
0&-1&0&0&0\\
0&0&0&-1&0\\
0&0&0&0&1
\end{pmatrix}.
\]

每一列都是 \(RB_bR^\mathsf T\) 在正交归一 STF 基上的坐标，因此列正交且范数为 1，直接得到 \((D^d)^\mathsf TD^d=I_5\)。对题面 \(R_2\)，独立计算后矩阵乘积为

\[
D^d(R_2R_1)=
\begin{pmatrix}
0&1&0&0&0\\
0&0&-1&0&0\\
-1&0&0&0&0\\
0&0&0&-1/2&-\sqrt3/2\\
0&0&0&\sqrt3/2&-1/2
\end{pmatrix},
\]

与 \(D^d(R_2)D^d(R_1)\) 一致。\(D^s=1\)，\(D^p=R\)。若只删去 \(B_{xy}\) 的 \(1/\sqrt2\)，基不再 Frobenius 正交归一；使用普通转置作为坐标回收时，d 表正交性和一般旋转群律检查将失败。若改用 Gram 度量可形成另一套非正交坐标，但那已不是题面冻结表示。

## A-E04 复球谐、Wigner 表示与复—实桥

定义方向是 \(c_{\mathrm c}=K_\ell c_{\mathrm r}\)。按行 \(m=-\ell,\ldots,+\ell\)、列为冻结实基，\(K_1\) 为

\[
K_1=\begin{pmatrix}
1/\sqrt2&i/\sqrt2&0\\
0&0&1\\
-1/\sqrt2&i/\sqrt2&0
\end{pmatrix}.
\]

\(K_2\) 由题面五条 \(Y_{2m}\) 恒等式逐行读取。二者满足 \(K_\ell K_\ell^\dagger=I\)，规范 payload hash 分别为

```text
K1 347e352605a3f4f3ccb078b6cedf5c755fdc6aa3527ea41a8ea3e93d076972a2
K2 5e783d9cdfe025238977f9e92d64d8b46e9a0e79eb8c9deba1af116aaafc7b82
```

coefficient 表示满足

\[
D_{\mathrm c}^{(\ell)}(R)=K_\ell D_{\mathrm r}^{(\ell)}(R)K_\ell^\dagger,
\qquad c'_{\mathrm c}=D_{\mathrm c}^{(\ell)}c_{\mathrm c}.
\]

函数点值来自 \((U(R)f)(\hat r)=f(R^{-1}\hat r)\)，其数组若按固定空间点采样，变换涉及自变量回拉；不能因为 component 数相同就直接送入 coefficient CG。只翻 \(m=+1\) 的局部相位而不同步 K、Wigner 表和下游 CG，会破坏相似变换或规范 payload；把点值数组当 coefficient 则在一般轴旋转下破坏 intertwiner。T-E04/T-E08 分别对这两类错误给出超过阈值的定向残差。

## A-E05 CG 耦合与相位自由

规范系数由

\[
C^{LM}_{\ell_1m_1,\ell_2m_2}
=(-1)^{\ell_1-\ell_2+M}\sqrt{2L+1}
\begin{pmatrix}\ell_1&\ell_2&L\\m_1&m_2&-M\end{pmatrix}
\]

生成，输入按 \((m_1,m_2)\) 字典序，输出按 \(L=0,1,2\) 且每通道 \(M=-L,\ldots,L\) 排列。非零项满足 \(M=m_1+m_2\)，完整 \(9\times9\) 耦合矩阵正交，且对一般轴满足

\[
C\,[D^{(1)}(R)\otimes D^{(1)}(R)]
=\bigoplus_{L=0}^2D^{(L)}(R)\,C.
\]

三个锚点分别为 \(+1/\sqrt3,+1/\sqrt2,+1\)，1×1/1×2 规范全表 SHA-256 为 `fd40673f73059974962cf9b8b3c9152b9af1bd28bb87028b9e4bffe797fd1a04`。

整个 \(L=0\) 通道乘 \(-1\) 并同步改变输出 basis 后，正交性与 intertwiner 都保持，只是项目规范表 hash 不再相同。只翻 \(L=1,M=0\) 行会破坏同一不可约通道的一般轴 intertwiner；只翻一个非零系数通常同时破坏正交性和 intertwiner。交换输入需要乘 \((-1)^{\ell_1+\ell_2-L}\)。\(1\otimes2\) 允许 \(L=1,2,3\)。

## A-E06 Hamiltonian 子块、左右作用与维度

行分块为 receiver 的 s 行 `[0:1]` 与 p 行 `[1:4]`，列分块为 sender 的 p 列 `[0:3]` 与 d 列 `[3:8]`：

- \(s-p\) 为 \(1\times3\)；
- \(s-d\) 为 \(1\times5\)（题面虽主要要求四类，完整 4×8 块自然包含此块）；
- \(p-p\) 为 \(3\times3\)；
- \(p-d\) 为 \(3\times5\)；
- 若 receiver 也含 d，\(d-d\) 为 \(5\times5\)。

表示矩阵为

\[
D_i=1\oplus D^p\in\mathbb R^{4\times4},
\qquad
D_j=D^p\oplus D^d\in\mathbb R^{8\times8},
\]

唯一协变式是 \(H'=D_iHD_j^\dagger\)，输出仍为 \(4\times8\)。在实基中 \(\dagger=\mathsf T\)。左右矩阵均正交/幺正，所以 \(H'\) 与 \(H\) 的奇异值相同；反向不成立，奇异值相同不能确定元素身份。`D_iH`、`HD_j^\mathsf T` 和 `D_iHD_j` 均保持合法 4×8 shape，但一般轴下与正确目标的归一化残差超过 \(10^{-4}\)。

## A-E07 Hermiticity、逆边与完整身份

正向 payload 和 hash 为

```text
["stageD-edge-v1","stageE-H",0,1,0,0,0]
1a8d2a609fbe3cc7c5e9de863375420544fc64f1887b2f1df26d5defd9b2a4a8
```

逆边交换端点、取反 shift；本题 shift 为零，因此数值仍为 `(0,0,0)`，但 row 和 edge ID 必须独立：

```text
["stageD-edge-v1","stageE-H",1,0,0,0,0]
88c94d43c0833d689aacac098a0709e61e08e83f598ec3c26ea91534b8b99bf4
```

逆块为 \(H_{10}=H_{01}^\dagger\in\mathbb R^{8\times4}\)。主动旋转保持 structure ID、receiver、sender、shift、payload、edge ID、mask 和轨道离散身份不变；笛卡尔方向、表示型特征和 block 数值按各自表示同步改变。

必须拒绝：将任意 JSON 重哈希后冒充规范 payload；payload 内端点与 row 端点不一致；shift 漂移；receiver/sender 轨道顺序与 block 行列不一致；逆边复用正向 row/ID；逆块漏转置或复基中漏共轭；mask 与 block shape 不同。hash 只证明某字节串的摘要自洽，奇异值只证明双侧幺正不变量；二者都不证明字节串是规范身份或行列属于正确轨道。

## A-E08 等变消息层与失败非线性

输入和 filter 均为 \((1,-)\)。张量积允许

\[
(1,-)\otimes(1,-)\to(0,+)\oplus(1,+)\oplus(2,+).
\]

若节点数为 \(N\)、边数为 \(E\)、输入 multiplicity 为 \(\mu\)，可记录为：节点 coefficient `[N,3,mu]`，边 filter `[E,3]`，耦合后各 \(L\) 消息 `[E,2L+1,mu]`，receiver 求和后 `[N,2L+1,mu]`，同型混合只改变最后的 multiplicity 轴，不混合不同 \(L,p\)。代码 provenance 必须同时冻结 `input_irrep=[1,-1]`、`filter_irrep=[1,-1]` 和 `output_irreps_with_parity=[[0,1],[1,1],[2,1]]`；实际轴序仍应从 provenance 与函数 contract 填入追踪表，不能只靠符号 shape 猜测。

CG intertwiner 保证每条消息按输出 \(D^{(L)}\) 变换；receiver sum 是线性的，并且旋转不改变离散 receiver 映射，因此聚合保持等变。标量非线性只作用于 \(L=0\)；偶标量门值乘高阶通道保持其 \((L,p)\)；高阶 coefficient 逐分量平方一般不与 \(D^{(L)}\) 交换。

direction 是 edge row 的物理几何，必须与 edge ID、filter payload、m 顺序、输入/filter/output 宇称和 CG 元数据共同进入 provenance。空间反演时输入与 filter 各乘 \(-1\)，乘积为 \(+1\)，所以 \(L=0,1,2\) 三个输出都为偶宇称；若把任一输出元数据伪造为奇宇称，则对单位归一化非零输出，正确值 \(y\) 与错误期望 \(-y\) 的归一化残差为 2。取反、滚动行、错误 parity、错误 CG hash 或 output-irrep 顺序都会使同一离散行读取错误表示对象；T-E07/T-E08 及 provenance validator 必须在 contraction 前拒绝或使反演检查失败。

## A-E09 局部架、退化拒绝与不连续

对 \(u=e_x,v=e_y\)，冻结右手架为 \(F=(e_x,e_y,e_z)=I\)。若 receiver/sender 局部表示矩阵分别为 \(U_i,U_j\)，局部块和推出为

\[
H_{\mathrm{loc}}=U_i^\dagger H U_j,
\qquad
H=U_iH_{\mathrm{loc}}U_j^\dagger.
\]

两端轨道内容不同，所以 \(U_i\) 为 4×4、\(U_j\) 为 8×8 的相应壳层块对角表示，不能用同一个 3×3 架直接左右乘 4×8 块。

零长度度量分别为 \(\zeta_u=\|u\|/s\)、\(\zeta_v=\|v\|/s\)。两者通过后才定义 \(\widehat u=u/\|u\|\)、\(\widehat v=v/\|v\|\) 和无量纲角退化度

\[
\eta=\|\widehat u\times\widehat v\|_2.
\]

float64 的拒绝条件为任一 \(\zeta\le10^{-12}\) 或 \(\eta\le10^{-8}\)；float32 为任一 \(\zeta\le10^{-5}\) 或 \(\eta\le10^{-4}\)。等号在拒绝侧。对题面幅值反例，\(\eta\approx7.5\times10^{-9}\)，应拒绝；未归一化投影长度为 \(1.5\times10^{-8}\)，若据此接受就错误地让共线判据依赖 \(v\) 的幅值。

固定后备轴会在“选哪个轴”的边界产生非协变或不连续分支，且隐藏输入本来未定义架的事实。取 \(\tau\) 为对应 frame threshold，\(v_+\) 与 \(v_-\) 的第二轴分别趋向 \(+e_y\) 与 \(-e_y\)，第三轴也随之翻转；两个架的 Frobenius 跳变趋近 \(2\sqrt2\)，相应回拉块可出现非消失跳变。T-E09 要求记录该正负极限反例。

## A-E10 精度、144 点扫描与成本

扫描轴为 dtype 2 种、seed 2 种、旋转数 4 种、multiplicity 倍率 3 种和尺度 3 种，总数 \(2\times2\times4\times3\times3=144\)。seed 只选择冻结图 G_A/G_B 及 edge identity；其余轴不能重建或改变图。

| 图 | MAC/rotation | aggregate add/rotation | array total bytes | reference peak bytes | contraction FLOP/rotation |
|---|---:|---:|---:|---:|---:|
| G_A | 168 | 52 | 2728 | 2280 | 336 |
| G_B | 378 | 143 | 5584 | 4576 | 756 |

规范结果为：最大残差 `1.9468769400071583e-07`；最坏 case `float32-s20260809-r257-m1-a1e+03`；rotation 189；ell 2；case digest `5317a387bfb026e53dceb31a85074d52ff520448c2fbac9649cb8013064cca7e`。

`float64` 的 \(10^{-6}>5\times10^{-12}\)，必须失败；`float32` 恰为 \(5\times10^{-6}\) 时按冻结“等号接受”规则通过。total 是所有列出数组完整物化的字节和，reference peak 是冻结流式调度的参考峰值；RSS 还含解释器与库，wall-time 受硬件和负载影响。规范 hash 包含确定性 case、残差、成本与数组摘要，不包含 wall-time benchmark。

## A-E11 自旋、时间反演与适用条件

冻结实轨道无自旋对象有 \(\Theta=K\)，故 \(\Theta^2=+I\)。spin-1/2 使用

\[
J_s=i\sigma_y=\begin{pmatrix}0&1\\-1&0\end{pmatrix},
\qquad \Theta=J_sK,
\qquad J_sJ_s^*=-I,
\]

所以 \(\Theta^2=-I\)。复轨道 coefficient 基中

\[
(J_\ell)_{m',m}=(-1)^m\delta_{m',-m},
\qquad J_\ell J_\ell^*=I,
\]

orbital×spin 的 unitary part 为 \(J_\ell\otimes J_s\)，平方为 \(-I\)。spinor 在 \(2\pi\) 旋转下得 \(-I\)，在 \(4\pi\) 下回到 \(+I\)。

时间反演要求独立保存并核验

\[
H(-k)=JH(k)^*J^\dagger,
\qquad
S(-k)=JS(k)^*J^\dagger,
\]

包括 partner ID、map、mask、轨道行和 provenance。只有在 TRIM，即 \(k\equiv-k+G\)，且体系保持时间反演、\(S\succ0\) 并使用正确广义本征问题时，\(\Theta^2=-I\) 才给出同一 k 的 Kramers 成对。一般 k 只能连接不同 partner；漏 `*` 破坏反线性；Zeeman 项在时间反演下变号，是预期破缺对照而不是通过样例。

## A-E12 端到端审计与授权边界

以正向 Hamiltonian 块第 `(px,dxy)` 分量为例，一份合格追踪如下：

| 环节 | 冻结记录 |
|---|---|
| 来源 | 第 15—20 章；D-E01—D-E09；统一表示约定 |
| 几何 | 主动 \(R\in SO(3)\)，先后顺序固定；反演另记 \(\det Q=-1\) |
| receiver 表示 | `s0,p0`，\((0,+)\oplus(1,-)\)，实基 `(s,px,py,pz)` |
| sender 表示 | `p0,d0`，\((1,-)\oplus(2,+)\)，实基冻结八轨道顺序 |
| 边身份 | `stageE-H,0,1,(0,0,0)`；payload/hash 为 A-E07 正向值 |
| 消息 provenance | direction/filter/CG table/output irreps 与同一 edge row 绑定 |
| block | float `[4,8]`；该分量是行 `px`、列 `dxy`；全 true mask |
| 协变 | \(H'=D_iHD_j^\dagger\)，按 dtype 阈值比较归一化残差 |
| 反证 | 只左乘、伪 payload 重哈希、direction 行滚动和漏共轭均实际失败 |
| 自动证据 | T-E01—T-E12 全通过；17/17 unittest；A/B/scan 字节确定；63/63 拒绝 |
| padding | NaN、0、\(10^{300}\) inactive 三探针活动输出和 loss 残差为 0；active NaN 拒绝 |
| 边界 | 只支持冻结合成表示、身份与 schema 契约 |
| 授权 | material/backend/DeepH object/budget/advanced physics 均为 `UNRESOLVED_M8` |

17 项 unittest 验证实现层回归；A/B/scan 双次 stdout 相同验证冻结输入下的字节确定性；144 点扫描覆盖 dtype/seed/旋转数/multiplicity/尺度组合；63/63 证明列出的 validator 故障实际拒绝；三种 padding 探针证明 inactive 数据在 contraction 前被切除。它们仍不能证明 DeepH/e3nn 安装、正式 Hamiltonian 标签、真实材料泛化、DFT 后端、实践 cutoff、真实训练成本或高级物理范围。

M8 前不得填写计算资源、DFT/数据后端、DeepH 软件对象、首个材料、训练/时间预算或高级物理范围。M8 集中冻结这些方案后，开始 M9 的正式安装、数据下载或复现实验前仍须用户再次明确授权。

## 13. 复现证据

固定环境与命令见[代码说明](../../../../05_code_exercises/stageE_synthetic_equivariance/README.md)。当前送审规范 stdout SHA-256 为：

```text
A    6a656a18bbfef042cbcd3049278c15fd0644f4b593d06e44a2b63c5fc78be856
B    b9e4ca3de9e671f4f9b674e40b5f62068f3a91e6ba886d4640d3b90aa6fd82d1
scan c13944029e29ef6b47919646952a5d9bdf6a018cee3f101429fab09967982a81
```

这些 hash 必须由真实子进程 stdout 重算，不能从文档抄录后视为执行证据。材料门控还需对本问题、本解答、[自学导航](../../../../03_textbook/chapters/stageE_self_study_guide.md)和[表示追踪模板](../../../../03_textbook/stageE_representation_trace_template.md)计算 SHA-256，并交由独立子 agent 审计。
