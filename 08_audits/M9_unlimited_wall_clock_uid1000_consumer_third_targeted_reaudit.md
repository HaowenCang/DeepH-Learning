# M9 D-018 UID1000 consumer 第三次独立定点复核

复核日期：2026-08-21  
复核对象：第三次冻结的 D-018 UID1000 consumer 实现，重点复核 `D018-UID-B06`，并回归 `D018-EGF-B01`、`D018-UID-B01`—`D018-UID-B05` 与 `D018-UID-B02-R01`  
复核方式：冻结闭集复算、源码执行顺序审阅、root 隔离临时目录恶意顶层 marker 与逐行 trace 穿透、真实 UID1000 临时 fixture、single-FD/metadata/link/TOCTOU/rename 故障回归、固定 Python 全量测试、AST/JSON/Pandoc/控制字符/cache 检查、正式 WSL 运行态前后只读核对  
执行边界：未创建正式 bootstrap、snapshot、staging 或 consumer gate；未执行 `source_prepare`、`source_build`、smoke、batch、GPU 或其他计算；未访问网络或外部系统

## 复核结论

**PASS**。`BLOCKING=0`，`NON_BLOCKING=0`。

第三次冻结实现关闭了 `D018-UID-B06`。项目侧 installer 以 `__main__` 启动时，在计算 `ADAPTER_IMPORT`、构造 adapter specification 或调用 `exec_module()` 之前，已经依据实际 `__file__` 拒绝非 trusted 路径。独立 root 临时目录恶意 adapter 顶层 marker 没有生成；逐行 trace 的最大执行行号为拒绝行 38，未进入第 39 行 adapter 选择区域。

此前 `D018-EGF-B01`、`D018-UID-B01`—`D018-UID-B05` 与 `D018-UID-B02-R01` 的关闭条件均无回归。固定 Python 原控制测试 109/109、consumer 测试 14/14 全部通过；consumer 24/24 与 overlap 16/16 冻结闭集匹配；13 项正式运行态测试前后逐字节不变；正式 consumer 对象和六项 source/build 产品继续缺席。

因此，允许主 agent 严格按当前工作包所载 single-FD loader，由 root 机械创建一次正式 bootstrap trust set、完整 consumer snapshot 与 consumer gate。该许可不包括消费 gate：创建后仍须由同一独立审计员完成正式对象和真实 UID1000 verifier 的执行事实复核；在该事实复核明确通过前，不得启动 `source_prepare`。本报告不授权 `source_build`、smoke、batch、GPU、Hamiltonian/SCF 标签或任何通用命令。

## 冻结对象与闭集

送审核心对象独立重算如下：

| 对象 | SHA-256 | bytes | 结果 |
|---|---|---:|---|
| `m9_budget_uid1000_consumer.py` | `72297aff63ea0affc5f38b2bc15f94f7bcab4771e8a8634b529704b71b5c7524` | 19610 | 与送审值一致 |
| `m9_uid1000_consumer_bootstrap.py` | `681901e066055411f2ea03f5fc8441697288c7be369fbde272c626d9905002b5` | 11824 | 与送审值一致 |
| `m9_uid1000_consumer_install.py` | `acb06c9bc4d7ae6549b43c52ff50e957212c947c9a1cab53e50b373a66e62201` | 19688 | 与送审值一致 |
| `test_m9_uid1000_consumer.py` | `bf959be80e280253153efa5691006fd821fcbb008db3ed87bdb3cd7830463ef9` | 30910 | 与送审值一致 |
| consumer contract | `4c7a1e9aca3e01c8384178704b0cf742d2a9722372a0bf2e9623607b8df6e755` | 3341 | 与送审值一致 |
| consumer frozen manifest | `8916df81d334718b12f9b6949425e6875809066b3c99841b6e235325b4ada40b` | 4103 | 与送审值一致，24/24 |
| consumer work package | `cf545ae65954f4bd6978abe0429d66b7a209ca8be11b2e76f45b15a7765193e2` | 10318 | 与送审值一致 |
| `master_execution_plan.md` | `1b440fc8f2645ac004339fd1ef85bdfecfbaadf960355726a75cdaa37f45ed78` | 19486 | 与送审值一致 |
| `progress_tracker.md` | `e02468cf23132ddf80a568e98e745b554de42f668f126ed7a52896fc798f3cfd` | 126084 | 与送审值一致 |
| `decisions.md` | `8966638e933123ffcd2c4f6bf8ab3447887d934386b6a88138e435e2b3b0c88a` | 28624 | 与送审值一致 |

consumer manifest 的 24 项文件均存在且逐项 SHA-256 匹配。原 source-launcher 控制面继续保持 D-018 冻结值：`m9_budget.py` 为 `25c92810de52229ff626b4d54f4bd2084453e2e834ff830232b8599033f6cce5`，原测试为 `8fd7b0eafebbe0d58f1e7c13ba0d5ede9881efd9cb070ecaa0bf6ab648073e59`，overlap frozen manifest 为 `db01a3d15c604b0fc8cc48858d38b3d28bc0c711eb0cba8634b94510f8139f95`，其 16/16 逐项匹配。旁路 consumer 层没有修改原 controller、source launcher 或其可执行闭集。

## D018-UID-B06 定点穿透

### 源码执行顺序

冻结 installer 的模块顶层顺序为：

1. 仅导入 Python 标准库并定义路径常量；
2. 计算 `RUNNING_INSTALLER = Path(__file__).resolve(strict=True)`；
3. 当 `__name__ == "__main__"` 且实际路径不等于 `TRUSTED_INSTALLER.resolve(strict=False)` 时，于第 38 行立即 `SystemExit`；
4. 第 39 行之后才选择 `ADAPTER_IMPORT`，随后才可能构造 specification 并执行 adapter。

因此，项目侧 installer 的正式直接启动路径不存在“先导入项目 adapter、后拒绝”的控制流。只有 root-owned bootstrap 闭集内的 trusted installer 能继续；该路径选择的也仅是同一 root-owned 闭集内的 `TRUSTED_ADAPTER`。

### 独立恶意 marker 负例

审计在 root 隔离临时目录复制冻结 installer，只把 `PROJECT_ADAPTER` 常量指向一个无害恶意 fixture。该 fixture 的模块顶层唯一副作用是写出 marker。随后用冻结 Python `-I -S -B` 直接启动临时项目 installer，结果为：

```text
RC=1
MARKER_LEXISTS=False
STDERR_LAST=consumer installer must run from the trusted bootstrap
PROBE_RC=0
```

marker 路径按目录项语义检查，既没有普通文件也没有悬空链接。临时目录在测试结束后自动清理。

### 独立逐行 trace 负例

另以 `runpy.run_path(..., run_name="__main__")` 对真实项目 installer 安装逐行 trace；若执行到第 39 行或以后，trace 会写出独立 marker。结果为：

```text
EXIT=consumer installer must run from the trusted bootstrap
MAX_LINE=38
LOADER_REGION_REACHED=False
TRACE_RC=0
```

该结果直接证明拒绝发生在 adapter 选择、specification 创建和 `exec_module()` 之前。`D018-UID-B06` 的关闭不依赖单元测试自报结论。

## 既有问题回归矩阵

| 问题 | 结果 | 独立复核证据与边界 |
|---|---|---|
| `D018-EGF-B01` | **PASS** | 临时 root-owned snapshot/gate 由真实 EUID 1000 子进程验证通过；UID1000 只读取九项明确可读 runtime、consumer gate 与 snapshot，不读取 root:root `0600` 的 D-017 gate、D-018 journal 或 pre-state snapshot。正式 gate 尚未创建，后续仍需事实复核。 |
| `D018-UID-B01` | **PASS** | 九项可读 runtime 全部绑定 path、bytes、SHA-256、uid、gid、mode、nlink；五项 UID1000:UID1000/`0644` 与四项 root:group1000/`0640` 分类严格。owner/group/mode/nlink、symlink 和 hardlink 漂移均拒绝。 |
| `D018-UID-B02` | **PASS** | bootstrap trust set 与完整 snapshot 均要求 root:group1000、目录 `0550`、成员 `0440`、普通文件、`nlink=1` 和严格目录闭集；receipt/manifest 绑定每个成员的字节数及 SHA-256。项目侧 adapter 不能作为正式入口。 |
| `D018-UID-B03` | **PASS** | 语义解析使用与 receipt 同次稳定读取的 payload；完成检查后复读全部 runtime 并逐项相等；adapter 包装原 `atomic_json`，在第一次正式状态写入前再次执行完整 verifier。跨读取漂移与首次写入边界回归均拒绝。 |
| `D018-UID-B02-R01` | **PASS** | 工作包 loader 以 `O_RDONLY|O_CLOEXEC|O_NOFOLLOW` 单次打开 bootstrap，要求普通单链接文件，从同一 FD 读取全部字节，核对前后 `fstat`、路径 inode/metadata 和固定 SHA，再 `compile/exec` 同一 payload。bootstrap 以同类 single-FD 算法绑定 bootstrap、installer、adapter、frozen manifest、PASS verdict 与本报告六个哈希后，才建立 root-owned trust set。错误 hash、symlink、hardlink 或路径替换均在执行 payload/安装前拒绝。 |
| `D018-UID-B04` | **PASS** | source/build 产品缺席使用 `os.path.lexists`；悬空 symlink 也登记为 present 并拒绝。真实 UID1000 dangling-symlink 回归通过。 |
| `D018-UID-B05` | **PASS** | bootstrap 和 snapshot 在 staging 已封存为 `0550`、最终 rename 失败后，均先复核 owner/group/mode、闭集、成员 `0440`/`nlink=1`、receipt/manifest 与同一冻结输入，再续提 rename；不重新读取未冻结代码。两条故障注入均成功续提，异常 sealed staging 拒绝。 |
| `D018-UID-B06` | **PASS** | root 恶意顶层 marker 与逐行 trace 均证明非 trusted `__main__` 在第 38 行退出，未到达 adapter loader 区域。 |

consumer adapter 只接受 `run` 子命令、`source_prepare` action 且拒绝自由 `--` argv；原 controller 在既存 `budget.lock` 内继续执行完整 action、bucket、gate、runtime、预算和 capability 检查。consumer gate scope 固定为 `ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018`，不能授权 `source_build`、通用 run 或 GPU 动作。

## 固定回归与格式验证

使用冻结 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B`，以 root 独立重放：

```text
Ran 109 tests in 29.579s
OK

Ran 14 tests in 9.241s
OK
```

consumer 14 项测试覆盖：原 launcher 冻结、single-FD loader、项目 adapter/installer 入口拒绝、真实 UID1000 verifier、runtime 字节与 metadata、snapshot link/metadata、跨读取漂移、首次状态写入复核、dangling product symlink、snapshot 幂等安装及两级 sealed staging rename 续提。测试均在临时目录运行，没有创建正式 consumer 对象。

adapter、bootstrap、installer、consumer tests 的 AST 为 4/4；四个相关 JSON 为 4/4；严格 Pandoc/MathML 为 5/5；consumer 24 项冻结文本控制字符为 0；controllers/scripts/tests 下 `__pycache__` 为 0。测试后再次复算核心冻结 SHA，未发现送审漂移。

## 正式运行态零写与产品缺席

固定回归前后 13 项正式运行态 SHA-256 完全一致：

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

按 `lexists` 检查，以下 11 个正式路径全部缺席：bootstrap root 及其 staging、snapshot root 及其 staging、consumer gate，以及六项 source/build 产品。没有生成 source_prepare transaction 或 capability；没有改变 CPU、GPU、存储预算、历史 raw usage/credit、ledger 字节、D-017/D-018 历史证据或无墙钟策略。

## 最终门控与授权边界

本轮允许生成 `M9_unlimited_wall_clock_uid1000_consumer_final_verdict.json`，其 schema 为 `m9-unlimited-wall-clock-uid1000-consumer-audit-verdict-v1`，并绑定当前工作包与本报告的 SHA-256。

主 agent 只被允许执行下列机械步骤：

1. 严格使用当前工作包逐字节给出的 single-FD loader、冻结 Python `-I -S -B`、当前 bootstrap SHA、installer SHA、adapter SHA、consumer frozen manifest SHA、PASS verdict SHA 与本报告 SHA，由 root 创建一次 bootstrap trust set；
2. 仅从该 root-owned trust set 内的 trusted installer 创建完整 snapshot 与 consumer gate；
3. 创建完成后停止，不消费 gate，并将正式 bootstrap/snapshot/gate、receipt/manifest、owner/group/mode/nlink/闭集、运行态与真实 UID1000 verifier 提交同一独立审计员作执行事实复核。

在上述事实复核明确 `PASS/BLOCKING=0/NON_BLOCKING=0` 前，仍**不允许**启动 UID1000 `source_prepare`。`source_build`、smoke、batch、GPU、Hamiltonian/SCF 标签、正式训练或通用命令继续不在本报告授权范围内。
