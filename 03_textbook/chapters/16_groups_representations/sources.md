# 第 16 章来源与论断边界

## 直接来源

| 来源 ID | 本章用途 | 本地证据 |
|---|---|---|
| E-FND-03 | 旋转群、\(SO(3)\)/\(SU(2)\)、角动量表示与耦合的基础 | [MIT 8.321 讲义快照](../../../01_sources/documentation/stageE/README.md) |
| E-GNN-02 | \(O(3)\) 不可约表示、宇称、multiplicity 与神经特征分型 | [e3nn 论文快照](../../../01_sources/documentation/stageE/geiger_2022_e3nn.pdf) |
| E-FND-01 | \(\ell,m\) 球谐标签及归一化接口 | [DLMF 14.30](../../../01_sources/documentation/stageE/dlmf_14_30_spherical_harmonics.html) |
| DH-02 | 论文层的 Hamiltonian 轨道表示与左右协变接口 | [DeepH-E3 论文快照](../../../01_sources/documentation/stageE/gong_2023_deeph_e3.pdf) |
| 阶段 D | 多壳层实际轨道身份、mask、edge key 与 provenance 接口 | [阶段 D 工作包](../../../08_audits/M6_stageD_work_package.md) |

## 论断边界

本章的实 \(p,d\) 矩阵由 [统一表示约定](../../stageE_representation_conventions.md) 的笛卡尔向量与对称无迹张量构造直接推出。该构造与化学轨道名称相容，但任何外部软件的顺序、归一化或符号必须通过显式置换—符号矩阵接入。\(SO(3)\) 下同维不代表 \(O(3)\) 下同型；极向量和轴向量必须保留宇称标签。DH-02 只支持论文级 Hamiltonian 表示对象与协变关系，不证明本章合成矩阵对应某个已选软件版本，也不授权数据、材料、DFT 设置或 SOC 实践。

## 来源—论断定位

| 来源或验证对象 | 已定位论断 | 材料入口 |
|---|---|---|
| E-FND-03 | 群表示、整数角动量空间、不可约性及 \(SO(3)\)/\(SU(2)\) 边界 | 正文 16.1—16.3、16.8.1；D-E02 第 3 节；A16-01—02 |
| E-FND-01 | \(\ell,m\)、维数 \(2\ell+1\) 与归一化球谐接口 | 正文 16.3.1、16.4；D-E02 第 3.3、4—6 节 |
| E-GNN-02 | \((\ell,p)\)、直和、multiplicity、同型混合和表示型特征布局 | 正文 16.2、16.5—16.7；A16-02、07—10 |
| DH-02 | Hamiltonian 两端轨道表示的论文级任务接口 | 正文 16.8.3；A16-10；不作软件或复现证据 |
| 阶段 D | shell/component/orbital identity、mask、完整 edge provenance | 正文 16.6.2、16.8.3；A16-06、10 |
| D-E02/D-E09 子推导 | \(s,p,d\) 构造、群律、宇称、维度、参数和局部字节预算 | [推导第 3—12 节](../../../04_derivations/stageE/16_real_spd_representations.md) |
| T-E03/T-E07/T-E10/T-E12 | \(p/d\) 表、宇称、成本子预算与 schema 故障注入；执行证据见 [Stage E 代码说明](../../../05_code_exercises/stageE_synthetic_equivariance/README.md) 与 [M7-09 定点复核](../../../08_audits/M7_stageE_code_blocking_reaudit.md) | 正文 16.7；推导第 11 节；Q16/A16-06—10 |
