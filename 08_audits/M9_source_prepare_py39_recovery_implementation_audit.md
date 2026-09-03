# M9 source_prepare Python 3.9 失败恢复包独立实施审计

审计日期：2026-08-27；第二次定点复核：2026-08-28  
审计对象：`M9-SP-PY39-B01` 的 Python 3.9 兼容修复与一次性失败恢复实现  
审计方式：冻结闭集全量哈希、正式失败现场前后只读 receipt 对照、固定 Python 3.9 回归、工作区外临时夹具逐阶段故障注入、链接/元数据/锁身份主动穿透、状态与 ledger 不变量复算  
执行边界：未执行 `create-gate`、`recover`、`source_prepare`、`source_build`、安装、下载或任何正式运行态写入；未使用 `py_compile`；全部破坏性注入仅发生在系统临时目录

## 第二次定点复核结论（当前正式结论）

**verdict：PASS。`BLOCKING=0`，`NON_BLOCKING=0`。**

本轮以当前 22 文件冻结闭集为唯一实施基线，对开放 finding `M9-SP-PY39-RCV-R01` 的关闭条件执行定点复核，并重检初审 `M9-SP-PY39-RCV-B01`—`B04` 的关键边界。控制器现已明确 `PHASES`/`PHASE_INDEX`，只接受同阶段、journal-first 相邻阶段以及 terminal transaction-first 特例；孤儿 transaction 和非法 phase-pair 在任何续提写入前拒绝。从 `LEDGER_COMMITTED`、`STATE_COMMITTED`、`WORKFLOW_COMMITTED` 起，恢复在后续正式写入前分别读取 journal 与 recovery transaction 中已经持久化的 `post_ledger`、`post_state`、`post_workflow`，要求候选 receipt 相等，并用当前 runtime 的完整 receipt 逐字段闭合；后续阶段继承该持久化 receipt，不再用重新采集的 inode 身份重新定义提交事实。因此 `M9-SP-PY39-RCV-R01` 标记为 `CLOSED`。

独立系统临时夹具在上述三个 COMMITTED 阶段分别注入同字节新 inode、symlink、hardlink、mode 和 owner 漂移，共 15/15 例均在下一次控制或 runtime 写入前被拒绝，既有 journal 与 recovery transaction 字节保持不变。合法状态组合共 12 例可安全续提；非法非相邻组合 1/1 与孤儿 transaction 1/1 零写拒绝；terminal transaction 已为 `SUCCESS_COMMITTED` 而 journal 仍为 `WORKFLOW_COMMITTED` 的单边窗口可仅补齐 journal，随后终态重放对 ledger、state、workflow、journal 和 transaction 均保持 inode、大小与字节不变。原 14 个 atomic-json 中断窗口、snapshot、rename、partial ledger、retirement 四态、预算/历史、gate/scope 漂移及 build/input Python 3.9 LF 写入路径由冻结专用测试复验通过；B01—B04 未发现回归，也未形成未经授权的半清状态。

### 当前冻结证据与测试结果

| 对象 | SHA-256 |
|---|---|
| 工作包 | `d3c768f635564a67134f25e54f0419fb873dfbfb0a90f3838150ca8cf805444c` |
| 恢复控制器 | `2975bfe8151740ff88a509e1ec72e139c4b43df86c26dd24667c57252fdc336e` |
| 19-receipt 恢复合同 | `c1583a02cc7e1d6393f015e9a5bff2165e62b0941ffa47d00694f5d002ed1d7b` |
| 15 项专用测试 | `675844668be01179bcb5750d850076e2c21e8b6b45fe0bdf1feb0a80518b7743` |
| 22 文件冻结 manifest | `a538b521e91fb171b6e844dcce25439ccf43bb4f2fe6f8c263e1f39cad5250dd` |

所有测试均使用固定解释器 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B`，未使用 `py_compile`：

```text
wsl.exe -u root -- /home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B /mnt/e/Projects/Codex/DeepH/06_reproduction/tests/test_m9_overlap_controls.py
Ran 110 tests in 35.738s — OK

wsl.exe -u root -- /home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B /mnt/e/Projects/Codex/DeepH/06_reproduction/tests/test_m9_source_prepare_py39_recovery.py
Ran 15 tests in 7.363s — OK

wsl.exe -u root -- /home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B /mnt/c/Users/20659/AppData/Local/Temp/m9_r01_targeted_reaudit.py
PASS；receipt drift 15/15 零控制写入拒绝；合法 phase-pair 12/12 可续提；非法 pair 1/1、孤儿 transaction 1/1 零写拒绝；terminal transaction-first 1/1 可补齐；terminal replay 1/1 零写
```

临时复核脚本在执行后删除，未进入工作区或冻结证据集。正式现场复核前后均为：22/22 冻结成员匹配；19/19 runtime receipt 匹配；state/workflow 双 `HARD_STOP`；ledger 61,248 bytes、SHA-256 `a2170772c37b601112f0d957a18a6e9375dc7cf2eb22697a26b61a5db3ed770d`；staging 原位，retired 与四个 recovery 控制对象缺席；`06_reproduction` cache 为 0。正式运行态未发生写入。

本 PASS 仅适用于上述当前冻结闭集、合同及正式失败现场。它只授权后续由主 agent 创建一次 recovery gate 并执行一次 `recover`；不授权 `source_prepare`、`source_build` 或任何后续计算。恢复完成后仍须按工作包执行事实审计、重建 consumer gate，并在取得新的明确单次授权后才可考虑 `source_prepare`。

## 第一次定点复核结论（历史，已由上方第二次定点复核结论取代）

复核日期：2026-08-27  
复核基线：冻结 manifest SHA-256 `3ac328ff9abb55f6629f4a39b086549c5eeb8e04226cfdfc248133eb0e69378c`，22/22 成员匹配；正式 runtime 19/19 receipt 匹配  
当前结论：**FAIL。`BLOCKING=1`，`NON_BLOCKING=0`。**

初审稳定 finding `M9-SP-PY39-RCV-B01`—`B04` 的原关闭条件均已落实：terminal replay 现在用 `O_NOFOLLOW` 稳定 FD 对 state、workflow、ledger 的完整 post receipt 执行链接、owner/group、mode、nlink、bytes、hash 与提交后 inode 闭合；`budget.lock` 已进入合同和 gate，并在 14 个 atomic-json 提交边界及 snapshot、rename、ledger、state、workflow、terminal 边界前后复核同一 FD/路径身份；`WORKFLOW_COMMITTED` 已作为独立 journal/transaction 阶段持久化；专用冻结测试已扩展到 13 项并覆盖原 B04 要求的崩溃、retirement、partial ledger、gate/scope、自绑定、预算历史和 build/input 真实写入矩阵。因此，B01、B02、B03、B04 均标记为 `CLOSED`。

但是，主动续提穿透发现新的稳定阻塞 `M9-SP-PY39-RCV-R01`。非终态 journal 中已经持久化的 post receipt 在恢复续提时没有被验证或继承；实现只校验 journal 的 base context，随后重新执行阶段逻辑并重新采集 receipt。固定 Python 3.9 临时夹具分别在 `LEDGER_COMMITTED`、`STATE_COMMITTED`、`WORKFLOW_COMMITTED` 已同时写入 journal 与 recovery transaction 后，把对应 ledger、state、workflow 替换为同字节、同 owner/group/mode/nlink 但不同 inode 的普通文件。三例均返回 rc=0，最终进入 `SUCCESS_COMMITTED`，并用新 inode receipt 覆盖先前阶段已经持久化的 receipt。由此，当前实现能够拒绝 terminal 之后的 same-byte inode drift，却不能拒绝 terminal 之前、已经有持久化 post receipt 的同类漂移。

本轮不生成 `08_audits/M9_source_prepare_py39_recovery_final_verdict.json`。当前 FAIL 不授权创建 recovery gate、执行 `recover` 或任何 `source_prepare`/`source_build`。

### 定点复核证据

| 对象 | SHA-256 |
|---|---|
| 修订工作包 | `bfa1c59d8d8d94c7f6a38da73b1c19a3ac161813a344dcf8657fb351a9f96df7` |
| 修订控制器 | `1ccb8095c0aec2ff00426cda62ffccbdc61322d03d2f8242d133e55268166b49` |
| 19-receipt 恢复合同 | `c1583a02cc7e1d6393f015e9a5bff2165e62b0941ffa47d00694f5d002ed1d7b` |
| 13 项专用测试 | `55fa6afe78a7a1c334a9c854adca392a04708fd306871c9ae3049d6537410b22` |
| 22 文件冻结 manifest | `3ac328ff9abb55f6629f4a39b086549c5eeb8e04226cfdfc248133eb0e69378c` |
| 定点穿透临时脚本 | `44188bcc4e37d14911d8c04fec95d14cdff47e51d9b88244da2cfc67484145cf` |

固定解释器 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 实测为 Python 3.9.23，`isolated=1`、`no_site=1`、`dont_write_bytecode=1`、`euid=0`。回归结果为：

```text
test_m9_overlap_controls.py: Ran 110 tests in 36.794s — OK
test_m9_source_prepare_py39_recovery.py: Ran 13 tests in 5.782s — OK
独立 lock-boundary 注入: 14/14 在下一正式边界拒绝，accepted=0
阶段 post-receipt inode 注入: ledger/state/workflow 3/3 被续提接受，accepted=3
```

专用测试的 14 个 atomic-json 窗口、snapshot/state/workflow/rename 断点、ledger partial append、retirement 四态、失败 snapshot 漂移、预算历史字段、terminal 链接/元数据/inode、初始 lock 身份以及 gate scope/report/verdict/work-package/frozen 预执行漂移均通过。`prepare_sources()` 与 `prepare_structure()` 在临时目录中实际进入各自写入分支，分别产生逐字节相等的 `alpha β\n` 与 `gamma δ\n` UTF-8/LF 文件；没有使用 `py_compile`，`06_reproduction` cache 为 0。

正式现场复核前后保持：19/19 receipt 匹配；budget state 与 workflow 双 `HARD_STOP`；ledger 61,248 bytes、63 行、SHA-256 `a2170772c37b601112f0d957a18a6e9375dc7cf2eb22697a26b61a5db3ed770d`；staging 原位且 inventory 仍为 140 目录、5,179 普通文件、5,319 records、632,029,184 allocated bytes、SHA-256 `0c0389f29f3a87e26af3c884b13bcc7c6dc6f183b50d803b9affa5fbd4e3920e`；retired 和四个 recovery 控制对象缺席；五项正式产品缺席；cache 为 0。所有破坏性注入均位于临时目录，未执行任何正式控制器动作。

### M9-SP-PY39-RCV-R01：非终态续提重新绑定已持久化 post receipt

可复现顺序如下：在临时夹具创建 gate；执行恢复并在 recovery transaction 的 `LEDGER_COMMITTED`、`STATE_COMMITTED` 或 `WORKFLOW_COMMITTED` 写入后注入崩溃；确认 journal 与 transaction 已记录该阶段及原 post receipt；用同字节、`1000:1000 / 0644 / nlink=1` 的新普通文件原子替换对应 runtime 路径；再次调用 `recover()`。当前三种情形均成功，旧 `st_ino` 被新 `st_ino` 取代并进入 terminal。

根因位于 resume 分支：读取既存 journal 后只比较 base 字段；除 `SUCCESS_COMMITTED` 外，不按 journal phase 验证 `post_ledger`、`post_state`、`post_workflow`，也不要求后续阶段沿用已经记录的 receipt。随后 `append_event_exact()` 或 state/workflow target 认领逻辑只检查 bytes/当前元数据，并重新采集 receipt，因而把 drifted inode 当作新的合法 post identity。

最小关闭条件是：建立允许的 journal/transaction phase-pair 状态机；对 `LEDGER_COMMITTED` 及以后阶段，在任何后续写入前要求当前 ledger receipt 逐字段等于首次持久化的 `post_ledger`；对 `STATE_COMMITTED` 及以后阶段同样验证并继承 `post_state`；对 `WORKFLOW_COMMITTED` 及以后阶段验证并继承 `post_workflow`。已经持久化的 post receipt 不得在续提中重新定义。冻结测试应在三个阶段分别注入 same-byte inode replacement，并扩展 symlink、hardlink、owner/group、mode、nlink 漂移，断言在任何进一步 journal/transaction/runtime 写入前拒绝且既有阶段证据保持不变。修复后须更新冻结闭集并由原审计员再次定点复核。

## 初审结论（历史，已由上方第一次定点复核结论取代）

**verdict：FAIL。`BLOCKING=4`，`NON_BLOCKING=0`。**

当前实现的正常崩溃续提主链在临时夹具中通过：从 journal 创建、失败事务快照、staging rename、ledger 部分追加、state 单边提交、workflow 单边提交到 terminal commit 的 13 个注入窗口均可恢复为单一 `SUCCESS_COMMITTED`，恢复事件计数为 1，干净终态重放未产生可观察写入。失败 transaction、consumed capability、FAIL launcher receipt、预算和历史字段在正常恢复夹具中保持不变，失败 transaction snapshot 与原字节相同。

但是，现有证据不能支持正式 PASS。终态重放没有对 state、workflow、ledger 执行 regular-file、owner/group、mode、nlink 与 inode 闭合验证，实测会接受同字节 symlink、hardlink 和权限漂移；恢复所持有的 `budget.lock` 也没有身份与元数据验证，实测可在错误的硬链接锁对象上完成恢复。实现还缺少明确要求的持久化 `WORKFLOW_COMMITTED` 阶段。已提交专用测试仅 5 项，没有覆盖这些安全边界，也没有实际执行 build/input 两条完整文件写入路径。因此不得创建正式 recovery gate，不得执行正式 `recover`，也不得生成 `M9_source_prepare_py39_recovery_final_verdict.json`。

## 审计依据与冻结证据

| 对象 | SHA-256 |
|---|---|
| 恢复工作包 | `7c04b506908008c0f51362ccf35347516e3c27251996f5cc4b9165ae0a8d8e85` |
| 恢复合同 | `f7e13541408394e1d7b38a564c41dc71ab706aa59bc7cd891a48d550e650d33f` |
| 22 文件冻结清单 | `4a709ca14367ccf983866ceb9de135cb2ec863fa28d921cb6760741bd373273c` |
| 恢复控制器 | `8db07d5a5806b4f0cfde355adec6ae138d76b959de5d261cf97ccb4f782ae531` |
| 专用恢复测试 | `1daa9059c00818370f3d52f883e469ff455a410230ca98e122b73e86a57c60f7` |
| 既有 overlap 控制测试 | `2e4a1c235e45764200c7a77ada852bd5a628a775dd43bcefa017d2bdd4caa86e` |
| `m9_overlap_common.py` | `91d2a6a824be1a4c715ee7dc6ba83d9e75931f781d669d796aaad2666739eb14` |
| `m9_openmx_build.py` | `ab6632784a744fd3f66c95aac30a56767f67af3d8d81147df2fc0d72b67102ec` |
| `m9_openmx_input.py` | `9d37b10d5c1916151684a60675efb6d962d8de984b7e9f4bcb2e666abd6f5102` |
| 原失败事实独立审计 | `bb4182f555dbd93b04eae50c79ba8e9e855cec75393465ac56ef23e505406bed` |
| `decisions.md` | `f79362d06034a322a09fb9bbd739bc17f36901d3239f9dc54294f825f508e1ea` |
| 临时主动穿透脚本 | `a9df0b2cd5eb55a56b4bbca6afd0f37e1a9d85fb18ff3fd3507b01dd1d09da99` |

冻结清单包含 22 个成员；逐文件重算结果为 `22/22` 匹配，mismatch 为 0。恢复合同绑定的 18 个正式 receipt 在审计前后均与合同的 SHA-256、bytes、uid、gid、mode、nlink、`st_dev` 和 `st_ino` 一致：

| 正式对象 | SHA-256 |
|---|---|
| budget state | `8a128719f80e584c2a1fbfafcc309e534b1b7d375e428a195c8f6349ea2b5656` |
| workflow | `92783147133967dc6dc6494220d7628de2e05de9c260b4ea4fa2bd2f1f44e4e2` |
| ledger | `a2170772c37b601112f0d957a18a6e9375dc7cf2eb22697a26b61a5db3ed770d` |
| failure transaction | `0a982e876e43768c6069fdeafd07e6e43ae03be3b1a0abc8584aa8d137bbcae7` |
| consumed capability | `7a3e21145fa31b2613d5d1a740e56ead4e28c3b06b3b371d529a7fbb77ebd905` |
| FAIL launcher receipt | `8217945664427eea38d7f546fa5a91689701a989601fbe539951214f7e872924` |
| consumer gate | `2ba96b8566f2ba38a528e4002dbaa0bebf4f9a7b8c5f10a92b89d643d11a85f2` |
| bootstrap receipt | `3172bf9516fed5dd2abb3669c705211428cbe6ebeea34fe96fcb6a3016d5f1ba` |
| snapshot manifest | `2d13e0c1fb1c1e635ad1730f44f21901340e7483d06356aa8eeb0e07f83dcec9` |
| D-017 transaction | `e9b8babcff8a2f42adea21d5cbce614b38f0854271d3389eae0bbcdd7d5e53bc` |
| D-017 gate | `8e66d65d17d3195f3df09db954afca4066c3ec91e2d8dad6d2aea06078d0d5ce` |
| active overlap gate | `78311a978c2472c85b35a745d80e1f33724c1500cf8d7bd244cdbe83c3fa3698` |
| retired overlap gate | `dbe4756142d0e921c3834330550310e85652503c04254b30bea1a069ff35377c` |
| D-018 gate | `286a0e409a80f85ca6bb39b76bdb977fc67ffa56f4646b00d3aad5943c98e880` |
| D-018 transaction | `41cbfbd4da1c3a0eea92731a00758355f46321d5b0a66260f53f628290d847ad` |
| D-018 execution gate | `bc51209c13570839c08dd4fc304fe39865a98ade69caeb23886602de2d8be6e9` |
| D-018 journal | `27a92edded459948150c750a4339692434e08a84cbc8879c63c71b6c14cb0e8a` |
| D-018 pre-state | `00a32bd7f28ad26fa600c8abe9d0fa64efe57e410eacb82ad2d201fa9adc5439` |

正式 ledger 保持 61,248 bytes、63 行，原 60,288-byte 前缀及 960-byte `OVERLAP_HARD_STOP` 后缀均不变；后缀 SHA-256 为 `2b5b69e8d3be617e357b177633c36a5d447dd244bd74e25c808f567c83c5aa20`。state 仍为 `hard_stopped=true`、`active_overlap_transaction=null`；workflow 仍为 `stage=HARD_STOP`、`hard_stopped=true`、`active_transaction=null`；失败 transaction 仍为 `FAILED_COMMITTED`。进程扫描未发现 source launcher、`m9_openmx_build`、OpenMX、make 或 configure 活动进程。

staging 的独立递归复算得到 140 个目录、5,179 个普通文件、5,319 条记录、619,112,384 apparent bytes、632,029,184 allocated bytes，控制器 canonical inventory SHA-256 为 `0c0389f29f3a87e26af3c884b13bcc7c6dc6f183b50d803b9affa5fbd4e3920e`，与合同一致；失败 makefile SHA-256 为 `bf01251254b3f0e3ee010346835bcbe4707aaa57c1f741eb1c84244e849e9d9b`。retired 目标、四个正式 recovery 控制对象和五项要求缺席的终态产品在审计前后均按 `lexists` 缺席。`06_reproduction` 下 `__pycache__`、`.pyc`、`.pyo` 计数为 0。

## 固定 Python 与测试结果

固定解释器为 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9`，实测 `Python 3.9.23`，并满足 `isolated=1`、`no_site=1`、`dont_write_bytecode=1`、`euid=0`。

执行命令与结果：

```text
wsl.exe -u root -- /home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B /mnt/e/Projects/Codex/DeepH/06_reproduction/tests/test_m9_overlap_controls.py
Ran 110 tests in 34.916s — OK

wsl.exe -u root -- /home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B /mnt/e/Projects/Codex/DeepH/06_reproduction/tests/test_m9_source_prepare_py39_recovery.py
Ran 5 tests in 0.211s — OK

wsl.exe -u root -- /home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B /mnt/c/Users/20659/AppData/Local/Temp/m9_py39_recovery_penetration.py
exit 0；13/13 注入窗口可续提；13/13 干净 terminal replay 零可观察写入；每例 recovery event count=1

wsl.exe -u root -- /home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B /mnt/e/Projects/Codex/DeepH/06_reproduction/controllers/m9_source_prepare_py39_recovery.py invalid-action
exit 1；仅输出 usage；正式 receipt、staging 与 control namespace 无变化
```

Python 3.9 LF 修复本身有正向证据：`write_utf8_lf()` 通过 `Path.open("w", encoding="utf-8", newline="\n")` 写入，CR 输入被拒绝；固定 Python 下真实临时文件得到逐字节相等的 UTF-8/LF bytes。AST 复核确认 `prepare_sources()` 和 `prepare_structure()` 各有且仅有一次直接 `write_utf8_lf` 调用，两个脚本均不再含 `Path.write_text(..., newline=...)`。其证据边界是：已提交测试只执行公共 writer 和渲染器，没有实际通过 `prepare_sources()` 与 `prepare_structure()` 的完整函数路径完成文件写入；这不足以满足工作包所列 build/input 两条正式调用路径测试要求，见 `M9-SP-PY39-RCV-B04`。

临时故障注入覆盖：`PREPARED` journal 后、snapshot bytes 后、`FAILURE_TX_SNAPSHOTTED` 后、rename 后、`STAGING_RETIRED` 后、ledger partial append、ledger 完整 append 后、`LEDGER_COMMITTED` 后、state bytes 后、`STATE_COMMITTED` 后、workflow bytes 后、terminal transaction 后和 terminal journal 后。所有正向夹具均恢复为一个 recovery event，failure snapshot 等于原 transaction，失败 transaction/capability/receipt 保持原 SHA，state 仅改变 `hard_stopped`、`last_event_utc` 和 recovery ID 字段，workflow 仅改变 `stage`、`hard_stopped` 和 recovery ID 字段；CPU、credit、GPU、storage history 与 wall-clock history 均保持。

## BLOCKING findings

### M9-SP-PY39-RCV-B01：terminal replay 未闭合 state/workflow/ledger 的链接与元数据身份

控制器在 `SUCCESS_COMMITTED` 分支只用 `Path.read_bytes()` 对 state/workflow 做 SHA-256，对 ledger 做 SHA-256 和 bytes 检查。该读取会跟随 symlink，也不检查 owner、group、mode、nlink、`st_dev` 或 `st_ino`。主动穿透在完整恢复后的临时终态分别注入以下漂移，三例均返回 `source_prepare_py39_already_recovered`、rc=0：

- state 路径替换为指向同字节文件的 symlink：接受；
- workflow 增加硬链接，使 `nlink=2`：接受；
- ledger 保持同字节但改为 mode `0666`：接受。

因此，“terminal replay 成功”目前不能证明终态仍是授权的普通单链接对象。最小修复条件是：terminal journal/transaction 应绑定 state、workflow、ledger 的完整 post receipt；终态通过 `O_NOFOLLOW` 的稳定 FD 读取并验证 regular、owner/group、mode、nlink、bytes、hash 以及已提交后的 `st_dev/st_ino`，且路径 `lstat` 必须与 FD 身份一致。应增加 state/workflow/ledger 的 symlink、dangling symlink、hardlink、owner/group、mode、same-byte inode replacement 负例及零写断言。

### M9-SP-PY39-RCV-B02：`budget.lock` 未绑定或验证锁对象身份

`recover()` 对固定路径执行 `os.open(LOCK, O_RDWR|O_NOFOLLOW)` 后立即 `flock`，没有验证该 FD 是合同绑定的 regular、owner/group、mode、nlink、`st_dev/st_ino`，也没有把 `fstat` 与路径 `lstat` 对照。正式 lock 当前为 `1000:1000 / 0644 / nlink=1 / dev=2096 / ino=50700`，但该对象不在恢复合同的 18 项 receipt 中。

临时穿透在 gate 创建后把 lock 路径替换为指向 decoy 的 mode `0666`、`nlink=2` 硬链接；`recover()` 仍返回 rc=0 并完成全部恢复。这意味着排他锁可能落在错误 inode 上，不能证明它与其他 M9 budget 入口使用的是同一互斥域。最小修复条件是：将 lock 的固定身份和允许元数据纳入合同与 gate，在获得 flock 后对 FD 和路径执行稳定 regular/nlink/owner/mode/dev/ino 校验，并在首次正式写入前复读；增加 symlink、hardlink、同字节/同路径 inode swap、owner/mode 漂移与错误锁并发负例。

### M9-SP-PY39-RCV-B03：缺少持久化 `WORKFLOW_COMMITTED` 阶段

要求的状态序列为 `PREPARED → FAILURE_TX_SNAPSHOTTED → STAGING_RETIRED → LEDGER_COMMITTED → STATE_COMMITTED → WORKFLOW_COMMITTED → SUCCESS_COMMITTED`。实现写入 workflow target 后直接构造并写入 `SUCCESS_COMMITTED`，源码与专用测试中均不存在 `WORKFLOW_COMMITTED`。在 workflow bytes 已提交而 terminal transaction 尚未写入的崩溃窗口，journal 仍停留在 `STATE_COMMITTED`；虽然当前实现能够续提，但没有持久化证据区分“workflow 尚未提交”与“workflow 已提交而 terminal 未提交”，也没有对该中间状态建立独立 post receipt。

最小修复条件是：workflow 写入或认领 target 后，先验证完整 post receipt，再将 journal 与 recovery transaction 持久化为 `WORKFLOW_COMMITTED`，之后才允许 `SUCCESS_COMMITTED`；测试应分别注入 workflow bytes 后、`WORKFLOW_COMMITTED` journal/transaction 两个单边窗口和 terminal 两个单边窗口，并断言任何非终态都不能被解释为新的执行授权。

### M9-SP-PY39-RCV-B04：已提交测试不足以支持安全实施结论

专用测试文件仅有 5 项：公共 LF writer、tree symlink、atomic temporary、ledger partial append、happy-path full recovery/replay。它没有覆盖逐阶段崩溃、rename 源/目标四态、失败 snapshot 漂移、terminal 链接/元数据、lock 身份、预算历史字段闭集、异常半清状态、gate 自绑定漂移和 recovery scope 负例。既有 110 项 overlap 测试主要覆盖旧控制面；其中 LF 测试只调用公共 writer，并通过源文本搜索排除 `newline=`，没有实际执行 build/input 两条完整写入路径。

独立临时穿透补足了一部分崩溃和不变量证据，并直接发现 B01/B02；它不能替代冻结回归闭集，因为临时脚本不在 22 文件 manifest 中。最小修复条件是：把上述矩阵加入 `test_m9_source_prepare_py39_recovery.py`，固定 Python 3.9 下执行 build/input 两条实际文件路径，并冻结更新后的控制器、测试、合同、工作包和清单；全套测试与独立重审均须为零问题。

## 正式零写入证据与适用范围

审计前后两次独立读取均得到：22/22 冻结文件匹配；18/18 正式 receipt 匹配；state/workflow 双 `HARD_STOP` 不变；ledger 为同一 61,248 bytes/63 行/SHA-256；staging 计数、bytes、inventory 与 makefile hash 不变；retired、四个正式 recovery 控制对象和五项终态产品保持缺席；相关活动进程为 0；`06_reproduction` cache 为 0。除本报告外，工作区没有由本审计新增或更新的文件；临时破坏性夹具不位于工作区或正式 WSL 运行态。

本报告的适用范围仅为当前 22 文件恢复闭集和合同绑定的正式失败现场。当前 FAIL 不授权任何 gate 或恢复动作。未来只有在上述四个 finding 关闭并由独立审计给出 `PASS/BLOCKING=0/NON_BLOCKING=0` 后，PASS 才只授权主 agent 机械创建一次 recovery gate 并执行一次 `recover`；该 PASS 不授权 `source_prepare`、`source_build`、smoke、batch、GPU、Hamiltonian、SCF 或其他 DFT 标签。恢复执行后仍须独立执行事实审计、重建并审计替代 consumer snapshot/gate，并取得新的明确单次 `source_prepare` 用户授权。
