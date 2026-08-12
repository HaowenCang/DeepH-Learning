# 阶段 B 综合问题：非正交周期矩阵到能带

本综合题用于验证材料是否覆盖完整对象链，不要求学习者提交个人作答。所有问题均有对应参考解答、数值阈值、失败机制和自动测试入口。

采用一维晶格 \(a=1\) 和两个局域轨道，定义

\[
H(0)=\begin{pmatrix}0.2&0.3\\0.3&1.2\end{pmatrix},
\quad
H(1)=\begin{pmatrix}-0.4&0.10\\0.05&-0.2\end{pmatrix},
\quad
H(2)=\begin{pmatrix}-0.06&0.02i\\0.01&-0.03\end{pmatrix},
\]

\[
S(0)=I,
\quad
S(1)=\begin{pmatrix}0.08&0.02\\0.01&0.05\end{pmatrix},
\quad
S(2)=\begin{pmatrix}0.01&0.005i\\0.002&0.008\end{pmatrix},
\]

并令 \(H(-R)=H(R)^\dagger\)、\(S(-R)=S(R)^\dagger\)。Fourier 约定为

\[
H(k)=\sum_R e^{+ikR}H(R),
\qquad
S(k)=\sum_R e^{+ikR}S(R).
\]

## C-B01 对象与共轭配对

说明 \(H_{ab}(R)\)、\(S_{ab}(R)\) 的 bra/ket 方向、形状和单位。逐指标推导 \(H(R)^\dagger=H(-R)\)，并说明为什么 \(H(1)\) 不需要自身 Hermitian。列出实际数据至少还需登记的四类语义元数据。

## C-B02 \(k\) 空间结构与正定性

由共轭配对证明全部 \(k\) 上的 \(H(k),S(k)\) Hermitian。计算 \(k=0,\pi\) 的矩阵；说明在调用 Hermitian-definite 广义求解前还必须检查什么，以及 Hermiticity 为什么不能替代该检查。

## C-B03 广义本征、归一化与误差口径

从局域基投影或 Rayleigh 商推出 \(H(k)c=E S(k)c\)。写出 \(S\)-归一化条件和逐本征对归一化 2-范数残差。计算 \(k=0,\pi\) 的广义谱，并说明简并处为何应比较子空间而非未经规范固定的逐列向量。

## C-B04 一般可逆与 unitary 基变换

对可逆矩阵 \(A\) 推导

\[
H'=A^\dagger HA,
\quad S'=A^\dagger SA,
\quad c'=A^{-1}c,
\]

并证明广义谱不变。再用 \(H=\operatorname{diag}(0,2)\)、\(S=I\)、\(E=0\)、\(c=(1,1)^T\)、\(A=\operatorname{diag}(0.1,1)\) 判断冻结的 Euclidean 归一化残差是否保持。说明 unitary 情形与一般可逆情形的边界。

## C-B05 Bloch/Fourier 闭合与中心规范

从有限 BvK 角色正交关系写出完整离散逆变换及 \(1/N\) 的位置。对

\[
U(k)=\operatorname{diag}(1,e^{0.37ik})
\]

证明同步变换 \(\bar H=U^\dagger HU\)、\(\bar S=U^\dagger SU\)、\(\bar c=U^{-1}c\) 保持能带和冻结残差；解释只变 \(H\) 的失败机制。

## C-B06 截断与采样

在完整循环网格上写出恢复 \(H(R),S(R)\) 的算法。比较以下三种操作：成对删除 \(R=\pm2\)、只删除 \(R=-2\)、把截断模型的 \(k\) 点从 64 增加到 128。分别判断 Hermiticity、模型内容和带差是否应恢复，并给出可执行判据。

## C-B07 失败诊断

对以下现象给出“对象检查—结构检查—数值检查—结论边界”的诊断链：

1. 忽略 \(S(k)\) 后带差约为 \(0.18\)；
2. 删除 \(H(-2)\) 后反 Hermitian 残差约为 \(0.138\)；
3. \(S\) 条件数增大时 \(S\)-正交残差上升，但归一化后向残差仍小。

说明哪些结果可以判定实现错误，哪些只表明数值敏感性增加，哪些还需要谱隙或目标能窗信息才能解释逐带误差。

## C-B08 可复现验收与来源边界

运行阶段 B JSON CLI 的默认配置和第二配置，核对 T-B01—T-B10、版本、种子、维数、\(N_k\)、容差、预期失败与退出码。说明这些合成结果能验证什么、不能外推什么；说明 M8 前对 DeepH、正式数据、DFT 标签、材料和后端的授权边界。

[参考解答](../solution/readme.md)给出逐项推导、数值和验证入口。解析推导总索引见[阶段 B 推导包](../../../../04_derivations/stageB/README.md)，自动实现见[阶段 B 代码说明](../../../../05_code_exercises/stageB_periodic_nonorthogonal/README.md)。
