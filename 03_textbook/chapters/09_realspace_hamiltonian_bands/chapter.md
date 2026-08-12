# 第 9 章　实空间 Hamiltonian、overlap 与能带

## 9.0 目标、依赖与边界

本章把第 3 章的 Hermitian-definite 广义本征问题与第 4 章的周期 Fourier 对组合为可执行对象链：

\[
\{H(\mathbf R),S(\mathbf R)\}
\longrightarrow
\{H(\mathbf k),S(\mathbf k)\}
\longrightarrow
\{E_{n\mathbf k},c_{n\mathbf k}\}.
\]

所有相位、bra/ket 方向和轨道中心规范服从[阶段 B 统一约定](../../stageB_conventions.md)。来源边界见[资料包](sources.md)，逐式推导见[实空间到能带推导](../../../04_derivations/stageB/09_realspace_to_bands.md)。本章只使用合成一维双轨道模型，不安装 DeepH、不下载正式数据、不选择材料或 DFT 后端。

## 9.1 周期局域基中的矩阵块

复合指标 \(a=(i,\mu)\)、\(b=(j,\nu)\) 同时记录原胞内原子与轨道。定义

\[
H_{ab}(\mathbf R)=\langle\phi_{a\mathbf0}|\hat H|\phi_{b\mathbf R}\rangle,
\qquad
S_{ab}(\mathbf R)=\langle\phi_{a\mathbf0}|\phi_{b\mathbf R}\rangle.
\]

对每个 \(\mathbf R\)，两者形状均为 \(M\times M\)；\(H\) 具有能量单位，\(S\) 无量纲。轨道排序、轨道相位、单位和 \(\mathbf R\) 方向必须随数据一并登记。

证据类型：`DIRECT_DERIVATION`。Hermiticity 与 Gram 定义给出

\[
H(\mathbf R)^\dagger=H(-\mathbf R),
\qquad
S(\mathbf R)^\dagger=S(-\mathbf R).
\]

\(\mathbf R=\mathbf0\) 块自身 Hermitian；非零块一般不必自身 Hermitian，而是与负平移块成对。

## 9.2 从实空间到 \(k\) 空间

### 9.2.1 矩阵组装

证据类型：`DIRECT_DERIVATION`。按冻结约定，

\[
H(\mathbf k)=\sum_{\mathbf R}e^{i\mathbf k\cdot\mathbf R}H(\mathbf R),
\qquad
S(\mathbf k)=\sum_{\mathbf R}e^{i\mathbf k\cdot\mathbf R}S(\mathbf R).
\]

完整共轭配对推出两者在每个 \(\mathbf k\) 上 Hermitian。代码应直接记录

\[
\|H(\mathbf k)-H(\mathbf k)^\dagger\|_F,
\qquad
\|S(\mathbf k)-S(\mathbf k)^\dagger\|_F,
\]

而不是先静默对称化。

### 9.2.2 正定性与广义本征

Hermitian 不等于正定。对全部受测 \(\mathbf k\) 必须确认

\[
\lambda_{\min}(S(\mathbf k))>0.
\]

随后求解

\[
H(\mathbf k)C(\mathbf k)
=S(\mathbf k)C(\mathbf k)E(\mathbf k),
\qquad
C^\dagger S C=I.
\]

能带是排序后的广义本征值集合。忽略 \(S(\mathbf k)\) 等价于把非正交基误当成正交基，一般会改变色散和能隙。

### 9.2.3 残差与简并

每个本征对都应报告归一化残差

\[
r_{n\mathbf k}=
\frac{\|Hc_n-E_nSc_n\|_2}
{(\|H\|_2+|E_n|\|S\|_2)\|c_n\|_2}.
\]

简并处单个本征矢和逐带标签不唯一；跨 \(k\) 跟踪应按能量簇、投影或子空间重叠，而不是仅按数组列号。

## 9.3 从矩阵质量解释能带

能带比较必须固定 \(k\) 路径、能量零点、目标能窗和带匹配规则。全带最大误差、目标能窗误差、带隙和带宽回答不同问题，不能互相替代。

若矩阵扰动为 \(\Delta H,\Delta S\)，精确本征对在近似矩阵束中的残差源为

\[
q=(\Delta H-E\Delta S)c.
\]

证据类型：`DIRECT_DERIVATION`。该式说明 overlap 误差按能量 \(E\) 与 Hamiltonian 误差耦合。矩阵范数小只是后向输入规模信息；前向能带误差还取决于 \(S\) 条件数、谱隙和简并结构。

## 9.4 Fourier 逆变换与截断

### 9.4.1 完整离散逆变换

在同一完整离散对上，

\[
H(\mathbf R)=\frac1N\sum_{\mathbf k}e^{-i\mathbf k\cdot\mathbf R}H(\mathbf k),
\qquad
S(\mathbf R)=\frac1N\sum_{\mathbf k}e^{-i\mathbf k\cdot\mathbf R}S(\mathbf k).
\]

该逆变换需要完整矩阵，而不是只有能带本征值。只保存 \(E_{n\mathbf k}\) 会丢失本征矢和规范信息，通常无法唯一恢复矩阵块。

### 9.4.2 实空间截断

删除 \(|\mathbf R|>R_c\) 的块会改变被 Fourier 变换的矩阵函数。若按 \(\pm\mathbf R\) 成对删除，Hermiticity 可以保持，但能带仍会改变；增加同一截断模型的 \(k\) 点只能更密地采样该错误模型，不能恢复被删块。

若输入缺少共轭块，不应先用

\[
H\leftarrow(H+H^\dagger)/2
\]

隐藏错误。应先报告缺块位置和反 Hermitian 残差，再把任何修复作为改变数据的显式操作。

## 9.5 一维双轨道贯穿例题

[例题](examples.md)固定 \(R=0,\pm1,\pm2\) 的复矩阵块，在 64 点循环网格上验证：

- 全 \(k\) Hermiticity 与 \(S(k)\succ0\)；
- 广义本征残差和 \(S\)-正交性；
- 完整矩阵块逆变换；
- 删除 \(\pm2\) 的截断能带误差；
- 忽略 \(S\)、删除单个共轭块和单边规范变换三类失败。

这些模型为 `PEDAGOGICAL`，数值不得外推为真实材料的跃迁范围或误差大小。

## 9.6 DeepH 对象接口与授权边界

DH-01 支持的原始 DeepH 对象分工是：模型预测实空间 Hamiltonian \(H(\mathbf R)\)，overlap \(S(\mathbf R)\) 则由局域基函数重叠以较低代价计算；两者随后分别组装为 \(H(\mathbf k),S(\mathbf k)\)，再求解广义本征问题得到能带。该陈述只界定原始论文中的工作流，不自动推广为现代软件的任务分工，也不据此推断具体字段名、轨道顺序、单位或相位。任何实际软件输出必须先显式映射到本教材约定。

M8 前继续禁止安装 DeepH 本体、下载正式训练数据、生成正式 DFT 标签或隐含选择材料体系与 DFT 后端。本章的全部实现只使用固定 Python 用户态依赖和合成矩阵。

## 9.7 自学检查

1. 为什么非零 \(H(\mathbf R)\) 块不必自身 Hermitian？
2. 为什么 \(S(\mathbf k)\) Hermitian 仍不足以调用定广义本征求解？
3. 为什么只有能带本征值不能唯一逆变换出 \(H(\mathbf R)\)？
4. 成对截断为何保持 Hermiticity却仍改变能带？
5. 为什么增加 \(k\) 点不能修复实空间截断？

[分层练习](../../../06_exercises/02-stageB/09_realspace_bands/problem/readme.md)与[参考解答](../../../06_exercises/02-stageB/09_realspace_bands/solution/readme.md)逐项覆盖上述链条；自动批量实现将在 M4-07 固化。
