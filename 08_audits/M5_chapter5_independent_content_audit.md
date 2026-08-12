# M5-02 第 5 章独立内容审计

- 审计日期：2026-08-04
- 审计对象：第 5 章“多电子问题与平均场”的资料、提纲、正文、例题、D-C01—D-C02 推导、Q5-01—Q5-10 及参考解答，并核对中央来源台账、书目、阶段 C 工作包和决策记录
- 审计性质：独立材料完备性、可自学性、公式条件、来源边界与可验证性审计
- 总体结论：`BLOCKING`
- `BLOCKING`：3 项
- 非阻塞项：1 项
- 是否允许 M5-02 标记为 `COMPLETED`：**否**
- 是否允许启动 M5-03：**否**。应由主 agent 完成 B01—B03 的最小修复，再由独立审计执行定点复核；本报告不以主 agent 自检替代复核结论。

## 1. 审计范围与 SHA-256 快照

本次逐项核查下列文件。除新增本审计报告外，未修改任何被审材料。

| 文件 | 审计时 SHA-256 |
|---|---|
| `03_textbook/chapters/05_many_electron_mean_field/sources.md` | `D0F0A2AD4247B298816F5912DBECDFFFA3045AC459F1381B86E6139A24E2D0F5` |
| `03_textbook/chapters/05_many_electron_mean_field/outline.md` | `0032025037BDCD0D1C0DC34A8692F24E588CC425A1BB732338325C5C9A38E54E` |
| `03_textbook/chapters/05_many_electron_mean_field/chapter.md` | `BC97AFF19EFBE890DFEFDDBD28CB4AB5A65E61EDB98FFB8D47F9A7628B4B1F52` |
| `03_textbook/chapters/05_many_electron_mean_field/examples.md` | `9740F46029CD31C08FE0215B9A6EF7809F0CF2C90B77EE3123F47B9BD4217BA6` |
| `04_derivations/stageC/05_many_electron_mean_field.md` | `1096C21CABDC668BE194AAC8633E6CAD3F6AB591A53065243B05EA0D451C4EFF` |
| `06_exercises/03-stageC/05_many_electron_mean_field/problem/readme.md` | `F93EAB1AC00C1BA02858B094696686FA71B6C40748759955298088F8C9F3CCF9` |
| `06_exercises/03-stageC/05_many_electron_mean_field/solution/readme.md` | `D1820D3D85C931F639DA32195185CABCB4CF0BA1BECFD83D48DF962A4F796EC0` |
| `02_source_ledger/source_table.csv` | `A00BE21BFED1962D2C4FA4E5E79EDA31055CC89A2AB6DCD3F9C3FB16A11E70A4` |
| `01_sources/bibliography.bib` | `935DAA9042635B7ACF7F82DE600B237E28A6F8F699F8A0494E14EAD458973895` |
| `08_audits/M5_stageC_work_package.md` | `AB9C0936890B77684C19E4D56CF819EB855B3656D4FBA3B190EBE2B2BC9B1AE0` |
| `decisions.md` | `072992EFCA9474B738CB48E7C18F85342FDDC4ABA7D25F62EB572552E429455C` |
| `01_sources/papers/li_et_al_2022_deeph.pdf` | `92C5A783B46475634A17D2D5F6557D8DE68D2F789F8DFB66182F56862580EC61` |
| `01_sources/documentation/martin_2004_table_of_contents.pdf` | `F58D75B9A3D3E85B2F94ED42FA070F090FAD075C0D9BABF4986C42591D1F69B8` |

后两份本地 PDF 的实际哈希与 `01_sources/README.md` 冻结值一致。

## 2. 已通过的内容与来源边界

### 2.1 来源用途

| 来源 | 独立核对结论 |
|---|---|
| FND-01 | 本章只把 Martin 2004 用作电子—核问题、BO、多电子与 HF 的教材主线，并在 `sources.md` 明确声明本地目录快照只能核版本和页码，不能替代正文公式证据；这一边界本身正确。中央条目的范围同步问题另列 N01。 |
| FND-07 | MIT 5.73 固定讲义直接覆盖完整电子—核 Hamiltonian、固定核电子问题、绝热基展开、导数耦合和近简并失效机制。本章没有把质量比提升为所有材料和激发态的普适误差界，使用未越权。 |
| FND-08 | MIT 10.675 Lecture 3 直接覆盖 Hartree 自洽、Slater determinant、Coulomb/交换项与 Fock 算符。本章对归一化、1RDM 和双计数作了独立推导，没有把简短讲义冒充完整函数分析证明。 |
| C-FND-03 | 用作 KS 非相互作用参考体系的后续接口是合理的；但当前正文和题解缺少 representability/系综条件，形成 B03。 |
| DH-01 | 本地原始 DeepH 正文独立复核确认其对象为特定 DFT 设置和局域 AO 表示下的 Hamiltonian 矩阵学习，目标是绕过新结构上的耗时 SCF。正文正确拒绝把该矩阵解释为精确多体 Hamiltonian、真实多体波函数、1RDM 或基组无关对象。 |

### 2.2 D-C01—D-C02 与对象层级

除 B01 所述单面截断条件外，D-C01 的主推导正确：完整 Hamiltonian 的五类项、固定核后 `H_e(R)` 与 `E_NN(R)` 的区分、绝热基乘积求导产生的一阶 `d_ab^I` 与二阶 `tau_ab^I`、非简并条件下导数耦合的能隙分母，以及严格简并点不能直接除以零，均有明确公式和边界。

D-C02 的 determinant 反对称性、正交占据轨道下的 `1/sqrt(N!)` 归一化、occupied-unitary 仅引入 `det(U)` 整体相位、占据投影不变、1RDM 的 trace/Hermiticity/正性、单 determinant 幂等性及闭壳层空间轨道约定均正确。双 determinant 相关纯态反例的四个自然占据数均为 `1/2`，确实给出纯态非幂等 1RDM。HF 的 Coulomb/交换、自旋选择、自项抵消和占据本征值双计数主链也正确。

密度、1RDM、有效一体 Hamiltonian、多体波函数四类对象在正文、练习和解答中保持分离；Hartree、HF、KS 的构造对象和缺失物理没有被“平均场”一词掩盖。除 B03 的适用域缺失外，没有发现把 KS determinant 或 DeepH 输出写成真实相互作用多体态的结论。

### 2.3 例题与练习

三个例题的解析结果均独立复算通过：

- 例 5-1 在 `a=1.5, Delta=0.2` 时，中心能隙为 `0.4`；以连续相位规范对本征矢作中心有限差分，得到导数耦合 `3.7499999997689373`，与解析值 `a/(2 Delta)=3.75` 一致。
- 例 5-2 的两电子 determinant 归一化、交换反对称、1RDM trace `2`、投影幂等和 occupied-unitary 不变性均成立。独立复矩阵复算的投影幂等误差为 `2.07e-16`，unitary 后投影差为 `9.53e-16`；相关纯态反例的非幂等范数为 `0.5`。
- 例 5-3 的内嵌 NumPy 代码原样执行通过。`(t,U)=(1.0,2.0)` 时占据本征值和为 `0`、双计数为 `1`、平均场能量为 `-1`；`(0.7,3.2)` 时相应值为 `1.8`、`1.6`、`0.2`，均与 `-2t+U/2` 一致。

Q5-01—Q5-10 与参考解答严格一一对应，无缺题或错位。Q5-02、Q5-04、Q5-06、Q5-09 均提供可复核公式链；Q5-10 列出固定核、理论近似、赝势/全电子、基/采样/收敛、表示、有效一体对象、能量口径和训练分布等十类错误，并给出不越界替代表述。材料建设模式没有恢复学习者闭卷作答门槛。

上述通过项不能抵消以下三个公式条件和材料闭合性阻塞。

## 3. BLOCKING

### B01：D-C01 单势能面方程的截断前提与实际删项不一致

**位置：**

- `04_derivations/stageC/05_many_electron_mean_field.md:100-112`；
- 相关概括见 `chapter.md:82`。

**问题：**

推导先得到包含全部 `d_ab^I` 和 `tau_ab^I` 的耦合核方程。D-C01.3 随后只声明“忽略与 `b != a` 的非对角耦合”，却直接写出仅含裸核动能和 `U_a(R)` 的方程。该方程同时删除了对角 `d_aa^I` 与 `tau_aa^I`。下一段虽然指出更精确处理可以保留 Born–Huang 修正和 Berry 连接，但没有把删除对角项所需的局部规范选择与额外近似写进当前方程的前提。因此，“只忽略非对角耦合”不能推出展示的方程，条件与结论不闭合。

**为何阻塞：**

D-C01 是本阶段冻结的关键推导。当前写法会使自学者误以为选择单电子面便自动消除全部对角几何项；在存在非平凡 Berry 连接、简并子空间或需要对角 Born–Oppenheimer 修正的情形下，该推断不成立。这不是措辞偏好，而是推导删项条件缺失。

**最小修复要求：**

在正文和 D-C01.3 中显式区分：仅投影到单面后的对角有效核方程；对角 Berry 连接/规范协变动能；对角 Born–Huang 修正；以及进一步采用局部平行输运规范并忽略相应对角修正后才得到当前最简方程。必须说明该局部规范不能无条件替代全局拓扑条件，简并子空间需矩阵值处理。Q5-02 参考解答应至少能定位这一删项条件。

### B02：三级提纲冻结的 5.5.4 授权边界在正文中缺失

**位置：**

- `outline.md:27` 冻结“5.5.4 M8 前授权边界”；
- `chapter.md:305-344` 的 5.5 节实际止于 5.5.3；
- 全局规则见 `decisions.md:84-93` 与 `M5_stageC_work_package.md:7`。

**问题：**

正文没有 5.5.4，也没有在本章集中写出 D-010 的 M8/M9 双授权规则。资料包和题目虽声明本章不使用真实后端、真实材料或正式标签，但未完整说明：M8 前禁止安装 DeepH 本体、下载正式训练数据、生成正式 DFT 标签或隐含选择材料体系/DFT 后端/实践软件版本；准备进入 M8 时须暂停集中决策；M8 冻结后、M9 正式安装/下载/复现实验前仍须再次取得明确执行授权。

**为何阻塞：**

本章三级提纲与正文不闭合，且缺失内容正是用户明确规定的外部动作安全边界。全局决策记录存在不能替代章内已冻结小节；材料建设门控要求教材本身可自学、可定位，不应要求读者通过项目管理文件补足缺章。

**最小修复要求：**

补齐正文 5.5.4，逐项写出 M8 前四项禁止、M8 集中决策暂停点和 M9 外部动作前二次授权点；说明本章所有矩阵、轨道和模型均为解析或合成教学对象。章节自检或 Q5-10 解答应提供到该小节的定位。

### B03：KS 辅助体系陈述缺少非相互作用 representability 与系综占据条件

**位置：**

- `chapter.md:307-317`；
- `solution/readme.md:102-113` 的 Q5-07 表；
- `sources.md:10` 对 C-FND-03 的边界仅写明“不把 KS determinant 当作真实多体波函数”。

**问题：**

正文无条件写成 KS 非相互作用参考体系的“基态密度与目标相互作用体系的基态密度一致”，并统一称“KS 轨道组成的 determinant”；Q5-07 解答同样写成“辅助 determinant 满足”反对称性。该表述没有声明所讨论密度的非相互作用 `v`-representability 条件，也没有区分整数占据的单 determinant 表示与简并/分数占据时的非相互作用系综表示。

**为何阻塞：**

本章将 KS 作为后续接口，接口的任务正是阻止对象层级越权。缺少 representability 和系综边界会把带条件的 KS 构造误读为任意相互作用密度都由一个纯 KS determinant 无条件表示。这与本阶段要求保留公式条件和来源边界不相容，不能全部推迟到第 6 章。

**最小修复要求：**

在 5.5.1、Hartree/HF/KS 比较表和 Q5-07 解答中增加适用域：在假定非相互作用可表示且采用整数占据的常规零温情形，可用单 determinant 表示辅助体系；存在简并、分数占据或更一般可表示性问题时，应使用非相互作用系综/占据数表述，不能强称单 determinant。`sources.md` 的 C-FND-03 边界也应同步登记该限制，同时保留“辅助对象不等于真实多体波函数”。

## 4. 非阻塞项

### N01：中央 FND-01 条目的范围说明未与本章来源包同步

`sources.md:7` 明确使用 Martin 2004 第 3 章第 52—70 页和第 5 章第 100—116 页支持本章；阶段 C 工作包也把 FND-01 的范围扩展到第 3、5—9、11—15 章。然而 `02_source_ledger/source_table.csv:19` 的 `primary_claims` 仍只列周期固体、KS/SCF、局域轨道和非正交性，`notes` 仍只列第 4、7、9、14、15 章。这不会使当前由 FND-07/FND-08 和直接推导交叉支持的公式失效，因此不单独阻塞 M5-02；但它破坏中央来源台账与章级来源包的一致性。

应在 B01—B03 修复时同步更新 FND-01 中央条目的 `primary_claims` 和页码范围，保留“目录快照只验证版本/定位、不替代正文证据”的限制。定点复核应确认 CSV 仍为固定 17 字段、source ID 无重复，且 BibTeX 书目未发生无依据漂移。

## 5. 静态、链接与数值检查

### 5.1 严格 Markdown/MathML 与控制字符

对七份章节 Markdown 使用 Pandoc：

```text
pandoc --from=markdown+tex_math_dollars+tex_math_single_backslash \
       --to=html5 --mathml --fail-if-warnings <file>
```

结果为 `7/7` 退出码 0。逐字符检查 C0 控制字符（允许 TAB/LF/CR）及 DEL，七份文件均为 0。未发现未闭合代码围栏或公式解析警告。

### 5.2 链接与引用定位

- FND-07 与 FND-08 的 MIT 官方 PDF 链接在审计时均返回 HTTP 200；
- C-FND-03 DOI 入口返回 HTTP 302 并指向 APS；本机后续 TLS 吊销服务器离线，故未把本机重定向后的 TLS 状态当作内容反证；DOI、卷页和书目三处一致；
- 章节指向推导、例题、问题和解答的四个本地目标均存在；
- Q5-01—Q5-10 与十个同名解答标题集合完全一致。

### 5.3 固定环境与内嵌代码

使用固定解释器：

```text
C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
Python 3.12.13
NumPy 2.3.5
```

例 5-3 的内嵌代码原样执行，全部断言通过；例 5-1 和例 5-2 使用独立实现复算，结果见第 2.3 节。测试没有安装 DeepH、没有访问正式训练数据、没有生成 DFT 标签，也没有选择真实材料或 DFT 后端。

## 6. 正式结论

第 5 章的多电子对象链、determinant 与 1RDM 主推导、HF 交换/双计数、三个例题、十道题解及 DeepH 对象边界总体扎实，静态渲染和数值复算均通过。但 D-C01 最简单单面方程的对角几何项删减条件不闭合，三级提纲所要求的 M8/M9 授权小节缺失，KS 辅助体系又缺少非相互作用 representability 与系综占据边界。这三项均直接影响公式条件、材料闭合性或对象层级，不能列为一般润色。

因此，本次正式结论为 `BLOCKING=3`：**不允许将 M5-02 标记为 `COMPLETED`，不允许启动 M5-03。** 主 agent 完成 B01—B03 并同步处理 N01 后，应由独立审计员对修订文件执行定点复核；只有复核明确给出 `BLOCKING=0`，才可更新里程碑状态。
