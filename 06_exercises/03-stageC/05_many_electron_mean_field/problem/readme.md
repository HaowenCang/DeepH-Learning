# 第 5 章练习：多电子问题与平均场

所有题目均可由第 5 章正文、例题和 D-C01—D-C02 推导包独立完成。题目不要求真实 DFT/DeepH 后端、材料结构或外部数据。

## Q5-01 Hamiltonian 项与固定核边界

写出非相对论电子—核 Coulomb Hamiltonian 的五类项。固定所有核坐标后，说明哪些项被删除、哪些项成为参数或常数，并区分电子能量 \(E_a^{\mathrm e}\) 与势能面 \(U_a\)。

## Q5-02 BO 导数耦合

从

\[
\Psi(\mathbf r,\mathbf R)=\sum_b\chi_b(\mathbf R)\Phi_b(\mathbf r;\mathbf R)
\]

出发，对 \(\nabla_I^2(\chi_b\Phi_b)\) 使用乘积法则，指出一阶和二阶导数耦合。解释为什么小电子能隙会使单势能面 BO 近似更危险。

## Q5-03 两电子 determinant

对两个正交归一自旋轨道 \(\chi_a\)、\(\chi_b\)，写出归一化两电子 Slater determinant，证明交换反对称性和归一化。若 \(\chi_a=\chi_b\)，结果是什么？

## Q5-04 occupied-unitary 变换

设 \(N\) 条占据轨道作 \(\widetilde X=XU\)，其中 \(U\) unitary。证明新 determinant 与旧 determinant 只差 \(\det U\)，并证明占据投影

\[
P=XX^\dagger
\]

不变。说明混合占据与未占据子空间为什么一般会改变物理态。

## Q5-05 1RDM 的基本性质

从 1RDM 定义证明：

1. \(\operatorname{Tr}\gamma=N\)；
2. \(\gamma(x,x')=\gamma^*(x',x)\)；
3. \(\langle f|\gamma|f\rangle\ge0\)；
4. \(n(x)=\gamma(x,x)\)。

指出计算一般二体相互作用期望值还缺少什么对象。

## Q5-06 幂等性与反例

证明单 determinant 的

\[
\gamma=\sum_{p=1}^{N}|\chi_p\rangle\langle\chi_p|
\]

满足 \(\gamma^2=\gamma\)。随后分析

\[
|\Psi\rangle=\frac1{\sqrt2}
(|a\alpha,a\beta\rangle+|b\alpha,b\beta\rangle)
\]

的自然占据数，说明为什么“纯态 1RDM 必幂等”是错误命题。

## Q5-07 Hartree、HF 与 KS 对象比较

按“变分或构造对象、反对称性、有效势/算符、缺失物理、总能量口径”五个维度比较 Hartree、HF 和 KS。不得仅用“都是平均场”作答。

## Q5-08 Coulomb、交换与自旋

对两个占据自旋轨道定义 \(J_{ab}\) 与 \(K_{ab}\)。证明 \(J_{aa}=K_{aa}\)。若 \(\chi_a=u\alpha\)、\(\chi_b=v\beta\)，说明为什么 \(K_{ab}=0\)，以及为什么 \(J_{ab}\) 一般仍非零。

## Q5-09 HF 本征值双计数

由

\[
\varepsilon_p=h_{pp}+\sum_q(J_{pq}-K_{pq})
\]

推出 HF 总能量与占据本征值和的关系。说明为什么该关系不能直接搬到任意 KS 泛函或有限温度自由能，而不登记相应能量口径。

## Q5-10 端到端对象审计

审查以下陈述：

> 对固定结构运行 DFT 得到 Hamiltonian，因此该矩阵就是材料的精确多体 Hamiltonian；DeepH 学会矩阵后也学会了精确波函数和总能量。

至少指出六个对象或近似层级错误，并给出一条不越界的替代表述。替代表述必须包含：固定核、理论层级、数值/表示依赖、网络预测对象及其不能自动消除的误差。

## 验收方式

材料建设模式不要求学习者提交闭卷作答。阶段审计检查：

- Q5-01—Q5-10 是否均有逐题参考解答；
- 每个公式是否声明适用条件；
- Q5-02、Q5-04、Q5-06、Q5-09 是否有可复核推导；
- Q5-10 是否覆盖从多体问题到 DeepH 标签的完整对象链；
- 参考解答是否明确列出常见误区和失败边界。
