# M7-06 第 19 章第二次定点复核

## 1. 结论

**结论：PASS。** `M7-C19-N01` 已关闭；`M7-C19-B01`、`M7-C19-B02` 无回归；没有新增问题。当前 `BLOCKING=0`、`NON_BLOCKING=0`。明确允许将 M7-06 标记为 `COMPLETED`，并允许启动 M7-07。

本复核由原独立审计员执行。被审教材、推导、例题、练习、答案、来源和门控全程只读；本次唯一新增文件为本报告。

## 2. N01 关闭证据

`04_derivations/stageE/19_equivariant_graph_hamiltonian.md` 当前 SHA-256 为：

`E021C84430750F1E3B857258BD0388AEB8D990AB60CF2D4DDF4BD98E41183F2B`。

第 626 行已经从错误的普通字母序列修订为

\[
F_-=\operatorname{diag}(1,-1,-1).
\]

该式现在把 `diag` 正确表示为对角矩阵算符。相邻公式仍为

\[
F_+=I,
\qquad
\lVert F_+-F_-\rVert_F
=2\sqrt2
=2.8284271247.
\]

独立矩阵复算给出 \(2.8284271247461903\)，与材料显示精度一致。阈值、正负近共线定义域、固定后备轴故障和 T-E09/T-E12 入口均未改变。因此 `M7-C19-N01=CLOSED`。

## 3. B01/B02 回归检查

`M7-C19-B01` 无回归。正文、D-E06、例 19-14、A19-03/A19-10 仍一致保持：

\[
y^{\mathrm{pv}}(R\widehat d)=D^*y^{\mathrm{pv}}(\widehat d),
\qquad
z^{\mathrm{cf}}=\overline{y^{\mathrm{pv}}},
\qquad
z^{\mathrm{cf}}(R\widehat d)=Dz^{\mathrm{cf}}(\widehat d).
\]

`stageE-edge-filter-v1`、递增 \(m\)、dtype/shape、宇称、basis family、三个规范 payload/hash 和 edge-row provenance 均保持第一次复核快照；一般轴复正例、直接输入点值故障及 T-E08/T-E12 映射未变化。

`M7-C19-B02` 无回归。D-E05—D-E07 的统一符号—维度—dtype—基—身份表、分项成立条件、输入/输出、最终不变量、残差对象、定义域和 T-E 入口仍完整。D-E06 的两边消息与一般轴复正反例，以及 D-E07 的双架、局部块不变、\(4\times8\) 回拉、阈值等号、固定后备轴 \(\sqrt2\) 和正负近共线 \(2\sqrt2\) 均保持一致。

## 4. 格式和相邻材料验证

七文件严格 Pandoc/HTML5 MathML/`--fail-if-warnings` 全部通过，MathML 数为 `3/4/161/97/228/16/87`，合计 596。独立 AST 与文本检查结果：

- 活动本地链接 5，断链 0；
- Raw TeX 节点 0；
- 非法控制字符 0；
- `outline.md`/`chapter.md` 三级标题 35/35 完全一致；
- Q19/A19 为 10/10 配对。

来源定位和 M8/M9 授权边界未发生变化。没有安装 DeepH/e3nn，没有引入正式数据或 DFT 标签，也没有隐含选择材料、DFT/数据后端、软件版本或高级物理实践范围。

## 5. 问题状态与退出判断

| 问题 ID | 状态 |
|---|---|
| `M7-C19-B01` | **CLOSED / 无回归** |
| `M7-C19-B02` | **CLOSED / 无回归** |
| `M7-C19-N01` | **CLOSED** |

本次新增问题 0，剩余 `BLOCKING=0`、`NON_BLOCKING=0`。第 19 章当前材料满足完备性、可自学性和可验证性门控，因此总体为 `PASS`：允许完成 M7-06，允许启动 M7-07。
