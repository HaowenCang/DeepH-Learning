# M9 source_build v3：恢复后的MPI修复消费链

日期：2026-08-31。状态：IMPLEMENTED_PENDING_INDEPENDENT_AUDIT。尚无实施PASS、安装PASS或执行许可；下列命令仅在所列独立门控全部通过后使用。

## 授权及父态

采用 [D-019](../00_scope/D019_standing_execution_authorization.md) 和 [持续执行授权原文](M9_standing_execution_authorization_20260831.md)，覆盖本工作包的实施、独立审计、安装、签发和编译自测；后续适用的失败恢复与重试不再重复申请人工批准，但仍须完整门控。

父态为MPI恢复独立审计PASS后的193对象，报告SHA `590121ae5d98c222a2014d315d8f28f08fad95be05cc4c46065e8bf55bd366d2`，证据SHA `177390748086e678d22c3f24531c5a9b326889e5acb7f3931275262cf27b2ed2`。state/workflow非hard-stop且活动事务为空，workflow=SOURCES_PREPARED；事务槽保留38a891fff6fd07675581b891766e02c6的FAILED_COMMITTED，不伪造成功父事务。

原始CPU build累计7214.469142588001秒、既有抵扣7200.075310528秒及全部GPU/存储历史继续保留。新阶段不修改上限，执行前由原预算函数按4GiB预测和实际余额检查；本段历史读数不能替代即时核验。

## 需要改变与必须保持的对象

| 环节 | v3要求 |
| --- | --- |
| 人工授权 | 绑定D-019持续授权，不复用旧v2用户单次授权 |
| namespace和runtime | 绑定193对象恢复后完整receipt，包括失败事务和恢复journal，不继续使用147对象v1安装基线 |
| consumer/installer | 新版本路径、新schema、新operation和nonce；保留旧版本及权限 |
| 子进程launcher | 精确绑定新安装入口与新单次capability，实际执行已验证MPI派生driver |
| build driver | 原SHA ab6632784a744fd3f66c95aac30a56767f67af3d8d81147df2fc0d72b67102ec保持不变；精确派生SHA5652ee35a3595f42bd3050e5825419175fc84526a421a0500559d4146f253d00 |
| 源码回执校验 | 明确核验原字节、派生规则和实际加载字节的关系，不把派生SHA冒充旧manifest原SHA |
| common上下文 | capability只安装一次；不调用只读verify_toolchain重置common模块或预算上下文 |
| 预算和失败处理 | 保留原CPU/GPU/存储检查、事务提交、超时停进程组、失败记账与双HARD_STOP |

v2直接重用不成立：其历史基线、成功source_prepare父事务条件和实际launcher来源均指向修复前状态。仅修改consumer入口中的版本检查不会改变子进程实际加载的旧driver。新实现应尽量复用经过验证的代码，但必须贯通consumer、budget构造的argv、launcher、source-only模块加载以及父进程回执校验。

## 实施与验证顺序

先实现并测试新来源绑定和完整链路，再冻结精确源码、测试、授权与父态清单，交独立agent进行实施审计。审计PASS且问题清零后，主端才执行零写预检及机械安装。安装后须由独立agent使用真实UID1000、固定Python3.9.23的-I/-S/-B和正式固定路径验收，不能用临时项目路径或root成功替代。

安装事实通过后签发新的单次机器permit，再独立复核实际permit、来源、运行态、预算与唯一argv。门控通过后主端执行一次source_build及原合同规定自测，保存完整结果并交独立执行事实审计。D-019已覆盖人工授权，不再在这些普通步骤间申请重复批准。

测试至少覆盖：旧193对象漂移和未知新增拒绝；八项root-only证据权限不变；旧审计、旧permit、旧operation及已消费capability拒绝；错误父事务或缺恢复事实拒绝；实际子进程加载派生driver而非旧driver；loader不读取缓存且不处理.pth；common capability上下文不被重置；launcher来源与预算回执验证一致；首次正式写入前重新核验；失败、超时、输出异常与重放停止；真实固定工具链完整检查通过。

编译验收仍覆盖HDF5 make check、两次OpenMX构建、源补丁限制、产物允许清单、动态库来源、日志和安装清单。只读工具链PASS不能替代构建PASS。构建后才按依赖推进结构500 smoke、450结构预算投影及逐结构overlap生成，各自独立门控继续有效。

## 实施、测试及独立早检修复

新代码为controllers下的m9_source_build_v3_consumer.py、m9_source_build_v3_install.py和m9_source_build_v3_launcher.py。版本化沿用v2的来源验证、root内容与UID1000固定八项metadata验证、原锁、完整树receipt、pristine-only安装和首写前守卫，改为MPI恢复193对象父态以及新路径/schema/operation/nonce；旧9/12/10/25/16来源闭集保持原字节。

原budget仍仅采用已验证的scope/action两字面量派生：原SHA `a94902a942f98217171be5d9967f469a4dd4563c80e6e6ef3d68e6cede71168d`，派生SHA `94050d73f498b84ab0054f64f1b04ea8667067f86a54ed3f352e6b926a9e691e`。consumer在内存中将budget的launcher常量改为新root-owned安装入口，将回执验证函数接至v3验证器，并保留v2首写前门控守卫；不改旧budget文件或记账分支。

新launcher先验证root-owned snapshot和实际consumer，再由consumer完整核验静态安装/许可权威；进入capability消费前检查真实父进程argv、子进程argv、source_build动作、无structure_id及4GiB forecast。原budget的capability不含required_forecast_bytes字段，该字段属于transaction；不得错误地要求capability提供它。source-only loader逐字验证原driver，调用已冻结repair.derive得到指定派生SHA并执行；common不重载、不重新安装预算上下文。回执同时记录base_sha256和实际派生sha256，父验证器不把派生SHA冒充旧manifest原SHA。

独立早检提出B01：父回执校验的静态权威检查可能抛SystemExit，而原budget只捕获Exception，导致事后失败计账无法完成。按diagnose流程在实际派生budget.command_overlap_run的post-child分支先复现；修复仅在新validate_launcher_receipt边界将SystemExit转换为ValueError，前置门控仍零写拒绝。回归验证原生hard_stop_both提交FAILED_COMMITTED、清空活动事务、保留GPU及原CPU后计入精确2秒、原ledger前缀不变且恰追加一个OVERLAP_HARD_STOP。最初夹具ledger是root-owned，随后按正式1000:1000/0644校正夹具；未改正式ledger权限。主端测试通过不代表B01已由独立审计员关闭。

测试文件为test_m9_source_build_v3_consumer.py（40项迁移回归）和test_m9_source_build_v3_chain.py（15项新增链路回归，含多组负例）。新增测试包括真实UID1000实际临时安装路径consumer/launcher加载、完整真实工具链检查、精确派生与common对象身份、静态权威漂移、旧/错误回执拒绝和B01原预算失败分支。临时整链采用精确父进程argv与实际新launcher消费BOUND，真实common.install_budget_context绑定RUNNING事务，加载真实派生driver，实际生成PASS/FAIL回执并由新父验证器检查；为避免正式计算，仅在测试夹具中将计算叶函数替换为只读verify_packages，并将common的运行态路径指向临时目录。父发证器是模拟原capability格式的夹具，不将其称为完整原budget进程编译测试；原budget路由、解析、首写与事后计账另有真实函数回归。临时输出中的installed/permit/PASS不代表正式安装或构建。

## 新冻结闭集与安装路径

新manifest严格19文件，覆盖consumer/installer/launcher、两测试、工作包、持续授权/D-019/授权解释独立报告、MPI恢复独立报告及完整证据、repair适配器、receipt工具、旧25/16/10/12/9五份manifest及旧v1安装verdict。snapshot包含这19项及新manifest、新实施report/verdict和派生budget四项，再加snapshot_manifest.json，共24个普通单链接文件。目录root:1000/0550，文件root:1000/0440；readiness/permit为root:1000/0640。

新snapshot为`/home/evan-williams/deeph-m9/controls/source-build-v3`，新gate为manifests/source_build_v3_gate.json，新permit为manifests/source_build_v3_execution_permit.json。初始193对象安装新增snapshot目录及24文件和gate，共26项，至219；permit再增1至220。所有旧对象保持receipt，仅controls/manifests父目录允许原安装规则规定的变化。两棵5319对象源码树仍完整逐项哈希检查。

operation_id=`7bc4139f7a9c4b768d3f9ec68c1d1048`，nonce=`a930f2b8e7ac449bb251482012eb99d1c7032df764985aaac34519bf6db2013a`。唯一编译argv如下：

```bash
/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B \
  /home/evan-williams/deeph-m9/controls/source-build-v3/m9_source_build_v3_consumer.py \
  run --build-operation-id 7bc4139f7a9c4b768d3f9ec68c1d1048 \
  --bucket none --cpu-bucket overlap_build --forecast-bytes 4294967296 \
  --overlap-operation --overlap-action source_build \
  --config /mnt/e/Projects/Codex/DeepH/06_reproduction/configs/m9_overlap_only_contract.json
```

实际解释器、UID1000、-I/-S/-B及逐token argv必须匹配；旧operation、额外/缩写/重复参数、smoke/batch、GPU、自由命令均拒绝。root installer继续由旧工作包的single-FD loader启动（loader SHA `c68e43b5de4fdadb44254fbfdd543f5ba2a29b6e41994021c55a3287b5f7491f`），参数为新installer path、self SHA、preflight/install/permit、consumer SHA、新frozen SHA、实施verdict SHA、实施report SHA；permit另加安装verdict/report SHA。

实施verdict schema=m9-source-build-implementation-verdict-v3；安装verdict schema=m9-source-build-installation-verdict-v3。均严格七字段schema/status/blocking/non_blocking/frozen_sha256/report_path/report_sha256，PASS且问题数为真实整数0，引用报告SHA必须逐字匹配。实施、安装、执行前、执行后独立审计仍分开；当前无任何正式v3 gate或permit。
