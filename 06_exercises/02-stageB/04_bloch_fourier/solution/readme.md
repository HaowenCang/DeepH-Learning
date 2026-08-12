# 第 4 章练习参考解答

## Q4-01

写 \(\mathbf G=\sum_i m_i\mathbf b_i\)、\(\mathbf R=\sum_j n_j\mathbf a_j\)，则

\[
\mathbf G\cdot\mathbf R
=2\pi\sum_i m_i n_i,
\]

所以指数为 1。有限集合为

\[
\mathcal R_N=\left\{\sum_i n_i\mathbf a_i:0\le n_i<N_i\right\},
\quad
\mathcal K_N=\left\{\sum_i\frac{m_i}{N_i}\mathbf b_i:0\le m_i<N_i\right\}.
\]

每个方向各有 \(N_i\) 个取值，故两集合均有 \(N=\prod_iN_i\) 个元素。

## Q4-02

令 \(z=e^{2\pi i(n-n')/N}\)。若 \(n=n'\pmod N\)，每项为 1，平均为 1；否则 \(z\ne1\) 且 \(z^N=1\)，所以

\[
\sum_{m=0}^{N-1}z^m=\frac{1-z^N}{1-z}=0.
\]

右侧是有限集合上的 Kronecker delta。Dirac delta 属于连续变量积分恒等式，量纲和归一化均不同。

## Q4-03

坐标表象中

\[
(\hat T_R\psi_k)(x)=\psi_k(x-R)=e^{-ikR}\psi_k(x).
\]

把 \(x\) 替换为 \(x+R\)，得 \(\psi_k(x)=e^{-ikR}\psi_k(x+R)\)，即

\[
\psi_k(x+R)=e^{ikR}\psi_k(x).
\]

负号属于主动平移算符，正号属于坐标点向前移动；混淆二者会造成伪相位冲突。

## Q4-04

直接作用平移算符并令 \(R'=R+T\)：

\[
\begin{aligned}
\hat T_T|\phi_{ak}\rangle
&=\frac1{\sqrt N}\sum_R e^{ikR}|\phi_{a,R+T}\rangle\\
&=e^{-ikT}|\phi_{ak}\rangle.
\end{aligned}
\]

平移不变性给出 \(\langle aR|\hat H|bR'\rangle=H_{ab}(R'-R)\)。代入两组 Bloch 和，令 \(D=R'-R\)，对 \(R\) 的求和产生 \(\delta_{kk'}\)，剩余为

\[
H_{ab}(k)=\sum_D e^{ikD}H_{ab}(D).
\]

## Q4-05

代入正变换：

\[
\begin{aligned}
\frac1N\sum_k e^{-ikR}H(k)
&=\sum_{R'}\left[\frac1N\sum_k e^{ik(R'-R)}\right]H(R')\\
&=H(R).
\end{aligned}
\]

若逆变换也使用正号，括号变为选择 \(R'=-R\) 的 delta，通常重建 \(H(-R)\) 而非 \(H(R)\)；在含复相位块时差异可被直接检出。

## Q4-06

由 Hermiticity，

\[
H_{ab}(R)^*
=\langle\phi_{bR}|\hat H|\phi_{a0}\rangle.
\]

整体平移 \(-R\) 得 \(H_{ba}(-R)\)。所以 \(H(R)^\dagger=H(-R)\)，并有

\[
\begin{aligned}
H(k)^\dagger
&=\sum_R e^{-ikR}H(R)^\dagger\\
&=\sum_R e^{-ikR}H(-R)=H(k).
\end{aligned}
\]

\(S\) 的 Gram 定义给出同样的 Hermiticity；正定性还要求任意非零系数的 \(c^\dagger S(k)c>0\)，不能由共轭对称单独推出。

## Q4-07

正变换给出

\[
H(k)=\varepsilon+te^{i(k+\varphi)}+te^{-i(k+\varphi)}
=\varepsilon+2t\cos(k+\varphi).
\]

删除负平移块后，虚部为 \(t\sin(k+\varphi)\)，一般非零。一维矩阵 Hermitian 等价于实数，因此失败来自缺失 \(-R\) 共轭块。

## Q4-08

令 \(U_{ab}=\delta_{ab}e^{ik\tau_a}\)，则列基 \(\bar\Phi=\Phi U\)。按矩阵元和同一态关系，

\[
\bar H=U^\dagger HU,
\quad
\bar S=U^\dagger SU,
\quad
\bar c=U^{-1}c.
\]

因此

\[
\bar H\bar c=U^\dagger Hc=E U^\dagger Sc=E\bar S\bar c,
\]

且 \(\bar c^\dagger\bar S\bar c=c^\dagger Sc\)。只变换 \(H\) 会破坏同一基下矩阵束的合同关系，不能用“规范自由”解释所得谱差。

## Q4-09

Cell-phase 中

\[
|\phi_{a,k+G}\rangle
=\frac1{\sqrt N}\sum_R e^{ikR}e^{iGR}|\phi_{aR}\rangle
=|\phi_{ak}\rangle.
\]

中心规范中则有

\[
|\bar\phi_{a,k+G}\rangle
=e^{iG\tau_a}|\bar\phi_{ak}\rangle.
\]

能量严格倒格周期。Cell-phase 矩阵在完整定义下也可严格周期；中心规范矩阵和系数先由

\[
D_G=\operatorname{diag}(e^{iG\tau_a})
\]

联系。对非简并带，数值本征矢还可带任意整体相位，比较前需要相位对齐；简并处允许子空间内任意幺正混合，只能比较投影算符或对齐整个简并子空间，不能要求逐带逐元素相等。

## Q4-10

固定 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0，例题脚本得到：

\[
\max_R|H_{\mathrm{rec}}(R)-H(R)|\approx4.1\times10^{-16},
\]

\[
\max_k|\operatorname{Im}H(k)|\approx1.3\times10^{-15}.
\]

同号逆变换最大误差约 \(0.233651\)，缺少负平移块后的最大虚部约 \(0.277995\)，均超过 \(10^{-2}\) 失败阈值。同步中心规范的最大谱差低于 \(10^{-12}\)，只变换 \(H\) 的谱差约 \(0.0822893>10^{-2}\)。

这些断言分别定位相位闭合、Hermiticity 和合同变换错误；不能把它们合并描述为单一“数值误差”。完整可执行命令见第 4 章例题末尾。

## 错误诊断汇总

| 现象 | 机制 | 修复 |
|---|---|---|
| 主动平移与坐标 Bloch 条件符号冲突 | 混淆 \(\psi(x-R)\) 与 \(\psi(x+R)\) | 固定平移算符定义后再比较 |
| 逆变换恢复 \(-R\) 块 | 正逆指数同号 | 使用冻结的负号逆变换 |
| \(H(k)\) 出现虚部或非 Hermitian 部分 | 缺失 \(-R\) 共轭块 | 成对维护 \(H(R)^\dagger=H(-R)\) |
| 规范变换后谱改变 | 只变 \(H\) 或系数方向错误 | 同步变换 \(H,S,c\) |
| Hermitian 的 \(S(k)\) 被直接判为合法 | 遗漏正定条件 | 检查最小特征值或 Cholesky |
