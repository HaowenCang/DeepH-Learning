# D-B06：从实空间矩阵块到广义本征能带

## 1. 对象、条件与单位

证据类型：来源对象配合 `DIRECT_DERIVATION`。

复合轨道指标为 \(a=(i,\mu)\)、\(b=(j,\nu)\)，每个原胞含 \(M\) 个轨道。冻结

\[
H_{ab}(\mathbf R)=\langle\phi_{a\mathbf0}|\hat H|\phi_{b\mathbf R}\rangle,
\qquad
S_{ab}(\mathbf R)=\langle\phi_{a\mathbf0}|\phi_{b\mathbf R}\rangle.
\]

因此 \(H(\mathbf R),S(\mathbf R)\in\mathbb C^{M\times M}\)。\(H\) 具有能量单位，\(S\) 无量纲；轨道排序、相位和 \(\mathbf R\) 方向属于数据语义的一部分。

## 2. 共轭配对与 \(k\) 空间组装

证据类型：`DIRECT_DERIVATION`。

Hermiticity 与 Gram 定义要求

\[
H(\mathbf R)^\dagger=H(-\mathbf R),
\qquad
S(\mathbf R)^\dagger=S(-\mathbf R).
\]

按阶段 B 约定组装

\[
H(\mathbf k)=\sum_{\mathbf R}e^{i\mathbf k\cdot\mathbf R}H(\mathbf R),
\qquad
S(\mathbf k)=\sum_{\mathbf R}e^{i\mathbf k\cdot\mathbf R}S(\mathbf R).
\]

完整共轭配对推出 \(H(\mathbf k)=H(\mathbf k)^\dagger\)、\(S(\mathbf k)=S(\mathbf k)^\dagger\)。标准主线还要求

\[
S(\mathbf k)\succ0
\]

对全部受测 \(\mathbf k\) 成立；应报告最小特征值或 Cholesky 成功性，而不能用 Hermiticity 代替。

## 3. 每个 \(k\) 点的广义本征问题

证据类型：`DIRECT_DERIVATION`；Hermitian-definite 算法类别由 FND-02—FND-04 锚定。

对每个 \(\mathbf k\)，求解

\[
H(\mathbf k)C(\mathbf k)
=S(\mathbf k)C(\mathbf k)E(\mathbf k),
\]

其中 \(C\in\mathbb C^{M\times M}\)，\(E=\operatorname{diag}(E_1,\ldots,E_M)\)，并规范化为

\[
C(\mathbf k)^\dagger S(\mathbf k)C(\mathbf k)=I.
\]

归一化残差为

\[
r_n(\mathbf k)=
\frac{\|H(\mathbf k)c_n-E_nS(\mathbf k)c_n\|_2}
{\bigl(\|H(\mathbf k)\|_2+|E_n|\|S(\mathbf k)\|_2\bigr)\|c_n\|_2}.
\]

简并或近简并处逐列本征矢与逐带排序不稳定，应比较分离能带簇的投影或子空间角度。

## 4. 完整离散逆变换

证据类型：`DIRECT_DERIVATION`。

在同一完整 \(\mathcal R_N/\mathcal K_N\) 对上，

\[
H(\mathbf R)=\frac1N\sum_{\mathbf k}e^{-i\mathbf k\cdot\mathbf R}H(\mathbf k),
\qquad
S(\mathbf R)=\frac1N\sum_{\mathbf k}e^{-i\mathbf k\cdot\mathbf R}S(\mathbf k).
\]

有限角色正交关系保证精确恢复原块。若只保存本征值而不保存完整 \(H(\mathbf k),S(\mathbf k)\)，一般不能唯一反演矩阵块：本征值丢失本征矢和规范信息。

## 5. 截断、采样和“重厄米化”

证据类型：定义后的 `DIRECT_DERIVATION` 与 `PEDAGOGICAL` 故障模型。

实空间截断定义为

\[
H_{R_c}(\mathbf R)=
\begin{cases}
H(\mathbf R),&|\mathbf R|\le R_c,\\
0,&|\mathbf R|>R_c,
\end{cases}
\]

\(S\) 同理。若按完整 \(\pm\mathbf R\) 对成对删除，Hermiticity 可保持，但 \(H(\mathbf k),S(\mathbf k)\) 和能带已经改变。增加同一截断模型的 \(k\) 点只能更密地采样改变后的函数，不能恢复被删除的块。

若输入缺少共轭块，事后使用

\[
H(\mathbf k)\leftarrow\frac12\bigl(H(\mathbf k)+H(\mathbf k)^\dagger\bigr)
\]

会隐藏数据错误并改变矩阵。诊断阶段应先报告反 Hermitian 残差和缺失块；只有在明确声明修复策略和误差影响后才能重厄米化。

## 6. 同步规范与轨道重排

证据类型：`DIRECT_DERIVATION`。

对任意逐 \(\mathbf k\) 可逆基变换 \(U(\mathbf k)\)，

\[
\bar H=U^\dagger HU,
\qquad
\bar S=U^\dagger SU,
\qquad
\bar C=U^{-1}C.
\]

同步变换保持广义谱、精确广义本征方程和 \(S\)-正交性。若原基中的残差向量为

\[
r=Hc-ESc,
\]

则新基中的残差向量满足 \(\bar r=U^\dagger r\)。因此任意可逆 \(U\) 只保证“零残差仍为零”以及残差向量的协变关系；第 3 节按 Euclidean 2-范数定义的归一化残差标量一般不保持不变，因为 \(\|U^\dagger r\|_2\)、\(\|U^\dagger HU\|_2\)、\(\|U^\dagger SU\|_2\) 和 \(\|U^{-1}c\|_2\) 都可能改变。只有 \(U\) 为 unitary 时，该归一化 Euclidean 残差保持不变。轨道重排、单轨道纯相位和轨道中心相位规范均属于 unitary 特例；只作用于行、只作用于 \(H\) 或使用不同轨道排序会破坏矩阵束等价性。

## 7. 矩阵误差与能带误差边界

证据类型：第 3 章误差链的 `DIRECT_DERIVATION` 应用。

若近似矩阵为 \(H+\Delta H,S+\Delta S\)，将精确本征对 \((E,c)\) 代入近似矩阵束，其一阶残差源为

\[
q=(\Delta H-E\Delta S)c.
\]

因此 \(H\) 与 \(S\) 的误差按能量 \(E\) 耦合。矩阵元素误差小并不自动保证目标能窗内逐带误差小；谱隙、\(S\) 条件数、简并和带匹配都会影响前向解释。比较能带时至少应登记 \(k\) 路径、带簇匹配、能量零点和目标能窗。

## 8. 失败边界与验证入口

- 缺少 \(-\mathbf R\) 共轭块：\(k\) 空间 Hermiticity 失败；
- 忽略 \(S(\mathbf k)\)：改变非正交问题，能带一般错误；
- \(S(\mathbf k)\) 非正定：标准广义求解器必须拒绝；
- 正逆 Fourier 相位不闭合：矩阵块重建失败；
- 成对截断虽保持 Hermiticity，但能带仍可能显著改变；
- 逐带比较跨越简并：排序标签可能跳变，应改用子空间或谱集合。

固定双轨道模型、逆变换、截断和失败断言见第 9 章 `examples.md`；批量随机与 JSON 验收属于 M4-07。
