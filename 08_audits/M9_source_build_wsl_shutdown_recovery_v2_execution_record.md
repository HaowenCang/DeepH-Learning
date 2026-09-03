# M9 source_build WSL shutdown recovery v2 主端执行记录

日期：2026-09-03。记录角色：主 agent。本记录只陈述机械 preflight、唯一 recover 及其后只读回读，不替代独立执行事实审计，不构成新的 source_build、permit、数据、训练或物理验证授权。

## 前置门控与冻结权威

v4 非终态中断已由独立审计判为 `FAIL / BLOCKING=1 / NON_BLOCKING=0`，阻塞项为 `M9-SB-V4-INT-B01`。恢复 v2 首轮实施审计的 `FAIL/BLOCKING=2/NON_BLOCKING=1` 保持不改写；修订后独立定点复核为 `PASS / BLOCKING=0 / NON_BLOCKING=0`。主端在执行前逐字复算下列入口，均与冻结值一致：

| 对象 | SHA-256 |
| --- | --- |
| 恢复控制器 | `21cf81c6a63218a6e1de23bf14e2e9d928eb413fd5529a2d18d0b8859d3a1801` |
| 恢复 frozen manifest | `139fb44a695873f1771fa05bd15bc28a9ac348ee2f6fc8a567080c7e920b1e62` |
| 严格 final verdict | `9f9331d5ca762f4fb54325a54fe21c9b7d4955d84856598d143e965f2f730fc9` |
| 独立定点复核报告 | `f39e977092fc5b141507542828fdacb6a045b343a1aebf23a2e95f252fde54f4` |
| single-FD loader 所在旧工作包 | `dc1d0d992f7e1328f79a4436eb4535b79ba2ab48fcee1b44fa498c31c30e91a2` |

恢复 frozen manifest 的十二个成员逐项复算无漂移。root 启动沿用旧替代 consumer 工作包中唯一 Python 代码块；按历史规则规范为 LF 并去除代码块终止换行后为 1,253 bytes，SHA-256 为 `c68e43b5de4fdadb44254fbfdd543f5ba2a29b6e41994021c55a3287b5f7491f`。第一次宿主预核验采用保留终止 LF 的候选，得到 `7ef52c014e29a7abbb462e63199665179f3a7d57e85337712364620741470cb4` 后即在 PowerShell 内停止；该候选没有启动 WSL 或恢复控制器，不计作 preflight/recover 调用。随后恢复到既有 1,253-byte 规则并命中审计固定哈希。

实际解释器为 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9`，以 Ubuntu-22.04、root、`-I -S -B` 启动。loader 后的参数依次为：

```text
/mnt/e/Projects/Codex/DeepH/06_reproduction/controllers/m9_source_build_wsl_shutdown_recovery_v2.py
21cf81c6a63218a6e1de23bf14e2e9d928eb413fd5529a2d18d0b8859d3a1801
ACTION
139fb44a695873f1771fa05bd15bc28a9ac348ee2f6fc8a567080c7e920b1e62
9f9331d5ca762f4fb54325a54fe21c9b7d4955d84856598d143e965f2f730fc9
f39e977092fc5b141507542828fdacb6a045b343a1aebf23a2e95f252fde54f4
```

`ACTION` 依次为 `preflight`、`recover`，各调用一次。任一命令的宿主会话均在原句柄内等待至完成，没有因超时或无输出而重启。

## 正式调用结果

唯一 preflight 始于 `2026-09-03T03:00:36.9001821Z`，止于 `2026-09-03T03:01:13.4851022Z`，宿主退出码为 0，原始 JSON 返回：

```json
{"elapsed_upper_bound_seconds": 138.401802566, "forecast_bytes": 1073741824, "source_build_authorized": false, "status": "PREFLIGHT_PASS", "writes": 0}
```

唯一 recover 始于 `2026-09-03T03:01:31.9737727Z`，止于 `2026-09-03T03:02:31.0852919Z`，宿主退出码为 0，原始 JSON 返回：

```json
{"clean_portable_sha256": "cf91d95aa8802925da676dab35fe5bb991a6061f809b871bca488f4c50347cc0", "elapsed_upper_bound_seconds": 138.401802566, "journal_sha256": "9ba4f235a9a4c4fb543ddf8ae47141b5d1c3cdddc592843dc187d22e0c234677", "runtime_sha256": {"/home/evan-williams/deeph-m9/manifests/budget_ledger.jsonl": "24253c63284171f826b6b068053e8bd7fe1fd1a8e2feadbca3f5885f4443ed8b", "/home/evan-williams/deeph-m9/manifests/budget_state.json": "c45337d97584abbce0c885ca233d9fd9bd9b548d17847a52a7f1b398fc9c1dec", "/home/evan-williams/deeph-m9/manifests/overlap_transaction.json": "cf17e84abf1303438220ad3a872375e779de19052a10cf2cee41055f0d04ed91", "/home/evan-williams/deeph-m9/manifests/overlap_workflow_state.json": "96778c2501f2d7eca33b973266e4a8e33e22bc65238cd0b9f12d014a3c5c7aa7"}, "source_build_authorized": false, "status": "RECOVERY_SUCCESS_COMMITTED"}
```

没有执行第二次 recover，也没有调用旧 v4 permit、operation、capability、launcher 或构建命令。

## 恢复后主端只读回读

四份运行态的实际 SHA-256 与 recover 返回完全一致。`budget_state.json` 为 `hard_stopped=false`、`active_overlap_transaction=null`，并新增 `recovered_from_source_build_wsl_shutdown=m9-source-build-wsl-shutdown-recovery-20260902-01`；所有旧恢复标记、D-017 抵扣及 GPU、smoke、batch 历史均保留。`overlap_build` 原始累计从 `7507.245045788001` 增至 `7645.646848354001` 秒；减去既有 `7200.075310528` 秒抵扣后为 `445.571537826001` 秒，没有重置或增加预算。

`overlap_workflow_state.json` 为 `hard_stopped=false`、`active_transaction=null`、`stage=SOURCES_PREPARED`。事务 `d52575f446d3c62f0fc93c3c65f3c959` 已成为 `FAILED_COMMITTED`，`end_utc=2026-09-01T14:49:10.512965566Z`、`elapsed_seconds=138.401802566`、`elapsed_semantics=conservative_wall_upper_bound_not_measured_cpu`、`exit_code=null`、`timed_out=false`，唯一 reason 为 `wsl_shutdown_external_interruption`。

ledger 为 70,635 bytes、69 行，SHA-256 `24253c63284171f826b6b068053e8bd7fe1fd1a8e2feadbca3f5885f4443ed8b`。相对 68,599-byte、SHA `f3f44ee5169bbeb44d175ff0aa381cda70684ad66f11ce57725c2e774471d4c7` 的原前缀恰增加一条 2,036-byte `SOURCE_BUILD_WSL_SHUTDOWN_RECOVERY` 事件；事件 ID、父事务、138.401802566 秒计量、D-019、frozen、实施 verdict/report、中断证据和 v4 preexecution 证据均已绑定。

树与控制对象的只读 receipt 如下：

| 对象 | 项数 | canonical SHA-256 / 关键事实 |
| --- | ---: | --- |
| 新 BUILD | 5,319 | `c9ac7a5cb34ef582ce06965d568a6fe0ded9ef4f2a51e2c07ab1e5e1898f1521`；portable SHA `cf91d95aa8802925da676dab35fe5bb991a6061f809b871bca488f4c50347cc0` |
| 新中断归档 | 7,621 | `9210f3c37f6b328691b4bed963ee11f57fb481ba48242d2450b8d7df4e174e9f` |
| 新日志归档 | 4 | `9ad2f041ace0a8c712febc81b086dff58e6b688155f755c73dd7e32c9658de96` |
| 干净退休来源树 | 5,319 | `060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359` |
| 上一轮中断归档 | 7,640 | `82bc6705ef8a507d2580630592f4903726622768aebb5bd7b1d22d93afa12515` |
| 上一轮日志归档 | 4 | `5ea65a500eaadc665b4d282ce8b8c55019629b722020b7baa73259c9f862d4de` |
| 恢复后正式 namespace | 301 | `5153de04dd6a33f8851cd898d8af9c8e655a57a161d31f70a7f60dc8032c0f42` |

新 BUILD 与干净退休来源树的普通文件 `(dev,inode)` 交集为 0。当前 `logs/overlap-build` 和恢复 staging 均缺席；新归档路径存在。root-private 控制目录为 root:root/0700，含 20 个成员；journal 为 `SUCCESS_COMMITTED`，九个阶段顺序完整，SHA-256 为 `9ba4f235a9a4c4fb543ddf8ae47141b5d1c3cdddc592843dc187d22e0c234677`。公开 snapshot 为 root:group1000/0550，含 4 个成员且不携带执行许可。

consumed capability、v4 gate、旧 permit 的 SHA-256 分别仍为 `8d6aff34eec0ee29ce8a7b8e6a8fdf8a76b78ec1fe5a5bd584ee1e2587607204`、`dcd0a0ed3307add49df5b7586ba0bf01b2fc55b0469a42067893e563ba2ff3c1` 和 `c3aae6ff0c5aaffb3d5a711b48e7dc505061959eb144509995f8e9890f5853d4`；launcher receipt 仍缺席。冻结证据列出的 HDF5 final prefix、两个 OpenMX manifest 和三个 OpenMX 可执行产品均缺席。

## 门控状态

主端机械结果为成功提交，但本记录不能自行判定执行事实门控通过。下一步只能由独立子 agent 对正式 301 项 namespace、运行态目标、ledger 原前缀与唯一追加、两棵归档和新 BUILD、无硬链接复制、PRIVATE/journal/snapshot、禁用产物、旧 v4 回放阻断以及预算保持进行只读事实审计。该审计给出 `PASS / BLOCKING=0 / NON_BLOCKING=0` 前，不得建立或消费新的 source_build gate/permit，也不得进入 structure 500 smoke、450 结构 batch、训练或物理验证。

## 独立执行事实审计跟进

独立子 agent 已完成正式执行事实审计并在主端发现 capability 摘要转录矛盾后完成事实更正。首版错误值不再作为 PASS 证据；正式对象从 4,513 bytes 复算得到 consumed capability SHA-256 `8d6aff34eec0ee29ce8a7b8e6a8fdf8a76b78ec1fe5a5bd584ee1e2587607204`、state `CONSUMED`。审计员对两份产物全部摘要字段重新复算，未发现第二处错误。

最终更正版判定为 `PASS / BLOCKING=0 / NON_BLOCKING=0`。报告 [M9_source_build_wsl_shutdown_recovery_v2_execution_independent_audit.md](M9_source_build_wsl_shutdown_recovery_v2_execution_independent_audit.md) SHA-256 为 `4d1d8b20327256b807203861f69e850d104858bc86a13e77dde77dff8f2c9e4b`；完整证据 [M9_source_build_wsl_shutdown_recovery_v2_postexecution_evidence.json](M9_source_build_wsl_shutdown_recovery_v2_postexecution_evidence.json) SHA-256 为 `b3477ede6590cda56d5cf45bb1a16809e591d6aa5858531807f5cc1513eaca36`。独立结论确认一次成功恢复提交；同时明确持久态不能证明零写 preflight 的调用次数，也不能证明首写前被拒绝的 recover 尝试次数。恢复执行事实门控现已通过，但仍不等于构建通过，也不直接签发下一次 source_build 权限。
