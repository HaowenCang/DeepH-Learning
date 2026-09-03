# M9 source_build v1 工作包

状态：`IMPLEMENTATION_PENDING_INDEPENDENT_AUDIT`。本文件是实施范围与验收合同，不是独立PASS结论。

## 授权、前置事实与不变边界

用户批准见 `M9_source_build_v1_user_authorization.md`。已完成的源码准备最终审计为 `M9_source_prepare_py39_fresh_execution_independent_audit.md`，SHA `89418b784d800e25d895b05360ecd086be217e5a820dcdca526ef0205b1cde71`；对应post evidence SHA为 `ee4d593ddb277a252cbd3a90b0e59f94b96fc1d614e2544dde22bb5b217f8455`。当前成功事务为 `dc75dda112af553377a697f629801782`，workflow=`SOURCES_PREPARED`，state/workflow均无hard-stop或active transaction。

本轮只建立编译消费链并在全部门控通过后执行一次冻结编译及构建自测，不下载、不运行材料结构、不进行smoke/batch/GPU/训练/DFT标签生成。保持原source launcher、build/common、16-file overlap及25-file consumer所有成员字节；新文件位于controllers和manifests，不向原scripts目录添加文件。主计划、进度台账和decisions暂保留为冻结历史来源，README及当前状态补充记录承担最新导航。

## 精确派生与复用

原root-owned v2 snapshot中的 `m9_budget.py` SHA为 `a94902a942f98217171be5d9967f469a4dd4563c80e6e6ef3d68e6cede71168d`。只对 `command_overlap_run()` 中连续的D-018 scope/action判断作一次精确bytes替换：

```text
!= "ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018"
or action != "source_prepare"
```

变为新scope `ALLOW_ONE_SOURCE_BUILD_AFTER_PREPARED` 与action `source_build`。实现匹配包含原缩进及换行，断言原SHA、匹配次数=1和派生SHA `94050d73f498b84ab0054f64f1b04ea8667067f86a54ed3f352e6b926a9e691e`，不做全局替换。其余CPU/GPU/存储、事务状态机、超时、hard-stop、capability、launcher以及构建参数保持逐字节。派生预算文件仅写入新root-owned snapshot，不改写原文件。

## 门控与闭集

新snapshot为 `/home/evan-williams/deeph-m9/controls/source-build-v1`，root:1000/0550，成员root:1000/0440单链接。它封存consumer、installer、测试、工作包、授权记录、源码准备事实与完整post evidence、既有receipt工具、两个旧冻结manifest、新冻结manifest、实施报告/verdict和派生budget。实际目录成员须严格等于manifest闭集，拒绝额外文件、symlink、hardlink、特殊文件、权限或字节漂移。

新readiness gate为 `manifests/source_build_v1_gate.json`，新执行许可为 `manifests/source_build_v1_execution_permit.json`，均root:1000/0640普通单链接。gate绑定新snapshot、冻结来源、实施PASS、授权记录、固定operation/nonce以及当前runtime；permit只在独立安装事实PASS后签发，绑定其报告/verdict与gate。旧gate、snapshot、source_prepare授权均不覆盖、不删除、不复用。

root安装前在原budget.lock `2096:50700` 内比对全部130项正式基线，包括root-private历史。UID1000验证可读正式闭集，root-private证据通过root签发和不可变审计哈希绑定，不降低权限。安装仅允许新snapshot/readiness gate及相应父目录变化；permit阶段仅新增许可及父目录时间变化。状态、workflow、ledger、旧事务与capability不因安装或签发改变。

完整准备树5319条receipt（5179文件、140目录）SHA为 `7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260`；原失败退休树同口径SHA为 `060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`。这些receipt包含路径、类型、inode、权限、nlink、大小、mtime/ctime和文件SHA，不含读取可变的atime。新consumer在原预算锁内和第一次atomic_json写入前验证完整树，而不只依赖official manifest的1577条路径；HDF5源码、configure及额外文件均被覆盖。预存HDF5 prefix、build/overlap manifest、构建日志、结构run root或活动staging都拒绝，不清理以规避门控。

安装采取pristine-only策略：snapshot、staging、gate/permit及其tmp若已存在则停止；不自动重放、续提或删除不完整安装。半安装状态没有执行许可，不能触发编译；若中断，应先只读审计现场再决定恢复办法。runtime发生任意变化后，旧执行许可不能再次消费。

## 唯一编译命令与预算

```bash
/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B \
  /home/evan-williams/deeph-m9/controls/source-build-v1/m9_source_build_consumer.py \
  run --build-operation-id 72cefbe283654fd5b85fb2e66d9c2dfb \
  --bucket none --cpu-bucket overlap_build --forecast-bytes 4294967296 \
  --overlap-operation --overlap-action source_build \
  --config /mnt/e/Projects/Codex/DeepH/06_reproduction/configs/m9_overlap_only_contract.json
```

新入口逐token接受唯一argv，拒绝旧授权、缩写、重复flag、额外cwd/log、结构id、自由命令、`--`、smoke/batch以及GPU参数。执行前budget预检仍为4 GiB预测和原overlap_build余额，运行超时仍由原剩余CPU子预算决定。执行后无论成功与否立即停止，不进入下一动作。

HDF5 make check、官方OpenMX构建及受控源码不变性、只修改两个overlap补丁C文件、最终动态库来源与版本、构建日志与产物allowlist均保留原强度。只完成上述内容不能关闭 `M9-DATA-B01`，不能宣称数据或训练完成。

## 独立审计与调用协议

实施测试包括精确派生、完整argv、严格字段/来源/快照闭集、HDF5和额外文件漂移、预存产物、非终态、重放、锁内首写前拒绝、真实临时文件与UID1000消费验证。原110 overlap、23 consumer和13 completion回归应无回归；禁止py_compile和缓存新增。正式审计由独立子agent完成，主agent实施修复，不替代PASS结论。

installer仅经旧替代工作包中已冻结single-FD loader运行，root和固定Python3.9.23 `-I -S -B`。loader后的参数为installer路径、installer SHA、action（preflight/install/permit）、consumer SHA、新frozen SHA、实施verdict SHA、实施report SHA；permit另追加安装verdict SHA和安装report SHA。preflight零写；install创建新snapshot/readiness；独立安装事实审计PASS后permit只签发单次许可；真实UID1000 `verify-execution` 通过后才运行上方唯一命令一次。

实施verdict严格字段为schema/status/blocking/non_blocking/frozen_sha256/report_path/report_sha256，schema=`m9-source-build-implementation-verdict-v1`；安装verdict同字段，schema=`m9-source-build-installation-verdict-v1`。两者均要求PASS且问题数为整数0。报告、verdict和所有冻结来源一经引用SHA，不就地修改；后续状态使用非冻结补充记录。
