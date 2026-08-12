# M5 阶段 C：DFT 与标签语义材料建设工作包

## 1. 目标与授权边界

M5 建设第 5—8、10 章，使读者能够从多电子问题与平均场近似出发，说明 Hohenberg–Kohn 定理和 Kohn–Sham 构造的准确作用边界，推导 Kohn–Sham 方程的主要变分步骤，把 SCF 写成可分析的固定点迭代，并区分理论近似、赝势/全电子处理、离散基、采样、电子温度、收敛阈值和表示转换对 Hamiltonian 标签语义的不同影响。

本阶段只使用权威来源、后端无关推导、教学级一维或有限维 SCF 模型和合成收敛数据。不安装或运行真实 DFT/DeepH 后端，不使用真实材料结构，不下载正式训练数据，不生成正式 DFT 标签，也不隐含选择泛函、赝势族、局域基、平面波后端、软件版本或首个材料体系。具体实践对象统一保留到 M8 决策；M8 冻结后，M9 外部动作前仍须明确执行授权。

## 2. 章节范围与依赖

| 章节 | 主题 | 关键依赖 | 本阶段必须形成的能力 |
|---|---|---|---|
| 第 5 章 | 多电子问题与平均场 | 阶段 B 态、算符与矩阵表示 | 区分多体波函数、密度、密度矩阵、Slater determinant、Hartree/Hartree–Fock/KS 平均场对象及 Born–Oppenheimer 边界 |
| 第 6 章 | Kohn–Sham DFT | 第 5 章；变分法 | 陈述 HK 定理边界，推导 KS 有效势和方程，区分精确形式与近似 \(E_{xc}\) |
| 第 7 章 | SCF 算法 | 第 6 章；数值固定点 | 建立密度—势—Hamiltonian—本征态—新密度依赖图，分析混合、Jacobian、振荡、阈值误判和成本 |
| 第 8 章 | 平面波、局域轨道、赝势与基组误差 | 阶段 B；第 6、7 章 | 区分全电子/赝势、平面波/局域基、\(k\) 采样、电子温度和投影/重建；定义标签表示语义 |
| 第 10 章 | 电子近视性、局域性与稀疏性 | 第 5—8 章；阶段 B 实空间矩阵 | 说明近视性的条件与限制，区分密度、密度矩阵和 Hamiltonian 块的局域性，建立可验证截断/稀疏误差 |

依赖顺序为第 5 章 \(\rightarrow\) 第 6 章 \(\rightarrow\) 第 7 章；第 8 章依赖第 6、7 章和阶段 B；第 10 章依赖第 5—8 章。M5 不使用任何后端专用输出作为完成条件。

## 3. 任务分解

| ID | 任务 | 状态 | 退出条件 |
|---|---|---|---|
| M5-01 | 冻结工作包、权威来源、来源边界和五章三级提纲 | `COMPLETED` | `M5_stageC_work_package_blocking_reaudit.md` 判定 M5-WP-B01—B04 全部关闭、新增 `BLOCKING=0`，允许启动 M5-02 |
| M5-02 | 第 5 章正文、例题、推导与题解 | `COMPLETED` | 独立初审三项阻塞及一项非阻塞经 `M5_chapter5_blocking_reaudit.md` 全部关闭，新增 `BLOCKING=0` |
| M5-03 | 第 6 章正文、例题、推导与题解 | `COMPLETED` | `M5_chapter6_B03_second_reaudit.md` 关闭最后 B03；B01—B05 全部关闭，新增及剩余 `BLOCKING=0` |
| M5-04 | 第 7 章正文、例题、推导与题解 | `COMPLETED` | `M5_chapter7_blocking_reaudit.md` 关闭唯一阻塞 M5-C7-B01；新增及剩余 `BLOCKING=0` |
| M5-05 | 第 8 章正文、例题、推导与题解 | `COMPLETED` | `M5_chapter8_blocking_reaudit.md` 关闭 M5-C8-B01 与 N01/N02；新增及剩余 `BLOCKING=0` |
| M5-06 | 第 10 章正文、例题、推导与题解 | `COMPLETED` | `M5_chapter10_independent_content_audit.md` 判定 `BLOCKING=0`；N01—N03 经 `M5_chapter10_nonblocking_reaudit.md` 全部关闭 |
| M5-07 | 阶段 C 解析推导包 | `COMPLETED` | 独立初审 `BLOCKING=0`；N01/N02 经 `M5_stageC_derivation_package_nonblocking_reaudit.md` 全部关闭，新增及剩余问题为 0 |
| M5-08 | 教学 SCF、收敛实验、测试与失败样例 | `COMPLETED` | 原审计员定点复核关闭 M5-CODE-B01；67/67 删除、47/47 对抗变异、9 项 unittest 与双 CLI 均通过，新增及剩余问题为 0 |
| M5-09 | 自学导航、标签模板与综合练习 | `COMPLETED` | 原审计员定点复核关闭 B01—B03；43/43 Pandoc、MathML、链接、控制字符、C-C07/C-C08 与代码回归均通过，新增及剩余问题为 0 |
| M5-10 | 阶段 C 正式独立材料总审计 | `COMPLETED` | `M5_stageC_final_blocking_reaudit.md` 判定 B01/N01/N02 全部 `CLOSED`，新增及剩余问题均为 0，明确允许 M5 完成与启动 M6 |

## 4. 来源体系与证据边界

| ID | 来源 | 固定用途 | 禁止外推 |
|---|---|---|---|
| FND-01 | R. M. Martin, *Electronic Structure*, 2004，第 3、5—9、11—15 章 | 多体背景、DFT、KS、SCF、赝势、平面波与局域轨道教材主线 | 目录快照不替代正文公式核查；不支持现代软件接口 |
| C-FND-02 | Hohenberg and Kohn, Phys. Rev. 136, B864 (1964), DOI `10.1103/PhysRev.136.B864` | 基态密度泛函与变分原理的原始边界 | 不提供现成精确近似泛函，不直接给出 KS 轨道算法 |
| C-FND-03 | Kohn and Sham, Phys. Rev. 140, A1133 (1965), DOI `10.1103/PhysRev.140.A1133` | 非相互作用参考体系、KS 方程与交换相关分解 | KS 轨道本征值不普遍等于全部多体激发能 |
| C-FND-04 | Mermin, Phys. Rev. 137, A1441 (1965), DOI `10.1103/PhysRev.137.A1441` | 有限温度密度泛函的理论边界 | 计算中的 smearing 参数不自动等同于目标物理温度 |
| C-FND-05 | Levy, PNAS 76, 6062—6065 (1979), DOI `10.1073/pnas.76.12.6062` | 在产生给定 \(N\)-representable 密度的反对称波函数上进行纯态 constrained search | 不等同于 HK 1964 的逐式代数推论；不自动给出系综凸扩展、下半连续闭包或处处可微性 |
| C-FND-06 | Lieb, Int. J. Quantum Chem. 24, 243—277 (1983), DOI `10.1002/qua.560240302` | Coulomb 体系密度泛函的函数空间、变分与凸分析框架 | 不应把下确界写成任意密度上必然由某波函数取得的最小值；使用时须声明密度域与拓扑条件 |
| C-NUM-01 | Woods, Payne, Hasnip, J. Phys.: Condens. Matter 31, 453001 (2019), DOI `10.1088/1361-648X/ab31c0` | SCF 非线性固定点、混合、病态与性能评估框架 | 不把某一混合器声明为所有体系最优 |
| C-NUM-02 | Payne et al., Rev. Mod. Phys. 64, 1045 (1992), DOI `10.1103/RevModPhys.64.1045` | 平面波赝势总能方法、迭代求解和数值成本 | 历史算法不等同于任一现代后端默认实现 |
| C-NUM-03 | Hamann, Schlüter, Chiang, Phys. Rev. Lett. 43, 1494 (1979), DOI `10.1103/PhysRevLett.43.1494` | norm-conserving 赝势的原始条件与 transferability 语境 | 不代表全部赝势/PAW 类型或具体元素文件质量 |
| C-LOC-01 | Prodan and Kohn, PNAS 102, 11635 (2005), DOI `10.1073/pnas.0505436102` | 电子近视性的定义、局部扰动与条件依赖 | 不推出任意金属/零温/长程相互作用下统一指数衰减 |
| DH-01 | 原始 DeepH 论文第 367—376 页 | 特定 DFT 设置下 Hamiltonian 标签与跳过新结构 SCF 的边界 | 不使标签超越其 DFT 理论、数值与表示层级 |
| DH-07 | HPRO 方法来源与现有台账 CLM-006 | 平面波结果到选定 AO \(H/S\) 的投影/重建原则 | 不声明 M8 前已有某后端/版本的可用转换器 |

原始论文明确陈述的定理、定义或算法对象标记为 `PRIMARY_EXPLICIT`；由这些定义逐步推出的教材公式标记为 `DIRECT_DERIVATION`；一维 SCF、有限矩阵、网格/采样和稀疏故障模型标记为 `PEDAGOGICAL`。Levy constrained search 与 Lieb 形式化属于各自来源中的 `PRIMARY_EXPLICIT`，不得归入从 HK 1964 直接代数推出的 `DIRECT_DERIVATION`。任何版本相关接口保留为 `PENDING_IMPLEMENTATION_CHECK`，M5 不以其完成为门槛。

## 5. 固定产物路径

| 类型 | 路径 |
|---|---|
| 正文/资料/提纲 | `03_textbook/chapters/05_many_electron_mean_field/`、`06_kohn_sham_dft/`、`07_scf_algorithms/`、`08_basis_pseudopotential_errors/`、`10_nearsightedness_locality_sparsity/` |
| 推导 | `04_derivations/stageC/05_many_electron_mean_field.md`、`06_kohn_sham_variation.md`、`07_scf_fixed_point.md`、`08_representation_and_label_error.md`、`10_nearsightedness_sparsity.md` |
| 练习与解答 | `06_exercises/03-stageC/` 下按五章和 `comprehensive` 分目录，每单元含 `problem/readme.md` 与 `solution/readme.md` |
| 代码与测试 | `05_code_exercises/stageC_teaching_scf/teaching_scf.py`、`run_experiments.py`、`test_teaching_scf.py`、`requirements.txt`、`README.md` |
| 自学导航 | `03_textbook/chapters/stageC_self_study_guide.md` |
| 标签模板 | `03_textbook/stageC_label_semantics_template.md` |

固定 Python 沿用 3.12.13、NumPy 2.3.5、SciPy 1.18.0；若需要新增用户态 Python 依赖，必须精确固定版本并在代码 README 记录同一解释器的复现命令。Windows/PowerShell 的规范复现入口冻结如下；其他机器可以替换 `$py` 路径，但不得改变 Python 小版本和依赖版本：

```powershell
$py='C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -c "import sys; assert sys.version_info[:3] == (3, 12, 13)"
& $py -m pip install --requirement 05_code_exercises/stageC_teaching_scf/requirements.txt
& $py -c "import numpy, scipy; assert numpy.__version__ == '2.3.5'; assert scipy.__version__ == '1.18.0'"
& $py -m unittest discover -s 05_code_exercises/stageC_teaching_scf -p 'test_*.py' -v
& $py 05_code_exercises/stageC_teaching_scf/run_experiments.py --format json --seed 20260805 --model-size 12 --grid-size 64
& $py 05_code_exercises/stageC_teaching_scf/run_experiments.py --format json --seed 20260806 --model-size 16 --grid-size 48
```

两次 JSON 命令都必须以退出码 0 结束，且分别报告 T-C01—T-C10 的正例与被强制捕获的预期失败。`requirements.txt` 必须使用精确 `==` 固定；安装任何新增用户态依赖后，README 还须登记实际安装命令、版本断言和 `pip check` 结果。

## 6. 解析推导门控

| ID | 推导 | 必须声明的条件与失败边界 |
|---|---|---|
| D-C01 | Born–Oppenheimer 分离与固定核电子问题 | 质量比/绝热近似；非绝热耦合不被静默删除；M5 不做核运动实践 |
| D-C02 | Slater determinant、密度与一体密度矩阵 | 反对称性、占据与自旋约定；平均场不等于消除关联 |
| D-C03 | HK 变分结构、Levy constrained search 与 Lieb 形式化接口 | 分开说明 HK 的外势—基态密度与变分结论、Levy 在给定纯态 \(N\)-representable 密度上的波函数受限搜索，以及使用 Lieb 框架时的函数空间、系综/凸扩展与下半连续边界；严格区分 \(v\)-representable 与 \(N\)-representable、纯态与系综、minimum 与 infimum、唯一性与简并；不把后两者写成 HK 1964 的直接推导，也不把定理写成已知可计算精确泛函 |
| D-C04 | KS 能量泛函到有效单粒子方程 | 原子单位、正交约束、Hartree 与 \(E_{xc}\) 变分导数、占据和边界条件 |
| D-C05 | SCF 固定点、线性混合与局部稳定性 | \(n_{m+1}=n_m+\alpha(F[n_m]-n_m)\)；Jacobian 谱半径只给局部结论；残差口径明确 |
| D-C06 | KS 方程离散到 \(Hc=ESc\) | 平面波时 \(S=I\) 的条件；局域非正交基保留 \(S\)；形状、单位和索引完整 |
| D-C07 | 离散/投影/重建误差到标签语义 | 固定表示和投影映射；能带相近不自动保证矩阵逐元素同义 |
| D-C08 | 近视性、密度矩阵衰减与稀疏截断 | 绝缘体/金属、温度、维数和谱隙边界；局部量近视不等于任意矩阵元素统一指数衰减 |

## 7. 自动测试与数值容差

阶段 C 使用合成、后端无关模型。计算统一采用 `float64`/`complex128`；向量默认用 Euclidean 范数，矩阵默认用 Frobenius 范数，例外处必须显式写出；随机过程用 `numpy.random.default_rng(seed)`。相对误差的分母均为相应参考范数与 \(10^{-15}\) 的较大者。每项测试必须在 JSON 中输出模型参数、实际指标、阈值、正例断言和预期失败的故障注入；任一预期失败未被捕获时，测试与 CLI 均须非零退出。

| ID | 冻结合成模型与指标 | 正例判据 | 故障注入与强制失败判据 |
|---|---|---|---|
| T-C01 | \(F(x)=Jx+b\)，\(J=\operatorname{diag}(0.2,0.5,-0.4)\)，\(b=(0.3,-0.2,0.1)^T\)，\(x_0=0\)，\(x_*=(I-J)^{-1}b\)；迭代 \(x_{m+1}=x_m+\alpha(F(x_m)-x_m)\)。收敛率取所有满足 \(10^{-8}<\lVert x_m-x_*\rVert_2<10^{-3}\) 的相邻误差比之中位数。 | \(\alpha=0.8\)，至多 100 步；最终误差 \(<10^{-10}\)，估计率与 \(\rho((1-\alpha)I+\alpha J)=0.6\) 之差 \(<5\times10^{-3}\)。若 \(x_0=x_*\)，必须在第 0 步返回 `converged=true`、零残差和 `estimated_rate=null`，不得除以零。 | 令 \(\alpha=2.0\)，固定执行 12 步；迭代矩阵谱半径为 1.8，末残差必须大于初残差的 10 倍，稳定性验证器必须拒绝该运行。 |
| T-C02 | 两分量非线性教学密度：\(N_e=1\)，\(v=(-0.1,0.1)^T\)，\(g=4\)，\(\beta=1\)，\(F_i(n)=N_e\exp[-\beta(v_i+gn_i)]/\sum_j\exp[-\beta(v_j+gn_j)]\)，\(n_0=(0.9,0.1)^T\)。残差 \(R_n=\lVert F(n)-n\rVert_2/N_e\)。 | \(\alpha=0.25\)，至多 80 步；\(R_n<10^{-9}\)，归一化误差 \(|\sum_i n_i-N_e|<10^{-12}\)，且所有 \(n_i>-10^{-14}\)。每步必须保持形状 `(2,)` 和有限值。 | 令 \(\alpha=1\) 且执行 20 步；该映射形成两周期，末残差必须 \(>1.3\)，验证器须以 `oscillation_or_divergence` 拒绝，不得仅因归一化保持而宣告收敛。 |
| T-C03 | 在 T-C02 每步同时记录 \(n_m,F(n_m),R_m\) 与教学能量 \(E(n)=\tfrac12g\lVert n\rVert_2^2+v^Tn\)；相对能量变化 \(D_m=|E_m-E_{m-1}|/(1+|E_m|)\)。 | 对 T-C02 正例，轨迹长度、形状、有限性逐步验证；最终同时满足 \(R_m<10^{-9}\) 与 \(D_m<10^{-9}\)，并保持 T-C02 的归一化与正性条件。 | 在 T-C02 的 \(\alpha=1\) 轨迹上注入错误报告 \(E_m^{\mathrm{fake}}=10^{-12}E_m\)。必须找到 \(D_m^{\mathrm{fake}}<10^{-10}\) 且 \(R_m>1\) 的步；`energy_only` 判据会误通过，而冻结的双判据必须拒绝。 |
| T-C04 | 扫描 \(\alpha\in\{0.10,0.25,0.40,0.60,1.00\}\)，每项最多 80 步；记录初值、迭代数、最终残差、终止原因和完整规范化轨迹摘要。相同 seed/参数重复运行，删除明确禁止写入规范 JSON 的墙钟时间后，对排序键 JSON 的 SHA-256 作比较。 | 同一配置重复两次的规范 JSON SHA-256 必须完全相同；所有运行均含 `converged`、`iterations`、`final_residual` 和 `termination_reason`。 | 对 \(\alpha=1\) 强制 `max_iter=20`；必须返回 `converged=false`、`termination_reason="max_iterations"`，且该预期失败被捕获后整套测试方可通过。 |
| T-C05 | 分辨率 \(p=(8,16,32,64,128)\)，参考值 \(q_*=1\)。正序列 \(q^+=(1.12,1.03,1.008,1.002,1.0005)\)；指标为绝对参考误差与相邻差。 | 最后三个层级的参考误差均 \(<10^{-2}\)，最后一级误差 \(<10^{-3}\)，且最后两个相邻差均 \(<10^{-2}\)；三项条件必须同时满足。 | 非单调序列 \(q^-=(1.12,1.03,1.0020,1.0015,1.0080)\)：32/64 的单个相邻差 \(5\times10^{-4}<10^{-3}\)，但 128 的参考误差 \(8\times10^{-3}>5\times10^{-3}\)。单对判据会误通过，多层级判据必须拒绝。 |
| T-C06 | 周期函数 \(f(k)=\exp(\cos k)\)，在 \(N_k=(4,8,16,32,64)\) 的等距网格上用均值积分；参考为 `scipy.special.iv(0,1)`。采样误差为绝对差；独立基误差注入为固定偏置 \(\delta_b=10^{-2}\)。 | \(N_k=16,32,64\) 的采样误差均 \(<10^{-12}\)，并分别报告采样轴与基轴。 | 对 \(q_{N_k}+\delta_b\)，即使 32/64 的采样差 \(<10^{-12}\)，相对精确参考的总误差仍 \(>5\times10^{-3}\)；把它归因为“采样已收敛所以总量已收敛”的验证器必须失败。 |
| T-C07 | \(S=\operatorname{diag}(1,2,1.5,2.3)\)，\(H=\operatorname{diag}(-1.2,-0.2,1.2,4.6)\)，广义谱参考为 \((-1.2,-0.1,0.8,2.0)\)。以固定可逆上三角复矩阵 \(A\)（对角为 \(1.2,0.9,1.1,0.8\)，\(A_{01}=0.2+0.1i,A_{12}=-0.15i,A_{23}=0.1\)）构造 \(H'=A^\dagger HA,S'=A^\dagger SA\)。归一残差为 \(\lVert H'c-ES'c\rVert_2/[(\lVert H'\rVert_2+|E|\lVert S'\rVert_2)\lVert c\rVert_2]\)。 | `scipy.linalg.eigh(H_prime,S_prime)` 的排序谱与参考最大差 \(<10^{-11}\)，每个本征对归一残差 \(<10^{-12}\)，且 \(S'\) 最小本征值 \(>0\)。 | 对同一 \(H'\) 错用普通 `eigvalsh(H_prime)`；其排序谱与广义谱最大差必须 \(>10^{-1}\)，验证器必须以 `overlap_ignored` 拒绝。 |
| T-C08 | \(d=\texttt{model-size}\ge12\)，用固定 seed 的复高斯矩阵 QR（对 \(R\) 对角相位作规范化）得 \(Q\)；\(H=Q\operatorname{diag}(\operatorname{linspace}(-3,3,d))Q^\dagger\)。令 \(p=\max(5,\lfloor d/3\rfloor)\)、\(q=\lfloor(d-p)/2\rfloor\)、\(B=Q[:,q:q+p]\)，\(H_p=B^\dagger HB\)，\(H_r=BH_pB^\dagger\)。 | \(\lVert B^\dagger B-I\rVert_F<10^{-12}\)，回投幂等残差 \(\lVert H_r-B(B^\dagger H_rB)B^\dagger\rVert_F/\max(\lVert H_r\rVert_F,10^{-15})<10^{-12}\)；必须报告 \(d,p,q\)、窗口、\(\lVert H-H_r\rVert_F/\lVert H\rVert_F\)，且两组冻结 CLI 的丢失范数均 \(>0.9\)。 | 在固定表示中，用标准基前两维旋转角 0.37 rad 的 \(U\) 构造 \(H_2=U^\dagger HU\)。两矩阵谱最大差须 \(<10^{-12}\)，但相对矩阵差须 \(>0.15\)；“谱相同即矩阵标签等同”的验证器必须拒绝。 |
| T-C09 | 按第 8 节列出的完整必填路径集合验证一个 `stageC-label-v1` 合成记录；标量类型、数组形状、SHA-256 的 64 位十六进制格式和所有 `UNRESOLVED_M8` 占位均须检查。 | 完整合成记录验证通过，并在 JSON 中报告必填路径总数与 schema 版本。 | 对每一个必填路径分别深拷贝记录并删除该路径；每个删除样例都必须抛出 `ValueError`，错误消息含缺失路径。只要任一删除未失败，参数化测试即失败。 |
| T-C10 | \(N=\texttt{grid-size}\ge48\)，\(R_{ij}=|i-j|\)，\(A_{\exp}=e^{-R/2}\)，\(A_{\mathrm{alg}}=(1+R)^{-1}\)。截断半径 \(R_c=(2,4,8,16)\)；记录非零比例、相对 Frobenius 截断误差和 \(y=A\mathbf1/N\) 的相对 2-范数误差。 | 每个 \(R_c\) 的三项指标必须由原矩阵与截断矩阵直接复算并与 JSON 值相差 \(<10^{-14}\)；对 \(A_{\exp}\) 在距离 4—12 拟合 `log(abs(A_ij))`，斜率与 \(-0.5\) 之差 \(<10^{-12}\)。 | 在 \(A_{\mathrm{alg}}\) 的距离 1—8 上拟合指数并外推到 16—31；逐距离均值的相对 2-范数外推残差必须 \(>0.8\)，从而拒绝“一个指数拟合适用于全部衰减族”的声明。 |

JSON CLI 固定输出 Python/NumPy/SciPy 版本、随机种子、模型维数、网格/采样参数、混合参数、上述每项模型参数/公式标识/指标/容差、失败注入及捕获证据、`conventions_version="stageC-v1"` 和 `backend="synthetic"`。墙钟时间、临时路径和无序对象不得进入规范 JSON。退出码 0 只表示全部正例和全部预期失败均通过强制断言。

## 8. 标签语义最低模板

`stageC-label-v1` 的必填路径如下。对象可以嵌套实现，但路径及语义不得删除；M5 合成记录中涉及真实实践选择的值统一写为 `UNRESOLVED_M8`，字段存在本身不构成后端、材料、泛函、赝势或软件版本选择。

| 分组 | 必填路径与约束 |
|---|---|
| 顶层与生成状态 | `schema_version`；`generation_status`（M5 只能为 `SYNTHETIC_M5`，真实生成保留 `UNRESOLVED_M8`） |
| 后端血缘 | `backend.name`、`backend.version`、`backend.commit`；M5 均可为 `UNRESOLVED_M8` |
| 制品身份 | `artifacts.inputs[]`、`artifacts.outputs[]`；每项必须有 `uri_or_path` 与 `sha256`，合成制品也使用真实内容哈希 |
| 结构与边界 | `structure.id`、`structure.sha256`、`structure.lattice`、`structure.species`、`structure.positions`、`structure.boundary_conditions`；M5 结构明确标记 `SYNTHETIC` |
| 理论层级 | `theory.electronic_structure_level`、`theory.xc`、`theory.all_electron_or_pseudopotential`、`theory.potential_dataset.id`、`theory.potential_dataset.sha256`、`theory.relativistic_treatment` |
| 基或网格 | `basis.type`、`basis.definition`、`basis.cutoff_or_grid`、`basis.id`、`basis.sha256` |
| 自旋 | `spin.polarization`、`spin.noncollinear`、`spin.soc` |
| 采样与边界相位 | `sampling.kind`、`sampling.k_mesh`、`sampling.k_shift`、`sampling.k_weights`；不用真实 \(k\) 点时须给出等价合成采样定义 |
| 电子数与占据 | `occupation.electron_count`、`occupation.smearing_method`、`occupation.temperature`、`occupation.reported_energy_functional` |
| 收敛 | `convergence.scf_residual_definition`、`convergence.scf_residual_tolerance`、`convergence.energy_tolerance`、`convergence.eigensolver_tolerance`、`convergence.max_iterations`、`convergence.achieved_metrics` |
| 矩阵表示 | `representation.output_object`、`representation.units`、`representation.orbital_ordering`、`representation.atom_orbital_index_map`、`representation.lattice_displacement_direction`、`representation.bra_ket_order`、`representation.fourier_forward`、`representation.fourier_inverse`、`representation.phase_or_gauge`、`representation.overlap_treatment` |
| 投影/重建 | `projection.method`、`projection.window`、`projection.source_dimension`、`projection.target_dimension`、`projection.loss_metric`、`projection.loss_value`、`projection.band_validation`、`projection.matrix_validation` |
| 验证记录 | `validation.commands`、`validation.environment.python`、`validation.environment.numpy`、`validation.environment.scipy`、`validation.seed`、`validation.audit_status` |

T-C09 必须从这张表生成单一必填路径集合，对完整记录进行正例验证，并对每个路径执行一次删除后失败的参数化负例。数组内部的必填成员（例如制品的 `uri_or_path`/`sha256`）也须分别删除验证；因此不得用仅检查顶层分组存在的弱验证器替代。

## 9. M5-01 独立工作包审计

独立子 agent 应检查：五章范围和依赖是否闭合；来源是否足以支持相应事实且未越权；HK/KS/SCF/基组/近视性的条件是否明确；D-C01—D-C08 和 T-C01—T-C10 是否可执行且不隐含后端；标签模板是否区分理论、数值、表示和模型误差；D-010 和 M8/M9 边界是否无冲突。只有 `BLOCKING=0` 且明确允许 M5-02 时，M5-01 才能完成。
