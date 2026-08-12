# M6-02 第 11 章 B01/N01 定点复核

- 复核日期：2026-08-04
- 复核角色：原 M6-02 独立内容审计员
- 原审计报告：`M6_chapter11_independent_content_audit.md`
- 复核范围：仅复核 M6-CH11-B01、M6-CH11-N01 及其修订是否引入新问题
- 结论：`PASS`
- `BLOCKING=0`
- `NON_BLOCKING=0`
- M6-02：**允许完成**
- M6-03：**允许启动**

## 1. 逐项复核结论

### M6-CH11-B01：`CLOSED`

原问题是 D-D02 把估计误差方差直接当作均方误差，并在缺少完整不相关条件时给出精确的已见组/新组平方误差和 Q11-09 数值结论。

修订后的 `04_derivations/stageD/11_supervised_gradients_leakage.md:119-169` 已完成以下闭合：

- 定义 \(\delta_g=\widehat b_g-b_g\) 和 \(\tau_g^2:=\mathbb E[\delta_g^2]\)，明确 \(\tau_g^2\) 是均方误差，不要求 \(\delta_g\) 无偏；若改用方差，需要另加偏差平方。
- 明确测试噪声分别与已见组估计误差 \(\delta_g\) 及新组随机效应 \(b_g\) 不相关，并说明独立性只是该条件的充分条件。
- 对 \(e_{\mathrm{seen}}=\delta_g-\varepsilon_{g,t}\) 给出包含 \(-2\operatorname{Cov}(\delta_g,\varepsilon_{g,t})\) 的一般均方公式。
- 对 \(e_{\mathrm{new}}=-b_g-\varepsilon_{g,t}\) 给出包含 \(+2\operatorname{Cov}(b_g,\varepsilon_{g,t})\) 的一般均方公式。
- 在两项协方差为零时得到 \(\tau_g^2+\sigma_\varepsilon^2\)、\(\sigma_b^2+\sigma_\varepsilon^2\) 及差值 \(\sigma_b^2-\tau_g^2\)；同时明确非零协方差可以改变差值乃至符号，因而不能无条件声称逐帧评价系统性偏低。

独立代数复核确认上述符号和系数正确。由于 \(\mathbb E[\varepsilon_{g,t}]=0\)，\(\mathbb E[\delta_g\varepsilon_{g,t}]=\operatorname{Cov}(\delta_g,\varepsilon_{g,t})\)，即使 \(\delta_g\) 有偏也成立；\(\tau_g^2\) 已直接包含其偏差平方。

`06_exercises/04-stageD/11_supervised_learning/problem/readme.md:49-51` 已把均方定义和两项不相关条件写入题面。`06_exercises/04-stageD/11_supervised_learning/solution/readme.md:101-119` 在这些条件下得到已见组 \(1.5\)、新组 \(5\)、差值 \(3.5\)，并正确列出两项协方差修正及符号失效边界。题目可以脱离推导上下文独立作答，参考解答与 D-D02 一致。

原 B01 的四项关闭条件全部满足，没有遗留歧义。

### M6-CH11-N01：`CLOSED`

`03_textbook/chapters/11_supervised_learning_optimization/chapter.md:199-205` 已把一层 tanh 网络输出统一为

\[
\widehat y=hv+c\mathbf1.
\]

该式在 \(h\in\mathbb R^{M\times q}\)、\(v\in\mathbb R^q\)、\(c\in\mathbb R\) 下严格属于 \(\mathbb R^M\)，与正文 `chapter.md:207-234` 的梯度形状、D-D01 的 \(Hv+c\mathbf1\) 及 Q11-04 的题面完全一致，不再依赖隐式标量广播。

## 2. 新增与剩余问题

- 新增 `BLOCKING`：0
- 新增 `NON_BLOCKING`：0
- 剩余 `BLOCKING`：0
- 剩余 `NON_BLOCKING`：0

本次修订只改变概率假设闭合、Q11-09 条件/边界和输出偏置记号。未发现其改变 MSE 平均口径、D-D01 梯度、T-D01/T-D02/T-D03 契约、来源边界或 M8/M9 禁止事项。

## 3. 复核性检查

- 四份修订文件严格 Pandoc stdout 解析 4/4 通过，合计产生 165 个 MathML 节点。
- 四份修订文件裸 CR 为 0，非法控制字符为 0。
- 定点复核哈希：
  - `chapter.md`：`4FB33A4E5CB49F4A4AC728958C047A3641D6C48600E1938E3CAF8DB268E75E88`
  - `11_supervised_gradients_leakage.md`：`1340AB3B01581429259BF7BC7AC13204D5CDD85854012DCC14C323099314D8CC`
  - 题目 `readme.md`：`424465AB60657BCD075F322D398861DA0AA07E918A08DCCB4706E6D3EA722A77`
  - 解答 `readme.md`：`7A2503ABAD80FE0091016407E90E9EF0A5EF977B3C974A01122478B60B5E45C5`

上述检查均为只读；未修改送审文件。

## 4. 最终门控结论

M6-CH11-B01 与 M6-CH11-N01 均已关闭，新增及剩余问题均为 0。定点复核结论为 `PASS`，明确允许将 M6-02 标记为 `COMPLETED`，并允许按依赖顺序启动 M6-03 第 12 章原子结构图表示材料建设。
