# M9 受限 overlap-only OpenMX 工作包独立审计

## 审计结论

结论为 `FAIL`。稳定问题为 `BLOCKING=6`、`NON_BLOCKING=0`。送审包正确冻结了软件来源、补丁顺序、PAO/VPS/basis、450 个结构的数学映射以及正常执行路径的 overlap HDF5 合同，但现有实现尚不能自动阻止编译失败、来源或 basis 穿透、特殊 OpenMX 模式、额外 DFT 输出以及 overlap 子预算绕过。按照 D-017 的前置门控，当前不允许安装系统包，不允许解压或构建 HDF5/OpenMX，不允许生成结构 500 输入，也不允许执行单结构 smoke。`M9-DATA-B01` 继续为 `OPEN`，M9-05 不允许启动。

本结论审计的送审主文件 SHA-256 为 `342ee2ff71f36b5b61a6b063510e83f0520e24dc15b4800a8012cdd0687daab4`，与委托值一致。六项阻塞均可在 D-017 已授权路线内由主 agent 修复；当前不需要新的用户路线决策。只有修复需要改变 OpenMX/HDF5/PAO/VPS/basis、450 结构映射、允许输出、材料、DeepH 版本、物理范围或预算时，才需要重新提交用户决策。

## 边界与方法

本审计对项目文件、WSL 来源对象、归档和源码均只读。没有安装软件包，没有解压归档，没有编译 HDF5 或 OpenMX，没有生成 OpenMX 输入，也没有运行 OpenMX。唯一新增项目文件是本报告。

核查没有采信主 agent 清单中的聚合结论，而是分别重算归档字节与 SHA-256、遍历全部 tar 成员、读取所需成员内容、检查固定 Git 提交和工作树、逐结构读取冻结数据、静态追踪 overlap-only 补丁和 DeepH-pack v0.2.2 解析器，并逐行审查输入生成器、输出验证器和预算执行器。四个 Python 脚本均独立通过 AST 解析，三份核心 JSON 均可解析；这只证明语法成立，不替代行为合同审计。

主要送审对象为：

- [`M9_overlap_only_openmx_work_package.md`](M9_overlap_only_openmx_work_package.md)；
- [`m9_overlap_only_contract.json`](../06_reproduction/configs/m9_overlap_only_contract.json)；
- [`m9_openmx_source_inspect.py`](../06_reproduction/scripts/m9_openmx_source_inspect.py)；
- [`m9_openmx_input.py`](../06_reproduction/scripts/m9_openmx_input.py)；
- [`m9_overlap_contract.py`](../06_reproduction/scripts/m9_overlap_contract.py)；
- [`m9_budget.py`](../06_reproduction/scripts/m9_budget.py) 与 [`budget_contract.json`](../06_reproduction/manifests/budget_contract.json)；
- 项目侧 [`openmx_overlap_source_manifest.json`](../06_reproduction/manifests/openmx_overlap_source_manifest.json) 和 WSL 运行时同名来源清单；
- [`decisions.md`](../decisions.md)、[`master_execution_plan.md`](../00_scope/master_execution_plan.md) 与 [`progress_tracker.md`](progress_tracker.md)。

## 软件身份、归档与补丁顺序

[OpenMX 官方下载页](https://www.openmx-square.org/download.html)将 3.9 基础包和 2021-10-17 修补包列为同一 3.9 发布链；[patch3.9.9 README](https://www.openmx-square.org/bugfixed/21Oct17/README.txt)与本地修补归档相符。[overlap-only-OpenMX 固定提交](https://github.com/mzjb/overlap-only-OpenMX/tree/c8bd8f4e01f9f19868bf2928671c21b12272a6f7)的 README 明确要求先取得 OpenMX 3.9.9 和 HDF5 1.12.1，再覆盖 `openmx.c` 与 `truncation.c`。因此，送审正文冻结的“3.9 基础包 → 官方 patch3.9.9 → 以冻结 makefile 做官方 3.9.9 编译链接 smoke → 固定提交的两个文件覆盖 → clean rebuild”核心先后关系正确，且不能把 overlap-only 文件提前应用；但机读顺序没有忠实表达该正文，见 `M9-OLP-B02`。

三份归档的独立结果如下：

| 对象 | 字节 | SHA-256 | 只读成员核查 |
|---|---:|---|---|
| `openmx3.9.tar.gz` | 166,014,953 | `27bb56bd4d1582d33ad32108fb239b546bdd1bdffd6f5b739b4423da1ab93ae2` | 1,596 个成员，其中 1,574 个普通文件、22 个目录；普通文件解压总字节 496,170,279；绝对路径、父目录分量、反斜杠、规范化重复、链接和特殊对象均为 0 |
| `patch3.9.9.tar.gz` | 1,074,993 | `20cccc4e3412a814a53568f400260e90f79f0bfb7e2bed84447fe071b26edd38` | 93 个成员，其中 92 个普通文件、1 个目录；普通文件解压总字节 7,210,068；相同安全计数均为 0 |
| `hdf5-1.12.1.tar.gz` | 13,534,796 | `79c66ff67e666665369396e9c90b32e238e501f345afd2234186bfb8331081ca` | 3,602 个普通文件；普通文件解压总字节 122,744,392；相同安全计数均为 0 |

HDF5 哈希也与 [HDF Group 1.12.1 官方 SHA-256 页面](https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.12/hdf5-1.12.1/src/hdf5-1.12.1.sha256.html)一致。overlap-only 仓库 HEAD 精确为 `c8bd8f4e01f9f19868bf2928671c21b12272a6f7`，工作树 clean，送审所列 `openmx.c` 与 `truncation.c` 哈希均成立。

项目侧来源清单 SHA-256 为 `6f9f659d0eaca7bdac989df0a661379a8e429aa58960c5fa98faa966ba9f575f`；它绑定的 WSL 运行时来源清单 SHA-256 为 `bdce33ea88a5214e631dd917fe6717967dd38e8bd2804ad53f3fbdc85f17397c`，重算一致。送审表中的合同、四个脚本、预算合同和项目侧来源清单八个哈希也均与当前文件一致。

这些结果证明来源身份可唯一确定，但当前 `m9_openmx_source_inspect.py` 只读取来源，未实现后续安全解压、补丁组合和构建树证明；该缺口见 `M9-OLP-B02`。

## Ubuntu/HDF5/OpenMPI 编译链

Ubuntu 22.04 apt 候选独立查询与工作包完全一致：OpenMPI `4.1.2-2ubuntu1`、ScaLAPACK `2.1.0-4`、FFTW `3.3.8-2ubuntu8`、BLAS/LAPACK `3.10.0-2ubuntu1`、`gfortran` 元包 `4:11.2.0-1ubuntu1`、Make `4.3-4.1build1`。当前实际 GCC/GFortran 为 11.4.0、Make 为 4.3；OpenMPI、ScaLAPACK 和 FFTW 的四个待装包仍未安装。HDF5 1.12.1 的独立前缀、禁用 Fortran/C++/static 和最终 `ldd` 绑定方案原则上可行，且可以避免系统 HDF5 1.10.7。

但是，冻结 OpenMX `CC` 缺少 `-fcommon`，`FC` 缺少 `-fallow-argument-mismatch`。patch3.9.9 的 `openmx_common.h` 在头文件中定义大量全局对象；GCC 10 以后默认 `-fno-common`，OpenMX 官方论坛已有 [GCC 11.2.1 多重定义的同版本复现](https://www.openmx-square.org/forum/patio.cgi?mode=view&no=2904)。同一源码附带的 ELPA Fortran 又含现代 GFortran 会拒绝的实参与形参类型不匹配；OpenMX 论坛给出的直接修复是 [`-fallow-argument-mismatch`](https://www.openmx-square.org/forum/patio.cgi?mode=view&no=3024)。因此当前冻结行在 GCC/GFortran 11.4.0 上不是可重建合同，而是具有已知确定性失败路径。

## PAO、VPS、basis 与 450 结构映射

从 OpenMX 3.9 基础归档中直接读取而非依赖清单，确认：

- `DFT_DATA19/PAO/C6.0.pao` 为 693,570 bytes，SHA-256 `1442a834dbc2b9b55e8f11a20734c7b77765fa4e05ca3e1b1f004da46bfaaef4`，内容登记 PAO 径向截断 6.0 Bohr；
- `DFT_DATA19/VPS/C_PBE19.vps` 为 333,898 bytes，SHA-256 `4b9c78eb72be25ca46366b8fd39c74ae7172d7db9e77b29782a42f71901b38a7`；
- `C6.0-s2p2d1` 对应两套 s、两套 p、一套 d，共 13 个实轨道函数，与冻结数据 450×72 行 `[0,0,1,1,2]` 一致。

450/450 个结构均独立读取。ID 严格为 `500,510,...,4990`；每个结构 72 个元素均为 C，轨道数组均为 `72×5` 且逐元素等于 `[0,0,1,1,2]`。以 (L=\mathrm{lat.dat}^{\mathsf T})、(X=\mathrm{site\_positions.dat}^{\mathsf T})、(F=X L^{-1}) 全量复算，450 个晶格行列式均为 `5657.804581140005 Å^3`，最大回代残差为 `3.552713678800501e-15 Å`；fractional 分量总范围为 `0.047340970907005` 至 `0.9517196302272068`。因此原子编号不重排、晶格转置和坐标公式本身唯一且正确。

问题不在数学映射，而在生成器没有把它绑定到冻结路径和冻结 PAO/VPS。`m9_openmx_input.py` 接受任意 `--processed-root`、`--output-root` 与 `--openmx-data-path`，不核对这些路径是否等于机读合同，也不在生成前读取并核对实际 PAO/VPS 哈希；它还提供可在结构 500 smoke 前一次生成全部输入的 `--all`，并从 `structure_mapping.json` 漏记 `rc.npz` 与 `rlat.dat`。这使正确公式仍可被用于错误来源或错误 basis，见 `M9-OLP-B03`。

## overlap-only 补丁、HDF5 与 DeepH 解析合同

固定补丁的普通输入路径在 `init()` 后执行 `truncation(1,0)`、`Set_OLP_Kin(OLP,H0)`，随后只有 `output_O_nm(OLP[0], "output/overlaps", 0, 1.0)` 被调用。`H0` 作为共享例程形成的临时 kinetic 数组没有在该正常路径中序列化。`output_O_nm` 的 dataset 名为五整数 JSON 列表，atom 下标为 1-based，矩阵维度由两端原子的轨道数决定，数据以 `H5T_NATIVE_DOUBLE` 写出；对本工作包冻结的单元素 basis 即 `float64 (13,13)`。

DeepH-pack v0.2.2 的 [`openmx_parse_overlap` 使用方式](https://github.com/mzjb/DeepH-pack/tree/v0.2.2)与工作包相符：读取 `output/overlaps_0.h5` 及 `openmx.out`，复制生成 `overlaps.h5`，并恢复结构文件。`m9_overlap_contract.py` 对顶层 dataset、五整数键、shape、dtype、有限值、与 `rh.npz` 键集合精确相等、反向键转置关系、raw/parsed 值精确复制，以及晶格/坐标/元素/轨道回读的主要检查是正确的。冻结关系为

\[
S(\mathbf R,i,j)=S(-\mathbf R,j,i)^{\mathsf T}.
\]

但是，“补丁只会走 overlap 路径”只在唯一正常 argv 和冻结 `Nomd` 输入成立。编译出的 `openmx.c` 仍保留 `-maketest/-runtest` 系列、`-forcetest/-forcetest2`、`-stresstest/-stresstest2` 与 `neb_check(argv)` 分派；其中 `-forcetest2` 和 `-stresstest2` 明确调用 `Check_Force`/`Check_Stress` 后再调用 `OutData`。因此二进制本身仍存在进入力、应力、SCF 或一般 OpenMX 输出的活动路径。当前没有受控启动器拒绝额外 argv、替代输入或直接执行错误二进制，见 `M9-OLP-B04`。

现有输出验证器也不能完整兜底。它只扫描小写 `*.h5`，且放行 `parsed_dir` 直属的任意 HDF5 文件；因此额外的 `hamiltonians.h5`、density HDF5 或其他后缀 DFT 输出可以不触发失败。它计算 atom-1 onsite 对称残差但从未与容差比较，随后 `eigvalsh` 只使用一个三角部分，不能证明送审文件声称的“对称且正定”。它也不核对执行 argv、二进制/组合源码/input/mapping 哈希或正常 overlap-only 退出标记，见 `M9-OLP-B05`。

## CPU、存储与执行顺序

审计时预算只读快照无既有违规：overlap build/smoke/batch 三个 CPU 桶均为 0 秒，训练与物理验证 GPU 桶均为 0 秒，兼容性 GPU 桶为 `54.848205606` 秒；合计表观字节 `29,869,225,117`、合计分配字节 `30,169,546,752`、VHDX 相对基线增长 `24,763,170,816`，原 100 GiB 总限均未触发。OpenMX 构建根、HDF5 1.12.1 前缀和 overlap run 根均不存在；没有 OpenMX 输入、二进制或 overlap 结果。因此，项目关于“尚未安装、编译、生成输入或计算”的状态链准确。

`m9_budget.py` 已增加 7,200/1,800/21,600 秒三个 CPU 桶并能在指定桶时设置超时，但 D-017 的 10 GiB overlap 新增存储子限没有进入状态、基线、`violations()` 或 forecast 计算。`--cpu-bucket` 默认是 `none`，`--forecast-bytes` 默认是 0 且没有拒绝负值；任何 overlap 命令都可省略 CPU 计账或存储预测。脚本也没有实现“结构 500 实测 → 450 保守投影 → 同时对 21,600 秒、10 GiB 和总余量硬停止”的计算，更没有把升序、逐结构验证和首错停止绑定到预算账本。因此当前工作包的“硬停止”陈述强于实际实现，见 `M9-OLP-B06`。

## 授权、状态与 M9 边界

D-017 明确只授权为冻结的 450 个 graphene 结构生成 same-basis overlap，不授权一般 DFT 或新标签；工作包、主计划和进度台账均将当前状态记为 `REVIEW/IN_PROGRESS`，并明确独立审计通过前不安装、不解压/编译、不生成输入、不运行。WSL 当前对象与这些陈述一致。

`M9-DATA-B01` 仍不能因为来源已冻结而关闭。只有 450/450 个合法 overlap 通过后续数据契约定点复核，才能提供非正交广义本征问题需要的 (S(\mathbf k))。本审计不降低 D-013 的矩阵、对称性或物理验收，也不把单个 onsite 块替代完整 (S(\mathbf k)) 条件检查。

## 稳定问题与最小关闭条件

### `M9-OLP-B01`：冻结 GNU 编译行与 GCC/GFortran 11.4 不兼容

- 级别：`BLOCKING`。
- 证据：`CC` 缺少 `-fcommon`，`FC` 缺少 `-fallow-argument-mismatch`；两类失败均有 OpenMX 3.9.9/GNU 10+ 的直接源码机制和官方论坛复现。
- 影响：官方 3.9.9 编译链接 smoke 和 overlap clean build 在冻结环境中具有确定性失败路径。
- 最小关闭条件：在工作包、机读合同和受控 makefile 生成逻辑中冻结两个兼容标志；只允许替换唯一活动 `CC/FC/LIB` 行；增加静态断言和负例，证明缺任一标志、额外活动定义或版本漂移会在构建前拒绝。实际编译仍须等重审放行后执行。

### `M9-OLP-B02`：没有可执行的安全组合与构建 provenance 实现

- 级别：`BLOCKING`。
- 证据：来源检查器只读归档和 Git 对象；没有脚本执行安全解压、按顺序应用全部 patch3.9.9 成员、在官方 smoke 后仅覆盖两个文件、生成精确组合树清单或拒绝顺序错误。机读合同还把“官方 3.9.9 编译 smoke”排在“应用冻结 makefile”之前，运行时来源清单则直接从官方 patch 跳到两个 overlap 文件覆盖，均不能执行正文所述顺序；官方 README 要求把补丁中的 `kpoint.in` 移至 `work`，机读对象也未记录该归位。
- 影响：失败矩阵所称“补丁顺序错误、额外覆盖、makefile 漂移自动拒绝”当前没有执行载体；手工命令可形成未受证明的混合源码。
- 最小关闭条件：提供单一受控 source/build 驱动，绑定三份来源哈希、目标根、成员安全规则、两阶段源码清单、两个 overlap 覆盖文件和唯一 makefile 定义；在编译前输出组合 manifest，并以自动负例证明路径、链接/特殊成员、漏补丁、乱序、额外覆盖和最终哈希漂移均被拒绝。审计阶段只能评审代码与合成负例，不能提前解压或编译正式对象。

### `M9-OLP-B03`：输入生成器可绕过冻结数据、basis 和 smoke 顺序

- 级别：`BLOCKING`。
- 证据：三个关键根路径由调用者任意提供；实际 C6.0 PAO/C_PBE19 VPS 哈希不核对；映射漏记两个冻结结构文件；`--all` 可在结构 500 smoke 前生成全部输入。
- 影响：可以静默使用不同 processed 数据或 DFT_DATA/basis，同时仍生成形式正确的 `openmx.dat` 和部分来源清单。
- 最小关闭条件：把合同自身哈希、processed 根、run 根和 DFT_DATA19 根绑定到冻结绝对路径；生成前逐次核对 PAO/VPS 和八个结构文件哈希；回读 16 位小数后的输入并复算原子顺序、晶格和坐标残差；以阶段状态禁止 smoke 前 `--all`，并为替代根、替代 PAO/VPS、原子重排、晶格错误、输入篡改和越序生成提供自动拒绝证据。

### `M9-OLP-B04`：没有受控启动器封闭 OpenMX 特殊模式与执行 provenance

- 级别：`BLOCKING`。
- 证据：冻结补丁保留 test、force、stress 和 NEB 活动分派；现有对象没有把唯一 argv、`-np 1`、`OMP_NUM_THREADS=1`、HDF5 前缀、最终二进制哈希、组合源码 manifest、输入/mapping 哈希和预算桶绑定为一个不可增参的启动动作。
- 影响：可直接运行错误二进制、添加 `-forcetest2/-stresstest2`、使用替代输入或绕过逐结构顺序，从而进入 Hamiltonian/SCF/力/应力或其他标签路径。
- 最小关闭条件：提供唯一受控 executor，只接受固定结构 ID，不接受自由 argv；运行前核对上述全部哈希和环境，明确拒绝所有额外参数、测试/force/stress/NEB 模式、多 rank、非冻结输入和直接批量跳跃；每个结构必须先取得验证 PASS 才能更新下一允许 ID。相应穿透负例必须自动失败。

### `M9-OLP-B05`：禁止输出与 onsite 对称性验证存在可穿透缺口

- 级别：`BLOCKING`。
- 证据：验证器只检查小写 `*.h5`，放行 `parsed_dir` 下任意 HDF5，不检查其他 DFT 文件或 OpenMX 特殊模式日志；onsite 对称残差只记录不判阈值。
- 影响：额外 Hamiltonian、density、SCF/能量/力文件可与合法 overlap 共存而被报告为 `PASS`；非对称 onsite 块也可能由 `eigvalsh` 的单三角语义掩盖。
- 最小关闭条件：建立正常运行和 parsed 输出的严格文件 allowlist，仅允许指定 raw/parsed overlap、冻结结构回读、映射、日志和验证报告；拒绝大小写/后缀变化的额外 HDF5及已知 DFT 输出，核对日志中的正常 overlap-only 路径和无特殊模式/SCF/OutData 证据；对 onsite 对称残差执行冻结容差断言；增加 Hamiltonian、density、能量、力、额外 rank、额外 parsed HDF5、特殊模式日志和非对称 onsite 负例。

### `M9-OLP-B06`：overlap CPU/10 GiB 子预算和投影并非硬约束

- 级别：`BLOCKING`。
- 证据：没有 overlap 存储基线或 10 GiB violation；CPU 桶和 forecast 可省略，forecast 还可为负；没有 450 投影和逐结构状态机。
- 影响：构建或批处理可不计入 CPU 子桶，可在总 100 GiB 未越界时超过 D-017 的 10 GiB 子限，也可不经 smoke 投影直接批量执行。
- 最小关闭条件：冻结 overlap 增量存储基线并在表观、分配及适用 VHDX 口径执行 10 GiB 上限；对 overlap executor 强制非 `none` 的正确 CPU 桶和非负、非省略 forecast；实现结构 500 实测到 450 的保守 CPU/存储投影及总余量比较；把 smoke、投影、升序运行、逐项 PASS 和首错 `HARD_STOP` 写入可原子恢复的状态机，并以越界、漏桶、负 forecast、越序和失败后继续的自动负例证明。

## 门控判定与后续动作

- 工作包审计：`FAIL`。
- `BLOCKING=6`。
- `NON_BLOCKING=0`。
- 是否允许安装 apt 包：否。
- 是否允许解压/构建 HDF5 或 OpenMX：否。
- 是否允许生成结构 500 输入：否。
- 是否允许单结构 smoke：否。
- `M9-DATA-B01`：`OPEN`。
- 是否允许 M9-05：否。
- 当前需要的用户路线决策：无。主 agent 应在 D-017 边界内修复 B01—B06，保持被审来源与正式运行时不动，再由同一独立审计员定点复核。若修复要改变 D-017 冻结对象或预算，才暂停并请求用户决策。

## 报告自身验证约定

本报告最终内容固定后执行 UTF-8 非 CR/LF/TAB 控制字符扫描、活动本地 Markdown 链接存在性检查，以及 Pandoc 使用 `markdown+tex_math_single_backslash`、HTML5 MathML 与 `--fail-if-warnings` 的严格转换；输出必须实际含 MathML 节点。最后计算本报告 SHA-256。为避免自引用改变文件内容，最终计数和 SHA-256 不写入正文，由交付消息提供。
