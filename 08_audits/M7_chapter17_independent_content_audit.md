# M7-04 第 17 章独立内容审计

## 1. 审计结论

**结论：FAIL**

- BLOCKING = 2
- NON_BLOCKING = 1
- 稳定问题 ID：M7-C17-B01、M7-C17-B02、M7-C17-N01。
- **不允许**将 M7-04 标记为 COMPLETED。
- **不允许**启动 M7-05。

第 17 章的核心数学主线整体正确：DLMF 14.30.1、Condon--Shortley 共轭关系、递增 \(m\) 顺序、主动函数作用、Wigner 群律、\(z\) 轴解析锚点、\(C_1/C_2\) 函数值矩阵、\(K_\ell=C_\ell^*\) 系数矩阵、实—复相似变换、复点值 \(D^*\) 与系数 \(D\) 的方向、实 \(p/d\) 双路线、宇称、未同步 \(m\) 逆序残差和实/复局部字节预算均通过独立复算。严格文档门控和十题十解配对也全部通过。

当前不能放行的原因不在上述核心代数，而在两个可执行接口仍未唯一冻结：球谐方向的“近零位移”拒绝规则缺少无量纲特征长度 \(s\)，且 Hamiltonian 实—复基变换没有兑现 sources.md 所声明的 mask、完整 edge identity 与 provenance 同步契约。另有一项提纲—正文结构漂移及一般轴例题缺失。若不修复，第三方虽能复算低阶矩阵，却仍不能无歧义实现零长度 validator 或安全地把稠密 \(K_\ell\) 接入带 padding、轨道身份和边身份的 Hamiltonian 数据。

## 2. 审计范围与独立性

本审计只读检查了下列对象：

- 第 17 章 sources.md、outline.md、chapter.md 与 examples.md；
- D-E03/D-E09 子推导 17_spherical_harmonics_wigner.md；
- Q17-01—Q17-10 与 A17-01—A17-10；
- M7_stageE_work_package.md 与 stageE_representation_conventions.md；
- DLMF 14.30 本地快照、阶段 E 来源索引、中央 CSV 台账与 BibTeX；
- 第 16 章实 \(p,d\)、多壳层、mask 与 provenance 接口；
- 阶段 D 工作包、统一周期图约定和阶段 D 总门控中的完整 edge identity、mask 与 provenance 边界；
- decisions.md 中 M8/M9 外部授权边界。

机器检查、公式核对和数值复算均由本审计重新执行，没有以主 agent 的预检结果替代独立判断。除本报告外，没有创建或修改其他文件。

## 3. 严格文档门控

### 3.1 Pandoc 与 MathML

七个送审文件均以 markdown+tex_math_single_backslash 输入格式严格转换为 HTML5/MathML，且启用 fail-if-warnings：

| 文件 | Pandoc exit code | MathML 节点 |
|---|---:|---:|
| sources.md | 0 | 6 |
| outline.md | 0 | 18 |
| chapter.md | 0 | 134 |
| examples.md | 0 | 60 |
| 17_spherical_harmonics_wigner.md | 0 | 144 |
| problem/readme.md | 0 | 48 |
| solution/readme.md | 0 | 77 |
| 合计 | 7/7 通过 | 487 |

Pandoc JSON AST 中的普通文本节点未发现 TeX 命令、数学定界符或 RawInline TeX 残留。数学表达均进入 Math 节点。

### 3.2 活动链接、控制字符与题解

- Pandoc AST 共解析 11 个活动本地链接，目标缺失数为 0；
- C0 与 DEL 控制字符错误数为 0；
- Q17-01—Q17-10 共 10 个，ID 唯一、连续且正文非空；
- A17-01—A17-10 共 10 个，ID 唯一、连续且正文非空；
- Q17 与 A17 的 ID 集合严格一一对应。

## 4. 来源与公式逐项核查

### 4.1 DLMF 14.30

本地快照实际 SHA-256 为

`D4547C98B7DAA72A6358233A78646A49013D9110FDD817E8CAF139F3CBDA9154`，

与阶段 E README、中央台账和送审来源记录一致。快照中的 DLMF 14.30.1 为

\[
Y_{\ell,m}(\theta,\phi)
=
\left[
\frac{(\ell-m)!(2\ell+1)}{4\pi(\ell+m)!}
\right]^{1/2}
e^{im\phi}\mathsf P_\ell^m(\cos\theta),
\]

14.30.6 为

\[
Y_{\ell,-m}=(-1)^m\overline{Y_{\ell,m}},
\]

14.30.7 为反演宇称，14.30.8 为正交归一。正文和推导中的定义、共轭与低阶 \(p,d\) 恒等式均与该快照相容；材料也正确警告不得在 DLMF Ferrers 定义上再次经验性叠加 \((-1)^m\)。

与本章直接相关的 MIT 8.321 第 20—21 讲、TFN、e3nn 论文和 DeepH-E3 论文快照均存在，实际 SHA-256 与阶段 E README 清单一致，PDF 头尾完整。中央 CSV 中 E-FND-01、E-FND-03、E-GNN-01、E-GNN-02、DH-02 均存在，BibTeX 键 dlmf1430、turner2017quantum321、thomas2018tfn、geiger2022e3nn、gong2023deephe3 均可定位。

### 4.2 来源边界

材料正确区分了三类证据：DLMF 与量子旋转讲义支持复球谐和旋转表示的数学对象；TFN/e3nn 论文支持球谐方向特征及不可约通道的一般接口；DH-02 只支持论文级 Hamiltonian 表示任务。正文没有把任一论文外推为 DeepH/e3nn 软件版本、正式数据、材料体系、DFT 设置或当前兼容性的证据。

M7-09 尚未执行 A/B 与 144 点扫描这一状态也被明确保留，没有把本章的解析矩阵和本地子预算冒充后续代码门控已经完成。

## 5. 数学与数值独立复算

### 5.1 主动作用、群律与 \(z\) 轴锚点

由

\[
[U(R)f](\widehat r)=f(R^{-1}\widehat r)
\]

可直接得到

\[
U(R_2)U(R_1)=U(R_2R_1),
\qquad
D(R_2R_1)=D(R_2)D(R_1).
\]

对 \(R_z(\alpha)\)，正文的

\[
D^{(\ell)}_{m'm}(R_z(\alpha))
=\delta_{m'm}e^{-im\alpha}
\]

方向正确。在 \(m\) 递增顺序和 \(\alpha=\pi/2\) 下，独立复算得到

\[
D^{(1)}=\operatorname{diag}(i,1,-i),
\qquad
D^{(2)}=\operatorname{diag}(-1,i,1,-i,-1),
\]

与正文、例题和题解一致。

### 5.2 \(C_1/C_2\)、\(K_\ell\) 与相似变换

按送审矩阵重建 (C_1,C_2) 后，独立结果为：

| 检查 | Frobenius 误差 |
|---|---:|
| \(C_1C_1^\dagger-I_3\) | \(3.14\times10^{-16}\) |
| \(C_2C_2^\dagger-I_5\) | \(4.44\times10^{-16}\) |
| \(R_z(\pi/2)\) 的 \(D^{(1)}\) 非对角部分 | 0 |
| \(R_z(\pi/2)\) 的 \(D^{(2)}\) 非对角部分 | 0 |

函数值关系 \(y_\ell=C_\ell r_\ell\) 与系数关系 \(c_{\mathrm c}=K_\ell c_{\mathrm r}\)、\(K_\ell=C_\ell^*\) 的转置/共轭方向正确。由

\[
D_{\mathrm c}=K_\ell D_{\mathrm r}K_\ell^\dagger
\]

恢复的实 \(p\) 矩阵严格为 \(R_z(\pi/2)\)，恢复的实 \(d\) 矩阵与第 16 章 \(B_a\mapsto RB_aR^{\mathsf T}\) 路线逐项一致。

### 5.3 一般轴随机旋转、实 \(p/d\) 双路线和点值

本审计使用 PCG64 seed 20260809 独立生成 200 组一般轴 Haar 旋转。以第 16 章的 \(D^p=R\)、\(D^d_{ab}=\operatorname{tr}(B_a^{\mathsf T}RB_bR^{\mathsf T})\) 和本章 \(K_1,K_2\) 构造复表示，最大绝对 Frobenius 误差为：

| 检查 | 最大误差 |
|---|---:|
| \(D^{(1)}(R_2R_1)-D^{(1)}(R_2)D^{(1)}(R_1)\) | \(6.21\times10^{-16}\) |
| \(D^{(2)}(R_2R_1)-D^{(2)}(R_2)D^{(2)}(R_1)\) | \(1.46\times10^{-15}\) |
| \(D^{(1)\dagger}D^{(1)}-I_3\) | \(2.59\times10^{-15}\) |
| \(D^{(2)\dagger}D^{(2)}-I_5\) | \(6.16\times10^{-15}\) |
| \(y_1(R\widehat r)-D^{(1)}(R)^*y_1(\widehat r)\) | \(3.02\times10^{-16}\) |
| \(y_2(R\widehat r)-D^{(2)}(R)^*y_2(\widehat r)\) | \(5.28\times10^{-16}\) |
| 实 \(p\) 点值直接旋转与表示路线 | \(1.25\times10^{-16}\) |
| 实 \(d\) 点值直接张量路线与表示路线 | \(4.46\times10^{-16}\) |

固定点 \(\widehat r=(1,2,2)^{\mathsf T}/3\) 的 \(\ell=1,2\) 点值误差分别为 \(8.78\times10^{-17}\) 和 \(2.10\times10^{-16}\)。因此材料关于“复点值使用 \(D^*\)，展开系数使用 \(D\)”的结论正确，一般轴上也不依赖 \(z\) 轴对角化的偶然性。

### 5.4 宇称、失败样例与相位自由

低阶函数直接给出

\[
y_1(-\widehat r)=-y_1(\widehat r),
\qquad
y_2(-\widehat r)=+y_2(\widehat r).
\]

材料同时说明一般网络通道必须显式记录 \((\ell,p)\)，没有把球谐轨道宇称 \((-1)^\ell\) 错误外推到所有同 \(\ell\) 特征。

对只改 \(K_1\mapsto JK_1\) 而未同步改写规范 Wigner 矩阵的错误夹具，独立得到

\[
D_{\mathrm{wrong}}=R_z(\pi/2)^{\mathsf T},
\qquad
\rho=2\sqrt{2/3}=1.6329931618554518,
\]

与材料一致且远高于 \(10^{-4}\)。材料也正确区分了“全部点值、系数、表示、CG 和元数据同步变换”的合法基自由，与只翻局部 \(m\) 相位或只改一个接口的规范不一致；没有重现 M7-01 已修复的“整通道相位一律判错”问题。

### 5.5 实/复局部字节子预算

独立按 NumPy dtype itemsize 核算：float64/complex128 为 8/16 bytes，float32/complex64 为 4/8 bytes；单个 \(\ell=1\) 副本为 24/48 bytes 或 12/24 bytes，单个 \(\ell=2\) 副本为 40/80 bytes 或 20/40 bytes。配置 A 的 19 个分量由 152 增至 304 bytes，配置 B 的 32 个分量由 128 增至 256 bytes。

材料把这些数严格限定为相同分量数的显式数组裸值子预算，没有外推成图 contraction、T-E10 total/reference peak、FLOP 或 wall-time，边界正确。

## 6. D-E03/D-E09 结构与自学性

D-E03/D-E09 子推导具有目标与边界、符号—维度表、适用条件、逐步推导、解析 \(z\) 轴锚点、固定点值例、未同步逆序和漏共轭失败、T-E03/04/07/10/12 映射及最终不变量。D-E09 只完成本章实/复局部字节对象，并把完整扫描留给 M7-09，结构满足工作包的一般要求。

正文、八个例题和十题十解已经覆盖规范、主动作用、低阶 Wigner 锚点、函数/系数映射、点值、宇称、零长度概念、顺序失败和接入审计。解答包含推理条件和不能推出的结论，不是只有数值答案。除第 8 节列出的缺口外，材料具备第三方自学和独立复算所需的主要链路。

## 7. Hamiltonian 基变换与授权边界

正文给出的两端基变换

\[
H_{\mathrm{complex}}
=K_iH_{\mathrm{real}}K_j^\dagger
\]

与系数基变换一致；表示矩阵也应以同一 \(K\) 作相似变换。该公式本身正确。当前缺陷是稠密基变换如何与 complete irrep shell、component mask、完整 edge identity 和 component provenance 对齐尚未写入实际材料，详见 M7-C17-B02。

送审范围没有安装或导入 DeepH/e3nn，没有下载正式训练数据，没有生成 DFT 标签，也没有隐含选择材料体系、DFT/数据后端、DeepH 软件对象、实践版本、Euler 软件接口或高级物理范围。M8 集中决策冻结及 M9 外部动作前再次明确授权的边界保持完整。

## 8. 问题清单与最小关闭条件

### M7-C17-B01：球谐方向的近零位移 validator 缺少无量纲尺度

- 严重度：BLOCKING
- 状态：OPEN
- 证据：chapter.md 17.6.1 只定义 \(\widehat d=d/\lVert d\rVert\)，随后称“零长度的精确拒绝阈值沿用阶段 E 统一约定”；examples.md 例题 7 又称“按冻结 dtype 阈值”拒绝；推导第 9 节和 A17-08 同样没有给出特征长度 \(s\)。但 stageE_representation_conventions.md 11.2 的冻结规则不是仅依赖 dtype 的绝对长度阈值，而是要求显式、有限、正的 \(s\)，并以 \(\zeta=\lVert u\rVert/s\) 与 dtype 对应 \(\tau_0\) 判定，等于阈值时拒绝。T-E09 的完整合同还是双向量局部架合同，不能在未说明映射时直接当成单个位移方向合同。
- 影响：同一非零位移在更换长度单位或扫描尺度后可能被不同实现判为接受或拒绝；第三方无法从本章唯一复现 float64/32 的边界夹具和 T-E12 失败矩阵。这直接破坏“公式条件与可验证性门控”。
- 最小关闭条件：在正文、例题、推导和相应答案中明确规定球谐方向输入必须携带什么特征长度 \(s\)，要求 \(s\) 有限且严格为正，并冻结 \(\zeta_d=\lVert d\rVert/s\)、float64/32 的 \(\tau_0\)、等号拒绝方向及阈值两侧夹具；明确这里只复用局部架合同的单向量零长度子规则，而不是暗示球谐方向需要第二参考向量。将该对象显式映射到 T-E04/T-E12；若选择不同合同，则必须在统一表示约定中先唯一冻结并说明尺度协变性。

### M7-C17-B02：Hamiltonian 基变换没有兑现 mask、edge identity 与 provenance 契约

- 严重度：BLOCKING
- 状态：OPEN
- 证据：sources.md 直接来源表声明阶段 D 用于“轨道顺序、mask、edge identity 与 provenance 接口”，来源—论断定位又声称这些对象已在正文 17.8.2—17.8.3 和 A17-10 中同步映射。实际正文 17.8.2 只写了 \(H_{\mathrm c}=K_iH_{\mathrm r}K_j^\dagger\)、表示矩阵、轨道顺序和笼统 provenance；正文及 A17-10 均没有出现 mask 或 edge identity。推导只要求 provenance 同步，也没有说明稠密 \(K_\ell\) 不能跨有效与 padding 分量混合。因而来源定位表对实际材料作了不可复核的过度声明。
- 影响：\(K_\ell\) 通常是稠密复矩阵，不是简单组件置换。若一个 irrep shell 只有部分组件有效，直接作用会把有效分量与 padding 混合；若复基组件继续沿用单个实轨道 component ID，则 provenance 也会失真。完整 edge key 本应在纯轨道基变换下保持不变，但材料没有冻结这一不变量。仅有矩阵公式不足以安全接入第 19 章 Hamiltonian 数据。
- 最小关闭条件：在正文、推导和 A17-10 中明确 \(K_i,K_j\) 只在完整有效的 shell/multiplicity 块内按块对角作用；padding 在作用前排除，component mask 不得被稠密变换静默穿透。冻结基变换后 provenance 的最小字段，至少包括 shell/multiplicity 身份、目标 basis family、递增 \(m\) 或实轨道 component 顺序及 \(K\) 的可追溯版本/哈希；不得把复组件伪装成未变化的单个实轨道 ID。明确结构 ID、receiver、sender、periodic shift、完整 edge key 和 edge 行序在纯基变换下不变，Hamiltonian、表示矩阵、component mask 与 provenance 共享同一块轴映射。同步修正 sources.md 的来源—论断定位，使其只声称实际可定位的内容。

### M7-C17-N01：冻结三级提纲与正文导航漂移，且缺一般轴工作例

- 严重度：NON_BLOCKING
- 状态：OPEN
- 证据：outline.md 预定 17.1.3 为 Condon--Shortley、17.1.4 为索引顺序、17.2.4 为 Euler 风险、17.3.3 为错顺序/相位/共轭，而正文将这些内容合并或移至其他节，并在 17.2.4 插入 \(z\) 轴锚点。更实质的差异是提纲 17.7.1 明确承诺“绕 \(z\) 轴和一般轴的低阶 Wigner 矩阵”，但八个例题中的显式 Wigner 计算全部使用 \(R_z(\pi/2)\)；一般轴只有可用公式和留待 M7-09 的随机验证入口，没有一例可逐步复算的非 \(z\) 轴 \(D^{(1)},D^{(2)}\) 工作例。
- 影响：核心公式并未因此错误，故不单独判为 blocking；但冻结提纲不能作为可靠导航，一般轴/Euler 风险的自学链也比承诺内容弱。
- 最小关闭条件：使 outline.md 与 chapter.md 的三级标题和材料入口一致，不得仅靠读者全文搜索寻找已移动内容；新增至少一个冻结的非 \(z\) 轴旋转，分别从 \(K_1RK_1^\dagger\) 和 \(K_2D^d(R)K_2^\dagger\) 给出可复算 \(D^{(1)},D^{(2)}\)，并以点值或群律作交叉验证。若决定不提供该例，应修订提纲承诺，但不得削弱工作包要求的正确例、失败例和数值入口。

## 9. 放行判定

M7-C17-B01 与 M7-C17-B02 均影响可执行合同和来源定位，不属于排版或措辞问题。在原审计员定点复核确认两个 BLOCKING 和一个 NON_BLOCKING 均关闭、且新增问题为 0 之前：

- M7-04 必须保持 REVIEW 或等价未完成状态；
- 不得将 M7-04 标记为 COMPLETED；
- 不得启动 M7-05 第 18 章主体建设。

主 agent 应实施修复并将相同稳定问题 ID 交回本审计员复核；本报告不代替修复，也不自行关闭问题。

## 10. 报告完整性

本报告写入后将独立执行严格 Pandoc/MathML、Pandoc AST 活动本地链接、控制字符和普通文本 TeX 残留检查。报告 SHA-256 在交付回报中给出，避免在报告正文中形成自指哈希。
