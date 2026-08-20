# M9 source-control recovery 失败执行只读专项审计

审计日期：2026-08-19  
审计范围：已授权的一次性 `overlap-recover-source-control-failure` 实际失败执行及其可恢复性  
审计方式：只读检查正式对象、冻结实现和回归测试；没有执行 recovery、recovery replay、source_prepare 或任何手工状态修补  

## 结论

本轮判定为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。

实际失败形成了可解释且内部一致的停止现场：恢复事务已创建、原失败事务的父快照已持久化、stale capability 已按原字节退役，随后在 recovery event 写入 ledger 之前因既存 ledger 的打开模式包含 `O_CREAT` 而收到 `PermissionError`。异常处理重新建立了 budget/workflow 双 `HARD_STOP`，并将 recovery transaction 持久化为 `FAILED_COMMITTED`。ledger 没有出现部分行或重复 event，budget state、原失败 transaction、active recovery gate、既有 disposition/refresh 证据及六项 source/build 产品均未发生越权变化。

该现场具有恢复所需的完整前缀证据，但当前冻结实现明确拒绝重放任何 `FAILED_COMMITTED` recovery transaction；即使只把入口集合机械扩展为允许该状态，`source_control_resume()` 仍会因 workflow 已由失败处理器更新而触发 `source_control_workflow_drift`。因此当前不得重试，也不得通过手工修改 transaction state、恢复 active capability 或删除失败 transaction 来规避该状态机。允许的最小方向是：在新的冻结闭集、专项审计和精确续提授权下，继续同一个 recovery transaction `4783a27441019358a0f15127f26d957d`，保留同一个 event ID，并以不含 `O_CREAT` 的既存文件追加语义写入 ledger。

## 冻结实现与复核方法

本轮复算得到：

- `06_reproduction/scripts/m9_budget.py`：`8f2cbb007045cf888e41893f8b0dc5d44f3fc88c0078590f24776724c9ede3a2`
- `06_reproduction/tests/test_m9_overlap_controls.py`：`432eb10457a88ad98fb94157d7c0fa376240a8e62404440115d7ae3b5d657f10`
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：`af86278da0cf6d68330f065dd8fbe50963b04b5c9c5b198f4cce5d2e0442e21d`
- `06_reproduction/manifests/m9_source_control_test_cleanup_frozen_hashes.json`：`6e0d799bf5ce60cd9ac18a8e384a5e71972e8f3a56d9c64665b9e71056b58495`

以 root、冻结 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9`、`-I -S -B` 重新运行当前测试，结果为 `Ran 82 tests in 15.344s`、`OK`、退出码 0。该结果不能否定本次正式失效：现有测试验证了 lock 使用 `r+`，但 `append_event()` 的临时目录测试没有复现正式 manifests 目录的 sticky/protected_regular 所有权组合，也没有覆盖 ledger 的 no-create 打开合同。测试后全部正式哈希保持下文所列值，cache 计数仍为 0。

## 实际阶段与持久化一致性

外部执行事实为 root 固定 Python、执行前 gate/preflight PASS、命令退出码 1、无 stdout。只读调用当前 `verify_source_control_recovery_gate_and_hashes()` 仍返回 `status=PASS`、`scope=ONE_TIME_SOURCE_CONTROL_RECOVERY`；所得 gate receipt 与 recovery transaction 内的 `gate_receipt` 完全相等。外层遥测的退出码按已提供事实记录；冻结函数在捕获该异常后内部返回 125，现有材料不足以判断外层执行器是否进行了退出码归一化，但这一边界不影响持久化阶段和根因判定。

恢复流程已经依次完成以下持久化动作：

1. 在既存 `budget.lock` 上以 `r+` 成功取得锁；lock 仍为 UID/GID `1000:1000`、`0644`、0 bytes、inode `50700`。
2. 创建 parent snapshot；其 2347 bytes 与原 `overlap_transaction.json` 逐字节相同，二者 SHA-256 均为 `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`。
3. 创建 recovery transaction `4783a27441019358a0f15127f26d957d`，保存 parent state/workflow/ledger、bootstrap 和 gate receipt。
4. 将 capability `f7c3b060e19e37e6da03f461d754d38c` 从 active path 原子退役；active path 缺席，retired path 为普通单链接文件，UID/GID `1000:1000`、`0600`、4309 bytes、SHA-256 `0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`。
5. recovery 进入 `SUCCESS_PENDING_COMMIT` 且 `ledger_phase=PENDING`，随后调用 `append_event_once()`。新 event ID 为 `4783a27441019358a0f15127f26d957d:source-control-recovery`。
6. ledger 打开在任何 event 字节写入前失败。异常处理将 workflow 写为新的 `HARD_STOP`，保持 budget state 为 `HARD_STOP`，最后将 recovery 写成 `FAILED_COMMITTED`。

正式对象的结果如下：

| 对象 | 只读事实 | 一致性判断 |
|---|---|---|
| recovery transaction | 5028 bytes，SHA `89483c5653b05063308896d5fe61809916f210a906e09eeda068867608bed44e`，`FAILED_COMMITTED`，`ledger_phase=PENDING` | 与失败阶段一致 |
| failure reason | `source_control_recovery:PermissionError:[Errno 13] Permission denied: '/home/evan-williams/deeph-m9/manifests/budget_ledger.jsonl'` | 与冻结调用路径一致 |
| parent snapshot | 2347 bytes，SHA `12f475...66309` | 与原失败 transaction 字节相等 |
| budget state | SHA `1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc` | 与执行前基线相同；仍 `hard_stopped=true` |
| workflow | SHA `73a3522af8a29d8300255b8deb9c2014628a27930ffb05b81f49255a8d5a8fbf` | 合法变化；`HARD_STOP` 且精确记录本次 failure reason |
| 原失败 transaction | SHA `12f475...66309`，ID `e5bfc046d4d5a1bd97507d37b40f1e0c`，`FAILED_COMMITTED` | 未变化 |
| ledger | 58462 bytes，60 行，SHA `25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f` | 与执行前基线相同；新 event 计数为 0 |
| active recovery gate | root:root、`0600`、nlink 1、1728 bytes、SHA `381c8fd6e9fa28479de4f2144e975ed32756af9ac9dfe90a6d5457208da1cefa` | 未变化，实际 verifier PASS |
| stale capability | active 缺席；retired receipt 与 transaction 中 before/after receipt 相同 | 原子退役已完成，未消费 |

retired capability 对应的 `.consumed.json` 与 `.launcher-receipt.json` 均缺席。ledger tip 仍是原失败 transaction `e5bfc046d4d5a1bd97507d37b40f1e0c` 的 `OVERLAP_HARD_STOP`，reason 仍为 `overlap_command_failed`；不存在部分 recovery event、同 ID 异载荷或额外 event。

## 根因

正式 manifests 目录为 root:GID1000、模式 `1770`、sticky bit 有效；`budget_ledger.jsonl` 是 UID/GID `1000:1000`、模式 `0644` 的既存普通文件，当前内核 `fs.protected_regular=2`。冻结实现的 `append_event()` 使用：

```python
with LEDGER_PATH.open("a", encoding="utf-8") as handle:
```

Python 的 `a` 模式包含 `O_WRONLY | O_APPEND | O_CREAT`。在上述 sticky、跨 UID 所有权和 `protected_regular=2` 组合下，即使调用者为 root，含 `O_CREAT` 的打开也会在既存文件上被拒绝。失败发生在 `write()` 之前，因而 ledger 的字节数、SHA、60 行事件集合和 tip 均保持原值。这与此前 `budget.lock` 的 `a+` 失效属于相同的文件打开合同问题，但本轮对象是 ledger，而不是锁。

适合该路径的最小打开语义是：只打开已存在文件，不允许创建；使用 `O_WRONLY | O_APPEND | O_CLOEXEC`，在平台支持时加入 `O_NOFOLLOW`，且明确不加入 `O_CREAT`。打开后应以同一 fd 执行 `fstat`，要求普通文件、UID/GID `1000:1000`、模式 `0644`、nlink 1，并要求路径 `lstat` 的 dev/inode/metadata 与 fd 一致；随后仅写入预先确定的单行 bytes、对同一 fd `fsync`，再验证旧 ledger 是精确前缀且后缀只可能为该 event 的规范编码。`Path.open("r+")` 加锁后 seek-to-end 也能消除 `O_CREAT`，但 `os.open(..., O_APPEND)` 更直接地表达追加原子性。

不应把通用 `append_event()` 改成“文件不存在则创建”的混合分支来修复该问题。source-control recovery 的前置合同已经绑定既存 ledger 的 bytes/SHA；缺席应当停止，而不是创建新 ledger。

## 越权产物与既有证据

六项闭集产品均缺席：

- `/home/evan-williams/deeph-m9/software/openmx-overlap-build`
- `/home/evan-williams/deeph-m9/software/openmx-overlap-build.staging`
- `/home/evan-williams/deeph-m9/env/hdf5-1.12.1`
- `openmx_official_3.9.9_tree_manifest.json`
- `openmx_overlap_tree_manifest.json`
- `openmx_overlap_build_manifest.json`

旧 invalid gate retired SHA `6bdd2f...f5821`、pre-lock retired gate SHA `5553de...5936`、disposition journal SHA `e97dc9...c8ece`、lock-refresh journal SHA `ec6a30...20519` 均未变化。cleanup retired artifact、receipt 和 journal 也分别保持 SHA `2e0aa6...9fc74`、`74b248...7fd49`、`1e0729...25d8d`。因此实际新增或变化仅限已授权 recovery 状态机的预期中间对象：parent snapshot、recovery transaction、capability rename 和 failure workflow。未发现 source_prepare、source build、GPU 任务、capability consumption 或其他越权运行产物。

## 阻塞问题

### M9-SPR-R33-B01 — root recovery 对既存 ledger 使用含 `O_CREAT` 的追加打开

严重性：BLOCKING。

`append_event_once()` 最终调用 `append_event()`，后者以 `Path.open("a")` 打开正式 ledger。在正式 owner/mode/sticky/sysctl 条件下，该模式确定性触发 `PermissionError`，使获授权的 recovery 无法在 ledger commit 阶段前进。82 项测试全部通过但未建模这一环境合同，说明当前回归闭集不足以证明正式可执行性。

最小关闭条件：使用不含 `O_CREAT` 的 existing-file-only、single-fd、no-follow、append、fsync 实现；严格验证 ledger 普通文件、owner/mode/nlink/dev/inode、父前缀和唯一规范后缀；新增与正式 `root:1000/1770 sticky`、ledger `1000:1000/0644`、`protected_regular` 语义相同的命令级负例，证明旧 `a` 会被拒且新实现只采用 no-create 模式。还应覆盖 open、write、file fsync 和后验检查各失败窗口，证明重入时 event 为 0 或 1 次，不会形成部分行或重复 ID。

### M9-SPR-R33-B02 — 当前 `FAILED_COMMITTED` 没有精确、可审计的同事务续提合同

严重性：BLOCKING。

`command_overlap_recover_source_control_failure()` 只允许 `PREPARED`、`CAPABILITY_RETIRED`、`SUCCESS_PENDING_COMMIT` 续提，并明确把 `FAILED_COMMITTED` 视为不可 replay 的终态。当前 transaction 因而会在取得锁后停止。机械加入 `FAILED_COMMITTED` 仍不充分：当前 workflow SHA 已由 `source_control_hard_stop()` 从父 SHA `2dbad9...6685d` 更新为 `73a352...a8fbf`，而 `source_control_resume()` 对未恢复 workflow 只接受父 SHA，故仍会失败。

最小关闭条件：只为本次精确失败形态定义续提状态，不得普遍开放所有 `FAILED_COMMITTED`。续提必须保持 recovery transaction ID `4783a27441019358a0f15127f26d957d` 和 event ID `4783a27441019358a0f15127f26d957d:source-control-recovery` 不变，并在任何新写入前同时绑定：

- 当前 recovery transaction SHA `89483c...ed44e`、`state=FAILED_COMMITTED`、`ledger_phase=PENDING`、精确 failure reason，且不存在 completed/post-state receipts；
- parent snapshot 与原 transaction 均为 SHA `12f475...66309` 且字节相等；
- retired capability SHA `0a4352...e91e`、4309 bytes、UID/GID `1000:1000`、`0600`、nlink 1，active/consumed/launcher paths 均缺席；
- state SHA `1a998b...4d7dc`、workflow SHA `73a352...a8fbf`、ledger SHA `25103d...8da4f`，并证明 event ID 当前计数为 0；
- active gate SHA `381c8f...1cefa`、其旧 gate receipt、固定 Python/bootstrap、原 failed transaction 及既有 disposition/refresh 证据。

修复 `m9_budget.py` 后，现 active gate 所绑定的 frozen manifest 必然过期；同时现 recovery transaction 又绑定旧 gate receipt。因此不能直接复用普通首次 recovery gate，也不能把旧 receipt 静默替换为新 receipt。应建立一次专用、root 私有、可崩溃续提的 post-failure gate/receipt 迁移记录，逐字节绑定旧 gate、旧 receipt、上述失败现场、新 frozen manifest、新专项 PASS verdict 和 replacement gate；恢复入口只在该迁移完整且实际 verifier 通过时接受 receipt 转换。该过程仍只能续提现有 transaction，不能创建第二个 recovery ID 或第二个 ledger event。

回归测试至少应覆盖：当前现场的首次续提成功；event 写入前失败、写入后且 recovery journal 更新前失败、ledger COMMITTED 后失败、state 与 workflow 各半提交；同 ID 同载荷重入、同 ID 异载荷拒绝、额外 event/ledger 顺序/父前缀漂移拒绝；failure workflow、state、parent、retired receipt、bootstrap、旧/新 gate receipt 任一漂移均在下一写入前停止；最终 `SUCCESS_COMMITTED` replay 零写入。所有窗口必须收敛到同一 transaction ID、恰好一个 ledger event 和同一最终 state/workflow/ledger receipts。

## 最终授权边界

当前证据允许保留该失败现场并开发、测试、审计上述修复；不允许现在重试 recovery，不允许手工把 `FAILED_COMMITTED` 改回 `SUCCESS_PENDING_COMMIT`，不允许恢复 active stale capability，不允许删除或重建 parent/recovery transaction，也不允许执行 source_prepare 或 source_build。

若 M9-SPR-R33-B01/B02 按最小关闭条件完成，独立审计确认 `BLOCKING=0`、`NON_BLOCKING=0`，并建立绑定新冻结闭集与当前失败现场的专用续提 verdict/gate，则可以把后续动作界定为原一次性 recovery transaction 的续提，而不是第二次独立 recovery。成功后仍应立即停止，独立核验单一 ledger event、state/workflow 恢复、terminal replay 零写入及无 source/build 产品，再另行判断 source_prepare 的授权；原一次性 recovery 授权不自动扩展到 source_prepare 或 source build。
