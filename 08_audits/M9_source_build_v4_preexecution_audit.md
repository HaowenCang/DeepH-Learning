# M9 source_build v4 独立执行前审计

日期：2026-09-01。审计角色：独立子 agent。结论为 **PASS / BLOCKING=0 / NON_BLOCKING=0**，两个问题计数均为整数。本结论仅放行下述冻结 v4 consumer 的唯一 `source_build` 命令一次；不证明构建、自测、结构计算、材料结果、GPU 或训练结果通过，也不授权任何重试。

## 安装权威与许可绑定

独立重算安装证据、报告和严格七字段 verdict，SHA-256 分别为 `aadf3801eaf50a0861bd330bb9f865758047d08749348e79d399c2f59cf7d3d3`、`8dde4b7594598c8f58381b6e675200b3587da7be0d97c3898418f701e846c8dc` 和 `fae99d0d4cda77565f1bbccfe9d04630ff60be3b7026d4c82649a72880dc4b56`。安装 verdict 为 `m9-source-build-installation-verdict-v4`、PASS/0/0，并绑定 frozen manifest `5862155306e595f268e996a9712194faabd2347e94b73a0118ebb403c763cf09` 与实际安装报告。

实际许可 `/home/evan-williams/deeph-m9/manifests/source_build_v4_execution_permit.json` 是 447 bytes、root:1000、0640、nlink 1 的普通文件，SHA-256 为 `c3aae6ff0c5aaffb3d5a711b48e7dc505061959eb144509995f8e9890f5853d4`，临时路径缺席。其字段闭集恰为 schema、gate SHA、operation、nonce、安装报告 SHA 和安装 verdict SHA；schema 为 `m9-source-build-execution-permit-v4`，并精确绑定 gate `dcd0a0ed3307add49df5b7586ba0bf01b2fc55b0469a42067893e563ba2ff3c1`、operation `bb0b7c8b982d4d72a66a1f01f95533da`、nonce `f6cbfb8b789687b250133b173e8ebf934e8ad3c2e5f8d5ed2baecf6d53c641d6` 及上述安装报告/verdict。没有接受主端记录作为许可正确性的自证。

## 274 对象闭集与运行态

从独立安装证据可逆解压完整 273 对象父态，得到 114969 canonical JSON bytes 和 SHA-256 `125eb54b21a7f0b23d558c32b88328544d8093f56f4fcf5e4f10e6c3d5935446`。root 对 manifests、controls 和 `/root/deeph-m9-control` 连续两次全量重采集，当前恰为 274 对象、115364 canonical JSON bytes、SHA-256 `6c2db9fb44776e40592e0a545e3db6a25628088159a6a7418f3cdabb54c7e6de`。相对 273 父态没有删除，唯一新增项就是 v4 permit；旧 273 项中只有 manifests 父目录的 `mtime_ns` 与 `ctime_ns` 发生许可安装所允许的变化，其余 receipt 逐项全等。完整 274 receipt 的可逆 gzip/base64 载荷已封存于 [执行前证据](M9_source_build_v4_preexecution_evidence.json)，其 SHA-256 为 `11c20faeb1069d29804d6ffa5b98705ab6579ced0a62ca7d2b0583eb1c7ecc70`。

四份运行态原字节与 273 安装基线相同：ledger `f3f44ee5169bbeb44d175ff0aa381cda70684ad66f11ce57725c2e774471d4c7`，state `cdfcf813f1e6c4759b0a8ef93a76d95a50d6e586ba5f4652908f6b1dd375dd7b`，workflow `271bd1c756b55db52b7cb479a7d679edb95e2d3bd33b21cfff88122f40459b34`，失败 transaction `433462132e40fd9f160bce150e20a7c3149227ad8bf4957e8d19d71e389ddb58`。state/workflow 均非 hard-stop、活动事务为空，workflow stage 为 `SOURCES_PREPARED`，两者保留恢复标记 `m9-source-build-host-shutdown-recovery-20260901-01`。旧 transaction 仍为 `FAILED_COMMITTED`、`source_build`、transaction id `4d7808af7df9418518a59afeba766eb9`，并保留同一恢复标记和 `host_shutdown_external_interruption` 原因。

BUILD 与退休失败树各 5319 个 receipt，连续两次采集全等，canonical SHA-256 分别为 `411a8a674559723f0616deafbe67c93d3e31453461fa6b2af26d4135bb3e1705` 和 `060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`。HDF5/OpenMX 安装 prefix、构建 manifest、构建日志、staging、材料运行与旧 v1 permit 等禁用对象均缺席；未发现 consumer、launcher、compiler、make、MPI 或 OpenMX 构建进程。项目 `06_reproduction` 与已安装 v4 snapshot 中的 `__pycache__`、`.pyc`、`.pyo` 数量均为 0。

## 真实 UID1000 零写验收

实际用户 `evan-williams` 以固定解释器 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 从 root-owned 已安装 snapshot 执行一次只读 `verify-execution`。解释器为 Python 3.9.23，euid 1000，isolated、no-site 和 dont-write-bytecode 均成立。命令退出 0、stderr 为空，返回 `status=PASS`、`action=source_build`、`source_build_executed=false`，runtime identity 为 `c042a2107e8f90782f295ded5f3eca7d81338bee597087d0c0d64549b42e1446`。

该命令前后完整 274 namespace、四份 runtime 原字节及两棵 5319 对象树均全等；没有 capability、receipt、事务、ledger 或构建产物写入。审计没有调用 `run`、launcher、source_build、installer、preflight 或 permit 写入口。

## 预算、唯一 argv 与不可重放边界

从已安装派生预算只读解析得到唯一请求 `source_build / overlap_build / 4294967296`，即时 `violations=[]`。有效 `overlap_build` CPU 为 `307.1697352600013` 秒，上限 7200 秒，余额 `6892.830264739999` 秒；原始 CPU、抵扣、GPU、存储基线及 unlimited wall-clock policy 均随四份 runtime 原字节保持不变。唯一允许的一次 consumer argv 按 token 为：

```json
["run","--build-operation-id","bb0b7c8b982d4d72a66a1f01f95533da","--bucket","none","--cpu-bucket","overlap_build","--forecast-bytes","4294967296","--overlap-operation","--overlap-action","source_build","--config","/mnt/e/Projects/Codex/DeepH/06_reproduction/configs/m9_overlap_only_contract.json"]
```

旧 v3 permit 的 schema、gate SHA、operation `7bc4139f7a9c4b768d3f9ec68c1d1048` 和 nonce 均与 v4 不同，不能授权 v4。当前 v4 permit 只绑定上述 operation、nonce、gate runtime 和唯一 argv；动作首次状态写发生在原 `budget.lock` 内并再次核验完整 gate。一次动作开始后，RUNNING、终态或外部中断状态都会使原 gate runtime 不再相等，因此同一 v4 permit 不能用于第二次消费。若进程在首次状态写之前被外部终止，则机器许可尚未发生消费，但该次宿主调用仍已用尽本报告放行的唯一调用次数，任何重试仍须重新建立并独立审计门控，不能把文件仍存在解释为重试授权。

## 最终判定

v4 执行前条件满足 **PASS / BLOCKING=0 / NON_BLOCKING=0**。当前没有审计采集进程。该判定仅允许主端以固定 Python 3.9.23、已安装 v4 consumer 和上列逐 token argv 启动唯一 `source_build` 一次；旧 v3 permit 不可复用，当前 v4 permit 在该次调用后也不可第二次消费。构建终态及自测仍须另作独立事实审计，结构 smoke/batch、材料计算、GPU 和训练均不在本放行范围内。
