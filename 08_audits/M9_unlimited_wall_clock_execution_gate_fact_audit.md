# M9 D-018 execution-fact gate 实际事实独立审计

审计日期：2026-08-20  
审计方式：正式对象只读冻结、root 与 UID1000 双身份验证器重放、结构化绑定复算、固定 Python 全量测试、测试前后正式对象哈希复核  
执行边界：未修改或替换 execution-fact gate；未执行 `source_prepare`、`source_build`、smoke、batch、GPU 或任何正式迁移重放

## 审计结论

**FAIL**。`BLOCKING=1`，`NON_BLOCKING=0`。

正式 execution-fact gate 本身是 root:UID1000、`0640`、单链接的稳定普通文件；其 schema、PASS 计数、scope、执行审计 verdict/report 以及迁移后十二项 runtime 哈希均正确。root 身份调用冻结的 `verify_unlimited_wall_clock_execution_fact_gate()` 返回精确 PASS，固定 Python 全量测试也为 109/109 通过。

但是，唯一获准消费 gate 的正式入口 `command_overlap_run()` 强制要求有效 UID 为 1000，而当前 verifier 会在该身份下重新打开 root:root、`0600` 的 D-017 recovery gate，并随后依赖同样不可读的 root-private D-018 journal/snapshot。独立以真实 UID1000 进程调用 verifier 得到退出码 1，首个稳定错误为：

```text
stable regular object is missing: /home/evan-williams/deeph-m9/manifests/overlap_source_control_recovery_gate.json
```

因此，现有 root PASS 只能证明 gate 内容与 root 可见的事实一致，不能证明授权主体能够消费该 gate。当前 **不得启动 UID1000 `source_prepare`**，也不得授权 `source_build` 或任何后继动作。

## 正式 gate 与绑定

正式 gate 实测 receipt 为：

| 字段 | 实测值 |
|---|---|
| path | `/home/evan-williams/deeph-m9/manifests/overlap_unlimited_wall_clock_execution_gate.json` |
| SHA-256 | `bc51209c13570839c08dd4fc304fe39865a98ade69caeb23886602de2d8be6e9` |
| bytes | 1764 |
| owner:group | `0:1000` |
| mode | `0640` |
| nlink | 1 |
| dev:ino | `2096:153521` |

其顶层字段为精确 `m9-unlimited-wall-clock-execution-gate-v1`、`decision_id=D-018`、`status=PASS`、`blocking=0`、`non_blocking=0`，scope 为且仅为 `ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018`。UID1000 对 gate 可读而不可写。

gate 绑定的结构化 verdict 为：

- `08_audits/M9_unlimited_wall_clock_migration_execution_final_verdict.json`；
- SHA-256 `d6c0939a3f369d570c3db4c6fae5d9104efee886c19830a0df2b11427e43cefb`，372 bytes；
- schema `m9-unlimited-wall-clock-execution-audit-verdict-v1`；
- `decision_id=D-018`、`verdict=PASS`、`blocking=0`、`non_blocking=0`。

verdict 进一步绑定 `M9_unlimited_wall_clock_migration_execution_independent_audit.md`，报告实测 SHA-256 为 `899d77448183a6b79c8f870c0473b18c4601274f0b6a0db78760519ce6d5090c`、9735 bytes，与 verdict 的 `report_sha256` 完全相同。正式 gate 的 `verdict_path` 和 `verdict_sha256` 也与当前对象完全相同。

## 十二项 runtime 与迁移终态

root 固定 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 独立执行 `verify_unlimited_wall_clock_execution_fact_gate()` 成功，返回 gate receipt、`SUCCESS_COMMITTED` transaction 和事务 ID `d018-unlimited-wall-clock-20260820-01`。gate 中十二项 runtime 与实际对象逐项相等：

| runtime 字段 | 实测 SHA-256 |
|---|---|
| `state_sha256` | `c56532b1f92573bd4324464d0b10004df4b5f8337d1e803fdcd80a2f320585a8` |
| `workflow_sha256` | `bd895b2831c805c44a180012ece64bdda00744340768c7062e33b856069fda8a` |
| `ledger_sha256` | `178106f0be9f80ff669ebd0865e214a4b9a60d115074ad0c97ae8de5f1ae33b7` |
| `overlap_transaction_sha256` | `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309` |
| `source_control_recovery_transaction_sha256` | `e9b8babcff8a2f42adea21d5cbce614b38f0854271d3389eae0bbcdd7d5e53bc` |
| `source_control_recovery_gate_sha256` | `8e66d65d17d3195f3df09db954afca4066c3ec91e2d8dad6d2aea06078d0d5ce` |
| `d018_gate_sha256` | `286a0e409a80f85ca6bb39b76bdb977fc67ffa56f4646b00d3aad5943c98e880` |
| `d018_transaction_sha256` | `41cbfbd4da1c3a0eea92731a00758355f46321d5b0a66260f53f628290d847ad` |
| `d018_journal_sha256` | `27a92edded459948150c750a4339692434e08a84cbc8879c63c71b6c14cb0e8a` |
| `d018_pre_state_snapshot_sha256` | `00a32bd7f28ad26fa600c8abe9d0fa64efe57e410eacb82ad2d201fa9adc5439` |
| `retired_overlap_gate_sha256` | `dbe4756142d0e921c3834330550310e85652503c04254b30bea1a069ff35377c` |
| `active_overlap_gate_sha256` | `78311a978c2472c85b35a745d80e1f33724c1500cf8d7bd244cdbe83c3fa3698` |

D-018 transaction、journal、snapshot、retired gate 与 active replacement gate 的 owner/group/mode/nlink 继续符合前次执行事实审计记录。D-018 transaction 和 journal 均为 `SUCCESS_COMMITTED`；execution-fact gate 的独立创建没有改写 state、workflow、ledger、历史 transaction、D-017 recovery 证据或 D-018 迁移证据。

D-018 frozen manifest 27/27、overlap frozen manifest 16/16 均逐项哈希匹配。当前冻结核心仍包括 `m9_budget.py` SHA-256 `25c92810de52229ff626b4d54f4bd2084453e2e834ff830232b8599033f6cce5` 和 `test_m9_overlap_controls.py` SHA-256 `8fd7b0eafebbe0d58f1e7c13ba0d5ede9881efd9cb070ecaa0bf6ab648073e59`。

## 产品、能力与回归

gate 的 `runtime.source_products_present` 为精确空列表。下列六项实测全部缺席：

- `/home/evan-williams/deeph-m9/software/openmx-overlap-build`；
- `/home/evan-williams/deeph-m9/software/openmx-overlap-build.staging`；
- `/home/evan-williams/deeph-m9/env/hdf5-1.12.1`；
- `/home/evan-williams/deeph-m9/manifests/openmx_official_3.9.9_tree_manifest.json`；
- `/home/evan-williams/deeph-m9/manifests/openmx_overlap_tree_manifest.json`；
- `/home/evan-williams/deeph-m9/manifests/openmx_overlap_build_manifest.json`。

capability 目录只有既有 `f7c3b060e19e37e6da03f461d754d38c.retired.json`，不存在 active `.json` capability。没有新的 source_prepare transaction 或 build 产品。

固定 Python 全量重放结果为：

```text
Ran 109 tests in 26.651s
OK
```

测试前后 execution-fact gate 加十二项正式 runtime 对象的 SHA-256、bytes、owner/group、mode、nlink 和 inode 均保持不变；控制脚本与测试目录的 `__pycache__` 数为 0。测试未消费正式 gate。

冻结代码对 `source_build` 的 scope 检查本身正确：UNLIMITED 分支要求 `action == "source_prepare"`，否则在 `Popen` 前拒绝。因此本报告没有发现 gate 文本将 scope 扩展到 `source_build`。然而，这一正确的窄 scope 不能消除 UID1000 无法通过前置事实验证的问题。

## D018-EGF-B01：授权主体无法读取 verifier 的必需证据

**级别：BLOCKING。**

### 复现事实

以 root 身份调用 verifier 返回 PASS；以真实用户 `evan-williams`（UID1000）调用同一冻结函数，未 patch `geteuid`、未替换路径、未模拟权限，得到退出码 1 和上述 `overlap_source_control_recovery_gate.json` missing 错误。该对象实际存在且 SHA 正确，但元数据为 `root:root/0600/1`，UID1000 的 `test -r` 为 false。D-018 journal 与 pre-state snapshot 同样为 `/root/...`、`root:root/0600/1`，UID1000 也不可读。

### 机制

`command_overlap_run()` 在 `m9_budget.py:5347-5349` 强制普通 overlap source 操作只能由 UID1000 执行。取得预算锁并读到 UNLIMITED policy 后，代码在 `m9_budget.py:5384-5385` 依次调用 `verify_unlimited_wall_clock_execution_ready()` 和 `verify_unlimited_wall_clock_execution_fact_gate()`。

后者通过 `d018_execution_runtime_receipts()` 重新读取十二项 runtime；该集合含 root-private D-017 recovery gate。随后 `verify_unlimited_wall_clock_execution_ready()` 还严格读取 root-private D-018 journal 和 snapshot。因此，root 审计路径和 UID1000 消费路径具有不同的可读对象集合，而当前实现将 root-only 完整事实验证直接复用于 UID1000 入口。失败发生在创建 transaction、capability 或子进程之前，当前行为是安全的零写拒绝，但也意味着 gate 不可被其唯一授权主体消费。

### 既有测试为何未发现

109 项测试中的 formal runtime binding 用临时 fixture 并在同一 root 测试进程内运行 verifier；入口测试则 patch `os.geteuid()` 返回 1000，同时 patch `verify_unlimited_wall_clock_execution_ready()` 或 execution-fact verifier。它们覆盖字段漂移、scope 和 Popen 前拒绝，但没有建立一个真实 UID1000 子进程去读取与正式权限等价的 root-private 对象。因此，109/109 PASS 与本次真实身份失败并不矛盾。

### 关闭条件

修复不得把既有 root-private D-017/D-018 证据简单改成 UID1000 可写，也不得重置或替换历史证据。可接受的设计应当区分：

- 由 root 审计并机械创建的 execution-fact gate 对 root-private 历史证据的封存绑定；
- UID1000 消费时必须实时复核的可读、不可写 runtime 和 source-product 缺席集合；
- `source_prepare` 唯一 scope、预算锁内二次 TOCTOU 检查、一次性 transaction/capability 语义。

修订后至少应新增真实 UID1000 子进程回归：在与正式 owner/group/mode 等价的 fixture 或正式只读现场上，execution-fact verifier 必须返回 PASS；同一身份的 `source_build` 仍须在任何 `Popen` 和状态写入前拒绝；root-private 对象仍应保持 root-only 且其哈希绑定不可由 UID1000 伪造。修复冻结后需要独立定点复核，不能以现有 root 109/109 测试替代。

## 最终门控

当前 execution-fact gate 内容真实且未漂移，但其正式消费链不可达。因此：

- **不允许消费该 gate 启动 UID1000 `source_prepare`**；
- **不允许 `source_build` 或任何后继动作**；
- 仅允许主 agent 修复 UID1000 消费路径、补充真实身份回归、更新相应冻结闭集，并将修订快照交回独立定点复核；
- 在本问题关闭前，不得通过改变 gate 文本、放宽 root-private 文件写权限或以 root 运行普通 overlap source 操作绕过失败。
