# M9 source_build v2 权限分层修复工作包

记录日期：2026-08-31。状态：IMPLEMENTATION_PENDING_INDEPENDENT_AUDIT。本文件规定实施与验收条件，不自证独立PASS。

## 授权与基线

用户新的明确“批准”见 `M9_source_build_v2_user_authorization.md`。仅修复v1实际UID1000不能读取root-only历史证据的问题，并在独立实施、安装及执行前门控全部通过后执行一次冻结编译与自测；不下载、不计算材料结构、不训练、不改变预算。

v1安装事实报告SHA `0a6b4ba15309eb8c44707ddf33840f052dca2888fd204502d851e171c77fb86f`，verdict SHA `52f5e775d3477688a84da6c409afaf96e6a8f34f44d315f8e17222a2c6ff36a4`，结论FAIL/1/0。完整147对象安装后baseline SHA `0e125e288af8299fb3cf6447ac379e3b946bd042ddd705537dcd9cff11300f00`，其中formal namespace canonical SHA `78003a0d58a321e5e2a57bf76b1fd2106bed92d894433a43bfbb6f45943a150e`。这些失败证据是v2历史基线，不是v2执行许可或成功结论。

workflow仍为SOURCES_PREPARED，事务 `dc75dda112af553377a697f629801782` 为source_prepare/SUCCESS_COMMITTED，active transaction为空。state/workflow/transaction/ledger SHA依次为 `3c57eca541fde4f9d939766940459dac7ac7058a3af899ed79154d1cf852eb3e`、`22cd75911994b708c19d1b7bfb1da84f264513dea59a9bd795a52e44933b0d32`、`2efb2729126903a1cd0d2f200565a225850e2fd3a0d10256f970b208318a75d6`、`0be27e9220b6597d47ee657bbe5169134118340c77a7a0af3722a4eb1ad885c2`。ledger SHA以机器baseline逐字节验证为准；不得重建ledger或覆盖成功事务。

## 修复机制与证明边界

v1仅排除了/root路径，却递归读取整个manifests；其8项固定历史文件为root:root/0600。因此root预检通过不等于UID1000入口可消费。中断前主端先将相同8项权限加入临时fixture，真实UID1000稳定复现同一路径的PermissionError；随后实现权限分层，令同一回归通过。诊断采用先复现、后修复流程，没有改动正式历史文件。

固定8项文件名见v1安装审计的完整表和v2代码ROOT_ONLY_NAMES，均位于固定runtime/manifests下。root安装与permit阶段在原budget.lock内使用实际文件读取，逐字核验147对象及其后允许的新对象，包括8项和/root历史。此路径不调用metadata-only替代逻辑。

UID1000公共遍历只对这8个明确绝对路径采用metadata-only分支，严格比较路径、类型、dev/ino、uid/gid/mode、nlink、大小、mtime/ctime，其他公共对象实际读取并哈希。不使用os.access动态分类，不捕获任意PermissionError后跳过；额外不可读对象、错误权限、链接、新inode、增删和漂移均拒绝。

readiness增加history_attestation_sha256，绑定baseline文件SHA、固定8项完整receipt以及/root集合。baseline和v1失败报告同时进入root-owned新snapshot，gate绑定snapshot。这里的内容哈希证明来自root在安装/permit时实际读取和封存；UID1000只证明当前可见元数据一致，不能称为重新读取了这些root-only内容。root是既有信任根；本修复不声称防御拥有root权限并能篡改信任根的对手。

## 新版本闭集及不变来源

新增consumer为 `06_reproduction/controllers/m9_source_build_v2_consumer.py`，installer为 `m9_source_build_v2_install.py`；不向旧scripts目录新增文件。旧25-file consumer、16-file overlap和10-file build-v1 manifest及成员保持原SHA。主计划、progress_tracker、decisions仍属旧冻结来源，不就地修改；当前状态记录和README承担最新导航。

v2新冻结manifest严格12文件：新consumer/installer/test/work/auth，v1安装baseline/report/verdict，原receipt工具，以及旧25/16/10三份manifest。新snapshot封存这些12项、新frozen、v2实施report/verdict、精确派生budget共16成员，另有snapshot_manifest.json，共17个普通单链接文件。目录root:1000/0550，文件root:1000/0440。

新路径固定为 `/home/evan-williams/deeph-m9/controls/source-build-v2`、`manifests/source_build_v2_gate.json` 和 `manifests/source_build_v2_execution_permit.json`；gate/permit为root:1000/0640。所有新schema使用v2，operation与nonce见新授权。v1 snapshot/gate和全部历史对象不在v2新增集合内，不能替换；v1 permit及其tmp必须缺席。安装预计147对象新增19对象至166，permit再增1至167；controls父目录nlink从7到8，其他父目录仅允许指定元数据变化。

安装采用pristine-only：新snapshot/staging、gate/permit或固定tmp预存则拒绝，不自动删除或续提。只读预检不写运行态。半安装没有许可不能执行；原锁dev/ino为2096:50700，uid/gid1000、0644、nlink1、空文件，身份不变。

## 原计算链和预算保持不变

原budget SHA `a94902a942f98217171be5d9967f469a4dd4563c80e6e6ef3d68e6cede71168d`；与v1相同，仅精确替换D-018连续两行scope/action，原SHA、匹配次数1、反向字节等同和派生SHA `94050d73f498b84ab0054f64f1b04ea8667067f86a54ed3f352e6b926a9e691e`共同约束。内部scope仍为ALLOW_ONE_SOURCE_BUILD_AFTER_PREPARED，外部v2权威严格区分版本。不修改原事务、capability、launcher、CPU/GPU/存储、计量与失败停机机制。

完整准备树和失败退休树各5319 receipts，canonical SHA分别为 `7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260` 和 `060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`。首次预算写入前完整验证，不仅检查1577条official manifest。预存HDF5 prefix、构建日志、overlap/build manifest、结构运行root或活动staging均拒绝。

已有原始overlap_build累计7212.901214103001秒，原抵扣7200.075310528秒，有效12.825903575000666秒，余额7187.174096424999秒；这些是基线值，不替代即时预检。原build/smoke/batch CPU上限7200/1800/21600秒；GPU总86400秒及原子限额不变；总存储100GiB、overlap增量10GiB、项目审计1GiB。新snapshot和审计文件计入存储；4GiB预测仍须原预算函数通过。无总墙钟期限不取消子预算超时。

## 唯一执行与独立门控

```bash
/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B \
  /home/evan-williams/deeph-m9/controls/source-build-v2/m9_source_build_v2_consumer.py \
  run --build-operation-id a237ec1f2b404d898840c643e9ae501b \
  --bucket none --cpu-bucket overlap_build --forecast-bytes 4294967296 \
  --overlap-operation --overlap-action source_build \
  --config /mnt/e/Projects/Codex/DeepH/06_reproduction/configs/m9_overlap_only_contract.json
```

逐token接受上述argv，拒绝缩写、重复或额外参数、自由命令、旧operation、source_prepare、结构id、smoke/batch及GPU。解释器固定3.9.23且-I/-S/-B，真实UID1000，从安装路径执行。完整门控在入口锁内、原控制器锁内及首次atomic_json之前重验；未完成事务分支也受首写守卫约束。runtime改变后拒绝重放。

root安装器继续仅通过旧替代工作包中SHA `c68e43b5de4fdadb44254fbfdd543f5ba2a29b6e41994021c55a3287b5f7491f` 的精确single-FD loader调用，旧工作包SHA `dc1d0d992f7e1328f79a4436eb4535b79ba2ab48fcee1b44fa498c31c30e91a2`。参数依次为installer path、self SHA、preflight/install/permit、consumer SHA、新frozen SHA、实施verdict SHA、实施report SHA；permit另加安装verdict及report SHA。所有报告/verdict一经SHA引用不就地修改。

独立实施verdict schema=m9-source-build-implementation-verdict-v2，安装verdict schema=m9-source-build-installation-verdict-v2，均严格7字段schema/status/blocking/non_blocking/frozen_sha256/report_path/report_sha256，PASS且问题数为真实整数0。先实施审计、再零写预检与安装、再独立安装事实审计；实际UID1000 verify-ready必须PASS，verify-execution在缺permit时必须到达明确FileNotFoundError许可路径且零写。随后root签发permit，再独立复核实际许可和UID1000 verify-execution，最后主端调用唯一命令一次。

## 测试和验收

v2现有40项测试覆盖原32项及真实8项权限布局、实际安装入口、有/无许可、root内容读取与UID元数据替代隔离、每个固定文件内容漂移、权限/链接/新inode、未知不可读对象、attestation漂移和v1权威拒绝。临时测试中的installed/PASS输出不代表正式安装。原v1 32、overlap 110、consumer 23、completion 13项回归均应通过。禁止py_compile或缓存新增。

正式安装与执行结果由独立子agent审计，主agent修复，不替代独立结论。编译保留完整HDF5 make check、两次OpenMX构建、两处C文件补丁限制、源码与产物允许清单、动态链接来源、日志和安装清单验证。任何一项未证明时，不称为构建PASS；构建通过也不关闭M9-DATA-B01、不放行材料结构或训练。
