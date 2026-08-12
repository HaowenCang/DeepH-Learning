# M5-01 阶段 C 工作包阻塞项独立定点复核

## 1. 复核结论

**总判定：PASS。** 首次正式独立审计冻结的 M5-WP-B01—B04 已全部关闭；当前快照没有新增 `BLOCKING`。记录 1 项不影响阶段许可的书目元数据修正建议。

因此：

- 允许将 M5-01 标记为 `COMPLETED`；
- 允许将 M5-02 标记为 `READY` 并启动第 5 章材料建设；
- M5 后续实施仍须遵守工作包的定量契约、D-010 材料建设模式和 M8/M9 双重外部授权边界。

本复核由首次审计 M5-WP-B01—B04 的同一独立子 agent 执行。复核直接读取并计算当前文件，没有依赖主 agent 对修复内容的概括。本报告是唯一新增文件，没有修改工作包、章节资料、提纲、来源台账、计划或进度记录。

## 2. 复核对象与快照入口

主要复核对象为：

- `08_audits/M5_stageC_work_package.md`，当前 SHA-256 为 `72E9808F2AD9204B7E47C3AF7D6458EBFF36A79CBAD16289F0B64CC94B88CA58`，与复核任务指定值一致；
- 第 5、6、7、8、10 章各自的 `sources.md` 和 `outline.md`；
- `02_source_ledger/source_table.csv` 与 `01_sources/bibliography.bib`；
- `00_scope/master_execution_plan.md`、`00_scope/learning_route.md`、`decisions.md`、`08_audits/progress_tracker.md`、`00_scope/unresolved_decisions.md`；
- 首次审计 `M5_stageC_work_package_independent_audit.md` 和 M4 最终审计 `M4_stageB_final_independent_audit.md`。

## 3. M5-WP-B01—B04 逐项复核

### M5-WP-B01：关闭

当前工作包及第 6 章资料包已经分别登记：

- C-FND-02：HK 1964，只承担外势—基态密度、普适泛函和基态变分原理；
- C-FND-05：Levy 1979，只承担给定纯态 `N`-representable 密度上的反对称波函数 constrained search；
- C-FND-06：Lieb 1983，承担 Coulomb 体系函数空间、变分和凸分析形式化。

`M5_stageC_work_package.md` 明确禁止把 Levy/Lieb 形式化写成 HK 1964 的直接代数推导，并在 D-C03 中要求区分 `v`-representable/`N`-representable、纯态/系综、minimum/infimum、唯一性/简并以及密度域和拓扑条件。第 6 章 `sources.md` 把 HK、KS、Levy 和 Lieb 分别标为各自来源中的 `PRIMARY_EXPLICIT`，只把后续正交约束变分和基离散标为 `DIRECT_DERIVATION`；`outline.md` 也为 Levy、Lieb 和来源分界设置独立三级条目。

独立查询出版记录确认：Levy 论文 DOI `10.1073/pnas.76.12.6062`、PNAS 76, 6062—6065 (1979) 的题名和范围正确；Lieb 论文 DOI `10.1002/qua.560240302`、Int. J. Quantum Chem. 24, 243—277 (1983) 的书目信息正确，其官方摘要明确讨论波函数—密度联系、HK 普适泛函的定义域问题和数学基础。来源、用途和禁止外推现已闭合。

### M5-WP-B02：关闭

T-C01—T-C10 已从模型类别清单修订为可实施的测试契约。统一冻结 `float64`/`complex128`、默认范数、相对误差分母、随机数生成器、JSON 指标和预期失败的非零退出条件；每项给出模型参数、公式、参考对象、正例阈值和故障注入。

独立使用固定 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0 复算关键数值，得到：

| 测试 | 独立复算结果 | 冻结判据 | 判定 |
|---|---:|---:|---|
| T-C01 稳定固定点最终误差 | `6.9297123595e-11`，44 步 | `<1e-10`，至多 100 步 | PASS |
| T-C01 估计收敛率 | `0.5999999999`，窗口内 23 个相邻比 | 与 `0.6` 差 `<5e-3` | PASS |
| T-C01 不稳定残差增长比 | `309.1761917` | `>10` | PASS |
| T-C02 正例最终残差 | `8.6138184805e-10`，16 步 | `<1e-9`，至多 80 步 | PASS |
| T-C02 归一化误差 | `1.1102230246e-16` | `<1e-12` | PASS |
| T-C02 负例末残差 | `1.3531192579` | `>1.3` | PASS |
| T-C03 伪能量误判 | 20 个步骤同时满足伪能量差 `<1e-10`、密度残差 `>1` | 至少存在 1 步 | PASS |
| T-C05 正例最后三级参考误差 | `0.008, 0.002, 0.0005` | 均 `<1e-2`，末级 `<1e-3` | PASS |
| T-C05 非单调故障 | 32/64 相邻差 `5e-4`，128 参考误差 `8e-3` | 单对误过、完整判据拒绝 | PASS |
| T-C06 `N_k=16,32,64` 误差 | 各为 `2.2204460493e-16` | 均 `<1e-12` | PASS |
| T-C07 广义谱最大误差 | `6.6613381478e-16` | `<1e-11` | PASS |
| T-C07 忽略 overlap 的谱差 | `0.9674651568` | `>1e-1` | PASS |
| T-C08 seed 20260805 丢失范数/等谱矩阵差 | `0.9598586726 / 0.2330607578` | `>0.9 / >0.15` | PASS |
| T-C08 seed 20260806 丢失范数/等谱矩阵差 | `0.9833167164 / 0.1745198962` | `>0.9 / >0.15` | PASS |
| T-C10 指数族拟合斜率 | `-0.49999999999999994` | 与 `-0.5` 差 `<1e-12` | PASS |
| T-C10 代数族指数外推残差 | `0.8429707836` | `>0.8` | PASS |

T-C04 对 `alpha=0.10,0.25,0.40,0.60,1.00` 的扫描要求同时保留收敛和未收敛状态；独立复算中前三者分别于 61、16、13 步达到 `1e-9` 残差，后两者在 80 步未达到阈值，符合“记录终止原因而不得把最大迭代写成成功”的契约。T-C08 两个冻结种子下的等谱误差均约 `4.44e-15`，满足 `<1e-12`。

当前数值门控不会用未绑定计算的布尔量替代指标。T-C03、T-C06、T-C08 和 T-C10 原先不可执行的语义拒绝条件均已转化为带上下界的确定性负例。

### M5-WP-B03：关闭

`stageC-label-v1` 已覆盖后端名称/版本/提交、输入输出制品身份与哈希、合成结构及边界、理论与赝势/全电子身份、基/网格、自旋、采样、电子数与占据、收敛、矩阵对象/单位/轨道与原子索引、胞位移方向、bra/ket、Fourier 正逆变换、相位/规范、overlap、投影窗口/维数/损失及矩阵/能带验证、环境和审计状态。

第 8 节表内共有 67 个显式路径或数组成员标记且无重复；其中 `artifacts.inputs[]` 和 `artifacts.outputs[]` 的 `uri_or_path`/`sha256` 被明确要求对每种数组成员分别执行删除负例。T-C09 规定从该表生成单一必填集合，对每个必填路径逐项深拷贝删除，任何删除未触发带路径的 `ValueError` 都使测试失败。该契约已排除只验证顶层分组的弱 schema 检查。

M5 合成记录的真实实践值保留为 `UNRESOLVED_M8`；字段存在不等于选择软件、材料、泛函或赝势。合成制品和合成结构仍要求真实内容哈希，因此 schema 同时保持可验证性与 M8 授权边界。

### M5-WP-B04：关闭

工作包已冻结当前 Windows/PowerShell 解释器绝对路径、Python/NumPy/SciPy 版本断言、精确 requirements 安装、unittest 发现命令和两组固定 seed/model-size/grid-size 的 JSON CLI 命令。解释器实际存在，独立查询版本为：

```text
Python 3.12.13
NumPy 2.3.5
SciPy 1.18.0
```

工作包还要求 `requirements.txt` 使用精确 `==`、新增依赖登记安装/断言/`pip check`，以及两次 CLI 同时输出全部正例与预期失败并以退出码 0 结束。`stageC_teaching_scf` 当前尚未实施，因而本复核不声称未来的 requirements、unittest 或 CLI 已经运行；M5-WP-B04 的复核对象是 M5-01 工作包是否已经提供一致、可执行的未来命令契约。实际代码与命令通过情况仍由 M5-08 和 M5-10 审计。

## 4. 新增阻塞项与非阻塞记录

### 新增 BLOCKING

无。`BLOCKING=0`。

### 非阻塞记录 M5-WP-N03：C-NUM-01 作者中间首字母

`02_source_ledger/source_table.csv` 和 `01_sources/bibliography.bib` 将 C-NUM-01 第三作者登记为 `P. D. Hasnip`；出版记录为 `P. J. Hasnip`。DOI、题名、年份、卷期、用途和证据边界均正确，因此该书目笔误不影响来源唯一定位、测试契约或阶段许可，但应在后续台账维护时更正。

## 5. 中央来源台账与治理文件

CSV 独立解析结果：数据行 32，所有行均为 17 字段，source ID 无重复；FND-01、C-FND-02—06、C-NUM-01—03、C-LOC-01、DH-01 和 DH-07 各出现一次。BibTeX 独立检查结果：31 个条目键，无重复键，左右花括号计数均为 272；新增九项阶段 C 论文均各出现一次。

当前 SHA-256：

| 文件 | SHA-256 |
|---|---|
| `02_source_ledger/source_table.csv` | `B0C3E069A8465BCB85AEFA8729AC7E9D487EA2ECA5BC4F45C6437AF16D00528E` |
| `01_sources/bibliography.bib` | `360D78005911E8D4902DEA5948608F80408BC5A201571CBA3B52B5233BB1F3FF` |
| `00_scope/master_execution_plan.md` | `45F986A5C9AE33A5DBE7B3CACBFBC810C1C9410029EE89A761042D4C5152673C` |
| `00_scope/learning_route.md` | `352C853017F6E84F26B59023E5432D611BC18F48E6ED7E0E853AF809A531BACA` |
| `decisions.md` | `072992EFCA9474B738CB48E7C18F85342FDDC4ABA7D25F62EB572552E429455C` |
| `08_audits/progress_tracker.md` | `6AB902DF8E0C4540BFFF536C288E1FFF0C7C181EA15CC72FA501A10AFF92AD91` |
| `00_scope/unresolved_decisions.md` | `92B403FE7B09A3BB1A3A7C45F355D3498198F5DB5F2E70B711D0FAB0E24C6A60` |
| `08_audits/M4_stageB_final_independent_audit.md` | `534AE8085CF6BCF3B684E59C836B23B0E996E3CF01B3E184DCD62FED623A752B` |
| `08_audits/M5_stageC_work_package_independent_audit.md` | `DB94C566D6C6808351BAC3CEA88CFEC063F9F420186B33020B69A0B71D902555` |

主计划当前显示 M4=`COMPLETED`、M5=`IN_PROGRESS`，与 M4 最终审计和进度台账一致。首次审计报告、四个未关闭项及本次主修复均在进度台账中可定位。

## 6. D-010 与 M8/M9 边界复核

当前 11 份工作包/章节文件没有出现具体泛函、赝势数据集、真实材料、DFT 后端或实践软件版本选择。LDA/GGA/meta/hybrid、norm-conserving/ultrasoft/PAW 和 HPRO 只作为理论分类、来源对象或待决接口；T-C01—T-C10 均为解析或合成模型，JSON 明确使用 `backend="synthetic"`。

`stageC-label-v1` 中的后端、软件版本和真实实践字段以 `UNRESOLVED_M8` 占位，没有通过 schema 暗中冻结实践对象。治理文件继续要求：M8 前不安装 DeepH、不下载正式训练数据、不生成正式 DFT 标签、不选择材料/DFT 后端/实践版本；准备进入 M8 时集中提交方案；M8 冻结后，在 M9 正式安装、下载、标签生成或复现实验前再次取得明确授权。未发现与 D-010、BLK-03 或 M4 最终许可冲突。

## 7. 11 份 Markdown 严格检查与冻结哈希

工作包及五章各自 `sources.md`、`outline.md` 的独立检查结果为：

```text
files=11
external_markdown_links=11
local_links=0
broken_local_links=0
control_files=0
pandoc_exit_0=11/11
mathml_nodes=129
```

Pandoc 命令口径为：

```powershell
pandoc --from=markdown+tex_math_single_backslash+tex_math_double_backslash `
  --to=html5 --mathml --fail-if-warnings <file>
```

11/11 文件退出码为 0；对生成 HTML 实际统计 `<math>` 节点共 129 个。控制字符检查覆盖 C0（保留制表、换行和回车）及 DEL。当前文件没有本地相对链接；外部链接均为来源 DOI。

| 文件 | SHA-256 |
|---|---|
| `08_audits/M5_stageC_work_package.md` | `72E9808F2AD9204B7E47C3AF7D6458EBFF36A79CBAD16289F0B64CC94B88CA58` |
| `03_textbook/chapters/05_many_electron_mean_field/sources.md` | `34D1E4FC41BBC587AAE8833BED9DD56806ED6D1672CD3A72476570C347716C26` |
| `03_textbook/chapters/05_many_electron_mean_field/outline.md` | `0032025037BDCD0D1C0DC34A8692F24E588CC425A1BB732338325C5C9A38E54E` |
| `03_textbook/chapters/06_kohn_sham_dft/sources.md` | `5997F3F0C1483040DF061707D9818D7A50C5F9F316947817FDF8CBAB5AD92CED` |
| `03_textbook/chapters/06_kohn_sham_dft/outline.md` | `963E5C99CD3EFCFA561774596B9D2491D3F4CA72576B2579D58441ACBF53C0B6` |
| `03_textbook/chapters/07_scf_algorithms/sources.md` | `AF7837E0605F523EA1B476548F815B7B71742965AB2028F56625CEC5B107F605` |
| `03_textbook/chapters/07_scf_algorithms/outline.md` | `D188BBEDCD8B58B0B8BD9F9526E786264E44B999F9B0B93D81B292DA36C5CC8F` |
| `03_textbook/chapters/08_basis_pseudopotential_errors/sources.md` | `56F8B4F0333CB6BF00266670B0931BF6834B756A5350F5FC0765299266BA6F51` |
| `03_textbook/chapters/08_basis_pseudopotential_errors/outline.md` | `F27DC48EB308F00558EAE8F5E4CFCC9C4376D580A1A2A928E1AB1CD291B29208` |
| `03_textbook/chapters/10_nearsightedness_locality_sparsity/sources.md` | `830D74AF4FBFC1ACCBBBF2AA9BFAB1917F28F56D7C24FA78850B5F67ED16F25E` |
| `03_textbook/chapters/10_nearsightedness_locality_sparsity/outline.md` | `61EC21F214DD5285A7BA0F366CE1D3513008C93816E8A5DC647687E1722C9431` |

## 8. 最终许可

- M5-WP-B01：**CLOSED**。
- M5-WP-B02：**CLOSED**。
- M5-WP-B03：**CLOSED**。
- M5-WP-B04：**CLOSED**。
- 新增 `BLOCKING`：**0**。
- M5-01：**允许 `COMPLETED`**。
- M5-02：**允许 `READY` 并启动**。

