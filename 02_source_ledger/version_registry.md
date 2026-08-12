# DeepH 软件与资料版本注册表

本表用于防止论文方法、旧版代码、现代代码和第三方说明之间的接口混用。任何安装、配置解释或代码引用都应先新增一行，并固定到发布版本或提交哈希。

| 对象 ID | 对象类型 | 官方位置 | 发布/提交 | 日期 | 语言/框架 | 配置格式 | 数据接口 | 对应论文 | 核验状态 | 备注 |
|---|---|---|---|---|---|---|---|---|---|---|
| LEGACY-PACK | M8 冻结的首轮实践源码仓库 | [mzjb/DeepH-pack](https://github.com/mzjb/DeepH-pack) | `v0.2.2`；提交 `66703c532a6f633f4bbc8f94f75c8698a7f89859` | 重新核对于 2026-08-11 | Python 3.9；PyTorch 1.9.1；PyG 1.7.2；e3nn 0.3.5；可选 Julia 1.6.6 | INI | 官方处理后 OpenMX graphene 数据；OpenMX 3.9 provenance/overlap 身份 | DH-01 | `PRIMARY_EXPLICIT` | D-013 已冻结、D-014 已授权；LGPL-3.0；实际安装仍须 M9-01 审计通过 |
| LEGACY-E3 | 旧版公开源码仓库 | [Xiaoxun-Gong/DeepH-E3](https://github.com/Xiaoxun-Gong/DeepH-E3) | `main`，尚未冻结提交 | 访问于 2026-08-03 | Python ≥3.9；PyTorch 1.9.0；PyG 1.7.2；e3nn 0.3.5；可选 Julia 1.5.4 | INI | 使用旧版预处理数据；可借用旧版 DeepH-pack 预处理 | DH-02 | `PRIMARY_EXPLICIT` | 仓库明确建议新用户考虑现代 DeepH-pack |
| XDEEPH | 磁性扩展源码仓库 | [mzjb/xDeepH](https://github.com/mzjb/xDeepH) | `main`，尚未冻结提交 | 访问于 2026-08-03 | 具体依赖待选定后从仓库锁定 | 待核验 | 磁结构数据与局域 Hamiltonian | DH-03 | `PARTIAL` | 论文与仓库存在；本轮未审计安装文件 |
| HYBRID-ADDON | 杂化泛函附加源码 | [aaaashanghai/DeepH-hybrid](https://github.com/aaaashanghai/DeepH-hybrid) | `main`，尚未冻结提交 | 访问于 2026-08-03 | 仓库说明复用 DeepH-E3 环境 | 依赖 DeepH-E3 | ABACUS/HSE 数据的附加处理 | DH-06 | `PRIMARY_EXPLICIT` | 不是完整独立包；数据页面文件受限 |
| HPRO-031 | 平面波—AO 转换软件 | [Xiaoxun-Gong/HPRO](https://github.com/Xiaoxun-Gong/HPRO)；PyPI `hpro` | PyPI 0.3.1；仓库提交待冻结 | 2026-06-24 发布；2026-08-03 访问 | Python ≥3.9；NumPy/SciPy/h5py；可选 MPI/SLEPc | Python API / CLI，待实践核验 | Quantum ESPRESSO、BerkeleyGW、GPAW、SIESTA 等；VASP 表中仅列结构输入 | DH-07 | `PRIMARY_EXPLICIT` | 实际选用前须用最小样例验证所需文件与矩阵精度 |
| MODERN-PACK-106 | 现代发布包 | [官方文档](https://docs.deeph-pack.com/deeph-pack/en/latest/)；PyPI `deepx-pack` | 1.0.6.post3 元数据 | 2026-01-19 发布；2026-08-03 访问 | Python ≥3.13,<3.15；JAX/Flax；GPU 文档列 CUDA 12.8/12.9 | TOML；`deeph-train` / `deeph-infer` | 现代 `DeepH` 格式 | SW-01 | `PRIMARY_EXPLICIT` | 官方页面要求申请获取实际软件；未定位公开主源码仓库，不直接安装 |
| MODERN-DOCK | 现代公开接口/后处理源码 | [kYangLi/DeepH-dock](https://github.com/kYangLi/DeepH-dock)；[文档](https://docs.deeph-pack.com/deeph-dock/en/latest/) | `main`，尚未冻结提交 | 访问于 2026-08-03 | Python；具体依赖在选用时锁定 | CLI `dock` + Python API | 现代 DeepH 格式；多 DFT 转换、矩阵与能带后处理 | SW-02 | `PRIMARY_EXPLICIT` | GPL-3.0；可以独立使用 |
| ABACUS-DOCK | DFT 接口边界 | [现代数据准备文档](https://docs.deeph-pack.com/deeph-pack/en/latest/core_workflows/data_preparation.html) | ABACUS 3.10 LTS | 访问于 2026-08-03 | ABACUS + DeepH-dock | ABACUS 输入 + `dock convert` | 当前只实现 ABACUS 原子轨道模式 | SW-02 | `PRIMARY_EXPLICIT` | 其他 ABACUS 版本输出名可能不同；平面波模式不能直接套用 |
| DEEPH-R-PAPER | 方法论文，无已核验代码 | [PRL 137, 046401](https://doi.org/10.1103/mbhs-vlby) | 期刊版本 | 2026-07-20 | 待代码公开后登记 | 待核验 | 实空间 KS 势到 Hamiltonian | DH-10 | `PARTIAL` | 不假定已经进入 MODERN-PACK-106 |

## 核验规则

“最新”属于随时间变化的属性，必须记录访问日期并以官方发布页、仓库提交或文档版本为证据。仓库默认分支的当前状态不能反向证明论文发表时使用的实现。若 README、代码和论文不一致，应分别登记，不通过推测强行统一。
