# M4-03 阻塞项独立定点复核

- 复核日期：2026-08-04
- 复核范围：M4-C3-B01、M4-C3-B02，以及原审计 N01 的非法 \(S\) 拒绝断言
- 复核性质：独立定点复核；除本报告外未修改任何材料、README、工作包或台账
- 总体结论：`PASS`
- 新增 `BLOCKING`：0
- M4-03：允许标记 `COMPLETED`
- M4-04：允许标记 `READY`

## 1. 输入快照

| 文件 | 复核 SHA-256 | 与委托快照一致 |
|---|---|---|
| `03_textbook/chapters/03_nonorthogonal_generalized_eigen/sources.md` | `0042B83F9772E77590BC5C69F3F73CC79251A2A648DD67A734DA1B1FEE532F20` | 是 |
| `03_textbook/chapters/03_nonorthogonal_generalized_eigen/chapter.md` | `A00F0172280F02D3DD9553248A50492D08715FD31889A58BC11121DF3A2A5AD2` | 是 |
| `03_textbook/chapters/03_nonorthogonal_generalized_eigen/examples.md` | `716ED6531FAE27D18E6F4EA5B182D569C83A5120F56A85F77261D22EC0169E4A` | 是 |
| `04_derivations/stageB/03_generalized_eigen.md` | `6AFF3009B5E0DDFD596D20B70C6110190EB5FCDE31751A6817991DF1564A36CC` | 是 |
| `06_exercises/02-stageB/03_generalized_eigen/problem/readme.md` | `E91C44B303238CAE2E562FDCF469DDFC5AFD2E2205999C701FC153AD9ABF9D7A` | 是 |
| `06_exercises/02-stageB/03_generalized_eigen/solution/readme.md` | `71978C21FA8BE89CB274E8744998241171B52CAAD5A1DCE386D56195BB189027` | 是 |

## 2. M4-C3-B01：关闭

### 2.1 一般实 \(\widehat E\) 的结构保持后向扰动

`chapter.md` 3.5.2 和推导 10.1 现已固定 \(\widehat E\in\mathbb R\)、\(\widehat c\ne0\)，并定义

\[
q=H\widehat c-\widehat E S\widehat c,
\quad
u=\frac{\widehat c}{\|\widehat c\|_2},
\quad
p=-\frac{q}{\|\widehat c\|_2},
\quad
\alpha=u^\dagger p\in\mathbb R.
\]

对

\[
\Delta H=pu^\dagger+up^\dagger-\alpha uu^\dagger
\]

逐式复核如下：Hermitian 的 \(H,S\) 与实 \(\widehat E\) 保证 \(\widehat c^\dagger q\) 及 \(\alpha\) 为实数，故 \(\Delta H=\Delta H^\dagger\)；又因 \(p^\dagger u=\alpha\)，有 \(\Delta H u=p\)，从而 \(\Delta H\widehat c=-q\) 和

\[
(H+\Delta H)\widehat c=\widehat E S\widehat c.
\]

算子 2-范数的三角不等式及 \(|\alpha|\le\|p\|_2\) 给出

\[
\|\Delta H\|_2\le3\|p\|_2
=3\frac{\|q\|_2}{\|\widehat c\|_2}.
\]

一般复 Hermitian 随机矩阵的独立数值复核得到后向消去残差 \(3.8351\times10^{-15}\)，实际界比值为 \(1.15385<3\)。构造、结构和 3 倍界均成立。

### 2.2 Rayleigh 商特例

当 \(\widehat E=\mathcal R(\widehat c)\) 时，材料正确推出 \(\widehat c^\dagger q=0\)、\(\alpha=0\)，从而

\[
\Delta H=pu^\dagger+up^\dagger,
\qquad
\|\Delta H\|_2\le2\frac{\|q\|_2}{\|\widehat c\|_2}.
\]

例 3.5 与 Q3-10 采用该特例。解析值 \(\widehat E=11/13\)、\(\widehat c^\mathsf Tq=0\)、\(\|\Delta H\|_2=1/26\le1/13\) 相互一致，参考解答给出了同一构造和界。

### 2.3 标准约化、本征值包含界和谱隙界

材料现已固定 \(\widehat c^\dagger S\widehat c=1\)，并令

\[
A=S^{-1/2}HS^{-1/2},
\quad y=S^{1/2}\widehat c,
\quad \rho=S^{-1/2}q.
\]

逐式检查确认 \(A=A^\dagger\)、\(\|y\|_2=1\) 以及 \(Ay-\widehat Ey=\rho\)。在 \(A\) 的正交本征基中展开 \(y\) 后，推导正确得到

\[
\min_i|E_i-\widehat E|\le\|\rho\|_2,
\qquad
\|\rho\|_2\le
\frac{\|q\|_2}{\sqrt{\lambda_{\min}(S)}}.
\]

当目标 \(E_j\) 为单本征值且

\[
\operatorname{sep}_j(\widehat E)
=\min_{i\ne j}|E_i-\widehat E|>0
\]

时，材料正确推导

\[
\sin\angle(y,u_j)
\le\frac{\|\rho\|_2}{\operatorname{sep}_j(\widehat E)}.
\]

利用 \(\|S^{-1/2}\|_2=\lambda_{\min}(S)^{-1/2}\)、\(\|c_j\|_2\ge\lambda_{\max}(S)^{-1/2}\) 和相位对齐后的单位向量距离界，映回系数坐标的

\[
\frac{\min_\varphi\|\widehat c-e^{i\varphi}c_j\|_2}{\|c_j\|_2}
\le
\sqrt{2\kappa_2(S)}
\frac{\|\rho\|_2}{\operatorname{sep}_j(\widehat E)}
\]

推导成立。正文和推导均明确说明：谱隙为零或很小时不得使用逐本征矢界，应改为比较与其余谱分离的不变子空间。此前缺失的条件、结构保持构造、后向界、前向界及简并边界均已补齐。

### 2.4 可执行验证

直接从 `examples.md` 提取并执行嵌入 Python 程序，固定环境为：

```text
Python 3.12.13
NumPy 2.3.5
SciPy 1.18.0
```

全部断言通过，关键输出为：

```text
eigenvalues       = [0.8452994616207486, 3.1547005383792515]
cond_S            = 2.999999999999999
backward_cancel   = 0.0
rho_norm          = 0.04441155916843269
sin_angle         = 0.0192343275196243
```

嵌入断言实际检查了 Hermiticity、后向残差精确消去、Rayleigh 特例 2 倍界、\(\rho\) 的 \(\lambda_{\min}(S)\) 界、本征值包含界、正谱隙角度界和 \(\sqrt{2\kappa_2(S)}\) 系数误差界。Q3-10 的题目与参考解答能够定位并复核同一确定性实例。因此 M4-C3-B01 关闭。

## 3. M4-C3-B02：关闭

`sources.md` 新增的“来源—推导定位”不是单纯标签计数，而是逐项建立了以下可定位映射：

- FND-01 → Gram 矩阵与非正交局域基语境 → 正文 3.1.1—3.1.3、推导第 2 节；
- FND-02/FND-03 → Hermitian-definite 广义本征对象 → 正文 3.2、推导第 3—5 节；
- FND-02/FND-04 → Cholesky 与对称正交化对象 → 正文 3.3、推导第 6—7 节；
- FND-03 → 一般可逆基变换的矩阵束对象 → 正文 3.4、推导第 8 节；
- FND-02—FND-04 → 定问题、正交化与误差分析对象 → 正文 3.5、推导第 9—10 节；
- 无真实体系来源主张 → 两轨道、病态和非法输入 → `examples.md`、Q3-09—Q3-10，标为 `PEDAGOGICAL`。

正文的 Gram 正定性、投影、Rayleigh 商、基变换、条件数、后向扰动和前向界均在对应公式链附近标注 `DIRECT_DERIVATION`。逐步推导文件在相同的对应小节重复标注，并在 Cholesky/对称正交化处明确区分“来源锚定的对象与条件”和“教材直接推出的公式链”。`sources.md` 末尾还明确限制来源仅锚定定义、问题类别和正交化对象，不把教材新推导冒充来源原文结论。此前的来源分类契约缺口已实质关闭，故 M4-C3-B02 关闭。

## 4. 非法 \(S\) 拒绝断言：已实际执行

嵌入程序定义 `solve_definite`，在 \(\lambda_{\min}(S)\le0\) 时显式抛出 `ValueError('S must be positive definite')`。程序随后分别传入

\[
\begin{pmatrix}1&1\\1&1\end{pmatrix},
\qquad
\begin{pmatrix}1&1.2\\1.2&1\end{pmatrix},
\]

并对两次异常的类型和消息执行断言；若任一非法输入未被拒绝，则显式抛出 `AssertionError('invalid S was not rejected')`。本次执行完整程序时循环和断言均实际运行并通过。因此，原审计 N01 所述缺口已提前于 M4-07 关闭；这不替代 M4-07 对正式 `solve_generalized` 接口的 T-B01 验收。

## 5. 渲染、链接与文本完整性

对六个复核对象逐文件执行：

```powershell
pandoc --from=markdown+tex_math_single_backslash+tex_math_double_backslash `
  --to=html5 --mathml --fail-if-warnings -o <temp.html> <input.md>
```

结果为 6/6 通过且无 warning。实际生成的 MathML 节点数依次为：`sources.md` 2、`chapter.md` 124、`examples.md` 54、推导 139、练习 40、参考解答 121，均大于 0。UTF-8 控制字符为 0；检查本地 Markdown 链接 6 个，缺失 0；行内和展示数学定界符不平衡为 0。

## 6. 最终判定

M4-C3-B01 与 M4-C3-B02 均已按原审计的最小修复要求关闭，没有发现由修订引入的新 `BLOCKING`。后向误差与前向误差链条现在具有明确条件、可逐式复核构造、定量界、谱隙/简并边界以及确定性代码断言；来源分类也已落实为来源—对象—推导位置的实质映射。因此本次定点复核结论为 `PASS`，允许 M4-03 标记 `COMPLETED`，允许 M4-04 标记 `READY`。
