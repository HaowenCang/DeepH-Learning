# M9 source-control recovery 第十六次阻塞项复核

## 结论

本轮结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。`nlink=1` 已进入 cleanup receipt，并在 rename 后、恢复态和终态多次复核；既有 48 项测试中的 rename 后硬链接注入也能在 receipt 写入前拒绝。然而，最后一次 link-count 检查与 SUCCESS journal 原子写之间仍有可利用窗口。独立重放在该窗口增加第二个硬链接，命令仍返回 0并形成 PASS/SUCCESS。正式 manifests 目录由 UID 1000 所有且 mode 0755，而 cleanup 以 root 执行；另一个 UID 1000 进程不受 budget lock 约束，能够实际实施该并发写入。

不得创建或执行 cleanup gate，不得执行 cleanup、source-control recovery 或 `source_prepare`。

## 冻结快照与复算结果

- `m9_budget.py`：`5c089486ce5d2ebccc48124775c0db6496c14ab709f02cda1e6b4b8756958cb2`
- `test_m9_overlap_controls.py`：`ef6a7497d83f150ee5372de60928178adba6757e5c2579947d9d2c447b1a0f55`
- source manifest：`9be64d366b1feab7b6928e99c8db377c6c5346e9660357e82154fcc1a2aba08f`，17/17 文件匹配
- cleanup manifest：`4b55e969dd17cb4ee6ac39ebfc78139d7443a0d16e5726870ba22f0e3d77284f`，4/4 文件匹配

冻结 Python 3.9 以 `-I -S -B` 运行 48/48 测试通过。测试前后五项正式 runtime 及伪 transaction 的 SHA-256 完全不变；控制目录没有 `.pyc`、`.pyo` 或 `__pycache__`。

## 已关闭子条件

cleanup 专用 receipt 现在记录 `nlink=1`。入口、PREPARED active、rename 后 retired、PREPARED rename 后恢复、RENAMED、写 receipt 前和 SUCCESS 读取均重复执行 single-link 检查。入口已有硬链接和在 `os.replace` 返回后立即注入硬链接均会拒绝，且后者不会生成 receipt。bootstrap、UTC、合法半提交 receipt 字节保留、伪造 receipt、PREPARED receipt 预检、symlink 与 active 漂移均未发现回归。

## 阻塞项

### M9-SPR-R13-B01：最终检查至 SUCCESS 提交仍有并发窗口

正常路径在写 PASS receipt 后，设置内存 journal 为 SUCCESS_COMMITTED，调用一次 `cleanup_assert_single_link(retired)`，随后原子写终态 journal。检查与终态提交不是不可分割操作；目录级写入权限也没有在该区间被撤销。

独立重放在最后一次 `cleanup_assert_single_link` 返回后、SUCCESS journal 的原子写开始前为 retired inode 创建第二个硬链接。命令返回 0，retired 的 `st_nlink` 为 2，PASS receipt 和 SUCCESS_COMMITTED journal 均存在。另一次重放在 PASS receipt 写入后注入链接：命令虽然拒绝，但现场保留 PASS receipt 和 RENAMED journal，说明失败现场还需要明确的安全恢复合同。

该并发不是仅存在于 mock 的理论路径。正式 manifests 目录为 UID/GID 1000、mode 0755；cleanup 要求 root 执行。UID 1000 的并发进程不需要获取 root 持有的 budget lock，即可在目录中创建指向 retired inode 的硬链接。

最小关闭条件：cleanup 事务期间必须建立所有潜在写入者都不能绕过的目录级排他条件，而不只是约定式文件锁。可行合同应明确记录并验证事务前后目录 owner/mode，并在 root 锁内临时移除 UID 1000 的目录写权限，完成终态写入和最终 `lstat` 后再按受控顺序恢复；或者采用等价的受保护目录/挂载机制。若恢复目录权限后外部仍可增加链接，则终态证据不能宣称永久不可变，执行后独立审计必须在继续 source recovery 前再次复核 nlink、inode和内容。对 receipt 已写但终态未提交的失败现场，应保留可验证的幂等恢复路径。

### M9-SPR-R9-B01：测试未覆盖最终提交窗口与真实目录权限

48 项测试覆盖 `os.replace` 后立即注入硬链接，但没有覆盖 PASS receipt 后、最后检查后至 SUCCESS 写入、SUCCESS 写入后以及目录权限恢复边界。测试也没有验证正式 manifests 目录的 owner/mode 与并发 UID 1000 写入能力，因而未发现上述可执行窗口。gate verifier 的 schema、decision、report、authorization、frozen、artifact、五项 runtime 和 absence 字段系统变异矩阵仍不完整。

最小关闭条件：增加各提交边界的并发注入测试，并验证目录权限变化、异常恢复、receipt 半提交和最终恢复权限后的独立复核条件。补齐 gate/runtime 逐字段变异；测试前后继续复算正式 runtime inventory且不产生 Python cache。

## 放行判断

当前为 `BLOCKING=2`、`NON_BLOCKING=0`、FAIL。达到下一轮独立零问题 PASS 前，不允许建立 cleanup gate或移动伪 transaction。实际 cleanup 后仍须独立只读复核，不能自动授权 source-control recovery 或 `source_prepare`。

## 报告终检

本报告定稿后执行严格 Pandoc/MathML、Markdown 本地链接、UTF-8、控制字符和 SHA-256 终检。报告不包含数学表达式或本地链接；MathML 和链接期望计数均为零。
