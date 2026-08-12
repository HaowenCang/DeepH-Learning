# 论断与来源登记

本文件在 M1 文献地图阶段开始填充。每个关键论断应有唯一编号，并记录其证据边界。搜索结果摘要、第三方博客和 AI 生成文本不能单独支持关键方法结论。

## 证据状态

- `PRIMARY_EXPLICIT`：原始论文正文、补充材料或官方版本文档明确陈述。
- `DIRECT_DERIVATION`：从已经列明的定义或公式直接推出，并附推导位置。
- `PEDAGOGICAL`：为教学目的加入的解释、例子或类比，不归因于原作者。
- `IMPLEMENTATION_INFERENCE`：根据代码行为作出的实现推断，尚缺官方说明或独立测试。
- `UNVERIFIED`：尚待原始资料或实验核查，不能进入定稿结论。
- `CONFLICT`：不同原始资料、版本或代码行为之间存在冲突，需要分别陈述。

## 登记模板

### CLM-000：论断标题

- 论断：
- 适用对象与版本：
- 证据状态：`UNVERIFIED`
- 直接来源：
- 来源位置：章节、公式、页码、文件路径或提交
- 支持强度与限制：
- 独立验证：
- 影响章节或实验：

## 已核验关键论断

### CLM-001：原始 DeepH 的任务与核心机制

- 论断：原始 DeepH 学习原子结构到给定局域原子轨道基中 DFT Hamiltonian 的映射，以局域性降低问题规模，并通过局域坐标与 MPNN 处理旋转协变和环境表征。
- 适用对象与版本：2022 年论文；旧版 `mzjb/DeepH-pack`。
- 证据状态：`PRIMARY_EXPLICIT`
- 直接来源：[Nature Computational Science 论文](https://doi.org/10.1038/s43588-022-00265-6)
- 来源位置：摘要、DeepH 理论框架与神经网络架构部分。
- 支持强度与限制：支持论文方法定义；不支持将其泛化为基组无关或适用于任意 DFT 设置的模型。
- 影响章节或实验：教材第 1、21—28 章；基线标签定义。

### CLM-002：DeepH-E3 的显式等变表示

- 论断：DeepH-E3 将 Hamiltonian 的轨道分量按旋转群不可约表示组织，使用 `E(3)` 等变网络，并将框架扩展至含 SOC 的自旋—轨道 Hamiltonian。
- 适用对象与版本：2023 年论文；`Xiaoxun-Gong/DeepH-E3`。
- 证据状态：`PRIMARY_EXPLICIT`
- 直接来源：[Nature Communications 论文](https://doi.org/10.1038/s41467-023-38468-8)、[官方仓库](https://github.com/Xiaoxun-Gong/DeepH-E3)
- 来源位置：论文方法与 SOC 小节；仓库安装与使用说明。
- 支持强度与限制：不由架构名称自动保证任意预处理与数据约定均满足等变性，仍需数值旋转测试。
- 影响章节或实验：教材第 15—20、29、36 章。

### CLM-003：xDeepH 对磁结构和时间反演的扩展

- 论断：xDeepH 同时以原子结构和磁结构为输入，学习自旋—轨道 DFT Hamiltonian，并纳入 `E(3)×{I,T}` 对称要求。
- 适用对象与版本：2023 年 xDeepH 论文与仓库。
- 证据状态：`PRIMARY_EXPLICIT`
- 直接来源：[Nature Computational Science 论文](https://doi.org/10.1038/s43588-023-00424-3)、[代码仓库](https://github.com/mzjb/xDeepH)
- 来源位置：摘要、图 1 与方法定义。
- 支持强度与限制：只支持磁性分支的方法定义；不构成简单无磁基线的前置要求。
- 影响章节或实验：教材第 20、31 章。

### CLM-004：DeepH-2 的证据层级

- 论断：DeepH-2 提出 equivariant local-coordinate transformer，以边方向定义局域轴，并报告相对 DeepH-E3 更低阶的角动量张量积复杂度。
- 适用对象与版本：arXiv `2401.17015`。
- 证据状态：`PRIMARY_EXPLICIT`
- 直接来源：[DeepH-2 预印本](https://arxiv.org/abs/2401.17015)
- 来源位置：物理先验、ELCT 架构、结果与总结。
- 支持强度与限制：截至核验日，主要方法证据为预印本；未定位独立公开代码仓库。复杂度和精度比较应保留其数据、硬件和实现条件。
- 影响章节或实验：教材第 30、40 章；方法效率比较。

### CLM-005：DeepH-hybrid 的非局域标签边界

- 论断：DeepH-hybrid 学习杂化泛函的广义 Kohn–Sham Hamiltonian；非局域精确交换使不重叠局域轨道之间也可能出现非零矩阵元，因而需要相对半局域 DFT 更长程的处理。
- 适用对象与版本：2024 年论文；附加代码仓库。
- 证据状态：`PRIMARY_EXPLICIT`
- 直接来源：[Nature Communications 论文](https://doi.org/10.1038/s41467-024-53028-4)、[附加代码](https://github.com/aaaashanghai/DeepH-hybrid)
- 来源位置：方法、讨论和代码可得性说明。
- 支持强度与限制：仓库明确说明只提供新增代码，需与 DeepH-E3 组合；不能视为独立完整发行版。
- 影响章节或实验：教材第 32、40 章。

### CLM-006：HPRO 是表示桥接而不是新预测网络

- 论断：HPRO/对应论文通过波函数投影或实空间重建，将平面波 DFT 结果转换为原子轨道 Hamiltonian，解决 DeepH 原先局限于 AO 后端的数据接口问题。
- 适用对象与版本：2024 年论文；HPRO 当前发布需另行冻结版本。
- 证据状态：`PRIMARY_EXPLICIT`
- 直接来源：[Nature Computational Science 论文](https://doi.org/10.1038/s43588-024-00701-9)、[HPRO 仓库](https://github.com/Xiaoxun-Gong/HPRO)
- 来源位置：论文摘要和方法；软件项目说明。
- 支持强度与限制：转换后的矩阵仍依赖所选择的 AO 表示；不能据此断言任意 VASP 输出都已存在可用接口。
- 影响章节或实验：教材第 8、24、32 章；平面波实践路线。

### CLM-007：DeepH-DFPT 依赖自动微分与响应对象

- 论断：Deep-learning DFPT 使用神经网络与自动微分计算扰动响应，并以电子—声子耦合等性质作为示例。
- 适用对象与版本：2024 年 PRL 论文。
- 证据状态：`PRIMARY_EXPLICIT`
- 直接来源：[Physical Review Letters 论文](https://doi.org/10.1103/PhysRevLett.132.096401)
- 来源位置：摘要、工作流与方法。
- 支持强度与限制：当前未定位独立官方代码仓库；复现可得性保持 `UNVERIFIED`。
- 影响章节或实验：教材第 32、37 章；高级响应分支。

### CLM-008：DeepH-UMM 的“通用”具有数据边界

- 论断：DeepH-UMM 通过大型材料数据库和改进架构建立多元素、多结构的 Hamiltonian 模型，并展示微调到特定材料任务的路径。
- 适用对象与版本：2024 年 Science Bulletin 论文。
- 证据状态：`PRIMARY_EXPLICIT`
- 直接来源：[Science Bulletin 论文](https://doi.org/10.1016/j.scib.2024.06.011)
- 来源位置：摘要、方法和实验。
- 支持强度与限制：由数据范围直接可知，“通用”不表示超出元素、轨道基组和结构覆盖后无条件可靠；代码与权重可得性尚未核实。
- 影响章节或实验：教材第 33—35 章。

### CLM-009：DeepH-Zero 对应 neural-network DFT 论文

- 论断：官方 DeepH-pack 资料将 PRL 133, 076401 列为 DeepH-Zero；论文方法把可微变分 DFT 的能量泛函作为网络优化信号，并实现 AI2DFT。
- 适用对象与版本：2024 年论文和 2026 年官方软件资料。
- 证据状态：`PRIMARY_EXPLICIT`
- 直接来源：[PRL 论文](https://doi.org/10.1103/PhysRevLett.133.076401)、[DeepH-pack 官方软件页面](https://pypi.org/project/deepx-pack/)
- 来源位置：论文方法；软件页面 Publications 列表。
- 支持强度与限制：论文正文主要称 neural-network DFT；“零训练数据”不应被解释为零初始化、零 DFT 计算或对任意体系的无条件保证。
- 影响章节或实验：教材第 33、41 章。

### CLM-010：DeepH-R 改变学习目标

- 论断：DeepH-R 学习旋转不变、基组无关的实空间 Kohn–Sham 势，再由该势构造 Hamiltonian，并把这一表示用于改善一般化与 DFPT 路径。
- 适用对象与版本：PRL 137, 046401，2026-07-20 发表。
- 证据状态：`PRIMARY_EXPLICIT`
- 直接来源：[Physical Review Letters 论文](https://doi.org/10.1103/mbhs-vlby)
- 来源位置：摘要与论文方法。
- 支持强度与限制：截至核验日未定位代码链接；也没有证据表明现代 DeepH-pack 已公开实现该方法。
- 影响章节或实验：教材第 24、32、33、41 章；后续目录应新增实空间势专题。

### CLM-011：旧版与现代 DeepH-pack 不兼容混用

- 论断：旧版 `mzjb/DeepH-pack` 要求 Python 3.9、PyTorch 1.9.1、PyG 1.7.2、e3nn 0.3.5 和 INI 配置；现代 DeepH-pack 以 JAX/Flax 重构，官方页面列出 Python 3.13、TOML/新命令和新的 `DeepH` 数据布局。
- 适用对象与版本：旧版仓库当前 README；现代 `deepx-pack 1.0.6.post3` 元数据与最新文档。
- 证据状态：`PRIMARY_EXPLICIT`
- 直接来源：[旧版仓库](https://github.com/mzjb/DeepH-pack)、[现代包页面](https://pypi.org/project/deepx-pack/)、[现代数据准备文档](https://docs.deeph-pack.com/deeph-pack/en/latest/core_workflows/data_preparation.html)
- 来源位置：旧版 Requirements/Usage；现代包 Core Features/Installation；现代数据格式说明。
- 支持强度与限制：公开网页会继续变化，实践时必须冻结发布和下载物；当前记录只适用于 2026-08-03 的状态。
- 影响章节或实验：所有代码章节与阶段 F。

### CLM-012：现代接口对 DFT 后端有明确版本和模式边界

- 论断：现代 DeepH-dock 文档列出 OpenMX、SIESTA、ABACUS、FHI-aims、HONPAS 等接口；ABACUS 转换当前针对 3.10 LTS 且只实现 AO 模式。文档当前列表不足以证明 VASP Hamiltonian 输出可直接转换。
- 适用对象与版本：2026-08-03 的官方 DeepH-pack/DeepH-dock 文档。
- 证据状态：`PRIMARY_EXPLICIT`（已列接口与 ABACUS 边界）；`DIRECT_DERIVATION`（不能据此宣称 VASP 已受支持）。
- 直接来源：[数据准备文档](https://docs.deeph-pack.com/deeph-pack/en/latest/core_workflows/data_preparation.html)、[DeepH-dock 文档](https://docs.deeph-pack.com/deeph-dock/en/latest/)
- 来源位置：DFT 接口列表与 ABACUS 小节。
- 支持强度与限制：接口可能更新；选择实践后端前应按当日文档和最小转换样例复核。
- 影响章节或实验：未决事项中的 DFT 后端选择；阶段 F 数据方案。

### CLM-013：原始 DeepH 的推理后计算边界

- 论断：在原始 DeepH 工作流中，网络预测给定非正交原子轨道基下的 Hamiltonian 矩阵；重叠矩阵由基函数内积得到而不由网络学习。对 \(H\) 和 \(S\) 作 Fourier 变换后，仍需解 \(H(\mathbf k)v=E S(\mathbf k)v\) 才能得到能带和本征态。
- 适用对象与版本：2022 年原始 DeepH 论文；不能自动推广到现代 DeepH-pack 的全部可选任务。
- 证据状态：`PRIMARY_EXPLICIT`
- 直接来源：[Nature Computational Science 论文](https://doi.org/10.1038/s43588-022-00265-6)
- 来源位置：正文第 375—376 页，“Physical properties derived from the DFT Hamiltonian”，式 (7)—(9)。
- 支持强度与限制：足以限定原始方法“绕过 SCF”不等于省略重叠矩阵、Fourier 变换、对角化或物理后处理；电子占据和具体性质仍需各自输入与公式。
- 影响章节或实验：教材第 1、4、12、28、37 章；原始 DeepH 复现验收。

### CLM-014：原始 DeepH 的数据划分与局域坐标位置

- 论断：原始 DeepH 补充材料明确列出各示例数据集的训练、验证和测试数量，并给出逐键定义局域坐标、将 Hamiltonian 块旋转到局域基以及预测后旋回 DFT 坐标的公式。
- 适用对象与版本：2022 年论文补充材料。
- 证据状态：`PRIMARY_EXPLICIT`
- 直接来源：[Springer Nature 补充材料](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs43588-022-00265-6/MediaObjects/43588_2022_265_MOESM1_ESM.pdf)
- 来源位置：补充材料第 2 页，Supplementary Section 2 与 Table 2；第 3—4 页，Supplementary Sections 3.1—3.3 与式 (1)—(10)。
- 支持强度与限制：支持原论文案例的划分和局域坐标机制；时间相邻 AIMD 帧的划分仍应在复现审计中单独检查相关性与潜在泄漏。
- 影响章节或实验：教材第 1、23、24、35、36 章；数据与等变性测试。
