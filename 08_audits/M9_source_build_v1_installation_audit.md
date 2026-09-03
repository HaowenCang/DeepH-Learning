# M9 source_build v1 独立安装事实审计

审计日期：2026-08-30  
结论：**FAIL / BLOCKING=1 / NON_BLOCKING=0**  
冻结manifest SHA-256：`b3a344e00d3cac19edcf23c69a2631307d6e08714c3a85c85eca8572f2496641`

## 结论与阻塞

正式snapshot和readiness gate已按预期安装，旧历史及源码树没有被改写，但真实UID1000不能通过已安装consumer的verify-ready。此次安装不能进入permit签发或source_build；实施阶段PASS和root安装返回成功均不能替代真实UID1000消费验证。

阻塞编号：`M9-SB-V1-INSTALL-B01`。`m9_source_build_consumer.py` 的 `runtime_and_history(private=False)` 只排除 `/root/`，仍对整个manifests目录调用递归内容哈希。该目录包含原本必须保持root:root/0600的历史证据；真实UID1000无权读取。失败调用链为 `main -> verify_gate -> runtime_and_history -> capture_tree -> filesystem_receipt -> stable_bytes -> os.open`，在以下路径产生 `PermissionError: [Errno 13] Permission denied`：

```text
/home/evan-williams/deeph-m9/manifests/overlap_source_control_recovery.test-artifact.retired.json
```

本审计以真实evan-williams UID/GID1000及固定Python3.9.23 `-I -S -B`，直接运行已安装snapshot中的consumer入口。verify-ready和verify-execution均退出1，stdout为空，并在上述同一历史文件提前拒绝。因此verify-execution的结果不是“已经到达缺permit检查并正确拒绝”；只能确认当前入口不可消费，permit实际缺席。没有调用run、installer、permit或任何构建动作。

实施阶段真实UID1000测试使用合成fixture，其manifests历史文件可读，未复现生产环境这8个root-only历史对象；root preflight及安装验证具有读取权限，也不能暴露此问题。此为一个权限分层实现缺陷，不是历史文件权限应当放宽的证据。既有实施报告/verdict保持原SHA，当前安装事实FAIL阻断后续阶段。

## 实际安装与不变证据

实际readiness gate SHA为 `90d91575a5d53a2efd015d72ebf6c7ac04440aca1a5b6ea3fee3df09461b3a7c`；snapshot manifest SHA为 `75f05a9e11a818f40f7b85cebf92410fc0fb2b6c64ce2ddcfdf1c0872fbac313`，与实施preflight预测一致。目录root:1000/0550，15个实际文件均root:1000/0440、普通单链接；14个封存成员加snapshot_manifest.json的严格闭集、全部成员大小/SHA和实施report/verdict绑定通过。gate为root:1000/0640、普通单链接。

相对source_prepare的130项完整基线，正式命名空间现有147项：仅新增snapshot目录、15文件和readiness gate共17对象。旧controls目录nlink由6变7、mtime/ctime变化，旧manifests父目录mtime/ctime变化；其余旧对象receipt逐项全等。旧25-file和16-file来源SHA、新10-file来源、派生预算与原预算的反向字节比较全部通过。

真实入口调用前后147项正式receipt完全一致，canonical SHA为 `78003a0d58a321e5e2a57bf76b1fd2106bed92d894433a43bfbb6f45943a150e`。两棵树亦前后完全一致：

| 对象 | 文件/目录 | 完整receipt canonical SHA-256 |
| --- | --- | --- |
| 已准备源码树 | 5179/140 | 7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260 |
| 原失败退休树 | 5179/140 | 060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359 |

state/workflow/当前source_prepare成功事务及ledger不变，workflow仍为SOURCES_PREPARED。ledger仍为64298 bytes，SHA `0be27e9220b6597d47ee657bbe5169134118340c77a7a0af3722a4eb1ad885c2`，没有新增执行事件。D-017/D-018、旧gate/snapshot、root-private失败与恢复证据全部保留。permit及其tmp缺席；没有编译产品、构建日志、活动staging或材料结构运行目录。

原始overlap_build累计7212.901214103001秒，有效12.825903575000666秒，剩余7187.174096424999秒；原抵扣、GPU历史和UNLIMITED墙钟策略不变。4 GiB预测的预算violations为空。采集时combined apparent/allocated为31130714386/31456145408 bytes，overlap增量为1261234655/1286324224 bytes，VHDX overlap增量1644167168 bytes。新增审计证据计入项目存储，后续即时预检不能使用旧快照替代。

## 固定的root-only历史集合

对旧基线所有非 `/root/` 路径，以真实UID1000只读检查权限，确认恰有以下8个不可读文件；均在 `/home/evan-williams/deeph-m9/manifests/` 下，为root:root/0600、nlink1、设备2096。路径、inode、大小、SHA以及完整时间戳均在持久化baseline中，不能动态忽略任何其他读取失败。

| 文件名 | inode | bytes | SHA-256 |
| --- | --- | --- | --- |
| overlap_source_control_recovery.test-artifact.retired.json | 153218 | 1644 | 2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74 |
| overlap_source_control_recovery_gate.closed-set-invalid.retired.json | 132095 | 1711 | 6bdd2fdbff6df6a7a8cfa1ba3cda038ca7cfe96b3b5dfb48905ef0f5151f5821 |
| overlap_source_control_recovery_gate.json | 153209 | 2398 | 8e66d65d17d3195f3df09db954afca4066c3ec91e2d8dad6d2aea06078d0d5ce |
| overlap_source_control_recovery_gate.pre-ledger-fix.retired.json | 153048 | 1728 | 381c8fd6e9fa28479de4f2144e975ed32756af9ac9dfe90a6d5457208da1cefa |
| overlap_source_control_recovery_gate.pre-lock-mode-refresh.retired.json | 139158 | 1723 | 5553de21184082b3ace505f4981f20c3116df7389805f2070ebf7e8b8dad5936 |
| overlap_source_control_test_artifact_cleanup.json | 153304 | 4242 | 1e0729d72bb7e45e773a61d9aff6228061a5b000cd218c23e5263153f2425d8d |
| overlap_source_control_test_artifact_retirement.json | 153217 | 3988 | 74b24867d06a437f0e693c8edd231ab4bc31782b8978abfff77b01658567fd49 |
| overlap_source_control_test_cleanup_gate.json | 139156 | 2713 | 12cec1f13eec81c110b8a7d66aecaf4e1786c0821c82a702885b9e74cfeb57b2 |

## 最小修复条件，仅建议

应保留v1安装、报告、verdict、冻结成员及历史权限不变，另建明确版本的修复方案并重新审计。root安装及permit前逐字核验完整历史；对上述固定8项和原root-private集合，由root签发且绑定新gate/snapshot的不可变receipt承担内容哈希证明。UID1000仍应检查它能观察的确切路径、类型、dev/ino、owner/group/mode、nlink、大小和mtime/ctime；其余可读历史继续由UID1000实际读取并哈希。

不可把捕获任意PermissionError后跳过、自动按当前可读性缩小闭集、chmod/chown旧证据，或复制成未经绑定的可写替代文件作为修复。新增/缺失对象、错误权限、同字节新inode、链接和未登记不可读对象仍须在任何写入前拒绝。

新测试应在临时夹具复现同样8项root:root/0600布局，并以真实UID1000完成已安装入口verify-ready；verify-execution应实际到达缺permit分支并零写拒绝。随后验证root-only对象内容/metadata漂移拒绝、root签发receipt绑定、未登记不可读对象拒绝，以及两次验证前后完整命名空间和预算不变。修复不能扩大此次source_build范围，本审计未实施上述方案或授权重放。

## 持久化证据与结束状态

独立证据文件为 `M9_source_build_v1_installation_postexecution_evidence.json`，643403 bytes，SHA `0e125e288af8299fb3cf6447ac379e3b946bd042ddd705537dcd9cff11300f00`。它保存147项完整receipt、允许的父目录差异、四份原始runtime字节（包括完整64298-byte ledger）、两个真实UID1000入口的完整argv/退出码/stderr、预算快照及完整准备树的gzip+Base64编码。树解压后的canonical JSON为5319项；文件从磁盘重新读取后，receipt整数精度、canonical SHA和原始字节均通过往返校验，可作为后续经过批准的修复审计基线。失败退休树保存完整receipt哈希，仍可独立逐文件重核。

严格Markdown、JSON字段及report SHA绑定、`git diff --check`通过，M9源码与controls缓存为0。本审计只新增报告、verdict及上述证据文件；正式运行态零写。结束状态为安装事实FAIL/1/0、permit缺席、source_build未执行；不得签发许可或继续编译。
