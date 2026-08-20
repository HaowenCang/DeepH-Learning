# M9 source-control recovery 第十一次阻塞项复核

## 结论

本轮结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。上一轮指出的 PREPARED journal 已落盘、rename 已完成而 RENAMED journal 尚未落盘的崩溃窗口已经能够补提交；SUCCESS_COMMITTED 终态也已比较 journal、保存回执和当前 retired artifact 的完整 receipt。然而，RENAMED 恢复态仍会在不核对 journal 原有 `retired_receipt` 的情况下覆盖该字段并提交成功。独立重放已证明，错误 SHA 的 RENAMED journal 可以被静默“修复”为成功状态。因此，`M9-SPR-R3-B01` 仍为 OPEN。

现有 40 项测试新增了 PREPARED rename 后窗口正例，但 active 漂移测试仍未调用命令主体，也没有覆盖 RENAMED journal receipt 漂移、both/neither、完整 gate 字段或五项 runtime 值的对抗矩阵。因此，`M9-SPR-R9-B01` 仍为 OPEN。

不得创建或执行 cleanup gate，不得执行 cleanup、source-control recovery 或 `source_prepare`。

## 冻结快照与复算结果

- `m9_budget.py`：`1f8bbb3b709670e3bd4e9aaffe884de3ef96c2d2bdb17ff37b1f9f3d5a24b17c`
- `test_m9_overlap_controls.py`：`b67debf2fcb07c8423524a06367baad58b2abf4965b13956ce53b23cf50d0067`
- source manifest：`07417307cc5482559aa65a8454559601674478c0ccb6d20ae450881342fa5565`，17/17 文件匹配
- cleanup manifest：`5aeaf1cb05f8bb6e5fa64c1c06cf0ba9825bff936540c5ac00f6f1d7402d0f36`，4/4 文件匹配

冻结 Python 3.9 以 `-I -S -B` 运行 40/40 测试通过。测试前后五项正常 runtime 及伪 transaction 的 SHA-256 完全不变；伪 transaction 仍为 1644 bytes、UID/GID 1000、mode 0644、SHA-256 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`。cleanup gate、cleanup journal、retirement receipt、source-control gate 和 parent snapshot 均不存在。控制目录没有 `.pyc`、`.pyo` 或 `__pycache__`。

## 阻塞项

### M9-SPR-R3-B01：OPEN

当前实现已关闭两个重要子问题。PREPARED 状态在 active 存在时先比较完整 original receipt 后才 rename；在 active 不存在而 retired 存在时，将其识别为 rename 后崩溃窗口，并比较由 original receipt 仅替换 path 得到的完整 retired receipt。SUCCESS_COMMITTED 分支也已要求 `journal.retired_receipt == saved.retired == current retired`。这些修复经代码复核和临时状态树重放均成立。

剩余穿透位于 RENAMED 分支。代码只要求状态属于 PREPARED 或 RENAMED，随后重新读取当前 retired artifact，并直接执行 `journal["retired_receipt"] = retired`。它没有先要求 RENAMED journal 中已经保存的 `retired_receipt` 与当前 retired artifact、original receipt 的非 path 字段完全一致。

独立重放构造了以下状态：active 不存在；retired artifact 的完整 receipt 正确；journal 为 RENAMED；journal 的 `retired_receipt.sha256` 被改为 64 个零；gate、context、original receipt 和当前 retired receipt均正确。命令返回 0，创建 PASS receipt，并把错误字段覆盖为真实 SHA 后写成 SUCCESS_COMMITTED。该行为无法区分“上一次正常写入后继续提交”与“RENAMED journal 证据已损坏或被替换”，会把证据漂移静默归一化为成功。

最小关闭条件：RENAMED 分支应当要求 journal 已含完整 `retired_receipt`，且它严格等于当前 retired artifact receipt；同时应当等于 original receipt 将 path 精确替换为固定 retired path 后的结果。字段缺失、SHA/bytes/UID/GID/mode/path 任一漂移均须在 receipt 或终态 journal 写入前零写入拒绝。PREPARED rename 后崩溃窗口仍可由当前逻辑生成可信 `retired_receipt` 并推进 RENAMED。

### M9-SPR-R9-B01：OPEN

40 项冻结测试中的 `test_cleanup_prepared_after_rename_window_resumes_through_command` 已真实调用命令主体，能够关闭上一轮的特定崩溃窗口。但 `test_cleanup_prepared_active_drift_is_zero_write` 仍只直接比较两个 receipt 字典并检查路径，未调用 cleanup 命令，也没有断言 journal、receipt 和目录 inventory 的逐字节零写入。

测试仍缺少 RENAMED journal `retired_receipt` 缺失及各字段漂移、PREPARED both/neither、retired receipt 漂移、SUCCESS journal/saved/current 三方漂移、gate schema/decision/report/authorization/frozen/artifact/runtime/absence 字段矩阵，以及五项 runtime 文件逐值漂移矩阵。本轮 40/40 测试未发现上述 RENAMED 穿透。

最小关闭条件：增加通过完整临时 gate、runtime、journal、artifact 和 lock 路径调用命令主体的对抗测试。至少覆盖 PREPARED 正常、active 漂移零写入、rename 后崩溃续提、both/neither、RENAMED receipt 缺失及每字段漂移、SUCCESS 三方 receipt 漂移；逐项断言退出状态、文件 inventory、内容哈希及 receipt。gate 与五项 runtime 应分别进行逐字段或逐值变异。测试前后继续复算正式 runtime inventory，且不得产生 Python cache。

## 放行判断

当前为 `BLOCKING=2`、`NON_BLOCKING=0`、FAIL。修复并再次独立复核达到零问题 PASS 前，不允许建立 cleanup gate，也不允许移动伪 transaction。即使后续 cleanup 审计通过，其授权范围也只应覆盖一次受控 retirement；实际 cleanup 完成后还需对 journal、retirement receipt、runtime 不变性和 artifact 路径执行独立只读复核，不能自动授权 source-control recovery 或 `source_prepare`。

## 报告终检

本报告定稿后执行严格 Pandoc/MathML 转换、Markdown 本地链接、控制字符和 SHA-256 终检。报告不包含数学表达式或本地链接；因此 MathML 和链接检查的期望计数均为零。
