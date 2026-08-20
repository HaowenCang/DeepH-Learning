# M9 D-018 UID1000 consumer 独立定点复核

复核日期：2026-08-21  
复核范围：`D018-EGF-B01`、`D018-UID-B01`、`D018-UID-B02`、`D018-UID-B03` 的关闭条件及相邻新增问题  
复核方式：冻结闭集与源码复算、真实 UID1000 临时权限重放、root 快照与安装器故障穿透、metadata/link/TOCTOU 主动测试、固定 Python 全量回归、正式 WSL 运行态前后只读核对  
执行边界：未创建正式快照、staging 目录或 consumer gate；未执行 `source_prepare`、`source_build`、smoke、batch、GPU 或正式迁移重放

## 复核结论

**FAIL**。`BLOCKING=3`，`NON_BLOCKING=0`。

修订实现已经实质关闭 `D018-EGF-B01`、`D018-UID-B01` 和 `D018-UID-B03` 的代码级问题：真实 UID1000 verifier 不再读取 root-private 证据；九项可读 runtime 使用完整 uid/gid/mode/nlink 收据；语义判断解析同次稳定读取的字节；终态再次读取全部 runtime；原 controller 首次 `atomic_json` 前再次调用完整 verifier。root-owned snapshot 一旦正确安装，成员的 `0440`、单链接、symlink/hardlink 和目录权限检查也能保护正式消费入口。

但是，`D018-UID-B02` 的端到端执行前信任尚未关闭：计划由 root 直接执行的项目侧 installer 在验证 frozen manifest 前，已经导入并执行 UID1000 可写的项目侧 adapter；installer 自身也由 UID1000 可写。另有两个相邻阻塞项：悬空的 source/build product symlink 被 `Path.exists()` 误判为缺席；snapshot staging 在 `chmod 0550` 后、rename 前失败时不能幂等续提。因此，本轮不得生成结构化 PASS verdict，不允许机械创建正式 snapshot 或 consumer gate，也不允许执行 `source_prepare` 或 `source_build`。

## 冻结对象与闭集

送审核心对象独立重算如下：

| 对象 | SHA-256 | bytes | 结果 |
|---|---|---:|---|
| `m9_budget_uid1000_consumer.py` | `f830f3219f49f0a3ae9461920ade4e6432bab7b10512f66fa7bcde31dd339159` | 19344 | 与送审值一致 |
| `m9_uid1000_consumer_install.py` | `23bd5de2873e4c04798d297f5445781b34ecbb91b225b05cb11b014a02c53a9d` | 12008 | 与送审值一致 |
| `test_m9_uid1000_consumer.py` | `26781da419702666217a4c264b5c28dd307e71d0275bfd56b50fad74ff400ec3` | 20573 | 与送审值一致 |
| `m9_uid1000_consumer_contract.json` | `1c56b37245978a56cf5fc03cb6ccfe3f43b7b63ce8e246c5f0875d4239e47b72` | 2416 | 与送审值一致 |
| consumer frozen manifest | `07c8865695293b1b895db02839fdb0ea6158ff7fcf212461b8ffe7db460ae0b7` | 3500 | 与送审值一致，21/21 |
| consumer work package | `0c834b83b9e18aae4cfe9a39138abdfc05755fb455cc15b65be6ff7502a44bf7` | 6869 | 与送审值一致 |

原 `m9_budget.py` 仍为 `25c92810de52229ff626b4d54f4bd2084453e2e834ff830232b8599033f6cce5`，原 `test_m9_overlap_controls.py` 仍为 `8fd7b0eafebbe0d58f1e7c13ba0d5ede9881efd9cb070ecaa0bf6ab648073e59`，原 `m9_overlap_frozen_hashes.json` 仍为 `db01a3d15c604b0fc8cc48858d38b3d28bc0c711eb0cba8634b94510f8139f95`。overlap 16/16 闭集逐项匹配，独立以 UID1000 调用原 `verify_overlap_control_directory()` 通过；原 source launcher、common、overlap contract、预算合同和 active overlap gate 没有因旁路层改变。

consumer manifest 的 21 项源文件逐项存在且 SHA-256 匹配。该结果证明当前工作区字节与送审冻结值一致，但不能替代下文所述“root 实际执行前信任”，因为 hash 验证函数本身必须先由可信代码执行。

## 原阻塞项关闭矩阵

| 原问题 | 定点结果 | 证据与边界 |
|---|---|---|
| `D018-EGF-B01` | **代码级关闭** | root 创建的临时 snapshot/gate 在真实 `setuid(1000)` 子进程中 verifier `rc=0`；D-017 gate、D-018 journal 与 pre-state snapshot 保持 root:root、`0600` 且不在 consumer runtime 读取集合中。正式 gate 尚未创建，故这不是正式执行事实放行。 |
| `D018-UID-B01` | **关闭** | 九项 runtime receipt 包含 path、bytes、SHA-256、uid、gid、mode、nlink，并按五项 UID1000:UID1000/0644 与四项 root:group1000/0640 分组强制。state 改 `0666`、source recovery transaction 改 `0666`、D-018 transaction 改 UID1000 owner 均稳定 `rc=1`。 |
| `D018-UID-B02` | **未端到端关闭** | 已安装 snapshot 的 root:group1000/0550 与成员 root:group1000/0440/nlink1 检查有效；snapshot hardlink 与 symlink 均 `rc=1`。但负责首次建立该信任根的 root installer 在任何 frozen/hash 验证前已执行 UID1000 可写代码，详见 `D018-UID-B02-R01`。 |
| `D018-UID-B03` | **关闭** | state/workflow/D-018 transaction 的语义解析使用 `consumer_runtime_snapshot()` 同次 payload；完成语义检查后再次读取全部 runtime 并要求完整收据相等。确定性地在第一次 snapshot 后改写 state 时，官方回归得到非零退出；原 controller 首个正式写操作是锁内 `atomic_json(OVERLAP_TRANSACTION, ...)`，适配器在调用原函数前再次完整验证。 |

正式入口的 scope 仍为且仅为 `ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018`。项目侧 adapter 直接调用被 `Path(__file__).resolve()` 身份检查拒绝；正式 adapter 必须来自 snapshot 中固定路径。参数前置检查与原 controller 的锁内 action 检查共同拒绝 `source_build`、自由 `--` argv、通用命令和 GPU bucket。

## D018-UID-B02-R01：root installer 在验证前执行 UID1000 可写代码

**级别：BLOCKING。** 这是原 `D018-UID-B02` 关闭条件的剩余部分。

### 实测与代码顺序

正式项目侧两个入口在 WSL/DrvFS 中实测均为 UID1000:UID1000、`0777`、`nlink=1`，UID1000 可写：

```text
m9_uid1000_consumer_install.py|uid=1000|gid=1000|mode=777|uid1000_write=yes
m9_budget_uid1000_consumer.py|uid=1000|gid=1000|mode=777|uid1000_write=yes
```

installer 第 17—24 行在模块顶层从项目路径构造 import specification，并立即执行 `specification.loader.exec_module(consumer)`。`verify_authorized_sources()` 到第 89 行才定义，只有进入 `main()` 后才会调用。因此，root 按合同直接运行 installer 时，项目侧 adapter 的任意顶层字节已经以 root 权限执行，随后才可能检查 adapter 是否等于 frozen hash。

installer 本身也位于同一个 UID1000 可写目录。它虽然被列入 21 项 manifest，但由 installer 自己在执行后验证自身或相邻 adapter，不能证明“已经执行的 root 代码”来自独立审计冻结字节。这正是上一报告对 `D018-UID-B02` 给出的执行前信任条件，而不是一般的执行后完整性检查。

### 影响

如果 adapter 在审计后、安装命令读取前被换入，top-level 代码可在 root 下先执行，再让后续 hash 检查失败；失败不能撤销已发生的 root 行为。即使 adapter 不变，installer 自身被换入时也没有更早的可信验证者。root-owned snapshot 对安装后的 UID1000 消费路径提供保护，但不能追溯地保护创建 snapshot 的首个 root 进程。

### 关闭条件

需要一个不从 UID1000 可写项目文件直接执行的可信 bootstrap。可接受方案应同时满足：

- bootstrap 本身来自 root-owned、UID1000 不可写对象，或由冻结命令行内联并绑定 installer 的固定 SHA；
- 以单 FD、`O_NOFOLLOW`、完整 inode/path 稳定检查读取 installer，核对固定 SHA 后执行捕获的同一字节，而不是重新按路径导入；
- installer 不得在验证项目 adapter 的 frozen hash 前 import/执行该 adapter；应先把经验证的原始字节安装到 root-owned snapshot，再从 snapshot 加载；
- 对 installer 和 adapter 的“换 inode、读后换路径、hash 后换入、恶意 top-level marker”建立确定性 root 权限负例，证明 marker 在验证失败时从未执行。

不得以“运行前人工再看一次 `sha256sum`”替代同一 FD 的验证与执行绑定，也不得把项目目录整体改成 root-owned 而破坏用户工作区。

## D018-UID-B04：悬空 source-product symlink 被判为产品缺席

**级别：BLOCKING。** 相邻新增问题。

`consumer_runtime_snapshot()` 第 220—222 行以：

```python
path.as_posix() for path in m9.SOURCE_RECOVERY_PRODUCTS if path.exists()
```

构造产品存在集合。`Path.exists()` 对悬空 symlink 返回 false。独立在真实 UID1000 fixture 中把 `SOURCE_RECOVERY_PRODUCTS` 的唯一成员设置为指向不存在目标的 symlink，得到：

```text
DANGLING_PRODUCT|rc=0|is_symlink=True|exists=False
```

consumer gate 与 execution gate 均声明 `source_products_present=[]`，verifier 因而通过。路径命名空间实际上已被占用，后续 source preparation 的目录创建、rename 或清理可能跟随或撞上该链接；更基本地说，这不满足“六项 source/build 产品及 staging 对象严格缺席”的合同。

关闭时应使用 `lstat()` 或等价的“路径对象存在”判断，只有 `FileNotFoundError` 才算缺席；普通文件、目录、FIFO、device、symlink（包括悬空 symlink）都必须登记为 present 并在首次写入前拒绝。应对六个正式产品路径逐类覆盖 dangling symlink、symlink-to-directory、普通文件和意外目录，并验证 runtime 初次读取、终态复读及首次 `atomic_json` guard 都拒绝。

## D018-UID-B05：staging 在 rename 前失败后不能幂等续提

**级别：BLOCKING。** 相邻新增问题。

成功路径的 installer 幂等测试通过：连续两次 `install_snapshot(payloads)` 返回相同 receipt/manifest，snapshot root 为 `0550`，成员为 root:group1000/`0440`/`nlink=1`。但该测试没有覆盖安装中断后的幂等性。

installer 第 194 行在 rename 前把 staging root 改成 `0550`，随后 fsync 目录并在第 200 行执行 `os.replace(STAGING_ROOT, SNAPSHOT_ROOT)`。独立令这次 replace 抛出模拟 `OSError`，首次调用留下完整但仍命名为 `.staging` 的 `0550` 目录；第二次原样调用立即在第 163—170 行要求既存 staging 必须为 `0700`，得到：

```text
FIRST_FAIL|OSError|staging_mode=0o550
RESUME|FAIL|SystemExit('consumer staging root metadata mismatch')
```

因此，一次 rename/宿主 I/O 瞬时失败会使正式机械安装无法重放，必须依赖未定义的手工删除、chmod 或移动。该状态既没有成功安装 snapshot，也不允许 installer 自己续提，与“root-only durable installer”和一次性机械创建流程的幂等要求不一致。

关闭时应把 staging 设计为可重放状态机：若发现 root:group1000/`0550` 的完整 staging，应严格验证 manifest、目录闭集、全部成员 receipt 与当前已授权 payload，随后安全地续提 rename；若是不完整或异常 staging，应在 root-only 精确目标验证后执行明确定义的恢复，而不是要求人工猜测。至少应注入 member create/chown/chmod/write/fsync、manifest write、directory chmod/fsync、rename 和 parent fsync 等故障，验证每个持久化窗口都能唯一续提或安全、明确地零写拒绝；本轮已稳定复现的 rename 窗口必须成为回归测试。

## 回归与格式验证

固定 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 独立重放：

```text
Ran 109 tests in 29.672s
OK

Ran 9 tests in 1.003s
OK
```

四个 Python 对象 AST 为 4/4；四个 JSON 为 4/4；Pandoc/MathML 为 5/5；送审对象控制字符为 0；controllers/scripts/tests 的 `__pycache__` 为 0。上述通过项说明冻结实现和现有测试内部一致，但 9 项 consumer 测试没有覆盖 installer 在 import 前的信任顺序、dangling product symlink 或 rename 失败后的 staging 续提，故不能消除三个阻塞项。

主动负例同时确认：state `0666`、source recovery transaction `0666`、D-018 transaction 改为 UID1000 owner、snapshot member hardlink、snapshot member symlink均被拒绝；baseline real UID1000 verifier 通过。这些证据支持原 B01/B03 与“安装后 snapshot member 防护”的正向关闭判断。

## 正式运行态与授权边界

审计前后正式对象的 SHA-256、bytes、owner/group、mode、nlink 和 inode 保持一致。核心值包括：

| 正式对象 | SHA-256 |
|---|---|
| budget state | `c56532b1f92573bd4324464d0b10004df4b5f8337d1e803fdcd80a2f320585a8` |
| workflow | `bd895b2831c805c44a180012ece64bdda00744340768c7062e33b856069fda8a` |
| ledger | `178106f0be9f80ff669ebd0865e214a4b9a60d115074ad0c97ae8de5f1ae33b7` |
| overlap transaction | `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309` |
| D-017 recovery transaction | `e9b8babcff8a2f42adea21d5cbce614b38f0854271d3389eae0bbcdd7d5e53bc` |
| D-017 root-private gate | `8e66d65d17d3195f3df09db954afca4066c3ec91e2d8dad6d2aea06078d0d5ce` |
| active overlap gate | `78311a978c2472c85b35a745d80e1f33724c1500cf8d7bd244cdbe83c3fa3698` |
| retired overlap gate | `dbe4756142d0e921c3834330550310e85652503c04254b30bea1a069ff35377c` |
| D-018 migration gate | `286a0e409a80f85ca6bb39b76bdb977fc67ffa56f4646b00d3aad5943c98e880` |
| D-018 transaction | `41cbfbd4da1c3a0eea92731a00758355f46321d5b0a66260f53f628290d847ad` |
| execution-fact gate | `bc51209c13570839c08dd4fc304fe39865a98ade69caeb23886602de2d8be6e9` |
| D-018 journal | `27a92edded459948150c750a4339692434e08a84cbc8879c63c71b6c14cb0e8a` |
| D-018 pre-state snapshot | `00a32bd7f28ad26fa600c8abe9d0fa64efe57e410eacb82ad2d201fa9adc5439` |

正式 snapshot root、`.staging` 和 consumer gate 均缺席；六项 source/build 产品按普通存在性检查均缺席；capability 没有新增 active 对象。此次审计的 dangling symlink 只存在于自动清理的临时目录，没有写入正式产品路径。

CPU、GPU、存储预算常量、历史 raw usage、D-017 credit、ledger prefix 与 D-018 无墙钟政策均未改变。本报告不授权 `source_build`、smoke、batch、GPU 或任何通用命令。

## 最终门控

当前 **不允许** root 机械创建正式 snapshot 或 consumer gate；不生成 `M9_unlimited_wall_clock_uid1000_consumer_final_verdict.json`。

主 agent 仅可修复：

- `D018-UID-B02-R01` 的 root 执行前信任与同 FD 验证/执行绑定；
- `D018-UID-B04` 的 dangling symlink/任意路径对象存在判定；
- `D018-UID-B05` 的完整 staging 故障续提与回归矩阵。

修订后应更新 adapter、installer、专用测试、合同、工作包和 consumer frozen manifest，完全冻结后交回同一独立审计员再次定点复核。在获得 `PASS/BLOCKING=0/NON_BLOCKING=0` 前，不得创建正式 consumer snapshot/gate，不得执行 `source_prepare` 或 `source_build`。
