# M7-10 阶段 E 自学材料正式独立审计

## 1. 结论

**结论：FAIL。** 当前送审快照存在 `BLOCKING=5`、`NON_BLOCKING=0`。因此不允许将 M7-10 标记为 `COMPLETED`，也不允许启动 M7-11 阶段 E 总审计。

本次审计采用材料建设模式：判据是材料完备性、可自学性和可验证性，不要求学习者闭卷作答、口头解释或提交逐阶段自测。六章既有材料、D-E01—D-E09 推导包和 M7-09 合成代码的先前独立门控均已有零问题 PASS；本轮新发现的问题集中在四份 M7-10 核心材料之间及其到既有合同的映射。主 agent 修订后，必须交回本独立审计员按本报告的稳定问题 ID 定点复核；主 agent 的内部检查不能自行关闭问题。

## 2. 被审快照与范围

四份核心材料的送审 SHA-256 为：

| 文件 | SHA-256 |
|---|---|
| `03_textbook/chapters/stageE_self_study_guide.md` | `26061BACD4B25CF42282CE4213FE706ED6441AE3048CF561F0076C65691E3E38` |
| `03_textbook/stageE_representation_trace_template.md` | `EB14FE43839104290CC7C9DF3AA3C23B800462B8304ADB65975A0089667FBF88` |
| `06_exercises/05-stageE/comprehensive/problem/readme.md` | `86D9EF6D5B4D0BCEB9598AF58555D391D12BF3638EF9A09CB91C16DC31D4533E` |
| `06_exercises/05-stageE/comprehensive/solution/readme.md` | `8A10D9705821C0309C77DB7A7279C06C26680E2C092CE88FE47012564A7B760E` |

沿核心材料及工作包继续核验了以下对象：

- `03_textbook/stageE_representation_conventions.md`，SHA-256 `139BB534474A6D585CD5A31D6DF08B2DEE74F9E855929786D075C81FB34579BC`；
- `04_derivations/stageE/README.md` 与 D-E01—D-E09 六份分章推导，索引 SHA-256 `A65BC7199E9852A49408E31CB1E53BD0F8A3AA4F329DCB931DC1E0E8B016CCFB`；
- 第 15—20 章 `chapter.md`、`examples.md` 以及六组章节问题/参考解答；每章问题和解答均各有 10 个二级题目，数量配对；
- `08_audits/M7_stageE_work_package.md`，SHA-256 `00A8D4A9DC2E3FFB373E5B646401AE98813742037E6BE0E2F131659269A678D1`；
- 阶段 E 代码的模型、驱动、测试和说明，SHA-256 分别为 `16CB3A0DFC34417D11186F3512919D29519315134F596BEA32D60EE722D9E114`、`66B203E7169BBA1A166743C2F04BC997C09D93859FF0AEE39263A7C98682A8A0`、`A50FDB2430DA5ECE4A6086074BDEC799397AC1B3303CB41618EE665322720715`、`42A98FEDA0E09D602C8CDFAA9F39F9A71B58E49DD4FD7802AB8066BD8D289768`；
- M7-09 第一次定点复核 `08_audits/M7_stageE_code_blocking_reaudit.md`，SHA-256 `AE6D507A0FDE1F7E1D136E8687968C0DF5903DF2EBD1E35626C4DD58FBACB4B6`，其结论为 PASS、零遗留问题。

## 3. 复现环境、命令与执行结果

唯一送审 Python 为：

```powershell
$python = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python --version
& $python -c "import numpy, scipy; print(numpy.__version__, scipy.__version__)"
& $python -m pip check
& $python -m unittest discover -s .\05_code_exercises\stageE_synthetic_equivariance -p 'test_*.py' -v
& $python .\05_code_exercises\stageE_synthetic_equivariance\run_experiments.py --config A --seed 20260809
& $python .\05_code_exercises\stageE_synthetic_equivariance\run_experiments.py --config B --seed 20260810
& $python .\05_code_exercises\stageE_synthetic_equivariance\run_experiments.py --scan
```

实测环境为 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0；`pip check` 返回 `No broken requirements found.`；17 项 unittest 全部通过。A、B、scan 均在两个独立子进程中逐字节相同，stdout SHA-256 分别为：

```text
A    18702d7746405d39a6cc3997069fbcd3a31e60f440c64ea46903ea5908787b64
B    a8eea1e0f0a76e365ed709b906645bc2744f3b8cc84ef2061d8fe5c82bd1285b
scan c13944029e29ef6b47919646952a5d9bdf6a018cee3f101429fab09967982a81
```

A/B 的 T-E01—T-E12 均为 `pass=true`、`overall_pass=true`。T-E12 实测 `rejected=63`、`total=63`、`unique_failure_names=63`，每项都有非空异常类型与消息；inactive padding 的 NaN、0、`1e300` 三个探针均得到活动残差 0、loss 0，active NaN 被拒绝。scan 有 144 个唯一 case，规范摘要为：

```text
max_residual = 1.9468769400071583e-07
worst_case = float32-s20260809-r257-m1-a1e+03
worst_rotation = 189
worst_ell = 2
canonical_case_digest = 5317a387bfb026e53dceb31a85074d52ff520448c2fbac9649cb8013064cca7e
```

扫描成本锚点也与文档一致：G_A 为 `168/52/2728/2280`，G_B 为 `378/143/5584/4576`，依次是每旋转 MAC、每旋转 receiver 聚合加法、完整物化数组字节和参考流式 peak 字节。

严格文档检查对核心材料、统一约定、推导索引、六章教材/例题、六组章节题解、代码说明、工作包和 M7-09 PASS 报告共 40 个输入运行：

```powershell
pandoc --from=markdown+tex_math_single_backslash --to=html5 --mathml --fail-if-warnings <file>
```

40/40 返回 0。另以 Pandoc JSON AST 递归读取活动 `Link`/`Image`，39 个唯一 Markdown 文件共发现 85 个本地目标，断链 0；非法控制字符 0；四份核心材料的 C-E/A-E 标题解析结果均为 01—12、各 12 个、无重复且标题层面一一配对。

## 4. 关键数学与数值独立复算

以下复算由独立短脚本按题面公式重建矩阵、payload 和有限和，没有从参考解答复制数值数组。

### 4.1 主动链、STF 实 d 表与 Hamiltonian 双侧作用

题面矩阵给出

```text
R1 r       = (-2, 1, 3)
R2 R1 r    = (-2, -3, 1)
R1 R2 r    = (3, 1, 2)
R1^T r     = (2, -1, 3)
```

按五个 Frobenius 正交归一 STF 基直接收缩，得到与 A-E03 相同的完整 (D^d(R_1)) 和 (D^d(R_2R_1))。独立残差为

```text
||(Dd(R1))^T Dd(R1)-I||_F = 9.930136612989092e-16
||Dd(R2 R1)-Dd(R2)Dd(R1)||_F = 5.20740757162067e-16
```

对冻结 \(4\times8\) 块重建 \(D_i=1\oplus R_1\)、\(D_j=R_1\oplus D^d(R_1)\)，(D_iHD_j^T) 仍为 \(4\times8\)，逆块为 \(8\times4\)，变换前后奇异值差的二范数为 `6.462750666145534e-16`。

### 4.2 K1/K2、CG 与边身份

独立构造规范紧凑 JSON 后得到：

```text
K1 347e352605a3f4f3ccb078b6cedf5c755fdc6aa3527ea41a8ea3e93d076972a2
K2 5e783d9cdfe025238977f9e92d64d8b46e9a0e79eb8c9deba1af116aaafc7b82
```

另按 Racah 有限和独立构造 \(1\otimes1\) 的 \(9\times9\) CG 矩阵，三个 DLMF-CS 锚点为 `0.5773502691896257`、`0.7071067811865475`、`1.0`；行、列正交残差分别为 `5.0992590710652775e-16`、`4.0437572205275285e-16`。交换相位对 (L=0,1,2) 分别为 `+1,-1,+1`，\(1\otimes2\) 允许 (L=1,2,3)。整条固定 (L) 通道的统一相位可视为输出基变换并保持 intertwiner；只改一个 (M) 行或单系数不是同一不可约输出基的整体变换。

正、逆 edge payload 的独立 SHA-256 为：

```text
["stageD-edge-v1","stageE-H",0,1,0,0,0]
1a8d2a609fbe3cc7c5e9de863375420544fc64f1887b2f1df26d5defd9b2a4a8
["stageD-edge-v1","stageE-H",1,0,0,0,0]
88c94d43c0833d689aacac098a0709e61e08e83f598ec3c26ea91534b8b99bf4
```

### 4.3 局部架与时间反演

统一约定和代码使用

\[
\eta_{\mathrm{contract}}=\lVert\widehat u\times\widehat v\rVert_2.
\]

取 `float64`、(s=1)、(u=(1,0,0))、\(v=(2,1.5\times10^{-8},0)\)，独立复算得到 `eta_contract=7.5e-9`，应按 `<=1e-8` 拒绝；追踪模板和 A-E09 当前所写的未归一化投影式则得到 `1.5e-8`，会接受同一输入。这是可执行的合同分叉，详见 `M7-SESS-B03`。

spinless 实轨道的 (Theta^2=+I)；对 \(J_s=\begin{smallmatrix}0&1\\-1&0\end{smallmatrix}\)，独立计算 (J_sJ_s^*=-I)。对 (ell=0,1,2) 的 \(J_{m'm}=(-1)^m\delta_{m',-m}\)，均有 (JJ^*=I)。冻结 TRIM 对角夹具的广义本征值为 `[0.25,0.25,0.6666666666666667,0.6666666666666667]`；只有 TRIM、时间反演保持、(Theta^2=-I)、\(S\succ0\) 和正确 H/S partner 同时成立时，才可把配对解释为同一 k 的 Kramers 简并。

## 5. 稳定问题

### M7-SESS-B01：自学导航系统性改写了已冻结的 D-E01—D-E09 编号，并含错误章节定位

**严重度：BLOCKING。** `stageE_self_study_guide.md` 第 15—18、29—38、46—53、62—70 行使用了一套与工作包及推导索引不同的 D-E 编号。例如：

- 工作包/推导索引冻结 D-E02 为实 (s,p,d) 表，D-E03 为球谐/Wigner，D-E04 为 CG，D-E05 为 Hamiltonian，D-E06 为消息层，D-E07 为局部架，D-E08 为自旋/时间反演；
- 自学导航却把 D-E02 写成 polar/axial/tensor，把 STF 表写成 D-E03，把 Wigner 写成 D-E04，把 CG 写成 D-E05，把 Hamiltonian 写成 D-E06，把局部架写成 D-E08，并在其第 5 节把这套错位定义重新列成表格；
- 单元表还把第 15 章文件标成 “D-E01/D-E02”、第 16 章标成 D-E03、第 17 章标成 D-E04、第 18 章标成 D-E05、第 19 章标成 D-E06—D-E08，均与审定索引不一致；
- 教材节号也有可操作性错误：polar/axial 位于第 16 章 16.5 而不是导航所列 16.6；局部架理论位于 19.6 而不是 19.8；残差与复杂度位于 19.7 而不是 19.9。

这不是文字标签问题。学习者或审计员沿导航反查 D-E04、D-E07 或 D-E08 时会到达错误能力对象，正向矩阵和反向索引因而不能唯一定位已审定推导。

**最小关闭条件：** 以 `M7_stageE_work_package.md` 第 62—74 行和 `04_derivations/stageE/README.md` 第 63—75 行为唯一编号源，逐行修订导航的单元表、正向矩阵、反向索引和“能力边界”表；修正 16.5、19.6、19.7 等章节节号；对 D-E01—D-E09 执行自动集合/目标比对，证明每个 ID 的语义和目标文件唯一一致。

### M7-SESS-B02：C-E08 题面与 A-E08 对节点输入宇称给出互斥答案

**严重度：BLOCKING。** C-E08 第 90 行明确冻结节点输入为 ((1,+)) coefficient；A-E08 第 167—170 行却声明“输入和 filter 均为 ((1,-))”，并据此写成

\[
(1,-)\otimes(1,-)\to(0,+)\oplus(1,+)\oplus(2,+).
\]

若遵守题面，方向生成的 (ell=1) filter 为 ((1,-))，则输出宇称应为 (+·-=-)，即

\[
(1,+)\otimes(1,-)\to(0,-)\oplus(1,-)\oplus(2,-).
\]

若解答才是预期合同，则必须把题面输入改为 ((1,-))。两种选择会改变逐层表示类型、门控合法性和 output-irrep provenance，不能由自学者自行猜测。标题虽有 12/12 配对，但 C-E08/A-E08 在技术内容上不一一对应。

**最小关闭条件：** 在题面、参考解答、导航矩阵、追踪示例和代码 provenance 之间冻结同一个输入宇称；按 \(p_{\mathrm out}=p_{\mathrm in}p_{\mathrm filter}\) 重写三条输出类型，并加入至少一个 (O(3)) 反演复算，使错误宇称元数据实际失败。不得只凭 (SO(3)) 残差宣称两种合同等价。

### M7-SESS-B03：局部架退化指标在统一约定/代码与追踪模板/综合解答之间不一致

**严重度：BLOCKING。** 统一表示约定第 273—279 行以及工作包 T-E09 冻结

\[
\eta=\lVert\widehat u\times\widehat v\rVert_2,
\]

代码 `local_frame` 也先归一化 (u,v)，再计算上述无量纲正弦指标。表示追踪模板第 147 行和 A-E09 第 191 行却写成

\[
\eta=\lVert v-(v\cdot e_1)e_1\rVert/s.
\]

后式会随 (v) 的幅值改变，而前式只依赖夹角；二者并非同一合同。第 4.3 节给出的固定输入使前式拒绝、后式接受，因此差异已经改变 validator 的边界判定。模板还只列一个 \(zeta=\lVert u\rVert/s\)，遗漏代码实际分别检查的 (zeta_u,zeta_v)。

**最小关闭条件：** 模板和 A-E09 必须逐字采用统一约定中的 (zeta_u,zeta_v) 及归一化叉积 (eta)，保留 dtype 阈值和等号拒绝；综合题或解答加入上述幅值反例，证明实现不会把有量纲投影长度当作无量纲角退化度。

### M7-SESS-B04：正向材料矩阵没有建立到例题、章节练习和参考解答的可执行路径

**严重度：BLOCKING。** 工作包第 149 行要求“能力 → 教材 → 推导 → 例题 → 代码 → 失败样例 → 练习/解答”的正向矩阵。当前导航第 3 节的列只有“教材、推导、代码入口、综合题、失败样例”，没有例题列和参考解答列。对该文件的 Pandoc AST 统计显示总计 18 个链接，其中 `examples.md` 链接为 0、`06_exercises` 链接为 0、`solution` 链接为 0。第 2 节虽以普通文本写“第 15/16 章例题与题解”，但没有给出目标文件，也没有把 C-E01—C-E12 各能力映射到具体例题、章节题目和 A-E 解答。

在材料建设模式下，学习者不被要求闭卷补齐缺失路径；导航本身必须使“看定义—跟推导—复算例题—运行代码—观察失败—做/查综合题解”可直接执行。现状不能满足该门控。

**最小关闭条件：** 在正向矩阵中为 C-E01—C-E12 逐行加入可点击的具体 `examples.md`、章节 `problem/readme.md`、章节 `solution/readme.md` 和综合 `solution/readme.md` 入口；矩阵应明确例题/失败样例编号，而不是只写“第 n 章例题与题解”。修订后用 AST 证明每个能力至少具有教材、推导、例题、代码、失败、练习和参考解答七类目标。

### M7-SESS-B05：表示追踪模板不能逐字段记录时间反演 partner provenance 与 mask

**严重度：BLOCKING。** 工作包和本轮审计任务要求模板逐层覆盖 time-reversal provenance、mask、dtype、shape 和条件。当前模板第 10 节只有 `basis/order`、unitary part、平方、`partner/condition`、残差和判定六列。它没有独立字段记录 `k_id`、`minus_k_id`、`partner_map`、H/S 各自的 k/-k row、orbital row IDs、active mask、H/S shape/dtype、partner provenance 或 TRIM reciprocal-vector 条件。第 4 节的通用消息层表虽有 mask/provenance 列，但不能替代反幺正 H/S partner 的双行身份记录。

M7-09 的 T-E11/T-E12 已经实际拒绝 wrong partner ID/map、partial mask、orbital row drift、漏共轭和错误 S partner；现有模板无法逐字段留下这些已经冻结的证据，因此读者可能只复算 \(JJ^*=\pm I\) 而遗漏独立 partner 合同。

**最小关闭条件：** 在模板第 10 节新增 H/S k/-k partner 表，至少包含 schema、k/minus-k ID 与坐标、partner map、orbital IDs、basis/component 顺序、shape、dtype、mask、H/S row provenance、(J)、关系残差、TRIM 判据和故障结果；表格字段须能直接承接 T-E11 的 `pair_identity`、array summary 和六项 partner 故障。

## 6. 已通过项目与证据边界

除上述五项外，本轮未发现新的独立问题：

- C-E01—C-E12 与 A-E01—A-E12 的标题集合和顺序为 12/12；C-E01—07、C-E09—12 的主要解析数值与独立复算相符；
- R1/R2、STF d 表、K1/K2、CG 三相位锚点、整通道相位自由、4×8 Hamiltonian 左右作用、正逆 edge payload/hash、144 点成本/最坏 case、spinless/spin-half/TRIM 条件均已实际复算；
- 代码 17/17、T-E01—12、63/63、padding、A/B/scan 确定性均通过，M7-09 PASS 报告无回归；
- strict Pandoc/MathML、AST 本地链接和控制字符检查通过；
- 固定 Python 环境未安装 DeepH、e3nn、ASE 或 pymatgen；代码依赖仍只有精确固定的 NumPy/SciPy；
- 四份核心材料均明确禁止在 M8 前安装 DeepH/e3nn、下载正式数据、生成 DFT 标签或选择材料/DFT/数据后端、DeepH 软件对象、首个材料、训练预算和高级物理范围；M8 冻结后、M9 正式动作前仍要求用户再次明确授权，未发现越界。

这些通过项只支持当前阶段 E 合成理论、身份和 schema 契约。它们不能证明真实 DeepH/e3nn、正式 Hamiltonian 标签、任一材料体系、任一 DFT/数据后端、实践 cutoff、真实训练成本、SOC/磁性方案或硬件预算已经选定或验证。

## 7. 最终计数与许可

| 稳定问题 ID | 严重度 | 状态 |
|---|---|---|
| `M7-SESS-B01` | BLOCKING | OPEN |
| `M7-SESS-B02` | BLOCKING | OPEN |
| `M7-SESS-B03` | BLOCKING | OPEN |
| `M7-SESS-B04` | BLOCKING | OPEN |
| `M7-SESS-B05` | BLOCKING | OPEN |

最终计数：`BLOCKING=5`、`NON_BLOCKING=0`、剩余问题 5。

因此本轮正式判定 **FAIL**：不允许将 M7-10 标记为 `COMPLETED`，不允许启动 M7-11。五项均按最小关闭条件修订后，应由同一独立审计员复核稳定 ID、相邻映射、严格格式和代码回归；只有复核达到 `PASS`、`BLOCKING=0`、`NON_BLOCKING=0` 且没有新增问题，才允许完成 M7-10 并启动 M7-11。
