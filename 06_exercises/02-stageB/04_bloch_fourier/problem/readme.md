# 第 4 章练习：周期性、Bloch 定理与 Fourier 约定

这些练习检验材料的完备性、可自学性和可验证性，不要求学习者提交个人作答。每题均有一一对应的参考解答和错误判据。

## Q4-01 直接晶格、倒格子与有限网格

由 \(\mathbf b_i\cdot\mathbf a_j=2\pi\delta_{ij}\) 证明 \(e^{i\mathbf G\cdot\mathbf R}=1\)。对含 \(N_i\) 个原胞的 Born–von Karman 超胞，写出允许的 \(\mathbf R\) 和 \(\mathbf k\) 集合，并说明总点数为何相同。

## Q4-02 有限角色正交关系

在一维取 \(R_n=na\)、\(k_m=2\pi m/(Na)\)。用有限几何级数证明

\[
\frac1N\sum_{m=0}^{N-1}e^{ik_m(R_n-R_{n'})}
=\delta_{n,n'\bmod N}.
\]

说明为什么这里不能把右侧直接写成连续 Dirac delta。

## Q4-03 主动平移与 Bloch 符号

采用 \((\hat T_R\psi)(x)=\psi(x-R)\)。从 \(\hat T_R|\psi_k\rangle=e^{-ikR}|\psi_k\rangle\) 推导 \(\psi_k(x+R)=e^{ikR}\psi_k(x)\)。解释两个指数符号为何相反。

## Q4-04 局域轨道 Bloch 和

对

\[
|\phi_{ak}\rangle=\frac1{\sqrt N}\sum_R e^{ikR}|\phi_{aR}\rangle
\]

证明 \(\hat T_T|\phi_{ak}\rangle=e^{-ikT}|\phi_{ak}\rangle\)。再由平移不变性证明不同 \(k\) 块之间的 Hamiltonian 矩阵元为零，并推导 \(H(k)=\sum_R e^{ikR}H(R)\)。

## Q4-05 Fourier 逆变换

使用 Q4-02 的正交关系，从正变换推导

\[
H(R)=\frac1N\sum_k e^{-ikR}H(k).
\]

指出若逆变换也使用 \(e^{+ikR}\)，重建对象通常发生什么变化。

## Q4-06 实空间厄米关系

从

\[
H_{ab}(R)=\langle\phi_{a0}|\hat H|\phi_{bR}\rangle
\]

和 \(\hat H=\hat H^\dagger\) 推导 \(H_{ab}(R)^*=H_{ba}(-R)\)，再证明 \(H(k)=H(k)^\dagger\)。说明为什么同样的证明只能给出 \(S(k)\) Hermitian，不能自动给出正定性。

## Q4-07 单轨道复跃迁链

取 \(H(0)=\varepsilon\)、\(H(1)=te^{i\varphi}\)、\(H(-1)=te^{-i\varphi}\)。求 \(H(k)\)，证明其为实数。删除 \(H(-1)\) 后计算反 Hermitian 或虚部，并解释失败机制。

## Q4-08 轨道中心规范

由

\[
|\bar\phi_{ak}\rangle=e^{ik\tau_a}|\phi_{ak}\rangle
\]

推导 \(\bar H=U^\dagger HU\)、\(\bar S=U^\dagger SU\)、\(\bar c=U^{-1}c\)，证明广义谱和态范数不变。说明只变换 \(H\) 为何不是合法规范变换。

## Q4-09 \(k+G\) 与系数周期性

分别在 cell-phase 和含轨道中心相位的基中推导 \(k\to k+G\) 的基变换。判断能量、矩阵和系数中哪些量严格周期，哪些量只在规范变换意义下等价。

## Q4-10 确定性有限 DFT 复算

独立复算[第 4 章例题](../../../../03_textbook/chapters/04_periodicity_bloch_reciprocal/examples.md)中的 \(N=8\) 模型和两轨道规范模型。至少断言：正反变换误差、正确 \(H(k)\) 虚部、同号逆变换失败、缺共轭块失败、同步规范谱不变、只变 \(H\) 的谱差。记录全部阈值和固定环境版本。
