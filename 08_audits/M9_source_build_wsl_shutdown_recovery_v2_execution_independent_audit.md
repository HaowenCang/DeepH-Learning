# M9 source_build WSL shutdown recovery v2 独立执行事实审计

## 判定

**PASS；BLOCKING = 0；NON_BLOCKING = 0。**

现有正式 WSL 证据支持：冻结的 WSL shutdown recovery v2 已形成一次且仅一次成功恢复提交；被外部中断的 v4 `source_build` 已按合同计入保守上界，失败事务及全部旧权限证据保留，运行态恢复为非 hard-stop 的 `SOURCES_PREPARED`，但没有产生新的构建许可或执行权限。本判定不授权新的 `source_build`、下载、材料计算、结构计算或训练。

本报告是审计产物事实更正版。首版把中间审计摘要中的错误 consumed-capability 摘要转录进报告和 evidence，而未使用正式对象的复算值；错误值已删除，不能继续作为 PASS 证据。定点更正时重新计算了报告/evidence 中全部摘要字段，未发现第二处复制或计算错误。正式 capability 为 4,513 bytes、SHA-256 `8d6aff34eec0ee29ce8a7b8e6a8fdf8a76b78ec1fe5a5bd584ee1e2587607204`、state `CONSUMED`，与冻结历史权威一致。

审计使用固定 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B`，从冻结 controller、work package、manifest、初始 FAIL 审计、定点 PASS 复核、v4 中断证据和正式对象独立重算。主执行记录 SHA-256 `c28d4de35b72662f30fbb8b804aca39f2846c30550c372ed55185a58ba08ea42` 仅用于定位，不作为任何 PASS 事实的证明。完整摘要证据为 `M9_source_build_wsl_shutdown_recovery_v2_postexecution_evidence.json`，SHA-256 `b3477ede6590cda56d5cf45bb1a16809e591d6aa5858531807f5cc1513eaca36`。

## 权威与 namespace

实际 controller、work package、frozen manifest 分别匹配 `21cf81c6a63218a6e1de23bf14e2e9d928eb413fd5529a2d18d0b8859d3a1801`、`23a3df56569a6ce2197be927878e0b3a46cf9df172f67e7078b416864dacf318`、`139fb44a695873f1771fa05bd15bc28a9ac348ee2f6fc8a567080c7e920b1e62`。初始 FAIL 报告/verdict 保持原字节；定点复核报告/verdict 匹配 `f39e977092fc5b141507542828fdacb6a045b343a1aebf23a2e95f252fde54f4` 与 `9f9331d5ca762f4fb54325a54fe21c9b7d4955d84856598d143e965f2f730fc9`。

以中断证据中的 275 项、canonical SHA-256 `8f904289db590a6bf68d7d62f0e13cda0893cec30321274d67559261758402b9` 为父态，当前正式 namespace 为 301 项、canonical SHA-256 `5153de04dd6a33f8851cd898d8af9c8e655a57a161d31f70a7f60dc8032c0f42`。差集恰为 26 项：root-private 目录及 20 个普通文件共 21 项，公开 snapshot 目录及 4 个普通文件共 5 项；无移除项。旧对象变化严格限于四份 runtime、ledger 及其允许的父目录元数据，未发现未知对象或越界修改。

## runtime、ledger 与预算历史

四份 runtime 均逐字匹配 controller 生成的目标：state `c45337d97584abbce0c885ca233d9fd9bd9b548d17847a52a7f1b398fc9c1dec`，workflow `96778c2501f2d7eca33b973266e4a8e33e22bc65238cd0b9f12d014a3c5c7aa7`，transaction `cf17e84abf1303438220ad3a872375e779de19052a10cf2cee41055f0d04ed91`，ledger `24253c63284171f826b6b068053e8bd7fe1fd1a8e2feadbca3f5885f4443ed8b`。

ledger 保留原 68,599-byte、SHA-256 `f3f44ee5169bbeb44d175ff0aa381cda70684ad66f11ce57725c2e774471d4c7` 前缀，68 行变为 69 行；新增后缀恰为一条 `SOURCE_BUILD_WSL_SHUTDOWN_RECOVERY` 事件。ledger 仍为 dev 2096、ino 50691、UID/GID 1000:1000、0644、单链接，证明追加未替换 ledger inode。事件保留 D-017 的 `7200.075310528` 秒抵扣、GPU 各桶和历史授权哈希，并以 `138.401802566` 秒 `conservative_wall_upper_bound_not_measured_cpu` 计入 overlap build；未重置或扩张任何预算。

事务保持原 `source_build` transaction id `d52575f446d3c62f0fc93c3c65f3c959`，终态为 `FAILED_COMMITTED`，reason 仅为 `wsl_shutdown_external_interruption`，elapsed `138.401802566`，`exit_code=null`，`timed_out=false`，launcher receipt SHA 为 null。state/workflow 均为 `hard_stopped=false`、`active=null`；workflow 阶段为 `SOURCES_PREPARED`。全部既有失败、恢复、抵扣和 GPU 历史标记保留，仅新增本次恢复 marker；`source_build_authorized=false`。

## 树、归档与恢复日志

中断 BUILD 已原子归档为 7,621 项，canonical SHA-256 `9210f3c37f6b328691b4bed963ee11f57fb481ba48242d2450b8d7df4e174e9f`；对原 BUILD 的逐相对路径 dev/ino/UID/GID/mode/nlink/bytes/kind/SHA 比较无差异。4 项中断日志同样以原 inode 身份归档，canonical SHA-256 `9ad2f041ace0a8c712febc81b086dff58e6b688155f755c73dd7e32c9658de96`。

新 BUILD 为 5,319 项，portable SHA-256 `cf91d95aa8802925da676dab35fe5bb991a6061f809b871bca488f4c50347cc0`，与 clean tree 完全等价；所有普通文件均为单链接，并且 BUILD 与 clean 的普通文件 inode 交集为零。既有 7,640 项 prior archive 和 4 项 prior log archive 分别保持 `82bc6705ef8a507d2580630592f4903726622768aebb5bd7b1d22d93afa12515` 与 `5ea65a500eaadc665b4d282ce8b8c55019629b722020b7baa73259c9f862d4de`，未改变。

root-private 闭集恰为目录加 20 文件，权限为目录 root:root 0700、文件 root:root 0600 单链接；全部载荷、before-runtime 副本及目标哈希匹配。journal SHA-256 `9ba4f235a9a4c4fb543ddf8ae47141b5d1c3cdddc592843dc187d22e0c234677`，终态 `SUCCESS_COMMITTED`，历史恰含 `PREPARED`、`INTERRUPTED_ARCHIVED`、`LOGS_ARCHIVED`、`CLEAN_TREE_CLONED`、`LEDGER_COMMITTED`、`TRANSACTION_COMMITTED`、`STATE_COMMITTED`、`WORKFLOW_COMMITTED`、`SUCCESS_COMMITTED` 九阶段；各阶段 post-receipt 与最终目标哈希一致。

公开 snapshot 恰为目录加 4 文件，目录 root:1000 0550，文件 root:1000 0440 单链接；manifest、源字节和闭集均精确匹配，且不含 permit、capability 或任何执行授权。

## 负面事实与旧权限回放

staging、当前 `logs/overlap-build`、launcher receipt 和六个最终构建产品均缺席；没有相关存活进程、cache、新 permit、新 capability、下载、数据生成、材料/结构计算或训练证据。旧 consumed capability、v4 gate 和 v4 permit 的 SHA 分别仍为 `8d6aff34eec0ee29ce8a7b8e6a8fdf8a76b78ec1fe5a5bd584ee1e2587607204`、`dcd0a0ed3307add49df5b7586ba0bf01b2fc55b0469a42067893e563ba2ff3c1`、`c3aae6ff0c5aaffb3d5a711b48e7dc505061959eb144509995f8e9890f5853d4`。

真实 UID1000 从已安装 v4 snapshot 以固定 Python 执行只读 `verify-execution`，退出 1，并以 `build historical namespace closure mismatch` 拒绝回放。调用前后 301 namespace、四份 runtime 和六棵树摘要完全相等，故旧 v4 permit/capability 不能被恢复后状态重新消费。

## 调用次数证据边界

正式持久态不能独立证明零写 preflight 被调用了几次。其原因是合规 preflight 不留下持久写入；“唯一 preflight”只能由宿主调用记录支持，不能由 WSL 终态反推。本证据边界不影响恢复事实判定，因为 preflight 的验收合同本身是零写。

持久态能够证明恰有一次成功 recovery commit：旧 ledger 精确前缀之后只有一条恢复事件，只有一份具有唯一九阶段历史的 `SUCCESS_COMMITTED` journal，只有一组恢复 marker、归档、private 与 snapshot 闭集，且 pristine-only 结构阻断第二次成功提交。但持久态同样不能证明总共尝试过几次 recover；任何在首写前被拒绝的零写尝试按设计不会留下记录。因此，本 PASS 严格表述为“一次成功恢复提交”，不把它扩张为“总调用尝试次数恰为一次”。

## 最终边界

未发现 blocking 或 non-blocking finding。恢复只把外部中断事实终态化并恢复 `SOURCES_PREPARED`；它不完成构建、不签发构建权限，也不授权重放 v4。任何后续 `source_build` 仍须建立新的版本化消费门控、独立审计并按现行授权程序签发新的单次机器权限。
