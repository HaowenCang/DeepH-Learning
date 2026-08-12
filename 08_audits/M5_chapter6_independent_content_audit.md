# M5-03 第 6 章独立正式内容审计

- 审计日期：2026-08-04
- 审计对象：第 6 章“ Kohn–Sham DFT ”的资料、提纲、正文、例题、D-C03—D-C04 推导、Q6-01—Q6-10 及参考解答；同时核对阶段 C 工作包、主执行计划、进度台账、决策记录、中央来源台账与书目
- 审计性质：独立材料完备性、可自学性、数学与物理条件、来源边界、授权边界和可复现性审计
- 总体结论：`BLOCKING`
- `BLOCKING`：5 项
- `NON_BLOCKING`：2 项
- 是否允许 M5-03 标记为 `COMPLETED`：**否**
- 是否允许启动 M5-04：**否**

当前材料的 KS 分解、轨道正交变分、分数占据与有限温度口径、本征值双计数、标签误差层和 M7-I/M8/M9 授权边界总体正确，数值例及嵌入代码也可复算。然而，HK 证明缺少使严格不等式成立的共同基态排除步骤，标准 Coulomb 密度域上的 Levy–Lieb 内层搜索被错误地保留为未决下确界，Lieb 拓扑与 `T_s` 可表示性边界没有闭合，单电子势抵消遗漏固定粒子数下的加法常数自由度，并且严格 Pandoc 实际失败且大量行内数学已退化为普通文本。这些缺陷直接影响本章冻结能力，不能以一般润色处理。

## 1. 审计范围与 SHA-256 冻结表

除新增本报告外，本次审计未修改任何被审材料、推导、题目、题解、计划、台账或决策文件。下表冻结审计时字节快照。

| 文件 | 审计时 SHA-256 |
|---|---|
| `03_textbook/chapters/06_kohn_sham_dft/sources.md` | `5997F3F0C1483040DF061707D9818D7A50C5F9F316947817FDF8CBAB5AD92CED` |
| `03_textbook/chapters/06_kohn_sham_dft/outline.md` | `963E5C99CD3EFCFA561774596B9D2491D3F4CA72576B2579D58441ACBF53C0B6` |
| `03_textbook/chapters/06_kohn_sham_dft/chapter.md` | `72798444743B9609605BE7E3AD44CEEA74B5089AE49D9B36EB208709C09D0863` |
| `03_textbook/chapters/06_kohn_sham_dft/examples.md` | `763C1843B485FF7C70D0BB8DDD8E72E751D06A3DF83AC30C8BB92F3C6C5AD5A5` |
| `04_derivations/stageC/06_kohn_sham_variation.md` | `553C8F4ACCE566D27C39B00EF87D26E7B165027D3E356F0FEEC675FEFD3350D0` |
| `06_exercises/03-stageC/06_kohn_sham_dft/problem/readme.md` | `0BD738EBFCC810F7671D751DA5EF8A7C0D6883B30D52EC5D8F30FBBDB483B3C4` |
| `06_exercises/03-stageC/06_kohn_sham_dft/solution/readme.md` | `F00E04926A4E0C7B861B4A224C7CE6E8D1DBAC0E69CCC2B6DA1246492423DF79` |
| `08_audits/M5_stageC_work_package.md` | `05BD9488229BCAB10DD43C7A5C24FB20F532D7085E6FAEFA0EB71C575E1A0B95` |
| `00_scope/master_execution_plan.md` | `67BC9A6C77F4338629EACA0A64FF7BFB7B43CD31633BC91155D6E74ADE9C6E3C` |
| `08_audits/progress_tracker.md` | `D944D906DFBBE548A1512712C614E628E094A4D8F32B9BF7F8D548CAA01D4369` |
| `decisions.md` | `272AED3AD8B771EA0D80FD1C06BECEDB9694A29A994323F820C61E9B2C0CE318` |
| `02_source_ledger/source_table.csv` | `3BB19A521C6EB0E4CBACEF6F7A48A613EE095BDC13A9ADB45845A75B0394F0A2` |
| `01_sources/bibliography.bib` | `935DAA9042635B7ACF7F82DE600B237E28A6F8F699F8A0494E14EAD458973895` |
| `01_sources/papers/li_et_al_2022_deeph.pdf` | `92C5A783B46475634A17D2D5F6557D8DE68D2F789F8DFB66182F56862580EC61` |
| `01_sources/documentation/martin_2004_table_of_contents.pdf` | `F58D75B9A3D3E85B2F94ED42FA070F090FAD075C0D9BABF4986C42591D1F69B8` |

## 2. 方法与独立复算

审计采用四层方法。第一层逐式检查 HK、Levy、Lieb、KS 与 Mermin 的对象、量词、定义域和推导条件；第二层把章级来源用途与中央 CSV、BibTeX、原始论文元数据及可访问正文证据交叉核对；第三层原样执行 Markdown 中的 Python/JSON 并以独立实现复算解析例；第四层使用阶段 C 冻结的 Pandoc 命令、控制字符扫描、题目—答案 ID 对照、CSV/BibTeX 结构检查和 SHA-256 冻结验证制品。

来源复核包括：APS 官方页所列 HK、KS、Mermin 的题名、卷页、日期和 DOI；PNAS/NCBI 的 Levy 论文记录及正文摘要；Wiley 的 Lieb 论文元数据；本地原始 DeepH PDF；Martin 本地文件仅按其明确边界用于版本与章页定位，不把目录快照当作公式正文。Levy 原文明确使用 constrained minima，并称固定密度搜索交付 minimum；Lieb 的标准 Coulomb 形式化进一步给出相应存在性结果。因此，审计没有仅凭二手教材习惯决定 B02。

独立数值结果如下。

- 例 6-1 在 `v=(-3,-0.4,0,0.7,2.5)`、`t=1` 上的密度差解析式与 `numpy.linalg.eigh` 最大差为 `2.220446049250313e-16`，逆映射最大差为 `1.7763568394002505e-15`。
- 例 6-4 在 τ 为 `0.1` 和 `0.4` 时分别得到 `(0.9820137900379085, 0.01798620996209156)` 与 `(0.7310585786300049, 0.2689414213699951)`，粒子数均为 1。Q6-08 得到 `(0.8807970779778823, 0.11920292202211755)`。
- 例 6-3 总能量为 `-7.030000000000001`；Q6-07 为 `-9.42`，按“错误值减正确值”定义的有符号误差为 `+1.02`。
- `examples.md` 的 2 个 Python 围栏与题解的 1 个 Python 围栏原样执行均为退出码 0；Q6-09 JSON 可由严格 JSON 解析器读取。
- Q6-09 四个声明字节串的 SHA-256 独立复算与记录完全一致：输入 `b938...9dc`、输出 `8410...5b6`、结构 `443a...f3d`、基定义 `649d...0ff`。

## 3. 已通过项

### 3.1 势常数、KS 分解和轨道变分

固定 `N` 时，`v -> v+C` 使 Hamiltonian 增加 `NC`，本征态和密度不变，能量整体平移；正文、D-C03 与 Q6-01 均保持这一条件。`E_xc=F-T_s-E_H` 被正确写成恒等分解，且没有缩减为“剩余经典相关”。Hartree 导数中的二分之一通过两项对称性正确消去。整数占据下的正交约束产生 Hermitian Lagrange 乘子矩阵，随后只在占据子空间内作 unitary 对角化；规范 KS 轨道在简并子空间中仍保留 unitary 自由度。

普通 `v_xc` 被限定为交换相关泛函具有所需函数导数时的乘法势。材料明确指出次梯度、整数粒子数导数不连续以及 orbital-dependent/hybrid 的非局域算符可能需要系综、次微分或 generalized KS。除 B03、B04 所述边界外，这一主链正确。

### 3.2 分数占据、Mermin 温度和数值 smearing

材料区分零温简并系综、数值 smearing 与物理 Mermin 温度，指出物理有限温度需要熵项、系综和报告量口径；也要求登记占据函数、参数、温度解释、收敛泛函及自由能/内能/零温外推。Fermi–Dirac 数值复算通过，没有把宽化参数自动解释为物理温度。

### 3.3 本征值、双计数和 DeepH 标签层级

常规局域 KS 条件下，材料正确得到

\[
E=\sum_i f_i\varepsilon_i-E_H+E_{xc}-\int v_{xc}n,
\]

并明确 generalized KS 或有限温度口径需要重推。正文区分精确形式化、xc 近似、全电子/赝势对象、离散与采样、SCF/本征求解、投影/重建和 DeepH 统计学习七层误差。原始 DeepH PDF 独立核对确认其目标是给定 DFT/局域基语义下的 Hamiltonian 矩阵映射并绕过新结构上的耗时 SCF；材料没有把网络拟合写成消除上游 xc、离散或表示误差。

### 3.4 授权边界

Q6-10 的 M7-I 配置与 D-011 一致：M7 后由新建的 `gpt-5.6-sol`、`max` 独立 agent 全量审计 M3—M7，主 agent 修复并交回原审计 agent 定点复核，直至新增及剩余问题均为 0。M8 集中冻结资源、后端、DeepH 对象、材料、预算及高级物理范围；M8 前禁止安装 DeepH、下载正式训练数据、生成正式 DFT 标签或隐含选择实践对象；M8 冻结后，M9 外部动作前仍需再次取得明确授权。未发现真实材料、DFT 后端、具体泛函、赝势、DeepH 版本或正式数据被隐含选择。

## 4. BLOCKING findings

### M5-C6-B01：HK 非简并反证缺少使 Rayleigh–Ritz 不等式严格化的闭合步骤，简并边界也未给出可复核命题

**位置：** `chapter.md:67-83`；`06_kohn_sham_variation.md:23-59`；`solution/readme.md:25-39`。

正文直接写出两条严格不等式，推导包则把“假设对方基态不是本方基态”列作前提。非简并性本身并不是展示出的代数步骤；还需排除两个不同局域势共享同一基态的情形。若共享 Ψ，两个 Schrödinger 方程相减给出

\[
\left[\sum_i (v-v')(\mathbf r_i)\right]\Psi=(E-E')\Psi.
\]

在声明的势类、算符定义域及相应非零/唯一延拓条件下，才能推出 `v-v'` 几乎处处为常数。当前材料没有证明或引用这一共同本征态引理，因而所谓“标准反证”实际只证明了一个附加假设下的条件命题。

简并时也不能只说严格不等式“可能退化”后转向模糊的集合/系综表述。对纯态基态密度，非严格变分不等式相加会强迫交叉 trial state 也是对方的基态，再由共同基态步骤处理势等价类；这仍不意味着密度唯一选择简并子空间中的某一波函数。系综密度则需单独写明集合与权重。当前答案没有给出这一区分，无法完成题目要求的独立复核。

**最小修复要求：** 在正文、D-C03.2 和 Q6-02 解答中补齐共同基态排除/处理步骤及所需势类、定义域和几乎处处条件；分别陈述非简并纯态、简并纯态和简并系综能推出什么，明确“势等价类唯一”与“简并子空间中的态不唯一”不是同一命题。来源包应为超出 HK 1964 非简并原始证明的简并扩展提供直接来源定位。

### M5-C6-B02：标准 Coulomb 密度域上的 Levy–Lieb 纯态 constrained search 被错误地保留为未决 infimum

**位置：** `chapter.md:103-124,168,175`；`06_kohn_sham_variation.md:78-121,190-198,439`；`problem/readme.md:19-25`；`solution/readme.md:50-84`；`sources.md:8-13`。

材料把内层纯态搜索定义为 `inf`，并把“只有另有存在性条件才可写 minimum”设置为题目预期答案。这一一般性提醒本身没有逻辑错误，但与本章已经声明的标准三维 Coulomb 密度域、有限内部能量波函数域以及 C-FND-05/C-FND-06 来源组合不相容。Levy 原文将该对象表述为 constrained minimum；Lieb 的标准形式化证明在相应 `N`-representable 密度域上内层下确界可达。应区分的是：

- 固定密度的 Levy–Lieb 内层搜索在标准定理条件下是 minimum，最小化波函数可以不唯一；
- 对密度的外层搜索可写 infimum，是否取得取决于外势问题是否有基态及完整存在性条件；
- 离开标准函数空间、改变相互作用或放宽算符条件时，才应重新审查可达性。

当前材料不只是选了更保守符号，还让 Q6-04 学习者把已由所引 Lieb 来源解决的存在性问题回答成“未决”，并把 “所有 infimum 均达到”列为 Levy 来源绝不支持的外推，因而来源边界失真。

**最小修复要求：** 统一修正文、推导、题目和题解，明确内层 minimum 与外层 infimum 的不同对象；准确归属 Levy 的构造与 Lieb 的存在性/函数分析结果；保留最小化态不唯一、非 `v`-representable 密度和非标准设置的边界，但不得继续把标准 Levy–Lieb 内层 minimum 写成未解决条件。

### M5-C6-B03：Lieb 的下半连续性缺少拓扑对象，且 `T_s` 的 constrained-search 域与 noninteracting `v`-representability 被混合

**位置：** `chapter.md:40-51,126-168,180-208`；`06_kohn_sham_variation.md:123-186,202-224`；`solution/readme.md:43-48,60-84`。

材料给出密度集合 `I_N` 嵌入 `L^1 ∩ L^3` 和势空间 `L^(3/2) + L^infinity`，随后声称 `F_L` 凸且下半连续，却明确不声明所用拓扑。下半连续性不是脱离拓扑的性质。标准表述至少应定义密度 Banach 空间 `X=L^1 ∩ L^3` 及其范数拓扑、对偶配对势空间 `X*=L^infinity + L^(3/2)`，并说明把泛函在不可接受密度上扩展为 `+infinity` 后所讨论的凸闭性/下半连续性和 Legendre–Fenchel 对偶。固定 `N` 时势还需模掉加法常数或显式保留相应规范。

可表示性部分又把两种不同问题合在“所需非相互作用可表示性”之下：用 determinant/非相互作用系综对固定密度作 constrained search 来定义 `T_s`，属于 noninteracting `N`-representability；要求该密度是某个局域一体势的基态密度，才是 noninteracting `v`-representability，并关系到普通局域 KS Euler 方程是否存在。当前正文在 `chapter.md:182-188` 先以未定义的“非相互作用可表示性”限制 `T_s`，随后又把单 determinant、简并系综和分数占据混列，不能让学习者判断哪个条件用于定义泛函、哪个条件用于产生局域势。

此外，标准连续空间的一体密度问题中，pure/ensemble `N`-representable 的状态类不同，但可表示密度域在适当条件下可同为声明的 `I_N`；相应 pure 与 ensemble constrained-search 泛函值和凸性仍可能不同。当前“这些集合不能视为相同”的笼统表述没有给出该条件关系。

**最小修复要求：** 明确 `X`、`X*`、范数/拓扑、扩展值约定、势常数商空间或规范及 `F_L` 与系综 constrained-search 泛函的精确关系；分开 pure/ensemble `N`-representability、interacting/noninteracting `v`-representability、`T_s` constrained search 与局域 KS 势存在性。Q6-03、Q6-04 解答应给出集合/泛函关系，而不只逐项复述定义。

### M5-C6-B04：单电子势抵消遗漏固定 `N` 受限导数的加法常数自由度

**位置：** `examples.md:96-114`；`06_kohn_sham_variation.md:363-377`；`problem/readme.md:37-39`；`solution/readme.md:145-162`。

对一个电子，能量等式 `E_xc[n]=-E_H[n]` 在适当密度域上正确。但本章从始至终固定 `∫n=1`；在该约束流形上只允许 `∫δn=0`。由

\[
\int (v_{xc}+v_H)\,\delta n=0
\]

对所有粒子数守恒方向成立，只能推出

\[
v_{xc}(\mathbf r)=-v_H(\mathbf r)+C
\]

几乎处处，而不是无规范说明的严格相等。选择相同势零点时可令 `C=0`；一般 `C` 只整体平移 KS 本征值，不改变轨道和密度。当前三处都直接写成 `v_xc=-v_H`，与本章 6.1.3 和 D-C03.6 已承认的势常数自由度不一致。

**最小修复要求：** 在例题、推导和 Q6-06 解答中把势抵消写成“到加法常数”并说明选定规范后可取 `C=0`；保留能量层面的严格 `E_xc=-E_H`、近似泛函通常不精确满足及多电子不可外推边界。

### M5-C6-B05：冻结的严格 Pandoc 验证失败，且大量行内数学已退化为普通文本

**位置：** `chapter.md:115-121,138-164`；`examples.md:15-178`，尤其 `156,162,170,178`；`06_kohn_sham_variation.md` 全文行内公式；`problem/readme.md:7-66`；`solution/readme.md` 全文行内公式，尤其 `194`。

按阶段既有命令执行：

```text
pandoc --from=markdown+tex_math_dollars+tex_math_single_backslash \
       --to=html5 --mathml --fail-if-warnings <file>
```

结果为 6/7 退出 0，`chapter.md` 退出码 3。四组集合式使用无效的 `\left{ ... \right}`，Pandoc 报 `unexpected control sequence \left`；应使用转义花括号或其他合法定界符。因此本章不能满足“所有严格 Pandoc 可复现”。

另外，D-C03/D-C04 推导包和参考解答的实际行内数学定界符数量均为 0，大量对象被写成普通 `(hat T)`、`(Psi)`、`(sqrt n\in H^1)`、`(phi_i^*)`、`(int v_Hn=2E_H)`；问题文件也有同类内容。它们虽然不触发 Pandoc warning，却只渲染为带反斜杠或丢失控制序列的普通文本。`examples.md` 含 5 个 TAB，题解含 1 个 TAB；其中 `\tau` 已变成 TAB 加 `au`，实际显示为 `( au=...)`。这使有限温度例题的核心变量损坏。

**最小修复要求：** 修复四组 TeX 集合定界符；把所有意在表达数学的普通括号恢复为合法 `\(...\)`，不得机械替换真正的中文括注；恢复 6 个 TAB 所吞掉的 `\tau`；随后对七文件执行严格 Pandoc/MathML、控制字符、代码围栏和人工渲染抽查。验收不能只看 Pandoc 退出 0，还应确认行内对象实际生成 MathML。

## 5. NON_BLOCKING findings

### M5-C6-N01：题集的“仅依据本章材料”声明与映射中的外部治理文件不一致

`problem/readme.md:3` 声称全部题目仅依据正文、例题和 D-C03—D-C04 即可完成，但 `problem/readme.md:96` 又把 Q6-09—Q6-10 映射到“阶段 C schema；D-010/D-011”。工作包冻结的 `03_textbook/stageC_label_semantics_template.md` 当前尚不存在，D-011 的精确模型配置也只在决策文件和参考解答中出现。参考解答本身完整且授权答案正确，因此不单独增加理论阻塞；但自学导航应提供可点击的实际路径，或把题集开头改为准确的材料范围。不得保留指向尚未交付文件的无说明依赖。

### M5-C6-N02：章级来源包缺少公式级页码/定理定位，离线独立复核仍依赖外部可用性

中央 CSV 与 BibTeX 中 C-FND-02—C-FND-06 的题名、作者、卷页和 DOI 一致，章级禁止外推边界总体合理；CSV 为 34 条数据记录、每条 17 字段、无重复 source ID，BibTeX 为 33 个唯一键且花括号平衡。可是，HK/KS/Mermin/Lieb 只有 DOI，没有页码内公式或定理编号，且本地没有相应全文快照；Martin 本地文件按记录仅为目录。此次联网核验能够确认来源，但后续离线审计不能仅凭当前本地证据重做公式级检查。建议在许可范围内补充精确页码、定理号或可长期访问的开放正文定位，并继续明确目录快照不替代正文。

## 6. 可复现性、完备性与来源边界结论

### 6.1 静态与结构检查

- 七份章级材料的严格 Pandoc 结果为 `6/7` 通过；失败详情见 B05。
- 除允许的 TAB/LF/CR 外，七文件 C0/DEL 控制字符为 0；但 TAB 所造成的 τ 损坏仍属内容错误。
- 问题与解答标题均完整覆盖 Q6-01—Q6-10，ID 集合一一对应，无缺题或错位。
- 三个 Python 围栏原样运行通过；Q6-09 JSON 可解析，四个内容哈希可复算。
- 中央 CSV/BibTeX 结构检查通过；本地 DeepH PDF 哈希与既有冻结值一致。

### 6.2 材料完备性与可自学性

材料已经覆盖题目要求的大多数知识对象，十题均有逐题答案，解析例、数值例、错误诊断和授权清单较完整。B01—B04 使关键数学边界仍不能从当前材料可靠学得，B05 又使推导与题解中的大量行内公式不能按预期渲染。因此当前只能判定为“结构齐全但内容与制品未达可自学门控”，不能判定材料完备。

### 6.3 来源授权边界

C-FND-02 用于 HK 唯一性与变分结构、C-FND-03 用于 KS 构造、C-FND-04 用于有限温度、C-FND-05 用于 pure constrained search、C-FND-06 用于函数空间与凸对偶的分工方向正确；没有发现把 DeepH 标签提升为精确多体 Hamiltonian，也没有以来源授权具体后端或泛函。B01 要求增加简并扩展来源，B02 是已有来源被错误解读，B03 是引用 Lieb 时缺少完整定理对象。除这些 finding 外，没有发现新的来源越权。

### 6.4 可验证性

数值与代码证据可验证，标签 JSON 的字节串哈希真实；但是 Markdown/MathML 制品门控失败。因此当前“数值可复算”不能替代“教材制品可复现”，总体可验证性判定为不通过。

## 7. 最终门控判定

本次独立正式内容审计冻结：

- `BLOCKING=5`；
- `NON_BLOCKING=2`；
- M5-C6-B01—B05 均未关闭；
- **禁止将 M5-03 标记为 `COMPLETED`；**
- **禁止启动 M5-04。**

主 agent 应实施 B01—B05 的最小修复，并在同一轮处理 N01/N02；随后必须由独立审计员对修订文件执行定点复核。只有定点复核明确给出新增及剩余 `BLOCKING=0`，才允许完成 M5-03 并启动 M5-04。主 agent 的自检、Pandoc 单次退出 0 或数值代码通过均不能替代该独立门控结论。
