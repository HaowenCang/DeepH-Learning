# M9 D-018 无总墙钟期限迁移第二次定点复核

## 复核结论

**PASS**。`BLOCKING=0`，`NON_BLOCKING=0`。

D018-B01—B06 及第一次定点复核提出的 D018-R01—R03 均已关闭。允许主 agent 依据本报告和结构化 verdict 创建一次正式 D-018 migration gate，并执行一次 `overlap-migrate-unlimited-wall-clock`。该放行只覆盖无总墙钟迁移本身；迁移完成后必须立即停止，进行独立执行事实审计并建立相应 execution-fact gate。当前结论不直接授权 `source_prepare`、`source_build`、smoke、batch、GPU 动作或其他通用命令。

本次复核没有创建正式 WSL gate，没有执行迁移或任何 source/build/计算动作，只新增本报告及其结构化 PASS verdict。

## 冻结一致性

复核开始时固定的核心对象 SHA-256 如下，均与送审冻结值一致：

| 对象 | SHA-256 |
|---|---|
| `06_reproduction/scripts/m9_budget.py` | `25c92810de52229ff626b4d54f4bd2084453e2e834ff830232b8599033f6cce5` |
| `06_reproduction/scripts/m9_overlap_common.py` | `a58cea8676b1825e44a2c8dbda16c591c148c15f8a513d1ee96fb8ffe9e4b52e` |
| `06_reproduction/scripts/m9_overlap_executor.py` | `2ed8c12a1ad8b179aaecc18acb2ea84f9aae0887b3accb06f68c1951289a8de2` |
| `06_reproduction/tests/test_m9_overlap_controls.py` | `8fd7b0eafebbe0d58f1e7c13ba0d5ede9881efd9cb070ecaa0bf6ab648073e59` |
| `06_reproduction/configs/m9_overlap_only_contract.json` | `19290a2bfeaf46b35185f0f61f6ee5d8fb688f3c67fefa8430cd143391fee70b` |
| `06_reproduction/manifests/budget_contract.json` | `0d281270160b7a127ab99035fa6f54cd83d220bb15a029a690e70aea6b5bd7a0` |
| `06_reproduction/manifests/m9_unlimited_wall_clock_contract.json` | `2b451c42c2401a220d19038af2ee6ba1843106508f8b057b8ce5dd2584fccff4` |
| `08_audits/M9_unlimited_wall_clock_migration_work_package.md` | `e23d59ea673421e1b2ca4755b3ea91806c7c7ba04573141d2ebdf3ff40f80ef3` |
| `08_audits/M9_unlimited_wall_clock_migration_targeted_reaudit.md` | `6b9ef51cfe2509b18dc8c2f271eac28e69820d311f9088d0aa3dd664970ac983` |
| `06_reproduction/manifests/m9_overlap_frozen_hashes.json` | `db01a3d15c604b0fc8cc48858d38b3d28bc0c711eb0cba8634b94510f8139f95` |
| `06_reproduction/manifests/m9_unlimited_wall_clock_frozen_hashes.json` | `f41553b6112482df1cb0bbb52e3311d6a60514b6f61252526924fa930489f4f9` |

D-018 frozen manifest 的 27 个成员与代码常量集合一致，全部存在且哈希匹配；overlap frozen manifest 的 16 个成员全部存在且哈希匹配。控制脚本目录只有冻结清单中的 12 个 `.py` 文件，不存在额外脚本、子目录、symlink、`.pyc`、`.pyo` 或 `__pycache__`。

## 独立验证结果

固定解释器 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 全量重放结果为：

```text
Ran 109 tests in 31.478s
OK
```

四个 Python 对象独立 AST 解析为 `4/4 PASS`。七个相关 Markdown 对象经 GFM 输入、HTML5/MathML 输出严格解析为 `7/7 PASS`；五个核心 JSON 对象独立解析为 `5/5 PASS`。

测试前后正式运行态七项 SHA-256 完全一致：

| 正式对象 | SHA-256 |
|---|---|
| `budget_state.json` | `00a32bd7f28ad26fa600c8abe9d0fa64efe57e410eacb82ad2d201fa9adc5439` |
| `overlap_workflow_state.json` | `bd895b2831c805c44a180012ece64bdda00744340768c7062e33b856069fda8a` |
| `budget_ledger.jsonl` | `dbc54580fc6e215319c3af8d33b7f803448baa50a928ee4a60151782c9fd5e3b` |
| `overlap_transaction.json` | `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309` |
| `overlap_source_control_recovery.json` | `e9b8babcff8a2f42adea21d5cbce614b38f0854271d3389eae0bbcdd7d5e53bc` |
| `overlap_source_control_recovery_gate.json` | `8e66d65d17d3195f3df09db954afca4066c3ec91e2d8dad6d2aea06078d0d5ce` |
| `overlap_work_package_audit_gate.json` | `dbe4756142d0e921c3834330550310e85652503c04254b30bea1a069ff35377c` |

正式状态仍为 LIMITED，唯一 violation 为 `wall_clock_limit`。D-018 migration gate、transaction、execution gate、journal、pre-state snapshot、retired old gate 和六项 source/build 产物均缺席。因此，复核过程满足正式状态零写入和 M8/M9 授权边界。

## 定点复核判断

### D018-R01：关闭

首次迁移在任何 snapshot 写入之前，以确定性预期 receipt 提交 root-private `PREPARED` journal。journal 已提交而 snapshot 尚不存在时，重放会重新读取正式 state，要求其 SHA-256 等于冻结 pre-runtime，再幂等创建 snapshot。模拟断电测试证明 journal 保持 PREPARED、snapshot 缺席时可续提同一事务至成功。

snapshot 创建发生确定性 I/O 失败时，journal 已存在，外层处理进入 `commit_d018_failure()`，形成唯一 failure event、budget hard stop、workflow HARD_STOP 和 root-owned `FAILED_COMMITTED` transaction。该路径不把 `D018SimulatedPowerLoss` 误记为确定性失败。

### D018-R02：关闭

`command_overlap_run()` 现在先以 `r+` 打开既存 `budget.lock` 并获取排他锁，再读取 state/workflow/overlap transaction、解析请求 action、判断 wall mode、验证 D-018 terminal evidence、验证 execution-fact gate、绑定 gate scope，并在同一锁内复核完整 runtime receipt。只有 `action == source_prepare` 且 scope 精确为 `ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018` 时才可继续。

独立检查确认：LIMITED 到 UNLIMITED 的锁边界变化会走 post-migration fact gate；scope 为 source_prepare 的 gate 不能授权 `source_build`；验证完成到 transaction PREPARED 之间没有协作控制器可取得同一正式锁推进 runtime。D-017 recovery transaction/gate 和 D-018 execution runtime 的原 SHA 仍被组合验证。

### D018-R03：关闭

非 overlap `command_run()` 取消了锁外 wall-mode 决策，改为先打开既存 lock 并取得排他锁，再读取 state 并判断 `wall_clock_policy_mode`。锁内状态为 UNLIMITED 时，在计算 command hash、创建子进程和任何正式写入之前直接拒绝。

LIMITED precheck 到 UNLIMITED locked-state 的确定性交错测试覆盖 `none`、`compatibility`、`training`、`physical_validation` 四个 bucket，均证明 `Popen` 未调用。由此，取消总墙钟没有重新产生任意命令、未计量 CPU 或隐式 GPU 通道。

## 相邻 B01—B06 回归判断

- B01：exact prefix、严格 partial、完整事件三态仍受确定性提交器约束；真实短写可回滚并只提交一次事件。
- B02：旧 gate 继续以单文件描述符绑定 `st_dev/st_ino`、bytes、owner、mode、nlink；同字节换 inode 被拒绝并形成双硬停。
- B03：D-017 transaction/gate、D-018 terminal evidence 和迁移后 execution-fact gate 组合验证；缺 gate 或错误 action 均在正式写入前拒绝。
- B04：generic `run` 在 D-018 后对全部 bucket 锁内零写拒绝；CPU-only 后继动作只能走冻结 action 与 CPU bucket。
- B05：成功 journal、partial ledger、PREPARED-before-snapshot 和 deterministic failure 路径均可续提；成功或失败事件各自保持 exactly once。
- B06：terminal verifier 继续严格绑定 journal 闭集与 SHA、snapshot、retired inode、replacement gate、冻结 prefix、事件完整字节、ledger SHA、state、transaction 和 D-017 证据；未发现回归。

## 门控范围

本报告允许的下一步仅为：主 agent 机械创建与本报告、结构化 verdict、授权记录、迁移合同、frozen manifest 和精确 pre-runtime 绑定的正式 D-018 migration gate；随后以冻结 root 入口执行一次迁移，并立即停止等待独立执行事实审计。

若正式 gate 构造值、任一冻结哈希、pre-runtime、owner/group/mode/link、产品缺席事实或执行入口与工作包不一致，则本 PASS 不适用，迁移必须拒绝。

