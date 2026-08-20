# M9 source-control gate disposition 第二十四次阻塞复核

## 结论

本轮独立只读复核结论为 **FAIL**：`BLOCKING=3`，`NON_BLOCKING=0`。新增的 `overlap-dispose-invalid-source-control-gate` 已建立专用 verdict 域、root/bootstrap 前置、`budget.lock`、PREPARED journal、旧 gate 退役、replacement 创建以及六个进程中断窗口的基本状态机；冻结测试 `70/70` 通过，正式现场保持零写入。但主动临时复现证明 journal 完整性、replacement gate 有效性和 transaction/parent namespace 缺席仍未形成闭合证据。

因此 `M9-SPR-R23-B01` 仍为 OPEN，并新增 `M9-SPR-R24-B01`、`M9-SPR-R24-B02`。本轮不得执行 disposition、gate replacement、recovery 或 `source_prepare`；也不得生成能够被正式命令消费的 disposition PASS verdict 或 replacement source-recovery PASS verdict。

## 冻结快照、测试与正式现场

独立复算的四项 SHA-256 与指定值完全一致：

- `06_reproduction/scripts/m9_budget.py`：`85f7d60b69a2443d512b7eb52327b8c3f2654649d6aa3effe6df5a78e7919497`
- `06_reproduction/tests/test_m9_overlap_controls.py`：`941a560dee19ce5701aff26425f88a49c55034168bbcebbca9dbdea3e4e7c112`
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：`b115c447e1a0e9e7ab64b079c6b20732b78c08c3ecd713e302657bfe9064665d`
- `06_reproduction/manifests/m9_source_control_test_cleanup_frozen_hashes.json`：`9cc97cfa6a36adcf8f639f00c22de2c4db8aea77951eec7d31b22bd1f3959d1f`

source frozen manifest 为 `18/18`，cleanup manifest 为 `4/4`。冻结 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9` 以 `-I -S -B` 执行完整测试，结果为 `Ran 70 tests in 15.524s`、`OK`、退出码 0。控制脚本和测试目录的 `.pyc`、`.pyo`、`__pycache__` 合计为 0。

正式旧 gate 保持 SHA-256 `6bdd2fdbff6df6a7a8cfa1ba3cda038ca7cfe96b3b5dfb48905ef0f5151f5821`、1711 bytes、root:root、mode 0600、nlink 1。正式 disposition journal 和 `.closed-set-invalid.retired.json` 均缺席；source recovery transaction 与 parent snapshot 均缺席。

测试和全部主动临时复现前后，五项正式 runtime SHA-256 不变：

- state：`1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`
- workflow：`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`
- failed transaction：`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`
- ledger：`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`
- stale capability：`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`

当前 `source_control_disposition_runtime_receipt()` 的完整正常返回应精确等于：

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

cleanup retired 对象、retirement receipt、cleanup journal、cleanup gate/root snapshot 和 security migration 的 SHA 分别保持 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`、`74b24867d06a437f0e693c8edd231ab4bc31782b8978abfff77b01658567fd49`、`1e0729d72bb7e45e773a61d9aff6228061a5b000cd218c23e5263153f2425d8d`、`12cec1f13eec81c110b8a7d66aecaf4e1786c0821c82a702885b9e74cfeb57b2`、`60fef9c099bfc345973bb9ac074f084f48e5e542508681fa4d55ceb099ba5c94`，与既有执行审计一致。六项 source/build 产品没有被创建。

## 已正确闭合的处置控制

实际 verifier 和临时文件探针确认以下条件均能停止：错误 disposition schema、错误 decision、错误 scope、报告 SHA 漂移、replacement verdict SHA 漂移、replacement verdict schema 漂移、frozen manifest 文件 SHA 漂移及授权记录 SHA 漂移。处置 verifier 的专用域为：

- schema：`m9-source-control-gate-disposition-audit-verdict-v1`
- decision：`D-017-source-control-gate-disposition-v1`
- scope：`RETIRE_CLOSED_SET_INVALID_GATE_AND_CREATE_REPLACEMENT_ONLY`

旧 gate 的 symbolic-link receipt 被判定为非普通 root 私有对象，hardlink receipt 因 nlink 不为 1 被拒绝。固定 `.tmp` 为 symlink 或 mode 异常时，root 私有原子 writer 在 target 创建前停止；root:root、0600、nlink 1 的部分内容 `.tmp` 能被截断并续提为完整 payload。通用冻结测试还覆盖 file fsync、replace、target recheck、target file fsync 和 directory fsync 的中断续提。

六个正式 disposition 窗口为 `prepared`、`rename`、`retired_journal`、`replacement`、`replacement_journal`、`terminal`。每个窗口在自动删除的完整临时树中第一次中断，第二次收敛到 `SUCCESS_COMMITTED`；未注入漂移时的终态 replay 字节不变。runtime receipt 漂移在 PREPARED journal 首写前停止；context、bootstrap、终态 retired receipt 和终态 replacement receipt 漂移也分别被拒绝。

这些结果说明基础持久化序列和原子 writer 可用，但不覆盖下面三个由实际函数复现的阻塞。

## M9-SPR-R23-B01：OPEN——journal 状态与历史 receipt 未闭合

处置命令读取已有 journal 时只检查 schema、`context` 和 `python_bootstrap`。除 `SUCCESS_COMMITTED` 特判外，`state` 没有允许集合检查，也没有按 PREPARED、INVALID_GATE_RETIRED、REPLACEMENT_CREATED 三个阶段核对该阶段应当持有的 receipts。

独立临时复现先完成一次正常 disposition，然后把 terminal journal 的 `old_gate.sha256` 改为另一值并保持其他字段不变。再次调用实际命令返回 0：

```text
TERMINAL_OLD_GATE_JOURNAL_DRIFT_ACCEPTED 0
```

把同一 journal 的 state 改为 `UNRECOGNIZED_STATE` 后再次调用，命令也返回 0，并把 journal 重写为 SUCCESS：

```text
UNKNOWN_JOURNAL_STATE_ACCEPTED 0
```

因此当前所谓 terminal replay 零写入仅对未漂移的合法样本成立；它不能证明 journal 的历史证据和状态机阶段保持一致。未知 state 被当作可续提状态，终态 `old_gate` receipt 也不属于 terminal 验证集合。

最小关闭条件：显式限定 state 为 PREPARED、INVALID_GATE_RETIRED、REPLACEMENT_CREATED、SUCCESS_COMMITTED；为每个 state 定义必需字段、禁止字段和 filesystem receipts，并在任何写入前逐项验证。SUCCESS 必须同时核对 `old_gate`、`retired_gate`、`replacement_gate`、context、bootstrap 和完成时间字段的结构；未知 state、缺字段、额外矛盾字段或任一历史 receipt 漂移均须零写入停止。冻结测试应对每个 state 的 state 名、old/retired/replacement receipts 和阶段错配建立负向矩阵。

## M9-SPR-R24-B01：OPEN——replacement 有效性未形成事务终态条件

`verify_source_control_gate_disposition()` 只比较 frozen manifest 文件自身的 SHA，并不解析 manifest 后逐项复算 18 个成员，也不调用控制目录闭集检查。独立临时复现先建立可通过的 disposition verdict，再只改变 manifest 登记的成员文件而保持 manifest 字节不变；实际 verifier 仍返回成功：

```text
FROZEN_MEMBER_DRIFT_ACCEPTED
```

处置命令在 replacement gate 写入后只检查该候选 gate 的目标 bytes/SHA receipt，随后写 REPLACEMENT_CREATED 和 SUCCESS；它没有调用 `verify_source_control_recovery_gate_and_hashes()`。因此，若 manifest 成员或控制目录在审计后漂移，命令可以退役旧 gate、创建一个随后会被 source recovery verifier 拒绝的 replacement gate，并仍将 disposition journal 标记为 SUCCESS。

最小关闭条件：在 PREPARED 首写前解析当前 18 项 manifest，验证 schema/decision、闭集相等、逐项文件哈希及控制目录无 cache/额外子目录；任何成员漂移必须保持 active old gate、retired path 和 journal 原样。replacement 创建后、REPLACEMENT_CREATED 或 SUCCESS 之前，必须对 replacement gate 调用实际 source recovery verifier，并把 verifier 绑定的 gate SHA、audit verdict SHA、frozen SHA、授权 SHA 持久化为终态 receipt。verifier 失败不得产生 SUCCESS。冻结测试应覆盖任一 manifest 成员漂移、控制目录 cache/额外对象和 replacement verifier 失败。

## M9-SPR-R24-B02：OPEN——transaction/parent namespace 缺席判定不完整

`source_control_disposition_runtime_receipt()` 使用 `Path.exists()` 判断 recovery transaction 和 parent 是否存在。该方法对 dangling symlink 返回 false。独立临时树在 recovery transaction 固定路径建立指向缺失目标的 symlink，其他 runtime 文件均有效；实际函数仍返回：

```text
DANGLING_RECOVERY_NAMESPACE_ACCEPTED True
```

这使 `recovery_transaction_absent=true` 不能证明固定 namespace 没有目录项。处置后该 symlink 仍会阻止或改变后续 transaction 原子创建语义，因此不是可接受的“缺席”现场。

最小关闭条件：transaction 和 parent 的缺席必须通过不跟随链接的 namespace 检查证明固定路径没有目录项；regular file、目录、symlink（包括 dangling）、hardlink 或其他对象均应在 PREPARED 首写前停止。runtime receipt 应明确绑定两个固定 path 的 namespace-absent 结果，冻结测试应覆盖 active/parent 的 regular、symlink、dangling symlink 和目录矩阵。

## 离线 source-index 回归

本轮测试已不读取可变的 `/var/lib/apt/lists`。`test_offline_recovery_manifest_and_source_chain` 读取正式 `overlap_offline_recovery_transaction.json`，先要求 state 为 `SUCCESS_COMMITTED`，再把其中持久化的 `source_index_receipts` 与冻结 offline manifest 的 keyring、两个 InRelease 和四个 Packages index SHA 逐项比较。独立读取确认正式 transaction 为 SUCCESS，七项 receipt 与 manifest 完全一致。该修改只核验已经提交的历史 receipt，不追认当前系统新索引，符合回归测试的冻结证据边界。

## 最终判断与放行边界

本轮为 `BLOCKING=3`、`NON_BLOCKING=0`、FAIL。70 项测试通过和正式现场零写入不关闭其未覆盖的一致性条件。应修复上述三项并重新冻结 controller、测试、source manifest 和 cleanup manifest，再执行同等独立复核。

只有后续达到 `BLOCKING=0`、`NON_BLOCKING=0`，才可同时签发 disposition 专用 JSON 和 replacement source-recovery JSON；即使签发，也仅授权一次受控 gate disposition，不自动授权 recovery 或 `source_prepare`。

本轮仅新增本报告。未新增可消费 PASS verdict，未修改旧 gate、runtime、cleanup 证据或冻结对象，未执行 disposition、recovery 或 `source_prepare`。
