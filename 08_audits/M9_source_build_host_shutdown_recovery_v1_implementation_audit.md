# M9 source_build 宿主关机恢复 v1 独立实施审计

审计日期：2026-09-01  
审计角色：独立子代理  
审计对象：`m9_source_build_host_shutdown_recovery_v1` 冻结实施  
结论：**PASS**  
阻塞问题：**0**  
非阻塞问题：**0**

## 1. 结论与边界

最终冻结实施通过独立源码审查、B01–B03 定点穿透、88 项隔离与回归测试、正式现场双重只读封印以及既有 single-FD loader 启动拒绝路径检查。证据支持主端在保持最终哈希不变的条件下，先通过既有 single-FD loader 执行一次正式零写 `preflight`；该 preflight 通过后，才可按同一冻结参数执行一次 `recover`。恢复执行结果仍须另行进行独立事实审计。

本 PASS 只证明恢复控制器的实施门控成立，不证明正式恢复已经执行，不构成 `source_build` 成功，也不签发或复用任何构建 permit、operation 或 capability。恢复成功后仍须建立 v4 构建消费链、独立实施与安装审计、新机器许可及执行前审计；structure 500、smoke、batch、材料计算、训练、GPU/DFT 和 M9-DATA-B01 均未放行。

## 2. 冻结来源和权威链

最终 `m9-host-shutdown-recovery-frozen-v1` 清单恰含 9 个直接成员，SHA-256 为 `3334010925f97486f58b2b3116b52b6b4cc48f34d4c8e0e1ec801de577bbc668`。关键对象为：

| 对象 | SHA-256 |
|---|---|
| 恢复控制器 | `4df3b47671b0d824631ed0acae27d8b1e1bea77c537794319d34c43e3944af8a` |
| 17 项恢复测试 | `6da8860d27eb24b578abdc1bc55b4adcde853d791ec33b312d3fc2eaf212807a` |
| 工作包 | `a59ac5b95226c5e2eb1eaf99b17192db36656d80d750741779d3f056eb6c4b1e` |
| v3 冻结清单 | `01a2a8f438d27d582abcf4536775b54605051a3458b06f2bc29c2c56222d4e58` |
| 中断独立报告 | `410468cea26e8d7359f400d3a3e1dbeb7723e2120560c89a2f093c0009d07104` |
| 中断完整证据 | `12907e82278f114e228c0b9e930564dafd18ab761159f70edd01ac2200f2f3d2` |
| v3 执行前证据 | `822e0fc61599db3b1b1135b2e384050ca373f0c4c08aea84bee70d7a3cee3b43` |

控制器要求 root、冻结 Python 3.9.23 以及 `-I -S -B`，入口参数闭集为 `self_sha preflight|recover frozen_sha verdict_sha report_sha`，不存在 resume、install、permit 或 build 动作。authority 对 verdict 采用严格七字段全等比较，要求 schema=`m9-host-shutdown-recovery-implementation-verdict-v1`、`PASS/0/0`、最终 frozen SHA、固定 WSL 报告路径和报告 SHA；整数类型检查排除布尔值替代。

独立复算确认 9 个直接来源全部匹配，并由 v3 清单绑定 61 个无冲突嵌套来源；原 `m9_budget.py` 必须位于该嵌套闭集并以冻结字节只读加载。既有 loader 从原替代工作包提取，工作包 SHA `dc1d0d992f7e1328f79a4436eb4535b79ba2ab48fcee1b44fa498c31c30e91a2`，规范化 loader SHA `c68e43b5de4fdadb44254fbfdd543f5ba2a29b6e41994021c55a3287b5f7491f`。使用该确切 loader 与控制器 SHA 启动非法 action 时，固定解释器成功进入控制器并在 authority 首行以 `no resume` 语义退出 1；未打开恢复写路径，证明 single-FD 启动兼容且动作闭集生效。

## 3. B01：首次写前全对象二次封印

B01 已关闭。初审版本仅在 `validate` 中核验非正式对象，`commit` 可把验证后漂移的构建树重新捕获为局部基准。最终版本由 `verify_current` 返回完整 seal，并在 `commit` 首个 `os.mkdir(PRIVATE)` 之前、同一 budget lock 内再次执行同一函数；第二次结果必须与 seal 全等，否则以 `recovery object drift before first write` 拒绝。

二次封印覆盖：

- 全部 authority 载荷和 221 项正式 namespace；
- state、workflow、transaction、ledger 四份原始字节；
- consumed capability、launcher receipt 缺席、精确进程 argv 与 v3 permit；
- 7,640 项中断树、5,319 项干净历史树的完整 receipt 与 portable 视图；
- 三份日志的严格路径闭集和逐对象 receipt；
- 六个禁用产物的 `lexists` 缺席；
- 原预算对 1 GiB 恢复 forecast 的即时 violations 与 storage snapshot；
- budget lock 的 descriptor/path 身份。

隔离负例在首次验证和首写之间分别注入未知正式 namespace、中断树、干净树、日志、禁用产物、匹配进程及存储预测漂移。七类变体均在创建 PRIVATE、archive 或 ledger 写入前拒绝，夹具全树前后相等。正式现场两次封印也全等，见第 6 节。

## 4. B02：克隆持久化、非硬链接和安装前验证

B02 已关闭。每个普通文件经 `copyfile`、owner/mode/time 元数据恢复后，以 `O_NOFOLLOW` 描述符验证普通文件且 `nlink=1`，随后执行文件自身 `fsync`。全部新目录，包括只含符号链接的嵌套目录，按深度从深到浅 `fsync`，最后持久化 staging 父目录。

`verify_no_hardlinks` 比较源、目标普通文件相对路径闭集，逐项要求目标 `nlink=1` 且 dev/inode 不与源文件相同。全量 portable receipt 相等和非硬链接验证均位于 staging rename 及 `CLEAN_TREE_CLONED` checkpoint 之前。文件或嵌套目录 `fsync` 故障会保留 staging 并在安装 rename 前停止；复制完成后篡改 staging 字节也会在 rename 前以 `clean clone differs` 拒绝，保留 archive、log archive 与 staging，且 pristine-only 规则禁止重放。

中断树和日志采用同文件系统 rename，rename 后逐 dev/inode、uid/gid、mode、nlink、bytes、kind 和文件 SHA 核验，再持久化父目录。干净历史源在克隆前后保持其完整 canonical receipt 不变。

## 5. B03：故障窗口、零写预检和不可重放

B03 已关闭。最终测试文件恰含 17 个测试方法，工作包声明与实际覆盖一致：

- `validate('preflight')` 在完整夹具上执行两次 seal，前后全树 receipt 相等并返回 `writes=0`；
- B01 七类首写漂移均零写拒绝；
- `PREPARED` 至 `SUCCESS_COMMITTED` 的 9 个 journal checkpoint 逐一在持久化后注入故障，验证相应 PRIVATE、archive、log archive、clean tree、ledger、runtime 或 snapshot 现场保留，并验证第二次调用被 pristine-only 规则拒绝；
- 普通文件与所有嵌套目录的 `fsync` 调用、文件/目录持久化故障、全量非硬链接、clone-after-copy 漂移均有直接负例；
- 短写循环、零写临时文件、ledger 部分行、非法相位、非法动作、精确孤立事务和 capability 进程匹配均被覆盖。

ledger 使用原 inode 以 `O_APPEND` 恰追加一行；前缀读取多一个字节以排除未知尾部，追加后核验完整 SHA 及 dev/inode、owner、mode、nlink 不变。部分行写入会被保留且不能重放。TX、state、workflow 按 `TX -> state -> workflow` 次序逐文件核对原字节、O_EXCL 临时文件、fsync、atomic replace 和 checkpoint；任一窗口失败均留下足以审计的 pristine-only 阻断对象。

## 6. 独立测试与正式只读现场

全部测试均由实际 root、固定解释器 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 运行，不使用 `py_compile`：

| 测试集合 | 结果 |
|---|---:|
| 宿主关机恢复 v1 | 17/17 PASS |
| 既有 MPI 恢复 | 16/16 PASS |
| v3 consumer | 40/40 PASS |
| v3 chain | 15/15 PASS |
| 合计 | 88/88 PASS |

正式现场只读等价检查未调用控制器 `main`、`preflight` 或 `recover`，而是从冻结字节加载 receipt 与原 budget 只读函数，连续执行两次 `verify_current` 并比较完整 seal，同时对正式 namespace、中断树、干净树和日志树做前后双快照。结果为 `READONLY_EQUIVALENT_PASS`、`writes=0`：

| 对象 | 数量 | canonical SHA-256 |
|---|---:|---|
| 正式 namespace | 221 | `f5e8e69b72f2992313db40f3668d7c9c3d0b9cefef66ee19a857f376b8b8eeb7` |
| 中断 BUILD 树 | 7,640 | `afbeae908757c7e4f26010f39543a54503210fff9d24c71845bba9cf688dfed3` |
| 干净历史树 | 5,319 | `060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359` |
| 日志树 | 4 | `3ef23ab6cc2348fe66b96ec3ecd56aa5172392afe48cf657213d0e30507a6e32` |

四份运行态仍为中断审计父态：state `715d1e034ea17391eb18ffb75eb7cb53ca1acf8121b47ed6b52da037645e1c96`、workflow `0f134f3afd26600a323de2c5c1e9c84f73925b699922820fabc9800a1e4cd2aa`、RUNNING transaction `22ce3538de8266a6f2965ea840cc7d92c9a2e8bb2de94443c24259d0759d2a92`、ledger `8dfbb2bb9f23ac9066b457553c2bccfa94a2ab7dde5d66f6315595caaa793421`。consumed capability SHA 为 `f8bcb3463c32286899a3a8b2461f820f8ed7e15e668da5b381bffc8df1c52721`，v3 permit SHA 为 `10d11a4bebc4f8d1595cfdb4bdd21d795848b643db556724ec57598a9d06c856`；匹配进程与 launcher receipt 均缺席，六个禁用产物均缺席。

1 GiB 即时恢复 forecast 的原 budget `violations=[]`。当前 combined allocated 为 31,576,125,440 bytes，相对 overlap baseline 增量 1,406,304,256 bytes；host VHDX 相对 overlap baseline 增量 1,946,157,056 bytes。cache 清理后复核为 0，冻结四对象 SHA 未改变。

## 7. 目标状态与预算保持

目标生成函数只对白名单字段实施变化：`overlap_build` 从 `7214.469142588001` 增加精确保守墙钟上界 `292.7759032` 至 `7507.245045788001`；其他 CPU 桶、全部 GPU、D-017 adjustment、存储基线、wall-clock policy 和历史字段原样保留。该数值明确标记为 `conservative_wall_upper_bound_not_measured_cpu`，不是实测 CPU 或原 monotonic 终值。

原 RUNNING transaction 被版本化为 `FAILED_COMMITTED`，`exit_code=null`、`timed_out=false`，唯一原因是 `host_shutdown_external_interruption`，并绑定中断报告、完整证据与恢复 ID。state/workflow 清空 active 指针，保持非 hard-stop 和 `SOURCES_PREPARED`，增加唯一恢复标记。ledger 事件和最终返回均固定 `source_build_authorized=false`。

公开 snapshot 只包含恢复控制器、中断 evidence、独立中断报告及四成员 manifest，owner/mode 为 root:group1000 的目录 0550、成员 0440，不包含 D-019 授权、permit 或可执行构建 capability。PRIVATE、snapshot、archive、log archive、staging 或临时文件任一预存均会在写前拒绝，因此本控制器不能覆盖或续提不完整恢复。

## 8. 最终判定

初审 B01、B02、B03 均已由最终冻结实现和直接负例关闭；未发现新的阻塞或非阻塞问题。正式实施判定为 **PASS / BLOCKING=0 / NON_BLOCKING=0**。允许的下一步仅为主端使用已审核 single-FD loader、最终控制器/manifest/verdict/report SHA 执行一次零写 `preflight`；只有该回执通过，方可执行一次 `recover`。本报告与 verdict 一经哈希绑定不得就地修改。
