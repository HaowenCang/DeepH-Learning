# 阶段 E 直接来源快照

## 1. 使用边界

本目录只保存 M7 群表示、球谐函数、张量积、等变网络与时间反演接口所需的固定文献快照。它们不构成 DeepH 软件安装、正式数据下载、材料体系选择、DFT 后端选择或 SOC 实践路线授权。`mit_8_512_lecture10_time_reversal.pdf` 登记为 E-SUP-01 检索期补充快照，不进入 M7 的直接论证链；时间反演主线使用 E-FND-03 的 MIT 8.321 第 22—23 讲。

## 2. 文件、来源 ID 与固定哈希

| 来源 ID | 本地文件 | 直接用途 | SHA-256 |
|---|---|---|---|
| E-FND-01 | `dlmf_14_30_spherical_harmonics.html` | 复球谐归一化、Condon--Shortley 相位和共轭关系 | `D4547C98B7DAA72A6358233A78646A49013D9110FDD817E8CAF139F3CBDA9154` |
| E-FND-02 | `dlmf_34_1_cg_relation.html` | Clebsch--Gordan 系数与 Wigner \(3j\) 的关系 | `D18A8C7EC7C6021C68585B40084CE882B841D018920459B82CBDF1FC36C15211` |
| E-FND-02 | `dlmf_34_3_3j_properties.html` | \(3j\) 对称性、选择定则和正交关系 | `075E37CF5EF5656BAAABAAEF18C7F768FA66ED0F5FB84DFFF314FB0852BFD06A` |
| E-FND-03 | `mit_8_321_lecture20_rotations.pdf` | 角动量矩阵元与旋转群 | `D7FE6547B80C9E1C1B5652AFA414AA82A0CA8E08148153536BFB5305C5016169` |
| E-FND-03 | `mit_8_321_lecture21_su2_addition.pdf` | \(SO(3)\)/\(SU(2)\)、角动量耦合、离散对称性 | `3984AC09661CBA332BF1D077DD547FCDE2A7A3B14CF33CB13EE68A06D6EFE72D` |
| E-FND-03 | `mit_8_321_lecture22_parity_time_reversal.pdf` | 宇称、选择定则、时间反演与自旋 | `A5EBCEFC91FA09AB6D37812FA00678C7E59BD08FFD9E0CDD627D5361BFD9AF4D` |
| E-FND-03 | `mit_8_321_lecture23_time_reversal_consequences.pdf` | 无自旋/半整数自旋、Kramers 结论 | `5529C63E13970D58674DE2B942224821E2D3710F7603485A3777C8F50882D297` |
| E-GNN-01 | `thomas_2018_tensor_field_networks.pdf` | 按表示类型组织特征、球谐滤波与 CG 张量积 | `21E19CC0148B8337198E4FA802D846B9C30D45FBA3C6AD76AC97788DF0F92D74` |
| E-GNN-02 | `geiger_2022_e3nn.pdf` | \(E(3)\) 表示、宇称、张量积和等变操作的统一框架 | `C04B2DE728EB8C0D06405043EE4FB0EEA666AC6C9615A396F1579A35D4BCEEDC` |
| DH-02 | `gong_2023_deeph_e3.pdf` | Hamiltonian 轨道块等变对象与 DeepH-E3 方法边界 | `379B288B66365D5202A481923746D5F01D8EB03433D2C67EA3E5E7261074596E` |
| E-SUP-01（补充、不进入直接链） | `mit_8_512_lecture10_time_reversal.pdf` | MIT 8.512 Theory of Solids II，2009 春季，第 10 讲 `Superconductors With Disorder`；含 10.1.1 时间反演小节，仅作检索留档 | `426E41E4ED6BCC48DF8256572F7D969DD47024E75DC0DAB96F0B04C0C0B70BFA` |

访问日期统一为 2026-08-09。在线入口分别为 [DLMF 14.30](https://dlmf.nist.gov/14.30)、[DLMF 34.1](https://dlmf.nist.gov/34.1)、[DLMF 34.3](https://dlmf.nist.gov/34.3)、[MIT 8.321 讲义目录](https://ocw.mit.edu/courses/8-321-quantum-theory-i-fall-2017/pages/lecture-notes/)、[Tensor Field Networks](https://arxiv.org/abs/1802.08219)、[e3nn 论文](https://arxiv.org/abs/2207.09453)、[DeepH-E3](https://arxiv.org/abs/2210.13955)和补充档案 [MIT 8.512 第 10 讲官方 PDF](https://ocw.mit.edu/courses/8-512-theory-of-solids-ii-spring-2009/7c18b5b0b6b1036d334ec864be5dac12_MIT8_512s09_lec10_rev.pdf)。

## 3. 来源到教材的证据边界

E-FND-01/02 固定复球谐与角动量耦合的相位和正交关系，但实 \(p,d\) 轨道的顺序、归一化、主动/被动方向和数组轴顺序属于本项目显式约定。E-FND-03 支持旋转群、\(SO(3)\)/\(SU(2)\)、宇称和反幺正时间反演的基础结论，但不支持任何特定 DeepH 软件接口。E-GNN-01/02 支持表示分型和张量积等变构造的一般机制，但架构名称、旋转数据增强或某个库调用均不能单独作为数值等变证据。DH-02 只支持论文层的方法对象与 Hamiltonian 等变关系；不得由此推断当前仓库、数据集、材料、DFT 设置或软件版本已经冻结。E-SUP-01 只登记作品身份和检索 provenance，不参与公式或章节范围的直接论证。

## 4. BibTeX 键

对应键为 `dlmf1430`、`dlmf34`、`turner2017quantum321`、`thomas2018tfn`、`geiger2022e3nn`、既有 `gong2023deephe3` 和补充档案 `rudner2009solids2lec10`。来源台账位于 [source_table.csv](../../../02_source_ledger/source_table.csv)，统一表示约定位于 [stageE_representation_conventions.md](../../../03_textbook/stageE_representation_conventions.md)。
