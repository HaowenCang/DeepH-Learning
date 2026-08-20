# M9 source-control gate disposition 第二十八次独立定点复核

## 结论

本轮独立只读定点复核结论为 **PASS**：`BLOCKING=0`，`NON_BLOCKING=0`。稳定问题 `M9-SPR-R28-B01` 已关闭。`command_dispose_invalid_source_control_gate()` 对既存 `budget.lock` 使用不含 `O_CREAT` 语义的 `r+` 打开方式；在正式 WSL 权限现场中，root 可以用该方式打开并取得排他锁，而原 `a+` 路径因 sticky 目录的 `protected_regular` 规则得到 `EACCES`。锁文件的 inode、元数据、长度和内容哈希在实测前后完全一致。

主 agent 可以先更新当前两份失效候选 verdict，使其绑定本报告、当前冻结清单和彼此的实际 SHA，再在实际 verifier 通过且正式现场未漂移的前提下，以冻结 Python 和 root 身份执行一次 `overlap-dispose-invalid-source-control-gate`。当前候选 verdict 不可消费。本 PASS 不授权 source-control recovery、`source_prepare` 或其他运行时动作；disposition 完成后应停止并进行新的独立只读事实审计。

## 冻结快照、闭集和正式测试

独立复算的四项 SHA-256 与指定值完全一致：

- `06_reproduction/scripts/m9_budget.py`：`f712188ed0af9beace844f2f3e534f05c6de6166458472b011a0d7f90f504c28`
- `06_reproduction/tests/test_m9_overlap_controls.py`：`d2b4d5d7c542d3e2c64997957eadfed978fedb6163b030a3e9b62207260a8486`
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：`3acf16f494390645fa4807284c70efda96bbcf583916b220dfc1bafca06c7022`
- `06_reproduction/manifests/m9_source_control_test_cleanup_frozen_hashes.json`：`ee1cede537d7b0c011f399dbfb94df1393c6d5e98cf3f3927012b982f34f24ad`

source manifest 的 18 个成员逐项复算为 `18/18`，cleanup manifest 的 4 个成员逐项复算为 `4/4`，无缺失或哈希不符。冻结 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9` 以 `-I -S -B` 执行完整套件，结果为 `Ran 75 tests in 17.009s`、`OK`、退出码 0。`06_reproduction` 内 `.pyc`、`.pyo` 和 `__pycache__` 合计为 0。

## M9-SPR-R28-B01：CLOSED

修复范围限定在 disposition 入口。代码在 root 身份、隔离 bootstrap 和两份 verdict 校验完成后，以 `LOCK_PATH.open("r+")` 打开既存锁，然后取得 `fcntl.LOCK_EX`；其他命令入口仍保持原有打开方式。由于 `r+` 不请求创建文件，既存锁缺席时会在取得锁和任何状态动作前停止，不会静默创建替代锁。

测试 fixture 在进入 disposition 命令前显式 `touch()` 锁文件。新增命令级测试监测该固定 path 的全部 `Path.open()` 调用，并令 `a+` 明确抛出代表正式内核行为的 `PermissionError`；实际命令成功完成且观测到的唯一锁模式严格为 `["r+"]`。这同时证明状态机没有经其他路径再次以 `a+` 打开 disposition 锁。

独立真实环境复现条件和结果如下：

```text
directory: /home/evan-williams/deeph-m9/manifests
directory receipt: uid=0 gid=1000 mode=1770
lock: /home/evan-williams/deeph-m9/manifests/budget.lock
lock receipt: uid=1000 gid=1000 mode=0644 nlink=1 bytes=0 inode=50700 dev=2096
a+: PermissionError errno=13 (EACCES)
r+: OPEN_LOCK_OK; LOCK_EX|LOCK_NB acquired and released
```

操作前后锁文件均为同一 inode 和 device，元数据相同，内容 SHA-256 均为 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。因此本次复现直接覆盖了导致前次正式尝试在取得锁前失败的实际文件系统条件，而不是仅依赖 mock 行为。

## 既有 TOCTOU、崩溃恢复和相邻门控

`read_strict_root_private_bytes()` 仍以 `O_RDONLY | O_NOFOLLOW | O_CLOEXEC` 单次打开对象，并在同一 fd 上执行读取前 `fstat`、完整 bytes 读取、读取后 `fstat` 和固定 path 的 `lstat`。device、inode、mode、UID/GID、nlink、size 与 payload 长度必须在 fd 和 path 间一致；`strict_root_private_json()` 直接解析同一 payload，没有恢复 receipt 后按路径二次读取的间隔。

除正式 75 项中的命令级终态 symlink/hardlink 零写入测试和单 FD 读取期间替换测试外，本轮在 root 私有临时目录主动重放四种变化：open 返回后将 path 换为 symlink、open 返回后增加 hardlink、同 fd 首次读取时换为 symlink、同 fd 首次读取时增加 hardlink。四项分别得到 metadata mismatch 或 `path changed while reading`，均未被接受。

disposition 的六个持久化中断窗口 `prepared`、`rename`、`retired_journal`、`replacement`、`replacement_journal`、`terminal` 及合法终态 replay 继续通过。第一次调用在指定持久化动作后中断，第二次续提到 `SUCCESS_COMMITTED`，其后的终态 replay 对 active、retired 和 journal 保持逐字节零写入。journal state、old-gate receipt、context、bootstrap、runtime、终态 active/retired receipt、dangling recovery namespace、verdict domain/frozen 闭集以及 replacement gate 的实际 verifier 回归均通过。

## 失效候选 verdict 的停止语义

当前两份候选文件保持前次创建后的原字节：

- `08_audits/M9_source_control_gate_disposition_final_verdict.json`：1590 bytes，SHA-256 `41101ecde4f7b4776424957cdbe54fbeaa16d463e1c49fbdfcdbd94083722bde`
- `08_audits/M9_source_control_recovery_replacement_final_verdict.json`：551 bytes，SHA-256 `ae67f77ff5de0a0b818ebae940323d53d7534f24b6f52b2298317158b46a0e76`

两者仍绑定第二十七次 source frozen manifest SHA `ec29651d5a4d2621f8026fe0ea91cf238f02ad62b05e3f8ba211184635488a07`，而当前值为 `3acf16f494390645fa4807284c70efda96bbcf583916b220dfc1bafca06c7022`。本轮以实际 `verify_source_control_gate_disposition()` 读取它们，结果在锁打开前明确停止为 `gate disposition frozen or authorization binding mismatch`。因此，前次失败没有使陈旧审计结论自动适用于修复后的代码，当前两份候选也不存在被误消费为新授权的证据。

## 正式现场前后不变性

全部检查、锁复现、TOCTOU 临时复现和 75 项测试前后，旧无效 gate 保持 SHA-256 `6bdd2fdbff6df6a7a8cfa1ba3cda038ca7cfe96b3b5dfb48905ef0f5151f5821`、1711 bytes、root:root、0600、nlink 1、inode 132095。正式 disposition journal、`.closed-set-invalid.retired.json`、source recovery transaction 和 parent snapshot 均缺席。

五项正式 runtime SHA-256 保持：

- state：`1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`
- workflow：`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`
- failed transaction：`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`
- ledger：`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`
- stale capability：`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`

cleanup retired 对象、retirement receipt、cleanup journal、cleanup gate/root snapshot、security migration 分别保持 SHA-256 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`、`74b24867d06a437f0e693c8edd231ab4bc31782b8978abfff77b01658567fd49`、`1e0729d72bb7e45e773a61d9aff6228061a5b000cd218c23e5263153f2425d8d`、`12cec1f13eec81c110b8a7d66aecaf4e1786c0821c82a702885b9e74cfeb57b2`、`60fef9c099bfc345973bb9ac074f084f48e5e542508681fa4d55ceb099ba5c94`。六项 source/build 产品继续缺席。

## 两份 verdict 更新与一次 disposition 的最小条件

允许主 agent 更新固定路径上的两份失效候选，但更新不等于沿用旧授权。replacement source-recovery verdict 必须重新绑定本报告和当前 source frozen manifest，并保持 schema `m9-source-control-recovery-audit-verdict-v1`、decision `D-017-source-control-recovery-v1`、scope `ONE_TIME_SOURCE_CONTROL_RECOVERY`、`verdict=PASS`、`blocking=0`、`non_blocking=0`；其 `audit_report_path`/`audit_report_sha256` 和 `frozen_hashes_sha256` 必须取本轮实际值。

disposition verdict 必须在 replacement verdict 的最终字节确定后重新生成，并保持 schema `m9-source-control-gate-disposition-audit-verdict-v1`、decision `D-017-source-control-gate-disposition-v1`、scope `RETIRE_CLOSED_SET_INVALID_GATE_AND_CREATE_REPLACEMENT_ONLY`、`verdict=PASS`、`blocking=0`、`non_blocking=0`。它必须绑定本报告的实际路径/SHA、replacement verdict 路径/SHA、旧 gate SHA/1711 bytes、source frozen manifest SHA `3acf16f494390645fa4807284c70efda96bbcf583916b220dfc1bafca06c7022`、授权记录 SHA `6b3e7a714a0adc8f00d56a45b5cedba99cbf941287109666cb1aac74bcf72da1`，以及以下完整 runtime 字典：

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

两份更新后的 JSON 必须可解析、无异常控制字符，并由实际 `verify_source_control_gate_disposition()` 在正式现场重新验收。仅在 verifier 成功、旧 gate receipt 与完整 runtime 仍匹配、四个后续对象仍缺席时，主 agent 才可执行一次 disposition。执行完成后授权立即终止，不得继续 recovery 或 `source_prepare`。

本轮最终计数为 `BLOCKING=0`、`NON_BLOCKING=0`。本报告自身未创建或更新任何 verdict，未执行 disposition、recovery 或 `source_prepare`，未修改任何被审对象或正式运行时。
