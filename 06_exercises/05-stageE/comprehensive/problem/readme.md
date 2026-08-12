# 阶段 E 综合问题：表示—消息—Hamiltonian—时间反演对象链

## 1. 题目范围与冻结输入

本题覆盖 C-E01—C-E12。各小题共享[阶段 E 统一表示约定](../../../../03_textbook/stageE_representation_conventions.md)、[表示追踪模板](../../../../03_textbook/stageE_representation_trace_template.md)、[推导总索引](../../../../04_derivations/stageE/README.md)和[合成代码说明](../../../../05_code_exercises/stageE_synthetic_equivariance/README.md)。不得用不同的主动/被动、实基顺序、\(m\) 顺序、CG 相位或 Hamiltonian 左右作用替换题面约定。

共同约定如下：

- 三维列向量采用主动正旋转，先 \(R_1\) 后 \(R_2\) 的总作用为 \(R_2R_1\)；
- 复球谐与 coefficient 的 \(m\) 顺序为 \(-\ell,\ldots,+\ell\)；实基顺序为 \((s)\)、\((p_x,p_y,p_z)\)、\((d_{xy},d_{yz},d_{zx},d_{x^2-y^2},d_{3z^2-r^2})\)；
- 归一化残差为 \(\rho(A,B)=\|A-B\|_F/\max(1,\|A\|_F,\|B\|_F)\)；`float64`/`float32` 阈值为 \(5\times10^{-12}\)/\(5\times10^{-6}\)，等号接受，非有限值拒绝；
- 周期边 payload 使用 `stageD-edge-v1` 紧凑 JSON；Hamiltonian 合成块的 structure ID 为 `stageE-H`；
- 所有实践字段均保持 `UNRESOLVED_M8`。

可使用固定 Python 环境和合成代码复算，但答案必须同时说明公式条件、身份映射和失败机制。

## C-E01 主动/被动与群复合

令

\[
R_1=\begin{pmatrix}0&-1&0\\1&0&0\\0&0&1\end{pmatrix},\qquad
R_2=\begin{pmatrix}1&0&0\\0&0&-1\\0&1&0\end{pmatrix},\qquad
r=(1,2,3)^\mathsf T.
\]

1. 计算主动链 \(r_1=R_1r\)、\(r_2=R_2r_1\) 和总矩阵；写出表示群律。
2. 对同一个物理向量，仅将坐标轴被动旋转 \(R_1\)，写出新分量。
3. 计算错误链 \(R_1R_2r\) 与把主动作用误写成 \(R_1^\mathsf Tr\) 的结果，说明为何不能用“都是正交矩阵”消除差异。

## C-E02 标量、极向量、轴向量与二阶张量

取反射 \(Q=\operatorname{diag}(-1,1,1)\)、极向量 \(v=(1,2,3)^\mathsf T\)、轴向量 \(a=(4,5,6)^\mathsf T\)、二阶张量 \(T=va^\mathsf T\)、偶标量 \(s_+=2\) 和伪标量 \(s_-=-3\)。

1. 分别写出 \(v,a,T,s_+,s_-\) 在 \(Q\) 下的变换，并给出 \((\ell,p)\) 或 polar/axial 类型。
2. 判断 \(v\cdot a\)、\(v\times v'\) 和 \(1+s_-\) 的宇称；说明哪一个可作为偶标量门值。
3. 解释为何只用 \(R\in SO(3)\) 的随机测试不能区分 polar 与 axial。

## C-E03 从 STF 基构造实 \(s,p,d\) 表

使用统一约定中的五个 Frobenius 正交归一 STF 矩阵 \(B_a\)，并令 \(R=R_1\)。

1. 由 \(D^d_{ab}(R)=\operatorname{tr}(B_a^\mathsf TRB_bR^\mathsf T)\) 计算完整 \(5\times5\) 矩阵。
2. 验证 \((D^d)^\mathsf TD^d=I\)，并用题面 \(R_2\) 验证 \(D^d(R_2R_1)=D^d(R_2)D^d(R_1)\)。
3. 写出 \(D^s,D^p\)，说明删去 \(B_{xy}\) 中的 \(1/\sqrt2\) 后哪些检查会失败。

## C-E04 复球谐、Wigner 表示与复—实桥

1. 从统一约定逐项写出 \(K_1,K_2\) 的定义方向 \(c_{\mathrm c}=K_\ell c_{\mathrm r}\)，验证幺正性，并重算规范 payload SHA-256。
2. 对 \(R_1\) 计算实表示与复表示，验证相似变换；明确函数点值与 coefficient 的变换矩阵是否相同、共轭或逆。
3. 构造两个失败样例：只翻转 \(m=+1\) 的 Condon--Shortley 相位；把按点值协变的数组直接输入 coefficient CG。给出残差或明确的契约失败。

## C-E05 CG 耦合与相位自由

1. 按 DLMF/Condon--Shortley 约定构造完整 \(1\otimes1=0\oplus1\oplus2\) 耦合矩阵，验证 selection rule、正交/完备和一般轴 intertwiner。
2. 独立核对三个锚点

   \[
   C^{00}_{1\,1,1\,-1}=1/\sqrt3,\quad
   C^{11}_{1\,1,1\,0}=1/\sqrt2,\quad
   C^{22}_{1\,1,1\,1}=1.
   \]

3. 比较三种修改：整个 \(L=0\) 通道乘 \(-1\) 并同步变换输出 basis；只翻 \(L=1,M=0\) 一行；只翻一个非零系数。分别说明规范表、正交性与 intertwiner 是否通过。
4. 写出交换输入所需相位 \((-1)^{\ell_1+\ell_2-L}\)，并说明 \(1\otimes2\) 的允许输出通道。

## C-E06 Hamiltonian 子块、左右作用与维度

receiver 轨道为 `(s,px,py,pz)`，sender 轨道为 `(px,py,pz,dxy,dyz,dzx,dx2-y2,d3z2-r2)`。冻结块为

\[
H_{rc}=0.1(8r+c+1),\qquad r=0,\ldots,3,\ c=0,\ldots,7.
\]

1. 按 receiver/sender 壳层把 \(H\) 分成 \(s-p,p-p,p-d\) 子块，并说明若 receiver 也含 d 壳时 \(d-d\) 块的 shape。
2. 对任意题面主动旋转写出 \(D_i,D_j\) 的块对角结构和唯一协变式，给出结果 shape。
3. 证明奇异值在双侧正交/幺正作用下不变；构造只左乘、只右乘和右侧漏转置/共轭三个 shape 合法的失败式。

## C-E07 Hermiticity、逆边与完整身份

正向边为 `(stageE-H,0,1,(0,0,0))`。

1. 写出其规范紧凑 JSON payload 和 SHA-256；构造逆边的端点、shift、payload、SHA-256 与 \(8\times4\) 块。
2. 说明旋转时哪些字段保持不变，哪些字段随表示作用改变。
3. 给出至少五个必须拒绝的变异，覆盖：任意 payload 重哈希、错误端点、错误 shift、轨道行错位、逆边未独立建行或漏共轭转置。
4. 解释为何奇异值相同或 hash 自洽不能替代完整身份和 Hermiticity。

## C-E08 等变消息层与失败非线性

设节点输入为 \((1,-)\) coefficient，polar 边方向生成 \((1,-)\) coefficient filter，使用 \(1\otimes1\to L=0,1,2\) CG 后按 receiver 求和，再在同型 multiplicity 轴线性混合。

1. 用表示追踪表写出 input、filter、tensor-product、message、aggregate 和 output 的 \((\ell,p)\)、multiplicity、component 顺序与 shape 符号。
2. 写出逐层等变证明所需的 intertwiner 和 receiver 聚合条件。
3. 判断标量非线性、偶标量门控、逐分量平方高阶 coefficient 是否保持 \(O(3)\) 等变。
4. 写出 \(p_{\mathrm{out}}=p_{\mathrm{in}}p_{\mathrm{filter}}\)，并用空间反演核对三个输出通道的宇称。说明 input/filter/output parity、direction 取反、direction 行滚动、错误 CG hash 或 output-irrep 元数据为什么必须由 provenance validator 拒绝。

## C-E09 局部架、退化拒绝与不连续

局部架以 \(u\) 定义第一轴，以去除平行分量后的 \(v\) 定义第二轴，第三轴由右手叉积给出；scale 为 1。

1. 对 \(u=(1,0,0)^\mathsf T,v=(0,1,0)^\mathsf T\) 构造局部架，并写出 receiver/sender 两端 4×8 Hamiltonian 的回拉和推出公式。
2. 分别定义 \(\zeta_u=\|u\|/s\)、\(\zeta_v=\|v\|/s\) 和 \(\eta=\|\widehat u\times\widehat v\|_2\)，列出 float64/float32 的零长度与共线阈值，并说明等号属于哪一侧。
3. 对 float64、\(s=1\)、\(u=(1,0,0)\)、\(v=(2,1.5\times10^{-8},0)\) 分别计算规范 \(\eta\) 与未归一化投影长度，判定 validator 应接受还是拒绝。
4. 解释为何不能用固定后备轴处理共线；比较 \(v_+=(1,4\tau,0)^\mathsf T\) 与 \(v_-=(1,-4\tau,0)^\mathsf T\) 的局部架极限，指出不连续的可观测量。

## C-E10 精度、144 点扫描与成本

1. 写出 144 点扫描的五个轴及组合数，解释 seed 与图身份的冻结关系。
2. 根据冻结锚点填写 G_A/G_B 的每旋转 MAC、聚合加法、total bytes 和 reference peak bytes，并换算 contraction FLOP。
3. 记录规范扫描的最大残差、最坏 case、rotation、ell 和 case digest；说明为何 `float64` 残差 \(10^{-6}\) 必须失败，而 `float32` 残差恰为 \(5\times10^{-6}\) 接受。
4. 区分完整物化数组字节、参考流式 peak、进程 RSS 与 wall-time benchmark；说明哪些字段进入规范 hash。

## C-E11 自旋、时间反演与适用条件

1. 对冻结实轨道无自旋对象写出 \(\Theta\) 与 \(\Theta^2\)；对 spin-1/2 写出 \(J_s=i\sigma_y\)、\(\Theta=J_sK\) 与 \(\Theta^2\)。
2. 在 DLMF-CS 复轨道 coefficient 基中写出 \((J_\ell)_{m'm}\)，验证 \(J_\ell J_\ell^*=I\)，再写出 orbital×spin 的 unitary part。
3. 解释 \(2\pi\) 与 \(4\pi\) 自旋旋转，写出 H/S 的独立 k/-k partner 条件。
4. 说明何时可推出 Kramers 简并；分别给出一般 k 冒充 TRIM、漏复共轭和 Zeeman 项三个失败样例。

## C-E12 端到端审计与授权边界

完成一份表格，把 C-E01—C-E11 中任意一个 Hamiltonian 输出分量沿以下链条完整追踪：

```text
来源与约定 -> 几何作用 -> (ell,p)/basis/component -> CG 路径
-> edge/direction provenance -> Hamiltonian 行列轨道 -> mask/dtype/shape
-> 正向残差 -> 定向故障 -> 自动测试 -> 证据边界 -> 授权状态
```

同时回答：

1. T-E01—T-E12、17 项 unittest、A/B/scan 字节确定性、63/63 故障矩阵和三种 padding 探针各验证什么；
2. 哪些结论仍不能从合成测试推出；
3. M8 前哪些字段必须保持 `UNRESOLVED_M8`；M8 冻结后开始 M9 前还缺少何种授权。

## 14. 复现要求

使用[代码说明](../../../../05_code_exercises/stageE_synthetic_equivariance/README.md)中的精确命令。提交或审计记录至少包含 Python/NumPy/SciPy 版本、`pip check`、17/17 unittest、A/B/scan 各两次 stdout SHA-256、144 点摘要、63/63 故障矩阵、三个 padding 探针、四份 M7-10 材料 SHA-256 以及所有未决授权字段。

本题的[参考解答](../solution/readme.md)可直接用于自学和独立复算；查看解答不改变材料建设门控。
