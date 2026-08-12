# 阶段 E 表示追踪模板：从群作用到边级 Hamiltonian 块

## 1. 目的与适用范围

本模板用于审计阶段 E 中几何对象、不可约表示、球谐 coefficient、CG 通道、等变消息、边级 Hamiltonian 块、局部架和时间反演接口之间的逐字段映射。任何结论都应先通过作用方向、basis、component、edge identity 和 provenance 检查，再比较数值残差。

模板只适用于第 15—20 章、D-E01—D-E09 与 `stageE-synthetic-equivariance-v1` 合成对象。它不证明 DeepH/e3nn、真实材料、DFT 标签或正式训练正确；相关实践选择在 M8 前保持 `UNRESOLVED_M8`。

## 2. 审计记录头

| 字段 | 期望或填写规则 | 实际值 | 判定 |
|---|---|---|---|
| record ID | 本次追踪唯一字符串 |  |  |
| date/timezone | ISO 日期，Asia/Shanghai |  |  |
| schema/version | 对象的冻结 schema |  |  |
| source object | 文件、函数、题目或 CLI |  |  |
| config/seed | A/20260809、B/20260810 或 scan case ID |  |  |
| Python | 3.12.13 |  |  |
| NumPy/SciPy | 2.3.5 / 1.18.0 |  |  |
| dtype | `float64`, `float32`, `complex128` 或 `complex64` |  |  |
| authorization | material/backend/DeepH object/budget/advanced physics 均为 `UNRESOLVED_M8` |  |  |
| code SHA-256 | 被执行代码逐文件 hash |  |  |
| evidence boundary | 仅说明本次记录实际验证的对象 |  |  |

## 3. 群元素与作用方向

三维向量使用列向量，主线采用主动正旋转 \(r'=Rr\)。先施加 \(R_1\)，再施加 \(R_2\)，总作用为 \(R_2R_1\)；被动换基分量为 \(r_{\mathrm{new}}=R^{\mathsf T}r_{\mathrm{old}}\)。

| 字段 | 期望 dtype/shape | 实际值/hash | 独立重算 | 判定 |
|---|---|---|---|---|
| group | `SO(3)` 或 `O(3)` |  |  |  |
| action | `active-object` 或 `passive-components` |  |  |  |
| `R1/R2` | float `[3,3]` |  | \(R^\mathsf TR=I\) |  |
| determinant | 有限标量 |  | 正旋转为 +1；反射/反演为 -1 |  |
| composition | `[3,3]` |  | 主动链为 \(R_2R_1\) |  |
| quaternion | float `[4]`，若使用 |  | 单位范数、规范符号 |  |
| rotation residual | 非负有限标量 |  | 用 dtype 对应 validator 阈值 |  |

不得把 Euler 角三元组直接当作旋转矩阵，也不得把被动转置写入主动对象链后继续沿用主动复合公式。

## 4. 不可约表示逐层表

对每一个输入、隐藏通道、消息、聚合和输出分别填写一行。\((\ell,p)\) 中 \(p\in\{+1,-1\}\) 是反演宇称；同一 \((\ell,p)\) 的多个 copy 用 multiplicity 表示。

| layer/object | semantic role | \((\ell,p)\) | multiplicity | component/basis order | dtype | exact shape | group action | mask | tolerance | provenance | 判定 |
|---|---|---|---:|---|---|---|---|---|---|---|---|
| input |  |  |  |  |  |  |  |  |  |  |  |
| edge filter |  |  |  |  |  |  |  |  |  |  |  |
| tensor product |  |  |  |  |  |  |  |  |  |  |  |
| message |  |  |  |  |  |  |  |  |  |  |  |
| aggregate |  |  |  |  |  |  |  |  |  |  |  |
| gate/mix |  |  |  |  |  |  |  |  |  |  |  |
| output |  |  |  |  |  |  |  |  |  |  |  |

必须显式回答：

- component 轴是否按 \(-\ell,-\ell+1,\ldots,\ell\) 或冻结实基排序；
- multiplicity 轴与 component 轴是否分开，shape 中分别位于哪一维；
- 标量门值属于 \((0,+)\) 还是伪标量 \((0,-)\)，其乘积是否保持目标宇称；
- 同型线性混合是否只作用在 multiplicity 轴；
- 高阶通道是否错误地逐分量施加非线性；
- inactive padding 是否在任何 contraction、归一化、预测或 loss 之前切除。

C-E08 冻结消息夹具必须记录为：节点输入 \((1,-)\)、方向 coefficient filter \((1,-)\)，因此输出依次为 \((0,+),(1,+),(2,+)\)。宇称遵循 \(p_{\mathrm{out}}=p_{\mathrm{in}}p_{\mathrm{filter}}\)；反演下两个输入都变号而三个输出保持不变。若 provenance 将输入或 filter 写成 \((1,+)\)，或将任一输出写成奇宇称，必须在 \(O(3)\) 元数据/反演检查中失败，不能用只覆盖 \(SO(3)\) 的残差放行。

## 5. 实 \(s,p,d\) 与复—实桥

| 对象 | 冻结顺序/shape | 实际值或 hash | 必须复算 | 判定 |
|---|---|---|---|---|
| s | `(s)` / `[1]` |  | \(D^{(0)}=1\) |  |
| p | `(px,py,pz)` / `[3]` |  | \(D^p(R)=R\) |  |
| d | `(dxy,dyz,dzx,dx2-y2,d3z2-r2)` / `[5]` |  | STF 正交、无迹、\(D^d_{ab}=\operatorname{tr}(B_a^\mathsf TRB_bR^\mathsf T)\) |  |
| K1 | complex `[3,3]` |  | 幺正；hash `347e...972a2` |  |
| K2 | complex `[5,5]` |  | 幺正；hash `5e783...f7b82` |  |
| complex coefficient | `[2\ell+1,multiplicity]` 或明确等价 shape |  | \(c'=D^{(\ell)}c\) |  |
| spherical point value | `[2\ell+1]` |  | 与 coefficient 变换方向分开验证 |  |

完整 hash 必须从[代码说明](../05_code_exercises/stageE_synthetic_equivariance/README.md)复制或由 payload 独立重算，记录中不得只保留省略号。若外部资料采用不同实基或相位，应先写出显式置换—符号/相位矩阵，再进入相似变换检查。

## 6. CG 路径与相位记录

每条耦合路径单独填写，不得只写“使用 CG”。输出宇称为 \(p_1p_2\)。

| path ID | \((\ell_1,p_1)\) | \((\ell_2,p_2)\) | \((L,p_1p_2)\) | input order | output M order | CG table/hash | exchange phase | multiplicity map | 判定 |
|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  | \((-1)^{\ell_1+\ell_2-L}\) |  |  |

同时记录以下四类检查：

| 检查 | 独立复算 | 结果 |
|---|---|---|
| selection rule | 非零项满足 \(M=m_1+m_2\)，\(|\ell_1-\ell_2|\le L\le\ell_1+\ell_2\) |  |
| orthogonality/completeness | 完整耦合矩阵单位正交/幺正 |  |
| intertwiner | 旋转后耦合等于输出表示作用 |  |
| phase contract | 三锚点为 \(+1/\sqrt3,+1/\sqrt2,+1\)，全表 hash 为 `fd40673f...d1a04` |  |

整条固定 \(L\) 输出通道统一乘 \(e^{i\phi_L}\) 或实数 \(\pm1\)，并同步变换输出 basis 与下游映射，是合法基变换；它可使规范表 hash 失败，但不应被误判为 intertwiner 失败。只翻一个非零系数、只翻部分 \(M\) 行或交换输入而漏相位必须失败。

## 7. 周期边、方向与消息 provenance

阶段 E 延用 `stageD-edge-v1` 紧凑 JSON：

```text
["stageD-edge-v1",structure_id,receiver,sender,n1,n2,n3]
```

| 字段 | 期望 dtype/shape | 实际值/hash | 独立重算 | 判定 |
|---|---|---|---|---|
| structure ID | 非空字符串 |  |  |  |
| receiver/sender | 整数标量或 `[E]` |  | 范围与方向 |  |
| shift | int `[3]` 或 `[E,3]` |  | 逆边为端点交换且 shift 取反 |  |
| edge payload | 规范紧凑 JSON |  | 解析后规范重编码 |  |
| edge ID | 64 位小写 SHA-256 |  | 从规范 payload 重算 |  |
| direction | float `[E,3]` |  | 非零、单位化、与 edge row 同序 |  |
| filter payload/hash | 每 \(\ell\) 一项 |  | coefficient filter、m 顺序与方向一致 |  |
| CG table hash | 固定 64 位 hash |  | 全表重算 |  |
| input irrep | `[1,-1]` |  | 节点 coefficient 为 \((1,-)\) |  |
| filter irrep | `[1,-1]` |  | polar direction coefficient 为 \((1,-)\) |  |
| output irreps/parities | `[[0,1],[1,1],[2,1]]` |  | \(p_{out}=p_{in}p_{filter}\) |  |

旋转只能改变笛卡尔 direction 与表示型特征，不改变端点、shift 或 edge ID。若 direction 取反或边行滚动而 provenance 未重建，validator 必须拒绝；若 provenance 同步伪造，则物理边语义已经改变，应由题目或上游身份契约判定，而不能视为原边的等变结果。

## 8. Hamiltonian 块逐字段表

| 字段 | 期望 | 实际值/hash | 独立重算 | 判定 |
|---|---|---|---|---|
| schema | `stageE-hamiltonian-edge-v1` |  |  |  |
| positive edge | `(stageE-H,0,1,(0,0,0))` |  | payload/hash |  |
| inverse edge | `(stageE-H,1,0,(0,0,0))` |  | 必须有独立 row/ID |  |
| receiver shells | `s0,p0` |  | orbitals `(s,px,py,pz)` |  |
| sender shells | `p0,d0` |  | orbitals `(px,py,pz,dxy,dyz,dzx,dx2-y2,d3z2-r2)` |  |
| forward block | float `[4,8]` |  | \(H_{rc}=0.1(8r+c+1)\) |  |
| inverse block | float `[8,4]` |  | \(H_{ji}=H_{ij}^\dagger\) |  |
| mask | bool，与 block 同 shape |  | 本夹具全 true |  |
| left representation | `[4,4]` |  | \(D_i=1\oplus D^p\) |  |
| right representation | `[8,8]` |  | \(D_j=D^p\oplus D^d\) |  |
| transformed block | `[4,8]` |  | \(D_iH D_j^\dagger\) |  |
| residual | 有限非负标量 |  | dtype 阈值 |  |

正向 payload 的完整 SHA-256 应为 `1a8d2a609fbe3cc7c5e9de863375420544fc64f1887b2f1df26d5defd9b2a4a8`，逆向为 `88c94d43c0833d689aacac098a0709e61e08e83f598ec3c26ea91534b8b99bf4`。任意 payload 重哈希仍必须通过 schema、structure ID、端点、shift、轨道表和正逆边语义核验，不能只验证 hash 自洽。

## 9. 局部架记录

| 字段 | 期望 | 实际值 | 判定 |
|---|---|---|---|
| dtype | float64 或 float32 |  |  |
| scale | 有限正标量 |  |  |
| primary vector \(u\) | `[3]` |  |  |
| reference vector \(v\) | `[3]` |  |  |
| \(\zeta_u=\|u\|/s\) | 无量纲 |  | float64 拒绝 \(\le10^{-12}\)，float32 拒绝 \(\le10^{-5}\) |
| \(\zeta_v=\|v\|/s\) | 无量纲 |  | 使用同一 dtype 零长度阈值，等号拒绝 |
| \(\widehat u,\widehat v\) | 各为 `[3]` |  | 仅在两项 \(\zeta\) 通过后归一化 |
| \(\eta=\|\widehat u\times\widehat v\|_2\) | 无量纲角退化度 |  | float64 拒绝 \(\le10^{-8}\)，float32 拒绝 \(\le10^{-4}\) |
| frame | `[3,3]` |  | 正交、右手、列轴顺序固定 |
| pullback/pushforward | 与目标块相容 |  | 双端局部架各自作用 |
| positive/negative limit | 两个非退化邻域样本 |  | 记录近共线跳变，不用后备轴掩盖 |

退化阈值的等号属于拒绝侧。幅值反例必须纳入记录：取 float64、\(s=1\)、\(u=(1,0,0)\)、\(v=(2,1.5\times10^{-8},0)\)，规范指标为 \(\eta\approx7.5\times10^{-9}\)，因此拒绝；未归一化投影长度为 \(1.5\times10^{-8}\)，若据此接受即说明错误地把有量纲幅值混入角退化合同。只展示单个非退化成功样例不能支持全域连续性。

## 10. 自旋与时间反演记录

反幺正算符写为 \(\Theta=JK\)，其中 \(K\) 是复共轭。记录必须说明轨道 basis、spin component 顺序、k 点定义域和是否位于 TRIM。

| 对象 | basis/order | unitary part \(J\) | 期望平方 | partner/condition | 实际残差 | 判定 |
|---|---|---|---|---|---|---|
| spinless real orbital | 冻结实轨道 | \(I\) | \(+I\) | H/S 的独立 k/-k row |  |  |
| complex orbital \(\ell\) | \(m=-\ell,\ldots,\ell\) | \((J_\ell)_{m'm}=(-1)^m\delta_{m',-m}\) | \(+I\) | basis bridge 已核对 |  |  |
| spin 1/2 | \((+1/2,-1/2)\) | \(i\sigma_y\) | \(-I\) | \(2\pi\to-I,4\pi\to+I\) |  |  |
| orbital × spin | 冻结 Kronecker 顺序 | \(J_\ell\otimes i\sigma_y\) | \(-I\) | H/S partner 与 mask/provenance 同步 |  |  |
| TRIM Kramers | 明确 \(k\equiv-k+G\) | 同上 | \(-I\) | 广义本征 \(Hc=\varepsilon Sc\)，\(S\succ0\) |  |  |

对实际 H/S partner 还必须填写下表；上面的算符表不能替代双行身份、mask 与数组 provenance。

| partner 字段 | 冻结期望 | 实际值/hash | 独立复算/故障 | 判定 |
|---|---|---|---|---|
| schema | `stageE-time-reversal-pair-v1` |  | 与 validator 常量一致 |  |
| `k_id/minus_k_id` | `stageE-k-general-001` / `stageE-minus-k-general-001` |  | ID 非空、互异且与 row provenance 一致 |  |
| `kpoint/minus_kpoint` | 各为 real `[3]`、同 dtype |  | 一般 k 夹具满足 \(-k\)；TRIM 另记 reciprocal vector \(G\) |  |
| `partner_map` | `[1,0]` |  | 双射、往返为恒等 |  |
| orbital IDs | `spin+1/2,spin-1/2`，k/-k 两端同序 |  | 任一 row drift 必须拒绝 |  |
| basis/component order | spin \((+1/2,-1/2)\)，若含轨道则另列 \(m\) 顺序 |  | 与 \(J\) 的行列一致 |  |
| H k/-k provenance | 独立 row ID、来源与完整轨道行 |  | 不得用同式自比或运行时复制替代 partner |  |
| S k/-k provenance | 独立 row ID、来源与完整轨道行 |  | 与 H 分开保存和核验 |  |
| `H_k/H_minus_k` | complex `[2,2]`、同一 complex dtype |  | 各自 Hermitian、有限 |  |
| `S_k/S_minus_k` | complex `[2,2]`、与 H 同 dtype |  | 各自 Hermitian、正定、有限 |  |
| `active_mask` | bool `[2,2]`，教学夹具全 true |  | partial mask 必须拒绝 |  |
| unitary part \(J\) | 与 basis/dtype 同步 |  | \(JJ^*=\pm I\) |  |
| H partner relation | \(H(-k)=JH(k)^*J^\dagger\) |  | 归一化残差与 dtype 阈值 |  |
| S partner relation | \(S(-k)=JS(k)^*J^\dagger\) |  | 独立残差，不得沿用 H 结果 |  |
| TRIM criterion | \(k=-k+G\) 且记录 \(G\)；一般 k 明确 false |  | 仅 TRIM 可作同 k Kramers 判据 |  |
| Kramers prerequisites | TR 保持、\(\Theta^2=-I\)、\(S\succ0\)、正确广义本征对象 |  | 成对本征值及 partner 向量条件 |  |
| T-E11 pair identity | pair ID/map/orbital rows/mask/shape/dtype 全通过 |  | 保存 `pair_identity` 与 array summary |  |
| 六项 partner 故障 | wrong ID、wrong map、partial mask、orbital row drift、wrong H partner、wrong S partner |  | 每项实际拒绝并记录异常 |  |

一般 k 只能建立 k 与 -k 的 partner 约束，不能直接宣称同一 k 的 Kramers 简并。漏复共轭、错误 \(J\)、错误 H/S partner 和 Zeeman 时间反演破缺项应当作为失败对照，而不是纳入通过样例。

## 11. 残差、成本与复现门控

统一残差为

\[
\rho(A,B)=\frac{\|A-B\|_F}{\max(1,\|A\|_F,\|B\|_F)}.
\]

| 记录项 | 期望 | 实际值 | 判定 |
|---|---|---|---|
| float64 threshold | \(5\times10^{-12}\)，等号接受 |  |  |
| float32 threshold | \(5\times10^{-6}\)，等号接受 |  |  |
| nonfinite | 一律拒绝 |  |  |
| worst rotation/ell | 每 case 明确 |  |  |
| scan cases | 144 个唯一 case |  |  |
| G_A cost | 168 MAC/rot，52 aggregate-add/rot |  |  |
| G_A bytes | total 2728，reference peak 2280 |  |  |
| G_B cost | 378 MAC/rot，143 aggregate-add/rot |  |  |
| G_B bytes | total 5584，reference peak 4576 |  |  |
| FLOP | contraction 按 2 FLOP/MAC |  |  |
| padding | NaN/0/1e300 三探针活动残差与 loss 为 0 |  |  |
| failures | 63/63 实际拒绝，名称唯一且有异常类型/消息 |  |  |

数组 `total` 是列出数组全部物化时的字节和；`reference peak` 是冻结流式调度的参考峰值。二者都不包括解释器、BLAS 临时缓冲或进程常驻内存，不能与 wall-time benchmark 或系统 RSS 混写。

## 12. 最终证据陈述

完成记录至少应包含：对象与来源、所有 shape/dtype/basis/order、群作用方向、edge/provenance、容差、正向残差、定向故障结果、payload/hash、代码 SHA、复现命令、授权字段和证据边界。建议使用以下结论模板：

```text
在 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0 与冻结配置下，
对象 ______ 的表示/身份/schema 契约通过；归一化残差为 ______，阈值为 ______；
定向故障 ______ 已实际失败，63 项矩阵为 ______/63；
本结果只支持阶段 E 合成契约，不支持真实 DeepH、材料、DFT 或训练结论；
material/backend/DeepH object/budget/advanced physics = UNRESOLVED_M8。
```

固定命令和完整 payload hash 见[代码说明](../05_code_exercises/stageE_synthetic_equivariance/README.md)，能力定位见[自学导航](chapters/stageE_self_study_guide.md)，端到端应用见[综合问题](../06_exercises/05-stageE/comprehensive/problem/readme.md)与[参考解答](../06_exercises/05-stageE/comprehensive/solution/readme.md)。
