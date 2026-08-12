# M9 阶段 F 工作包第二次定点复核

## 1. 正式结论

**结论：PASS。** `M9-F-WP-B05` 已关闭；第一次定点复核已关闭的 `M9-F-WP-B01`—`M9-F-WP-B04` 未发生回归。本次没有发现新增问题。

- `M9-F-WP-B01`—`M9-F-WP-B05`：`CLOSED=5`，`OPEN=0`；
- 新增 `BLOCKING=0`；
- 新增 `NON_BLOCKING=0`；
- 当前总剩余 `BLOCKING=0`、`NON_BLOCKING=0`；
- 是否允许启动 M9-02：**允许**。

该放行严格限定为 D-013/D-014 和修订工作包规定的 M9-02：可以开始冻结的 WSL 系统工具、Python/Julia/CUDA 用户态环境与依赖安装，并随后进入固定 DeepH-pack 的兼容性门控。它不表示 PyTorch 1.9.1/CUDA 11.1 已在计算能力 8.9 上兼容，不表示可以安装 OpenMX/其他 DFT、生成正式标签或自动重启，也不表示数据、训练、矩阵、对称性或物理验收已经通过。

## 2. 复核范围、约束与输入快照

本次只复核第一次定点报告 [`M9_stageF_work_package_blocking_reaudit.md`](M9_stageF_work_package_blocking_reaudit.md) 的 B05、B01—B04 回归面及三份委托修订文件。除新增本报告外，没有修改任何被审材料；没有安装软件、下载正式数据、启动训练、读取 WSL 用户文件或接触认证口令。

| 输入 | 字节数 | SHA-256 | 判定 |
|---|---:|---|---|
| [`M9_stageF_work_package_blocking_reaudit.md`](M9_stageF_work_package_blocking_reaudit.md) | 12,009 | `112A839D6D40422260848A94D3FAFAB2141F3ADA0A2BF79EFD012BCEA79FE008` | 第一次复核基线 |
| [`M9_stageF_work_package.md`](M9_stageF_work_package.md) | 11,349 | `E7167988D8A66711BF40E249D75DC5B812DD646632B7E194642C9042C86743BA` | 匹配委托快照 |
| [`budget_contract.json`](../06_reproduction/manifests/budget_contract.json) | 2,825 | `B428C01437A57F63BFD0809F31F64A6432422FE8890EC0A8FBD28B7580FEACE9` | 匹配委托快照 |
| [`06_reproduction/README.md`](../06_reproduction/README.md) | 1,253 | `2C3A457F2DA3136F92AEECCB7AEBDF5FF9885EFFAFC2642B006785AB174CB11D` | 匹配委托快照 |
| [`decisions.md`](../decisions.md) | 15,272 | `28146406676BF3A22E388C4539BCF541E5AA7AC83DCB3AAE67FE2A8E46226C6D` | B01 基线未变 |
| [`m9_preflight.json`](../06_reproduction/manifests/m9_preflight.json) | 1,035 | `B6F787A1F88FDAC006531F5398AE45215C39CE942D3CEA0D3F4B97141FED1B83` | B01 基线未变 |
| [`master_execution_plan.md`](../00_scope/master_execution_plan.md) | 18,289 | `66D92810C12BF23B6EA1ED87FEA8C091801BAC5E8568651839A23BF0C4CD3A43` | B01/B03 基线未变 |
| [`M8_decision_package.md`](../00_scope/M8_decision_package.md) | 13,018 | `931746ABFC303497FA68590F68D6F1F7A0872C956050842626DB1CD851F6E0FA` | 授权与预算基线未变 |
| [`direct-environment.yml`](../06_reproduction/environment/direct-environment.yml) | 494 | `57D49382584C9A82080436A90564972BC3007E9921848E3CB74A5E701295D491` | 冻结依赖候选未变 |

三个委托修订哈希全部匹配。`budget_contract.json` 可被严格 JSON 解析；墙钟、GPU 与存储数值仍分别为 604,800 秒、86,400 秒和 107,374,182,400 字节，GPU 三个互斥桶仍满足

\[
7200+57600+21600=86400\ \mathrm{s}=24\ \mathrm{GPU\,h}.
\]

## 3. `M9-F-WP-B05` 定点复核：CLOSED

### 3.1 对象分类与路径白名单

第一次复核指出，原 `paths_outside_linux_root_for_m9_artifacts_forbidden=true` 无条件禁止所有 M9 产物位于 Linux 根之外，与项目侧必须保存的小型审计产物直接冲突。

修订工作包 `M9_stageF_work_package.md:53-55` 现在把对象分为两类：

- 大型软件、安装环境、正式下载、解压数据、图、检查点、日志和运行时结果只能位于 `/home/evan-williams/deeph-m9`；
- 项目侧只允许保存机读白名单中的小型清单、配置、脚本、测试、控制文档和 M9 审计/报告，不得借白名单保存数据集、环境、检查点或大型运行时对象。

机读合同 `budget_contract.json:40-58,80-87` 将允许范围具体化为：完整目录 `E:\Projects\Codex\DeepH\06_reproduction`、文件名前缀 `E:\Projects\Codex\DeepH\08_audits\M9_`，以及 README、决策记录、主计划、M8 决策包、版本注册表和进度台账六个精确控制文件。硬停止字段已收窄为 `large_or_runtime_artifacts_outside_linux_root_forbidden=true`，同时规定只有该项目侧白名单可以出现在 Linux 根之外。工作包、JSON 和复现 README 的对象分类与路径集合现在一致，不再禁止合同自身、配置、测试或审计报告。

`budget_contract.json:52-57` 的 `forbidden_content` 中 `environment` 应按同一合同上下文解释为已安装环境或环境目录，而不是环境规格、锁文件或重建声明；否则当前白名单中的 `06_reproduction/environment/direct-environment.yml` 会产生自相矛盾。工作包 `M9_stageF_work_package.md:53` 和 README `06_reproduction/README.md:3` 已明确禁止的是“大型软件、环境”以及“数据集、环境或检查点”，同时允许小型配置。结合冻结文件自身位于 `environment/` 目录且工作包 M9-02 明确要求输出环境锁和重建命令，唯一一致的可执行解释是：项目侧可保存环境规范与锁证据，不可保存实际安装环境。该语义足以执行，未形成新的开放问题。

### 3.2 1 GiB 子上限和当前证据

项目侧白名单子上限明确冻结为 1,073,741,824 字节。第二次复核报告生成前，独立递归清点得到：

- `06_reproduction/` 中 4 个现有文件；
- `08_audits/M9_*` 中 3 个现有文件；
- 上述 7 个 M9 专用工作文件合计表观大小严格为 46,675 字节，与委托给出的当前证据一致；
- 六个精确控制文件当前完整表观大小合计为 173,482 字节；
- 若按机读合同对全部当前白名单文件完整计量，去重后的总表观大小为 220,157 字节，仍远低于 1 GiB。

46,675 字节是 M9 专用目录/前缀对象的当前小计，不是包含六个精确控制文件后的全部白名单总量。该差异不构成合同冲突，因为机读合同要求运行账本记录 `project_audit_apparent_bytes` 和 `project_audit_allocated_bytes`，实际执行时应对全部白名单对象去重后计量；本报告新增后也必须在第一个变更性 M9 命令前重新实测，而不能继续沿用 46,675 字节作为起始总量。

### 3.3 合并 100 GiB 与 VHDX 独立上限

`budget_contract.json:36-79` 已同时定义下列存储指标：

- Linux 工作根表观字节与实际分配字节；
- 项目侧白名单表观字节与实际分配字节；
- 两者去重后的合计表观字节与合计分配字节；
- `E:\Laptop\WSL\ext4.vhdx` 相对预算起点的增长。

合计表观字节、合计分配字节和 VHDX 增长分别受 107,374,182,400 字节上限约束；项目侧白名单还独立受 1 GiB 子上限。工作包要求下载、解压、图生成和训练前记录当前值、保守预测增量与预测后值；达到或预测超过任一墙钟、GPU、项目侧子上限或总存储上限时，拒绝启动操作、写入 `HARD_STOP` 并暂停。不得删除已登记证据、把大型对象移入白名单或移到其他合同外路径规避预算。

该设计同时防止“Linux 逻辑占用小但 VHDX 膨胀”和“把运行对象移到项目目录规避 Linux 计量”两类逃逸。B05 的最小关闭条件已全部满足，判定关闭。

## 4. B01—B04 回归复核

| 原问题 | 状态 | 回归证据 |
|---|---|---|
| `M9-F-WP-B01` 授权链 | `CLOSED` | D-014、预检、主计划、M8 决策包均未变；M9 仍为已授权但等待 M9-01 复核的 `REVIEW`，DFT、标签生成和自动重启仍禁止 |
| `M9-F-WP-B02` 预算计量 | `CLOSED` | 7 天、24 GPU 小时、2/16/6 桶、100 GiB、失败/OOM计入、预测硬停和证据保留均未弱化；B05 修订增加了项目侧子限额和合并计量 |
| `M9-F-WP-B03` 对称性验收 | `CLOSED` | M9-04 适用性判定与 M9-06 rotation、inversion、spinless time-reversal (H/S) 及广义谱要求保持不变 |
| `M9-F-WP-B04` 阈值冻结 | `CLOSED` | 全部阈值仍必须在 M9-04 后、任何训练或模型输出观察前冻结，且不得依据结果放宽 |

B05 修订仅收紧产物布局和预算计量，没有扩大授权、改变冻结软件/数据/材料/后端/物理范围，也没有削弱兼容性、数据契约、矩阵、对称性、物理或独立总审计门控。

## 5. 新增问题与最终门控意见

新增 `BLOCKING=0`，新增 `NON_BLOCKING=0`。原审计及两次复核累计的 B01—B05 均已关闭，当前没有剩余问题。

因此允许启动 M9-02。执行时必须以第一个变更性 M9 命令建立预算账本起点，重新实测 Linux 根、全部项目侧白名单对象和 VHDX 基线，并严格遵守 D-014、工作包和预算合同。若旧 PyTorch/CUDA 栈在计算能力 8.9 上失败、需要 Windows 重启、需要改变冻结对象、达到或预测超过预算，必须保存证据并暂停，不得自行升级、换源、换材料、安装 DFT 或生成标签。

## 6. 报告自身验证方法

本报告最终内容固定后，应执行 UTF-8 非 CR/LF/TAB 控制字符扫描；活动本地 Markdown 链接存在性检查；Pandoc 3.6.4 使用 `markdown+tex_math_single_backslash`、`--fail-if-warnings` 和 HTML5 MathML 的严格转换；检查输出中实际存在 `<math>` 节点；最后计算报告 SHA-256。报告自身哈希不嵌入正文，以避免自引用改变文件内容；最终验证计数和 SHA-256 由交付消息给出。
