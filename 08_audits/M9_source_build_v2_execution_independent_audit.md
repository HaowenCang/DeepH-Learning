# M9 source_build v2 独立执行事实审计

审计日期：2026-08-31。结论：FAIL；blocking=1，non_blocking=0。阻塞项：M9-SB-V2-EXEC-B01，冻结OpenMPI版本输出比较与实际绝对路径调用的程序名前缀不一致。唯一授权source_build已经消费并失败，尚未进入configure/make；失败事务、预算记账、双HARD_STOP及历史保留核验通过，但这不构成构建PASS或重试许可。

正式只读采集于2026-08-31T07:33:09.498944+00:00完成。本轮仅新增本报告和postexecution evidence，未修改冻结代码、旧报告、运行态或权限，未调用consumer run、install、permit、recovery或会阻塞获取运行锁的命令。诊断遵循先复现、再单变量区分假设的流程，未进入修复和构建回归阶段。

## 真实执行与失败链

以完整167对象执行前证据SHA `4efc0337731d39412e312b84998096252600bd4f6ce8b7e22976eda5a226747a`为基线，独立核验实际消费的budget argv逐token等于已批准命令：真实UID1000、固定Python3.9.23 `-I -S -B`、root-owned source-build-v2 consumer、唯一operation、source_build、overlap_build及4GiB forecast。未出现结构id、自由命令、smoke/batch或GPU动作。

事务 `38a891fff6fd07675581b891766e02c6` 与capability `284bd6ba705e9b9bd9c4fa0f3c08290b`逐项绑定，child_pid=402。capability为CONSUMED，未消费原文件已缺席，留下单个consumed及单个FAIL launcher receipt。launcher完整argv的canonical SHA `edccba35a2c5521db245cf06989554852c6e50789ed9a9ea05ba2156aac119f9`与事务/唯一ledger事件一致。budget argv、两级isolated/no-site/no-bytecode provenance及stdlib模块内容哈希均匹配；receipt中的两个FrozenSourceLoader模块为冻结m9_overlap_common和m9_openmx_build，未读取bytecode。独立按完整NUL分隔argv检查/proc，未发现原budget或launcher仍运行；不以PID是否存在单独推断存活。

| 终态证据 | 值 |
| --- | --- |
| transaction state | FAILED_COMMITTED |
| prepared/start/end UTC | 07:27:33.075063 / 07:27:43.855704 / 07:27:45.423678，均为2026-08-31 |
| elapsed / child exit / timed_out | 1.567928485秒 / 1 / false |
| reasons | overlap_command_failed |
| consumed SHA | `29533a038e4711706887e44b9d24bde36a34c9bfa274e9317ac5be672937c49e` |
| FAIL launcher receipt SHA | `9a05a92597a30f3cd1e1fd4746cf1bc8e9c531dece812f24ab9f6297a25d12f9` |

两项新capability文件均为uid/gid1000、0600、nlink1，分别4511及5045 bytes。原v2 snapshot、gate和permit及旧v1/consumer/root-only历史身份哈希不变。

launcher receipt保存完整traceback：`m9_overlap_source_launcher.py:313 -> dispatch:287 -> m9_openmx_build.py:574 -> verify_packages:281`，最终ValueError为 `toolchain version mismatch: openmpi_showme_version='/usr/bin/mpicc: Open MPI 4.1.2 (Language: C)'`。按冻结源码，verify_packages位于HDF5配置、日志创建及首次run_logged之前；HDF5 configure的调用在598行，make及OpenMX编译更晚。因此现有证据证明本次失败在configure/make之前，不是HDF5或OpenMX编译器报错。

宿主exec会话退出1是主实施端报告的观测；独立正式事务明确记录child退出1。冻结budget非超时失败分支按代码返回125，该层返回码未单独采集；不将宿主退出码等同budget返回码，也不推定宿主存在throw包装。没有为核对返回码而重跑。

## B01根因与覆盖边界

真实UID1000使用固定构建环境（固定PATH、HOME和C.UTF-8）直接调用冻结`verify_packages(contract)`，稳定复现相同ValueError。只读差分保持执行文件始终为 `/usr/bin/mpicc`，仅改变argv[0]：

| argv[0] | 实际完整输出 |
| --- | --- |
| `/usr/bin/mpicc` | `/usr/bin/mpicc: Open MPI 4.1.2 (Language: C)` |
| `mpicc`，仍显式指定executable=`/usr/bin/mpicc` | `mpicc: Open MPI 4.1.2 (Language: C)` |

合同要求第二行字符串，而冻结driver通过已验证绝对路径调用，实际得到第一行；差异恰为`/usr/bin/`前缀。同一文件解析至 `/usr/bin/opal_wrapper`，SHA `96ab8abeb55cc4fe8bde3d927e98babf7627a6a44b65ce8ce8b4b1f1434c9fcf`。这支持“完整展示字符串比较与argv[0]口径不一致”，不支持“OpenMPI版本已经改变”的判断。

为区分其他假设，独立额外核验8个Ubuntu构建包、6个runtime包均与合同精确版本一致；gcc/gfortran均11.4.0，mpicc/mpif90分别展开到冻结gcc/gfortran，9个工具的绝对路径解析均符合合同。这些补充检查是本轮只读诊断，不表示失败运行曾越过verify_packages执行到后续验证，更不证明尚未运行的动态链接、构建产物或自测通过。

现有`test_m9_overlap_controls.py:152`的版本漂移负例mock了包查询并在gcc=10.5.0处即终止，未覆盖真实绝对路径mpicc输出的正常分支。既有测试及v2实施/安装PASS不能推出该未覆盖路径可构建。该缺口作为同一B01的预防条件记录，不另计重复阻塞项。

## 状态、预算和受控增量

实际namespace为169对象：167基线仅新增上述consumed及FAIL receipt，未删除旧对象。旧对象仅budget_state、workflow、transaction、ledger四个运行态文件和manifests/capability两个父目录发生预期变化；父目录仅时间/大小等允许元数据变化，其余旧成员全部逐项全等。旧source_prepare事务槽已按本次正式动作更新，但其完整原始字节保存在不变的执行前证据中，不能误称当前事务文件仍为旧字节。

| 当前对象 | bytes | SHA-256 |
| --- | --- | --- |
| budget_state | 2201 | `f4b08d2465cddee559664a98fe854289c4ef995ee873a590e6aba24b7f4cec01` |
| workflow | 808 | `60d0c789b3ac093c22245b277e532149ea8275c04781b492940998b02650a0cc` |
| transaction | 2345 | `2920d80e431992cc8a23abe409d2d513b7a567e44651382d09a82b8af085161d` |
| ledger | 65261 | `50334d8f6748816da3910e13fb31e12f5c31dbb9048871b2493a17785802b706` |

ledger前64298 bytes与已封存原字节严格相同，其SHA仍 `0be27e9220b6597d47ee657bbe5169134118340c77a7a0af3722a4eb1ad885c2`；尾部恰新增963 bytes、一个OVERLAP_HARD_STOP事件，绑定本事务、command SHA、失败原因及当前CPU/GPU计数。没有追加成功、恢复或第二次执行事件。

state/workflow均hard_stopped=true且active=null，workflow=HARD_STOP；state除本次CPU增量、hard-stop状态与最后事件时间外，与执行前精确相同。workflow除规定hard-stop字段外也精确相同。CPU原始累计由7212.901214103001增至7214.469142588001秒，按原控制器计入1.567928485秒；原抵扣7200.075310528未变，有效累计14.393832060000932秒、余额7185.606167939999秒。smoke/batch用量不变，GPU compatibility=54.84820560599999秒，training/physical_validation均0。预算余额不是解除硬停的依据。

准备树及失败退休树各5319项receipt与执行前完整哈希相同，分别为 `7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260`、`060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`。HDF5安装prefix、overlap-build日志目录、构建/overlap产物manifest、材料运行root、新staging/tmp均缺席。旧固定8项root-only权限、/root证据、D-017/D-018及全部旧冻结25/16/10和新12来源闭集不变。没有新编译产物、材料结构或训练证据。

## 证据封存与最小后续方案

`M9_source_build_v2_postexecution_evidence.json`保存完整169项receipt、四份当前runtime原始字节（含完整ledger）、原前缀绑定、新增事件、capability/FAIL receipt及完整traceback、两树检查和真实UID诊断输出。文件189674 bytes，SHA `e6f02744745837ae200998cf6d1e7701283721e8ed64c550e98d58b416f5f325`；namespace canonical SHA `417101edb36bd11ad652e18d5fd4f6b86f36844743d330970cc4a2d051497c7c`。落盘后canonical和raw字节哈希复核通过，纳秒整数无浮点损失。诊断前后169对象及两树完整字典全等，正式零写；M9缓存=0。报告Pandoc严格Markdown及git diff --check通过。

最小源码修复应在新的版本化driver中，仅为OpenMPI展示字符串统一已冻结绝对路径与合同程序名的比较口径，并保留精确版本、Language、包版本、wrapper编译器和绝对路径验证；不采用任意前缀忽略、模糊版本匹配或PATH回退。不就地改写原16/25/10/12闭集及v2 snapshot/gate/permit。新版本还需明确其冻结launcher/driver加载链，避免只改项目文件而实际消费旧snapshot。

新回归应先在真实UID1000、同一固定环境和绝对路径调用上复现B01，再证明仅该口径修正后完整只读工具链预检通过；错误版本、错误程序名/路径、额外文本、错误Language和wrapper漂移仍须拒绝。此前尚未执行的configure/make、HDF5自测、两次OpenMX构建、动态链接及产物验收不可省略。

继续推进需要用户明确批准新的修复与恢复工作包：保留本次失败事务/capability/receipt/ledger前缀和全部预算，独立审计并事实核验一次性恢复，再建立新版本消费门控、完成实施与安装审计、使用新operation/nonce与新许可，并获得新的单次source_build授权。当前v2 permit虽保留，但已绑定旧runtime，事务失败且双HARD_STOP，不能重放；本报告不实施或授权上述方案。M9-DATA-B01仍OPEN，后续材料结构、smoke/batch和训练不在当前许可内。
