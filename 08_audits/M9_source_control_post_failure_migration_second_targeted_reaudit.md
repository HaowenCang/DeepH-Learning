# M9 post-failure migration R34-B01/B02/B03 第二次定点复核

审计日期：2026-08-19  
审计范围：`M9-SPR-R34-B01`、`M9-SPR-R34-B02`、`M9-SPR-R34-B03` 的最终关闭证据  
审计约束：正式现场只读；主动故障重放仅使用临时目录；未创建或执行正式 gate、migration、recovery、source_prepare 或 source build

## 结论

本轮判定为 **PASS**：`BLOCKING=0`，`NON_BLOCKING=0`。三个稳定问题均为 **CLOSED**。

当前实现已使 failed recovery transaction 的首次 receipt 与 root-private original snapshot 复用一次稳定读取所得的同一 payload；后续每次 journal 重入又按状态验证正式 recovery transaction。`PREPARED`、`GATE_RETIRED` 要求原失败 transaction，`REPLACEMENT_CREATED` 仅接受原 transaction 或严格完整的 migrated transaction，`RECOVERY_RECEIPT_MIGRATED`、`SUCCESS_COMMITTED` 要求 journal 冻结的 migrated SHA。迁移时间 `migration_utc` 在 journal 中一次冻结，完整 migrated payload 因而可确定性复核。

UID1000 正式对象的 fixed tmp durable helper 现在先 `fchmod`、后 `fchown`，并能在严格限定为 root:root、空、普通文件、nlink 1 的自身 pre-chown 中断现场上安全续提；异常 owner、非空或链接对象仍停止。ledger append 使用 existing-only、no-follow、同 fd `O_RDWR|O_APPEND`，写入后在关闭 fd 前再次读取并验证原 prefix 的 size 和 SHA。主动重放确认：PREPARED recovery transaction 漂移在下一状态写入前停止；root-owned empty tmp 可以续提并收敛为唯一 UID1000 target；`pread` 后、`write` 前对同 inode、同尺寸 prefix 的变化导致 `append prefix changed during write`，不会被接受为成功。

因此，本轮允许生成本报告所绑定的 migration verdict 与 replacement recovery verdict，并在下述精确前置条件成立时执行一次 `overlap-migrate-source-control-post-failure`。本报告不授权 source-control recovery resume、source_prepare、source build、smoke、batch 或 GPU 动作。

## 冻结快照与完整回归

独立复算六项摘要均与送审值完全一致：

- `m9_budget.py`：`8a21f1768cc14a086d4b8edb7ea8c8e76a7213ef9871eb5489a9463ef0cd8d8a`；
- `test_m9_overlap_controls.py`：`6e6d6463631fd44b7b592353ecb8ad611ca2822f81b00572edbc6b626ad95e98`；
- source frozen manifest：`03ed6d0e4b2ff126d11d0e5e772e479bf9c3f14f5bb2833de0358fa500fb0350`，19/19，mismatch=0；
- cleanup frozen manifest：`262971954db403700d27e1df35365cf3e6a4acf3937a766f2bd0f89f642897ef`，4/4，mismatch=0；
- post-failure contract：`dbb93a26d7a5b80b6992ead374dda8421d763679ce63ecf349688b4a38426c2e`；
- authorization：`8c9602d5cc774c64f87a41c13d68223583cc91d19596568055ea6c2eaef0e42b`。

以 root 和固定解释器 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 独立运行完整测试，结果为 `Ran 89 tests in 19.164s`、`OK`、退出码 0。测试覆盖每个 journal 状态的 immutable runtime 校验、root empty tmp 各 durability 窗口、同 fd prefix 变化、合法 proper-prefix suffix、同 transaction/event 的 exactly-once 续提及 terminal zero-write。`06_reproduction` 下 `__pycache__`/`.pyc` 计数为 0。

## 正式现场不变性

测试与主动重放后，正式 failed execution 证据仍为：

| 对象 | SHA-256 |
|---|---|
| failed recovery transaction | `89483c5653b05063308896d5fe61809916f210a906e09eeda068867608bed44e` |
| recovery parent / overlap transaction | `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309` |
| budget state | `1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc` |
| failed workflow | `73a3522af8a29d8300255b8deb9c2014628a27930ffb05b81f49255a8d5a8fbf` |
| ledger | `25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f` |
| retired capability | `0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e` |
| active source recovery gate | `381c8fd6e9fa28479de4f2144e975ed32756af9ac9dfe90a6d5457208da1cefa` |

failed transaction、parent/state/workflow/ledger、retired capability 和 active gate 均保持普通文件、nlink 1 及既有 owner/mode；active gate 为 root:root `0600`。post-failure journal、original transaction snapshot、pre-ledger-fix retired gate 均以 `lexists` 语义缺席。六项 source/build 产品均缺席。正式现场没有出现 migration、recovery resume 或 source preparation 写入。

## 稳定问题关闭判定

### M9-SPR-R34-B01 — CLOSED

`post_failure_runtime_receipts()` 对 recovery transaction 使用稳定单文件描述符读取，并将该次读取的 `recovery_bytes` 直接用于 original snapshot，不再从路径二次吸收内容。`verify_post_failure_immutable_runtime(runtime, journal)` 将 recovery transaction 纳入逐状态不变量：早期状态绑定 original SHA，后期状态绑定 migrated SHA，并验证 transaction ID、event ID、parent snapshot、new gate receipt、migration journal path 和冻结的 `migration_utc`。journal 重入时该检查发生在下一次正式状态写入前。

主动重放改变 PREPARED 场景的 recovery transaction 而保持其他 runtime 不变，结果为拒绝；代码和回归还覆盖各 journal 状态的 recovery/workflow/ledger 漂移以及 terminal replay。首次 snapshot payload、receipt SHA 和 journal original SHA 由同一稳定 bytes 派生。因此 B01 的读取一致性、状态一致性和下一写入前停止条件全部满足。

### M9-SPR-R34-B02 — CLOSED

`atomic_owned_durable_bytes/json()` 对新 fixed tmp 先建立受控 mode，再变更 owner；重入只对 root:root、size 0、普通文件、nlink 1 的 pre-chown tmp 执行受限接管，随后在同 fd 完成目标 owner/mode、写入、file fsync、atomic replace、target receipt/content recheck、target fsync 和 directory fsync。其他 root-owned 非空 tmp、错误 owner/mode、symlink、hardlink 仍不被接受。

独立 root/sticky 临时重放构造 open 后、ownership 变更前留下的 root:root empty fixed tmp；第二次调用成功续提，最终仅存在 UID/GID1000、`0644`、nlink 1、内容准确的 target，tmp 消失。完整测试覆盖 root empty tmp 在后续 durability 窗口的续提。因此 B02 的可证明中断续提条件满足。

### M9-SPR-R34-B03 — CLOSED

`append_existing_regular_bytes()` 以 existing-only 的 `O_RDWR|O_APPEND|O_CLOEXEC|O_NOFOLLOW` 打开 ledger；在同 fd 上验证预期 prefix size/SHA，执行 append 和 file fsync，并在关闭 fd 前再次以同 fd `pread` 验证原 prefix 的 size/SHA，同时核对 fd/path dev、inode、metadata 和最终 size。prefix 变化会停止，不会把语义等价但 raw bytes 不同的 ledger 当作成功。

独立主动重放在第一次 `pread` 后、append `write` 前修改同 inode、同尺寸 prefix，helper 明确拒绝；测试还覆盖 write 后校验、short write、合法 exact proper-prefix suffix、path/content TOCTOU、同一 event exactly once 和 terminal zero-write。事件已经写入而 prefix 后验失配的现场会保持可审计失败，而不会提交 migration success。因此 B03 的 raw prefix 保真和 exactly-once 条件满足。

## 允许范围与执行前置条件

允许范围仅为：由主 agent 使用本报告对应的两份专用 PASS verdict，执行一次 `overlap-migrate-source-control-post-failure`。执行必须同时满足：

- 六项冻结摘要仍等于本报告所列值，19/19 与 4/4 仍为 mismatch=0；
- `verify_source_control_post_failure_migration()` 在正式执行前返回 PASS，且 verdict、replacement verdict、contract、authorization、failed runtime 的绑定与本报告一致；
- failed recovery transaction、parent、state、workflow、ledger、retired capability、active gate 的 SHA 与上表一致；post-failure journal、original snapshot、pre-ledger-fix retired gate仍缺席；
- 使用 root、固定 Python、既存 `budget.lock` 的 `r+` 模式；不得以手工方式修改任何 runtime；
- 六项 source/build 产品仍缺席。

任一条件不成立时应在首次正式写入前停止。本次一次性 migration 执行完成后必须立即停止并进行独立执行事实审计。即使 migration 成功，也不得直接续提 source-control recovery，更不得执行 source_prepare 或 source build。
