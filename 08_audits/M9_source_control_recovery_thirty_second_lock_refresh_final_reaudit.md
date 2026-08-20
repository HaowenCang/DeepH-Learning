# M9 source-control recovery 第三十二次 lock-refresh 最终定点复核

## 结论

本轮独立只读质量定点复核结论为 **PASS**：`BLOCKING=0`，`NON_BLOCKING=0`。`M9-SPR-R30-B01` 与 `M9-SPR-R30-B02` 均已关闭。

replacement verdict 在专用 verifier 中现在只读取一次，校验 SHA、解析 JSON 和生成 `verified_bindings` 均复用同一 payload；command 在锁内只消费该绑定。replacement gate 在 source verifier 返回后、`REPLACEMENT_CREATED` 持久化后以及 `SUCCESS_COMMITTED` 持久化后均受到单 FD strict receipt+payload 检查。若 SUCCESS 写入期间发生不一致，journal 转为 `FAILED_COMMITTED`，命令抛出并且不输出成功。

主 agent 可以基于本报告生成 lock-refresh 专用 verdict 与 source-recovery replacement verdict，并在两份 JSON 的实际路径、SHA、当前 frozen snapshot、授权记录、旧 active gate和完整 post-disposition runtime 均通过实际 verifier 后，以 root 和冻结 Python执行一次 `overlap-refresh-source-control-recovery-gate`。本 PASS 不授权 source-control recovery 或 `source_prepare`；refresh 执行后必须停止并进行独立事实审计。

## 冻结对象与闭集

独立复算的四项 SHA-256 与指定值一致：

- `06_reproduction/scripts/m9_budget.py`：`8f2cbb007045cf888e41893f8b0dc5d44f3fc88c0078590f24776724c9ede3a2`
- `06_reproduction/tests/test_m9_overlap_controls.py`：`432eb10457a88ad98fb94157d7c0fa376240a8e62404440115d7ae3b5d657f10`
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：`af86278da0cf6d68330f065dd8fbe50963b04b5c9c5b198f4cce5d2e0442e21d`
- `06_reproduction/manifests/m9_source_control_test_cleanup_frozen_hashes.json`：`6e0d799bf5ce60cd9ac18a8e384a5e71972e8f3a56d9c64665b9e71056b58495`

source manifest 的 18 个成员逐项复算为 `18/18`，cleanup manifest 的 4 个成员为 `4/4`，无缺失或哈希不符。`06_reproduction` 内 `.pyc`、`.pyo` 与 `__pycache__` 合计为 0。

冻结 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9` 以 `-I -S -B` 运行正式测试，结果为 `Ran 82 tests in 16.642s`、`OK`、退出码 0。新增回归包括实际 verifier replacement 读取次数严格为 1，以及 `REPLACEMENT_CREATED`/`SUCCESS_COMMITTED` 两个持久化边界与 symlink/hardlink 两种变化的四项组合。

## M9-SPR-R30-B01：CLOSED

`verify_source_control_gate_lock_refresh()` 先以单次 `read_bytes()` 得到 `replacement_bytes`。同一 bytes 随后用于：

- 与 refresh verdict 中的 `replacement_verdict_sha256` 比较；
- UTF-8 解码和 JSON object 解析；
- 验证 source-recovery schema、D-017 decision 与 PASS 0/0；
- 生成返回的 `verified_bindings["replacement_verdict_sha256"]`。

本轮以实际 verifier、完整临时 report/verdict/frozen/auth/control 闭集和 `Path.read_bytes` 计数器重放 R31 双读取条件。实际 replacement 读取次数为 1，返回 binding 与 refresh verdict 所授权 SHA 完全相等。因此不再存在第一次 SHA 校验和第二次解析来自不同 payload 的路径。

command 构造 replacement gate 时显式传入 bindings 中的 replacement verdict SHA 与 frozen SHA；journal context 的 refresh verdict、replacement verdict、frozen 和 authorization SHA 也均直接来自同一 bindings 字典。专用 verifier 返回后改变 replacement verdict 的正式负例进一步证明：target gate 保留原 binding，实际 source verifier因 report SHA不一致停止，变化后的 SHA不会被 target gate或journal吸收。

由此，验证 bytes、解析 payload、target gate和journal context属于同一次确认快照，满足 R30-B01 与 R31遗留双读取的最小关闭条件。

## M9-SPR-R30-B02：CLOSED

replacement gate创建或恢复后，命令执行以下一致性序列：

1. 取得前置 root-private receipt；
2. 调用实际 `verify_source_control_recovery_gate_and_hashes()` 并要求 payload 等于确定性 replacement gate；
3. 以单 FD `strict_root_private_json()` 后验读取 active path，要求 receipt 等于前置 receipt且解析 payload 等于确定性 gate；
4. 持久化 `REPLACEMENT_CREATED`；
5. 再次执行单 FD strict receipt+payload检查；
6. 持久化 `SUCCESS_COMMITTED`；
7. 第三次执行单 FD strict receipt+payload检查；若不一致，将 journal持久化为 `FAILED_COMMITTED`、记录 `replacement_changed_during_terminal_commit` 和失败时间，并重新抛出错误。

单 FD严格读取继续要求普通文件、root:root、0600、nlink 1，并在同一 fd上比较读取前后与最终 path 的 device、inode、mode、UID/GID、nlink、size以及payload长度。

本轮主动重放的结果为：

| 注入边界 | path变化 | 命令结果 | journal结果 |
|---|---|---|---|
| source verifier期间 | symlink replacement | 抛出，未成功 | `OLD_GATE_RETIRED` |
| source verifier期间 | hardlink增加 | 抛出，未成功 | `OLD_GATE_RETIRED` |
| `REPLACEMENT_CREATED` 写入时 | symlink replacement | 抛出，未成功 | `REPLACEMENT_CREATED` |
| `REPLACEMENT_CREATED` 写入时 | hardlink增加 | 抛出，未成功 | `REPLACEMENT_CREATED` |
| `SUCCESS_COMMITTED` 写入时 | symlink replacement | 抛出，未成功 | `FAILED_COMMITTED` |
| `SUCCESS_COMMITTED` 写入时 | hardlink增加 | 抛出，未成功 | `FAILED_COMMITTED` |

`REPLACEMENT_CREATED` 异常现场再次调用时，由异常 active receipt零写入停止。`FAILED_COMMITTED` 再次调用时，由 journal终态零写入停止，不能通过普通续提转为 SUCCESS。两类失败分支均未输出 `source_control_gate_lock_refreshed`。

因此，原 source-verifier窗口、R31 后验检查至 SUCCESS 的相邻窗口，以及 SUCCESS 写入期间窗口均在首次调用内形成可证明的非成功结果；R30-B02 已关闭。

## 六个持久化窗口与状态续提

独立逐状态重放六个正常崩溃窗口，第一次停止现场与续提结果如下：

| 中断点 | 第一次持久 journal state | active / pre-lock retired | 第二次调用 | 正常终态 replay |
|---|---|---|---|---|
| `prepared` | `PREPARED` | present / absent | `SUCCESS_COMMITTED` | 零写入 |
| `rename` | `PREPARED` | absent / present | `SUCCESS_COMMITTED` | 零写入 |
| `retired_journal` | `OLD_GATE_RETIRED` | absent / present | `SUCCESS_COMMITTED` | 零写入 |
| `replacement` | `OLD_GATE_RETIRED` | present / present | `SUCCESS_COMMITTED` | 零写入 |
| `replacement_journal` | `REPLACEMENT_CREATED` | present / present | `SUCCESS_COMMITTED` | 零写入 |
| `terminal` | `SUCCESS_COMMITTED` | present / present | `SUCCESS_COMMITTED` | 零写入 |

每个第二次调用均返回 0；随后第三次调用中 active、pre-lock retired和journal三对象逐字节不变。`PREPARED`、`OLD_GATE_RETIRED`、`REPLACEMENT_CREATED` 与合法 `SUCCESS_COMMITTED` 的正常续提语义保持一致；`FAILED_COMMITTED` 是明确的非成功终态，不进入正常续提集合。

## 真实锁语义

正式 manifests 目录保持 root:GID1000、1770，`budget.lock` 保持 UID/GID1000:1000、0644、nlink 1、0 bytes、inode 50700。以 root 和冻结 Python对同一锁执行只读打开/加锁复现：`a+` 得到 `PermissionError errno=13`，`r+` 成功取得和释放 `LOCK_EX|LOCK_NB`。锁 inode 与 SHA 在操作前后不变，SHA为 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。

refresh 与 source-control recovery 两个入口均使用 `r+` 打开既存锁；命令级测试分别确认观测到的唯一模式为 `r+`。锁缺席时不会静默创建替代锁。

## 正式现场前后不变性

全部读取、临时复现和测试前后，正式现场保持：

- active pre-lock gate：SHA-256 `5553de21184082b3ace505f4981f20c3116df7389805f2070ebf7e8b8dad5936`，1723 bytes，root:root、0600、nlink 1、inode 139158；
- old-invalid retired gate：SHA-256 `6bdd2fdbff6df6a7a8cfa1ba3cda038ca7cfe96b3b5dfb48905ef0f5151f5821`，1711 bytes，root:root、0600、nlink 1、inode 132095；
- disposition journal：SHA-256 `e97dc9b00a798f5a26807e5af18c78c2779be4ab144adeaa39f5be4338dc8ece`，3748 bytes、root:root、0600、nlink 1；
- state：`1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`；
- workflow：`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`；
- failed transaction：`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`；
- ledger：`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`；
- stale capability：`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`。

refresh 专用两份 verdict、pre-lock retired gate、root refresh journal、source recovery transaction和parent均缺席。

## 一次 refresh 的精确放行边界

replacement source-recovery verdict 应写入 `08_audits/M9_source_control_recovery_lock_replacement_final_verdict.json`，保持 schema `m9-source-control-recovery-audit-verdict-v1`、decision `D-017-source-control-recovery-v1`、scope `ONE_TIME_SOURCE_CONTROL_RECOVERY`、PASS 0/0，并绑定本报告路径/SHA与当前 source frozen manifest SHA `af86278da0cf6d68330f065dd8fbe50963b04b5c9c5b198f4cce5d2e0442e21d`。

lock-refresh verdict 应在 replacement verdict最终字节确定后写入 `08_audits/M9_source_control_gate_lock_refresh_final_verdict.json`，保持 schema `m9-source-control-gate-lock-refresh-audit-verdict-v1`、decision `D-017-source-control-gate-lock-refresh-v1`、scope `RETIRE_PRE_LOCK_MODE_GATE_AND_CREATE_REPLACEMENT_ONLY`、PASS 0/0。它必须绑定本报告路径/SHA、replacement verdict路径/SHA、旧 active gate SHA `5553de21184082b3ace505f4981f20c3116df7389805f2070ebf7e8b8dad5936` 与 1723 bytes、当前 frozen SHA、授权记录 SHA `6b3e7a714a0adc8f00d56a45b5cedba99cbf941287109666cb1aac74bcf72da1`，以及 `source_control_lock_refresh_runtime_receipt()` 返回的完整字典。

两份 JSON 应严格 UTF-8可解析且无异常控制字符。只有实际 `verify_source_control_gate_lock_refresh()` 返回的两份 payload和四项 bindings与文件精确相等、正式 runtime与对象缺席条件仍无漂移时，主 agent才可执行一次 refresh。执行后授权立即终止并进入独立事实审计；不得在同一授权下继续 recovery或 `source_prepare`。

最终计数：`BLOCKING=0`，`NON_BLOCKING=0`。本轮只新增本报告，未创建 verdict，未执行正式 refresh、recovery或 `source_prepare`，未修改被审对象或正式运行时。
