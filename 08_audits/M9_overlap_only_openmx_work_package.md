# M9 受限 overlap-only OpenMX 工作包

## 1. 状态、授权与门控

- 日期：2026-08-13
- 状态：`BLOCKING_REAUDIT_PENDING`
- 依据：D-013、D-014、D-016 与用户对“受限 overlap-only OpenMX 路线”的明确授权；新授权登记为 D-017。
- 目标：只为冻结的 450 个 graphene 结构生成与 Hamiltonian 相同 OpenMX basis 下的实空间 overlap 块，以关闭 `M9-DATA-B01`；不得生成、保存或使用 Hamiltonian、SCF、能量、力、密度矩阵或其他 DFT 标签。
- 当前门控：只允许冻结来源、编写合同和准备可审计代码。独立工作包审计达到 `PASS` 且剩余问题为 0 之前，禁止安装系统包、解压或编译 OpenMX/HDF5、生成 OpenMX 输入、运行任何结构计算。

本包不改变冻结的材料、DeepH 版本、非磁/无 SOC 范围、24 GPU 小时或 100 GiB 总存储。D-018 已将 M9 总墙钟策略改为无时限，但原 7 天起点、截止时间与历史超期证据继续保留；CPU、GPU、存储和 overlap 子预算均不重置、不增加。overlap 路线不使用 GPU；其 CPU 墙钟和存储配额仍是独立硬上限。

## 2. 软件与来源对象

| 对象 | 冻结身份 | 本地证据 |
|---|---|---|
| OpenMX 基础包 | [官方 OpenMX 3.9](https://www.openmx-square.org/download.html)，`openmx3.9.tar.gz`，166,014,953 bytes，SHA-256 `27bb56bd4d1582d33ad32108fb239b546bdd1bdffd6f5b739b4423da1ab93ae2` | `/home/evan-williams/deeph-m9/downloads/overlap_sources/openmx3.9.tar.gz` |
| 官方修补包 | [OpenMX patch3.9.9](https://www.openmx-square.org/bugfixed/21Oct17/README.txt)，`patch3.9.9.tar.gz`，1,074,993 bytes，SHA-256 `20cccc4e3412a814a53568f400260e90f79f0bfb7e2bed84447fe071b26edd38` | `/home/evan-williams/deeph-m9/downloads/overlap_sources/patch3.9.9.tar.gz` |
| overlap-only 修改 | [mzjb/overlap-only-OpenMX](https://github.com/mzjb/overlap-only-OpenMX) 提交 `c8bd8f4e01f9f19868bf2928671c21b12272a6f7`，clean | `/home/evan-williams/deeph-m9/software/overlap-only-OpenMX` |
| HDF5 | [HDF5 1.12.1 官方源码](https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.12/hdf5-1.12.1/src/)，13,534,796 bytes，官方及本地 SHA-256 `79c66ff67e666665369396e9c90b32e238e501f345afd2234186bfb8331081ca` | `/home/evan-williams/deeph-m9/downloads/overlap_sources/hdf5-1.12.1.tar.gz` |
| DeepH 解析器 | `mzjb/DeepH-pack` v0.2.2，提交 `66703c532a6f633f4bbc8f94f75c8698a7f89859` | `/home/evan-williams/deeph-m9/software/DeepH-pack` |

来源只读检查器为 [`m9_openmx_source_inspect.py`](../06_reproduction/scripts/m9_openmx_source_inspect.py)。运行时清单 `/home/evan-williams/deeph-m9/manifests/openmx_overlap_source_manifest.json` 的 SHA-256 为 `bdce33ea88a5214e631dd917fe6717967dd38e8bd2804ad53f3fbdc85f17397c`。该历史清单只作为来源身份观察，不再承担可执行顺序语义；正式组合顺序由机读合同和唯一受控驱动 [`m9_openmx_build.py`](../06_reproduction/scripts/m9_openmx_build.py) 执行。驱动拒绝绝对路径、父目录、反斜杠、规范化重复、链接和特殊 tar 成员，并为官方 3.9.9 树与最终 overlap 树分别生成逐文件组合清单。

补丁顺序严格为：安全解压 OpenMX 3.9 基础包 → 官方 patch3.9.9 除 `kpoint.in` 外的全部普通成员写入 `openmx3.9/source` → `kpoint.in` 唯一写入 `openmx3.9/work/kpoint.in` → 写入唯一活动 `CC/FC/LIB` → 固定官方组合树清单并完成官方 3.9.9 编译链接烟雾 → 只用冻结提交中的 `openmx.c` 和 `truncation.c` 覆盖同名文件 → 证明两个组合树只有这两条路径不同 → clean rebuild。不得把 overlap-only 文件先于官方编译应用，也不得从仓库 `main` 动态取得新提交。

## 3. PAO、VPS 与 basis

冻结的物种定义是：

```text
C  C6.0-s2p2d1  C_PBE19
```

- PAO：`openmx3.9/DFT_DATA19/PAO/C6.0.pao`，693,570 bytes，SHA-256 `1442a834dbc2b9b55e8f11a20734c7b77765fa4e05ca3e1b1f004da46bfaaef4`。
- VPS：`openmx3.9/DFT_DATA19/VPS/C_PBE19.vps`，333,898 bytes，SHA-256 `4b9c78eb72be25ca46366b8fd39c74ae7172d7db9e77b29782a42f71901b38a7`。
- PAO 截断半径：6.0 Bohr。
- 轨道行：`[0,0,1,1,2]`，即两套 s、两套 p、一套 d，共 13 个实原子轨道函数；必须与冻结数据的 450×72 行逐行一致。

这些对象来自 OpenMX 3.9 基础归档中的 DFT_DATA19，不从其他 OpenMX 版本、外部 PAO 数据库或本地缓存替换。

## 4. 编译合同

### 4.1 Ubuntu 包

目标系统是已冻结的 Ubuntu 22.04.5 LTS。允许在工作包审计通过后由 WSL root 安装以下精确 apt 候选；实际安装版本必须逐项等于表中值，否则停止：

| 包 | 版本 |
|---|---|
| `openmpi-bin` | `4.1.2-2ubuntu1` |
| `libopenmpi-dev` | `4.1.2-2ubuntu1` |
| `libscalapack-openmpi-dev` | `2.1.0-4` |
| `libfftw3-dev` | `3.3.8-2ubuntu8` |
| `libblas-dev` | `3.10.0-2ubuntu1` |
| `liblapack-dev` | `3.10.0-2ubuntu1` |
| `gfortran` | `4:11.2.0-1ubuntu1` |
| `make` | `4.3-4.1build1` |

现有编译器实测为 GCC/GFortran 11.4.0；`libblas-dev`、`liblapack-dev`、`gfortran` 和 `make` 已安装，其余缺失项只在审计放行后安装。禁止加入 MKL、Intel MPI、系统 HDF5 1.10.7 或未冻结的编译器路径。

### 4.2 HDF5

HDF5 1.12.1 以 `gcc 11.4.0`、`CFLAGS=-O2 -fPIC` 构建到 `/home/evan-williams/deeph-m9/env/hdf5-1.12.1`：

```bash
./configure --prefix=/home/evan-williams/deeph-m9/env/hdf5-1.12.1 \
  --enable-shared --disable-static --disable-fortran --disable-cxx
make -j2
make check -j1
make install
```

配置摘要、`make check` 结果、安装树清单和库文件哈希必须进入运行时清单。任何测试失败均停止，不能回退到系统 HDF5 1.10.7。

### 4.3 OpenMX makefile

官方 patch3.9.9 的 `makefile` 只替换首个活动的 `CC`、`FC`、`LIB` 定义：

```make
CC = /usr/bin/mpicc -O3 -fopenmp -fcommon -Dkcomp -I${HDF5_PREFIX}/include
FC = /usr/bin/mpif90 -O3 -fopenmp -fallow-argument-mismatch -Dkcomp
LIB = -L${HDF5_PREFIX}/lib -Wl,-rpath,${HDF5_PREFIX}/lib -lhdf5 -lscalapack-openmpi -lfftw3 -llapack -lblas -lmpi_usempif08 -lmpi_usempi_ignore_tkr -lmpi_mpifh -lgfortran -lm -lpthread
```

`${HDF5_PREFIX}` 在生成 makefile 时替换为冻结的绝对前缀，不依赖调用 shell 的临时变量。`-fcommon` 与 `-fallow-argument-mismatch` 是 GCC/GFortran 11.4 下 OpenMX 3.9.9 的兼容性合同；缺少任一标志、出现重复活动定义或编译器/OpenMPI 版本漂移均在编译前拒绝。构建环境的 `PATH` 收紧为 `/usr/sbin:/usr/bin:/sbin:/bin`，不搜索 `/usr/local`；实际调用使用冻结的 `/usr/bin/gcc`、`gfortran`、`mpicc`、`mpif90`、`make`、`git`、`ldd`、`dpkg-query` 和 `dpkg`，逐项核对规范路径、版本、字节与 SHA-256。对 `mpicc/mpif90 --showme:command` 还要求分别唯一展开为 `gcc/gfortran`，并按冻结 PATH 解析到已登记的系统编译器规范对象；固定 PATH 内的同名影子或调用者 PATH 前置包装器均不能参与构建。

先执行官方 3.9.9 `make clean && make -j2 all && make install`，对编译后新增文件执行明确的 build-artifact allowlist；clean 后重新枚举实际完整受控路径集合，证明它与编译前集合及内容一致。再覆盖两个 overlap-only 文件，重新枚举而非复用旧路径表，证明两阶段路径集合相等、内容差异恰为 `source/openmx.c` 与 `source/truncation.c`。最终 build manifest 保存 HDF5 configure argv/编译器/CFLAGS、`make check` 退出码与日志哈希、完整安装树 inventory、HDF5 库哈希，以及 `ldd` 每个实际规范库路径、字节、SHA-256、dpkg 包和版本；HDF5 必须唯一来自冻结前缀，OpenMPI/ScaLAPACK/FFTW/BLAS/LAPACK/GFortran 必须属于冻结运行库包。

## 5. 450 个结构的唯一映射

机读合同为 [`m9_overlap_only_contract.json`](../06_reproduction/configs/m9_overlap_only_contract.json)，输入生成器为 [`m9_openmx_input.py`](../06_reproduction/scripts/m9_openmx_input.py)。结构 ID 必须严格为 `500,510,...,4990`，共 450 个，按数值升序运行。

对每个结构：

- OpenMX 原子编号 `1..72` 与 `site_positions.dat` 的列 `0..71` 一一对应，不允许排序、包装后重排或按空间位置重新编号。
- OpenMX 晶格行向量是 `lat.dat.T`；笛卡尔坐标是 `site_positions.dat.T`，单位 Å。
- 输入 fractional 坐标唯一采用 `X_frac = X_cart @ inv(L)`，以 16 位小数写出；`X_frac @ L` 与原坐标的最大绝对残差必须不超过 `1e-12 Å`。
- 输入固定为 `FRAC`、晶格单位 `Ang`、300 Ry、`1×1×1` k 网格、非磁、无 SOC、`MD.Type Nomd`。k 网格和 SCF 字段仅满足 OpenMX 输入解析；冻结补丁在 SCF 前退出，不能产生 SCF 标签。
- 每个结构在运行前生成 `structure_mapping.json`，保存原始结构文件哈希、输入哈希、原子映射、晶格行列规则和 round-trip 残差。

生成器没有自由根路径和 `--all` 接口，只接受单个冻结 `--structure-id`。每次生成前均核对 3600 文件清单 `/home/evan-williams/deeph-m9/manifests/graphene_inventory.json` 的 SHA-256 `048e376ffdf52b3c3a5aba53904a00bda7f55280ed3afd8de55e8515d8247800`、数据合同 SHA-256 `a23e84db1ac3b3d496b73d3103d307619daac32c80c8c87be35a684ca12b31b0`、该结构八个源文件的清单哈希，以及实际 PAO/VPS 哈希。`rc.npz`、`rh.npz` 和 `rlat.dat` 均不得从映射 provenance 中省略。输入写完后重新解析 72 个原子和 3 个晶格行，核对编号、物种、电荷、晶格与坐标回代；状态机只允许先生成 500，再在投影通过后逐个生成 510 至 4990。

送审前已只读调用同一映射函数核对 450/450 个结构，未生成输入或运行目录：结构数为 450，最大 fractional round-trip 残差为 `3.552713678800501e-15 Å`，450 个晶格行列式均为 `5657.804581140005 Å^3`。

冻结补丁调用共享的 `Set_OLP_Kin(OLP,H0)` 例程，可能在内存中形成未输出的临时 kinetic 数组；唯一允许序列化的电子结构矩阵是 `output_O_nm(OLP[0],"output/overlaps",0,1.0)` 写出的 overlap。任何 `H0`、Hamiltonian、密度、能量、力或其他 DFT 矩阵文件一旦出现，均判为越权失败并停止。

## 6. 输出模式与验证

单 MPI rank 命令固定为：

```bash
env OMP_NUM_THREADS=1 \
  LD_LIBRARY_PATH=/home/evan-williams/deeph-m9/env/hdf5-1.12.1/lib \
  /usr/bin/mpirun --bind-to none -np 1 OPENMX_BINARY openmx.dat > openmx.std 2> openmx.err
```

规范原始输出只有 `output/overlaps_0.h5`。补丁源码冻结的 HDF5 合同为：

- 顶层 dataset 名是 `[R1, R2, R3, i, j]`，五个整数；`i,j` 是 1-based 原子编号；
- dataset 为 `float64`、shape `(13,13)`，行列顺序继承 `C6.0-s2p2d1`；
- 每个结构的键集合必须与对应 `rh.npz` 完全相等，预期为 2,880 个键；不能用缺键、并集或近邻重构代替；
- 对所有键验证 `S(R,i,j)=S(-R,j,i)^T`，最大绝对残差不超过 `1e-10`；所有值有限；
- `deeph.preprocess.openmx_parse_overlap` 生成 `overlaps.h5` 后，键和值必须与原始 HDF5 完全一致；解析所得晶格、坐标、元素和轨道行必须分别回到冻结结构，浮点最大绝对残差不超过 `1e-10 Å`；
- `output` 下不允许额外 rank 文件；运行目录在报告写入前必须与合同中的完整文件 allowlist 精确相等，大小写变化的额外 HDF5、Hamiltonian、density、energy、force、stress、SCF 或其他 DFT 输出均拒绝。

唯一公开变更入口是预算脚本的动作 API；[`m9_overlap_executor.py`](../06_reproduction/scripts/m9_overlap_executor.py) 本身不以公开环境变量证明调用者身份。预算进程为每次非 apt 动作生成一次性 capability，绑定预算 PID、子 PID、transaction ID、动作、结构、CPU 桶、forecast 和精确 launcher argv；[`m9_overlap_source_launcher.py`](../06_reproduction/scripts/m9_overlap_source_launcher.py) 在派发前以私有权限原子消费，并由控制器回查正在运行的事务。直接伪造原三个公开环境变量、自由 argv、特殊模式或多 rank 均不能建立 capability。

预算入口和 source launcher 均只允许冻结 Python 以 `-I -S -B` 启动；隔离且禁 site 的模式在执行入口正文前排除脚本目录、当前目录、用户 site、site-packages 及 `.pth` 处理。两个入口核对 isolated/no-site/dont-write-bytecode 标志、`sys.path`，并把 `argparse/hashlib/json/pathlib` 的 stdlib loader、origin 与 SHA-256 写入启动 provenance。capability 被验证、项目源码 loader 建立且合同哈希通过后，唯一冻结的 dependency site-packages 才以普通 `sys.path.append` 加入；禁止 `site.addsitedir`，回执必须记录 `pth_processed=false`。控制目录必须恰好等于冻结清单登记的全部 Python 文件，任何未登记 `.py`、`.pyc`、`.pyo`、`__pycache__`、其他子目录或符号链接均拒绝。launcher 随后逐个读取已哈希 UTF-8 源码、核对 SHA-256、`compile()` 并由自定义 `FrozenSourceLoader` 执行，回执记录每个模块的 `path/loader/origin/hash/bytecode_consulted=false`。DeepH v0.2.2 parser 同样要求 clean 固定提交、树内无 symlink/`__pycache__`/`.pyc`，并通过 source-only loader 导入。executor 运行前核对最终二进制、官方/overlap 组合树、build manifest、输入、八文件映射、PAO/VPS 和 parser identity，固定 `-np 1`、`OMP_NUM_THREADS=1`、HDF5 前缀和运行目录。每次执行生成一次性定稿的回执，绑定固定 argv、全部哈希、预算 transaction、CPU 桶、预测、起止时间、退出码、日志和三种 payload 增量。

验证器为 [`m9_overlap_contract.py`](../06_reproduction/scripts/m9_overlap_contract.py)。它要求全部 72 个 onsite overlap 块分别在 `1e-10` 内对称且正定，并核对 stdout 的 overlap-only 正常路径标记、空 stderr 和无特殊模式/SCF 标记。完整 `S(k)` 的正定性、条件数、Fourier 约定和广义本征验收仍在 M9-06 统一冻结，不以 onsite 检查代替。

## 7. 预算、顺序和硬停止

所有变更命令继续经 `m9_budget.py run --overlap-operation` 的冻结 action API 执行；D-018 后禁止通用 `run` 任意命令，未来 GPU 动作须另建冻结 action 与门控。D-018 只取消总墙钟截止时间；100 GiB 三口径硬上限、全部历史用量和下列 overlap-only 子预算不重置：

| 操作 | 子上限 |
|---|---:|
| apt/HDF5/OpenMX 准备与编译 | 7,200 CPU 墙钟秒 |
| 结构 500 单结构烟雾 | 1,800 CPU 墙钟秒 |
| 450 结构全批次 | 21,600 CPU 墙钟秒 |
| 新增存储 | 10 GiB |
| GPU | 0 秒 |

独立审计 PASS 后先由 [`m9_budget.py`](../06_reproduction/scripts/m9_budget.py) 的 `overlap-init` 在同一锁内校验审计门和冻结哈希，同时建立 overlap 存储基线、预算/工作流状态与事务日志。之后每个变更动作必须使用 `run --overlap-operation --overlap-action ACTION`，不得提供子命令或自由 argv；预算进程自己构造固定 apt 或 source-only launcher 命令。显式 forecast 不仅要非负，还必须达到冻结操作下界：apt 512 MiB、source prepare 1 GiB、source build 4 GiB、smoke prepare 1 MiB、smoke run 64 MiB、project 1 MiB；batch prepare/run 均不得低于通过 450 投影写入工作流的 `per_structure_forecast_bytes`。

每个动作采用 journaled `PREPARED → RUNNING → SUCCESS_COMMITTED/FAILED_COMMITTED` 事务。预算和工作流同时登记 active transaction；apt 失败、controller 异常、SIGTERM/SIGKILL、超时、launcher 回执错误或进程重启后发现非终态事务，均在同一预算锁下把预算与工作流同时提交为不可继续的 `HARD_STOP`。子进程使用新进程组，超时先终止全组再升级 kill。

正式调用骨架唯一为：

```bash
/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B \
  /mnt/e/Projects/Codex/DeepH/06_reproduction/scripts/m9_budget.py \
  run --bucket none --cpu-bucket BUCKET --forecast-bytes BYTES \
  --overlap-operation --overlap-action ACTION \
  --config /mnt/e/Projects/Codex/DeepH/06_reproduction/configs/m9_overlap_only_contract.json \
  [--structure-id ID]
```

`ACTION` 只可为 `apt_install/source_prepare/source_build/smoke_prepare/smoke_run/project/batch_prepare/batch_run`，且动作、桶、阶段、结构 ID 与 forecast 下界必须一致；命令末尾不得出现 `--` 或任何子命令。`overlap-init` 也必须用同一冻结 Python 的 `-I -S -B` 方式执行。

10 GiB 子限从 `OVERLAP_BUDGET_START` 同时按 combined apparent、combined allocated 和 VHDX growth 三个增量口径计算。500 smoke 的 payload 增量取三者最大值，每结构另加 1 MiB 控制文件保守余量，再以 `ceil(value × 450 × 1.25)` 投影；CPU 同样以 `ceil(max(smoke_seconds,1) × 450 × 1.25)` 投影。投影须同时不超过 21,600 CPU 秒、10 GiB 子限和 100 GiB 三口径总余量；D-018 后不再与总墙钟余量比较。

执行顺序不可跳过：

1. 本工作包独立审计 `PASS`，剩余问题 0。
2. 安装精确系统包；构建并测试 HDF5；官方 OpenMX 3.9.9 编译链接烟雾；应用 overlap-only 两文件并重新构建。
3. 只生成结构 500 输入，执行单结构烟雾；验证源、输入、键、反向关系、坐标回读、禁止输出和哈希。
4. 依据结构 500 实测保守投影 450 结构的 CPU 墙钟和存储。若投影超过 21,600 CPU 秒、10 GiB 或 100 GiB 总存储余量，写入 `HARD_STOP` 并暂停；无总墙钟期限不改变这些停止条件。
5. 按升序逐结构执行；每个结构通过验证后才可运行下一个，首个失败即停止，不跳过失败结构。
6. 450/450 通过后，由同一独立审计员定点复核 `M9-DATA-B01`。只有其明确 `CLOSED` 才允许恢复 M9-05 划分与训练。

任何命令需要 Windows 重启、软件/数据/基组/映射变更、结果后放宽容差、额外预算或输出超出 overlap-only 边界时，立即停止并重新请求授权。

## 8. 失败矩阵

自动拒绝矩阵实现于 [`test_m9_overlap_controls.py`](../06_reproduction/tests/test_m9_overlap_controls.py)，当前 18/18 通过。除第一轮已有的编译标志、危险 tar、输入、输出和投影负例外，新增 PATH 前置假工具与 MPI wrapper 底层编译器影子隔离、构建后未登记普通文件、HDF5 安装树逐文件哈希、公开环境变量伪造、自由子命令、forecast=0/低于投影、预算与工作流双硬停止，以及相邻 sourceless 恶意 pyc 在普通 `-B` 下实际执行、恶意 site-packages `.pth` 在 `-I -B` 下先于正文执行、两者在正式 `-I -S -B` 下均被隔离且控制目录缓存/未登记源码被拒绝的穿透证据。

正式运行还必须自动拒绝：源归档或仓库哈希错误、补丁顺序错误、PAO/VPS 替换、apt 版本漂移、HDF5 测试失败或链接到 1.10.7、多 MPI rank、输入篡改、HDF5 非 `float64(13,13)`、NaN/Inf、键缺失/多余、逆边缺失或转置残差超限、解析后坐标/轨道漂移、额外 DFT 标签、越序、首错后继续以及预算预测或实测越界。正式对象只能在本工作包定点复核通过后产生。

## 9. 送审对象与审计问题

送审核心对象及当前 SHA-256：

| 文件 | SHA-256 |
|---|---|
| `06_reproduction/configs/m9_overlap_only_contract.json` | `327e37d130504944babf6a9c3ed5d4dcc0e8b05b2b04979300ac12cfaf3377ea` |
| `06_reproduction/scripts/m9_overlap_common.py` | `588b60e124f90fb97ef6ab9e248c91fc423196860c2306d285594fd2611ed6d0` |
| `06_reproduction/scripts/m9_openmx_build.py` | `53c6e04cedce994b088b7b6dc738753d378cbcbc15d40600b30d85d87ff78268` |
| `06_reproduction/scripts/m9_openmx_input.py` | `1b7d4acc6b455c9dd3ad3ace51d64a53c792cf45be253553b2a1d2aa3588f19b` |
| `06_reproduction/scripts/m9_overlap_contract.py` | `3c95e18023965c88dd16b15d944c3d3f50409371d51e63066349302dcf199ed0` |
| `06_reproduction/scripts/m9_overlap_executor.py` | `714159bd3b0d6ea6dbbc167c4034aca444cf29fd77d24b03201c2373e96ebd9a` |
| `06_reproduction/scripts/m9_overlap_source_launcher.py` | `4e3d4d11685d4d28ee3f708edbdfc1fe44b2148df423e817f4d6cacddfc67510` |
| `06_reproduction/scripts/m9_budget.py` | `b4573997a1951517c0153bd7238d19e02a14e4cc49680ff15dd4b044f00d4a8d` |
| `06_reproduction/scripts/m9_compatibility_smoke.py` | `983dfc35d116d3dff031603f6604f7d80c03d22be10ea7a3183a33416ce84890` |
| `06_reproduction/scripts/m9_dataset_archive.py` | `2c4a80e54d6ec9c155f6967fa1a5f44e59f0a4f1addd5c7ce562ebca6c5ea060` |
| `06_reproduction/scripts/m9_data_contract.py` | `253bd3daeefa69dc204263074578c3659d52e26bff111afac67c2ce54ab860f4` |
| `06_reproduction/scripts/m9_openmx_source_inspect.py` | `69b7fbb59d2b9d6b0fbdc24c37af85cbb124f5cf3ecc9cb3ce2252c5ad54c9c6` |
| `06_reproduction/scripts/m9_range_download.py` | `6697be45763e4a2b0c4230810a8e4cdcac77681c1e7c28799cbacfa415231db0` |
| `06_reproduction/tests/test_m9_overlap_controls.py` | `79b22d09d673f0f1ef6e6bc38f3a3b03d7993d2a961f2321444bc916053fae79` |
| `06_reproduction/manifests/budget_contract.json` | `96b1821e681fb53425bf2f738f0e8c7defc99f044f83bce57cb6c830b79953f3` |
| `06_reproduction/manifests/openmx_overlap_source_manifest.json` | `c000810f1df35f5aa96aa68c276104dcaf34324ea847806ace63a56a1bb2d70a` |
| `06_reproduction/manifests/m9_overlap_frozen_hashes.json` | `365547aa3107de393eefa6767c4f44e90e54b2490b174546c9f825c211db57af` |

除本工作包自身外，上表所有执行控制对象由冻结哈希清单绑定；独立复核通过后，运行时审计门还必须绑定本工作包、定点复核报告和冻结清单三者的 SHA-256。任何对象变化都会在 apt、构建、输入或运行前拒绝。

独立审计应至少回答：软件与补丁身份是否唯一；GNU/OpenMPI 链接合同是否足以在 Ubuntu 22.04 重建；PAO/VPS/basis 是否与冻结数据一致；450 个结构的行列/原子映射是否唯一；补丁是否只序列化 overlap；HDF5 键和值能否无歧义进入 DeepH v0.2.2；失败矩阵和预算能否阻止静默越权；本包是否足以在不降低 M9 原验收强度的条件下关闭 `M9-DATA-B01`。
