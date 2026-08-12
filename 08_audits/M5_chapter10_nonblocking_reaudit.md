# M5-06 第 10 章非阻塞项独立定点复核

- 复核日期：2026-08-04
- 原审计：`08_audits/M5_chapter10_independent_content_audit.md`
- 原审计 SHA-256：`AE23CC8F9EBDDF4F86E623AD72620684DCAF80520C1A0F4B0CAD63CEF1CA22B6`
- 复核范围：原审计 `M5-C10-N01`—`M5-C10-N03` 的定点修复，以及修订文件的 Pandoc/Python 回归
- 复核结论：`PASS`
- 原非阻塞项：`CLOSED=3`，`OPEN=0`
- 新增 `BLOCKING`：0 项
- 是否维持 M5-06 `COMPLETED` 许可：**是**
- 是否维持 M5-07 启动许可：**是**

本次只读复核确认 N01—N03 均按原审计建议完成最小修订，且没有改变 T-C10 的衰减族、截断半径、三项指标、数值阈值、来源边界或 M8/M9 授权条件。四个修订文件严格 Pandoc 通过，例题中的四个 Python 块继续全部通过。未发现修订引入新的内容阻塞。

## 1. 修订快照

| 文件 | 复核时 SHA-256 | 与主 agent 提交值 |
|---|---|---|
| `03_textbook/chapters/10_nearsightedness_locality_sparsity/outline.md` | `108989C163D1C2646F3EBCF8142B035ECE96EAFD0638E65465F8836986A678CB` | 一致 |
| `03_textbook/chapters/10_nearsightedness_locality_sparsity/chapter.md` | `D5F2D603BE69814F162835123BAEF71BFE2135A57C629D16C2C848AFA62BC385` | 一致 |
| `03_textbook/chapters/10_nearsightedness_locality_sparsity/examples.md` | `30CB8ECC09C5DE5F14DB3341BF0A71BC20405876F1F46ECA8CD99681C524CDEC` | 一致 |
| `04_derivations/stageC/10_nearsightedness_sparsity.md` | `F72E9C78EB0D7B0D566D0388DCA88649BD2BFBCD1472775F37A081B604F929E4` | 一致 |

除新增本复核报告外，本独立复核未修改任何教材、推导、题解、计划或追踪器。

## 2. 定点 finding 复核

### M5-C10-N01：`CLOSED`

**原问题。** 例 10-3 定义 `H=diag(-2,-1,0,1,2,3)`，正文却称其有 6 个非零元素；代码和参考解答采用正确值 5。

**复核证据。** `examples.md:121` 现明确写为：由于一个对角元恰为零，`H` 只有 5 个非零元素，变换后的 `H'` 在本例中有 36 个非零元素。该表述与同文件 Python 断言

```python
assert np.count_nonzero(np.abs(H) > 1e-12) == 5
assert np.count_nonzero(np.abs(H_rotated) > 1e-12) == dimension**2
```

及参考解答保持一致。例 10-3 独立执行通过，幺正性和等谱断言未回归。

**判定。** N01 已关闭；无剩余问题。

### M5-C10-N02：`CLOSED`

**原问题。** T-C10 的一般输入域 `N=grid-size>=48` 只在工作包冻结；章级材料只显示代表值 `N=64`。

**复核证据。** `chapter.md:138` 现声明矩阵维数取冻结 CLI 的

\[
N=\text{grid-size}\ge48,
\]

并说明本章例题使用合法实例 `N=64`。`D-C08:159` 同时声明两个衰减族均为 `N x N`，并明确冻结 CLI 分别使用 `N=64` 与 `N=48`。这使一般参数域、章级代表实例和后续两组冻结运行之间的关系均可独立定位。修订没有改变距离矩阵、衰减函数、`Rc=(2,4,8,16)`、拟合窗口或容差。

**判定。** N02 已关闭；无剩余问题。

### M5-C10-N03：`CLOSED`

**原问题。** 三级提纲承诺“稀疏率—截断范数—能带差三联表”，而实际 T-C10 和例 10-1 的第三指标为作用量误差。

**复核证据。** `outline.md:25` 已改为“稀疏率—截断范数—作用量误差三联表”。该标题现在与正文定义的非零比例、相对 Frobenius 截断误差和 `y=A1/N` 相对作用量误差，以及例 10-1 和冻结 T-C10 一致。材料仍在其他小节把广义谱和目标物性保留为独立误差层级，没有把作用量误差冒充能带误差。

**判定。** N03 已关闭；无剩余问题。

## 3. 回归验证

对四个修订文件逐一执行：

```text
pandoc <file> \
  --from markdown+tex_math_dollars+tex_math_single_backslash \
  --to html5 --mathml --fail-if-warnings
```

结果为 `4/4` 退出码 0。`examples.md` 仍恰含 4 个 Python 围栏；使用固定解释器 Python 3.12.13、NumPy 2.3.5 原样独立执行，结果为 `4/4` 退出码 0。例 10-1 的截断指标、例 10-2 的指数斜率与代数外推失败、例 10-3 的 `5 -> 36` 非零元素反例以及例 10-4 的截断/采样分轴结论均未回归。

修订仅补正局部计数、一般参数域和提纲标题。未发现新的数学错误、T-C10 协议漂移、DeepH 来源越权、正式数据/软件动作或隐含实践对象选择。

## 4. 最终判定

- `M5-C10-N01=CLOSED`；
- `M5-C10-N02=CLOSED`；
- `M5-C10-N03=CLOSED`；
- 原非阻塞项剩余数量：0；
- 新增 `BLOCKING=0`；
- 新增 `NON_BLOCKING=0`；
- **维持 M5-06 可标记为 `COMPLETED` 的结论；**
- **维持 M5-07 可启动的结论。**

本次定点复核不替代后续 M5 阶段总审计；但就原审计 N01—N03 及其修订回归而言，问题已经全部关闭。
