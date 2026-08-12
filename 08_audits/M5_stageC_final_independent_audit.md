# M5-10 阶段 C 正式独立材料总审计

- 审计时间：2026-08-04（Asia/Shanghai）
- 审计对象：M5 阶段 C 当前工作区快照
- 审计结论：`FAIL`
- `BLOCKING=1`
- `NON_BLOCKING=2`
- M5 状态：不得标记为完成
- M6 许可：不允许进入

## 1. 独立性、权限边界与范围

本审计由新的独立审计 agent 执行。既有章节审计、定点复核和工作包状态只用于定位曾经发生过的争议，不作为当前结论的替代证据。公式、数值、代码、链接、来源和授权边界均以本次读取的当前文件内容重新判定。

审计过程保持只读。除本报告外，未修改教材、提纲、来源、推导、代码、练习、工作包、README、决策记录、主计划或进度台账；`py_compile` 使用进程内临时目录，不在项目内生成或改写字节码。

直接受审范围包括：

- `08_audits/M5_stageC_work_package.md` 与只读状态参照 `08_audits/progress_tracker.md`；
- 第 5、6、7、8、10 章各自的 `outline.md`、`sources.md`、`chapter.md`、`examples.md`；
- `04_derivations/stageC/README.md` 与五个推导文件，覆盖 D-C01—D-C08；
- `06_exercises/03-stageC/` 的五章问题/解答及综合问题/解答，覆盖各章 Q 题与 C-C01—C-C10；
- `03_textbook/chapters/stageC_self_study_guide.md`、`03_textbook/stageC_label_semantics_template.md`；
- `05_code_exercises/stageC_teaching_scf/` 的五个源材料文件，覆盖 T-C01—T-C10；
- 统一记号、中央来源台账、本地来源登记、`decisions.md`、`master_execution_plan.md`、`learning_route.md`、未决决策及项目 README。

## 2. 当前快照冻结

本次冻结 61 个文件。清单按 POSIX 相对路径排序，每行内容为 `相对路径<TAB>文件 SHA-256<LF>`；该清单本身的 SHA-256 为：

`afc2f6ef4e30b02564982438e7c61ec2d34ed2d92cfe191708ae874a166d44a7`

该摘要不包含本报告，避免报告自指。完整逐文件哈希见附录 A。

## 3. 来源、公式与材料覆盖矩阵

| 单元 | 主要来源等级与边界 | 公式/对象复核 | 材料链 | 判定 |
|---|---|---|---|---|
| 第 5 章；D-C01/D-C02 | FND-01、FND-07、FND-08 为教材/讲义主线；C-FND-03、DH-01 只作 KS/DeepH 接口。BO 几何项、1RDM 与 HF 代数按 `DIRECT_DERIVATION` 使用，有限模型按 `PEDAGOGICAL` 使用 | 电子—核到固定核方程、导数耦合、对角 Berry 连接、Born–Huang 修正、determinant 反对称/归一化、1RDM trace/正性/幂等边界、HF Coulomb/交换及双计数均成立 | outline/sources/chapter/examples、Q5-01—Q5-10 与解答、C-C01 均可定位 | `PASS` |
| 第 6 章；D-C03/D-C04 | C-FND-02—07 分别承担 HK、KS、Mermin、Levy、Lieb 与简并/多变量边界；未把 Levy/Lieb 冒写为 HK 1964 的直接推论 | 固定问题族与势常数规范、共同基态步骤、简并纯态/系综边界、纯态与系综 constrained search、`minimum`/`infimum`、`X=L^1\cap L^3` 与对偶势空间、凸下半连续闭包、KS 约束变分、Hartree 导数、单电子抵消到常数、本征值和双计数、Mermin/smearing 语义均闭合 | Q6-01—Q6-10、C-C02/C-C03 与推导、例题、正文一致 | `PASS` |
| 第 7 章；D-C05 | C-NUM-01、C-NUM-02、FND-01 支持 SCF 固定点、混合、病态与成本语境；未声称某一混合器普遍最优 | D-C05 与 Q7-03 解答正确给出 Fréchet 余项 `o(||e||)`，固定点、Jacobian、谱映射、非正规瞬态、预条件约束和双停止判据均成立；但章正文把同一假设下的余项错误加强为二阶 `O(||e||^2)` | Q7-01—Q7-10、T-C01—T-C04 和 C-C04/C-C05 可定位；正文与推导/题解在余项阶数上不一致 | `BLOCKING`：M5-C-FINAL-B01 |
| 第 8 章；D-C06/D-C07 | FND-01、C-NUM-02/03、C-FND-04、DH-07 分别限定基/赝势/有限温度/投影接口；未把历史方法当作现代后端接口 | Galerkin 离散、平面波 `S=I` 条件、非正交 `Hc=ESc`、合同变换、正交投影、非正交双侧 `S_B^{-1}` 回投、等谱矩阵差和多轴误差均成立 | Q8-01—Q8-10、T-C05—T-C09、C-C06—C-C08 均可定位；三级提纲与最终章号存在导航漂移 | 公式与验证 `PASS`；见 N01 |
| 第 10 章；D-C08 | C-LOC-01 只支持条件化近视性；FND-01 与 DH-01 只支持局域基/DeepH 表示接口；未外推通用指数率或通用 cutoff | 近视性、1RDM 衰减、固定基 `H/S` 稀疏三对象分离；绝缘体/金属、温度、维数、长程 Coulomb、基变换、Hermiticity 配对与截断误差边界均成立 | Q10-01—Q10-10、T-C10、C-C09/C-C10 可定位；三级提纲末段与最终章号存在导航漂移 | 公式与验证 `PASS`；见 N01 |

五章依赖顺序 `5 -> 6 -> 7`、`8 <- 6/7/阶段 B`、`10 <- 5—8/阶段 B` 闭合。材料建设模式仍保留教材、推导、例题、逐题解答、代码、失败注入和独立审计证据，没有以取消学习者闭卷作答为由降低知识、来源或验证强度。

15 个章节来源 ID（C-FND-02—07、C-NUM-01—03、C-LOC-01、FND-01/07/08、DH-01/07）全部存在于中央 `source_table.csv`，各章 `sources.md` 的用途与禁止外推项未发现越权。真实后端接口均保持待 M8/M9 冻结或验证。

## 4. D/T/C/Q 定位和相互一致性

| 对象 | 计数与定位 | 结果 |
|---|---|---|
| D-C01—D-C08 | `04_derivations/stageC/README.md` 可定位到五个推导文件、对应章节和练习 | 8/8 可定位；除 B01 所述正文阶数记号外，推导链一致 |
| T-C01—T-C10 | 工作包、代码 README、`run_experiments.py` 与自学指南均使用同一编号 | 10/10 存在；两组 CLI 均 10/10 pass，所有预期失败均被捕获 |
| 五章 Q 题 | Q5、Q6、Q7、Q8、Q10 各 10 题 | 问题/解答 ID 逐项严格相等，50/50 配对 |
| C-C01—C-C10 | comprehensive problem/solution | 10/10 严格配对；C-C07 明确区分四维 T-C07 与十二维 T-C08；C-C08 明确七层技术检查加独立审计 |
| 自学导航 | 能力 -> 教材 -> 推导 -> 例题 -> 问题 -> 解答 -> T-C 代码 -> 失败诊断 | 全链可走通，活动链接有效 |

## 5. 关键解析与数值独立复算

本节数值由独立短程序从冻结公式重建，未调用 `run_suite` 或项目测试函数；另对五章 `examples.md` 的 15 个 Python 代码块和 Q6 解答中的 1 个代码块逐块执行，16/16 退出码均为 0。

| 项目 | 独立复算结果 | 冻结判据 | 判定 |
|---|---:|---:|---|
| T-C01 固定点 | `(0.375, -0.4, 1/14)` | 解析值 | `PASS` |
| T-C01 `alpha=2` 恰 12 次更新 | `r12/r0 = 309.1761916881516`，保存 13 个状态残差 | `>10`；更新数必须为 12 | `PASS` |
| T-C02 正例 | 第 16 步；残差 `8.613820050582771e-10`；密度 `(0.5166646086469048, 0.4833353913530952)` | `<1e-9`，归一化/正性/shape/有限性 | `PASS` |
| T-C02 失败 | 20 步末残差 `1.3531192579224054` | `>1.3` 且拒绝 | `PASS` |
| T-C03 伪能量见证 | fake energy change `3.4980818644017046e-13`，同时密度残差 `1.316815663204585` | `<1e-10` 且 `>1`，双判据拒绝 | `PASS` |
| T-C05 | 正序列末三级误差 `(0.008, 0.002, 0.0005)`；负序列末误差 `0.008` | 多层正例通过；负例 `>0.005` | `PASS` |
| T-C06 | `I0(1)=1.2660658777520084`；固定偏置后总误差约 `0.01` | 采样轴通过但总误差 `>0.005` | `PASS` |
| T-C07 | 广义谱 `(-1.2,-0.1,0.8,2.0)`；忽略 S 最大差 `0.9674651567663939`；归一残差 `1.49e-16` | 谱差 `<1e-11`、残差 `<1e-12`、错误普通谱差 `>0.1` | `PASS` |
| T-C08，d=12 | 丢失范数 `0.95985867258085`；等谱矩阵差 `0.23306075775057758`；谱差 `4.44e-15` | `>0.9`、`>0.15`、`<1e-12` | `PASS` |
| T-C08，d=16 | 丢失范数 `0.9833167163767138`；等谱矩阵差 `0.17451989619254055`；谱差 `4.44e-15` | 同上 | `PASS` |
| T-C09 | 67 条必填路径；47 个对抗变异 = type 9 + shape 11 + hash 8 + M8 choice 19 | 67/67 删除失败，47/47 变异拒绝 | `PASS` |
| T-C10，N=64/48 | 指数斜率均 `-0.49999999999999994`；代数尾外推残差均 `0.8429707836304159` | 斜率误差 `<1e-12`；尾残差 `>0.8` | `PASS` |

工作包、章内例题、推导、综合解答和 JSON 的上述数值一致。T-C10 的每个截断指标由原矩阵与截断矩阵重算，最大记录差为 0。

## 6. 固定解释器、命令与结果

固定解释器：

`C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`

实际环境：Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0，与 `requirements.txt` 和代码 README 完全一致；依赖仅为精确固定的用户态 `numpy==2.3.5`、`scipy==1.18.0`。本次未执行安装。

| 命令/检查 | 结果 |
|---|---|
| 版本断言 | 3 项全部通过 |
| `python -m pip check` | 退出码 0；`No broken requirements found.` |
| 对 `teaching_scf.py`、`run_experiments.py`、`test_teaching_scf.py` 执行 `py_compile` | 3/3 通过；编译目标位于自动清理的临时目录 |
| `python -m unittest discover -s .\05_code_exercises\stageC_teaching_scf -p 'test_*.py' -v` | 9/9 通过，退出码 0 |
| CLI seed 20260805 / model-size 12 / grid-size 64 | 退出码 0；`overall_pass=true`；T-C01—T-C10 全 pass；输出 SHA-256 `9aa7ccad03a3237056e122950f21ad44a2441933a63b6bfc82efe367eb0730ce` |
| 同一 CLI 第二次运行 | 字节相同；SHA-256 相同 |
| CLI seed 20260806 / model-size 16 / grid-size 48 | 退出码 0；`overall_pass=true`；T-C01—T-C10 全 pass；输出 SHA-256 `ce52babd2b0c839646a0a28929dda87f26a2cb27b202fc50d28fd6cd4db4c5a4` |
| 同一 CLI 第二次运行 | 字节相同；SHA-256 相同 |

两组 JSON 均含 `conventions_version=stageC-v1`、`backend=synthetic`、固定环境、seed/维数/网格、每项实际指标、阈值和预期失败证据；没有 NaN、Infinity、墙钟时间、临时路径或无序随机对象。CLI 退出码 0 在实现中受到正例断言和预期失败断言共同约束。

## 7. 标签模板专项复核

`REQUIRED_PATHS` 与工作包第 8 节的最低契约在语义上逐项相同，共 67 条，包含输入/输出制品数组内部的 `uri_or_path` 与 `sha256`。正例记录为 `stageC-label-v1`、`generation_status=SYNTHETIC_M5`。

验证层次实际区分为：

1. 67 条路径存在性；
2. 标量、数组、映射类型，有限值，shape 与数组间关系；
3. 四个 SHA-256 的 64 位小写十六进制格式及按 seed/冻结合成内容重算；
4. 14 个 `UNRESOLVED_M8` 路径和 7 个合成白名单对象；
5. SCF、投影、谱和截断等数值结构；
6. 单位、轨道顺序、bra/ket、位移方向、Fourier、规范与 overlap 语义；
7. 矩阵、谱、目标子空间和适用物理量的前向验证；
8. 独立审计。

67 个删除负例均抛出含完整缺失路径的 `ValueError`。47 个对抗变异全部被拒绝并定位字段。材料明确说明 schema pass 只证明最低契约，不证明理论选择、标签矩阵、能带或物性正确，因此未发现把 schema 通过等同物理正确的越权结论。

## 8. 结构、MathML、字节与链接检查

结构检查采用 61 文件范围，其中 55 个 Markdown 文件使用 Pandoc 3.6.4 和输入格式 `markdown+tex_math_single_backslash`，从而把项目采用的 `\(...\)` 与 `\[...\]` 均按数学对象处理。

| 检查 | 结果 |
|---|---|
| 严格 Pandoc -> HTML5/MathML | 55/55 退出码 0，无警告 |
| MathML XML 解析 | 2,109/2,109 片段通过 |
| 活动本地链接 | 145/145 目标存在；0 断链 |
| 裸 CR | 0 |
| C0 非法控制字符及 DEL | 0 |
| 空文件 | 0 |
| 五章问题/解答 ID | 50/50 一一对应 |
| 综合问题/解答 ID | 10/10 一一对应 |
| 章内 Python 代码块 | 15/15 通过 |
| 练习解答 Python 代码块 | 1/1 通过 |

自学指南能够从能力定位到教材、推导、例题、问题、解答、代码和失败诊断；其直接链接均有效。两个提纲同步问题列入 NON_BLOCKING，而不是把已有正文内容误判为缺失。

## 9. 授权边界与外部动作

当前材料、代码和合成记录没有安装或调用真实 DFT/DeepH 后端，没有下载正式数据，没有生成正式标签，也没有把材料、泛函、赝势/全电子、局域基/平面波、采样、投影工具、DeepH 版本、自旋/SOC 或计算资源静默冻结为实践选择。

`decisions.md` 的 D-009 只授权必要的 Python 用户态依赖且要求版本固定；当前实际环境与 README 一致。D-010 与 D-011、主执行计划、学习路线、未决事项、工作包、自学指南和各章边界一致：M8 前保持实践对象未决；M7-I 通过后才准备 M8 集中决策；即使 M8 已冻结，M9 的正式安装、下载、标签生成或复现实验仍需明确执行授权。未发现授权弱化。

## 10. BLOCKING

### M5-C-FINAL-B01：SCF 正文在仅假设 Fréchet 可微时错误声称二阶余项

- 文件：`03_textbook/chapters/07_scf_algorithms/chapter.md`
- 位置：第 143—164 行，尤其第 154—155 行和第 161—164 行。
- 当前内容：先仅假设 `F` 在固定点附近 Fréchet 可微，随后写

  \[
  F[n_*+e_m]=n_*+J_*e_m+O(\|e_m\|^2)
  \]

  并在混合误差递推中继续使用 `O(||e_m||^2)`。
- 错误机制：Fréchet 可微一般只保证余项为 `o(||e_m||)`。要得到 `O(||e_m||^2)`，需要更强条件，例如导数在邻域内局部 Lipschitz，或二阶导数存在并在相应邻域有界。正文没有声明这些条件。
- 内部反证：`04_derivations/stageC/07_scf_fixed_point.md` 第 88—107 行和 `06_exercises/03-stageC/07_scf_algorithms/solution/readme.md` 第 61—75 行均正确使用 `o(||e_m||)`，所以当前教材主正文与正式推导/解答不一致。
- 风险：该写法把一阶可微条件错误加强为二阶误差界，直接影响局部收敛证明的条件语义，属于明确数学错误，而非排版偏好。
- 逐文件修复要求：在 `chapter.md` 两处把 `O(||e_m||^2)` 改为 `o(||e_m||)`，并保持后续局部结论与 D-C05 一致；或者显式增加足以推出二阶余项的正则性假设并给出依据。推荐前者，因为它与既有 D-C05 和 Q7-03 解答完全一致。修复后应重新执行该章、D-C05、Q7 问题/解答、综合材料的严格 Pandoc/MathML 和全文一致性搜索，并交由独立审计定点复核。

## 11. NON_BLOCKING

### M5-C-FINAL-N01：第 8、10 章三级提纲与最终正文编号/末段覆盖漂移

- 文件：
  - `03_textbook/chapters/08_basis_pseudopotential_errors/outline.md`
  - `03_textbook/chapters/10_nearsightedness_locality_sparsity/outline.md`
- 证据：第 8 章提纲把“全电子与赝势”列为 8.1，但最终正文 8.1 是对象链、该主题位于 8.2，后续主题整体错位，且正文 8.6—8.9 没有对应提纲段；第 10 章提纲 10.5 是“例题、代码与诊断”，最终正文 10.5 是“标签局域性声明”，正文 10.6/10.7 未进入提纲。
- 边界：正文、推导、自学导航、练习和链接已经覆盖这些内容，故没有造成核心材料缺失或错误引用，本次列为非阻塞导航一致性问题。
- 逐文件修复要求：把两个 `outline.md` 更新为与最终 `chapter.md` 的一级/二级编号和主题一致；不得删除现有来源、公式、例题或失败边界。

### M5-C-FINAL-N02：根 README 的 M5 当前工作描述滞后

- 文件：`README.md`
- 位置：第 11 行。
- 证据：该行仍称“当前建设自学导航、标签语义模板和综合练习，随后执行总审计”，而工作包与进度台账已明确 M5-09 完成、M5-10 正在执行。
- 边界：`08_audits/M5_stageC_work_package.md` 与 `08_audits/progress_tracker.md` 的正式状态均正确，故不影响本次门控事实判断。
- 逐文件修复要求：在 B01 修复和独立定点复核后，按实际门控状态更新 README；在独立复核通过前不得提前写成 M5 完成或已进入 M6。

## 12. 最终判定

当前快照的来源分工、BO/HF/DFT/KS/SCF/离散/投影/近视性主体内容、D-C01—D-C08、T-C01—T-C10、C-C01—C-C10、50 道章题与解答、schema 强验证、固定环境代码、两组冻结 CLI、MathML、链接、字节结构和 M8/M9 授权边界总体成立。

但是，M5-C-FINAL-B01 是当前主教材中的明确数学条件错误。总门控规则要求任何数学错误均记 `BLOCKING`，因此不能用 D-C05 和题解中的正确版本替代修复正文，也不能因分项审计曾通过而忽略。

最终结论为：

- `FAIL`
- `BLOCKING=1`
- `NON_BLOCKING=2`
- 不允许将 M5 标记为完成
- 不允许进入 M6

只有修复 M5-C-FINAL-B01，并由独立审计对修复后的新快照确认 `BLOCKING=0`、给出明确许可后，M5 才可完成并进入 M6。N01/N02 应同步关闭，但不得在复核完成前预写通过状态。

## 附录 A：61 文件当前 SHA-256

```text
00_scope/learning_goal.md  6be732a2675ff568991907e4e69b03717f12d7bcc6e3df79aba31734db855451
00_scope/learning_route.md  352c853017f6e84f26b59023e5432d611bc18f48e6ed7e0e853af809a531baca
00_scope/master_execution_plan.md  67bc9a6c77f4338629eaca0a64ff7bfb7b43cd31633bc91155d6e74ade9c6e3c
00_scope/prerequisite_map.md  08ebdf87330b2cd3a25be03e043069e7d510bb8baa193fb5bee0d5980a04dc85
00_scope/unresolved_decisions.md  92b403fe7b09a3bb1a3a7c45f355d3498198f5db5f2e70b711d0fab0e24c6a60
01_sources/README.md  96cdec62825a7c4a69f8d481af05d09a58667b3d6ef66bdd52881ec2cd38c93a
01_sources/bibliography.bib  289ea496144d01b5582a4a480292ec0bd65f87d51f5920ad4b9ad2b69f2f962e
02_source_ledger/claims_and_sources.md  1b85f724e85e178500cdb15376e7953f8e787467c0f6af448cefa0e2499696d5
02_source_ledger/literature_map.md  739bf54e720deffb1d53a4be059c1430411a25bf7d7e99539fbf7526b5179db1
02_source_ledger/source_table.csv  29c3bd17ff9731dd0d3d2d563a93531e42f867bad6793f6622d275af9cafca4e
02_source_ledger/version_registry.md  48428cb61b64311c00a42e113eb7ca36855ba800625713f160bf2008f4c938a8
03_textbook/chapters/05_many_electron_mean_field/chapter.md  ee17931f2a4d4ff0ba036f9ab714c4cc8b3486c5775162610a2e25839a77058c
03_textbook/chapters/05_many_electron_mean_field/examples.md  9740f46029cd31c08fe0215b9a6ef7809f0cf2c90b77ee3123f47b9bd4217ba6
03_textbook/chapters/05_many_electron_mean_field/outline.md  0032025037bdcd0d1c0dc34a8692f24e588cc425a1bb732338325c5c9a38e54e
03_textbook/chapters/05_many_electron_mean_field/sources.md  1e2ba235c96269d0f0820f13c7483c9591d024d0168700ce8f97f8613af92f07
03_textbook/chapters/06_kohn_sham_dft/chapter.md  c8615170818e798a2ee2f5b663e984a63683841983c5f6345683a92173f2f859
03_textbook/chapters/06_kohn_sham_dft/examples.md  d087d0d7f4a845c582786577c0f437cbbe32acc4c55ca21a02ee2499f0d82b49
03_textbook/chapters/06_kohn_sham_dft/outline.md  d6df864f953a7d9e6f94cbb6f7283715f23485ecf80c23f1ab99275fa6347489
03_textbook/chapters/06_kohn_sham_dft/sources.md  7acfdac4106c0930b54d469dbad35ba9a8f6b00c05d1f8e4d124f9df52cc4bfd
03_textbook/chapters/07_scf_algorithms/chapter.md  2a493af5d5168e52b91e4ec61b15952d9dcaa11fa4238e79a2dcd8403261b431
03_textbook/chapters/07_scf_algorithms/examples.md  4a98a7601e2225e5265e9fb25484f906e01acbc995ed91fa780666152f83b803
03_textbook/chapters/07_scf_algorithms/outline.md  d188bbedcd8b58b0b8bd9f9526e786264e44b999f9b0b93d81b292da36c5cc8f
03_textbook/chapters/07_scf_algorithms/sources.md  af7837e0605f523ea1b476548f815b7b71742965ab2028f56625cec5b107f605
03_textbook/chapters/08_basis_pseudopotential_errors/chapter.md  cb8a8dc8b81705640487e0e9528c2699df749ab3b9a72beb3f8f640e11c2c85b
03_textbook/chapters/08_basis_pseudopotential_errors/examples.md  317da0aff7c10ca9f373d32766e261d37885c630694526635f36ac0c4105408a
03_textbook/chapters/08_basis_pseudopotential_errors/outline.md  f27dc48eb308f00558eae8f5e4cfcc9c4376d580a1a2a928e1ab1cd291b29208
03_textbook/chapters/08_basis_pseudopotential_errors/sources.md  18fcdfe53d44b1ef9217d2e9193a4c98817751eeb60d5fc4461397e5f11587b1
03_textbook/chapters/10_nearsightedness_locality_sparsity/chapter.md  d5f2d603be69814f162835123baef71bfe2135a57c629d16c2c848afa62bc385
03_textbook/chapters/10_nearsightedness_locality_sparsity/examples.md  30cb8ecc09c5de5f14db3341bf0a71bc20405876f1f46eca8cd99681c524cdec
03_textbook/chapters/10_nearsightedness_locality_sparsity/outline.md  108989c163d1c2646f3ebcf8142b035ece96eafd0638e65465f8836986a678cb
03_textbook/chapters/10_nearsightedness_locality_sparsity/sources.md  830d74af4fbfc1accbbbf2aa9bfab1917f28f56d7c24fa78850b5f67ed16f25e
03_textbook/chapters/stageC_self_study_guide.md  6ee83c5c64ac8b095ae742f657a264d78755d2a3c83d776e7b0aa6af0c6b48af
03_textbook/notation.md  576b5222c54206dbd1d48043e2719c6888fde35ebbc207fa8be5070b0cd80398
03_textbook/stageC_label_semantics_template.md  5cc2b7778739f7d46e9fab64f8a9605f0d7abfc0a5d107f2a0746d78569438cc
04_derivations/stageC/05_many_electron_mean_field.md  01385729d1d0df6b50b3e4ef0e9624959845d2fd55e2a49d0d28e1009b7f64d2
04_derivations/stageC/06_kohn_sham_variation.md  9986fce7facdeabe55cbf6dcc8e5c1dd6c86e0bb7ab7ecfdd0ba7a5d16975335
04_derivations/stageC/07_scf_fixed_point.md  0353ccca35d27e357604e189c139c8a1f2bdfc47d57b217c781516165fd138b7
04_derivations/stageC/08_representation_and_label_error.md  5b432fece9975840ee655ed8cfd678bf5d54e4b7ee897f55f0d88380673c1cb7
04_derivations/stageC/10_nearsightedness_sparsity.md  708603589dceb4ec68b5a6c17b1012a97db62aeb8834b2e8ce570bd255cd191b
04_derivations/stageC/README.md  8c0a8ed24c112233d8e5f8ebf25918dd58616a4b023f1463f5971cc7b6b00a1d
05_code_exercises/stageC_teaching_scf/README.md  ff82358bd8422a6a457764c0d308bbd3f8c09d78e559567b5283eeeaff4dce70
05_code_exercises/stageC_teaching_scf/requirements.txt  cc3efbcd187c80addd5db987ee90ad17bd481814985761d7b5cfac3f0b5e10e4
05_code_exercises/stageC_teaching_scf/run_experiments.py  746681fc4bba4eee98b89870c6683c6a8251eea28be01b1d8d5fa0d81b1128e9
05_code_exercises/stageC_teaching_scf/teaching_scf.py  597af234a2688cd9cf71d2c501514ee07700a2fb0361026aef4be0221bebd867
05_code_exercises/stageC_teaching_scf/test_teaching_scf.py  688956a996a48d4a04280f3a45735b47c5d19cbc21ac9576c73c9b2057ddd59b
06_exercises/03-stageC/05_many_electron_mean_field/problem/readme.md  f93eab1ac00c1ba02858b094696686fa71b6c40748759955298088f8c9f3ccf9
06_exercises/03-stageC/05_many_electron_mean_field/solution/readme.md  4106a40cba1a278089ff86f2379e2ce5feb4bfce57b879595bc31d567a4f5db1
06_exercises/03-stageC/06_kohn_sham_dft/problem/readme.md  c32bbf291cceab5ce09117a9d75c3bd8701ff05dcd7302919ea0805f242a5e8b
06_exercises/03-stageC/06_kohn_sham_dft/solution/readme.md  beb13cd4a85837203a3806789b11368e5da1619e498dd73900afa3ce5115b63e
06_exercises/03-stageC/07_scf_algorithms/problem/readme.md  56e739cd792180a4dff5b7fbd50c224fbe59f52670f511e41084710e7ef5d986
06_exercises/03-stageC/07_scf_algorithms/solution/readme.md  9b67c6768cf350f756aaaf4755d6a07656fd57b8e425c314604f7d1413ee8b02
06_exercises/03-stageC/08_basis_pseudopotential_errors/problem/readme.md  284bc3577f1dc1eaf84fc2c7b66fdcf07c6337022fdadf9aef440eba9f7e8179
06_exercises/03-stageC/08_basis_pseudopotential_errors/solution/readme.md  9b4fadc414a1fb1856c3ba4c72ece08d1a42927098f38fb2a82e19eecb251076
06_exercises/03-stageC/10_nearsightedness_locality_sparsity/problem/readme.md  255e6749d7292ad85752ebb89b4053520840a5f06788dbe51bf49dd0616888a4
06_exercises/03-stageC/10_nearsightedness_locality_sparsity/solution/readme.md  a18a1a60fadd74a2f5f3831693c63297addfc1eaa02a5d7ee9e5ff16d5eae2ad
06_exercises/03-stageC/comprehensive/problem/readme.md  6a93b0a90521df3f4514ba387cd0426c451b9122c5949b447c2536a21c3947f6
06_exercises/03-stageC/comprehensive/solution/readme.md  5f7e33ba67e0951eb025f50139227cb848e8c59b6ffb451a93c270b2a7ec2ff2
08_audits/M5_stageC_work_package.md  2835ba288ebb4bd201c8fcd6b069a96e74e90d57abf4175bffec82635140a07a
08_audits/progress_tracker.md  cb921e43f65cc40d62b25682003138708d498e2461977b2072c2058fa7b4ec15
README.md  6201d3665bcc6d5dfaf06dffb85885efadb9a957a38c8cbe823336b5b4a2d917
decisions.md  272aed3ad8b771ea0d80fd1c06becedb9694a29a994323f820c61e9b2c0ce318
```
