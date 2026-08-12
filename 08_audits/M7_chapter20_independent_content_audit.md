# M7-07 第 20 章正式独立内容审计

## 1. 审计结论

**结论：FAIL。** 当前送审快照存在 `BLOCKING=1`、`NON_BLOCKING=1`。因此不允许将 M7-07 标记为 `COMPLETED`，也不允许启动 M7-08。主 agent 修订后，必须由本独立审计员对稳定问题 ID 执行定点复核；主 agent 的内部验证不能替代独立结论。

第 20 章关于 \(SO(3)/SU(2)\) 双覆盖、自旋 \(1/2\) lift、轨道—自旋 Kronecker 顺序、反幺正时间反演、\(\Theta^2=JJ^*\)、复轨道基中的 \(J_\ell\)、Hamiltonian/overlap 的 \(k/-k\) 配对、Kramers 条件、宇称组合、成本边界和 M8/M9 授权边界，均与阶段 E 冻结约定一致。独立数值复算没有发现核心物理或表示公式错误。但是，`chapter.md` 的核心 Pauli 分解公式包含一个 U+000B 控制字符，并把本应为 `\varepsilon` 的对象实际损坏为 `arepsilon`；这直接违反“非法控制字符为 0”的硬门控，也使严格 Pandoc 成功不能代表公式语义正确。`examples.md` 另有一处遗漏反斜杠的 `\in`，形成可由上下文恢复但仍需关闭的 MathML 语义缺陷。

## 2. 独立性、范围与方法

本审计由新的独立子 agent 完成。七个被审材料全程只读；本次唯一新增文件为本报告。审计范围为：

- `03_textbook/chapters/20_spin_time_reversal_complex/{sources.md,outline.md,chapter.md,examples.md}`；
- `04_derivations/stageE/20_spin_time_reversal_complex.md`；
- `06_exercises/05-stageE/20_spin_time_reversal_complex/{problem,solution}/readme.md`；
- `08_audits/M7_stageE_work_package.md`、`03_textbook/stageE_representation_conventions.md`；
- 第 15—19 章已经审定的旋转、复—实轨道、CG、Hamiltonian 块和 provenance 接口；
- 阶段 E 直接来源快照、README 与中央来源台账。

独立检查包括：

- 标准 Pauli 基、\((m_s=+1/2,-1/2)\) 顺序、\(2\pi/4\pi\)、\(U\to R\)、双覆盖和轨道—自旋 Kronecker 轴；
- 反线性、\(\Theta^2=JJ^*\)、无自旋实基 \(K\)、复轨道 \(J_\ell\)、\(J_{\mathrm c}=KJ_{\mathrm r}K^{\mathsf T}\)、自旋 \(J_s=i\sigma_y\)、整体相位边界和三个规范 payload/hash；
- \(JD(R)^*J^\dagger=D(R)\)、Hamiltonian/overlap \(k\)-pair、Hermiticity、Pauli 奇偶、partner/schema/provenance 和定向失败；
- Kramers 同能与正交、TRIM/一般 \(k\) 定义域、Zeeman/磁性破缺及 \(P/\Theta\) 复合条件；
- D-E08/D-E09 子对象的符号、维度、输入输出、成立条件、推导、正反例、最终不变量和 T-E11/T-E12 映射；
- 七文件严格 Pandoc/MathML、Pandoc AST 活动链接、Raw TeX、控制字符、三级标题、12 个例题和 Q20/A20 10/10；
- 阶段 E 11 个来源快照的 SHA-256、逐项来源定位和 M8/M9 授权扫描。

复算环境为 Python 3.12.13、NumPy 2.3.5；随机复算使用 `numpy.random.default_rng(20260810)`。没有安装或导入 DeepH/e3nn，没有下载正式数据，也没有生成 DFT 标签。

## 3. 当前送审快照

| 文件 | SHA-256 |
|---|---|
| `sources.md` | `D6425F7603C9DFA208F11F1B79AC7C904A7C9A3BA060DA06A7A36BBB1DE9F965` |
| `outline.md` | `C76CC2F8A59E6E6C47F6F8B5EDA096FAE8F36A61780AE82267FF8705C843339B` |
| `chapter.md` | `6FAEA587F3740BEDE965605BEE6C9D5C6B87963C193F1AD7AD3D0F108811A6F8` |
| `examples.md` | `59A1F2EF65CBA16B6ABE70EE249671924291E1D4E5C14F8C5AF3D957552AC872` |
| `20_spin_time_reversal_complex.md` | `E3397B367E8AE477B2026AA6935240FC811C458AAAEEBB435621904FA337BE96` |
| `problem/readme.md` | `4BCBFE4AF887DC6A545CD6F6EDE870668D84E746A5869B9966660F0ECF694232` |
| `solution/readme.md` | `017B893B5BE3F201FB899C161518C818AA0BF0B9BAA823D3912328D07E7D37E8` |

## 4. 独立复算结果

### 4.1 \(SU(2)\) lift、双覆盖与群律

独立采用标准 Pauli 矩阵和

\[
U(q)=wI-i(x\sigma_x+y\sigma_y+z\sigma_z)
\]

构造 200 对 Gaussian 归一化一般四元数 \(q_1,q_2\)，按 Hamilton 积 \(q_{21}=q_2q_1\) 检查主动复合。最大残差为：

| 对象 | 200 组最大误差/残差 |
|---|---:|
| \(U^\dagger U=I\) | \(4.48\times10^{-16}\) |
| \(|\det R-1|\) | \(1.33\times10^{-15}\) |
| Pauli 迹公式 \(U\to R\) | \(4.10\times10^{-16}\) |
| \(U(q_2q_1)=U(q_2)U(q_1)\) | \(2.09\times10^{-16}\) |
| \(R(q_2q_1)=R(q_2)R(q_1)\) | \(8.53\times10^{-16}\) |
| \(J_sU^*J_s^\dagger=U\) | \(0\) |

对一般轴 \((1,2,3)/\sqrt{14}\)，\(U(2\pi)=-I_2\) 与 \(U(4\pi)=I_2\) 的归一化残差分别为 \(1.22\times10^{-16}\) 和 \(2.45\times10^{-16}\)。材料采用的 Pauli 基、主动旋转号、spin 顺序和 \(U\to R\) 方向一致；\(U\) 与 \(-U\) 给同一 \(R\)，但连续 lift identity 不能由 \(R\) 唯一恢复的边界陈述正确。

### 4.2 轨道、自旋与反幺正基变换

按第 17 章冻结的

\[
K_1=
\begin{pmatrix}
1/\sqrt2&i/\sqrt2&0\\
0&0&1\\
-1/\sqrt2&i/\sqrt2&0
\end{pmatrix}
\]

独立得到

\[
J_1=K_1K_1^{\mathsf T}
=
\begin{pmatrix}
0&0&-1\\
0&1&0\\
-1&0&0
\end{pmatrix}.
\]

与材料固定数组的残差为 \(1.81\times10^{-16}\)；误用 \(K_1K_1^\dagger=I\) 的定向残差为 \(1.1547005383792515\)。在 200 个一般轴旋转上，复 \(\ell=1\) 的 \(J_1D_1^*J_1^\dagger=D_1\) 最大残差为 \(4.29\times10^{-16}\)；对 orbital-major/spin-minor 的 \(D_1\otimes U\) 与 \(J_1\otimes J_s\)，最大残差为 \(4.13\times10^{-16}\)。

固定

\[
\psi=(1,1+i)^{\mathsf T}/\sqrt3
\]

的反线性残差、\(\Theta^2\psi=-\psi\) 残差和 \(\langle\psi\mid\Theta\psi\rangle\) 均为 0；错误线性映射 \(L(\psi)=J_s\psi\) 给 \(\lVert L(i\psi)+iL(\psi)\rVert_2=2\)。整体相位 \(J\mapsto e^{i\phi}J\) 同时不改变 \(JJ^*\) 与 \(JH^*J^\dagger\)，但会改变项目规范字节对象的区分正确。

三个 UTF-8、无空白 payload 的独立 SHA-256 为：

| 对象 | 独立 SHA-256 |
|---|---|
| spinless real | `56342DB661DA6F8D9CC8C3BF6E241DCB9817F42E63A33CAD9AF9364BCC8DF6EC` |
| spin half | `F8B5E9591B791A2DBD9B262736718C8B391B75DE6CE720335D1AD5B8F1AFF444` |
| orbital l1 | `230AA31FC0201B4F2D7F8981A3244049C280F75CB2C753F38F9CE9D86A250980` |

三者均与推导表一致。`complex128` 数学 payload hash 与实际 `complex64` 数组字节 hash 必须分列的边界也已明确保留。

### 4.3 Hamiltonian、Pauli 奇偶与失败样例

例 20-5 在 \(k=0.7\) 的两矩阵、零配对残差和本征值 \(1.53560897,2.92329634\) 可独立复现；它们在一般 \(k\) 不简并的解释正确。为避免纯实矩阵掩盖漏共轭，另构造含 \(\sigma_y\) 的固定偶/奇 Pauli 模型，并对 200 个均匀随机 \(k\in[-\pi,\pi]\) 检查：

- Hermiticity 最大残差为 0；
- \(H(-k)=J_sH(k)^*J_s^\dagger\) 最大残差为 0；
- 漏复共轭的残差范围为 \(6.34\times10^{-4}\) 至 \(5.36\times10^{-1}\)，全部高于 \(10^{-4}\)；
- 固定复矩阵中使用错误 \(J=I\) 的残差为 \(5.93\times10^{-1}\)；
- 固定错误 partner 行残差为 \(6.65\times10^{-1}\)；
- Zeeman \(H_B=\sigma_z\) 残差为 2。

因此 Hamiltonian/overlap 的共轭方向、Pauli scalar 偶/自旋向量奇、Hermiticity、错误 partner/provenance 和磁性破缺门控均正确。材料也明确指出按谱排序相等不足以替代矩阵、basis、mask、actual orbital/spin 与 partner row 的完整 schema。

### 4.4 Kramers、Bloch 定义域与 \(P\Theta\)

对 200 个随机 \(4\times4\) Hermitian 矩阵，使用 \(J=I_2\otimes J_s\) 投影到同一 TRIM fiber 的时间反演不变子空间。时间反演残差最大值为 0；相邻 Kramers 本征值最大劈裂为 \(3.11\times10^{-15}\)；任一本征向量与其时间反演像的最大内积模为 \(5.55\times10^{-17}\)。

推导正确保留以下必要条件：\(\Theta\) 反幺正、\(\Theta^2=-I\)、Hamiltonian 定义域由 \(\Theta\) 保持且时间反演不变、没有保持同号的外磁场/磁序、basis/k-pair/provenance 相容。一般 \(k\) 只支持 \(\mathcal H_k\leftrightarrow\mathcal H_{-k}\) 的同谱配对；同一 \(k\) 简并还需 \(-k=k+G\) 及 reciprocal/basis 回拉。若 \([P,\Theta]=0\)、\(P^2=I\)，则 \((P\Theta)^2=P^2\Theta^2\)；含非平凡平移、不对易内部作用或磁性群时重新推导的边界正确。

### 4.5 D-E08/D-E09、例题与授权边界

D-E08 推导具备统一符号/shape/dtype/provenance 表、输入输出、逐步推导、成立条件、固定正例、定量失败、T-E11/T-E12 映射和最终不变量。D-E09 的自旋扩维子对象正确区分：

\[
P\to2P,\qquad
P^2\to4P^2,
\]

`float64` spinless 到 `complex128` spinful 的持久字节比 8，以及一般 dense 双侧作用的 complex MAC 比 8。材料没有把 complex MAC 套用实 kernel 的 2 FLOP/MAC，也没有把解析倍数冒充实际软件 wall-time 或 M7-09 的 144 点执行证据。

例 20-1—20-12 共 12 个，覆盖 lift、轴顺序、反线性、复轨道 basis route、\(k\)-pair、TRIM、Zeeman、漏共轭、整体相位、宇称和成本。Q20-01—Q20-10 与 A20-01—A20-10 为严格 10/10，逐题非空，能够从定义、推导、失败样例和授权边界完成自学闭合。

材料始终把 SOC、磁性、双群和 DeepH-E3 限定为理论或论文级候选接口；未选择材料、DFT/数据后端、DeepH/e3nn 软件对象或版本，未下载数据、生成标签或授权外部执行。M8 集中决策与 M9 二次明确授权均保持完整。

## 5. 文档、来源与导航验证

七文件均以 `markdown+tex_math_single_backslash`、HTML5 MathML、`--fail-if-warnings` 返回 0。MathML 节点数依次为 `25/18/207/75/143/31/52`，合计 551。Pandoc JSON AST 共解析 5 个活动本地链接，缺失目标为 0；RawInline/RawBlock TeX 节点为 0。

`outline.md` 与 `chapter.md` 的三级标题均为 29 个，文本和顺序 29/29 完全一致。Q/A ID 唯一、顺序相同。阶段 E README 登记的 11 个来源快照实际 SHA-256 全部一致；E-FND-03 的 MIT 8.321 第 20—23 讲确实支持 \(SU(2)\) 双覆盖、\(2\pi\) 符号、宇称/时间反演、\(\Theta^2=-I\) 和 Kramers 条件。E-FND-01/02 与 DH-02 的用途和限制与中央来源台账一致，E-SUP-01 没有进入直接论证链。

但是，C0 控制字符扫描实际得到 1 个错误：`chapter.md` UTF-8 字符偏移 6585 为 U+000B。严格 Pandoc 返回 0 不会代替此独立字符门控，也不会检查合法 MathML 是否表达了作者预期的关系算符。

## 6. 问题清单

### M7-C20-B01：Pauli 分解核心公式含 U+000B，并把 \(\varepsilon\) 损坏为普通 `arepsilon`

**严重度：BLOCKING。**

**证据：** `chapter.md:332` 当前字节对象在等号后为 U+000B，随后直接是 `arepsilon(\boldsymbol k)I`，而不是 `\varepsilon(\boldsymbol k)I`。同文件第 336、346 行和 D-E08 第 252、264 行均使用正确的 `\varepsilon`，因此预期对象没有歧义。七文件独立 C0 扫描得到 `chapter.md` 1 个非法控制字符，其余 6 文件为 0。

Pandoc 严格转换仍返回 0，但该事实只能说明解析器没有发出 warning，不能证明公式对象正确。控制字符没有生成 TeX 控制序列；Pauli 分解的第一项因而不是材料随后讨论的 scalar coefficient \(\varepsilon(k)\)。该位置属于 \(H(k)=\varepsilon(k)I+\boldsymbol b(k)\cdot\sigma\) 的核心定义，同时工作包和章级门控明确要求非法控制字符为 0，故不能按普通排版瑕疵放行。

**最小关闭条件：** 仅将 `chapter.md:332` 的 U+000B 与 `arepsilon` 修正为字面 TeX `\varepsilon`；重跑七文件控制字符扫描并得到 0，重跑严格 Pandoc/MathML，并检查生成 AST/MathML 中该节点确为希腊小写 \(\varepsilon\)。同时复核相邻 Pauli 奇偶、Hamiltonian 配对和文件 hash，不能用清洗后静默丢弃控制字符而保留 `arepsilon`。

### M7-C20-N01：例 20-2 的集合隶属符遗漏反斜杠

**严重度：NON_BLOCKING。**

**证据：** `examples.md:44` 当前写为

\[
D_{p\otimes s}=R\otimes U_{1/2}in\mathbb C^{6\times6}.
\]

其中 `in` 是两个普通数学字母，不是关系算符 \(\in\)。Pandoc 会把它转换成合法 MathML，因此 `--fail-if-warnings` 不会报警。正文第 120—130 行、例题前后文和 A20-02 均给出正确轴顺序、shape，并且参考解答明确写为 `\in\mathbb C^{6\times6}`；所以该缺陷不改变独立复算的 Kronecker 数组，也不单独推翻核心表示合同。但是，它使承担自学锚点功能的例题公式具有错误 MathML 语义，不能在问题总数为 0 的章级门控中保留。

**最小关闭条件：** 仅把 `examples.md:44` 的 `in\mathbb C` 改为 `\in\mathbb C`；重跑严格 Pandoc/MathML，并检查该节点为 relation operator；复核例 20-2 与 A20-02 的 component 顺序、\(6\times6\) shape 和显式置换说明不变。

## 7. 退出判断

当前 `BLOCKING=1`、`NON_BLOCKING=1`。核心 \(SU(2)\)、反幺正、复轨道基变换、Hamiltonian 时间反演、Kramers 条件、D-E08/D-E09 子对象、来源边界和 M8/M9 禁令未发现其他问题；200 组一般轴、Hamiltonian 与 Kramers 独立复算均通过。现有两个问题均可由局部文本修订关闭，但 B01 直接违反控制字符硬门控，N01 仍违反自学例题的数学语义完整性。

因此：

- M7-07 当前不得完成；
- M7-08 当前不得启动；
- 主 agent 应按最小关闭条件修订 B01/N01，不应借此改变已通过的物理公式、约定或授权边界；
- 修订后须由本独立审计员复核两个稳定 ID 及相邻回归；只有 `BLOCKING=0`、`NON_BLOCKING=0` 且无新增问题，才允许完成 M7-07 并启动 M7-08。

本报告写入后将独立执行严格 Pandoc/MathML、活动链接和控制字符检查；稳定 SHA-256 作为交付元数据回报，避免在报告正文内形成自指 hash。
