# M9 受限 overlap-only OpenMX 工作包

## 1. 状态、授权与门控

- 日期：2026-08-12
- 状态：`REVIEW`
- 依据：D-013、D-014、D-016 与用户对“受限 overlap-only OpenMX 路线”的明确授权；新授权登记为 D-017。
- 目标：只为冻结的 450 个 graphene 结构生成与 Hamiltonian 相同 OpenMX basis 下的实空间 overlap 块，以关闭 `M9-DATA-B01`；不得生成、保存或使用 Hamiltonian、SCF、能量、力、密度矩阵或其他 DFT 标签。
- 当前门控：只允许冻结来源、编写合同和准备可审计代码。独立工作包审计达到 `PASS` 且剩余问题为 0 之前，禁止安装系统包、解压或编译 OpenMX/HDF5、生成 OpenMX 输入、运行任何结构计算。

本包不改变冻结的材料、DeepH 版本、非磁/无 SOC 范围、7 天总墙钟、24 GPU 小时或 100 GiB 总存储。overlap 路线不使用 GPU；其 CPU 墙钟和存储配额是原总预算内的保守子上限，不构成预算扩张。

## 2. 软件与来源对象

| 对象 | 冻结身份 | 本地证据 |
|---|---|---|
| OpenMX 基础包 | [官方 OpenMX 3.9](https://www.openmx-square.org/download.html)，`openmx3.9.tar.gz`，166,014,953 bytes，SHA-256 `27bb56bd4d1582d33ad32108fb239b546bdd1bdffd6f5b739b4423da1ab93ae2` | `/home/evan-williams/deeph-m9/downloads/overlap_sources/openmx3.9.tar.gz` |
| 官方修补包 | [OpenMX patch3.9.9](https://www.openmx-square.org/bugfixed/21Oct17/README.txt)，`patch3.9.9.tar.gz`，1,074,993 bytes，SHA-256 `20cccc4e3412a814a53568f400260e90f79f0bfb7e2bed84447fe071b26edd38` | `/home/evan-williams/deeph-m9/downloads/overlap_sources/patch3.9.9.tar.gz` |
| overlap-only 修改 | [mzjb/overlap-only-OpenMX](https://github.com/mzjb/overlap-only-OpenMX) 提交 `c8bd8f4e01f9f19868bf2928671c21b12272a6f7`，clean | `/home/evan-williams/deeph-m9/software/overlap-only-OpenMX` |
| HDF5 | [HDF5 1.12.1 官方源码](https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.12/hdf5-1.12.1/src/)，13,534,796 bytes，官方及本地 SHA-256 `79c66ff67e666665369396e9c90b32e238e501f345afd2234186bfb8331081ca` | `/home/evan-williams/deeph-m9/downloads/overlap_sources/hdf5-1.12.1.tar.gz` |
| DeepH 解析器 | `mzjb/DeepH-pack` v0.2.2，提交 `66703c532a6f633f4bbc8f94f75c8698a7f89859` | `/home/evan-williams/deeph-m9/software/DeepH-pack` |

来源只读检查器为 [`m9_openmx_source_inspect.py`](../06_reproduction/scripts/m9_openmx_source_inspect.py)。运行时清单 `/home/evan-williams/deeph-m9/manifests/openmx_overlap_source_manifest.json` 的 SHA-256 为 `bdce33ea88a5214e631dd917fe6717967dd38e8bd2804ad53f3fbdc85f17397c`。该清单核对了所有归档成员的安全规范路径、重复路径、链接/特殊对象、总成员数和必要成员哈希；执行时没有解压、编译、安装或计算。

补丁顺序严格为：OpenMX 3.9 基础包 → 官方 patch3.9.9 的全部成员写入 `openmx3.9/source` → 先对官方 3.9.9 做编译链接烟雾 → 只用冻结提交中的 `openmx.c` 和 `truncation.c` 覆盖同名文件 → 再做 clean build。不得把 overlap-only 文件先于官方 patch 应用，也不得从仓库 `main` 动态取得新提交。

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
make check -j2
make install
```

配置摘要、`make check` 结果、安装树清单和库文件哈希必须进入运行时清单。任何测试失败均停止，不能回退到系统 HDF5 1.10.7。

### 4.3 OpenMX makefile

官方 patch3.9.9 的 `makefile` 只替换首个活动的 `CC`、`FC`、`LIB` 定义：

```make
CC = mpicc -O3 -fopenmp -Dkcomp -I${HDF5_PREFIX}/include
FC = mpif90 -O3 -fopenmp -Dkcomp
LIB = -L${HDF5_PREFIX}/lib -Wl,-rpath,${HDF5_PREFIX}/lib -lhdf5 -lscalapack-openmpi -lfftw3 -llapack -lblas -lmpi_usempif08 -lmpi_usempi_ignore_tkr -lmpi_mpifh -lgfortran -lm -lpthread
```

`${HDF5_PREFIX}` 在生成 makefile 时替换为冻结的绝对前缀，不依赖调用 shell 的临时变量。先执行官方 3.9.9 `make clean && make -j2 all && make install`，记录编译器、链接依赖和二进制哈希；再覆盖两个 overlap-only 文件，执行同一 clean build。最终以 `ldd` 证明链接到冻结 HDF5 1.12.1、OpenMPI、ScaLAPACK、FFTW、BLAS/LAPACK，而不是系统 HDF5 1.10.7。

## 5. 450 个结构的唯一映射

机读合同为 [`m9_overlap_only_contract.json`](../06_reproduction/configs/m9_overlap_only_contract.json)，输入生成器为 [`m9_openmx_input.py`](../06_reproduction/scripts/m9_openmx_input.py)。结构 ID 必须严格为 `500,510,...,4990`，共 450 个，按数值升序运行。

对每个结构：

- OpenMX 原子编号 `1..72` 与 `site_positions.dat` 的列 `0..71` 一一对应，不允许排序、包装后重排或按空间位置重新编号。
- OpenMX 晶格行向量是 `lat.dat.T`；笛卡尔坐标是 `site_positions.dat.T`，单位 Å。
- 输入 fractional 坐标唯一采用 `X_frac = X_cart @ inv(L)`，以 16 位小数写出；`X_frac @ L` 与原坐标的最大绝对残差必须不超过 `1e-12 Å`。
- 输入固定为 `FRAC`、晶格单位 `Ang`、300 Ry、`1×1×1` k 网格、非磁、无 SOC、`MD.Type Nomd`。k 网格和 SCF 字段仅满足 OpenMX 输入解析；冻结补丁在 SCF 前退出，不能产生 SCF 标签。
- 每个结构在运行前生成 `structure_mapping.json`，保存原始结构文件哈希、输入哈希、原子映射、晶格行列规则和 round-trip 残差。

送审前已只读调用同一映射函数核对 450/450 个结构，未生成输入或运行目录：结构数为 450，最大 fractional round-trip 残差为 `3.552713678800501e-15 Å`，450 个晶格行列式均为 `5657.804581140005 Å^3`。

冻结补丁调用共享的 `Set_OLP_Kin(OLP,H0)` 例程，可能在内存中形成未输出的临时 kinetic 数组；唯一允许序列化的电子结构矩阵是 `output_O_nm(OLP[0],"output/overlaps",0,1.0)` 写出的 overlap。任何 `H0`、Hamiltonian、密度、能量、力或其他 DFT 矩阵文件一旦出现，均判为越权失败并停止。

## 6. 输出模式与验证

单 MPI rank 命令固定为：

```bash
env OMP_NUM_THREADS=1 \
  LD_LIBRARY_PATH=/home/evan-williams/deeph-m9/env/hdf5-1.12.1/lib \
  mpirun --bind-to none -np 1 OPENMX_BINARY openmx.dat > openmx.out 2> openmx.err
```

规范原始输出只有 `output/overlaps_0.h5`。补丁源码冻结的 HDF5 合同为：

- 顶层 dataset 名是 `[R1, R2, R3, i, j]`，五个整数；`i,j` 是 1-based 原子编号；
- dataset 为 `float64`、shape `(13,13)`，行列顺序继承 `C6.0-s2p2d1`；
- 每个结构的键集合必须与对应 `rh.npz` 完全相等，预期为 2,880 个键；不能用缺键、并集或近邻重构代替；
- 对所有键验证 `S(R,i,j)=S(-R,j,i)^T`，最大绝对残差不超过 `1e-10`；所有值有限；
- `deeph.preprocess.openmx_parse_overlap` 生成 `overlaps.h5` 后，键和值必须与原始 HDF5 完全一致；解析所得晶格、坐标、元素和轨道行必须分别回到冻结结构，浮点最大绝对残差不超过 `1e-10 Å`；
- `output` 下不允许额外 rank 文件，运行目录中不允许任何其他 HDF5 电子结构输出。

验证器为 [`m9_overlap_contract.py`](../06_reproduction/scripts/m9_overlap_contract.py)。它还要求 atom-1 onsite overlap 块对称且正定。完整 `S(k)` 的正定性、条件数、Fourier 约定和广义本征验收仍在 M9-06 统一冻结，不以单个 onsite 块代替。

## 7. 预算、顺序和硬停止

所有变更命令继续经 `m9_budget.py run` 执行，原预算截止时间和 100 GiB 三口径硬上限不重置。overlap-only 子预算为：

| 操作 | 子上限 |
|---|---:|
| apt/HDF5/OpenMX 准备与编译 | 7,200 CPU 墙钟秒 |
| 结构 500 单结构烟雾 | 1,800 CPU 墙钟秒 |
| 450 结构全批次 | 21,600 CPU 墙钟秒 |
| 新增存储 | 10 GiB |
| GPU | 0 秒 |

执行顺序不可跳过：

1. 本工作包独立审计 `PASS`，剩余问题 0。
2. 安装精确系统包；构建并测试 HDF5；官方 OpenMX 3.9.9 编译链接烟雾；应用 overlap-only 两文件并重新构建。
3. 只生成结构 500 输入，执行单结构烟雾；验证源、输入、键、反向关系、坐标回读、禁止输出和哈希。
4. 依据结构 500 实测保守投影 450 结构的墙钟和存储。若投影超过 21,600 秒、10 GiB 或原总预算余量，写入 `HARD_STOP` 并暂停。
5. 按升序逐结构执行；每个结构通过验证后才可运行下一个，首个失败即停止，不跳过失败结构。
6. 450/450 通过后，由同一独立审计员定点复核 `M9-DATA-B01`。只有其明确 `CLOSED` 才允许恢复 M9-05 划分与训练。

任何命令需要 Windows 重启、软件/数据/基组/映射变更、结果后放宽容差、额外预算或输出超出 overlap-only 边界时，立即停止并重新请求授权。

## 8. 失败矩阵

下列失败必须有自动拒绝证据：源归档/成员/仓库提交哈希错误；补丁顺序错误；PAO/VPS 被替换；apt 版本漂移；HDF5 测试失败或链接到 1.10.7；多 MPI rank；原子重排；晶格转置错误；fractional round-trip 超限；输入哈希错误；HDF5 非 `float64(13,13)`；NaN/Inf；键缺失/多余；逆边缺失或转置残差超限；解析后坐标/轨道漂移；额外 HDF5/DFT 标签；结构失败后继续；预算预测或实测越界。

## 9. 送审对象与审计问题

送审核心对象及当前 SHA-256：

| 文件 | SHA-256 |
|---|---|
| `06_reproduction/configs/m9_overlap_only_contract.json` | `18B37BF98E49B20BC531AD9C36CC3C0812F2B5ACF1A84EE4D5E621082874C3EB` |
| `06_reproduction/scripts/m9_openmx_source_inspect.py` | `69B7FBB59D2B9D6B0FBDC24C37AF85CBB124F5CF3ECC9CB3CE2252C5AD54C9C6` |
| `06_reproduction/scripts/m9_openmx_input.py` | `5E89845B796EDA7F4AE08EF4657B4CB399D089AF9A1112A80D78E4CA7F9573E7` |
| `06_reproduction/scripts/m9_overlap_contract.py` | `83B684A6DDA25BC49BF57C91131678BE5F89AEF018274A8D971FF6779BC9A615` |
| `06_reproduction/scripts/m9_budget.py` | `265117AFECBB8427E9128C904C9CBBC0FCF6A7018AAF9697E6BA83DDAB2A1EF8` |
| `06_reproduction/manifests/budget_contract.json` | `36FF0EFE2DCDBAFBCA712E93D037E8798E747CAB7BEADFCB72941B5CF88816D2` |
| `06_reproduction/manifests/openmx_overlap_source_manifest.json` | `6F9F659D0EACA7BDAC989DF0A661379A8E429AA58960C5FA98FAA966BA9F575F` |

独立审计应至少回答：软件与补丁身份是否唯一；GNU/OpenMPI 链接合同是否足以在 Ubuntu 22.04 重建；PAO/VPS/basis 是否与冻结数据一致；450 个结构的行列/原子映射是否唯一；补丁是否只序列化 overlap；HDF5 键和值能否无歧义进入 DeepH v0.2.2；失败矩阵和预算能否阻止静默越权；本包是否足以在不降低 M9 原验收强度的条件下关闭 `M9-DATA-B01`。
