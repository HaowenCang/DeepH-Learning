# M9 一次性 source-control test cleanup 执行独立事实审计

## 结论

本轮执行后事实审计结论为 **PASS**：`BLOCKING=0`，`NON_BLOCKING=0`。正式现场与一次性 cleanup 的预期终态完全一致：active 伪对象缺席，retired 对象保留原内容和 inode 并加固为 root:root、0600、nlink 1；cleanup gate、root 私有 snapshot、安全迁移 journal、cleanup journal 与 retirement receipt 的哈希、schema、状态、路径、inode、snapshot、runtime 和时间绑定闭合；五项正式 runtime 未变化，source-control gate/parent 及 source/build 产物仍缺席，冻结闭集与 cache 条件均满足。

执行方记录的命令结果为 `rc=0`，stdout `status=test_artifact_retired`。本审计没有重放命令；独立确认的持久化终态与该记录一致。零问题 PASS 仅说明可以进入后续 source-control recovery 的准备阶段，不授权创建或执行后续 gate，不授权 source-control recovery、`source_prepare` 或其他运行时动作。

## Artifact 与目录终态

active 路径 `/home/evan-williams/deeph-m9/manifests/overlap_source_control_recovery.json` 不存在。retired 路径 `/home/evan-williams/deeph-m9/manifests/overlap_source_control_recovery.test-artifact.retired.json` 的独立实测结果为：

- SHA-256：`2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`
- 大小：1644 bytes
- UID/GID：0/0
- mode：0600
- nlink：1
- dev/inode：2096/153218

该 inode 与 cleanup 前 active 伪对象记录的 inode 153218 相同，证明本次终态来自同一对象的目录项迁移和权限加固，而非内容重建。manifests 目录实测为 UID 0、GID 1000、mode 1770；sticky bit 存在。root 私有 trust root `/root/deeph-m9-control/source-control-test-cleanup` 为 root:root、0700。

## Gate、snapshot 与迁移 journal

cleanup gate 为 root:root、0600、nlink 1、2713 bytes，SHA-256 为 `12cec1f13eec81c110b8a7d66aecaf4e1786c0821c82a702885b9e74cfeb57b2`。root 私有 snapshot 也是 root:root、0600、nlink 1、2713 bytes，SHA-256 相同；逐字节比较结果相等。

安全迁移 journal `/root/deeph-m9-control/source-control-test-cleanup/security_migration.json` 为 root:root、0600、nlink 1，SHA-256 为 `60fef9c099bfc345973bb9ac074f084f48e5e542508681fa4d55ceb099ba5c94`。其 schema 为 `m9-source-control-test-security-migration-v1`，state 为 `SUCCESS_COMMITTED`，path 与实际 journal 路径一致。

迁移 journal 的 `gate_inode` 为 dev 2096、ino 139156、2713 bytes、root:root、0600、nlink 1，与当前 cleanup gate 的实际 receipt 完全一致。`gate_sha256` 与当前 gate 及 snapshot SHA-256 相同。journal 中的 snapshot receipt 与实际 snapshot 的 path、bytes、SHA-256、UID/GID、mode、nlink 完全一致。其 parent after receipt 与实际 manifests 终态 root:gid1000、1770 一致，artifact active/retired 路径及 before/hardened 权限合同也与执行前后事实一致。

## Cleanup journal 与 retirement receipt

cleanup journal `/home/evan-williams/deeph-m9/manifests/overlap_source_control_test_artifact_cleanup.json` 为 root:root、0600、nlink 1，SHA-256 为 `1e0729d72bb7e45e773a61d9aff6228061a5b000cd218c23e5263153f2425d8d`。其 schema 为 `m9-source-control-test-artifact-cleanup-v1`，state 为 `SUCCESS_COMMITTED`。

retirement receipt `/home/evan-williams/deeph-m9/manifests/overlap_source_control_test_artifact_retirement.json` 为 root:root、0600、nlink 1，SHA-256 为 `74b24867d06a437f0e693c8edd231ab4bc31782b8978abfff77b01658567fd49`。其 schema 为 `m9-source-control-test-artifact-retirement-v1`，status 为 `PASS`，reason 为 `test_isolation_failure_artifact`。

cleanup journal 和 receipt 的 context 逐字段相等。两者均绑定同一 gate SHA、cleanup frozen SHA、授权 SHA、结构化审计 verdict SHA、artifact SHA、五项正式 runtime SHA、root:root 0600 文件安全合同、root:gid1000 1770 parent 合同、`protected_hardlinks=1` 及同一 verified snapshot receipt。该 context 又与安全迁移 journal 的 gate binding 和 cleanup gate 字段一致。

cleanup journal 的 original receipt 与 receipt 的 `original` 相同；retired receipt 与 receipt 的 `retired` 相同，且 retired receipt 与当前文件现场完全一致。original 与 retired 在 bytes、SHA-256、UID/GID、mode、nlink 上相同，仅路径按迁移合同变化。cleanup journal 与 receipt 的 Python bootstrap receipt 完全相同，并记录冻结 Python 3.9、isolated、no-site 和 dont-write-bytecode 均为 true。

四个 UTC 时间均可解析，且满足严格执行顺序：

- prepared：`2026-08-19T10:11:56.313212Z`
- retirement receipt：`2026-08-19T10:11:56.327625Z`
- cleanup completed：`2026-08-19T10:11:56.334969Z`
- security migration completed：`2026-08-19T10:11:56.342587Z`

## 正式 runtime 与 source/build 不变性

五项正式 runtime 的独立 SHA-256 为：

- budget state：`1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`
- workflow：`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`
- transaction：`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`
- ledger：`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`
- capability：`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`

上述值与 gate、迁移 journal、cleanup context、cleanup frozen manifest 及 cleanup 前基线完全一致。正式 source-control recovery gate 与 parent snapshot 仍不存在。

以下 source/build 产品均保持缺席，与 cleanup 前状态一致：`openmx-overlap-build`、`openmx-overlap-build.staging`、`env/hdf5-1.12.1`、`openmx_official_3.9.9_tree_manifest.json`、`openmx_overlap_tree_manifest.json`、`openmx_overlap_build_manifest.json`。因此没有证据表明 cleanup 触及 source 解包、HDF5 安装、OpenMX build 或相关 manifest。

source frozen manifest 登记对象为 `17/17` 匹配，cleanup frozen manifest 登记对象为 `4/4` 匹配。控制脚本目录中的 `.pyc`、`.pyo` 与 `__pycache__` 合计为零。

## 只读重复运行证据核对

未实际 replay cleanup。按照冻结实现的 terminal branch 逐项进行只读 predicate 核对：active 缺席、retired/receipt/cleanup journal/migration journal 均存在；两个 journal 均为 `SUCCESS_COMMITTED`；当前 retired receipt 同时等于 cleanup journal 与 retirement receipt 中的 retired receipt；original、context 和 bootstrap 交叉一致；gate inode、snapshot、runtime、parent 与文件安全合同均无漂移。所有 already-retired 返回前的终态证据条件均满足。因此现有现场具备重复运行时只读验证后返回的证据，但本审计没有通过实际重放扩大授权或改变状态。

## 最终判定与边界

本轮为 `BLOCKING=0`、`NON_BLOCKING=0`、PASS。一次性 cleanup 执行结果已通过独立只读事实审计，进入后续 source-control recovery 准备的前置审计条件已满足。本结论不授权创建或执行 source-control recovery gate，不授权 recovery、`source_prepare`、build、smoke、batch 或其他运行时动作；任何后续阶段仍需单独明确授权及其相应 gate。

本轮除新增本报告外未修改任何运行时或被审文件，未执行 gate、cleanup replay、source-control recovery 或 `source_prepare`。
