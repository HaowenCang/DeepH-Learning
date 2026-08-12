# 第 8 章练习参考解答

## Q8-01

对象链为

\[
\text{连续理论}
\to\text{核/价处理}
\to\text{离散基/网格}
\to\mathbf k\text{ 采样与占据}
\to\text{SCF/本征收敛}
\to\text{矩阵表示}
\to\text{投影/重建}
\to\text{标签制品}
\to\text{DeepH 预测}.
\]

xc 属于理论近似；赝势属于核—价处理；cutoff 和 FFT 网格属于离散；\(\mathbf k\) 点属于采样；smearing 属于占据/温度语义；SCF 属于迭代误差；投影属于表示转换；DeepH 误差属于对固定标签映射的学习误差。

题中推理不成立。DeepH 矩阵误差趋近零最多说明它在冻结的基、规范和生成条件下复现标签；标签仍可包含 xc、赝势、离散、采样、未收敛或投影误差。后层误差趋零不能逆向删除上游偏差。

## Q8-02

对固定 \(l\)、参考能量和 \(r_c\)，主要条件包括：伪本征值与参考全电子本征值一致；\(r>r_c\) 的实/伪径向函数一致；核心区范数一致；匹配处函数及所需导数连续；参考能量附近对数导数及其能量导数一致。

这些条件约束参考环境附近的散射响应，因而支持 transferability；它们没有遍历所有化学环境、氧化态、压力和高能态，也没有给出统一误差界。标签至少登记元素、价电子组态、赝势类型、生成/发布身份、相对论处理、文件内容哈希及与后端的接口身份。

ultrasoft/PAW 还涉及增强电荷、投影子、变换算符或广义重叠对象。norm-conserving 的条件不能替代这些形式体系的定义，也不能证明其特定数据集质量。

## Q8-03

以

\[
|\psi\rangle=\sum_\nu c_\nu|\phi_\nu\rangle
\]

代入 Galerkin 条件

\[
\langle\phi_\mu|(\hat h-E)|\psi\rangle=0
\]

得到

\[
\sum_\nu
\langle\phi_\mu|\hat h|\phi_\nu\rangle c_\nu
=
E\sum_\nu
\langle\phi_\mu|\phi_\nu\rangle c_\nu.
\]

定义

\[
H_{\mu\nu}=\langle\phi_\mu|\hat h|\phi_\nu\rangle,
\qquad
S_{\mu\nu}=\langle\phi_\mu|\phi_\nu\rangle,
\]

于是 \(Hc=ESc\)，其中 \(H,S\in\mathbb C^{M\times M}\)、\(c\in\mathbb C^M\)。

对任意非零 \(c\)，若基线性无关，

\[
c^\dagger Sc
=\left\|\sum_\mu c_\mu|\phi_\mu\rangle\right\|^2>0,
\]

故 \(S\succ0\)。若 \(S\) 非正定，标准 Hermitian-definite 广义问题的输入条件不成立，应检查线性相关、积分和索引；若最小特征值很小，问题病态，正交化和系数对扰动敏感。删除小方向会改变子空间，必须登记阈值和影响。

## Q8-04

平面波

\[
\phi_{\mathbf G}(\mathbf r)
=\Omega^{-1/2}e^{i(\mathbf k+\mathbf G)\cdot\mathbf r}
\]

满足

\[
\langle\phi_{\mathbf G}|\phi_{\mathbf G'}\rangle
=\frac1\Omega\int_\Omega
e^{i(\mathbf G'-\mathbf G)\cdot\mathbf r}\,d\mathbf r
=\delta_{\mathbf G\mathbf G'}.
\]

整个离散问题写成 \(Hc=Ec\) 还要求标准 \(L^2\) 内积、普通范数约束、一致离散积分，且形式体系没有附加广义重叠算符。ultrasoft/PAW 等可在正交平面波系数上定义非平凡物理内积，所以基 Gram 矩阵为 \(I\) 不等于完整问题必无 \(S\)。

cutoff 控制波函数有限子空间；FFT 网格控制实空间乘积、密度和势的离散及混叠；\(\mathbf k\) 网格控制 Brillouin 区积分。改变一个轴不能替代另外两个轴的收敛检查。

## Q8-05

对正序列，参考误差为

\[
(0.12,0.03,0.008,0.002,0.0005),
\]

相邻差为

\[
(0.09,0.022,0.006,0.0015).
\]

最后三个误差均小于 \(10^{-2}\)，最后误差小于 \(10^{-3}\)，最后两个相邻差均小于 \(10^{-2}\)，故正例通过。

对负序列，参考误差为

\[
(0.12,0.03,0.002,0.0015,0.008),
\]

相邻差为

\[
(0.09,0.028,0.0005,0.0065).
\]

32/64 的差 \(5\times10^{-4}<10^{-3}\)，但 128 的参考误差 \(8\times10^{-3}>5\times10^{-3}\)。只选择最平的一对忽略了后续反弹，属于局部假平台。

## Q8-06

修正 Bessel 函数的积分表示为

\[
I_0(z)=\frac1{2\pi}\int_0^{2\pi}e^{z\cos k}\,dk.
\]

取 \(z=1\) 即得题中等式。等距规则为

\[
q_N=\frac1N\sum_{j=0}^{N-1}
\exp\left[\cos\left(\frac{2\pi j}{N}\right)\right].
\]

冻结复算中 \(N=16,32,64\) 的绝对误差均约为 \(2.22\times10^{-16}<10^{-12}\)。加入 \(\delta_b=10^{-2}\) 后，总误差约 \(10^{-2}>5\times10^{-3}\)，但 32/64 的采样差仍小于 \(10^{-12}\)。

可辨识扫描应先固定基、赝势、smearing 和 SCF 容差，扫描至少三个 \(\mathbf k\) 层级；随后固定已选采样，单独扫描基 cutoff。每条轴都保存完整输入、参考/外推假设、相邻差和目标量误差，不能同时改变两个轴后分摊总差。

## Q8-07

原矩阵对角，广义谱为

\[
E_i=H_{ii}/S_{ii}=(-1.2,-0.1,0.8,2.0).
\]

一致合同变换给出

\[
H'-ES'=A^\dagger(H-ES)A,
\]

所以

\[
\det(H'-ES')
=|\det A|^2\det(H-ES).
\]

\(A\) 可逆时零点相同，广义谱保持。

逐本征对残差为

\[
r_i=
\frac{\|H'c_i-E_iS'c_i\|_2}
{(\|H'\|_2+|E_i|\|S'\|_2)\|c_i\|_2}.
\]

分母用算符范数和本征值尺度归一化，使残差相对于该本征方程的自然量级无量纲。冻结计算中每个 \(r_i<10^{-12}\)，且 \(S'\succ0\)。

直接计算 \(\operatorname{eigvalsh}(H')\) 等价于把 \(S'\) 替换为 \(I\)，所解物理内积和本征方程都改变；最大谱差约 0.967。因此它不是同一问题的较粗求解，而是对象错误。

## Q8-08

令 \(P_B=BB^\dagger\)。由 \(B^\dagger B=I\)，

\[
P_B^\dagger=P_B,\qquad P_B^2=P_B.
\]

于是

\[
B(B^\dagger HB)B^\dagger=P_BHP_B=H_r
\]

且

\[
P_BH_rP_B=P_B(P_BHP_B)P_B=H_r.
\]

丢失范数 \(\|H-H_r\|_F/\|H\|_F\) 衡量固定完整矩阵对固定子空间的回投损失；它不等于能带误差、物性误差或任意其他材料上的投影误差。

对 unitary \(U\)，

\[
\det(U^\dagger HU-EI)
=\det(U^\dagger)\det(H-EI)\det(U)
=\det(H-EI),
\]

故谱保持。但固定标准坐标下 \(U^\dagger HU\) 的元素通常不同；只有同步声明基和规范变化后，它才与原矩阵代表同一算符。冻结反例的相对矩阵差大于 0.15，而谱差小于 \(10^{-12}\)。

若 \(B^\dagger B=S_B\ne I\)，目标矩阵是

\[
H_B=B^\dagger HB,\qquad S_B=B^\dagger B,
\]

应解 \(H_Bc=ES_Bc\)。列满秩时完整空间正交投影为

\[
P_B=B S_B^{-1}B^\dagger,
\]

不能使用 \(BB^\dagger\)。完整空间回投算符为

\[
H_r^{(\mathrm{nonorth})}
=P_BHP_B
=B S_B^{-1}H_BS_B^{-1}B^\dagger,
\]

并满足

\[
P_BH_r^{(\mathrm{nonorth})}P_B
=H_r^{(\mathrm{nonorth})}.
\]

对应丢失范数为

\[
\ell_H^{(\mathrm{nonorth})}
=\frac{\|H-H_r^{(\mathrm{nonorth})}\|_F}
{\max(\|H\|_F,10^{-15})}.
\]

数值实现应稳定求解含 \(S_B\) 的线性系统，而不显式形成病态逆。

缩放反例取 \(B=2e_1\)、\(H=h|e_1\rangle\langle e_1|\)。此时 \(S_B=4\)、\(H_B=4h\)，正确公式回投为 \(h|e_1\rangle\langle e_1|\)，与目标子空间上的原算符一致；错误照搬正交公式得到

\[
BH_BB^\dagger
=16h|e_1\rangle\langle e_1|,
\]

它随基列的任意缩放改变，故不具有固定算符语义。

## Q8-09

数值 smearing 是改善占据和积分稳定性的数值设置；物理有限温度需要 Mermin 系综、熵项和明确热力学变量。可能报告的量包括自由能 \(F=E-TS\)、内部能 \(E\)、带熵修正的零温外推量。不同量即使数值接近也不是同一对象，比较必须固定定义和单位。

合成摘要示例：

- backend：name/version/commit 均为 UNRESOLVED_M8；
- artifacts：输入、输出路径和真实合成内容 SHA-256；
- structure：SYNTHETIC 标识、晶格、物种、位置和边界；
- theory：electronic_structure_level、xc、全电子/赝势、数据集 ID/哈希、相对论均保留未决；
- basis/sampling/occupation：合成基定义、\(\mathbf k\) 点/偏移/权重、电子数、smearing 方法、温度和报告能量；
- convergence：SCF/能量/本征阈值、最大步数和达到值；
- representation：\(H/S\)、单位、轨道—原子索引、晶格位移方向、bra/ket、Fourier 正逆、相位/规范、overlap；
- projection：方法、窗口、源/目标维数、损失定义和值、能带/矩阵验证；
- validation：命令、Python/NumPy/SciPy、seed 和审计状态。

字段中的实践对象保持 UNRESOLVED_M8；合成数组和制品则提供真实可验证内容及哈希。

## Q8-10

SCF 残差小于 \(10^{-10}\) 只支持按给定残差定义的自洽性，不支持基组、采样或理论误差已经收敛。32/64 \(\mathbf k\) 差很小是两个层级的局部证据；缺少更多层级或参考时，现有证据不足以排除非单调假平台。投影后窗口内能带误差小于 \(10^{-3}\) 支持该窗口和匹配规则下的谱门控，但不能推出矩阵元素、带外状态或其他物性一致。

缺少赝势哈希使核处理身份不可复现；缺少轨道顺序和相位规范使矩阵逐元素比较无定义；只比较一个 cutoff 不能建立基收敛；若实际表示非正交却省略 overlap，则普通谱对象错误。

最小补充验证包括：登记赝势文件身份和哈希；冻结轨道映射、单位、相位与 Fourier 约定；增加至少两个 cutoff 层级并固定其他轴；增加采样层级或可信参考；保存并验证 \(S\succ0\)，使用广义本征求解；同时报告投影丢失范数、矩阵门控和目标物性门控。

M8 前仍禁止安装 DeepH 本体、下载正式训练数据、生成正式 DFT 标签或隐含选择材料、DFT 后端和实践软件版本。M7-I 通过后才集中提交 M8 决策；M8 冻结后，在 M9 正式安装、下载或复现实验前还需一次明确执行授权。
