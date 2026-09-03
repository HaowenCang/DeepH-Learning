# M9 source_build v4 中断事实独立审计

日期：2026-09-02。审计角色：独立子 agent。判定为 **FAIL / BLOCKING=1 / NON_BLOCKING=0**，两个问题计数均为整数。本结论证明唯一 v4 `source_build` 已进入 HDF5 构建后因 WSL 实例关机而遗留非终态事务；它不是构建成功，也不是原预算正常提交的失败。当前不得重放 v4 permit、capability 或构建命令。

## 权威与证据边界

独立重算执行前报告和完整 274 对象证据，SHA-256 分别为 `b817c7505b5b667dbb990cdfcc5687c87cffd9170f45cef4539096f63b02b727` 与 `11c20faeb1069d29804d6ffa5b98705ab6579ced0a62ca7d2b0583eb1c7ecc70`。其可逆载荷解压为 274 项、canonical SHA-256 `6c2db9fb44776e40592e0a545e3db6a25628088159a6a7418f3cdabb54c7e6de`。主端执行记录 SHA-256 `b961f28a1c8fd281291aa7f6cb17be05e547286ff5159d9b123ae932ed8d59d3` 只用于定位会话和 PID，没有作为判定自证。

本次 [完整中断证据](M9_source_build_v4_interruption_postexecution_evidence.json) SHA-256 为 `9985eff9ec38d5763ace3ede75eef418ed8d57bbf5f7611025154f992debebbb`。其中保存了可逆压缩的完整 275 正式 namespace、完整 7621 项 BUILD receipt、完整 4 项日志树及三个日志原字节、四份 runtime 原字节、capability、时间线、预算和负面检查。两次连续采集均相等；正式采集结束时没有遗留审计进程。

## M9-SB-V4-INT-B01：非终态外部中断

相对执行前 274 对象，当前正式 namespace 恰为 275 项、115823 canonical JSON bytes，SHA-256 `8f904289db590a6bf68d7d62f0e13cda0893cec30321274d67559261758402b9`。没有删除，唯一新增对象为 capability `c68a261b9f1e95c692a3b4241360440e.consumed.json`。旧对象变化严格限于 manifests 与 capability 父目录 metadata，以及 `budget_state.json`、`overlap_workflow_state.json`、`overlap_transaction.json` 三个运行态文件；v4 snapshot、gate 和 permit receipt 与执行前逐项全等。

当前 state 与 workflow 均非 hard-stop，但 active id 均为 `d52575f446d3c62f0fc93c3c65f3c959`。transaction 为 `source_build/RUNNING`，同一 transaction id，child PID 397，prepared UTC `2026-09-01T14:46:32.118063Z`，start UTC `2026-09-01T14:46:52.111163Z`。capability 已从 BOUND 变为 `CONSUMED`，SHA-256 `8d6aff34eec0ee29ce8a7b8e6a8fdf8a76b78ec1fe5a5bd584ee1e2587607204`，并精确绑定固定 Python、v4 consumer、唯一逐 token argv、同一事务、4 GiB forecast 和 v4 launcher；BOUND 路径及 launcher receipt 均缺席。

ledger 仍为执行前原字节：68599 bytes、68 行、SHA-256 `f3f44ee5169bbeb44d175ff0aa381cda70684ad66f11ce57725c2e774471d4c7`。原始 `overlap_build` CPU `7507.245045788001` 秒、抵扣、GPU 和历史存储基线不变，有效 CPU 仍为 `307.1697352600013` 秒。因此既没有 SUCCESS/FAIL 事务提交，也没有对应 ledger 或 hard-stop 事件。这与原预算的普通失败路径不符；普通失败必须接收子进程终态并提交 FAILED、清空 active、计量 CPU 和写入 ledger。

BUILD 从执行前 5319 项、SHA-256 `411a8a674559723f0616deafbe67c93d3e31453461fa6b2af26d4135bb3e1705` 变为 7621 项、SHA-256 `25fa00697f192967f8adcc0656eea976eeb9839390a78757a04d00ac66796dc0`，其中识别出 1144 个 HDF5 `.o/.lo/.la/.so` 或 `.libs` 中间对象。当前日志树有 4 项、SHA-256 `f1d69a2016dc0ae5df54519d4155a9b0317bcb7c4edf55cdea85c43d9a4b1db3`：configure、make、check 三个日志分别为 `9eaddfc26b2640b71f8ced44a19e29b437a7551bfb2b885444e256c064967a25`、`ef498488710ead1c4913c50a8439d20ae53a1824040ad0595a4dc864bf47eb3b`、`fc4f27dbab3719115e1eb862c659f8cd251ca4d015cda6eb3daef29074e3ccfe`。控制流及日志共同证明 HDF5 configure 和 make 已完成并进入 `make check -j1`；check 在 `cache_image` 测试处以两级 `make ... Terminated` 结束。

HDF5 安装 prefix、OpenMX official/overlap 二进制、OpenMX tree/build manifest 均缺席，OpenMX 编译尚未开始。干净 retired 树仍为 5319 项、SHA-256 `060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`。上一轮 7640 项 BUILD 归档和 4 项日志归档也分别保持 `82bc6705ef8a507d2580630592f4903726622768aebb5bd7b1d22d93afa12515` 与 `5ea65a500eaadc665b4d282ce8b8c55019629b722020b7baa73259c9f862d4de`。当前未发现 consumer、launcher、compiler、make、MPI 或 OpenMX 构建进程；项目与已安装 controls 中缓存对象为 0。

这些事实排除 BUILD PASS：没有 launcher PASS receipt、SUCCESS_COMMITTED transaction、BUILD_PASSED workflow、成功 ledger 事件或最终产品。也排除原预算正常 FAIL：没有子进程退出回执、FAILED_COMMITTED、active 清理、计量或失败 ledger 事件。因此当前只可分类为“外部 WSL 实例停止造成的非终态中断”。

## 时间线与计量建议

WSL `wtmp` 原始记录给出该实例 boot `2026-09-01T14:45:53.733510Z`、shutdown `2026-09-01T14:49:10.411143Z`。前一 boot 的 journal 在香港时间 22:49:10 依次记录 P9 `Operation canceled`、`System is powering down`、`System Power Off`、`Shutting down` 和 `Journal stopped`。`hdf5-check.log` 最后 mtime 为 `2026-09-01T14:49:10.512965566Z`，只比 wtmp shutdown 晚约 0.102 秒，且末尾为 `Terminated`，两类独立证据在误差范围内一致。

Windows System 日志的 Event 1074、6006、Kernel-General 13 分别发生在 `2026-09-01T16:58:00.6358453Z`、`16:58:50.6880266Z`、`16:58:57.6665475Z`。Event 1074 比 WSL shutdown 晚 `7730.224702` 秒，约 2 小时 8 分 50 秒。因此 Windows 整机关机不能解释为同一时刻事件；现有证据也不能确定是谁或什么机制发起 22:49 的 WSL 实例关机。能够确定的是关机发生在预算子进程外部，并终止了仍在运行的 HDF5 check。

恢复计量应采用与既有预算语义一致的保守 wall-clock 上界：从 transaction start `2026-09-01T14:46:52.111163Z` 到两项终止证据中较晚的 check 日志 mtime `2026-09-01T14:49:10.512965566Z`，即 `138.401802566` 秒。该值是控制器兼容的保守 wall 上界，不是测得的多核 aggregate CPU。若恢复严格追加此值，有效 `overlap_build` CPU 将为 `445.5715378260013` 秒，仍低于 7200 秒上限。当前即时存储在 0 与 4 GiB forecast 下均为 `violations=[]`；这只证明预算余量，不构成重试许可。

## 阻塞项与恢复验收条件

**BLOCKING M9-SB-V4-INT-B01：** 当前事务和 active 字段仍为 RUNNING，capability 已消费而没有 launcher receipt，BUILD/日志又包含未归档的部分构建现场。在完成版本化恢复及其独立实施、执行事实审计前，不得继续 M9 构建或后续 smoke。

最小恢复门控应满足以下可验证条件：

- 以本报告完整证据绑定当前 275 项正式 namespace、四份 runtime 原字节、完整 7621 项 BUILD、完整日志、5319 项干净 retired、旧 7640/4 项归档、已消费 capability、v4 gate 与 permit；未知对象或任一漂移均在首次写前零写拒绝。
- 使用新的 root-owned、版本化、pristine-only recovery snapshot/gate；在原 `budget.lock` 内再次全量复核后才允许首次写。故障窗口必须保留现场，不得提供无证明的自动重放。
- 将当前 BUILD 和日志分别归档到绑定 transaction id 的新且原先缺席路径，不覆盖旧归档；rename 前后验证 inode/receipt，持久化文件和所有父目录。随后只从受信 retired clean 树复制到新 staging，逐项验证便携内容/metadata、无 hardlink 交叉及目录 fsync，再原子安装为新的干净 BUILD。
- 保留 v4 snapshot、gate、permit、已消费 capability、receipt 缺席事实、旧失败事务及全部历史证据；不得删除、覆盖或把旧 permit/capability 重新标为可用。
- 将本次 transaction 版本化提交为外部 WSL shutdown 导致的 FAILED_COMMITTED，清空 state/workflow active，workflow 保持 `SOURCES_PREPARED`；只允许这些明确白名单字段变化。ledger 必须保留现有 68599-byte 前缀并只追加一个恢复事件，按 `138.401802566` 秒进行控制器兼容的保守计量，CPU/GPU/抵扣/存储历史不得重置。
- recovery 不得签发新 build permit、不得启动构建。恢复成功及独立事实审计通过后，任何再次编译仍需新的版本化 consumer/readiness/permit 门控；现有 v4 permit、operation 和 consumed capability 均不可重放。

## 最终判定

判定为 **FAIL / BLOCKING=1 / NON_BLOCKING=0**。阻塞原因不是已证明的编译错误，而是 WSL 实例关机在 HDF5 check 中途终止进程，使原预算无法提交终态。现有证据不足以识别 WSL shutdown 的发起者，也不支持把约两小时后的 Windows 整机关机视为同一事件。当前仅允许设计和独立审计上述版本化恢复；本审计没有执行恢复、重试、构建、preflight、install、permit 或任何正式写动作。
