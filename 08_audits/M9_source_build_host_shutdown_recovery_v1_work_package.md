# M9 source_build 宿主关机中断恢复 v1 工作包

日期：2026-09-01。状态：IMPLEMENTED_PENDING_INDEPENDENT_AUDIT。D-019持续授权覆盖本恢复的实施、审计和执行；它不取消独立技术门控，也不授权重放v3 permit或扩大科学范围。

## 事实对象与失败语义

v3唯一source_build已消费operation `7bc4139f7a9c4b768d3f9ec68c1d1048`及capability `3cd45d83e11ec6fe0e39725dfe7c6d79`。transaction `4d7808af7df9418518a59afeba766eb9`在宿主关机后保留RUNNING；state/workflow仍引用该活动事务，ledger仍为执行前原前缀。capability已消费但launcher receipt缺席。因此它是外部中断的未提交事务，不得伪装为正常退出码，也不得通过重放旧命令让原预算控制器事后提交。

宿主System事件1074记录2026-08-31 23:23:35+08由Explorer发起关闭电源；HDF5 check日志于23:23:45以`Terminated`截止；Kernel-General 13记录内核关闭UTC `2026-08-31T15:24:41.9861032Z`。原事务start UTC为`2026-08-31T15:19:49.210200Z`。恢复采用二者之差292.7759032秒作为保守CPU wall charge上界；不新增抵扣、不改变上限，且明确记录这是宿主关机上界而非原monotonic终值。

## 恢复目标

恢复必须在原budget.lock独占锁内验证独立中断事实报告、完整证据和冻结来源闭集，并逐字绑定当前未提交运行态、完整ledger前缀、已消费capability、缺失receipt、v3 permit、三份构建日志、部分构建树、两棵历史源码树及宿主关机证据记录。

正式变化限于：

- 将中断工作树原子改名为带transaction ID的retired目录，保留全部inode、字节和部分产物；
- 将三份中断日志目录原子改名为对应retired目录；
- 从只读核验过的既有干净退休树复制一份新工作树，逐相对路径核验文件字节、类型、权限和链接目标；不修改干净来源树；
- 将原RUNNING transaction版本化提交为FAILED_COMMITTED，原因只能是`host_shutdown_external_interruption`，退出码为null、timed_out=false，绑定关机证据与中断树/日志receipt；
- 在原ledger inode上恰追加一条`SOURCE_BUILD_HOST_SHUTDOWN_RECOVERY`，补记292.7759032秒至原`overlap_build`累计；保留原前缀、全部GPU、smoke/batch、存储预算、抵扣与历史字段；
- 清空state/workflow活动事务，恢复非hard-stop `SOURCES_PREPARED`，写入新恢复标记；
- 保存root-private完整恢复来源、原运行态、独立证据、journal及目标哈希；公开只读snapshot只包含后续验证所需的恢复适配器和固定事实，不携带执行许可。

HDF5 prefix、build manifest、overlap tree manifest与材料run root在恢复前必须缺席。恢复动作不得执行configure、make、OpenMX、材料计算、训练、下载或permit。任何前置漂移或阶段写入失败均保留现场并停止；不得尝试覆盖式重放。

## 验证与后续门控

测试应覆盖精确RUNNING中断语义、旧permit/operation不可重用、保守计量、ledger单行追加、transaction终态、两棵树原子归档/重建、日志归档、复制树漂移、未知对象、短写、各持久化窗口故障与零写preflight。首次验证返回后、首个写操作发生前，控制器必须在同一锁内第二次完整复核并比较封印值；复核对象包括全部authority载荷、221项正式namespace、四份runtime原字节、capability/receipt/进程、permit、两棵树的全量receipt和portable视图、日志闭集、禁用产物以及1 GiB存储预测。正式恢复须先经独立实施审计PASS/0/0，再由主端执行一次preflight及一次recover；执行事实另行独立审计。

恢复PASS只重建`SOURCES_PREPARED`和干净工作树，不等于构建通过。随后须建立v4单次consumer/launcher和新permit，绑定恢复后的新runtime、已归档中断证据和新工作树；执行前独立门控通过后才能重新从HDF5配置开始构建。M9-DATA-B01、structure 500 smoke、batch、训练和物理验证均不因本恢复自动放行。

## 实施说明

实现对象为`m9_source_build_host_shutdown_recovery_v1.py`及其隔离测试。控制器使用冻结Python3.9.23 `-I -S -B`与root身份，先通过single-FD启动链验证自身、严格七字段独立verdict、九项直接来源及v3 manifest指向的全部嵌套历史来源；随后独占原budget.lock并保持描述符与路径身份检查。完整221项namespace从独立evidence内的canonical JSON gzip载荷恢复并逐项比较；四份runtime原字节、permit、consumed、缺receipt、7,640项中断树、5,319项干净历史树、三日志、禁用产物和原预算1GiB恢复预测均在首次写前复核。

恢复阶段journal依次记录PREPARED、INTERRUPTED_ARCHIVED、LOGS_ARCHIVED、CLEAN_TREE_CLONED、LEDGER_COMMITTED、TRANSACTION_COMMITTED、STATE_COMMITTED、WORKFLOW_COMMITTED和SUCCESS_COMMITTED。中断树和日志采用同文件系统原子rename，逐inode及安全字段核验；干净历史树使用非硬链接复制并逐相对路径比较字节、类型、owner/mode和链接目标。每个复制出的普通文件在owner、mode和时间元数据设置完成后均通过自身描述符执行`fsync`；所有新建目录（包括只包含符号链接的嵌套目录）由深到浅执行`fsync`，父目录随后持久化；全量普通文件非硬链接核验在rename及阶段checkpoint之前完成。复制前后历史树全量身份不变。ledger保持原inode/权限并只追加一行；三个JSON分别在替换前重新核验原字节，使用O_EXCL临时文件和原子replace。任何既有目标、临时文件、未知namespace、来源/树/日志/产物/进程/预算/锁漂移、短写或阶段故障均停止，不恢复重放。

隔离测试目前17个测试方法。除真实九文件authority与嵌套历史闭集、严格verdict夹具、精确孤立事务、保守计量与历史保持、无效字段、完整commit、non-pristine拒绝、短写/零写、ledger部分写、非法动作和精确进程匹配外，还包括：真实`validate('preflight')`前后全夹具receipt相等；首次写边界的未知正式namespace、中断树、干净树、日志、禁用产物、进程和存储预测七类漂移均零写拒绝；九个journal持久化窗口逐一在checkpoint完成后注入故障，核验现场保留且第二次调用被pristine-only规则拒绝；复制出的每个普通文件和所有嵌套目录均出现耐久化调用；文件与嵌套目录`fsync`故障均在安装rename前停止并保留staging；克隆与源树不存在硬链接；复制结束后的staging字节漂移在安装rename前被拒绝，现场保留且不可重放。正式现场另做过一次零写下层复核：221 namespace、7,640中断树、5,319干净树、raw runtime、consumed及缺receipt均一致；原预算对1GiB恢复预测返回violations=[]。这些主端结果不替代独立实施审计。

独立初审提出的B01（首次写前只复核正式namespace）、B02（复制文件及嵌套目录缺少完整耐久化）和B03（测试声明超过实际覆盖）已在本版本中按上述机制实施修复；关闭与否仍由独立定点复核决定。
