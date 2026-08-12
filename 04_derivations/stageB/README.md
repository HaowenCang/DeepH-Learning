# 阶段 B 解析推导包：D-B01—D-B06

## 1. 作用与证据边界

本索引把阶段 B 的六项必需推导组织为一个可逐项复核的依赖链。它不替代四个推导正文，也不新增软件接口或真实材料结论。共同的列基、bra/ket 方向、实空间平移和 Fourier 相位服从[阶段 B 统一约定](../../03_textbook/stageB_conventions.md)；验收口径服从[M4 阶段 B 工作包](../../08_audits/M4_stageB_work_package.md)。

标准教材、数值线性代数资料和原始论文只用于锚定其明确支持的对象、定义与算法条件；定义之后的代数步骤标记为 `DIRECT_DERIVATION`，合成数值模型与故障注入标记为 `PEDAGOGICAL`。原始 DeepH 来源不支持具体软件字段、轨道排序、现代软件任务分工或真实材料误差结论。

## 2. 统一对象与适用条件

阶段 B 的标准主线限于有限维复内积空间、线性无关局域基和 Hermitian-definite 矩阵束：

\[
H=H^\dagger,
\qquad
S=S^\dagger\succ0.
\]

周期部分先在完整有限 Born–von Karman 晶格及其对偶 \(k\) 网格上推导；无限积分只作为明确标记的形式极限。每个实空间矩阵块都采用

\[
H_{ab}(\mathbf R)=
\langle\phi_{a\mathbf0}|\hat H|\phi_{b\mathbf R}\rangle,
\qquad
S_{ab}(\mathbf R)=
\langle\phi_{a\mathbf0}|\phi_{b\mathbf R}\rangle.
\]

若 \(S\) 奇异、非 Hermitian 或不定，若基变换矩阵奇异，或若 Fourier 网格不完整，则相应标准结论不再适用；材料必须转入失败诊断，不能静默修补后继续沿用主线结论。

## 3. 六项推导的覆盖矩阵

| ID | 推导目标 | 主推导 | 关键条件 | 必须保留的不变量与边界 |
|---|---|---|---|---|
| D-B01 | 态、算符矩阵元、Gram 矩阵与一致基变换 | [有限维基表示与一致变换](02_basis_representation.md)第 1—5 节 | 同一有限维子空间；有序基线性无关；\(A\) 可逆 | \(\Phi'=\Phi A\)、\(c'=A^{-1}c\)、\(H'=A^\dagger HA\)、\(S'=A^\dagger SA\)；奇异 \(A\) 或改变子空间不是无损基变换 |
| D-B02 | 从投影与 Rayleigh 商得到 \(Hc=ESc\) | [非正交广义本征推导](03_generalized_eigen.md)第 2—5 节 | \(H=H^\dagger\)；基线性无关，故 \(S\succ0\) | 投影式与变分式给出同一矩阵束；若 \(S\not\succ0\)，不调用实谱和完备 \(S\)-正交本征基结论 |
| D-B03 | Cholesky、对称正交化与逆映射 | [非正交广义本征推导](03_generalized_eigen.md)第 6—7、9—10 节 | Hermitian-definite；分解成功；记录小特征值方向 | 给出标准问题变量与原系数的双向映射；默认数值实现不显式形成矩阵逆；删除小特征值方向会改变有效子空间 |
| D-B04 | 一般可逆基变换下的广义谱不变 | [有限维基表示与一致变换](02_basis_representation.md)第 5 节；[非正交广义本征推导](03_generalized_eigen.md)第 8 节 | \(A\) 可逆且 \(H,S,c\) 同步变换 | \(\det(H'-ES')=|\det A|^2\det(H-ES)\)；一般可逆变换保持广义谱、精确方程和物理态范数，但不保持任意 Euclidean 矩阵/残差范数 |
| D-B05 | 实空间厄米关系与 \(k\) 空间 Hermiticity | [Bloch、Fourier 与实空间厄米关系](04_bloch_fourier.md)第 4、6 节；[实空间到能带](09_realspace_to_bands.md)第 1—2 节 | 冻结 bra/ket 方向；平移协变；\(\pm\mathbf R\) 块完整配对 | \(H(\mathbf R)^\dagger=H(-\mathbf R)\)、\(S(\mathbf R)^\dagger=S(-\mathbf R)\)；非零块不必自身 Hermitian；缺共轭块必须触发失败 |
| D-B06 | 周期 Fourier 正反变换、相位规范和能带对象链 | [Bloch、Fourier 与实空间厄米关系](04_bloch_fourier.md)第 2—8 节；[实空间到能带](09_realspace_to_bands.md)第 2—7 节 | 完整有限 \(\mathcal R_N/\mathcal K_N\) 对；固定正负号与 \(1/N\)；每个 \(k\) 上 \(S(k)\succ0\) | \(H(k)=\sum_R e^{+ikR}H(R)\)、逆变换含 \(e^{-ikR}/N\)，\(S\) 同步；轨道中心相位须同步作用于 \(H,S,c\)；截断与采样不得混同 |

## 4. 推导依赖顺序

推导应按以下依赖阅读和复核：

\[
\text{D-B01}
\longrightarrow
\{\text{D-B02},\text{D-B04}\}
\longrightarrow
\text{D-B03},
\]

\[
\text{D-B05}
\longrightarrow
\text{D-B06},
\qquad
\{\text{D-B02},\text{D-B03}\}
\longrightarrow
\text{D-B06 的逐 }k\text{ 广义本征步骤}.
\]

D-B04 与 D-B06 的“规范不变”必须区分代数对象。任意可逆合同变换保持广义谱、精确本征方程和 \(S\)-正交性，残差向量按 \(r' = A^\dagger r\) 协变；工作包采用的 Euclidean 归一化残差标量只有在 \(A\) 为 unitary 时才保持不变。

## 5. 逐项可验证性

| 检查对象 | 正例证据 | 必须拒绝或显式暴露的失败 |
|---|---|---|
| 一致基变换 | 第 2、3 章例题与练习验证期望值、广义谱和 \(S\)-范数 | 只变 \(H\)、只变系数、奇异变换、把非 unitary 变换后的普通谱当作不变量 |
| Hermitian-definite 求解 | 第 3 章固定模型验证实谱、归一化残差、\(S\)-正交和两种约化 | 非正定/奇异 \(S\)、显式逆作为默认路径、用小后向误差无条件推出小逐带前向误差 |
| 周期 Fourier 对 | 第 4 章固定离散模型验证角色正交、正逆变换、\(k+G\) 和中心规范 | 正反号不闭合、遗漏 \(1/N\)、只对矩阵束一侧施加规范 |
| 实空间矩阵到能带 | 第 9 章双轨道模型验证全 \(k\) Hermiticity、\(S(k)\succ0\)、逐本征对残差、逆变换和能带 | 缺 \(-R\) 块、忽略 \(S\)、静默重厄米化、用加密 \(k\) 网格冒充恢复已截断块 |

固定数值环境、JSON 输出字段、随机种子、批量测试和统一容差将在 M4-07 固化。本推导包的 M4-06 退出条件是：D-B01—D-B06 均可从本索引定位到逐式推导，所有适用条件和失败边界可定位，公式能严格渲染，本地链接有效，并通过独立内容审计。
