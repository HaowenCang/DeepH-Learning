# M6-09 阶段 D 材料完备性、可自学性与可验证性总门控包

> 当前状态：`REVIEW`。本文件只冻结阶段 D 当前总快照、证据索引和正式审计要求，不自行给出 M6 通过结论。只有新的独立子 agent 对当前总快照判定 `BLOCKING=0`、`NON_BLOCKING=0` 并明确允许完成 M6、启动 M7，主 agent 才能更新里程碑状态。

## 1. 门控目标与范围

阶段 D 覆盖第 11—14 章，目标是把结构分组、监督回归、解析梯度、周期有向多重图、普通同步 MPNN 和边级轨道块输出连接为一条可追踪、可复算、可执行失败的对象链：

\[
\text{结构组与帧}
\longrightarrow
\text{周期图与张量}
\longrightarrow
\text{同步消息传递}
\longrightarrow
\text{边级轨道块}
\longrightarrow
\text{分组评价与失败诊断}.
\]

依据 D-010 材料建设模式，学习者闭卷作答、口头解释和逐阶段自测不构成阻塞证据；原有知识范围、推导条件、来源边界、练习强度和技术验证均保留。总审计判断材料是否可由第三方系统自学和独立复核，不审查个人学习表现。

本阶段只使用确定性合成结构、合成分组、合成轨道身份和合成监督目标。M8 前禁止安装 DeepH、下载正式训练数据、生成 DFT 标签或隐含选择材料体系、DFT/数据后端与 DeepH 软件对象。

## 2. 冻结材料对象

- [M6 工作包](M6_stageD_work_package.md)：范围、依赖、来源边界、D-D01—D-D07、T-D01—T-D10 和退出标准；
- [统一周期图约定](../03_textbook/stageD_graph_conventions.md)：行晶格、receiver-first、完整边键、镜像协变和 provenance；
- [阶段 D 自学导航](../03_textbook/chapters/stageD_self_study_guide.md)：D1—D4 顺序、六类材料正向映射、反向入口和诊断；
- [张量追踪模板](../03_textbook/stageD_tensor_trace_template.md)：graph、单边、轨道块、置换、换胞、concat/padded、前后向和失败注入；
- 第 11—14 章各自的 `sources.md`、`outline.md`、`chapter.md`、`examples.md`；
- [D-D01—D-D07 推导索引](../04_derivations/stageD/README.md)及四份逐式推导；
- `06_exercises/04-stageD/` 下四章与 comprehensive 的成对 problem/solution，含 C-D01—C-D10；
- [阶段 D 代码说明](../05_code_exercises/stageD_synthetic_mpnn/README.md)、`staged_models.py`、`run_experiments.py`、`test_staged_models.py` 和 `requirements.txt`；
- [阶段 D 来源快照索引](../01_sources/documentation/stageD/README.md)、中央 `source_table.csv` 与 `bibliography.bib`。

总审计的活动 Markdown 核心集合固定为 36 个文件：四章 16 个、推导 5 个、章节/综合题解 10 个，以及工作包、统一约定、自学导航、追踪模板和代码 README 各 1 个。

## 3. 统一对象与不变量

### 3.1 周期图与身份

晶格三行是晶格矢量，\(r=fA\)。边 \(e=(i\leftarrow j,n)\) 的位移为

\[
d_e=(f_j+n-f_i)A,\qquad
0<\rho_e=\lVert d_e\rVert_2\le r_c.
\]

零位移自环排除；\(i=j,n\ne0\) 的自镜像和同一 \((i,j)\) 的多个 shift 均可保留。完整键为

\[
K_e=(\text{structure\_id},i,j,n_1,n_2,n_3).
\]

edge ID 的规范 payload 是 UTF-8 紧凑 JSON 数组
`["stageD-edge-v1",structure_id,i,j,n1,n2,n3]` 的 SHA-256。ID、端点、shift、位移、距离、prediction、mask、block shape 和轨道身份必须共享同一行映射。

### 3.2 镜像完备性与换胞

核心几何使用 `float64`；cell 必须有限、可逆且 \(\kappa_2(A)<10^8\)，cutoff 必须有限且严格为正。安全镜像盒为

\[
M_k=\left\lceil r_c\lVert A^{-1}_{:k}\rVert_2+1\right\rceil.
\]

解析盒过滤后的完整边键必须与外扩一层暴力盒相同。逐原子代表变化 \(\widetilde f_i=f_i+q_i\) 时，

\[
n'=n+q_i-q_j,\qquad
n^{\mathrm{can}}=n'-q_i+q_j=n.
\]

配对必须使用回拉完整键，不得使用原行号、距离或仅原子对。

### 3.3 MPNN、轨道块与 batch

每层同步读取 \(h^{(\ell-1)}\)，按 receiver 聚合；\(L\) 层支持只可沿不超过 \(L\) 条有向前驱边传播。普通节点置换等变性不推出三维旋转等变性。

轨道块的有效分量数为 \(p_ip_j\)，component mask 是左连续 true 前缀；局部下标按 row-major 反解，并与两端有序实际轨道 ID 表一致。masked MSE 以总有效分量数 \(S>0\) 平均，inactive padding 在读取、统计、前向与 loss 前切除。

`stageD-batch-v1` 的 concat 形式以 batch 槽位、`node_graph_id`、`edge_graph_id` 和 offset 定位各图，structure ID 逐图非空但不要求批内唯一；padded 形式使用左连续 node/edge mask 和无效端点 \(-1\)。sum/mean 的空入边输出零，mean 同时返回 `has_incoming=false`；max 拒绝空集。

## 4. 知识、推导、练习与自学门控

| 能力轴 | 教材与推导 | 题解与代码证据 | 关键失败边界 |
|---|---|---|---|
| 分组学习与评价 | 第 11 章；D-D01/D-D02 | 第 11 章题解；C-D01—03；T-D01—03 | 逐帧泄漏、只看训练下降、损坏 test 目标 |
| 属性多重图与置换 | 第 12 章；D-D03 | 第 12 章题解；C-D04/C-D07/C-D09；T-D04/T-D07/T-D09 | 端点/行/provenance 错位、错误去重、跨图边 |
| 同步普通 MPNN | 第 13 章；D-D01/D-D04/D-D06 | 第 13 章题解；C-D02/C-D08/C-D10；T-D02/T-D08/T-D09 | 五类错误反传、异步穿透、空入边与复杂度误报 |
| 周期邻居与身份 | 第 14 章；D-D05/D-D07 | 第 14 章题解；C-D05—07/C-D09；T-D05—07/T-D10 | 固定小盒、最小镜像、固定 shift、病态 cell |
| 端到端自学性 | 自学导航与追踪模板 | C-D01—C-D10 成对解答、A/B CLI、失败矩阵 | 任一能力找不到教材/推导/代码/题解/失败入口 |

独立总审计应确认四章各至少包含两个解析或手算例题、八道以上分类型练习和逐题解答；D-D01—D-D07 条件闭合；T-D01—T-D10 的正例与强制失败真实执行；C-D01—C-D10 从分组划分贯穿到轨道块追踪、batch、复杂度与授权停点。

## 5. 直接来源与证据边界

阶段 D 的五项新增直接来源为 D-FND-01/02、D-GNN-01/02、D-PBC-01；固定本地快照及 SHA-256 见[来源索引](../01_sources/documentation/stageD/README.md)。中央台账当前 hash 为：

- `02_source_ledger/source_table.csv`：`2B1BC9AA97669253F42B26790D82E38A971DA9588115763A4E1BFACAF6C4739C`；
- `01_sources/bibliography.bib`：`D1293349ED30AACC9AEA8BAD47A443B1C75AE1746FA876B635E792FCFEBD8398`；
- 阶段 D 快照索引：`E757323A2E758275FEAD820A2FF5DEBF49CBF089226086B811394203CD3F18E3`。

这些来源支持监督学习、梯度法、普通 MPNN、集合聚合与周期晶体图的一般对象。它们不直接规定本项目的分组生成式、镜像界、edge schema、轨道排序、材料、cutoff、DFT 后端、DeepH 版本或真实误差。相应公式必须标记为直接推导或教学构造。

DH-01 只用于限定 DeepH 的任务联系：局部原子环境与原子对映射到 Hamiltonian 块；不得据此声称本阶段已安装、复现或验证 DeepH。

## 6. 代码、环境与可执行门控

固定环境为 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0。当前运行时曾缺失 SciPy，已依据用户授权用精确 `requirements.txt` 恢复 `scipy==1.18.0`；`numpy==2.3.5` 已满足，`pip check` 无破损。复现命令为：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m pip install --requirement .\05_code_exercises\stageD_synthetic_mpnn\requirements.txt
& $py -c "import sys, numpy, scipy; assert sys.version_info[:3] == (3,12,13); assert numpy.__version__ == '2.3.5'; assert scipy.__version__ == '1.18.0'"
& $py -m pip check
& $py -m unittest discover -s .\05_code_exercises\stageD_synthetic_mpnn -p 'test_*.py' -v
& $py .\05_code_exercises\stageD_synthetic_mpnn\run_experiments.py --format json --config A --seed 20260806
& $py .\05_code_exercises\stageD_synthetic_mpnn\run_experiments.py --format json --config B --seed 20260817
```

预期为 13/13 unittest；A/B 均 `overall_pass=true` 且 T-D01—T-D10 全部通过；同一配置双次子进程 stdout 字节一致；错误 seed 退出码 2。当前规范 stdout SHA-256 为：

- A：`2F45DC8C53C1E1D968B3F4633CCC8590540AB8E08667A340054F15F9F3CCA6EE`；
- B：`88BF70A4218E2B10C8410644B7B899ECF50A6F6993E83E93C496450069693BD6`。

T-D02 检查 A/B 的 132/300 个参数坐标和五类实际错误反传；T-D03 的新组 test MSE 必须低于 0.02 且低于零基线四分之一；T-D09 必须捕获 36/36 schema 失败；T-D10 必须捕获 16/16 硬失败。规范 JSON 排除墙钟时间；benchmark 只能作为非规范环境快照。

代码冻结 hash：

| 文件 | SHA-256 |
|---|---|
| `staged_models.py` | `B640F81C2DED530C53A42AB5D707685DBDD6A6C872687518C3CAF2C49739DDD5` |
| `run_experiments.py` | `32B0B8F725B8695C182D3EEA500D24708B240D74F95B2AB2AE8FFC73CFA44149` |
| `test_staged_models.py` | `611926403A3819DECFAD29C705AF696B0BA0EBDD3FC185549587CBE7B868F403` |
| `README.md` | `A02493AEFE386C9E7823C5A8AA0C36EFC3C4F39B68823D6C87B350070FF398B8` |

## 7. 已有独立分项审计

| 工作项 | 清零结论与报告 hash |
|---|---|
| M6-01 工作包 | B01—B03/N01—N03 关闭，`M6_stageD_work_package_blocking_reaudit.md`，`A2D1EC1DFC81FF6E5F4D94E86222FDDC41EE6CDCB34E35FEEE7B5866ACF94D99` |
| M6-02 第 11 章 | B01/N01 关闭，`M6_chapter11_blocking_reaudit.md`，`62E0EEF679294F31CD8A443121385AC056F31A7C7276D11B88C66E18CBE8F6E3` |
| M6-03 第 12 章 | B01—B03/N01 关闭，`M6_chapter12_second_reaudit.md`，`92A71FFEA6894C6EEDCC28E720E4CE17BB5B6C0948489BAEAA0DC2C8B5388024` |
| M6-04 第 13 章 | B01 关闭，`M6_chapter13_blocking_reaudit.md`，`34EBA50DBC873F3ECEFA3234E2726B0318C93BFE62BBB85DB613E4FF43D86576` |
| M6-05 第 14 章 | B01/B02/N01/N02 关闭，`M6_chapter14_blocking_reaudit.md`，`D5F5EA344B11A6D0CEC962259463408563D6F0D9CA66D2DA6F0FF61E0A5B1AB9` |
| M6-06 推导包 | D-D01—D-D07 全部通过，`M6_stageD_derivation_package_independent_audit.md`，`A1267D57ECE93CD1CA7BC5AFCEA60ACACC175BD5315D8E9211DEA7224CD22FBE` |
| M6-07 代码 | B01—B05/N01 经三次复核清零，`M6_stageD_code_third_reaudit.md`，`CA54C0904F9722C6E97765FA51772BD51410D4057EAEFC4DC5B4E50C9FABE896` |
| M6-08 自学材料 | B01/N01—N03 关闭，`M6_stageD_self_study_blocking_reaudit.md`，`F4BC84784C02E53874B52B5C936DAAF6F9F5D85F7FC0C7A7219004D116D6373F` |

已有分项审计只能作为历史证据，不能替代 M6-09 对跨文件一致性、当前 hash 和材料总完备性的重新判断。

## 8. 主 agent 内部预检

当前内部预检结果为：

- 36/36 个阶段 D 核心 Markdown 以 `markdown+tex_math_single_backslash` 严格 Pandoc/MathML 通过；
- 59 个活动本地 Markdown 链接全部存在；
- MathML 节点合计 1,294，非法控制字符为 0；
- 第 11—14 章 problem/solution 均为 10/10 题组，C-D01—C-D10 与 A-D01—A-D10 一一对应；
- C-D04 唯一 payload `["stageD-edge-v1","stageD-main",2,0,-1,0,0]` 的 SHA-256 为 `14dc675ce342830589c8b2687fbdcb4c3d88056164913163ff76a33c9812328f`；
- 主夹具 bounds 为 \((2,2,2)\)、候选 2000、保留边 18；C-D07 夹具保留 8 条边；
- concat 为 \(N_{\mathrm{tot}}=6,E_{\mathrm{tot}}=26\)，padded 为 \([B,N_{\max},E_{\max},P_{\max}]=[2,4,18,4]\)；
- 13/13 unittest、A/B 双次字节确定性、错误 seed、36/36 T-D09、16/16 T-D10 和 `pip check` 通过。

这些结果是主 agent 预检，不构成独立通过结论。独立审计员应重新运行关键命令、复算关键对象并冻结自己的当前快照。

## 9. 已知未决项与授权边界

阶段 D 没有允许带入 M7 的已知内容缺陷。跨阶段未决项 BLK-03 仍为：计算资源、DFT/数据后端、DeepH 软件对象、首个材料体系、时间与训练预算和高级物理范围尚未冻结。该项按用户指示只在准备进入 M8 时集中提交，不阻塞 M7 的理论、教材和合成验证。

M8 前继续禁止安装 DeepH、下载正式训练数据、生成正式 DFT 标签或隐含选择材料、后端和实践软件版本。M7 完成后还必须由 `gpt-5.6-sol`、`max` 推理强度的独立子 agent 对 M3—M7 执行全量总审计并清零。M8 决策冻结后，在 M9 正式安装、下载或复现实验前仍需再次取得明确执行授权。

## 10. M6-09 独立总审计要求

新的独立子 agent 只允许新增正式总审计报告，不得修改教材、推导、题解、代码、来源、计划、tracker 或本门控包。报告至少应包含：

- 独立性声明、审计范围和当前核心文件 SHA-256；
- 第 11—14 章知识范围、公式条件、来源边界、跨章对象链和失败边界；
- D-D01—D-D07、T-D01—T-D10、C-D01—C-D10 的逐项可定位性与正确性；
- 完整边键、edge ID、轨道 provenance、置换、换胞、镜像完备性、batch/padding、解析梯度、分组评价与复杂度的独立复算；
- 36 文件严格 Pandoc/MathML、链接、控制字符、题解配对、13 项 unittest、A/B CLI 字节确定性、错误 seed、36/36 与 16/16 失败矩阵的实际结果；
- M8/M9 授权边界以及 BLK-03 能否安全带入 M7 的判断；
- 所有 `BLOCKING` 与 `NON_BLOCKING` 稳定 ID、证据和最小关闭条件；
- `PASS/FAIL`，以及是否明确允许 M6 `COMPLETED`、M7 `IN_PROGRESS`。

通过标准为 `BLOCKING=0`、`NON_BLOCKING=0`、无新增问题，并明确允许完成 M6 与启动 M7。若发现问题，主 agent 实施修复后必须由同一独立审计员定点复核；主 agent 不得用本门控包、内部预检或既有分项审计替代正式结论。
