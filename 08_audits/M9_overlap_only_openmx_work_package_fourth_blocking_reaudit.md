# M9 overlap-only OpenMX 工作包第四次定点复核

## 复核结论

第四次定点复核结论为 `FAIL`。`M9-OLP-B07` 的 `.pth` 启动穿透已经关闭，但“所有正式入口只允许冻结 Python”仍有一个可执行缺口，因此 B07 继续为 `OPEN`。已关闭的 `M9-OLP-B01`、`M9-OLP-B02`、`M9-OLP-B04`、`M9-OLP-B06` 未发现相邻回归。没有新增稳定问题 ID。当前统计为 `BLOCKING=1`、`NON_BLOCKING=0`。

当前不允许创建运行时 `overlap_work_package_audit_gate.json`，不允许启动 apt 安装、HDF5/OpenMX 解压或构建，不允许生成结构 500 的真实输入，也不允许运行单结构 smoke。`M9-DATA-B01` 因缺失 overlap 继续为 `OPEN`，M9-05 不得启动。遗留问题可在 D-017 既有授权内修复，不需要新的用户路线决策。

送审对象身份独立重算一致：第三次定点复核报告 SHA-256 为 `aa93a3711ae5143d2c968deae4dfb54df75727d72106b9e9f5b1443218915de4`；工作包为 `9cc36ddcda704b3434b1bb5a26bbab0f20e673ebe532133e834e775157b66d66`；冻结清单为 `4d004c0b0647c696bd6e3e8bdebf92b5bf4b19ff97bd11113e0cea4dd4a35aa5`。

## 边界与独立方法

本次复核只读检查冻结项目对象、现有 WSL 环境和状态，并在系统临时目录运行无正式产物的合成穿透。没有安装 apt 包，没有解压或编译 HDF5/OpenMX，没有生成真实输入，没有运行 OpenMX，也没有创建 audit gate、workflow 或 transaction。唯一新增项目文件为本报告。

独立复核对象包括：

- [`M9_overlap_only_openmx_work_package_third_blocking_reaudit.md`](M9_overlap_only_openmx_work_package_third_blocking_reaudit.md)；
- [`M9_overlap_only_openmx_work_package.md`](M9_overlap_only_openmx_work_package.md)；
- [`m9_overlap_frozen_hashes.json`](../06_reproduction/manifests/m9_overlap_frozen_hashes.json)；
- [`m9_overlap_only_contract.json`](../06_reproduction/configs/m9_overlap_only_contract.json)；
- [`m9_budget.py`](../06_reproduction/scripts/m9_budget.py)、[`m9_openmx_build.py`](../06_reproduction/scripts/m9_openmx_build.py)、[`m9_openmx_input.py`](../06_reproduction/scripts/m9_openmx_input.py)、[`m9_overlap_common.py`](../06_reproduction/scripts/m9_overlap_common.py)、[`m9_overlap_contract.py`](../06_reproduction/scripts/m9_overlap_contract.py)、[`m9_overlap_executor.py`](../06_reproduction/scripts/m9_overlap_executor.py) 与 [`m9_overlap_source_launcher.py`](../06_reproduction/scripts/m9_overlap_source_launcher.py)；
- [`test_m9_overlap_controls.py`](../06_reproduction/tests/test_m9_overlap_controls.py)、[`budget_contract.json`](../06_reproduction/manifests/budget_contract.json) 与 [`openmx_overlap_source_manifest.json`](../06_reproduction/manifests/openmx_overlap_source_manifest.json)。

冻结清单登记的 16 个对象逐项重新读取并计算 SHA-256，结果为 16/16 一致；13 个 Python 对象全部以 UTF-8 解码并通过独立 AST 解析。冻结的 WSL Python 3.9 以 `-I -S -B` 直接运行正式测试文件，18/18 通过。测试通过数仅作为回归证据；下述结论还来自真实入口控制流和独立负例。

## `M9-OLP-B07` 定点复核

### 已关闭部分：site、`.pth` 与相邻 bytecode

预算生成的 source launcher argv 已冻结为 `python3.9 -I -S -B`。预算入口与 launcher 的 bootstrap 检查都要求 `isolated=true`、`no_site=true`、`dont_write_bytecode=true`，并拒绝 bootstrap `sys.path` 中的脚本目录、当前目录和 site-packages。冻结 Python 3.9 在该模式下的实际 `sys.path` 只有标准库 zip、标准库目录和 `lib-dynload`，没有 site-packages。

launcher 在原子消费并回查 capability 后建立五个项目模块的 source-only finder，载入并安装预算上下文，再读取已哈希合同。只有上述步骤成功后，合同中唯一的 dependency site-packages 才通过 `sys.path.append` 加入；代码没有调用 `site.addsitedir`，回执明确记录 `added_after_capability=true`、`method=sys.path.append`、`site_addsitedir_called=false`、`pth_processed=false`，预算端逐字段回查。普通 append 不处理 `.pth`，也不自动导入 sitecustomize 或 usercustomize。

独立临时 venv 重放确认：恶意 `.pth` 在 `-I -B` 下先于安全正文执行，而 `-I -S -B` 只执行安全正文。相邻 sourceless pyc、控制目录未登记源码/cache、项目模块 bytecode 和 DeepH parser bytecode 的既有拒绝路径也保持。因此第三次报告指出的 site 初始化缺口本身已经满足最小关闭条件。

### 未关闭部分：`overlap-init` 未强制冻结 Python 身份

工作包声称“预算入口和 source launcher 均只允许冻结 Python”。`command_overlap_run()` 确实在 bootstrap 检查之后比较 `sys.executable` 与冻结的 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9`；launcher argv 也使用该绝对解释器。但是 `command_overlap_init()` 只调用 `isolated_bootstrap_provenance()`，没有执行同一解释器身份比较。该函数只从当前 `sys.prefix` 推导标准库根，因此任意其他 Python 只要以 `-I -S -B` 启动、四个 bootstrap 模块来自它自己的标准库，就会通过。

独立无写入重放使用系统 `/usr/bin/python3.10 -I -S -B` 加载冻结 `m9_budget.py` 并调用 `isolated_bootstrap_provenance()`。检查成功返回，记录的 `python_executable` 为 `/usr/bin/python3.10`；冻结期望值为 Python 3.9，二者明确不相等。由此，在 audit gate 建立后，调用者可以用错误 Python 执行公开的 `overlap-init`，创建正式预算基线、workflow、transaction 和 capability 目录；这些状态随后被视为正式运行链的起点。

这不是纯文档偏差。初始化会写入正式预算与工作流状态，并且是后续 apt/build/smoke 的必要前置。使用未冻结解释器会使 bootstrap stdlib 来源、JSON/路径行为和初始化回执偏离 D-015/D-017 的冻结环境；同时后续 `command_overlap_run` 又拒绝错误 Python，造成正式状态由一个未授权对象创建、动作由另一个对象继续的来源断裂。现有 18 项测试只覆盖 `.pth` 和相邻 pyc，没有直接断言错误 Python 不能进入 `overlap-init`。

该问题仍属于 B07 的“所有正式入口可信启动边界”，因此沿用原稳定 ID，不新增问题。

最小关闭条件：把冻结 Python 规范身份检查提升为所有 overlap 正式动作的公共入口前置条件，至少同时覆盖 `overlap-init` 与 `--overlap-operation`，并在任何状态读取或写入前失败。可由 `isolated_bootstrap_provenance()` 同时核对 `Path(sys.executable).resolve(strict=True) == OVERLAP_PYTHON.resolve(strict=True)`，或由两条命令在调用公共验证器后才继续。增加负例：用另一 Python 的 `-I -S -B` 调用 `overlap-init`，必须在创建预算基线、workflow、transaction、capability 目录或 ledger 事件之前拒绝；冻结 Python 3.9 的同型入口应通过启动前检查。现有 no-site、`.pth`、控制目录、两层 receipt 与 source-only 检查应保持不回归。

## 已关闭项相邻回归

### `M9-OLP-B01`：保持 `CLOSED`

固定 PATH 仍为 `/usr/sbin:/usr/bin:/sbin:/bin`；MPI wrapper 的底层 `gcc`、`gfortran` 展开、规范路径、字节和 SHA-256 绑定仍存在。no-site 改动没有放宽工具链或动态库 provenance。

### `M9-OLP-B02`：保持 `CLOSED`

官方与 overlap 两阶段实际树的集合/内容比较、构建产物 allowlist、HDF5 configure/check、安装树 inventory 和库哈希均保留。未发现 B07 修订改变构建来源合同。

### `M9-OLP-B04`：保持 `CLOSED`

公开环境变量与自由 argv 仍不能建立预算上下文；一次性 capability 继续绑定父子 PID、transaction、动作、结构、桶、forecast 和精确 `-I -S -B` launcher argv，并原子消费。错误 Python 的 `overlap-init` 路径发生在 capability 创建之前，属于 B07 的入口可信性，而不是 B04 capability 条件的回归。

### `M9-OLP-B06`：保持 `CLOSED`

非零 forecast 下界、batch 投影下界、三口径 10 GiB 上限、CPU 桶、进程组终止和可恢复双状态事务均保留；相关正式测试通过。未发现 no-site 或依赖 append 改变预算事务行为。

## 状态、预算和授权回归

复核结束前再次只读检查，运行时 audit gate、workflow、transaction、OpenMX build root、HDF5 1.12.1 安装前缀和 overlap run root全部不存在。这与“尚未启动受控外部动作”的状态一致，也表明本次合成负例没有生成正式对象。

D-017 仍只授权冻结 450 个 graphene 结构的 same-basis overlap；Hamiltonian、SCF、能量、力、密度矩阵和其他 DFT 标签仍被禁止。B07 遗留项只要求将现有解释器身份检查应用到初始化入口，不要求改变材料体系、basis、软件对象或预算。因此当前需要的用户路线决策为“无”；主 agent 可在现有授权内修复，但必须再次由独立审计关闭。

## 最终门控

- 第四次定点复核：`FAIL`。
- `M9-OLP-B01`：保持 `CLOSED`。
- `M9-OLP-B02`：保持 `CLOSED`。
- `M9-OLP-B04`：保持 `CLOSED`。
- `M9-OLP-B06`：保持 `CLOSED`。
- `M9-OLP-B07`：`OPEN`，`BLOCKING`。
- 新增问题：无。
- `BLOCKING=1`。
- `NON_BLOCKING=0`。
- 是否允许创建运行时 audit gate：否。
- 是否允许进入 D-017 的 apt 安装、解压、构建、结构 500 输入或 smoke：否。
- 是否允许 M9-05：否。
- 当前需要用户路线决策：无。

## 报告自身验证约定

本报告定稿后执行 UTF-8 控制字符扫描、活动本地 Markdown 链接检查，以及 Pandoc `markdown+tex_math_single_backslash`、HTML5 MathML、`--fail-if-warnings` 严格转换；输出必须包含 MathML。最后计算 SHA-256。为避免自引用改变正文，最终哈希由交付消息报告。用于验证 MathML 的审计恒等式为 \(18=18\)。
