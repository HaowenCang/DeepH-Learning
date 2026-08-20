# M9 source-control recovery 第三十次 lock-mode gate refresh 阻塞复核

## 结论

本轮独立只读复核结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。recovery 与 refresh 入口改用既存锁的 `r+` 已解决 root 在 sticky 目录中以 `a+` 请求 `O_CREAT` 时得到 `EACCES` 的已知问题；专用 verdict 域、post-disposition runtime、旧 gate 固定收据、root 私有 journal、六个崩溃窗口和常规终态 replay 也已建立。但主动临时复现发现两个未被 78 项覆盖的一致性窗口：锁前已验证的控制材料可以在命令后续按路径读取时被吸收为另一组字节；replacement gate 的严格 receipt 与实际 source verifier 之间发生路径或链接元数据变化时，首次调用仍会提交 `SUCCESS_COMMITTED` 并返回 0。

因此当前不允许创建 `M9_source_control_gate_lock_refresh_final_verdict.json` 或 `M9_source_control_recovery_lock_replacement_final_verdict.json`，也不允许执行一次性 refresh。用户已经给出的单次 source-control recovery 授权保持存在，但在 refresh 修复、再次独立零问题复核以及 refresh 执行事实审计完成前，不得消费该授权。本报告不授权 refresh、recovery、disposition replay 或 `source_prepare`。

## 冻结快照与正式现场

独立复算的四项 SHA-256 与指定值一致：

- `06_reproduction/scripts/m9_budget.py`：`6414f194484b9063f09bfc55f0d3af7ec575c3f265d274a2655ceda0f4ca1539`
- `06_reproduction/tests/test_m9_overlap_controls.py`：`6f763ecaaad660a3fe84c83d2d4101650b269ebabf73639c9f23f72f9fc4b145`
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：`c49f9e89435fa599cae472ea79c5cadb1be2b83c9d41f81ab92648b2b6f986a4`
- `06_reproduction/manifests/m9_source_control_test_cleanup_frozen_hashes.json`：`e82e2cd138cee66d2d194b8b2f3c489ea18bd3a8eed98d80d2fbacf4d16d35c7`

source manifest 的 18 个成员逐项复算为 `18/18`，cleanup manifest 的 4 个成员为 `4/4`，无缺失或哈希不符。`06_reproduction` 下 `.pyc`、`.pyo` 和 `__pycache__` 合计为 0。

正式现场前后保持：active pre-lock gate SHA-256 `5553de21184082b3ace505f4981f20c3116df7389805f2070ebf7e8b8dad5936`、1723 bytes、root:root、0600、nlink 1、inode 139158；old-invalid retired gate SHA-256 `6bdd2fdbff6df6a7a8cfa1ba3cda038ca7cfe96b3b5dfb48905ef0f5151f5821`、1711 bytes、root:root、0600、nlink 1、inode 132095；disposition journal SHA-256 `e97dc9b00a798f5a26807e5af18c78c2779be4ab144adeaa39f5be4338dc8ece`、3748 bytes、root:root、0600、nlink 1。

五项 runtime 保持原基线：state `1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`、workflow `2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`、failed transaction `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`、ledger `25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`、stale capability `0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`。

`source_control_lock_refresh_runtime_receipt()` 实际返回上述五项哈希，并额外绑定 disposition journal SHA `e97dc9b00a798f5a26807e5af18c78c2779be4ab144adeaa39f5be4338dc8ece`、invalid-retired gate SHA `6bdd2fdbff6df6a7a8cfa1ba3cda038ca7cfe96b3b5dfb48905ef0f5151f5821` 及 recovery transaction/parent 缺席。refresh 专用两份 verdict、pre-lock retired gate、root refresh journal、recovery transaction 和 recovery parent 全部缺席。

当前 active gate仍绑定 refresh 前 frozen SHA；实际 `verify_source_control_recovery_gate_and_hashes()` 对当前新 frozen snapshot 得到 `source-control recovery frozen hash binding mismatch`。这是 refresh 所要处置的预期前置状态，不构成本报告新增问题，同时证明未刷新 gate 不能直接进入 recovery。

## 已满足的控制条件

`verify_source_control_gate_lock_refresh()` 对 refresh verdict 强制 schema `m9-source-control-gate-lock-refresh-audit-verdict-v1`、decision `D-017-source-control-gate-lock-refresh-v1`、scope `RETIRE_PRE_LOCK_MODE_GATE_AND_CREATE_REPLACEMENT_ONLY`、PASS 0/0、旧 gate 固定 SHA/1723 bytes、报告路径/SHA、replacement verdict 路径/SHA、当前 frozen SHA 和授权记录 SHA；它逐项复算 18 成员并检查控制目录闭集。replacement verdict 至少被限定为 source-recovery 专用 schema、D-017 decision 和 PASS 0/0。

refresh 命令在 root 与隔离 bootstrap 验证后以 `LOCK_PATH.open("r+")` 打开既存锁，并在锁内复算 post-disposition runtime。正式目录 root:GID1000/1770、锁 UID/GID1000:1000/0644 的实际内核复现结果为：`a+` 得到 errno 13，`r+` 成功取得和释放排他锁；锁 inode 50700、0 bytes 与空文件 SHA 前后相同。recovery 入口也使用 `r+`，对应命令级测试观测到唯一模式为 `r+`。

旧 active gate或 runtime 在首写前漂移时，临时复现分别得到固定 receipt mismatch 和 runtime drift，refresh journal 与 pre-lock retired 保持缺席。既存终态 journal 改为 symlink 或增加 hardlink时，命令分别由 `O_NOFOLLOW` 或 nlink 1 条件停止，active 与 retired bytes 不变。journal 通过现有单 FD `read_strict_root_private_bytes()` 完成 open、fstat、同 fd read、再次 fstat 和 path lstat 的 device/inode/metadata/size一致性验证。

冻结 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9` 以 `-I -S -B` 执行正式套件，结果为 `Ran 78 tests in 16.453s`、`OK`、退出码 0。`prepared`、`rename`、`retired_journal`、`replacement`、`replacement_journal`、`terminal` 六个中断窗口均可在第二次调用续提至 `SUCCESS_COMMITTED`；常规终态 replay 对 active、pre-lock retired 和 journal 保持逐字节零写入。

以上结果确认常规状态机和既存异常输入可以停止，但不能反证以下两个主动复现的窗口。

## M9-SPR-R30-B01：锁前验证材料与锁内消费字节不一致

`command_refresh_source_control_recovery_gate()` 在取得锁前调用 `verify_source_control_gate_lock_refresh()` 并得到解析后的 refresh verdict 与 replacement verdict。取得锁之后，`lock_refresh_source_control_gate()` 又直接按路径读取 replacement verdict 与 frozen manifest 来生成 replacement gate 的 `audit_report_sha256` 和 `frozen_hashes_sha256`；journal context 也再次按路径读取 refresh verdict、replacement verdict、frozen manifest 和授权记录。命令没有要求这些后续读取的 SHA 仍等于锁前 verifier 已验证并由 refresh verdict 授权的 SHA。

临时复现让专用 verifier 先返回一份 replacement verdict，并记录其已授权 SHA `e411cedeaaad969401247e88c6557135fb3b8e0b486421591849984a4fe12589`；在 verifier 返回后、runtime 收据阶段，把文件改为仍满足 source-recovery schema/decision/PASS 0/0 的另一组有效 JSON 字节，SHA 为 `e382647d944ef8a75fac46d4d10a904e6822bc119efd9b68af4960ae272f92fb`。命令返回 0，journal 达到 `SUCCESS_COMMITTED`，journal context 与 replacement gate 的 audit SHA 均采用改变后的 `e382...92fb`，而不是 verifier 已绑定的 `e411...2589`。

这不是格式解析问题；改变后的 JSON 仍满足现有 source gate verifier 对 structured verdict 的全部必需字段。其结果是 refresh verdict 所授权的控制材料与最终 gate/journal 所记录的控制材料可以不属于同一次验证快照，破坏了审计授权、journal context 和 replacement gate 之间的事务一致性。

最小关闭条件：refresh verifier 应返回或固定每个已验证材料的精确 bytes/SHA；锁内构造 replacement gate 和 journal context 必须只使用这些已验证值，不得用后续路径读取结果替换它们。在第一次正式持久化前，应重新读取并要求 refresh verdict、replacement verdict、报告、frozen manifest 和授权记录的实际 SHA 与已验证快照完全一致；此后的实际 source verifier应继续用 gate 中的固定 SHA拒绝任何漂移。测试至少应分别覆盖 refresh verdict、replacement verdict、frozen成员/manifest、报告和授权记录在 verifier 返回后、锁取得前及锁内首写前变化，且要求零正式状态写入。

## M9-SPR-R30-B02：replacement receipt 与 source verifier 之间的路径一致性未闭合

replacement gate 创建后，命令先调用 `strict_root_private_receipt()` 得到 root:root、0600、nlink 1 收据，再调用 `verify_source_control_recovery_gate_and_hashes()`。后者目前用 `Path.is_file()`、`read_text()` 和 `read_bytes()` 按路径读取 gate，并不返回或验证同一 fd 的 root 私有 receipt。命令随后直接把先前 receipt 写入 `REPLACEMENT_CREATED` 和 `SUCCESS_COMMITTED`，没有在 source verifier 返回后重新确认 path 仍对应同一 device/inode/metadata。

临时复现精确放在严格 receipt 已取得、source verifier开始读取的边界，并保持 replacement payload 不变：

```text
symlink path replacement: rc=0, journal=SUCCESS_COMMITTED, active is_symlink=True
hardlink added:           rc=0, journal=SUCCESS_COMMITTED, active nlink=2
```

两种情况下 verifier 返回的 JSON payload 都与确定性 replacement payload 相等，因而现有 payload 相等检查没有停止命令。journal 中的 replacement receipt 却已不再描述提交时的 active path。下一次 terminal replay 会由严格 receipt 发现漂移，但首次调用已经输出成功并持久化终态，不能把后续可检测性视为首次提交的一致性证明。

最小关闭条件：source-control recovery gate verifier 对正式 root gate 应使用单一 fd 的 `O_NOFOLLOW|O_CLOEXEC` 严格读取，同时验证 root:root、0600、nlink 1 及 read 前后 fd/path 的 device、inode、metadata、size 与 bytes；它应返回实际 receipt 和解析 payload。refresh 命令必须要求该 verifier receipt 与刚创建并拟写入 journal 的 receipt 完全相等，且在写入 `REPLACEMENT_CREATED` 和 `SUCCESS_COMMITTED` 前保持该绑定。新增命令级测试应在 receipt 后、verifier读取期间分别进行 symlink path replacement和 hardlink增加，要求停止且不得写入成功终态；终态 replay 的相同负例也应继续成立。

## 判定与后续范围

本轮两个问题均直接影响一次性 refresh 首次成功的可证明性，故均计为 BLOCKING。正式 78/78 证明的是已列举路径和常规崩溃续提，不包含两项主动复现，不能据此生成零问题 PASS verdict。

关闭 `M9-SPR-R30-B01` 和 `M9-SPR-R30-B02` 后，应冻结新的 budget、tests、source manifest 和 cleanup manifest，补齐上述负例，重新运行全套，并再次独立核对正式 active gate、old-invalid retired、disposition journal、锁、五项 runtime、refresh 对象缺席和 cache=0。只有新的独立报告给出 `BLOCKING=0`、`NON_BLOCKING=0`，主 agent 才可以创建两份 refresh verdict 并执行一次 refresh；refresh 完成后仍须独立执行事实审计，之后才能重新判断既有单次 recovery 授权是否可消费。

最终计数：`BLOCKING=2`，`NON_BLOCKING=0`。本轮未创建 verdict，未执行 refresh、recovery、disposition replay 或 `source_prepare`，未修改任何被审对象或正式运行时。
