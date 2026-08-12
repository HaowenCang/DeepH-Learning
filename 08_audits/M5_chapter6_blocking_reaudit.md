# M5-03 第 6 章阻塞项定点复核

- 复核日期：2026-08-04
- 原正式审计：`08_audits/M5_chapter6_independent_content_audit.md`
- 原正式审计 SHA-256：`A61B46BEEAF7C141DD0B65E51B0E1302D2586CF96A6CAA45C135D358C9E0EC3D`
- 复核范围：原审计 M5-C6-B01—B05、M5-C6-N01—N02，以及修订引入的新增问题
- 复核性质：独立定点复核；不采用主 agent 的预检结论替代逐项证据
- 总体结论：`BLOCKING`
- 原阻塞项关闭：4 项
- 原阻塞项未关闭：1 项
- 原非阻塞项关闭：2 项
- 新增阻塞项：0 项
- 是否允许 M5-03 标记为 `COMPLETED`：**否**
- 是否允许启动 M5-04：**否**

修订已经关闭 HK 共同基态与简并边界、Levy–Lieb 内外层搜索、单电子势规范及 Markdown/MathML 制品问题，原两项非阻塞问题也已处理。M5-C6-B03 仍未关闭：材料虽然补齐了 Lieb 密度空间、势空间、范数拓扑、扩展值和势常数商空间，但始终只称 \(F_{\mathrm L}\) 与系综 constrained-search 泛函“相应”，没有写出标准条件下的精确等同关系；同时，\(T_s\) 的搜索式刻意“不预先限定具体非相互作用状态类”，因而没有定义纯态与系综搜索究竟由哪些 Slater determinant 对象组成。这不是措辞偏好，而是两个泛函定义仍未闭合。

## 1. 修订快照与 SHA-256 冻结

本次定点复核除新增本报告外，没有修改被审材料。下表冻结正式判定所依据的字节快照。

| 文件 | 复核时 SHA-256 |
|---|---|
| `03_textbook/chapters/06_kohn_sham_dft/sources.md` | `5692C1ED215EE908100D78C00D5EA4191ACEDF21B75EC113C7B9290769EE39C3` |
| `03_textbook/chapters/06_kohn_sham_dft/outline.md` | `D6DF864F953A7D9E6F94CBB6F7283715F23485ECF80C23F1AB99275FA6347489` |
| `03_textbook/chapters/06_kohn_sham_dft/chapter.md` | `D6C30E26BD3CD4665571A1CADEFE74BA7DE8E1C09786FCE0BF4B6A25150D60E7` |
| `03_textbook/chapters/06_kohn_sham_dft/examples.md` | `D087D0D7F4A845C582786577C0F437CBBE32ACC4C55CA21A02EE2499F0D82B49` |
| `04_derivations/stageC/06_kohn_sham_variation.md` | `5F18E987CF42BA6590F37B8E8D79808001D330CB04EFC9FDAD86123BA70941E6` |
| `06_exercises/03-stageC/06_kohn_sham_dft/problem/readme.md` | `C32BBF291CCEAB5CE09117A9D75C3BD8701FF05DCD7302919EA0805F242A5E8B` |
| `06_exercises/03-stageC/06_kohn_sham_dft/solution/readme.md` | `F31BE64EBCD4E622340BB30EF4CEA0EA91AFB591D612D21941379CBE30BC6D35` |
| `08_audits/M5_stageC_work_package.md` | `E09E0EAEDA2DA9F6ABD92268C6111A5F6FF2C741E8A55D6767E662674FC1F956` |
| `00_scope/master_execution_plan.md` | `67BC9A6C77F4338629EACA0A64FF7BFB7B43CD31633BC91155D6E74ADE9C6E3C` |
| `08_audits/progress_tracker.md` | `098C93203FD295D4F1EB4596D76649C680CE0119DC61210B04C232310CFBAE9F` |
| `decisions.md` | `272AED3AD8B771EA0D80FD1C06BECEDB9694A29A994323F820C61E9B2C0CE318` |
| `02_source_ledger/source_table.csv` | `29C3BD17FF9731DD0D3D2D563A93531E42F867BAD6793F6622D275AF9CAFCA4E` |
| `01_sources/bibliography.bib` | `289EA496144D01B5582A4A480292EC0BD65F87D51F5920AD4B9AD2B69F2F962E` |
| `01_sources/papers/li_et_al_2022_deeph.pdf` | `92C5A783B46475634A17D2D5F6557D8DE68D2F789F8DFB66182F56862580EC61` |
| `01_sources/documentation/martin_2004_table_of_contents.pdf` | `F58D75B9A3D3E85B2F94ED42FA070F090FAD075C0D9BABF4986C42591D1F69B8` |
| `08_audits/M5_chapter6_independent_content_audit.md` | `A61B46BEEAF7C141DD0B65E51B0E1302D2586CF96A6CAA45C135D358C9E0EC3D` |

## 2. 原阻塞项复核

### M5-C6-B01：`CLOSED`

正文、D-C03.2 和 Q6-02 现已从两个共享基态 Schrödinger 方程相减，得到

\[
\left[\sum_i(v-v')(\mathbf r_i)\right]\Phi=(E-E')\Phi,
\]

并声明共同算符定义域、允许的局域标量势类以及几乎处处非零或相应唯一延拓条件。在这些条件下逐一改变电子坐标，推出 \(v-v'\) 几乎处处为常数；排除该情形后，非简并 Rayleigh–Ritz 不等式才严格化。该步骤关闭了原审计所指出的共同基态逻辑缺口。

材料还分别处理了非简并纯态、简并纯态和简并系综。简并纯态的两条非严格不等式相加后迫使交叉 trial state 也为对方基态，再回到共同基态步骤；结论是局域标量势等价类唯一，而不是简并子空间内波函数唯一。系综情形另行要求共同能量基态集合与权重。自旋密度、流密度等多基本变量理论被明确排除在标量粒子密度命题的无条件外推之外。

新增 C-FND-07 的元数据与原文内容已独立核对。APS 元数据和开放手稿均对应 Capelle、Ullrich、Vignale，*Physical Review A* **76**, 012508 (2007)，DOI `10.1103/PhysRevA.76.012508`；论文确实讨论简并共同基态、多基本变量 DFT 的势非唯一性及相应恢复边界。来源包给出页码范围和开放手稿定位。因此 B01 的逻辑与来源要求均已关闭。

### M5-C6-B02：`CLOSED`

正文、D-C03.4、Q6-04 题目和解答已经统一区分两个搜索层级。在声明的标准三维 Coulomb 条件下，固定密度的纯态 Levy–Lieb 搜索写为

\[
F_{\mathrm{LL}}^{\mathrm{pure}}[n]
=\min_{\Psi\mapsto n}\langle\Psi|\hat T+\hat W|\Psi\rangle,
\]

并说明最小化波函数存在但可以不唯一；外层密度搜索继续写 infimum，其是否取得取决于给定外势问题是否存在基态。离开标准函数空间、改变相互作用或算符条件时重新审查内层可达性。材料也准确区分 Levy 的 constrained-minimum 构造与 Lieb 对标准 Coulomb 域的存在性闭合。原先把标准内层 minimum 留作未决 infimum 的错误已经消除。

### M5-C6-B03：`OPEN`

修订已经满足原 finding 的大部分要求：正文与 D-C03.5 定义

\[
X=L^1(\mathbb R^3)\cap L^3(\mathbb R^3),\qquad
\|n\|_X=\|n\|_1+\|n\|_3,
\]

及 \(X^*=L^\infty+L^{3/2}\)，明确使用 \(X\) 的范数拓扑、把不可接受密度处的泛函值扩展为 \(+\infty\)，并在固定 \(N\) 时使用 \(X^*/\mathbb R\) 或固定势零点。pure/ensemble \(N\)-representability、interacting/noninteracting \(v\)-representability 也已分开；Q6-03 能正确说明密度集合可以相同而状态类与泛函性质不同。

但是，正文第 6.2.4、D-C03.5 和 Q6-04 解答均只写 \(F_{\mathrm L}\) 与 \(F_{\mathrm{ens}}\) “相应”。“相应”既不是等式，也没有说明定义域和扩展约定，不能回答原 finding 要求的“精确关系”。在本章采用的标准三维 Coulomb 条件、固定 \(N\)、\(X=L^1\cap L^3\) 及不可接受密度扩展为 \(+\infty\) 的约定下，应明确写出

\[
F_{\mathrm L}=F_{\mathrm{ens}}
=\operatorname{cl}_{\|\cdot\|_X}\operatorname{conv}
F_{\mathrm{LL}}^{\mathrm{pure}},
\]

其中 \(F_{\mathrm{ens}}\) 的搜索对象是归一化、有限内部能量的反对称 \(N\) 电子统计密度算符；等式只在声明的标准条件和共同扩展约定下成立。“纯态与系综泛函值不能混同”应解释为 \(F_{\mathrm{LL}}^{\mathrm{pure}}\) 与其凸、下半连续闭包不能逐点无条件混同，而不是暗示 \(F_{\mathrm L}\) 与已经定义的标准系综 constrained-search 泛函仍可能不同。

同一问题还出现在 \(T_s\)。正文称

\[
T_s[n]=\inf_{\Gamma_s\mapsto n}\operatorname{Tr}(\Gamma_s\hat T)
\]

是“不预先限定具体非相互作用状态类的统一定义”。搜索类不确定时，同一符号可以指单 determinant 纯态搜索，也可以指其系综凸化；二者不是同一个定义。特别是，若把 \(\Gamma_s\) 任意理解为所有反对称密度算符，就没有表达 KS 非相互作用态由 Slater determinants 组成的限制。

**最小可执行修复：** 在正文第 6.2.4、D-C03.5 和 Q6-04 中，把“相应”替换为带标准条件和扩展约定的上述精确等式，并明确闭凸包所使用的 \(X\) 范数拓扑。在正文第 6.3.1 与 D-C04.1 中至少选择并定义一个主对象；建议定义系综形式

\[
T_s^{\mathrm{ens}}[n]
=\inf_{\Gamma_s\mapsto n}\operatorname{Tr}(\Gamma_s\hat T),
\]

其中 \(\Gamma_s\) 明确为归一化、有限动能的 Slater determinant 投影的凸组合；另将纯态形式写为

\[
T_s^{\mathrm{pure}}[n]
=\inf_{\Phi\mapsto n}\langle\Phi|\hat T|\Phi\rangle,
\]

其中 \(\Phi\) 限于归一化 Slater determinant。随后说明本章无上标的 \(T_s\) 采用哪一个，并保持“定义泛函所需的 noninteracting \(N\)-representability 不等于局域势实现所需的 noninteracting \(v\)-representability”。这两处修复后才可重新复核 B03。

### M5-C6-B04：`CLOSED`

例 6-2、D-C04.7 和 Q6-06 已保留能量层面的严格关系 \(E_{xc}[n]=-E_H[n]\)，同时从固定粒子数允许方向 \(\int\delta n=0\) 推出

\[
v_{xc}(\mathbf r)=-v_H(\mathbf r)+C.
\]

材料说明选定相同势规范后可令 \(C=0\)，一般常数只平移 KS 本征值而不改变轨道和密度，并保留近似泛函与多电子体系不可外推边界。原势规范遗漏已经关闭。

### M5-C6-B05：`CLOSED`

七份章级 Markdown 逐文件执行下列严格命令，结果均为退出码 0：

```text
pandoc --from=markdown+tex_math_dollars+tex_math_single_backslash \
       --to=html5 --mathml --fail-if-warnings -- <file>
```

生成的 MathML 节点数分别为：`sources.md` 6、`outline.md` 6、`chapter.md` 118、`examples.md` 47、D-C03/D-C04 推导 136、问题 19、解答 81。该结果确认修复后的行内和陈列数学实际进入 MathML，而不是仅使 Pandoc 静默通过。人工抽查 HK、Levy–Lieb、Lieb 对偶、\(T_s\)、单电子势抵消、有限温度 \(\tau\) 和本征值重建式，未见原先的普通文本反斜杠、非法 `\left` 或 TAB 吞字符问题。

七文件的 TAB、除 TAB/LF/CR 外 C0 控制字符和 U+FFFD 替换字符均为 0。两个 `examples.md` Python 围栏和一个题解 Python 围栏原样执行均为退出码 0；题解唯一 JSON 围栏由严格解析器读取成功。B05 已关闭。

## 3. 原非阻塞项复核

### M5-C6-N01：`CLOSED`

题集开头现准确声明 Q6-01—Q6-08 可只依据章内材料完成，Q6-09—Q6-10 需要阶段 C 工作包与决策记录。题面新增两个相对链接，分别解析到实际存在的 `08_audits/M5_stageC_work_package.md` 和 `decisions.md`；不再依赖不存在的 `03_textbook/stageC_label_semantics_template.md`。导航与材料范围已经一致。

### M5-C6-N02：`CLOSED`

章级来源表已为 C-FND-02—C-FND-07 补充公式、段落、页码或定理用途定位，并继续声明来源的禁止外推边界。C-FND-07 另给开放手稿定位，可支持简并与多基本变量势非唯一性边界的离线复核。中央来源表的 C-FND-07 行与 BibTeX 条目的题名、作者、卷、文章号、年份和 DOI 一致。Martin 文件继续被限定为目录定位材料，没有被冒充公式正文。原建议已经落实。

## 4. 结构、代码与来源台账验证

- 问题与解答均含 Q6-01—Q6-10，顺序和 ID 集合一一对应。
- 问题文件中的两个相对 Markdown 链接均解析到现存文件。
- 三个 Python 围栏原样执行均为退出码 0；代码数量严格为 `2 + 1 = 3`。
- 题解含且仅含一个 JSON 围栏，严格解析通过。
- Q6-09 的四个固定字节串 SHA-256 独立复算均匹配：`b938...9dc`、`8410...5b6`、`443a...f3d`、`649d...0ff`。
- `source_table.csv` 含 35 条数据记录、每条 17 字段、35 个唯一 `source_id`；C-FND-07 恰有一条且字段完整。
- `bibliography.bib` 含 34 个条目、34 个唯一键，花括号平衡；`capelle2007degenerate` 的卷页年 DOI 与来源表一致。
- 未发现修订引入具体材料、DFT 后端、xc 泛函、赝势、DeepH 版本、正式训练数据或其他 M8/M9 实践选择。

## 5. 新增 finding 检查

未发现独立于原 M5-C6-B01—B05 的新增阻塞项或新增非阻塞项。B03 中关于 \(F_{\mathrm L}\)/\(F_{\mathrm{ens}}\) 和 \(T_s\) 状态类的问题是原 finding 明列验收条件的剩余部分，故不重复编号为新 finding。

## 6. 最终门控

本次定点复核冻结：

- M5-C6-B01：`CLOSED`；
- M5-C6-B02：`CLOSED`；
- M5-C6-B03：`OPEN`；
- M5-C6-B04：`CLOSED`；
- M5-C6-B05：`CLOSED`；
- M5-C6-N01：`CLOSED`；
- M5-C6-N02：`CLOSED`；
- 剩余 `BLOCKING=1`；
- 新增 `BLOCKING=0`；
- **禁止将 M5-03 标记为 `COMPLETED`；**
- **禁止启动 M5-04。**

主 agent 应只实施 B03 所列的最小修复，然后把新的正文、推导和 Q6-04 解答字节快照交回同一独立审计员定点复核。只有后续复核确认上述精确等式、共同扩展约定和 \(T_s\) 搜索状态类均已定义，且新增及剩余 `BLOCKING=0`，才可完成 M5-03 并启动 M5-04。
