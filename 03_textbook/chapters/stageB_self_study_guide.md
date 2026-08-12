# 阶段 B 自学导航：非正交基、周期表示与实空间能带

## 1. 使用方式与完成口径

阶段 B 的目标是把有限维量子矩阵表示、Hermitian-definite 广义本征问题、周期 Bloch/Fourier 表示和实空间矩阵到能带的对象链连接起来。依据材料建设模式，本指南保留检查问题、练习和综合题，但不要求学习者提交闭卷作答、口头解释或阶段自测。阶段完成证据来自材料覆盖、参考解答、可执行代码、失败样例和独立审计，而不是个人作答记录。

全部周期符号服从[阶段 B 统一约定](../stageB_conventions.md)。若其他资料采用不同的 bra/ket 方向、Fourier 正负号、轨道中心相位或基变换方向，应先写出显式映射，不得把两套公式直接拼接。

## 2. 前置条件与建议顺序

前置知识包括复向量空间、内积、矩阵乘法、Hermitian 与正定矩阵、基础本征值问题和单粒子量子力学。缺少某项时，可以先查阅第 2、3 章对应的小节和例题；它不构成学习者本人必须通过的先验考试。

建议按以下顺序使用材料：

| 单元 | 核心问题 | 教材与推导 | 例题、练习与验证 |
|---|---|---|---|
| B1 有限基表示 | 同一态在换基后，基、系数、矩阵元和 Gram 矩阵分别如何变换？ | [第 2 章](02_quantum_states_operators_matrices/chapter.md)；[D-B01 推导](../../04_derivations/stageB/02_basis_representation.md) | [例题](02_quantum_states_operators_matrices/examples.md)；[问题](../../06_exercises/02-stageB/02_basis/problem/readme.md)与[解答](../../06_exercises/02-stageB/02_basis/solution/readme.md)；T-B03、T-B10 |
| B2 非正交广义本征 | 为什么出现 \(Hc=ESc\)，何时具有实谱与完整 \(S\)-正交本征基，如何稳定约化？ | [第 3 章](03_nonorthogonal_generalized_eigen/chapter.md)；[D-B02—D-B04 推导](../../04_derivations/stageB/03_generalized_eigen.md) | [例题](03_nonorthogonal_generalized_eigen/examples.md)；[问题](../../06_exercises/02-stageB/03_generalized_eigen/problem/readme.md)与[解答](../../06_exercises/02-stageB/03_generalized_eigen/solution/readme.md)；T-B01—T-B04 |
| B3 周期表示 | 有限 BvK 平移群如何产生闭合 Fourier 对，实空间厄米关系如何保证全 \(k\) Hermiticity？ | [第 4 章](04_periodicity_bloch_reciprocal/chapter.md)；[D-B05/D-B06 推导](../../04_derivations/stageB/04_bloch_fourier.md) | [例题](04_periodicity_bloch_reciprocal/examples.md)；[问题](../../06_exercises/02-stageB/04_bloch_fourier/problem/readme.md)与[解答](../../06_exercises/02-stageB/04_bloch_fourier/solution/readme.md)；T-B05、T-B06、T-B08 |
| B4 实空间到能带 | 如何从 \(H(R),S(R)\) 组装 \(H(k),S(k)\)，求解能带并区分截断、采样和规范误差？ | [第 9 章](09_realspace_hamiltonian_bands/chapter.md)；[D-B06 对象链](../../04_derivations/stageB/09_realspace_to_bands.md) | [例题](09_realspace_hamiltonian_bands/examples.md)；[问题](../../06_exercises/02-stageB/09_realspace_bands/problem/readme.md)与[解答](../../06_exercises/02-stageB/09_realspace_bands/solution/readme.md)；T-B07—T-B10 |

每个单元应按“正文定义—逐式推导—例题—练习—参考解答—自动测试—失败诊断”顺序核对。直接阅读参考解答不会使材料门控失效，因为本阶段验收的是材料可自学性；但应当同时查看错误机制和验证入口，不能只记最终数值。

## 3. 能力—材料—验证映射

| 能力 ID | 可验证能力 | 材料入口 | 自动或解析验证 | 失败边界 |
|---|---|---|---|---|
| D-B01 | 区分态、列基、系数和矩阵元，执行一致可逆基变换 | 第 2 章；`02_basis_representation.md` | 第 2 章练习；T-B03、T-B10 | 奇异变换、改变子空间、只变 \(H\) 或只变系数 |
| D-B02 | 从投影和 Rayleigh 商分别推出 \(Hc=ESc\) | 第 3 章第 3—5 节；`03_generalized_eigen.md` | 第 3 章 Q3-02—Q3-04；T-B01、T-B02 | \(S\not\succ0\) 时不得套用 Hermitian-definite 结论 |
| D-B03 | 完成 Cholesky 与对称正交化的变量替换和逆映射 | 第 3 章第 6—10 节 | 第 3 章例题与 Q3-05—Q3-08；T-B01、T-B02、T-B04 | 显式逆作为默认实现、删除小特征值方向却声称无损 |
| D-B04 | 证明一般可逆合同变换保持广义谱，并限定 Euclidean 残差不变量 | 第 2、3、9 章相关推导 | Q9-08；T-B03、T-B08、T-B10 | 一般非 unitary 变换不保持冻结的 Euclidean 归一化残差标量 |
| D-B05 | 从冻结矩阵元方向推出 \(H(R)^\dagger=H(-R)\)，并推广到 \(S\) | 第 4、9 章；`04_bloch_fourier.md` | 第 4 章 Q4-06；第 9 章 Q9-02；T-B06 | 非零块不必自身 Hermitian；缺少共轭块不能静默重厄米化 |
| D-B06 | 推导闭合 Fourier 对、中心规范和实空间到能带链 | 第 4、9 章；两份 D-B06 推导 | 第 4、9 章练习；T-B05、T-B07—T-B09 | 正反号、\(1/N\)、\(S\) 同步、有限/无限和截断/采样边界不得混淆 |

[解析推导总索引](../../04_derivations/stageB/README.md)给出 D-B01—D-B06 的条件与依赖关系；[代码说明](../../05_code_exercises/stageB_periodic_nonorthogonal/README.md)给出 T-B01—T-B10、固定版本和复现命令。综合使用入口为[阶段 B 综合问题](../../06_exercises/02-stageB/comprehensive/problem/readme.md)与[参考解答](../../06_exercises/02-stageB/comprehensive/solution/readme.md)。

## 4. 关键自学检查与答案定位

以下检查用于导航，不要求提交个人答案：

| 检查问题 | 答案定位 | 对应验证 |
|---|---|---|
| 为什么矩阵元换基是合同变换，而系数是逆变换？ | D-B01 第 2—3 节；第 2 章练习 Q2-06 | T-B03 |
| 为什么 Hermitian 的 \(S\) 仍不足以保证标准广义求解有效？ | 第 3 章第 2 节；练习 Q3-01、Q3-07 | T-B01、T-B04 |
| 完整 \(S\)-正交本征基的存在依赖哪一步？ | D-B02/D-B03 第 5—7 节：Hermitian 谱定理与可逆逆映射 | T-B02 |
| 为什么 \(H(R)\) 的非零块不必自身 Hermitian？ | D-B05 第 6 节；第 9 章 Q9-02 | T-B06 |
| 为什么正变换用 \(e^{+ikR}\) 而逆变换用 \(e^{-ikR}/N\)？ | D-B06 的有限角色正交与逆变换 | T-B05 |
| 为什么一般可逆基变换不保持当前归一化 Euclidean 残差？ | 第 9 章推导第 6 节；Q9-08 | T-B03、T-B10 |
| 为什么增加 \(k\) 点不能恢复被删的 \(R=\pm2\) 块？ | 第 9 章第 9.4 节；Q9-07 | T-B09 |
| 原始 DeepH 中 \(H\) 与 \(S\) 分别如何获得？ | 第 9 章第 9.6 节与资料包 DH-01 边界 | 不推广到现代软件；M8 冻结后再核软件对象 |

## 5. 常见错误及诊断顺序

| 现象 | 优先检查 | 机制判断 | 对应材料/测试 |
|---|---|---|---|
| 换基后普通谱改变 | 是否同步变换 \(S\) 与系数 | 非 unitary 基下普通本征问题不是原广义问题 | D-B01/D-B04；T-B03 |
| 求解器输出复能量或失败 | \(H/S\) Hermiticity、\(S\) 最小特征值 | 输入不属于 Hermitian-definite 类，不能先怪求解器 | 第 3 章；T-B01/T-B02/T-B04 |
| \(H(k)\) 不 Hermitian | \(\pm R\) 块、复共轭与指标交换 | 实空间配对或索引方向错误 | D-B05；T-B06 |
| Fourier 逆变换得到 \(-R\) 块 | 正反相位是否同号、\(1/N\) 是否遗漏 | 离散角色正交未闭合 | D-B06；T-B05 |
| 中心规范后能带改变 | \(H,S,c\) 是否同步作用同一 \(U(k)\) | 只变矩阵束一部分，不再是同一表示 | 第 4、9 章；T-B08 |
| 加密 \(k\) 网格仍有固定带差 | 是否删除远程实空间块 | 截断改变模型，采样不能恢复缺失信息 | 第 9 章；T-B09 |
| 重厄米化后错误“消失” | 先记录缺块与反 Hermitian 残差 | 平均操作改变数据并掩盖上游错误 | 第 9 章 Q9-07/Q9-10；T-B06 |

诊断时应先确认对象、形状、单位、索引顺序和约定，再检查矩阵结构与数值残差，最后讨论前向能带误差。小后向残差不能在没有谱隙和条件数信息时自动解释为小逐带前向误差。

## 6. 可执行复现入口

固定 Python 为 3.12.13，依赖为 NumPy 2.3.5、SciPy 1.18.0。完整命令见[代码说明](../../05_code_exercises/stageB_periodic_nonorthogonal/README.md)。默认门控应满足：

- 5 项单元测试全部通过；
- JSON 包含 `conventions_version="stageB-v1"`、版本、种子、维数、\(N_k\)、容差、T-B01—T-B10 指标和预期失败；
- 默认与第二配置均以退出码 0 返回，`overall_pass=true`；
- 非正定 \(S\)、非 Hermitian \(H\)、同号 Fourier 逆变换、缺共轭块、忽略 \(S\)、单边规范、截断和单边置换均必须被实际执行并断言捕获。

## 7. 阶段边界与后续接口

阶段 B 的材料可以说明原始 DeepH 的抽象对象链，但不能据此猜测任何现代软件字段、文件格式、轨道排序或版本行为。M8 前仍禁止安装 DeepH 本体、下载正式训练数据、生成正式 DFT 标签或隐含选择材料体系、DFT 后端和实践软件版本。阶段 B 的所有数值均来自合成矩阵，不能外推为真实材料的跃迁范围、条件数或能带误差。

M4-08 完成后只进入 M4-09 阶段 B 独立材料总审计。只有总审计明确 `BLOCKING=0` 并允许进入依赖阶段，M4 才能完成；不要求学习者本人提交作答。
