# M9 source-control recovery 控制包最终阻塞复核

## 结论

本轮独立只读最终复核结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。`M9-SPR-IMP-B02`、`B03`、`B04`、`B06` 及测试污染问题 `M9-SPR-R3-B01` 已关闭；`M9-SPR-IMP-B01` 因审计 verdict 决策域与冻结解释器入口仍未闭合而重新开放，`M9-SPR-IMP-B05` 因正式恢复状态机测试仍不完整而保持 OPEN。

当前不得创建一次性 source-control recovery gate，不得执行 recovery，也不得执行 `source_prepare`。cleanup 执行审计的零问题 PASS 只关闭测试污染及其清理事实，不替代 source-control recovery 自身的 gate/verifier 和状态机测试要求。

## 冻结对象与正式测试

当前送审对象的独立 SHA-256 为：

- `06_reproduction/scripts/m9_budget.py`：`cbc3ee8aadb6f9494af4fc870fff392d53bcb72b45fa91de90f546f51f7deb5c`
- `06_reproduction/tests/test_m9_overlap_controls.py`：`0f2c86a13637ff4cec376d287e387e5dc1d317219e6afdc33cfce6812a96b91a`
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：`795a6f3816862920286f7b47ba1a7cd9b5313a1d3a4fa7ec775e37686f3bc57c`

source recovery frozen manifest 登记对象前后均为 `17/17` 匹配。冻结 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9` 以 `-I -S -B` 运行完整正式测试，结果为 `61/61` 通过。测试前后五项 runtime、retired 测试对象、cleanup receipt/journal/gate、可信 snapshot 与 migration journal 的 SHA-256 均不变；正式 source-control recovery transaction、parent snapshot 和 gate 继续缺席。控制脚本目录的 `.pyc`、`.pyo` 和 `__pycache__` 合计为零。因此 `M9-SPR-R3-B01` 的正式运行态污染已经由经审计 cleanup 清除，当前测试也未再产生正式运行态写入。

然而，61 项总数包含大量 overlap、offline recovery 和 cleanup 测试。与 source-control recovery 主体直接相关的正式测试仍只有 EUID 拒绝、gate 路径分离、event 幂等、retired 后缀、产品闭集、process receipt helper、parent snapshot 漂移、state-first 半提交及损坏 ledger 双硬停等少量用例。总数和零写入事实不能替代缺失的恢复状态机覆盖。

## 当前固定失败事实

真实 failed overlap transaction 的 SHA-256 为 `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`，2347 bytes、UID/GID 1000、mode 0644、nlink 1。其关键字段为：

- transaction ID：`e5bfc046d4d5a1bd97507d37b40f1e0c`
- state：`FAILED_COMMITTED`
- action/bucket：`source_prepare` / `overlap_build`
- exit code：1
- timed out：false
- reason：`overlap_command_failed`
- forecast/required forecast：1073741824 / 1073741824 bytes
- child PID：373，当前不存在
- elapsed：`0.715775579 s`
- command SHA-256：`8b0a62821b31c63ec0714be201326ecb33d01992ae0738ce216657be5b7e720f`

budget state 和 workflow 仍为双 HARD_STOP，active transaction 均为空，workflow stage 为 `HARD_STOP`，`apt_install_completed=true`。五项正式 runtime SHA-256 为：

- budget state：`1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`
- workflow：`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`
- failed transaction：`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`
- ledger：`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`
- stale capability：`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`

ledger 为 58462 bytes、60 条 JSON event；tip 为 `OVERLAP_HARD_STOP`，transaction ID 与上述失败事务相同，reason 为 `overlap_command_failed`，command SHA-256 相同，记录的 `overlap_build` 累计 CPU 为 `7200.791086107 s`。固定 ledger 全文件 SHA 同时约束 event 集合、顺序和 tip。

唯一活动 stale capability 为 `f7c3b060e19e37e6da03f461d754d38c.json`，4309 bytes、UID/GID 1000、mode 0600、nlink 1。其 state 为 `BOUND`，action 为 `source_prepare`，transaction ID 与失败事务一致，child PID 373 和 budget PID 294 在最终复核时均不存在。对应 `.consumed.json` 和 `.launcher-receipt.json` 均缺席。

使用上述真实 receipt 构造只存在于内存的 gate，并调用实际 `source_control_preflight()`，得到固定 transaction ID、capability path 和 receipt，未产生写入。这证明当前现场可满足 B02 的 fail-closed preflight，包括 D-017 apt recovery/package状态、stale capability、source/build 产品和正式 runtime 绑定。

六项 source/build 产品均缺席：`openmx-overlap-build`、`openmx-overlap-build.staging`、`env/hdf5-1.12.1`、`openmx_official_3.9.9_tree_manifest.json`、`openmx_overlap_tree_manifest.json`、`openmx_overlap_build_manifest.json`。正式 source-control recovery transaction、parent snapshot 和 gate 也均缺席。

cleanup 后 retired 测试对象、retirement receipt、cleanup journal、cleanup gate、root 私有 snapshot 和 migration journal 继续保持上一轮执行审计的精确 SHA 与 owner/mode/nlink；active 伪 transaction 保持缺席。因此 `M9-SPR-R3-B01` 为 CLOSED，不再阻塞真实 recovery transaction 的首次创建。

## 历史稳定问题复核

### M9-SPR-IMP-B01：REOPENED

当前 verifier 正确要求 source recovery gate 自身为 `D-017-source-control-recovery-v1`、零问题 PASS，并把审计 JSON 限制在 `08_audits` 直接子路径，绑定其 SHA；授权记录和 source frozen manifest 也绑定固定路径与 SHA，source frozen 文件集合要求与代码内 `SOURCE_RECOVERY_CONTROL_FILES` 精确相等并逐项复算。

但 verifier 对审计 JSON 只检查顶层 `verdict=PASS`、`blocking=0`、`non_blocking=0`，不检查 audit verdict 的 schema 或 decision ID。独立临时候选 gate 使用当前 cleanup verdict `M9_source_control_test_cleanup_final_verdict.json` 作为 `audit_report_path`，其 report decision ID 为 `D-017-source-control-test-cleanup-v1`，而 gate decision ID 为 `D-017-source-control-recovery-v1`；在绑定该错误审计域 JSON 的真实 SHA、真实授权 SHA 和当前 `17/17` source frozen manifest 后，实际 `verify_source_control_recovery_gate_and_hashes()` 返回成功。由此，cleanup 审计可以被错误归属于 source recovery 放行，未满足第一次复核所要求的唯一 recovery verdict 决策域。

source recovery 命令还没有调用 `isolated_bootstrap_provenance()`。独立使用系统 `/usr/bin/python3` 3.10.12、`-I -S -B` 进入命令并令 gate verifier 在入口返回定点 sentinel 时，gate verifier 调用次数为 1，bootstrap provenance 调用次数为 0。静态调用链同样确认该命令在 EUID root 检查后直接进入 gate verifier。也就是说，当前入口没有证明实际解释器是冻结 Python 3.9，也没有把实际 Python/bootstrap receipt 写入 recovery transaction。现有 `test_overlap_init_rejects_nonfrozen_python_before_state_write` 只覆盖 overlap init，不覆盖 source recovery。

最小关闭条件：

- source recovery audit verdict 必须具有专用 schema 和明确的 source recovery decision ID，并由 verifier 同时校验；cleanup、offline recovery 或其他零问题 PASS JSON 必须被拒绝。
- source recovery 命令必须在 gate、锁和任何状态动作前调用冻结 bootstrap provenance，要求固定 Python 3.9、`-I -S -B`、受限 `sys.path` 和冻结 stdlib module receipts；该 receipt 应进入 recovery transaction 或等价的持久化证据。
- 对 source recovery 入口增加错误 Python、缺少 `-I/-S/-B`、错误 verdict schema/decision、自由报告路径、授权漂移、frozen 闭集漂移和控制目录/cache 异常测试，并断言在任何正式路径写入前停止。

### M9-SPR-IMP-B02：CLOSED

固定 failed transaction 全文件 SHA、ID、state/action/bucket/exit/timed-out/reason/forecast/child PID，双 HARD_STOP，runtime SHA，D-017 apt recovery/package终态，stale capability receipt/状态/PID/消费证据和六项产品闭集均由当前 preflight 与真实现场闭合。实际只读 preflight 通过。

### M9-SPR-IMP-B03：CLOSED

当前首次路径在 capability rename 前写 PREPARED recovery，并把 parent transaction 的 bytes/SHA/size、state/workflow/ledger receipts、stale/retired paths 和 event 持久化。parent snapshot 已存在时要求逐字节等于固定 parent；snapshot 与 PREPARED 之间中断后可通过相同 bytes 续提。resume 每次重新核验 parent transaction 与 snapshot，并验证 retired receipt。第三次报告以来该状态机实现未发生削弱。

### M9-SPR-IMP-B04：CLOSED

当前首次路径统一进入 `source_control_resume()`；ledger 只接受 parent event-set 或 parent 加唯一同载荷 recovery event。resume 可识别 state 已提交而 workflow 尚未提交的实际半提交，终态分支只读核验 post state/workflow/ledger 和唯一 event-set。异常统一进入 `source_control_hard_stop()`。第三次报告已通过临时状态机复现关闭 B04，当前实现保留这些机制。正式覆盖不完整的问题归入 B05，不重复计为 B04 实现阻塞。

### M9-SPR-IMP-B05：OPEN

61 项正式测试没有执行完整 `command_overlap_recover_source_control_failure()` 首次成功路径，也没有建立完整临时可写闭集来逐点注入以下持久化边界：parent snapshot 创建与 PREPARED 之间、capability rename 后、CAPABILITY_RETIRED 后、SUCCESS_PENDING_COMMIT 后、ledger append 后、ledger phase journal 后、state 写入后、state phase journal 后、workflow 写入后及 terminal journal 后。当前仅有 state-first 半提交的单一成功续提测试。

正式测试也没有验证成功 `SUCCESS_COMMITTED` replay 为零写入；没有覆盖 parent ledger 额外 event、同 ID 异载荷、有效 JSON 顺序漂移、state/workflow/ledger 的 parent 或 terminal receipt 漂移；没有验证首次成功与 resume 的最终 recovery receipt 结构完全相同；没有通过真实 launcher 选择规则证明 retired capability 不可消费；没有覆盖 UID 1000 新 `source_prepare` capability 的创建与消费生命周期。损坏 ledger 双硬停和 parent snapshot 漂移虽已覆盖，但不能代表上述矩阵。

错误 Python 与错误 audit verdict 决策域没有正式测试，EUID 仅覆盖 non-root 拒绝。测试中的 `process_matches_receipt` helper 也未形成 source recovery 完整 PID/终态用例。因此 `61/61 PASS` 与 runtime 零写入只证明既有用例隔离正确，尚不能关闭原 B05 的状态机级最小条件。

最小关闭条件：建立临时完整状态树，重定向 recovery transaction、parent snapshot、state、workflow、ledger、capability root、lock、gate 及全部可能写路径；执行一次真实首次成功并在上述每个持久化点中断后重入；逐项断言 event 唯一、parent/retired/post receipts、双 HARD_STOP 或幂等完成、terminal replay 零写入以及首次/resume 终态同构。补全 B01 的错误解释器和 verdict 决策域测试、runtime/ledger 漂移矩阵、retired 实际不可消费与 UID 1000 新 capability 生命周期。完整测试前后继续要求正式 runtime inventory 和 SHA 零变化、source recovery 三对象缺席、`17/17` 及 cache=0。

### M9-SPR-IMP-B06：CLOSED

当前 source frozen manifest SHA 与指定值一致，内部 17 个对象为 `17/17` 匹配，budget controller 与测试 SHA 均与 manifest 一致。B01/B05 修复必然改变 controller、测试和 manifest；届时必须重新生成并独立复算最终闭集，本次关闭不授权复用当前 manifest 创建 gate。

### M9-SPR-R3-B01：CLOSED

经批准的一次性 cleanup 已把确定性伪 transaction 原子迁移为 root:root、0600、nlink 1 的 `.test-artifact.retired.json`，并形成零问题执行审计。当前 active recovery transaction 缺席，cleanup receipt/journals/snapshot/migration 证据完整。61 项测试前后正式 runtime 及 cleanup 证据 SHA 不变，source recovery transaction、parent 和 gate 均未出现。测试污染及测试隔离两个阶段的关闭条件均已满足。

## 放行判断

当前为 `BLOCKING=2`、`NON_BLOCKING=0`、FAIL。稳定问题 `M9-SPR-IMP-B01` 与 `M9-SPR-IMP-B05` 均未关闭，因此主 agent 不得创建一次性 source-control recovery gate。修复后应重新冻结 controller、测试和 source manifest，运行完整隔离测试并接受新的独立定点复核；只有达到 `BLOCKING=0`、`NON_BLOCKING=0` 并产生 source recovery 专用结构化 verdict 后，才允许主 agent 创建一次性 gate。

即使后续复核 PASS，也只允许按明确授权决定是否创建 gate，不自动授权执行 recovery 或 `source_prepare`。实际 recovery 成功仍须独立只读结果审计，之后才能另行判断是否允许 UID 1000 使用全新 transaction/capability 重试一次 `source_prepare`；不包含 `source_build`。

本轮除新增本报告外未修改被审对象或正式运行时，未创建或执行 gate、recovery 或 `source_prepare`。所有定点复现均使用临时文件或在状态写入前由 sentinel 停止。
