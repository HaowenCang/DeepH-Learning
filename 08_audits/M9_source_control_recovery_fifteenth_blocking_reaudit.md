# M9 source-control recovery 第十五次阻塞项复核

## 结论

本轮结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。初始硬链接对象已能在 rename 前零写入拒绝，但 single-link 检查只在命令入口执行一次。独立重放在 active 到 retired 的 rename 后立即增加第二个硬链接，后续仍写入 PASS receipt 和 SUCCESS_COMMITTED journal。硬链接对象身份阻塞仍未关闭，现有 47 项测试未覆盖 rename 后 link count 漂移。

不得创建或执行 cleanup gate，不得执行 cleanup、source-control recovery 或 `source_prepare`。

## 冻结快照与复算结果

- `m9_budget.py`：`ffabb24a96ac101760b0b85efafb4bf2c4ac21a1a925c769c0134c3d3873e06c`
- `test_m9_overlap_controls.py`：`d79d3bbf657a21b34e893671b855a722530c60b01826e2d7680521fb62f23466`
- source manifest：`2747d354d1ad1a7b0c7cd572978d1f0b3e23d8fdcc11a5b23425587b7f28856a`，17/17 文件匹配
- cleanup manifest：`5fb02f0963cf7f4466d016f49ce963aa162fef214e79268d181dcf4449a02169`，4/4 文件匹配

冻结 Python 3.9 以 `-I -S -B` 运行 47/47 测试通过。测试前后五项正式 runtime 及伪 transaction 的 SHA-256 完全不变；控制目录没有 `.pyc`、`.pyo` 或 `__pycache__`。

## 已关闭子条件

命令在锁内对 active、retired、receipt 和 journal 固定路径拒绝 symlink，并对当时已存在的路径要求 `lstat().st_nlink == 1`。初始 active 硬链接测试会在任何 cleanup 写入前拒绝。PREPARED 既存 receipt 也已在 rename 前拒绝。bootstrap、UTC、RENAMED 合法半提交字节保留、伪造 receipt、SUCCESS 终态和 PREPARED active 漂移均未发现回归。

## 阻塞项

### M9-SPR-R13-B01：rename 后 link count 漂移可获得 PASS

single-link 检查仅在读取 journal 和执行 rename 之前发生一次。`file_stat_receipt()` 仍不记录 `st_nlink`、device 或 inode，rename 后、RENAMED 恢复和 SUCCESS 终态均没有再次执行不跟随链接的 link count 检查。

独立重放使 active 在入口时为单链接普通文件，因此通过前置检查；在 `os.replace(active, retired)` 返回后立即为 retired inode 创建第二个硬链接。命令随后正常读取 bytes、SHA、UID、GID 和 mode，写入 PASS receipt 与 SUCCESS_COMMITTED journal并返回 0。终态 retired 的 `st_nlink` 为 2，外部链接存在。该外部路径可以继续修改同一 inode，破坏 retired 证据。

最小关闭条件：把普通文件类型和 `st_nlink == 1` 纳入不跟随链接的文件身份 receipt，并在每个关键阶段重新核验：初始 active、rename 前 active、rename 后 retired、PREPARED rename 后恢复、RENAMED、写 receipt 前及 SUCCESS。应尽可能基于已打开文件描述符执行 `fstat` 与内容哈希，降低 path 级 TOCTOU；link count 或 inode/device 漂移必须在 PASS 写入前拒绝。增加 rename 后注入硬链接及恢复态硬链接的命令级负例。

### M9-SPR-R9-B01：对抗测试仍不足

47 项测试只覆盖入口已有硬链接，没有覆盖检查后至 rename、rename 后至 receipt、RENAMED 恢复及 SUCCESS 终态的 link count 漂移。因此全部测试通过仍未发现上述实际穿透。gate verifier 的 schema、decision、report、authorization、frozen、artifact、五项 runtime 和 absence 字段系统变异矩阵仍不完整。

最小关闭条件：补充各状态和写入边界的硬链接注入测试，断言拒绝时 journal、receipt、artifact 和目录 inventory 的允许变化；补齐 gate 与 runtime 值的逐项变异。测试前后继续复算正式 runtime inventory且不产生 Python cache。

## 放行判断

当前为 `BLOCKING=2`、`NON_BLOCKING=0`、FAIL。达到下一轮独立零问题 PASS 前，不允许建立 cleanup gate或移动伪 transaction。实际 cleanup 后仍须独立只读复核，不能自动授权 source-control recovery 或 `source_prepare`。

## 报告终检

本报告定稿后执行严格 Pandoc/MathML、Markdown 本地链接、UTF-8、控制字符和 SHA-256 终检。报告不包含数学表达式或本地链接；MathML 和链接期望计数均为零。
