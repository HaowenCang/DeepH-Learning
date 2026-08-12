# M6-08 阶段 D 自学材料正式独立审计

## 1. 审计身份、范围与规则

- 审计对象：M6-08 自学导航、张量追踪模板、综合题与参考解答。
- 审计角色：新的独立审计员；未参与本轮四份材料的建设或修复。
- 写入边界：除本报告外，未修改教材、推导、代码、计划、tracker 或其他审计文件。
- 放行规则：只有 `BLOCKING=0` 且 `NON_BLOCKING=0`，才允许完成 M6-08 并启动 M6-09。
- 审计日期：2026-08-09。

本报告审计的四份目标快照如下：

| 文件 | SHA-256 |
|---|---|
| `03_textbook/chapters/stageD_self_study_guide.md` | `13FB3C5EA09DF4B4147481E0B1EE2A7297F89B3CAB3928B3FBE19C201528251C` |
| `03_textbook/stageD_tensor_trace_template.md` | `034A602102783D3B66B24DC10A459CC40AE1C765595E495EEEC331C2C8F984B6` |
| `06_exercises/04-stageD/comprehensive/problem/readme.md` | `DD7062CD0F6256CFF45E8E5DCF0F5A9F96EB6C56EAC43353D41A9B4AB267AD9C` |
| `06_exercises/04-stageD/comprehensive/solution/readme.md` | `B7548D391DABE5AE127A5B3845C5DB66E0E57696E2289B2C179A84C19E678DA0` |

交叉核对的工作包快照为 `7DD663291CDD9D029D52D9FC27EBA70DA6C3641E2E55540792C1808772C5DCE0`。代码快照分别为：`staged_models.py` `B640F81C2DED530C53A42AB5D707685DBDD6A6C872687518C3CAF2C49739DDD5`、`run_experiments.py` `32B0B8F725B8695C182D3EEA500D24708B240D74F95B2AB2AE8FFC73CFA44149`、`test_staged_models.py` `611926403A3819DECFAD29C705AF696B0BA0EBDD3FC185549587CBE7B868F403`、代码 `README.md` `A02493AEFE386C9E7823C5A8AA0C36EFC3C4F39B68823D6C87B350070FF398B8`。

## 2. 总结论

**结论：`FAIL`。**

- `BLOCKING=1`
- `NON_BLOCKING=3`
- **不允许完成 M6-08。**
- **不允许启动 M6-09。**

失败原因不是代码运行、关键数值或边集合错误。四份材料的总体覆盖已经形成，10/10 综合题与答案成对，严格 Markdown/MathML、活动链接、控制字符、A/B CLI、错误 seed、13 项测试及关键独立复算均通过。当前阻塞来自 C-D04 的冻结身份问题没有得到唯一、可执行的参考答案；另有三项导航或模板契约不精确。依据本阶段“可自学性与可验证性”门控以及零问题放行规则，仍不能放行。

## 3. 门控逐项结果

| 门控对象 | 判定 | 独立证据 |
|---|---|---|
| C-D01—C-D10 题目完整性 | `PASS` | 题目文件恰有 C-D01—C-D10 十个一级题组，各题均含多分支、条件、失败样例或验证要求。 |
| A-D01—A-D10 配对与非空目录 | `PASS` | `problem/` 与 `solution/` 均非空；答案文件恰有 A-D01—A-D10 十个对应题组。 |
| 知识范围与端到端对象链 | `PASS` | 覆盖分组评价、masked MSE、完整反传、普通 MPNN、周期多重边、代表变换、镜像界、感受野、两种 batch、复杂度和授权停点。 |
| 正向“能力—教材—推导—代码—练习—失败样例”映射 | `PASS` | 自学导航 2.1 节逐项覆盖十项能力，D-D01—D-D07、T-D01—T-D10 和 C-D01—C-D10 均有入口。 |
| 反向入口与诊断映射 | `PASS` | 自学导航 2.2、4、6、7 节可从代码、失败现象、测试和问题回查教材与推导；但章节号精度另见 N01。 |
| 张量追踪覆盖 | `PASS` | 模板覆盖 graph、单边、edge output、轨道块、置换、换胞、concat、padded、前后向、失败注入和复现记录；schema 名称与代码常量一致。 |
| 公式条件与失败边界 | `PASS` | 行晶格、receiver-first、float64、`rtol=0, atol=1e-12`、`kappa_2<1e8`、有限正 cutoff、同步更新、空入边策略、连续 mask 与 M8/M9 边界均明确。 |
| C-D04 冻结身份的唯一参考答案 | `FAIL` | 问题固定 `stageD-main`，答案与模板却把 structure ID 是否改变写成二选一，未给出该冻结问题的唯一规范 payload 和 SHA-256；见 B01。 |
| 严格 Markdown 与 MathML | `PASS` | 四文件使用 `pandoc --from markdown+tex_math_single_backslash --to html5 --mathml --fail-if-warnings`，退出码均为 0；MathML 节点数依次为 13、88、46、146。 |
| 活动链接 | `PASS` | 独立解析 28、4、0、2 个 Markdown 本地链接，工作区内目标全部存在，无越界目标。 |
| 控制字符 | `PASS` | 四文件 UTF-8 文本中的非法 C0 控制字符为 0。 |
| 来源与授权边界 | `PASS` | 未把合成阈值外推到真实 Hamiltonian；M8 前禁装 DeepH、禁正式数据与 DFT 标签、禁隐含选材/后端/版本；M9 外部执行需再次授权。 |

## 4. BLOCKING

### B01：C-D04 的 structure ID 与 edge ID 没有冻结成唯一可执行答案

**证据。** `problem/readme.md` 的 C-D04 已明确该夹具的 structure ID 是 `stageD-main`，只规定节点旧编号到新编号的置换和边行倒序，并未规定 structure ID 改名。按照题面给出的旧到新映射，旧边 `(0,1,(-1,0,0))` 应变成 `(2,0,(-1,0,0))`。然而 `solution/readme.md` 第 113 行写成“若测试为新结构 ID……若契约保留 structure ID……”，张量模板第 145 行也写成“用新 structure ID……或按冻结测试契约处理”。这使同一道冻结题产生两个不同规范 payload 和两个不同 SHA-256，且答案没有给出当前题面的确定 hash。

独立按题面复算得到：

```text
["stageD-edge-v1","stageD-main",2,0,-1,0,0]
SHA-256 = 14dc675ce342830589c8b2687fbdcb4c3d88056164913163ff76a33c9812328f
```

当前 T-D04 代码也保留 `stageD-main`，由重编号后的端点与原 shift 重算 edge ID；代码中的 `permutation` 数组按“新行取哪个旧行”使用，再由 `inverse` 形成旧编号到新编号映射。综合题则直接给出旧到新映射。两者可以等价核对，但参考答案应当明确数组方向，不能以二选一掩盖。

**影响。** edge ID 是边输出、轨道 provenance、置换双射和后续 batch 追踪的离散主键。参考答案未冻结 identity 字节，就无法对 C-D04 的“哪些字段必须重算”进行唯一验收，也无法直接复现对应 SHA。这违反 M6-08 的可验证性门控。

**最小关闭条件。** 同时完成以下修订：

1. 在 C-D04 参考答案中明确本题保留 `stageD-main`，给出变换后完整键、上述紧凑 JSON payload 与 SHA-256；
2. 明确综合题的 `pi` 是旧编号到新编号，而代码数组是新行到旧行，并给出通过逆置换对应的说明；
3. 把张量模板的节点置换 edge-ID 规则改成确定规则：structure ID 是否改变由变换契约预先冻结；对本阶段 T-D04 保持不变，只从同一 ID、新端点和 shift 重算。若保留“新 structure ID”变体，应单列为不属于本题的扩展变体。

## 5. NON_BLOCKING

### N01：自学导航中的章节定位有多处偏移

**证据。** 自学导航第 32、106 行把逐原子周期代表变换定位到第 14 章 14.4，但实际推导与公式位于 14.5；14.4 是最小镜像与重复边。第 34、108 行对多重边身份的第 12 章定位写成 12.2，而直接内容位于 12.1.3、12.5.3 或 12.6.2。第 36、110 行对 batch/NaN padding 的主要定位未指向 12.2.2—12.2.3。文件链接本身有效，但章节级导航会把自学者送到相邻而非直接论证位置。

**最小关闭条件。** 修正上述章节号，使周期代表变换指向 14.5，batch/NaN 直接指向 12.2.2—12.2.3，多重边与完整身份分别指向 12.1.3、12.5.3/12.6.2 和 14.4.2—14.4.3；重新运行活动链接与严格 Pandoc 检查。

### N02：模板要求“structure_id 批内唯一”，但冻结 batch validator 不执行该契约

**证据。** 张量模板第 39 行要求检查 `structure_id` 批内唯一性。独立把两个相同 `stageD-main` 图传入 `make_concat_batch` 与 `make_padded_batch`，两者均接受，得到 `['stageD-main','stageD-main']`。当前 validator 使用 `edge_graph_id` 或 batch 槽位划分各图，并未把 structure ID 全局唯一作为冻结条件。模板因此比可执行 schema 多声明了一项未测试约束。

**最小关闭条件。** 二选一并明确冻结：若沿用当前代码契约，把模板改为“structure ID 逐图非空，batch 槽位/graph ID 参与批内定位”，不再声称批内唯一；若确需全局唯一，则必须同时在 concat/padded validator 与失败矩阵中加入重复 structure ID 拒绝。仅修改文案而保留两种解释不算关闭。

### N03：padding 探针运行次数自相矛盾

**证据。** 张量模板第 178 行写“记录两次运行”，紧随其后的表格实际列出有限零、NaN、`10^300` 三种运行；C-D09 题目和答案也正确要求三运行残差检查。

**最小关闭条件。** 把模板改为“记录三次运行”，保持三个探针与零残差判据不变。

## 6. 独立执行与复算证据

### 6.1 运行环境

```text
Python 3.12.13
NumPy 2.3.5
SciPy 1.18.0
pip check: No broken requirements found.
```

本审计未安装任何新依赖。

### 6.2 自动测试、CLI 与确定性

- `python -m unittest discover -s 05_code_exercises/stageD_synthetic_mpnn -p test_*.py -v`：13/13 通过。
- 配置 A `seed=20260806`：退出码 0，`overall_pass=true`，真实 stdout SHA-256 为 `2F45DC8C53C1E1D968B3F4633CCC8590540AB8E08667A340054F15F9F3CCA6EE`；独立重复两次字节完全一致。
- 配置 B `seed=20260817`：退出码 0，`overall_pass=true`，真实 stdout SHA-256 为 `88BF70A4218E2B10C8410644B7B899ECF50A6F6993E83E93C496450069693BD6`；独立重复两次字节完全一致。
- 配置 A 错误 seed `0`：退出码 2、stdout 为空，stderr 明确要求 seed `20260806`。
- T-D09：A/B 均为 36/36 预期失败实际捕获；T-D10：A/B 均为 16/16。
- T-D03：A 的 test MSE/MAE 为 `0.0019442385963440796` / `0.03826902222542553`，B 为 `0.005013176247195347` / `0.0569399961624116`；均低于 0.02 且低于各自零基线四分之一，损坏目标约为 0.99。

### 6.3 周期图、身份与张量独立复算

- 主夹具：独立由 `A^-1` 列范数得到 bounds `(2,2,2)`；候选数 `4^2*5^3=2000`；距离过滤后完整有向边数为 18。
- 主夹具前两边：独立复得 `(0,1,(-1,0,0))` 的位移 `(-0.81,0.20,0.19)`、距离 `0.8556868586112564`、ID `d54362...0707dd`；以及 `(0,1,(0,0,0))` 的位移 `(0.59,0.20,0.19)`、距离 `0.6513063795173513`、ID `38b010...8e3bf`。
- C-D07：独立枚举得到八条边，包含四条非零自镜像和四条跨原子边；零位移自环均排除。固定 `[-1,1]^3` 在 C-D06 的 `diag(0.4,5,5)` 夹具中遗漏 `n=(+/-2,0,0)` 两条自镜像。
- 换胞符号：对 `q_0=(1,-1,0)`、`q_1=(-2,0,1)`，独立复得 `n'=(2,-1,-1)`、回拉 `(-1,0,0)`；错误固定 shift 的分数误差为 `(-3,1,1)`。
- batch：concat 为 `N_tot=6,E_tot=26`，第二图 offset 4；padded 为 `[B,Nmax,Emax,Pmax]=[2,4,18,4]`。主要 shape、dtype、第二图 inactive 端点 `-1`、node mask `[true,true,false,false]` 与 edge mask 8 个有效行均与材料一致。
- 轨道身份：主夹具首边 block shape `(1,2)`，mask `[true,true,false,false]`，有效实际轨道对为 `(syn:0:0,syn:1:0)` 与 `(syn:0:0,syn:1:1)`。
- 激活字节：配置 A 为 2304 bytes，配置 B 为 4608 bytes；均由 `8L(3Nd+2Ed)` 独立复算。

## 7. 来源、结论边界与复核要求

四份材料正确把结构组泄漏反例、有限镜像界、边 schema、复杂度估计和数值阈值标为本项目推导或教学构造，没有冒充外部来源原文。阶段 D 的成功证据只支持冻结合成对象上的数据划分、普通 MPNN、周期图、输出 schema 和失败验证；不能推出真实 Hamiltonian 精度、材料迁移、DFT 后端正确、旋转等变性或 DeepH 已可执行。

B01 与 N01—N03 修复后，应由同一独立审计员对修订快照执行定点复核。定点复核至少重新检查：C-D04 唯一 payload/hash、置换数组方向、章节定位、batch structure-ID 契约、三种 padding 探针、四文件 SHA、严格 Pandoc/MathML、活动链接、13 项测试、A/B stdout hash 与错误 seed。只有复核确认原问题全部关闭、无新增问题，并报告 `BLOCKING=0`、`NON_BLOCKING=0`，才允许完成 M6-08 和启动 M6-09。
