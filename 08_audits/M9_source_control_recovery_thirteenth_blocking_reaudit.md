# M9 source-control recovery 第十三次阻塞项复核

## 结论

本轮结论为 **FAIL**：`BLOCKING=3`，`NON_BLOCKING=0`。上一轮要求的 frozen bootstrap 绑定、receipt UTC、合法 RENAMED 半提交字节保留、伪造 receipt 拒绝、SUCCESS 终态验证及 PREPARED active 漂移命令级拒绝均已实现并通过定点重放。然而，独立状态矩阵仍发现两条可稳定穿透的执行路径：PREPARED 下既存 receipt 的拒绝发生在 active 已被 rename 之后；初始 artifact 可以是指向同哈希文件的符号链接并最终获得 PASS。现有 44 项测试没有覆盖这两条路径，测试门控阻塞也未关闭。

不得创建或执行 cleanup gate，不得执行 cleanup、source-control recovery 或 `source_prepare`。

## 冻结快照与复算结果

- `m9_budget.py`：`ecc1ced3ef1957783d9c4f20021bae8b8613fc6e6918a2d89d7e97eacab4de9a`，133295 bytes
- `test_m9_overlap_controls.py`：`ac8c9770aed9734e5c1fe8c2367c45f1fd5dd938cce8db594bc0e16e4b1412cf`，57529 bytes
- source manifest：`468021d4ece9e3f10be80043c4a0ba7ca1b381ac5456583374449a8873e2b298`，17/17 文件匹配
- cleanup manifest：`5ac4e77904d7042351aeceef24d40bdb7cceaa25063cf0ed0d661992fbd160f3`，4/4 文件匹配

冻结 Python 3.9 以 `-I -S -B` 运行 44/44 测试通过。测试前后五项正常 runtime 及伪 transaction 的 SHA-256 完全不变；伪 transaction 仍为 SHA-256 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`。控制目录没有 `.pyc`、`.pyo` 或 `__pycache__`。

## 已关闭子条件

RENAMED journal 已有合法 receipt 时，命令验证固定 schema、PASS、reason、original、retired、context、当前 frozen bootstrap、可解析 UTC 以及 UID/GID/mode，并保持 receipt 原字节，只补提 SUCCESS journal。伪造 receipt 和 SUCCESS 终态 receipt 异载荷均在写入前拒绝。journal 的 bootstrap 也必须等于本次 `isolated_bootstrap_provenance()`，因而此前“journal 与 receipt 共同伪造 bootstrap”的穿透已关闭。

PREPARED active receipt 漂移的正式命令级测试会断言 active、journal 原字节不变，且 retired 与 receipt 不产生；该特定子条件也已关闭。

## 阻塞项

### M9-SPR-R3-B01：PREPARED 既存 receipt 非零写入拒绝

PREPARED 分支先核 active receipt，然后执行 `os.replace(active, retired)`。代码直到 rename 完成、再次读取 retired receipt 之后，才进入统一的“receipt 已存在”分支并抛出 `cleanup PREPARED receipt must be absent`。

独立重放构造 PREPARED journal、正确 active artifact、retired 不存在以及内容为 `{}` 的既存 receipt。命令最终抛出预期错误，但现场已经变为 active 不存在、retired 存在；journal 和 receipt 原字节未变。即该不可能状态并非零写入拒绝，而是先执行授权对象的关键移动再拒绝。此后再次进入会走 PREPARED rename 后窗口，与原始异常现场无法等价区分。

最小关闭条件：在 PREPARED 分支执行任何 `os.replace` 之前，必须要求 retirement receipt 不存在；存在时应在 active、retired、journal、receipt 和目录 inventory 全部不变的条件下拒绝。对 PREPARED active 存在与 rename 后窗口两种形态均应执行该前置条件。

### M9-SPR-R13-B01：符号链接 artifact 可获得 PASS

入口仅使用 `Path.is_file()`、`Path.stat()` 和 `read_bytes()`；这些操作默认跟随符号链接。receipt 没有记录文件类型，rename 前后也没有 `is_symlink()` 或 `lstat()` 拒绝。因此，指向字节、owner、mode 和 SHA 均符合预期目标的符号链接可通过全部检查。

独立重放创建指向伪 transaction 副本的 active symlink。命令返回 0，把 symlink 本身 rename 为 retired symlink，生成 PASS receipt，并将 journal 写为 SUCCESS_COMMITTED；结果 `retired.is_symlink()` 为真。该路径没有原子移动授权中指明的固定普通文件对象，只移动了一个引用，且 retired 证据仍会随链接目标变化或消失。

最小关闭条件：初始、PREPARED active、PREPARED rename 后 retired、RENAMED 和 SUCCESS 全阶段均应使用不跟随链接的文件类型检查，明确要求 active/retired 是非 symlink 的普通文件。receipt 应绑定足以证明对象身份的 `lstat` 类型信息；rename 前后都应复核。任何 symlink、硬链接策略未满足的对象或特殊文件均须零写入拒绝。若硬链接也不允许，应固定 `st_nlink == 1`。

### M9-SPR-R9-B01：对抗测试仍不足

44 项测试已经显著增强，但没有 PREPARED 既存 receipt 在 rename 前零写入、active/retired symlink、特殊文件及链接计数矩阵，因而未发现上述两条实际穿透。gate verifier 也仍主要由代码检查和集成成功路径间接覆盖，缺少 schema、decision、report、authorization、frozen、artifact、runtime 五值和 absence 字段的逐项变异测试。

最小关闭条件：增加完整命令级临时状态树测试，覆盖 PREPARED 两种形态下 receipt 存在的零写入拒绝；active 与 retired 各阶段的 symlink、非普通文件和明确的硬链接策略；逐项断言错误、路径、原字节、权限和 inventory。补齐 gate 及五项 runtime 的字段或值变异矩阵。测试前后继续复算正式 runtime inventory且不产生 Python cache。

## 放行判断

当前为 `BLOCKING=3`、`NON_BLOCKING=0`、FAIL。达到下一轮独立零问题 PASS 前，不允许建立 cleanup gate，也不允许移动伪 transaction。后续即使工作包 PASS，授权范围也只覆盖一次 cleanup；实际执行结果仍须独立只读复核，不能自动授权 source-control recovery 或 `source_prepare`。

## 报告终检

本报告定稿后执行严格 Pandoc/MathML、Markdown 本地链接、UTF-8、控制字符和 SHA-256 终检。报告不包含数学表达式或本地链接；MathML 和链接期望计数均为零。
