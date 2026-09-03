# M9 Python 3.9 恢复后单次 source_prepare 用户授权

授权日期：2026-08-30。当前任务：`019fc7b8-cd95-7d20-84d0-229e2a73749e`。

## 授权依据与范围

上一条明确请求为：“是否授权执行一次 `source_prepare`，仅校验、解包并准备已冻结的本地源码，不下载、不编译、不运行结构计算，继续计入原预算？”用户随后回复：“授权”。本记录将该回复绑定到上述单次动作，不推定用户授权任何其他动作。

前置独立安装事实审计为 `PASS/BLOCKING=0/NON_BLOCKING=0`，报告为 `08_audits/M9_py39_consumer_gate_completion_execution_independent_audit.md`，SHA-256 为 `798ada7ed0c8835cc56b28d168188d61688e21d2ecdfacfb4d56ac6da660bcdc`。真实 UID1000 已能验证已安装 gate；本次仍须在签发授权及执行前复核实际 gate、冻结来源、runtime 和预算。

允许的唯一动作是校验已冻结的本地 OpenMX 3.9、官方 3.9.9 补丁和 HDF5 1.12.1 源码包，安全解包，应用官方补丁，生成冻结 makefile 与来源清单，并提交 `SOURCES_PREPARED`。不允许下载、source build、smoke、batch、GPU、训练、Hamiltonian、SCF 或其他 DFT 标签生成。执行返回后停止并由独立子 agent 审计；失败、超时或拒绝后不自动重试，不清理失败证据。

D-018 的总墙钟策略仍为 `UNLIMITED`，不重置或增加 CPU、GPU、存储预算。此次执行计入原 `overlap_build` CPU 子预算，GPU bucket 为 `none`，存储预测为 `1073741824` bytes；历史原始用量、此前已批准的抵扣、失败与恢复证据全部保留。

## 单次绑定

- schema：`m9-source-prepare-py39-single-run-authorization-v1`。
- decision：`D-018-PY39-CONSUMER-REPLACEMENT`。
- scope：`ALLOW_EXACTLY_ONE_SOURCE_PREPARE`。
- operation id：`f9824f0eb63e41f19699c1114b13537e`。
- authorization nonce：`2c1c2cd40cdd5d0823fb7ad7f6ac5d6f9d39d4fa762f9d7588a5e1ebe92f1c33`。
- 授权对象固定路径：`/home/evan-williams/deeph-m9/manifests/overlap_source_prepare_py39_single_run_authorization.json`。
- 本记录固定路径：`/mnt/e/Projects/Codex/DeepH/08_audits/M9_source_prepare_py39_fresh_user_authorization.md`。
- readiness consumer gate SHA-256：`520a8cffcab9c91400647e486de796853d8a00073892e3a4b0472cafbf9dd5c9`。
- active overlap gate SHA-256：`229f0846c3d22917ccb955729a577168880bca6a53ad07f32502b0ae4a4e27ab`。

root 签发的授权对象须严格符合既有 12 字段 schema，并绑定本记录 SHA-256、上述 consumer/active gate、当前 runtime canonical SHA-256、operation id、nonce 和唯一 action。若现有授权路径或其临时路径已存在，不覆盖，不自动续签。任何漂移都应停止，不能重置状态以使授权通过。

## 唯一完整动作参数

以 WSL `Ubuntu-22.04` 中真实 `evan-williams` UID1000、冻结 Python 3.9.23 执行以下命令一次；不存在自由子命令、结构编号、额外 cwd 或 log 参数。

```bash
/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B \
  /home/evan-williams/deeph-m9/controls/uid1000-consumer-py39-v2/m9_budget_uid1000_consumer.py \
  run --consumer-operation-id f9824f0eb63e41f19699c1114b13537e \
  --bucket none --cpu-bucket overlap_build --forecast-bytes 1073741824 \
  --overlap-operation --overlap-action source_prepare \
  --config /mnt/e/Projects/Codex/DeepH/06_reproduction/configs/m9_overlap_only_contract.json
```

该授权不改变旧 consumer gate、失败事务或历史授权的含义；实际一次性动作由当前 runtime 绑定、既有预算锁、预算事务及子进程 capability 共同限制。本记录完成签发后保持字节不变，后续结果另写执行事实记录。
