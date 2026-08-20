# M9 source-control recovery 第二十三次闭集与 gate 处置审计

## 结论

本轮独立只读复核结论为 **FAIL**：`BLOCKING=1`，`NON_BLOCKING=0`。修订后的 source-control recovery 控制包本身通过冻结闭集、状态机测试和正式现场零写入复核；上一轮遗漏 `m9_range_download.py` 的 17 项闭集已经修复为完整 18 项闭集。唯一阻塞为新发现的 gate 生命周期授权问题 `M9-SPR-R23-B01`：现存旧 gate 从未通过当前 verifier，但对它执行原子 rename 仍是对 root 控制对象的状态变更，不属于已使用的 `CREATE_SOURCE_CONTROL_RECOVERY_GATE_ONLY` 授权范围。

因此，当前不得退役、覆盖或替换旧 gate，不得创建第二份 gate，也不得执行 recovery 或 `source_prepare`。需要先形成 source recovery gate 处置专用的结构化零问题 verdict，并把退役与替代创建定义为可中断续提的一次性状态机。由于本轮不是零问题 PASS，未新增新的 source recovery PASS verdict。

## 新冻结快照与完整闭集

独立复算的四项 SHA-256 与指定值完全一致：

- `06_reproduction/scripts/m9_budget.py`：`531d88183344b310c3fc3edb2e6556b0c377df0746bd342a2350b1810686c862`
- `06_reproduction/tests/test_m9_overlap_controls.py`：`18b8bc97c280601c44baa132bbc84a7ee448b8f7f230bc49037dce5dc018cb93`
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：`07e47c760b4b612c8b269c20abfb11c93da1f11d74becaff3ad1e79abcf3a092`
- `06_reproduction/manifests/m9_source_control_test_cleanup_frozen_hashes.json`：`37bfafcb1f04871879e839781fd62d58164a8b4746046f2a75982b7e3d8394ae`

`06_reproduction/scripts` 当前恰有 12 个 `.py` 控制文件。`SOURCE_RECOVERY_CONTROL_FILES` 完整列出这 12 个文件，包括此前遗漏的 `m9_range_download.py`；再加测试、合同、三项 manifest 和授权记录，source frozen manifest 总数为 18。独立逐项复算结果为 `18/18`，cleanup manifest 为 `4/4`。

新增正式测试 `test_source_control_frozen_set_covers_entire_control_directory` 不依赖手工重复计数，而是把控制目录实时枚举的全部 `*.py` resolved path 与 `SOURCE_RECOVERY_CONTROL_FILES` 中同目录 `.py` 的 resolved path 集合直接比较。该断言能够同时发现未来遗漏和非目录内错误登记。verifier 仍要求 manifest 文件集合与代码内闭集严格相等并逐项复算，因此代码集合、manifest 和目录实际对象三者现已形成一致性约束。

冻结 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9` 以 `-I -S -B` 执行完整测试，实际结果为 `Ran 67 tests in 16.814s`、`OK`、退出码 0。新增闭集测试通过，上一轮针对专用 verdict schema/decision、bootstrap 前置、完整首次成功、11 个持久化中断窗口、终态零写入、ledger/state/workflow/bootstrap/gate 漂移、retired 不可消费及 UID 1000 新 capability 一次性消费的测试继续全部通过。控制目录和测试目录的 `.pyc`、`.pyo`、`__pycache__` 合计为 0。

## 旧 gate 的固定事实与实际拒绝

现存路径为：

`/home/evan-williams/deeph-m9/manifests/overlap_source_control_recovery_gate.json`

独立 receipt 为 SHA-256 `6bdd2fdbff6df6a7a8cfa1ba3cda038ca7cfe96b3b5dfb48905ef0f5151f5821`、1711 bytes、root:root、mode 0600、nlink 1。其 `frozen_hashes_sha256` 仍绑定旧 17 项 manifest SHA `7875ff2e2114210e33c52de2de59ee1c8d3f64171a85dc78d30514e7e91357ed`，audit verdict SHA 仍绑定上一轮 `20d74df762902e6ec9eb7643a021365670de4b5a7f54399ec12c5ae6c0df1b98`。

以 root 身份和冻结 Python `-I -S -B` 只调用当前实际 `verify_source_control_recovery_gate_and_hashes()`，结果为：

```text
OLD_GATE_REJECTED source-control recovery frozen hash binding mismatch
```

该 verifier 调用没有进入 recovery 命令。调用前后旧 gate SHA、五项正式 runtime SHA 均逐字节不变，正式 recovery transaction 和 parent snapshot 均缺席。因此旧 gate 已证明在新快照下 fail-closed，从未形成有效 gate receipt，也没有触发 recovery 状态动作。

## 正式现场前后不变性

旧 gate 拒绝探针、完整 67 项测试及全部只读核验前后，五项正式 runtime SHA-256 保持：

- budget state：`1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`
- workflow：`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`
- failed transaction：`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`
- ledger：`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`
- stale capability：`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`

六项 source/build 产品全部缺席；正式 recovery transaction 和 parent snapshot 缺席。旧 gate 保持上述固定 SHA 与 metadata，未被移动或覆盖。

cleanup 证据也保持既有审计值：retired 对象 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`，retirement receipt `74b24867d06a437f0e693c8edd231ab4bc31782b8978abfff77b01658567fd49`，cleanup journal `1e0729d72bb7e45e773a61d9aff6228061a5b000cd218c23e5263153f2425d8d`，cleanup gate 与 root snapshot `12cec1f13eec81c110b8a7d66aecaf4e1786c0821c82a702885b9e74cfeb57b2`，security migration `60fef9c099bfc345973bb9ac074f084f48e5e542508681fa4d55ceb099ba5c94`。因此本轮测试没有写入正式 runtime 或污染 cleanup 审计链。

## M9-SPR-R23-B01：OPEN

上一轮结构化 verdict 的 scope 为 `CREATE_SOURCE_CONTROL_RECOVERY_GATE_ONLY`，并绑定旧 controller、旧测试和旧 17 项 manifest。该授权已经通过创建当前 1711-byte gate 被实际使用。当前 gate 虽因闭集不完整而从未通过 verifier，但它仍是 root:root、0600 的正式控制对象；把它 rename 为 `.closed-set-invalid.retired.json` 会改变正式 control namespace 和对象生命周期状态。`D-017-source-control-recovery-v1` 说明恢复业务决策域，不能替代对这项新状态变更的明确授权。

现有 scope 也没有定义 rename 成功而新 gate 尚未创建时的持久化中断状态。把“退役旧 gate”和“创建替代 gate”视为一条普通 CREATE 操作，会使重复调用无法仅由当前 verdict 判断是在首次创建、失败重试还是未经授权的第二次创建。因此，建议的最小处置不能在现有 `CREATE_SOURCE_CONTROL_RECOVERY_GATE_ONLY` 下直接放行。

### 最小关闭条件

需要新增独立结构化处置 verdict，建议至少使用专用 schema，例如 `m9-source-control-recovery-gate-disposition-verdict-v1`，并满足：

- `decision_id=D-017-source-control-recovery-v1`、`verdict=PASS`、`blocking=0`、`non_blocking=0`；
- scope 精确限制为 `RETIRE_CLOSED_SET_INVALID_GATE_AND_CREATE_REPLACEMENT_ONLY`；
- 绑定旧 gate 的固定 path、SHA-256、1711 bytes、UID/GID、0600、nlink 1，以及实际 verifier 的固定拒绝类别；
- 绑定旧 gate 的目标 retired path，并要求操作前该路径缺席；retired 文件必须保持原字节、root:root、0600、nlink 1；
- 绑定正式 transaction/parent 缺席、五项 runtime 固定 SHA、六项产品缺席以及 cleanup 证据固定 SHA；
- 绑定新的 source recovery audit verdict 路径/SHA、新 18 项 manifest 路径/SHA、授权记录 SHA 和替代 gate 的确定性目标字节/SHA；
- 明确要求整个处置持有 `budget.lock`，并在每个状态转换前重新核对上述 receipts；
- 定义至少三个可重复识别的状态：旧 active 精确且 retired 缺席；active 缺席且 retired 精确；新 active 精确且 retired 精确。任何其他组合必须停止；
- 旧 gate rename 后执行 directory fsync；替代 gate 通过受控固定临时文件完成 file fsync、atomic replace、target metadata/bytes recheck 和 directory fsync。若在任一持久化点中断，第二次调用必须从上述状态续提，而不得重写 retired 字节或产生第二个 active gate；
- 替代 gate 创建完成后，只读调用当前 verifier，并要求它在新 controller、专用 verdict 和 18 项 manifest 上通过；该通过仍不自动授权执行 recovery。

完成上述处置 verdict 与可中断续提机制后，应另行独立定点复核。只有该复核达到 `BLOCKING=0`、`NON_BLOCKING=0`，才可执行一次精确绑定的旧 gate 退役与替代 gate 创建操作。

## 最终边界

修订后的 18 项 source recovery 控制包和 67 项测试没有发现实现缺陷；本轮唯一阻塞是旧 gate 的处置授权与中断续提语义。最终计数为 `BLOCKING=1`、`NON_BLOCKING=0`，因此未生成新的 source recovery PASS verdict，也不允许主 agent 根据本报告修改 gate。

本轮仅新增本报告，未修改被审对象、旧 gate、正式 runtime 或 cleanup 证据；未创建或执行 gate、recovery、`source_prepare`。
