# M9 Python 3.9 consumer gate completion 独立执行事实审计

审计日期：2026-08-30  
决策边界：`D-018-PY39-CONSUMER-GATE-COMPLETION`  
审计角色：独立子 agent；主 agent 执行 completion，审计 agent 仅只读核验正式对象  
结论：**PASS / BLOCKING=0 / NON_BLOCKING=0**

## 当前判断与证据边界

缺失的 readiness consumer gate 已正确安装，字节与前次独立 preflight 的确定性结果完全一致；正式命名空间变化仅为该 gate 新增以及 manifests 父目录 mtime/ctime 更新。其余 125 项原正式对象的路径、类型、inode、安全 metadata、大小、时间和文件 SHA 保持原值，父目录上述两时间字段除外。真实 UID1000 已从 root-owned v2 snapshot 载入实际 adapter，在既存 budget lock 内通过只读 `verify_consumer_gate()`。

本 PASS 足以进入“请求新的、明确的、单次 `source_prepare` 用户授权”环节，但不是该授权本身。single-run authorization object 仍缺席；未建立 operation id、nonce 或授权记录，不得据本报告直接执行 `source_prepare`。build、smoke、batch、GPU、Hamiltonian/SCF、DFT 等动作不在本结论许可范围内。

主实施记录 `M9_py39_consumer_gate_completion_execution_record.md` 的 SHA-256 为 `e78cec3ce9b2894f8ddfaff5b58156ada51fd7dd930f34f39e64e4635b0207c8`，已独立重算，只作为执行参数线索。安装是否成立以本次读取的真实文件、前次独立基线哈希、冻结输入和实际 UID1000 verifier 结果判断，不以主实施记录自证。审计没有重放 `complete`，没有运行原 installer 顶层入口，没有调用 source action 或任何预算计算。

## 安装依据与实际 gate

前次独立实施审计和 final verdict 的最终冻结 SHA 仍分别为：

```text
report  48ddb4b760348e1a7f07572a8873b8e13df17983a9d338dfad5e909c6936eb7e
verdict 4ff45c308cc1f7b5dc9579d9617697ae6bc2e3fa9df65626a1f6967741b3ab84
```

四个受审输入保持原版本：

```text
controller c2c235c444bae0f613078a060efa9733f869533385fa84268bfd2cc2b3c3ef55
test       05ae6f542c6c9ea22d38d4899298a3ccf16f4ed4c8763309737fedb22a34331a
failure    843122abdb878b40abd7da09b3689ee3e77e11271fe348b637519aeec3a6a400
work       53ef0b0e1923b571b275affb91cdc944c6d363d3ae3a85b60997b2dd67bf830f
```

实际安装对象为 `/home/evan-williams/deeph-m9/manifests/overlap_source_prepare_py39_uid1000_consumer_gate.json`。该对象为普通单链接文件，`5535 bytes`，owner/group 为 `0:1000`，mode 为 `0640`，device/inode 为 `2096:162440`，SHA-256 为 `520a8cffcab9c91400647e486de796853d8a00073892e3a4b0472cafbf9dd5c9`。其 mtime_ns 为 `1788060325537677975`，ctime_ns 为 `1788060325545677975`。

root 侧通过只读路径重新验证 trusted bootstrap、25-file frozen closure、全部 authorized source bytes、封存 snapshot、recovery core、`SUCCESS_COMMITTED` refresh 和历史闭集，再将规范化 receipt 传入纯构造函数 `build_consumer_gate()`。独立重建的预期 JSON 对象与实际 gate 对象全等；采用既定缩进、UTF-8 和末尾 LF 序列化后，预期与实际 `5535` 字节逐字节全等。该 SHA 也与前次独立 single-FD preflight 的预期值一致。

gate 的 schema 为 `m9-source-prepare-py39-uid1000-consumer-gate-v1`，decision 为 `D-018-PY39-CONSUMER-REPLACEMENT`，状态为 `PASS/0/0`，scope 严格为 `ALLOW_ONE_SOURCE_PREPARE_AFTER_PY39_RECOVERY`。它按旧已审计 gate schema 绑定 replacement verdict、consumer frozen manifest、snapshot manifest、recovery fact report、recovery implementation verdict、固定 recovery gate/transaction、历史 consumer/bootstrap/snapshot/execution gate、active gate 及当前 runtime。completion 审计文件属于此次安装动作的独立外部门控，不擅自增加到旧 gate schema 或原 25-file 冻结闭集中。

## 正式写集合与前次独立基线比较

比较范围为 manifests、controls 和 `/root/deeph-m9-control` 三个互不重叠的完整正式树。receipt 包含路径、类型、dev/ino、uid/gid/mode/nlink、大小、mtime_ns、ctime_ns、文件 SHA-256 或 symlink target；读取可能更新的 atime 不属于本比较口径。每次采集均使用两次完整且相等的无跟随遍历。

前次独立审计的 125 项基线清单未另行落盘保存，工具回执和冻结审计报告保存了其紧凑、排序 JSON 的 SHA-256：

```text
219a5711fd66f8b75d120f4115176c20ae26f567da445c83b3ac7f2d4b6da87e
```

因此本次不声称持有先前落盘清单，而使用哈希验证的内存重建：独立采集安装后的 126 项清单，移除唯一新增 gate；仅对 manifests 父目录的 mtime_ns/ctime_ns 尝试既存 active gate ctime 候选 `1788013796283394842`，保持其他所有对象及字段不变。首个候选重算即与上述前次独立承诺的 SHA-256 精确相等。该结果在 SHA-256 抗碰撞假设下验证了原 125 项完整基线的恢复，而非把推测的时间当作事实。没有修改任何磁盘时间或文件。

父目录的实际差异为：

| 字段 | completion 前 | completion 后 |
| --- | --- | --- |
| dev:ino | 2096:50688 | 2096:50688 |
| uid:gid / mode / nlink | 0:1000 / 01770 / 3 | 0:1000 / 01770 / 3 |
| bytes | 4096 | 4096 |
| mtime_ns | 1788013796283394842 | 1788060325545677975 |
| ctime_ns | 1788013796283394842 | 1788060325545677975 |

安装后完整 126 项清单 SHA-256 为 `bc4b963661cb43e8273049f611023db34864e60b0160ee1e17553f01e624296e`。root 侧只读事实验证及真实 UID1000 verifier 执行前后均逐项全等，并保持该 SHA。未发现额外新增、删除、替换、权限变化或历史文件改写。

## Trusted snapshot、runtime 与历史证据

v2 bootstrap 的 5 个声明成员及 receipt、v2 snapshot 的 28 个声明成员及 manifest 均逐成员验证，root 为 `0:1000/0550`，成员为 `0:1000/0440` 普通单链接文件，路径闭集、大小、SHA 正确。原 consumer frozen manifest 仍为 25-file 闭集，主计划、进度台账和 decisions 等既有冻结输入保持原字节。历史 bootstrap 5-member、历史 snapshot 27-member 和历史 consumer gate 同样通过完整闭集及固定 SHA 验证。

refresh journal 仍为 `SUCCESS_COMMITTED`，SHA-256 `b9d7800e471fe74da00fb78ac911004106db1195326812d098b575f5c25fb292`。active gate 保持 device/inode `2096:162490`、SHA-256 `229f0846c3d22917ccb955729a577168880bca6a53ad07f32502b0ae4a4e27ab`；retired old-active gate 保持 device/inode `2096:153476`、SHA-256 `78311a978c2472c85b35a745d80e1f33724c1500cf8d7bd244cdbe83c3fa3698`。snapshot staging 和 refresh staging 均缺席。

关键 runtime 与失败记录保持如下 receipt：

| 对象 | device:inode | bytes | SHA-256 |
| --- | --- | --- | --- |
| state | 2096:162448 | 2195 | f51960808c7e0c518972cd717ae94fbc2a070be57638862c4b143970f3223e73 |
| workflow | 2096:162446 | 709 | 384a4de85803666e305ca55b38dd6966c40244f789ac887a52b5a282095e2492 |
| ledger | 2096:50691 | 61826 | 5253620510f84d1987874c5fa571f6016cedfbdabc6e80a4b126e724839b1ea9 |
| 原失败 transaction | 2096:153683 | 2347 | 0a982e876e43768c6069fdeafd07e6e43ae03be3b1a0abc8584aa8d137bbcae7 |

budget lock 保持 `2096:50700`、`1000:1000/0644`、单链接空文件。真实 `verify_recovered_core()` 逐项对比 recovery transaction 固定的 post-state/workflow/ledger receipt 与 immutable pre-runtime receipt，验证 recovery gate/transaction/failure snapshot 的固定哈希及 metadata，并验证原失败 transaction 与 failure snapshot 字节相同。D-017/D-018 gate、transaction、execution gate、journal、pre-state snapshot、已消费 capability 和 FAIL launcher receipt 均保持原身份与哈希。

state 的总墙钟策略仍为 `UNLIMITED`，hard_stopped 为 false，active_overlap_transaction 为 null；workflow 仍为 `AUDIT_PASSED`、hard_stopped=false、active_transaction=null。历史失败原因字段继续保留。CPU 原始 overlap_build 用量为 `7206.669426146001` 秒，原非计算超时抵扣 `7200.075310528` 秒未改变；其他 overlap CPU bucket 仍为 0，GPU compatibility 历史用量为 `54.84820560599999` 秒，其他 GPU bucket 仍为 0。ledger 没有新增事件或用量记录，CPU/GPU/存储约束未被 completion 改写。

## 真实 UID1000 verifier

独立审计使用 `/usr/sbin/runuser -u evan-williams -- /home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 启动新进程，实际 uid/gid 均为 `1000`，实测 Python 为 `3.9.23`，isolated/no_site/dont_write_bytecode 均启用。

该进程从 `/home/evan-williams/deeph-m9/controls/uid1000-consumer-py39-v2/m9_budget_uid1000_consumer.py` 载入实际已安装 adapter，而非项目侧文件或 mock。adapter 的原控制器也由同一封存 snapshot 的 `m9_budget.py` 实际载入。审计先核对 root-owned snapshot 与 adapter 的安全 metadata，再用 `O_NOFOLLOW` 打开既存 budget lock，在同一 FD 排他锁内调用 `verify_consumer_gate()`，并在调用前后检查锁 FD/路径身份及完整 consumer runtime。

实际返回：`uid1000_verify_consumer_gate_pass`，进程退出码 `0`，stderr 为空；gate receipt 与本报告实际 receipt 一致，runtime 前后全等，authorization 按 `lexists` 缺席。额外只读审计 hook 记录并拒绝任何 `/root/` 文件打开，实测 root-private 读取尝试为 `[]`。root 外层采集的完整 126 项正式清单也在 UID1000 进程前后完全相等。

本次只调用 readiness verifier，没有调用 adapter `main()`、authorization 消费函数或任何 `source_prepare` 命令。因此该结果证明实际 UID1000 能验证现有 readiness gate，不等同于已授权或已执行一次 source preparation。

## 文档与最终门控

本报告通过 Pandoc `markdown+tex_math_single_backslash -> html5 --mathml --fail-if-warnings` 严格检查；`git diff --check` 通过。`06_reproduction` 下 `__pycache__`/`.pyc` 数量为 0，正式控制树也无缓存新增；未使用 `py_compile`。本轮只新增本执行事实报告，未修改已有 PASS 报告、final verdict 或受审冻结文件。

最终判定为安装事实 `PASS/0/0`。下一步仅可请求新的单次 `source_prepare` 用户授权；授权对象应在取得明确授权后另行绑定授权记录、consumer/active gate、当前 runtime、唯一 operation id、nonce 与唯一 action。当前 authorization 缺席，该后续动作尚未获得许可。
