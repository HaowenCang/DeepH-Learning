# M9 overlap-only 离线 apt 恢复第四次定点复核

## 复核结论

第四次定点复核结论为 `FAIL`。`M9-REC-B03` 与 `M9-REC-B04` 已满足上一轮全部最小关闭条件；`M9-REC-B02` 与 `M9-REC-B07` 仍为 `OPEN`。`M9-REC-B01`、`M9-REC-B05`、`M9-REC-B06` 未发现相邻回归。当前统计为 `BLOCKING=2`、`NON_BLOCKING=0`。

不得创建状态为 `PASS` 的 recovery gate，不得执行离线安装，也不得进入恢复后的 source prepare 或构建。剩余问题都是局部控制与送审状态问题，不需要新的用户路线决策。

本轮送审快照的主要 SHA-256 为：

- `m9_budget.py`：`4a56c44171f8fe021cf14ba530d5d23644e9015e071db9036bf634a44cc69fee`；
- `m9_offline_recovery_frozen_hashes.json`：`463bec1098815e18ba74754cf659c8ca9cc1a16a49e79f412d54400ecd497c79`；
- `test_m9_overlap_controls.py`：`bfb5f20bb6f1a69cf091839421890ea5838ebebf78458b8093d4cc4fb806b1bf`；
- 第三次复核报告：`79344b638dfaa9bba713758ba797a6ed7d69517991defed8325589f4bf44d683`。

## 审计方法和边界

本次只读检查代码、候选 frozen manifest、控制目录和历史报告，并执行冻结 Python 22 项测试、callback 异常真实子进程重放、gate 集合复算及报告文本穿透。没有创建 gate，没有安装或配置软件包，没有改变预算、workflow 或 transaction，没有解压或编译 HDF5/OpenMX。callback 负例产生的临时 sleep 子进程由被审函数自身终止并回收。

冻结 Python 以 `-I -S -B` 运行正式测试，22/22 通过。该结果作为回归证据；下述两项定向穿透未包含在当前正式测试中。

## 已关闭项

### `M9-REC-B03`：`CLOSED`

正常 spawn 后，callback 立即记录 PID、PGID、`/proc/<pid>/stat` starttime、cmdline SHA-256、命令 SHA-256与 active 状态。重入不再只以 PID 存活判断，而是重新读取进程 receipt 并逐项比较 PGID、starttime 和 cmdline hash；PID 重用不能满足该身份。

`run_recovery_child()` 现在捕获 callback 的任意异常，先向新进程组发送 TERM 并等待，必要时升级 KILL 并再次回收，之后才重抛异常。独立用 `/bin/sleep 30` 和故意抛错 callback 重放，函数返回异常后 `kill(pid,0)` 已不能探测该进程。第三次报告的 callback 失败遗留活动进程和 PID 身份缺口已关闭。

### `M9-REC-B04`：`CLOSED`

ledger parser 现在拒绝无效 JSON、非 object 和重复 event ID；同 ID 的 payload 以 canonical hash 绑定，`append_event_once()` 只有在已存在载荷完全一致时才幂等返回，否则拒绝。resume 和初次成功提交均重新比较完整规范载荷 hash，ledger 写入继续执行 flush 与 fsync。

空账本时返回 `set()` 而正常返回 `dict` 是类型不一致，但对当前唯一调用的空容器 membership 与 `.get()` 路径存在潜在差异：`resume_pending_recovery_commit()` 会对结果调用 `.get()`，因此真正的空 ledger 会触发异常。不过正式 M9 ledger 已包含历史事件，且恢复 transaction 绑定其非空前缀；当前运行路径不存在空 ledger。该差异不构成本次实际阻塞，但建议以后统一返回空字典。

第三次报告指出的损坏行和重复 ID 穿透已关闭。

### 既有关闭项相邻回归

来源索引与 InRelease 关系、45 个归档合同、pre/post dpkg 全记录精确比较、pre-ledger 与父原字节快照绑定均保持。未发现 B03/B04 修订影响 `M9-REC-B01`、`M9-REC-B05` 或 `M9-REC-B06`。

## 仍开放的阻塞项

### `M9-REC-B02`：报告结论以任意子串判断，可由历史 FAIL 报告穿透

recovery gate 与 follow-up manifest 的集合矛盾已经修复：代码必需集合为 19 项，去掉 manifest 自身后与 manifest 内 18 项精确相等。候选 manifest 的 18 个文件哈希和顶层 contract hash也一致。

但 gate 对审计结论的验证仅检查报告正文是否分别包含字符串 `PASS`、`BLOCKING=0`、`NON_BLOCKING=0`。历史三份正式 FAIL 报告均在描述关闭条件或禁止事项时包含这三个字符串；独立扫描确认三份报告都满足当前布尔条件。因此 gate 可以绑定第三次 `FAIL/BLOCKING=4` 报告的真实 SHA-256，同时把 gate 自报为 PASS，并通过报告检查。

将报告限制在 `08_audits` 目录不能解决语义伪造；任意普通 Markdown 也可加入三个字符串。

最小关闭条件：不要从自由文本搜索结论。应固定唯一下一次复核报告路径，并由独立审计交付一个结构固定、被 gate 精确绑定的机读 verdict，例如 JSON 中严格等于 `status=PASS, blocking=0, non_blocking=0, audit_report_sha256=<exact>`；机读 verdict 自身也必须进入 gate/frozen 闭集。若仍解析 Markdown，应只解析唯一、锚定、禁止重复的结构化 front matter 或最终门控表，并拒绝正文其他位置的同名字段。增加历史三份 FAIL 报告、正文诱饵、重复字段、路径替换和真正 PASS verdict 正例。

### `M9-REC-B07`：控制目录 cache 在送审快照中重现

follow-up frozen manifest 已加入顶层 contract hash，登记 12 个实际控制 Python 文件和全部恢复/合同对象；18/18 当前哈希匹配。从文件集合设计看，第二、三次报告指出的 follow-up 缩减和 gate 集合矛盾已修复。

但复核开始时实际控制目录存在 `06_reproduction/scripts/__pycache__/m9_budget.cpython-39.pyc`。`verify_overlap_control_directory()` 明确拒绝任意子目录、pyc 或未登记项，故 follow-up verifier 在当前状态仍必然失败。主证据所称“显式移除 scripts __pycache__”与实际送审快照不一致；很可能是随后执行 `py_compile` 又生成了 cache。

最小关闭条件：删除该 cache 目录并在所有正式测试和 compile 检查中使用不会向控制目录写 bytecode 的方式；终检时应证明控制目录恰为 frozen manifest 登记的 12 个普通 `.py` 文件。增加完整候选 gate 下的 `verify_recovered_overlap_gate_and_hashes()` 真实正例，并在该正例之后再次枚举控制目录，确认没有测试自生成 cache。

## 最终门控

- 第四次定点复核：`FAIL`；
- `BLOCKING=2`；
- `NON_BLOCKING=0`；
- 不允许创建 PASS recovery gate；
- 不允许执行离线安装或恢复后 follow-up；
- 当前无需新的用户路线决策。

主 agent 应只修复 B02 的结构化 verdict 绑定和 B07 的 cache/真实 follow-up 正例，再交回独立定点复核。

## 报告终检

本报告定稿后执行 UTF-8 控制字符扫描、活动本地 Markdown 链接检查，以及 Pandoc `markdown+tex_math_single_backslash` 到 HTML5 MathML 的 `--fail-if-warnings` 严格转换。用于验证 MathML 的恒等式为 \(22=22\)。最终 SHA-256 在交付消息中报告。
