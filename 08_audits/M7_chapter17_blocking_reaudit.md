# M7-04 第 17 章第一次定点复核

## 1. 复核结论

**结论：PASS**

- M7-C17-B01：CLOSED
- M7-C17-B02：CLOSED
- M7-C17-N01：CLOSED
- 新增 BLOCKING = 0
- 新增 NON_BLOCKING = 0
- 剩余 BLOCKING = 0
- 剩余 NON_BLOCKING = 0
- **允许**将 M7-04 标记为 COMPLETED。
- **允许**启动 M7-05。

修订快照已经唯一冻结球谐方向的无量纲近零 validator、完整 shell/mask/padding 规则、stageD-edge-v1 边身份不变量、统一 shell-pair 轴、复分量 provenance 和 \(K_1/K_2\) 规范载荷哈希；冻结提纲与正文三级标题严格一致，并新增 \(R_x(\pi/2)\) 的实—复双路线工作例。独立格式检查、哈希复算和数值复算未发现相邻回归或新增问题。

## 2. 范围与独立性

本次只读复核了：

- 第 17 章 sources.md、outline.md、chapter.md 与 examples.md；
- D-E03/D-E09 子推导 17_spherical_harmonics_wigner.md；
- Q17-01—Q17-10 与 A17-01—A17-10；
- M7_stageE_work_package.md、stageE_representation_conventions.md；
- 第 16 章实 \(p,d\) 接口；
- stageD_graph_conventions.md、M6_stageD_work_package.md 中的 edge、mask 与 provenance 契约；
- DLMF 14.30 和阶段 E 来源索引；
- M8/M9 授权边界。

复核没有采用主 agent 的修复说明替代独立判断。除本报告外，没有创建或修改其他文件。

## 3. 严格文档门控

七个送审文件均以 markdown+tex_math_single_backslash 输入格式、HTML5/MathML 输出格式和 fail-if-warnings 重新执行 Pandoc：

| 文件 | Pandoc exit code | MathML 节点 |
|---|---:|---:|
| sources.md | 0 | 6 |
| outline.md | 0 | 10 |
| chapter.md | 0 | 162 |
| examples.md | 0 | 84 |
| 17_spherical_harmonics_wigner.md | 0 | 190 |
| problem/readme.md | 0 | 48 |
| solution/readme.md | 0 | 93 |
| 合计 | 7/7 通过 | 593 |

Pandoc JSON AST 共解析 11 个活动本地链接，缺失目标为 0。C0/DEL 控制字符、普通文本 TeX 残留和 RawInline/RawBlock TeX 均为 0。

Q17-01—Q17-10 与 A17-01—A17-10 均为 10 个唯一、连续、非空对象，ID 集合严格一一对应。outline.md 与 chapter.md 的 36 个二、三级标题按顺序、层级和标题文本逐项相同。

## 4. 原问题定点判定

### 4.1 M7-C17-B01：CLOSED

原问题要求方向 validator 不得使用未定义的 dtype 绝对长度阈值，而须冻结有限正尺度 \(s\)、无量纲

\[
\zeta_d=\frac{\lVert d\rVert_2}{s},
\]

以及 dtype 阈值、等号方向和两侧夹具。

修订后的正文 17.6.1、例题 7、推导第 9 节和 A17-08 已共同规定：

- 输入为有限 \(d\)、显式 \(s\) 与 dtype，且 \(s\) 必须有限并严格大于 0；
- float64 使用 \(\tau_0=10^{-12}\)，float32 使用 \(\tau_0=10^{-5}\)；
- 仅当 \(\zeta_d>\tau_0\) 时接受，\(\zeta_d=\tau_0\) 拒绝；
- 四点夹具为
  \[
  d_\varepsilon=(\varepsilon s,0,0),
  \qquad
  \varepsilon\in\{0,\tfrac12\tau_0,\tau_0,2\tau_0\};
  \]
- 前三点拒绝，最后一点接受；
- NaN、无穷、\(s\le0\) 与错误 rank/shape 在归一化前拒绝；
- \(d,s\) 同时按相同正尺度缩放时判定不变；
- 此处仅复用局部架合同的单向量零长度子规则，不引入第二参考向量或共线指标 \(\eta\)；
- 方向求值映射到 T-E04，schema、非法尺度和阈值失败映射到 T-E12。

独立使用实际 float64/float32 运算复算 \(s=2\) 的四点夹具，结果均分别为

\[
(0,\tfrac12\tau_0,\tau_0,2\tau_0),
\]

判定依次为 reject、reject、reject、accept。float32 存储的 \(10^{-5}\) 在等号夹具中与实际 \(\zeta_d\) 相等，未发生边界方向漂移。因此 B01 的公式条件、尺度协变性和自动门控入口均已唯一，问题关闭。

### 4.2 M7-C17-B02：CLOSED

原问题要求 Hamiltonian 基变换兑现 sources.md 已声明的完整 shell、mask、padding、edge identity 与 provenance 契约。

修订后的正文 17.8.2、推导第 12 节和 A17-10 已明确：

- \(K_i\) 按 shell ID 与 multiplicity ID 构造活动 shell 的块对角直和；
- 每个活动 \(\ell\) shell 必须完整包含 \(2\ell+1\) 个分量；
- component mask 对一个 shell 只允许全真或全假，部分真/部分假必须拒绝；
- 全假 padding shell 在稠密 \(K_\ell\) 作用前切除，变换后按原槽位恢复并保持全假；
- 只有行、列 shell 的完整笛卡尔积有效时，才执行
  \[
  H_{\alpha\beta,\mathrm c}
  =K_{\ell_\alpha}H_{\alpha\beta,\mathrm r}K_{\ell_\beta}^\dagger;
  \]
- 纯轨道基变换保持 stageD-edge-v1 的 structure ID、receiver、sender、整数周期 shift、完整 edge key 和 edge 行序不变；
- Hamiltonian、两端表示、component mask 与 provenance 使用同一 edge-row/shell-pair 轴映射；
- 复分量 provenance 记录 structure/atom/edge identity、shell/multiplicity、\(\ell\)、宇称、real-spd-v1 源基、complex-dlmf-cs-v1 目标基、递增 \(m\)、stageE-K-coeff-v1、载荷哈希和完整源 component 支持集合；
- 复分量不得伪装成一个未变化的实 orbital component ID。

该 edge payload 与阶段 D 的

["stageD-edge-v1",structure_id,receiver,sender,nx,ny,nz]

一致。sources.md 的阶段 D、DH-02、D-E03/D-E09 与 T-E06/T-E12 定位现均可在正文、推导和 A17-10 中逐项找到，不再存在过度声明。

本次还独立复算了 stageE-K-coeff-v1 的两个 ASCII 紧凑 JSON 载荷：

| 对象 | 独立 SHA-256 | 材料值 |
|---|---|---|
| \(K_1\) | 347E352605A3F4F3CCB078B6CEDF5C755FDC6AA3527EA41A8EA3E93D076972A2 | 一致 |
| \(K_2\) | 5E783D9CDFE025238977F9E92D64D8B46E9A0E79EB8C9DEBA1AF116AAAFC7B82 | 一致 |

对 300 个随机 \(3\times5\) 实 \(p\)-\(d\) shell-pair 块执行

\[
H_{\mathrm c}=K_1H_{\mathrm r}K_2^\dagger,
\qquad
H_{\mathrm r}'=K_1^\dagger H_{\mathrm c}K_2,
\]

最大往返 Frobenius 误差为 \(1.95\times10^{-15}\)。另对随机旋转验证实基协变、基变换与复基两端协变的交换图，误差为 \(8.32\times10^{-16}\)。公式、块轴和来源定位均无相邻矛盾，B02 关闭。

### 4.3 M7-C17-N01：CLOSED

outline.md 已按实际材料重排，和 chapter.md 的 36 个二、三级标题严格相同。原来承诺但缺失的一般轴工作例现已加入 examples.md 例题 3 和 D-E03 第 7.3 节。

冻结旋转为

\[
R_x(\pi/2)=
\begin{pmatrix}
1&0&0\\
0&0&-1\\
0&1&0
\end{pmatrix}.
\]

独立从第 16 章 \(B_a\) 共轭重建 \(D^d_{\mathrm r}(R_x)\)，再由

\[
D^{(1)}_{\mathrm c}=K_1R_xK_1^\dagger,
\qquad
D^{(2)}_{\mathrm c}=K_2D^d_{\mathrm r}(R_x)K_2^\dagger
\]

复算送审的 \(3\times3\) 与 \(5\times5\) 复矩阵，最大逐元素误差分别为 \(1.11\times10^{-16}\) 和 \(1.67\times10^{-16}\)。两矩阵的幺正误差分别为 \(5.46\times10^{-16}\)、\(1.22\times10^{-15}\)，四次幂单位元误差分别为 \(1.09\times10^{-15}\)、\(2.44\times10^{-15}\)。反向相似变换恢复 \(R_x,D^d_{\mathrm r}(R_x)\) 的误差分别为 \(4.60\times10^{-16}\)、\(5.13\times10^{-16}\)。

该例不是 \(z\) 轴对角矩阵的改写，实际提供了实 \(p/d\) 双路线、群律和逆变换交叉验证。N01 关闭。

## 5. 相邻回归与新增问题检查

使用 PCG64 seed 20260810 独立生成 300 组一般轴旋转并复算原章核心不变量：

| 检查 | 最大误差 |
|---|---:|
| \(\ell=1\) 复表示群律 | \(7.14\times10^{-16}\) |
| \(\ell=2\) 复表示群律 | \(1.34\times10^{-15}\) |
| \(\ell=1\) 幺正性 | \(2.77\times10^{-15}\) |
| \(\ell=2\) 幺正性 | \(6.20\times10^{-15}\) |
| \(\ell=1\) 点值 \(D^*\) 协变 | \(2.40\times10^{-16}\) |
| \(\ell=2\) 点值 \(D^*\) 协变 | \(5.86\times10^{-16}\) |

DLMF 14.30 本地快照 SHA-256 仍为

D4547C98B7DAA72A6358233A78646A49013D9110FDD817E8CAF139F3CBDA9154，

与阶段 E README 一致。Condon--Shortley、递增 \(m\)、函数值 \(C_\ell\)、系数 \(K_\ell=C_\ell^*\)、点值 \(D^*\)/系数 \(D\)、宇称、未同步逆序残差和实/复字节子预算均无回归。

送审材料没有安装或导入 DeepH/e3nn，没有正式数据或 DFT 标签，没有选择材料体系、DFT/数据后端、DeepH 软件对象、实践版本、Euler 软件接口或高级物理范围。M8 集中冻结和 M9 外部动作前二次授权仍完整。

未发现新增 BLOCKING 或 NON_BLOCKING 问题。

## 6. 放行判定

M7-C17-B01、M7-C17-B02 与 M7-C17-N01 已全部关闭，新增及剩余问题均为 0。第 17 章在材料完备性、可自学性、可验证性、来源定位、数值正确性和授权边界上达到 M7-04 章级门控。

因此允许主 agent 将 M7-04 标记为 COMPLETED，并按依赖顺序启动 M7-05。

## 7. 报告完整性

本报告写入后将独立执行严格 Pandoc/MathML、Pandoc AST 活动本地链接、控制字符和普通文本 TeX 残留检查。报告 SHA-256 在交付回报中给出，避免正文自指哈希。
