# 阶段 C 综合问题：从固定核多电子对象到可验证 Hamiltonian 标签

本综合题用于验证阶段 C 材料能否覆盖完整对象链，不要求学习者提交个人作答。C-C01—C-C10 均有对应参考解答、条件边界、数值判据、失败机制和自动验证入口。全部数值对象为解析或合成对象；不得据此选择真实材料、DFT 后端、DeepH 版本、泛函、赝势、基或投影软件。

## C-C01 多电子对象、BO 边界与 1RDM

从电子—核 Hamiltonian

\[
\hat H=\hat T_n+\hat T_e+\hat V_{nn}+\hat V_{ne}+\hat V_{ee}
\]

出发，说明固定核电子 Hamiltonian 保留和删除哪些项。将总波函数展开为

\[
\Psi(r,R)=\sum_a \chi_a(R)\Phi_a(r;R),
\]

写出核方程中由 \(\nabla_R\Phi_a\) 产生的导数耦合，并说明何种额外条件下才得到单一势能面上的最简核运动方程。

再对两占据轨道 determinant 写出 1RDM，证明占据空间内 unitary 旋转保持密度和 1RDM。说明该幂等性结论为何不能推广到一般相关多体态。

## C-C02 HK、Levy、Lieb 与可表示性

对固定粒子数 \(N\) 的外势问题，分别陈述：

1. HK 外势—基态密度唯一性的常数规范、共同基态和简并边界；
2. Levy 纯态 constrained search 的搜索对象和密度域；
3. 系综扩展与 Lieb 泛函的凸、下半连续闭包关系；
4. \(N\)-representability、interacting \(v\)-representability、noninteracting \(N\)-representability 和 noninteracting \(v\)-representability 的区别。

判断下列句子是否成立并修正：“HK 定理证明任意非负归一化密度都由唯一外势产生，而且 universal functional 的 minimum 总能由单个纯态取得。”

## C-C03 KS 变分、有效势与总能量

从

\[
E[n]=T_s[n]+\int v_{\mathrm{ext}}(r)n(r)\,dr+E_H[n]+E_{xc}[n]
\]

和轨道正交约束出发，推导 KS 方程及

\[
v_s=v_{\mathrm{ext}}+v_H+v_{xc}.
\]

写出用 KS 本征值和重建总能量时必须修正的 Hartree 与交换相关双计数。说明为什么“KS 方程形式精确”不等于“已有精确可计算的 \(E_{xc}\)”，也不等于全部 KS 本征值都是多体激发能。

## C-C04 线性 SCF 固定点与稳定性

采用

\[
F(x)=Jx+b,
\quad
J=\operatorname{diag}(0.2,0.5,-0.4),
\quad
b=(0.3,-0.2,0.1)^T,
\]

以及混合迭代

\[
x_{m+1}=x_m+\alpha(F(x_m)-x_m).
\]

求固定点 \(x_*\) 和误差迭代矩阵 \(M_\alpha\)。分别计算 \(\alpha=0.8\) 与 \(\alpha=2\) 的谱半径，解释 T-C01 正例和“恰执行 12 次更新”的失败协议。若 \(x_0=x_*\)，说明实现应如何处理速率估计。

## C-C05 非线性 SCF、双判据与可复现记录

考虑

\[
F_i(n)=\frac{\exp[-(v_i+4n_i)]}{\sum_j\exp[-(v_j+4n_j)]},
\quad
v=(-0.1,0.1)^T,
\quad
n_0=(0.9,0.1)^T.
\]

定义粒子数归一化残差和教学能量

\[
R_m=\|F(n_m)-n_m\|_2,
\qquad
E(n)=2\|n\|_2^2+v^Tn.
\]

说明 T-C02/T-C03 为何同时检查残差、能量变化、粒子数、正性、shape 和有限性。解释以下三类失败为何必须区分：\(\alpha=1\) 的两周期、伪能量缩放导致 energy-only 误通过、达到 `max_iter` 但残差不合格。

为 T-C04 设计最小规范记录：列出必须进入 JSON 的字段，以及墙钟时间为何不得进入确定性哈希。

## C-C06 多轴离散与采样收敛

对参考值 \(q_*=1\)，给定

\[
q^+=(1.12,1.03,1.008,1.002,1.0005),
\]

\[
q^-=(1.12,1.03,1.0020,1.0015,1.0080),
\]

对应分辨率 \((8,16,32,64,128)\)。计算最后三个参考误差和最后两个相邻差，按 T-C05 判定正负序列；说明只检查 32/64 一对为何会误判。

再对 \(f(k)=\exp(\cos k)\) 的周期等权积分说明 T-C06 如何分离 \(k\) 采样误差与固定基偏置 \(10^{-2}\)。判断“64 点与 32 点结果相同，所以总误差小于 \(10^{-12}\)”是否成立。

## C-C07 广义本征、投影回投与等谱反例

给定

\[
S=\operatorname{diag}(1,2,1.5,2.3),
\quad
H=\operatorname{diag}(-1.2,-0.2,1.2,4.6).
\]

求广义谱。证明对可逆 \(A\)，\(H'=A^\dagger HA\)、\(S'=A^\dagger SA\) 保持广义谱，并写出归一化后向残差。解释为什么对 \(H'\) 调用普通 `eigvalsh` 是不同问题。

对正交列矩阵 \(B\)，写出 \(H_p=B^\dagger HB\) 和 \(H_r=BH_pB^\dagger\) 的回投一致性。

等谱失败样例另采用 T-C08 的冻结对象，不沿用上面的四维对角 \(H\)：令 \(d=12\)、seed 为 20260805，对复高斯矩阵作带对角相位规范的 QR 得 \(Q\)，并定义

\[
H^{(12)}=Q\operatorname{diag}(\operatorname{linspace}(-3,3,12))Q^\dagger .
\]

令 \(U\) 只在固定标准基第 0、1 维旋转 0.37 rad，\(H_2^{(12)}=U^\dagger H^{(12)}U\)。计算谱最大差和相对 Frobenius 矩阵差，说明为何二者可等谱但不构成同一固定坐标标签。另说明如果把相同旋转直接施加到题首四维对角 \(H\)，为何不能引用 T-C08 的冻结数值阈值。

## C-C08 标签 schema 与授权故障注入

依据 [`stageC-label-v1`](../../../../03_textbook/stageC_label_semantics_template.md)，把最低技术验证分为七层：路径存在；结构验证（类型、shape、有限性与数组关系）；内容身份；M8 哨兵/合成白名单；数值结构；固定表示语义一致性；前向物理量。再把独立审计列为第八步。解释每层通过能证明什么、不能证明什么。

说明当前 T-C09 的 47 个对抗变异只直接分类为 type、shape、hash 和 M8 choice；它们不能被过度解释为已经穷尽单位、轨道顺序、bra/ket、Fourier、规范、overlap 处理或全部前向物理验证。

针对以下变异逐项给出预期失败原因和应定位的字段：

- `convergence.max_iterations="eighty"`；
- `structure.lattice` 为含字符串的 \(3\times3\) 数组；
- `sampling.k_mesh=[1,1]`；
- `representation.output_object="H,S"`；
- 实际 SHA 字段改为 `"0"*64`；
- `structure.species=["Si","O"]`；
- `basis.type="plane_wave"`；
- `sampling.kind="monkhorst_pack"`；
- `projection.method="HPRO"`。

说明为什么 67/67 路径删除全部失败仍不足以覆盖这些错误。

## C-C09 局域性、截断指标与外推失败

在 \(N=64\) 上定义距离 \(R_{ij}=|i-j|\) 和

\[
A_{\exp,ij}=e^{-R_{ij}/2},
\qquad
A_{\mathrm{alg},ij}=\frac{1}{1+R_{ij}}.
\]

对截断半径 \(R_c\) 写出非零比例、相对 Frobenius 误差和对 \(x=\mathbf 1/N\) 的相对作用量误差。说明为什么三指标都应由原矩阵和截断矩阵直接复算。

对指数族在距离 4—12 拟合 \(\log|A_{ij}|\)，给出理论斜率。解释为什么把距离 1—8 上得到的指数拟合外推到代数族的 16—31 区间应被 T-C10 拒绝。再区分电子近视性、1RDM 衰减和固定基下 \(H/S\) 块稀疏三种陈述。

## C-C10 端到端标签血缘与 M8/M9 边界

构造以下对象链的审计表：

\[
\text{结构与边界}
\to \text{固定核理论对象}
\to \text{理论/赝势层级}
\to \text{基与采样}
\to \text{SCF 固定点}
\to \text{投影与矩阵表示}
\to \text{标签记录}
\to \text{DeepH 训练/推理}
\to \text{矩阵与前向物理量验证}.
\]

对每条箭头列出至少一个误差来源、一个必须保存的证据字段和一个失败样例。说明阶段 C 的合成材料已经验证了哪些机制，仍未决定哪些实践事项。最后写出 M8 决策冻结与 M9 外部执行授权的两道独立门槛。

[参考解答](../solution/readme.md)给出逐项推导、数值和验证入口。[阶段 C 推导总索引](../../../../04_derivations/stageC/README.md)给出 D-C01—D-C08 的前提；[自动验收说明](../../../../05_code_exercises/stageC_teaching_scf/README.md)给出 T-C01—T-C10 的复现命令。
