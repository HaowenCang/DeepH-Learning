# M6-03 第 12 章第二次最小定点复核

- 复核日期：2026-08-04
- 复核角色：原 M6-03 独立内容审计子 agent
- 前次复核：`M6_chapter12_blocking_reaudit.md`
- 复核范围：前次剩余 `M6-CH12-B03` 与新增 `M6-CH12-N01`
- 复核方式：只读逐行核对与零基索引独立复算
- 总结论：`PASS`
- `BLOCKING=0`
- `NON_BLOCKING=0`
- 新增问题：`0`
- 剩余问题：`0`
- M6-03：**允许完成**
- M6-04：**允许启动**

## 1. M6-CH12-B03：CLOSED

复核位置：

- `03_textbook/chapters/12_atomic_graph_representation/chapter.md:247-277`
- 尤其 `03_textbook/chapters/12_atomic_graph_representation/chapter.md:253-265`
- `03_textbook/chapters/12_atomic_graph_representation/examples.md:45-55`
- `06_exercises/04-stageD/12_atomic_graph/problem/readme.md:35-37`
- `06_exercises/04-stageD/12_atomic_graph/solution/readme.md:89-117`
- `08_audits/M6_stageD_work_package.md:162-166`

正文的计数关系现已改为

\[
\sum_{a=0}^{P_{\max}-1}\texttt{mask}_{ea}=p_i p_j,
\]

与同段冻结的零基有效位置

\[
\texttt{mask}_{ea}\iff 0\le a<p_i p_j
\]

完全一致。对 \(p_i=2,p_j=3,P_{\max}=9\)，合法 mask 在 \(a=0,\ldots,5\) 为真，按修订后的求和范围恰好计得 6；不存在遗漏 \(a=0\) 或访问 \(a=P_{\max}\) 的越界。

\(P_{\max}\) 下界、右侧连续 padding、行优先展平、\(\alpha=\lfloor a/p_j\rfloor\)、\(\beta=a\bmod p_j\)、节点有序轨道列表、逐分量 int64 索引数组、padding=\(-1\) 及两类失败夹具均保持不变。前次指出的最后一个零基/一基冲突已经消除，B03 全部关闭。

## 2. M6-CH12-N01：CLOSED

复核位置：

- `03_textbook/chapters/12_atomic_graph_representation/examples.md:3`
- `03_textbook/chapters/12_atomic_graph_representation/examples.md:18`
- `03_textbook/chapters/12_atomic_graph_representation/examples.md:29`
- `03_textbook/chapters/12_atomic_graph_representation/examples.md:41`
- `03_textbook/chapters/12_atomic_graph_representation/examples.md:45`
- `03_textbook/chapters/12_atomic_graph_representation/examples.md:57`
- `03_textbook/chapters/12_atomic_graph_representation/examples.md:61`
- `03_textbook/chapters/12_atomic_graph_representation/examples.md:65`

例题标题现按文件顺序连续为：

1. 例 12-1 三节点置换；
2. 例 12-2 合法多重边与非法重复；
3. 例 12-3 双向展开；
4. 例 12-4 聚合碰撞；
5. 例 12-5 可变轨道块 mask；
6. 例 12-6 空入边聚合；
7. 例 12-7 拼接批中的跨图边；
8. 例 12-8 逐边排序与输出配对。

编号严格递增，未发现正文、练习、解答或工作包对后三例存在旧编号引用。N01 已关闭。

## 3. 最小回归检查

- B01、B02 的既有关闭结论未受本次两处修订影响：拼接/padding 批 schema、跨图边断言、空 sum/mean 和 max 拒绝策略均未改变。
- B03 的正文、例题、Q12-07/A12-07 与工作包 4.5/T-D09 现统一采用零基展平和连续 prefix mask。
- `chapter.md` 与 `examples.md` 均可按 UTF-8 严格解码；裸 CR 为 0，非法控制字符为 0。
- 未发现本次修复引入的新问题；未修改任何送审文件，唯一写入为本复核报告。

## 4. 最终门控结论

前次剩余 B03 与新增 N01 均为 `CLOSED`，新增及剩余问题均为 0。当前 `BLOCKING=0`、`NON_BLOCKING=0`，结论为 `PASS`。

本独立复核明确允许将 M6-03 标记为 `COMPLETED`，并允许启动 M6-04。
