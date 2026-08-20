# M9 D-018 UID1000 consumer 第二次独立定点复核

复核日期：2026-08-21  
复核对象：第二次冻结的 D-018 UID1000 consumer 实现，重点复核 `D018-UID-B02-R01`、`D018-UID-B04`、`D018-UID-B05` 的关闭条件及相邻新增问题  
复核方式：冻结闭集复算、源码控制流审阅、临时目录与故障注入重放、恶意顶层代码穿透、固定 Python 回归、AST/JSON/Pandoc/控制字符/cache 检查、正式 WSL 运行态前后只读核对  
执行边界：未创建正式 bootstrap、snapshot、staging 或 consumer gate；未执行 `source_prepare`、`source_build`、smoke、batch、GPU 或任何正式迁移动作；未访问网络或外部系统

## 复核结论

**FAIL**。`BLOCKING=1`，`NON_BLOCKING=0`。

第二次冻结实现已经关闭上一报告中的三个既有问题：工作包 single-FD loader 固定并执行同一组 bootstrap 字节；bootstrap 建立 root-owned 严格闭集；产品缺席改用 `lexists`；bootstrap 与 snapshot 的 `0550` sealed staging 均可在最终 rename 失败后，以同一冻结输入验证并续提。固定 Python 的原 109 项测试与 consumer 14 项测试全部通过，consumer 23/23 和 overlap 16/16 冻结闭集在本次审计采样时均匹配。

但是，发现一个相邻阻塞项 `D018-UID-B06`：冻结 installer 在模块顶层根据自身是否位于 trusted 路径选择 adapter；当项目侧 installer 被直接执行时，它选择 UID1000 可写的项目侧 adapter，并在 `main()` 的 trusted-installer 身份拒绝之前调用 `exec_module()`。临时恶意 adapter 的顶层 marker 已在 installer 非零退出之前实际写出。因此，“项目侧入口不能直接作为正式入口”在进程退出状态上成立，但在“不执行未受信任代码”这一必要安全语义上不成立。

本轮不得生成结构化 PASS verdict，不允许创建正式 bootstrap、snapshot 或 consumer gate，也不允许消费 consumer gate 执行 `source_prepare`。本报告不授权 `source_build` 或任何后续动作。

## 审计冻结边界

本次独立复核采样并重算的送审核心对象如下：

| 对象 | SHA-256 | bytes | 采样结果 |
|---|---|---:|---|
| `06_reproduction/controllers/m9_budget_uid1000_consumer.py` | `65173bd85c9bf1687de959c16e5474ee1f18e20ae4a9fcbdf1d2953fb2672fb7` | 19527 | 与送审值一致 |
| `06_reproduction/controllers/m9_uid1000_consumer_bootstrap.py` | `470278705aabc14f493cd3c8fe774a4e152bd174d7f78068495cee4811430353` | 11825 | 与送审值一致 |
| `06_reproduction/controllers/m9_uid1000_consumer_install.py` | `85354ee57f8a842b8daa061cbd3bae4d4ced93241f6fefcb02a750331af41628` | 19506 | 与送审值一致 |
| `06_reproduction/tests/test_m9_uid1000_consumer.py` | `e5bc99252347d906c3b4cce7404f37b1a91fb84a88676c87d0845b0c128acfa1` | 29258 | 与送审值一致 |
| `06_reproduction/manifests/m9_uid1000_consumer_contract.json` | `d0e88b3453aeb3dd3176329f60edc955a93be356e4e28871f74da2c87a68b9c2` | 3342 | 与送审值一致 |
| `06_reproduction/manifests/m9_unlimited_wall_clock_uid1000_consumer_frozen_hashes.json` | `5a0f125cafa11bc8af4a61c9e87f566b3f7146f186bbc494c4464b483f5b3a61` | 3902 | 与送审值一致，23/23 |
| `08_audits/M9_unlimited_wall_clock_uid1000_consumer_work_package.md` | `fbd499832b16e1eae74d3749af80ada9fa36273bcc2ce3df840c8bffac2ba019` | 9995 | 与送审值一致 |

原 source-launcher 控制面同时保持原冻结值：`m9_budget.py` 为 `25c92810de52229ff626b4d54f4bd2084453e2e834ff830232b8599033f6cce5`，原测试为 `8fd7b0eafebbe0d58f1e7c13ba0d5ede9881efd9cb070ecaa0bf6ab648073e59`，overlap frozen manifest 为 `db01a3d15c604b0fc8cc48858d38b3d28bc0c711eb0cba8634b94510f8139f95`，16/16 逐项匹配。旁路 consumer 层没有扩张原 source launcher 的可执行闭集。

发现 `D018-UID-B06` 后，主工作区出现了新的 installer/test 字节。该后续修订不属于上述冻结采样，也不参与本报告结论；它必须更新工作包、合同、测试、台账和冻结清单后形成新的完整闭集，再接受独立复核。本报告保留原冻结快照的失败事实，不把后续未冻结修订倒推为本轮通过。

## 既有阻塞项关闭结果

| 问题 | 结果 | 独立证据与边界 |
|---|---|---|
| `D018-UID-B02-R01` | **关闭，但产生相邻 B06** | 工作包 loader 以 `O_RDONLY|O_CLOEXEC|O_NOFOLLOW` 单次打开 bootstrap，要求普通文件且 `nlink=1`，从同一 FD 读取、前后 `fstat` 和路径身份稳定、核对固定 SHA，再对捕获的同一 payload `compile/exec`。symlink 与 hardlink 负例均非零退出且无 marker。bootstrap 再以相同 single-FD 语义读取 installer/adapter，建立 root:group1000 的 `0550` 严格闭集，成员 `0440`、`nlink=1`，并绑定 bootstrap、installer、adapter、frozen manifest、PASS verdict、PASS report 六个审计哈希和 receipt。该链保护了被授权的工作包 loader 路径；但项目 installer 仍可被直接启动并先执行 project adapter，故新增 B06。 |
| `D018-UID-B04` | **关闭** | consumer 以 `os.path.lexists(path)` 判定 source/build product 路径是否已占用。独立与固定回归均确认：指向不存在目标的悬空 symlink 仍被登记为 present 并拒绝，未再被 `Path.exists()` 误判为缺席。普通文件、目录及 symlink 均不能穿过产品缺席门控。 |
| `D018-UID-B05` | **关闭** | bootstrap 和 snapshot 的 staging 在封存为 root:group1000/`0550` 后，如果最终 `os.replace` 失败，重放会先核对 staging 类型、owner/group/mode、闭集、成员 `0440`/`nlink=1`、receipt/manifest 与当前冻结输入；完全一致时只续提最终 rename，不重新读取未冻结项目代码。bootstrap 与 snapshot 两条 rename-failure 注入测试均能由同一输入完成；异常 sealed staging 则拒绝。 |

目录闭集、symlink、hardlink、owner/group/mode/nlink、固定参数和 receipt 的主动负例未发现相邻回归。正式入口 scope 仍严格为 `ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018`；adapter 仍只接受固定的 `source_prepare` argv，拒绝 `source_build`、通用命令与 GPU bucket。

## D018-UID-B06：项目 installer 在身份拒绝前执行未受信任 adapter

**级别：BLOCKING。** 这是本轮新发现的相邻问题。

### 控制流事实

送审冻结 installer 在模块顶层执行以下顺序：

1. 解析 `RUNNING_INSTALLER = Path(__file__).resolve(strict=True)`；
2. 当它不是 trusted installer 时，把 `ADAPTER_IMPORT` 设为项目侧 `PROJECT_ADAPTER`；
3. 通过 `spec_from_file_location()` 构造模块，并立即执行 `specification.loader.exec_module(consumer)`；
4. 进入 `main()` 后才解析正式 trusted installer，并以 `RUNNING_INSTALLER != trusted_installer` 拒绝项目侧入口。

因此，项目侧命令最终 `rc != 0` 不能证明未受信任代码没有执行。DrvFS 项目 adapter 属于 UID1000 可写工作区；root 启动项目 installer 后，adapter 顶层代码在 trusted-path 检查之前以 root 权限运行。后续拒绝或 hash 失败无法撤销已经发生的副作用。

### 主动穿透

独立测试仅在自动清理的临时目录中复制送审 installer，把其 `PROJECT_ADAPTER` 固定路径替换为临时恶意 adapter。恶意 adapter 在模块顶层写 marker，并提供 installer 完成 import 所需的最小常量。以 root 身份、固定 Python 参数启动该临时项目 installer，得到：

```text
DIRECT_INSTALLER_RC=1
MARKER_EXISTS=True
MARKER_VALUE=EXECUTED_BEFORE_REJECTION
STDERR_LAST=trusted consumer bootstrap is not installed
```

该结果证明退出拒绝发生在恶意顶层代码执行之后。测试只写临时目录，未触碰正式 bootstrap、snapshot、gate 或运行态。

### 影响与边界

工作包 single-FD loader 与 root bootstrap 本身没有被该负例突破：从正式授权 loader 开始的链确实把 installer/adapter 固定到审计字节。问题在于项目侧 installer 仍是一个可直接启动的 Python 入口，并在证明自己位于 root-owned trusted bootstrap 之前主动导入项目 adapter。合同明确要求项目侧 bootstrap、installer、adapter 均不得直接作为正式 Python 文件入口；对 installer 而言，这一要求必须解释为“在执行任何 project adapter 字节之前拒绝”，而不只是最终返回非零。

### 关闭条件

应当在任何 adapter import、`module_from_spec` 或 `exec_module` 之前完成 installer 自身份检查。项目侧 installer 的 `__main__` 路径必须先验证 `RUNNING_INSTALLER == TRUSTED_INSTALLER.resolve(strict=True)`，不成立时立即退出；trusted installer 只能导入 `TRUSTED_ADAPTER`，不得保留项目路径 fallback。至少应增加以下确定性回归：

- 把项目 adapter 替换为带顶层 marker 的临时文件，直接执行项目 installer 后应 `rc != 0` 且 marker 不存在；
- trusted installer 对 symlink、hardlink、错误 inode、错误 owner/group/mode/nlink 和闭集漂移均应在 import 前拒绝；
- 断言 trusted installer 实际 import 的唯一 adapter 路径是 root-owned bootstrap 闭集内 `TRUSTED_ADAPTER`；
- 修复后重新冻结 installer、tests、contract、work package、台账与 23 项 manifest，避免以未冻结补丁替代审计对象。

## 回归、格式与证据一致性

固定 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 独立重放结果：

```text
Ran 109 tests in 29.688s
OK

Ran 14 tests in 1.042s
OK
```

adapter、bootstrap、installer、consumer tests 的 AST 为 4/4；四个相关 JSON 为 4/4；严格 Pandoc/MathML 为 5/5；送审文本控制字符为 0；controllers/scripts/tests 下 `__pycache__` 为 0。consumer frozen manifest 为 23/23，overlap frozen manifest 为 16/16。上述通过项证明第二次冻结实现与既有测试内部一致，但 14 项测试没有建立“项目 installer 拒绝之前 marker 必须不存在”的负例，因而不能消除 `D018-UID-B06`。

主动测试还确认：工作包 loader 的同 FD 读取/执行、bootstrap 六哈希绑定、bootstrap 闭集、snapshot 闭集、metadata 与 receipt、悬空 product symlink、bootstrap sealed staging rename 续提和 snapshot sealed staging rename 续提均按合同工作。没有发现 B04/B05 或原 source-launcher 16 项闭集回归。

## 正式运行态与零写证明

审计前后 13 项正式运行态的 SHA-256 保持一致：

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

正式 `/home/evan-williams/deeph-m9/controls/uid1000-consumer-bootstrap`、其 `.staging`、正式 `/home/evan-williams/deeph-m9/controls/uid1000-consumer`、其 `.staging` 以及 consumer gate 均保持缺席。六项 source/build 产品、source_prepare transaction/capability 也未因本次审计生成。CPU、GPU、存储预算、全部历史 raw usage/credit、ledger 前缀、D-017/D-018 历史证据和无墙钟策略均未改变。

## 最终门控

本轮明确结论为：

- **不允许**生成 `M9_unlimited_wall_clock_uid1000_consumer_final_verdict.json`；
- **不允许**机械创建正式 root bootstrap、consumer snapshot 或 consumer gate；
- **不允许**启动 UID1000 `source_prepare`；
- **不授权**`source_build`、smoke、batch、GPU 或通用命令。

主 agent 应只修复并冻结 `D018-UID-B06`：把 installer 自身份拒绝移到任何 adapter import/执行之前，并以“直接执行项目 installer 时恶意 top-level marker 不存在”作为强制负例。形成新的完整冻结闭集后，应交回同一独立审计员复核；只有独立结论为 `PASS/BLOCKING=0/NON_BLOCKING=0` 时，才可生成结构化 consumer verdict 并进入机械创建正式 bootstrap/snapshot/gate 的下一门控。
