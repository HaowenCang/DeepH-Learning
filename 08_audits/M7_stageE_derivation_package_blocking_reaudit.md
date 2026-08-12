# M7-08 阶段 E 解析推导包第一次定点复核

## 1. 复核结论

**结论：PASS。** 稳定问题 `M7-DE-B01` 与 `M7-DE-B02` 均为 **CLOSED**。本次复核发现 `BLOCKING=0`、`NON_BLOCKING=0`、新增问题 0、剩余问题 0。

因此允许将 M7-08 标记为 `COMPLETED`，并允许启动 M7-09 合成表示、等变层、自动测试与失败矩阵建设。该放行仅关闭解析推导包门控，不替代 M7-09 的正式 CLI、A/B、144 点、双子进程确定性和故障注入执行，也不改变 M8/M9 与 D-011 边界。

## 2. 独立性、范围与修订快照

本复核由原 M7-08 独立审计员执行，只复核正式报告中两个稳定问题的最小关闭条件、相邻已通过合同和修订引入的新问题。三个主修订文件保持只读；其余六份推导文件同样未修改。本报告是唯一新增文件。

修订快照 SHA-256 为：

| 文件 | SHA-256 | 相对首次审计 |
|---|---|---|
| `04_derivations/stageE/15_group_actions_equivariance.md` | `914FAEBC4C8B36C37EE647A42B35832682BE4A866834CB7F7EBA9A19696F3DB9` | B01 定点修订 |
| `04_derivations/stageE/README.md` | `A65BC7199E9852A49408E31CB1E53BD0F8A3AA4F329DCB931DC1E0E8B016CCFB` | B02 定点修订 |
| `03_textbook/stageE_representation_conventions.md` | `139BB534474A6D585CD5A31D6DF08B2DEE74F9E855929786D075C81FB34579BC` | B02 定点修订 |
| `16_real_spd_representations.md` | `EE59FC78011C45691345D4C7D83651446582D858F83522AD055CFE77C851A23F` | 未改 |
| `17_spherical_harmonics_wigner.md` | `0FE372A2AD42E60374F5FADEFCA30CADFA9B8FA904CAE22544419C9C9AA55179` | 未改 |
| `18_tensor_products_clebsch_gordan.md` | `645BA9326EDFACEC64B276F9029D86C89E63F2E71900DC47CC67121B29E7120A` | 未改 |
| `19_equivariant_graph_hamiltonian.md` | `E021C84430750F1E3B857258BD0388AEB8D990AB60CF2D4DDF4BD98E41183F2B` | 未改 |
| `20_spin_time_reversal_complex.md` | `E3397B367E8AE477B2026AA6935240FC811C458AAAEEBB435621904FA337BE96` | 未改 |

后五份逐项推导与首次审计快照完全相同；D-E02—D-E08 的既有数学内容没有被此次定点修订改写。

## 3. M7-DE-B01：CLOSED

### 3.1 对象、基矩阵与坐标公式

修订后的 D-E01 第 3.1 节明确区分主动旋转和被动换基。旧基矩阵以基向量为列，冻结为右手正交 Cartesian 基：

\[
E_{\mathrm{new}}=E_{\mathrm{old}}R,
\qquad R\in SO(3).
\]

同一物理向量保持不变：

\[
v_{\mathrm{phys}}
=E_{\mathrm{old}}[v]_{\mathrm{old}}
=E_{\mathrm{new}}[v]_{\mathrm{new}}
=E_{\mathrm{old}}R[v]_{\mathrm{new}}.
\]

由 \(E_{\mathrm{old}}^{-1}=E_{\mathrm{old}}^{\mathsf T}\) 得到

\[
[v]_{\mathrm{new}}=R^{\mathsf T}[v]_{\mathrm{old}}.
\]

该推导说明 \(R^{\mathsf T}\) 作用于同一物理对象的新坐标，而主动式 \(v'=Rv\) 作用于固定基中旋转后的物理向量。旧报告指出的对象身份缺失已经消除。文件还明确限制于同一三维 Euclidean 空间的右手正交 Cartesian 基；非正交基必须使用一般逆矩阵。rank、shape、dtype 和有限性拒绝也已写明。

### 3.2 连续复合

两次新基右因子为 \(R_1,R_2\) 时，材料逐步给出

\[
E_1=E_0R_1,
\qquad
E_2=E_1R_2=E_0R_1R_2,
\]

\[
[v]_2=R_2^{\mathsf T}R_1^{\mathsf T}[v]_0
=(R_1R_2)^{\mathsf T}[v]_0.
\]

所以连续被动坐标算符按 \(R_2^{\mathsf T}R_1^{\mathsf T}\) 作用；材料明确说明这不是固定基中的主动 \(R_2R_1\) 对象链。独立生成 200 组一般旋转和向量，\(R_2^{\mathsf T}(R_1^{\mathsf T}v)\) 与 \((R_1R_2)^{\mathsf T}v\) 的最大绝对差为 \(8.88\times10^{-16}\)。

### 3.3 解析正例、定量失败与映射

冻结 \(R_z(\pi/2)\)、\(E_0=I\)、\([v]_0=e_x\) 后，修订给出

\[
[v]_1=R^{\mathsf T}e_x=-e_y,
\qquad
E_1[v]_1=R(-e_y)=e_x=v_{\mathrm{phys}}.
\]

独立复算得到同一坐标与精确回构。若把被动坐标式误作主动旋转，正确 \(Re_x=e_y\) 与错误 \(R^{\mathsf T}e_x=-e_y\) 的归一化残差为 2，与材料一致。

D-E01/T-E01/T-E02 映射现真实指向第 3.1—3.2 节，并列出主动/被动复合、回构正例和残差 2 失败。原有主动 \(R_2R_1\)、行晶格 \(A'=AR^{\mathsf T}\)、距离平方 26、极/轴向量、二阶张量和周期边身份均未改变。因此 `M7-DE-B01=CLOSED`。

## 4. M7-DE-B02：CLOSED

### 4.1 rotations 与四元数生命周期唯一化

README 和统一表示约定现同时冻结：

- `rotations` 唯一指 C-order、目标浮点 dtype、shape \((n_R,3,3)\) 的旋转矩阵数组，nbytes 为 \(9n_Rb\)；
- `quaternion_gaussian_raw` 是 C-order、`float64`、shape \((n_R,4)\) 的预处理临时量；
- 规范单位四元数工作数组使用目标 dtype、同一 \((n_R,4)\) shape；
- 两个四元数数组在 `rotations` 形成后、抽取 \(x_0\) 前释放；
- 两者不进入 reference `array_bytes_total` 或 `array_bytes_peak`；若分析旋转生成阶段峰值，必须按独立操作图逐名报告；
- 释放时点不改变 PCG64 后续节点特征和逐边权重的抽样顺序。

因此原报告指出的 quaternion/rotation 双重解释和生命周期歧义已经消除。

### 4.2 完整逐数组表与解析公式

两份文件均逐名冻结 coordinates、receiver、sender、shift、rotations 以及每个 \(\ell=0,1,2\) 的 \(x_\ell,W_\ell,m_\ell,h'_\ell\) 的 shape、dtype 和 nbytes。令 \(b\) 为目标浮点元素字节数、\(c_\ell=2\ell+1\)、

\[
S_x=\sum_\ell n_\ell c_\ell,
\qquad
S_W=\sum_\ell n_\ell^2,
\]

则材料给出

\[
\mathrm{array\_bytes\_total}
=3Nb+40E+9n_Rb+2NS_xb+ES_Wb+ES_xb,
\]

\[
\mathrm{array\_bytes\_peak}
=3Nb+40E+9n_Rb+2NS_xb+ES_Wb
+\max_\ell(En_\ell c_\ell b).
\]

前式逐项包含 \(x\)、\(h'\)、\(W\)、所有完整物化 \(m\)；后式保留 \(x,h',W\) 常驻并只加入最大单个 \(m_\ell\)。操作图与原 reference kernel 一致。

### 4.3 独立逐项复算

对 float64、\(n_R=1\)、\((n_0,n_1,n_2)=(2,2,1)\)，独立按表复算：

| 数组族 | \(G_A\) | \(G_B\) |
|---|---:|---:|
| coordinates | 96 | 168 |
| receiver + sender + shift | 320 | 720 |
| rotations \((1,3,3)\) | 72 | 72 |
| all \(x_\ell\) | 416 | 728 |
| all \(W_\ell\) | 576 | 1296 |
| all \(m_\ell\) | 832 | 1872 |
| all \(h'_\ell\) | 416 | 728 |
| total | 2728 | 5584 |

最大消息数组为 \(m_1\)，分别为 384/864 bytes，所以 reference peak 为

\[
2728-832+384=2280,
\qquad
5584-1872+864=4576.
\]

同一独立脚本还恢复 \(G_A/G_B\) 的 MAC 168/378 与 aggregation add 52/143。README 和统一约定中的逐项表、解析式和整数锚点完全一致。PCG64 draw order、A/B、固定图、144 点、scan/config 互斥、wall-time 排除和各章局部成本边界均未改变。因此 `M7-DE-B02=CLOSED`。

## 5. 相邻合同与文档回归

七个推导文件均以 `markdown+tex_math_single_backslash`、HTML5 MathML 和 `--fail-if-warnings` 返回 0。MathML 节点分别为：

| 文件 | MathML 节点 |
|---|---:|
| README | 137 |
| D-E01 | 157 |
| D-E02 | 181 |
| D-E03 | 190 |
| D-E04 | 270 |
| D-E05—07 | 228 |
| D-E08 | 143 |
| **合计** | **1306** |

Pandoc JSON AST 解析 27 个本地活动链接，断链 0；RawInline/RawBlock TeX 为 0；数学节点外 TeX 命令候选为 0；C0/DEL 非法控制字符为 0。

相邻回归结果为：

- D-E02—D-E08 文件 hash 与首次审计完全相同；
- 主动列向量、\(R_2R_1\)、行晶格、实 \(p,d\)、\(C/K\)、点值 \(D^*\)/coefficient \(D\)、CG 相位/宇称、\(z^{\mathrm{cf}}=\overline{y^{\mathrm{pv}}}\)、Hamiltonian 双侧作用、逆边、edge row、局部架阈值、标准 Pauli、自旋顺序、\(J_c=KJ_rK^{\mathsf T}\)、H/S k-pair 与 Kramers/TRIM 均无回归；
- D-E09 仍严格区分数学残差、模型误差、reference contraction、receiver 聚合、各章局部成本和可选 wall-time；
- M7-08 仍只冻结 oracle，明确把正式 A/B、144 点、双子进程规范 JSON、自动测试与失败矩阵留到 M7-09。

未发现修订引入新的数学、身份、成本、来源、渲染或授权问题。

## 6. M8/M9 与退出判断

修订没有改变授权边界。M7 后仍须完成 M7-11，并按 D-011 由 `gpt-5.6-sol`/`max` 独立执行 M3—M7 全量总审计；通过后才准备 M8 集中决策冻结。M8 冻结后，M9 的 DeepH/e3nn 安装、正式数据下载、DFT 标签生成或复现实验仍须再次获得明确执行授权。

稳定问题状态为：

| 问题 ID | 原严重度 | 状态 | 剩余条件 |
|---|---|---|---|
| `M7-DE-B01` | BLOCKING | **CLOSED** | 无 |
| `M7-DE-B02` | BLOCKING | **CLOSED** | 无 |

最终计数：`BLOCKING=0`、`NON_BLOCKING=0`、新增问题 0、剩余问题 0。

因此本次定点复核判定 **PASS**，允许完成 M7-08 并启动 M7-09。本报告写入后将独立执行严格 Pandoc/MathML、AST 链接、Raw TeX、数学节点外 TeX 和控制字符检查；稳定 SHA-256 作为交付元数据回报，避免正文自指哈希。
