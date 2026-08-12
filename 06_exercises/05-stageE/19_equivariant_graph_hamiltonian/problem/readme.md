# 第 19 章练习

## Q19-01 表示型 tensor schema

配置 A 有 \((n_{0,+},n_{1,-},n_{2,+})=(3,2,2)\)。写出单节点各类型 shape、总 component 数和旋转作用轴。说明 flatten 后任意线性层为何一般破坏类型，并列出最小 schema 字段。

## Q19-02 周期边方向与消息类型

对边 \(e=(i,j,n)\) 写出 receiver、sender、位移、距离和列方向。设发送特征为 \((1,-1)\)，filter 为 \((1,-1)\)，列出允许输出类型。说明旋转、反演、节点置换和换胞分别作用于哪些对象。

## Q19-03 最小消息层等变证明

从径向偶标量、球谐、CG intertwiner、receiver sum、同型线性混合和偶标量门控逐步证明端到端等变。指出函数值 \(D^*\) 与 coefficient \(D\) 混用、高阶逐分量非线性和伪标量 \(1+s_-\) 各破坏哪一步。

## Q19-04 Hamiltonian 左右作用与 shape

把 \(H_{ij}\) 视为从 sender 轨道空间到 receiver 轨道空间的映射，推导

\[
H_{ij}'=D_iH_{ij}D_j^\dagger.
\]

写出 \(s-p,p-s,p-d,d-p\) shape 和旋转式。说明非方块为何能定位 receiver/sender 交换。

## Q19-05 固定 \(4\times8\) 合成块

复算例 19-3 的 \(R,D^d,D_i,D_j,H'\)，并验证：

1. 正确双侧作用；
2. 只左乘、只右乘和右侧漏转置的冻结残差；
3. 奇异值不变；
4. inverse block 旋转后仍为正确转置。

说明这些数值为什么不是材料统计。

## Q19-06 复基、Hermiticity 与逆边

推导

\[
H_{ji,-n}'=(H_{ij,n}')^\dagger
\]

并解释非零 shift 块为何不必自身 Hermitian。给出复基中普通转置代替共轭转置的明确失败条件。为什么缺逆边后不应先重厄米化？

## Q19-07 batch、mask、edge 与 provenance

为 concat 和 padded 两种 batch 写出 \((\ell,p)\) 节点 tensor 及非方 Hamiltonian 块的 shape、mask 和身份合同。列出至少八类应拒绝的 schema/行映射变异，并说明 inactive NaN 为什么不能先乘零 mask。

## Q19-08 局部架和回拉

从 \(F(RX)=RF(X)\) 推导局部块不变与全局回拉协变。写出 \(u,v,s\) 的 float64/32 零长度、近共线阈值和等号方向，构造非退化正例，并说明任意后备轴为何失败。

## Q19-09 误差与成本分层

区分数学等变残差、浮点误差、合成 target 误差和 wall-time。写出 T-E10 的 144 点网格轴、config/scan 互斥、MAC/FLOP、receiver 聚合、array total/reference peak 的报告要求。为什么 complex MAC 不能直接照搬实 kernel 的 2 FLOP？

## Q19-10 端到端门控与授权边界

为一条周期边 Hamiltonian 预测对象链写出“输入 schema→方向 validator→球谐→CG 路径→聚合/门控→轨道块→逆边/Hermiticity→batch/provenance→残差/失败矩阵”的可执行合同。映射 D-E05—D-E07/D-E09 到 T-E06/T-E08—T-E10/T-E12，并说明本章通过后仍禁止哪些 M8/M9 外部动作。
