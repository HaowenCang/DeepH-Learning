# M9 source-control test cleanup 第二十次独立可靠性复核

## 结论

本轮结论为 **FAIL**：`BLOCKING=1`，`NON_BLOCKING=0`。上一轮的实现缺陷 `M9-SPR-R19-B01` 已关闭：冻结实现能够把 verifier 同一次文件描述符读取所得的精确 gate 字节、SHA-256 和 inode receipt 固化到 root 私有 snapshot，并由安全迁移 journal、cleanup context 和最终 receipt 引用同一 snapshot receipt；原 gate 在 verifier 返回后被删除、原 inode 内容改变、替换为另一份可解析 JSON 对象或在 snapshot 写入期间发生变化时，均在 parent 权限迁移、artifact rename、cleanup journal/receipt 和正式 runtime 写入前停止。

然而，稳定问题 `M9-SPR-R9-B01` 尚未满足上一轮规定的最小关闭条件。冻结正式测试虽然增至 60 项且全部通过，但名为 directory fsync 的注入实际发生在第二次 `fsync`，对应 committed target file，而不是第三次调用的 directory file descriptor；正式测试还未定向覆盖 committed target metadata recheck 中断、固定临时文件 wrong-owner 状态及另一份字段完整的结构合法 PASS gate。独立临时复现表明当前实现对这些状态能够停止或幂等续提，但一次性 cleanup gate 的放行条件要求冻结回归证据完整，不能用本轮外部审计脚本代替被冻结测试。因此不得创建或执行一次性 cleanup gate，也不得执行 cleanup、source-control recovery 或 `source_prepare`。

## 冻结对象与现场不变性

独立复算的四项 SHA-256 与本轮指定值完全一致：

- `06_reproduction/scripts/m9_budget.py`：`cbc3ee8aadb6f9494af4fc870fff392d53bcb72b45fa91de90f546f51f7deb5c`
- `06_reproduction/tests/test_m9_overlap_controls.py`：`228dd8d1c993d022107229a415527ef93261ad4ab9b967195d070203b8607392`
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：`743dd6cdaabf04affe344127e345457d64e55605da41b6d1a04cc532762b9d05`
- `06_reproduction/manifests/m9_source_control_test_cleanup_frozen_hashes.json`：`4c5a59af650e1cd683b643b0e6aa424fd87e8cfb69309bbdd0fe11985a0d7ee6`

source frozen manifest 登记对象前后均为 `17/17` 匹配，cleanup frozen manifest 登记对象前后均为 `4/4` 匹配。冻结 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9` 以 `-I -S -B` 运行完整正式测试，结果为 `60/60` 通过。

正式运行时对象在测试和全部临时复现前后保持以下 SHA-256：

- budget state：`1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`
- workflow：`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`
- transaction：`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`
- ledger：`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`
- capability：`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`

伪 transaction 前后均为 SHA-256 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`、1644 bytes、UID/GID 1000、mode 0644、nlink 1。retired、retirement receipt、cleanup journal、cleanup gate、source-control gate 和 source-control parent 均保持不存在；正式 `/root/deeph-m9-control/source-control-test-cleanup` 初始和终检均不存在。控制脚本目录中 `.pyc`、`.pyo` 与 `__pycache__` 合计为零。

## M9-SPR-R19-B01：CLOSED

`verify_source_control_test_cleanup_gate()` 使用一个 `os.open` 返回的文件描述符完成 `fstat -> read -> fstat`，并把同次读取的 bytes、SHA-256 及 dev、ino、size、uid、gid、mode、nlink receipt 保存到内存 gate。独立构造完整有效 gate 并调用实际 verifier 时，gate 路径的 `os.open` 计数为 1；返回 bytes 与输入逐字节一致，SHA-256 一致，inode receipt 与现场 `lstat` 一致。

`stage_cleanup_gate_snapshot()` 在 root:root、0700 的可信目录中以 root:root、0600、nlink 1 保存精确 bytes，并在写入前后分别重新打开原 gate 路径核对原 inode receipt 和 bytes。安全迁移 journal 的 `gate_binding` 同时记录原 gate inode receipt、原 gate SHA-256 与可信 snapshot receipt。实际临时 cleanup 完成后，cleanup journal context 和最终 receipt context 的 `verified_gate_snapshot` 均与迁移 journal 的 snapshot receipt 完全相等，且 snapshot SHA-256 与原 gate SHA-256 相等。

独立临时状态树得到以下停止语义：

- verifier 返回后删除 gate：报 `cleanup verified gate path is unavailable`，可信目录未建立，parent 保持 0755。
- verifier 返回后原 inode 内容改变：报 `cleanup verified gate path drift`，可信目录未建立，parent 保持 0755。
- verifier 返回后替换为另一份可解析 JSON 对象：报 `cleanup verified gate path drift`，可信目录未建立，parent 保持 0755。
- snapshot 写入完成但第二次原 gate 核对前改变 gate：报 `cleanup verified gate path drift`；允许已提交的 root 私有 snapshot 保留作为可审计半提交，但 migration journal 不存在，parent 仍为 0755，未发生 chown、chmod、artifact rename、cleanup receipt 或正式 runtime 写入。

完整临时 cleanup 使用正式伪对象字节复现后，parent 为 root:1000、1770，可信目录为 root:root、0700，snapshot 和 migration journal 均为 root:root、0600，migration 状态为 `SUCCESS_COMMITTED`。第二次运行返回 already-retired 语义，migration、snapshot、cleanup journal、receipt 和 retired artifact 的 SHA-256 全部保持不变。因此实现层面的同一 snapshot 绑定、owner/mode/path 合同和重复运行幂等性成立。

## 持久化 JSON 中断恢复复现

独立 root 临时目录直接运行 `atomic_private_durable_bytes()`，未 mock 掉文件系统写入。固定 `.tmp` 含有 owner/mode 正确的部分内容时，函数截断并写入完整 payload，最终 target 为 root:root、0600、nlink 1，`.tmp` 消失。固定 `.tmp` 为 symlink、hardlink、wrong owner 或 wrong mode 时，函数均以 `root-private atomic temporary file mismatch` 停止，target 不建立，关联 sibling 内容不变。

逐点中断结果如下：

- 第一次 `fsync` 失败：完整 payload 留在 `.tmp`，target 不存在；重入提交成功。
- `replace` 失败：完整 payload 留在 `.tmp`，target 不存在；重入提交成功。
- committed target metadata recheck 返回异常：target 已含完整 payload、`.tmp` 已消失；本次停止，重入重新提交成功。
- committed target file 的第二次 `fsync` 失败：target 已含完整 payload；重入成功。
- directory file descriptor 的第三次 `fsync` 失败：target 已含完整 payload；重入成功。

以上各次重入的终态均为 payload 精确匹配、root:root、0600、nlink 1、固定 `.tmp` 不存在。由此可判定当前持久化函数具备所需的可恢复状态划分；剩余阻塞属于冻结回归证据不完整，而不是本轮已观察到的实现恢复失败。

## M9-SPR-R9-B01：OPEN

冻结测试 `test_atomic_private_durable_bytes_failure_matrix_is_resumable` 将 `file_fsync` 的注入点设为第一次 `fsync`，将名为 `directory_fsync` 的注入点设为第二次 `fsync`。实现顺序实际为：临时文件 `fsync`、原子 replace、committed target file `fsync`、directory file descriptor `fsync`。因此第二次调用证明的是 committed target file fsync 的续提，第三次调用的 directory fsync 尚未进入冻结测试。

同一冻结测试没有在 replace 之后、directory fsync 之前令 committed target metadata recheck 失败。固定临时对象异常矩阵只包含 symlink、hardlink 和 wrong mode，没有 wrong owner。gate replacement 矩阵包含非 JSON、仅含 `status=PASS` 的不完整 JSON 和删除，但没有保留全部合同字段、同时改变证据绑定的另一份结构合法零问题 PASS gate。snapshot 写入期间漂移用例已经存在并有效，不属于剩余缺口。

最小关闭条件：保持稳定问题 ID `M9-SPR-R9-B01`，在冻结正式测试中增加或修正以下定向状态：第三次 `fsync` 的真实 directory fsync 中断；replace 后 committed target metadata recheck 中断；固定 `.tmp` wrong-owner；字段完整但证据值不同的结构合法 PASS gate 替换。每个中断用例应分别断言第一次停止后的 target/`.tmp` 精确状态、第二次运行的幂等续提终态，以及五项正式 runtime、伪 transaction、17/17、4/4 和 cache=0 不变。更新冻结测试后还需同步合法更新两份冻结 manifest，并由新的独立复核重新计算全部哈希。

## 放行判断与审计边界

当前为 `BLOCKING=1`、`NON_BLOCKING=0`、FAIL。`M9-SPR-R19-B01` 已关闭，但 `M9-SPR-R9-B01` 仍为 OPEN；未达到 `BLOCKING=0` 且 `NON_BLOCKING=0`，因此主 agent 不得创建一次性 cleanup gate。即使后续复核达到零问题 PASS，也只允许主 agent 按明确授权决定是否创建该一次性 gate，不自动授权 cleanup、source-control recovery、`source_prepare` 或其他动作。

本轮除新增本报告外未修改冻结对象或其他被审对象；未创建或执行 gate，未整理或移动任何正式运行时对象，未执行 recovery 或 `source_prepare`。全部行为复现均位于自动删除的临时目录。
