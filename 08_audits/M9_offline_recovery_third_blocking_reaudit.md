# M9 overlap-only 离线 apt 恢复第三次定点复核

## 复核结论

第三次定点复核结论为 `FAIL`。`M9-REC-B01`、`M9-REC-B05`、`M9-REC-B06` 保持 `CLOSED`；`M9-REC-B02` 因新的 gate 集合矛盾而重新 `OPEN`；`M9-REC-B03`、`M9-REC-B04`、`M9-REC-B07` 仍为 `OPEN`。当前统计为 `BLOCKING=4`、`NON_BLOCKING=0`。

不得创建状态为 `PASS` 的 `overlap_offline_recovery_gate.json`，不得执行离线安装，也不得进入恢复后的 source prepare、HDF5/OpenMX 构建或结构 smoke。剩余问题仍属于 D-017 已批准范围内的控制实现修复，不需要新的材料、软件、预算或物理路线决策。

本轮送审快照的主要 SHA-256 为：

- `m9_budget.py`：`6e5c72083ac1faf50f9576d51257c430e4de5b569f5e9fdf94e33a651905f0f8`；
- `m9_offline_recovery_frozen_hashes.json`：`ec8a8227d05a8585c106ede9cada97461353cdb887be1d98ce2d379f5f6c062d`；
- `m9_offline_apt_manifest.json`：`f54d61cbf4f6cb82dcd1cd0daa17ff2cf013f328b19d3222cff1a37dba637616`；
- `test_m9_overlap_controls.py`：`bfb5f20bb6f1a69cf091839421890ea5838ebebf78458b8093d4cc4fb806b1bf`；
- 第二次复核报告：`caa372947a0ffd00b8b3ed1d14181363cd202bd268d970ec123d6b4ed4b183f0`。

## 审计边界与证据

本次只读核对送审代码、合同、候选 frozen manifest、Ubuntu 来源链和现有 WSL 状态，并执行冻结 Python 测试、py-compile、ledger 定向穿透、gate 集合代数检查和 callback 异常子进程重放。没有创建 recovery gate，没有安装或配置软件包，没有修改预算、workflow 或 transaction，没有解压或编译 HDF5/OpenMX。唯一新增项目文件为本报告。

冻结 Python 3.9 以 `-I -S -B` 执行正式测试，22/22 通过；`m9_budget.py` py-compile 通过。定向重放产生的 30 秒 sleep 审计子进程已由审计员终止并回收，复核结束时 `/proc/<pid>` 不存在。测试通过数不能替代以下穿透结果。

## 保持关闭的项目

### `M9-REC-B01`：保持 `CLOSED`

InRelease 签名、SHA-256 段的 suite/component/path/bytes/hash、四个 Packages 索引、重复身份记录集合和 45 个归档 Filename/SHA-256 的链仍完整；正式来源链测试通过。未发现本轮状态机修订影响来源边界。

### `M9-REC-B05`：保持 `CLOSED`

postcheck 仍要求 45 个目标包的 version/status 精确匹配 manifest，新增包集合恰为目标集合，全部非目标 package/version/status 与 pre 映射精确相等；dpkg audit 和 updates 目录仍须为空。未发现相邻回归。

### `M9-REC-B06`：保持 `CLOSED`

pre-ledger SHA-256、bytes、行数、末事件摘要、pre state/workflow、父 transaction 及父文件原字节快照绑定均保留。父 transaction 不由恢复失败路径覆盖。

## 开放阻塞项

### `M9-REC-B02`：recovery gate 的闭集合同当前不可满足

代码定义的 recovery gate `files` 必需集合共有 8 个对象，其中一个是 recovery frozen manifest；去掉该 manifest 后，gate 文件映射应有 7 项。新的 follow-up frozen manifest 则合理扩展为 18 个执行与合同对象。

但 `verify_recovery_gate_and_hashes()` 仍要求 `frozen_files == gate_files_without_manifest`。因此它同时要求 18 项映射等于 7 项映射，任何 gate 都不可能通过。独立集合复算得到 `18 != 7`。

此外，固定 `RECOVERY_AUDIT_REPORT` 仍指向第二次报告 `M9_offline_recovery_blocking_reaudit.md`；该报告的正式结论是 `FAIL/BLOCKING=3`。代码只核报告路径与哈希，不验证报告结论，却允许 gate 自报 `PASS`。这既不能绑定本次审计，也可能使 PASS gate 指向明确 FAIL 的报告。

最小关闭条件：区分安装 gate 的最小受审闭集与 follow-up 执行超集。gate 应精确绑定 recovery 必需对象和 follow-up manifest 自身 SHA-256，但不得要求 manifest 内部 18 项等于 gate 的 7 项；应分别验证两个集合各自的固定合同。固定报告路径必须更新为下一次实际 PASS 候选报告，并由可信机读 companion 或严格受控 gate 生成流程绑定 `PASS/BLOCKING=0/NON_BLOCKING=0`，不得指向历史 FAIL 报告。增加 7/18 正例、集合混淆、历史 FAIL 报告和报告替换负例。

### `M9-REC-B03`：spawn callback 异常仍会遗留活动进程，PID 身份也未绑定

正常路径现在在 `Popen` 后立即调用 callback，把 child PID、命令哈希和 active 状态写入 journal；命令返回后再写 inactive。这关闭了正常 callback 成功时的写入延迟。

但是 `run_recovery_child()` 在调用 `on_spawn(proc.pid)` 时没有异常保护。如果 callback 因锁、JSON、磁盘或状态错误抛出异常，函数直接退出且没有终止或回收刚创建的新进程。外层只得到异常，不知道 PID，随后可能把恢复提交为 HARD_STOP，而 dpkg 子进程仍继续运行。

独立用 `/bin/sleep 30` 和故意抛错的 callback 重放：函数抛出 `RuntimeError` 后，该 child 仍可由 `kill(pid, 0)` 探测为存活。审计员随后显式终止并回收该进程。这证明 callback 并未形成“先 journal 或先停进程”的原子边界。

重入检查仍只用 PID 存活性，没有把 `/proc/<pid>/stat` starttime、进程组 ID 和已冻结 argv 身份与 journal 比较；PID 重用可能把无关进程误判为恢复子进程。

最小关闭条件：`Popen` 后的 callback 必须位于 `try` 中；callback 失败时立即对新进程组执行 TERM/KILL、wait 回收，再向上抛错并硬停。journal 应记录 PID、PGID、proc starttime 和 argv/cmdline hash；重入只有在四项身份均匹配时才判为活动恢复子进程。补充 callback 写失败、锁失败、PID 重用、匹配 live child、stale child 与整组终止的真实负例。

### `M9-REC-B04`：ledger 仍接受损坏行和重复 event ID

`ledger_event_ids()` 现把 event ID 映射到 canonical payload hash；`append_event_once()` 会拒绝单个同 ID、不同载荷，正常 resume 也比较预期 canonical hash。这关闭了第二次报告的基本错载荷穿透。

但 parser 遇到无效 JSON 时直接 `continue`，不会拒绝损坏或截断账本；同一 event ID 出现多次时由后读行静默覆盖。独立重放表明：账本含一行损坏 JSON 加一行正确事件时被接受；同 ID 先错误 credit、后正确 credit 时只保留最后 hash，也被视为合法。append-only ledger 因此不能证明不存在更早的冲突或截断证据。

函数在 ledger 不存在时还返回 `set()` 而正常类型为 `dict`。当前空容器不影响简单 membership，但暴露了未严格冻结的解析合同。

最小关闭条件：ledger reader 应始终返回同一结构；任一空行以外的不可解析行、非 object、缺关键字段、重复 event ID 均必须拒绝。重复 ID 即使 canonical payload 相同也应拒绝，除非合同明确只允许一个物理记录并由 `append_event_once` 保证不追加。需要覆盖截断末行、损坏中间行、同 ID 同载荷、同 ID 异载荷、非 object 和空 ledger 负例。

### `M9-REC-B07`：follow-up manifest 已扩展，但当前仍不能形成可运行 gate

候选 follow-up manifest 已加入顶层 `contract_sha256`，并登记控制目录全部 12 个 Python 文件，以及 offline manifest、预算合同、overlap 合同、测试、工作包和授权记录。18 个登记对象的当前 SHA-256 与候选值一致。从静态文件范围看，第二次报告指出的缩减执行集合已修复。

然而 follow-up verifier 首先调用同一个 `verify_recovery_gate_and_hashes()`；B02 的 18 对 7 集合矛盾会使它在检查 follow-up manifest 前必然失败。因此恢复成功后的 `source_prepare` 仍不可达。

此外，当前控制目录存在 `__pycache__/m9_budget.cpython-39.pyc`。`verify_overlap_control_directory()` 明确拒绝任意子目录或 pyc；即使修复 B02，当前 follow-up gate 仍会因该目录失败。该 cache 不是 frozen manifest 对象，也不应通过放宽 allowlist 保留。

最小关闭条件：先按 B02 拆分 gate 闭集与 follow-up 超集校验；清除控制目录全部 `__pycache__`、`.pyc`、`.pyo`，并在 gate 创建和每次 follow-up 前继续严格拒绝其重现。增加使用候选 PASS gate 的 `verify_recovered_overlap_gate_and_hashes()` 真实正例，以及缺任一执行脚本、错误 contract hash、额外控制文件和 cache 负例。

## 最终门控

- 第三次定点复核：`FAIL`；
- `BLOCKING=4`；
- `NON_BLOCKING=0`；
- 不允许创建 PASS recovery gate；
- 不允许执行离线安装或恢复后 follow-up；
- 当前无需新的用户路线决策。

主 agent 应修复 B02、B03、B04、B07 后再次交回独立定点复核。只有所有阻塞关闭且严格 gate 正例能实际通过，才能创建一次性 recovery gate。

## 报告终检

本报告定稿后执行 UTF-8 控制字符扫描、活动本地 Markdown 链接检查，以及 Pandoc `markdown+tex_math_single_backslash` 到 HTML5 MathML 的 `--fail-if-warnings` 严格转换。用于验证 MathML 的恒等式为 \(22=22\)。最终 SHA-256 在交付消息中报告。
