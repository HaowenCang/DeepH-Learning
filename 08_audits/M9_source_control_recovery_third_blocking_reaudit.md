# M9 source-control recovery 第三次阻塞项复核

## 结论

本轮定点复核结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。上一轮仍开放的 `M9-SPR-IMP-B04` 在临时状态机穿透下达到关闭条件；`M9-SPR-IMP-B05` 仍为 OPEN，并新增 `M9-SPR-R3-B01`：测试隔离缺失导致 34 项测试实际污染正式 WSL recovery transaction 路径。

当前不得创建 source-control recovery gate，不得执行 `overlap-recover-source-control-failure`，不得重试 `source_prepare`，也不得把当前伪 transaction 当作任何成功恢复证据。

## 冻结对象与审计边界

送审对象独立复算为：

- `06_reproduction/scripts/m9_budget.py`：SHA-256 `c388c986d50461936552767ec3e1c96217c48dffa439373fd2caebffacd91a8f`；
- `06_reproduction/tests/test_m9_overlap_controls.py`：SHA-256 `ff9f8db6bb6d4bc6d602a0dacd946eef424461f9253cde5b8bb3d7fbc9554d5d`；
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：SHA-256 `9d674e2ef6d3c32afc037a2393603c291b1ff4da5044d03410b6bb0358932027`。

冻结清单为 `17/17` 匹配。审计没有创建 gate、没有执行正式恢复 CLI、没有重试 `source_prepare`。状态机穿透使用临时目录和 mock 路径；但按送审说明实际运行 34 项测试时，测试自身的路径隔离缺陷向正式 WSL manifests 写入了伪 transaction。发现后立即停止进一步测试，未删除或改写该现场。

## 原阻塞项复核

### M9-SPR-IMP-B04：CLOSED

首次路径现在完成 PREPARED 和 capability retirement 后统一调用 `source_control_resume`，不再复制另一套 state/workflow/ledger 提交逻辑。resume 对父事务、parent snapshot、retired receipt 和 ledger event-set 实施精确核验；ledger 只允许父集合或父集合加唯一同载荷 recovery event。

state 与 workflow 恢复现在分别通过 `recovered_from_source_prepare_control_failure` 识别已提交对象。临时目录实际重放“ledger 已提交、state 已恢复、workflow 仍为父 HARD_STOP”断点，结果为退出码 0，workflow 被幂等恢复并提交统一的 post state/workflow/ledger SHA。该行为关闭上一轮的半提交阻塞。

`SUCCESS_COMMITTED` 路径现只读核验 post state、workflow、ledger 和唯一 event-set后返回，不再回退重写中间态。ledger 损坏、父对象漂移、event-set 漂移和终态 receipt 不一致均被统一异常边界捕获，并调用 `source_control_hard_stop` 返回 125；新增损坏 ledger 测试验证这一点。由此 B04 的最小关闭条件已满足。

### M9-SPR-IMP-B05：OPEN

测试数量从 32 增至 34，新增了 state-first 半提交完成和终态损坏 ledger 双硬停测试；这两项确实覆盖 B04 的关键反例。然而状态机测试的文件路径隔离不完整，已经产生正式运行态污染，故测试证据本身不能通过。

具体而言，`test_source_control_resume_completes_state_first_half_commit` mock 了 transaction、parent snapshot、state、workflow 和 ledger，却没有 mock `SOURCE_CONTROL_RECOVERY_TRANSACTION`。`source_control_resume` 在临时状态机运行中多次调用 `atomic_json(SOURCE_CONTROL_RECOVERY_TRANSACTION, recovery)`，实际目标仍是：

`/home/evan-williams/deeph-m9/manifests/overlap_source_control_recovery.json`

因此测试不是隔离测试。它还会生成 `__pycache__` 以外的正式运行态对象，而“pyc=0”无法检测这种污染。

最小关闭条件：所有调用 `source_control_resume`、`source_control_hard_stop` 或 recovery CLI 的测试必须把整个可写闭集重定向至临时目录，至少包括 recovery transaction、parent snapshot、state、workflow、ledger、capability root 和 lock；测试前后应断言正式 WSL runtime inventory 与哈希完全不变。增加专门回归，若任一正式路径被打开用于写入则测试失败。修复后重新运行完整测试并独立核对零运行态写入。

## 新增阻塞项

### M9-SPR-R3-B01：正式运行态存在测试生成的伪 SUCCESS_COMMITTED transaction

本轮按送审命令执行 34 项测试后，只读检查发现正式文件：

`/home/evan-williams/deeph-m9/manifests/overlap_source_control_recovery.json`

其现场 receipt 为：

- SHA-256：`2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`；
- bytes：1644；
- UID/GID：1000/1000；
- mode：0644；
- state：`SUCCESS_COMMITTED`；
- parent transaction ID：伪值 `parent`；
- retired capability path：`/tmp/tmpo1f2oo5_/cap.retired.json`，该临时目录已经消失；
- event ID：`r:event`，事件类型为测试值 `RECOVER`。

与之对应的正式 source-control parent snapshot 和 gate 均不存在。真实失败事务、真实 stale capability、budget state、workflow 和 ledger 的已知哈希仍保持原现场：

- budget state：`1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`；
- workflow：`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`；
- failed overlap transaction：`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`；
- ledger：`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`；
- stale capability：`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`。

伪 transaction 的存在会使正式 recovery CLI 在获取锁后进入 existing transaction 分支；其 terminal receipt 又引用不存在的测试临时对象，因而不能视为 harmless 文件，也不能由普通恢复逻辑覆盖。不得手工编辑为真实内容，不得绕过它执行 recovery。

最小关闭条件分为两个阶段：

1. 先修复 B05 的测试隔离并冻结新代码、测试和 manifest；不得在修复前再次运行有污染的 34 项测试。
2. 建立一次性、可审计的测试污染清理事务。清理程序应在 `budget.lock` 排他锁下，精确要求伪文件 SHA、bytes、UID/GID/mode、测试 parent/event/temp path 全部匹配，并同时要求正式 source gate/parent snapshot 不存在、真实 state/workflow/ledger/failed transaction/stale capability 的上述 SHA 全部未变。符合时应将伪文件原子重命名为明确的 `.test-artifact.retired.json` 证据文件或移动至专用审计隔离目录，记录原/新路径、bytes、SHA、owner、mode、清理授权和时间；不应直接无证据删除。任一字段不符必须拒绝且不改变状态。

该清理只处理由送审测试产生的确定性伪对象，不属于新的材料、DFT 或软件路线选择；但在主 agent 实施前，应先由独立审计批准清理合同。清理后应复算真实状态五项哈希和正式 recovery 对象不存在性，再重新执行已隔离测试，并再次确认 runtime inventory 零变化。

## 放行判断

当前结论为 FAIL，`BLOCKING=2`、`NON_BLOCKING=0`。不得创建 gate、执行 recovery CLI 或重试 `source_prepare`。主 agent可修复测试隔离，并起草上述一次性污染清理合同；在独立审计批准前不得移动、删除或改写伪 transaction。

只有 B05 与 R3-B01 均关闭、最终测试证明零正式运行态写入、冻结闭集重新达到 `N/N` 匹配，并由独立审计产生唯一结构化零问题 PASS verdict 后，才允许创建 source-control gate。本轮 B04 的关闭不等同于恢复已获放行。

## 报告终检

本报告定稿后执行严格 Pandoc/MathML 转换、活动本地 Markdown 链接检查、UTF-8 非法控制字符扫描和最终 SHA-256 复算；结果随交付消息报告。
