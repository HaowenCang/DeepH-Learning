# M9 source-control gate disposition 第二十六次阻塞复核

## 结论

本轮独立只读定点复核结论为 **FAIL**：`BLOCKING=1`，`NON_BLOCKING=0`。当前实现能够拒绝命令调用开始前已经存在的 symlink 或 hardlink journal，新增冻结测试也正确断言这些预置异常下 active、retired、journal 零写入。然而 `strict_root_private_receipt(journal)` 与随后 `journal.read_text()` 是两次独立路径访问；receipt 成功后、JSON 读取前发生的 path/inode/link 变化仍会被接受。因此 `M9-SPR-R25-B01` 保持 OPEN。

主 agent 当前不得创建 disposition PASS verdict 或 replacement source-recovery PASS verdict，也不得执行 disposition、recovery 或 `source_prepare`。

## 冻结快照与正式现场

独立复算的四项 SHA-256 与指定值完全一致：

- `06_reproduction/scripts/m9_budget.py`：`554a4ce0213241f006b2b993f588dac486fd2fcba7cc2bfc7497feaf4fa5fa68`
- `06_reproduction/tests/test_m9_overlap_controls.py`：`3d7777ace9d3af71cedcfdb066e7d3dc3fc7773445c2ae720dd82097734754d2`
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：`3bb59c6e1ff22d75474a6af80b542ea0c545034d76caebf335bf3fe72c77dc3c`
- `06_reproduction/manifests/m9_source_control_test_cleanup_frozen_hashes.json`：`532eac3326e8dbbb1471ce22d8b5bcdfc85039115c302f3217550a3937fba09d`

source manifest 独立复算为 `18/18`，cleanup manifest 为 `4/4`，mismatch 均为 0。冻结 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9` 以 `-I -S -B` 执行完整测试，结果为 `Ran 73 tests in 14.532s`、`OK`、退出码 0。控制脚本和测试目录中的 `.pyc`、`.pyo`、`__pycache__` 合计为 0。

正式旧无效 gate 保持 SHA-256 `6bdd2fdbff6df6a7a8cfa1ba3cda038ca7cfe96b3b5dfb48905ef0f5151f5821`、1711 bytes、root:root、0600、nlink 1。正式 disposition journal、`.closed-set-invalid.retired.json`、source recovery transaction 和 parent snapshot 均缺席。

五项正式 runtime SHA-256 在完整测试和全部主动临时复现前后保持：

- state：`1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`
- workflow：`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`
- failed transaction：`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`
- ledger：`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`
- stale capability：`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`

cleanup retired 对象、retirement receipt、cleanup journal、cleanup gate/root snapshot、security migration 分别保持 SHA-256 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`、`74b24867d06a437f0e693c8edd231ab4bc31782b8978abfff77b01658567fd49`、`1e0729d72bb7e45e773a61d9aff6228061a5b000cd218c23e5263153f2425d8d`、`12cec1f13eec81c110b8a7d66aecaf4e1786c0821c82a702885b9e74cfeb57b2`、`60fef9c099bfc345973bb9ac074f084f48e5e542508681fa4d55ceb099ba5c94`。六项 source/build 产品继续缺席。

## 当前修复已证明的范围

`command_dispose_invalid_source_control_gate()` 在 `journal_present` 为真时，现于 JSON 解析前调用：

```python
strict_root_private_receipt(SOURCE_CONTROL_GATE_DISPOSITION_JOURNAL)
```

该 helper 对调用时已经可见的 symlink、非普通文件、非 root:root、mode 非 0600 或 nlink 非 1 journal 返回停止。新增命令级测试先完成正常终态，再分别把固定 journal path 改为 symlink 或给它增加第二个 hardlink；两项均要求 `SystemExit`，并逐字节核对 active、retired、journal 未变化。该测试本身有效，且在 73 项套件中通过。

相邻既有条件也保持闭合：未知 journal state、`old_gate` 完整 receipt 漂移、runtime 漂移、dangling recovery transaction/parent、frozen 18 成员漂移、控制目录闭集漂移及 replacement verifier payload 漂移均会停止。六个 disposition 中断窗口 `prepared`、`rename`、`retired_journal`、`replacement`、`replacement_journal`、`terminal` 仍可续提到合法终态；未发生 receipt/path 漂移时的 terminal replay 为逐字节零写入。固定 `.tmp` 和 root 私有原子 writer 的部分内容、symlink、hardlink、owner/mode、fsync、replace、target recheck 与 directory fsync 测试继续通过。

## M9-SPR-R25-B01：OPEN

当前已有 journal 的读取顺序为：

```python
strict_root_private_receipt(journal_path)
journal = json.loads(journal_path.read_text(...))
```

`strict_root_private_receipt()` 内部本身也是 path 状态检查、`lstat()` 和 `read_bytes()` 的组合；返回后没有保留已验证文件描述符。调用方随后重新按 path 打开 journal，也没有把读取 bytes 的 device/inode receipt 与先前 receipt 比较，或在读取后确认固定 path 仍指向同一 inode。

独立 root 临时终态复现通过定点 wrapper 先让真实 `strict_root_private_receipt()` 完整成功，再在它返回后、`read_text()` 执行前分别进行以下变化：

- 用内容完全相同的 sibling 文件替换固定 path，并使固定 path 成为指向 sibling 的 symlink；
- 保持固定 journal path 不变，但为该 inode 增加第二个 hardlink，使 nlink 从 1 变为 2。

实际命令结果为：

```text
SYMLINK_AFTER_RECEIPT ACCEPTED 0 IS_SYMLINK True NLINK 1
HARDLINK_AFTER_RECEIPT ACCEPTED 0 IS_SYMLINK False NLINK 2
```

两次调用都读取了相同 JSON bytes，active、retired 和 journal 内容也保持不变，但命令返回成功时 journal 的对象身份或 link receipt 已不再满足 root 私有合同。由此，预置 symlink/hardlink 测试关闭的是检查前状态，尚未关闭 receipt 与读取之间的同一对象一致性。

### 最小关闭条件

- 通过 `O_RDONLY | O_NOFOLLOW` 单次打开 journal；在同一 fd 上 `fstat()` 验证普通文件、root:root、0600、nlink 1，并从同一 fd 读取全部 bytes 后解析 JSON。
- receipt 应包含至少 device、inode、UID/GID、mode、nlink、size 和 bytes SHA；读取结束后再次 `fstat()`，要求同一 fd receipt 未改变。
- 关闭 fd 前后应以不跟随链接的 path receipt 重新核对固定 journal path 仍指向同一 device/inode，仍为 root:root、0600、nlink 1。任何变化均在 active/retired/journal 写入前停止。
- 冻结命令级测试除预置 symlink/hardlink 外，还应在“初次 fd receipt 后、bytes 读取期间、读取完成后 path recheck 前”分别注入 path replacement、symlink 和 hardlink 变化，并断言 active、retired、journal 零写入。

## 放行判断

本轮为 `BLOCKING=1`、`NON_BLOCKING=0`、FAIL。主 agent 不允许基于当前快照创建 disposition verdict 或 replacement verdict，也不允许执行一次 disposition。修复 `M9-SPR-R25-B01` 后需要重新冻结 controller、测试和两个 manifest，并再次进行独立定点复核；只有零问题 PASS 才能进入 verdict 创建与一次性 disposition 阶段。

本轮仅新增本报告；未创建任何可消费 verdict，未修改被审对象、旧 gate、正式 runtime 或 cleanup 证据，未执行 disposition、recovery 或 `source_prepare`。
