# M9 D-018 无总墙钟期限迁移执行事实独立审计

## 审计结论

**PASS**。`BLOCKING=0`，`NON_BLOCKING=0`。

正式一次性迁移已按冻结事务 `d018-unlimited-wall-clock-20260820-01` 成功提交。允许主 agent 机械创建 `m9-unlimited-wall-clock-execution-gate-v1` execution-fact gate；该 gate 必须绑定本报告、结构化 verdict 和本报告核实的完整迁移后 runtime，scope 只能为 `ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018`。

本结论不直接执行或放宽 `source_prepare`、`source_build`、smoke、batch、GPU 或通用命令。execution-fact gate 缺失、runtime 漂移、scope 不一致或 owner/group/mode/link 不满足冻结合同时，后继入口仍必须零写拒绝。

审计没有创建 execution-fact gate，没有执行任何 source/build/计算动作。最终持久化新增仅为本报告及其结构化 PASS verdict。

## 正式对象实测值

执行后正式对象的独立 SHA-256 和元数据如下：

| 对象 | SHA-256 | bytes | owner:group / mode / nlink |
|---|---|---:|---|
| `budget_state.json` | `c56532b1f92573bd4324464d0b10004df4b5f8337d1e803fdcd80a2f320585a8` | 2104 | `1000:1000 / 0644 / 1` |
| `overlap_workflow_state.json` | `bd895b2831c805c44a180012ece64bdda00744340768c7062e33b856069fda8a` | 722 | `1000:1000 / 0644 / 1` |
| `budget_ledger.jsonl` | `178106f0be9f80ff669ebd0865e214a4b9a60d115074ad0c97ae8de5f1ae33b7` | 60288 | `1000:1000 / 0644 / 1` |
| `overlap_transaction.json` | `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309` | 2347 | `1000:1000 / 0644 / 1` |
| `overlap_source_control_recovery.json` | `e9b8babcff8a2f42adea21d5cbce614b38f0854271d3389eae0bbcdd7d5e53bc` | 8383 | `1000:1000 / 0644 / 1` |
| `overlap_source_control_recovery_gate.json` | `8e66d65d17d3195f3df09db954afca4066c3ec91e2d8dad6d2aea06078d0d5ce` | 2398 | `0:0 / 0600 / 1` |
| active `overlap_work_package_audit_gate.json` | `78311a978c2472c85b35a745d80e1f33724c1500cf8d7bd244cdbe83c3fa3698` | 960 | `0:1000 / 0640 / 1` |
| retired old overlap gate | `dbe4756142d0e921c3834330550310e85652503c04254b30bea1a069ff35377c` | 804 | `1000:1000 / 0644 / 1` |
| formal D-018 migration gate | `286a0e409a80f85ca6bb39b76bdb977fc67ffa56f4646b00d3aad5943c98e880` | 2114 | `0:1000 / 0640 / 1` |
| D-018 transaction | `41cbfbd4da1c3a0eea92731a00758355f46321d5b0a66260f53f628290d847ad` | 3835 | `0:1000 / 0640 / 1` |
| root-private migration journal | `27a92edded459948150c750a4339692434e08a84cbc8879c63c71b6c14cb0e8a` | 4896 | `0:0 / 0600 / 1` |
| root-private pre-state snapshot | `00a32bd7f28ad26fa600c8abe9d0fa64efe57e410eacb82ad2d201fa9adc5439` | 1422 | `0:0 / 0600 / 1` |

固定代码的 `verify_unlimited_wall_clock_execution_ready()` 对该正式状态独立返回 `SUCCESS_COMMITTED` 和同一 transaction ID。测试前后上述十二项 SHA-256 全部保持不变。

## transaction 与 journal

transaction 和 journal 均为 `SUCCESS_COMMITTED`，transaction ID、event ID、policy、gate receipt、pre-runtime、snapshot receipt、retired/replacement gate receipt、ledger commit、迁移后 state SHA、journal context 和完成时间互相一致。transaction 记录的 journal SHA-256 与 root-private journal 实测 SHA-256 均为 `27a92edded459948150c750a4339692434e08a84cbc8879c63c71b6c14cb0e8a`。

迁移 bootstrap 明确记录并独立核对为：

- Python：`/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9`；
- `isolated=true`、`no_site=true`、`dont_write_bytecode=true`；
- `sys.path` 仅含冻结 Python 的 zip、stdlib 和 `lib-dynload`；
- `argparse`、`hashlib`、`json`、`pathlib` 四个 stdlib 源文件的现有 SHA-256 均与 journal receipt 相同。

不存在 FAILED transaction、第二事务、第二迁移事件或中间 journal 状态。

## ledger prefix 与唯一事件

迁移前 ledger 长度为 59097 字节，SHA-256 为 `dbc54580fc6e215319c3af8d33b7f803448baa50a928ee4a60151782c9fd5e3b`。执行后 ledger 的前 59097 字节独立重算仍得到同一 SHA-256，说明历史 prefix 逐字节保留。

prefix 后只有一个 1191 字节 canonical JSON 事件，SHA-256 为 `4cab5bf1d53723d2f0e70c7075b38da795b1828e79f463888645373a67e94194`。全 ledger 中 event ID `d018-unlimited-wall-clock-20260820-01:unlimited-wall-clock` 仅出现一次；其 payload 为 `M9_UNLIMITED_WALL_CLOCK_MIGRATION`，绑定 D-018、原始 start/deadline、604800 秒历史限制、正式 gate SHA、pre-state SHA 和完整 UNLIMITED policy。最终长度 60288 字节和 SHA-256 `178106f0be9f80ff669ebd0865e214a4b9a60d115074ad0c97ae8de5f1ae33b7` 与 transaction/journal 完全一致。

## state、预算与历史用量

root-private pre-state snapshot 与迁移前 `budget_state.json` SHA-256 完全相同。将 snapshot 与迁移后 state 做结构化逐键比较，差异严格只有：

- 新增冻结的 `wall_clock_policy`，mode 为 `UNLIMITED`；
- `last_event_utc` 更新为唯一迁移事件时间 `2026-08-20T15:04:56.681598Z`。

原 `start_utc=2026-08-11T14:50:05.7533015Z`、`deadline_utc=2026-08-18T14:50:05.7533015Z` 和 604800 秒限制均保留为历史证据。下列内容逐值未变：

- raw CPU：`overlap_build=7200.791086107`、`overlap_smoke=0`、`overlap_batch=0`；
- 原 CPU credit：`7200.075310528` 及其 D-017 parent、decision、时间和 adjustment ID；
- GPU：compatibility `54.84820560599999` 秒，training 和 physical-validation 均为 0；
- VHDX 起始 baseline、overlap storage baseline、恢复标记、全部失败与恢复证据；
- `hard_stopped=false`、`active_overlap_transaction=null`。

固定 status 独立输出 `wall_clock_mode=UNLIMITED`、`deadline_remaining_seconds=null`、`violations=[]`。CPU/GPU/存储预算常量和 baseline 没有重置或增加；取消墙钟没有转化为新 CPU/GPU/存储额度。

## D-017、workflow 与 gate 迁移

workflow SHA-256 与迁移前完全相同，仍为 `AUDIT_PASSED`、`hard_stopped=false`、`active_transaction=null`。D-017 source-control recovery transaction 和 root-private D-017 gate SHA-256 均与正式 migration gate 的 pre-runtime 绑定相同；recovery transaction 仍为 `SUCCESS_COMMITTED`、`ledger_phase=COMMITTED`，其 post-state、post-workflow 和 post-ledger SHA 分别等于 D-018 的三项 pre-runtime SHA。

历史 `overlap_transaction.json` 仍为先前的 `FAILED_COMMITTED source_prepare` 证据，SHA-256 未变；本次迁移没有覆盖、伪装或重置该证据。state/workflow 当前均无 active transaction。

旧 overlap gate 的执行前 receipt 绑定 `dev:ino=2096:1163`。retired 文件实测仍为同一 `2096:1163`、同一 804 字节、同一 SHA-256、owner、mode 和单链接属性。新 active gate 由当前 overlap frozen manifest、D-018 结构化 PASS verdict、授权记录和旧 overlap work package 独立确定性重建，所得 960 字节与正式 active gate 逐字节相同，SHA-256 为 `78311a978c2472c85b35a745d80e1f33724c1500cf8d7bd244cdbe83c3fa3698`。

UID1000 对新 active gate 和 D-018 transaction 均可读、不可写；manifest 目录为 `root:evan-williams/1770`，sticky bit 与 root ownership 阻止 UID1000 替换 root-owned active gate。

## 正式 gate 与冻结证据

正式 migration gate 为 root:UID1000、0640、单链接对象，SHA-256 为 `286a0e409a80f85ca6bb39b76bdb977fc67ffa56f4646b00d3aad5943c98e880`。其绑定均独立复算通过：

- 授权记录 SHA-256：`8655037c3dee93f4ae0f9819e7409ff373ff660ed110f8cee25cde68dddd7b9a`；
- D-018 contract SHA-256：`2b451c42c2401a220d19038af2ee6ba1843106508f8b057b8ce5dd2584fccff4`；
- D-018 frozen manifest SHA-256：`f41553b6112482df1cb0bbb52e3311d6a60514b6f61252526924fa930489f4f9`；
- migration audit verdict SHA-256：`0d36aa2cbe21a27cdd5c11d8f20eb942af2874a6b98082ac149490f437fe290c`；
- 第二次定点复核报告 SHA-256：`5209d6bda24e00634a27f60fc409eb1d792f334f0cacb3ffc6ef515290759292`；
- migration work package SHA-256：`e23d59ea673421e1b2ca4755b3ea91806c7c7ba04573141d2ebdf3ff40f80ef3`。

D-018 frozen manifest 27/27、overlap frozen manifest 16/16 成员均存在且哈希匹配。正式 gate 的 pre-runtime 与 pre-state、workflow、ledger、overlap transaction、D-017 transaction/gate 和旧 overlap gate 的实测迁移前 receipt 全部一致。

## 产品缺席与回归测试

以下六项 source/build 产品全部缺席：

- `software/openmx-overlap-build`；
- `software/openmx-overlap-build.staging`；
- `env/hdf5-1.12.1`；
- `manifests/openmx_official_3.9.9_tree_manifest.json`；
- `manifests/openmx_overlap_tree_manifest.json`；
- `manifests/openmx_overlap_build_manifest.json`。

`overlap_unlimited_wall_clock_execution_gate.json` 缺席；未创建新的 source_prepare transaction 或 active capability。capability 目录只有既有 D-017 retired capability，未出现 active `.json` capability。

固定 Python 在迁移后独立全量重放结果为：

```text
Ran 109 tests in 29.291s
OK
```

测试前后十二个正式迁移对象 SHA-256 全部不变；控制脚本目录 cache 数为 0。测试未执行正式迁移 replay、source_prepare、build、smoke、batch 或 GPU 动作。

## 门控许可

允许主 agent 机械创建一个 root:UID1000、0640、单链接的 execution-fact gate。该 gate 应绑定：

- 本报告和结构化零问题 PASS verdict；
- 当前 state、workflow、ledger、overlap transaction、D-017 transaction/gate；
- formal D-018 gate、SUCCESS transaction、SUCCESS journal、pre-state snapshot；
- retired old gate、new active overlap gate；
- 六项 source/build 产品缺席事实。

除上述机械 gate 创建外，若任何正式对象在创建 gate 前发生漂移，本 PASS 自动失效，应重新执行事实审计，不得继续 `source_prepare`。

