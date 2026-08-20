# M9 D-018 无总墙钟期限迁移独立审计

## 审计结论

**FAIL**。`BLOCKING=6`，`NON_BLOCKING=0`。

当前送审实现不得用于创建正式 D-018 migration gate，也不得执行正式 `overlap-migrate-unlimited-wall-clock`。97 项自动测试全部通过，但这些测试未覆盖 ledger 部分追加、旧 gate inode 替换、迁移失败双硬停、D-017 后继门控和通用 `run` 授权逃逸，因此不能据此推出迁移满足授权边界。

本结论为独立审计结论。审计过程未创建正式 WSL gate，未执行正式迁移、`source_prepare`、`source_build`、smoke、batch 或 GPU 动作，也未生成结构化 PASS verdict。

## 审计对象与冻结一致性

送审核心对象的实测 SHA-256 与冻结值一致：

| 对象 | SHA-256 |
|---|---|
| `06_reproduction/scripts/m9_budget.py` | `eb8e061dd3d894c6aa0b8f8a0d240b625592785cf10e105bb5e5a235faaf48c2` |
| `06_reproduction/scripts/m9_overlap_common.py` | `088943ea5325f631bd10ab9d4dc2321a7d2075423be1f1fb6070188935e70c23` |
| `06_reproduction/scripts/m9_overlap_executor.py` | `2ed8c12a1ad8b179aaecc18acb2ea84f9aae0887b3accb06f68c1951289a8de2` |
| `06_reproduction/tests/test_m9_overlap_controls.py` | `a85f48ec7ea2cbd445ca3566deb909291a824fde325d084ccf2494ea2b2aeca6` |
| `06_reproduction/manifests/m9_unlimited_wall_clock_frozen_hashes.json` | `c65f606bf977a5517a6ddae347ca8b193bbfb0b603a2bbceba0a5cb96a9d56ed` |
| `06_reproduction/manifests/m9_unlimited_wall_clock_contract.json` | `1aea2a64879c12c5847c1562e25e37a2af1796089dd0358ce056ff7e9220304a` |
| `08_audits/M9_unlimited_wall_clock_authorization.md` | `8655037c3dee93f4ae0f9819e7409ff373ff660ed110f8cee25cde68dddd7b9a` |
| `08_audits/M9_unlimited_wall_clock_migration_work_package.md` | `b42f9e83ec34502643725c20044f1b466d5f187fbeac87a3efd54cf646a17f70` |
| `06_reproduction/manifests/m9_overlap_frozen_hashes.json` | `223b6bb78c13ff20bbfc62fcbd154a4a113f7a4c51f967fbb04ea74ba7f36088` |

`m9_unlimited_wall_clock_frozen_hashes.json` 的 25 项成员闭集存在且哈希匹配。独立测试使用固定解释器 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B`，结果为 `Ran 97 tests in 30.810s`、`OK`。测试前后正式运行态哈希均为：

| 正式对象 | 测试前后 SHA-256 |
|---|---|
| `budget_state.json` | `00a32bd7f28ad26fa600c8abe9d0fa64efe57e410eacb82ad2d201fa9adc5439` |
| `overlap_workflow_state.json` | `bd895b2831c805c44a180012ece64bdda00744340768c7062e33b856069fda8a` |
| `budget_ledger.jsonl` | `dbc54580fc6e215319c3af8d33b7f803448baa50a928ee4a60151782c9fd5e3b` |
| `overlap_transaction.json` | `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309` |
| `overlap_source_control_recovery.json` | `e9b8babcff8a2f42adea21d5cbce614b38f0854271d3389eae0bbcdd7d5e53bc` |

正式 D-018 gate、transaction、journal、pre-state snapshot 和 retired old gate 在测试前后均不存在；控制脚本目录未出现 `__pycache__`、`.pyc` 或 `.pyo`。因此，本次审计本身满足正式状态零写入要求。

## 阻塞项

### D018-B01：D-018 ledger 部分追加不能续提

`command_migrate_unlimited_wall_clock()` 在 `NEW_GATE_CREATED` 阶段直接调用 `append_event_once()`。该路径会先用 `ledger_event_ids()` 解析完整 ledger；若进程在 ledger 的一次 `write(2)` 已写入事件前缀、但尚未完成或尚未提交 journal 时终止，下一次执行会因末行不是完整 JSON 而在解析阶段失败。仓库已有 `resume_partial_existing_append()`，但 D-018 迁移函数没有调用该函数。

现有崩溃窗口测试只在各 journal 状态写入前抛出 Python 异常。它没有制造真实的部分 `O_APPEND`、进程终止或末行前缀，因此没有验证工作包要求的“partial append resume”。此外，如果完整事件已经存在而 journal 仍停在 `NEW_GATE_CREATED`，`append_event_once()` 直接返回，不再验证事件之前的 ledger prefix 是否仍等于迁移前冻结 prefix。

影响是一次允许的迁移可能把既存 ledger 留在不可解析且不可续提的状态，或在 replay 时接受已变化的历史 prefix。这违反 existing-only、exactly-once、prefix 保留和 crash-resumable 条件。

修复验收应至少包括：D-018 专用的 exact-prefix/exact-event/partial-event 三态判定；只允许回滚冻结事件的严格非空真前缀；完整事件存在时仍验证冻结 prefix；真实短写及写后 journal 前终止测试；终态 replay 零写入。

### D018-B02：旧 overlap gate 归档未绑定原 inode，存在 TOCTOU

迁移在创建 journal 时读取旧 gate receipt，随后在 `PREPARED` 阶段再次读取并比较 receipt，再调用路径级 `os.replace()`。receipt 只包含 path、bytes、SHA-256、UID、GID、mode 和 nlink，不含 `st_dev` 与 `st_ino`；迁移后的 retired receipt 比较同样不含 inode。

正式旧 gate 当前为 UID1000、0644，所在目录为 `root:evan-williams/1770`。UID1000 仍可改写或替换自己拥有的旧 gate；`budget.lock` 只约束协作进程，不能阻止路径外并发替换。因此，旧 gate 可在最后一次读取与 `os.replace()` 之间被换成另一 inode。只要字节和元数据相同，迁移会接受该替换，并错误声称 retired 对象保持了原 inode 身份。

这不满足工作包明确规定的“字节、inode 身份、owner、mode 和单链接属性”保留，也不满足送审要求中的 old-gate TOCTOU 防护。

修复验收应绑定原对象和 retired 对象的 `st_dev/st_ino`，并加入读取后、rename 前同字节换 inode 的故障注入测试。检测到替换时必须拒绝并进入规定的失败状态，不能形成成功事务。

### D018-B03：迁移后的 `source_prepare` 绕过原 D-017 gate 与迁移执行事实门控

`command_overlap_run()` 在状态为 `UNLIMITED` 时只调用 `verify_unlimited_wall_clock_execution_ready()`；该分支优先于 `recovered_from_source_prepare_control_failure` 分支，因此不会再调用 `verify_source_control_recovery_gate_and_hashes()`。`validate_overlap_request()` 对 `source_prepare` 仅检查 workflow stage 和 `apt_install_completed`，没有恢复 D-017 结构化 gate、recovery transaction 或独立执行事实审计的验证。

D-018 transaction 虽然包含 `pre_runtime`，其中记录 source-control recovery transaction SHA，但 `verify_unlimited_wall_clock_execution_ready()` 不校验 transaction 的 `pre_runtime`，也不重新校验当前 D-017 transaction/gate。合同声明的 `source_prepare_requires_separate_execution_fact_audit=true` 也没有对应的可执行 gate。

因此，D-018 完成后技术路径不再保证 `source_prepare` 受原 D-017 gate 和迁移后独立事实审计约束。这违反既定依赖顺序与用户授权边界。

修复验收应使 unlimited 路径组合验证而非替代 D-017：验证 D-018 终态、原 D-017 gate/recovery transaction 的冻结绑定，以及迁移执行事实独立零问题 verdict/gate；在该事实 gate 缺失时，`source_prepare` 必须在任何正式写入前拒绝。

### D018-B04：通用 `run --bucket none` 在 UNLIMITED 下形成无 CPU 计量、无 timeout 的任意命令通道

非 overlap 的 `command_run()` 接受任意 `args.command`。D-018 状态下 `deadline_remaining()` 返回 `None`；当 `--bucket none` 时，`timeout_seconds` 保持 `None`，子进程可无期限运行。该路径既不使用 overlap CPU bucket，也不增加 `cpu_seconds`，且不验证 D-017/D-018 overlap gate、action API、workflow stage 或命令 allowlist。

这意味着迁移后可以通过通用 `run --bucket none -- <任意命令>` 执行未计入 CPU 预算的任意编译或计算，绕过 `source_build`、smoke、batch 的依赖顺序与授权。取消总墙钟因而被转化为新增的无限 CPU 执行能力，与“不重置或增加 CPU 预算”直接冲突。

修复验收应在 D-018/overlap-only 路线中关闭通用任意命令入口，或把每个允许命令映射到冻结 action、对应 CPU bucket、workflow stage、forecast 和 gate。应增加明确证明 arbitrary build/smoke/batch command 在任何 `--bucket none` 组合下零写拒绝的测试。

### D018-B05：迁移异常没有 budget/workflow 双硬停提交

`command_migrate_unlimited_wall_clock()` 没有覆盖事务主体的失败捕获与持久化失败提交。旧 gate 已归档、新 gate 已创建、ledger 已追加或 state 已迁移后的任一校验或 I/O 异常都会直接退出；函数不会把 budget state 与 overlap workflow 同时标记为 hard-stopped，也不会形成绑定首错原因的失败事务。

虽然若干不完整终态会被后续 verifier 拒绝，但“被 verifier 拒绝”不等于按合同提交双硬停。尤其在 `STATE_COMMITTED` 后，预算状态已经是 UNLIMITED，仍必须依靠缺失 transaction 的间接拒绝；正式状态本身不记录首错与硬停止事实。

这违反送审要求中的失败双硬停与首错证据保留。现有 D-018 测试只验证异常后可以续提到成功，没有验证不可恢复异常、双硬停、首错唯一性和失败 replay。

修复验收应区分可安全续提的模拟断电与确定性校验失败；后者必须以 crash-resumable 方式同时提交 budget/workflow hard stop、首错 ledger 事件和失败 transaction，并加入每个持久化阶段的故障矩阵及终态 replay 测试。

### D018-B06：终态 verifier 未验证关键历史证据与事件 payload

`verify_unlimited_wall_clock_execution_ready()` 只验证 transaction 的 schema/state/identity/policy/gate receipt、当前 state policy、active replacement gate 以及 ledger 中存在指定 event ID。它没有验证：

- root-private migration journal 为 `SUCCESS_COMMITTED` 且 context 未漂移；
- pre-state snapshot 仍存在并匹配冻结 state；
- retired old gate 仍存在且匹配 transaction/journal receipt；
- transaction 的 `pre_runtime`、`pre_state_snapshot`、`retired_overlap_gate`、`replacement_overlap_gate`、`ledger_sha256`、`migrated_state_sha256` 和 `journal_context_sha256`；
- ledger 事件 payload 是否等于 D-018 确定性事件，而不仅是 event ID 存在；
- 迁移前 ledger prefix 和迁移后 ledger 整体 SHA 是否匹配 root-owned transaction 所记录的值。

正式 ledger 为 UID1000、0644；仅检查 event ID 存在不能防止同 ID payload 或历史 prefix 被改写。终态 verifier 因而可能在 retired gate、journal、snapshot 或 ledger 证据丢失或漂移时仍放行后续动作。

这违反“保留全部历史用量与证据”、retired gate 保留、ledger prefix 和 exactly-once payload 绑定要求。

修复验收应把上述终态字段纳入严格闭集验证，确定性重建并核对 event payload/hash，验证冻结 prefix 与迁移后完整 ledger，并对 journal、snapshot、retired gate、transaction 每个字段的删除和漂移加入零写拒绝测试。

## 已满足但不足以放行的条件

送审实现确实把 `start_utc`、`deadline_utc` 和 604800 秒保留为历史字段；在正常无故障测试路径中，state 由 pre-state snapshot 复制，只新增 D-018 policy 并更新 `last_event_utc`。CPU/GPU/存储常量与合同中的 unchanged limits 一致；overlap action 的 CPU timeout 在 unlimited 状态下仍取所属 CPU bucket 的剩余量；迁移函数本身没有直接调用 source/build/smoke/batch/GPU 子程序；source/build 六项产物在正式运行态缺席。

这些正向证据只能说明正常路径的主要数值语义基本正确，不能消除上述授权逃逸、证据链和崩溃恢复缺陷。

## 复核门槛

主 agent 应修复 D018-B01 至 D018-B06，更新受影响代码、测试、合同、工作包和两组 frozen manifest，并提交同一独立审计员进行定向复核。复核必须得到 `PASS`、`BLOCKING=0`、`NON_BLOCKING=0` 后，方可生成结构化 verdict、创建正式 D-018 gate 并执行一次迁移。

