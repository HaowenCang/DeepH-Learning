# M9 source-control gate disposition 第二十五次阻塞复核

## 结论

本轮独立只读复核结论为 **FAIL**：`BLOCKING=1`，`NON_BLOCKING=0`。第二十四次报告的三个问题 `M9-SPR-R23-B01`、`M9-SPR-R24-B01`、`M9-SPR-R24-B02` 均已按其固定失败复现关闭；冻结测试 `72/72` 通过，正式现场保持零写入。但主动终态复现发现一个新的 root 私有 journal receipt 缺口 `M9-SPR-R25-B01`：已存在 journal 的内容会被读取和核对，但 journal 路径自身没有经过 non-link、root:root、0600、nlink 1 的 receipt 验证，因此 symlink 和 hardlink journal 可以被当作有效终态证据。

本轮不得执行 disposition、recovery 或 `source_prepare`，不得修改旧 gate，也不得签发 disposition PASS verdict 或 replacement source-recovery PASS verdict。

## 冻结对象与正式测试

独立复算的四项 SHA-256 与指定值完全一致：

- `06_reproduction/scripts/m9_budget.py`：`e01d9dd81364dcfbaa82c2842234d3ebb9cc7c7af42ec6dbded7205046bd43ee`
- `06_reproduction/tests/test_m9_overlap_controls.py`：`f0bcf2fa3ac33c9ed97a55c387b712151e794fd8cd3fedeb36e2800f8f5fb0fc`
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：`cda3bb815098385c767f09f2aa440c283178cbad8420856e36d35dec112ce7c4`
- `06_reproduction/manifests/m9_source_control_test_cleanup_frozen_hashes.json`：`52ba6f48c813ef9593eae5b1b0dfc21df3ba52167c24574e08729928c94e3abd`

source manifest 独立复算为 `18/18`，cleanup manifest 为 `4/4`。冻结 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9` 以 `-I -S -B` 执行完整测试，结果为 `Ran 72 tests in 15.770s`、`OK`、退出码 0。控制脚本和测试目录中的 `.pyc`、`.pyo`、`__pycache__` 合计为 0。

正式旧 gate 仍为 SHA-256 `6bdd2fdbff6df6a7a8cfa1ba3cda038ca7cfe96b3b5dfb48905ef0f5151f5821`、1711 bytes、root:root、0600、nlink 1。正式 disposition journal、`.closed-set-invalid.retired.json`、source recovery transaction 和 parent snapshot 均缺席。

五项正式 runtime SHA-256 在测试和全部临时复现前后保持：

- state：`1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`
- workflow：`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`
- failed transaction：`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`
- ledger：`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`
- stale capability：`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`

cleanup retired 对象、retirement receipt、cleanup journal、cleanup gate/root snapshot、security migration 分别保持 SHA-256 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`、`74b24867d06a437f0e693c8edd231ab4bc31782b8978abfff77b01658567fd49`、`1e0729d72bb7e45e773a61d9aff6228061a5b000cd218c23e5263153f2425d8d`、`12cec1f13eec81c110b8a7d66aecaf4e1786c0821c82a702885b9e74cfeb57b2`、`60fef9c099bfc345973bb9ac074f084f48e5e542508681fa4d55ceb099ba5c94`。六项 source/build 产品继续缺席。

## 第二十四次三个问题的关闭证据

### M9-SPR-R23-B01：CLOSED

已有 disposition journal 的 state 现在严格限定为 PREPARED、INVALID_GATE_RETIRED、REPLACEMENT_CREATED、SUCCESS_COMMITTED。每次重入均要求 `old_gate` 是完整字典，并精确绑定 active gate 固定 path、SHA、1711 bytes、UID/GID 0、mode 0600、nlink 1。

冻结测试在 PREPARED 后分别改变 state 和 `old_gate.sha256`，均要求零写入停止。独立复现得到：

```text
STATE REJECTED source-control gate disposition journal state mismatch
OLD_GATE REJECTED source-control gate disposition old receipt drift
```

未知 state 和历史 old-gate receipt 漂移不再被续提或改写，前一报告的两个固定失败事实均已关闭。

### M9-SPR-R24-B01：CLOSED

disposition verifier 现在解析当前 source frozen manifest，要求文件集合与 `SOURCE_RECOVERY_CONTROL_FILES` 的 18 项 resolved path 精确相等，逐项拒绝 symlink、缺失或 SHA 不匹配成员，并再次执行控制目录闭集检查。冻结成员内容改变而 manifest 字节不变时，测试得到 `gate disposition frozen member mismatch`。

replacement gate 写入后以及 SUCCESS_COMMITTED replay 时，命令均实际调用 `verify_source_control_recovery_gate_and_hashes()`，并要求 verifier 返回的 payload 与确定性 `replacement_gate` 完全相等。独立终态复现把 verifier 返回改为空字典，得到：

```text
TERMINAL_VERIFIER_MISMATCH_REJECTED terminal replacement gate verifier payload mismatch
```

因此 frozen 成员一致性与 replacement gate 的实际可验证性都已成为处置终态条件。

### M9-SPR-R24-B02：CLOSED

recovery transaction 和 parent 的缺席判定现同时检查 `exists()` 与 `is_symlink()`。冻结负例在 transaction 固定路径建立 dangling symlink，`source_control_disposition_runtime_receipt()` 返回 `gate disposition requires absent recovery transaction and parent`，不再生成 `recovery_transaction_absent=true` receipt。

同一 exists-or-is-symlink 规则已用于 disposition journal、active gate 和 retired gate 的 namespace presence 分支；active/retired 随后交由严格 root 私有对象 receipt 拒绝链接及 nlink 异常。

## 六个中断窗口、临时文件与绑定复核

正式测试覆盖 `prepared`、`rename`、`retired_journal`、`replacement`、`replacement_journal`、`terminal` 六个持久化窗口。每项先在完成相应持久化动作后注入 `KeyboardInterrupt`，再由第二次调用续提到 SUCCESS_COMMITTED；未漂移终态 replay 对 active、retired、journal 三项逐字节零写入。

disposition schema、decision、scope、报告 SHA、replacement verdict SHA/schema、source frozen manifest SHA、授权记录 SHA、runtime 完整字典、context 和 bootstrap 的错误值均能停止。旧 active/retired gate 的 symlink、hardlink、owner/mode/nlink 异常通过 `strict_root_private_receipt()` 拒绝。固定临时文件对 symlink、hardlink、wrong-owner/mode、部分内容以及 file fsync、replace、target recheck、target file fsync、directory fsync 中断具有既有原子 writer 负例和续提测试。

这些证据说明 disposition 的业务授权域、冻结闭集、对象迁移和 replacement 验证已经闭合；剩余问题只涉及 journal 文件自身的 metadata/namespace receipt。

## M9-SPR-R25-B01：OPEN——已有 root 私有 journal 的对象 receipt 未验证

首次 PREPARED journal 由 `atomic_root_private_json()` 创建，正常文件因此为 root:root、0600、nlink 1。但重入路径只通过：

```python
journal_present = journal.exists() or journal.is_symlink()
journal = json.loads(journal.read_text(...))
```

读取已有 journal 后，代码验证 payload schema、context、bootstrap、state 和 old_gate 字段，却没有对 `SOURCE_CONTROL_GATE_DISPOSITION_JOURNAL` 本身调用 `strict_root_private_receipt()`，也没有通过同一文件描述符绑定实际读取 bytes 与 inode receipt。

独立 root 临时终态复现先完成一次正常 disposition，再保持 journal bytes 完全不变，分别把固定 journal path 改为指向该内容的 symlink，以及给 journal 增加第二个 hardlink。实际命令均返回 0：

```text
SYMLINK_JOURNAL_ACCEPTED 0 STILL_SYMLINK True
HARDLINK_JOURNAL_ACCEPTED 0 NLINK 2
```

这表明 journal 的内容一致不等于 root 私有控制对象身份一致。终态 replay 在这两种 metadata/namespace 漂移下仍报告成功，因而当前 72 项正常 replay 不能证明正式 journal 始终保持 non-link、单链接和私有 owner/mode。

### 最小关闭条件

- 每次发现 journal namespace 已存在时，必须在解析 JSON 前验证固定 path 是普通文件、非 symlink、root:root、mode 0600、nlink 1；dangling 与指向有效文件的 symlink 均须拒绝。
- 应从单次 `O_NOFOLLOW` 文件描述符读取 journal bytes，并以同一 fd 的 device/inode/UID/GID/mode/nlink/size receipt 绑定解析内容；读取后重新核对固定 path 仍指向同一 inode。
- 上述验证必须覆盖 PREPARED、INVALID_GATE_RETIRED、REPLACEMENT_CREATED 和 SUCCESS_COMMITTED 每次重入，包括 terminal replay；不符合时 active、retired、journal 均零写入。
- 冻结测试应增加 existing journal 的 symlink、dangling symlink、hardlink、wrong owner、wrong mode 以及读取期间 path/inode 变化矩阵，并分别断言 disposition 命令在任何 gate/runtime mutation 前停止。

## 最终边界

本轮计数为 `BLOCKING=1`、`NON_BLOCKING=0`、FAIL。第二十四次三个稳定问题已经关闭，但 `M9-SPR-R25-B01` 未满足 root 私有 journal 的最小可靠性条件。修复后需重新冻结四项对象并进行定点复核；只有达到零问题 PASS，才可同时生成 disposition 专用 verdict 和 replacement source-recovery verdict。

本轮仅新增本报告；未创建任何可消费 PASS verdict，未执行 disposition、recovery、`source_prepare`，未修改旧 gate、正式 runtime、cleanup 证据或被冻结对象。
