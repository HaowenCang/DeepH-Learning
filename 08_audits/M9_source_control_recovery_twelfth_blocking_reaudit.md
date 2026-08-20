# M9 source-control recovery 第十二次阻塞项复核

## 结论

本轮结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。上一轮发现的 RENAMED journal `retired_receipt` 漂移已能在写入前拒绝，`M9-SPR-R3-B01` 的该子条件已经关闭。然而，RENAMED 恢复分支不检查 retirement receipt 是否已经存在及其内容，任何既存 receipt 都会被覆盖为新的 PASS receipt，并将 journal 提交为 SUCCESS_COMMITTED。独立重放已证明伪造 receipt 会被静默覆盖。因此，事务仍不能安全恢复“receipt 已落盘、SUCCESS journal 尚未落盘”的真实崩溃窗口，`M9-SPR-R3-B01` 仍为 OPEN。

现有 41 项测试仅新增 RENAMED journal `retired_receipt` 的单一 SHA 漂移负例；active 漂移测试仍未调用命令主体，既存 receipt、both/neither、完整 gate 字段及五项 runtime 值的对抗矩阵仍缺失。因此，`M9-SPR-R9-B01` 仍为 OPEN。

不得创建或执行 cleanup gate，不得执行 cleanup、source-control recovery 或 `source_prepare`。

## 冻结快照与复算结果

- `m9_budget.py`：`13124bb8ac8897e90e868eae4e20f67246af9586b145e91583a847a3ebddf105`
- `test_m9_overlap_controls.py`：`13d2ad1104e409636a05cead260c27671933916e7a27f0c405930e79cc96ac0d`
- source manifest：`70be62cfac38acb8703500df16a2348bcc0fc5661b461cf0fba3d2d69b969d6f`，17/17 文件匹配
- cleanup manifest：`050089da26f0e675224c549394900568e49024f06713a4d64ed598f6509000c7`，4/4 文件匹配

冻结 Python 3.9 以 `-I -S -B` 运行 41/41 测试通过。测试前后五项正常 runtime 及伪 transaction 的 SHA-256 完全不变；伪 transaction 仍为 SHA-256 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`。控制目录没有 `.pyc`、`.pyo` 或 `__pycache__`。

## 阻塞项

### M9-SPR-R3-B01：OPEN

当前代码在 RENAMED 状态下已经要求 journal 中的 `retired_receipt` 严格等于当前 retired artifact receipt。独立重放上一轮的错误 SHA journal 得到拒绝，且没有生成 receipt；这一修复有效。

剩余问题位于紧接其后的提交步骤。正常写入顺序为 RENAMED journal、retirement receipt、SUCCESS_COMMITTED journal。若进程在第二步后崩溃，恢复现场必然是 journal 为 RENAMED 且 receipt 已存在。当前恢复分支不区分 receipt 缺失与已存在，也不读取或验证既存 receipt，而是无条件调用原子写入覆盖该路径，然后提交 SUCCESS_COMMITTED。

独立临时状态树重放构造了正确的 gate context、original receipt、RENAMED journal `retired_receipt` 和当前 retired artifact，同时预先写入内容为 `{"status":"FORGED"}` 的 receipt。命令返回 0，将该文件覆盖为 PASS，并把 journal 提交为 SUCCESS_COMMITTED。该路径会静默消除损坏、替换或未授权写入证据；对于合法的半提交 receipt，也会重写其 UTC 与 bootstrap 证据，因而不具备幂等补提交性质。

最小关闭条件：在 PREPARED 或 RENAMED journal 存在时，应明确处理 receipt 状态。PREPARED 下 receipt 必须不存在，否则零写入拒绝。RENAMED 下若 receipt 不存在，可以创建一次；若已存在，则必须严格验证固定 schema、PASS status、reason、original、retired、context 及受约束的 bootstrap provenance，验证成功后保留原字节并只补提 SUCCESS journal；任一字段、格式、owner、mode 或路径异常均须零写入拒绝。SUCCESS_COMMITTED 终态也应验证 receipt 的 schema、reason 和必要 provenance，而不只验证核心字典。

### M9-SPR-R9-B01：OPEN

新增 `test_cleanup_renamed_receipt_drift_rejects_through_command` 已真实调用命令主体，并覆盖 RENAMED journal 中 SHA 漂移的一个负例。它关闭了第十一次报告中的具体重放，但没有覆盖本轮发现的既存 receipt 分支。

`test_cleanup_prepared_active_drift_is_zero_write` 仍只比较 mock receipt 与 original 字典，没有调用 cleanup 命令，也没有断言 journal、receipt 和目录 inventory 的逐字节零写入。测试仍缺少 PREPARED/RENAMED 下既存 receipt 的合法半提交与伪造内容、both/neither、receipt owner/mode/schema/reason/provenance、SUCCESS 三方 receipt 漂移、gate schema/decision/report/authorization/frozen/artifact/runtime/absence 字段矩阵，以及五项 runtime 文件逐值漂移矩阵。本轮 41/41 测试未发现既存 receipt 覆盖穿透。

最小关闭条件：增加完整临时 gate、runtime、journal、artifact、receipt 和 lock 状态树的命令级测试。至少覆盖 receipt 缺失时一次写入、合法 RENAMED 半提交 receipt 的字节级保留、伪造或损坏 receipt 的零写入拒绝、PREPARED receipt 不可能状态、active 漂移、both/neither、SUCCESS 全字段验证；逐项断言退出状态、文件 inventory、内容哈希和权限。gate 与五项 runtime 应分别进行逐字段或逐值变异。测试前后继续复算正式 runtime inventory，且不得产生 Python cache。

## 放行判断

当前为 `BLOCKING=2`、`NON_BLOCKING=0`、FAIL。修复并再次独立复核达到零问题 PASS 前，不允许建立 cleanup gate，也不允许移动伪 transaction。后续即使 cleanup 工作包达到零问题 PASS，其授权范围也只应覆盖一次受控 retirement；实际执行结果仍须独立只读复核，不能自动授权 source-control recovery 或 `source_prepare`。

## 报告终检

本报告定稿后执行严格 Pandoc/MathML 转换、Markdown 本地链接、控制字符和 SHA-256 终检。报告不包含数学表达式或本地链接；因此 MathML 和链接检查的期望计数均为零。
