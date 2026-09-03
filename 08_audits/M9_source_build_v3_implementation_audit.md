# M9 source_build v3 独立实施审计

日期：2026-08-31。结论：PASS；blocking=0，non_blocking=0，均为整数。早检B01经定点复核关闭。本结论仅覆盖下列冻结实施，不是实际安装、执行许可或构建成功的事实验收。

## 冻结对象与授权

独立读取完整工作包、consumer、installer、launcher、两份新测试及相关旧预算、common和driver路径。新manifest严格19文件，所有成员及递归引用的旧9/12/10/25/16文件闭集逐字核验通过；旧文件未修改。D-019及其独立解释报告提供持续人工授权，但不替代独立门控和新的单次机器permit/capability，也不自动调整数值预算或物理范围。

| 对象 | SHA-256 |
| --- | --- |
| v3 frozen manifest | `01a2a8f438d27d582abcf4536775b54605051a3458b06f2bc29c2c56222d4e58` |
| consumer | `0e81f6748bfaf26edb752293b781a0992fe7e657b54ac74856fc4e0f28c06a17` |
| installer | `98ad46b52931c658f5627912cd724932a4ace009cede006de15b4d96d61104e9` |
| launcher | `6c6f5e222463dbca65a6d747ba1f766630dd2f698ba74f2e207f5ea8566fede6` |
| 工作包 | `0f91b2a23676a9e418d02717cbc1a6226840a588ea6af032f920ff0211c9e635` |

## B01关闭及执行链判断

早检已用临时真实夹具复现：安装事实文件漂移使回执校验抛出SystemExit，原budget的except Exception无法捕获，事后失败提交和CPU增量落盘因此可能被跳过。修复仅在新validate_launcher_receipt边界将SystemExit转换为ValueError；前置门控仍按原方式零写拒绝，没有改写旧预算实现。

独立复跑实际派生budget.command_overlap_run的事后回归：模拟子进程退出0后改变临时安装事实文件，真实验证器拒绝，原生hard_stop_both返回125并提交FAILED_COMMITTED；CPU由14增加至16秒，GPU原值不变，state/workflow均hard_stopped且活动事务清空，原ledger前缀保留并恰追加一个OVERLAP_HARD_STOP。子进程替身只调用一次。该测试隔离时间、进程及资源测量，不模拟hard_stop_both、记账提交或异常转换，因此支持关闭B01，但不是正式计算实验。

预算源仍由原SHA `a94902a942f98217171be5d9967f469a4dd4563c80e6e6ef3d68e6cede71168d`进行唯一scope/action两字面量派生，得到 `94050d73f498b84ab0054f64f1b04ea8667067f86a54ed3f352e6b926a9e691e`。运行时仅接入新launcher常量、新回执验证器和既有首写前门控守卫；原CPU/GPU/存储计量、事务、超时进程组停止及失败分支保留。

唯一consumer argv约束真实UID1000、固定Python3.9.23及-I/-S/-B、operation `7bc4139f7a9c4b768d3f9ec68c1d1048`、source_build、无GPU/structure_id和4GiB forecast。新launcher验证root-owned snapshot与静态permit权威，再核验真实父/子argv和BOUND capability；common从实际CONSUMED文件及RUNNING事务验证PID/事务绑定。driver通过已冻结repair.derive精确派生为 `5652ee35a3595f42bd3050e5825419175fc84526a421a0500559d4146f253d00`，common对象及已安装上下文没有被只读工具链函数重置。父回执分别核验原driver SHA、实际派生SHA、来源闭集、隔离启动、依赖路径加入方式及v3权威绑定。

首次预算写入仍在原budget.lock内重新验证完整父态和两树；恢复后的FAILED_COMMITTED事务被明确接受为历史终态，同时要求恢复标记、SOURCES_PREPARED、非hard-stop及无活动事务。运行中和事后只检查静态权威，不误要求已变化的runtime仍等于执行前基线。旧操作、旧permit及完成/失败后重放不能通过执行前基线核验。

## 安装与许可边界

installer在首次写入前核验独立权威、完整root历史、两树和原预算即时预测；仅允许pristine新snapshot/staging/gate/permit命名空间。24文件snapshot要求root:1000/0440、单链接，目录0550；安装新增26对象至219，permit另新增1对象至220。除规定controls/manifests父目录变化，旧193对象不应改变。中断保留staging并拒绝重放，不提供自动续提或清理。

安装只产生readiness，不签发执行permit；permit需严格七字段的安装独立PASS及其报告哈希，并再次全量root核验。root实际读取全部历史，包括/root及固定8个root-only对象；UID1000只对这8项以root绑定内容哈希配合完整lstat元数据核验，其余公共对象真实读取，未知不可读对象不忽略。正式安装事实审计仍应验证实际24文件闭集和真实UID1000固定入口，不能以root或临时夹具成功替代。

## 独立测试与正式只读证据

使用固定Python3.9.23 -I -S -B，独立运行test_m9_source_build_v3_consumer.py的40项、test_m9_source_build_v3_chain.py的15项，全部通过；旧overlap控制110项、UID1000 consumer 23项、completion 13项也全部退出0通过。测试中的安装、许可及失败注入均在临时隔离目录。

新增整链测试以真实UID1000运行临时已安装consumer/launcher，精确父argv签发临时BOUND，实际common验证RUNNING/CONSUMED上下文，实际加载MPI派生driver，产生PASS/FAIL回执并由父验证器验收。夹具在冻结临时副本前注入路径设置，模拟原capability发行格式，并把计算叶替换为只读verify_packages；它不是完整原budget驱动的正式构建。原budget路由、解析、首写及事后提交另由实际函数回归覆盖。真实工具链完整14包、版本、wrapper及路径检查通过，不等于configure/make、自测或构建产物已通过。

正式只读采集于2026-08-31T14:58:39.648966+00:00结束，未调用正式main/preflight/install/permit/run/recover。持原锁直接调用只读核验函数，前后193完整receipt与已封存MPI恢复证据完全相等，canonical SHA为 `ea1c2bf5ba92b11d96f59ed7b74af8e302c368418122c468fb889a6fa030c5f1`。基线文件M9_source_build_mpi_recovery_v1_postexecution_evidence.json的SHA为 `177390748086e678d22c3f24531c5a9b326889e5acb7f3931275262cf27b2ed2`；它保存完整receipt和原始runtime，本轮实际读取后逐字比较，不仅比较预先声明的哈希。

准备树与退休树各5319项，前后完整字典相等，canonical SHA分别为 `7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260`、`060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`。失败事务、旧consumed/FAIL receipt/permit、所有旧snapshot及恢复journal均原身份不变。新v3 snapshot/staging/gate/permit及相应tmp全部缺席；HDF5 prefix、编译日志、构建产物manifest和材料运行目录仍缺席。

真实UID1000在正式布局上通过公共历史函数核验160对象、固定8项metadata及两树，退出0、stderr为空；前后runtime SHA均为 `354888ae6331993a9b28952a146006a3d96e61788965518f79f57b9f11392263`。该核验从已哈希的项目模块调用只读函数，明确不是尚未安装的v3入口验收。其前后root再次核对193对象和两树，全等。

| 正式runtime | bytes | SHA-256 |
| --- | --- | --- |
| state | 2291 | `3523f0d17ccc2168289c5992db691441dd68eb3f09dde3e73de12a4a2ec80560` |
| workflow | 905 | `4438c7fce6b5d94268b12d9f2c17876bf6b4f100c22c4610ba215b3c6d1862fa` |
| 失败transaction | 2345 | `2920d80e431992cc8a23abe409d2d513b7a567e44651382d09a82b8af085161d` |
| 完整ledger | 66755 | `8dfbb2bb9f23ac9066b457553c2bccfa94a2ab7dde5d66f6315595caaa793421` |

state/workflow活动事务为空，stage=SOURCES_PREPARED。CPU原始7214.469142588001秒、既有抵扣7200.075310528秒、有效14.393832060000932秒、余额7185.606167939999秒；smoke/batch为0，GPU compatibility=54.84820560599999秒、training/physical_validation为0。原预算对4294967296 bytes预测返回violations=[]。采集时总apparent/allocated为31133641292/31459217408 bytes，overlap增量1264161561/1289396224 bytes，VHDX为28097642496 bytes；这些读数不替代后续执行前即时检查。M9控制器、脚本、测试及正式controls缓存扫描为0。工作包、本报告Pandoc严格Markdown和git diff --check通过。

## 最终边界

该冻结实施可进入主端single-FD loader零写预检及一次机械安装流程；本审计没有执行这些动作。安装事实独立PASS、新单次permit与执行前独立核验仍须完成，随后仅执行工作包唯一source_build命令一次。D-019覆盖人工权限但不允许复用旧机器令牌。构建结果、后续结构smoke/batch、GPU或训练没有因本PASS获得技术放行；M9-DATA-B01仍OPEN。报告与verdict封存后不回写。
