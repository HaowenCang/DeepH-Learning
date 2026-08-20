# M9 source-control gate disposition 执行独立事实审计

## 结论

本轮执行后独立只读事实审计结论为 **PASS**：`BLOCKING=0`，`NON_BLOCKING=0`。正式 disposition 已形成相互一致的 `SUCCESS_COMMITTED` journal、原 gate retired 对象和 replacement active gate；旧 gate 字节与原 inode 保真，replacement gate 是由 retired payload 与当前 replacement verdict 确定性重建的精确结果，并通过实际 `verify_source_control_recovery_gate_and_hashes()`。

现有证据允许项目进入 source-control recovery 的下一独立授权检查点，但本报告不授权执行 source-control recovery、disposition replay、`source_prepare` 或任何其他运行时动作。后续若拟执行 recovery，应另行确认当前 active gate、冻结闭集、正式 runtime、failed transaction、stale capability 和 source/build 缺席条件仍未漂移，并取得明确的单次执行授权。

## 审计边界与输入

主 agent 提供的命令遥测为：root 身份、冻结 Python、`-I -S -B`，退出码 0，stdout 中 `replacement_sha256=5553de21184082b3ace505f4981f20c3116df7389805f2070ebf7e8b8dad5936`。本轮没有重复执行该命令，而是独立读取持久化现场，并用当前冻结实现的纯读取 verifier 验证结果。因而，退出码和 stdout 属于外部提供的执行记录；replacement SHA、journal 终态及其全部绑定则由本轮独立文件系统证据确认。

本轮未调用 disposition replay、source-control recovery 或 `source_prepare`。除新增本报告外，没有修改正式对象。

## 冻结对象与审计链

四项冻结 SHA-256 保持第二十八次获准快照：

- `06_reproduction/scripts/m9_budget.py`：`f712188ed0af9beace844f2f3e534f05c6de6166458472b011a0d7f90f504c28`
- `06_reproduction/tests/test_m9_overlap_controls.py`：`d2b4d5d7c542d3e2c64997957eadfed978fedb6163b030a3e9b62207260a8486`
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：`3acf16f494390645fa4807284c70efda96bbcf583916b220dfc1bafca06c7022`
- `06_reproduction/manifests/m9_source_control_test_cleanup_frozen_hashes.json`：`ee1cede537d7b0c011f399dbfb94df1393c6d5e98cf3f3927012b982f34f24ad`

source frozen manifest 的 18 个成员逐项复算为 `18/18`，cleanup manifest 的 4 个成员为 `4/4`，均无缺失或不匹配。第二十八次报告保持 9707 bytes、SHA-256 `bf8f350d80ad9f76f963cd31f8d6070fa7417c480690949ca7947c334a917c63`。

更新后的 disposition verdict 为 1587 bytes、SHA-256 `f998a0119ae75d5afa41b5652f56a6abb46198522dd3ebc6a8be0ab17ef60f77`。其 schema、decision、scope、PASS 0/0、旧 gate SHA/1711 bytes、第二十八次报告路径/SHA、replacement verdict 路径/SHA、当前 source manifest SHA、授权记录 SHA 和完整 runtime 字典均与 journal context 及现场一致。

replacement source-recovery verdict 为 548 bytes、SHA-256 `2e149fe1f490b0c672b552cd447d48ef8be8fe60efd9d2f8a5e7f6311f831a9a`。其 schema 为 `m9-source-control-recovery-audit-verdict-v1`，decision 为 `D-017-source-control-recovery-v1`，scope 为 `ONE_TIME_SOURCE_CONTROL_RECOVERY`，结论为 PASS 0/0，并绑定第二十八次报告和当前 source frozen manifest。

## 三项 disposition 持久化对象

active replacement gate 的独立收据为：

```text
path=/home/evan-williams/deeph-m9/manifests/overlap_source_control_recovery_gate.json
uid=0 gid=0 mode=0600 nlink=1 bytes=1723 inode=139158 dev=2096
sha256=5553de21184082b3ace505f4981f20c3116df7389805f2070ebf7e8b8dad5936
```

retired old gate 的独立收据为：

```text
path=/home/evan-williams/deeph-m9/manifests/overlap_source_control_recovery_gate.closed-set-invalid.retired.json
uid=0 gid=0 mode=0600 nlink=1 bytes=1711 inode=132095 dev=2096
sha256=6bdd2fdbff6df6a7a8cfa1ba3cda038ca7cfe96b3b5dfb48905ef0f5151f5821
```

第二十八次执行前审计记录的旧 active gate inode 同为 132095，当前 retired 对象仍保持该 inode、1711 bytes 与原 SHA。因此现有证据支持旧 gate 经同一文件系统内原子 rename 保真迁移，而不是被重新序列化或内容替换。

root journal 的严格单 fd 收据为：

```text
path=/root/deeph-m9-control/source-control-gate-disposition.json
uid=0 gid=0 mode=0600 nlink=1 bytes=3748
sha256=e97dc9b00a798f5a26807e5af18c78c2779be4ab144adeaa39f5be4338dc8ece
```

journal schema 为 `m9-source-control-gate-disposition-v1`，state 为 `SUCCESS_COMMITTED`；`prepared_utc=2026-08-19T11:56:33.700612Z`，`completed_utc=2026-08-19T11:56:35.922838Z`，完成时间晚于准备时间。`old_gate`、`retired_gate` 和 `replacement_gate` 三个 receipt 的 path、SHA、bytes、root:root、0600、nlink 1 均与实际对象一致。

journal context 精确绑定 disposition verdict SHA、replacement verdict SHA、current frozen manifest SHA、authorization record SHA、完整 runtime、旧 gate SHA/bytes 和 replacement gate SHA/bytes。以当前冻结 Python 重新计算 `isolated_bootstrap_provenance()`，结果与 journal 的 `python_bootstrap` 完全相等，包括 executable、`-I/-S/-B` 语义、sys.path 及 argparse/hashlib/json/pathlib 的 origin、loader 和 SHA。

本轮以程序化断言核对 journal schema/state、两份 verdict、frozen/auth、runtime/bootstrap、old-to-retired receipt、replacement receipt、时间顺序及两个实际 verifier，共 17 项，结果为 `17/17 true`。

## Replacement gate 的完整有效性

active gate 具有 schema `m9-source-control-recovery-gate-v1`、decision `D-017-source-control-recovery-v1`、status PASS、blocking 0、non_blocking 0 和 scope `ONE_TIME_SOURCE_CONTROL_RECOVERY`。其 audit report 指向 replacement structured verdict，SHA 为 `2e149fe1f490b0c672b552cd447d48ef8be8fe60efd9d2f8a5e7f6311f831a9a`；授权记录 SHA 为 `6b3e7a714a0adc8f00d56a45b5cedba99cbf941287109666cb1aac74bcf72da1`；frozen manifest SHA 为 `3acf16f494390645fa4807284c70efda96bbcf583916b220dfc1bafca06c7022`。

本轮将 retired old-gate payload 与当前 replacement verdict 交给纯函数 `replacement_source_control_gate()` 重建期望 payload，所得对象与 active gate 完全相等。随后以 root 和冻结 Python 实际调用 `verify_source_control_recovery_gate_and_hashes()`；它返回的 payload 与 active gate 相等，并逐项验证 structured PASS verdict、授权、18 项 frozen 闭集和完整控制目录。实际 `verify_source_control_gate_disposition()` 也返回与两份当前 verdict 相等的 payload。该验证只读取对象，没有执行 disposition 或 recovery。

active gate 对正式父失败事务的绑定保持：transaction ID `e5bfc046d4d5a1bd97507d37b40f1e0c`、SHA `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`；对 state、workflow、ledger 和 stale capability 的绑定也与下述现场一致。

## Runtime、锁和无越权产物

正式 `budget.lock` 仍为 UID/GID 1000:1000、0644、nlink 1、0 bytes、inode 50700，SHA-256 为空文件固定值 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`，与 disposition 前收据一致。

五项 runtime SHA-256 保持原基线：

- state：`1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`
- workflow：`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`
- failed transaction：`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`
- ledger：`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`
- stale capability：`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`

failed transaction 仍为 `FAILED_COMMITTED`、action `source_prepare`、exit code 1、reason `overlap_command_failed`；ledger tip 仍是同 transaction ID 和 reason 的 `OVERLAP_HARD_STOP`。stale capability 仍为 `BOUND`、action `source_prepare`、UID/GID 1000:1000、mode 0600、nlink 1，budget PID 294 和 child PID 373 均不存在。对应 `.consumed.json` 和 `.launcher-receipt.json` 均缺席。

正式 source recovery transaction 与 parent snapshot 均缺席。六项 source/build 产品 `openmx-overlap-build`、`openmx-overlap-build.staging`、`env/hdf5-1.12.1`、`openmx_official_3.9.9_tree_manifest.json`、`openmx_overlap_tree_manifest.json`、`openmx_overlap_build_manifest.json` 均缺席。因此，除 disposition 规范内的 journal、retired old gate 和 replacement active gate 外，没有观察到 recovery、capability 消费、source 解包、HDF5 安装、OpenMX build 或相关 manifest 产物。

cleanup retired 对象、retirement receipt、cleanup journal、cleanup gate/root snapshot 和 security migration 继续保持既有 SHA-256：`2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`、`74b24867d06a437f0e693c8edd231ab4bc31782b8978abfff77b01658567fd49`、`1e0729d72bb7e45e773a61d9aff6228061a5b000cd218c23e5263153f2425d8d`、`12cec1f13eec81c110b8a7d66aecaf4e1786c0821c82a702885b9e74cfeb57b2`、`60fef9c099bfc345973bb9ac074f084f48e5e542508681fa4d55ceb099ba5c94`。

## 回归与后置不变性

冻结 Python 以 `-I -S -B` 重新运行正式套件，结果为 `Ran 75 tests in 15.268s`、`OK`、退出码 0。测试前后 active、retired、journal、lock、五项 runtime 和全部 cleanup 证据的 SHA 均不变；source recovery transaction/parent、consumed/launcher receipt 仍缺席。`06_reproduction` 内 `.pyc`、`.pyo` 和 `__pycache__` 合计为 0。

## 下一授权检查点

本次 disposition 执行事实满足进入下一检查点的最小条件：终态 journal 完整且可验证、旧 gate 保真 retired、replacement gate 通过实际 verifier、正式 runtime 与 capability 现场未漂移、recovery transaction/parent 和 source/build 产品缺席、控制闭集与测试回归通过。

“允许进入下一授权检查点”仅表示可以开展 source-control recovery 的最终执行前只读核验或生成与该核验绑定的新授权材料，不表示可以立即运行 recovery。任何 recovery 执行仍应绑定本报告之后的当前现场，并明确限制为一次 source-control recovery；执行完成后应立即停止，另行进行执行事实审计。当前绝不授权 recovery、`source_prepare` 或 disposition replay。

最终计数：`BLOCKING=0`，`NON_BLOCKING=0`。
