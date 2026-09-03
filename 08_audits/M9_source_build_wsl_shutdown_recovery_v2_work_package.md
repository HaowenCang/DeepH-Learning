# M9 source_build WSL 关机中断恢复 v2 工作包

日期：2026-09-03。状态：REVISED_PENDING_INDEPENDENT_TARGETED_REAUDIT。首轮独立实施审计为 `FAIL/BLOCKING=2/NON_BLOCKING=1`，其报告与 verdict 保持不改写；本修订只在重新冻结后接受独立定点复核。D-019 持续授权覆盖本恢复的实施、审计与单次执行，但不取消独立技术门控，不授权重放 v4 permit/capability，也不扩大冻结的 overlap-only 科学范围。

## 失败事实与恢复边界

v4 唯一 `source_build` 已消费 operation `bb0b7c8b982d4d72a66a1f01f95533da` 和 capability `c68a261b9f1e95c692a3b4241360440e`。transaction `d52575f446d3c62f0fc93c3c65f3c959` 在 WSL 实例关机后仍为 `RUNNING`；state/workflow 仍指向该活动事务，ledger 保持执行前 68,599-byte 前缀，launcher receipt 缺席。独立审计 `M9_source_build_v4_interruption_independent_audit.md` 给出 `FAIL / BLOCKING=1 / NON_BLOCKING=0`，阻塞项为 `M9-SB-V4-INT-B01`。该状态属于外部 WSL 实例中断形成的未提交事务，不能伪装为普通构建退出，也不能重放已消费权限。

事务起始时间为 `2026-09-01T14:46:52.111163Z`；HDF5 check 日志最后修改时间为 `2026-09-01T14:49:10.512965566Z`，尾部在 `cache_image` 测试中出现 `Terminated`。恢复采用二者之差 `138.401802566` 秒作为控制器兼容的保守 wall 上界计入 `overlap_build`，不是聚合 CPU 实测值。原 raw CPU 为 `7507.245045788001` 秒，计入后为 `7645.646848354001` 秒；保留既有 `7200.075310528` 秒抵扣后，effective CPU 为 `445.5715378260013` 秒，仍低于 7200 秒上限。不得重置或增加 CPU、GPU、存储预算。

## 冻结对象

恢复控制器直接冻结以下十二项来源：控制器、隔离测试、本工作包、D-019、v4 中断独立报告、v4 中断完整证据、v4 执行前证据、只读 receipt 模块、当前 budget 模块、v4 frozen manifest，以及首轮 FAIL 报告和严格 verdict。执行 authority 精确 single-FD 固定这十二项、v4 manifest 本身及其 22 个直接成员；receipt 与 budget 均只从已经固定的原字节编译加载，不回退读取项目同名文件。首轮 FAIL 不被覆盖；定点复核另写 targeted report 和 final verdict，正式恢复同时绑定二者。

旧 manifest 的固定字节仅证明历史时点曾声明哪些摘要，不声称其可变路径叶仍保有全部历史字节，也不把二层历史叶作为本恢复的执行依赖。历史扫描发现十个同路径多摘要版本，其中 `master_execution_plan.md` 的 `4f454c5b...`、`progress_tracker.md` 的 `fcc8326e...` 和 `decisions.md` 的 `d1b5a40c...` 三个旧版本在现有工作树、Git、root-private 和 installed controls 中均无可重建副本；该证据边界被明确保留，不通过当前同名文件替代。此定义消除了首轮 B02 的含糊一层递归和不可满足的历史叶假设，同时保持实际执行模块闭集完整。

恢复前必须再次逐字或逐 receipt 绑定：

- 275 项完整正式 namespace，canonical SHA-256 `8f904289db590a6bf68d7d62f0e13cda0893cec30321274d67559261758402b9`；
- 四份 runtime 原字节及 68,599-byte ledger 前缀；
- 已消费 capability SHA-256 `8d6aff34eec0ee29ce8a7b8e6a8fdf8a76b78ec1fe5a5bd584ee1e2587607204`、缺失 launcher receipt、匹配进程为空；
- v4 gate SHA-256 `dcd0a0ed3307add49df5b7586ba0bf01b2fc55b0469a42067893e563ba2ff3c1` 和 permit SHA-256 `c3aae6ff0c5aaffb3d5a711b48e7dc505061959eb144509995f8e9890f5853d4`；
- 当前部分 BUILD 7,621 项，canonical SHA-256 `25fa00697f192967f8adcc0656eea976eeb9839390a78757a04d00ac66796dc0`；
- 当前日志树 4 项，canonical SHA-256 `f1d69a2016dc0ae5df54519d4155a9b0317bcb7c4edf55cdea85c43d9a4b1db3`，并逐字核验三份日志；
- 干净退休树 5,319 项，canonical SHA-256 `060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`；
- 上一轮中断归档树 7,640 项及日志归档 4 项，canonical SHA-256 分别为 `82bc6705ef8a507d2580630592f4903726622768aebb5bd7b1d22d93afa12515` 和 `5ea65a500eaadc665b4d282ce8b8c55019629b722020b7baa73259c9f862d4de`；
- HDF5 prefix、OpenMX build/tree manifest 与三个 OpenMX 二进制均缺席；1 GiB 恢复存储预测无违规。

## 唯一允许的正式变化

控制器只能在原 `budget.lock` 独占锁内完成以下版本化恢复：

- 将当前部分 BUILD 原子改名为 `openmx-overlap-build.interrupted-d52575f446d3c62f0fc93c3c65f3c959.retired`，保留字节与 inode 证据；
- 将当前日志目录原子改名为 `overlap-build.interrupted-d52575f446d3c62f0fc93c3c65f3c959.retired`；
- 从已证明干净的退休树复制新 BUILD，逐相对路径核验文件、目录、符号链接、owner/mode 与内容，且禁止任何普通文件与来源树形成硬链接；
- 将事务提交为 `FAILED_COMMITTED`，原因为 `wsl_shutdown_external_interruption`，`exit_code=null`、`timed_out=false`，并绑定中断报告、证据、部分构建树和日志树；
- 在原 ledger inode 上恰追加一条 `SOURCE_BUILD_WSL_SHUTDOWN_RECOVERY`，补记 `138.401802566` 秒；
- 清空 state/workflow 活动事务，保持非 hard-stop 的 `SOURCES_PREPARED`，新增 `recovered_from_source_build_wsl_shutdown` 标记，同时保留全部旧恢复标记、预算与历史字段；
- 保存 root-private 来源、恢复前 runtime、journal 与目标哈希，并生成不含执行权限的公开只读 snapshot。

恢复动作不得运行 configure、make、OpenMX、材料计算、训练或下载，不得生成新 permit。所有归档、staging、private、snapshot 与临时路径均要求 pristine；任何来源、namespace、runtime、树、日志、进程、产品、预算或锁漂移都应在写入前失败。第一次验证返回后，首个写操作前还必须在同一锁内再次完整复核并比较封印值。进程封印不仅匹配 capability 的 consumer/launcher argv，还遍历 `/proc`，识别包含固定 build/log/transaction/capability 锚点的 wrapper，以及 cwd 或 executable 位于 BUILD/LOGS 的 configure、make/gmake、编译器、链接器、HDF5 测试、MPI wrapper 和 OpenMX 进程；无法读取且不能证明无关的进程身份按 fail-closed 拒绝。

## 持久化与失败语义

恢复 journal 依次记录 `PREPARED`、`INTERRUPTED_ARCHIVED`、`LOGS_ARCHIVED`、`CLEAN_TREE_CLONED`、`LEDGER_COMMITTED`、`TRANSACTION_COMMITTED`、`STATE_COMMITTED`、`WORKFLOW_COMMITTED` 和 `SUCCESS_COMMITTED`。部分树与日志采用同文件系统 rename；新树中的每个普通文件及全部目录执行 `fsync`，父目录随后持久化。ledger 只追加且保持 inode/权限；三个 JSON 使用 O_EXCL 临时文件、原权限与原子 replace。

本控制器为 pristine-only，不提供 resume。任一持久化窗口失败时保留现场并停止；不得覆盖、清理或重放。测试覆盖精确孤立事务、保守计量、历史字段保持、完整 commit、首写边界对 namespace/两棵当前树/两个旧归档/gate/permit/日志/禁用产品/进程/存储的漂移拒绝、全部九个持久化窗口、短写与部分 ledger 追加、复制 fsync 故障、staging 漂移、无硬链接以及零写 preflight。首轮 B01/N01 的回归另覆盖 wrapper、孤立 make/gcc、无关 make、不可读进程 fail-closed、两次 seal 间新增孤立进程零写拒绝、v4 精确直接成员语义，以及 formal roots 全部由临时 fixture 派生；测试应以 root 和 UID1000 分别运行，并证明不读取正式 root-private namespace。

## 门控顺序

冻结 manifest 建立后，独立子 agent 必须对实现与工作包给出严格 `PASS / BLOCKING=0 / NON_BLOCKING=0`，并生成与 controller 严格匹配的 verdict；主端不得自行替代该结论。通过后才允许主端分别执行一次机械 preflight 和一次 recover。恢复执行事实还须接受独立审计；只有该事实审计通过，才能为后续 source_build 建立全新的版本化 consumer、launcher、gate、permit 与执行前审计。

恢复 PASS 仅表示中断事务被保守提交且干净 BUILD 得到重建，不表示 OpenMX 构建通过，也不放行数据、structure 500 smoke、batch、训练或物理验证。
