# M7-02 第 15 章第二次定点复核

## 1. 复核结论

**结论：PASS**

- `M7-02-R1-N01 = CLOSED`。
- 首次审计 `M7-02-B01`—`M7-02-B04`、`M7-02-N01`：无回归，保持 `CLOSED`。
- 新增问题：0。
- `BLOCKING = 0`。
- `NON_BLOCKING = 0`。
- **允许**将 M7-02 标记为 `COMPLETED`。
- **允许**启动 M7-03。

例题 3 新增距离回归说明中的向量差和平方距离现均使用有效数学定界符，并分别生成 MathML。修订未引入数值、链接、题解、来源、章节结构或授权边界回归。第 15 章当前满足材料完备性、可自学性与可验证性门控。

## 2. 定点修复核查

### M7-02-R1-N01：CLOSED

**位置：** `03_textbook/chapters/15_geometric_transformations_equivariance/examples.md:98`。

当前文本已将两段表达写为

\[
u-v=(-1,3,-4)^{\mathsf T},
\qquad
1+9+16=26.
\]

严格 Pandoc 输出确认两段分别生成 inline MathML；第一段的 TeX annotation 保留 `u-v=(-1,3,-4)^{\mathsf T}`，第二段保留 `1+9+16=26`。普通文本 TeX 命令扫描结果为 0，不再出现 `\mathsf` 被剥离的问题。

`examples.md` 严格 `markdown+tex_math_single_backslash` 转换返回 0，生成 61 个 MathML 节点，控制字符错误数为 0。文件 SHA-256 为 `B49003BA17359EBFA6FC7C137B7BBAA9BF6430EC0DD62C640A7A15FDB21F494E`。

## 3. 相邻回归检查

独立复算得到：

\[
\lVert u-v\rVert_2^2=26,
\qquad
\lVert Ru-Rv\rVert_2^2=26,
\]

与修订后的例题和推导一致。错转置定量失败残差为

\[
\rho=\sqrt{5/7}=0.8451542547285166,
\]

与 D-E01/D-E09 的失败锚点一致且远大于 `10^{-4}`。

其余 6 个核心材料文件的 SHA-256 与第一次复核时完全一致：

| 文件 | SHA-256 |
|---|---|
| `sources.md` | `55FF87EAECAA8E25D1B3D23EC71366F357536E2830A7F52401B5090CE8711E00` |
| `outline.md` | `C721E4AB45F85A5ED2A3813B9BB0BC4D561DD582C5D2126923047EC6E4D4FF48` |
| `chapter.md` | `833399ECD426F06891BCCF9ADD9A520353E39986D12DA1ECEF0C25D0B2573333` |
| `15_group_actions_equivariance.md` | `3D8618858684BDDDD2278388BDD5AC56D96693D23895D37E150650C992CDAA5D` |
| `problem/readme.md` | `5FC7A4FB1D0A14F6C24310EBB7C5058FE1A1DCB3D078E79C0D78DD2B8912C687` |
| `solution/readme.md` | `090BDD803BDDB81DED584E02C7EEBCA6C1027DE42E600666AFEF73951DEE950D` |

因此：

- B01 的 `\sqrt{26}` 数值与直接平方回归保持正确；
- B02 的符号—维度表、完整正反例、T-E 映射和 M7-08/M7-09 未执行边界保持完整；
- B03 的 DH-02 论文级来源限制及来源—论断定位保持完整；
- B04 的章节小结与第 16 章接口保持完整；
- 原 N01 的 `R`、`\det R`、`SO(3)`、`O(3)` 数学定界符保持正确。

## 4. 全范围机器检查

7 个送审 Markdown 文件均以严格 `markdown+tex_math_single_backslash` 转换成功，MathML 节点数如下：

| 文件 | MathML 节点 |
|---|---:|
| `sources.md` | 4 |
| `outline.md` | 9 |
| `chapter.md` | 144 |
| `examples.md` | 61 |
| `15_group_actions_equivariance.md` | 121 |
| `problem/readme.md` | 16 |
| `solution/readme.md` | 56 |
| 合计 | 411 |

13 个活动本地链接零断链；7 个文件控制字符错误数为 0；数学定界符外的 TeX 命令候选数为 0。Q15-01—Q15-10 与 A15-01—A15-10 各 10 个，ID 唯一、按序一一对应且内容非空。

## 5. 来源与授权边界回归

章级来源文件继续保留 E-FND-03、E-GNN-01、E-GNN-02、DH-02 和阶段 D 的用途与不得外推边界；DH-02 只作为论文层 Hamiltonian 块关系证据。材料没有安装或导入 DeepH/e3nn，没有使用正式数据、生成 DFT 标签或选择材料、DFT/数据后端、软件对象及高级物理实践范围。

M8 的集中决策冻结与 M9 开始正式安装、下载或复现实验前的二次授权要求均保持不变。

## 6. 门控决定

第二次定点复核确认：

- 全部既有稳定问题为 `CLOSED`；
- 新增问题为 0；
- `BLOCKING=0`；
- `NON_BLOCKING=0`。

因此，独立审计明确允许将 M7-02 标记为 `COMPLETED`，并允许按依赖顺序启动 M7-03。

## 7. 报告完整性

报告自身的严格 Pandoc/MathML、活动本地链接和控制字符检查在写入后独立执行；稳定 SHA-256 由交付回报提供，避免在报告正文内形成自指哈希。
