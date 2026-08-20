# M9 overlap-only OpenMX 工作包第五次定点复核

## 复核结论

第五次定点复核结论为 `PASS`。第四次报告唯一仍开放的 `M9-OLP-B07` 已满足全部最小关闭条件，现为 `CLOSED`；`M9-OLP-B01`、`M9-OLP-B02`、`M9-OLP-B04`、`M9-OLP-B06` 未发现相邻回归。没有新增问题。当前统计为 `BLOCKING=0`、`NON_BLOCKING=0`。

允许主 agent 依据本报告建立运行时 `overlap_work_package_audit_gate.json`，随后进入 D-017 已授权的受控外部动作：冻结 apt 安装、来源准备、HDF5/OpenMX 构建、结构 500 输入准备与单结构 smoke。每一步仍必须通过预算 action API、forecast、事务、来源哈希和失败硬停止；本次 PASS 不授权自由命令、批量 450 结构运行或 M9-05。批量运行仍须等待结构 500 smoke 与投影门，M9-05 仍须等待 450/450 overlap 合同通过并由独立审计关闭 `M9-DATA-B01`。

送审对象身份独立重算一致：第四次定点复核报告 SHA-256 为 `1499bb8993e341cedcaa5e7d243853b575d2cdea550a80d4d48d11bf6b58444c`；工作包为 `ed3b5db4aada793264d4b2e46f5d87dd35a397ff3d763cfba665fed6b87f9236`；冻结清单为 `365547aa3107de393eefa6767c4f44e90e54b2490b174546c9f825c211db57af`。

## 边界与独立方法

本次复核只读检查冻结项目对象、现有 WSL 环境和状态，并执行无正式产物的入口负例与单元测试。没有安装 apt 包，没有解压或编译 HDF5/OpenMX，没有生成真实输入，没有运行 OpenMX，也没有创建 audit gate、workflow 或 transaction。唯一新增项目文件为本报告。

独立复核对象包括：

- [`M9_overlap_only_openmx_work_package_fourth_blocking_reaudit.md`](M9_overlap_only_openmx_work_package_fourth_blocking_reaudit.md)；
- [`M9_overlap_only_openmx_work_package.md`](M9_overlap_only_openmx_work_package.md)；
- [`m9_overlap_frozen_hashes.json`](../06_reproduction/manifests/m9_overlap_frozen_hashes.json)；
- [`m9_overlap_only_contract.json`](../06_reproduction/configs/m9_overlap_only_contract.json)；
- [`m9_budget.py`](../06_reproduction/scripts/m9_budget.py)、[`m9_openmx_build.py`](../06_reproduction/scripts/m9_openmx_build.py)、[`m9_openmx_input.py`](../06_reproduction/scripts/m9_openmx_input.py)、[`m9_overlap_common.py`](../06_reproduction/scripts/m9_overlap_common.py)、[`m9_overlap_contract.py`](../06_reproduction/scripts/m9_overlap_contract.py)、[`m9_overlap_executor.py`](../06_reproduction/scripts/m9_overlap_executor.py) 与 [`m9_overlap_source_launcher.py`](../06_reproduction/scripts/m9_overlap_source_launcher.py)；
- [`test_m9_overlap_controls.py`](../06_reproduction/tests/test_m9_overlap_controls.py)、[`budget_contract.json`](../06_reproduction/manifests/budget_contract.json) 与 [`openmx_overlap_source_manifest.json`](../06_reproduction/manifests/openmx_overlap_source_manifest.json)。

冻结清单登记的 16 个对象逐项重新读取并计算 SHA-256，结果为 16/16 一致；13 个 Python 对象全部以 UTF-8 解码并通过独立 AST 解析。冻结的 WSL Python 3.9 以 `-I -S -B` 直接运行正式测试文件，19/19 通过。测试通过数仅作为回归证据；B07 的关闭还基于下述真实入口重放和状态不变性核对。

## `M9-OLP-B07`：`CLOSED`

### 冻结解释器身份前置

`m9_budget.isolated_bootstrap_provenance()` 的第一项可执行检查现在解析 `sys.executable`，并要求其规范路径严格等于冻结的 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9`。只有解释器身份通过后，才继续检查 `isolated`、`no_site`、`dont_write_bytecode`、bootstrap `sys.path` 和四个 stdlib 模块来源。

`command_overlap_init()` 与 `command_overlap_run()` 都把该公共函数作为函数体首个操作。初始化路径在打开预算锁、读取 state、读取 audit gate、创建 manifest 对象或写入任何 transaction/workflow 之前验证解释器；运行路径也在校验 gate、创建 manifest 目录、读取状态或进入锁之前验证。原来只存在于 run 路径的重复解释器检查已删除，因此两条正式路径不会形成不同的身份规则。

### 错误解释器真实入口负例

本次独立执行真实命令：

```text
/usr/bin/python3.10 -I -S -B /mnt/e/Projects/Codex/DeepH/06_reproduction/scripts/m9_budget.py overlap-init
```

命令退出码为 1，stdout 为空，stderr 明确报告 `formal overlap entry requires frozen Python`，并列出系统 Python 3.10 与冻结 Python 3.9 的规范路径差异。重放前后逐项核对了 workflow、transaction、capability 目录、budget lock、budget ledger 与 budget state：前三者始终不存在；后三者的存在性、字节数和 SHA-256 全部不变。因此拒绝发生在正式初始化状态或审计事件写入之前。

正式测试中的同类端到端负例也核对 workflow/transaction 的前后存在状态相等。结合静态控制流顺序，第四次报告指出的错误解释器初始化穿透已经关闭。

### 既有启动边界保持

正式入口与 launcher 仍统一使用 `-I -S -B`，并核对 `no_site`；bootstrap `sys.path` 不含脚本目录、当前目录或 site-packages。dependency site-packages 仍只在 capability、项目 source-only loader 和合同哈希建立后通过普通 `sys.path.append` 加入，不调用 `site.addsitedir`，回执继续绑定 `pth_processed=false`。恶意 `.pth`、相邻 sourceless pyc、控制目录 cache/未登记源码、项目模块 bytecode 与 DeepH parser bytecode 的负例保持。

控制目录独立枚举结果为 12 个普通 `.py` 文件，与冻结清单登记集合精确相等；不存在子目录、符号链接、`.pyc` 或 `.pyo`。因此 B07 从解释器入口、site 初始化、控制目录、项目模块到 DeepH parser 的全部既定关闭条件均已满足。

## 已关闭项相邻回归

### `M9-OLP-B01`：保持 `CLOSED`

固定 PATH 仍为 `/usr/sbin:/usr/bin:/sbin:/bin`；MPI wrapper 的底层 `gcc`、`gfortran` 展开、规范路径、字节与 SHA-256 绑定仍存在。解释器身份修复没有改变工具链或动态库 provenance。

### `M9-OLP-B02`：保持 `CLOSED`

官方与 overlap 两阶段实际树比较、构建产物 allowlist、HDF5 configure/check、安装树 inventory 和库哈希均保留；对应测试通过。未发现 B07 修订影响构建来源合同。

### `M9-OLP-B04`：保持 `CLOSED`

公开环境变量与自由 argv 仍不能建立预算上下文；一次性 capability 继续绑定父子 PID、transaction、动作、结构、桶、forecast 和精确 `-I -S -B` launcher argv，并由 launcher 原子消费。冻结解释器公共前置检查进一步收紧了 capability 之前的入口，没有放宽 B04。

### `M9-OLP-B06`：保持 `CLOSED`

非零 forecast 下界、batch 投影下界、三口径 10 GiB 上限、CPU 桶、进程组终止和可恢复双状态事务均保留；forecast、投影与双硬停止回归通过。未发现公共 bootstrap 检查改变预算事务语义。

## 状态、预算和授权边界

复核结束前再次只读检查，运行时 audit gate、workflow、transaction、OpenMX build root、HDF5 1.12.1 安装前缀和 overlap run root全部不存在。这与“尚未启动受控外部动作”的状态一致，也表明本次负例没有生成正式对象。

本报告的 `PASS` 只关闭 overlap-only OpenMX 工作包自身的运行前审计门。D-017 仍只授权冻结 450 个 graphene 结构的 same-basis overlap；Hamiltonian、SCF、能量、力、密度矩阵和其他 DFT 标签仍被禁止。创建 audit gate 后，主 agent 可以按既定依赖顺序执行 apt、source prepare、source build、结构 500 prepare 和 smoke；任何失败必须同时硬停止预算与 workflow。

当前不需要新的用户路线决策，也不需要新的外部执行授权：上述受控动作已由 D-017 授权。但本报告不直接关闭 `M9-DATA-B01`，不允许跳过结构 500 与投影门进入 batch，也不允许启动 M9-05。

## 最终门控

- 第五次定点复核：`PASS`。
- `M9-OLP-B01`：保持 `CLOSED`。
- `M9-OLP-B02`：保持 `CLOSED`。
- `M9-OLP-B04`：保持 `CLOSED`。
- `M9-OLP-B06`：保持 `CLOSED`。
- `M9-OLP-B07`：`CLOSED`。
- 新增问题：无。
- `BLOCKING=0`。
- `NON_BLOCKING=0`。
- 是否允许创建运行时 audit gate：是。
- 是否允许进入 D-017 的受控 apt、来源准备、构建、结构 500 输入与 smoke：是，必须逐动作遵守预算和事务门。
- 是否立即允许 batch 450 结构：否；必须先通过结构 500 smoke 与投影门。
- 是否允许 M9-05：否；必须等待 450/450 overlap 与 `M9-DATA-B01` 独立复核关闭。
- 当前需要用户路线决策：无。

## 报告自身验证约定

本报告定稿后执行 UTF-8 控制字符扫描、活动本地 Markdown 链接检查，以及 Pandoc `markdown+tex_math_single_backslash`、HTML5 MathML、`--fail-if-warnings` 严格转换；输出必须包含 MathML。最后计算 SHA-256。为避免自引用改变正文，最终哈希由交付消息报告。用于验证 MathML 的审计恒等式为 \(19=19\)。
