# M9 post-failure migration R34-B01/B02/B03 第一次定点复核

审计日期：2026-08-19  
审计范围：`M9-SPR-R34-B01`、`M9-SPR-R34-B02`、`M9-SPR-R34-B03` 的关闭证据  
审计约束：只读正式现场；仅在临时目录进行主动故障重放；未创建或执行正式 gate、migration、recovery、source_prepare  

## 结论

本轮判定为 **FAIL**：`BLOCKING=3`，`NON_BLOCKING=0`。三个稳定问题均为 **PARTIALLY CLOSED / REMAINS OPEN**，因此不生成 migration verdict 或 replacement recovery verdict。

新实现已经完成三项重要修复：每次 migration journal 重入都会调用 `verify_post_failure_immutable_runtime()`，workflow/ledger 漂移能够停止；source recovery transaction、state、workflow 改用 `atomic_owned_json()`，UID1000 stale tmp 的常规续提和 file/target/directory fsync 已建立；ledger 采用 `O_RDWR|O_APPEND`、no-create、no-follow、同 fd `pread` 的 prefix SHA/size 绑定，并能回滚 helper 检测到的 short write及恢复合法 proper-prefix suffix。

但主动重放确认仍有三个未闭合窗口：

- immutable runtime 重检不包括 recovery transaction；该对象漂移时检查仍成功，且 initial snapshot 仍来自与前次 receipt 分离的路径读取。
- durable owned tmp 若在 `open(O_EXCL)` 后、`fchown` 前中断，会留下 root-owned tmp；重入只接受 UID1000 tmp，因而停止。
- ledger prefix 只在 append 前校验；在 `pread` 完成后、`write` 前发生同 inode、同尺寸 prefix 变化时，append 仍被接受。

这些窗口分别违反上一轮 B01/B02/B03 的最小关闭条件，且 89 项测试没有覆盖它们。当前不得创建两份 verdict，也不得执行 migration 或 recovery resume。

## 冻结复算与测试

六项复算与送审值完全一致：

- `m9_budget.py`：`a7f7eca590d6d4988677443dcdbfa6d676d74841f78292194a32f274b737dfa9`，238727 bytes；
- `test_m9_overlap_controls.py`：`c317cb0fc63b1c2f036406be3cdee605eb9b49588025dc85c4fb908d482e5939`，182356 bytes；
- source manifest：`b08283ab0c870ff920ca56a192154cc53c4321889cf1bbfb02142e81f7dcde10`，19/19；
- cleanup manifest：`4971daf91c36d09786157b0db436b1f624b89035d2128b1d69540fc8ef2d9fc6`，4/4；
- post-failure contract：`dbb93a26d7a5b80b6992ead374dda8421d763679ce63ecf349688b4a38426c2e`；
- authorization：`8c9602d5cc774c64f87a41c13d68223583cc91d19596568055ea6c2eaef0e42b`。

root 固定 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 独立运行结果为 `Ran 89 tests in 18.728s`、`OK`。新增三项测试分别验证 ledger prefix/partial suffix、UID1000 stale tmp 和 immutable workflow/ledger；它们均通过，但没有覆盖下文三个残余窗口。

测试前后正式 failed recovery transaction、parent、state、workflow、ledger、retired capability、active gate 的 SHA 保持：

- recovery `89483c5653b05063308896d5fe61809916f210a906e09eeda068867608bed44e`；
- parent `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`；
- state `1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`；
- workflow `73a3522af8a29d8300255b8deb9c2014628a27930ffb05b81f49255a8d5a8fbf`；
- ledger `25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`；
- retired capability `0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`；
- active gate `381c8fd6e9fa28479de4f2144e975ed32756af9ac9dfe90a6d5457208da1cefa`。

post-failure journal、original snapshot、pre-ledger-fix retired gate 均以 `lexists` 语义保持缺席；六项 source/build 产品未出现；cache=0。正式现场未被本轮测试或审计修改。

## M9-SPR-R34-B01 — PARTIALLY CLOSED / REMAINS OPEN

### 已关闭部分

`verify_post_failure_immutable_runtime()` 现在对 parent snapshot、parent transaction、state、workflow、ledger、retired capability 使用 `read_stable_regular_bytes()`，并在 journal 初建或重入后、状态处理前调用。临时改变 workflow 或 ledger 会产生 `post-failure immutable runtime drift`；因此上一轮“PREPARED 后 workflow 漂移仍 terminal success”的直接路径已经关闭。相同调用位置适用于 `PREPARED`、`GATE_RETIRED`、`REPLACEMENT_CREATED`、`RECOVERY_RECEIPT_MIGRATED` 和 `SUCCESS_COMMITTED` 重入。

### 残余阻塞

immutable 集合不包含 `SOURCE_CONTROL_RECOVERY_TRANSACTION`。独立临时重放保持 parent/state/workflow/ledger/retired 不变，仅改变 recovery transaction SHA；`verify_post_failure_immutable_runtime(runtime)` 仍正常返回，输出为 `recovery_sha_drifted=true`、`immutable_check_accepted=true`。

command 首次分支的 `post_failure_runtime_receipts()` 仍通过 `is_symlink()`、`is_file()`、`lstat()`、`read_bytes()` 多次路径读取 recovery；随后又单独执行 `SOURCE_CONTROL_RECOVERY_TRANSACTION.read_bytes()` 建立 original snapshot。这两个读取没有同一 fd/inode/payload 绑定。journal 重入后也只核 root-private snapshot，而不要求当前 recovery 在 `PREPARED`/`GATE_RETIRED` 阶段仍等于 original SHA。实际 current recovery 直到 replacement gate 已创建后才在 `REPLACEMENT_CREATED` 分支检查，故漂移可能导致 gate 已退役/替换后才停止，不满足“下一正式写入前拒绝”。

最小关闭条件：

- 首次 runtime receipt 与 original snapshot 必须来自 recovery transaction 的同一次 `O_NOFOLLOW|O_CLOEXEC` 单 fd read，绑定 dev/inode/owner/mode/nlink/size/SHA/payload。
- `verify_post_failure_immutable_runtime()` 必须按 journal state 纳入 recovery：`PREPARED`、`GATE_RETIRED`、`REPLACEMENT_CREATED` 要求 current SHA 等于原 failed recovery `89483c...ed44e`；`RECOVERY_RECEIPT_MIGRATED`、`SUCCESS_COMMITTED` 要求等于 journal 的 migrated recovery SHA，并完整验证 migration payload、同 transaction/event 和 new gate receipt。
- 增加五个 journal state × recovery/workflow/ledger 漂移的命令级测试，断言在下一写入前停止；还应核 `context_sha256` 和 terminal replay 零写入。

## M9-SPR-R34-B02 — PARTIALLY CLOSED / REMAINS OPEN

### 已关闭部分

`atomic_owned_durable_bytes/json()` 以 fixed tmp、首次 `O_CREAT|O_EXCL`、重入 no-create/no-follow、严格 UID/GID/mode/nlink、write、file fsync、replace、target 内容/metadata、target fsync 和 directory fsync 更新 UID1000 runtime。正式 sticky/protected_regular 环境的 UID1000 stale tmp 测试通过；source recovery transaction、state、workflow 已使用该 helper。上一轮“tmp 已 chown UID1000 后重入再次 PermissionError”已关闭。

### 残余阻塞

首次 tmp 创建后立即在同一 try 内执行 `fchown`/`fchmod`。若进程在 `os.open(O_EXCL)` 成功后、`fchown` 前中断，tmp 合法地保持 root:root。重入分支只接受预期 UID/GID1000，因此把这个自身产生的 crash state 判为 `owned atomic temporary metadata mismatch`。

独立 root sticky 临时重放创建了与该窗口一致的 root:root、`0644` fixed tmp。再次调用 `atomic_owned_json()` 得到 `ValueError: owned atomic temporary metadata mismatch`，tmp 保留，未能续提。89 项测试只构造 UID1000 stale tmp，没有构造 pre-fchown root-owned tmp。

最小关闭条件：明确记录并接受 helper 自身可能产生的两个合法 tmp 阶段：新建后的 root-owned pre-chown receipt，以及 chown 后 UID1000 receipt；其他 owner/mode/nlink 仍拒绝。更稳妥的实现应在 root-private migration journal 中记录 tmp inode/path/phase，或使重入能证明 root-owned tmp 是本次固定目标的合法 pre-chown 临时对象，然后通过同 fd 完成 fchown、truncate/write/fsync。补充 open 后、fchown 后、fchmod 后、truncate、partial write、file fsync、replace、target recheck、target fsync、directory fsync 的逐窗口第二次续提测试，并断言最终 transaction SHA、owner/mode/nlink 和 tmp 缺席唯一。

## M9-SPR-R34-B03 — PARTIALLY CLOSED / REMAINS OPEN

### 已关闭部分

ledger 正常 append 已使用 `O_RDWR|O_APPEND|O_CLOEXEC|O_NOFOLLOW`，无 `O_CREAT/O_TRUNC`。helper 在同一 fd 上以 `pread` 校验 expected prefix size/SHA；检测 short return 后 truncate 到原 size 并 fsync。`source_control_resume()` 对 suffix 只接受空、完整 exact event 或 exact proper prefix；proper prefix 经同 fd 验证后 truncate/fsync，再重新读取精确 parent prefix。测试证明注入 short write 后 helper 回滚，人工 proper-prefix suffix 可恢复。

### 残余阻塞

prefix 只在 write 前验证。`os.write()` 完成后，代码仅比较 dev/inode/metadata 和 size 增量，没有再次从同一 fd `pread` 并验证 raw prefix 与 exact suffix。独立临时重放在 helper 已完成 prefix pread 后、实际 append write 前，用同一路径写入同 inode、同尺寸、JSON 语义相同但字段顺序不同的 prefix；随后 append 正常完成。函数输出 `accepted=true`、`prefix_changed=true`，没有异常。

该窗口仍可绕过后续 `ledger_event_ids()`，因为 canonical event mapping 不区分 JSON 字段顺序或等价空白；最终变化后的 raw prefix可能被记录为新的 post-ledger SHA，违反 contract 的 `preserve_ledger_prefix=true`。

最小关闭条件：append 后、关闭 fd 前，必须通过同一 fd 重新读取并验证 `current_bytes == exact_original_prefix + exact_event_line`，同时验证 size、inode和路径 receipt；验证失败时不得宣告成功。若 prefix 已变化而 event 已追加，状态机应停止并保留可审计现场，不能仅按 event map接受。增加 pread 后/write 前同 inode同尺寸 raw mutation、write 后/post-read 前 mutation、完整 event+prefix drift、path replacement 的主动测试；同一 transaction/event 的后续 resume 和 terminal replay必须证明原 prefix逐字节不变且 event恰好一次。

## 最终边界

当前不满足创建 migration verdict、replacement recovery verdict或执行一次 migration 的条件。允许的后续工作仅限按上述三个残余关闭条件修改冻结实现与测试，再进行第二次定点复核。

只有新的独立报告达到 `BLOCKING=0`、`NON_BLOCKING=0`，才可生成两份专用 verdict；即使届时 PASS，允许范围也只能是执行一次 `overlap-migrate-source-control-post-failure`，随后立即停止并进行 migration 执行事实审计。不得在同一步执行 recovery resume、source_prepare、source build、smoke、batch 或 GPU 动作。
