# M9 source_prepare Python 3.9 失败执行事实独立审计

审计日期：2026-08-21  
审计对象：完整冻结 argv 下首次实际进入 source launcher 后发生的 `source_prepare` 失败  
审计方式：失败后立即只读冻结正式运行态、transaction/ledger exactly-once 复算、capability 与 launcher receipt 绑定复算、部分暂存树递归盘点、产品与进程检查、冻结 Python API 签名核验、冻结代码与清单哈希核验  
执行边界：本审计未修改或清理任何 WSL 对象，未重试 `source_prepare`，未执行 `source_build`、smoke、batch 或 GPU；唯一新增对象为本报告

## 审计结论

本轮结论为 **FAIL**。`BLOCKING=1`，`NON_BLOCKING=0`。

失败处置控制本身按设计工作：本次调用建立了唯一 transaction，签发并消费了唯一 action capability；source launcher 记录唯一 `FAIL` receipt；父控制器随后把 transaction 提交为 `FAILED_COMMITTED`，把 budget state 与 workflow 同时置为 `HARD_STOP`，并在旧 ledger 前缀后恰好追加一个 `OVERLAP_HARD_STOP` 事件。活动 transaction 已清空，子进程 PID 391 与相关构建进程均不存在。因此，现有证据支持“失败已确定性提交且计算已停止”，不支持把本次失败解释为仍在后台运行或未结算的事务。

但是，`source_prepare` 没有完成。六个受控 source/build 路径中五个终态或 manifest 产品缺席，`openmx-overlap-build.staging` 则留有 632,029,184 bytes 分配空间的部分源码树。consumer gate 文件字节未被改写，但它绑定的运行态已经漂移；真实 UID1000 verifier 现在以 `D-018 consumer runtime drift` 拒绝，不能再作为可消费门控。技术意义上的 action capability 已经消费，本报告此前放行的“一次 source_prepare”执行机会也已用尽。

根因是冻结实现与冻结 Python 3.9 的 API 不兼容，而不是 Python 版本或源文件哈希漂移。冻结 Python 为 3.9.23；该版本 `pathlib.Path.write_text()` 的签名不接受 `newline`，但冻结 `m9_openmx_build.py` 在 `prepare_sources()` 中调用了 `makefile.write_text(..., newline="\n")`。launcher receipt 证明实际加载的正是冻结 SHA-256 `53c6e04c...f78268`，未咨询 bytecode。相同兼容模式还存在于冻结 `m9_openmx_input.py`，如不一并修复，将在后续输入生成路径再次触发同类失败。

稳定阻塞项为 **M9-SP-PY39-B01**：冻结 Python 3.9 下的可执行 source/smoke 写入路径使用了仅较新 Python 才支持的 `Path.write_text(newline=...)` 调用，现有测试只验证纯 `render_makefile()`，没有在固定 Python 3.9 下执行实际文件写入路径。该问题在修复、冻结清单更新、失败态恢复和新门控独立审计完成前阻塞任何 `source_prepare` 重试；本报告不授权清理暂存树、恢复 hard stop、创建替代 gate、重试或执行 `source_build`。

## 失败事务与双硬停

实际 transaction 为：

| 字段 | 实测值 |
|---|---|
| transaction ID | `80e28da82f076f4f7b1811f5897216bd` |
| action / bucket | `source_prepare` / `overlap_build` |
| transaction state | `FAILED_COMMITTED` |
| command SHA-256 | `971fb8c5b2d490791265acd0c6bb7b13ac827d89111f1f93855fe73d67f1d8f9` |
| forecast / required | `1073741824` / `1073741824` bytes |
| child PID | `391`，已不存在 |
| elapsed | `5.878340039` seconds |
| exit / timeout | `1` / `false` |
| history | `FAILED_PENDING_COMMIT` → `FAILED_COMMITTED` |
| failure UTC | `2026-08-20T17:35:07.339852Z` |
| reason | `overlap_command_failed` |

transaction 中冻结 bootstrap 仍为 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9`，并记录 `isolated=true`、`no_site=true`、`dont_write_bytecode=true`。transaction 文件实测 SHA-256 为 `0a982e876e43768c6069fdeafd07e6e43ae03be3b1a0abc8584aa8d137bbcae7`，2347 bytes，`1000:1000 / 0644 / nlink=1`。

budget state 与 workflow 的双硬停一致：

- budget state：`hard_stopped=true`，`active_overlap_transaction=null`，`last_event_utc` 等于 failure UTC；
- workflow：`stage=HARD_STOP`，`hard_stopped=true`，`hard_stop_reason=["overlap_command_failed"]`，`active_transaction=null`，`hard_stop_utc` 等于 failure UTC；
- state 与 workflow 没有残留活动事务，transaction 已进入唯一终态；
- `/proc` 扫描中 source launcher、`m9_openmx_build`、OpenMX、`make` 与 `configure` 相关命中均为 0。

对应正式文件为：

| 对象 | SHA-256 | bytes | uid:gid / mode / nlink |
|---|---|---:|---|
| budget state | `8a128719f80e584c2a1fbfafcc309e534b1b7d375e428a195c8f6349ea2b5656` | 2106 | `1000:1000 / 0644 / 1` |
| workflow | `92783147133967dc6dc6494220d7628de2e05de9c260b4ea4fa2bd2f1f44e4e2` | 610 | `1000:1000 / 0644 / 1` |
| overlap transaction | `0a982e876e43768c6069fdeafd07e6e43ae03be3b1a0abc8584aa8d137bbcae7` | 2347 | `1000:1000 / 0644 / 1` |

因此，失败没有落在 PREPARED、RUNNING 或 `FAILED_PENDING_COMMIT` 崩溃窗口；双硬停和失败 transaction 已完整提交。

## Ledger exactly-once 与预算历史

失败前 ledger 的 60,288 bytes 前缀逐字节保留，SHA-256 为 `178106f0be9f80ff669ebd0865e214a4b9a60d115074ad0c97ae8de5f1ae33b7`。失败后 ledger 总长为 61,248 bytes、63 行、SHA-256 `a2170772c37b601112f0d957a18a6e9375dc7cf2eb22697a26b61a5db3ed770d`。新增后缀恰为 960 bytes、SHA-256 `2b5b69e8d3be617e357b177633c36a5d447dd244bd74e25c808f567c83c5aa20`，并且只含一个完整 JSONL 事件：

```text
event=OVERLAP_HARD_STOP
transaction_id=80e28da82f076f4f7b1811f5897216bd
command_sha256=971fb8c5b2d490791265acd0c6bb7b13ac827d89111f1f93855fe73d67f1d8f9
reasons=["overlap_command_failed"]
utc=2026-08-20T17:35:07.339852Z
```

事件中的 CPU/GPU/storage snapshot 与失败提交状态一致。`overlap_build` 原始 CPU 从 `7200.791086107` 增至 `7206.669426146001`，增量恰为 transaction elapsed `5.878340039` seconds；既有 noncompute credit 仍为 `7200.075310528`，未重置也未扩大，故当前 effective overlap-build CPU 为约 `6.594115618` seconds。GPU 三个 bucket 完全未变：compatibility `54.84820560599999` seconds，training 与 physical validation 均为 0。

wall-clock policy 仍为 `UNLIMITED/D-018`；historical start、deadline、historical limit、authorization/contract/gate 哈希全部保留。失败事件的 storage snapshot 为：combined allocated `30,821,646,336`、自 overlap baseline 增量 `651,825,152`；combined apparent `30,508,671,948`、增量 `639,192,217`；host VHDX `27,325,890,560`、自 overlap baseline 增量 `905,969,664`。这些数值均未超过冻结 10 GiB overlap storage limit。审计期间只读查询观察到 host VHDX 计量值可随 WSL 外部状态变化，因此恢复门控应绑定恢复执行前的新鲜 storage snapshot；不得把这种计量变化误记为本审计写入或作为删除暂存树的理由。

## Capability 与 launcher receipt

capability 根目录仍为 `1000:1000 / 0700`。与本次事务对应的活动 capability 已经原子转为以下两个受保护对象：

| 对象 | SHA-256 | bytes | uid:gid / mode / nlink |
|---|---|---:|---|
| `acc4548498ba22d8ce894b2725f89daf.consumed.json` | `7a3e21145fa31b2613d5d1a740e56ead4e28c3b06b3b371d529a7fbb77ebd905` | 4439 | `1000:1000 / 0600 / 1` |
| `acc4548498ba22d8ce894b2725f89daf.launcher-receipt.json` | `8217945664427eea38d7f546fa5a91689701a989601fbe539951214f7e872924` | 4764 | `1000:1000 / 0600 / 1` |

`consumed.json` 为 `state=CONSUMED`，其 action、bucket、forecast、transaction ID、完整 budget argv 与 launcher argv 均与正式 transaction 相互绑定。原活动路径 `acc4548498ba22d8ce894b2725f89daf.json` 按 `lexists` 缺席，因此不存在可重复消费的同一 capability。

launcher receipt 为 `status=FAIL`，绑定相同 transaction 与 capability。它记录的唯一错误为：

```text
TypeError: write_text() got an unexpected keyword argument 'newline'
```

traceback 路径为 `m9_overlap_source_launcher.py:310 main` → `:280 dispatch` → `m9_openmx_build.py:534 prepare_sources`。receipt 还证明实际 source loader 为 `FrozenSourceLoader`，`bytecode_consulted=false`；加载的 `m9_openmx_build.py` SHA-256 为 `53c6e04cedce994b088b7b6dc738753d378cbcbc15d40600b30d85d87ff78268`，`m9_overlap_common.py` 为 `a58cea8676b1825e44a2c8dbda16c591c148c15f8a513d1ee96fb8ffe9e4b52e`。因此失败不是由未冻结代码、`.pyc` 或另一 Python 路径引入。

capability 目录另有 D-017 历史 `f7c3b060e19e37e6da03f461d754d38c.retired.json`；其存在不属于本次事务，也没有被改写。

## 部分暂存树与正式产品

六项受控正式产品状态为：

| 产品 | 状态 |
|---|---|
| `software/openmx-overlap-build` | 缺席 |
| `software/openmx-overlap-build.staging` | **存在，部分树** |
| `env/hdf5-1.12.1` | 缺席 |
| `manifests/openmx_official_3.9.9_tree_manifest.json` | 缺席 |
| `manifests/openmx_overlap_tree_manifest.json` | 缺席 |
| `manifests/openmx_overlap_build_manifest.json` | 缺席 |

暂存根为 `1000:1000 / 0755` 的真实目录，顶层闭集为 `hdf5-source` 与 `openmx3.9`。递归 `lstat` 盘点得到 5319 个记录，其中目录 140、普通文件 5179、symlink 0、其他类型 0；普通文件 apparent bytes 为 `619112384`，所有记录的 allocated bytes 总计 `632029184`。以相对路径排序，并对每项记录 type、mode、uid、gid、nlink、size 与普通文件 SHA-256 后进行 canonical JSON 编码，盘点哈希为 `05c20c3455994889efe81c9f8f02d193c8a086c77149c641b0a9ac6ea8652d97`。

关键中间对象均存在：`openmx3.9`、`openmx3.9/source`、`hdf5-source/hdf5-1.12.1`。失败点目标 `openmx3.9/source/makefile` 为 43,014 bytes、SHA-256 `bf01251254b3f0e3ee010346835bcbe4707aaa57c1f741eb1c84244e849e9d9b`。由于 `Path.write_text()` 在打开目标前即因参数绑定失败，makefile 字节仍是已提取和已打补丁后的失败前内容；本报告没有重写、移动或删除它。

该部分树是失败事实证据，也是下一次调用可能发生路径冲突的正式阻塞对象。不得把“正式 build root 缺席”误述为“没有任何 source_prepare 写入”，也不得在没有恢复工作包、精确 inventory 绑定和独立执行审计时直接删除或覆盖 `.staging`。

## Consumer gate 与历史证据

consumer gate 本身仍为 root:group1000、`0640`、普通单链接文件，4283 bytes，SHA-256 保持 `2ba96b8566f2ba38a528e4002dbaa0bebf4f9a7b8c5f10a92b89d643d11a85f2`。bootstrap receipt 与 snapshot manifest 也分别保持 `3172bf9516fed5dd2abb3669c705211428cbe6ebeea34fe96fcb6a3016d5f1ba` 和 `2d13e0c1fb1c1e635ad1730f44f21901340e7483d06356aa8eeb0e07f83dcec9`。

但是，consumer gate 是对执行前 runtime 的 sealed receipt，不是可变计数器。当前 state、workflow、ledger、overlap transaction 已合法变化，且 staging 产品出现；因此真实 UID1000 `verify_consumer_gate()` 现在以 `SystemExit: D-018 consumer runtime drift` 拒绝。结论应表述为：gate 文件未被改写，但其一次性作用已经完成，当前不能验证或再次消费。

受保护历史控制对象仍保持既有字节：

| 对象 | SHA-256 |
|---|---|
| D-017 source-control recovery transaction | `e9b8babcff8a2f42adea21d5cbce614b38f0854271d3389eae0bbcdd7d5e53bc` |
| D-017 recovery gate | `8e66d65d17d3195f3df09db954afca4066c3ec91e2d8dad6d2aea06078d0d5ce` |
| active overlap gate | `78311a978c2472c85b35a745d80e1f33724c1500cf8d7bd244cdbe83c3fa3698` |
| retired pre-D018 overlap gate | `dbe4756142d0e921c3834330550310e85652503c04254b30bea1a069ff35377c` |
| D-018 migration gate | `286a0e409a80f85ca6bb39b76bdb977fc67ffa56f4646b00d3aad5943c98e880` |
| D-018 transaction | `41cbfbd4da1c3a0eea92731a00758355f46321d5b0a66260f53f628290d847ad` |
| D-018 execution-fact gate | `bc51209c13570839c08dd4fc304fe39865a98ade69caeb23886602de2d8be6e9` |
| D-018 migration journal | `27a92edded459948150c750a4339692434e08a84cbc8879c63c71b6c14cb0e8a` |
| D-018 pre-state snapshot | `00a32bd7f28ad26fa600c8abe9d0fa64efe57e410eacb82ad2d201fa9adc5439` |

其中 root-private D-017 gate、D-018 journal 与 pre-state snapshot 继续保持 root-only 权限，没有因执行或审计而降权。现有证据支持 CPU/GPU/存储预算定义、D-017/D-018 历史授权及无墙钟迁移事实均未被重置或替换。

## 根因判定：冻结代码兼容缺陷，而非版本漂移

冻结解释器的只读实测结果为：

```text
Python 3.9.23 | packaged by conda-forge
Path.write_text (self, data, encoding=None, errors=None)
Path.open       (self, mode='r', buffering=-1, encoding=None, errors=None, newline=None)
```

冻结 contract 明确指定 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9`。`m9_overlap_frozen_hashes.json`、offline/source-control/D-018 frozen manifests 均把 `m9_openmx_build.py` 绑定为 SHA-256 `53c6e04c...f78268`；项目当前文件、launcher loaded-source receipt 与这些清单三者一致。由此可以排除“实际运行了错误 Python 版本”与“执行文件偏离冻结版本”两种解释。

直接缺陷位于 `prepare_sources()`：

```python
makefile.write_text(
    render_makefile(...),
    encoding="utf-8",
    newline="\n",
)
```

Python 3.9 在进入方法主体和打开文件前就拒绝未知关键字 `newline`。现有 `test_m9_overlap_controls.py` 只对 `render_makefile()` 的纯文本变换做单元测试，没有执行 `prepare_sources()` 的实际写文件分支，所以 109 项回归能够通过但不能覆盖这一运行时 API 契约。

主动相邻搜索还发现 `m9_openmx_input.py` 存在：

```python
input_path.write_text(input_text, encoding="utf-8", newline="\n")
```

该文件当前 SHA-256 为 `1b7d4acc6b455c9dd3ad3ace51d64a53c792cf45be253553b2a1d2aa3588f19b`。这一路径不构成本次 traceback 的直接原因，但与已证实根因完全同构，并将在固定 Python 3.9 的后续输入生成阶段失败。因此，M9-SP-PY39-B01 的关闭条件必须覆盖两个可执行调用点；只改 line 534 会留下可预测的相邻阻塞。

## M9-SP-PY39-B01 关闭条件

最小代码修复应保留显式 LF 行尾，并改用 Python 3.9 已支持的 `Path.open(..., newline="\n")`：

```python
rendered = render_makefile(...)
with makefile.open("w", encoding="utf-8", newline="\n") as handle:
    handle.write(rendered)
```

`m9_openmx_input.py` 的同类调用也应采用相同机制。不得以升级 Python 掩盖问题，因为 Python 3.9 是现有合同与 bootstrap receipt 的冻结对象；升级解释器会扩大依赖与复现边界，不是本阻塞项的最小修复。

代码关闭至少需要：

- 固定 Python 3.9 `-I -S -B` 下执行真实 makefile 写入路径，验证无 `TypeError`、输出 bytes 与预期完全一致且只含 LF；
- 固定 Python 3.9 下执行 OpenMX input 写入路径的等价回归；
- 证明失败点之前的 extract/patch/source inventory 语义未因修复改变；
- 更新所有直接或传递绑定这两个脚本的 frozen manifests、contracts、工作包与测试哈希，并完成 closed-set 自洽检查；
- 由独立审计员对修订快照给出 `PASS/BLOCKING=0/NON_BLOCKING=0`，主 agent 不得用自身测试结论替代。

## 最小恢复与重新执行门控

当前不是可以原命令直接重试的状态。最小安全恢复应建立独立的一次性 recovery 工作包，并冻结以下输入：失败 state/workflow/transaction/ledger 的完整 receipt、consumed capability 与 FAIL launcher receipt、旧 ledger prefix 和唯一失败后缀、上述 staging canonical inventory、六正式产品状态、进程缺席、当前 CPU/GPU/storage 用量以及全部 D-017/D-018 历史对象。

恢复实现应满足：

- 不删除、截断或原地复用 `.staging`；在再次确认 exact inventory 后，将其原子退休到 transaction ID 唯一绑定的只读失败证据路径，例如 `openmx-overlap-build.failed-80e28da82f076f4f7b1811f5897216bd.retired`；如目标已存在，只允许 exact-byte/metadata 幂等续提；
- 在新事务覆盖通用 `overlap_transaction.json` 前，为本次 `FAILED_COMMITTED` transaction 建立不可变、哈希绑定的历史副本；consumed capability 与 FAIL receipt 保持原位且不可修改；
- 恢复 state/workflow 时保留 raw CPU 增量 `5.878340039`、既有 credit、GPU 用量、storage 历史与全部 ledger 前缀，不得把实际失败耗时返还为 credit；
- ledger 只允许 exactly-once 追加一个有稳定 event ID 的 recovery 事件；不得改写既有 63 行；
- 所有 rename、ledger append、state/workflow/transaction 写入均需具备 crash-resumable journal、失败双硬停与独立执行事实审计；
- 修订代码和冻结清单通过实现审计后，重新机械生成并事实审计与新代码闭集一致的 root-owned consumer snapshot/gate；旧 gate 与旧 snapshot 作为历史证据保留，不得原地伪装为仍有效；
- recovery execution fact 与替代 consumer gate 均获独立 PASS 后，方可请求或记录一次新的、明确的 `source_prepare` 执行授权；执行后仍应立即停止作事实审计。

由于本次 action capability 已消费、consumer gate 已失效且一次性程序门控已经执行，现有 D-017/D-018 execution gate 不能自行解释为“自动允许第二次 source_prepare”。任何重试都必须建立在修复后的新 closed set、正式 hard-stop recovery、替代 consumer gate 事实审计以及新的单次执行授权之上。

本报告明确禁止当前直接重试、清理 staging、恢复 hard stop、执行 `source_build`、smoke、batch、GPU、数据下载、DFT 标签生成或训练。
