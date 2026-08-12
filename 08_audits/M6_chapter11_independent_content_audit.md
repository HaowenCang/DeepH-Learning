# M6-02 第 11 章正式独立内容审计

- 审计日期：2026-08-04
- 审计角色：独立内容审计子 agent
- 审计方式：只读检查、公式重推、独立数值复算、来源与边界核对
- 总结论：`FAIL`
- `BLOCKING=1`
- `NON_BLOCKING=1`
- M6-02：**不得完成**
- M6-03：**不得启动**

第 11 章已经覆盖监督回归对象、经验风险与目标风险、结构组划分、训练/验证/测试职责、预处理泄漏、MSE 平均口径、线性与一层 tanh 网络反向传播、有限差分、严格凸二次目标步长、正则化、早停、合成数据边界及 M8/M9 禁令。线性梯度、tanh 梯度、有限差分、步长谱半径、六个例题和十组题解的独立复算均未发现数值错误。当前失败的原因是 D-D02 把“估计误差方差”直接当作均方误差，并在未声明新组偏置与测试噪声不相关的情况下给出精确平方误差与系统性低估结论；Q11-09 的数值解答继承了这一未闭合假设。另有一处 tanh 输出偏置记号与本章自己的形状规范不一致。

## 1. 审计范围

送审材料包括：

- `03_textbook/chapters/11_supervised_learning_optimization/sources.md`
- `03_textbook/chapters/11_supervised_learning_optimization/outline.md`
- `03_textbook/chapters/11_supervised_learning_optimization/chapter.md`
- `03_textbook/chapters/11_supervised_learning_optimization/examples.md`
- `04_derivations/stageD/11_supervised_gradients_leakage.md`
- `06_exercises/04-stageD/11_supervised_learning/problem/readme.md`
- `06_exercises/04-stageD/11_supervised_learning/solution/readme.md`
- `08_audits/M6_stageD_work_package.md` 中 D-D01/D-D02、T-D01/T-D02/T-D03 及教材门控
- `03_textbook/stageD_graph_conventions.md` 中数值环境与 M8 前授权边界

未修改任何送审文件。唯一写入为本审计报告。

## 2. 问题清单

### M6-CH11-B01：D-D02 的精确均方误差比较缺少零偏与不相关条件

- 级别：`BLOCKING`
- 位置：
  - `04_derivations/stageD/11_supervised_gradients_leakage.md:122-128`
  - `04_derivations/stageD/11_supervised_gradients_leakage.md:130-148`
  - `06_exercises/04-stageD/11_supervised_learning/problem/readme.md:49-51`
  - `06_exercises/04-stageD/11_supervised_learning/solution/readme.md:101-119`

D-D02 把已见组估计误差的“方差”记为 \(\tau_g^2\)，随后直接使用

\[
\mathbb E[(\widehat b_g-b_g)^2]=\tau_g^2.
\]

该等式还要求估计误差 \(\delta_g:=\widehat b_g-b_g\) 零均值；否则应为

\[
\mathbb E[\delta_g^2]
=\operatorname{Var}(\delta_g)
+\mathbb E[\delta_g]^2.
\]

也可以不要求零偏，但必须从一开始把 \(\tau_g^2\) 定义为均方误差 \(\mathbb E[\delta_g^2]\)，而不是方差。

此外，文本只声明测试噪声与 \(\widehat b_g\) 的估计误差独立，没有声明新组随机效应 \(b_g\) 与测试噪声 \(\varepsilon_{g,t}\) 不相关。忽略公共斜率误差时，两个预测误差实际满足

\[
\mathbb E[e_{\mathrm{seen}}^2]
=\mathbb E[\delta_g^2]
+\sigma_\varepsilon^2
-2\operatorname{Cov}(\delta_g,\varepsilon_{g,t}),
\]

\[
\mathbb E[e_{\mathrm{new}}^2]
=\sigma_b^2
+\sigma_\varepsilon^2
+2\operatorname{Cov}(b_g,\varepsilon_{g,t}),
\]

其中交叉项的符号取决于误差定义，但其不能在未给条件时被删除。当前材料不足以推出 Q11-09 解答中的精确数值 \(1.5\)、\(5\) 和差值 \(3.5\)，也不足以无条件推出逐帧评价必然系统性偏低。D-D02 已正确说明结论不是任意数据集的普遍定量界，但适用模型本身的矩条件仍未闭合。

关闭条件：

1. 显式定义 \(\delta_g=\widehat b_g-b_g\)，并选择以下一种一致口径：假设 \(\mathbb E[\delta_g]=0\) 且 \(\operatorname{Var}(\delta_g)=\tau_g^2\)，或直接定义 \(\tau_g^2:=\mathbb E[\delta_g^2]\)。
2. 显式假设测试噪声分别与 \(\delta_g\) 及新组 \(b_g\) 不相关；使用独立性作为充分条件亦可。
3. 在这些条件下推导已见组与新组总平方误差及其差，并说明有偏或存在协方差时需要增加哪些项、原“系统性低估”结论何时不再成立。
4. 同步修订 Q11-09 的题面与参考解答，使数值结论的条件可从题面独立获得。

### M6-CH11-N01：tanh 输出偏置记号依赖未声明的标量广播

- 级别：`NON_BLOCKING`
- 位置：
  - `03_textbook/chapters/11_supervised_learning_optimization/chapter.md:199-205`
  - `03_textbook/chapters/11_supervised_learning_optimization/chapter.md:207-234`
  - 对照 `04_derivations/stageD/11_supervised_gradients_leakage.md:14-18`

正文定义 \(h\in\mathbb R^{M\times q}\)、\(v\in\mathbb R^q\)、\(c\in\mathbb R\)，却写成 \(\widehat y=hv+c\)。按严格线性代数形状，\(hv\in\mathbb R^M\) 不能直接与标量相加；同一正文稍后又要求不能依赖隐式广播。推导文件和练习已采用无歧义的 \(Hv+c\mathbf1\)，因此解析梯度本身正确，但正文记号对自学者不一致。

关闭条件：把正文输出式统一为 \(\widehat y=hv+c\mathbf1\)，或在首次出现时明确定义“标量加向量”表示逐分量加偏置；前一种方式与推导和练习完全一致。

## 3. 已通过项目

### 3.1 监督学习对象与评价边界

- `chapter.md:11-25` 明确定义 \((x_s,y_s,g_s)\)、模型预测和结构组作用，并把阶段 D 限于合成输入与合成标签。
- `chapter.md:27-47` 区分经验风险与目标风险，没有把训练风险下降外推为目标风险下降。
- `chapter.md:49-59`、`63-82` 正确分离参数、超参数和随机种子，明确测试集不得参与梯度、预处理、模型选择、早停或阈值回调；训练统计量复用于验证/测试的口径正确。
- `chapter.md:84-120` 给出组三集合两两不交条件，并准确区分已见组插值、新组评价、组成外推和时间外推；没有声称单一分组适合所有任务。

### 3.2 MSE、梯度、有限差分与步长

- 标量 MSE 的 \(1/M\)、多输出逐元素 MSE 的 \(1/(Mp)\) 和批 MSE 的 \(1/B\) 口径明确；正文同时指出逐元素、逐块和逐结构平均不等价。
- 线性回归梯度中的系数 \(2/M\)、偏置梯度和矩阵形状正确。
- 除 N01 的输出记号外，一层 tanh 网络的 \(\delta_y\)、\(\delta_Z\)、\(\nabla_WL\)、\(\nabla_bL\)、\(\nabla_vL\) 与 \(\partial L/\partial c\) 的形状和系数正确；D-D01 与参考解答一致。
- 中心有限差分定义、光滑条件、\(O(h^2)\) 截断误差、过小步长的消减误差及稳定化误差分母均正确；明确限定有限差分只作实现检查。
- 对 \(H\succ0\) 的严格凸二次目标，固定步长从任意初值严格收敛的条件 \(0<\eta<2/\lambda_{\max}(H)\) 正确，且没有外推为一般非凸网络的全局保证。

### 3.3 例题、练习与参考解答

- 六个例题均可独立复算，组交集、线性梯度、步长谱半径、有限差分、训练统计量泄漏及两种聚合层级的结论正确。
- 题目与答案为 10/10 一一对应，目录成对且非空。
- Q11-01—Q11-08、Q11-10 的解答完整且与正文一致。Q11-09 的算术正确，但其概率假设不完整，已归入 B01。

### 3.4 来源、自学性与授权边界

- `sources.md:3-9` 将 D-FND-01、D-FND-02 和 D-GNN-01 分别定位到作品、章节或节，并明确结构组泄漏是项目教学推导、训练下降不等于最终正确性、图结构细节留待第 12—14 章。
- 三项来源快照实测 SHA-256 与 `01_sources/documentation/stageD/README.md:7-9` 及中央来源台账完全一致。
- 正文、推导、六例、十题和逐题答案形成连续自学链；B01 修复后，D-D02 才达到可独立验证的条件完备性。
- `chapter.md:355-367` 和 A11-10 正确保留 M8/M9 停点：M7 与 M7-I 通过后进入 M8 决策冻结；M8 冻结后，M9 外部动作仍需用户明确授权。未发现安装 DeepH、下载正式训练数据、生成 DFT 标签或隐含选择材料/后端/版本的内容。

## 4. 独立复算记录

使用 Python 3.12.13、NumPy 2.3.5、float64，在不写入文件的条件下独立复算：

| 对象 | 独立结果 | 审计判断 |
|---|---:|---|
| 例 11-2：\(L,\partial_wL,\partial_bL\) | \(2.5,-5,-3\) | 与材料一致 |
| Q11-05：\(\eta=0.05\) 谱半径 | \(0.95\) | 一致 |
| Q11-05：\(\eta=0.19\) 谱半径 | \(0.9\) | 一致 |
| Q11-05：\(\eta=0.2\) 谱半径 | \(1\) | 不严格收敛，一致 |
| Q11-05：\(\eta=0.25\) 谱半径 | \(1.5\) | 发散，一致 |
| Q11-08：逐元素/逐结构 MSE | \(0.4/0.625\) | 一致 |
| Q11-09：在补足独立/零偏条件后 | \(1.5/5/3.5\) | 算术一致，条件见 B01 |

另以固定随机的 \(M=5,d=3,q=4\) tanh 网络逐参数执行中心有限差分。\(h=10^{-3},10^{-4},10^{-5},10^{-6}\) 时最大稳定化误差依次为

\[
7.640\times10^{-7},\quad
7.644\times10^{-9},\quad
6.852\times10^{-11},\quad
4.016\times10^{-10}.
\]

解析梯度在全部步长上均满足 T-D02 的 \(10^{-5}\) 门槛；\(W,b,v,c\) 梯度形状分别为 \((3,4),(4),(4),()\)，与 D-D01 一致。该复算只验证送审公式，不替代后续 T-D02 对正式教学实现和强制失败注入的代码门控。

## 5. 文档完整性检查

- 9/9 范围文件通过严格 Pandoc stdout 解析；五个数学主体文件共产生 186 个 MathML 节点。
- 4/4 本地 Markdown 链接有效。
- 裸 CR 为 0，非法控制字符为 0。
- 提纲 11.1—11.7 的二级、三级标题顺序与正文一致；正文另附“本章可复核清单”，不构成范围漂移。
- 审计前记录的九份送审文件 SHA-256 已保留于审计运行输出；本报告生成前未改动送审文件。

## 6. 最终门控结论

当前 `BLOCKING=1`、`NON_BLOCKING=1`，结论为 `FAIL`。M6-02 不得标记为 `COMPLETED`，M6-03 不得启动。主 agent 应关闭 B01，并宜同时关闭 N01；随后须由本独立审计员执行定点复核。只有复核确认 B01/N01 均关闭、没有引入新问题，并给出 `BLOCKING=0`、`NON_BLOCKING=0` 和明确放行结论后，才允许完成 M6-02并启动 M6-03。
