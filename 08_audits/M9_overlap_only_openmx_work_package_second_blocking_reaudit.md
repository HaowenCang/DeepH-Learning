# M9 overlap-only OpenMX 工作包第二次定点复核

## 复核结论

第二次定点复核结论为 `FAIL`。`M9-OLP-B02`、`M9-OLP-B04`、`M9-OLP-B06` 已满足第一次复核规定的最小关闭条件；`M9-OLP-B01` 与 `M9-OLP-B07` 仍为 `OPEN`。没有新增稳定问题 ID。当前统计为 `BLOCKING=2`、`NON_BLOCKING=0`。

当前不允许创建运行时 `overlap_work_package_audit_gate.json`，不允许启动 apt 安装、HDF5/OpenMX 解压或构建，不允许生成结构 500 的真实输入，也不允许运行单结构 smoke。`M9-DATA-B01` 因缺失 overlap 继续为 `OPEN`，M9-05 不得启动。两个遗留项均可在 D-017 既有授权内修复，不需要新的用户路线决策。

送审对象身份独立重算一致：第一次定点复核报告 SHA-256 为 `69b74d2dd5e3ef26208cf9db59c77f2c3962f3da46cee4cd80299e0c5aac25d5`；工作包为 `c92e35f406f5bb6055067ecaa406cfa500453112b5e44bf128af55a030a155fd`；冻结清单为 `74f3c907f097f15fb77f81dd5b05f8e0da8aba003144be8f67c792d51fc30caa`。

## 边界与独立方法

本次复核只读检查冻结项目对象、现有 WSL 来源和状态，并在系统临时目录运行无正式产物的合成穿透。没有安装 apt 包，没有解压或编译 HDF5/OpenMX，没有生成真实输入，没有运行 OpenMX，也没有创建 audit gate、workflow 或 transaction。唯一新增项目文件为本报告。

独立复核对象包括：

- [`M9_overlap_only_openmx_work_package_first_blocking_reaudit.md`](M9_overlap_only_openmx_work_package_first_blocking_reaudit.md)；
- [`M9_overlap_only_openmx_work_package.md`](M9_overlap_only_openmx_work_package.md)；
- [`m9_overlap_frozen_hashes.json`](../06_reproduction/manifests/m9_overlap_frozen_hashes.json)；
- [`m9_overlap_only_contract.json`](../06_reproduction/configs/m9_overlap_only_contract.json)；
- [`m9_budget.py`](../06_reproduction/scripts/m9_budget.py)、[`m9_openmx_build.py`](../06_reproduction/scripts/m9_openmx_build.py)、[`m9_openmx_input.py`](../06_reproduction/scripts/m9_openmx_input.py)、[`m9_overlap_common.py`](../06_reproduction/scripts/m9_overlap_common.py)、[`m9_overlap_contract.py`](../06_reproduction/scripts/m9_overlap_contract.py)、[`m9_overlap_executor.py`](../06_reproduction/scripts/m9_overlap_executor.py) 与 [`m9_overlap_source_launcher.py`](../06_reproduction/scripts/m9_overlap_source_launcher.py)；
- [`test_m9_overlap_controls.py`](../06_reproduction/tests/test_m9_overlap_controls.py)、[`budget_contract.json`](../06_reproduction/manifests/budget_contract.json) 与 [`openmx_overlap_source_manifest.json`](../06_reproduction/manifests/openmx_overlap_source_manifest.json)。

冻结清单登记的 12 个对象逐项重新读取并计算 SHA-256，结果为 12/12 一致；9 个 Python 对象全部以 UTF-8 解码并通过独立 AST 解析。冻结的 WSL Python 3.9 以 `-B` 复跑正式测试，16/16 通过。测试通过数仅作为回归证据；下述结论还来自对真实控制流和独立负例的检查。

## 遗留项定点复核

### `M9-OLP-B01`：仍为 `OPEN`

已关闭的部分包括：GNU 11 所需 `-fcommon` 与 `-fallow-argument-mismatch` 已冻结；makefile 的 `CC`、`FC` 使用 `/usr/bin/mpicc` 与 `/usr/bin/mpif90`；构建驱动逐项核对冻结工具的规范路径、字节与 SHA-256；最终动态库记录规范路径、字节、SHA-256、dpkg 包和冻结版本；HDF5 只允许一个冻结前缀。调用者把 `/tmp/fake-first` 前置到 PATH 的现有测试也确认不会直接继承该 PATH。

但是，冻结的构建 PATH 仍为 `/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`，不是第一次复核要求的固定最小系统 PATH。`/usr/bin/mpicc` 与 `/usr/bin/mpif90` 是解析到 `/usr/bin/opal_wrapper` 的编译器包装器；makefile 虽以绝对路径启动包装器，包装器再按 PATH 解析底层 `gcc` 或 `gfortran`。因此，预置于 `/usr/local/bin` 的同名工具仍位于冻结 `/usr/bin` 工具之前，而现有测试只排除了调用者的 `/tmp` 路径，没有主动检查 `/usr/local/bin/gcc`、`gfortran` 等固定 PATH 内前置对象。`mpicc --showme:version` 也只核对 Open MPI 包装器版本，不能证明实际被包装器执行的底层编译器身份。

这意味着工具清单可正确登记 `/usr/bin/mpicc -> /usr/bin/opal_wrapper`，同时实际编译仍可能由未登记的 `/usr/local/bin/gcc` 完成。该路径违反 B01 的“实际工具来源唯一”和“固定最小 PATH”条件，必须在任何构建之前关闭。

最小关闭条件：将构建和预算子进程 PATH 收紧到不含 `/usr/local` 前置目录的冻结系统路径，并冻结、核对 MPI 包装器展开后的底层编译器命令与规范身份；或者使 MPI 包装器使用已核对的绝对底层编译器。增加固定 PATH 内 `/usr/local/bin` 前置假 `gcc`/`gfortran` 的拒绝测试，证明版本探测与真实编译均不能到达假工具。动态库来源清单的现有实现应保持不回归。

### `M9-OLP-B02`：`CLOSED`

构建驱动现在分别枚举官方编译清理后的实际受控路径和覆盖 overlap-only 两文件后的实际受控路径，先要求路径集合相等，再要求内容差异严格等于 `source/openmx.c`、`source/truncation.c`。官方与最终编译阶段均调用构建产物检查；新增非基线普通文件只有冻结的构建后缀或三个明确二进制路径可以通过，合成的 `source/new-provenance.txt` 在任何清单写出前被拒绝。

HDF5 build manifest 现已登记 configure argv、绝对 `CC`、`CFLAGS`、configure 日志哈希、`make check` 退出码与日志哈希、完整安装树中每个普通文件或内部链接及其哈希，以及 HDF5 库对象。官方树与 overlap 树各有独立机读清单及哈希。上述实现和负例满足第一次复核的全部最小关闭条件，未发现相邻回归。

### `M9-OLP-B04`：`CLOSED`

公开环境变量不再构成预算授权。预算进程只接受冻结 action API，不接受自由 argv；非 apt 动作由固定 Python、固定 source launcher 和一次性 capability 调用。capability 绑定 transaction ID、预算父 PID 与完整 argv、子 PID、action、structure ID、CPU bucket、forecast、冻结状态快照和固定 launcher argv，并要求私有 owner/mode。source launcher 回查活父进程命令行、原子写入 consumed 记录并删除未消费记录；控制器随后从账本和 transaction 回查该上下文。独立伪造原来的全部公开环境变量时，build、prepare、run 和 project 所用上下文检查均在写入前失败。

launcher receipt 还绑定 transaction、consumed capability 和实际载入的五个冻结控制模块。B07 所述启动阶段 bytecode 风险仍可破坏整个 Python 进程的可信起点，但它是已有 B07 的直接范围，不表示一次性 capability 机制本身仍缺少 B04 规定的 PID/命令/桶/forecast/原子消费条件。因此 B04 独立关闭，B07 继续阻塞运行。

### `M9-OLP-B06`：`CLOSED`

预算合同为 apt、source prepare、source build、smoke prepare、smoke run、project 冻结了非零 forecast 下界；batch prepare/run 必须使用不低于通过结构 500 投影写入 workflow 的每结构 forecast。预算进程在启动子进程前，在预算锁内同时读取并核对 stage、next structure ID、active structure、apt 前置状态和 forecast。`forecast=0`、低于冻结下界、低于投影值、错误 ID、自由 argv 均在动作前拒绝。

开始、运行、成功与失败由 `overlap_transaction.json` 的 `PREPARED`、`RUNNING`、`SUCCESS_COMMITTED`、`FAILED_PENDING_COMMIT`、`FAILED_COMMITTED` 状态串联预算与 workflow。失败提交先写可恢复事务，再把预算和 workflow 同时置为 hard stop，最后提交事务；发现未完成事务且子进程已消失时也进入同一失败提交。正式控制流使用新进程组，超时先终止进程组，必要时升级为强制终止，随后才提交双状态。

除现有单元测试外，本次在临时状态路径独立重放 apt 非零退出、controller 类强制退出、超时终止和死子进程恢复四种路径；4/4 均得到预算 `hard_stopped=true`、workflow `hard_stopped=true` 且 `stage=HARD_STOP`、transaction `FAILED_COMMITTED`。三口径 10 GiB overlap 上限、CPU 桶、\(450\times1.25\) 投影和事前 forecast 检查均保留。因此 B06 的最小关闭条件已满足。

### `M9-OLP-B07`：仍为 `OPEN`

五个项目控制模块现在确实由 `FrozenSourceLoader` 读取已哈希 UTF-8 源码、直接 `compile` 并执行，不查询 `.pyc`；DeepH parser 也由 `DeepHSourceLoader` 从 clean 的冻结提交源码载入，且在导入前拒绝 DeepH 树内的 `.pyc`、`__pycache__` 和符号链接。这关闭了第一次复核所述“指定 pycache prefix 中替换冻结项目模块”的直接路径。

但是，正式入口仍以 `python3.9 -B script.py` 启动，没有 `-I` 或 `-P`。Python 在执行 `m9_budget.py` 或 `m9_overlap_source_launcher.py` 正文前，会把脚本目录加入模块搜索路径；两个入口在建立 source-only finder 和验证自身哈希之前，已经通过普通 import 载入 `argparse`、`hashlib`、`json`、`pathlib` 等模块。冻结清单只登记 12 个指定文件，不拒绝脚本目录中新出现的同名源码或 sourceless bytecode，也没有记录这些启动模块的 loader/origin。

本次使用同一个冻结 Python 3.9 在系统临时目录重放：相邻放置合法的 sourceless `argparse.pyc`，其内容输出 `MALICIOUS`，再以正式同型 `-B launcher.py` 启动。结果为退出码 0 且输出 `MALICIOUS`；改用 `-I -B` 后不再载入该相邻 bytecode。该负例证明 `-B` 只禁写 bytecode，不能为 source-only launcher 建立可信启动边界。由于恶意模块在 launcher 自身哈希、capability 和冻结 source loader 运行前执行，后续 receipt 只能记录五个受控模块，不能检出已发生的启动阶段执行。

最小关闭条件：所有正式 Python 入口，包括 `m9_budget.py` 和 source launcher，必须以隔离/安全路径模式启动，使脚本目录和当前目录不能参与普通 import；同时在冻结清单或入口检查中拒绝控制目录的未登记 `.py`、`.pyc`、`__pycache__` 与同名影子模块。应新增端到端负例，在正式入口相邻位置或等价可搜索路径预置时间戳有效及 sourceless 恶意 pyc，证明它们均不能执行。receipt 应记录启动边界和关键 bootstrap 模块的 loader/origin；现有五个项目模块与 DeepH parser 的 source-only 检查应保持。

## 状态、预算和授权回归

复核结束前再次只读检查，运行时 audit gate、workflow、transaction、OpenMX build root、HDF5 1.12.1 安装前缀和 overlap run root全部不存在。这与“尚未启动受控外部动作”的状态一致，也表明本次合成负例没有生成正式对象。

D-017 仍只授权冻结 450 个 graphene 结构的 same-basis overlap；Hamiltonian、SCF、能量、力、密度矩阵和其他 DFT 标签仍被禁止。B01 与 B07 是工具来源和 Python 启动可信边界问题，不要求改变材料体系、basis、软件对象或预算。因此当前需要的用户路线决策为“无”；主 agent 可在现有授权内修复，但必须再次由独立审计关闭。

## 最终门控

- 第二次定点复核：`FAIL`。
- `M9-OLP-B01`：`OPEN`，`BLOCKING`。
- `M9-OLP-B02`：`CLOSED`。
- `M9-OLP-B04`：`CLOSED`。
- `M9-OLP-B06`：`CLOSED`。
- `M9-OLP-B07`：`OPEN`，`BLOCKING`。
- 新增问题：无。
- `BLOCKING=2`。
- `NON_BLOCKING=0`。
- 是否允许创建运行时 audit gate：否。
- 是否允许 apt 安装、解压、构建、结构 500 输入或 smoke：否。
- 是否允许 M9-05：否。
- 当前需要用户路线决策：无。

## 报告自身验证约定

本报告定稿后执行 UTF-8 控制字符扫描、活动本地 Markdown 链接检查，以及 Pandoc `markdown+tex_math_single_backslash`、HTML5 MathML、`--fail-if-warnings` 严格转换；输出必须包含 MathML。最后计算 SHA-256。为避免自引用改变正文，最终哈希由交付消息报告。
