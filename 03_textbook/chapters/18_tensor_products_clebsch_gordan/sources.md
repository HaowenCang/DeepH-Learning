# 第 18 章来源与论断边界

## 直接来源

| 来源 ID | 本章用途 | 本地证据 |
|---|---|---|
| E-FND-02 | CG 与 Wigner \(3j\) 的关系、选择定则、对称性和正交关系 | [DLMF 34.1/34.3](../../../01_sources/documentation/stageE/README.md) |
| E-FND-03 | 角动量加法与 \(SO(3)\)/\(SU(2)\) 接口 | [MIT 8.321 第 21 讲](../../../01_sources/documentation/stageE/mit_8_321_lecture21_su2_addition.pdf) |
| E-GNN-01 | CG 张量积作为表示型特征耦合机制 | [TFN 快照](../../../01_sources/documentation/stageE/thomas_2018_tensor_field_networks.pdf) |
| E-GNN-02 | tensor product paths、宇称和 multiplicity | [e3nn 论文快照](../../../01_sources/documentation/stageE/geiger_2022_e3nn.pdf) |

## 论断边界

本章采用 [统一表示约定](../../stageE_representation_conventions.md) 的 Condon--Shortley 相位和 \(m,M\) 递增顺序。DLMF 支持系数关系和正交性质，但代码中的轴布局、通道 multiplicity、归一化和路径枚举仍须显式冻结。只满足维数相加或选择定则不足以证明 intertwiner 正确，必须数值检查完整群作用恒等式。另一方面，固定 \(L\) 输出通道的整体相位是合法基自由；项目以 DLMF 规范表和低阶锚点约束序列化一致性，但不得把整通道统一翻相位误写为等变性破坏。

## 来源—论断定位

| 论断对象 | 直接来源 | 教材定位 | 推导/题解定位 | 证据边界 |
|---|---|---|---|---|
| CG--\(3j\) 关系与 Condon--Shortley 相位 | E-FND-02，DLMF 34.1 | 18.2.3—18.2.5 | D-E04 第 5 节；A18-02/A18-06 | 支持规范系数关系；不规定代码轴布局 |
| 三角条件、\(M=m_1+m_2\)、交换与正交/完整性 | E-FND-02，DLMF 34.3 | 18.2.1—18.3.3 | D-E04 第 4、6 节；A18-01—A18-05 | 选择定则不是完整等变证明 |
| 角动量加法、最高权重与降算符低阶构造 | E-FND-03，第 21 讲 | 18.3.4、18.4、18.5.2 | D-E04 第 7—8 节；A18-03/A18-07/A18-08 | 包含 \(1\otimes2\) 三个最高行锚点；只支持一般 \(SO(3)\)/\(SU(2)\) 结构，不支持具体软件 API |
| CG 张量积等变层、类型和路径 | E-GNN-01/E-GNN-02 | 18.5—18.8 | D-E04 第 10—12、14 节；A18-08—A18-10 | 支持一般机制；不证明本项目未来实现或 DeepH 版本兼容 |
| D-E04/T-E05 规范表与 intertwiner 双门控 | 上述直接来源与项目冻结约定 | 18.3、18.4.3、18.7 | D-E04 第 8.3、9、14—15 节；A18-06—A18-08 | 整通道相位自由必须与局部相位错误分开；STF 交叉固定为 \(z^{(2)}=K_2q\)，不得拟合 |
| D-E06/T-E07/T-E08/T-E12 消息与宇称门控子对象 | E-GNN-01/E-GNN-02 与阶段 D 身份合同 | 18.5.1、18.6、18.8 | D-E04 第 10—12、14.2 节；A18-09/A18-10 | 类型保持门值必须为 \((0,+1)\)；伪标量非线性须有确定奇偶性；正式代码证据见 [Stage E 代码说明](../../../05_code_exercises/stageE_synthetic_equivariance/README.md) 与 [M7-09 定点复核](../../../08_audits/M7_stageE_code_blocking_reaudit.md) |
| D-E09/T-E10 局部成本与全扫描边界 | 项目教学构造 | 18.5.4、18.8.3 | D-E04 第 13、14.3 节；A18-10 | 9 次乘积形成、18 个非零投影项/零初始化 MAC 与 9 次真实累加仅为单副本对 \(1\otimes1\) CG 子预算，不是端到端 FLOP |

## 复现与授权边界

本章例题和推导使用解析系数、固定低阶矩阵与合成旋转，不需要新增 Python 依赖。M7-09 已在固定 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0 下实现 T-E05/T-E07/T-E08/T-E10/T-E12；代码与独立放行证据分别见 [Stage E 代码说明](../../../05_code_exercises/stageE_synthetic_equivariance/README.md) 和 [`M7_stageE_code_blocking_reaudit.md`](../../../08_audits/M7_stageE_code_blocking_reaudit.md)。本章不得被解释为安装 e3nn/DeepH、下载训练数据、生成 DFT 标签或选择材料、DFT/数据后端和实践软件版本的授权。
