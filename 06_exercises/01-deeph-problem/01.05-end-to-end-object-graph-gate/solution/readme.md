# 01.05 端到端对象图综合材料题参考解答

本参考解答给出最低完整对象图，不是唯一允许的排版。建议自学时先完成 problem 再核对本文件，但 D-010 不要求学习者提交闭卷版本；M3-08 审查本答案是否完整、准确、可定位且可与代码/来源相互验证。

## 训练链参考图

\[
\begin{aligned}
&\text{结构} + \text{固定 DFT 设置}\\
&\quad\longrightarrow \text{SCF/电子结构计算}\\
&\quad\longrightarrow \text{波函数、密度及必要辅助对象}\\
&\quad\longrightarrow \text{给定 AO 基中的 }H\text{ 标签与相容 }S\\
&\quad\longrightarrow \text{轨道/相位/局域坐标/图预处理}\\
&\quad\longrightarrow \text{训练样本}\\
&\quad\longrightarrow \text{模型参数}.
\end{aligned}
\]

这里的 \(H\) 是固定电子结构设置和固定表示下的监督矩阵，不是基组无关算符；\(S\) 是否为网络目标取决于具体方法和版本，不能统一假定。HPRO 可位于“平面波结果到 AO \(H/S\) 标签”的表示桥接箭头。DeepH-dock 可位于数据标准化、DFT 接口或后处理箭头，但不是训练映射本身。

## 新结构推理链参考图

\[
\begin{aligned}
&\text{新结构}\\
&\quad\longrightarrow \text{周期原子图与几何特征}\\
&\quad\longrightarrow \widehat H_{ij}(\mathbf R)\text{ 局域块}\\
&\quad\longrightarrow \text{旋回统一坐标并按轨道/平移组装}\\
&\quad\longrightarrow \widehat H(\mathbf k),\ S(\mathbf k)\\
&\quad\longrightarrow \widehat H(\mathbf k)c_{n\mathbf k}
=E_{n\mathbf k}S(\mathbf k)c_{n\mathbf k}\\
&\quad\longrightarrow \text{占据与进一步性质后处理}.
\end{aligned}
\]

原始 DeepH 主要替代新结构上为取得目标 Hamiltonian 标签而执行的 SCF 路径。它不消除训练集 DFT 生成、电子结构理论误差、\(S\) 的获得、矩阵组装、Fourier 变换、广义本征求解、占据或进一步性质计算。

## 方法位置

| 方法 | 改变或承担的位置 | 不应写成 |
|---|---|---|
| 原始 DeepH | 结构/图到固定 AO Hamiltonian 块的学习映射 | 直接替代全部 DFT 与后处理 |
| HPRO | 平面波电子结构结果到选定 AO \(H/S\) 的标签表示桥接 | 新结构 Hamiltonian 预测 GNN |
| DeepH-dock | DFT 接口、标准数据、overlap/对角化/波函数及转换等后处理平台 | Hamiltonian 学习网络本身 |
| DeePTB | 环境依赖 tight-binding 参数或谱目标；语义可不同于逐元素 AO 标签 | 与原始 DeepH 天然具有同一监督对象 |
| DeepH-R | 把学习对象改为实空间 Kohn–Sham 势，再构造目标基矩阵 | 消除整个计算链的离散与基依赖 |

## 最低箭头审计示例

| ID | 输入与输出 | 固定约定/假设 | 可能误差 | 可执行验证 |
|---|---|---|---|---|
| T1 | 结构与 DFT 设置 → SCF 结果 | 泛函、赝势、基、\(k\) 点、自旋、阈值固定 | 理论近似、基组和采样未收敛 | 基组/\(k\) 点/阈值收敛与元数据核对 |
| T2 | SCF 结果 → AO \(H/S\) 标签 | 投影窗、轨道排序、相位和单位固定 | 投影、截断、索引或单位错误 | 重构谱、Hermiticity、维数和单位检查 |
| T3 | 标签与结构 → 图训练样本 | 截断、局域坐标和数据划分固定 | 周期镜像遗漏、坐标不连续、数据泄漏 | 邻居/平移检查、旋转测试、结构组划分审计 |
| I1 | 新结构 → 周期图 | 晶胞、坐标和截断约定固定 | 镜像或邻居错误 | 周期平移与重复边检查 |
| I2 | 周期图 → \(\widehat H\) 局域块 | 模型版本、轨道约定和输出解码固定 | 分布外误差、协变残差、块尺寸错误 | 旋转/置换测试、块模式和不确定性检查 |
| I3 | 局域块 → 统一坐标实空间矩阵 | 主动/被动旋转、相位和索引固定 | 未旋回、漏块、共轭配对错误 | 随机旋转残差、\(H(R)^\dagger=H(-R)\) |
| I4 | \(H(R),S(R)\) → \(H(k),S(k)\) | Fourier 符号和晶格平移集合固定 | 相位、截断或混叠错误 | 正反变换、\(k\) 空间 Hermiticity |
| I5 | \(H(k),S(k)\) → 本征量 | \(S\succ0\)、求解器和简并处理固定 | 病态 \(S\)、残差或能带匹配错误 | 最小本征值/条件数、残差、\(S\)-正交与子空间检查 |
| I6 | 本征量 → 物理量 | 费米能、占据、温度、网格及算符定义固定 | 占据、积分或导数误差 | 粒子数、网格收敛、守恒量与独立后处理比较 |

## 可选修正记录应达到的粒度

若学习者选择保存修正记录，每项修正应指出具体节点或箭头，例如：“第一版把 \(\widehat H\) 标为算符；修正为给定 AO 基中的模型预测矩阵，因为网络输出与轨道排序、相位和单位共同定义；新增一致基变换后的谱核验。”这段示例用于提高自学可诊断性，不构成 M3 状态所需的个人作答证据。
