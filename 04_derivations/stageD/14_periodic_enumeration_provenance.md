# D-D05/D-D07：周期镜像枚举与代表协变

## D-D05：有限镜像枚举界与完备性

设 \(A\in\mathbb R^{3\times3}\) 为 float64 行晶格矩阵，所有元素有限，\(\sigma_{\min}(A)>0\)、\(\kappa_2(A)<10^8\)。cutoff \(r_c\) 必须是有限 float64 标量且严格大于 0；NaN、\(+\infty\)、\(-\infty\) 和非正数均不在本推导定义域。规范分数坐标满足 \(f_i,f_j\in[0,1)^3\)。定义

\[
d_{ijn}=(f_j+n-f_i)A,
\qquad n\in\mathbb Z^3.
\]

令 \(B=A^{-1}\) 和 \(x=f_j+n-f_i\)。由 \(x=d_{ijn}B\)，第 \(k\) 分量满足

\[
|x_k|
=|d_{ijn}B_{:k}|
\le\lVert d_{ijn}\rVert_2\lVert B_{:k}\rVert_2.
\]

若 \(\lVert d_{ijn}\rVert_2\le r_c\)，则

\[
|f_{jk}+n_k-f_{ik}|
\le r_c\lVert B_{:k}\rVert_2.
\]

再由 \(|n_k|\le |f_{jk}+n_k-f_{ik}|+|f_{jk}-f_{ik}|\) 且 \(|f_{jk}-f_{ik}|<1\)，得到

\[
|n_k|<r_c\lVert B_{:k}\rVert_2+1.
\]

因此采用冻结的整数上界

\[
M_k=\left\lceil r_c\lVert B_{:k}\rVert_2+1\right\rceil
\]

必然包含所有 cutoff 内的镜像。枚举有限笛卡尔积 \(\prod_k\{-M_k,\ldots,M_k\}\)，再过滤 \(0<\lVert d_{ijn}\rVert_2\le r_c\)，所得边集完备。

该证明给出安全上界，不声称最紧。扩展盒 \(M_k+1\) 过滤后应得到相同完整边键集合；若不同，则实现违反了上述推导或边界循环。只用固定 \([-1,1]^3\) 没有一般完备性保证。

候选数上界为

\[
N^2\prod_{k=1}^3(2M_k+1).
\]

当 \(\sigma_{\min}\) 很小或 cutoff 很大时，\(\lVert B_{:k}\rVert_2\) 可很大，候选成本随之增长。阶段 D 在 \(\kappa_2\ge10^8\) 时直接拒绝；这不会消除所有大成本情形，因此实现还必须报告候选数和保留边数。

## D-D07：周期代表变换和边 provenance

从规范代表 \(f_i\) 出发，给每个原子选择整数 \(q_i\in\mathbb Z^3\)：

\[
\widetilde f_i=f_i+q_i.
\]

基线边为 \(e=(i,j,n)\)。定义变换后镜像

\[
n'=n+q_i-q_j.
\]

则

\[
\begin{aligned}
\widetilde d_{ijn'}
&=(\widetilde f_j+n'-\widetilde f_i)A\\
&=(f_j+q_j+n+q_i-q_j-f_i-q_i)A\\
&=(f_j+n-f_i)A\\
&=d_{ijn}.
\end{aligned}
\]

所以距离也不变。反向回拉为

\[
n^{\mathrm{can}}=n'-q_i+q_j=n.
\]

映射

\[
T_q:(i,j,n)\mapsto(i,j,n+q_i-q_j)
\]

的逆为 \(T_{-q}\)，故它在整数边三元组集合上是双射。对 cutoff 过滤后的物理边集，位移不变又保证成员资格不变。因此应先用

\[
K_q(e')=(\texttt{structure\_id},i,j,n_x^{\mathrm{can}},n_y^{\mathrm{can}},n_z^{\mathrm{can}})
\]

精确匹配，再比较浮点位移。若所有 \(q_i=q\)，则 \(n'=n\)。若不同 \(q_i\) 下错误保持 \(n'=n\)，一般不再满足位移等式，必须失败。

规范边身份由下列字段类型和顺序固定的 JSON 数组给出：版本与 `structure_id` 为字符串，\(i,j,n_x,n_y,n_z\) 为十进制整数。

```text
["stageD-edge-v1",structure_id,i,j,nx,ny,nz]
```

实际规范字节串必须用 `ensure_ascii=false`、`separators=(",",":")` 无空格序列化并编码为 UTF-8，再计算 SHA-256；其中 shift 使用回拉后的规范整数。对例 14-8 的具体值，规范字节串为 `["stageD-edge-v1","syn-14",0,1,-1,0,0]`，哈希必须为 `f83e3b238ba5c1b71cc773c08afa5fab22c35c1e38c6418b629fde616f5020e3`。不同 \(n\) 必须产生不同离散输入，不得按 \((i,j)\) 或距离折叠。浮点位移不进入 ID，避免把容差依赖混入身份；但 ID 正确也不替代 `rtol=0, atol=1e-12` 的位移/距离回归。

边 provenance 应同时保存完整离散键、整数 shift、位移、距离以及边输出的块形状、mask、局部与实际轨道身份。排序、批处理、换胞回拉和置换逆映射必须保持行级同步。完整键重复、ID 冲突、删除 shift 或轨道身份与端点不一致都应拒绝。
