# M9 source_build 宿主关机中断恢复 v1 主端执行记录

日期：2026-09-01。主 agent 执行记录，不替代独立执行事实审计，不构成编译许可或下一次构建授权。

## 范围与前置权威

依据 [D-019 持续执行授权](../../00_scope/D019_standing_execution_authorization.md)（解释复核 PASS/0/0）、[中断独立事实审计](M9_source_build_v3_interruption_independent_audit.md)（INTERRUPTED_NONTERMINAL，BLOCKING=1）和 [恢复 v1 独立实施审计](M9_source_build_host_shutdown_recovery_v1_implementation_audit.md)（PASS/BLOCKING=0/NON_BLOCKING=0），主端执行了一次零写 `preflight` 和一次 `recover`，各一次，无重放。

主端执行前完整读回并逐项核验以下 SHA-256，全部与冻结值一致：

| 对象 | SHA-256 |
| --- | --- |
| 恢复控制器 | `4df3b47671b0d824631ed0acae27d8b1e1bea77c537794319d34c43e3944af8a` |
| 恢复 frozen manifest | `3334010925f97486f58b2b3116b52b6b4cc48f34d4c8e0e1ec801de577bbc668` |
| 实施 verdict 文件 | `77f86ea6aec7138aaced6b2bc66a4836482cd9f0509e4bdb5c41a6fe3806d95d` |
| 实施审计报告 | `fd1778bdbf3807f8ae25edeae7047c53dd4152bed7a1c12edca9d2c3bef5b518` |
| 工作包 | `a59ac5b95226c5e2eb1eaf99b17192db36656d80d750741779d3f056eb6c4b1e` |
| 中断独立报告 | `410468cea26e8d7359f400d3a3e1dbeb7723e2120560c89a2f093c0009d07104` |
| 中断完整证据 | `12907e82278f114e228c0b9e930564dafd18ab761159f70edd01ac2200f2f3d2` |

root 启动沿用旧替代 consumer 工作包中的唯一 single-FD loader：先核验工作包 SHA `dc1d0d992f7e1328f79a4436eb4535b79ba2ab48fcee1b44fa498c31c30e91a2`，提取其中唯一 Python 块并规范 CRLF 后核验 loader SHA `c68e43b5de4fdadb44254fbfdd543f5ba2a29b6e41994021c55a3287b5f7491f`；启动前在宿主侧再次重算 loader 字节，不从未验证字节启动。

## 精确启动及次数

WSL Ubuntu-22.04，root，固定 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B -c <loader>`。loader 后的固定参数如下，ACTION 依次为 preflight、recover，各调用一次：

```text
/mnt/e/Projects/Codex/DeepH/06_reproduction/controllers/m9_source_build_host_shutdown_recovery_v1.py
4df3b47671b0d824631ed0acae27d8b1e1bea77c537794319d34c43e3944af8a
ACTION
3334010925f97486f58b2b3116b52b6b4cc48f34d4c8e0e1ec801de577bbc668
77f86ea6aec7138aaced6b2bc66a4836482cd9f0509e4bdb5c41a6fe3806d95d
fd1778bdbf3807f8ae25edeae7047c53dd4152bed7a1c12edca9d2c3bef5b518
```

preflight 返回 `{"status":"PREFLIGHT_PASS","writes":0,"source_build_authorized":false,"elapsed_upper_bound_seconds":292.7759032,"forecast_bytes":1073741824}`，宿主退出码 0。随后 recover 单次调用直接完成，宿主退出码 0，返回 `RECOVERY_SUCCESS_COMMITTED`、`source_build_authorized=false`、`journal_sha256=4a15312a17cb5b74f27409f19f757d11eb486f999433f328723cc6b4051af566`。没有重复调用，没有为验证幂等性再次调用正式动作。

## 恢复后主端读回

| 对象 | bytes / 关键字段 | SHA-256 |
| --- | --- | --- |
| budget_state.json | hard_stopped=false；active_overlap_transaction=null；overlap_build 原始 7507.245045788001 秒 | `cdfcf813f1e6c4759b0a8ef93a76d95a50d6e586ba5f4652908f6b1dd375dd7b` |
| overlap_workflow_state.json | hard_stopped=false；active_transaction=null；stage=SOURCES_PREPARED | `271bd1c756b55db52b7cb479a7d679edb95e2d3bd33b21cfff88122f40459b34` |
| overlap_transaction.json | `4d7808af7df9418518a59afeba766eb9` 已版本化为 FAILED_COMMITTED，exit_code=null、timed_out=false、reasons=[host_shutdown_external_interruption]、elapsed_semantics=conservative_wall_upper_bound_not_measured_cpu | `433462132e40fd9f160bce150e20a7c3149227ad8bf4957e8d19d71e389ddb58` |
| budget_ledger.jsonl | 68,599 bytes = 原 66,755 前缀 + 恰一条 1,844-byte 恢复事件 | `f3f44ee5169bbeb44d175ff0aa381cda70684ad66f11ce57725c2e774471d4c7` |

四份运行态 SHA 与 recover 返回的 `runtime_sha256` 完全一致。state 与 workflow 均新增唯一恢复标记 `recovered_from_source_build_host_shutdown=m9-source-build-host-shutdown-recovery-20260901-01`，全部历史恢复标记、D-017 抵扣、D-018 无总墙钟策略、GPU 计数（compatibility 54.84820560599999 秒、training/physical_validation 为 0）、smoke/batch 计数 0 原样保留。新增计量 292.7759032 秒明确标记为宿主关机保守墙钟上界而非实测 CPU；D-017 抵扣后有效累计约 307.169735260000932 秒，7,200 秒额度余额约 6892.830264739999068 秒。

账本恢复事件绑定 D-019、frozen、实施 verdict/报告及中断证据 SHA；原 66,755-byte 前缀由 root-private `before-budget_ledger.jsonl` 归档保留。账本原始前缀及逐对象身份的正式结论以独立事实审计为准。

## 树、日志与产物

- 中断工作树已原子改名为 `software/openmx-overlap-build.interrupted-4d7808af7df9418518a59afeba766eb9.retired`，7,640 项；三份中断日志归档为 `logs/overlap-build.interrupted-4d7808af7df9418518a59afeba766eb9.retired`。
- 新工作树 `software/openmx-overlap-build` 从只读核验过的干净退休树复制，5,319 项，顶层为 `hdf5-source`、`openmx3.9`；干净历史树 `openmx-overlap-build.failed-80e28da82f076f4f7b1811f5897216bd.retired` 仍为 5,319 项。recover 返回 `clean_portable_sha256=cf91d95aa8802925da676dab35fe5bb991a6061f809b871bca488f4c50347cc0`。
- root-private 归档 `/root/deeph-m9-control/source-build-host-shutdown-recovery-v1` 为 root:root/0700，17 个 0600 文件（含 journal、全部 authority 载荷与四份 before 运行态）；journal SHA 与 recover 返回一致。
- 公开只读 snapshot `/home/evan-williams/deeph-m9/controls/source-build-host-shutdown-recovery-v1` 为 root:1000/0550，恰含 4 个 0440 成员（recovery_controller.py、interruption_evidence.json、interruption_report.md、snapshot_manifest.json），不携带执行许可。
- staging 临时路径不存在；HDF5 安装 prefix、OpenMX 二进制、build manifest、材料 run root 继续缺席。没有执行 configure、make、OpenMX、材料计算、训练、下载或 permit 动作。

## 后续边界

本次恢复只重建非 hard-stop 的 `SOURCES_PREPARED` 父态和干净工作树，**不等于构建通过**。旧 v3 permit、operation、已消费 capability 和原命令均不得重放。下一步须建立 v4 单次 consumer/launcher 与新 permit，绑定恢复后的新 runtime、已归档中断证据和新工作树，经独立实施审计、安装事实审计和执行前复核 PASS 后才可重新从 HDF5 配置开始构建。M9-DATA-B01 继续 OPEN；structure 500 smoke、450 结构 batch、训练和物理验证均未放行。正式执行事实审计结论另行封存。

## 独立执行事实审计跟进

独立子 agent 已完成正式执行事实审计，结论为 `PASS / BLOCKING=0 / NON_BLOCKING=0`。报告 [M9_source_build_host_shutdown_recovery_v1_execution_independent_audit.md](M9_source_build_host_shutdown_recovery_v1_execution_independent_audit.md) SHA-256 为 `41fc9940fa8f7ac66b7d8978e429e7b41c3f3f1753e2b2c37c59148f36829c78`；完整证据 [M9_source_build_host_shutdown_recovery_v1_postexecution_evidence.json](M9_source_build_host_shutdown_recovery_v1_postexecution_evidence.json) SHA-256 为 `42e05a042ab66c41b31e03ee9a126eec58a1480c382834bd07cd9244f88d602a`。

独立证据确认 244 项正式闭集、四份 runtime 精确目标、账本原前缀与唯一恢复事件、三棵树和日志归档、PRIVATE/journal/公开 snapshot、旧 v3 回放阻断、预算历史和禁用产物缺席均符合合同。成功改变状态的 recover 可由唯一事件、journal、archive 和重建树证明恰一次；零写 preflight 不留下正式持久痕迹，其历史调用次数不能仅由正式字节独立反推。该证据边界不影响恢复事实 PASS，但禁止把主端调用次数陈述扩张为可由持久态独立证明的事实。
