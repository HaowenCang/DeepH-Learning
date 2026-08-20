# M9 post-failure source-control migration 执行事实独立审计

审计日期：2026-08-19  
执行对象：一次性 `overlap-migrate-source-control-post-failure`  
执行信封：root 固定 Python `-I -S -B`，报告命令退出码 0，stdout/stderr 为空  
审计约束：正式现场全程只读；未执行 migration replay、source-control recovery resume、source_prepare、source build、smoke、batch 或 GPU 动作

## 结论

本轮判定为 **PASS**：`BLOCKING=0`，`NON_BLOCKING=0`。

持久化现场证明同一 failed source-control recovery transaction 已完成一次受控 post-failure migration：root-private journal 为 `SUCCESS_COMMITTED`；原失败 transaction 字节已完整保存；旧 gate 原子退役且字节不变；replacement gate 与确定性重建结果逐字节相等并通过正式 source gate verifier；现有 recovery transaction 保留原 transaction ID、event ID、`FAILED_COMMITTED` 和 `ledger_phase=PENDING`，仅新增经审计的 migration receipt、更新 gate receipt并保留 failure history。budget state、failed workflow、ledger、parent transaction 和 retired capability 均保持授权摘要，ledger 中该 recovery event 仍为 0 次。

未发现 migration 范围外的运行时变化或 source/build 产品。因此，下一步只允许续提这一个既存 transaction `4783a27441019358a0f15127f26d957d` 的同一个 recovery event `4783a27441019358a0f15127f26d957d:source-control-recovery`。不得创建新 recovery transaction 或新 recovery event，也不得在同一步执行 source_prepare、source build 或其他下游动作。

## 独立现场复算

所有正式对象均以 root 只读方式重新读取，摘要和元数据如下：

| 对象 | SHA-256 | bytes | owner/mode/nlink |
|---|---|---:|---|
| migration journal | `3d84cf6a82b3403e63ce22b72712efa232feca6d3a8dd3e17d877b9f48c4cb6d` | 6446 | root:root `0600`, 1 |
| original failed recovery snapshot | `89483c5653b05063308896d5fe61809916f210a906e09eeda068867608bed44e` | 5028 | root:root `0600`, 1 |
| pre-ledger-fix retired gate | `381c8fd6e9fa28479de4f2144e975ed32756af9ac9dfe90a6d5457208da1cefa` | 1728 | root:root `0600`, 1 |
| active replacement gate | `8e66d65d17d3195f3df09db954afca4066c3ec91e2d8dad6d2aea06078d0d5ce` | 2398 | root:root `0600`, 1 |
| migrated recovery transaction | `9279e561c8328c674465a95fcb37fc1c9618bc1dcfe8b302cdb6655802aa2a2a` | 8007 | UID/GID1000 `0644`, 1 |
| recovery parent / overlap transaction | `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309` | 2347 | UID/GID1000 `0644`, 1 |
| budget state | `1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc` | 1334 | UID/GID1000 `0644`, 1 |
| failed workflow | `73a3522af8a29d8300255b8deb9c2014628a27930ffb05b81f49255a8d5a8fbf` | 631 | UID/GID1000 `0644`, 1 |
| budget ledger | `25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f` | 58462 | UID/GID1000 `0644`, 1 |
| retired capability | `0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e` | 4309 | UID/GID1000 `0600`, 1 |
| budget lock | empty SHA `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 | UID/GID1000 `0644`, 1 |

活动 stale capability 路径仍缺席；capability 目录只包含上述 retired capability。六项 source/build 产品——`openmx-overlap-build`、`openmx-overlap-build.staging`、`env/hdf5-1.12.1` 及三项 source/build manifest——全部缺席。`06_reproduction` 下 cache 计数为 0。

控制包及授权材料保持第二次定点复核时的冻结摘要：budget `8a21f1768cc14a086d4b8edb7ea8c8e76a7213ef9871eb5489a9463ef0cd8d8a`，tests `6e6d6463631fd44b7b592353ecb8ad611ca2822f81b00572edbc6b626ad95e98`，source frozen manifest `03ed6d0e4b2ff126d11d0e5e772e479bf9c3f14f5bb2833de0358fa500fb0350`，cleanup manifest `262971954db403700d27e1df35365cf3e6a4acf3937a766f2bd0f89f642897ef`，post-failure contract `dbb93a26d7a5b80b6992ead374dda8421d763679ce63ecf349688b4a38426c2e`，authorization `8c9602d5cc774c64f87a41c13d68223583cc91d19596568055ea6c2eaef0e42b`。migration verdict、replacement verdict和前置报告摘要也分别保持 `1263d7e654b6e7b7ad99a847e048720070c2247bc205146feead11afdfa7a442`、`b62c65e02c247eae56a8fae687cd05946dcf6aedfa6c4f2177bf4298255e84b4`、`dc0b4d4672934b63ec075b639420b73cb175b302f6f21d7f082fcac2568c8ab8`。

## Journal 与状态一致性

root-private journal 的 schema 为 `m9-source-control-post-failure-migration-v1`，状态为 `SUCCESS_COMMITTED`，`prepared_utc=2026-08-19T14:10:37.948687Z`，冻结的 `migration_utc=2026-08-19T14:10:39.958130Z`，`completed_utc=2026-08-19T14:10:39.996886Z`，时间顺序一致。固定 Python bootstrap完整记录 isolated、no-site、dont-write-bytecode、解释器路径以及四个标准库模块的 origin/loader/SHA。

独立重算 journal `context` 的 canonical SHA 得到 `06b7081c10c7437d665cf1e50e2f08ba781c360aea02037c84912b891f0b58a4`，与 `context_sha256` 相等。context 同时绑定：原活动 gate receipt、原 transaction snapshot receipt、replacement gate预期 SHA/bytes和迁移前全部 runtime 摘要。journal 的 verdict、replacement verdict、frozen manifest和contract receipt均与正式材料相等；其 `runtime` 与 migration verdict 的 `failed_runtime` 相等。

journal 的 `migrated_recovery_sha256` 等于当前 recovery transaction SHA；`replacement_gate`、`retired_gate` 及 original snapshot receipts分别等于现场普通文件 receipt。不存在链接或多链接退化。

## 原对象保真与 replacement gate

original snapshot 的 5028 字节 SHA与迁移前 failed recovery transaction摘要 `89483c...ed44e` 完全相等。snapshot 内 transaction ID、event ID、`FAILED_COMMITTED`、failure reason 和原 gate receipt均保持原值。

退役 gate的 1728 字节 receipt与 journal `context.old_gate` 完全相等，因此旧 gate在 rename过程中未被改写。以退役 gate、journal 冻结的 replacement verdict/frozen/authorization/contract/runtime重新调用 `build_post_failure_replacement_gate()`，所得序列化字节与当前 active gate逐字节相等，SHA为 `8e66d65d...d0d5ce`。

只读调用 `verify_source_control_recovery_gate_and_hashes()` 返回与 active gate payload相同的 PASS对象。其 scope为 `ONE_TIME_SOURCE_CONTROL_RECOVERY`，审计材料绑定 replacement verdict `b62c65e0...5e84b4`，frozen manifest绑定 `03ed6d0e...fb0350`，授权绑定 `8c9602d5...0e42b`；`post_failure_resume` 精确绑定同一 transaction/event、原失败 transaction、failed workflow、ledger、contract及 event count 0。

## Migrated recovery transaction

当前 recovery transaction 仍为：

- `transaction_id=4783a27441019358a0f15127f26d957d`；
- `event_id=4783a27441019358a0f15127f26d957d:source-control-recovery`；
- `state=FAILED_COMMITTED`；
- `ledger_phase=PENDING`；
- 原 failure reason保持 `budget_ledger.jsonl` 的 `PermissionError`；
- `post_failure_migration.status=PASS`。

将 original snapshot 与当前 transaction作结构差异复核，变化仅位于 `failure_history`、`gate_receipt` 和新增的 `post_failure_migration`。`failure_history` 保存原失败摘要；新 migration receipt绑定 original snapshot、old/new gate receipts、failed state/workflow、ledger、migration verdict、journal path/context和冻结时间。transaction/event没有替换或新建。

只读调用 `validate_migrated_failed_recovery()` 成功；migration receipt中的 `migrated_utc`与 journal冻结值一致，gate receipt与 verifier计算值相等。对 ledger重新解析，目标 event ID计数为 0，未出现部分或重复 recovery event。因此当前状态正是同一 transaction在 ledger append之前可续提的 `PENDING` 点，而不是一次新 recovery。

## 授权边界

本报告的零问题 PASS仅解除 post-failure migration执行后的事实检查点。下一步允许范围严格限于消费当前 active one-time gate，续提同一 transaction ID和同一 event ID的 `overlap-recover-source-control-failure`。执行前仍应重新验证 active gate、migration journal、original snapshot、migrated transaction、parent/state/workflow/ledger/retired capability及 frozen闭集；任一摘要、receipt或 event count漂移均应在首次写入前停止。

该续提应实现 ledger event恰好一次并将同一 transaction收敛到其既定终态；不得通过新 transaction或新 event处理既有失败。即使 recovery resume成功，也必须立即停止并进行独立执行事实审计。source_prepare、source build、smoke、batch、GPU及其他下游动作仍未获本报告授权。
