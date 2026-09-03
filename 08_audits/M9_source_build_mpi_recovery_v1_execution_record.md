# M9 OpenMPI 修复及一次性恢复执行记录

日期：2026-08-31。主agent执行记录，不替代独立审计，不构成编译许可。本记录在恢复程序完成后制作；最终独立结论另行封存。

## 范围与实际结果

根据 [本次用户授权](M9_source_build_mpi_recovery_v1_user_authorization.md)，完成最小版本化修复和真实工具链回归，并在 [独立实施审计](M9_source_build_mpi_recovery_v1_implementation_audit.md) PASS/0/0后执行一次零写preflight和一次recover。二者均退出0；恢复器返回RECOVERY_SUCCESS_COMMITTED，明确source_build_authorized=false。没有重编译、HDF5自测、下载、材料结构、smoke/batch、GPU或训练。

修复并非修改系统软件版本：原build driver完整字节SHA `ab6632784a744fd3f66c95aac30a56767f67af3d8d81147df2fc0d72b67102ec`保持不变，仅新增精确派生，SHA `5652ee35a3595f42bd3050e5825419175fc84526a421a0500559d4146f253d00`。diagnose流程先在真实UID1000复现原始B01，再证明完整verify_packages通过；独立复跑9项适配器及16项恢复测试、补充真实snapshot消费与权威负例通过。

本次实施权威SHA如下：新frozen=`743e3e596d816a7c316a2f7c901b812c650f72bb926aa6698f3c7f72e40818bc`；实施报告=`da6f0acdd95dafcd0bb907464f182f1312412d4fab2b3ef668f67c96dad097ee`；verdict=`347ff79b2485fa1a939983e4edab6ebf533e29a106a447d45b53fa0d436ece45`；授权记录=`5b62617dd9a236c062c1df6a95ccb245484634518d0fbfa029d82f1ca081ac83`。主端读回核对后才执行，不用临时测试PASS对象代替正式权威。

## 精确启动及次数

使用旧替代consumer工作包中唯一Python块的原single-FD loader：旧工作包SHA `dc1d0d992f7e1328f79a4436eb4535b79ba2ab48fcee1b44fa498c31c30e91a2`，提取并去CRLF后的loader SHA `c68e43b5de4fdadb44254fbfdd543f5ba2a29b6e41994021c55a3287b5f7491f`。PowerShell先验证二者，再以root、冻结Python3.9.23 `-I -S -B -c $buildLoader`调用恢复器，不从未验证字节启动。

恢复器路径为 `/mnt/e/Projects/Codex/DeepH/06_reproduction/controllers/m9_source_build_mpi_recovery_v1.py`；loader后的固定参数如下，ACTION仅依次为preflight、recover，各一次：

```text
2df09743fbcab63824cec6d3768e10df3ace7b53af8167080c07a946f2927aa9
ACTION
743e3e596d816a7c316a2f7c901b812c650f72bb926aa6698f3c7f72e40818bc
347ff79b2485fa1a939983e4edab6ebf533e29a106a447d45b53fa0d436ece45
da6f0acdd95dafcd0bb907464f182f1312412d4fab2b3ef668f67c96dad097ee
```

preflight宿主会话77403，只轮询原会话，返回PREFLIGHT_PASS、writes=0、M9_NATIVE_EXIT=0。recover单次调用直接完成，宿主退出0、M9_NATIVE_EXIT=0，输出控制耗时8.527947249000135秒。该耗时单独保存在恢复journal，不新增抵扣、不重置或删除已计量失败CPU用量。没有重复调用恢复器，亦没有为验证幂等性再次调用正式动作。

## 恢复对象、账本与预算

恢复ID=`m9-source-build-mpi-recovery-20260831-01`，固定event UTC=`2026-08-31T08:07:55.031189Z`。journal六阶段为PREPARED、SNAPSHOT_COMMITTED、LEDGER_COMMITTED、STATE_COMMITTED、WORKFLOW_COMMITTED、SUCCESS_COMMITTED。journal为26271 bytes，SHA `31d27bc69268a78f8093492e352d7af759162161df82dfe30e647bfeebad2fe2`。

private归档路径 `/root/deeph-m9-control/source-build-mpi-recovery-v1`，root:root/0700，17个0600文件；新只读修复snapshot路径 `/home/evan-williams/deeph-m9/controls/source-build-mpi-repair-v1`，root:1000/0550，5个0440文件。snapshot manifest SHA `90541ee5d29ca5032868dc6461a6691b1e49b11fc3a4b6f7999427f7448a63e4`与preflight预测一致。实际安装路径的真实UID1000 verify-toolchain已在恢复器内执行并通过；随后独立执行事实审计再次验证通过，见下文封存结论。

恢复后主端读回：

| 对象 | bytes | SHA-256 |
| --- | --- | --- |
| budget_state.json | 2291 | `3523f0d17ccc2168289c5992db691441dd68eb3f09dde3e73de12a4a2ec80560` |
| overlap_workflow_state.json | 905 | `4438c7fce6b5d94268b12d9f2c17876bf6b4f100c22c4610ba215b3c6d1862fa` |
| overlap_transaction.json | 2345 | `2920d80e431992cc8a23abe409d2d513b7a567e44651382d09a82b8af085161d` |
| budget_ledger.jsonl | 66755 | `8dfbb2bb9f23ac9066b457553c2bccfa94a2ab7dde5d66f6315595caaa793421` |

state/workflow均hard_stopped=false，workflow=SOURCES_PREPARED，活动事务为空。原失败事务38a891fff6fd07675581b891766e02c6仍为FAILED_COMMITTED，不将失败改写为成功。ledger原65261 bytes由before归档保留，追加一个1494-byte SOURCE_BUILD_MPI_RECOVERY事件，包含原前缀SHA、父失败事务、授权/审计绑定和完整预算计数；原始字节前缀及逐对象身份的正式结论以独立事实审计为准。

CPU原始overlap_build仍7214.469142588001秒，既有抵扣7200.075310528秒，有效累计14.393832060000932秒、余额7185.606167939999秒。smoke/batch计数0；GPU compatibility仍54.84820560599999秒，training/physical_validation为0。全部CPU/GPU/存储上限和D-018无总墙钟期限策略不变。新增归档和审计文件计入原存储预算。

## 独立验收与后续边界

[独立执行事实报告](M9_source_build_mpi_recovery_v1_execution_independent_audit.md) 已封存为PASS/BLOCKING=0/NON_BLOCKING=0，SHA `590121ae5d98c222a2014d315d8f28f08fad95be05cc4c46065e8bf55bd366d2`；[执行后完整证据](M9_source_build_mpi_recovery_v1_postexecution_evidence.json) SHA `177390748086e678d22c3f24531c5a9b326889e5acb7f3931275262cf27b2ed2`。独立证明193对象的24项新增及允许变化、失败证据身份、账本原前缀和唯一恢复事件、六阶段journal、两树与预算保留，实际固定snapshot的UID1000消费通过；旧v2 verify-execution按预定负例拒绝且零写。主端读回报告及SHA，并在收尾时再次逐项核验193对象全等、旧budget/launcher进程缺席；不以自检替代独立结论，不改写旧v2 FAIL及全部已冻结报告。

本次只恢复至SOURCES_PREPARED，并安装只读修复来源，不是新的编译consumer/launcher。未来应建立新的来源与消费绑定，采用已验证派生字节进行source-only加载，保留原预算、capability、事务及首次写前核验；不把verify-toolchain当构建入口，也不重置已安装的common预算上下文。旧v2 snapshot/gate/permit均保留但不可复用；新入口独立实施和安装审计后，仍需新的单次source_build授权才可执行编译及自测。

正式build、500号结构smoke、450结构batch和训练尚未完成，M9-DATA-B01继续OPEN。主计划、progress_tracker、decisions属于旧冻结来源，本次只更新未冻结的当前状态和README导航，不改写旧来源闭集。
