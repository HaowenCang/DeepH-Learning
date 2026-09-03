# M9 source-build v3 外部中断独立事实审计

审计日期：2026-09-01  
审计角色：独立子代理  
审计对象：唯一一次获准的 M9 `source_build` v3 正式执行在宿主关机后的事实状态  
结论：**INTERRUPTED_NONTERMINAL / FAIL**  
阻塞问题：**1**  
非阻塞问题：**0**

## 1. 结论

唯一一次 v3 `source_build` 已真实消费执行许可并进入构建链，但没有形成 `SUCCESS_COMMITTED` 或 `FAILED_COMMITTED` 终态。权威事务 `4d7808af7df9418518a59afeba766eb9` 仍为 `RUNNING`，budget 与 workflow 的 active 指针仍指向该事务；原父进程 PID 294、子 launcher PID 396 在 WSL 重启后均不存在，且没有 launcher receipt。该状态属于**由宿主关机造成的非终态外部中断**，不是受控预算超时，也不能视为构建失败提交或构建通过。

构建实际到达 HDF5 `make check -j1`：configure 日志和 make 日志均显示前序阶段完成，check 日志最终停在 `Testing: btree2`，尾行为 `make: *** [Makefile:715: check-recursive] Terminated`。HDF5 安装前缀、HDF5 install 日志、OpenMX 二进制、官方二进制副本及两个 OpenMX 构建清单均不存在。因此，现有证据只支持“configure 与 make 完成、check 部分执行并被终止”；不支持 HDF5 自测通过，也不支持已进入 HDF5 install 或 OpenMX 编译。

当前必须停止在恢复门控之前。旧 v3 permit、gate、已消费 capability 或原命令均不得重放；完成版本化恢复、独立实施审计和独立恢复事实审计后，下一次构建仍须签发新的单次机器许可并绑定恢复后的新基线。

## 2. 证据范围与稳定性

执行前权威基线为 `M9_source_build_v3_preexecution_evidence.json`，SHA-256 `822e0fc61599db3b1b1135b2e384050ca373f0c4c08aea84bee70d7a3cee3b43`，含 220 项正式命名空间 receipt 与四份运行态原始字节。本次只读采集进行了前后双快照，未调用 consumer `run`、budget 入口、installer、permit 或 recovery，也未取得预算锁；采集前后正式命名空间、prepared 树、retired 树及日志树均无变化，M9 cache 计数为 0。完整结果封存在 `08_audits/M9_source_build_v3_interruption_postexecution_evidence.json`。

当前正式命名空间为 221 项，canonical SHA-256 为 `f5e8e69b72f2992313db40f3668d7c9c3d0b9cefef66ee19a857f376b8b8eeb7`。相对 220 项基线：

- 唯一新增对象是 `overlap_capabilities/3cd45d83e11ec6fe0e39725dfe7c6d79.consumed.json`；
- 内容发生预期执行期变化的文件仅为 `budget_state.json`、`overlap_workflow_state.json`、`overlap_transaction.json`，另有 `manifests` 与 `overlap_capabilities` 两个父目录元数据变化；
- permit 原对象保持不变，BOUND capability 已不存在，launcher receipt 不存在；
- ledger 仍为执行前原始字节，66,755 bytes，SHA-256 `8dfbb2bb9f23ac9066b457553c2bccfa94a2ab7dde5d66f6315595caaa793421`，没有构建终态事件。

当前运行态 SHA-256 分别为：

- `budget_state.json`：`715d1e034ea17391eb18ffb75eb7cb53ca1acf8121b47ed6b52da037645e1c96`；
- `overlap_workflow_state.json`：`0f134f3afd26600a323de2c5c1e9c84f73925b699922820fabc9800a1e4cd2aa`；
- `overlap_transaction.json`：`22ce3538de8266a6f2965ea840cc7d92c9a2e8bb2de94443c24259d0759d2a92`。

state 与 workflow 均未 hard-stop，stage 仍为 `SOURCES_PREPARED`，但 active 指针为 `4d7808af7df9418518a59afeba766eb9`。事务记录 action=`source_build`、bucket=`overlap_build`、forecast=4 GiB、child_pid=396、state=`RUNNING`，缺少 end、elapsed、exit、timeout、reason 与 launcher receipt 字段。已消费 capability 完整绑定原预算 argv、PID 294、launcher PID 396、该事务和 `source_build` 动作，说明许可链确实开始执行；缺少终态 receipt 则说明链未完成。

## 3. 构建树、日志与产物

prepared 树由执行前 5,319 项、canonical SHA-256 `7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260` 变为 7,640 项、canonical SHA-256 `afbeae908757c7e4f26010f39543a54503210fff9d24c71845bba9cf688dfed3`；这是 configure、make 与部分 check 的受控中间产物，不是可重新使用的 pristine 输入。自事务开始时间起有 2,392 个路径的时间戳或存在性变化，其精确路径清单已压缩封存在 evidence。

三份日志的固定结果为：

| 日志 | bytes | SHA-256 | 判读 |
|---|---:|---|---|
| `hdf5-configure.log` | 25,508 | `c6a76a377ea44024fac7c2a83e496907fd79665c431ce9b8fdb2ec8f95077b07` | configure 已完成 |
| `hdf5-make.log` | 190,832 | `3e6e7606d6c3d98ee85e18558d6b9c05583c0c7acf349fa2d4e31a1663988d53` | make 已完成 |
| `hdf5-check.log` | 135,350 | `12835bcc606f6399f65e3ba42a3e459117fdb540cf06a75df89fd1aedda064e2` | check 在 btree2 被 Terminated |

retired 历史树仍为 5,319 项，canonical SHA-256 `060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`，与执行前完全相同。官方受控 OpenMX 树 1,577 项与清单 SHA-256 `00b244438bc8c66ab5daf208874c4fd1ed2ba5fc69ffd2dda87436eccc47f1a7` 一致，无漂移。未发现 HDF5 安装前缀、OpenMX 编译产物、材料结构运行、训练或 GPU/DFT 动作。

## 4. 外部中断归因与预算计量边界

宿主事件日志提供了相互一致的只读证据：

- User32 事件 1074，RecordId 15842，`2026-08-31T23:23:35.9424034+08:00`：Explorer 代表登录用户发起关机，原因标为 Other (Unplanned)；
- EventLog 事件 6006，RecordId 15870，`2026-08-31T23:24:35.2278534+08:00`：Event Log 服务停止；
- Kernel-General 事件 13，RecordId 15890，`2026-08-31T23:24:41.9861048+08:00`，内嵌系统关机 UTC 为 `2026-08-31T15:24:41.9861032Z`。

三份事件 XML 的 UTF-16 SHA-256 分别为 `328fe76dfc58b52939ff38a61d863f751f15c0f3ae15fb21fb5dd5dcb7b559bf`、`a9535b7959ae42bff76e8e24d382e60b7200b84c67159181eb723e3b1244de62`、`d1dbaf9922a652217ca21a88466d4a36ff6901d63717fc02b6e0ee8afbaf6072`。结合 check 日志的 `Terminated`、无预算 hard-stop ledger 事件、无终态 receipt 以及 WSL 新 boot ID，证据支持宿主关机导致进程链消失；没有证据支持 WSL 自发崩溃或预算超时。

从事务 start UTC `2026-08-31T15:19:49.210200Z` 到 Kernel-General 内嵌关机 UTC 的精确差值为 **292.7759032 秒**。将其作为恢复时 `overlap_build` 的保守计量上界是可接受的，但必须标明它是墙钟上界而非实测 CPU：其中可能包含进程已经终止到内核最终关机之间的时间，因此不会低估本次正式动作。按十进制计算，历史 raw `overlap_build` 可由 `7214.469142588001` 增至 `7507.245045788001`，D-017 抵扣后的 effective 值可由 `14.393832060000932` 增至 `307.169735260000932`，对应 7,200 秒额度仍余 `6892.830264739999068` 秒。恢复实现不得把该上界描述为 CPU 测量，也不得重置既有 CPU、GPU、credit 或调整历史。

## 5. 回放阻断与恢复最低条件

旧 v3 机器许可不能放行重试。其原因不是 permit 文件消失，而是已安装 consumer 在许可验证后要求 readiness gate 内的 runtime 与当前 runtime 完全一致；当前 active 指针和 `RUNNING` 事务已使该条件失败。原 capability 已变为 `CONSUMED` 且无 launcher receipt，也不能重新绑定或补写为成功。直接重新执行原 argv、伪造终态、删除 capability、清理 prepared 树或复用旧 permit 均会破坏审计链。

后续恢复至少应当：

- 逐字保留本次执行前基线、当前三份非终态运行态、完整 ledger 原前缀、consumed capability、permit/gate/snapshot、缺失 BOUND/receipt 的事实及三份日志；
- 封存当前 7,640 项 prepared 树的完整身份，不在原位清理或把部分 check 解释为 PASS；retired 历史树和官方受控树继续保持原身份；
- 以版本化、pristine-only、阶段化 journal 和明确 write-set 的恢复控制器处理孤立事务，在首次写前证明 PID 消失、父态完整、授权、预算和所有历史闭集；
- 将孤立 `RUNNING` 事务以明确的外部中断语义终结，采用上述 292.7759032 秒保守上界计量，只追加一次可审计恢复/中断事件，并以白名单方式清理 active 指针；
- 恢复到可构建父态时使用重新验证的 pristine 源树，不复用当前已变异树；恢复事实须经独立审计；
- 为任何下一次构建建立并审计新的 consumer/gate/snapshot/permit/capability 链，绑定恢复后 runtime 与新树。D-019 的持续人工授权可以覆盖恢复实施，但不能替代这些独立 PASS 或复用一次性机器令牌。

## 6. 问题计数与证据边界

**阻塞问题 1：正式构建事务因宿主关机停留在无存活进程、无终态 receipt 的 `RUNNING` 状态，prepared 树含部分构建/自测产物。** 最小解除条件是上述版本化恢复门控经独立实施审计、唯一恢复执行和独立事实审计通过；之后另建并审计新的单次构建消费链。当前没有非阻塞问题。

本报告是中断事实审计，不是恢复实施审计、构建通过证明或下一次执行许可。它不判断未完成的 HDF5 check 若继续运行是否会通过，也不推断 OpenMX 编译结果。
