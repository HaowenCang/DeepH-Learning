# M9 source-control gate lock-refresh 执行独立事实审计

## 结论

本轮执行后独立只读事实审计结论为 **PASS**：`BLOCKING=0`，`NON_BLOCKING=0`。正式 lock-refresh 已形成相互一致的 `SUCCESS_COMMITTED` root journal、pre-lock retired gate 和 replacement active gate。旧 active gate的字节、inode和严格 receipt得到保真保存；新 active gate与由 retired payload、当前 replacement verdict及已验证 bindings 确定性重建的对象完全相等，并通过实际 `verify_source_control_recovery_gate_and_hashes()`。

结合用户已经明确给出的“授权执行一次性 source-control recovery”，现有授权链和正式现场足以允许主 agent执行一次、且仅一次 `overlap-recover-source-control-failure`。执行前仍必须由实际 source gate verifier通过，并确认本报告所列 gate、runtime、failed transaction、stale capability及对象缺席条件无漂移。该授权仅覆盖源控制状态恢复本身，不覆盖随后 `source_prepare`、source build、GPU任务或其他运行时动作；recovery执行后必须立即停止并进行新的独立事实审计。

## 审计边界与执行记录

主 agent提供的执行遥测为：root身份、冻结 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9`、`-I -S -B`，退出码0，stdout中 `replacement_sha256=381c8fd6e9fa28479de4f2144e975ed32756af9ac9dfe90a6d5457208da1cefa`。本轮没有执行 refresh replay，而是独立读取持久化结果并调用纯读取 verifier。

因此，rc和stdout属于提供的命令遥测；replacement SHA、journal终态、receipt、verdict/frozen/auth/runtime绑定及新 gate有效性由本轮独立文件系统证据确认。本轮未调用 refresh、source-control recovery或 `source_prepare`，除新增本报告外没有修改正式对象。

## 冻结对象与审计材料

四项冻结 SHA-256 保持获准快照：

- `06_reproduction/scripts/m9_budget.py`：`8f2cbb007045cf888e41893f8b0dc5d44f3fc88c0078590f24776724c9ede3a2`
- `06_reproduction/tests/test_m9_overlap_controls.py`：`432eb10457a88ad98fb94157d7c0fa376240a8e62404440115d7ae3b5d657f10`
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：`af86278da0cf6d68330f065dd8fbe50963b04b5c9c5b198f4cce5d2e0442e21d`
- `06_reproduction/manifests/m9_source_control_test_cleanup_frozen_hashes.json`：`6e0d799bf5ce60cd9ac18a8e384a5e71972e8f3a56d9c64665b9e71056b58495`

source manifest的18个成员逐项复算为 `18/18`，cleanup manifest的4个成员为 `4/4`。第32次独立报告保持10482 bytes、SHA-256 `cfdbd46798e90c84f076bfa82badcb5be70b0942d883b3b02662a268f7baaebf`。

refresh verdict 为1797 bytes、SHA-256 `77e7038f58cd685539bfe82986a548605c3b24c5a9ae7ff3edb16fe03f8039d1`。它具有 schema `m9-source-control-gate-lock-refresh-audit-verdict-v1`、decision `D-017-source-control-gate-lock-refresh-v1`、scope `RETIRE_PRE_LOCK_MODE_GATE_AND_CREATE_REPLACEMENT_ONLY`、PASS 0/0，并绑定第32次报告、replacement verdict、旧 active gate SHA/1723 bytes、当前 frozen、授权记录和完整 post-disposition runtime。

replacement verdict 为551 bytes、SHA-256 `8a329ec9edce4a1c1b984ec561847cfce0ed4493e4b6dedb404fc8a9b816c739`。它具有 schema `m9-source-control-recovery-audit-verdict-v1`、decision `D-017-source-control-recovery-v1`、scope `ONE_TIME_SOURCE_CONTROL_RECOVERY`、PASS 0/0，并绑定第32次报告和当前 frozen manifest。

实际 `verify_source_control_gate_lock_refresh()` 返回的 refresh/replacement payload与上述文件相等，并返回四项 bindings：refresh verdict `77e703...f8039d1`、replacement verdict `8a329e...16c739`、frozen `af8627...442e21d`、authorization `6b3e7a...f72da1`。

## 三项 lock-refresh 持久化对象

replacement active gate的严格收据为：

```text
path=/home/evan-williams/deeph-m9/manifests/overlap_source_control_recovery_gate.json
uid=0 gid=0 mode=0600 nlink=1 bytes=1728 inode=153048 dev=2096
sha256=381c8fd6e9fa28479de4f2144e975ed32756af9ac9dfe90a6d5457208da1cefa
```

pre-lock retired gate的严格收据为：

```text
path=/home/evan-williams/deeph-m9/manifests/overlap_source_control_recovery_gate.pre-lock-mode-refresh.retired.json
uid=0 gid=0 mode=0600 nlink=1 bytes=1723 inode=139158 dev=2096
sha256=5553de21184082b3ace505f4981f20c3116df7389805f2070ebf7e8b8dad5936
```

第32次执行前复核记录的旧 active gate inode同为139158，且SHA、bytes与当前 retired对象相同。该证据支持旧 gate经同文件系统原子rename保真退役，没有发生重新序列化或内容替换。

root refresh journal的单 FD严格收据为：

```text
path=/root/deeph-m9-control/source-control-gate-lock-refresh.json
uid=0 gid=0 mode=0600 nlink=1 bytes=3957
sha256=ec6a30547c78a0b2030069b8d6a682fadef7e7fb20062bcf76672b604f020519
```

journal schema为 `m9-source-control-gate-lock-refresh-v1`，state为 `SUCCESS_COMMITTED`；`prepared_utc=2026-08-19T12:53:50.076867Z`，`completed_utc=2026-08-19T12:53:52.309645Z`，完成时间晚于准备时间。`old_gate`、`retired_gate` 和 `replacement_gate` 三个receipt的path、SHA、bytes、root:root、0600、nlink 1均与实际对象一致。

journal context精确绑定refresh verdict SHA、replacement verdict SHA、current frozen SHA、authorization SHA、完整runtime、旧gate SHA/bytes及replacement gate SHA/bytes。以当前冻结Python重新计算 `isolated_bootstrap_provenance()`，与journal的 `python_bootstrap` 完全相等，包括executable、隔离/no-site/no-bytecode标记、sys.path，以及argparse/hashlib/json/pathlib的loader、origin和SHA。

本轮程序化核对journal schema/state、四项bindings、runtime/bootstrap、old/retired/replacement receipts、时间顺序、确定性重建与实际source verifier，共20项，结果为 `20/20 true`。

## 新 active gate 的确定性与实际有效性

本轮从pre-lock retired gate读取原payload，并以当前replacement verdict、bindings中的replacement verdict SHA和frozen SHA调用 `lock_refresh_source_control_gate()`。所得确定性对象与新active gate逐字段完全相等。

新 gate具有schema `m9-source-control-recovery-gate-v1`、decision `D-017-source-control-recovery-v1`、status PASS、blocking 0、non_blocking 0和scope `ONE_TIME_SOURCE_CONTROL_RECOVERY`。其audit report指向replacement structured verdict并绑定SHA `8a329ec9edce4a1c1b984ec561847cfce0ed4493e4b6dedb404fc8a9b816c739`；frozen SHA为 `af86278da0cf6d68330f065dd8fbe50963b04b5c9c5b198f4cce5d2e0442e21d`；authorization SHA为 `6b3e7a714a0adc8f00d56a45b5cedba99cbf941287109666cb1aac74bcf72da1`。

以root和冻结Python实际调用 `verify_source_control_recovery_gate_and_hashes()`，返回payload与active gate完全相等。verifier同时确认structured PASS verdict、authorization、18项frozen闭集及控制目录闭集。该调用只读取对象，没有执行recovery。

## Runtime、既有 disposition 证据与无越权产物

五项正式runtime SHA保持：

- state：`1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`
- workflow：`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`
- failed transaction：`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`
- ledger：`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`
- stale capability：`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`

此前disposition journal保持SHA `e97dc9b00a798f5a26807e5af18c78c2779be4ab144adeaa39f5be4338dc8ece`、root:root、0600、nlink 1；closed-set-invalid retired gate保持SHA `6bdd2fdbff6df6a7a8cfa1ba3cda038ca7cfe96b3b5dfb48905ef0f5151f5821`、1711 bytes、root:root、0600、nlink 1。两项均被refresh runtime和journal context继续绑定。

`budget.lock` 保持UID/GID1000:1000、0644、nlink 1、0 bytes、inode50700和空文件SHA `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。

failed transaction仍为transaction ID `e5bfc046d4d5a1bd97507d37b40f1e0c`、`FAILED_COMMITTED`、action `source_prepare`、exit code 1、reason `overlap_command_failed`。ledger tip仍为同transaction ID/reason的 `OVERLAP_HARD_STOP`。

stale capability仍为 `BOUND`、action `source_prepare`、同transaction ID、UID/GID1000:1000、0600、nlink 1；budget PID294和child PID373均不存在。对应 `.consumed.json` 与 `.launcher-receipt.json` 缺席。

source recovery transaction和parent均缺席。六项source/build产品 `openmx-overlap-build`、`openmx-overlap-build.staging`、`env/hdf5-1.12.1`、`openmx_official_3.9.9_tree_manifest.json`、`openmx_overlap_tree_manifest.json`、`openmx_overlap_build_manifest.json` 均缺席。因此除refresh规范内的journal、pre-lock retired gate和replacement active gate外，没有观察到recovery、capability消费、source解包、HDF5安装、OpenMX build或相关manifest产物。

cleanup retired对象、retirement receipt、cleanup journal、cleanup gate/root snapshot和security migration继续保持SHA `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`、`74b24867d06a437f0e693c8edd231ab4bc31782b8978abfff77b01658567fd49`、`1e0729d72bb7e45e773a61d9aff6228061a5b000cd218c23e5263153f2425d8d`、`12cec1f13eec81c110b8a7d66aecaf4e1786c0821c82a702885b9e74cfeb57b2`、`60fef9c099bfc345973bb9ac074f084f48e5e542508681fa4d55ceb099ba5c94`。

## 回归与后置不变性

冻结Python以 `-I -S -B` 重跑正式测试，结果为 `Ran 82 tests in 16.430s`、`OK`、退出码0。测试前后active gate、pre-lock retired gate、refresh journal、lock、五项runtime、disposition证据和cleanup证据的SHA均不变；recovery transaction/parent及capability consumed/launcher receipt仍缺席。`06_reproduction`内cache对象合计为0。

## 一次性 recovery 授权的消费边界

当前证据链由以下部分组成：用户明确语句“授权执行一次性 source-control recovery”；D-017 source-control recovery decision；`AUTH-M9-SOURCE-CONTROL-RECOVERY-2026-08-14-01` 授权记录；第32次零问题lock-refresh控制包审计；本次零问题refresh执行事实审计；当前实际PASS source-recovery gate；以及未漂移的failed transaction、runtime、stale capability和产品缺席现场。

该链已构成执行一次 `overlap-recover-source-control-failure` 的充分、精确授权。执行必须满足：

- root身份和冻结Python `-I -S -B`；
- 执行前实际 `verify_source_control_recovery_gate_and_hashes()` 返回当前active payload；
- active gate仍为SHA `381c8fd6e9fa28479de4f2144e975ed32756af9ac9dfe90a6d5457208da1cefa`、1728 bytes、root:root、0600、nlink 1；
- 五项runtime、failed transaction ID/state/reason、BOUND capability receipt与PID死亡条件仍匹配；
- recovery transaction/parent、consumed/launcher receipt及六项source/build产品仍缺席；
- 仅调用一次 `overlap-recover-source-control-failure`，完成后立即停止。

该授权允许恢复source-control状态机、退役旧stale capability、提交新一次性capability并完成相应ledger/state/workflow恢复事务。它不允许消费新capability来运行 `source_prepare`，不允许source build，也不允许GPU或其他M9动作。recovery执行结果必须另行独立事实审计；只有该审计和后续单独用户授权均满足时，才可讨论 `source_prepare`。

最终计数：`BLOCKING=0`，`NON_BLOCKING=0`。本报告未执行refresh replay、recovery或 `source_prepare`，未修改任何正式对象。
