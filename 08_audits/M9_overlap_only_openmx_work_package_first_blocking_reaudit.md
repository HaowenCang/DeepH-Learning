# M9 overlap-only OpenMX 工作包第一次定点复核

## 复核结论

第一次定点复核结论为 `FAIL`。原六项中 `M9-OLP-B03`、`M9-OLP-B05` 已关闭；`M9-OLP-B01`、`M9-OLP-B02`、`M9-OLP-B04`、`M9-OLP-B06` 未满足全部最小关闭条件或相邻回归。新增稳定阻塞项 `M9-OLP-B07`。当前统计为 `BLOCKING=5`、`NON_BLOCKING=0`。

当前不允许创建运行时 `overlap_work_package_audit_gate.json`，不允许启动 apt 安装、HDF5/OpenMX 解压或构建，不允许生成结构 500 的真实输入，也不允许运行单结构 smoke。`M9-DATA-B01` 继续为 `OPEN`，M9-05 不得启动。现有阻塞均可在 D-017 已授权范围内修复，不需要新的用户路线决策。

送审对象身份重算一致：原独立审计报告 SHA-256 为 `d0e8d9d4a60e93d0106f369fb70022db0acafb906dee267c60bacbed4c4efb90`；修订工作包为 `21e36c815d537fc919de938e0b8bc5f98d8456dae9cde5f64442fc8aa1f58e7f`；冻结清单为 `a372cf80fe837a6073cc385f64065b3be84964ff0e0f00b036151335c98fce08`。

## 复核边界与方法

本次复核只读检查正式来源、冻结数据、项目代码、预算状态和授权记录。没有安装 apt 包，没有解压或编译 HDF5/OpenMX，没有生成真实 OpenMX 输入，没有运行 OpenMX。仅运行不产生正式对象的静态分析、全量数据扫描、现有单元测试和临时目录合成穿透；唯一新增项目文件为本报告。

复核对象包括：

- [`M9_overlap_only_openmx_work_package.md`](M9_overlap_only_openmx_work_package.md)；
- [`M9_overlap_only_openmx_work_package_independent_audit.md`](M9_overlap_only_openmx_work_package_independent_audit.md)；
- [`m9_overlap_frozen_hashes.json`](../06_reproduction/manifests/m9_overlap_frozen_hashes.json)；
- [`m9_overlap_only_contract.json`](../06_reproduction/configs/m9_overlap_only_contract.json)；
- [`m9_openmx_build.py`](../06_reproduction/scripts/m9_openmx_build.py)、[`m9_openmx_input.py`](../06_reproduction/scripts/m9_openmx_input.py)、[`m9_overlap_executor.py`](../06_reproduction/scripts/m9_overlap_executor.py)、[`m9_overlap_contract.py`](../06_reproduction/scripts/m9_overlap_contract.py)、[`m9_overlap_common.py`](../06_reproduction/scripts/m9_overlap_common.py) 与 [`m9_budget.py`](../06_reproduction/scripts/m9_budget.py)；
- [`test_m9_overlap_controls.py`](../06_reproduction/tests/test_m9_overlap_controls.py)、[`budget_contract.json`](../06_reproduction/manifests/budget_contract.json) 与 [`openmx_overlap_source_manifest.json`](../06_reproduction/manifests/openmx_overlap_source_manifest.json)。

## 冻结哈希、来源和全量数据回归

`m9_overlap_frozen_hashes.json` 登记的 11 个执行控制对象均逐项重新读取并计算 SHA-256，结果为 11/11 一致；冻结清单自身哈希也与送审值一致。八个 Python 对象全部通过独立 AST 解析。冻结 WSL Python 下复跑 `test_m9_overlap_controls.py`，10/10 测试通过。

三份归档重新全量遍历而非采信来源清单：

| 归档 | 字节 | SHA-256 | 成员与安全结果 |
|---|---:|---|---|
| `openmx3.9.tar.gz` | 166,014,953 | `27bb56bd4d1582d33ad32108fb239b546bdd1bdffd6f5b739b4423da1ab93ae2` | 1,596 成员，1,574 普通文件、22 目录；不安全路径、规范化重复、链接或特殊对象均为 0 |
| `patch3.9.9.tar.gz` | 1,074,993 | `20cccc4e3412a814a53568f400260e90f79f0bfb7e2bed84447fe071b26edd38` | 93 成员，92 普通文件、1 目录；相同安全计数均为 0；`kpoint.in` 恰好 1 个 |
| `hdf5-1.12.1.tar.gz` | 13,534,796 | `79c66ff67e666665369396e9c90b32e238e501f345afd2234186bfb8331081ca` | 3,602 个普通文件；相同安全计数均为 0 |

overlap-only 仓库仍为 clean 提交 `c8bd8f4e01f9f19868bf2928671c21b12272a6f7`；两个补丁文件 SHA-256 分别为 `96fe547d48147263a017bc116996734504d0f7862245d753a5b80c04a52cfcd5` 和 `6abaa8c7d53a8e7fa10d32b4b59ea5686dabf48694b20ffbec2932e6aa759624`。DeepH-pack 仍为 clean tag `v0.2.2`、提交 `66703c532a6f633f4bbc8f94f75c8698a7f89859`。

冻结数据执行了全量回归：450/450 个结构严格为 `500,510,...,4990`；3600/3600 个文件的大小与 SHA-256 均等于 inventory；总字节 `2360825225`。450 个 `info.json` 全部为 `nsites=72`、`norbits=936`、`isorthogonal=false`、`isspinful=false`。全部 1,296,000 个 `rc` 数组均为有限 `float64 (3,3)`，全部 1,296,000 个 `rh` 数组均为有限 `float64 (13,13)`，每结构键数 2,880 且 `rc/rh` 键集合相同。450 个晶格行列式均为 `5657.804581140005 Å^3`，坐标最大回代残差为 `3.552713678800501e-15 Å`。因此，3600 文件清单、八文件结构合同、PAO/VPS 绑定所依赖的数据来源及原子/晶格/坐标数学映射没有回归。

## 原问题定点复核

### `M9-OLP-B01`：未关闭

`CC` 已加入 `-fcommon`，`FC` 已加入 `-fallow-argument-mismatch`；唯一活动 `CC/FC/LIB`、缺标志和版本漂移的现有合成测试均通过。这关闭了原报告指出的直接 GNU 11 编译标志错误。

但是，构建驱动对工具链身份的验证和实际调用均使用继承 `PATH` 中的裸命令：`gcc`、`gfortran`、`mpicc`、`make`、`git` 和 `ldd`。预算执行器没有像 OpenMX executor 那样把构建子进程 `PATH` 固定为系统路径；因而调用者可通过 PATH 前置包装器同时伪造版本输出和实际构建工具。现有“版本漂移拒绝”单元测试只 mock 返回文本，没有验证可执行文件解析路径。最终 `ldd` 也只做字符串包含检查，没有解析并绑定每个实际库的规范路径、版本和 SHA-256。

最小关闭条件：冻结并核对 `/usr/bin/gcc`、`/usr/bin/gfortran`、`/usr/bin/mpicc`、`/usr/bin/mpif90`、`/usr/bin/make`、`/usr/bin/git`、`/usr/bin/ldd` 等实际解析路径，构建环境使用固定最小 PATH；为 PATH 前置假工具增加拒绝测试；解析最终动态链接对象的规范路径，并把 HDF5、OpenMPI、ScaLAPACK、FFTW、BLAS/LAPACK 实际库的版本和 SHA-256 写入 build manifest。

### `M9-OLP-B02`：未关闭

安全 tar 成员检查、patch3.9.9 的 `kpoint.in → work/kpoint.in` 归位、官方 patch 应用顺序、官方编译后只覆盖 `openmx.c` 与 `truncation.c` 的控制逻辑已经实现，相关合成负例通过。

仍有两项 provenance 缺口。其一，官方树的路径集合在编译前冻结，最终 overlap 树只对这份旧路径列表重算；官方编译阶段若新增未列出的非 `.o/.a/.so/.mod` 文件，最终“两树仅两文件不同”的比较不会发现。其二，工作包要求 HDF5 配置摘要、测试结果、安装树清单和库文件哈希进入运行时清单，但当前 build manifest 只有日志哈希、HDF5 前缀字符串和 `ldd` 文本，没有安装树 inventory 或库哈希。

最小关闭条件：分别从两阶段实际树重新枚举完整受控路径集合，先证明集合相等，再证明内容差异恰为 `source/openmx.c`、`source/truncation.c`；明确构建产物 allowlist，而不是以旧路径列表忽略新增对象。build manifest 还应登记 HDF5 configure 摘要、`make check` 成功证据、完整安装树 inventory 及关键库 SHA-256，并增加“官方编译后新增未登记普通文件”的穿透测试。

### `M9-OLP-B03`：已关闭

输入生成器不再接受任意根或 `--all`，只接收单个冻结结构 ID。processed、run、DFT_DATA、inventory 和数据合同路径均来自哈希绑定的机读合同；每次生成核对该结构八个文件及 PAO/VPS 哈希，映射记录 `rc.npz`、`rh.npz`、`rlat.dat` 等全部八文件，写出后重新解析 72 个原子、三行晶格和 16 位小数坐标。状态机强制先 500、投影通过后再按 ID 升序。全量数据回归及现有负例未发现相邻回归。

### `M9-OLP-B04`：未关闭

预算命令的 argv allowlist 已能拒绝直接 OpenMX、自由参数、特殊模式、多 rank 和直接输入生成器；executor 也固定了 OpenMX argv、`OMP_NUM_THREADS=1`、HDF5 前缀、二进制/源码/输入/映射哈希、DeepH 提交和回执字段。

但是，build、input 与 executor 判断自己是否由预算执行器启动，只检查三个公开环境变量：`M9_OVERLAP_BUDGET_WRAPPED=1`、正确的 `M9_OVERLAP_CPU_BUCKET` 和非负 `M9_OVERLAP_FORECAST_BYTES`。独立重放直接设置这三个变量后，三个控制器的包装器检查全部返回通过。审计门和状态机仍会限制阶段，但一旦审计门与状态合法，控制器可以绕过 `m9_budget.py run` 直接执行，从而不记 CPU、存储 forecast、命令哈希或超时进程组。

最小关闭条件：取消由可继承环境变量单独证明父控制器身份的设计。受控 mutation 应由预算进程直接调用不可从 CLI 进入的控制接口，或使用预算账本中一次性、原子消费并绑定 PID/命令哈希/桶/forecast 的 capability；子控制器须回查并原子消费该记录。增加直接伪造全部相关环境变量的 build、prepare、run 和 project 穿透测试，均应在任何写入前失败。

### `M9-OLP-B05`：已关闭

pre-parser allowlist 与最终 allowlist 已分离；运行目录使用精确文件集合，拒绝符号链接、大小写或后缀变化的额外 HDF5 和已知 Hamiltonian/density/energy/force/stress/SCF 文件名。日志要求三个正常 overlap-only 标记、空 stderr，并拒绝特殊模式与 SCF 标记。raw/parsed HDF5 继续核对 key、shape、dtype、有限性、反向关系 \(S(\mathbf R,i,j)=S(-\mathbf R,j,i)^{\mathsf T}\) 和精确复制；72 个 onsite 块均执行 `1e-10` 对称阈值和正定性检查。现有测试主动加入额外 HDF5、SCF 日志和非对称 onsite 后均正确拒绝，未发现相邻回归。

### `M9-OLP-B06`：未关闭

预算代码已实现三口径 overlap 基线和 10 GiB 上限、非负且不可省略的 forecast、三个 CPU 桶、整进程组 SIGTERM/SIGKILL、500 smoke 后的 `450×1.25` CPU/存储投影、升序状态机和首错停止。现有投影测试分别覆盖 CPU、三口径存储和总预算失败。

但硬预算仍有三个可执行缺口：

- `--forecast-bytes` 只要求非负，合法值 0 可用于 apt、解压、构建及所有 batch 结构；预算执行器没有将它与已冻结操作下界或投影得到的 `per_structure_forecast_bytes` 比较。因此一次操作可在事前以 0 通过，事后才越过 10 GiB 或总限，不满足“下一操作越界前停止”。
- `project_batch()` 将 batch 每结构 forecast 写入 workflow state，但 `m9_budget.py` 不读取该状态，非 500 的 prepare/run 也不要求调用值至少等于此 forecast。
- 超时或 apt 失败只由预算执行器写预算 `HARD_STOP`；被终止的控制器没有机会写 workflow `HARD_STOP`，apt 本身也不调用 workflow 控制器。因此“首错同时原子停止预算和工作流”尚未实现。可伪造包装环境还使整个预算与进程组终止层可被绕过。

最小关闭条件：为四类正式操作冻结可审计的非零 forecast 下界，batch prepare/run 强制等于或高于投影状态值；预算进程在启动前读取并原子验证 workflow stage、next ID 和 forecast。预算与 workflow 的开始/成功/失败状态应由同一持锁事务或可恢复的两阶段事件控制，确保 apt 失败、controller 异常、SIGTERM/SIGKILL 和重启恢复都同时进入不可继续的硬停止。增加 forecast=0、低于投影 forecast、apt 失败、controller 被 SIGKILL 及超时后的双状态断言。

## 新问题

### `M9-OLP-B07`：预置 pycache 可绕过冻结源码

- 级别：`BLOCKING`。
- 证据：正式命令使用 `-B -X pycache_prefix=/home/evan-williams/deeph-m9/manifests/.disabled-pycache`。`-B` 只禁止写入 bytecode，不禁止读取已有、时间戳有效的 `.pyc`；`pycache_prefix` 只是改变读取位置。临时目录重放先为同尺寸恶意源码生成有效 pyc，再恢复相同时间戳和尺寸的良性源码；以正式同型 flags 启动后，实际导入结果为 `MALICIOUS`。当前代码既不要求该前缀不存在/为空，也不扫描或哈希其中内容。
- 影响：`m9_overlap_common`、`m9_openmx_input`、`m9_overlap_contract` 等导入模块可在源文件 11/11 哈希不变时执行预置 bytecode，穿透审计门、路径、输出或状态检查。项目现有 `__pycache__` 在指定 prefix 下通常不会被读取，但这不能防止冻结 prefix 自身被预置。
- 最小关闭条件：正式控制路径完全禁用 bytecode 读取，而非只禁写。可选实现包括在启动前以受控父进程证明 prefix 不存在并使用不可预置的私有临时空目录，同时在导入前后拒绝任何 `.pyc`；或使用只从已哈希源码显式加载且拒绝 bytecode loader 的入口。所有导入模块应记录实际 `__file__`/loader/origin，并增加在指定 prefix 预置时间戳有效恶意 pyc 的端到端拒绝测试。

## 状态、预算与授权回归

审计时三个 overlap CPU 桶仍均为 0 秒，训练和物理验证 GPU 桶均为 0，兼容性 GPU 为 `54.848205606` 秒；当前预算状态无 violation。运行时 audit gate、workflow state、OpenMX build root、HDF5 1.12.1 安装前缀和 overlap run root均不存在，支持“尚未安装、解压、编译、生成输入或计算”的状态记录。

D-017 授权边界没有被修订：只允许冻结 450 个 graphene 结构的 same-basis overlap，不允许 Hamiltonian、SCF、能量、力、密度矩阵或其他 DFT 标签。此次失败来自控制实现仍可穿透，不是要求改变材料、basis、软件对象或预算。因此主 agent 可在现有授权内修复；在复核 PASS 前不得创建一个声称 PASS 的运行时 gate。

## 最终门控

- 定点复核：`FAIL`。
- 已关闭：`M9-OLP-B03`、`M9-OLP-B05`。
- 未关闭：`M9-OLP-B01`、`M9-OLP-B02`、`M9-OLP-B04`、`M9-OLP-B06`。
- 新增：`M9-OLP-B07`。
- `BLOCKING=5`。
- `NON_BLOCKING=0`。
- 是否允许创建运行时 audit gate：否。
- 是否允许 apt 安装、解压或构建：否。
- 是否允许结构 500 输入或 smoke：否。
- 是否允许 M9-05：否。
- 当前需要用户决策：无。
- 下一动作：主 agent 修复 B01、B02、B04、B06、B07，并由本审计员再次定点复核；不得由主 agent 自行宣告关闭。

## 报告自身验证约定

本报告定稿后执行 UTF-8 控制字符扫描、活动本地 Markdown 链接检查，以及 Pandoc `markdown+tex_math_single_backslash`、HTML5 MathML、`--fail-if-warnings` 严格转换；输出必须包含 MathML。最后计算 SHA-256。为避免自引用改变正文，最终哈希由交付消息报告。
