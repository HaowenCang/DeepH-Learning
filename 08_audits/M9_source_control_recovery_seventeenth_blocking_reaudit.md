# M9 source-control recovery 第十七次阻塞项复核

## 结论

本轮结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。将 manifests 目录从 UID/GID 1000、0755 加固为 root:1000、0750，且 cleanup 对象改为 root:root、0600，能够关闭 UID 1000 在 cleanup 提交窗口创建硬链接的路径。但该权限状态被设计为永久终态；后续 `command_overlap_run` 明确要求 EUID 1000，并需要在 manifests 目录创建临时文件、原子替换状态和追加 ledger。UID 1000 在 root:1000、0750 目录没有写权限，因此 `source_prepare` 合同将稳定失败。当前没有独立、审计化的权限恢复或隔离写入方案。

不得创建或执行 cleanup gate，不得执行 cleanup、source-control recovery 或 `source_prepare`。

## 冻结快照与复算结果

- `m9_budget.py`：`9c7940eec26b92040fb00841b1cd32f699c76cdb5861023906e7b428d792902f`
- `test_m9_overlap_controls.py`：`5c27d71421809791c2d5fc646ed15d8fb60f41cb9095030693bd9c3590d20903`
- source manifest：`462691432a92b94ed85cd10e52f1f014eb839952523ef487f767779459fe416f`，17/17 文件匹配
- cleanup manifest：`3061638785030eda59566295fee78f743cd575b9d29a113de34c2eb1d3f5f2c5`，4/4 文件匹配

冻结 Python 3.9 以 `-I -S -B` 运行 49/49 测试通过。测试前后五项正式 runtime 及伪 transaction 的 SHA-256 完全不变。当前正式 manifests 目录仍为 UID/GID 1000、0755；五项 runtime 和伪 transaction 仍由 UID 1000 所有。retired、receipt、journal 和 cleanup gate 均不存在。

## 已关闭子条件

gate 严格绑定目录权限从 UID/GID 1000、0755 到 root:1000、0750。root 在锁内执行 chown/chmod，并复核结果。active 或 retired artifact 被加固为 root:root、0600；新 journal 与 receipt 通过 root 私有原子写入创建。UID 1000 在 0750 目录不再具有目录写权限，因此不能在 cleanup 最终检查与 SUCCESS 提交之间创建新硬链接。既有 nlink、symlink、bootstrap、UTC、PREPARED、RENAMED 和 SUCCESS 检查未发现回归。

## 阻塞项

### M9-SPR-R17-B01：加固终态破坏后续 UID 1000 运行合同

目录加固函数在已处于 root:1000、0750 时直接视为成功，并没有后续恢复步骤。cleanup receipt context 也把该状态记录为终态。source-control recovery 以 root 运行，仍可在目录中写入并通过 `preserve_owner` 把普通状态文件交还 UID 1000；但紧接其后的正式 overlap 执行入口明确拒绝非 EUID 1000。

`command_overlap_run` 在每次动作中调用 `atomic_json` 创建 `*.tmp` 并 `os.replace` 状态、workflow 和 transaction，同时追加 budget ledger。目录 mode 0750 对 GID 1000 只有读和执行权限，没有写权限。即使现有文件本身为 UID 1000、0644，创建临时文件和 rename 仍需目录写权限；因此 UID 1000 的 `source_prepare` 必然在控制写入阶段失败。

最小关闭条件：必须增加独立、可审计的 post-cleanup 权限生命周期合同，而不是简单恢复 0755。该合同应同时保证：cleanup 终态 retired/journal/receipt 不能被 UID 1000 修改、替换、删除或硬链接；正式 runtime 状态目录仍允许 UID 1000 进行受控 atomic write；目录与对象应分区到不同受保护子目录，或由可信 root broker 执行状态提交。若确需权限迁移，应具有单独 gate、状态机、崩溃恢复、pre/post owner/mode/inventory receipt，并在 source recovery 与 `source_prepare` 前独立复核。

### M9-SPR-R9-B01：安全合同测试仅验证加固，不验证后续可执行性

新增测试只断言 `prepare_cleanup_parent_security` 调用 chown/chmod 并返回 root:1000、0750。它没有以 UID 1000 验证 `atomic_json` 临时文件创建、ledger append 或 `command_overlap_run` 的最小控制写入，也没有覆盖 chown 成功但 chmod 失败、权限已半迁移时的重入、root 私有对象与恢复权限之间的隔离矩阵。因此 49/49 不能证明 cleanup 后路线可继续。

最小关闭条件：增加真实权限语义测试，至少验证 post-cleanup、post-source-recovery 和 pre-source_prepare 各阶段的目录/object owner/mode、允许和禁止的 UID 1000 操作、异常恢复与重入。测试应证明被允许的状态提交可成功，同时 retired 证据不能被修改、替换、删除或增加链接。

## 放行判断

当前为 `BLOCKING=2`、`NON_BLOCKING=0`、FAIL。达到下一轮独立零问题 PASS 前，不允许建立 cleanup gate或移动伪 transaction。目录安全生命周期冻结并实际 cleanup 后仍须独立复核，不能自动授权 source-control recovery 或 `source_prepare`。

## 报告终检

本报告定稿后执行严格 Pandoc/MathML、Markdown 本地链接、UTF-8、控制字符和 SHA-256 终检。报告不包含数学表达式或本地链接；MathML 和链接期望计数均为零。
