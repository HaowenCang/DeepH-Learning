# M9 阶段 F 工作包第一次阻塞项定点复核

## 1. 正式结论

**结论：FAIL。** 原审计 `M9-F-WP-B01`—`M9-F-WP-B04` 均已按各自最小关闭条件修订，逐项判定为 `CLOSED`；但预算机读合同引入 1 项新的内部矛盾，登记为 `M9-F-WP-B05`。本次复核结果为：

- 原问题：`CLOSED=4`，`OPEN=0`；
- 新增问题：`BLOCKING=1`，`NON_BLOCKING=0`；
- 当前总剩余：`BLOCKING=1`，`NON_BLOCKING=0`；
- 是否允许启动 M9-02：**不允许**。

新问题不要求改变 D-013/D-014 的软件、数据、硬件、授权、预算或物理范围，只需消除预算合同对项目侧小型审计产物的放置规则与工作包/README 的直接冲突。修复后应交回同一独立审计员作第二次定点复核；只有复核明确给出 `PASS`、`BLOCKING=0`、`NON_BLOCKING=0`，才允许启动 M9-02。

## 2. 复核范围、约束与输入快照

本次只复核原报告 [`M9_stageF_work_package_independent_audit.md`](M9_stageF_work_package_independent_audit.md) 的 B01—B04、对应修订及修订直接影响面。除新增本报告外，没有修改任何被审材料；没有安装软件、下载正式数据、启动训练或执行复现实验。只读核对了冻结 VHDX 路径是否存在，没有读取、索取、复制、推断或记录任何认证口令。

| 输入 | 字节数 | SHA-256 | 与委托快照 |
|---|---:|---|---|
| [`M9_stageF_work_package_independent_audit.md`](M9_stageF_work_package_independent_audit.md) | 17,710 | `B93F2B9DFB3F7FD2509E4EECF33624BC1B0C80DE7ACBBF719247056DA0339566` | 原审计基线 |
| [`decisions.md`](../decisions.md) | 15,272 | `28146406676BF3A22E388C4539BCF541E5AA7AC83DCB3AAE67FE2A8E46226C6D` | 匹配 |
| [`M9_stageF_work_package.md`](M9_stageF_work_package.md) | 10,809 | `458A2C6B527D0F0DB8CFD51521B0C52EEE40797F34C411672EFBDBEDF12B2285` | 匹配 |
| [`budget_contract.json`](../06_reproduction/manifests/budget_contract.json) | 1,678 | `C598A3392347587249C929ECD87BB69CD548EE98B36CD9C8F8DF01A2356782B1` | 匹配 |
| [`m9_preflight.json`](../06_reproduction/manifests/m9_preflight.json) | 1,035 | `B6F787A1F88FDAC006531F5398AE45215C39CE942D3CEA0D3F4B97141FED1B83` | 匹配 |
| [`master_execution_plan.md`](../00_scope/master_execution_plan.md) | 18,289 | `66D92810C12BF23B6EA1ED87FEA8C091801BAC5E8568651839A23BF0C4CD3A43` | 匹配 |
| [`06_reproduction/README.md`](../06_reproduction/README.md) | 1,087 | `9F17EADD406E898C30EDD7047F35D638F1D909FB01312AD295B41456AD678661` | 影响面快照 |
| [`M8_decision_package.md`](../00_scope/M8_decision_package.md) | 13,018 | `931746ABFC303497FA68590F68D6F1F7A0872C956050842626DB1CD851F6E0FA` | 影响面快照 |
| [`direct-environment.yml`](../06_reproduction/environment/direct-environment.yml) | 494 | `57D49382584C9A82080436A90564972BC3007E9921848E3CB74A5E701295D491` | 未变 |

五个委托指定修订哈希全部匹配。两个 JSON 文件均可被严格解析；预算合同的三个 GPU 桶之和为

\[
7200+57600+21600=86400\ \mathrm{s}=24\ \mathrm{GPU\,h},
\]

墙钟上限为 604,800 秒，存储上限为 107,374,182,400 字节。只读文件系统核对确认 `E:\Laptop\WSL\ext4.vhdx` 当前存在；该核对不证明未来预算合规，只证明机读合同引用的宿主路径是实际对象。

## 3. 原阻塞项逐项复核

### 3.1 `M9-F-WP-B01`：CLOSED

原问题要求在 D-013 后建立不可覆盖的独立 M9 授权记录，并统一主计划、M8 决策包、预检和复现 README 的状态。

修订后的 D-014 `decisions.md:129-139` 明确记录：用户是在 D-013 之后对单独提出的 M9 执行范围回复“授权”，不是从 M8 冻结推定；允许动作包括现有 WSL 配置、冻结依赖和 DeepH-pack 安装、官方 graphene 下载及复现实验；禁止 OpenMX/其他 DFT、正式标签生成、静默换路线和自动重启；口令不得读取、复制、持久化或回显；M9-01 问题清零仍是 M9-02 的前置条件。D-014 还固定首次送审工作包 SHA-256，修订只收紧合同而不扩大授权。

`m9_preflight.json:4-10` 同时引用 D-013、D-014，并保持 DFT、标签生成和自动重启为 `false`。主计划 `master_execution_plan.md:66,82` 已把 M9 统一为 `REVIEW`，明确当前是“已授权但等待 M9-01 定点复核”；复现 README `06_reproduction/README.md:5` 和 M8 决策包 `M8_decision_package.md:10,123` 使用同一状态与禁止边界。授权来源、范围、禁止项和门控状态现在唯一且可追溯，B01 关闭。

### 3.2 `M9-F-WP-B02`：CLOSED，但修订引入 B05

原问题要求把 7 天、24 GPU 小时、2/16/6 GPU 小时子桶和 100 GiB 转化为统一、机读、可执行的计量和硬停止合同。

工作包 `M9_stageF_work_package.md:46-54` 与 `budget_contract.json:1-59` 已实现下列要求：

- 7 天从定点复核通过后的第一个变更性 M9 命令开始，保存 UTC 起点和固定截止；每条后续命令执行前检查剩余时间，并以剩余秒数作为 timeout 上限；
- 单卡 GPU 时间按全部 M9 CUDA 进程占用区间的并集累计，成功、失败、异常退出、OOM、烟雾、训练、验证、复跑、推理和诊断均计入；
- `compatibility=7200`、`training=57600`、`physical_validation=21600` 三桶互斥，总和严格等于 86,400 秒；事件保存桶、UTC/单调时钟、PID、退出码、命令/配置哈希和累计值；
- 存储同时记录 Linux 工作根的表观字节、实际分配字节和宿主 VHDX 相对起点的增长，三项分别受 100 GiB 上限约束；下载、解压、图生成和训练前必须记录现值、保守预测增量和预测后值；
- 达到任一墙钟、GPU 总量/子桶或存储上限，或者预测下一不可分割操作会越界时，拒绝启动、写入 `HARD_STOP` 并暂停；统一停止清单 `M9_stageF_work_package.md:134-151` 也已同步。

这些内容满足 B02 原最小关闭条件，因此 B02 本身关闭。新出现的产物放置矛盾单独登记为 B05，不能借 B02 关闭而忽略。

### 3.3 `M9-F-WP-B03`：CLOSED

原问题要求 M9-04 对旋转、反演、时间反演逐项判定适用性，并让 M9-06 对适用项冻结变换约定、配对对象、残差和失败样例，至少覆盖非磁无 SOC graphene 的无自旋时间反演 (H/S) 与广义谱关系。

工作包 `M9_stageF_work_package.md:88-99` 现在要求数据契约逐项判定刚体旋转、空间反演和无自旋时间反演的适用性，并定位结构或 (k) 点配对、轨道基变换、相位和 parity 数据；缺少合法对象时必须明确其是否触发数据契约失败。M9-06 `M9_stageF_work_package.md:107-124` 已分别规定：

- 旋转采用 AO 块协变回拉，并冻结主动/被动方向、轨道表示、edge/(k) 键、残差归一化及定向错误失败样例；
- 反演采用轨道 parity 和 (k) 点映射验证 (H/S)，并包含漏 parity 或错配对失败样例；
- 非磁无 SOC graphene 至少验证 (H(\mathbf{k})=H(-\mathbf{k})^*)、(S(\mathbf{k})=S(-\mathbf{k})^*) 及对应广义谱对称性，同时冻结 Fourier 相位、规范键、简并匹配和漏共轭失败样例。

修订没有把缺失对象静默记为不可评估，也没有用能带对称性替代矩阵级 (H/S) 验证。B03 关闭。

### 3.4 `M9-F-WP-B04`：CLOSED

原问题要求全部验收阈值在 M9-04 数据与精度核对完成后、任何 M9-05 训练或模型输出观察之前冻结。

工作包 `M9_stageF_work_package.md:124` 现已逐字落实该顺序：阈值只能在数据清单、官方配置和精度核对之后登记，且必须早于任何训练、使用模型输出的验证、试推理或诊断。机读阈值清单必须包含指标定义、归一化、聚合、单位、适用子集、绝对/相对容差、依据、UTC 和 SHA-256；冻结后只允许因书写或实现错误通过新决策修订，并保留旧值、理由和新值，不得依据已观察模型结果放宽。B04 关闭。

## 4. 新增 BLOCKING

### `M9-F-WP-B05`：预算合同无条件禁止 Linux 工作根之外的 M9 产物，与强制项目侧产物冲突

**位置与证据。** `budget_contract.json:52-59` 的硬停止对象包含

```json
"paths_outside_linux_root_for_m9_artifacts_forbidden": true
```

该字段没有把“大型运行产物”与“小型项目侧审计产物”区分，也没有例外路径。相反，工作包 `M9_stageF_work_package.md:44` 明确要求项目侧保存不含凭据的小型清单、配置、验证代码和报告；复现 README `06_reproduction/README.md:3,9-20` 将 `06_reproduction/manifests/`、`configs/`、`scripts/`、`tests/` 和 `reports/` 全部定义为 M9 的预期项目侧产物。这些路径位于 Windows 项目工作区，不在 `/home/evan-williams/deeph-m9` 内。当前预算合同文件自身也位于项目侧 `06_reproduction/manifests/`。

**影响。** 若严格执行机读布尔字段，后续生成工作包强制要求的项目侧配置、测试、清单和报告即违反预算合同；若忽略该字段，则“不得移到合同外路径规避预算”的机器约束没有明确适用范围。两种解释都不能形成唯一、可自动验证的产物布局与存储预算结论，因此该矛盾必须在 M9-02 前消除。

**最小关闭条件。** 将机读字段收窄为“禁止把软件、环境、正式数据、图缓存、检查点、运行日志及其他大型/运行时产物移出 Linux 工作根以规避预算”，并显式列出允许的项目侧小型审计路径 `06_reproduction/environment/`、`manifests/`、`configs/`、`scripts/`、`tests/`、`reports/`。同时冻结项目侧增量的处理口径：将其计入 100 GiB 总量，或设定一个明确、保守且计入总预算的小型产物子上限；无论采用哪种口径，都不得删除已登记证据或把大型产物伪装为项目侧小文件规避上限。同步工作包相关文字和 JSON schema 后，重新固定二者 SHA-256。

## 5. 新增问题与回归检查

除 B05 外，没有发现修订引入新的授权扩大、禁止项弱化、版本/材料/后端漂移、预算数值错误、对称性公式方向错误或阈值后验放宽。`direct-environment.yml` 保持未变；D-014 没有授权 OpenMX/其他 DFT、标签生成或自动重启；M9-01 仍明确要求问题为 0 才可开始系统包、语言环境和 DeepH 安装。

`NON_BLOCKING=0`。B05 是可局部修复的机器合同冲突，不是措辞便利性问题，故不降级为非阻塞建议。

## 6. 最终门控意见

原 B01—B04 已全部关闭，但当前仍有新增 `M9-F-WP-B05`。因此本轮不能给出 `PASS`，也不允许启动 M9-02。主 agent 只需修订预算合同及工作包中直接相关的产物放置/计量文字，不应改变 D-013/D-014、2/16/6 GPU 小时、7 天、100 GiB、数据、软件、硬件、对称性或阈值冻结范围。

第二次定点复核至少应确认：

- 项目侧允许路径与 Linux 运行根的对象类别互斥、无矛盾；
- 项目侧增量具有明确的 100 GiB 计量或子上限口径；
- 大型/运行时产物不能通过移出 Linux 根规避预算；
- 预算证据不得删除；
- B05 关闭且无新增问题。

只有第二次定点复核明确给出 `PASS`、`BLOCKING=0`、`NON_BLOCKING=0` 后，才允许启动 M9-02。该放行仍只表示可以开始环境安装与兼容性门控，不表示 PyTorch 1.9.1/CUDA 11.1 在计算能力 8.9 上已经兼容，也不表示数据、训练、矩阵、对称性或物理验收已经通过。

## 7. 报告自身验证方法

本报告最终内容固定后，应执行 UTF-8 非 CR/LF/TAB 控制字符扫描；活动本地 Markdown 链接存在性检查；Pandoc 3.6.4 使用 `markdown+tex_math_single_backslash`、`--fail-if-warnings` 和 HTML5 MathML 的严格转换；检查输出中实际存在 `<math>` 节点；最后计算报告 SHA-256。报告自身哈希不嵌入正文，以避免自引用改变文件内容；严格验证结果和最终 SHA-256 由交付消息给出。
