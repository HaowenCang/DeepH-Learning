# 01.02 核心推导题

所有推导必须先声明矩阵维数、Hermiticity、\(S\) 的正定性、Fourier 符号和旋转的主动/被动约定。只写最终公式不构成通过。

### D1 从基展开得到广义本征问题

从 \(|\psi_n\rangle=\sum_\nu c_{\nu n}|\phi_\nu\rangle\) 与 \(\hat H|\psi_n\rangle=E_n|\psi_n\rangle\) 出发，推导 \(Hc_n=E_nSc_n\)，并给出归一化条件。

### D2 一致基变换的谱不变性

设 \(A\) 可逆，\(H'=A^\dagger HA\)、\(S'=A^\dagger SA\)。用特征行列式证明广义本征值不变，并说明为何只变换 \(H\) 是错误操作。

### D3 实空间与倒空间 Hermiticity

采用

\[
H(\mathbf k)=\sum_{\mathbf R}e^{i\mathbf k\cdot\mathbf R}H(\mathbf R)
\]

的约定，从 \(H(\mathbf R)^\dagger=H(-\mathbf R)\) 推出 \(H(\mathbf k)^\dagger=H(\mathbf k)\)。写出反变换成立所需的离散采样条件。

### D4 轨道块旋转协变

在明确的被动基变换约定下，推导两个原子轨道子空间之间矩阵块的变换式。说明为什么标量不变网络不能仅凭输出若干数字就自动保证该关系。

### D5 简单广义本征值的一阶扰动

对 \(Hc=ESc\)、\(c^\dagger Sc=1\) 求微分，推导

\[
\delta E=c^\dagger(\delta H-E\delta S)c,
\]

并列出至少四种不能直接按该标量公式解释的情形。

## 最低通过标准

每题的中间等式可复核；D2 同时变换 \(H,S\)；D3 的相位符号前后一致；D4 声明表示矩阵方向；D5 不把局部一阶式写成全局误差界。

