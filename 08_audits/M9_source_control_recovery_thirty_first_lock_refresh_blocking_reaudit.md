# M9 source-control recovery 第三十一次 lock-refresh 定点复核

## 结论

本轮只读软件质量定点复核结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。R30-B01 与 R30-B02 均得到实质性修复，但尚未达到完整关闭条件。

R30-B01 的锁后吸收问题已在 command 层消除：replacement gate 与 journal context 只使用 `verified_bindings`，不再在锁内重新计算并吸收新的材料 SHA。但实际 verifier 对 replacement verdict 仍执行两次独立 `read_bytes()`；第一次字节用于与 refresh verdict 比较，第二次字节用于解析并生成 `verified_bindings`。两次读取不一致时，第二份未由 refresh verdict 授权的 SHA 仍可被返回为“已验证绑定”。

R30-B02 的原始 source-verifier 期间路径变化已由后验单 FD strict JSON 检查阻止；然而，该检查之后、写入 `REPLACEMENT_CREATED` 与 `SUCCESS_COMMITTED` 之间仍没有再次绑定 active gate。主动复现在持久化 `REPLACEMENT_CREATED` 时改变 active path，首次命令仍返回 0 并提交 `SUCCESS_COMMITTED`，下一次 replay 才发现不一致。

因此当前不允许主 agent 生成两份 refresh verdict，也不允许执行一次 refresh。既有单次 source-control recovery 用户授权不得在本轮结论下消费。本报告不授权 refresh、recovery 或 `source_prepare`。

## 冻结对象、闭集与正式现场

独立复算的四项 SHA-256 与指定值一致：

- `06_reproduction/scripts/m9_budget.py`：`9568be90c7f2286ad4cecceb99ddc85df73d6fc80aa2bead21144b4d814b2fff`
- `06_reproduction/tests/test_m9_overlap_controls.py`：`794a6f2e5acebba3a6a5fed57943f769583af1cf2dae27a21c06a19534b39f81`
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：`a28e4b6edfd04f4754422262f2585f85c900374c2a20cb938b92188bc02542b3`
- `06_reproduction/manifests/m9_source_control_test_cleanup_frozen_hashes.json`：`1494bc65f388f4d8b4089f1694ce14fe475041f3f705c927360e4dc502a81127`

source manifest 的 18 个成员逐项复算为 `18/18`，cleanup manifest 的 4 个成员为 `4/4`，无缺失或哈希不符。`06_reproduction` 内 `.pyc`、`.pyo` 和 `__pycache__` 合计为 0。

正式现场在全部临时复现和测试前后保持：

- active pre-lock gate：SHA-256 `5553de21184082b3ace505f4981f20c3116df7389805f2070ebf7e8b8dad5936`，1723 bytes，root:root、0600、nlink 1、inode 139158；
- old-invalid retired gate：SHA-256 `6bdd2fdbff6df6a7a8cfa1ba3cda038ca7cfe96b3b5dfb48905ef0f5151f5821`，1711 bytes，root:root、0600、nlink 1、inode 132095；
- disposition journal：SHA-256 `e97dc9b00a798f5a26807e5af18c78c2779be4ab144adeaa39f5be4338dc8ece`，3748 bytes，root:root、0600、nlink 1；
- budget lock：空文件 SHA `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`，UID/GID 1000:1000、0644、nlink 1、inode 50700；
- state、workflow、failed transaction、ledger、stale capability 分别保持 `1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`、`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`、`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`、`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`、`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`。

refresh 专用两份 verdict、pre-lock retired gate、root refresh journal、source recovery transaction 和 parent 均缺席。没有创建或执行任何正式 gate、refresh、recovery 或 `source_prepare`。

## 已确认的修复与绑定机制

`verify_source_control_gate_lock_refresh()` 现在返回 refresh verdict、replacement verdict 与 `verified_bindings`。command 在锁内构造 replacement gate 时显式传入 `verified_bindings["replacement_verdict_sha256"]` 和 `verified_bindings["frozen_hashes_sha256"]`；journal context 的 refresh verdict、replacement verdict、frozen 与 authorization SHA 也全部直接来自同一 bindings 字典。由此，R30 中 command 锁内按路径重读并把变化后 SHA 吸收到 target gate/context 的原路径已经移除。

在 replacement 创建或续提后，command 调用实际 `verify_source_control_recovery_gate_and_hashes()`，要求解析 payload 等于确定性 replacement gate；随后再用 `strict_root_private_json()` 对 active path 执行单 FD `O_NOFOLLOW|O_CLOEXEC` 读取，并同时要求后验 receipt 等于前置 receipt、后验解析 payload 等于确定性 replacement gate。终态 replay 也执行 source verifier 与同样的后验 receipt+payload 检查。

主动重放 R30-B02 的原始窗口时，在 source verifier 期间分别把 active path 换为同 payload symlink或为同 inode 增加 hardlink。两项均停止，journal 保持 `OLD_GATE_RETIRED`，未进入 `SUCCESS_COMMITTED`：symlink 由 `O_NOFOLLOW` 拒绝，hardlink 由 nlink 1 条件拒绝。因此 R30-B02 原始复现已关闭。

新增 post-verifier material drift 回归也证明：专用 verifier 返回后改变 replacement verdict，target gate 仍保留 bindings 中的旧 SHA，实际 source verifier因 audit report hash 不一致停止，journal 不进入 SUCCESS。该结果确认 command 层不再吸收 verifier 返回后的新 SHA。

## 四状态、六窗口与终态 replay

本轮除正式 80 项外，独立逐状态重放六个持久化中断窗口。每个第一次停止现场与第二次续提结果如下：

| 中断点 | 第一次持久 journal state | active / pre-lock retired | 第二次调用 | 终态 replay |
|---|---|---|---|---|
| `prepared` | `PREPARED` | present / absent | `SUCCESS_COMMITTED` | 零写入 |
| `rename` | `PREPARED` | absent / present | `SUCCESS_COMMITTED` | 零写入 |
| `retired_journal` | `OLD_GATE_RETIRED` | absent / present | `SUCCESS_COMMITTED` | 零写入 |
| `replacement` | `OLD_GATE_RETIRED` | present / present | `SUCCESS_COMMITTED` | 零写入 |
| `replacement_journal` | `REPLACEMENT_CREATED` | present / present | `SUCCESS_COMMITTED` | 零写入 |
| `terminal` | `SUCCESS_COMMITTED` | present / present | `SUCCESS_COMMITTED` | 零写入 |

每个第二次调用均返回 0；其后再次调用时，active、pre-lock retired 和 journal 三对象逐字节不变。常规四状态续提、旧 gate 保真、replacement 普通文件 receipt 与解析 payload 一致性在这些路径上成立。

冻结 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9` 以 `-I -S -B` 运行正式测试，结果为 `Ran 80 tests in 16.266s`、`OK`、退出码 0。80 项包含新增 post-verifier material drift 和 source-verifier 期间 symlink/hardlink 负例，但没有覆盖以下两个主动复现。

## M9-SPR-R30-B01：仍未关闭——replacement verifier 内部双读取

当前 verifier 先在 replacement binding 条件中调用 `replacement_path.read_bytes()` 并把该次 SHA 与 refresh verdict 中的 `replacement_verdict_sha256` 比较；条件通过后，又调用一次 `replacement_path.read_bytes()` 赋给 `replacement_bytes`，再从第二次 payload 解析 replacement verdict，并将第二次 payload 的 SHA写入 `verified_bindings`。第二次 SHA没有再次与 refresh verdict 所授权的 SHA比较。

本轮使用实际 verifier 和完整临时 verdict/report/frozen/auth/control 闭集，使 replacement path 的第一次读取返回原 bytes，第二次读取返回仍满足 source-recovery schema、decision、PASS 0/0但带有不同 provenance 字段的另一组 bytes。结果为：

```text
replacement read count = 2
refresh-verdict-authorized SHA = b52230fd1fd55132b5606c685506c9df5d875fb54ab61d062856c36541391b3d
returned verified_bindings SHA = 6ff9acde01ce07937251647822d11725e8bc1a1b542330d5b2df9ce2da8703ae
returned replacement payload = second read payload
verifier result = accepted
```

command 之后只消费 bindings 的改动不能修复 bindings 自身来自不同读取的问题。该结果仍允许 target gate 和 journal 使用一组未由 refresh verdict 的 replacement SHA字段授权的字节，故 R30-B01 未关闭。

最小关闭条件：对 replacement verdict 只执行一次 `read_bytes()`，先保存为 `replacement_bytes`，再用同一 bytes 同时完成 SHA 比较、UTF-8/JSON 解析和 `verified_bindings` 生成。新增测试应使 replacement path 的连续读取返回不同 payload，并断言 verifier只读取一次，或在任何不一致时停止；测试还应断言返回 binding 严格等于 refresh verdict 的 `replacement_verdict_sha256`。

## M9-SPR-R30-B02：仍未关闭——后验检查与 SUCCESS 提交之间缺少再次确认

当前非终态路径在 source verifier 后执行一次严格后验读取，随后依次持久化 `REPLACEMENT_CREATED` 和 `SUCCESS_COMMITTED`，两次 journal 写入之间没有再次检查 active gate。因而，原 source-verifier 期间窗口虽然关闭，但后验检查完成之后发生的相邻路径或链接元数据变化仍可被首次成功提交覆盖。

本轮在严格后验检查已经通过后，于 `atomic_root_private_json()` 完成 `REPLACEMENT_CREATED` 持久化时分别注入同 payload symlink path replacement 和 hardlink 增加。两项结果为：

```text
symlink: rc=0, journal=SUCCESS_COMMITTED, active is_symlink=True
hardlink: rc=0, journal=SUCCESS_COMMITTED, active nlink=2
```

两项下一次 terminal replay 都能由严格 root-private 检查拒绝，但首次调用已经输出 `source_control_gate_lock_refreshed` 并持久化 SUCCESS。后续可检测性不能证明首次 SUCCESS 时 journal receipt 与 active path 一致，因此 R30-B02 仍未完整关闭。

最小关闭条件：在 `REPLACEMENT_CREATED` 已持久化之后、设置和写入 `SUCCESS_COMMITTED` 之前，再次执行实际 source gate verifier以及单 FD strict JSON读取，并要求 receipt 与 journal `replacement_gate`、payload 与确定性 replacement gate完全相等。新增命令级负例应在 `REPLACEMENT_CREATED` 持久化时分别注入 symlink path replacement和hardlink增加，要求不写 SUCCESS、不返回 0；终态 replay 的相同异常仍应拒绝。若实现选择其他提交协议，也必须保证 SUCCESS 写入所依据的 receipt/payload 是该提交阶段重新确认的同一绑定。

## 最终判定

R30-B01 与 R30-B02 均保留为 BLOCKING。80/80 与常规六窗口证明状态机的既有恢复路径成立，但没有覆盖实际 verifier 内部双读取或后验检查后的相邻终态窗口，不能据此生成 refresh PASS verdict。

只有两项最小关闭条件落实、冻结 SHA更新、相应负例进入正式测试并由新的独立复核给出 `BLOCKING=0`、`NON_BLOCKING=0` 后，才允许主 agent 生成两份 refresh verdict并执行一次 refresh。refresh 执行后仍需独立事实审计，之后才能判断既有单次 recovery 用户授权是否可以消费。

最终计数：`BLOCKING=2`，`NON_BLOCKING=0`。本轮只新增本 Markdown 报告，未创建 verdict，未执行正式 refresh、recovery 或 `source_prepare`，未修改被审对象或正式运行时。
