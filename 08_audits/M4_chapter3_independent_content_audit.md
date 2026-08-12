# M4-03 第 3 章独立内容审计

- 审计日期：2026-08-04
- 审计对象：M4-03“非正交基与广义本征值问题”正文、推导、例题、练习与参考解答，以及阶段 B 统一约定和 M4 工作包
- 审计性质：独立材料完备性、可自学性和可验证性审计
- 总体结论：`BLOCKING`
- 是否允许将 M4-03 标记为完成：**否**
- 是否允许进入 M4-04：**否**。应由主 agent 完成下述最小修复，再由独立审计复核 `BLOCKING` 是否清零。

## 1. 审计范围与快照

本次逐项核查以下文件，未修改任何被审计材料：

| 文件 | 审计时 SHA-256 |
|---|---|
| `03_textbook/chapters/03_nonorthogonal_generalized_eigen/sources.md` | `210B7CC54E85C2645FAEFAD28266F979774A73554CA3F261E2200B5E1A12EA49` |
| `03_textbook/chapters/03_nonorthogonal_generalized_eigen/outline.md` | `F55F00EEA3D3ED8ED7F798B2D12FA9C13215A6F52878D9B6BEAD006EA1D92BEB` |
| `03_textbook/chapters/03_nonorthogonal_generalized_eigen/chapter.md` | `86535574779FA4D8ACB1817A74C80A1C42B85CC9F26923BF1BBCB48E3035984A` |
| `03_textbook/chapters/03_nonorthogonal_generalized_eigen/examples.md` | `AD26EBAF5AF1C5D6D64F95606CF5C1A1D1A6E71857073F44BC3D114FD5F04534` |
| `04_derivations/stageB/03_generalized_eigen.md` | `C0F40B073838CD214078C327B4498B2C2891AAED5F4CAAE7BB5DE6CF74B98AB8` |
| `06_exercises/02-stageB/03_generalized_eigen/problem/readme.md` | `0DF6B90DF8F5A6E1695502C0FC6B5BA2E53C083F506D87E9CC2B055236534CB7` |
| `06_exercises/02-stageB/03_generalized_eigen/solution/readme.md` | `6AB74B1771050473446528BD4FE28B7FAAB869C59B24761BA49B3CBE65FB7767` |
| `03_textbook/stageB_conventions.md` | `66A135C38DBA8536D88701ED85DEBAE51D60A3E48CD0D09DFBBB463A2240B464` |
| `08_audits/M4_stageB_work_package.md` | `B33789AFF5DF0701AA7E9CCA2DDCBDD66CF514975CC0CAAAEB81623276F5667A` |

## 2. 已满足内容

在主问题条件 \(H=H^\dagger\)、\(S=S^\dagger\succ0\) 下，Gram 矩阵正定性、投影方程、Rayleigh 商驻值、实谱、\(S\)-正交性、Cholesky 约化、对称正交化和一般可逆基变换的主代数链基本正确。矩阵与向量形状、复共轭、简并子空间比较、显式求逆的限制以及奇异、非正定、非 Hermitian 和维数不匹配等失败边界均有覆盖。统一基变换规则与 `stageB_conventions.md` 一致，没有发现相位约定或 DeepH 软件接口越界。

两轨道例题的闭式谱、(S\)-归一化本征矢、Cholesky 约化、对称正交化和同步合同变换均经固定环境复算通过。十道练习与十份参考解答一一对应，能够覆盖定义、两种推导、两种约化、基变换、闭式复算和失败分类。

上述结果不足以解除阻塞，因为病态性部分尚未达到提纲明确规定的“残差、后向误差与谱敏感性”推导强度，来源分类契约也未在材料中落实。

## 3. BLOCKING

### B01：后向误差与前向误差只作定性陈述，缺少可复核构造、界和适用条件

**位置：**

- `outline.md:33-35` 明确要求“残差、后向误差与谱敏感性”；
- `chapter.md:243-250` 定义归一化残差后，直接声称小残差意味着满足附近矩阵束，并称病态或近简并时不保证小前向误差；
- `solution/readme.md:192-194` 将同一结论作为 Q3-10 的答案，但仍未给出附近 Hermitian 矩阵束的构造、扰动范数界、谱隙条件或 (S\) 条件数进入误差界的方式；
- `04_derivations/stageB/03_generalized_eigen.md:276-306` 仅给出 (S\) 的范数等价和定性放大解释，未推导残差对应的后向扰动及前向界。

**为何阻塞：**

“小残差是后向稳定性证据”并非无需条件的口号。当前材料没有说明近似本征值是否取实数、近似向量采用何种归一化、扰动是否保持 Hermitian-definite 结构，也没有展示一个可代回验证的 \(\Delta H\) 或 \((\Delta H,\Delta S)\)。同样，前向本征值/本征矢误差必须依赖标准化残差、谱隙以及 (S\) 的最小特征值或条件数；当前文本只说“可能放大”，学习者无法据此计算、验证或判断结论何时失效。因此，现有材料没有满足工作包关于公式条件和可验证性的强度，也没有完成三级提纲 3.5.2。

**最小修复要求：**

1. 在正文和逐步推导中固定近似对的条件，例如 \(\widehat E\in\mathbb R\)、\(\widehat c^\dagger S\widehat c=1\)，定义未归一化残差 \(q=H\widehat c-\widehat E S\widehat c\)。
2. 给出保持 Hermiticity 的显式后向扰动构造并逐式验证。例如在 \(\widehat E=\mathcal R(\widehat c)\) 时利用 \(\widehat c^\dagger q=0\)，构造 Hermitian \(\Delta H\)，验证 \((H+\Delta H)\widehat c=\widehat E S\widehat c\)，并给出 \(\|\Delta H\|_2\) 关于 \(\|q\|_2/\|\widehat c\|_2\) 的可核对上界。若选择一般 \(\widehat E\)，则必须保留使构造 Hermitian 且精确消去残差的校正项。
3. 通过标准 Hermitian 约化 \(A=S^{-1/2}HS^{-1/2}\)、\(y=S^{1/2}\widehat c\) 定义标准残差 \(\rho=S^{-1/2}q\)，至少推导一个本征值包含界以及带正谱隙的本征矢或不变子空间角度界。必须明示 \(\|\rho\|_2\le \|q\|_2/\sqrt{\lambda_{\min}(S)}\)，并说明从正交坐标映回系数坐标时 (S\) 的条件数如何影响向量误差；谱隙为零或很小时不得套用逐向量界。
4. 增加一个一一对应的练习/解答或确定性数值断言，复核后向扰动确实消去残差，并复核所给界在固定样例上成立。只增加定性文字不足以解除本项阻塞。

### B02：`DIRECT_DERIVATION` 来源分类契约未落实到正文和推导

**位置：**

- `sources.md:10` 要求 Gram 正定性、投影方程、Rayleigh 商、基变换谱不变性和条件数影响“均应由定义逐步推导并标记为 `DIRECT_DERIVATION`”；
- `08_audits/M4_stageB_work_package.md:34-38` 再次规定标准定义后的代数步骤使用该标记；
- `chapter.md` 和 `04_derivations/stageB/03_generalized_eigen.md` 中没有任何 `DIRECT_DERIVATION` 标记。全文检索仅在资料包和工作包契约处命中，未在实际教学内容处命中。

**为何阻塞：**

当前材料虽然在 `chapter.md:20` 标记了教学模型为 `PEDAGOGICAL`，但没有按已冻结来源边界区分“来源支持的定义/结论”与“由定义直接推出的本教材推导”。读者无法仅凭正文定位哪些结论属于直接推导，也无法确认五项指定推导是否全部履行来源契约。该问题直接违反 M4-01 已冻结的审计输入，不属于可延后到 M4-07 的代码任务。

**最小修复要求：**

在正文和逐步推导中对上述五类内容逐项显式标注 `DIRECT_DERIVATION`，并在来源说明中建立来源 ID—定义/定理—直接推导小节的可定位映射。标记应落在具体小节或公式链附近，不能只在章首作一次笼统声明；病态性部分只能对实际已推导并声明条件的界使用该标记，不能把未经证明的经验性判断标记为直接推导。

## 4. NON_BLOCKING 与后续强制项

### N01：当前 M4-03 复现脚本没有非法 (S\) 的可执行拒绝断言

`examples.md:108-129` 给出了奇异 \(S_{\mathrm{sing}}\) 和不定 \(S_{\mathrm{indef}}\) 的数值矩阵，并正确说明二者应被 Hermitian-definite 路径拒绝；但 `examples.md:138-160` 的实际脚本没有构造这两个输入，没有调用拒绝路径，也没有对异常类型和消息作断言。因此，**当前被审计材料中不存在非法 \(S\) 的可执行拒绝断言**。

本次将其列为 `NON_BLOCKING`，原因是 `chapter.md:270` 和推导文件末尾已明确把自动失败断言安排到 M4-07，工作包 T-B01 也已冻结“非正定 (S\) 抛出 `ValueError` 且消息含 `positive definite`”的验收标准。该延期不影响 M4-03 的正文、推导与解答任务边界，但在 M4-07 完成或 M4 阶段门控前必须实现并实际运行；仅让 SciPy/Cholesky 偶然抛出底层异常、仅打印异常或只检查特征值而不断言拒绝行为，均不满足 T-B01。为提高本章当前的独立可验证性，可在例题复现脚本中提前加入奇异与不定输入的显式拒绝断言。

## 5. 自动核验结果

### 5.1 固定 Python 复算

使用工作包固定解释器：

```text
Python 3.12.13
NumPy 2.3.5
SciPy 1.18.0
```

逐句复算 `examples.md:138-160` 的确定性程序，所有现有断言通过，得到：

```text
eigenvalues = [0.8452994616207486, 3.1547005383792515]
generalized residual 2-norm = 2.220446049250313e-16
S-orthogonality Frobenius norm = 4.997674892762528e-16
cond_2(S) = 2.999999999999999
```

Cholesky 与对称正交化谱差、同步合同变换谱差均低于 (10^{-12})；只变换 (H\) 的失败断言按预期被检出。该脚本没有非法 (S\) 的拒绝断言，见 N01。

### 5.2 Pandoc、链接、控制字符和数学定界符

对九个审计对象逐文件执行：

```powershell
pandoc --from=gfm+tex_math_dollars --to=html5 --mathml --fail-if-warnings ...
```

结果为 9/9 通过，无 Pandoc warning。UTF-8 扫描结果为控制字符 0 个；本地 Markdown 链接共检查 7 个，缺失 0 个；行内 `\(...\)` 与展示 `\[...\]` 定界符计数均平衡。未发现会阻止当前 Markdown/MathML 渲染的格式错误。

## 6. 最终判定

M4-03 的主代数内容和确定性例题已具备较好基础，但 B01 使“残差—后向误差—前向误差”链条停留在不可复核的定性层面，B02 则违反已冻结的来源分类契约。两项均直接影响材料完备性、可自学性和可验证性，故本轮审计结论为 `BLOCKING`。在主 agent 完成最小修复并由独立复核确认两项清零前，不允许将 M4-03 标记为完成，也不允许进入 M4-04。
