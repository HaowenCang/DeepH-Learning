# M6-05 第 14 章独立内容审计

## 1. 审计结论

**结论：FAIL**

- `BLOCKING = 2`
- `NON_BLOCKING = 2`
- **不允许**将 M6-05 标记为完成。
- **不允许**启动 M6-06。

第 14 章的周期图定义、有限镜像枚举证明、逐原子换胞双射、多重边规则、复杂度主项和 M8/M9 授权边界在数学主线上基本成立；独立复算也确认了代表性数值答案和规范边 ID 哈希。但当前正文、例题、推导与练习中存在系统性的行内数学定界符缺失，Pandoc 会把大量 TeX 命令作为普通 Markdown 转义并生成语义残缺的正文，而不是 MathML。主教材还没有把“cutoff 必须有限”落实到 validator 的硬失败条件。因此，当前材料尚未满足材料完备性、可自学性和可验证性门控。

## 2. 审计范围与方法

审计依据为：

- `08_audits/M6_stageD_work_package.md`；
- `03_textbook/stageD_graph_conventions.md`；
- 第 12、13 章冻结的图 schema、批处理、轨道身份与 provenance 契约；
- 第 14 章 `sources.md`、`outline.md`、`chapter.md`、`examples.md`；
- `04_derivations/stageD/14_periodic_enumeration_provenance.md`；
- Q14-01—Q14-10 与 A14-01—A14-10。

审计执行了逐行公式与条件核查、独立代数推导、确定性数值复算、规范 JSON/SHA-256 复算、题目—答案数量核对、来源与授权边界核对，以及只向标准输出转换的 Pandoc/MathML 检查。未修改任何被审材料、计划、台账、README 或代码。

独立复算结果如下：

| 对象 | 独立结果 | 判定 |
|---|---|---|
| row-lattice 例 Q14-01 | `(0.75,0.5,0.5) @ A = (2,1.5,2)` | 与 A14-01 一致 |
| 单原子单位晶胞、`r_c=sqrt(2)` | 距离 1 的 shift 6 个，距离 `sqrt(2)` 的 shift 12 个，共 18 个 | 与 A14-03 一致 |
| 例 14-5 多重镜像 | `n_x=0,-1` 两解，距离均为 0.5 | 与正文和 A14-04 一致 |
| 逐原子换胞 Q14-05 | `n'=(4,-4,-2)`，回拉为 `(1,-1,0)`，错误不变换的位移误差为 `(q_j-q_i)A` | 与 A14-05 一致 |
| 例 14-8 规范边 ID | `SHA-256 = f83e3b238ba5c1b71cc773c08afa5fab22c35c1e38c6418b629fde616f5020e3` | 与例题一致 |
| 内容数量 | 例题 8 个；题目 10 个；参考解答 10 个 | 数量门槛满足 |

## 3. BLOCKING 问题

### M6-05-B01：系统性缺失行内数学定界符，渲染后公式语义损坏

**位置：**

- `03_textbook/chapters/14_periodic_graph_neighbor_lists/chapter.md:16-46`，并系统性延续至 `58-273`；
- `03_textbook/chapters/14_periodic_graph_neighbor_lists/examples.md:19-24,43-71,80-82,95-131`；
- `04_derivations/stageD/14_periodic_enumeration_provenance.md:5-49,53-105`；
- `06_exercises/04-stageD/14_periodic_graph/problem/readme.md:13-45`；
- `06_exercises/04-stageD/14_periodic_graph/solution/readme.md:24-42,46-52,74-116,120-146`。

**证据：** 大量本应写成 `\(...\)` 的行内数学仅写成普通括号，例如正文第 16 行的 `(f_i\in\mathbb R^3)`、推导第 5 行的 `(A\in\mathbb R^{3\times3})` 和题目第 17 行的完整不等式。使用冻结的 `markdown+tex_math_single_backslash` 转换时，Pandoc 不会把这些片段识别为数学；反斜杠被当作 Markdown 转义。例如推导第 5 行实际渲染为近似 `(AR^{3})`、`(sigma_{}(A)>0)` 和 `(f_i,f_j^3)`，集合、关系符和黑板粗体信息均丢失。第 14 章正文的 Pandoc 输出仍含可见的字面 TeX 命令，而普通 `--fail-if-warnings` 返回 0，说明现有语法预检会产生假阴性。例 14-5 第 80—82 行还把 `\quad` 写成了 `quad`，在 display math 中被解释为变量乘积，而不是间距命令。D-D05 第 49 行另有 `(sigma_{\min}\)` 的不配对定界符。

这不是纯排版问题。行内公式承担了条件、量词、集合、索引和不等式的教学语义；渲染后丢失这些信息会使 D-D05/D-D07、题目条件及参考解答无法可靠自学和核验。

**关闭条件：** 对上述五个材料对象执行全量行内数学修复：所有数学表达使用有效且配对的 `\(...\)` 或 display math 定界符；修复 `\quad`、`σ_min` 片段和其他残缺命令。之后应同时满足：严格 Pandoc 转换成功；渲染产物中无本应属于数学的字面 TeX 残留；人工抽查 D-D05 条件、Q14-02 不等式、A14-03 计数、例 14-5 和 D-D07 双射均生成正确 MathML。仅获得 Pandoc exit code 0 不足以关闭本项。

### M6-05-B02：主教材的 cutoff validator 条件遗漏正无穷等非有限输入

**位置：**

- `03_textbook/chapters/14_periodic_graph_neighbor_lists/chapter.md:58-64`；
- `03_textbook/chapters/14_periodic_graph_neighbor_lists/chapter.md:263-265`；
- 对照契约：`08_audits/M6_stageD_work_package.md:176`；
- 对照推导：`04_derivations/stageD/14_periodic_enumeration_provenance.md:5`。

**证据：** D-D05 门控与推导均要求有限 cutoff，但正文只声明 `r_c>0`，硬失败列表也只列“非正 cutoff”。`+inf` 满足正数条件，却使 `ceil(r_c ||B_:k|| + 1)` 不再是有限整数，候选盒无法构造。NaN 的比较行为也不应依赖语言偶然性。当前正文会允许学习者据此写出只检查 `r_c <= 0` 的 validator，与 D-D05 的有限性前提不一致。

**关闭条件：** 在第 14 章对象定义、枚举前置条件、失败边界及相应 Q/A 验证矩阵中统一明确：cutoff 必须是有限 float64 标量且严格大于 0；NaN、`+inf`、`-inf` 和非正数均须定向失败。后续 T-D10 也应具有对应失败夹具，但本次关闭只要求先把 M6-05 材料契约冻结清楚。

## 4. NON_BLOCKING 问题

### M6-05-N01：D-D07 独立推导文件未完整冻结规范 JSON 的字节序列化参数

**位置：**

- `04_derivations/stageD/14_periodic_enumeration_provenance.md:97-103`；
- 对照定义：`03_textbook/chapters/14_periodic_graph_neighbor_lists/chapter.md:158-164`；
- 对照工作包：`08_audits/M6_stageD_work_package.md:121-129`。

**证据：** D-D07 文件将带空格和占位符的数组展示为“JSON 数组的 UTF-8 SHA-256”，但没有在该独立推导中给出 `ensure_ascii=false` 与 `separators=(",",":")`。同一个 JSON 值可以有多种合法字节表示，SHA-256 取决于字节而不只取决于抽象值。主教材和工作包已有正确参数，故总契约尚不含错误结论，但 D-D07 单独阅读时不能唯一复现 edge ID。

**关闭条件：** 在 D-D07 文件内补齐 `ensure_ascii=false`、无空格 separators、UTF-8 和字段类型/顺序，明确代码块是 schema 示意还是实际规范字节串，并用例 14-8 的已复算哈希作回归锚点。

### M6-05-N02：`L r_c` 几何支持结论未在本章原位列全成立条件

**位置：**

- `03_textbook/chapters/14_periodic_graph_neighbor_lists/chapter.md:213-233`；
- 对照契约：`08_audits/M6_stageD_work_package.md:175`。

**证据：** 三角不等式正确证明了任意不超过 L 条、每段不超过 cutoff 的已提升周期路径，其端到端位移范数不超过 `L r_c`；正文也正确否定了逆命题。但“L 层局部 MPNN 的几何影响”还依赖局部消息、同步层更新、初始特征未预编码全局结构，并且没有全局读出回灌、跨图边或越过图距离的更新。工作包 D-D04 已明确指出跳连或全局读出会改变结论，本章没有在该结论原位列出这些条件。该遗漏不会推翻当前三角不等式，但削弱了独立自学时的适用边界。

**关闭条件：** 在 14.6.1—14.6.2 原位补充上述局部性与同步更新条件，并区分“图结构可达上界”“输入特征的信息来源”和“数值上实际非零影响”；保持“几何距离小于 `L r_c` 不推出存在 L 跳路径”的现有边界。

## 5. 已通过的审计项

以下对象在当前审计中未发现新的实质错误：

- row-lattice、规范坐标、逐分量 floor、receiver/sender/shift 角色与位移方向一致；
- D-D05 使用逆晶格列范数的有限盒证明成立，float64 条件数严格阈值与 `A_-`/`A_0`/`A_+` 边界一致；扩展一层盒被正确定位为实现回归检查而非理论证明替代品；
- 零位移自环排除、非零自镜像保留、多镜像不按原子对或距离折叠；`2r_c<lambda_1(A)` 被正确表述为在精确最近晶格向量求解下保证单镜像的充分条件，且明确排除了斜晶胞逐分量折回的通用性；
- D-D07 的 `n'=n+q_i-q_j`、回拉键、双射和位移不变证明正确，位移/距离容差为 `rtol=0, atol=1e-12`；
- 直接候选复杂度、稳定排序、普通 MPNN 时间主项和第 13 章冻结激活数组字节数彼此一致，并区分构图与网络成本；
- provenance 覆盖原子对、镜像、轨道块、mask、局部与实际轨道身份，排序、批处理和换胞回拉要求行级同步；
- 8 个例题、10 道题目及 10 份参考解答均非空，包含多重边、病态晶胞、换胞错误、provenance 变异等失败样例；
- 直接来源用途与不得外推边界清楚；M8 前禁止项、M8 决策停点及 M9 再授权要求未被越权改变。

## 6. 复核要求

主 agent 应先实施 M6-05-B01 与 M6-05-B02 的修复，并处理两项非阻塞问题。完成后应由本独立审计 agent 对稳定 ID `M6-05-B01`、`M6-05-B02`、`M6-05-N01`、`M6-05-N02` 执行定点复核，同时报告新增问题数与剩余问题数。只有在 `BLOCKING=0` 且复核明确允许时，才可将 M6-05 标记完成并启动 M6-06。
