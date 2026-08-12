# M6-01 阶段 D 工作包定点复核

## 1. 复核结论

- 复核日期：2026-08-04
- 原审计报告：`M6_stageD_work_package_independent_audit.md`
- 复核范围：M6-D-WP-B01—B03、M6-D-WP-N01—N02 及修订引入的回归风险
- 总结论：`PASS`
- 原问题状态：B01 `CLOSED`；B02 `CLOSED`；B03 `CLOSED`；N01 `CLOSED`；N02 `CLOSED`
- 新增问题：0
- 剩余 `BLOCKING=0`
- 剩余 `NON_BLOCKING=0`
- M6-01：**允许标记为完成**
- M6-02：**允许启动**

本次只执行定点审计，没有修改或格式化任何送审源文件。Markdown 解析仅使用 Pandoc 的 stdout 并管道到 `Out-Null`，未使用 `-o/--output`，也未将输出重定向到送审文件。唯一新增文件为本报告。

## 2. 原问题逐项复核

### M6-D-WP-B01：CLOSED

原问题为周期代表变换的输入域与“规范物理边键”没有形成可执行契约。

修订后的 `08_audits/M6_stageD_work_package.md:47-58` 已把任意有限代表 \(widetilde f_i\in\mathbb R^3\) 分解为规范存储 \(f_i\in[0,1\)^3) 和整数 (q_i)，并明确区分允许未折回代表的构图数学原语与只保存规范代表的序列化 validator。`103-129` 进一步冻结：

- (widetilde f_i=f_i+q_i) 的协变测试域；
- (n'=n+q_i-q_j) 与回拉 \(n^{\mathrm{can}}=n'-q_i+q_j=n\)；
- 精确离散键 \(K_q=(\texttt{structure\_id},i,j,n_x^{\mathrm{can}},n_y^{\mathrm{can}},n_z^{\mathrm{can}})\)；
- 字典序一一配对；
- 采用规范镜像字段的 canonical JSON 数组、UTF-8 和 SHA-256 `edge_instance_id`；
- 浮点位移与距离的 float64、`rtol=0, atol=1e-12` 比较；
- 不得按 ((i,j)) 或距离折叠周期多重边。

`131-135` 和 T-D05（`184`）已给出公共非零 (q)、逐原子不同 (q_i) 以及错误保持 (n'=n) 三类确定性夹具。`03_textbook/stageD_graph_conventions.md:7-16` 与主工作包一致。

独立复算确认：回拉后离散键恢复原 (n)，正确变换的位移在冻结容差内一致；逐原子 (q_i) 不同时错误保持 (n'=n) 被拒绝；canonical JSON 的 SHA-256 为 64 位十六进制标识。输入域、边双射、稳定身份和浮点比较口径均已唯一化，原阻塞条件消失。

### M6-D-WP-B02：CLOSED

原问题为 T-D10 的“近奇异晶胞”没有量化阈值或阈值冻结规则。

修订后的 `M6_stageD_work_package.md:77-83` 已冻结 IEEE 754 float64、SVD 奇异值和无量纲 2-范数条件数：非有限晶格或 \(sigma_{\min}=0\) 拒绝；可逆但 \(kappa_2(A)\ge10^8\) 的教学输入拒绝；只有 (kappa_2(A)<10^8) 进入枚举。该判据在晶格整体长度缩放下不变，并明确区分数学奇异与可逆但按教学数值策略拒绝的近奇异对象。

同一位置冻结三组边界夹具：

- \(A_-=\operatorname{diag}(1,1,2\times10^{-8})\)，\(kappa_2=5\times10^7\)，接受；
- \(A_0=\operatorname{diag}(1,1,10^{-8})\)，(kappa_2=10^8)，拒绝；
- \(A_+=\operatorname{diag}(1,1,5\times10^{-9})\)，\(kappa_2=2\times10^8\)，拒绝。

D-D05（`170`）、T-D10（`189`）和 `stageD_graph_conventions.md:8` 已同步。独立 float64/SVD 复算得到三者条件数分别为 \(5\times10^7,10^8,2\times10^8\)，判定依次为接受、拒绝、拒绝。原审计要求的 dtype、尺度感知判据、阈值、边界处理和阈值两侧夹具均已满足。

### M6-D-WP-B03：CLOSED

原问题为中央未决事项文件仍允许在 M7-I 之前触发 M8。

`00_scope/unresolved_decisions.md:18` 现明确规定：M7 完成且 M7-I 对 M3—M7 的全量独立总审计通过后，才暂停并提交 M8 决策包；M8 必须由用户明确冻结；开始 M9 的 DeepH 安装、正式数据下载、正式标签生成或复现实验前仍需再次取得明确执行授权。

该表述与 `decisions.md:95-104`、`00_scope/master_execution_plan.md:62-64` 和 `08_audits/progress_tracker.md:32-35,134` 一致，不再存在可绕过 M7-I 的治理路径。M8/M9 双授权边界保持完整。

### M6-D-WP-N01：CLOSED

原问题为四章来源包的节号损坏及部分定位过泛。

复核确认：

- `03_textbook/chapters/11_supervised_learning_optimization/sources.md:7` 已定位 Gilmer 第 2 节及 PMLR pp. 1264—1265；
- `03_textbook/chapters/12_atomic_graph_representation/sources.md:5-8` 已定位 Zaheer 第 2.1—2.2 节、Gilmer 第 2 节、CGCNN 期刊页 145301-2/Fig. 1(a) 前多重图定义，以及 DH-01 正文/补充材料页码；
- `03_textbook/chapters/13_message_passing_networks/sources.md:5-8` 已定位 Gilmer 第 2—3 节、Zaheer 第 2.1—2.2 节、Goodfellow 第 8 章和 DH-01 页码；
- `03_textbook/chapters/14_periodic_graph_neighbor_lists/sources.md:5-7` 已定位 CGCNN 主文及同一固定 arXiv PDF 内附的 “Construction of crystal graphs” 补充部分、Gilmer 第 2 节和 DH-01 补充材料。

对固定 PDF 的只读文本核对确认这些节、页、图和补充材料标题存在，且各行仍保留“不外推周期枚举、通用 cutoff、旋转等变或实践版本”的来源边界。损坏的 `` `2 ``/`` `2—3 `` 已全部消除。

### M6-D-WP-N02：CLOSED

原问题为五个阶段 D 来源 ID 到四个作品级 BibTeX 条目的映射不显式。

`01_sources/bibliography.bib:372-392` 已新增 `goodfellow2016chapter5` 与 `goodfellow2016chapter8` 两个章节级条目，分别包含章名、章号、固定 URL 和 D-FND-01/D-FND-02 注记。`01_sources/documentation/stageD/README.md:15` 已显式冻结五项映射：

- D-FND-01 → `goodfellow2016chapter5`；
- D-FND-02 → `goodfellow2016chapter8`；
- D-GNN-01 → `gilmer2017mpnn`；
- D-GNN-02 → `zaheer2017deepsets`；
- D-PBC-01 → `xie2018cgcnn`。

独立解析确认中央 CSV 为 40 条数据记录、每条 17 字段、ID 唯一，五个阶段 D ID 各出现一次；BibTeX 共 40 个唯一键，上述五个映射为 5/5 存在。共享专著不再导致章节快照归属不明。

## 3. 回归与新增问题检查

- 对修订工作包、统一约定、治理文件、阶段 D 来源 README、四章来源包、四章提纲、主计划、学习路线、决策记录、进度台账和原审计报告执行严格 Pandoc stdout 解析，17/17 通过；非法控制字符和裸 CR 为 0。
- 定点修订范围内 7 个活动本地链接均存在。学习路线中被简单正则误识别为链接的两处 `\mathbf r` 属于数学语法，不是 Markdown 链接；未形成断链。
- 五份本地来源快照 SHA-256 与 README 及中央台账登记值保持一致，没有发生来源二进制替换。
- 行晶格、逆晶格列范数枚举界、src/dst 方向、求和置换性质、edge provenance、章节范围以及 M8 前禁止 DeepH/正式数据/DFT 标签/隐含实践选择等原已通过内容没有回归。
- 没有发现修订引入的新 BLOCKING 或 NON_BLOCKING 问题。

## 4. 最终门控意见

B01—B03 与 N01—N02 均已按原报告关闭，新增及剩余问题均为 0。M6-01 的来源边界、周期图契约、验证门控和治理授权条件已经达到可执行、可复核状态。因此允许将 M6-01 标记为 `COMPLETED`，并允许按依赖顺序启动 M6-02 第 11 章监督学习、优化与泛化材料建设。
