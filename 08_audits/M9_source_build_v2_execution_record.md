# M9 source_build v2 单次执行记录

记录日期：2026-08-31。记录角色：主 agent 执行事实记录，不替代独立审计，不构成恢复或重试授权。

## 结论与授权消费

已在 v2 实施、安装及执行前独立审计均为 PASS/0/0 后执行唯一冻结命令一次。正式执行在工具链版本检查处失败，未进入 HDF5 configure、make、make check、install 或两次 OpenMX 编译。事务为 `FAILED_COMMITTED`，state/workflow 均已 hard-stop。没有重试、修复冻结文件、恢复状态、下载、材料结构计算或训练。

授权依据为 [v2 用户授权](M9_source_build_v2_user_authorization.md)，SHA `fc3031ea4c14d37c219002ea3eb534d80a39829c7b8243472acbcc68d1012e24`。最终 [执行前独立复核](M9_source_build_v2_preexecution_audit.md) SHA `ee11a04904675e5dbdd05f00e0fdd82b71edda8fcd430787b92353910a7ec963`，完整 167 对象执行前证据 SHA `4efc0337731d39412e312b84998096252600bd4f6ce8b7e22976eda5a226747a`。实际 permit SHA `b00e367be4f06f81a6e8d2e86b72d058c2d6e59e84729637d7f03a8f50594d9e`；该许可绑定旧 runtime，本次执行改变 runtime 后不得复用。

## 唯一实际命令

```powershell
wsl -d Ubuntu-22.04 -u evan-williams -- /home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B /home/evan-williams/deeph-m9/controls/source-build-v2/m9_source_build_v2_consumer.py run --build-operation-id a237ec1f2b404d898840c643e9ae501b --bucket none --cpu-bucket overlap_build --forecast-bytes 4294967296 --overlap-operation --overlap-action source_build --config /mnt/e/Projects/Codex/DeepH/06_reproduction/configs/m9_overlap_only_contract.json
```

宿主 exec session 为 `34271`，初始返回运行中，随后只轮询同一会话；最终宿主工具报告 exit_code=1。没有再次启动命令。正式 transaction 中子进程 exit_code=1、timed_out=false；冻结 budget 的非超时失败分支按代码返回125，但本次未独立采集该层 `$LASTEXITCODE`，不能把宿主会话1等同于 budget 的返回值，也不能据125推断超时。

transaction `38a891fff6fd07675581b891766e02c6`，action=source_build，bucket=overlap_build，forecast=4294967296 bytes。prepared_utc=`2026-08-31T07:27:33.075063Z`，child start=`2026-08-31T07:27:43.855704Z`，child end=`2026-08-31T07:27:45.423678Z`，elapsed=1.567928485秒，failure commit=`2026-08-31T07:27:49.420683Z`。最终 state=`FAILED_COMMITTED`，reason=`overlap_command_failed`。这些时间来自事务，不将入口验证耗时误记为子进程计量。

新 capability 为 `284bd6ba705e9b9bd9c4fa0f3c08290b`，consumed 文件 SHA `29533a038e4711706887e44b9d24bde36a34c9bfa274e9317ac5be672937c49e`，FAIL launcher receipt SHA `9a05a92597a30f3cd1e1fd4746cf1bc8e9c531dece812f24ab9f6297a25d12f9`。receipt 中的冻结源码加载、事务绑定和 traceback 均保留。

## 失败与只读诊断

实际异常为：

```text
ValueError: toolchain version mismatch: openmpi_showme_version='/usr/bin/mpicc: Open MPI 4.1.2 (Language: C)'
```

调用链为 source-only launcher → `m9_openmx_build.build_sources()` → `verify_packages()`。后者在旧冻结源码第281行对完整字符串严格比较；合同预期 `mpicc: Open MPI 4.1.2 (Language: C)`，实际冻结命令使用 `/usr/bin/mpicc --showme:version`，其输出前缀含绝对路径。拒绝发生在第574行的包与工具链检查，早于第595行之后的配置、构建与日志写入。

按 diagnose 流程，在禁止正式重放的前提下进行了只读最小对照。固定 PATH、LANG 和 LC_ALL 时，绝对路径调用得到 `/usr/bin/mpicc:`，短名称调用得到 `mpicc:`，均报告 Open MPI 4.1.2；实际解析路径为 `/usr/bin/opal_wrapper`。本次未改 PATH、合同、包装器或已安装版本。现有 `test_toolchain_version_drift_is_rejected` 在 gcc 负例即结束，不能证明真实 MPI 绝对路径输出的正例通过。后续修复应补足真实调用链回归及完整工具链只读预检；上述诊断不等于修复已经完成。

## 用量与现场

本次 CPU 原始 overlap_build 从7212.901214103001增至7214.469142588001秒，增量1.567928485秒。既有 apt 抵扣7200.075310528秒未改变，有效累计约14.393832060秒，剩余约7185.606167940秒。build/smoke/batch上限仍为7200/1800/21600秒；smoke和batch用量为0。GPU compatibility历史54.84820560599999秒，training和physical_validation仍为0；无新抵扣、额度重置或预算增加。

主端只读核验得到以下执行后 SHA：

| 对象 | SHA-256 |
| --- | --- |
| budget_state.json | `f4b08d2465cddee559664a98fe854289c4ef995ee873a590e6aba24b7f4cec01` |
| overlap_workflow_state.json | `60d0c789b3ac093c22245b277e532149ea8275c04781b492940998b02650a0cc` |
| overlap_transaction.json | `2920d80e431992cc8a23abe409d2d513b7a567e44651382d09a82b8af085161d` |
| budget_ledger.jsonl | `50334d8f6748816da3910e13fb31e12f5c31dbb9048871b2493a17785802b706` |

ledger现为65261 bytes；独立审计确认前序64298 bytes逐字节不变，尾部恰为一个963-byte `OVERLAP_HARD_STOP`。旧 source_prepare 成功事务原字节已封存在执行前证据中；本次事务槽合法更新为失败事务，不删除任何历史失败、成功或恢复记录。v1/v2安装、旧root-only权限和全部冻结来源均保持原样。

最终 [执行事实独立报告](M9_source_build_v2_execution_independent_audit.md) 为FAIL/BLOCKING=1/NON_BLOCKING=0，问题编号 `M9-SB-V2-EXEC-B01`，SHA `2bcf74043ae31d6cbe5e7165be139b0d7056f90a80451fb31cc1d5deed727829`。[执行后证据](M9_source_build_v2_postexecution_evidence.json) SHA `e6f02744745837ae200998cf6d1e7701283721e8ed64c550e98d58b416f5f325`。主端读回并核对文件SHA一致。独立审计确认169对象仅为167基线新增consumed及FAIL receipt，旧成员仅四项runtime和规定父目录变化，两树各5319项receipt全等；另行只读核验14包、gcc/gfortran、两个MPI wrapper和9工具路径均符合合同，但不证明未执行的构建通过。本记录不反向改写前序PASS报告，也不宣称M9或构建完成。

## 后续边界

当前只能整理证据与提出修复方案。建议另获明确授权后，在新版本工作包中精确修复输出前缀检查，保持绝对工具路径、Open MPI 4.1.2及其余软件/物理/预算合同不变，补充真实UID1000回归；独立审计修复与一次性恢复方案，封存本次失败后再执行和独立验收恢复、重建来源与消费门控。旧16/25/10/12文件manifest及其成员不得就地覆盖。上述恢复不包含再次编译，正式重试前仍应单独取得新的单次执行授权。

不放行500号结构smoke、450结构batch、overlap数据生成、GPU、训练、Hamiltonian/SCF或其他DFT标签。`M9-DATA-B01`继续OPEN。
