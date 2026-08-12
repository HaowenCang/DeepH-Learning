# M2 资料缺口关闭记录

## 结论

第 1 章送交独立内容审计所需的基础资料和原始 DeepH 页码已经就绪。四项原缺口中，电子结构教材、广义厄米本征问题、正交化约化、一阶微扰定理和 DH-01 正文/补充材料定位已经关闭；现代 DeepH-pack 的矩阵对象分工仍保持未核验，但不阻塞第 1 章概念审计。

## 基础资料核定

| ID | 固定资料 | 已核对位置 | 用途 |
|---|---|---|---|
| FND-01 | Martin, *Electronic Structure*, Cambridge University Press, 2004 | 第 4 章，第 73—99 页；第 7 章，第 135—151 页；第 9 章，第 172—186 页；第 14 章，第 272—297 页；第 15 章，第 298—312 页 | 周期固体、Kohn–Sham、SCF、局域轨道、非正交性 |
| FND-02 | Golub and Van Loan, *Matrix Computations*, 4th ed., 2013 | 第 8.7 节，第 497—512 页 | 对称定广义本征问题的数值结构 |
| FND-03 | Gu et al., “Generalized Hermitian Eigenvalue Problems,” SIAM, 2000 | 第 109—133 页 | 复数厄米定矩阵束及算法边界 |
| FND-04 | Higham, “Applications,” in *Functions of Matrices*, SIAM, 2008 | 第 35—53 页；相关约化式见第 35 页 | \(B^{-1/2}\) 对称正交化与 Cholesky 约化 |
| FND-05 | Greenbaum, Li, and Overton, “First-Order Perturbation Theory for Eigenvalues and Eigenvectors,” *SIAM Review*, 2020 | 第 463—482 页；Theorem 1 见第 465 页 | 简单特征值的一阶微扰定理；广义 \(H/S\) 形式据此作直接推导 |

书目信息和章节页码分别由出版社页面、ISBN 对应目录和 SIAM 官方页面交叉核对。目录只证明章节范围；具体公式进入正文时仍应回到相应正文核对定义和条件。FND-05 原文定理针对标准矩阵本征问题；本章的 \(c^\dagger(\delta H-E\delta S)c\) 形式必须继续标记为对广义本征方程的直接微分结果。

## DH-01 页码与公式定位

| 位置 | 已核对内容 | 可支持的第 1 章结论 |
|---|---|---|
| 正文第 375 页，Methods / Dataset preparation | VASP 用于 AIMD 结构生成；OpenMX 3.9、PBE、赝势、原子轨道与截断用于 Hamiltonian 标签 | 标签由固定电子结构设置定义，不能视为基组无关真值 |
| 正文第 375—376 页，式 (7)—(9) | 非正交 AO 下的 \(H\)、\(S\)，重叠矩阵由基函数内积得到，Fourier 后解广义本征问题 | “跳过 SCF”后仍需 \(S\)、Fourier 变换、广义本征求解和性质后处理 |
| 正文第 376 页，Details on training | MPNN 层数、截断、特征、优化器与分块/整体输出方式 | 实现细节只适用于原始版本，不能移植为现代软件默认值 |
| 补充材料第 2 页，Section 2 / Table 2 | 各数据集的训练、验证和测试数量与抽帧规则 | 数据划分需要按结构和时间相关性审计，不能只报告样本数 |
| 补充材料第 3—4 页，Sections 3.1—3.3，式 (1)—(10) | 局域坐标定义、Wigner 旋转、返回 DFT 坐标的逆变换及 LCMP 动机 | 原始方案学习局域坐标中的不变量表示，但最终矩阵必须旋回共同 DFT 坐标后组装 |

## 未关闭项目

- 现代 DeepH-pack 对 Hamiltonian、overlap 和 density matrix 的实际分工需要取得具体发布物后核验。
- 旧版仓库的轨道排序、掩码、球谐与 Fourier 约定需要在代码章节逐文件审计。

这两项不得被原始论文的式 (7)—(9)替代，但不会改变第 1 章对对象层级和原始计算链的概念说明。
