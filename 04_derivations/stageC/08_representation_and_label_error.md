# D-C06—D-C07：离散表示、投影重建与标签误差

本推导包对应第 8 章。D-C06 从连续单粒子方程投影到普通或广义矩阵本征问题；D-C07 区分离散、采样、投影、规范和标签制品误差，并给出 T-C05—T-C08 的可复算对象。所有实践后端、材料和参数保持到 M8。

## D-C06 离散 Kohn–Sham 方程

### D-C06.1 有限试探空间

令 \(\hat h\) 是固定自洽密度下的单粒子 Hermitian 算符，选取 \(M\) 个线性无关试探函数

\[
\Phi=(|\phi_1\rangle,\ldots,|\phi_M\rangle).
\]

近似态写为

\[
|\psi\rangle=\Phi c=\sum_{\nu=1}^{M}c_\nu|\phi_\nu\rangle,
\qquad
c\in\mathbb C^M.
\]

Galerkin 条件要求残差与试探空间正交：

\[
\langle\phi_\mu|(\hat h-E)|\psi\rangle=0,
\qquad \mu=1,\ldots,M.
\]

定义

\[
H_{\mu\nu}=\langle\phi_\mu|\hat h|\phi_\nu\rangle,
\qquad
S_{\mu\nu}=\langle\phi_\mu|\phi_\nu\rangle.
\]

于是

\[
Hc=ESc,
\qquad H,S\in\mathbb C^{M\times M}.
\]

若 \(\hat h\) Hermitian 且积分一致，则 \(H=H^\dagger\)；若基线性无关，则

\[
c^\dagger Sc=\|\Phi c\|^2>0
\]

对任意非零 \(c\) 成立，故 \(S\succ0\)。如果实际矩阵不满足这些条件，应先诊断积分、索引、截断或线性相关问题，而不能静默调用普通 Hermitian 求解器。

### D-C06.2 平面波何时给出 \(S=I\)

固定周期胞体积 \(\Omega\) 和 \(\mathbf k\)，取

\[
\phi_{\mathbf G}(\mathbf r)
=\Omega^{-1/2}e^{i(\mathbf k+\mathbf G)\cdot\mathbf r}.
\]

在同一胞上的标准 \(L^2\) 内积给出

\[
\langle\phi_{\mathbf G}|\phi_{\mathbf G'}\rangle
=\frac1\Omega\int_\Omega
e^{i(\mathbf G'-\mathbf G)\cdot\mathbf r}\,d\mathbf r
=\delta_{\mathbf G\mathbf G'}.
\]

因此对选定有限平面波集合，基 Gram 矩阵为 \(I\)。要把离散方程进一步写成

\[
Hc=Ec,
\]

还需普通范数约束、同一离散内积以及没有另行引入广义重叠算符。ultrasoft/PAW 等形式即使使用正交平面波展开，也可因变换后的物理内积而具有 \(S\ne I\)。所以“平面波基正交”和“完整形式体系是普通本征问题”是两个命题。

### D-C06.3 非正交局域基

一般局域轨道具有

\[
S_{\mu\nu}\ne\delta_{\mu\nu}.
\]

本征矢应按

\[
c_i^\dagger Sc_j=\delta_{ij}
\]

归一化。若对同一物理试探空间作可逆基变换

\[
\Phi'=\Phi A,\qquad A\in\mathbb C^{M\times M}\ \text{可逆},
\]

则

\[
H'=A^\dagger HA,\qquad
S'=A^\dagger SA,\qquad
c'=A^{-1}c.
\]

广义谱和物理态保持，而矩阵元素通常改变。若只变换 \(H\) 而不同步 \(S\)、系数和标签规范，就不是同一表示变换。

### D-C06.4 离散误差的条件

有限子空间只给出投影问题。增大基或网格通常改变：

- 试探空间；
- 积分/FFT 精度；
- Hamiltonian 的自洽密度；
- Pulay 项或导数量；
- 输出投影的源空间。

因此，严格的嵌套 Rayleigh–Ritz 单调结论只适用于固定算符、嵌套子空间和一致变分量；不能自动推广到重新自洽后的力、应力、矩阵元素或不同赝势之间。

## D-C07 误差轴、投影与标签语义

### D-C07.1 多轴误差不能由单一差值识别

把合成输出写成

\[
q=q(p,k,s,\tau,r),
\]

其中 \(p\) 表示基/网格分辨率，\(k\) 表示采样，\(s\) 表示 smearing，\(\tau\) 表示迭代容差，\(r\) 表示输出表示或投影。若同时改变多个变量，

\[
q(p_2,k_2,\ldots)-q(p_1,k_1,\ldots)
\]

不能唯一归因于其中一个误差轴。一个可审计设计应固定其余变量，只扫描一个轴，并保存至少三个层级、参考或外推假设、绝对误差和相邻差。

误差预算可用三角不等式给出保守上界，但各分量通常相关：

\[
\|q_{\mathrm{label}}-q_{\mathrm{target}}\|
\le
\|e_{\mathrm{theory}}\|
+\|e_{\mathrm{core}}\|
+\|e_{\mathrm{basis}}\|
+\|e_k\|
+\|e_{\mathrm{SCF}}\|
+\|e_{\mathrm{projection}}\|.
\]

该式是记账上界，不证明误差统计独立，也不允许用误差抵消来宣布各层都已收敛。

### D-C07.2 T-C05 多层级序列

对 \(q_*=1\) 和

\[
q^+=(1.12,1.03,1.008,1.002,1.0005),
\]

参考误差为

\[
(0.12,0.03,0.008,0.002,0.0005),
\]

相邻差为

\[
(0.09,0.022,0.006,0.0015).
\]

最后三个参考误差均小于 \(10^{-2}\)，最后一级小于 \(10^{-3}\)，最后两个相邻差均小于 \(10^{-2}\)。

对

\[
q^-=(1.12,1.03,1.0020,1.0015,1.0080),
\]

32/64 的差为 \(5\times10^{-4}\)，但 128 的参考误差为 \(8\times10^{-3}\)。故单对差小于 \(10^{-3}\) 不能推出最后结果误差小于 \(5\times10^{-3}\)。

### D-C07.3 T-C06 采样轴与基轴

周期平均

\[
q=\frac1{2\pi}\int_0^{2\pi}e^{\cos k}\,dk=I_0(1)
\]

用等距梯形规则

\[
q_N=\frac1N\sum_{j=0}^{N-1}
\exp\left[\cos\left(\frac{2\pi j}{N}\right)\right]
\]

计算。对解析周期函数，该规则快速收敛；冻结 \(N=16,32,64\) 的误差均小于 \(10^{-12}\)。

若独立注入基偏置

\[
\delta_b=10^{-2},
\qquad
\widetilde q_N=q_N+\delta_b,
\]

则 \(\widetilde q_N\) 的总误差仍约为 \(10^{-2}\)，即使 \(q_{32}=q_{64}\) 到浮点精度。该例构造性地证明采样收敛不推出总误差收敛。

### D-C07.4 正交目标子空间

设完整空间 Hamiltonian \(H\in\mathbb C^{d\times d}\) Hermitian，\(B\in\mathbb C^{d\times p}\) 满足

\[
B^\dagger B=I_p.
\]

令

\[
P=BB^\dagger,\qquad
H_p=B^\dagger HB,\qquad
H_r=BH_pB^\dagger=PHP.
\]

则 \(P=P^\dagger=P^2\)。回投幂等一致性为

\[
P H_r P=H_r.
\]

丢失范数

\[
\ell_H=\frac{\|H-H_r\|_F}{\max(\|H\|_F,10^{-15})}
\]

只衡量固定完整矩阵在该投影/回投规则下的矩阵损失。它不是能带误差的同义词；\(H_p\) 和 \(H\) 的维数也不同，必须定义能带窗口和匹配规则后才能比较谱。

### D-C07.5 非正交目标空间

若 \(B\) 列满秩但

\[
S_B=B^\dagger B\ne I,
\]

矩阵元为

\[
H_B=B^\dagger HB,\qquad S_B=B^\dagger B.
\]

目标空间中的物理谱由

\[
H_Bc=ES_Bc
\]

给出。完整空间正交投影是

\[
P_B=B S_B^{-1}B^\dagger.
\]

固定完整空间内积下，回投算符为

\[
\begin{aligned}
H_r^{(\mathrm{nonorth})}
&=P_BHP_B\\
&=B S_B^{-1}(B^\dagger HB)S_B^{-1}B^\dagger\\
&=B S_B^{-1}H_BS_B^{-1}B^\dagger.
\end{aligned}
\]

由 \(P_B^2=P_B=P_B^\dagger\)，

\[
P_BH_r^{(\mathrm{nonorth})}P_B
=H_r^{(\mathrm{nonorth})}.
\]

对应表示损失为

\[
\ell_H^{(\mathrm{nonorth})}
=\frac{\|H-H_r^{(\mathrm{nonorth})}\|_F}
{\max(\|H\|_F,10^{-15})}.
\]

这些公式要求 \(B\) 列满秩、完整空间内积固定、\(S_B\succ0\)。若 \(S_B\) 病态，显式求逆会放大误差；数值实现应以 Cholesky、Hermitian-definite 求解或等价稳定分解实现两次 \(S_B\) 线性求解，并登记条件数、阈值和删减子空间。这里给出数学对象，不冻结具体算法。

正交公式 \(BH_BB^\dagger\) 在非正交情形一般错误。取 \(B=2e_1\) 及 \(H=h|e_1\rangle\langle e_1|\)，则 \(S_B=4\)、\(H_B=4h\)。正确公式给

\[
B S_B^{-1}H_BS_B^{-1}B^\dagger
=h|e_1\rangle\langle e_1|,
\]

而错误公式给

\[
BH_BB^\dagger
=16h|e_1\rangle\langle e_1|.
\]

这个反例表明，缺少两侧对偶度量会使重建算符依赖基函数的任意缩放。

### D-C07.6 T-C07 一致合同变换

取

\[
S=\operatorname{diag}(1,2,1.5,2.3),
\qquad
H=\operatorname{diag}(-1.2,-0.2,1.2,4.6).
\]

原广义谱逐分量为

\[
E_i=H_{ii}/S_{ii}=(-1.2,-0.1,0.8,2.0).
\]

对可逆 \(A\)，

\[
H'=A^\dagger HA,\qquad S'=A^\dagger SA.
\]

行列式满足

\[
\det(H'-ES')
=|\det A|^2\det(H-ES),
\]

故广义谱保持。若忽略 \(S'\) 而求 \(H'\) 的普通谱，所解问题已经改变。冻结矩阵给出的最大谱差约为 0.967，大于 \(10^{-1}\) 的拒绝阈值。

### D-C07.7 T-C08 投影损失与等谱反例

固定 seed 的规范 QR 给出 unitary \(Q\)，

\[
H=Q\operatorname{diag}(\operatorname{linspace}(-3,3,d))Q^\dagger.
\]

取 \(B=Q[:,q:q+p]\) 后，\(B^\dagger B=I\)，所以第 D-C07.4 节公式直接适用。两组冻结配置的 \(\ell_H\) 均大于 0.9，表明目标子空间只保留完整矩阵的一部分。

另取 unitary \(U\) 并定义

\[
H_2=U^\dagger HU.
\]

冻结故障注入令 \(U\) 只在固定标准基的前两维作角度 \(0.37\ \mathrm{rad}\) 的实正交旋转，其余维保持不变。

由 unitary 相似变换，\(H_2\) 与 \(H\) 的谱完全相同；但在固定标准基中，

\[
\frac{\|H_2-H\|_F}{\|H\|_F}
\]

可以非零。冻结旋转给出两组值均大于 0.15。因此只有在轨道映射和规范同步后，矩阵逐元素比较才有语义。

### D-C07.8 标签身份与验证层次

矩阵标签不是裸数组，而是

\[
\mathcal L=
(H,S,\mathcal I,\mathcal U,\mathcal F,\mathcal G,\mathcal P,\mathcal C),
\]

其中 \(\mathcal I\) 是轨道/原子/晶格位移索引，\(\mathcal U\) 是单位，\(\mathcal F\) 是 Fourier 约定，\(\mathcal G\) 是相位/规范，\(\mathcal P\) 是投影定义，\(\mathcal C\) 是理论和数值生成条件。制品路径、内容哈希和软件身份提供血缘。

验证应分为：

\[
\text{schema 完整}
\;\not\Rightarrow\;
\text{数值正确}
\;\not\Rightarrow\;
\text{物理目标充分}.
\]

schema 检查只能证明必填语义存在；矩阵、谱和物性验证分别回答不同问题。能带接近不能无条件推出矩阵相同，矩阵接近也不能无条件推出所有敏感响应量接近。

T-C09 的完整 stageC-label-v1 必填路径集合、数组内部成员、类型/形状/SHA-256/UNRESOLVED_M8 约束及“逐路径删除必须抛出含缺失路径 ValueError”规范，以[阶段 C 工作包第 8 节](../../08_audits/M5_stageC_work_package.md)为单一冻结来源；本推导不复制该表，以避免双份 schema 漂移。

## D-C06/D-C07 验收清单

- 从 Galerkin 条件推导 \(Hc=ESc\)，并给出 \(H,S,c\) 的形状和 Hermitian/正定条件；
- 明确平面波 \(S=I\) 需要正交平面波、标准内积和普通范数形式；
- 对非正交局域基保留 \(S\) 和一致合同变换；
- 把 cutoff/网格、采样、smearing、SCF 和投影作为不同误差轴；
- 完整复算 T-C05—T-C08 的正例、阈值和故障注入；
- 区分正交与非正交目标子空间的投影公式；
- 区分 schema、矩阵、能带和物性门控；
- 不隐含选择赝势、基、后端、材料、投影软件或实践参数。

## 来源与证据状态

| 来源 | 本推导使用对象 | 状态与边界 |
|---|---|---|
| [第 8 章 sources.md](../../03_textbook/chapters/08_basis_pseudopotential_errors/sources.md) 的 FND-01/C-NUM-02 | 平面波、局域基、离散与历史数值语境 | PRIMARY_EXPLICIT；不冻结现代后端格式 |
| 同表 C-NUM-03 | norm-conserving 条件与 transferability | PRIMARY_EXPLICIT；不推广到 ultrasoft/PAW |
| 同表 C-FND-04 | 有限温度理论边界 | PRIMARY_EXPLICIT；数值 smearing 不自动等于物理温度 |
| 同表 DH-07 | PW 到选定 AO 表示的投影/重建接口 | PRIMARY_EXPLICIT；M8 前不声明可用版本或命令 |
| D-C06/D-C07 的 Galerkin、合同变换与投影代数 | \(Hc=ESc\)、\(P_BHP_B\)、误差分层 | DIRECT_DERIVATION |
| T-C05—T-C09 合成序列、矩阵和 schema 故障 | 数值容差与失败语义 | PEDAGOGICAL |
