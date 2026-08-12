# 阶段 E 统一表示约定

## 1. 适用范围与优先级

本文件冻结第 15—20 章、D-E01—D-E09、T-E01—T-E12 和阶段 E 综合材料共同使用的旋转、表示、球谐、轨道块与时间反演约定。若引用资料或软件采用其他约定，必须先写出显式变换再比较；不得凭相同符号假定数组语义相同。本文件只约束理论与合成验证，不选择 DeepH/e3nn 软件版本、材料体系、DFT 后端或正式数据对象。

## 2. 几何作用与复合顺序

三维向量均为列向量。主线中的 \(R\in SO(3)\) 是主动正旋转：

\[
\boldsymbol r'=R\boldsymbol r,
\qquad
R^{\mathsf T}R=I,
\qquad
\det R=+1.
\]

先施加 \(R_1\)，再施加 \(R_2\)，总作用为 \(R_2R_1\)。任意表示固定满足

\[
D^{(\ell)}(R_2R_1)
=D^{(\ell)}(R_2)D^{(\ell)}(R_1).
\]

被动坐标变换必须单列为 \(\boldsymbol r_{\mathrm{new}}=R^{\mathsf T}\boldsymbol r_{\mathrm{old}}\)。本文不把被动坐标分量与主动旋转后的物理向量混写。反射或反演属于 \(O(3)\) 而非 \(SO(3)\)，必须同时记录行列式和宇称。

## 3. 函数空间与 Wigner 表示

主动旋转算符定义为

\[
[U(R)f](\widehat{\boldsymbol r})
=f(R^{-1}\widehat{\boldsymbol r}).
\]

复球谐采用 E-FND-01 的 DLMF 归一化与 Condon--Shortley 相位，索引顺序固定为 \(m=-\ell,-\ell+1,\ldots,\ell\)。Wigner 矩阵不依赖某个 Euler 角软件接口，而由下式操作性定义：

\[
U(R)Y_{\ell m}
=\sum_{m'=-\ell}^{\ell}
Y_{\ell m'}D^{(\ell)}_{m'm}(R).
\]

因此球谐展开系数按 \(c'=D^{(\ell)}(R)c\) 变换，且 \(D^{(\ell)}(R)\) 为幺正矩阵。若后续使用 Euler 角公式，必须先验证其轴顺序、内禀/外禀、主动/被动和共轭方向与本定义一致。

## 4. 实 \(s,p,d\) 基与复—实映射

\(s\) 基为一维标量，\(D^{(0)}(R)=1\)。实 \(p\) 基按

\[
(p_x,p_y,p_z)
\]

排序并采用单位球面归一化函数 \(p_a=\sqrt{3/(4\pi)}\,\widehat r_a\)，故

\[
D^{p}(R)=R.
\]

实 \(d\) 基按

\[
(d_{xy},d_{yz},d_{zx},d_{x^2-y^2},d_{3z^2-r^2})
\]

排序。令 \(e_x,e_y,e_z\) 为笛卡尔单位列向量，并定义 Frobenius 正交归一的对称无迹矩阵

\[
\begin{aligned}
B_{xy}&=(e_xe_y^{\mathsf T}+e_ye_x^{\mathsf T})/\sqrt2,\\
B_{yz}&=(e_ye_z^{\mathsf T}+e_ze_y^{\mathsf T})/\sqrt2,\\
B_{zx}&=(e_ze_x^{\mathsf T}+e_xe_z^{\mathsf T})/\sqrt2,\\
B_{x^2-y^2}&=(e_xe_x^{\mathsf T}-e_ye_y^{\mathsf T})/\sqrt2,\\
B_{3z^2-r^2}&=(-e_xe_x^{\mathsf T}-e_ye_y^{\mathsf T}+2e_ze_z^{\mathsf T})/\sqrt6.
\end{aligned}
\]

相应单位球面归一化函数为

\[
d_a(\widehat{\boldsymbol r})
=\sqrt{\frac{15}{8\pi}}
\widehat{\boldsymbol r}^{\mathsf T}B_a\widehat{\boldsymbol r},
\]

实 \(d\) 表由

\[
D^d_{ab}(R)
=\operatorname{tr}\!\left(B_a^{\mathsf T}RB_bR^{\mathsf T}\right)
\]

唯一确定。该矩阵为实正交表示，并满足与 \(R\) 相同的复合顺序。

复—实映射通过下列函数恒等式冻结：

\[
\begin{aligned}
Y_{1,-1}&=(p_x-i p_y)/\sqrt2,
&Y_{1,0}&=p_z,
&Y_{1,1}&=-(p_x+i p_y)/\sqrt2,\\
Y_{2,-2}&=(d_{x^2-y^2}-i d_{xy})/\sqrt2,
&Y_{2,-1}&=(d_{zx}-i d_{yz})/\sqrt2,
&Y_{2,0}&=d_{3z^2-r^2},\\
Y_{2,1}&=-(d_{zx}+i d_{yz})/\sqrt2,
&Y_{2,2}&=(d_{x^2-y^2}+i d_{xy})/\sqrt2.
\end{aligned}
\]

由这些等式构造的复—实矩阵必须逐项验证幺正性，并满足同一旋转在两种基中的相似变换关系。任何不同的实球谐顺序或相位均须显式给出置换—符号矩阵。

## 5. \(O(3)\) 宇称与向量类型

轨道型不可约表示记为 \((\ell,p)\)，其中反演宇称 \(p=(-1)^\ell\)。因此主线的 \(s,p,d\) 轨道宇称依次为 \(+1,-1,+1\)。极向量在反演下变号，轴向量不变；两者虽然在 \(SO(3)\) 下均按三维向量变换，但在 \(O(3)\) 下不是同一表示。等变测试必须分别覆盖正旋转和至少一个行列式为 \(-1\) 的变换，不得用 \(SO(3)\) 通过结果替代宇称检查。

## 6. Clebsch--Gordan 耦合

Clebsch--Gordan 系数采用 E-FND-02 与上述 Condon--Shortley 相位，耦合态定义为

\[
|LM\rangle
=\sum_{m_1,m_2}
C^{LM}_{\ell_1m_1,\ell_2m_2}
|\ell_1m_1\rangle|\ell_2m_2\rangle.
\]

输出通道按 \(L=|\ell_1-\ell_2|,\ldots,\ell_1+\ell_2\) 递增排列，每个通道内 \(M=-L,\ldots,L\)。非零项必须满足 \(M=m_1+m_2\)，且耦合矩阵必须验证正交/幺正与 intertwiner 恒等式。阶段 E 至少显式构造 \(0\otimes\ell\)、\(1\otimes1=0\oplus1\oplus2\) 和 \(1\otimes2=1\oplus2\oplus3\) 中代码实际使用的低阶部分。

每个不可约输出通道都存在整体相位自由：复基中可将整个固定 \(L\) 通道乘以 \(e^{i\phi_L}\)，实基中可整体乘以 \(\pm1\)。只要输出表示基和所有下游映射同步变换，这属于合法基变换，不破坏正交性或 intertwiner，不能被称为数学错误。本项目仍需固定唯一的序列化规范，因此代码中的规范 CG 表必须逐项符合 E-FND-02 的 DLMF/Condon--Shortley 约定；该检查验证“项目规范一致性”，而不是验证等变性本身。

初始 \(1\otimes1\) 表用以下三个非零系数锚定三个输出通道的整体相位：

\[
C^{00}_{1\,1,\,1\,-1}=+\frac1{\sqrt3},
\qquad
C^{11}_{1\,1,\,1\,0}=+\frac1{\sqrt2},
\qquad
C^{22}_{1\,1,\,1\,1}=+1.
\]

规范表测试必须比较全部非零系数、零模式和输入交换关系，而不只比较这三个锚点。整条 \(L\) 通道统一翻相位若没有同步更改规范元数据，应当只在“规范表一致性”检查中失败；只翻转一个非零系数、只翻转部分 \(M\) 行、错换输入轴而不施加 \((-1)^{\ell_1+\ell_2-L}\) 的交换相位，必须在规范表或 intertwiner 检查中失败。

## 7. Hamiltonian 轨道块协变

对结构 \(X\) 及其主动旋转 \(RX\)，原子 \(i,j\) 上分别按 \(D_i(R),D_j(R)\) 变换的轨道基块固定满足

\[
H_{ij}(RX)
=D_i(R)H_{ij}(X)D_j(R)^\dagger.
\]

实基中 \(\dagger\) 退化为转置；复基中必须保留共轭。一个包含多壳层的节点表示使用按冻结轨道顺序组成的块对角 \(D_i(R)\)。Hermiticity、周期逆边关系、完整边键、mask 和轨道 provenance 继续沿用阶段 B/D 契约；旋转不得改变边的离散端点与周期 shift，仅旋转笛卡尔几何并同步更新所有表示型特征。

归一化协变残差统一为

\[
\rho(A,B)
=\frac{\lVert A-B\rVert_F}
{\max(1,\lVert A\rVert_F,\lVert B\rVert_F)}.
\]

## 8. 等变消息与非线性

标量门控、径向函数和同型通道线性混合可以保持表示类型；不同 \((\ell,p)\) 通道的耦合必须通过满足 intertwiner 条件的张量积。逐分量任意非线性一般不对 \(\ell>0\) 等变，因此主线只允许标量非线性或由标量门控高阶通道。架构名称、数据增强或在少量旋转上的近似一致不能替代逐层表示契约和随机群作用测试。

## 9. 局部坐标与显式等变的比较边界

局部坐标法只有在坐标架构造唯一、连续、取向规则完整并与目标块的回拉/推出公式一致时，才可给出协变输出。零长度方向、共线参考向量、近简并本征方向和符号翻转均可能使局部架不定义或不连续。阶段 E 必须给出精确退化拒绝和近退化扰动失败样例；不得把一个非退化案例的成功外推为全域等变证明。

## 10. 自旋与时间反演接口

Pauli 矩阵采用标准 \((m_s=+1/2,-1/2)\) component 顺序：

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

无自旋主线中的 \(\Theta=K\) 明确限定于冻结实轨道基，故 \(\Theta^2=+I\)。在 DLMF-CS 复轨道 coefficient 基、\(m=-\ell,\ldots,\ell\) 升序中，unitary part 固定为

\[
(J_\ell)_{m',m}=(-1)^m\delta_{m',-m},
\qquad
J_\ell J_\ell^*=+I.
\]

若 \(c_{\mathrm c}=K_\ell c_{\mathrm r}\)，则反幺正基变换为

\[
J_{\ell,\mathrm c}
=K_\ell J_{\ell,\mathrm r}K_\ell^{\mathsf T},
\]

不得误写为普通线性算符的共轭相似变换。自旋 \(1/2\) 接口固定

\[
J=i\sigma_y=
\begin{pmatrix}
0&1\\
-1&0
\end{pmatrix},
\qquad
\Theta=JK,
\qquad
\Theta^2=JJ^*=-I.
\]

对时间反演不变的合成自旋 Hamiltonian，接口检查为

\[
H(-\boldsymbol k)=JH(\boldsymbol k)^*J^\dagger.
\]

全局相位不同的时间反演算符物理等价，但代码与材料必须坚持上式的固定 \(J\)。第 20 章只建立 \(SU(2)\)、双值表示、反幺正作用和 Kramers 条件的理论接口；是否把 SOC、磁性或自旋轨道块纳入首个正式实践属于 M8 决策，不由 M7 隐含确定。

规范版本为 `stageE-time-reversal-v1`。spin-half 的无空白 JSON payload

`["stageE-time-reversal-v1","spin-half",[0.5,-0.5],"complex128","J=i*sigma_y",[[[0,0],[1,0]],[[-1,0],[0,0]]]]`

的 SHA-256 为 `F8B5E9591B791A2DBD9B262736718C8B391B75DE6CE720335D1AD5B8F1AFF444`。数学对象 hash、实际 dtype 和运行数组字节 hash 必须分字段记录。时间反演与旋转还必须满足

\[
JD(R)^*J^\dagger=D(R),
\]

并使用相同的 orbital/spin component 顺序和 \(SU(2)\) lift identity。

## 11. 数值精度与失败判据

### 11.1 旋转生成器与 validator

随机旋转由固定种子的四维标准正态向量按 \((w,x,y,z)\) 顺序归一化为单位四元数，再按固定多项式公式转换到 \(SO(3)\)；归一化四维 Gaussian 在 \(S^3\) 上均匀，经过双覆盖给出 Haar \(SO(3)\)。所有输入必须为有限数，旋转矩阵 shape 必须严格为 \((3,3)\)，四元数 shape 必须严格为 \((4,)\)，禁止广播。

令

\[
\epsilon_R=\frac{\lVert R^{\mathsf T}R-I\rVert_F}{\max(1,\lVert I\rVert_F)},
\qquad
\epsilon_{\det}=|\det R-1|,
\qquad
\epsilon_q=\bigl|\lVert q\rVert_2-1\bigr|.
\]

float64 使用 \(\tau_R=\tau_q=5\times10^{-12}\)，float32 使用 \(\tau_R=\tau_q=5\times10^{-6}\)。仅当 \(\epsilon_R\le\tau_R\) 且 \(\epsilon_{\det}\le\tau_R\) 时接受旋转矩阵；仅当 \(\epsilon_q\le\tau_q\) 时接受已归一化四元数，等于阈值时接受。原始 Gaussian 四元数由生成器先检查有限性和非零范数，再归一化；validator 不得静默归一化用户提交的“单位四元数”。

四元数序列化采用唯一符号：令 \(\varepsilon_{\mathrm{pivot}}=32\,\mathrm{eps}(\mathrm{dtype})\)，找到 \((w,x,y,z)\) 中第一个绝对值严格大于 \(\varepsilon_{\mathrm{pivot}}\) 的分量，并令其为正；严格为零的分量统一序列化为正零。单位四元数必有这样的 pivot。边界夹具使用

\[
R_\delta=\operatorname{diag}(1+\delta,1,1),
\qquad
q_\delta=(1+\delta,0,0,0),
\]

分别取 \(\delta=0.4\tau_R,2\tau_R\) 与 \(\delta=0.5\tau_q,2\tau_q\)：前者必须落在接受侧，后者必须落在拒绝侧，并记录 validator 实际计算的残差。NaN、无穷、反射矩阵、零四元数、错误 rank/shape 和 dtype 必须定向拒绝。

### 11.2 局部坐标退化契约

局部架输入为两个有限向量 \(u,v\) 和一个显式、有限、正的特征长度 \(s\)；合成夹具固定 \(s=1\)。先计算

\[
\zeta_u=\frac{\lVert u\rVert_2}{s},
\qquad
\zeta_v=\frac{\lVert v\rVert_2}{s}.
\]

若任一 \(\zeta\le\tau_0\) 则拒绝，其中 float64 的 \(\tau_0=10^{-12}\)，float32 的 \(\tau_0=10^{-5}\)，等于阈值时拒绝。通过零长度检查后先归一化 \(\widehat u,\widehat v\)，再使用无量纲退化指标

\[
\eta=\lVert\widehat u\times\widehat v\rVert_2.
\]

若 \(\eta\le\tau_{\mathrm{frame}}\) 则拒绝；float64 使用 \(\tau_{\mathrm{frame}}=10^{-8}\)，float32 使用 \(\tau_{\mathrm{frame}}=10^{-4}\)，等于阈值时拒绝。接受后唯一构造

\[
e_1=\widehat u,\qquad
\widetilde e_2=\widehat v-(e_1^{\mathsf T}\widehat v)e_1,\qquad
e_2=\frac{\widetilde e_2}{\lVert\widetilde e_2\rVert_2},\qquad
e_3=e_1\times e_2.
\]

阈值夹具固定 \(u=(1,0,0)\)、\(v_\varepsilon=(1,\varepsilon,0)/\sqrt{1+\varepsilon^2}\)，并扫描

\[
\varepsilon\in
\{0,\tau_{\mathrm{frame}}/4,\tau_{\mathrm{frame}}/2,
\tau_{\mathrm{frame}},2\tau_{\mathrm{frame}},
4\tau_{\mathrm{frame}},10^{-2}\}.
\]

每个 dtype 使用自己的阈值；测试以实际计算的 \(\eta\) 判定，\(\eta\le\tau_{\mathrm{frame}}\) 必须拒绝，\(\eta>\tau_{\mathrm{frame}}\) 必须接受。另以 \(\lVert u\rVert/s\) 为 \(0,0.5\tau_0,\tau_0,2\tau_0\) 检查零长度边界。不得使用任意后备轴。

### 11.3 固定合成配置与扫描网格

阶段 E 冻结两个主配置：

| 配置 | seed | dtype | 随机旋转数 | multiplicity \((0e,1o,2e)\) | 合成图 \((N,E)\) | 输入尺度 |
|---|---:|---|---:|---|---|---:|
| A | 20260809 | float64 | 64 | \((3,2,2)\) | \((4,8)\) | \(1\) |
| B | 20260810 | float32 | 257 | \((5,4,3)\) | \((7,18)\) | \(10^3\) |

CLI 的 config A/B 必须展开为表中全部字段；同时提交冲突的显式字段必须拒绝。T-E01、T-E03—T-E10 和 T-E12 均运行 A/B；T-E02、T-E07、T-E11 还必须运行各自冻结的解析夹具。每个配置在两个独立子进程中各运行一次，确定性摘要必须为 UTF-8 规范 JSON：键排序、无额外空格、禁止 NaN/Infinity。摘要不得包含 wall-time、绝对路径、进程 ID 或线程调度信息，两次 stdout 必须字节完全相同。

T-E10 的正确性扫描冻结为下列笛卡尔积：

\[
\begin{aligned}
\mathrm{dtype}&\in\{\mathrm{float64},\mathrm{float32}\},\\
\mathrm{seed}&\in\{20260809,20260810\},\\
n_R&\in\{1,8,64,257\},\\
m&\in\{1,2,4\},\\
\alpha&\in\{10^{-3},1,10^3\}.
\end{aligned}
\]

其中 multiplicity 基准为 \((2,2,1)\)，由 \(m\) 整体放大；\(\alpha\) 同时缩放合成非零几何和非零特征，但不改变离散 edge key。共 \(144\) 个组合，不得在观察结果后删点或放宽阈值。每个组合报告最大归一化残差、最坏旋转索引、数组激活字节和由实际 contraction shape 直接计数的乘加次数。确定性正确性与精确字节/FLOP 只执行一次完整网格，再由两个子进程复现摘要；可选 wall-time 必须另做 3 次 warm-up 与 7 次测量，报告 median/IQR、CPU 和线程环境，并与规范 stdout/hash 完全分离。

144 点扫描是独立的 stageE-scan-v1 模式，与 config A/B 互斥。config A/B 模式不允许覆盖表中任何字段；scan 模式不读取 A/B 默认值，也不接受任意 seed、dtype、旋转数、multiplicity、尺度、节点数或边数覆盖，只能完整枚举上述笛卡尔积。调试时可以按规范 case ID 只读重放单点，但单点结果不计入门控。

seed 同时选择唯一的离散图，图本身不由 RNG 抽样：

- seed 20260809 使用 \(G_A\)，\(N=4,E=8\)，节点坐标依次为
  \[
  (0,0,0),\ (0.7,-0.2,0.1),\ (1.1,0.8,-0.3),\ (-0.4,1.2,0.6),
  \]
  有向 \((\mathrm{receiver},\mathrm{sender})\) 依次为
  \[
  (0,1),(1,0),(1,2),(2,1),(2,3),(3,2),(3,0),(0,3).
  \]
- seed 20260810 使用 \(G_B\)，\(N=7,E=18\)，节点坐标依次为
  \[
  \begin{aligned}
  &(0,0,0),\ (0.4,-0.7,0.2),\ (1.3,0.1,-0.5),\\
  &(-0.2,1.1,0.7),\ (0.9,1.4,-0.8),\ (-1.0,0.3,1.2),\ (0.2,-1.2,0.9),
  \end{aligned}
  \]
  无向原型边为
  \[
  \{0,1\},\{1,2\},\{2,3\},\{3,4\},\{4,5\},
  \{5,6\},\{6,0\},\{0,3\},\{2,5\},
  \]
  并按每个原型先较小端点接收、再反向的顺序展开为 18 条有向边。

两图的周期 shift 均固定为 \((0,0,0)\)，完整 edge identity 为 \((\mathrm{receiver},\mathrm{sender},0,0,0)\)，不得按无向原型去重。尺度 \(\alpha\) 只乘节点坐标和随后生成的非零连续特征，不改变 \(N,E\)、edge identity 或 edge 顺序。

每个扫描点使用 numpy.random.Generator(numpy.random.PCG64(seed))。抽样顺序固定为：先以 float64 C-order 抽取 shape \((n_R,4)\) 的标准正态四元数；再按 \(\ell=0,1,2\) 依次抽取节点特征 \(x_\ell\)；最后按 \(\ell=0,1,2\) 依次抽取逐边标量权重 \(W_\ell\)。所有随机数组先以 float64 生成，再转换到目标 dtype；四元数转换后在目标 dtype 中归一化并执行第 11.1 节的符号规范，随后转换为 C-order、目标 dtype、shape \((n_R,3,3)\) 的 `rotations` 矩阵数组。

生命周期严格冻结如下：float64、shape \((n_R,4)\) 的 `quaternion_gaussian_raw` 和目标 dtype、同 shape 的规范单位四元数都只是旋转生成预处理临时量；`rotations` 形成后，两者必须在抽取 \(x_0\) 之前释放。它们不进入 `array_bytes_total`，也不进入 reference contraction 的 `array_bytes_peak`。若实现另行分析旋转生成阶段峰值，应以独立字段逐名计入这两个临时量，不得改写 reference 字段。释放时点只冻结物化生命周期，不改变 PCG64 的后续抽样顺序。

T-E10 的冻结参考 kernel 为同型通道逐边线性消息：

\[
m_{\ell,e,a,k}
=\sum_{b=1}^{n_\ell}
W_{\ell,e,a,b}\,
x_{\ell,\mathrm{sender}(e),b,k},
\qquad
h'_{\ell,i,a,k}
=\sum_{e:\mathrm{receiver}(e)=i}m_{\ell,e,a,k},
\]

其中 \(n_\ell=m(2,2,1)_\ell\)，\(k=1,\ldots,2\ell+1\)。数组 shape 固定为

\[
x_\ell:(N,n_\ell,2\ell+1),\quad
W_\ell:(E,n_\ell,n_\ell),\quad
m_\ell:(E,n_\ell,2\ell+1),\quad
h'_\ell:(N,n_\ell,2\ell+1).
\]

成本字段同时输出

\[
\begin{aligned}
\mathrm{mac\_per\_rotation}
&=\sum_{\ell=0}^2 E\,n_\ell^2(2\ell+1),\\
\mathrm{mac\_total}
&=n_R\,\mathrm{mac\_per\_rotation},\\
\mathrm{flop\_total}
&=2\,\mathrm{mac\_total}.
\end{aligned}
\]

这里一个 MAC 固定计为一次乘法加一次累加，故为 2 FLOP；flop_total 只包含上式 contraction，不包含 receiver 聚合、旋转生成、validator、归一化、非线性或内存移动。receiver 聚合另输出

\[
\mathrm{aggregation\_add\_per\_rotation}
=\sum_{\ell=0}^2
\left[\sum_i\max(\deg^-_i-1,0)\right]n_\ell(2\ell+1)
\]

及其乘 \(n_R\) 的 total。

令目标浮点 dtype 的单元素字节数为 \(b\)，并记 \(c_\ell=2\ell+1\)。数组字节摘要必须逐名输出下列严格 shape、dtype 和 nbytes：

| 名称 | shape | dtype | nbytes |
|---|---|---|---:|
| coordinates | \((N,3)\) | target float | \(3Nb\) |
| receiver | \((E,)\) | int64 | \(8E\) |
| sender | \((E,)\) | int64 | \(8E\) |
| shift | \((E,3)\) | int64 | \(24E\) |
| rotations | \((n_R,3,3)\) | target float | \(9n_Rb\) |
| each \(x_\ell\) | \((N,n_\ell,c_\ell)\) | target float | \(Nn_\ell c_\ell b\) |
| each \(W_\ell\) | \((E,n_\ell,n_\ell)\) | target float | \(En_\ell^2b\) |
| each \(m_\ell\) | \((E,n_\ell,c_\ell)\) | target float | \(En_\ell c_\ell b\) |
| each \(h'_\ell\) | \((N,n_\ell,c_\ell)\) | target float | \(Nn_\ell c_\ell b\) |

`rotations` 在本表中唯一指旋转矩阵，不指四元数。coordinates 和所有浮点表示数组使用目标 dtype；receiver/sender/shift 固定为 int64。定义：

- array_bytes_total：上述全部命名数组各完整物化一次时的 nbytes 之和；
- array_bytes_peak：参考流式调度中 coordinates/edge arrays/rotations/全部 \(x_\ell,W_\ell\) 与全部预分配 \(h'_\ell\) 常驻，再加单个最大的 \(m_\ell\) 时的字节和；
- NumPy 内部未暴露临时量、解释器对象、allocator 开销和 BLAS workspace 不计入二者。

令 \(S_x=\sum_\ell n_\ell c_\ell\)、\(S_W=\sum_\ell n_\ell^2\)。上述表逐项给出

\[
\mathrm{array\_bytes\_total}
=3Nb+40E+9n_Rb+2NS_xb+ES_Wb+ES_xb,
\]

\[
\mathrm{array\_bytes\_peak}
=3Nb+40E+9n_Rb+2NS_xb+ES_Wb
+\max_\ell(En_\ell c_\ell b).
\]

在 float64、\(n_R=1\)、\((n_0,n_1,n_2)=(2,2,1)\) 时，逐数组族复算为：

| 数组族 | \(G_A\) | \(G_B\) |
|---|---:|---:|
| coordinates | 96 | 168 |
| receiver/sender/shift | 320 | 720 |
| rotations \((1,3,3)\) | 72 | 72 |
| all \(x_\ell\) | 416 | 728 |
| all \(W_\ell\) | 576 | 1296 |
| all \(m_\ell\) | 832 | 1872 |
| all \(h'_\ell\) | 416 | 728 |
| total | 2728 | 5584 |

最大单个 \(m_\ell\) 为 \(m_1\)，其字节为 384/864；故 reference peak 为 \(2728-832+384=2280\) 与 \(5584-1872+864=4576\)。

因此同一扫描 case 的图、RNG、数组 shape、MAC/FLOP、逐数组字节、total 和 peak 均可由契约独立复算。作为口径锚点，在 float64、\(n_R=1\)、\(m=1\) 时，\(G_A\) 的 mac_per_rotation、aggregation_add_per_rotation、array_bytes_total、array_bytes_peak 依次为 \(168,52,2728,2280\)；\(G_B\) 依次为 \(378,143,5584,4576\)。这些整数必须由逐数组明细重算得到，禁止直接硬编码后跳过 shape 检查。

float64 的群律、正交性、表示复合、intertwiner 和协变残差阈值为 \(5\times10^{-12}\)，float32 为 \(5\times10^{-6}\)。错误的转置、复合顺序、遗漏共轭、错误宇称或错位轨道顺序的定向失败夹具应至少产生 \(10^{-4}\) 的归一化残差；若随机对象偶然低于此值，必须使用冻结的非对称解析夹具，不得放宽错误判据。所有报告必须列出配置 ID、seed、dtype、样本数、最坏样例和 validator 残差。
