# M9 Python 3.9 consumer gate completion 独立实施审计

## 2026-08-30 B01 独立定点复核：当前结论

本节替代下方历史初审的当前许可判断；历史 `FAIL/BLOCKING=1/NON_BLOCKING=0` 全文保留，不作为修订实现的结论。原初审 agent 已中断，本轮由主实施 agent 之外的新独立审计 agent 接续，未修改受审实现、测试、工作包、失败记录或任何既有冻结输入。

**当前代码与测试审计结论：PASS，BLOCKING=0，NON_BLOCKING=0。`M9-PY39-COMP-B01` 已关闭。** 本结论只适用于下列四文件闭合版本；不是 completion 执行事实审计，不授权 `source_prepare` 或任何后续计算。

```text
controller c2c235c444bae0f613078a060efa9733f869533385fa84268bfd2cc2b3c3ef55
test       05ae6f542c6c9ea22d38d4899298a3ccf16f4ed4c8763309737fedb22a34331a
failure    843122abdb878b40abd7da09b3689ee3e77e11271fe348b637519aeec3a6a400
work       53ef0b0e1923b571b275affb91cdc944c6d363d3ae3a85b60997b2dd67bf830f
```

### B01 修复与真实调用路径

`run_completion_under_lock()` 在既存同一 budget lock 内先执行真实 `verify_installation_guard()`，逐成员验证历史 bootstrap/snapshot 闭集和历史 consumer gate，并用 `lexists` 排除 authorization，包括 dangling symlink。随后 `read_terminal_snapshot()` 检查 replacement snapshot 已存在、staging 缺席、root 的 owner/group/mode、manifest 来源闭集、每个成员的严格 receipt 和实际字节，以及目录精确闭集。以上均只读，不调用 installer。

`read_terminal_refresh()` 先重放 recovery gate/transaction/failure snapshot、post-state/workflow/ledger 与全部 immutable pre-runtime receipt，绑定原 budget lock FD/inode；随后通过真实 `read_bound_refresh_journal()` 验证 journal 严格相位字段闭集、schema/decision、固定旧 active receipt、新 active SHA、staging/retired 路径及锁身份。controller 明确要求 journal 已存在且 state 精确为 `SUCCESS_COMMITTED`，再经真实 `validate_refresh_namespace()` 和 `verify_installation_preflight()` 验证 active/retired 的继承 inode、metadata、字节哈希与 refresh staging 缺席。只有上述检查完成后，才调用旧 `prepare_snapshot_for_refresh()` 与 `refresh_active_overlap_gate()`。

已逐行审查旧续提实现：snapshot 存在且已封存时 `install_snapshot()` 仅验证并返回；`SUCCESS_COMMITTED` refresh 跳过全部 commit/staging/rename 分支，只执行 terminal receipt 验证。原 inode-rich refresh 用于 terminal preflight，局部 normalized 副本仅供 `build_consumer_gate()`；七个共享字段全等及仅有 dev/ino 两字段差的条件保持不变。

controller 在潜在 mutator 前对 manifests、controls、root-private control 三个互不重叠正式树执行两次完整且相等的递归无跟随快照，记录路径、类型、dev/ino、uid/gid/mode/nlink、大小、mtime/ctime、文件 SHA 或 symlink target。终态重放与 gate 构造后再次捕获，要求逐项全等；读取引起的 atime 不属于该零写比较口径。`complete` 的首次创建只允许 consumer gate 与其父目录大小/mtime/ctime 改变，父目录安全身份不变；既有 gate 只允许全部正式对象相等。旧 `install_consumer_gate()` 对既有对象验证精确 JSON 及序列化字节，不覆盖不同对象。

### 独立动态验证

固定解释器 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 实测版本为 `3.9.23`。专用 completion 测试 `13/13`、consumer 测试 `23/23`、overlap 控制测试 `110/110` 全部通过。专用测试的 mock 范围已与真实调用链分开核查，未把 mock 成功视为文件安全验证的替代。

审计另以 `/tmp/m9-audit-*` 临时夹具运行 16 项真实 helper 负例：snapshot 缺失、snapshot staging dangling symlink、额外成员、错误 root mode、成员字节漂移、来源闭集缺项；journal 缺失、四种合法非终态 `PREPARED/STAGED/OLD_RETIRED/ACTIVE_REPLACED`、额外字段、active inode 漂移、retired inode 漂移、refresh staging dangling symlink；authorization dangling symlink。只替换路径常量与用于侦测越界的三个潜在 mutator，保留真实 snapshot、journal、namespace、历史、recovery 和 guard 验证。16 项均抛出预期拒绝，`prepare_snapshot_for_refresh`、`refresh_active_overlap_gate`、`install_consumer_gate` 调用次数全部为零，临时树执行前后完整 receipt 全等。

另在独立临时 gate 路径调用真实 `install_consumer_gate()`：首次创建通过真实 write-set 验证；同字节 replay 保持 inode、mtime/ctime 和全树 receipt；不同字节 gate 零写拒绝。测试结束后正式三树仍逐项相等。未对正式 consumer gate 调用安装函数。

### 现场状态与历史不变性

实时只读复核确认 v2 bootstrap 的 5 个声明成员及 receipt、v2 snapshot 的 28 个声明成员及 manifest 均为精确闭集，安全 metadata 和全部成员 SHA 正确；consumer frozen manifest 仍为原 25-file 闭集。历史 bootstrap 5 个声明成员、历史 snapshot 27 个声明成员及其 receipt/manifest 逐项验证通过，原 consumer gate 保持固定哈希。不得为更新进度而改写 master execution plan、progress tracker 或 decisions 等冻结文件。

三树共 `125` 个正式对象。以 `json.dumps(receipts, sort_keys=True, separators=(",", ":"))` 的 UTF-8 字节计算，现场完整 receipt 清单 SHA-256 为 `219a5711fd66f8b75d120f4115176c20ae26f567da445c83b3ac7f2d4b6da87e`，独立只读 terminal proof 与临时负例执行前后均保持不变。

refresh journal 仍为 `SUCCESS_COMMITTED`，SHA-256 `b9d7800e471fe74da00fb78ac911004106db1195326812d098b575f5c25fb292`。active receipt 保持 inode `2096:162490`、SHA-256 `229f0846c3d22917ccb955729a577168880bca6a53ad07f32502b0ae4a4e27ab`；retired receipt 保持 inode `2096:153476`、SHA-256 `78311a978c2472c85b35a745d80e1f33724c1500cf8d7bd244cdbe83c3fa3698`。snapshot staging、refresh staging、replacement consumer gate、single-run authorization 均缺席。

```text
state    f51960808c7e0c518972cd717ae94fbc2a070be57638862c4b143970f3223e73
workflow 384a4de85803666e305ca55b38dd6966c40244f789ac887a52b5a282095e2492
ledger   5253620510f84d1987874c5fa571f6016cedfbdabc6e80a4b126e724839b1ea9 (61,826 bytes)
failure  0a982e876e43768c6069fdeafd07e6e43ae03be3b1a0abc8584aa8d137bbcae7
```

state 仍为 `UNLIMITED`、非 hard-stop、active transaction 为空；workflow 仍为 `AUDIT_PASSED`、非 hard-stop、active transaction 为空。真实 `verify_recovered_core()` 绑定 recovery transaction 的原 post receipt 和 immutable pre-runtime receipt，因此预算与历史用量不以新读取结果重新定义。失败 transaction、capability、FAIL receipt、恢复 transaction/failure snapshot、D-017/D-018 历史证据均保持原 receipt。

### 文档、缓存与 single-FD preflight

四文件 SHA 已独立重算；严格 Markdown 使用 Pandoc `markdown+tex_math_single_backslash -> html5 --mathml --fail-if-warnings`，`git diff --check` 无错误。`06_reproduction` 下 `__pycache__`/`.pyc` 数量为 0；未使用 `py_compile`。

代码审计 PASS 后已生成严格 15 字段 final verdict，绑定本报告和四文件路径及 SHA，再从前序 replacement 工作包原文提取唯一 Python 代码块作为 single-FD loader，仅以 action=`preflight` 调用；未用普通直接执行替代 loader。原 loader 源的 UTF-8 SHA-256 为 `c68e43b5de4fdadb44254fbfdd543f5ba2a29b6e41994021c55a3287b5f7491f`。

首次正式 preflight 退出码为 `0`、stderr 为空，返回 `preflight_pass`，预期 consumer gate SHA-256 为 `520a8cffcab9c91400647e486de796853d8a00073892e3a4b0472cafbf9dd5c9`。外部审计快照覆盖同一 125 个正式对象，before/after 清单 SHA 均为 `219a5711fd66f8b75d120f4115176c20ae26f567da445c83b3ac7f2d4b6da87e`，逐字段比较完全相等；consumer gate 与 authorization 仍缺席。首次调用消费的报告 SHA 为 `9ce1ea9c1689ad1bceac4987cd41f5bba53384a31d16a693f1b07d0765a075dd`，verdict SHA 为 `fdd3d3d18cf9e7a449f26617184aea1701b3061848441774373d8ac9a36707ed`；该版本仅用于记录首次预检，不得替代最终绑定。

本节补充实际结果后，final verdict 重新绑定最终报告 SHA，并要求以最终 report/verdict SHA 再次运行相同只读 loader preflight；最终文件 SHA、参数数组 SHA 和复核结果由独立审计返回回执给出，不在报告内部引入自引用哈希。任何预检失败均应撤回 PASS。正式 `complete` 从未执行，readiness gate 尚未存在；本轮不构成安装完成或执行事实审计通过，未创建 authorization，未调用 `source_prepare`、build、smoke、batch、GPU 或 DFT。

## 历史初审记录：2026-08-29（保留原文）

审计日期：2026-08-29  
决策边界：`D-018-PY39-CONSUMER-GATE-COMPLETION`  
审计对象：completion controller、专用测试、失败事实记录、completion 工作包、已安装 v2 trust root/snapshot、实时 refresh 部分终态、历史 evidence、budget/state/workflow/ledger 及旧 trusted installer 输入契约  
执行边界：未执行 `complete`；未创建 authorization；未调用 `source_prepare`、build、smoke、batch、GPU 或 DFT；因结论为 FAIL，按工作包门控未执行 single-FD `preflight`

## 结论

**verdict：FAIL。`BLOCKING=1`，`NON_BLOCKING=0`。**

失败事实、实时部分终态和 receipt normalization 的根因均得到独立复现。`normalized_refresh_for_gate()` 只在局部副本中以 runtime active receipt 替换 inode-rich active receipt，原 refresh 继续传给 terminal preflight；该语义修正本身正确。

但是，controller 没有在调用旧 installer 的可写续提函数之前强制证明 snapshot 已封存且 refresh journal 已为 `SUCCESS_COMMITTED`。`preflight` 与 `complete` 共用同一路径，都会先调用 `prepare_snapshot_for_refresh()` 和 `refresh_active_overlap_gate()`。在 snapshot/journal 缺失或 refresh 处于较早但合法阶段时，这两个函数会创建 snapshot、写 journal/staging 并 rename active/retired gate。因此 `preflight` 不是代码语义上的零写动作，`complete` 的唯一写集合也没有被限制为缺失 consumer gate。

该问题记为稳定阻塞项 `M9-PY39-COMP-B01`。当前不得执行 completion preflight 或 complete，也不得把本 FAIL verdict 作为消费许可。

## 冻结输入

审计侧独立重算四个受审输入，均与工作包给定值一致：

- controller：`6e9b270c599a02856db09861b108ff0d3769bc077872568383f48989a6c6d9b1`；
- test：`db5d49ddf3fd983e65e4881912f1c6c86b7d6a56f044a2f597984c3b235442f6`；
- failure record：`843122abdb878b40abd7da09b3689ee3e77e11271fe348b637519aeec3a6a400`；
- work package：`71de9d80365c97a295dea8124896a514942f9dc93734c387928d324dd50ecb0d`。

controller 的 `verify_audit_authority()` 对 verdict 采用严格 15 字段闭集，要求精确 schema、decision id、`PASS/0/0` 以及 controller/work-package/failure-record/test/report 的 POSIX 路径和 SHA-256 绑定。普通直接执行不能替代外层 single-FD loader；本审计没有以直接调用冒充正式 preflight。

## 失败事实与实时部分终态

失败记录所述事实与实时 WSL 一致：

- v2 bootstrap root 为 root:group1000、`0550`，receipt 声明的 5 个成员逐项满足 root:group1000、`0440`、普通单链接、大小和 SHA-256，目录闭集严格相等；receipt 为 1,399 bytes，SHA-256 `3107543507a64e2eb7e50227293b278e35a95e87b4815c1674ce70ea14673fea`；
- v2 snapshot root 为 root:group1000、`0550`，manifest 声明的 28 个成员逐项满足 root:group1000、`0440`、普通单链接、大小和 SHA-256，目录闭集严格相等；manifest 为 9,746 bytes，SHA-256 `b9c7358b1f976d85c31f2defec1e06d25338ea3dfbe51b1594eb2e6ca1b3fc7d`；
- root-private refresh journal 为 `SUCCESS_COMMITTED`，1,733 bytes，SHA-256 `b9d7800e471fe74da00fb78ac911004106db1195326812d098b575f5c25fb292`；
- replacement active gate 为 1,053 bytes、inode `2096:162490`、SHA-256 `229f0846c3d22917ccb955729a577168880bca6a53ad07f32502b0ae4a4e27ab`；
- retired old active gate 保持原 inode `2096:153476` 和 SHA-256 `78311a978c2472c85b35a745d80e1f33724c1500cf8d7bd244cdbe83c3fa3698`；
- staging、replacement consumer gate 与 single-run authorization 均按 `lexists` 缺席。

state、workflow、ledger 和历史失败 transaction 仍分别为：

```text
state    f51960808c7e0c518972cd717ae94fbc2a070be57638862c4b143970f3223e73
workflow 384a4de85803666e305ca55b38dd6966c40244f789ac887a52b5a282095e2492
ledger   5253620510f84d1987874c5fa571f6016cedfbdabc6e80a4b126e724839b1ea9 (61,826 bytes)
failure  0a982e876e43768c6069fdeafd07e6e43ae03be3b1a0abc8584aa8d137bbcae7
```

state 仍为 `UNLIMITED`、非 hard-stop、active transaction 为空；workflow 仍为 `AUDIT_PASSED`、非 hard-stop、active transaction 为空。历史 bootstrap 5-member 闭集和历史 snapshot 27-member 闭集逐成员复核通过，receipt/manifest SHA-256 分别保持 `3172bf9516fed5dd2abb3669c705211428cbe6ebeea34fe96fcb6a3016d5f1ba`、`2d13e0c1fb1c1e635ad1730f44f21901340e7483d06356aa8eeb0e07f83dcec9`。没有证据表明预算、历史用量、ledger 或历史 evidence 在失败中发生改变。

## Receipt normalization 与旧 installer 契约

实时 refresh `active` receipt 的字段为：

```text
path, bytes, sha256, uid, gid, mode, nlink, dev, ino
```

实时 consumer runtime active receipt 的字段为：

```text
path, bytes, sha256, uid, gid, mode, nlink
```

七个共享字段逐项全等，集合差恰为 `dev`、`ino`；实时值分别为 `2096`、`162490`，均为非布尔正整数。旧 trusted installer 的 `build_consumer_gate()` 使用整对象条件：

```python
refresh.get("active") != runtime.get("active_overlap_gate_sha256")
```

由此可确认原 installer 的 `Python-3.9 recovery terminal evidence mismatch` 是字段域不同导致的确定性假阴性，而不是 active gate 字节或 inode 漂移。

`normalized_refresh_for_gate()` 先严格要求字段集合差恰为 `{dev, ino}`、二者为非布尔正整数、共享字段全等，然后执行浅层 `dict(refresh)` 并只替换新副本的 `active`。测试确认原 `refresh["active"]`、`retired` 和 `journal` 不被修改。controller 随后把 normalized 副本传给 `build_consumer_gate()`，而把原 inode-rich `refresh` 传给两次 `verify_installation_preflight(..., refresh=refresh)`。该局部规范化与 terminal inode 验证的分工正确。

## 测试、缓存与文档

专用测试使用固定 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B`：

```text
Ran 3 tests in 0.000s — OK
```

三项测试覆盖：只删除 dev/ino 且不修改输入、共享字段漂移拒绝、额外/缺失字段及无效 inode 拒绝。它们没有覆盖 `run_completion()`、`preflight` 零写、`complete` 唯一写集合、非 terminal journal、缺失 snapshot/journal、consumer gate different/identical replay 或 authorization 负例。

`06_reproduction` 下 `__pycache__`/`.pyc` 数量为 0。failure record 与 work package 均通过 Pandoc `markdown+tex_math_single_backslash -> html5 --mathml --fail-if-warnings`；本报告生成后亦按相同规则验证。

## BLOCKING finding

### `M9-PY39-COMP-B01`：preflight 零写与 complete 唯一写集合未由 controller 强制

`run_completion()` 在取得 `budget.lock` 后的顺序为：

```text
verify_installation_guard
prepare_snapshot_for_refresh
refresh_active_overlap_gate
verify_installation_preflight
runtime / normalization / build_consumer_gate
...
if action == preflight: 检查 consumer gate 缺席并返回
else: install_consumer_gate
```

action 分支发生在两个旧续提函数之后。已安装 trusted installer 与项目冻结副本 SHA-256 均为 `991d1dcfddfc1ef0f16bfaadfd05411e555dfaa77b4dccfe2bc6bb2973c6a3b6`；其实现明确包含下列潜在写入：

- `prepare_snapshot_for_refresh()` 在 journal 缺席路径调用 `install_snapshot()`，可创建/rename replacement snapshot；
- `refresh_active_overlap_gate()` 可调用 `atomic_root_private_json()` 写 refresh journal；
- 可调用 `atomic_owned_durable_bytes()` 写 staging gate；
- 可调用 `rename_d018_gate_preserving_inode()` 退休旧 active 或激活 staging。

controller 没有在这些调用之前要求 snapshot root 已存在、refresh journal 已存在且 state 精确为 `SUCCESS_COMMITTED`，也没有先验证 terminal active/retired/staging namespace。当前实时状态恰好为 terminal，只能说明本次现场可能走只读分支，不能证明动作契约对缺失或漂移状态零写拒绝。

审计侧以 mock 只替代旧 installer 的潜在写函数，保留真实 `run_completion("preflight")` 调用顺序；即使模拟 journal 为非 terminal，controller 仍返回 `preflight_pass`，事件为：

```json
[
  "history",
  "guard",
  "prepare_may_write",
  "refresh_may_write",
  "terminal_preflight",
  "runtime",
  "build_gate",
  "guard",
  "terminal_preflight"
]
```

这证明 controller 没有 action-specific 的首写前 terminal gate。因而 `preflight` 的零写属性来自当前外部状态偶然满足，而不是由代码边界强制；同理，`complete` 可能写入 consumer gate 之外的正式对象。

**修复要求：** 在调用 `prepare_snapshot_for_refresh()` 或 `refresh_active_overlap_gate()` 前，controller 必须以稳定、严格、零写方式证明：v2 snapshot root 已存在并为精确封存闭集；root-private refresh journal 已存在、字段闭合、state 精确为 `SUCCESS_COMMITTED`；replacement active 与 retired receipt/inode 精确匹配 journal；staging 缺席；authorization 缺席。只有在证明这两个旧函数对当前状态是 terminal replay 后才可调用。`preflight` 应在任何潜在 mutator 前固定 action=zero-write，并比较完整正式对象前后快照；`complete` 的允许写集合必须精确为 consumer gate 的首次原子创建，或既有同字节 gate 的只读 replay。应增加覆盖 `run_completion()` 的缺失/非 terminal snapshot/journal、非法 namespace、preflight 全对象零写、complete 单路径写和相同/不同既有 gate 测试。

## 许可边界与 preflight 状态

本审计为 `FAIL / BLOCKING=1 / NON_BLOCKING=0`。依据明确门控，未生成可消费 PASS verdict，也未通过 single-FD loader执行 `preflight`；因此不存在可报告的正式 preflight 零写成功证据。审计过程自身只执行只读 WSL inventory 和临时目录/mock 穿透，正式 WSL 对象保持上述哈希与命名空间状态。
