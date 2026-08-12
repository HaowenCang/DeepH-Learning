# 第 1 章资料包：DeepH 所求解的问题

## 资料使用原则

本章只回答 DeepH 的任务定义、对象层级、计算流程、困难来源和最低验证标准，不展开 Kohn–Sham DFT、群表示论或网络层的完整推导。超出这一范围的数学与物理内容只建立接口，并指向后续章节。

章节草稿使用以下证据标签：

- `【原始资料】`：原始论文、补充材料或官方版本文档明确陈述；
- `【公式推出】`：由本章已定义公式直接推出；
- `【教学补充】`：为澄清对象和因果关系构造的解释或例子；
- `【实现推测】`：由代码结构推断、但尚未由文档或测试确认；
- `【待验证】`：资料或版本不足，不能进入定稿结论。

## 核心资料

| 资料 ID | 资料 | 本章使用范围 | 不在本章据此主张的内容 |
|---|---|---|---|
| DH-01 | [原始 DeepH 论文](https://doi.org/10.1038/s43588-022-00265-6)及[补充材料](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs43588-022-00265-6/MediaObjects/43588_2022_265_MOESM1_ESM.pdf) | 任务定义；局域 AO Hamiltonian；局域性；局域坐标；MPNN；跳过新结构 SCF 后的电子结构求解；正文第 375—376 页和补充材料第 2—4 页 | 不把论文案例精度推广到任意材料、泛函、基组或分布外结构 |
| DH-02 | [DeepH-E3 论文](https://doi.org/10.1038/s41467-023-38468-8) | 说明 Hamiltonian 矩阵不是普通旋转标量；原始局域坐标方案的负担；显式等变方法的动机 | 不在第 1 章推导 Wigner 矩阵或张量积，也不比较具体网络超参数 |
| DH-07 | [平面波到 AO 表示的论文](https://doi.org/10.1038/s43588-024-00701-9) | 说明 DeepH 标签与基组/后端之间的接口问题；平面波结果需要投影或重建到 AO 表示 | 不宣称任意平面波软件已有直接转换接口 |
| DH-10 | [DeepH-R 论文](https://doi.org/10.1103/mbhs-vlby) | 说明 AO Hamiltonian 学习的基依赖为何促使后续方法改学实空间 KS 势 | 不把 2026 年新方法写成已经完全取代 AO Hamiltonian 路线，也不推断代码状态 |
| SW-01 | [现代 DeepH-pack 论文](https://doi.org/10.1038/s41524-026-02219-2) | 当前软件生态的统一目标；Hamiltonian 到能带、DOS、波函数等下游量的工作流 | 不在本章写安装命令；不将软件可用性等同于所有方法均公开可复现 |
| SW-02 | [DeepH-dock 数据与后处理文档](https://docs.deeph-pack.com/deeph-dock/en/latest/) | 现代工作流中 DFT 接口、标准数据与后处理的角色 | 不把随时间变化的接口列表写成永久支持承诺 |

## 基础资料

| 资料 ID | 资料与固定版本 | 本章使用位置 | 证据边界 |
|---|---|---|---|
| FND-01 | Richard M. Martin, *Electronic Structure: Basic Theory and Practical Methods*, Cambridge University Press, 2004, ISBN 978-0-521-78285-2 | 第 4 章“Periodic solids and electron bands”，第 73—99 页；第 7 章“The Kohn–Sham ansatz”，第 135—151 页；第 9 章“Solving Kohn–Sham equations”，第 172—186 页；第 14 章“Localized orbitals: tight-binding”，第 272—297 页；第 15 章“Localized orbitals: full calculations”，第 298—312 页 | 支持周期体系、Kohn–Sham、SCF、局域轨道与非正交性的基础定义；不支持 DeepH 软件或性能结论 |
| FND-02 | Gene H. Golub and Charles F. Van Loan, *Matrix Computations*, 4th ed., Johns Hopkins University Press, 2013, ISBN 978-1-4214-0794-4 | 第 8.7 节“Generalized Eigenvalue Problems with Symmetry”，第 497—512 页 | 支持对称定广义本征问题的数值线性代数背景；复数厄米表述结合 FND-03 |
| FND-03 | M. Gu et al., “Generalized Hermitian Eigenvalue Problems,” in *Templates for the Solution of Algebraic Eigenvalue Problems*, SIAM, 2000, 第 109—133 页，[DOI](https://doi.org/10.1137/1.9780898719581.ch5) | 广义厄米本征问题 \(Ax=\lambda Bx\)、定矩阵束及相应数值方法 | 支持问题类别、谱性质和算法边界；不单独支持本章的一阶扰动公式，该式仍应在正文中直接推导 |
| FND-04 | Nicholas J. Higham, “Applications,” in *Functions of Matrices: Theory and Computation*, SIAM, 2008，第 35—53 页，[DOI](https://doi.org/10.1137/1.9780898717778.ch2) | 第 35 页的 \(B^{-1/2}AB^{-1/2}\) 对称正交化约化与 \(B=R^*R\) Cholesky 约化 | 支持正定重叠矩阵下从广义问题到标准厄米问题的约化；不把显式形成平方根矩阵写成数值实现的默认方案 |
| FND-05 | Anne Greenbaum, Ren-Cang Li, and Michael L. Overton, “First-Order Perturbation Theory for Eigenvalues and Eigenvectors,” *SIAM Review* 62, 2020，第 463—482 页，[DOI](https://doi.org/10.1137/19M124784X) | 第 465 页 Theorem 1：简单特征值的一阶导数 \(\lambda'=y^*A'x\) | 支持简单特征值一阶微扰的标准定理；本章 \(\delta H-E\delta S\) 形式仍标记为对 \(Hc=ESc\) 的直接推导，并显式限定可微性、简单特征值、\(S\succ0\) 与 \(S\)-归一化 |

上述版本与页码已经核定。Martin 的章节页码来自 Cambridge University Press 的 ISBN 对应目录；Golub–Van Loan 的章节页码由出版社书目信息与 ISBN 对应目录交叉核对；FND-03—05 的页码与定理位置由 SIAM 官方页面给出。

## 论断—来源对应

| 本章论断 | 证据 | 登记位置 |
|---|---|---|
| 原始 DeepH 预测给定局域 AO 表示下的 DFT Hamiltonian，而不是基组无关的精确算符 | DH-01 + 定义 | `CLM-001` |
| 显式等变方法的动机来自 Hamiltonian 轨道块的旋转协变性质 | DH-02 | `CLM-002` |
| 平面波 DFT 不能未经表示转换直接提供固定 AO Hamiltonian 标签 | DH-07 | `CLM-006` |
| DeepH-R 把学习目标改为实空间 Kohn–Sham 势 | DH-10 | `CLM-010` |
| 旧版和现代 DeepH-pack 在框架、配置和数据布局上不可混用 | SW-01/SW-02 + 旧仓库 | `CLM-011` |
| 当前文档不足以证明 VASP Hamiltonian 已有现代直接接口 | SW-02 | `CLM-012` |
| 原始 DeepH 中网络预测 \(H\)，而 \(S\) 由基函数内积得到；Fourier 变换后解广义本征问题 | DH-01 正文第 375—376 页，式 (7)—(9) | `CLM-013` |
| 原始数据划分与局域坐标定义分别见补充材料第 2 页和第 3—4 页 | DH-01 补充材料 | `CLM-014` |

## 已关闭与剩余资料缺口

已关闭：

- DH-01 正文第 375 页给出 OpenMX 3.9、PBE、赝势、轨道基和截断；第 375—376 页式 (7)—(9)给出 \(H\)、\(S\) 与广义本征问题；第 376 页给出网络训练设置。
- DH-01 补充材料第 2 页给出训练、验证和测试划分；第 3—4 页给出局域坐标、Wigner 旋转及返回 DFT 坐标的逆变换。
- FND-01—05 已固定版本、章节和页码，覆盖 Kohn–Sham、SCF、局域非正交基、广义厄米本征问题、正交化约化与简单特征值一阶微扰。广义 \(H/S\) 扰动式仍作为直接推导审计，不伪装成 FND-05 的原文公式。
- 对原始 DeepH，“绕过 SCF”的边界已经明确：网络给出 \(H\)，\(S\) 由基函数内积得到，随后仍需 Fourier 变换、广义本征求解和性质后处理。

仍未关闭：

- 应核对 DH-01 与旧版仓库在轨道排序、掩码、实/复球谐和 Fourier 相位方面是否完全一致；该项阻塞代码级章节，不阻塞第 1 章概念正文。
- 教材正文采用的完整 Bloch 和 Fourier 正反变换约定应在第 4 章统一冻结；第 1 章只保留显式标注为示例的正变换。
- 现代 DeepH-pack 对 Hamiltonian、overlap 和 density matrix 的预测或计算分工仍需按实际可获得版本核验，不能用原始 DeepH 的分工替代现代软件结论。

上述剩余缺口不阻塞第 1 章独立内容审计，但在相应软件或公式章节定稿前必须解决。
