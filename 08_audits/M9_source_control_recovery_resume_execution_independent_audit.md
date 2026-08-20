# M9 同一事务 source-control recovery resume 执行事实独立审计

审计日期：2026-08-19  
执行对象：`m9_budget.py overlap-recover-source-control-failure` 续提既存 transaction  
执行信封：root 固定 Python `-I -S -B`，报告退出码 0，stdout status 为 `source_control_recovery_resumed_after_ledger_fix`  
审计约束：正式现场全程只读；未执行 recovery replay、source_prepare、source build、smoke、batch 或 GPU 动作

## 结论

本轮判定为 **PASS**：`BLOCKING=0`，`NON_BLOCKING=0`。

持久化现场证明，既存 recovery transaction `4783a27441019358a0f15127f26d957d` 已使用原事件 `4783a27441019358a0f15127f26d957d:source-control-recovery` 从 post-failure migration 的 `FAILED_COMMITTED`/`PENDING` 点续提到 `SUCCESS_COMMITTED`/`COMMITTED`。没有建立第二个 recovery transaction或第二个 recovery event。

ledger 原 58,462 字节前缀逐字节保持原摘要，新增 suffix恰为该事件的一条规范 JSONL记录；61 行 ledger中目标 event恰好出现一次。budget state和workflow均解除 hard stop并绑定原 parent transaction，workflow stage为 `AUDIT_PASSED`。recovery transaction记录的 post-state、post-workflow、post-ledger摘要与正式现场完全一致。活动 gate、post-failure migration journal、original snapshot、retired old gate、parent及retired capability均保持既有证据。

未发现 recovery范围外的运行时变化或 source/build产品。下一步仅允许进入受控 `source_prepare`：按 `AUTH-M9-SOURCE-CONTROL-RECOVERY-2026-08-14-01` 和 D-017，重新验证当前终态后创建并消费一个新的 UID1000 source_prepare transaction/capability。不得执行 source build、OpenMX smoke、batch、正式 DFT标签、M9-05 或其他下游动作。

## 正式现场独立复算

| 对象 | SHA-256 | bytes | owner/mode/nlink |
|---|---|---:|---|
| recovery transaction | `e9b8babcff8a2f42adea21d5cbce614b38f0854271d3389eae0bbcdd7d5e53bc` | 8383 | UID/GID1000 `0644`, 1 |
| budget ledger | `dbc54580fc6e215319c3af8d33b7f803448baa50a928ee4a60151782c9fd5e3b` | 59097 | UID/GID1000 `0644`, 1 |
| budget state | `00a32bd7f28ad26fa600c8abe9d0fa64efe57e410eacb82ad2d201fa9adc5439` | 1422 | UID/GID1000 `0644`, 1 |
| workflow | `bd895b2831c805c44a180012ece64bdda00744340768c7062e33b856069fda8a` | 722 | UID/GID1000 `0644`, 1 |
| active recovery gate | `8e66d65d17d3195f3df09db954afca4066c3ec91e2d8dad6d2aea06078d0d5ce` | 2398 | root:root `0600`, 1 |
| post-failure migration journal | `3d84cf6a82b3403e63ce22b72712efa232feca6d3a8dd3e17d877b9f48c4cb6d` | 6446 | root:root `0600`, 1 |
| original failed recovery snapshot | `89483c5653b05063308896d5fe61809916f210a906e09eeda068867608bed44e` | 5028 | root:root `0600`, 1 |
| pre-ledger-fix retired gate | `381c8fd6e9fa28479de4f2144e975ed32756af9ac9dfe90a6d5457208da1cefa` | 1728 | root:root `0600`, 1 |
| recovery parent / overlap transaction | `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309` | 2347 | UID/GID1000 `0644`, 1 |
| retired capability | `0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e` | 4309 | UID/GID1000 `0600`, 1 |
| budget lock | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 | UID/GID1000 `0644`, 1 |

所有对象均为普通文件且 nlink 1。原 stale capability路径保持缺席，capability目录只包含其 retired副本。正式 source/build六项产品——`openmx-overlap-build`、`openmx-overlap-build.staging`、`env/hdf5-1.12.1`及三项 source/build manifest——全部缺席。

冻结控制文件保持：budget `8a21f1768cc14a086d4b8edb7ea8c8e76a7213ef9871eb5489a9463ef0cd8d8a`，tests `6e6d6463631fd44b7b592353ecb8ad611ca2822f81b00572edbc6b626ad95e98`，source manifest `03ed6d0e4b2ff126d11d0e5e772e479bf9c3f14f5bb2833de0358fa500fb0350`，cleanup manifest `262971954db403700d27e1df35365cf3e6a4acf3937a766f2bd0f89f642897ef`，post-failure contract `dbb93a26d7a5b80b6992ead374dda8421d763679ce63ecf349688b4a38426c2e`。`06_reproduction` cache计数为 0。

## Transaction 终态一致性

recovery transaction的 schema仍为 `m9-source-control-recovery-v1`，transaction ID和嵌入 event transaction ID均为 `4783a27441019358a0f15127f26d957d`；event ID保持原值。transaction保留原 failure reason、原失败 SHA和 `failure_history`，同时保持经执行事实审计的 `post_failure_migration.status=PASS`及 old/new gate、original snapshot、failed state/workflow、ledger、contract、verdict和 migration journal绑定。

本次续提新增的终态字段为：

- `ledger_phase=COMMITTED`；
- `state_commit_phase=WORKFLOW_COMMITTED`；
- `state=SUCCESS_COMMITTED`；
- `post_ledger_sha256=dbc54580fc6e215319c3af8d33b7f803448baa50a928ee4a60151782c9fd5e3b`；
- `post_state_sha256=00a32bd7f28ad26fa600c8abe9d0fa64efe57e410eacb82ad2d201fa9adc5439`；
- `post_workflow_sha256=bd895b2831c805c44a180012ece64bdda00744340768c7062e33b856069fda8a`；
- `completed_utc=2026-08-19T14:16:26.625521Z`。

三项 post摘要均与当前正式文件重新计算值相等。只读调用 `validate_migrated_failed_recovery()` 成功，证明 post-failure migration receipt、journal、original snapshot、当前 gate和固定 bootstrap仍一致。只读 `verify_source_control_recovery_gate_and_hashes()` 返回与 active gate payload相同的 PASS对象；gate scope仍为 `ONE_TIME_SOURCE_CONTROL_RECOVERY`，并精确绑定本 transaction/event及迁移前 event count 0。

## Ledger exactly-once 与 raw prefix保真

当前 ledger共61行、59,097字节。按 recovery transaction冻结的 `parent_ledger_bytes=58462` 分割：

- 前缀 SHA-256为 `25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`，与失败前授权 ledger逐字节一致；
- suffix为635字节，逐字节等于对原 recovery event执行 `sort_keys=True` 后加换行的唯一规范JSONL记录；
- 全 ledger解析后，目标 event ID计数为1；
- 该 event的 canonical payload hash与 ledger event map中的值相等；
- 未观察到 partial suffix、额外 event、同 ID异载荷或顺序漂移。

因此 ledger append满足 existing-only恢复合同的 raw-prefix保持和 exactly-once要求。该事实也说明当前 `SUCCESS_COMMITTED`不是仅依赖 transaction字段宣告，而是与持久化 ledger内容一致。

## State 与 workflow 收敛

budget state为 `hard_stopped=false`、`active_overlap_transaction=null`，`recovered_from_source_prepare_control_failure=e5bfc046d4d5a1bd97507d37b40f1e0c`。workflow为 `hard_stopped=false`、`active_transaction=null`、`stage=AUDIT_PASSED`，并绑定同一 parent transaction。原 HARD_STOP reason和时间仍保留为历史证据，没有被删除或改写为不存在的成功历史。

parent snapshot和正式 overlap transaction仍逐字节相同，SHA均为 `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`；retired capability receipt未变。migration journal仍为 `SUCCESS_COMMITTED`且 SHA未变。由此可确认恢复顺序已经收敛为 ledger committed、state recovered、workflow recovered、transaction success，且迁移证据没有在续提过程中漂移。

## 下一步边界

本报告只关闭同一 source-control recovery transaction的执行事实检查点。现有授权记录明确允许在恢复双重状态机后重新创建 UID1000的全新 source_prepare transaction，同时明确排除 source build及后续计算。因此下一步仅允许受控 source_prepare，并应满足：

- 在任何正式写入前重新验证 recovery transaction `SUCCESS_COMMITTED`及其三项 post摘要；
- 重新验证 ledger目标 event恰好一次、parent/gate/migration journal/original snapshot/retired capability与本报告一致；
- 使用冻结 launcher和固定 Python，通过既定预算锁与一次性新 capability建立一个 source_prepare transaction；
- source_prepare完成或失败后立即停止并进行独立事实审计。

本报告不允许复用已退役 stale capability，不允许重跑 source-control recovery，也不允许把 source_prepare许可扩展到 source build、smoke、batch、GPU、正式 DFT标签或 M9-05。
