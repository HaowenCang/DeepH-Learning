# M9 source_prepare Python 3.9 失败恢复工作包

状态：`READY_FOR_FIRST_TARGETED_REAUDIT`  
决策边界：D-017、D-018  
稳定问题：`M9-SP-PY39-B01`  
唯一动作：恢复已审计的 Python 3.9 兼容性失败；不授权新的 `source_prepare`、`source_build` 或计算。

## 1. 事实基础

正式 `source_prepare` 事务 `80e28da82f076f4f7b1811f5897216bd` 在冻结 Python 3.9.23 中调用 `Path.write_text(newline=...)` 后失败。独立事实审计报告为 `08_audits/M9_source_prepare_python39_failure_independent_audit.md`，SHA-256 `bb4182f555dbd93b04eae50c79ba8e9e855cec75393465ac56ef23e505406bed`。失败已提交为 `FAILED_COMMITTED`，budget state 与 workflow 均为 `HARD_STOP`；ledger 在原 60,288-byte 前缀后只增加一个 960-byte `OVERLAP_HARD_STOP` 事件。已消费 capability 与 FAIL launcher receipt 保持原位，活动 PID 为 0。

`openmx-overlap-build.staging` 是本次失败的部分写入证据：包含 140 个目录、5,179 个普通文件、无链接或特殊对象，分配空间 632,029,184 bytes。该目录不得删除、清空、覆盖或原地复用。

## 2. 兼容性修复

`m9_openmx_build.py` 与 `m9_openmx_input.py` 的文本写入统一调用 `m9_overlap_common.write_utf8_lf()`。该函数在文本含 CR 时拒绝，并通过 Python 3.9 支持的 `Path.open("w", encoding="utf-8", newline="\n")` 写入。固定 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 的真实文件测试必须证明：

- 不产生 `TypeError`；
- UTF-8 bytes 与渲染器输出逐字节相等；
- 只允许 LF 行尾；
- build 与 input 两条正式调用路径均不再含 `Path.write_text(..., newline=...)`；
- 原 makefile 渲染、输入渲染、inventory 与禁止输出合同无回归。

## 3. 恢复输入闭集

机读合同为 `06_reproduction/manifests/m9_source_prepare_py39_recovery_contract.json`。它精确绑定 19 个正式对象：

- `budget.lock` 的固定 path、空内容 SHA、owner/group、mode、nlink、`st_dev/st_ino`；
- budget state、workflow、ledger、失败 transaction；
- consumed capability 与 FAIL launcher receipt；
- consumer gate、bootstrap receipt、snapshot manifest；
- D-017 transaction/gate、active/retired overlap gate；
- D-018 gate、transaction、execution gate、journal 与 pre-state snapshot；
- 每个对象的 path、SHA-256、bytes、uid/gid、mode、nlink；关键对象另绑定 `st_dev/st_ino`；
- ledger 的原前缀、失败后缀和完整字节；
- staging 的递归 closed set、计数、bytes、实现 inventory hash、独立审计 inventory hash 与失败 makefile hash；
- raw CPU、credit、GPU 与 `UNLIMITED` 墙钟策略；
- 五项终态/manifest 产品缺席。

旧 transaction、capability、receipt、consumer gate、历史 gate、CPU/GPU/storage 用量和 ledger 失败事件均为不可变证据。

## 4. 一次性控制对象

控制器为 `06_reproduction/controllers/m9_source_prepare_py39_recovery.py`。正式 gate、journal、recovery transaction 与失败 transaction snapshot 均位于 `/root/deeph-m9-control`，必须为 root:root、`0600`、普通单链接文件。唯一恢复 ID 为 `m9-source-prepare-py39-recovery-20260827-01`。

控制器只接受：

```text
create-gate
recover
```

两条入口均要求 root、固定 Python、`-I -S -B`。`create-gate` 只能在独立实现审计为 `PASS/BLOCKING=0/NON_BLOCKING=0` 后执行；它必须绑定结构化 verdict、审计报告、工作包、合同、冻结清单、全部失败现场 receipt 和当时的 staging inventory。`recover` 只接受该 root-private gate。

## 5. 状态机与崩溃续提

恢复在合同与 gate 同时绑定的既存 `budget.lock` 排他锁内执行。取得 `flock` 后及每个正式提交边界前，控制器均须用同一 FD 和路径 `lstat` 复核 regular、owner/group、mode、nlink、bytes、SHA、`st_dev/st_ino`。阶段为：

1. `PREPARED`；
2. `FAILURE_TX_SNAPSHOTTED`；
3. `STAGING_RETIRED`；
4. `LEDGER_COMMITTED`；
5. `STATE_COMMITTED`；
6. `WORKFLOW_COMMITTED`；
7. `SUCCESS_COMMITTED`。

任何正式写入前必须持久化 `PREPARED` journal。失败 transaction 逐字节复制为 root-private snapshot，原路径不变。staging 只允许同文件系统 `os.replace` 到：

```text
/home/evan-williams/deeph-m9/software/openmx-overlap-build.failed-80e28da82f076f4f7b1811f5897216bd.retired
```

rename 前后必须复算完整 inventory；源存在/目标缺席时执行 rename，源缺席/目标存在且 inventory 相等时认领已完成 rename，其他组合拒绝。不得复制后删除。

ledger 只追加一个 canonical JSONL `OVERLAP_SOURCE_PREPARE_PY39_RECOVERY` 事件。完整事件已存在时只验证；partial append 只在现有 ledger 是预计算目标的严格前缀时补齐；其他尾部拒绝。原 61,248-byte ledger 保持严格前缀。

state 仅允许：保留所有预算、历史用量和 wall-clock 证据，把 `hard_stopped` 改为 false、保持 active transaction 为空、记录 recovery ID 与恢复 UTC。workflow 仅允许恢复为 `AUDIT_PASSED`、非 hard-stop、无 active transaction并记录相同 recovery ID。两者提交后必须分别形成完整 post receipt；ledger 追加后也形成完整 post receipt。terminal journal/transaction 逐项绑定三者的 path、SHA、bytes、owner/group、mode、nlink 与提交后的 `st_dev/st_ino`，terminal replay 通过稳定 `O_NOFOLLOW` FD 读取并与路径身份闭合，且不得写入。失败 transaction、capability 与 FAIL receipt不得修改。

## 6. 审计矩阵

独立实现审计至少覆盖：

- 固定 Python 下全部既有 110 项控制测试与 15 项专用恢复测试；后者内部覆盖全部 14 个 journal/transaction 提交窗口及多组链接、锁、phase-pair、gate/scope、自绑定、rename 和 receipt 子例；
- build/input 真实 UTF-8 LF 写入；
- contract 与 frozen manifest 全量哈希；
- staging inventory 的独立复算；
- gate/verdict/report/work-package 自绑定；
- journal 创建前后、snapshot 写入、rename 前后、ledger partial append、state/workflow 单边提交的逐阶段恢复；
- symlink、hardlink、owner/mode、inode、runtime、ledger、staging、makefile 与产品缺席漂移拒绝；
- terminal replay 零写；
- 测试前后正式失败现场零变化，cache 为 0。

## 7. 初审问题与定点修复

2026-08-27 首次独立实施审计为 `FAIL/BLOCKING=4/NON_BLOCKING=0`，报告 SHA-256 为 `fc8ed7e4428e7e8e7b27ca15f0db9c397193cc452bc2389ef24cad9ffb27ae0d`。本次定点修订仅关闭该报告的 B01—B04：

- B01：terminal journal/transaction 改为绑定 state、workflow、ledger 的完整 post receipt；新增同字节 symlink、hardlink、mode 与 inode replacement 零写拒绝；
- B02：合同和 gate 新增 `budget.lock` 固定 receipt；取得锁后及各提交边界前复核 FD/路径同一身份；新增 symlink、hardlink、mode 与 inode replacement 零写拒绝；
- B03：在 workflow target 写入并验证后，先持久化 `WORKFLOW_COMMITTED` journal/transaction，再进入 terminal；
- B04：专用测试由 5 项扩展为 13 项，执行 14 个 atomic-json 崩溃窗口、snapshot/state/workflow/rename 断点、账本部分追加、retirement 四态、失败快照漂移、预算历史闭集、terminal 身份负例、锁身份负例、gate/scope/report/verdict/work-package/frozen 自绑定负例，以及 `prepare_sources()`/`prepare_structure()` 两条真实 UTF-8/LF 写入路径。

主任务的测试通过不关闭上述 finding。只有原独立审计员对 B01—B04 定点复核为 `PASS/BLOCKING=0/NON_BLOCKING=0`，才允许生成结构化 verdict并进入一次性 recovery gate。

第一次定点复核已确认 B01—B04 全部 `CLOSED`，但新增 `M9-SP-PY39-RCV-R01`：续提会重新采集并覆盖已持久化阶段的 post receipt。第二轮修订建立允许的 journal/transaction phase-pair 状态机；从 `LEDGER_COMMITTED`、`STATE_COMMITTED`、`WORKFLOW_COMMITTED` 起，分别在任何后续写入前验证并继承首次持久化的 post receipt，禁止同字节新 inode、symlink、hardlink、owner/group、mode 或 nlink 漂移重新定义身份。专用测试新增三个阶段 × 五种漂移矩阵以及非法 phase-pair、孤儿 transaction 零写拒绝。只有原审计员确认 R01 `CLOSED` 且新增/剩余问题为 0，才允许生成结构化 verdict。

2026-08-28 在正式创建恢复门控前的重复只读预检中发现 `M9-SP-PY39-RCV-R02`：失败事务保留的历史 `child_pid=391` 已结束，但短生命周期 WSL 进程可复用 PID 391；原恢复控制器仅以 `/proc/<pid>` 是否存在判定原 launcher 存活，导致同一预检先通过、后误阻塞。修订后，`FAILED_COMMITTED` 必须同时具备非零退出码、非超时、开始/结束/失败时间、非负 elapsed、唯一失败原因以及 capability/transaction 相同 child PID；活动进程判据改为当前 `/proc/<pid>/cmdline` 与冻结 consumed capability 的完整 `launcher_argv` 逐参数、逐字节相等。不同 argv 的复用 PID 不再阻塞，完全相同 argv 的活动 launcher 仍必须阻塞。新增合成回归测试覆盖两种分支。原独立审计 agent 必须定点复核 R02，并在 B01—B04、R01 均保持关闭且无新增问题后生成新的独立报告与结构化 verdict；旧 PASS verdict 不得用于创建恢复门控。

R02 首次定点复核判定 `FAIL/BLOCKING=1/NON_BLOCKING=0`：使用 `payload.split(b"\0")` 后删除空字段，不是原始 cmdline 的完整字节相等；末尾或中间额外空参数会被误接受，冻结 argv 合法含空参数时反而误拒绝。第二轮修订禁止 expected argv 字段内嵌 NUL，并以 `b"\0".join(encoded_argv) + b"\0"` 构造唯一 canonical cmdline bytes，与 `/proc/<pid>/cmdline` 原始 bytes 直接相等比较。冻结测试在原两分支上增加末尾额外空参数、中间额外空参数、expected 含空参数精确正例和 expected 内嵌 NUL 拒绝例。只有原审计员确认上述反例全部关闭且无回归，R02 才可标记为 `CLOSED`。

独立定点复核只允许更新或新增：

- `08_audits/M9_source_prepare_py39_recovery_implementation_audit.md`；
- 仅在零问题 PASS 时新增 `08_audits/M9_source_prepare_py39_recovery_final_verdict.json`。

## 8. 授权边界

实现审计 PASS 只允许机械创建一次 recovery gate并执行一次 `recover`。执行后必须立即停止并完成独立执行事实审计。恢复成功本身不授权 `source_prepare`；还必须重建并事实审计替代 root-owned consumer snapshot/gate，然后取得新的明确单次 `source_prepare` 用户授权。`source_build`、smoke、batch、GPU、Hamiltonian、SCF 与其他 DFT 标签继续禁止。
