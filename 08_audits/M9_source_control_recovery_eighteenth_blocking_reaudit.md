# M9 source-control recovery 第十八次阻塞项复核

## 结论

本轮结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。root:1000、1770 sticky 目录同时满足两项核心运行语义：UID 1000 不能删除或硬链接 root:root、0600 的 cleanup 证据，又能创建临时文件并原子替换其本人所有的 runtime 文件。此前 TOCTOU 与后续 `overlap_run` 可写性冲突已关闭。然而，目录和 artifact 权限迁移是多系统调用序列，缺少迁移 journal 与中间态恢复。`chown` 成功而 `chmod` 失败时会产生既非 before 也非 hardened 的状态，下一次运行稳定拒绝，无法继续或有审计化回滚。

不得创建或执行 cleanup gate，不得执行 cleanup、source-control recovery 或 `source_prepare`。

## 冻结快照与复算结果

- `m9_budget.py`：`846ea30551f50764561a7f1761a7c735b2bbc2b9ad1c4dd2f23783aad155d665`
- `test_m9_overlap_controls.py`：`7598854f2a948b7d4182166722e40a5ebfc714a0d948d1abf3d1f70757a52ce2`
- source manifest：`ca8b094bd559c0e45ba2bf9fba451a98283ded87765fb84f7b216d6ae4d24ce6`，17/17 文件匹配
- cleanup manifest：`fb81bedcf726c248a8ce5ce5837db90307a3e8b98e922900d750f61af9da5c64`，4/4 文件匹配

冻结 Python 3.9 以 `-I -S -B` 运行 50/50 测试通过。测试前后五项正式 runtime 及伪 transaction 的 SHA-256 完全不变；控制目录没有 `.pyc`、`.pyo` 或 `__pycache__`。

## 已关闭子条件

gate 绑定目录从 UID/GID 1000、0755 迁移为 root:1000、1770，并以该 sticky 权限作为成功终态；绑定 `protected_hardlinks=1`。cleanup artifact、journal 和 receipt 为 root:root、0600。

独立 root/UID 1000 权限试验证明：在 root:1000、1770 目录中，UID 1000 删除 root:root、0600 retired 返回 EPERM，创建其硬链接也被 `protected_hardlinks=1` 拒绝；同一 UID 可以创建 runtime 临时文件，并原子替换 UID 1000 所有的 runtime 文件。因此 cleanup 证据保护与后续 `command_overlap_run` 目录写入可同时成立。

## 阻塞项

### M9-SPR-R18-B01：权限迁移中间态不可恢复

目录迁移依次执行 `chown(parent, 0, 1000)` 与 `chmod(parent, 01770)`，没有先写迁移 journal，也没有异常补偿。如果 chown 成功而 chmod 失败，现场为 root:1000、0755。`prepare_cleanup_parent_security` 的重入只接受原始 1000:1000、0755或完整 hardened root:1000、1770；该半迁移状态会稳定触发 precondition mismatch。

artifact 加固也依次执行 chown root:root、chmod 0600。若第二步失败，现场 root:root、0644既不满足原始 1000:1000、0644，也不满足 hardened root:root、0600；下一次运行同样稳定拒绝。journal 尚未建立时，这些中间态没有事务 ID、原始 receipt、失败阶段或授权绑定，不能区分本次受控半迁移与外部漂移。

最小关闭条件：在任何 chown/chmod 前建立 root 私有、冻结 gate 绑定的安全迁移 journal，记录目录和 artifact 的完整 before/hardened receipt及当前 phase。重入应只对精确可证明的中间态执行幂等补提交；任一额外漂移拒绝。每个系统调用后更新 phase并 fsync。对首次 journal 写入本身也需有预定义固定路径与安全创建合同。补充 chown 成功/chmod 失败、journal 各半提交点、重复运行及外部漂移测试。

### M9-SPR-R9-B01：测试未覆盖权限迁移失败矩阵

50 项测试通过 mock 验证正常 chown/chmod 调用和最终状态，但没有令各系统调用逐点失败并重入；也没有覆盖目录 root:1000、0755、artifact root:root、0644、journal 写入半提交或 chown/chmod 顺序异常。因此无法支持“失败保持硬化且可恢复”的合同。

最小关闭条件：增加目录与 artifact 每个权限系统调用的失败注入、完整文件 inventory、权限 receipt、journal phase和重入测试。正式测试前后继续复算 runtime，且 cache 必须为零。

## 放行判断

当前为 `BLOCKING=2`、`NON_BLOCKING=0`、FAIL。达到下一轮独立零问题 PASS 前，不允许建立 cleanup gate或移动伪 transaction。实际 cleanup 后仍须独立只读复核，不能自动授权 source-control recovery 或 `source_prepare`。

## 报告终检

本报告定稿后执行严格 Pandoc/MathML、Markdown 本地链接、UTF-8、控制字符和 SHA-256 终检。报告不包含数学表达式或本地链接；MathML 和链接期望计数均为零。
