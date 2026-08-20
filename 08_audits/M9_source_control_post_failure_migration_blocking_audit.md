# M9 post-failure source-control migration 与 existing-only ledger append 独立审计

审计日期：2026-08-19  
审计对象：post-failure gate/receipt migration、同一 source-control recovery transaction 续提、existing-only ledger append  
审计方式：冻结对象复算、代码与合同审查、root 固定 Python 完整测试、临时目录主动故障重放、正式现场前后只读核对  

## 结论

本轮判定为 **FAIL**：`BLOCKING=3`，`NON_BLOCKING=0`。

实现已正确消除正式 ledger 打开时的 `O_CREAT`：正常 existing-only 路径采用 `O_WRONLY | O_APPEND | O_CLOEXEC | O_NOFOLLOW`，并以同一 fd 执行 `fstat`、write 和 file fsync；真实 root、sticky、`fs.protected_regular=2` 环境的正常追加测试通过。实现也建立了专用 migration verdict、contract、root-private failed-transaction snapshot、root-private journal、old→new gate 和同 transaction/event receipt migration 的基本状态机。

但当前证据不足以允许正式 migration。独立主动重放确认三类持久化缺口：

- `PREPARED` journal 重入不重新核验冻结 failed runtime；workflow 已漂移时命令仍返回 0，并将 migration journal 提交为 `SUCCESS_COMMITTED`。
- `RECOVERY_RECEIPT_MIGRATED` 前对正式 recovery transaction 的更新仍使用固定 `.tmp`、无 file/directory fsync 的 `atomic_json()`；若在 tmp 已 chown 为 UID1000 后中断，重入会再次因 `protected_regular` 失败。
- ledger helper 虽不再请求创建文件，却只核 size/metadata，不核同一 fd 上的原始前缀内容；同 inode、同尺寸的前缀变化可被接受，短写还会留下不可解析的部分 event，现有状态机不能证明续提收敛到 event 恰好一次。

因此没有生成 migration verdict 或 replacement source-recovery verdict，也不允许创建或执行正式 migration、recovery resume、source_prepare 或 source build。

## 冻结闭集与正式测试

复算结果与送审值完全一致：

- `06_reproduction/scripts/m9_budget.py`：`bc05409df17492512827cb9ac2af2a410cb9a298468ed6d1b263b3aaf153693e`，228331 bytes；
- `06_reproduction/tests/test_m9_overlap_controls.py`：`7f6c6243e1c10bad0c8b66f62a4d88635bad7e7be2116cecf6f76d64ab01db5a`，177350 bytes；
- source frozen manifest：`43345f3d50ba7cb1f0c295d120d7441f3aaad3fcde6afa92ef5303c04d66d0d8`，19/19 匹配；
- cleanup frozen manifest：`0a249b264887a894922a0a0a80d223bb191f7dc8e432a6b5488de5f35f119289`，4/4 匹配；
- post-failure contract：`b975b63c2034a54592535e250e411909ad0f844149c3aacbe6fe8285b4e0053a`；
- authorization：`8c9602d5cc774c64f87a41c13d68223583cc91d19596568055ea6c2eaef0e42b`。

contract 的 schema、decision 和 scope 分别为 `m9-source-control-post-failure-contract-v1`、`D-017-source-control-post-failure-migration-v1`、`MIGRATE_AND_RESUME_SAME_SOURCE_CONTROL_RECOVERY_TRANSACTION`。其 failed runtime 精确绑定 transaction `4783a27441019358a0f15127f26d957d`、同一 recovery event、parent/state/workflow/ledger、retired capability 和 active gate；authorization 明确把剩余权限限制为修复 existing-only append、迁移旧 gate receipt 并续提同一 transaction/event，不授权第二个 recovery、source_prepare 或 source build。

以 root、冻结 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9`、`-I -S -B` 独立运行完整测试，结果为 `Ran 86 tests in 17.067s`、`OK`、退出码 0。测试前后正式对象哈希不变，post-failure journal、original snapshot、pre-ledger-fix retired gate 持续缺席，六项 source/build 产品持续缺席，cache 计数为 0。

86 项中与本轮新增范围直接相关的测试只有：existing-only 正常 flags/inode、symlink/hardlink 拒绝、真实 root sticky/protected_regular 正常追加，以及一项 migration→resume 成功路径。migration 成功测试同时 mock 了 migration verifier、source gate verifier、strict root-private JSON/receipt、root-private atomic bytes/JSON；它没有执行真实 root-private journal 或 receipt migration 的故障窗口，也没有 `PREPARED`、`GATE_RETIRED`、`REPLACEMENT_CREATED`、`RECOVERY_RECEIPT_MIGRATED`、`SUCCESS_COMMITTED` 的逐状态重入矩阵。因此 86/86 是必要证据，但不是本轮可靠性结论的充分证据。

## 正式现场零写入核对

测试前后以下值保持一致：

| 对象 | SHA-256 / 状态 |
|---|---|
| failed recovery transaction | `89483c5653b05063308896d5fe61809916f210a906e09eeda068867608bed44e` |
| parent snapshot / parent transaction | `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309` |
| budget state | `1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc` |
| failed workflow | `73a3522af8a29d8300255b8deb9c2014628a27930ffb05b81f49255a8d5a8fbf` |
| ledger | `25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f` |
| retired capability | `0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e` |
| active gate | `381c8fd6e9fa28479de4f2144e975ed32756af9ac9dfe90a6d5457208da1cefa` |
| budget lock | empty SHA `e3b0c442...b855` |
| disposition journal | `e97dc9b00a798f5a26807e5af18c78c2779be4ab144adeaa39f5be4338dc8ece` |
| lock-refresh journal | `ec6a30547c78a0b2030069b8d6a682fadef7e7fb20062bcf76672b604f020519` |

failed transaction 为 UID/GID `1000:1000`、`0644`、nlink 1；retired capability 为 `1000:1000`、`0600`、nlink 1；active gate 为 root:root、`0600`、nlink 1。`/root/deeph-m9-control/source-control-post-failure-migration.json`、`source-control-failed-recovery-original.json` 和 `overlap_source_control_recovery_gate.pre-ledger-fix.retired.json` 均以 `lexists` 语义确认缺席。

六项 source/build 产品均缺席：`openmx-overlap-build`、`openmx-overlap-build.staging`、`env/hdf5-1.12.1` 及三项 source/build manifest。由此可确认本轮审计和测试没有执行正式 migration/recovery，也没有产生 source_prepare 或 build 产物。

## 已成立的实现部分

`append_existing_regular_bytes()` 的正常路径明确不含 `O_CREAT`/`O_TRUNC`，包含 `O_APPEND`、`O_CLOEXEC` 和可用时的 `O_NOFOLLOW`。它在 open 前检查普通文件、UID/GID、mode、nlink；open 后要求 fd 与路径 dev/inode/metadata 一致；写入后执行 file fsync、检查 size 增量、再次核 fd/path metadata，再执行 parent directory fsync。真实 root 测试在 root:GID1000、`1770` sticky 目录中对 UID/GID1000、`0644` ledger 成功追加，说明上一轮正式 `PermissionError` 的直接打开模式根因已被关闭。

`verify_source_control_post_failure_migration()` 对 migration verdict、replacement verdict、19 项 frozen manifest、authorization、contract 和 failed runtime 建立了独立 domain。migration command 在 lock 前验证材料，在 `r+` lock 内建立 root-private original snapshot 和 `PREPARED` journal，然后依次进入 `GATE_RETIRED`、`REPLACEMENT_CREATED`、`RECOVERY_RECEIPT_MIGRATED`、`SUCCESS_COMMITTED`。replacement gate 的构造保留旧 gate 字段，更新 verdict/frozen/auth，并加入 transaction/event/failed workflow/ledger/contract 的 `post_failure_resume` 绑定；创建后实际调用 source gate verifier。receipt migration 保留 transaction/event ID，在 recovery transaction 中记录旧/new gate receipt 和 root-private original snapshot。

这些结构方向正确，但下列阻塞使其尚不能形成可证明的故障恢复合同。

## 阻塞问题

### M9-SPR-R34-B01 — journal 重入不重新核验状态特定的 failed runtime，允许漂移后 terminal success

严重性：BLOCKING。

`post_failure_runtime_receipts(runtime)` 只在 journal 不存在的首次分支调用。journal 已为 `PREPARED` 或后续状态时，command 只核 journal 内的 verdict/frozen/contract/runtime 字段和 original snapshot；它不重新读取并比较 state、workflow、ledger、parent、retired capability 等仍应冻结的正式对象。因而 journal 建立后的 UID1000 runtime 变化不会阻止 gate retirement、replacement creation 和 recovery receipt migration。

独立临时目录重放使用正式 failed transaction、parent、state、workflow、ledger、retired capability 和 old gate 的拷贝。第一次调用在真实 `PREPARED` root-private journal 落盘后中断；随后仅改变 workflow，使其 SHA 从授权值 `73a352...a8fbf` 变为 `6b81467a...c7229`；第二次调用仍返回 0，并把 journal 写为 `SUCCESS_COMMITTED`。这直接证明 runtime exact binding 在重入路径上没有被执行。后续 recovery resume 可能因 workflow hash 不匹配而重新 hard-stop，但 migration 已被错误标为 terminal success，违反了“迁移成功即 receipt 可消费”的一致性语义。

此外，首次 `post_failure_runtime_receipts()` 对 UID1000 对象使用 `is_symlink()`、`is_file()`、`lstat()`、`read_bytes()` 的多次路径读取，不是 single-fd receipt。recovery transaction 随后又以新的 `read_bytes()` 建立 original snapshot。路径在这些读取之间发生替换时，可能在 first mutation 前后消费不同 inode；当前只在较晚阶段得到失败，而不是形成同一字节/同一 inode 的前置绑定。

最小关闭条件：

- 对 UID1000 recovery、parent、transaction、state、workflow、ledger、retired capability 使用 `O_NOFOLLOW | O_CLOEXEC` 单 fd 读取，执行 open→fstat→同 fd read→fstat→lstat，并绑定 dev/inode/owner/mode/nlink/size/SHA/payload；original snapshot 必须来自同一次 recovery fd payload。
- 每次重入、每个下一状态写入前按当前 journal state 重新核验所有不应变化的 runtime。`PREPARED` 要求 original recovery 和 old active/retired gate 二选一的合法崩溃现场；`GATE_RETIRED` 要求 old retired 精确、active 缺席；`REPLACEMENT_CREATED` 要求 replacement 精确；`RECOVERY_RECEIPT_MIGRATED`/`SUCCESS_COMMITTED` 要求 migrated recovery 精确。parent/state/workflow/ledger/retired capability 在所有 migration 状态中均须保持 contract 值。
- 使用 `lexists`/`exists-or-is-symlink` 拒绝 active/retired/journal 路径的 dangling symlink 和不属于合法状态的目录项；重算 `context_sha256 == canonical_hash(context)`。
- 增加五状态逐项漂移测试；每种 state/workflow/ledger/parent/recovery/retired/gate 漂移都必须在下一正式写入前停止，journal 不得进入 `SUCCESS_COMMITTED`。

### M9-SPR-R34-B02 — recovery receipt migration 使用非持久化 fixed tmp，崩溃后不可证明续提

严重性：BLOCKING。

在 `REPLACEMENT_CREATED` 阶段，代码用通用 `atomic_json()` 写回正式 `overlap_source_control_recovery.json`。该函数固定使用 `<target>.tmp`，通过 `Path.write_text()` 创建/截断，随后 chown 为 UID1000，再 `os.replace()`；它没有 file fsync、target 后验 receipt 或 parent directory fsync。

如果执行在 tmp 已写入并 chown 为 UID1000、但尚未 replace 时中断，固定 tmp 会留在 root:GID1000、`1770` sticky manifests 目录。独立 root 临时复现把该现场构造为 UID1000 fixed tmp；下一次 `atomic_json()` 的 `Path.write_text()` 因带 `O_CREAT|O_TRUNC` 而收到 `PermissionError`，与先前 ledger/lock 的 `protected_regular` 机理相同。该窗口使 `REPLACEMENT_CREATED` 无法续提。即使没有中断，缺少 fsync 也不能证明 journal 的 `migrated_recovery_sha256` 所引用 transaction 已达到持久化边界。

最小关闭条件：为 UID1000、`0644` runtime JSON 实现 existing-target、durable atomic replacement 合同。固定或记录的 tmp 若已存在，应以不含 `O_CREAT`、含 `O_NOFOLLOW` 的 fd 打开，严格核 owner/mode/nlink/dev/inode 后覆盖；首次创建应使用 `O_CREAT|O_EXCL`。必须对同 fd 完整写入、flush/fsync，验证 tmp payload/metadata，replace 后验证 target payload/metadata，再执行 target file fsync 与 directory fsync。应覆盖 tmp 部分内容、symlink、hardlink、wrong owner/mode，以及 create/write/file-fsync/replace/target-recheck/target-fsync/directory-fsync 的每个中断点，证明第二次调用收敛到同一 migrated recovery SHA。

测试还必须在 migration transaction 写入后、`RECOVERY_RECEIPT_MIGRATED` journal 写入前中断，确认重入识别已经迁移的同一 transaction，而不重复追加 `failure_history`、不改变 transaction/event ID，并保持 old/new gate receipt 唯一。

### M9-SPR-R34-B03 — ledger prefix/content 与短写恢复没有形成 exactly-once 持久化合同

严重性：BLOCKING。

existing-only helper 的 stable fields 不含内容哈希；fd 以 `O_WRONLY` 打开，不能从同一 fd 验证 append 前的精确 prefix。写后检查只要求 inode/metadata 稳定和 `size == old_size + payload_size`。独立临时重放在 helper 已取得 fd 后，用另一写入者把 ledger 前缀改成同 inode、同尺寸、JSON 语义相同但字段顺序不同的 bytes，然后执行 append。helper 正常返回，证明“preserve exact ledger prefix”并未由 fd 合同保证。

`source_control_resume()` 虽在 append 前读取并核 parent ledger SHA，但 append 后只调用 `ledger_event_ids()` 比较 canonical event mapping；它没有重新读取并核验原始前缀 bytes。字段顺序或空白变化会产生相同 canonical mapping，因此上述同尺寸变化可以越过后验检查并成为新的 `post_ledger_sha256`。

短写恢复也不成立。独立注入让 `os.write()` 只提交目标 event 的前三个 bytes；helper 抛出 `OSError: ledger append was short`，但 ledger 已从 `BASE\n` 变为 `BASE\nREC`。下一次 `ledger_event_ids()` 会遇到无效 JSON；当前代码没有在 exact parent prefix 后识别、截断或安全完成这个部分 suffix 的协议，因而不能从该合法 I/O 故障窗口续提到 event 恰好一次。

最小关闭条件：

- append 前通过可读写或只读绑定 fd 得到 exact parent prefix receipt，并在持有 budget lock 时将 append 限定为 `original_size` 之后的规范 event bytes；append 后重新读取同 inode 或以严格 fd 读取验证 `current_bytes == original_prefix + exact_event_line`，不能只比较 canonical event mapping。
- 明确定义 suffix 状态机：空 suffix、完整 exact suffix、目标 event 的严格前缀、其他 suffix。空 suffix 可写；完整 suffix视为已提交；严格部分前缀只能在核对 inode、parent prefix、event ID 和 transaction journal 后安全截断至 parent size 再重写，或采用能避免暴露部分 ledger 行的等价持久化协议；其他 suffix 必须停止。
- 对 write short、write exception after N bytes、file fsync 中断、append 后 recovery journal 写入前中断、directory fsync 中断逐点重放；每次第二次调用必须收敛为同一 ledger bytes、同一 transaction/event ID、event 计数恰好 1。还应覆盖同 inode 同尺寸 raw-prefix 变化、symlink/hardlink/path replacement、同 ID 异载荷和额外 event。

## 状态机与授权边界

当前 PREPARED→GATE_RETIRED→REPLACEMENT_CREATED→RECOVERY_RECEIPT_MIGRATED→SUCCESS_COMMITTED 的无中断成功序列可以在临时测试中完成，并保持同 transaction/event；但这不能替代崩溃恢复证明。B01 表明重入可在 runtime 漂移后错误成功，B02 表明 receipt migration 的固定 tmp 中断不可续提，B03 表明 ledger I/O 中断可能留下没有恢复协议的部分 event。因此 terminal replay zero-write 只对无故障 happy path 成立，尚不能外推到正式状态机。

本报告不授权生成两份 verdict，也不授权执行一次 migration。允许的后续动作仅限修改被冻结审对象、补充回归并重新独立审计；在新的报告达到 `BLOCKING=0`、`NON_BLOCKING=0` 后，才可考虑生成：

1. `m9-source-control-post-failure-migration-verdict-v1` / `D-017-source-control-post-failure-migration-v1` 的 migration verdict；
2. `m9-source-control-recovery-audit-verdict-v1` / `D-017-source-control-recovery-v1` 的 replacement verdict。

即使未来 migration 审计 PASS，允许范围也只能是创建这两份 verdict 并执行一次 `overlap-migrate-source-control-post-failure`，完成后立即停止并进行独立执行事实审计。不得在同一授权步骤中执行 recovery resume；recovery resume 仍须以 migration 执行事实审计 PASS 为新的检查点。source_prepare、source build、smoke、batch、GPU 与 M9-05 均不在本轮授权范围。
