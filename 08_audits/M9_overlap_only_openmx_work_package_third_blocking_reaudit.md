# M9 overlap-only OpenMX 工作包第三次定点复核

## 复核结论

第三次定点复核结论为 `FAIL`。`M9-OLP-B01` 已满足第二次复核规定的最小关闭条件；`M9-OLP-B07` 仍为 `OPEN`。已关闭的 `M9-OLP-B02`、`M9-OLP-B04`、`M9-OLP-B06` 未发现相邻回归。没有新增稳定问题 ID。当前统计为 `BLOCKING=1`、`NON_BLOCKING=0`。

当前不允许创建运行时 `overlap_work_package_audit_gate.json`，不允许启动 apt 安装、HDF5/OpenMX 解压或构建，不允许生成结构 500 的真实输入，也不允许运行单结构 smoke。`M9-DATA-B01` 因缺失 overlap 继续为 `OPEN`，M9-05 不得启动。遗留问题可在 D-017 既有授权内修复，不需要新的用户路线决策。

送审对象身份独立重算一致：第二次定点复核报告 SHA-256 为 `a88ba0ac3321313d249f88edcf9e2a225ad4b87935da51a8dff664af7a90c342`；工作包为 `aa303b100314c936be667aa8388e995a522cb8bd5b684c2836c274a36b34ea7a`；冻结清单为 `fc51fb8f8df9f82812840277995da27dd84b4fe2e10ee6bc0cf896be432a67a4`。

## 边界与独立方法

本次复核只读检查冻结项目对象、现有 WSL 来源和状态，并在系统临时目录运行无正式产物的合成穿透。没有安装 apt 包，没有解压或编译 HDF5/OpenMX，没有生成真实输入，没有运行 OpenMX，也没有创建 audit gate、workflow 或 transaction。唯一新增项目文件为本报告。

独立复核对象包括：

- [`M9_overlap_only_openmx_work_package_second_blocking_reaudit.md`](M9_overlap_only_openmx_work_package_second_blocking_reaudit.md)；
- [`M9_overlap_only_openmx_work_package.md`](M9_overlap_only_openmx_work_package.md)；
- [`m9_overlap_frozen_hashes.json`](../06_reproduction/manifests/m9_overlap_frozen_hashes.json)；
- [`m9_overlap_only_contract.json`](../06_reproduction/configs/m9_overlap_only_contract.json)；
- [`m9_budget.py`](../06_reproduction/scripts/m9_budget.py)、[`m9_openmx_build.py`](../06_reproduction/scripts/m9_openmx_build.py)、[`m9_openmx_input.py`](../06_reproduction/scripts/m9_openmx_input.py)、[`m9_overlap_common.py`](../06_reproduction/scripts/m9_overlap_common.py)、[`m9_overlap_contract.py`](../06_reproduction/scripts/m9_overlap_contract.py)、[`m9_overlap_executor.py`](../06_reproduction/scripts/m9_overlap_executor.py) 与 [`m9_overlap_source_launcher.py`](../06_reproduction/scripts/m9_overlap_source_launcher.py)；
- [`test_m9_overlap_controls.py`](../06_reproduction/tests/test_m9_overlap_controls.py)、[`budget_contract.json`](../06_reproduction/manifests/budget_contract.json) 与 [`openmx_overlap_source_manifest.json`](../06_reproduction/manifests/openmx_overlap_source_manifest.json)。

冻结清单登记的 16 个对象逐项重新读取并计算 SHA-256，结果为 16/16 一致；13 个 Python 对象全部以 UTF-8 解码并通过独立 AST 解析。冻结的 WSL Python 3.9 以 `-I -B` 直接运行正式测试文件，18/18 通过。测试通过数仅作为回归证据；下述结论还来自真实启动语义、控制流和独立负例。

## 遗留项定点复核

### `M9-OLP-B01`：`CLOSED`

冻结构建 PATH 已收紧为 `/usr/sbin:/usr/bin:/sbin:/bin`，构建和预算子进程都不再搜索 `/usr/local`。makefile 的 `CC`、`FC` 分别以绝对 `/usr/bin/mpicc`、`/usr/bin/mpif90` 启动，构建驱动还对两个 wrapper 执行 `--showme:command`：结果必须严格分别为单 token 的 `gcc`、`gfortran`，再按冻结 PATH 解析并与已登记 `/usr/bin/gcc`、`/usr/bin/gfortran` 的规范对象比较。解析对象的路径、字节和 SHA-256 均写入构建来源记录。

独立合成重放确认 `gcc` 与 `gfortran` 按新 PATH 分别解析到已登记的 GNU 11 规范对象；改变固定 PATH 使假 `/usr/local/bin/gcc` 前置时，wrapper 校验在构建前拒绝。现有工具版本、可执行对象哈希、HDF5/OpenMPI/ScaLAPACK/FFTW/BLAS/LAPACK 动态库来源检查仍保留。因此第二次复核指出的“MPI wrapper 底层编译器未唯一绑定”路径已关闭，B01 全部最小关闭条件满足。

### `M9-OLP-B07`：仍为 `OPEN`

已关闭的部分包括：预算入口与 source launcher 都要求冻结 Python 的 isolated 与 dont-write-bytecode 标志，预算固定调用 launcher argv 为 `python3.9 -I -B`；脚本目录与当前目录不得出现在 `sys.path`；控制目录必须恰好等于冻结清单登记的 12 个 Python 文件，并拒绝未登记 `.py`、`.pyc`、`.pyo`、`__pycache__`、子目录和符号链接；launcher receipt 同时绑定预算与 launcher 的 bootstrap provenance、五个项目模块的 source-only loader provenance。相邻 sourceless `argparse.pyc` 在普通 `-B` 下执行 `MALICIOUS`、在 `-I -B` 下不再由脚本目录载入的现有负例也独立复现通过。

但是，`-I` 并不隐含 `-S`。冻结 Python 在 `-I -B` 下仍自动导入 `site`，`sys.path` 实际仍包含环境的 `site-packages`；Python 会在执行 `m9_budget.py` 或 launcher 正文之前处理该目录中的 `.pth` 文件，其中以 `import` 开头的行可以执行任意 Python 代码。入口正文内的 `isolated_bootstrap_provenance()` 只能事后记录四个 stdlib 模块，既不能阻止此前 `.pth` 执行，也没有冻结、枚举或哈希 site-packages 的 `.pth`、`sitecustomize.py`、`usercustomize.py`。

本次使用同一个冻结 Python 3.9 在系统临时目录创建无 pip 的临时 venv，并在其 site-packages 放置只含一行 import 的恶意 `.pth`。以正式同型 `-I -B -c "print('SAFE_BODY')"` 启动时，入口正文前实际输出 `MALICIOUS_PTH`，随后才输出 `SAFE_BODY`；改为 `-I -S -B` 后只输出 `SAFE_BODY`。该负例不依赖脚本目录、当前目录或 `.pyc`，直接证明当前修复尚未建立“入口正文前无未冻结代码执行”的可信边界。

该路径与第二次报告 B07 的根因相同，即 source-only loader 与 receipt 建立之前仍可由 Python 默认启动机制执行未冻结对象，因此继续使用原稳定 ID，不新增问题。

最小关闭条件：所有正式 Python 控制入口与预算生成的 launcher argv 必须禁用自动 site 初始化，例如冻结为 `-I -S -B`，并核对 `sys.flags.no_site`；正式 `sys.path` 不得包含 site-packages 或其他非冻结第三方搜索路径。若必须保留 site，则必须在解释器启动前以外部可信机制冻结并核对全部 `.pth`、sitecustomize、usercustomize 及其可达代码，但现有工作包没有这种机制。应新增端到端恶意 `.pth` 负例，证明其 import 行在预算入口与 launcher 正文之前均不能执行；现有控制目录、相邻 pyc、两层 bootstrap receipt 和 DeepH source-only 检查应保持不回归。

## 已关闭项相邻回归

### `M9-OLP-B02`：保持 `CLOSED`

官方编译清理后与 overlap 覆盖后的实际受控路径仍分别枚举，路径集合必须相等，内容差异仍严格限制为 `source/openmx.c`、`source/truncation.c`。构建产物 allowlist、未登记普通文件拒绝、HDF5 configure/check 证据、完整安装树 inventory、库哈希及两阶段清单哈希均保留。B01 的 PATH 修复没有放宽该树和来源合同。

### `M9-OLP-B04`：保持 `CLOSED`

公开环境变量仍不能建立预算上下文；自由 argv 仍被拒绝。一次性 capability 继续绑定父子 PID、transaction、固定动作、结构、桶、forecast 与精确 `-I -B` launcher argv，并由 launcher 私有原子消费。B07 的 site 启动缺口会破坏整个 Python 入口的可信前提，但没有发现 capability 机制自身对 B04 条件的相邻回归；B07 在修复并复核通过前仍统一阻止外部动作。

### `M9-OLP-B06`：保持 `CLOSED`

非零 forecast 下界、batch 每结构投影下界、三口径 10 GiB 上限、三个 CPU 桶、启动前 stage/next ID/forecast 核对、进程组超时终止和可恢复双状态事务均保留。18 项测试中的 forecast、投影和 apt/controller/timeout 双硬停止回归通过；没有发现 PATH 或 bootstrap 修订改变预算事务行为。

## 状态、预算和授权回归

复核结束前再次只读检查，运行时 audit gate、workflow、transaction、OpenMX build root、HDF5 1.12.1 安装前缀和 overlap run root全部不存在。这与“尚未启动受控外部动作”的状态一致，也表明本次合成负例没有生成正式对象。

D-017 仍只授权冻结 450 个 graphene 结构的 same-basis overlap；Hamiltonian、SCF、能量、力、密度矩阵和其他 DFT 标签仍被禁止。B07 是 Python 启动可信边界问题，不要求改变材料体系、basis、软件对象或预算。因此当前需要的用户路线决策为“无”；主 agent 可在现有授权内修复，但必须再次由独立审计关闭。

## 最终门控

- 第三次定点复核：`FAIL`。
- `M9-OLP-B01`：`CLOSED`。
- `M9-OLP-B02`：保持 `CLOSED`。
- `M9-OLP-B04`：保持 `CLOSED`。
- `M9-OLP-B06`：保持 `CLOSED`。
- `M9-OLP-B07`：`OPEN`，`BLOCKING`。
- 新增问题：无。
- `BLOCKING=1`。
- `NON_BLOCKING=0`。
- 是否允许创建运行时 audit gate：否。
- 是否允许 apt 安装、解压、构建、结构 500 输入或 smoke：否。
- 是否允许 M9-05：否。
- 当前需要用户路线决策：无。

## 报告自身验证约定

本报告定稿后执行 UTF-8 控制字符扫描、活动本地 Markdown 链接检查，以及 Pandoc `markdown+tex_math_single_backslash`、HTML5 MathML、`--fail-if-warnings` 严格转换；输出必须包含 MathML。最后计算 SHA-256。为避免自引用改变正文，最终哈希由交付消息报告。用于验证 MathML 的审计恒等式为 \(16=16\)。
