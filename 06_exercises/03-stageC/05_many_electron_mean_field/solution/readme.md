# 第 5 章练习参考解答

## Q5-01

完整 Hamiltonian 为

\[
\hat H=\hat T_N+\hat T_e+\hat V_{NN}+\hat V_{ee}+\hat V_{eN}.
\]

固定 \(\mathbf R\) 后，\(\hat T_N\) 不进入电子本征问题；\(\hat V_{eN}\) 中的核坐标成为外部参数；\(V_{NN}=E_{NN}(\mathbf R)\) 成为对电子坐标的常数。电子方程通常用

\[
\hat H_e=\hat T_e+\hat V_{ee}+\hat V_{eN}
\]

求得 \(E_a^e\)，而势能面为 \(U_a=E_a^e+E_{NN}\)。常数不改变固定构型下的电子本征函数，却会随构型变化并影响核所见势能面、力和结构比较。

常见错误是把“固定核”说成未作近似的完整电子—核问题，或在比较结构能量时漏掉 \(E_{NN}\)。

## Q5-02

乘积法则给出

\[
\nabla_I^2(\chi_b\Phi_b)
=(\nabla_I^2\chi_b)\Phi_b
+2(\nabla_I\chi_b)\cdot(\nabla_I\Phi_b)
+\chi_b\nabla_I^2\Phi_b.
\]

投影到 \(\Phi_a\) 后定义

\[
\mathbf d_{ab}^I=\langle\Phi_a|\nabla_I\Phi_b\rangle,
\qquad
\tau_{ab}^I=\langle\Phi_a|\nabla_I^2\Phi_b\rangle.
\]

非简并条件下，

\[
\mathbf d_{ab}^I
=\frac{\langle\Phi_a|\nabla_I\hat H_e|\Phi_b\rangle}
{E_b-E_a},
\qquad a\ne b.
\]

小能隙会放大导数耦合，因而单面近似更危险。该式在严格简并点不能除以零；应改用简并子空间或 diabatic 处理。仅说“核重所以 BO 永远成立”遗漏了能隙、核运动尺度和电子态光滑性。

还须区分三步删项。只忽略 \(b\ne a\) 的非对角耦合后，单面方程仍含对角 Berry 连接

\[
\mathbf A_a^I=i\langle\Phi_a|\nabla_I\Phi_a\rangle
\]

和 Born–Huang 修正

\[
\Phi_a^{\mathrm{BH}}
=\sum_I\frac{
\langle\nabla_I\Phi_a|\nabla_I\Phi_a\rangle
-|\langle\Phi_a|\nabla_I\Phi_a\rangle|^2
}{2M_I}.
\]

只有在局部无简并区域选择平行输运规范使 \(\mathbf A_a^I=0\)，并再独立忽略 \(\Phi_a^{\mathrm{BH}}\)，才得到仅含裸核动能和 \(U_a\) 的最简方程。该局部规范不保证全局 Berry 相位消失；简并子空间需要矩阵值连接。完整配方和规范变换见 D-C01.3。

## Q5-03

归一化 determinant 为

\[
\Phi(x_1,x_2)=\frac1{\sqrt2}
[\chi_a(x_1)\chi_b(x_2)-\chi_b(x_1)\chi_a(x_2)].
\]

交换 \(x_1,x_2\) 后括号两项互换，整体变号。范数展开产生两个直接项和两个交叉项；直接项各为 1，交叉项含 \(\langle a|b\rangle\) 而为零，所以范数为 \((1+1)/2=1\)。若 \(\chi_a=\chi_b\)，两项完全抵消，determinant 为零。

## Q5-04

电子坐标上的 Slater 矩阵满足 \(\widetilde M=MU\)，所以

\[
\det\widetilde M=\det M\det U.
\]

unitary 矩阵满足 \(|\det U|=1\)，因此只增加整体相位。占据投影为

\[
\widetilde P=(XU)(XU)^\dagger
=XUU^\dagger X^\dagger=XX^\dagger=P.
\]

若变换混入未占据轨道并改变 \(P\)，新的 determinant 占据了不同子空间，一体密度矩阵和一般可观测量都会改变。仅在完整新占据子空间仍与旧子空间相同时才是规范变化。

## Q5-05

把 \(x'=x\) 后积分，利用 \(\Psi\) 归一化，直接得到 \(\operatorname{Tr}\gamma=N\)。定义中交换 \(x,x'\) 并取复共轭，得到 Hermiticity。对任意 \(f\)，

\[
\langle f|\gamma|f\rangle
=N\int dx_2\cdots dx_N
\left|\int f^*(x)\Psi(x,x_2,\ldots),dx\right|^2\ge0.
\]

所以 \(\gamma\) 半正定。定义的对角就是 \(n(x)\)。一般二体相互作用需要二体约化密度矩阵；1RDM 只保证所有一体算符期望值可由 \(\operatorname{Tr}(a\gamma)\) 得到。

## Q5-06

对正交占据轨道，

\[
\gamma^2
=\sum_{pq}|p\rangle\langle p|q\rangle\langle q|
=\sum_p|p\rangle\langle p|=\gamma.
\]

给定双 determinant 态在四个自旋轨道上的自然占据数均为 \(1/2\)，总和为 2。于是 \(\gamma\) 的这四个本征值是 \(1/2\)，而 \(\gamma^2\) 的本征值是 \(1/4\)，两者不等。该态仍是纯多体态，因此“纯态”不蕴含“1RDM 幂等”；幂等是单 determinant 的更强结构。

## Q5-07

| 维度 | Hartree | HF | KS |
|---|---|---|---|
| 对象 | 可分离轨道乘积 | 单 Slater determinant | 在所需非相互作用可表示域中的密度与辅助体系；常规零温整数占据时可用单 determinant，简并/分数占据时须允许非相互作用系综 |
| 反对称性 | 一般不满足 | determinant 精确满足 | 单 determinant 或系综的各个 determinant 满足，但辅助对象不是一般真实多体态 |
| 有效算符 | 一体项加局域 Coulomb 平均场 | Coulomb 加非局域交换 | 外势、Hartree 与 \(v_{xc}[n]\) |
| 缺失物理 | 交换与相关 | 超出单 determinant 的相关 | 精确 \(E_{xc}\) 未知，实践需近似；可表示性和占据条件不可省略 |
| 能量 | 需扣除 Coulomb 双计数 | 需扣除 \((J-K)\) 双计数 | 必须按所用 KS 能量/自由能泛函组合，不能仅求本征值和 |

共同点是都可能形成自洽有效一体方程；不同点是变分对象和近似内容不同。KS determinant 只是在相应可表示性与整数占据条件下的辅助表示，不是任意相互作用密度的无条件纯态表示，也不是真实相互作用多体波函数。

## Q5-08

\[
J_{ab}=\iint\frac{|\chi_a(x)|^2|\chi_b(x')|^2}{r_{12}},dx,dx',
\]

\[
K_{ab}=\iint\frac{\chi_a^*(x)\chi_b^*(x')
\chi_a(x')\chi_b(x)}{r_{12}},dx,dx'.
\]

令 \(a=b\) 时两式 integrand 相同，所以 \(J_{aa}=K_{aa}\)，同一占据自旋轨道的 HF 自相互作用抵消。对 \(u\alpha\) 与 \(v\beta\)，交换 integrand 的自旋部分含 \(\alpha^*(s)\beta(s)\) 或其共轭，积分为零；Coulomb 项只含各自模平方，自旋积分各为 1，通常不为零。

这不表示 HF 没有任何自相互作用或相关误差；结论只针对同一占据自旋轨道的显式 \(J_{aa}-K_{aa}\)。

## Q5-09

对占据轨道求和：

\[
\sum_p\varepsilon_p
=\sum_p h_{pp}+\sum_{pq}(J_{pq}-K_{pq}).
\]

HF 总能量只有一半的成对和，所以

\[
E_{HF}
=\sum_p\varepsilon_p
-\frac12\sum_{pq}(J_{pq}-K_{pq}).
\]

KS 中交换相关能量与势的关系不是简单的 HF \(J-K\) 半数扣除；有限温度还可能报告自由能、内能或外推零温能量。因此，迁移公式前必须登记理论、占据、smearing/温度和 reported energy functional。

## Q5-10

原陈述至少有以下错误：

1. 固定结构已经采用固定核/BO 层级，不是完整电子—核量子问题；
2. 实践 DFT 使用近似交换相关泛函，不能直接称为精确；
3. 赝势或全电子处理改变 Hamiltonian 的理论与数值对象；
4. 基组、网格、\(k\) 采样和收敛阈值引入离散/数值依赖；
5. 矩阵依赖轨道基、排序、相位、胞位移和 Fourier 约定；
6. KS Hamiltonian 是有效一体算符，不是完整相互作用多体 Hamiltonian；
7. Hamiltonian 矩阵不等于多体波函数，也不等于 1RDM；
8. 本征值和一般不等于总能量；
9. DeepH 的监督目标继承标签理论和表示误差；
10. 网络在训练分布外是否可靠需要单独验证。

不越界的替代表述为：

> 对固定核构型，在明确的电子结构理论、赝势或全电子设置、基/采样/收敛参数及矩阵表示约定下，可以生成自洽有效一体 Hamiltonian 标签。DeepH 学习该固定语义下从结构到 Hamiltonian 矩阵块的映射；它可以减少新结构上重复标签生成的成本，但不会自动恢复精确电子—核多体波函数，也不会消除标签的理论、离散、投影和数值误差。

本题的外部动作边界还必须定位到正文 5.5.4：M8 前不安装 DeepH 本体、不下载正式训练数据、不生成正式 DFT 标签，也不选择材料/后端/实践版本；准备进入 M8 时暂停集中决策，M8 冻结后在 M9 外部动作前再次取得明确授权。

## 错误诊断汇总

- 把固定核参数化说成删除全部近似：回到 Q5-01/Q5-02；
- 把 determinant 等同于任意反对称态：回到 Q5-03/Q5-06；
- 把轨道规范变化当作态变化：检查占据投影，见 Q5-04；
- 把密度、1RDM 与 Hamiltonian 混为同一矩阵：回到 Q5-05/Q5-10；
- 把交换等同于相关：对照 Q5-07/Q5-08；
- 把自洽本征值和当作总能量：执行 Q5-09；
- 把 DeepH 输出称为基组无关精确多体对象：按 Q5-10 的对象链逐层纠正。
