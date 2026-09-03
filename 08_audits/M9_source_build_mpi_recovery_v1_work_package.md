# M9 OpenMPI 前缀修复与一次性恢复工作包

日期：2026-08-31。实施工作包，独立审计前不自证PASS。授权见同目录 `M9_source_build_mpi_recovery_v1_user_authorization.md`，仅修复、真实只读回归和一次性恢复；不授权再次编译。

## 唯一父态及问题范围

失败父事务为 `38a891fff6fd07675581b891766e02c6`、source_build/FAILED_COMMITTED，capability为 `284bd6ba705e9b9bd9c4fa0f3c08290b`。独立报告SHA `2bcf74043ae31d6cbe5e7165be139b0d7056f90a80451fb31cc1d5deed727829`，169对象及四份原始runtime证据SHA `e6f02744745837ae200998cf6d1e7701283721e8ed64c550e98d58b416f5f325`，namespace canonical `417101edb36bd11ad652e18d5fd4f6b86f36844743d330970cc4a2d051497c7c`。源码准备树和失败退休树各5319项，canonical分别为 `7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260` 和 `060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`。

当前state/workflow均HARD_STOP、活动事务为空；ledger65261 bytes，SHA `50334d8f6748816da3910e13fb31e12f5c31dbb9048871b2493a17785802b706`。失败发生于HDF5 configure之前，不能省略尚未执行的编译、自测和动态链接验收。问题仅为合同预期`mpicc:`而固定绝对路径调用输出`/usr/bin/mpicc:`；14包、gcc/gfortran、两个wrapper和9工具路径的只读核验通过。

## 最小修复及实际消费边界

新增 `m9_openmx_mpi_repair_v1.py` 作为明确只读入口，命令仅接受 `verify-toolchain`；拒绝build、run、permit或恢复。用真实UID1000、冻结Python3.9.23 `-I -S -B`运行。其派生输入是原build driver完整字节SHA `ab6632784a744fd3f66c95aac30a56767f67af3d8d81147df2fc0d72b67102ec`，精确一次替换 `if output != toolchain[name]:` 所在行。仅在name为openmpi_showme_version、命令路径恰`/usr/bin/mpicc`且原合同字符串完全匹配时，expected增加固定`/usr/bin/`。其他分支和整份driver其余字节不变，可逆替换全等；派生SHA `5652ee35a3595f42bd3050e5825419175fc84526a421a0500559d4146f253d00`。

不改变执行命令、不回退PATH、不容忍任意前缀、不模糊版本。仍严格拒绝错误版本、Language、程序名、额外文本、绝对路径及wrapper漂移。实际调用的是派生driver的完整verify_packages，不用独立写出的简化版本检查替代；其旧build_sources保留原capability守卫，只读入口从不安装capability或调用构建。

新只读snapshot固定为 `/home/evan-williams/deeph-m9/controls/source-build-mpi-repair-v1`，root:1000/0550；四份0440单链接普通文件为适配器、原build driver、原common、原合同，再加0440 snapshot_manifest，共5文件。实际安装后UID1000读取本snapshot内的固定来源，再进行同一精确派生及完整只读工具链检查；目录、文件元数据和成员闭集均验证。不是从可写项目副本冒充实际安装消费。

此snapshot只提供经验证的修复来源，不是新的编译consumer、launcher或许可。未来编译链应在新的独立工作包中让source-only loader消费本派生SHA及其原始/派生来源记录，保留capability、真实预算父argv及事务检查；不能调用仍加载旧driver的v2链。新consumer/launcher尚未实现，不把本次恢复称为build-ready。正式重新编译前仍需新的单次执行授权。

## 新冻结闭集和独立权威

新manifest严格9文件：恢复器、适配器、两份新测试、工作包、授权、v2执行后完整baseline、v2失败独立报告、原v2 consumer。schema=`m9-mpi-recovery-frozen-v1`，只含schema/files。原v2 consumer按固定SHA加载，继续核验旧12/25/16/10闭集及成员，不修改或覆盖旧文件；其receipt工具按旧绑定读入，root全量读取包括8项root-only及/root证据，不做metadata-only替代。

独立实施verdict恰7字段：schema=`m9-mpi-recovery-verdict-v1`、status=PASS、blocking/non_blocking为真实整数0、frozen_sha256、report_path、report_sha256。报告和verdict各自作为启动参数固定SHA；一经引用不得改写。未经PASS/0/0不得正式preflight或recover。

恢复器只接受self_sha、preflight或recover、frozen_sha、verdict_sha、report_sha五个参数；root、固定解释器、隔离/no-site/no-bytecode、原budget.lock O_NOFOLLOW和LOCK_NB、原dev/ino/权限都应通过。调用继续使用既有single-FD loader：从旧 `M9_source_prepare_py39_consumer_replacement_work_package.md` 提取唯一Python块，去CRLF后的精确SHA为 `c68e43b5de4fdadb44254fbfdd543f5ba2a29b6e41994021c55a3287b5f7491f`，旧工作包SHA `dc1d0d992f7e1328f79a4436eb4535b79ba2ab48fcee1b44fa498c31c30e91a2`。loader稳定读同一fd、固定恢复器SHA后才执行，不用另写临时bootstrap。

## 一次性恢复及允许写集合

采用pristine-only，不提供resume。新private目录、snapshot、snapshot staging、state/workflow固定tmp任一预存即零写拒绝。旧169项receipt、四份raw runtime、两树、已缺席的产物/临时路径、实际历史完整argv不存活、原CPU/GPU/存储检查全部通过后，且在同一原锁内重验所有冻结输入，才允许首次mkdir。预算函数以实际hard-stopped state及1MiB恢复存储预测调用，只允许唯一拒绝项ledger_already_hard_stopped；不能过滤其他超限。

private目录为 `/root/deeph-m9-control/source-build-mpi-recovery-v1`，root:root/0700。保存9冻结来源、新manifest、实施报告/verdict共12文件，加四份before-runtime和journal，共17文件，root:root/0600。连同public snapshot，预计169对象新增24对象至193。旧对象仅ledger、state、workflow及三个父目录按允许规则变化；失败transaction文件、consumed、FAIL receipt、原gate/permit、所有旧snapshot及两树原位原身份保留。

新目录创建仅允许指定父目录nlink+1；文件新增/替换仅允许父目录时间和大小变化。每一步写前及写后检查完整闭集及原锁身份，不能同字节换inode后重新采样接受。替换采用O_EXCL/O_NOFOLLOW固定tmp、完整短写循环、fsync和原子rename，并将实际fd身份与新目标receipt绑定；残留tmp不清理。ledger仅对已存在且完整receipt绑定的原inode追加固定事件，不创建新ledger、不截断、不重建、不补齐未知尾部。

恢复ID=`m9-source-build-mpi-recovery-20260831-01`。在首次写前生成一次UTC、恢复event及目标bytes，写入journal后不重新生成。phase顺序为PREPARED、SNAPSHOT_COMMITTED、LEDGER_COMMITTED、STATE_COMMITTED、WORKFLOW_COMMITTED、SUCCESS_COMMITTED，每阶段journal持久保存四份post-runtime receipt。ledger追加一个SOURCE_BUILD_MPI_RECOVERY，绑定失败事务、原ledger前缀、授权/审计和全部预算用量，明确source_build_authorized=false。

目标state由失败原始对象复制，只改hard_stopped=false、last_event_utc并新增recovered_from_source_build_mpi_failure。workflow只改hard_stopped=false、stage=SOURCES_PREPARED并新增同名恢复标记；原hard_stop_reason/utc作为历史保留。所有CPU/GPU计数、credits、history、原预算策略和限额精确不变。失败事务仍FAILED_COMMITTED，不把失败事务改成成功事务。

任何异常立即退出，保留已写证据、partial ledger和tmp，不自动回滚、重试、清理或续提。即使故障发生在workflow已写而最终journal未提交的窗口，也不能宣称恢复成功：没有新的编译许可，旧consumer因当前FAILED_COMMITTED及runtime变化拒绝。下一次尝试遇到预存private/snapshot会零写拒绝，需新的独立复核及授权；不能从state布尔值推定正式就绪。

## 测试、门控及预算

diagnose回归先运行未修复的真实绝对路径调用，捕获同一B01；再运行派生driver完整验证并通过。测试覆盖仅verify_packages AST变化、可逆字节、所有MPI输出负例、路径/wrapper漂移、链接/多链接/来源漂移、无capability拒绝构建和只读CLI拒绝写动作。恢复测试使用临时隔离fixture，不写正式运行态；覆盖白名单目标、失败tx身份保留、phase及预算、29个文件持久窗口、目录/密封/追加/实际安装校验故障、短写、部分事件、残留tmp、同字节新inode、锁替换、额外对象、未知ledger尾部和终态漂移；成功重放仅零写拒绝。

复现命令：

```bash
/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B /mnt/e/Projects/Codex/DeepH/06_reproduction/tests/test_m9_openmx_mpi_repair_v1.py -v
# 上一条以真实UID1000运行；下一条以root运行隔离权限fixture。
/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B /mnt/e/Projects/Codex/DeepH/06_reproduction/tests/test_m9_source_build_mpi_recovery_v1.py -v
```

无需新Python依赖或软件安装。原CPU build/smoke/batch上限7200/1800/21600秒，原始build累计7214.469142588001秒、既有抵扣7200.075310528秒不变；GPU历史compatibility54.84820560599999秒、training/physical_validation为0。无总墙钟期限不取消子预算。新审计和snapshot计入原存储；恢复控制耗时单独保存在journal，不新增CPU抵扣或重置已计量失败用量。

实施独立审计PASS后，主端执行一次零写preflight，再执行一次recover。随后独立审计真实193对象增量、所有原字节/权限、精确目标和唯一ledger事件、两树、真实已安装UID1000只读消费、无新编译permit和无运行产物，才可报告恢复完成。M9-DATA-B01继续OPEN；下一阶段新消费链和编译仍保持门控。
