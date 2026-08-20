# M9 source-control recovery 控制包第二十二次最终定点复核

## 结论

本轮独立只读定点复核结论为 **PASS**：`BLOCKING=0`，`NON_BLOCKING=0`。上一轮保持开放的 `M9-SPR-IMP-B01` 与 `M9-SPR-IMP-B05` 均已满足最小关闭条件；连同此前已经关闭的 `M9-SPR-IMP-B02`、`B03`、`B04`、`B06` 和测试污染问题 `M9-SPR-R3-B01`，当前 source-control recovery 控制包不存在已知未关闭问题。

本 PASS 仅允许主 agent 按明确授权创建一次性 source-control recovery gate。它不授权执行 gate、recovery、`source_prepare` 或其他运行时动作。

## 冻结闭集与正式测试

独立复算的四项 SHA-256 与指定冻结快照完全一致：

- `06_reproduction/scripts/m9_budget.py`：`0b49bd41f17caa56fa088cee2620dcb965df9c57b3e9b02bf3eeba853e178e49`
- `06_reproduction/tests/test_m9_overlap_controls.py`：`3cfccbeb70dcf7311889738b52b387e890c33170e89d74eb129f8ec366959351`
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：`7875ff2e2114210e33c52de2de59ee1c8d3f64171a85dc78d30514e7e91357ed`
- `06_reproduction/manifests/m9_source_control_test_cleanup_frozen_hashes.json`：`332e25c05ab0739da10a991601883fc6363d962ef18ee5da9e2199e08226908c`

source recovery manifest 的 17 个对象为 `17/17` 匹配，cleanup manifest 的 4 个对象为 `4/4` 匹配。冻结解释器 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9` 实际版本为 Python 3.9.23；`sys.executable` 与冻结路径一致，`isolated=1`、`no_site=1`、`dont_write_bytecode=true`。以该解释器执行：

```text
/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B \
  /mnt/e/Projects/Codex/DeepH/06_reproduction/tests/test_m9_overlap_controls.py
```

冻结测试文件实际发现并执行 66 项，而不是修订前的 61 项；新增数量对应本轮定点覆盖。结果为 `Ran 66 tests`、`OK`，进程退出码 0。测试进程 UID 为 1000。控制脚本和测试目录中的 `.pyc`、`.pyo`、`__pycache__` 合计为 0。

## M9-SPR-IMP-B01：CLOSED

当前 source recovery verifier 要求审计 JSON 位于 `08_audits` 直接子路径，并同时验证：

- audit verdict schema 精确为 `m9-source-control-recovery-audit-verdict-v1`；
- decision ID 精确为 `D-017-source-control-recovery-v1`；
- `verdict=PASS`、`blocking=0`、`non_blocking=0`；
- audit verdict、授权记录和 source frozen manifest 的固定路径与 SHA-256；
- source frozen 文件集合与代码内 17 项闭集严格相等、逐项哈希匹配，且控制目录不存在额外缓存、符号链接或子目录。

冻结测试分别证明错误 verdict schema、错误 decision、自由报告路径、授权内容漂移、冻结对象漂移及控制目录 cache 均在 gate 验证阶段停止。独立临时复现进一步把当前 cleanup 专用结构化 PASS JSON 绑定到内存构造的 source recovery gate；实际 verifier 返回 `source-control recovery gate lacks structured PASS verdict`。因此，其他决策域的零问题 PASS 不会被错误归入 source recovery。

`command_overlap_recover_source_control_failure()` 在 EUID 检查后立即调用 `isolated_bootstrap_provenance()`，其调用顺序早于 gate verifier、gate receipt、锁获取和任何状态动作。独立入口探针令 bootstrap 固定停止，结果为 `GATE_CALLED False`；冻结正式测试同时以系统 Python 3.10 和缺少 `-S` 的冻结 Python 调用验证错误解释器/标志组合均失败，且三个正式 recovery 对象逐字节不变。

首次 recovery transaction 持久化 `python_bootstrap` 及 `gate_receipt`。后者绑定 decision ID、gate 字节 SHA、audit verdict 路径/SHA、授权 SHA 和 frozen manifest SHA；每次 resume 均要求当前 bootstrap 与 gate receipt 精确等于持久化值。由此，B01 对专用审计域、冻结入口顺序以及 bootstrap/gate receipt 持久化的最小关闭条件全部满足。

## M9-SPR-IMP-B05：CLOSED

正式状态机测试把 state、workflow、failed parent transaction、ledger、lock、recovery transaction、parent snapshot、gate、capability root 和全部 source/build 产品重定向到自动删除的临时闭集。它先执行完整首次成功基线，再分别在以下 11 个已经发生持久化动作后的窗口注入 `KeyboardInterrupt`：

`parent_snapshot`、`prepared`、`capability_rename`、`capability_retired`、`success_pending`、`ledger_append`、`ledger_phase`、`state_write`、`state_phase`、`workflow_write`、`terminal`。

每个窗口均证明第一次调用在指定半提交现场停止，第二次调用从持久化证据续提到 `SUCCESS_COMMITTED`；stale capability 被迁移为 retired，recovery event 恰好一次，`python_bootstrap` 和 source recovery `gate_receipt` 保持绑定。每个中断分支的最终 recovery receipt 结构与无中断首次成功基线同构。随后对 state、workflow、parent transaction、ledger、recovery transaction、parent snapshot 和 retired capability 的完整字节集合执行终态 replay，所有字节均不变。

漂移矩阵从真实 `PREPARED` 半提交状态分别注入 parent transaction 漂移、parent ledger 额外 event、相同 event ID 的不同载荷、有效 JSON ledger 顺序改变、state 漂移、workflow 漂移、bootstrap receipt 漂移和 gate receipt 漂移。每项均返回 125，把 state/workflow 置为双 HARD_STOP，并把 recovery journal 置为 `FAILED_COMMITTED`。成功终态后的 state、workflow 或 ledger 漂移也分别返回 125 并进入 HARD_STOP。因此 raw ledger 前缀、事件集合、事件顺序、载荷一致性及 parent/terminal receipts 都具有显式失败语义。

launcher 选择规则的真实临时复现证明 `.retired.json` 后缀不能作为活动 capability 消费。正式测试运行于 UID 1000，创建 mode 0600、state `BOUND`、action `source_prepare` 的全新 capability；launcher 第一次消费形成 `CONSUMED` receipt 并删除活动路径，第二次消费返回“未签发”。由此，B05 对完整首次成功、11 个中断续提窗口、终态零写入 replay、漂移矩阵、retired 不可消费和 UID 1000 新 capability 一次性生命周期的最小关闭条件全部满足。

## 正式现场前后不变性

完整测试及独立临时探针前后，五项正式 runtime SHA-256 保持不变：

- budget state：`1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`
- workflow：`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`
- failed transaction：`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`
- ledger：`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`
- stale capability：`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`

这保持了此前已审计的 failed parent transaction、双 HARD_STOP、ledger tip、stale capability 和缺席消费证据。六项 source/build 产品继续缺席；正式 `overlap_source_control_recovery.json`、`overlap_source_control_recovery_parent.json` 和 `overlap_source_control_recovery_gate.json` 三个 recovery 对象也继续缺席。

cleanup 执行证据同样保持不变：

- retired 测试对象：`2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`
- retirement receipt：`74b24867d06a437f0e693c8edd231ab4bc31782b8978abfff77b01658567fd49`
- cleanup journal：`1e0729d72bb7e45e773a61d9aff6228061a5b000cd218c23e5263153f2425d8d`
- cleanup gate 与 root 私有 snapshot：`12cec1f13eec81c110b8a7d66aecaf4e1786c0821c82a702885b9e74cfeb57b2`，两者逐字节相等
- security migration journal：`60fef9c099bfc345973bb9ac074f084f48e5e542508681fa4d55ceb099ba5c94`

retired、receipt 和 cleanup journal 为 root:root、0600、nlink 1；trust root 为 root:root、0700，snapshot 与 migration 为 root:root、0600、nlink 1。manifests root 为 root:GID 1000、1770 sticky。上述证据与测试前基线一致，证明正式测试未复活 active 伪 transaction，也未写入 cleanup 证据。

## 稳定问题与放行边界

- `M9-SPR-IMP-B01`：CLOSED。专用 verdict schema/decision、冻结闭集、bootstrap 前置及 bootstrap/gate receipt 持久化均已验证。
- `M9-SPR-IMP-B02`：CLOSED。固定失败事务、runtime、ledger tip、stale capability 和六项产品闭集未漂移。
- `M9-SPR-IMP-B03`：CLOSED。parent snapshot、PREPARED 与 capability retirement 的持久化恢复语义由完整中断矩阵验证。
- `M9-SPR-IMP-B04`：CLOSED。ledger/state/workflow 的提交顺序、半提交续提、双 HARD_STOP 和终态核验由完整状态机测试验证。
- `M9-SPR-IMP-B05`：CLOSED。首次成功、11 个 crash window、终态零写入、漂移矩阵和一次性 capability 生命周期均已覆盖。
- `M9-SPR-IMP-B06`：CLOSED。更新后的四项冻结 SHA、source `17/17`、cleanup `4/4` 和 cache=0 均独立复算通过。
- `M9-SPR-R3-B01`：CLOSED。active 测试伪对象缺席，retired/receipt/journal/trust-root 证据完整且测试前后不变。

最终计数为 `BLOCKING=0`、`NON_BLOCKING=0`。最小放行范围为 `CREATE_SOURCE_CONTROL_RECOVERY_GATE_ONLY`。即使创建 gate，仍不得据此执行 recovery 或 `source_prepare`；实际 recovery 需要另行明确授权，并在执行后接受独立只读事实审计。

本轮除新增本报告及其专用结构化 verdict 外未修改任何被审对象或正式运行时；未创建或执行 gate、recovery 或 `source_prepare`。全部定点复现仅使用自动删除的临时目录或在状态动作之前停止。
