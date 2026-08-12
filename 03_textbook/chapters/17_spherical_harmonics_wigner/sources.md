# 第 17 章来源与论断边界

## 直接来源

| 来源 ID | 本章用途 | 本地证据 |
|---|---|---|
| E-FND-01 | DLMF 归一化复球谐、Condon--Shortley 相位和共轭关系 | [DLMF 14.30 快照](../../../01_sources/documentation/stageE/dlmf_14_30_spherical_harmonics.html) |
| E-FND-03 | 角动量矩阵元、旋转群和 \(\ell,m\) 表示 | [MIT 8.321 第 20—21 讲](../../../01_sources/documentation/stageE/README.md) |
| E-GNN-01 | 球谐方向滤波与旋转等变特征 | [TFN 快照](../../../01_sources/documentation/stageE/thomas_2018_tensor_field_networks.pdf) |
| E-GNN-02 | 球谐与不可约表示在等变网络中的接口 | [e3nn 论文快照](../../../01_sources/documentation/stageE/geiger_2022_e3nn.pdf) |
| DH-02 | 论文层 Hamiltonian 轨道表示的复—实基接口边界 | [DeepH-E3 论文快照](../../../01_sources/documentation/stageE/gong_2023_deeph_e3.pdf) |
| 阶段 D | 轨道顺序、mask、edge identity 与 provenance 接口 | [阶段 D 工作包](../../../08_audits/M6_stageD_work_package.md) |

## 论断边界

Wigner \(D\) 以 [统一表示约定](../../stageE_representation_conventions.md) 的函数作用等式定义，不依赖未冻结的软件 Euler 角接口。复—实矩阵由 DLMF 球谐与本项目归一化实 \(p,d\) 函数的恒等式直接导出。若使用任何库函数，必须先通过点值协变、群律和相似变换测试，不能仅凭函数名判断共轭或轴顺序。DH-02 只支持论文级 Hamiltonian 表示对象；本章的 \(C_\ell,K_\ell\) 是项目约定推导，不证明任何 DeepH/e3nn 软件实现、数据、材料或 DFT 设置已经兼容。

## 来源—论断定位

| 来源或验证对象 | 已定位论断 | 材料入口 |
|---|---|---|
| E-FND-01 | DLMF 复球谐归一化、Condon--Shortley、共轭与低阶函数接口 | 正文 17.1、17.3—17.4；D-E03 第 3、6—7 节；A17-01、04—05 |
| E-FND-03 | 角动量基、旋转算符、Wigner 表示和 \(SO(3)\) 群律 | 正文 17.2；D-E03 第 4—5 节；A17-02—03 |
| E-GNN-01/02 | 球谐方向特征、不可约通道、径向—角向分工及网络接口 | 正文 17.5—17.7；A17-06—10 |
| DH-02 | Hamiltonian 复—实轨道基同步变换的论文级任务边界 | 正文 17.8.2；A17-10；不作软件或复现证据 |
| 阶段 D | 轨道顺序、mask、edge/provenance 在基变换中的同步映射 | 正文 17.8.2—17.8.3；A17-10 |
| D-E03/D-E09 子推导 | 函数作用、\(C_\ell/K_\ell\)、相似变换、点值、方向 validator、Hamiltonian 块/身份接口和存储子预算 | [推导第 3—14 节](../../../04_derivations/stageE/17_spherical_harmonics_wigner.md) |
| T-E03/T-E04/T-E06/T-E07/T-E10/T-E12 | 实表、复—实/点值、Hamiltonian 块身份、宇称、成本和 schema 失败矩阵；执行证据见 [Stage E 代码说明](../../../05_code_exercises/stageE_synthetic_equivariance/README.md) 与 [M7-09 定点复核](../../../08_audits/M7_stageE_code_blocking_reaudit.md) | 正文 17.6—17.8；推导第 13 节；Q17/A17-05—10 |
