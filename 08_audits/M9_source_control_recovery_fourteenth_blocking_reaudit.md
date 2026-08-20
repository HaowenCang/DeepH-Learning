# M9 source-control recovery 第十四次阻塞项复核

## 结论

本轮结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。上一轮发现的 PREPARED 既存 receipt 先 rename 后拒绝和符号链接 artifact 获得 PASS 均已关闭；bootstrap、UTC、RENAMED、SUCCESS 和 active 漂移矩阵亦未发现回归。然而，文件身份合同仍未绑定硬链接计数。独立重放证明，具有第二个外部硬链接的 active 普通文件可以获得 PASS，retired 对象仍可通过外部链接改写。因此对象身份阻塞仍未关闭，现有 46 项测试也未覆盖该路径。

不得创建或执行 cleanup gate，不得执行 cleanup、source-control recovery 或 `source_prepare`。

## 冻结快照与复算结果

- `m9_budget.py`：`d3cefc474f47b5d1e6c3742963d93931a037d44c1b51acfdb76c45f9691674fb`，133649 bytes
- `test_m9_overlap_controls.py`：`ba9fd3f5fa4f045f71984aa1c59524128b0c4cb74458725a3742a3c129919c03`，62175 bytes
- source manifest：`e9ceeba4fe473cb1caa80640b53682739cebf8052fd447a2e3541906bbcbaf02`，17/17 文件匹配
- cleanup manifest：`f171ee7b8d6d7abaee7d2674b925a7e3664f8d9c8c59738312fc3b4983231644`，4/4 文件匹配

冻结 Python 3.9 以 `-I -S -B` 运行 46/46 测试通过。测试前后五项正常 runtime 及伪 transaction 的 SHA-256 完全不变；伪 transaction 仍为 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`。控制目录没有 `.pyc`、`.pyo` 或 `__pycache__`。

## 已关闭子条件

PREPARED journal 下 receipt 是否存在的检查已移动至任何 `os.replace` 之前。命令级测试构造正确 active 和既存 receipt，验证拒绝后 active、journal、receipt 原字节不变且 retired 不产生。上一轮的非零写入拒绝已经关闭。

命令在锁内、gate 和 runtime 验证后，对 active、retired、receipt 与 journal 四个固定路径统一执行 `is_symlink()` 拒绝。初始 active symlink 和 PREPARED 后 retired symlink 均在任何 cleanup 写入前拒绝；代码路径覆盖 RENAMED 与 SUCCESS。bootstrap 必须绑定本次 frozen provenance，receipt 必须具有可解析 UTC；合法 RENAMED 半提交保持 receipt 原字节，只补提终态 journal。上述定点重放未发现回归。

## 阻塞项

### M9-SPR-R13-B01：硬链接对象身份未绑定

符号链接已禁止，但 `file_stat_receipt()` 只记录 path、bytes、SHA-256、UID、GID 和 mode，不记录文件类型、device、inode 或 link count。普通文件具有多个硬链接时，`is_symlink()` 为假，现有 receipt 也与单链接对象相同。

独立重放复制固定伪 transaction 为 active 普通文件，再为同一 inode 创建第二个硬链接。命令返回 0，写入 PASS receipt 和 SUCCESS_COMMITTED journal；retired 的 `st_nlink` 仍为 2，外部硬链接仍存在。cleanup 后，外部路径可修改同一 inode，使 retired 证据发生变化；同时，“把固定伪对象移入 retired 路径”的独占对象语义不成立。

最小关闭条件：应使用不跟随链接的 `lstat`/`fstat` 证据要求 active 和 retired 均为普通文件且 `st_nlink == 1`，并把必要文件身份字段纳入 original/retired receipt。检查必须覆盖初始、PREPARED active、PREPARED rename 后、RENAMED 与 SUCCESS；rename 前后均复核。硬链接或特殊文件必须在任何 cleanup 写入前零写入拒绝。

### M9-SPR-R9-B01：对抗测试仍不足

46 项测试已覆盖 PREPARED 既存 receipt 顺序和 active symlink，但没有 active/retired 硬链接、FIFO/socket/device 等非普通文件以及 link count 漂移矩阵，因而未发现实际硬链接穿透。gate verifier 仍缺 schema、decision、report、authorization、frozen、artifact、五项 runtime 和 absence 字段的系统逐项变异测试。

最小关闭条件：增加完整命令级测试，至少覆盖 active 与各恢复状态 retired 的 `st_nlink > 1`、非普通文件、rename 前后 link count 漂移，并逐项断言零写入、路径、原字节、权限和 inventory。补齐 gate 及五项 runtime 的字段或值变异矩阵。测试前后继续复算正式 runtime inventory且不产生 Python cache。

## 放行判断

当前为 `BLOCKING=2`、`NON_BLOCKING=0`、FAIL。达到下一轮独立零问题 PASS 前，不允许建立 cleanup gate，也不允许移动伪 transaction。实际 cleanup 即使获得授权，完成后仍须独立只读复核，不能自动授权 source-control recovery 或 `source_prepare`。

## 报告终检

本报告定稿后执行严格 Pandoc/MathML、Markdown 本地链接、UTF-8、控制字符和 SHA-256 终检。报告不包含数学表达式或本地链接；MathML 和链接期望计数均为零。
