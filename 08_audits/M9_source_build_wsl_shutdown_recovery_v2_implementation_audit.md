# M9 source_build WSL shutdown recovery v2 独立实施审计

日期：2026-09-02。审计角色：独立子 agent。最终判定为 **FAIL / BLOCKING=2 / NON_BLOCKING=1**。本审计未调用正式 `preflight`、`recover`、permit、capability、launcher 或构建入口，也未修改正式 WSL runtime、树、日志、gate 或 permit。

## 冻结来源与只读现场

送审控制器、测试、工作包和九项 frozen manifest 的实际 SHA-256 分别为 `e700b622c1cd36f14bb9ec75d4fbae3639117407f17027c9f90cfb7d351ef0dc`、`a150187a92f58e7ef465a04be5c4382af2e502ad9d7724e3be4ed0a63680b015`、`5523669ac1b36d973201c04e61d26272d3f950b42e0317221639b411b765dc8b` 和 `c0095d8ec211d66c9bb46e5a518892c365252cd97df139bb7008a225389d00a0`，均与送审值一致。manifest schema 和九项直接路径闭集正确，九项直接成员当前字节均匹配其声明摘要。

采用固定 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B`，以 root 对控制器的 `verify_current` 做两次连续、非 action 的只读等价核验。两次 seal 相等：正式 namespace 为 275 项、canonical SHA-256 `8f904289db590a6bf68d7d62f0e13cda0893cec30321274d67559261758402b9`；BUILD 为 7,621 项、`25fa00697f192967f8adcc0656eea976eeb9839390a78757a04d00ac66796dc0`；日志为 4 项、`f1d69a2016dc0ae5df54519d4155a9b0317bcb7c4edf55cdea85c43d9a4b1db3`；clean 为 5,319 项、`060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`；旧 BUILD 归档为 7,640 项、`82bc6705ef8a507d2580630592f4903726622768aebb5bd7b1d22d93afa12515`；旧日志归档为 4 项、`5ea65a500eaadc665b4d282ce8b8c55019629b722020b7baa73259c9f862d4de`。capability SHA-256 为 `8d6aff34eec0ee29ce8a7b8e6a8fdf8a76b78ec1fe5a5bd584ee1e2587607204`，launcher receipt 缺席；v4 gate 与 permit 分别匹配 `dcd0a0ed3307add49df5b7586ba0bf01b2fc55b0469a42067893e563ba2ff3c1` 和 `c3aae6ff0c5aaffb3d5a711b48e7dc505061959eb144509995f8e9890f5853d4`。

四份 runtime 原字节 SHA-256 分别为 state `b067c25dd9144fb7f40994b196b60a1f0cd4a22c4d72d558388f54ce5aa1259e`、workflow `deb554bc2df789ae56341f44045f861d026f1937375a6251ccc8871b8e6f1fe6`、transaction `d953bfb4c21e9dffdf945f7b5a7a610321d19a1a659e5f6d908185fab5f555db` 和 ledger `f3f44ee5169bbeb44d175ff0aa381cda70684ad66f11ce57725c2e774471d4c7`。1 GiB forecast 的即时 `violations=[]`。目标计算将 `overlap_build` 从 `7507.245045788001` 精确增加到 `7645.646848354001`，保留抵扣和 GPU，并生成 `source_build_authorized=false` 的单条 2,036-byte ledger 事件。独立的较宽 `/proc` 只读扫描在采集时未发现 wrapper、configure、make、编译器、MPI、HDF5 或 OpenMX 构建进程。该现场事实不消除下述首写竞态缺口。

## 阻塞发现

### M9-WSL-REC-V2-B01：首写前进程封印不能排除孤立构建子进程

`process_alive()` 只把 capability 中 `budget_argv` 与 `launcher_argv` 编码成两个完整 NUL cmdline，并仅在 `/proc/*/cmdline` 与二者逐字相等时返回 true。wrapper、configure、`make`、gcc/gfortran、链接器、HDF5 测试、MPI wrapper 或 OpenMX 子进程一旦脱离原父进程，其 cmdline 不等于这两个数组，即使仍在写 BUILD，也会被视为“无进程”。读取 cmdline 的 `PermissionError` 同样被静默忽略。

固定解释器负例将临时 `/proc` 夹具设为 `/usr/bin/make\0-j2\0`，得到 `orphan_make_detected=False`；将同一夹具改为 capability 的精确 budget argv 后得到 `exact_budget_detected=True`。因此，工作包关于“任何进程漂移均在写入前失败”的要求没有实现。`commit()` 虽在首写前执行第二次完整 `verify_current()` 并比较 seal，但两次均调用同一不充分的检测器，仍可能在活跃子进程继续修改 BUILD 时开始 rename。

最小验收条件是：在同一预算锁内的初次验证和首写前复核均 fail-closed 枚举与该 BUILD/LOGS/工具链相关的全部存活进程，不只匹配两个父级 argv；至少覆盖 wrapper、configure、make/gmake、编译器/链接器、HDF5 测试、MPI wrapper 和 OpenMX，并对不能证明无关的不可读 cmdline 拒绝。测试应包含孤立子进程正例、无关进程负例，以及两次 seal 之间出现孤立子进程时的零写拒绝。

### M9-WSL-REC-V2-B02：v4 frozen authority 只展开一层，并未递归封印全部嵌套来源

`authority()` 读取 v4 manifest 的直接成员；若直接成员本身含 `files`，则收集其成员并 pin 一次，但不会继续解析新发现的 manifest。独立 trace 将实际 `pinned()` 调用集与 v4 manifest 的传递图比较，确认有七个可达成员未被 authority 读取或摘要核验：

- `06_reproduction/manifests/m9_overlap_frozen_hashes.json`
- `08_audits/M9_overlap_only_openmx_work_package.md`
- `08_audits/M9_source_control_recovery_resume_execution_independent_audit.md`
- `08_audits/M9_unlimited_wall_clock_authorization.md`
- `08_audits/M9_unlimited_wall_clock_migration_independent_audit.md`
- `08_audits/M9_unlimited_wall_clock_migration_targeted_reaudit.md`
- `08_audits/M9_unlimited_wall_clock_migration_work_package.md`

传递图含 98 个 v4 后代成员；上述七项均未出现在实际 pin trace 中。现有 authority 测试只断言函数成功返回，没有断言 pin 集等于传递闭集，也没有二层叶节点漂移负例。进一步扫描显示，更深历史 manifest 还对若干后来版本化更新过的同一路径声明不同摘要；因此不能只增加一个无语义区分的递归循环。最小验收条件是先定义可满足的版本化传递闭集：历史版本应当使用唯一的不可变路径或快照，随后对每个 manifest 节点和叶节点单 FD pin，带 visited/cycle 防护与 path-to-digest 冲突拒绝，并测试二层叶 drift、摘要冲突和循环/重复引用。当前实现不符合工作包“递归核验全部嵌套来源”的明示声明。

## 非阻塞发现

### M9-WSL-REC-V2-N01：隔离测试读取正式 root-private namespace

测试 Fixture patch 了 `ROOT` 和 `PRIVATE`，但生产 `formal_namespace()` 的第三个根写死为 `/root/deeph-m9-control`。因此测试并非完全临时隔离，而会读取正式 root-private 树。root 身份运行时 17/17 通过；同一固定解释器以默认 UID1000 运行时 rc=1，17 个 test method 中产生 42 个 error case，首因均为无法读取 `/root/deeph-m9-control`。末尾 `test_process_detection_uses_exact_original_argv` 还只把 `/proc` mock 为空，没有验证其名称所称的精确匹配或孤立子进程拒绝。

该问题本身没有证明正式恢复会错误写入，故计为 non-blocking；但它削弱测试的可复现性和“隔离测试”声明。应将 formal roots 由可 patch 的 root/private 参数派生，使 Fixture 全部落在临时目录，并断言测试前后没有读取或改变正式 namespace。

## 其余核验与结论边界

以 root 和固定解释器运行送审恢复测试为 17/17 OK；必要旧回归 `test_m9_source_build_v4_consumer.py` 为 42/42 OK，`test_m9_source_build_v4_chain.py` 为 15/15 OK。控制器的 138.401802566 秒保守计费、FAILED_COMMITTED/SOURCES_PREPARED 目标、原 inode ledger 单行追加、原子 rename、普通文件独立复制、普通文件和目录 fsync、九阶段 journal、pristine-only/no-resume、禁止新 permit/build，以及主要故障窗口的保留语义，在静态审阅与现有隔离故障测试中未发现其他矛盾。项目 `06_reproduction` 下未发现 `__pycache__` 或 `.pyc`。

由于 B01 允许首写前漏检仍可修改 BUILD 的进程，B02 又使来源 authority 小于声明的传递闭集，当前控制器不得执行正式 preflight 或 recover。判定为 **FAIL / BLOCKING=2 / NON_BLOCKING=1**；现有 runtime 与全部失败证据应保持原样，修复后重新冻结并接受独立定点复核。
