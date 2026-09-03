# M9 当前执行状态补充记录

更新日期：2026-09-03。记录角色：主 agent 状态汇总，不替代独立审计，不构成新的执行授权。

## 最新事实（2026-09-03）

v4 唯一 `source_build` 的 WSL shutdown 非终态中断已完成独立审计、版本化恢复及恢复后独立事实审计。中断独立审计为 `FAIL/BLOCKING=1/NON_BLOCKING=0`；恢复 v2 首轮实施审计的历史 `FAIL/BLOCKING=2/NON_BLOCKING=1` 保持不改写，修订实现的独立定点复核为 `PASS/BLOCKING=0/NON_BLOCKING=0`。主端核验 frozen SHA `139fb44a695873f1771fa05bd15bc28a9ac348ee2f6fc8a567080c7e920b1e62`、final verdict SHA `9f9331d5ca762f4fb54325a54fe21c9b7d4955d84856598d143e965f2f730fc9`、定点报告 SHA `f39e977092fc5b141507542828fdacb6a045b343a1aebf23a2e95f252fde54f4` 和 single-FD loader SHA `c68e43b5de4fdadb44254fbfdd543f5ba2a29b6e41994021c55a3287b5f7491f` 后，各执行一次零写 preflight 和一次机械 recover。preflight 返回 `PREFLIGHT_PASS/writes=0`；recover 返回 `RECOVERY_SUCCESS_COMMITTED/source_build_authorized=false`，均退出 0，没有重放旧 v4 权限。

恢复后的 transaction `d52575f446d3c62f0fc93c3c65f3c959` 为 `FAILED_COMMITTED`，reason 仅为 `wsl_shutdown_external_interruption`，`exit_code=null`、`timed_out=false`；以 `138.401802566` 秒 `conservative_wall_upper_bound_not_measured_cpu` 补记。state/workflow 均为非 hard-stop、active 为空，workflow 为 `SOURCES_PREPARED`。`overlap_build` 原始累计为 `7645.646848354001` 秒，既有 D-017 抵扣 `7200.075310528` 秒及 GPU/smoke/batch 历史完整保留，没有重置或增加预算。ledger 保留原 68,599-byte/SHA `f3f44ee5169bbeb44d175ff0aa381cda70684ad66f11ce57725c2e774471d4c7` 前缀并恰追加一条恢复事件，现为 70,635 bytes、SHA `24253c63284171f826b6b068053e8bd7fe1fd1a8e2feadbca3f5885f4443ed8b`。

正式执行事实独立审计的事实更正版为 `PASS/BLOCKING=0/NON_BLOCKING=0`。更正版报告 SHA 为 `4d1d8b20327256b807203861f69e850d104858bc86a13e77dde77dff8f2c9e4b`，完整 evidence SHA 为 `b3477ede6590cda56d5cf45bb1a16809e591d6aa5858531807f5cc1513eaca36`；首版审计产物曾手工误转录 consumed capability 摘要，已由原独立审计员从正式对象定点复算并更正为 4,513 bytes、SHA `8d6aff34eec0ee29ce8a7b8e6a8fdf8a76b78ec1fe5a5bd584ee1e2587607204`、state `CONSUMED`，全字段复算未发现第二处错误。独立证据确认恢复后正式 namespace 为 301 项、7,621 项中断 BUILD 与 4 项日志以原身份归档、5,319 项新 BUILD 与 clean tree portable 等价且无文件硬链接、root-private 九阶段 journal 与公开 snapshot 完整、六个最终构建产品继续缺席；真实 UID1000 的旧 v4 `verify-execution` 退出 1 且前后零写。

v5 新版本化 source-build 实施包现已完成主端建设并冻结，包含 consumer、install、launcher、父 namespace 证据、工作包和两组自动测试。冻结清单 schema 为 `m9-source-build-frozen-v5`，共 26 个成员，清单 SHA 为 `124beb3e1734caf7e4660b7377f5b3187b3932b74fa6edfd74acb3d72b2ebe40`；父 namespace 证据 SHA 为 `8a02bc5650cf75e9e86f200204e9fe449c516c5693ff98b526ae8d45243506be`。主端测试为 42/42 consumer 加 15/15 chain，共 57/57 通过；静态复核确认全部 26 个成员散列命中、五个 Python 文件可解析。该结果只是送审前实施证据，不是独立审计结论。

依用户关于套餐额度的暂停要求，当前状态固定为 `PENDING_INDEPENDENT_IMPLEMENTATION_AUDIT`。本轮未启动 v5 独立实现审计，正式 WSL 中不存在 v5 snapshot、gate 或 permit，runtime 四项散列保持恢复完成值，未执行 source_build、结构计算、数据生成或训练。恢复时应从 v5 冻结清单的独立实现审计开始；只有该审计通过后，才可依次进入机械安装、独立安装事实审计、单次 permit、执行前复核及冻结构建。恢复 PASS 不等于 OpenMX 构建 PASS；structure 500 smoke、450 结构 batch、训练与物理验证仍未放行，`M9-DATA-B01` 继续 OPEN。

## 最新事实（2026-09-01 第二次更新）

宿主关机中断恢复 v1 已在门控内执行完毕：中断独立事实审计（INTERRUPTED_NONTERMINAL，BLOCKING=1）与恢复 v1 独立实施审计（PASS/0/0，frozen SHA `3334010925f97486f58b2b3116b52b6b4cc48f34d4c8e0e1ec801de577bbc668`）均已封存。主端核验冻结哈希与 single-FD loader（SHA `c68e43b5de4fdadb44254fbfdd543f5ba2a29b6e41994021c55a3287b5f7491f`）后，各执行一次零写 preflight（PREFLIGHT_PASS，writes=0）与一次 recover（RECOVERY_SUCCESS_COMMITTED，source_build_authorized=false，宿主退出码 0，无重放）。

恢复后主端读回：state/workflow 均 hard_stopped=false、active 事务为 null、stage=SOURCES_PREPARED；事务 `4d7808af7df9418518a59afeba766eb9` 已版本化为 FAILED_COMMITTED（exit_code=null、timed_out=false、reason=host_shutdown_external_interruption）；`overlap_build` 保守补记 292.7759032 秒至 7507.245045788001 秒（标记为墙钟上界非实测 CPU），GPU/smoke/batch/存储/抵扣全部保留。ledger 为 68,599 bytes，SHA `f3f44ee5169bbeb44d175ff0aa381cda70684ad66f11ce57725c2e774471d4c7`，恰追加一条恢复事件。中断树（7,640 项）与三份日志已原子归档为 retired；新工作树（5,319 项）从干净退休树复制且 staging 无残留；HDF5 prefix、OpenMX 产物、材料 run root 继续缺席。详见 [主端执行记录](M9_source_build_host_shutdown_recovery_v1_execution_record.md)。

恢复执行独立事实审计现已封存为 `PASS/BLOCKING=0/NON_BLOCKING=0`。报告 SHA 为 `41fc9940fa8f7ac66b7d8978e429e7b41c3f3f1753e2b2c37c59148f36829c78`，完整证据 SHA 为 `42e05a042ab66c41b31e03ee9a126eec58a1480c382834bd07cd9244f88d602a`。独立核验确认恢复后正式闭集为 244 项、四份 runtime 精确命中目标、账本只有唯一恢复事件、BUILD/CLEAN 为非硬链接干净复制、PRIVATE/journal/snapshot 完整，旧 v3 回放被当前 runtime 与 consumed 状态共同阻断。

**最新执行状态**：v4 实施、安装事实和执行前审计均已 `PASS/0/0`。执行前报告 SHA 为 `b817c7505b5b667dbb990cdfcc5687c87cffd9170f45cef4539096f63b02b727`，完整 274 对象证据 SHA 为 `11c20faeb1069d29804d6ffa5b98705ab6579ced0a62ca7d2b0583eb1c7ecc70`。主端依此启动唯一 v4 source_build 一次；曾确认进入 HDF5 编译和 `make check`。重新进入工作区时原宿主会话句柄缺失且无相关进程，但事务仍为 `d52575f446d3c62f0fc93c3c65f3c959/RUNNING`，state/workflow 仍指向该活动事务，capability 已 CONSUMED、launcher receipt 缺席，ledger/CPU 尚未终态记账，HDF5 check 日志以 `Terminated` 结束。WSL 记录 2026-09-01 22:49 实例 shutdown；Windows 整机关机在次日 00:58，不能混同。当前正在独立审计该非终态中断事实；不得重放 v4 permit/operation/capability 或构建命令。M9-DATA-B01 继续 OPEN。

## 当前结论（2026-09-01 第一次更新，恢复前时点）

2026-09-01更新：宿主会话61603因整机关机消失，正式consumer/launcher不再存活。Windows System事件1074记录2026-08-31 23:23:35+08:00由Explorer代表用户发起关闭电源；HDF5 check日志在23:23:45以`make: ... Terminated`终止，Windows于23:24:41记录内核关闭，9月1日14:02:44重新启动。transaction `4d7808af7df9418518a59afeba766eb9`仍为RUNNING，state/workflow仍指向该活动事务，capability `3cd45d83e11ec6fe0e39725dfe7c6d79`已消费但缺launcher receipt，ledger仍为执行前66755 bytes/SHA `8dfbb2bb9f23ac9066b457553c2bccfa94a2ab7dde5d66f6315595caaa793421`。仅有HDF5配置、编译和未完成的自测日志；HDF5安装prefix、OpenMX构建日志、构建manifest及材料run root均缺席。该事实属于外部非终态中断，不是构建PASS，也不是控制器正常提交的FAIL；旧permit和operation不得重放。现已交独立子agent封存中断事实，再按D-019实施版本化恢复、保守计量与新执行门控。

历史时点：v3[执行前独立复核](M9_source_build_v3_preexecution_audit.md) 已封存PASS/0/0，报告SHA `812294edd8c5f750b578109a693982e8a620a5bee9500dd58a2948d8991ede58`，完整220对象证据SHA `822e0fc61599db3b1b1135b2e384050ca373f0c4c08aea84bee70d7a3cee3b43`。主端核验后执行唯一冻结source_build一次，宿主会话61603，consumer PID294、launcher PID396；当时HDF5配置完成并进入make。该会话后续受上述整机关机中断，不再运行；本段仅保留启动时点事实。

最新事实：v3 [独立安装事实审计](M9_source_build_v3_installation_audit.md) 已封存为PASS/0/0，报告SHA `bd84bbca67c2b0d1cae5865d7369462f2c94d75d659f85f895761997f317f181`，verdict SHA `60b22f6a0a8ba2f756d4829aa461f6d0ffdcf79d681c4d15c22a5c3671abc755`。真实219对象及UID1000固定入口验收通过。主端随后经同一已审核loader执行一次permit签发，宿主会话97351结束为0；返回许可SHA `10d11a4bebc4f8d1595cfdb4bdd21d795848b643db556724ec57598a9d06c856`、source_build_executed=false。当前等待独立执行前复核220对象、实际许可及即时预算，尚未编译；以下“安装审计中/未签发”的表述均为此前时点历史，不覆盖本段最新事实。

v3编译消费链的 [独立实施审计](M9_source_build_v3_implementation_audit.md) 已封存为PASS/0/0，早检B01已独立关闭；报告SHA `0b306f893d87aae84fae4c1d87bf0fb6d0875a32054918092e00ca64e39c87e4`，verdict SHA `ef362e2b58385e84d833f389fc38d701651238af131a69929edc16862e9d908d`。19文件manifest SHA `01a2a8f438d27d582abcf4536775b54605051a3458b06f2bc29c2c56222d4e58`；55项新测试及110/23/13项旧回归独立通过。主端读回权威后，以single-FD loader分别执行一次零写preflight和一次install，均退出0。实际gate SHA `d87228156b3a5c576658eb907f5edc0d6cf0fc89d423df6056f50a71f12f7329`，snapshot SHA `a2eea49fdf6853ccb76233c7bd14b1d08407046daf54d4b625c013f549cf000a`，与预测一致。详见 [主安装记录](M9_source_build_v3_installation_record.md)。当前正在独立安装事实审计，permit尚未签发，尚未重新编译；机械安装成功不能代替实际UID1000独立验收。

用户已新增D-019持续执行授权，见 [原文及边界](M9_standing_execution_authorization_20260831.md) 与 [独立解释复核](M9_standing_execution_authorization_20260831_independent_review.md)。解释复核为PASS/0/0，报告SHA `1a6272daf68fb12968ca92289d60dac913a1550fd2e3f562fc71af80793a3462`；它不是编译实施、安装或执行门控。此前“等待新的人工编译授权”的阻塞已经解除。后续本任务所需的权限、失败恢复与重试由持续授权覆盖，不再重复索取人工批准；技术门控、一次性机器许可、失败停机和证据保留不变。新编译消费链尚未独立验收，不得直接重用旧入口。

M9仍为 `IN_PROGRESS`。用户已另行批准最小版本化修复、真实工具链回归和经独立审计的一次性恢复，见 [本次授权](M9_source_build_mpi_recovery_v1_user_authorization.md)。修复的 [独立实施审计](M9_source_build_mpi_recovery_v1_implementation_audit.md) 和 [独立执行事实审计](M9_source_build_mpi_recovery_v1_execution_independent_audit.md) 均为PASS/BLOCKING=0/NON_BLOCKING=0。后者报告SHA `590121ae5d98c222a2014d315d8f28f08fad95be05cc4c46065e8bf55bd366d2`，[完整193对象执行后证据](M9_source_build_mpi_recovery_v1_postexecution_evidence.json) SHA `177390748086e678d22c3f24531c5a9b326889e5acb7f3931275262cf27b2ed2`。

一次零写preflight和一次recover均退出0，恢复journal为SUCCESS_COMMITTED。当前state/workflow均hard_stopped=false、活动事务为空，workflow为SOURCES_PREPARED；原失败事务仍原位FAILED_COMMITTED。正式193对象恰为原169新增24项，失败transaction、consumed、FAIL receipt、旧permit/gate及两棵源码树原身份不变；实际固定snapshot的真实UID1000完整工具链检查通过。主端在续行收尾时再次逐项核验193对象与独立基线一致，未发现旧budget/launcher仍运行。详见 [恢复主执行记录](M9_source_build_mpi_recovery_v1_execution_record.md)。

该次恢复授权本身不包含重编译；其后的D-019现已覆盖后续执行的人工授权。MPI恢复当时只安装只读修复snapshot，旧v2 verify-execution已由独立审计按预定负例确认拒绝且零写。随后新v3消费链已通过独立实施审计并机械安装；仍需完成独立安装事实验收、签发新单次permit及执行前复核，才执行冻结source_build及构建自测，不再额外申请人工批准。旧permit和一次性恢复均不得重放。M9-DATA-B01仍OPEN，材料结构、smoke/batch、训练和物理验证尚未满足技术进入条件；完整学习路径目标尚未完成。

## 保留的 v2 门控与失败历史

M9仍为 `IN_PROGRESS`。用户已明确批准保留v1和旧凭据权限，建立v2修复门控，经独立实施及安装审计通过后执行一次冻结编译与自测，见 [v2新授权](M9_source_build_v2_user_authorization.md)。[v2实施独立审计](M9_source_build_v2_implementation_audit.md) 及 [独立安装事实审计](M9_source_build_v2_installation_audit.md) 均为PASS/0/0；218项独立测试通过，真实UID1000的已安装verify-ready通过，缺permit时准确拒绝，正式166对象及两树在验证前后保持不变。

随后主端按冻结loader执行一次permit签发，退出码0，实际permit SHA `b00e367be4f06f81a6e8d2e86b72d058c2d6e59e84729637d7f03a8f50594d9e`。[执行前独立复核](M9_source_build_v2_preexecution_audit.md) 为PASS/0/0，报告SHA `ee11a04904675e5dbdd05f00e0fdd82b71edda8fcd430787b92353910a7ec963`，完整167对象基线及真实UID1000 verify-execution均通过。安装记录见 [主安装记录](M9_source_build_v2_installation_record.md)。这些PASS仅证明对应阶段，不代表编译通过。

在上述门控通过后，主端执行唯一冻结命令一次，宿主exec会话34271报告退出1；实际子事务 `38a891fff6fd07675581b891766e02c6` 为source_build/FAILED_COMMITTED，child exit_code=1、timed_out=false，state/workflow均hard_stopped=true且活动事务为空，workflow为HARD_STOP。失败发生于OpenMPI版本字符串严格比较：预期`mpicc: Open MPI 4.1.2 (Language: C)`，实际绝对路径调用返回`/usr/bin/mpicc: Open MPI 4.1.2 (Language: C)`。未进入HDF5配置、make或OpenMX编译；没有材料结构计算或训练。详见 [v2主执行记录](M9_source_build_v2_execution_record.md)。[执行事实独立审计](M9_source_build_v2_execution_independent_audit.md) 最终为FAIL/BLOCKING=1/NON_BLOCKING=0，问题 `M9-SB-V2-EXEC-B01`，报告SHA `2bcf74043ae31d6cbe5e7165be139b0d7056f90a80451fb31cc1d5deed727829`；[执行后完整证据](M9_source_build_v2_postexecution_evidence.json) SHA `e6f02744745837ae200998cf6d1e7701283721e8ed64c550e98d58b416f5f325`。独立确认两棵源码树、旧冻结来源及权限不变，失败记账正确；14包和其余工具链只读核验符合合同，不能据此宣称构建成功。

该次唯一编译授权已经消费，不能重用旧permit。当时按失败规则保留v1/v2安装、全部历史凭据和失败现场，没有就地修改旧冻结控制器、放宽权限或自动清除HARD_STOP。随后依据新的明确授权完成了上述版本化修复与一次性恢复；此历史失败报告仍保持原FAIL结论，不因恢复成功而改写。

此前v1因独立安装审计发现权限阻塞而停止。[v1实施独立审计](M9_source_build_v1_implementation_audit.md) 为 `PASS/BLOCKING=0/NON_BLOCKING=0`，178项独立回归通过；零写preflight通过后，snapshot/readiness机械安装成功，见 [v1主端安装记录](M9_source_build_v1_installation_record.md)。但真实UID1000安装后 `verify-ready` 不能读取保留为root:root/0600的历史凭据 `manifests/overlap_source_control_recovery.test-artifact.retired.json`；实施测试的临时权限布局未覆盖该情况。因此，机械安装成功不能视为安装事实通过。

v1阶段未签发执行许可，也未启动编译、材料结构计算或训练。[v1独立安装事实审计](M9_source_build_v1_installation_audit.md) 最终为 `FAIL/BLOCKING=1/NON_BLOCKING=0`，阻塞编号 `M9-SB-V1-INSTALL-B01`，报告SHA `0a6b4ba15309eb8c44707ddf33840f052dca2888fd204502d851e171c77fb86f`。固定不可读集合共8项；v1的`verify-ready`、`verify-execution`均在首个历史文件读取处退出1，后者尚未到达缺permit检查，不将其误记为许可拒绝测试通过。

[完整v1安装后证据](M9_source_build_v1_installation_postexecution_evidence.json) SHA `0e125e288af8299fb3cf6447ac379e3b946bd042ddd705537dcd9cff11300f00`，记录147项正式receipt、原始runtime字节和真实UID1000失败输出。独立审计确认验证前后147对象、两棵源码树及预算历史不变；v1 permit缺席。已安装v1、已冻结报告和manifest、原历史凭据均保留，不修改旧权限、不就地修补v1、不自动重试。v2依据新批准采用root实际内容核验与封存receipt，UID1000验证固定8项可见metadata，其余公共文件仍真实读取；实现完成不等于独立安装事实通过。

D-018 无总墙钟期限策略已经生效，CPU、GPU、存储预算和全部历史用量、失败及恢复证据继续保留。Python 3.9 失败恢复和版本化 consumer 安装链已通过独立审计。此前唯一一次 `source_prepare` 已返回退出码0，事务 `SUCCESS_COMMITTED`，workflow `SOURCES_PREPARED`；执行后独立事实审计为 `PASS/BLOCKING=0/NON_BLOCKING=0`。该旧授权执行已经完成，不能复用；新编译授权不更改此前任何运行事实。

前置 [安装执行事实审计](M9_py39_consumer_gate_completion_execution_independent_audit.md) SHA-256 为 `798ada7ed0c8835cc56b28d168188d61688e21d2ecdfacfb4d56ac6da660bcdc`。[单次授权签发与执行前独立审计](M9_source_prepare_py39_fresh_authorization_independent_audit.md) SHA-256 为 `2bc82001d681c8ac6ab0afd69ffe39d3d856381d264c2954c86b8dd0be8ebbde`。[本次主执行记录](M9_source_prepare_py39_fresh_execution_record.md) 记录动作与参数，不自证执行后审计通过。

最终 [单次源码准备独立执行事实审计](M9_source_prepare_py39_fresh_execution_independent_audit.md) SHA-256 为 `89418b784d800e25d895b05360ecd086be217e5a820dcdca526ef0205b1cde71`；[执行后独立证据](M9_source_prepare_py39_fresh_postexecution_evidence.json) SHA-256 为 `ee4d593ddb277a252cbd3a90b0e59f94b96fc1d614e2544dde22bb5b217f8455`。主执行记录中“待独立审计”保留其审计前时间点含义，当前结论以本段最终独立报告为准。

## 源码准备历史与尚未完成事项

缺失的 readiness consumer gate 已安装，其 SHA-256 为 `520a8cffcab9c91400647e486de796853d8a00073892e3a4b0472cafbf9dd5c9`。独立审计确认正式变化仅为该 gate 新增和 manifests 父目录 mtime/ctime 更新。真实 UID/GID1000 进程使用冻结 Python 3.9.23 的 `-I -S -B` 选项，从已安装 root-owned snapshot 加载实际 adapter，在原 budget lock 内通过 `verify_consumer_gate()`；没有读取 root-private 文件，验证前后正式对象不变。

该安装审计之后，source_prepare单次授权对象已签发并独立验收，SHA-256 为 `62bf44207a3f3338fce3f8b4476a0b37be97f7587d2f07148aa3978b9014b4ab`。主 agent 当时以真实 UID1000 执行了一次冻结命令，transaction id 为 `dc75dda112af553377a697f629801782`，capability id 为 `f58c6a5904391d5659201dabf22a787b`，launcher receipt 为 `PASS`。当次执行后的state和workflow均非hard-stop，active transaction均为null，workflow为`SOURCES_PREPARED`；这是本次source_build之前的历史快照。该次source_prepare未执行source build、smoke、batch、GPU、Hamiltonian/SCF或其他DFT标签生成。authorization保留为历史证据，不能再次消费；当前运行态以本记录开头的MPI恢复独立事实结论为准。

独立审计将实际准备树与三个冻结归档及官方补丁、makefile规则在内存中逐成员重算：5179文件、140目录、619112473 apparent bytes全部一致，official manifest覆盖1577条来源路径和92条补丁写入路径。没有编译产物、HDF5安装prefix、结构run root或活动staging。旧失败退休树也通过原inventory全量复核。

M9-01—03 已通过。M9-04 的官方 graphene 发布数据下载、安全解包和 450 结构合同已完成，但 overlap 缺失问题 `M9-DATA-B01` 仍为 `OPEN`；正式训练及物理验证尚不能启动。材料建设阶段 M3—M7 完成不等于 M9 复现实验完成。

## 预算与历史证据

无时限仅指取消总墙钟截止期限，不取消各操作的 CPU/GPU 计量、子预算超时、存储预测或失败停机。历史起点 `2026-08-11T14:50:05.7533015Z` 和历史截止时间 `2026-08-18T14:50:05.7533015Z` 继续作为历史字段保留。

| 预算 | 保持不变的上限 |
| --- | --- |
| overlap CPU build / smoke / batch | 7200 / 1800 / 21600 秒 |
| GPU 总额 | 86400 秒；compatibility / training / physical_validation 为 7200 / 57600 / 21600 秒 |
| 总存储 | 100 GiB；按合同分别核验 apparent、allocated、VHDX 增量 |
| overlap 存储增量 / 项目审计子限额 | 10 GiB / 1 GiB |

此前source_prepare由原预算控制器记录CPU增量 `6.231787957` 秒，原始 `overlap_build` 从 `7206.669426146001` 增至 `7212.901214103001` 秒。source_build前置失败继续计入 `1.567928485` 秒，原始累计现为 `7214.469142588001` 秒；此前已批准的非计算apt超时抵扣仍为 `7200.075310528` 秒，未新增抵扣或重置原始用量。按既有公式，有效累计约14.393832060秒，余额约7185.606167940秒。GPU compatibility历史用量仍为 `54.84820560599999` 秒，training和physical_validation均为0；smoke和batch CPU均为0。MPI恢复精确保留这些计数和预算字段，控制耗时8.527947249000135秒单独存于journal，不新增抵扣。机器HARD_STOP已按批准解除，但新消费门控及单次授权仍未建立，余额不构成重试许可。

source_prepare签发前ledger为61826 bytes、SHA-256 `5253620510f84d1987874c5fa571f6016cedfbdabc6e80a4b126e724839b1ea9`，执行后为64298 bytes、SHA-256 `0be27e9220b6597d47ee657bbe5169134118340c77a7a0af3722a4eb1ad885c2`；对应独立审计确认仅新增一个2472-byte `OVERLAP_COMMAND`，原前缀不变。本次source_build失败后ledger为65261 bytes，SHA `50334d8f6748816da3910e13fb31e12f5c31dbb9048871b2493a17785802b706`，追加一个963-byte `OVERLAP_HARD_STOP`；独立审计已确认64298-byte原前缀全等，无额外成功、恢复或重复执行事件。当前事务槽已更新为本次失败事务，旧成功事务原字节在167对象执行前基线中保留；更早失败、恢复transaction、旧gate、retired对象及snapshot也继续保留。

随后MPI恢复在原ledger inode上追加唯一1494-byte `SOURCE_BUILD_MPI_RECOVERY`，事件UTC为`2026-08-31T08:07:55.031189Z`；当前ledger66755 bytes、SHA `8dfbb2bb9f23ac9066b457553c2bccfa94a2ab7dde5d66f6315595caaa793421`。独立审计确认原65261-byte前缀严格不变，事件绑定父失败事务、授权/审计和全部用量，source_build_authorized=false。新private归档保存完整失败前态；当前失败事务文件本身仍原inode、原字节。

## 后续顺序与授权边界

1. 源码准备和独立事实审计已经完成。保留全部证据，不重试旧授权。已经准备的对象为 OpenMX 3.9、官方 3.9.9 补丁、HDF5 1.12.1 源码、冻结 makefile 和来源清单，不是已编译的运行环境。
2. v2前置失败之后，最小MPI版本化修复、真实工具链回归、一次性恢复及独立实施/执行事实审计已经完成。保留全部旧冻结闭集、失败证据和只读修复snapshot；不重放恢复或旧permit。恢复完成不等于构建通过。
3. 依据D-019持续授权，建立并独立验收绑定派生driver及193对象恢复基线的新编译consumer/launcher，签发新的单次许可，才可执行冻结source_build及构建自测。只有编译与独立事实审计通过，并满足各后续门控和预算条件，才进入500号结构smoke、450结构成本与存储预测、逐结构overlap生成和验证。人工授权已覆盖这些动作；技术进入条件不能因此省略。
4. 完成 overlap 合同并由独立子 agent 关闭 `M9-DATA-B01` 后，才按冻结 M9 计划推进训练、物理验收和最终独立审计。Hamiltonian、SCF、其他 DFT 标签生成及超预算动作仍不在授权范围内。

## 与冻结计划文件的关系

`00_scope/master_execution_plan.md`、`08_audits/progress_tracker.md` 和 `decisions.md` 是当前25-file consumer frozen manifest的成员。为维持已审计安装入口和来源绑定，本轮不改写这些文件；其中较早的“等待复核/安装”文字属于冻结时点的状态，不能覆盖本记录引用的新独立事实结论。持续授权以 [D-019追加决策](../00_scope/D019_standing_execution_authorization.md) 登记，替代重复人工批准要求，但不自动改变D-013/D-014/D-017/D-018的数值与技术合同或机器门控。后续如需更新冻结成员，应先遵循既有来源变更与门控重建规则。
