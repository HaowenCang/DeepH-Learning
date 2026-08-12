# M7-06 第 19 章第一次阻塞项定点复核

## 1. 结论

**结论：FAIL。** 原稳定问题 `M7-C19-B01`、`M7-C19-B02` 均已关闭，当前 `BLOCKING=0`；相邻回归发现新的 `M7-C19-N01`，当前 `NON_BLOCKING=1`。因此仍不允许完成 M7-06，也不允许启动 M7-07。N01 修订后须由本独立审计员再次复核。

本复核由原独立审计员执行。被审教材、推导、例题、练习、答案、来源和门控全程只读；本次唯一新增文件为本报告。

## 2. 当前送审快照

| 文件 | SHA-256 |
|---|---|
| `sources.md` | `C5DFA7DCECE7E32326BF681BE61F2864ACE80C8C82EC08D51AC2ABF7606615D9` |
| `outline.md` | `3A7F34120FD10AF1F9504386E1BFA271CB66C06CE662666572CA82898B523502` |
| `chapter.md` | `E644E2A7E87E6ADB1F5635A3476903FA752B9359FA26E0330D1F54E839B00D0A` |
| `examples.md` | `64F9927CCBC64828AAB663F1F13DC22CCB37F6FAE6FE5B90D3E5A36BFB22FA66` |
| `19_equivariant_graph_hamiltonian.md` | `20F2CACDF708EFCEE2ABA7763B6930B32EDA4F9D8B76FB147BC5BCF03B37C52F` |
| `problem/readme.md` | `7326494AF5ECA7151B94AFF1456C97C36F495EB41B86C32E5F208A2EA0A03B37` |
| `solution/readme.md` | `D29D9050818D07D52D4395CBD7F696718A2FEDB801CBA65FBCD4D670312AB053` |

独立计算所得哈希与送审登记完全一致。

## 3. M7-C19-B01 复核

**状态：CLOSED。**

正文、D-E06、例 19-14、A19-03 和 A19-10 已明确且一致地冻结：

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

规范 CG 的第二输入均为 \(z^{\mathrm{cf}}\)，不再直接使用点值。材料同步规定 \(m=-\ell,\ldots,\ell\) 升序、单边 shape \((2\ell+1,)\)、边数组 shape \((E,2\ell+1)\)、`complex128`/`complex64`、宇称 \((-1)^\ell\)、basis family `dlmf-cs-pointvalue-conjugate`、version `stageE-edge-filter-v1`，以及 edge row、完整 edge key/ID、方向、\(\ell\)、version/hash 和 provenance 不变。T-E08/T-E12 的正例和定向失败入口已经补齐。

三个规范 payload 的独立紧凑 UTF-8 JSON 哈希为：

| \(\ell\) | payload | SHA-256 |
|---:|---|---|
| 0 | `["stageE-edge-filter-v1","dlmf-cs-pointvalue-conjugate",0,[0],"complex","z=conjugate(y)"]` | `549A79B3656BAA8736315F6D12F195013301C0FCDFE97BFDF3C73ECD85F58692` |
| 1 | `["stageE-edge-filter-v1","dlmf-cs-pointvalue-conjugate",1,[-1,0,1],"complex","z=conjugate(y)"]` | `55144ADBD95056208733AB51FF2EFB16789A95A855234641A4521C41FB577D06` |
| 2 | `["stageE-edge-filter-v1","dlmf-cs-pointvalue-conjugate",2,[-2,-1,0,1,2],"complex","z=conjugate(y)"]` | `1A940F1CDCBC62B99BA56D6AA5E50619FB96C85FB0DDCC86913405CBACA97295` |

三项与正文逐字节一致。

按例 19-14 独立构造 Rodrigues 旋转、冻结 \(K_1\)、DLMF-CS 点值和 coefficient Wigner 矩阵，得到：

- 正确 filter 残差 `6.618174011697163e-17`；
- 直接把点值当 coefficient 的故障残差 `0.5219896443149824`。

以独立 seed 1906 对 \(\ell=1,2\) 各执行 200 个一般轴与随机球面点，正确路线最大残差为 \(2.37\times10^{-16}\)、\(5.25\times10^{-16}\)；错误点值按 \(D\) 比较的最大残差为 \(0.9749763\)、\(1.0925483\)。因此原 B01 的公式、schema、数值和失败入口均已实质关闭。

## 4. M7-C19-B02 复核

**状态：CLOSED。**

推导第 2.1 节已增加 D-E05—D-E07 统一符号—维度—dtype—基—身份表，覆盖 \(H,D_i,D_j,x,y^{\mathrm{pv}},z^{\mathrm{cf}},w,C,m,a,h,u,v,F,U_i,U_j,\overline H\) 的 rank、shape、表示基及 node/edge/path/shell/orbital 身份。第 3、4、8 节分别列出 D-E06、D-E05、D-E07 的输入、输出、成立条件、最终不变量和 T-E 入口；第 11 节按三项汇总残差对象、定义域及退出门控。

D-E06 第 3.6 节已包含两边实消息：

\[
m_1=(2,0,0)^{\mathsf T},\quad
m_2=(0,3/2,0)^{\mathsf T},\quad
a_i=(2,3/2,0)^{\mathsf T},
\]

在 \(R_z(\pi/2)\) 下逐边与聚合残差均为 0；同节还包含一般轴复正反例并映射到 T-E08/T-E12。

D-E07 第 8.5 节给出两个不同非退化架、\(U_i=1\oplus F_i\)、\(U_j=F_j\oplus D^d(F_j)\) 和完整 \(4\times8\) 局部块。独立复算全部 32 个显示项一致，且：

- 局部块不变残差 `3.344731488386981e-16`；
- 原架局部化—回拉残差 `2.730550825873186e-16`；
- 旋转后全局回拉残差 `2.0733316800407606e-16`。

float64/float32 的阈值复算均得到：零长度比例 \(0,0.5\tau_0,\tau_0\) 拒绝而 \(2\tau_0\) 接受；近共线比例 \(0,\tau/4,\tau/2,\tau\) 拒绝而 \(2\tau,4\tau\) 接受；等号拒绝。固定全局 \(e_y\) 后备轴的故障为 \(\sqrt2=1.4142135623730951\)，正负近共线接受侧框架跳变为 \(2\sqrt2=2.8284271247461903\)。D-E07 已明确接受域、阈值拒绝域和近退化不连续。原 B02 已关闭。

## 5. 格式、来源与授权边界

七文件严格 Pandoc/HTML5 MathML/`--fail-if-warnings` 全部通过，MathML 数为 `3/4/161/97/228/16/87`，合计 596。Pandoc AST 检查结果：

- 活动本地链接 5，断链 0；
- Raw TeX 节点 0；
- 非法控制字符 0；
- `outline.md`/`chapter.md` 三级标题 35/35 完全一致；
- Q19/A19 为 10/10 配对。

阶段 E README 登记的 11 个直接来源快照实际 SHA-256 全部一致。来源定位仍只把 TFN/e3nn/DeepH-E3 用作论文级机制或任务联系，没有安装 DeepH/e3nn、引入正式数据或 DFT 标签，也没有选择软件版本、材料、DFT/数据后端、SOC/磁性范围或训练预算。M8 集中决策与 M9 二次授权边界无回归。

## 6. 新问题

### M7-C19-N01：近共线负侧框架的 diag 算符遗漏 TeX 反斜杠

**严重度：NON_BLOCKING。**

`04_derivations/stageE/19_equivariant_graph_hamiltonian.md:626` 当前写为

\[
F_-=operatorname{diag}(1,-1,-1),
\]

而不是

\[
F_-=\operatorname{diag}(1,-1,-1).
\]

Pandoc 可以转换前者，因而严格转换不会报警，但其 MathML 语义是普通数学字母组成的 `operatorname`，不是对角矩阵算符。上下文、独立矩阵复算和 \(2\sqrt2\) 结果均证明预期对象明确，因此该项不构成 B02 残留或数值错误，但仍是正式推导中的公式排版语义缺陷。

**最小关闭条件：** 仅把该处 `operatorname{diag}` 改为 `\operatorname{diag}`，重跑七文件严格 Pandoc/MathML、Raw TeX/控制字符及相邻近共线公式检查。不得改变阈值、矩阵、跳变值或其他已关闭合同。

## 7. 退出判断

| 问题 ID | 状态 |
|---|---|
| `M7-C19-B01` | **CLOSED** |
| `M7-C19-B02` | **CLOSED** |
| `M7-C19-N01` | **NEW / OPEN** |

当前 `BLOCKING=0`、`NON_BLOCKING=1`、原问题遗留 0、新增问题 1。零问题门控尚未满足，故总体为 `FAIL`：不允许完成 M7-06，不允许启动 M7-07。
