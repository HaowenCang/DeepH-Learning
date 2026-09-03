# M9 source_prepare Python 3.9 一次性恢复执行事实独立审计

审计日期：2026-08-28  
审计对象：正式一次性 recovery 的持久化执行事实  
审计方式：固定 Python 3.9 `-I -S -B` 下的稳定 FD receipt、控制对象内容、ledger prefix/event、state/workflow 精确目标、retired closed-set、不可变历史证据与正式现场前后 aggregate fingerprint 对照  
执行边界：未调用 `create-gate`、`recover`、`source_prepare`、`source_build`、安装、下载或任何正式运行态写入命令；未使用 `py_compile`；项目内仅新增本报告

## 结论

**verdict：PASS。`BLOCKING=0`，`NON_BLOCKING=0`。**

独立证据确认，主 agent 报告的单次正式调用已完整提交为 `source_prepare_py39_recovered`，recovery ID 为 `m9-source-prepare-py39-recovery-20260827-01`。恢复状态机已到达唯一 `SUCCESS_COMMITTED` 终态；失败证据、预算历史与旧控制对象保持不变；staging 仅通过同一 closed-set 的 retired 路径保存；ledger 恰好新增一个 canonical recovery event；state/workflow 仅发生合同允许的变化。未发现半提交、重复事件、证据重绑定、未授权产品或活动计算进程。

本 PASS 只确认 recovery 已按审计合同发生，不授权 `source_prepare`、`source_build` 或其他计算。

## 1. Gate 与授权绑定

正式 gate `/root/deeph-m9-control/source-prepare-py39-recovery-gate.json` 为 root:root、mode `0600`、nlink 1 的普通文件；receipt 为 11,476 bytes、`st_dev=2096`、`st_ino=130280`，SHA-256：

```text
6a887aafc84ec6bbb558423159faac86f971265497ea79d5d9bd147a8263b73d
```

控制器的只读 `load_gate()` 校验通过。gate 精确绑定：

| 对象 | SHA-256 |
|---|---|
| PASS verdict | `665d83d24dee5ae894afd48e4b24c228ac84ca8a05f89b8add649f8573efb508` |
| R02 第二次定点复核报告 | `b5d7a15ccbb0fa0f80543f29a824265130968496f208e4af8e12c0cccd0039c3` |
| recovery work package | `804406a561b7f86ce46321aa3286552ddeabf07b430e3f29736570f9b9f7a72d` |
| 22 文件 frozen manifest | `9923f68e77e5ad63350af84ed42c9eac1826621f6c5a9a0c9b48df6d4c875d8d` |

gate 内 19 个 pre-runtime receipts 与 recovery contract 的 19 项逐字段相等。冻结 manifest 逐文件重算为 22/22 匹配。gate receipt 又被 terminal journal/transaction 原样持久化，未发生授权对象替换。

## 2. 终态控制对象与状态机

recovery journal 与 recovery transaction 均为 root:root、mode `0600`、nlink 1 的普通文件，大小均为 9,845 bytes；两者字节完全相等，SHA-256 同为：

```text
75daebc349615fb9599120002f2df11a8acd01e630aa6a703cc9fe5aad1a6a8b
```

两者均为 `SUCCESS_COMMITTED`，并一致绑定 decision `D-018`、failure transaction `80e28da82f076f4f7b1811f5897216bd`、recovery ID、recovery UTC `2026-08-28T10:02:59Z`、gate receipt、19 项 pre receipts、原 staging inventory、固定 retired 路径、ledger event、`post_ledger`、`post_state`、`post_workflow` 及 retired inventory。当前 ledger/state/workflow 的完整 receipts 分别逐字段等于 terminal 中持久化的 post receipts；未发现续提重绑定。

## 3. 失败证据与不可变历史

root-private failure snapshot 为 root:root、mode `0600`、nlink 1，大小 2,347 bytes；其字节与原 `/home/evan-williams/deeph-m9/manifests/overlap_transaction.json` 完全相等，SHA-256 均为：

```text
0a982e876e43768c6069fdeafd07e6e43ae03be3b1a0abc8584aa8d137bbcae7
```

原失败 transaction 仍为 `FAILED_COMMITTED`。consumed capability SHA-256 `7a3e21145fa31b2613d5d1a740e56ead4e28c3b06b3b371d529a7fbb77ebd905`，FAIL launcher receipt SHA-256 `8217945664427eea38d7f546fa5a91689701a989601fbe539951214f7e872924`。consumer gate、bootstrap receipt、snapshot manifest、D-017 transaction/gate、active/retired overlap gate、D-018 gate/transaction/execution gate/journal/pre-state snapshot 均保持 recovery contract 的 pre receipts；这些不可变对象的 SHA、bytes、owner/group、mode、nlink 及合同绑定的 inode 身份无漂移。

`budget.lock` 仍为合同和 gate 绑定的原对象：SHA-256 为 empty-file hash `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`，当前完整 receipt 与 pre receipt 相等，锁 inode 未被替换。

## 4. Staging retirement

原 `/home/evan-williams/deeph-m9/software/openmx-overlap-build.staging` 已按 `lexists` 缺席；固定 retired 路径存在：

```text
/home/evan-williams/deeph-m9/software/openmx-overlap-build.failed-80e28da82f076f4f7b1811f5897216bd.retired
```

稳定 `lstat` 与递归复算确认 root 为真实目录，闭集内没有 symlink 或特殊对象；每条记录的 mode、uid/gid、nlink、size 与普通文件 SHA 均进入 inventory hash，因此当前闭集不存在未绑定的 hardlink 或权限漂移。复算结果与 gate 中原 staging inventory 及 terminal retired inventory 完全一致：

| 指标 | 结果 |
|---|---:|
| directories | 140 |
| regular files | 5,179 |
| records | 5,319 |
| apparent bytes | 619,112,384 |
| allocated bytes | 632,029,184 |
| inventory SHA-256 | `0c0389f29f3a87e26af3c884b13bcc7c6dc6f183b50d803b9affa5fbd4e3920e` |

路径归一化回原 staging root 后，inventory 与恢复前 closed-set 逐字段相等；没有复制后删除或内容重建的证据。

## 5. Ledger exactly-once 证据

当前 ledger 为 uid/gid `1000:1000`、mode `0644`、nlink 1，大小 61,826 bytes、64 行，SHA-256：

```text
5253620510f84d1987874c5fa571f6016cedfbdabc6e80a4b126e724839b1ea9
```

前 61,248 bytes 与失败现场 ledger 逐字节相等，SHA-256 仍为 `a2170772c37b601112f0d957a18a6e9375dc7cf2eb22697a26b61a5db3ed770d`。其后仅有一行；该行逐字节等于 terminal `ledger_event` 的 canonical JSON 加单个 LF，suffix SHA-256 为 `e802d39aa5e2fd82c4252fc21124c778088348ba55df57fb6e13cc2d3f8e7485`。事件为 `OVERLAP_SOURCE_PREPARE_PY39_RECOVERY`，event ID `m9-source-prepare-py39-recovery-20260827-01:recovery`，绑定原 failure transaction SHA、retired path 与 staging inventory SHA。全 ledger 中该 event ID 恰好出现一次，无 partial append 或重复提交。

## 6. State、workflow 与预算历史

当前 budget state 为 uid/gid `1000:1000`、mode `0644`、nlink 1，2,195 bytes，SHA-256 `f51960808c7e0c518972cd717ae94fbc2a070be57638862c4b143970f3223e73`。相对 gate 的 `pre_state`，实际变化键只有：

```text
hard_stopped
last_event_utc
recovered_from_source_prepare_py39_failure
```

`hard_stopped=false`，`active_overlap_transaction=null`，恢复 ID 与 recovery UTC 正确；active 字段在恢复前后均为 null，故不构成字节差异。由 `pre_state` 构造合同目标后与当前 state 全对象相等。CPU limits/raw usage、唯一 credit、GPU limits/usage、storage 证据及 `UNLIMITED` wall-clock policy/history 均与 pre-state 完全相等。

当前 workflow 为 uid/gid `1000:1000`、mode `0644`、nlink 1，709 bytes，SHA-256 `384a4de85803666e305ca55b38dd6966c40244f789ac887a52b5a282095e2492`。相对 `pre_workflow`，实际变化键只有 `stage`、`hard_stopped` 与 recovery ID；当前 `stage=AUDIT_PASSED`、`hard_stopped=false`、`active_transaction=null`。由 pre-workflow 构造合同目标后与当前 workflow 全对象相等。

## 7. 产品、进程、cache 与零写入

合同列出的五项 source/build 终态产品全部按 `lexists` 缺席。`/proc` cmdline 扫描未发现 source launcher、`m9_openmx_build.py`、OpenMX、make 或 configure 活动进程。`06_reproduction` 下 `__pycache__`、`.pyc`、`.pyo` 计数为 0。

审计在写报告前后分别对 gate、journal、transaction、failure snapshot、16 项不可变 runtime、post state/workflow/ledger、retired inventory、完整 state/workflow、ledger event、产品缺席与活动进程结果构造 canonical aggregate fingerprint。写报告前 fingerprint 为：

```text
c438df8c97a48dff34e3b1c552c641e35500f5de20bb3e0ee7c2d555bcd7c5de
```

写报告后的独立复算得到同一 fingerprint，journal/transaction 仍逐字节相等，gate、snapshot、retired、ledger、state/workflow、产品缺席和进程结果均未变化。该对照排除本审计对正式运行态的可观察写入；项目内除本报告外未新增或修改文件。

## 8. 授权边界与下一步

本 PASS 只确认 recovery 事实已完整、唯一且与授权 gate 一致。它不授权再次调用 `recover`，不授权 `source_prepare`、`source_build`、smoke、batch、GPU、Hamiltonian、SCF 或任何其他计算。

下一步必须重建替代的 root-owned consumer snapshot/gate，并对其执行独立事实审计。只有该 consumer 证据通过后，才可向用户请求新的、明确的、单次 `source_prepare` 授权；在取得该授权前不得执行 source prepare/build。
