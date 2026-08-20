# M9 source-control gate disposition 第二十七次最终定点复核

## 结论

本轮独立只读定点复核结论为 **PASS**：`BLOCKING=0`，`NON_BLOCKING=0`。`M9-SPR-R25-B01` 已关闭。既存 disposition journal 现在通过单一文件描述符完成 non-link、root:root、0600、nlink 1、device/inode、size 与 bytes 的一致性验证，JSON 直接从同一 fd 所读 payload 解析；open 后及读取期间的 symlink/hardlink/path 变化均能在状态动作前停止。

主 agent 可以基于本报告机械创建 disposition 专用 verdict 和 replacement source-recovery verdict，并在两份 JSON 的路径、SHA 与当前冻结现场全部通过实际 verifier 后执行一次 `overlap-dispose-invalid-source-control-gate`。本 PASS 不授权执行 source-control recovery、`source_prepare` 或其他运行时动作。

## 冻结快照与正式测试

独立复算的四项 SHA-256 与指定值完全一致：

- `06_reproduction/scripts/m9_budget.py`：`5a1fb9c9e7d348e78992d7f0b7e832225a50334de033150276f9cd6902899eb5`
- `06_reproduction/tests/test_m9_overlap_controls.py`：`f926e238bc080a291e7a2f82588b9a6b8900e37b7e485ca305b44ed402aa5838`
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：`ec29651d5a4d2621f8026fe0ea91cf238f02ad62b05e3f8ba211184635488a07`
- `06_reproduction/manifests/m9_source_control_test_cleanup_frozen_hashes.json`：`69cb9cf141735ea2a25e12ff8e02a4ecaeaf9539376452f4e66e513f3a787f8d`

source manifest 独立复算为 `18/18`，cleanup manifest 为 `4/4`。冻结 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9` 以 `-I -S -B` 执行完整正式测试，结果为 `Ran 74 tests in 14.508s`、`OK`、退出码 0。控制脚本和测试目录中的 `.pyc`、`.pyo`、`__pycache__` 合计为 0。

## M9-SPR-R25-B01：CLOSED

新增 `read_strict_root_private_bytes(path)` 使用 `O_RDONLY | O_NOFOLLOW | O_CLOEXEC` 单次打开固定 journal path。在同一 fd 上执行：

- 读取前 `fstat()`，要求普通文件、root:root、mode 0600、nlink 1；
- 从同一 fd 循环读取完整 bytes；
- 读取后再次 `fstat()`；
- 对固定 path 执行不跟随链接的 `lstat()`；
- 比较读取前 fd、读取后 fd 与最终 path 的 device、inode、mode、UID/GID、nlink、size，并要求 payload 长度等于 fd size。

`strict_root_private_json()` 直接对该函数返回的 payload 执行 UTF-8 和 JSON object 解析。`command_dispose_invalid_source_control_gate()` 不再先取得 receipt 后按路径二次读取 journal，而是一次调用 `strict_root_private_json()` 同时取得已验证 bytes 与解析结果。

冻结命令级测试首先证明调用开始前已经存在的 symlink 或 hardlink journal 会停止，且 active、retired、journal bytes 不变。新增单 FD 测试在首次 `os.read()` 时分别把固定 path 换为 symlink，或为已打开 inode 增加第二个 hardlink；两项均得到 `root-private control object path changed while reading`。

独立终态复现进一步覆盖两个注入阶段：open 返回后、首次 `fstat` 前，以及首次同 FD read 中。每个阶段分别进行 symlink/path replacement 和 hardlink 增加，实际命令结果为：

```text
after_open symlink REJECTED root-private control object path changed while reading
after_open hardlink REJECTED root-private control object metadata mismatch
during_read symlink REJECTED root-private control object path changed while reading
during_read hardlink REJECTED root-private control object path changed while reading
```

四项复现中 active gate、retired gate 和 journal payload 均未被命令改写。由此，预置对象异常、open 后变化、读取中变化和读取后 path receipt 已共同覆盖上一轮的 receipt/read 间隔，`M9-SPR-R25-B01` 的最小关闭条件满足。

## 状态机与相邻门控回归

disposition 状态严格限定为 PREPARED、INVALID_GATE_RETIRED、REPLACEMENT_CREATED、SUCCESS_COMMITTED；每次重入及终态均绑定完整 `old_gate` path/SHA/bytes/root:root/0600/nlink 1 receipt。未知 state、old-gate receipt、context、bootstrap、runtime、retired/replacement terminal receipt 漂移均停止。

六个持久化中断窗口 `prepared`、`rename`、`retired_journal`、`replacement`、`replacement_journal`、`terminal` 继续通过：第一次调用在指定动作已持久化后中断，第二次调用续提到 SUCCESS_COMMITTED；合法终态 replay 对 active、retired 和 journal 逐字节零写入。

disposition verdict 的 schema、decision、scope、报告 SHA、replacement verdict 路径/SHA、frozen manifest SHA、授权记录 SHA 均为固定门控。verifier 逐项复算 source manifest 的 18 个成员并检查控制目录闭集；frozen 成员漂移在首写前停止。replacement gate 创建后与终态 replay 均实际调用 `verify_source_control_recovery_gate_and_hashes()`，并要求返回 payload 与确定性 replacement payload 完全一致。

recovery transaction、parent、journal、active/retired namespace 均采用 exists-or-is-symlink 语义；transaction/parent dangling symlink 不会被记为缺席。active/retired 与既存 journal 随后分别进入严格 root 私有 receipt/reader。固定临时文件对部分内容、symlink、hardlink、wrong owner/mode，以及 file fsync、replace、target recheck、target file fsync、directory fsync 中断的拒绝或续提测试保持通过。

## 正式现场前后不变性

测试与全部独立临时复现前后，旧无效 gate 保持 SHA-256 `6bdd2fdbff6df6a7a8cfa1ba3cda038ca7cfe96b3b5dfb48905ef0f5151f5821`、1711 bytes、root:root、0600、nlink 1。正式 disposition journal、`.closed-set-invalid.retired.json`、source recovery transaction 和 parent snapshot 均缺席。

五项正式 runtime SHA-256 保持：

- state：`1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`
- workflow：`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`
- failed transaction：`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`
- ledger：`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`
- stale capability：`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`

cleanup retired 对象、retirement receipt、cleanup journal、cleanup gate/root snapshot、security migration 分别保持 SHA-256 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`、`74b24867d06a437f0e693c8edd231ab4bc31782b8978abfff77b01658567fd49`、`1e0729d72bb7e45e773a61d9aff6228061a5b000cd218c23e5263153f2425d8d`、`12cec1f13eec81c110b8a7d66aecaf4e1786c0821c82a702885b9e74cfeb57b2`、`60fef9c099bfc345973bb9ac074f084f48e5e542508681fa4d55ceb099ba5c94`。六项 source/build 产品继续缺席。

## Verdict 创建与一次 disposition 的精确边界

replacement source-recovery verdict 应写入 `08_audits/M9_source_control_recovery_replacement_final_verdict.json`，并至少具有：schema `m9-source-control-recovery-audit-verdict-v1`、decision `D-017-source-control-recovery-v1`、`verdict=PASS`、`blocking=0`、`non_blocking=0`。

disposition verdict 应写入 `08_audits/M9_source_control_gate_disposition_final_verdict.json`，并具有：schema `m9-source-control-gate-disposition-audit-verdict-v1`、decision `D-017-source-control-gate-disposition-v1`、scope `RETIRE_CLOSED_SET_INVALID_GATE_AND_CREATE_REPLACEMENT_ONLY`、`verdict=PASS`、`blocking=0`、`non_blocking=0`。它必须绑定本报告路径/SHA、replacement verdict 路径/SHA、旧 gate SHA/1711 bytes、source frozen manifest SHA `ec29651d5a4d2621f8026fe0ea91cf238f02ad62b05e3f8ba211184635488a07`、授权记录 SHA `6b3e7a714a0adc8f00d56a45b5cedba99cbf941287109666cb1aac74bcf72da1`，以及以下完整 runtime 字典：

```json
{
  "state_sha256": "1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc",
  "workflow_sha256": "2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d",
  "transaction_sha256": "12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309",
  "ledger_sha256": "25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f",
  "stale_capability_sha256": "0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e",
  "recovery_transaction_absent": true,
  "recovery_parent_absent": true
}
```

两份 JSON 创建并复算无误后，主 agent 可以使用冻结 Python、root 身份执行一次 `overlap-dispose-invalid-source-control-gate`。执行后必须停止，不得在同一授权下继续 recovery 或 `source_prepare`；disposition 结果需要新的独立只读事实审计。

本轮最终计数为 `BLOCKING=0`、`NON_BLOCKING=0`。本报告自身未创建 verdict，未执行 disposition、recovery 或 `source_prepare`，未修改任何被审对象或正式运行时。
