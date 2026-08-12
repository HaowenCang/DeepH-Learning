# 第 19 章参考解答

## A19-01 表示型 tensor schema

单节点 shape 为

\[
(3,1),\qquad(2,3),\qquad(2,5),
\]

总 component 数

\[
3+6+10=19.
\]

旋转只作用最后的 \(2\ell+1\) 轴；multiplicity 轴只允许同型混合。任意 \(19\times19\) 权重会混合不同 \((\ell,p)\) 或在同一 irrep 内任意依赖 \(m\)，一般不与表示对易。

最小 schema 包括 \((\ell,p)\)、multiplicity、dtype、shape、component 顺序、basis family、node/graph identity、active mask、有限值、表示版本和容差。

## A19-02 周期边方向与消息类型

\(e=(i,j,n)\) 中 \(i\) 是 receiver，\(j\) 是 sender：

\[
d_e=(f_j+n-f_i)A,\quad
r_e=\lVert d_e\rVert,\quad
\widehat d_{\mathrm{col}}=d_e^{\mathsf T}/r_e.
\]

\((1,-1)\otimes(1,-1)\) 允许

\[
(0,+1),(1,+1),(2,+1).
\]

旋转作用于笛卡尔方向和表示 component；反演另乘显式宇称；节点置换重排节点轴和端点；换胞改变 fractional representative 并按阶段 D 更新/回拉 shift。纯旋转不改变离散 edge key。

## A19-03 最小消息层等变证明

\(w(r):(0,+1)\) 不变。复球谐函数点值和进入 CG 的 coefficient filter 是两个不同对象：

\[
y^{\mathrm{pv}}_\ell(R\widehat d)
=D^{(\ell)}(R)^*y^{\mathrm{pv}}_\ell(\widehat d),
\]

\[
z^{\mathrm{cf}}_\ell(\widehat d)
:=\overline{y^{\mathrm{pv}}_\ell(\widehat d)},
\qquad
z^{\mathrm{cf}}_\ell(R\widehat d)
=D^{(\ell)}(R)z^{\mathrm{cf}}_\ell(\widehat d).
\]

其中 \(m=-\ell,\ldots,\ell\) 升序，shape 为 \((E,2\ell+1)\)，dtype 为 `complex128`/`complex64`，宇称为 \((-1)^\ell\)，basis family/version 为 `dlmf-cs-pointvalue-conjugate`/`stageE-edge-filter-v1`。每一行保留原 edge key/ID、方向、\(\ell\)、版本/hash 和 provenance。CG 满足

\[
C(D_{\mathrm{in}}\otimes D_f)=D_LC.
\]

所以以 \(x\) 和 \(z^{\mathrm{cf}}\) 为两个 coefficient 输入时，每条消息按 \(D_L\) 变换。sum 与 \(D_L\) 线性对易，同型权重只作用 multiplicity 轴，偶标量门控也对易，故复合等变。例 19-14 的一般轴 `complex128` 正例残差为 \(6.62\times10^{-17}\)。

把点值 \(D^*\) 当 coefficient \(D\) 会在球谐—CG 接口错向；同一一般轴对象的残差为 \(0.5219896443\)。逐分量高阶非线性不与一般非对角 \(D_L\) 对易；\(1+s_-\) 在反演下无确定宇称，使 \(O(3)\) 类型链断裂。

## A19-04 Hamiltonian 左右作用与 shape

\(H_{ij}:\mathcal V_j\to\mathcal V_i\) 要求

\[
D_iH_{ij}=H_{ij}'D_j.
\]

右乘 \(D_j^{-1}=D_j^\dagger\) 得

\[
H_{ij}'=D_iH_{ij}D_j^\dagger.
\]

\[
s-p:1\times3,\quad H'=HD_p^\dagger;
\]

\[
p-s:3\times1,\quad H'=D_pH;
\]

\[
p-d:3\times5,\quad H'=D_pHD_d^\dagger;
\]

\[
d-p:5\times3,\quad H'=D_dHD_p^\dagger.
\]

receiver/sender 交换会把 \(3\times5\) 变成 \(5\times3\)，不能靠相同方阵 shape 隐藏。

## A19-05 固定 \(4\times8\) 合成块

按例 19-3 构造

\[
D_i=1\oplus R,\qquad D_j=R\oplus D^d(R)
\]

和 C-order \(H_{ab}=0.1(8a+b+1)\)。正确结果是例题给出的 \(4\times8\) 数组。错误相对正确输出的归一化残差为

\[
0.5461588700,\quad
0.05995264977,\quad
0.9216691727.
\]

左右正交作用使奇异值保持，最大变化 \(3.55\times10^{-15}\)。逆块

\[
H_{ji}=H_{ij}^{\mathsf T}
\]

按 \(D_jH_{ji}D_i^{\mathsf T}\) 旋转后，与正向旋转块转置最大差 \(8.88\times10^{-16}\)。

这些数值来自单个合成矩阵、固定旋转和 float64，只是实现锚点，不能推出真实材料精度或成本。

## A19-06 复基、Hermiticity 与逆边

由

\[
H_{ji,-n}=H_{ij,n}^\dagger
\]

得

\[
\begin{aligned}
H_{ji,-n}'
&=D_jH_{ij,n}^\dagger D_i^\dagger\\
&=(D_iH_{ij,n}D_j^\dagger)^\dagger.
\end{aligned}
\]

非零 shift 的伴随位于另一条 \(-n\) 边，所以单块无需自身 Hermitian。若 \(D_j\) 有非实相位且 \(H\) 对应列非零，则 \(D_j^{\mathsf T}\ne D_j^\dagger\)，普通转置给出错误相位。

缺逆边说明数据/枚举/索引合同失败。先平均重厄米化会改变矩阵并掩盖缺失对象，应先报告反 Hermitian 残差和缺边。

## A19-07 batch、mask、edge 与 provenance

concat 节点类型 shape 为

\[
(N_{\mathrm{tot}},n_{\ell,p},2\ell+1),
\]

padded 为

\[
(B,N_{\max},n_{\ell,p}^{\max},2\ell+1).
\]

非方块 padded 可为

\[
(B,E_{\max},P_i^{\max},P_j^{\max}).
\]

mask 必须能恢复 graph/node/edge、左右 shell 和 component；complete irrep shell 全真或全假。

拒绝项包括：错误 rank、component 宽度非 \(2\ell+1\)、active NaN、partial shell mask、非 prefix padding、边端点越界、prediction 多/少行、几何独立滚动、edge key/provenance 单独排序、左右轨道 mask 与 block shape 不符、graph ID/count/offset 冲突、旋转时修改 shift。

不能先乘零 mask，因为 IEEE 算术中

\[
0\cdot\mathrm{NaN}=\mathrm{NaN}.
\]

必须先用布尔索引切除 inactive 区。

## A19-08 局部架和回拉

若 \(U_i'=D_i(R)U_i\)，则

\[
\overline H'
=U_i'^\dagger(D_iHD_j^\dagger)U_j'
=\overline H.
\]

回拉

\[
H=U_i\overline HU_j^\dagger
\]

给出双侧协变。

输入有限 \(u,v\) 和有限正 \(s\)。float64/32：

\[
\zeta_{u,v}\le10^{-12}/10^{-5}
\]

拒绝；

\[
\eta=\lVert\widehat u\times\widehat v\rVert
\le10^{-8}/10^{-4}
\]

拒绝；等号拒绝。正例 \(u=(1,0,0)\)、\(v=(1,1,0)/\sqrt2\)、\(s=1\) 给 \(F=I\)，旋转后给 \(F'=R\)。后备全局轴不随输入旋转，故一般不满足 \(F(RX)=RF(X)\)。

## A19-09 误差与成本分层

等变残差检验变换合同；float dtype/尺度决定舍入；target MAE/MSE 检验拟合；wall-time 受硬件和调度影响。四者不能互相替代。

T-E10 网格为

\[
\{64,32\}
\times\{20260809,20260810\}
\times\{1,8,64,257\}
\times\{1,2,4\}
\times\{10^{-3},1,10^3\},
\]

共 \(2\cdot2\cdot4\cdot3\cdot3=144\) 点。scan mode 与 config A/B 互斥；seed 映射固定图。MAC 从 contraction shape 计数，每个实 MAC=2 FLOP；receiver 聚合加法另报。数组逐名称给 shape/dtype/nbytes、total/reference peak；wall-time 单列且不入 hash。complex multiply-add 展开为多次实乘/加，不能视为一个实 MAC。

## A19-10 端到端门控与授权边界

合同顺序为：

1. 验证图、cell/cutoff、完整 edge key、node/edge/shell schema；
2. 用有限正尺度执行方向零长度合同；
3. 生成 \(m\) 升序的冻结复点值 \(y^{\mathrm{pv}}\)，在同一 edge row 显式取 \(z^{\mathrm{cf}}=\overline{y^{\mathrm{pv}}}\)，验证 `stageE-edge-filter-v1` 的 basis/version/hash 和 \(z(R\widehat d)=Dz(\widehat d)\)；
4. 只把 coefficient 节点特征与 \(z^{\mathrm{cf}}\) 送入冻结 CG，依据 \((\ell,p)\)、CG 表/hash、快轴和路径 provenance contraction；
5. receiver sum、同型混合和偶标量门控；
6. 按 receiver/bra 与 sender/ket shell 组装块并双侧变换；
7. 对 \((j,i,-n)\) 验证共轭逆边；
8. 在 concat/padded 中保持 prediction—mask—轨道—edge 统一行；
9. 分列逐层/端到端残差、target 误差、MAC/FLOP/bytes；
10. 实际执行只左乘、漏 \(\dagger\)、错 shell、错 edge-row、partial mask、padding NaN、把 \(D^*\) 点值直接送入 coefficient CG、filter hash/\(m\) 顺序/provenance 错配、高阶非线性、伪标量坏门控、局部架退化和错误回拉。

D-E05→T-E06，D-E06→T-E08，D-E07→T-E09，D-E09→T-E10，schema/故障矩阵→T-E12。

本章通过后仍不得安装 DeepH/e3nn、下载正式训练数据、生成 DFT 标签或选择材料、DFT/数据后端、软件对象/版本、SOC/磁性实践范围和训练预算。M8 集中冻结方案后，M9 外部动作前还需再次明确授权。
