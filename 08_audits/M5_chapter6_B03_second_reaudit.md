# M5-03 第 6 章 B03 第二次独立定点复核

- 复核日期：2026-08-04
- 首次正式审计：`08_audits/M5_chapter6_independent_content_audit.md`
- 第一次定点复核：`08_audits/M5_chapter6_blocking_reaudit.md`
- 本轮对象：M5-C6-B03 第二轮最小修复及其可能引入的真实回归
- 复核原则：不重开第一次定点复核已关闭的 B01、B02、B04、B05、N01、N02，除非第二轮修订引入可证实回归
- 总体结论：`PASS`
- M5-C6-B03：`CLOSED`
- 剩余 `BLOCKING`：0 项
- 新增 `BLOCKING`：0 项
- 新增 `NON_BLOCKING`：0 项
- 是否允许 M5-03 标记为 `COMPLETED`：**是**
- 是否允许启动 M5-04：**是**

第二轮修订已经在正文、D-C03.5 和 Q6-04 中明确给出同一标准条件下的 Lieb—系综—纯态闭凸关系，并在正文与 D-C04.1 中分别定义非相互作用纯态和系综搜索状态类。noninteracting \(N\)-representability 与局域势 \(v\)-representability 的边界保持正确；七文件严格 Pandoc、MathML、控制字符、三个 Python 围栏和一个 JSON 围栏均无回归。因此，第一次定点复核所保留的唯一阻塞项已经关闭。

## 1. 修订快照与 SHA-256 冻结

本次复核除新增本报告外，没有修改任何被审材料。下列哈希冻结最终门控依据。

| 文件 | 复核时 SHA-256 |
|---|---|
| `03_textbook/chapters/06_kohn_sham_dft/sources.md` | `7ACFDAC4106C0930B54D469DBAD35BA9A8F6B00C05D1F8E4D124F9DF52CC4BFD` |
| `03_textbook/chapters/06_kohn_sham_dft/outline.md` | `D6DF864F953A7D9E6F94CBB6F7283715F23485ECF80C23F1AB99275FA6347489` |
| `03_textbook/chapters/06_kohn_sham_dft/chapter.md` | `C8615170818E798A2EE2F5B663E984A63683841983C5F6345683A92173F2F859` |
| `03_textbook/chapters/06_kohn_sham_dft/examples.md` | `D087D0D7F4A845C582786577C0F437CBBE32ACC4C55CA21A02EE2499F0D82B49` |
| `04_derivations/stageC/06_kohn_sham_variation.md` | `9986FCE7FACDEABE55CBF6DCC8E5C1DD6C86E0BB7AB7ECFDD0BA7A5D16975335` |
| `06_exercises/03-stageC/06_kohn_sham_dft/problem/readme.md` | `C32BBF291CCEAB5CE09117A9D75C3BD8701FF05DCD7302919EA0805F242A5E8B` |
| `06_exercises/03-stageC/06_kohn_sham_dft/solution/readme.md` | `BEB13CD4A85837203A3806789B11368E5DA1619E498DD73900AFA3CE5115B63E` |
| `08_audits/M5_stageC_work_package.md` | `F8A7CD395F851055D500CC3A8239CE0AFA36F542F122532A0F184169FAA08893` |
| `00_scope/master_execution_plan.md` | `67BC9A6C77F4338629EACA0A64FF7BFB7B43CD31633BC91155D6E74ADE9C6E3C` |
| `08_audits/progress_tracker.md` | `01CCF58EC0ABFF1E2C6E933DD7014FEC72B9CB988117FD33661BA0509FFFECA9` |
| `decisions.md` | `272AED3AD8B771EA0D80FD1C06BECEDB9694A29A994323F820C61E9B2C0CE318` |
| `02_source_ledger/source_table.csv` | `29C3BD17FF9731DD0D3D2D563A93531E42F867BAD6793F6622D275AF9CAFCA4E` |
| `01_sources/bibliography.bib` | `289EA496144D01B5582A4A480292EC0BD65F87D51F5920AD4B9AD2B69F2F962E` |
| `08_audits/M5_chapter6_independent_content_audit.md` | `A61B46BEEAF7C141DD0B65E51B0E1302D2586CF96A6CAA45C135D358C9E0EC3D` |
| `08_audits/M5_chapter6_blocking_reaudit.md` | `BC9E87D2C09D51D80DD148AC965EDEB42147C3477A008BBDEA9EEB2D67E7D9E3` |

相对于第一次定点复核快照，知识材料的实质修订限于 `sources.md`、`chapter.md`、D-C03/D-C04 推导和 Q6 解答；工作包与进度台账只记录“第二轮修复完成、等待独立复核”，仍保持 M5-03 `IN_PROGRESS`、M5-04 `PLANNED`，没有提前越过门控。

## 2. Lieb、系综与纯态闭凸关系

### 2.1 正文第 6.2.4：`PASS`

正文先定义标准系综 constrained-search 泛函

\[
F_{\mathrm{ens}}[n]
:=\min_{\Gamma\mapsto n}
\operatorname{Tr}\Gamma(\hat T+\hat W),
\]

并明确 \(\Gamma\) 是归一化、有限内部能量的反对称 \(N\) 电子统计密度算符。正文同时保留以下共同条件：标准三维 Coulomb 设置、固定 \(N\)、密度 Banach 空间

\[
X=L^1(\mathbb R^3)\cap L^3(\mathbb R^3),
\qquad
\|n\|_X=\|n\|_1+\|n\|_3,
\]

势空间 \(X^*=L^\infty+L^{3/2}\)、固定粒子数下的势常数商空间，以及把不可接受密度上的泛函值共同扩展为 \(+\infty\)。在这些条件下，正文明确写出

\[
F_{\mathrm L}
:=F_{\mathrm{ens}}
:=\operatorname{cl}_{\|\cdot\|_X}
\operatorname{conv}F_{\mathrm{LL}}^{\mathrm{pure}}.
\]

正文定义 \(\operatorname{conv}\) 为凸包，定义 \(\operatorname{cl}_{\|\cdot\|_X}\) 为 \(X\) 范数拓扑中的下半连续闭包，并声明等同关系只在所述标准条件和共同扩展约定下使用。符号 `:=` 在此明确表达定义性等同，不造成第一次复核所指出的“仅称相应”的不确定性。

正文还正确说明：pure/ensemble \(N\)-representable 的密度域在适当条件下可以相同，但 \(F_{\mathrm{LL}}^{\mathrm{pure}}\) 不能与其凸、下半连续闭包逐点无条件混同；该说明没有再暗示 \(F_{\mathrm L}\) 与已经定义的标准 \(F_{\mathrm{ens}}\) 可能不同。

### 2.2 D-C03.5：`PASS`

D-C03.5 使用与正文相同的 \(X\)、\(X^*\)、范数拓扑、固定 \(N\) 势规范和 \(+\infty\) 扩展约定，并逐字给出相同的三重关系。它再次定义统计密度算符的归一化、反对称 \(N\) 电子和有限内部能量条件，解释凸包与范数下半连续闭包，并把外推禁令限定到未声明的函数空间或相互作用。推导包与正文不存在对象、拓扑或量词差异。

### 2.3 Q6-04：`PASS`

Q6-04 解答先分别给出纯态 Levy–Lieb minimum、Lieb 对偶泛函、\(X\)、\(X^*\)、范数拓扑、不可接受密度处的 \(+\infty\) 扩展和固定 \(N\) 势商空间，再给出相同的

\[
F_{\mathrm L}
:=F_{\mathrm{ens}}
:=\operatorname{cl}_{\|\cdot\|_X}
\operatorname{conv}F_{\mathrm{LL}}^{\mathrm{pure}}.
\]

解答明确系综搜索对象以及 `conv`、`cl` 的含义，并继续区分固定密度内层 minimum 与外层 infimum。因而学习者不需要依赖正文中的隐含约定才能判断等式的域、拓扑或状态类。

### 2.4 来源边界：`PASS`

章级 C-FND-06 现明确登记标准 Coulomb 密度域、内层 minimum、三重闭凸关系、变分与 Legendre–Fenchel 对偶，并要求使用时声明 \(X\) 拓扑、对偶势空间、共同扩展约定和纯态/系综边界。该补充没有冻结具体 DFT 后端或近似泛函，也没有把闭凸关系外推到未声明设置。

## 3. 非相互作用动能搜索状态类

### 3.1 正文第 6.3.1：`PASS`

正文分别定义

\[
T_s^{\mathrm{pure}}[n]
:=\inf_{\Phi\mapsto n}
\langle\Phi|\hat T|\Phi\rangle,
\]

其中 \(\Phi\) 限于归一化、有限动能的 Slater determinant；以及

\[
T_s^{\mathrm{ens}}[n]
:=\inf_{\Gamma_s\mapsto n}
\operatorname{Tr}(\Gamma_s\hat T),
\]

其中

\[
\Gamma_s=\sum_a w_a|\Phi_a\rangle\langle\Phi_a|,
\qquad
w_a\ge 0,
\qquad
\sum_a w_a=1,
\]

且每个 \(\Phi_a\) 都属于上述 Slater determinant 类。正文明确规定本章无上标的 \(T_s\) 统一表示 \(T_s^{\mathrm{ens}}\)，仅在限制到单 determinant 时写 \(T_s^{\mathrm{pure}}\)。因此搜索对象、纯态/系综差别和后文符号约定均已闭合。

### 3.2 D-C04.1：`PASS`

D-C04.1 给出与正文相同的两项定义、权重条件和无上标约定。没有继续使用第一次定点复核所批评的“不预先限定具体状态类的统一定义”。推导包后续能量分解中出现的无上标 \(T_s\) 因而有唯一、可回溯的含义。

### 3.3 可表示性边界：`PASS`

两处材料均明确区分：

- constrained search 的定义需要相应非相互作用纯态或系综状态类中的 noninteracting \(N\)-representability；
- 密度是某个局域一体势的基态密度属于更强的 noninteracting \(v\)-representability，并关系到普通局域 KS Euler 方程是否能以乘法势实现；
- 局域势不存在时，constrained-search 泛函本身不因此失效，仍可讨论系综、次梯度或 generalized KS。

该边界与第一次定点复核要求一致，没有把定义 \(T_s\) 与局域势存在性重新混同。

## 4. 制品与代码回归验证

七份章级 Markdown 分别执行：

```text
pandoc --from=markdown+tex_math_dollars+tex_math_single_backslash \
       --to=html5 --mathml --fail-if-warnings -- <file>
```

结果如下。

| 文件 | Pandoc 退出码 | MathML 节点 | TAB | 其他 C0 | U+FFFD |
|---|---:|---:|---:|---:|---:|
| `sources.md` | 0 | 7 | 0 | 0 | 0 |
| `outline.md` | 0 | 6 | 0 | 0 | 0 |
| `chapter.md` | 0 | 134 | 0 | 0 | 0 |
| `examples.md` | 0 | 47 | 0 | 0 | 0 |
| `06_kohn_sham_variation.md` | 0 | 149 | 0 | 0 | 0 |
| `problem/readme.md` | 0 | 19 | 0 | 0 | 0 |
| `solution/readme.md` | 0 | 89 | 0 | 0 | 0 |

七文件严格 Pandoc 为 7/7 通过；新增闭凸关系、纯态 \(T_s\)、系综 \(T_s\) 和 \(\Gamma_s\) 权重式均实际生成 MathML。七文件 TAB、除 TAB/LF/CR 外的 C0 控制字符和 U+FFFD 替换字符均为 0。

`examples.md` 中两个 Python 围栏和题解中的一个 Python 围栏按原文逐块交给固定 Python 解释器执行，三者退出码均为 0。题解含且仅含一个 JSON 围栏，严格 JSON 解析成功。第二轮修订没有改变问题 ID、例题数值、代码或标签 JSON，因此第一次定点复核已关闭的制品与可复算项没有回归。

## 5. 新增 finding

没有发现第二轮修订引入新的数学、物理、来源、制品或授权问题：

- 新增 `BLOCKING=0`；
- 新增 `NON_BLOCKING=0`。

工作包与进度台账在本报告生成前仍保持 M5-03 `IN_PROGRESS`、M5-04 `PLANNED`，只记录等待独立复核，没有把主 agent 的预检当作通过结论。

## 6. 最终门控判定

本次第二次独立定点复核冻结：

- M5-C6-B03：`CLOSED`；
- 第一次定点复核已关闭的 B01、B02、B04、B05、N01、N02：未发现回归；
- 剩余 `BLOCKING=0`；
- 新增 `BLOCKING=0`；
- 新增 `NON_BLOCKING=0`；
- **允许将 M5-03 标记为 `COMPLETED`；**
- **允许启动 M5-04。**

该许可仅适用于本报告冻结的文件快照。若正文、推导、题解或来源边界在状态更新前发生实质变化，应重新核对相应哈希和受影响结论。
