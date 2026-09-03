# M9 D-018 UID1000 consumer 正式机械安装执行事实独立审计

审计日期：2026-08-21  
审计对象：正式 root bootstrap trust set、完整 UID1000 consumer snapshot、consumer gate 及其执行前运行态  
审计方式：实际文件 SHA-256 与 metadata 独立复算、两级目录闭集与 receipt/manifest 逐项重建、27 项 snapshot payload 对源字节复核、consumer gate 确定性重建、真实 EUID 1000 verifier、execution-fact/runtime 绑定复算、source_prepare 零执行证据、固定 Python 全量回归及正式对象测试前后零漂移核对  
执行边界：本审计只读；未执行 `source_prepare`、`source_build`、smoke、batch、GPU 或其他计算；未创建、修改或替换任何正式运行对象

## 审计结论

**PASS**。`BLOCKING=0`，`NON_BLOCKING=0`。

正式 bootstrap trust set、完整 snapshot 与 consumer gate 均与第三次独立定点复核冻结对象严格一致。两个目录均为 root:group1000、`0550`；全部成员均为 root:group1000、`0440`、普通文件、`nlink=1`；consumer gate 为 root:group1000、`0640`、普通文件、`nlink=1`。bootstrap receipt、六个审计哈希、27 项 snapshot source、snapshot manifest、PASS verdict、第三次报告、工作包、consumer frozen manifest、授权与既有 execution-fact gate 的绑定全部复算通过。

以真实 EUID 1000 和冻结 Python `-I -S -B` 从 installed snapshot 加载 adapter，`verify_consumer_gate()` 返回正式 consumer gate SHA-256 `2ba96b8566f2ba38a528e4002dbaa0bebf4f9a7b8c5f10a92b89d643d11a85f2`。固定回归 109/109 与 14/14 通过，监测的 50 个新旧正式对象测试前后 inode、metadata、字节数与 SHA-256 完全一致。六项 source/build 产品仍缺席；没有新 source_prepare transaction、活动 capability、consumed capability 或 launcher receipt；没有 source/build 进程。

因此，允许下一步严格从 installed snapshot、以 UID1000 和冻结 Python `-I -S -B`，按现有预算/事务/launcher 控制仅执行一次 `source_prepare`。执行结束后，无论成功、失败、超时或控制拒绝，都必须立即停止，不得自动进入 `source_build`，并将 transaction、capability/consumed/launcher receipt、ledger、state/workflow、六项产品、进程及预算用量提交同一独立审计员作执行事实审计。

本报告不授权 `source_build`、smoke、batch、GPU、Hamiltonian/SCF 标签、正式训练、数据下载或任何通用命令。

## 正式对象清单与 metadata

### Bootstrap trust set

正式目录：`/home/evan-williams/deeph-m9/controls/uid1000-consumer-bootstrap`

目录实测为 root:group1000、`0550`、真实目录，闭集恰为六个成员：

| 成员 | SHA-256 | bytes | uid:gid / mode / nlink |
|---|---|---:|---|
| `m9_uid1000_consumer_bootstrap.py` | `681901e066055411f2ea03f5fc8441697288c7be369fbde272c626d9905002b5` | 11824 | `0:1000 / 0440 / 1` |
| `m9_uid1000_consumer_install.py` | `acb06c9bc4d7ae6549b43c52ff50e957212c947c9a1cab53e50b373a66e62201` | 19688 | `0:1000 / 0440 / 1` |
| `m9_budget_uid1000_consumer.py` | `72297aff63ea0affc5f38b2bc15f94f7bcab4771e8a8634b529704b71b5c7524` | 19610 | `0:1000 / 0440 / 1` |
| `M9_unlimited_wall_clock_uid1000_consumer_final_verdict.json` | `edc3c9050ab5ca73ec6e145b4da02f78733d10266f7950a6e693b6cf04a2eee7` | 595 | `0:1000 / 0440 / 1` |
| `M9_unlimited_wall_clock_uid1000_consumer_third_targeted_reaudit.md` | `602c47cf4b4c8504b32ac747f75397a33561214f3d20e736f0543ea004920d75` | 12390 | `0:1000 / 0440 / 1` |
| `bootstrap_receipt.json` | `3172bf9516fed5dd2abb3669c705211428cbe6ebeea34fe96fcb6a3016d5f1ba` | 1347 | `0:1000 / 0440 / 1` |

没有 symlink、hardlink 或额外目录项。`uid1000-consumer-bootstrap.staging` 按 `lexists` 缺席。

### Snapshot

正式目录：`/home/evan-williams/deeph-m9/controls/uid1000-consumer`

目录实测为 root:group1000、`0550`、真实目录，闭集为 28 个成员：27 个 source snapshot 加一个 `snapshot_manifest.json`。28 个成员全部为 root:group1000、`0440`、普通文件、`nlink=1`。snapshot manifest 实测为：

- schema：`m9-uid1000-consumer-snapshot-v1`；
- decision：`D-018`；
- issue：`D018-EGF-B01`；
- SHA-256：`2d13e0c1fb1c1e635ad1730f44f21901340e7483d06356aa8eeb0e07f83dcec9`；
- bytes：9022；
- `files`：27 项，键集合与 `CONSUMER_SNAPSHOT_SOURCES` 完全相等。

独立从 trusted installer 只读调用 `verify_trusted_bootstrap()` 与 `verify_authorized_sources()`，获得 27 项授权 payload；逐项通过 snapshot manifest 定位成员，复核 snapshot path、bytes、SHA-256、实际 payload 与授权 payload 全部相等。snapshot 目录名集合也与 manifest 推导集合加 manifest 本身完全相等。没有 symlink、hardlink、路径逃逸或未登记成员；`uid1000-consumer.staging` 按 `lexists` 缺席。

## Bootstrap receipt 与六哈希绑定

`bootstrap_receipt.json` 字段闭集为 `schema_version`、`decision_id`、`frozen_hashes_sha256`、`members`，其语义为：

- schema：`m9-uid1000-consumer-bootstrap-v1`；
- decision：`D-018`；
- frozen manifest：`8916df81d334718b12f9b6949425e6875809066b3c99841b6e235325b4ada40b`；
- members：bootstrap、installer、adapter、PASS verdict、第三次独立报告五项，每项 bytes 与 SHA-256 均等于 trust set 实际字节。

工作包 single-FD loader 所需六个哈希由 receipt 与安装字节共同闭合：bootstrap、installer、adapter 三项来自 24/24 consumer frozen manifest；frozen manifest 自身 SHA 与 receipt 相等；PASS verdict 与第三次报告的实际 SHA 分别为 `edc3c905...2eee7` 与 `602c47cf...20d75`，与 receipt 及 root-owned 成员一致。

PASS verdict 的 schema 为 `m9-unlimited-wall-clock-uid1000-consumer-audit-verdict-v1`，decision 为 `D-018`，结论为 `PASS/BLOCKING=0/NON_BLOCKING=0`。它绑定：

- 当前工作包 SHA-256 `cf545ae65954f4bd6978abe0429d66b7a209ca8be11b2e76f45b15a7765193e2`；
- 第三次独立报告 SHA-256 `602c47cf4b4c8504b32ac747f75397a33561214f3d20e736f0543ea004920d75`。

以上对象同时存在于完整 snapshot，并与项目冻结源逐字节相等。

## Consumer gate 与确定性重建

正式 gate：`/home/evan-williams/deeph-m9/manifests/overlap_unlimited_wall_clock_uid1000_consumer_gate.json`

实测属性：root:group1000、`0640`、普通文件、`nlink=1`、4283 bytes、SHA-256 `2ba96b8566f2ba38a528e4002dbaa0bebf4f9a7b8c5f10a92b89d643d11a85f2`。

gate 字段闭集、schema、decision、PASS/0/0 与唯一 scope `ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018` 均正确。它直接绑定：

- consumer frozen manifest：`8916df81...ada40b`；
- snapshot manifest：`2d13e0c1...3dcec9`；
- PASS verdict：`edc3c905...2eee7`；
- D-018 authorization：`8655037c...d7b9a`；
- execution-fact gate：`bc51209c...be6e9`；
- D-018 transaction：`41cbfbd4...d847ad`；
- 九项 UID1000 可读 runtime 的完整 path/bytes/SHA/uid/gid/mode/nlink receipt。

独立使用 root-owned trusted installer 的 `build_consumer_gate()` 对正式 snapshot 和当前运行态只读重建 gate，再以代码冻结的 `json.dumps(..., ensure_ascii=False, indent=2) + "\n"` 编码。重建字节与正式 gate 逐字节相同，重建 SHA-256 同为 `2ba96b8566f2ba38a528e4002dbaa0bebf4f9a7b8c5f10a92b89d643d11a85f2`。因此 gate 不是仅在字段意义上近似一致，而是当前冻结输入的唯一确定性产物。

## Execution-fact 与运行态绑定

既有 execution-fact gate 保持 `m9-unlimited-wall-clock-execution-gate-v1`、`PASS/0/0` 及相同 scope。其 13 项 runtime canonical SHA-256 独立复算为 `ed579067a25ab7f65e6f59aafc7ac1b2c5b7759a662e9c83709a630e2711578c`，与 consumer gate 的 `sealed_execution_runtime_sha256` 相等。consumer runtime 与 execution runtime 的八个 receipt SHA 交集为 8/8 相等，双方的 `source_products_present` 均为空列表。

当前语义状态为：

- wall-clock policy：`UNLIMITED`；
- budget：`hard_stopped=false`，`active_overlap_transaction=null`；
- workflow：`AUDIT_PASSED`、`hard_stopped=false`、`active_transaction=null`；
- D-018 transaction：`SUCCESS_COMMITTED`。

13 项历史正式对象保持既有 SHA-256：

| 正式对象 | SHA-256 |
|---|---|
| budget state | `c56532b1f92573bd4324464d0b10004df4b5f8337d1e803fdcd80a2f320585a8` |
| workflow | `bd895b2831c805c44a180012ece64bdda00744340768c7062e33b856069fda8a` |
| ledger | `178106f0be9f80ff669ebd0865e214a4b9a60d115074ad0c97ae8de5f1ae33b7` |
| overlap transaction | `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309` |
| D-017 recovery transaction | `e9b8babcff8a2f42adea21d5cbce614b38f0854271d3389eae0bbcdd7d5e53bc` |
| D-017 gate | `8e66d65d17d3195f3df09db954afca4066c3ec91e2d8dad6d2aea06078d0d5ce` |
| active overlap gate | `78311a978c2472c85b35a745d80e1f33724c1500cf8d7bd244cdbe83c3fa3698` |
| retired overlap gate | `dbe4756142d0e921c3834330550310e85652503c04254b30bea1a069ff35377c` |
| D-018 migration gate | `286a0e409a80f85ca6bb39b76bdb977fc67ffa56f4646b00d3aad5943c98e880` |
| D-018 transaction | `41cbfbd4da1c3a0eea92731a00758355f46321d5b0a66260f53f628290d847ad` |
| D-018 execution-fact gate | `bc51209c13570839c08dd4fc304fe39865a98ade69caeb23886602de2d8be6e9` |
| D-018 journal | `27a92edded459948150c750a4339692434e08a84cbc8879c63c71b6c14cb0e8a` |
| D-018 pre-state snapshot | `00a32bd7f28ad26fa600c8abe9d0fa64efe57e410eacb82ad2d201fa9adc5439` |

该结果证明机械安装没有重置或增加 CPU/GPU/存储预算，没有修改 raw usage、credit、ledger、D-017/D-018 证据或无墙钟政策。

## 真实 UID1000 verifier

独立实际命令环境满足：

```text
EUID=1000
PYTHON=/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9
FLAGS=isolated:1,no_site:1,dont_write_bytecode:1
```

从 installed snapshot 的 `m9_budget_uid1000_consumer.py` 加载并调用 `verify_consumer_gate()`，结果为：

```text
GATE_SHA=2ba96b8566f2ba38a528e4002dbaa0bebf4f9a7b8c5f10a92b89d643d11a85f2
EXECUTION_GATE_SHA=bc51209c13570839c08dd4fc304fe39865a98ade69caeb23886602de2d8be6e9
SCOPE=ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018
STATUS=PASS
UID1000_VERIFY_RC=0
```

该子进程没有读取 root-private D-017 gate、D-018 journal 或 pre-state snapshot；历史 root-private 权限没有降低。

## Source_prepare 零执行证据

按 `lexists` 检查，以下六项 source/build 产品全部缺席：

- `software/openmx-overlap-build`；
- `software/openmx-overlap-build.staging`；
- `env/hdf5-1.12.1`；
- `manifests/openmx_official_3.9.9_tree_manifest.json`；
- `manifests/openmx_overlap_tree_manifest.json`；
- `manifests/openmx_overlap_build_manifest.json`。

budget state 与 workflow 的 active transaction 均为 null。`overlap_transaction.json` 仍是 D-017 历史失败事务，SHA-256 保持 `12f475b7...b66309`；机械安装没有建立新 source_prepare transaction。capability 目录中唯一成员是历史 D-017 已退休的 `f7c3b060e19e37e6da03f461d754d38c.retired.json`，不存在活动 `.json`、`.consumed.json` 或 `.launcher-receipt.json`。独立 `/proc` 扫描未发现 source launcher、OpenMX build 或 OpenMX 进程。

因此，现有证据支持“机械安装只创建 bootstrap/snapshot/gate，尚未消费 gate 或执行 source_prepare”。

## 安装后回归与零漂移

在正式安装完成后，以 root 和冻结 Python `-I -S -B` 独立重放：

```text
Ran 109 tests in 40.716s
OK

Ran 14 tests in 12.358s
OK
```

审计在测试前后同时记录 13 项历史运行态、consumer gate、bootstrap 目录及六成员、snapshot 目录及 28 成员，共 50 个正式对象的 `st_dev`、`st_ino`、mode、uid、gid、nlink、size 与 SHA-256。结果为 50/50 完全一致。项目 controllers/scripts/tests 及两个正式只读目录中的 `__pycache__` 数量为 0。

## 下一步授权边界

本报告明确允许下一步**只执行一次** UID1000 `source_prepare`，并附加以下强制条件：

- 必须从 installed snapshot 入口启动；
- 必须使用冻结 Python `-I -S -B`、EUID 1000、既有 budget lock、consumer gate 与 D-017 action API；
- action 只能是 `source_prepare`，不得携带自由 shell argv；
- 不得同时或随后启动 `source_build`、smoke、batch 或 GPU；
- 执行一旦返回、失败、超时、hard-stop 或出现控制异常，必须立即停止；
- 停止后应由同一独立审计员核对 transaction、state/workflow、ledger exactly-once、capability/consumed/launcher receipt、source 产品、残留进程、CPU/存储用量和失败恢复边界，再决定是否允许 `source_build`。

因此，本轮门控仅从“允许机械安装”推进到“允许一次 source_prepare”。它不构成 source build 或任何后续 M9 动作的授权。
