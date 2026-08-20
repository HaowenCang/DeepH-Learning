# M9 无总墙钟期限迁移工作包

## 1. 目标与边界

本工作包实施 D-018：取消 M9 总墙钟期限，但不重置或增加任何 CPU、GPU 或存储预算，并保留 D-013/D-014/D-017 的全部历史证据。迁移只改变墙钟执行策略和因控制代码变更而必须更新的 overlap 审计 gate，不执行源码准备、编译或计算。

## 2. 状态语义

迁移前 `budget_state.json` 保留原始 `start_utc` 和 `deadline_utc`。迁移后仍逐字保留这两个字段，并新增 `wall_clock_policy`：其 `mode` 为 `UNLIMITED`，同时绑定 D-018、迁移事务、唯一 ledger 事件、授权记录、迁移合同和执行 gate 的 SHA-256。`deadline_remaining_seconds` 在该策略下为 JSON `null`；`violations()` 不再产生 `wall_clock_limit`，但任何 malformed policy 必须产生 `wall_clock_policy_invalid`。

CPU timeout 仍由动作所属 CPU 子预算的剩余量决定；GPU 动作仍由 GPU 分桶剩余量决定。通用 `run` 在 D-018 后必须于任何正式写入和子进程创建前拒绝，不能通过 `--bucket none` 或伪装成 GPU bucket 把取消总墙钟转换为任意命令通道。后续 CPU-only 操作只能通过冻结 action、对应 CPU bucket、forecast、workflow 和 gate 的 overlap 路径执行；未来 GPU 动作须另行建立冻结 action 与独立门控。CPU、GPU、存储、forecast 和首错硬停止逻辑均不得放宽。

## 3. 一次性迁移

唯一入口为冻结 Python 以 root 身份执行 `m9_budget.py overlap-migrate-unlimited-wall-clock`。入口在既存 `budget.lock` 上取得排他锁，绑定迁移前 budget state、workflow、ledger、overlap transaction、source-control recovery transaction、source-control recovery gate、active overlap gate 和六项 source/build 产物缺席事实。

迁移 journal 的成功状态顺序为 `PREPARED -> OLD_GATE_RETIRED -> NEW_GATE_CREATED -> LEDGER_COMMITTED -> STATE_COMMITTED -> SUCCESS_COMMITTED`。`PREPARED` journal 必须是第一个 durable 事务对象，其中预先绑定确定性的 snapshot receipt；其后才允许幂等创建 snapshot。journal 已提交而 snapshot 缺失的进程死亡须续提同一事务，snapshot 创建的确定性失败须转入唯一双硬停止；禁止形成 snapshot 存在而 journal 缺失的孤儿状态。旧 overlap gate 必须在同一打开文件描述符上绑定 `st_dev/st_ino`、字节、owner、mode 与单链接属性，再原子改名为 `overlap_work_package_audit_gate.pre-d018.retired.json`；读后、改名前的同字节 inode 替换必须拒绝。新 gate 由冻结工作包、独立结构化 PASS verdict 和新 frozen manifest 确定性构造，owner/group/mode 固定为 `root:evan-williams/0640`，以便 UID1000 launcher 只读而不能改写。

ledger 只能对既存 UID1000、0644、单链接文件执行 `O_APPEND` 且不得 `O_CREAT`；事件 ID 和 canonical payload 唯一。提交器必须区分冻结 prefix、冻结 prefix 加事件严格真前缀、冻结 prefix 加完整事件三种状态；仅允许回滚非空严格真前缀后重写同一事件，完整事件 replay 仍须核对历史 prefix 与完整 payload。迁移中断后只能续提同一 transaction/event，不得创建第二事务、第二事件或覆盖历史 prefix。正式 budget state 只能从迁移前精确 SHA 或同一 journal 绑定的精确迁移后 payload继续。

确定性校验或 I/O 失败不得只依靠后继 verifier 间接拒绝。进入 `PREPARED` 后的首个确定性失败必须通过专用 failure journal 续提为唯一 hard-stop ledger 事件、budget `hard_stopped=true`、workflow `HARD_STOP` 和 root-owned `FAILED_COMMITTED` D-018 transaction；模拟进程死亡只保留可续提中间态，不应被误记为确定性失败。

成功终态 verifier 必须严格核对 journal 闭集与 SHA、迁移前 state snapshot、retired gate inode receipt、replacement gate、迁移前完整 runtime、D-017 source-control recovery transaction 与 gate、冻结 ledger prefix、唯一事件完整字节、迁移后 ledger SHA、迁移后 state 和 transaction 全字段。迁移完成本身不放行 `source_prepare`：独立执行事实审计后还须建立 `m9-unlimited-wall-clock-execution-gate-v1`，绑定执行报告、结构化零问题 verdict、D-018 transaction/journal/snapshot、D-017 证据、state/workflow/ledger、两份 overlap gate 和六项产物缺席事实。wall mode、D-017/D-018/execution-fact gate、完整 runtime 和 action scope 必须在取得既存 `budget.lock` 后的同一临界区内验证，并在任何事务写入前重新读取相同 runtime；source-prepare gate 不得授权 source build。通用 `run` 的禁用判定也必须在同一既存锁内完成并持续覆盖至 `Popen`。

## 4. 独立验收

独立审计至少应验证：

- 授权、合同、代码、测试、工作包和两组 frozen manifest 哈希闭集；
- 原 deadline 与 604800 秒仅转为历史证据，没有被删除或改写；
- CPU/GPU/存储常量、raw usage、credit、基线与 ledger prefix不变；
- limited/expired、unlimited、malformed policy 三类状态的 `violations/status/timeout` 行为；
- gate 错误 verdict、错误 runtime、缺文件、symlink/hardlink、owner/mode、哈希漂移和 TOCTOU 拒绝；
- 六个成功 journal 中断窗口、真实 ledger 短写以及 failure journal 中断窗口均可续提；同一成功事件或失败事件恰好一次，终态 replay 零写入；
- PREPARED journal 与 snapshot 之间的模拟断电能够续提，snapshot 创建确定性失败能够唯一双硬停止；
- 旧 gate 同字节换 inode、journal/snapshot/retired gate/ledger/state/transaction 任一漂移均拒绝；
- 确定性失败提交 budget/workflow 双硬停，保留唯一首错和失败 transaction；
- D-018 后的通用 `run` 任意命令在任意 bucket 组合下均于子进程创建前零写拒绝；
- D-018 执行事实 gate 缺失时 `source_prepare` 在任何正式写入前拒绝，并且 D-017 recovery transaction/gate 证据保持原 SHA；
- migration/source_prepare 与 source_prepare/source_build 两组锁竞争不能使用陈旧 gate 或错误 scope；LIMITED 锁前观察与 UNLIMITED 锁内状态交错时，通用 `run` 的全部 bucket 均不得创建子进程；
- UID1000 可以读取并验证新 overlap gate，但不能修改、删除或替换 root 所有的 gate；
- 迁移前后六项 source/build 产物均缺席。

只有独立审计结论为 `PASS`、`BLOCKING=0`、`NON_BLOCKING=0`，才允许创建正式 migration gate并执行一次迁移。执行后必须立即停止并进行新的独立事实审计；本工作包不授权直接执行 `source_prepare`。
