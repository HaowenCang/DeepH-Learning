# M9 D-018 无总墙钟期限迁移定点复核

## 复核结论

**FAIL**。`BLOCKING=3`，`NON_BLOCKING=0`。

D018-B01—B06 的主要直接修复已经实现，但独立穿透检查发现三个未被 104 项测试覆盖的持久化或 verify-to-use 时序缺陷。当前版本仍不得用于创建正式 D-018 migration gate，不得执行正式 `overlap-migrate-unlimited-wall-clock`，也不得生成结构化 PASS verdict。

本次复核只新增本报告；未创建正式 WSL gate，未执行正式迁移、`source_prepare`、`source_build`、smoke、batch 或 GPU 动作。

## 冻结对象与独立验证

下列核心 SHA-256 与送审冻结值一致：

| 对象 | SHA-256 |
|---|---|
| `m9_budget.py` | `c2b23dba54593cbf004366a4407a5123bb05e80b935cec4109c1d367e09f9045` |
| `m9_overlap_common.py` | `b29c1bc550060c0faaef664a8b52371ff0b3f06061e2089194293278368c5507` |
| `m9_overlap_executor.py` | `2ed8c12a1ad8b179aaecc18acb2ea84f9aae0887b3accb06f68c1951289a8de2` |
| `test_m9_overlap_controls.py` | `539f4a0177a10adc886854ded52f096e855c2b4e776783ecb6c299cef615285e` |
| `m9_unlimited_wall_clock_contract.json` | `4d33f628b6074508538291a753f84e871c21fd20682432eab92ae16972938b0c` |
| `M9_unlimited_wall_clock_migration_work_package.md` | `5b807dca335eb605a6cf2af2c5f4f1db22fd4dab7ea58ba9b8801f5bff44b3b3` |
| `m9_overlap_frozen_hashes.json` | `565a879451c9b656506ff1744166a1b05587650fe046e956228990db3e3f20b1` |
| `m9_unlimited_wall_clock_frozen_hashes.json` | `25107ce6bead0828ecce442923b8186b4a05c49a42ffe47c1335231ef20d1444` |
| 首次独立审计报告 | `9958cc768ee1dc55251216cf9207d6863defdba3ad374155fb8a6e88fec3d59b` |

独立枚举结果为 D-018 frozen manifest `26/26`、overlap frozen manifest `16/16`，成员均存在且哈希匹配。固定解释器 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 独立重放得到 `Ran 104 tests in 35.338s`、`OK`。

测试前后正式运行态七项 SHA-256 均保持不变：

| 正式对象 | SHA-256 |
|---|---|
| `budget_state.json` | `00a32bd7f28ad26fa600c8abe9d0fa64efe57e410eacb82ad2d201fa9adc5439` |
| `overlap_workflow_state.json` | `bd895b2831c805c44a180012ece64bdda00744340768c7062e33b856069fda8a` |
| `budget_ledger.jsonl` | `dbc54580fc6e215319c3af8d33b7f803448baa50a928ee4a60151782c9fd5e3b` |
| `overlap_transaction.json` | `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309` |
| `overlap_source_control_recovery.json` | `e9b8babcff8a2f42adea21d5cbce614b38f0854271d3389eae0bbcdd7d5e53bc` |
| `overlap_source_control_recovery_gate.json` | `8e66d65d17d3195f3df09db954afca4066c3ec91e2d8dad6d2aea06078d0d5ce` |
| `overlap_work_package_audit_gate.json` | `dbe4756142d0e921c3834330550310e85652503c04254b30bea1a069ff35377c` |

正式状态仍为 LIMITED 且仅有 `wall_clock_limit`；D-018 migration gate、transaction、execution gate、journal、snapshot、retired gate 及六项 source/build 产物仍缺席。控制目录未产生 cache 文件。

## 原问题定点状态

| 原问题 | 复核状态 | 依据 |
|---|---|---|
| D018-B01 ledger 部分追加 | 直接路径已修复 | `commit_exact_existing_ledger_event()` 区分 exact prefix、严格真前缀、完整事件；独立短写测试通过。仍需随下述持久化时序修复后回归。 |
| D018-B02 old-gate inode/TOCTOU | 直接路径已修复 | receipt 纳入 `st_dev/st_ino`；同字节换 inode 被检测并进入失败提交。 |
| D018-B03 D-017 与执行事实门控 | **未完全关闭** | 证据绑定函数与 execution fact gate 已增加，但校验发生在获取正式锁之前，存在陈旧授权使用窗口，见 D018-R02。 |
| D018-B04 通用任意命令通道 | **未完全关闭** | UNLIMITED 直接拒绝已增加，但模式检查发生在获取正式锁之前，迁移并发可使锁内执行使用不同状态，见 D018-R03。 |
| D018-B05 迁移失败双硬停 | **未完全关闭** | `commit_d018_failure()` 覆盖已有 journal 的失败；snapshot 已写而 journal 尚未创建的窗口仍不可续提且不双硬停，见 D018-R01。 |
| D018-B06 终态证据绑定 | 终态字段直接检查已修复，但 use-time 仍不完整 | journal 闭集、snapshot、retired inode、ledger exact bytes、state、transaction 与 D-017 证据均被核对；然而验证结果未与后继锁内状态原子绑定，见 D018-R02。 |

## 阻塞项

### D018-R01：pre-state snapshot 先于 PREPARED journal 提交，形成不可续提孤儿窗口

首次迁移在持有 `budget.lock` 后先执行 `atomic_root_private_bytes(UNLIMITED_WALL_CLOCK_PRE_STATE_SNAPSHOT, state_bytes)`，随后读取旧 gate inode、构造 journal，最后才提交 `PREPARED` journal。若进程在 snapshot 已 durable commit 后、journal 创建前终止，或旧 gate inode 读取在该位置发生确定性失败，则正式状态为“snapshot 存在、journal 不存在”。

下一次入口在 journal 缺席分支中明确因 `D-018 state snapshot exists without journal` 拒绝。外层异常处理又以 journal 是否存在作为进入 `commit_d018_failure()` 的前提，因此既不能续提成功事务，也不会提交 budget/workflow 双硬停和失败 transaction。

独立故障注入在 snapshot 提交后令旧 gate inode 读取失败，实测结果为：

```text
exit injected-after-snapshot
snapshot True journal False tx False
state_hard False workflow_hard False
```

这说明现有 104 项测试覆盖了五个后继 journal 状态和真实 ledger 短写，但没有覆盖首个 durable snapshot 与 PREPARED journal 之间的窗口。该缺陷违反 crash-resumable 和“正式写入后的确定性失败必须形成可审计终态”要求。

修复验收应使第一个 durable 事务对象足以唯一恢复 snapshot 创建。可采用先提交包含预期 state receipt 的 PREPARED journal，再幂等创建并回填 snapshot receipt，或增加严格绑定的 pre-journal 恢复对象。必须新增 snapshot 写后、journal 写前的模拟断电和确定性失败测试，分别证明同事务续提及唯一双硬停失败提交。

### D018-R02：overlap gate 与执行事实 gate 在取锁前验证，锁内可能使用陈旧授权

`command_overlap_run()` 先读取 state/workflow，调用 D-018 terminal verifier 和 execution fact gate verifier，随后才以 `LOCK_PATH.open("a+")` 获取 `budget.lock`，并在锁内重新加载 state/workflow、验证 action 与启动事务。门控验证结果没有携带到锁内进行同一 runtime receipt 的复核，也没有绑定本次请求的 action。

因此存在不要求越权编辑的合法控制器并发：一个 `source_prepare` 进程和一个后继 `source_build` 进程都可在迁移后事实 gate 的原始 runtime 上完成锁外验证；`source_prepare` 先取得锁并把 workflow 推进到 `SOURCES_PREPARED`，等待中的 `source_build` 随后取得锁，按新 stage 通过 `validate_overlap_request()`，却使用了先前 scope 为 `ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018` 的陈旧验证结果。类似地，在 migration 与 UID1000 overlap 入口交错时，入口可在 LIMITED 状态验证旧 gate，等待 root 迁移释放锁后在 UNLIMITED 状态继续，而未验证 post-migration execution fact gate。

这使 B03 的“事实 gate 缺失时零写拒绝”和 B06 的“完整 runtime 绑定”只在校验瞬间成立，未绑定到实际使用时刻。现有测试只模拟 verifier 立即失败及 runtime 静态漂移，没有覆盖 verifier 返回后、取得锁前的状态推进。

修复验收应在持有既存 `budget.lock` 的同一临界区内读取 wall mode、验证 D-018/D-017/execution-fact runtime、绑定请求 action 与 gate scope、再次读取相同 runtime receipts，然后才允许创建 overlap transaction。应增加 migration-versus-source_prepare、source_prepare-versus-source_build 两组确定性交错测试，证明陈旧 gate 不能产生任何正式写入或子进程。

### D018-R03：通用 `run` 的 D-018 禁用检查位于取锁前，迁移竞态可重新开放任意命令

非 overlap `command_run()` 在获取 `budget.lock` 前读取 `pre_state` 并仅在该快照为 UNLIMITED 时拒绝；进入锁后重新加载 state，却不再检查 `wall_clock_policy_mode(state)`。随后 `violations()` 对已迁移的合法 UNLIMITED state 不产生 `wall_clock_limit`，因而会继续创建任意子进程。

存在直接的协作进程竞态：通用 `run` 在 root 迁移提交 state 前读取到 LIMITED，然后等待 root 持有的 lock；迁移完成后，`run` 取得锁并读取到 UNLIMITED。由于锁内没有重复禁用检查，该任意命令会绕过 B04 修复。此路径不依赖手工修改 state，也不依赖伪造 gate。

现有“all buckets zero-write rejection”测试只让首次 pre-state 已经是 UNLIMITED，没有测试 LIMITED precheck 与 UNLIMITED locked state 的交错。

修复验收应把通用 `run` 的 wall-mode 禁用判定移入持锁临界区，并确保从状态复核到 `Popen` 之间不存在可被另一个协作控制器改变的窗口。应加入 root migration 与 generic `run` 的确定性交错测试，对 `none` 和全部 GPU bucket 证明 Popen 未调用、state/ledger/workflow/transaction 零写入。

## 最终门槛

主 agent 应修复 D018-R01—R03，更新受影响代码、测试、工作包、合同及两组 frozen manifest，再交由同一独立审计员复核。只有后续复核达到 `PASS`、`BLOCKING=0`、`NON_BLOCKING=0`，才允许生成 `M9_unlimited_wall_clock_migration_final_verdict.json`、创建正式 D-018 migration gate并执行一次迁移。

