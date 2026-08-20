# M9 source-control recovery 第一次阻塞项复核

## 结论

本轮定点复核结论为 **FAIL**：`BLOCKING=6`，`NON_BLOCKING=0`。`M9-SPR-IMP-B01` 至 `M9-SPR-IMP-B06` 均未满足全部最小关闭条件。当前不得创建 source-control recovery gate，不得执行 `overlap-recover-source-control-failure`，也不得重试 `source_prepare`。

本结论不撤销已经成功提交的 offline apt recovery，也不改变 D-017 的用户授权边界。六项问题均是当前受控恢复实现及其验证证据内部的阻塞，不要求新增材料体系、DFT 后端、DeepH 对象或预算路线决策。

## 审计对象与只读边界

最终冻结送审对象实测为：

- `06_reproduction/scripts/m9_budget.py`：SHA-256 `ffdaaaafc6e0defa68bafb24224bcb11f5bce3f2515e89a7c82c763a047c5971`；
- `06_reproduction/tests/test_m9_overlap_controls.py`：SHA-256 `eb78a230b3cbe270418e574b92890aebdcdb76d3aa49c8a8f547e14b88e9d2ed`；
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：SHA-256 `36730b74d362d9b536f3f5cd08acc4dcc42fda1aac2b849e263f760b7b38a4b2`。

审计期间未创建 gate、recovery transaction 或 parent snapshot，未执行恢复 CLI，未改写 WSL 状态、capability、ledger、dpkg 数据库或 source/build 对象。当前以下正式恢复对象均不存在：

- `/home/evan-williams/deeph-m9/manifests/overlap_source_control_recovery_gate.json`；
- `/home/evan-williams/deeph-m9/manifests/overlap_source_control_recovery.json`；
- `/home/evan-williams/deeph-m9/manifests/overlap_source_control_recovery_parent.json`。

## 稳定阻塞项

### M9-SPR-IMP-B01：恢复 gate 的独立报告来源边界未闭合

当前 verifier 已要求独立 schema、零问题 PASS、D-017 decision ID、授权记录、结构化 JSON verdict、报告 SHA、冻结清单 SHA、失败事务对象和 stale capability 对象。这些是有效修复。

但是 `verify_source_control_recovery_gate_and_hashes` 没有把 `audit_report_path` 规范解析后限制在项目 `08_audits` 目录，也没有限制为本轮唯一指定的独立复核 verdict。任意位置的 JSON 只要自报 `verdict=PASS`、`blocking=0`、`non_blocking=0`，再由 gate 记录其 SHA，便可满足当前报告检查。相邻的 offline recovery verifier 已实施审计目录父路径约束，source-control verifier 没有保持同一边界。

最小关闭条件：要求规范绝对报告路径严格位于 `08_audits` 下，并固定为本轮独立复核产生的唯一结构化 verdict；继续绑定其 SHA 和零问题 PASS 字段。自由位置或其他报告不得充当 recovery gate 证据。

### M9-SPR-IMP-B02：preflight 产物闭集仍缺 staging

当前 preflight 已能在只读实机状态上通过。独立构造与当前失败事实完全一致的内存 gate 后，`source_control_preflight` 返回固定失败事务 `e5bfc046d4d5a1bd97507d37b40f1e0c`、固定 capability `f7c3b060e19e37e6da03f461d754d38c.json` 及 SHA-256 `0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`。既有只读源码仓库不再被误判为本次新产物；gate 也已精确绑定 capability path、ID、bytes、SHA、UID、GID 和 mode。

但是 `SOURCE_RECOVERY_PRODUCTS` 只检查最终 build root、HDF5 prefix 和三个 manifest，没有检查 `m9_openmx_build.prepare_sources` 实际使用的 `openmx-overlap-build.staging`。该 staging 目录在安全解压开始时即创建，直到最后才以 `os.replace` 变为 build root；因此它是 source preparation 失败后必须为 absent 的核心残留路径。当前实机 staging 的确不存在，但代码未把这一事实纳入 fail-closed preflight，未达到原 B02 对 build root 与 staging 同时为空的最小条件。

最小关闭条件：把由冻结 contract 推导的 `openmx-overlap-build.staging` 加入 source recovery 产物拒绝闭集，并加入其存在时拒绝、其不存在时通过的测试。路径应由固定 build-root contract 推导，不能接受自由输入。

### M9-SPR-IMP-B03：parent snapshot 不可作为可重放证据

首次执行的 `existing` 初始化、PREPARED 中的 stale/retired 路径和固定 event、retired bytes/SHA/UID/GID/mode receipt 均已修复。`process_matches_receipt` 的缩进错误也已修复。

剩余问题集中在 parent snapshot。实现先写 `overlap_source_control_recovery_parent.json.tmp`，再替换正式 parent snapshot，之后才写 PREPARED journal。若进程在正式 snapshot 替换后、PREPARED 写入前中断，下一次执行因为没有 recovery transaction 会删除临时文件并无条件覆盖现有正式 snapshot；它既不拒绝已有 snapshot，也不核对已有 snapshot 是否与固定父事务逐字节一致。`source_control_resume` 虽检查当前 `OVERLAP_TRANSACTION` 的 SHA，却从不读取或核验 `SOURCE_CONTROL_RECOVERY_PARENT`，因此 recovery 中记录的 `parent_snapshot_sha256` 不参与任何恢复判断。

最小关闭条件：正式 parent snapshot 必须使用不可静默覆盖的原子创建或“已存在则精确 bytes/SHA 验证”语义；PREPARED journal 应记录 snapshot 路径、bytes 和 SHA；每个 resume 路径必须核验正式 snapshot 与 journal 及固定失败事务一致。snapshot 与 PREPARED 之间中断后应能够安全重入，不得覆盖漂移证据。

### M9-SPR-IMP-B04：中间态恢复仍会分叉或接受 ledger 漂移

当前 resume 已核验当前父事务 SHA/ID，并在三个非终态检查 parent state 与 workflow SHA。这仍不足以形成四阶段崩溃恢复合同。

其一，journal 已记录 `parent_ledger_sha256`，但 `source_control_resume` 在追加 event 前不核验当前 ledger 是否等于 parent ledger，或在 SUCCESS_PENDING_COMMIT 时是否只增加了唯一、同载荷的目标 event。外部追加或损坏只要不触发 `ledger_event_ids` 的目标 ID 冲突，仍可能与恢复 event 一同被接受。

其二，event 成功追加后，代码依次写 budget state 和 workflow。若在 state 已解除 HARD_STOP、workflow 尚未解除时中断，下一次 resume 会因为 state SHA 不再等于 parent SHA 而调用 `source_control_hard_stop`，而不是识别合法的半提交阶段并完成幂等恢复。原最小条件要求每个 journal 写入点中断后可重放；当前实现只把这类合法中断转为失败。

其三，首次成功路径与 resume 成功路径分叉。resume 会记录 `post_state_sha256`、`post_workflow_sha256`、`post_ledger_sha256`，首次路径不会记录；`SUCCESS_COMMITTED` 重放则在 gate 校验后直接返回 0，不复核 retired receipt、唯一 ledger event、post state/workflow 或父快照。由此同一逻辑成功状态存在两种证据强度，终态 receipt 也不能自证。

最小关闭条件：在 journal 中明确记录 ledger 阶段和 state/workflow 提交阶段；按阶段只允许 parent ledger 或 parent ledger 加唯一同载荷 event；对 state-first/workflow-first 中断实施幂等完成或可证明的双硬停恢复；首次路径与 resume 共用一个提交函数并产生完全相同的 post receipts；SUCCESS_COMMITTED 重放必须先验证完整终态 receipt 才能返回 0。

### M9-SPR-IMP-B05：29 项测试没有验证恢复状态机

固定 Python 3.9 `-I -S -B` 下，29 项 unittest 已独立运行并全部通过，耗时约 6.0 秒。新增 source-control 测试仍只有四项：非 root 拒绝、两个 gate 路径对象不相等、通用 event 幂等以及字符串后缀断言。

这些测试没有执行 root 首次恢复、真实 preflight、staging 残留、capability gate binding、parent snapshot 中断、PREPARED/CAPABILITY_RETIRED/SUCCESS_PENDING_COMMIT 重入、ledger 漂移、state/workflow 半提交、终态重放或实际 retired capability 不可消费。`".retired.json".endswith(".retired.json")` 也不能证明活动 glob 与 launcher 消费规则真实排除 retired 文件。

最小关闭条件：使用临时完整状态树和受控 process receipts 做状态机级测试，逐一覆盖首次成功、每个持久化点中断与重入、B01/B02 全部漂移、同 ID 异载荷、parent snapshot 已存在且同/异内容、ledger 额外 event/损坏、双状态半提交、terminal replay、retired 不可消费、root 普通 overlap 拒绝以及 UID 1000 新 source_prepare capability 创建与消费。每个失败例必须断言 state/workflow/ledger/capability 的精确不变或规定的双 HARD_STOP 终态。

### M9-SPR-IMP-B06：冻结清单内部有一个字符级错误

source-specific frozen manifest 本身实测 SHA 为 `36730b74d362d9b536f3f5cd08acc4dcc42fda1aac2b849e263f760b7b38a4b2`，登记 17 个闭集对象。但其中 `m9_budget.py` 的 expected SHA 写成：

`ffdaaaafc6e0defa68bafb24224cbb11f5bce3f2515e89a7c82c763a047c5971`

实际 SHA 为：

`ffdaaaafc6e0defa68bafb24224bcb11f5bce3f2515e89a7c82c763a047c5971`

两者在 `...24cbb11...` 与 `...24bcb11...` 处发生字符次序错误，因此独立复算结果为 `16/17` 匹配，而不是 `17/17`。当前 verifier 会在 frozen file mismatch 处拒绝任何候选 gate。

最小关闭条件：完成 B01 至 B05 的代码与测试修复后重新生成 manifest，程序化复算全部 17 个或更新后的完整闭集，要求逐项 `N/N` 匹配并另行复算 manifest 本身 SHA。不得手工抄写散列。随后才能由独立审计生成唯一结构化零问题 PASS verdict，并由主 agent 依据最终 verdict SHA 与 manifest SHA 创建一次性 gate。

## 已确认的边界与放行判断

授权记录仍只允许处理这一次固定的 `source_prepare` capability owner/mode 控制失败，且明确不授权 source build、OpenMX smoke、批量 overlap、正式 DFT 标签或 M9-05。普通 overlap 入口的 EUID 1000 约束仍位于主要状态变更之前。当前真实 preflight 在提供正确固定事实时可达，现有 29 项测试没有既有回归；这些通过项不关闭上述六项阻塞。

当前不允许创建 source-control recovery gate，不允许执行 recovery CLI，也不允许再次启动 `source_prepare`。主 agent 可在既有 D-017 授权内修复 B01 至 B06；修复后须再次独立定点复核。只有 `BLOCKING=0`、`NON_BLOCKING=0`，且结构化 verdict、最终 frozen manifest 和一次性 gate 三者哈希闭合后，才允许执行一次 source-control recovery。实际 recovery 成功仍应接受只读结果复核，然后才能以 UID 1000 和全新 transaction/capability 重试一次 `source_prepare`；该放行不包含 `source_build`。

## 报告终检

本报告执行严格 Pandoc/MathML 转换、活动本地 Markdown 链接检查、UTF-8 非法控制字符扫描和 SHA-256 复算。最终结果随交付消息报告。
