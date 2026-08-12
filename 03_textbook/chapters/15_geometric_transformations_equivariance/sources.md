# 第 15 章来源与论断边界

## 直接来源

| 来源 ID | 本章用途 | 本地证据 |
|---|---|---|
| E-FND-03 | 旋转作为量子对称变换、连续群与离散对称性的基础定义 | [MIT 8.321 第 20—23 讲](../../../01_sources/documentation/stageE/README.md) |
| E-GNN-01 | 旋转/平移等变网络的对象类型与按表示变换的特征 | [TFN 快照](../../../01_sources/documentation/stageE/thomas_2018_tensor_field_networks.pdf) |
| E-GNN-02 | \(E(3)\) 不变、等变、表示与宇称的统一术语 | [e3nn 论文快照](../../../01_sources/documentation/stageE/geiger_2022_e3nn.pdf) |
| DH-02 | 论文层的周期 Hamiltonian 轨道块等变任务关系 | [DeepH-E3 论文快照](../../../01_sources/documentation/stageE/gong_2023_deeph_e3.pdf) |
| 阶段 D | 节点置换、周期边、完整边键和 provenance | [阶段 D 工作包](../../../08_audits/M6_stageD_work_package.md) |

## 论断边界

本章将群作用、不变量和等变量写成可检验定义。主动/被动方向、列向量和残差阈值依据 [阶段 E 统一约定](../../stageE_representation_conventions.md) 冻结，属于项目显式约定。E-GNN-01/02 支持一般等变机制，但不证明任意命名为“equivariant”的程序正确；旋转增强、单个旋转样例或标量输出一致均不足以替代逐层协变测试。DH-02 只支持论文层的方法对象与 Hamiltonian 块等变关系，不构成 DeepH/e3nn 软件安装、仓库版本、数据、材料、DFT 设置、SOC 实践或复现实验的证据与授权。

## 来源—论断定位

| 来源或验证对象 | 已定位论断 | 材料入口 |
|---|---|---|
| E-FND-03 | 正旋转、反射、群复合及旋转作为量子对称变换的基础边界 | 正文 15.2.3、15.3.1—15.3.3；推导第 3 节 |
| E-GNN-01 | 标量、向量与高阶表示型特征以及输入/输出表示不同的等变映射 | 正文 15.1.2、15.4.1—15.4.4；A15-01、A15-10 |
| E-GNN-02 | \(E(3)\)、\(O(3)\)、\(SO(3)\)、宇称及表示型等变术语 | 正文 15.3、15.4、15.5.2—15.5.3；A15-05、A15-09 |
| DH-02 | 周期 Hamiltonian 轨道块是表示型协变对象，而非逐元素旋转不变量 | 正文 15.4.2、15.8.1；A15-10；仅作论文级方法证据 |
| 阶段 D | 周期边、完整边键、置换、换胞与 provenance 的离散接口 | 正文 15.1.1、15.3.4、15.5.5、15.8.2；Q15/A15-07—08、10 |
| D-E01/D-E09 子推导 | 主动/被动、复合、几何对象、残差与精度/成本边界 | [推导第 3—13 节](../../../04_derivations/stageE/15_group_actions_equivariance.md) |
| T-E01/T-E02/T-E07/T-E10 | 旋转 validator、几何作用、宇称、残差和成本扫描的验证契约；执行证据见 [Stage E 代码说明](../../../05_code_exercises/stageE_synthetic_equivariance/README.md) 与 [M7-09 定点复核](../../../08_audits/M7_stageE_code_blocking_reaudit.md) | 正文 15.6；推导第 12 节；Q15/A15-09—10 |
