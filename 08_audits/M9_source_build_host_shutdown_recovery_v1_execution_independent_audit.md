# M9 source_build 宿主关机恢复 v1 独立执行事实审计

日期：2026-09-01。审计角色：独立子 agent。审计对象是正式 WSL 中已经结束的宿主关机恢复 v1；主端执行记录仅作为定位线索，不作为自证。审计期间未调用 `preflight`、`recover`、`source_build`、permit、预算写入口或任何构建命令，正式运行态保持只读。

## 判定

**PASS / BLOCKING = 0 / NON_BLOCKING = 0。**

现有证据支持：恢复以经独立实施审计的精确冻结实现完成了一次成功的状态变更提交；中断事务被版本化为 `FAILED_COMMITTED`，原账本 66,755-byte 前缀不变且只追加一条 1,844-byte 恢复事件；中断树和日志被保留为版本化归档，新 BUILD 是 CLEAN 的非硬链接干净复制；state/workflow 回到非 hard-stop 的 `SOURCES_PREPARED`，但没有签发新的构建许可，也没有执行新的编译、材料计算或训练。

本判定只说明恢复事实满足合同，不等于 `source_build` 已通过，也不允许重放旧 v3 permit、operation 或 capability。后续构建仍须建立并独立验收绑定当前 244 对象父态、新 BUILD 和本报告的新版本 consumer/launcher，再签发新的单次机器许可。

完整机器证据见 [postexecution evidence](M9_source_build_host_shutdown_recovery_v1_postexecution_evidence.json)，SHA-256 为 `42e05a042ab66c41b31e03ee9a126eec58a1480c382834bd07cd9244f88d602a`。

## Authority 与调用边界

固定 Python 3.9.23 `-I -S -B` 下，以只读方式加载冻结恢复控制器的 `authority`。控制器、frozen manifest、实施 verdict、实施报告分别为：

- `4df3b47671b0d824631ed0acae27d8b1e1bea77c537794319d34c43e3944af8a`
- `3334010925f97486f58b2b3116b52b6b4cc48f34d4c8e0e1ec801de577bbc668`
- `77f86ea6aec7138aaced6b2bc66a4836482cd9f0509e4bdb5c41a6fe3806d95d`
- `fd1778bdbf3807f8ae25edeae7047c53dd4152bed7a1c12edca9d2c3bef5b518`

严格七字段 verdict 为 PASS/0/0，9 项冻结来源、嵌套 v3 来源及原预算实现均由 authority 逐项固定读取；只读加载得到 12 个不重复 payload，未调用 `validate` 或 `main`。

正式持久证据可独立证明**成功改变状态的 recovery commit 恰为一次**：账本中 recovery ID `m9-source-build-host-shutdown-recovery-20260901-01` 恰出现一次；同一 ID 只有一个 root-private `SUCCESS_COMMITTED` journal、一个版本化中断树、一个日志归档和一个重建 BUILD。恢复器是 pristine-only，成功后这些固定目标已存在，不能再次成功提交。零写 `preflight` 不留下正式持久痕迹，因此其历史调用次数不能由正式命名空间反推；主执行记录称一次，但该陈述未用于本 PASS 的关键推导。现有证据也不能穷尽证明是否发生过额外的零写或失败尝试，只能排除第二次成功状态变更提交。

## 正式命名空间与运行态

中断证据中 221 对象的完整压缩 receipt 基线解码、哈希和闭集均通过。恢复后两次独立采集得到稳定的 244 对象，canonical SHA-256 为 `b80ef48974aca25da529c8a1c81c5d1974dff91c03bb844ebd4e0090e42a0e`。相对父态恰新增 23 对象：PRIVATE 目录及 17 文件、公开 snapshot 目录及 4 文件；无删除。旧对象只有以下 7 项变化，符合工作包写集合：`manifests`、`controls`、`/root/deeph-m9-control` 三个父目录，以及四份 runtime。其余旧对象 receipt 全等；未知正式对象为 0。

四份 runtime 的实际字节均与冻结控制器从中断原始字节机械派生的目标逐字相等：

| 对象 | 恢复前 SHA-256 | 恢复后 SHA-256 | bytes |
| --- | --- | --- | ---: |
| `budget_state.json` | `715d1e034ea17391eb18ffb75eb7cb53ca1acf8121b47ed6b52da037645e1c96` | `cdfcf813f1e6c4759b0a8ef93a76d95a50d6e586ba5f4652908f6b1dd375dd7b` | 2,393 |
| `overlap_workflow_state.json` | `0f134f3afd26600a323de2c5c1e9c84f73925b699922820fabc9800a1e4cd2aa` | `271bd1c756b55db52b7cb479a7d679edb95e2d3bd33b21cfff88122f40459b34` | 1,006 |
| `overlap_transaction.json` | `22ce3538de8266a6f2965ea840cc7d92c9a2e8bb2de94443c24259d0759d2a92` | `433462132e40fd9f160bce150e20a7c3149227ad8bf4957e8d19d71e389ddb58` | 2,483 |
| `budget_ledger.jsonl` | `8dfbb2bb9f23ac9066b457553c2bccfa94a2ab7dde5d66f6315595caaa793421` | `f3f44ee5169bbeb44d175ff0aa381cda70684ad66f11ce57725c2e774471d4c7` | 68,599 |

账本前 66,755 bytes 与中断基线严格相同，后缀恰为控制器重新计算的一条 1,844-byte `SOURCE_BUILD_HOST_SHUTDOWN_RECOVERY` 事件；账本的 dev/ino、uid/gid、mode 和 nlink 前后全等。事件绑定父事务、D-019、冻结清单、实施报告/verdict及中断报告/证据，且 `source_build_authorized=false`。

state 只改变 `active_overlap_transaction`、`cpu_seconds`、`last_event_utc` 和新增恢复标记；workflow 只改变活动事务和新增恢复标记，stage 保持 `SOURCES_PREPARED`。父事务 `4d7808af7df9418518a59afeba766eb9` 为 `source_build/FAILED_COMMITTED`，`end_utc=2026-08-31T15:24:41.9861032Z`，保守上界计量 `292.7759032` 秒，语义为 `conservative_wall_upper_bound_not_measured_cpu`，`exit_code=null`、`timed_out=false`、reason 为 `host_shutdown_external_interruption`，launcher receipt 为空。该版本化失败事务没有被伪装为构建成功。

## 树、日志与持久恢复证据

对 BUILD、ARCHIVE、CLEAN 和日志归档均执行全树 receipt 扫描：

| 树 | 对象数 | 当前 canonical SHA-256 | portable SHA-256 |
| --- | ---: | --- | --- |
| 新 BUILD | 5,319 | `411a8a674559723f0616deafbe67c93d3e31453461fa6b2af26d4135bb3e1705` | `cf91d95aa8802925da676dab35fe5bb991a6061f809b871bca488f4c50347cc0` |
| 中断 ARCHIVE | 7,640 | `82bc6705ef8a507d2580630592f4903726622768aebb5bd7b1d22d93afa12515` | `065c2e640bebd671ff59d81af377f8a988b4f59126de4846e539f30f02eac4a3` |
| 历史 CLEAN | 5,319 | `060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359` | `cf91d95aa8802925da676dab35fe5bb991a6061f809b871bca488f4c50347cc0` |
| 日志 ARCHIVE | 4 | `5ea65a500eaadc665b4d282ce8b8c55019629b722020b7baa73259c9f862d4de` | `aa0483234d5c78bdede18a8f10df33f5c4a11ab79a889f25907442f7d5739946` |

新 BUILD 与 CLEAN 的 portable receipt 全等；5,179 个普通文件逐项 dev/ino 均不相同，目的文件 nlink 全为 1，排除硬链接复制。CLEAN 的完整 canonical 与中断证据完全相同。三份归档日志的字节、inode、权限和时间戳与中断证据相同；仅日志根目录因 rename 发生 ctime 变化，符合 Linux rename 语义。

中断证据保存了 7,640 项树的完整 canonical `afbeae908757c7e4f26010f39543a54503210fff9d24c71845bba9cf688dfed3`，但没有保存逐项 receipt 字典。因 rename 会改变归档根目录 ctime，恢复后不能仅用当前树反推出旧 canonical。冻结控制器在首次写前核验该 canonical，并在 rename 后、`INTERRUPTED_ARCHIVED` checkpoint 前逐项核验 dev/ino、uid/gid、mode、nlink、bytes、kind 和文件 SHA；当前完整归档、9 相位 journal 与冻结实现共同支持归档身份结论。报告不把缺失的旧逐项字典追认为已保存，这是本项证据边界。

PRIVATE 当前恰为目录加 17 文件：目录 root:root/0700，文件均 root:root/0600、nlink 1。17 文件与冻结 authority 的 12 个不重复 payload、四份 before-runtime 和 journal 逐字相符。journal 为 11,425 bytes，SHA-256 `4a15312a17cb5b74f27409f19f757d11eb486f999433f328723cc6b4051af566`；9 相位从 `PREPARED` 到 `SUCCESS_COMMITTED` 顺序精确，每一相位 runtime 哈希与预期提交窗口相符，事件、事件行和四个目标 SHA 均可重算全等，`source_build_authorized=false`。

公开 snapshot 恰为目录加 4 文件：目录 root:1000/0550，成员均 root:1000/0440、nlink 1，成员闭集为恢复控制器、中断报告、中断证据和 snapshot manifest；每个字节与 PRIVATE/冻结来源绑定相符，不含 authorization、permit 或执行入口扩权。

## 旧执行链、禁用产物与预算

旧 capability SHA-256 仍为 `f8bcb3463c32286899a3a8b2461f820f8ed7e15e668da5b381bffc8df1c52721`，状态为 `CONSUMED`；旧 permit SHA-256 仍为 `10d11a4bebc4f8d1595cfdb4bdd21d795848b643db556724ec57598a9d06c856`，两者 receipt 与中断基线全等，launcher receipt 继续缺席。旧 v3 gate 所绑定的四份 runtime SHA 全部与当前 runtime 不同，且旧 consumer 固定要求的事务 ID 为 `38a891fff6fd07675581b891766e02c6`，当前事务为 `4d7808af7df9418518a59afeba766eb9/FAILED_COMMITTED`。因此旧 permit、operation、capability 和旧命令不能重放。

原 `logs/overlap-build`、恢复 staging、HDF5 安装 prefix、OpenMX 安装 prefix、build manifest 和材料 run root 均缺席；未发现相关 budget/launcher/recovery、HDF5、make、OpenMX 或材料计算进程。`06_reproduction` 与正式 manifests/controls/root-private 范围内 `__pycache__`、`.pyc`、`.pyo` 为 0。

即时预算只读核验在 forecast 0 和 1 GiB 下均 `violations=[]`。`overlap_build` 原始累计为 `7507.245045788001` 秒，D-017 抵扣 `7200.075310528` 秒保持不变，有效累计 `307.1697352600013` 秒，7,200 秒子额度余量 `6892.830264739999` 秒。GPU 历史保持 compatibility `54.84820560599999` 秒、training/physical_validation 为 0；D-018 `UNLIMITED` 墙钟策略、CPU adjustments、smoke/batch 计数均与中断父态相同。存储即时快照中，combined allocated 为 `32207781888` bytes、相对 overlap baseline 增长 `2037960704` bytes，1 GiB 恢复预测仍无违规；这只是当前预算可行性读数，不是下一次构建的机器许可。

## 最终边界

恢复 v1 的执行事实通过，问题计数为 0/0。允许据此将父态记为“宿主关机中断已恢复、源码仍处于 `SOURCES_PREPARED`”；不得记为 BUILD_PASSED，不得关闭 `M9-DATA-B01`，不得进入结构 smoke/batch、材料计算或训练。D-019 提供持续人工授权，但不替代后续 v4 实施审计、安装事实审计、单次机器 permit 和执行前复核。
