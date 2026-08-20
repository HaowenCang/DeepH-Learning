# M9 overlap-only 离线 apt 恢复第二次定点复核

## 复核结论

第二次定点复核结论为 `FAIL`。首轮报告的 `M9-REC-B01`、`M9-REC-B02`、`M9-REC-B05` 和 `M9-REC-B06` 已满足最小关闭条件；`M9-REC-B03`、`M9-REC-B04` 和 `M9-REC-B07` 仍为 `OPEN`。当前统计为 `BLOCKING=3`、`NON_BLOCKING=0`。

不得基于本报告创建状态为 `PASS` 的 `overlap_offline_recovery_gate.json`，不得执行离线安装，也不得进入 HDF5/OpenMX 构建。剩余问题均为恢复控制与后续 gate 衔接缺陷，不改变用户已经批准的软件、数据、输出、物理范围或 300 秒恢复上限。

本轮最终送审快照的主要 SHA-256 为：

- `m9_budget.py`：`74952228f217570aa697d5844937859393332e59ab98f900e5e657170cbdc514`；
- `m9_offline_recovery_frozen_hashes.json`：`05fb5c91f63351a045d20fe019a56b6ce688847a7939906827c9bab311c1dcce`；
- `m9_offline_apt_manifest.json`：`f54d61cbf4f6cb82dcd1cd0daa17ff2cf013f328b19d3222cff1a37dba637616`；
- `test_m9_overlap_controls.py`：`bfb5f20bb6f1a69cf091839421890ea5838ebebf78458b8093d4cc4fb806b1bf`；
- 首轮独立报告：`c30f03845e6979e6ce171006a6166e647d63f6c55b95fce599921293a18b92fb`。

## 边界与独立证据

本次只读检查当前项目对象、WSL APT 索引、本地归档和运行时状态；执行了无安装作用的来源链、哈希、AST、冻结 Python 测试及定向穿透。没有创建 recovery gate，没有安装或配置包，没有修改预算、workflow 或 transaction，没有解压或编译 HDF5/OpenMX。唯一新增项目文件为本报告。

冻结 Python 3.9 以 `-I -S -B` 运行正式测试，22/22 通过；`m9_budget.py` AST 解析通过。测试通过是回归证据，不替代下述定向状态机检查。

## 已关闭项

### `M9-REC-B01`：`CLOSED`

来源验证现在从已验签的 jammy 和 jammy-updates InRelease 中解析 `SHA256` 段，并按 suite、component、相对路径、bytes 和 SHA-256 核对四个 Packages 文件。逐包索引由单记录改为记录集合，因此相同 package/version/architecture 出现在多个组件时不再由遍历顺序覆盖；45 项均能找到同时匹配规范化 Filename 和归档 SHA-256 的记录。

独立复算确认 45/45 归档 bytes、MD5、SHA-256 和 Debian control identity 一致；四个 Packages 文件均与相应 InRelease 的 SHA-256/bytes/path 记录一致；正式来源链测试通过。首轮的多记录覆盖和未强制 InRelease 摘要关系已关闭。

### `M9-REC-B02`：`CLOSED`

recovery gate 现在要求固定 schema、`PASS`、零问题、D-017 recovery decision ID 和唯一报告路径 `08_audits/M9_offline_recovery_blocking_reaudit.md`。`files` 必须与代码内必需集合精确相等；候选 recovery frozen manifest 的 `files` 又必须与 gate 去掉 manifest 自身后的映射精确相等。缺失或额外对象均不能通过。

候选 manifest 当前逐项绑定恢复授权、预算入口、offline manifest、预算合同、overlap 合同、正式测试和工作包；gate 另行绑定候选 manifest 与本报告。因此首轮指出的任意非空子集 gate 穿透已经关闭。B07 指出的 follow-up 文件范围是相邻用途问题，不重新打开 gate 自身闭集问题。

### `M9-REC-B05`：`CLOSED`

全局 dpkg 状态 receipt 现在保存 package 到 `version\tstatus` 的规范映射。postcheck 要求 45 个目标包逐项精确等于 manifest version 与 `install ok installed`；要求新增包名集合精确等于 45 个目标；并要求所有非目标包的 version/status 与 pre 映射一致。`dpkg --audit` 和 updates 目录仍须为空。

因此，既有包版本或状态漂移、目标版本错误和额外新增包均会触发恢复 HARD_STOP。首轮仅比较包名的问题已关闭。

### `M9-REC-B06`：`CLOSED`

恢复 transaction 现绑定 pre-ledger SHA-256、bytes、行数与末行 SHA-256，同时绑定 pre state、workflow 和原父 transaction。父快照改为直接复制原字节并立即回读验证，不再通过 JSON 重序列化产生不同字节。原父 transaction 仍不被恢复函数覆盖。

这些字段足以标识恢复开始时的共同证据前缀；首轮的 pre-ledger 缺失和父快照摘要不自洽已关闭。

## 仍开放的阻塞项

### `M9-REC-B03`：运行中子 PID 未及时进入 journal

入口能在重启时识别 `PREPARED`、`OFFLINE_APT_RUNNING` 和其他非终态 transaction；若没有活动子进程，会把恢复、预算和 workflow 提交为 `FAILED_COMMITTED/HARD_STOP`。这关闭了静态遗留状态。

但实际子 PID 只在 `run_recovery_child()` 等待子进程结束并返回后加入内存列表，并在全部命令结束后才写入 recovery transaction。一个 dpkg 子进程正在运行时，磁盘 transaction 的 `child_pids` 仍为空。此时第二个恢复入口取得预算锁，会把第一个入口的 transaction 判断为“无活动子进程”的非终态并提交 HARD_STOP；第一个 dpkg 进程却继续运行。硬停止因此不能阻止正在变更系统包状态的进程，且两个控制器随后会竞争写同一 transaction。

最小关闭条件：`Popen` 成功后、等待前，必须在同一预算锁下把 `active_child_pid`、进程组 ID、命令序号和 argv hash 写入 recovery journal；子进程终止并回收后再原子清除或移入 completed 列表。重入时检测到 live PID/进程组必须只拒绝并保持现状，不得提交 HARD_STOP；检测到 stale PID 才允许提交失败。需要覆盖真实长运行子进程、并发重入、stale PID、PID 重用身份核对和 controller kill 后整组终止的负例。

### `M9-REC-B04`：ledger 幂等性只比较 event ID，不比较事件内容

成功路径已增加 `SUCCESS_PENDING_COMMIT`、规范 commit events、`event_id`、flush 和 `fsync`，并在解除 HARD_STOP 前确认两个 ID 存在。这显著收紧了提交顺序。

但 `append_event_once()` 仅检查 ledger 是否已有相同 `event_id`。如果已有同 ID、不同载荷的记录，它会跳过正确事件；`resume_pending_recovery_commit()` 随后也仅检查 ID 集合并继续应用 credit、解除 HARD_STOP。独立定向重放写入同 ID、错误 event type 和错误 credited seconds 后调用 `append_event_once()`，错误行保持不变，而函数将其视为已提交。

最小关闭条件：幂等键必须绑定完整规范事件。读取 ledger 时应建立 `event_id -> canonical event hash` 唯一映射，拒绝重复 ID、同 ID 不同内容和不可解析行；`append_event_once()` 只有在现有规范 hash 与预期完全一致时才可跳过。recovery journal 应记录每个 commit event 的规范 SHA-256，resume 前后逐项核对。增加同 ID 错误 credit、错误 parent、错误 event type、重复 ID 和截断末行负例。

### `M9-REC-B07`：follow-up frozen manifest 仍不能通过自身验证

普通 overlap 动作在 workflow 含 `recovered_from_hard_stop` 时已经切换到 `verify_recovered_overlap_gate_and_hashes()`，不再仅使用旧 gate；方向正确。

但候选 recovery frozen manifest 顶层没有 `contract_sha256`，而 verifier 强制要求该字段等于 overlap contract 的实际 SHA-256。因此 follow-up 验证当前必然以 `recovered overlap contract hash mismatch` 退出。

更关键的是，manifest 的 `files` 只登记一个 Python 控制文件 `m9_budget.py`。随后 `verify_overlap_control_directory(frozen)` 要求控制目录实际 Python 文件集合与 frozen manifest 登记集合精确相等；目录中仍存在 source launcher、executor、build、input、contract、common 等正式 Python 文件，所以即使补上 `contract_sha256`，验证仍会拒绝。

此外，source_prepare 和后续动作会实际加载或调用上述控制对象，而当前 recovery manifest 未绑定它们。该范围不足以延续第五次工作包审计所建立的 source-only、executor、build 和 parser 边界。

最小关闭条件：follow-up frozen manifest 应包含 overlap contract 的顶层 SHA-256，并纳入旧 16 个执行控制对象中仍参与后续动作的完整集合，再以当前修订后的 `m9_budget.py`、recovery 授权、offline manifest、预算合同、测试和本报告扩展，而不是缩减为恢复入口的七个对象。recovery gate 可以保留较小的安装必需闭集，但 follow-up manifest 必须是可执行对象超集。增加恢复成功状态下 `source_prepare` gate 正例，以及缺任一控制 Python、旧 hash、错误 contract hash、控制目录额外文件和混合旧新 manifest 负例。

## 最终门控

- 第二次定点复核：`FAIL`；
- `BLOCKING=3`；
- `NON_BLOCKING=0`；
- 不允许创建 PASS recovery gate；
- 不允许执行离线安装或恢复后 follow-up；
- 当前不需要新的用户路线决策。

主 agent 应只修复 `M9-REC-B03`、`M9-REC-B04`、`M9-REC-B07` 及相邻回归，再交回同一独立审计员定点复核。只有三项均为 `CLOSED` 且问题计数为零，才能建立一次性 recovery gate。

## 报告终检

本报告定稿后执行 UTF-8 控制字符扫描、活动本地 Markdown 链接检查，以及 Pandoc `markdown+tex_math_single_backslash` 到 HTML5 MathML 的 `--fail-if-warnings` 严格转换。用于验证 MathML 的恒等式为 \(22=22\)。最终 SHA-256 在交付消息中报告。
