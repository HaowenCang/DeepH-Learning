# M9 D-018 UID1000 consumer 旁路适配器独立实现审计

审计日期：2026-08-20  
适用问题：`D018-EGF-B01`  
审计方式：冻结闭集复算、代码与合同审查、真实 UID1000 临时权限重放、owner/mode/link 与跨读取 TOCTOU 主动穿透、固定 Python 回归、正式 WSL 运行态前后只读核对  
执行边界：未创建正式 consumer gate；未执行 `source_prepare`、`source_build`、smoke、batch、GPU 或正式迁移重放

## 审计结论

**FAIL**。`BLOCKING=3`，`NON_BLOCKING=0`。

旁路方向正确关闭了上一轮 `D018-EGF-B01` 的直接权限矛盾：新 consumer verifier 在真实 UID1000 下能够只读取 root:UID1000-group、`0640` 的 consumer/execution gate 和 UID1000 可读运行态，不会重开 root:root、`0600` 的 D-017 gate、D-018 journal 或 snapshot。原 `m9_budget.py`、原 109 项测试、source launcher、common、overlap contract 和原 16/16 闭集均逐字节保持冻结值；适配器也只接受 `source_prepare` 形态，并把三个代理安装到原 controller 的锁内调用点。

但是，当前实现没有满足工作包自己规定的 metadata 与 TOCTOU 门控。真实 UID1000 主动穿透得到三类稳定 PASS 绕过：可读 runtime 的 owner/mode 漂移仍通过；20 项冻结成员的 hardlink/owner/mode 漂移仍通过；runtime receipt 之后、语义读取之前替换 state 时，当前 state 哈希已经不同于 consumer gate 的 sealed runtime，但 verifier 仍返回 PASS。因此，不允许机械创建正式 consumer gate，不允许执行 `source_prepare`，也不允许 `source_build` 或任何后继动作。

## 送审对象冻结

| 对象 | SHA-256 | bytes | 结果 |
|---|---|---:|---|
| `06_reproduction/controllers/m9_budget_uid1000_consumer.py` | `a7a373dcc9c910ba28051b3e3ccd3a9ed9d0ca1c99771384a317150f68b1524e` | 12546 | 与送审值一致 |
| `06_reproduction/tests/test_m9_uid1000_consumer.py` | `8186a19d983521b222a4ea61fdd10bab95903e04e1f317cad8c194a5de7d0bef` | 13633 | 与送审值一致 |
| `06_reproduction/manifests/m9_uid1000_consumer_contract.json` | `24eb75d323849eee876a86ebbcd5ea7b5625788e5aadc0d5d206d4d4c79e46dc` | 1446 | 与送审值一致 |
| `06_reproduction/manifests/m9_unlimited_wall_clock_uid1000_consumer_frozen_hashes.json` | `c74a5fe37438bbf017b3f3d5636faad5b1ef2f1917904499e68a4e0ff356d637` | 3267 | 与送审值一致 |
| `08_audits/M9_unlimited_wall_clock_uid1000_consumer_work_package.md` | `1327222f174158779bc1d5427092bfd3c373f7857acbf09b35efba7293a08861` | 6140 | 与送审值一致 |

原执行链的关键对象保持：

| 原冻结对象 | SHA-256 |
|---|---|
| `m9_budget.py` | `25c92810de52229ff626b4d54f4bd2084453e2e834ff830232b8599033f6cce5` |
| `test_m9_overlap_controls.py` | `8fd7b0eafebbe0d58f1e7c13ba0d5ede9881efd9cb070ecaa0bf6ab648073e59` |
| `m9_overlap_frozen_hashes.json` | `db01a3d15c604b0fc8cc48858d38b3d28bc0c711eb0cba8634b94510f8139f95` |
| `m9_overlap_only_contract.json` | `19290a2bfeaf46b35185f0f61f6ee5d8fb688f3c67fefa8430cd143391fee70b` |
| `m9_overlap_source_launcher.py` | `4e3d4d11685d4d28ee3f708edbdfc1fe44b2148df423e817f4d6cacddfc67510` |
| `m9_overlap_common.py` | `a58cea8676b1825e44a2c8dbda16c591c148c15f8a513d1ee96fb8ffe9e4b52e` |

专用 consumer manifest 为 20/20 哈希匹配；原 overlap manifest 为 16/16 哈希匹配。独立以 UID1000 调用原 `verify_overlap_control_directory()` 通过，适配器位于单独的 `06_reproduction/controllers/`，没有进入或改变原 `06_reproduction/scripts/` source-launcher 可执行闭集。

## 已通过的设计边界

适配器的顶层参数过滤只接受 `run`、`--overlap-operation` 和 `--overlap-action source_prepare`，拒绝其他 action 及自由 `--` argv。原 controller 在 UNLIMITED 分支还会再次要求 `action == "source_prepare"`，所以重复参数不能把 consumer scope 扩展为 `source_build`。smoke、batch、GPU 和通用 shell command 均未获得新入口。

`verify_consumer_gate()` 对 consumer gate 与历史 execution-fact gate 使用原冻结 `read_d018_control_json()`，要求 root:UID1000-group、`0640`、普通文件、`nlink=1`。主动重放确认：consumer gate 增加 hardlink、execution gate 改为 `0660`、冻结成员改成 symlink、任一 source product 出现时均退出码非零。consumer gate 的必需字段闭集、精确 scope、verdict/report/work-package、授权、consumer frozen manifest、execution gate SHA、sealed execution runtime canonical hash、D-018 transaction 与可读 runtime 字节哈希均有显式绑定。

真实 `setuid(1000)` 的官方临时 fixture 验证为 PASS，且 root-private D-017 gate、D-018 journal/snapshot 保持 root:root、`0600`，没有被降权或读取。该结果证明旁路适配器确实消除了上一版“UID1000 必须直接读取 root-private 证据”的矛盾；下述失败来自新的完整性实现缺口，而不是原问题仍未改变。

## D018-UID-B01：可读 runtime 的 owner/group/mode 未进入收据与比较

**级别：BLOCKING。**

### 证据

`consumer_runtime_receipts()` 在适配器第 81—103 行对九项运行态调用 `m9.read_stable_regular_bytes()`，但只把 SHA-256 写入 `runtime`，ledger 另加字节数。原 reader 只拒绝非普通文件、symlink、`nlink != 1` 和单次读取期间 inode/path 变化；它不会强制每类正式对象的 owner、group 或 mode。consumer gate 的 runtime 结构也没有保存这些 metadata，故后续等值比较不可能发现纯 metadata 漂移。

在 root 创建、UID1000 消费的真实临时子进程中，以下三项分别独立修改，文件字节和 consumer gate 均不改，verifier 每次仍返回退出码 0：

```text
state_mode_0666|rc=0
d018_tx_owner_uid1000|rc=0
source_tx_mode_0666|rc=0
```

这直接违反工作包第 3 节“任何 owner、group、mode、link count 漂移均拒绝”的门控。尤其 D-018 transaction 从 root 所有改为 UID1000 所有后仍 PASS，会把原本不可由消费者替换的执行事实对象降为同一消费者可控，而 gate 只比较内容哈希，不能表达这一信任边界变化。

### 关闭条件

应为九类可读 runtime 定义逐对象的精确 owner/group/mode/nlink 期望，并把单 FD 得到的完整 receipt 纳入 consumer gate runtime 或等价的确定性绑定。语义检查必须使用同一次稳定读取所得 payload，不能再通过路径进行未绑定读取。测试应逐项覆盖 owner、group、mode、nlink、symlink、非普通文件和路径换 inode，并验证拒绝发生在正式 transaction/capability/state/workflow/ledger 首次写入之前。

## D018-UID-B02：20 项冻结闭集未拒绝 hardlink 与 metadata 漂移，且执行对象为消费者可写

**级别：BLOCKING。**

### 证据

适配器第 176—182 行对 frozen member 依次调用 `path.is_symlink()`、`path.is_file()` 和 `path.read_bytes()`，随后只比较 SHA-256。该实现既不是单 FD 稳定读取，也不检查 `nlink`、owner、group 或 mode。独立在真实 UID1000 fixture 中对唯一冻结成员实施下列变化，verifier 均返回退出码 0：

```text
frozen_control_hardlink|rc=0
frozen_control_mode_0666|rc=0
frozen_control_owner_uid1000|rc=0
```

symlink 负例会被现有显式检查拒绝，但 hardlink 保持同一内容哈希且 `is_file()` 为真，因而绕过。多次基于路径的检查之间还存在 rename/symlink 换入窗口。

正式 `/mnt/e` 现场进一步显示 adapter、原 controller、consumer contract 和 consumer frozen manifest 当前均呈 `UID1000:UID1000/0777/nlink=1`，UID1000 的 `test -w` 为 true。adapter 在任何 gate/frozen 验证前就由 Python 执行，并先加载原 controller；因此，仅由正在执行的同一 UID1000 代码事后核对自身及已加载 controller 的路径哈希，不能建立“实际执行字节等于 root 审计冻结字节”的先验。即使不采用恶意消费者模型，该 metadata 事实也与工作包要求的完整 owner/mode/link 漂移拒绝不一致。

### 关闭条件

所有 frozen member 至少应通过单 FD、`O_NOFOLLOW`、读前/读后/path 同 inode检查，并强制 `nlink=1` 及冻结的 owner/group/mode。对 adapter 和其将加载的 controller，还需要在执行发生前建立 root 信任：例如由 root-owned、UID1000 不可写的固定入口验证并执行已绑定字节，或把经审计适配器部署为 root-owned、UID1000 只读可执行对象。不能依靠可写适配器的自验证来证明自身未被替换。原 16/16 source-launcher 闭集可以继续逐字节不变，但新增 consumer 信任入口必须拥有独立、可验证的执行前保护。

## D018-UID-B03：runtime receipt 与语义复读之间存在可通过的跨对象 TOCTOU

**级别：BLOCKING。**

### 证据

适配器第 216 行先调用 `consumer_runtime_receipts()` 并与 consumer/execution gate 比较；第 222—226 行随后又按路径调用 `load_state()`、`load_workflow_state_budget()` 和 D-018 transaction 的 `read_text()`。因此，hash receipt 所代表的 payload 与语义条件所解析的 payload不是同一稳定读取结果。

独立在真实 UID1000 子进程中建立与正式 owner 可写性相同的 state，在 `consumer_runtime_receipts()` 返回后、`load_state()` 前加入一个不影响 `UNLIMITED`、hard-stop 和 active transaction 判断的新字段。结果为：

```text
cross_read_toctou|rc=0|current_equals_sealed=False
```

即 verifier 返回 PASS 时，路径上当前 state 的 SHA-256 已不等于 consumer gate 的 `runtime.state_sha256`。`budget.lock` 只能约束遵守同一锁协议的 controller；正式 state、workflow、ledger 和历史普通 transaction 由 UID1000 所有，同一 UID 的外部进程能够不取得该 advisory lock 而改写或换入对象。所谓“最后 runtime 代理再次验证”仍调用同一存在窗口的函数，不能关闭 receipt 与语义复读之间的不一致。

### 关闭条件

每项语义判断应直接解析并使用同一次单 FD 稳定读取所得 payload；不得在 receipt 比较通过后重新按路径读取相同对象。最终代理需要对全部消费者可写 runtime 取得一个内部自洽的快照，并在原 controller 首次持久化之前验证该快照仍对应当前受控对象；若设计继续依赖 `budget.lock`，还应明确并测试非合作同 UID 写入者的边界，或通过文件所有权/受控写入代理使消费者不能绕过锁直接替换关键证据。定点测试必须建立 receipt 后换 inode/换内容的确定性窗口，并断言 verifier 非零退出且没有 Popen/状态写入。

## 回归、格式与正式现场

固定 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 独立重放结果：

```text
Ran 109 tests in 25.670s
OK

Ran 5 tests in 0.082s
OK
```

四个 Python 对象 AST 解析 4/4；consumer JSON 与相邻合同 JSON 为 4/4；Pandoc/MathML 5/5；所查送审对象控制字符为 0；controllers/scripts/tests 的 `__pycache__` 目录为 0。上述通过项证明原回归和当前五项专用测试内部一致，但五项专用测试只改变五个 runtime 的内容字节，且其 lock proxy 测试用 mock 直接调用代理；没有覆盖本报告的 metadata、frozen hardlink 和 receipt 后语义复读窗口。

正式 WSL 九项 consumer-readable runtime 在审计前后 SHA-256 完全不变：

| 对象 | SHA-256 |
|---|---|
| budget state | `c56532b1f92573bd4324464d0b10004df4b5f8337d1e803fdcd80a2f320585a8` |
| workflow | `bd895b2831c805c44a180012ece64bdda00744340768c7062e33b856069fda8a` |
| ledger | `178106f0be9f80ff669ebd0865e214a4b9a60d115074ad0c97ae8de5f1ae33b7` |
| overlap transaction | `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309` |
| D-017 recovery transaction | `e9b8babcff8a2f42adea21d5cbce614b38f0854271d3389eae0bbcdd7d5e53bc` |
| D-018 migration gate | `286a0e409a80f85ca6bb39b76bdb977fc67ffa56f4646b00d3aad5943c98e880` |
| D-018 transaction | `41cbfbd4da1c3a0eea92731a00758355f46321d5b0a66260f53f628290d847ad` |
| execution-fact gate | `bc51209c13570839c08dd4fc304fe39865a98ade69caeb23886602de2d8be6e9` |
| active overlap gate | `78311a978c2472c85b35a745d80e1f33724c1500cf8d7bd244cdbe83c3fa3698` |

root-private D-017 gate、D-018 journal、snapshot 与 retired gate 也保持原 SHA、owner/group/mode/nlink/inode。六项 source/build 产品全部缺席，正式 consumer gate 缺席，capability 目录没有新增 active capability。本审计没有对正式 WSL 状态执行写操作。

## 最终门控

当前不允许机械创建 `/home/evan-williams/deeph-m9/manifests/overlap_unlimited_wall_clock_uid1000_consumer_gate.json`。不生成结构化 PASS verdict。

主 agent 仅可修复 `D018-UID-B01`、`D018-UID-B02`、`D018-UID-B03`，补齐真实 UID1000 metadata、hardlink/执行前信任和确定性 TOCTOU 回归，更新专用合同、工作包、测试与 consumer frozen manifest，然后将完全冻结的修订快照交回同一独立审计员定点复核。在获得 `PASS/BLOCKING=0/NON_BLOCKING=0` 前，不得创建正式 consumer gate，不得执行 `source_prepare` 或 `source_build`。
