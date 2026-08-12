# 01.02 核心推导题参考解答

## D1 从基展开得到广义本征问题

左乘 \(\langle\phi_\mu|\) 得

\[
\sum_\nu\langle\phi_\mu|\hat H|\phi_\nu\rangle c_{\nu n}
=E_n\sum_\nu\langle\phi_\mu|\phi_\nu\rangle c_{\nu n}.
\]

定义 \(H_{\mu\nu}=\langle\phi_\mu|\hat H|\phi_\nu\rangle\) 与 \(S_{\mu\nu}=\langle\phi_\mu|\phi_\nu\rangle\)，便得到 \(Hc_n=E_nSc_n\)。当基线性无关时 \(S\succ0\)；厄米定问题的本征矢可选为

\[
c_m^\dagger Sc_n=\delta_{mn}.
\]

若基线性相关，\(S\) 可能奇异，此时应先处理冗余子空间，而不能直接调用正定广义本征求解器。

## D2 一致基变换的谱不变性

对任意 \(E\)，

\[
H'-ES'=A^\dagger(H-ES)A.
\]

因此

\[
\det(H'-ES')=\det(A^\dagger)\det(H-ES)\det(A)
=|\det A|^2\det(H-ES).
\]

因 \(A\) 可逆，前因子非零，两个特征行列式具有相同零点。系数坐标按 \(c'=A^{-1}c\) 变换。若只令 \(H'=A^\dagger HA\) 而保留旧 \(S\)，所得矩阵对不再表示同一算符与内积结构，谱不变性的前提被破坏。

## D3 实空间与倒空间 Hermiticity

由所给约定，

\[
\begin{aligned}
H(\mathbf k)^\dagger
&=\sum_{\mathbf R}e^{-i\mathbf k\cdot\mathbf R}H(\mathbf R)^\dagger\\
&=\sum_{\mathbf R}e^{-i\mathbf k\cdot\mathbf R}H(-\mathbf R)\\
&=\sum_{\mathbf R'}e^{i\mathbf k\cdot\mathbf R'}H(\mathbf R')
=H(\mathbf k),
\end{aligned}
\]

其中最后一步令 \(\mathbf R'=-\mathbf R\)，并要求求和集合在取负后闭合。对含 \(N_k\) 个相容网格点的离散变换，反变换为

\[
H(\mathbf R)=\frac{1}{N_k}\sum_{\mathbf k}e^{-i\mathbf k\cdot\mathbf R}H(\mathbf k),
\]

前提是实空间平移按对应有限超胞取模，采样网格与该超胞互为离散 Fourier 对；否则会发生混叠或截断误差。

## D4 轨道块旋转协变

采用被动基变换：原子 \(i\) 与 \(j\) 的轨道列向量分别变为 \(|\phi_i'\rangle=|\phi_i\rangle U_i(Q)\)、\(|\phi_j'\rangle=|\phi_j\rangle U_j(Q)\)。于是

\[
H_{ij}'(Q\mathcal G)
=U_i(Q)^\dagger H_{ij}(\mathcal G)U_j(Q).
\]

这里 \(\mathcal G\) 表示几何和其他输入；若改用主动旋转或相反的基列约定，\(U\) 与 \(U^\dagger\) 的位置会相应改变。关键要求是输入几何、输出轨道表示和测试约定一致。普通标量网络逐分量输出矩阵块时，并无结构性约束保证各分量按该群表示混合；必须通过局域坐标构造、显式等变架构或其他受约束解码，并执行随机旋转残差测试。

## D5 简单广义本征值的一阶扰动

微分 \(Hc=ESc\) 得

\[
\delta Hc+H\delta c
=\delta ESc+E\delta Sc+ES\delta c.
\]

左乘 \(c^\dagger\)。由 \(c^\dagger H=E c^\dagger S\)（厄米问题、实本征值）可消去含 \(\delta c\) 的两项，再用 \(c^\dagger Sc=1\)，得到

\[
\delta E=c^\dagger(\delta H-E\delta S)c.
\]

该式不能无条件用于：简并本征值；近简并且扰动与谱隙同量级；有限大扰动而忽略高阶项；扰动后 \(S\) 不再正定；非厄米矩阵束；比较时基、索引或相位未对齐；需要本征矢/子空间误差而非单一本征值误差。简并情形应在简并子空间内对投影扰动矩阵对角化，近简并情形还应报告子空间和谱隙。

