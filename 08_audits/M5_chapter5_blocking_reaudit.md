# M5-02 第 5 章阻塞项独立定点复核

- 复核日期：2026-08-04
- 前序审计：`08_audits/M5_chapter5_independent_content_audit.md`
- 前序结论：`BLOCKING=3`，非阻塞项 1
- 复核范围：M5-C5-B01—B03 与 N01；同时执行章节静态渲染、控制字符、练习映射和内嵌代码回归
- 复核结论：B01—B03 全部 `CLOSED`，N01 `CLOSED`，新增 `BLOCKING=0`
- 是否允许 M5-02 标记为 `COMPLETED`：**是**
- 是否允许启动 M5-03：**是**

## 1. 独立性与复核快照

本次只核对前序审计冻结项及其必要回归，不重新替主 agent 撰写材料。除新增本报告外，未修改任何被审文件。委托给出的五个修订文件 SHA-256 与独立复算结果全部一致。

| 文件 | 复核时 SHA-256 |
|---|---|
| `03_textbook/chapters/05_many_electron_mean_field/sources.md` | `1E2BA235C96269D0F0820F13C7483C9591D024D0168700CE8F97F8613AF92F07` |
| `03_textbook/chapters/05_many_electron_mean_field/outline.md` | `0032025037BDCD0D1C0DC34A8692F24E588CC425A1BB732338325C5C9A38E54E` |
| `03_textbook/chapters/05_many_electron_mean_field/chapter.md` | `EE17931F2A4D4FF0BA036F9AB714C4CC8B3486C5775162610A2E25839A77058C` |
| `03_textbook/chapters/05_many_electron_mean_field/examples.md` | `9740F46029CD31C08FE0215B9A6EF7809F0CF2C90B77EE3123F47B9BD4217BA6` |
| `04_derivations/stageC/05_many_electron_mean_field.md` | `01385729D1D0DF6B50B3E4EF0E9624959845D2FD55E2A49D0D28E1009B7F64D2` |
| `06_exercises/03-stageC/05_many_electron_mean_field/problem/readme.md` | `F93EAB1AC00C1BA02858B094696686FA71B6C40748759955298088F8C9F3CCF9` |
| `06_exercises/03-stageC/05_many_electron_mean_field/solution/readme.md` | `4106A40CBA1A278089FF86F2379E2CE5FEB4BFCE57B879595BC31D567A4F5DB1` |
| `02_source_ledger/source_table.csv` | `3BB19A521C6EB0E4CBACEF6F7A48A613EE095BDC13A9ADB45845A75B0394F0A2` |
| `01_sources/bibliography.bib` | `935DAA9042635B7ACF7F82DE600B237E28A6F8F699F8A0494E14EAD458973895` |
| `08_audits/M5_stageC_work_package.md` | `AB9C0936890B77684C19E4D56CF819EB855B3656D4FBA3B190EBE2B2BC9B1AE0` |
| `decisions.md` | `072992EFCA9474B738CB48E7C18F85342FDDC4ABA7D25F62EB572552E429455C` |
| `08_audits/M5_chapter5_independent_content_audit.md` | `ACD58C7F43696EB6047DD155576E9105691AEEB7A4125ECA2ACEFAF0EB1BD7EF` |

## 2. 阻塞项逐项复核

### M5-C5-B01：`CLOSED`

前序问题是只声明忽略非对角面间耦合，却在最简方程中同时静默删除对角导数项。修订后的 `04_derivations/stageC/05_many_electron_mean_field.md:98-170` 已把三个操作明确分开：忽略 `b != a` 非对角耦合；选择局部平行输运规范；另行忽略 Born–Huang 标量修正。

独立逐式复核如下：

1. 由归一化条件得到 `d_aa^I` 为纯虚量，并正确写出

   \[
   \tau_{aa}^{I}=\nabla_I\cdot\mathbf d_{aa}^{I}
   -\langle\nabla_I\Phi_a|\nabla_I\Phi_a\rangle.
   \]

2. 采用 `A_a^I=i d_aa^I` 时，配方后的协变动能为

   \[
   \frac{(-i\nabla_I-\mathbf A_a^I)^2}{2M_I}.
   \]

   展开该式并加上

   \[
   \Phi_a^{\mathrm{BH}}=
   \sum_I\frac{\langle\nabla_I\Phi_a|\nabla_I\Phi_a\rangle
   -|\mathbf d_{aa}^{I}|^2}{2M_I}
   \]

   后，恰好恢复原对角投影中的 `-d_aa^I dot grad/M_I-tau_aa^I/(2M_I)`；符号一致。

3. 在 `|Phi_a> -> exp(i theta)|Phi_a>`、`chi_a -> exp(-i theta)chi_a` 下，材料正确得到

   \[
   \mathbf A_a^I\mapsto\mathbf A_a^I-\nabla_I\vartheta,
   \]

   且 `(-i grad-A)chi` 以 `exp(-i theta)` 协变。独立数值代数断言也验证了该号约定。

4. Born–Huang 项被正确写成投影到电子态正交补后的导数范数；在电子基完备时等于 `sum_(b != a)|d_ba^I|^2/(2M_I)`，不会因令 `d_aa^I=0` 自动消失。

5. `chapter.md:82-110` 已给出同一层级的可自学概括；`solution/readme.md:51-67` 的 Q5-02 明确定位对角 Berry 连接、Born–Huang 修正和 D-C01.3。材料同时说明局部规范不保证全局 Berry 相位或非平凡曲率消失，简并子空间须使用矩阵值连接。

最简裸核动能方程现在只在局部无简并、可选平行输运规范，并另行忽略 Born–Huang 修正后出现。前提与删项完全闭合，B01 关闭。

### M5-C5-B02：`CLOSED`

`chapter.md:374-385` 已补齐三级提纲冻结的 5.5.4。该小节逐项写明 M8 前禁止：

- 安装 DeepH 本体；
- 下载正式训练数据；
- 生成正式 DFT 标签；
- 显式或隐含选择首个材料体系、DFT/数据后端或实践软件版本。

同一小节明确规定：M3—M7 材料建设和独立门控完成、准备进入 M8 时暂停并集中提交计算资源、后端、软件对象、材料体系、时间/训练预算和高级物理范围方案；M8 冻结后，在 M9 正式安装、数据下载或复现实验前再次请求明确执行授权。Q5-10 解答也定位到该小节。正文与 `decisions.md:84-93` 及阶段 C 工作包一致，未把教学模型解释为实践选择。B02 关闭。

### M5-C5-B03：`CLOSED`

KS 接口边界已在三个层级同步修订：

- `sources.md:10` 对 C-FND-03 明确登记非相互作用可表示性、整数占据 determinant 与简并/分数占据系综边界；
- `chapter.md:337-345` 只在具有所需非相互作用 `v`-representability、常规零温整数占据且不需要系综处理的条件下使用单 KS determinant；存在简并、分数占据或更一般可表示性问题时，改用非相互作用系综和占据数表述；
- `solution/readme.md:125-131` 的 Q5-07 比较表和解释采用相同条件，并说明单 determinant 或系综均为辅助对象，不是真实相互作用多体波函数。

修订后不再声称任意相互作用密度都由一个纯 KS determinant 无条件表示，也没有把 representability 条件误写成实践泛函已知。B03 关闭。

## 3. 非阻塞项复核

### N01：`CLOSED`

`02_source_ledger/source_table.csv:19` 的 FND-01 已同步覆盖第 3、5 章的电子—核、多电子、BO、独立电子与 HF 用途，并保留第 4、6—9、11—15 章的阶段 C 其他范围。页码与章级来源包及阶段 C 工作包一致，限制字段继续明确：本地出版社目录快照只核版本、章节和页码，不替代公式级证据，也不支持 DeepH 软件声明。

独立 CSV 结构检查得到：表头和全部 34 条记录均为 17 字段；34 个 source ID 全部唯一；不存在坏宽度行或重复 ID。中央范围不一致已消除，N01 关闭。

## 4. 回归检查

### 4.1 Markdown、MathML 与控制字符

对七份章节 Markdown 逐一运行：

```text
pandoc --from=markdown+tex_math_dollars+tex_math_single_backslash \
       --to=html5 --mathml --fail-if-warnings <file>
```

结果为 `7/7` 退出码 0。七份文件的非法 C0/DEL 控制字符数均为 0。新增 Berry/Born–Huang 公式没有引入 MathML 解析警告。

### 4.2 练习映射与数值代码

Q5-01—Q5-10 与十个同名参考解答标题仍严格一一对应。使用固定解释器 Python 3.12.13、NumPy 2.3.5 原样执行例 5-3 内嵌代码，两组 `(t,U)` 的密度、谱和双计数断言全部通过。另以独立随机复向量检查 `A=i d` 的规范变换号，并检查 Born–Huang 被积量的正性，断言通过。未安装或运行 DeepH/DFT 后端，未访问正式数据。

## 5. 正式结论

M5-C5-B01—B03 已全部按前序审计要求关闭，N01 已同步关闭；静态渲染、控制字符、CSV 结构、练习映射和内嵌代码回归均通过。本次定点复核未发现新增 `BLOCKING`。

正式结论为 `BLOCKING=0`。**允许将 M5-02 标记为 `COMPLETED`，允许启动 M5-03。** 本结论只授权依赖顺序中的材料建设，不改变 M8 前四项禁令，也不构成 M9 外部动作授权。
