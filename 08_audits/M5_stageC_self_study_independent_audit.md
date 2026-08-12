# M5-09 阶段 C 自学材料独立审计

## 1. 独立性、范围与结论

- 审计时间：2026-08-04 06:16:08 +08:00。
- 审计角色：独立材料完备性与可自学性审计员；未参与本轮被审材料建设。
- 只读约束：未修改教材、推导、代码、练习、README、工作包、决策记录或进度台账；本文件是唯一新增文件。
- 核心范围：`stageC_self_study_guide.md`、`stageC_label_semantics_template.md`、阶段 C 综合问题与解答。
- 交叉范围：第 5、6、7、8、10 章的 chapter/examples/sources，阶段 C 五个推导及索引，教学 SCF 实现/测试/README，M5 工作包和 `decisions.md`。
- 审计口径：材料建设模式不要求学习者闭卷作答、口头说明或提交阶段自测，但不得降低知识范围、来源边界、数学条件、数值判据、失败样例和独立审计门槛。

**最终结论：FAIL。`BLOCKING=3`，`NON_BLOCKING=0`。当前不允许把 M5-09 标记为完成，也不允许启动 M5-10。**

失败原因不是代码门控退化：固定环境下 9 项 unittest、两组冻结 CLI、67/67 删除和 47/47 对抗变异均通过。阻塞集中在两份核心导航/模板的数学渲染与非法控制字符、C-C07 的对象与数值对应，以及 C-C08 的验证层次完整性。

## 2. 快照与 SHA-256

审计快照共 47 个文件。聚合哈希的构造方式为：按工作区相对路径排序，每行写入 `<lowercase-sha256><two spaces><forward-slash-relative-path>\n`，再对 UTF-8 清单计算 SHA-256。

- 快照文件数：47。
- 聚合 SHA-256：`1e717a6c6f9eb3a2e6df477a9b53934bb1325e07bed0afc81eec70804eeb813b`。

| 文件 | SHA-256 |
|---|---|
| `03_textbook/chapters/stageC_self_study_guide.md` | `fb9dd0b47c986e8b03e360221a911fc9618d6967c85eba971e20e10533471f17` |
| `03_textbook/stageC_label_semantics_template.md` | `b4db5c5fdcca1362b1add5ece69255e237817404abc7f23d48b24462a94edd7f` |
| `06_exercises/03-stageC/comprehensive/problem/readme.md` | `f79564cabeb58c3e72850d91b97e6de46fc04a89479b81bed35e0e68125e5bf1` |
| `06_exercises/03-stageC/comprehensive/solution/readme.md` | `3152ae9cb02cfb6cd0ecef2470af4bf16b5cc6d442f337d4e014d3642ab38d4f` |
| `04_derivations/stageC/README.md` | `8c0a8ed24c112233d8e5f8ebf25918dd58616a4b023f1463f5971cc7b6b00a1d` |
| `05_code_exercises/stageC_teaching_scf/README.md` | `ff82358bd8422a6a457764c0d308bbd3f8c09d78e559567b5283eeeaff4dce70` |
| `05_code_exercises/stageC_teaching_scf/requirements.txt` | `cc3efbcd187c80addd5db987ee90ad17bd481814985761d7b5cfac3f0b5e10e4` |
| `05_code_exercises/stageC_teaching_scf/teaching_scf.py` | `597af234a2688cd9cf71d2c501514ee07700a2fb0361026aef4be0221bebd867` |
| `05_code_exercises/stageC_teaching_scf/run_experiments.py` | `746681fc4bba4eee98b89870c6683c6a8251eea28be01b1d8d5fa0d81b1128e9` |
| `05_code_exercises/stageC_teaching_scf/test_teaching_scf.py` | `688956a996a48d4a04280f3a45735b47c5d19cbc21ac9576c73c9b2057ddd59b` |
| `08_audits/M5_stageC_work_package.md` | `0fb3821fdca4c4015725015cde95a90d7fd81c5b559b03fb2a4e6377540bf497` |
| `decisions.md` | `272aed3ad8b771ea0d80fd1c06becedb9694a29a994323f820c61e9b2c0ce318` |

五个推导文件的哈希为：D-C01/D-C02 `01385729d1d0df6b50b3e4ef0e9624959845d2fd55e2a49d0d28e1009b7f64d2`，D-C03/D-C04 `9986fce7facdeabe55cbf6dcc8e5c1dd6c86e0bb7ab7ecfdd0ba7a5d16975335`，D-C05 `0353ccca35d27e357604e189c139c8a1f2bdfc47d57b217c781516165fd138b7`，D-C06/D-C07 `5b432fece9975840ee655ed8cfd678bf5d54e4b7ee897f55f0d88380673c1cb7`，D-C08 `708603589dceb4ec68b5a6c17b1012a97db62aeb8834b2e8ce570bd255cd191b`。

## 3. 总体门控审计

| 审计项 | 结果 | 独立判断 |
|---|---|---|
| 材料建设模式 | PASS | 指南明确不要求个人闭卷/口头/自测证据，同时保留教材、推导、例题、练习、解答、代码、失败样例和独立审计；与 D-010 一致。 |
| 原知识与技术门槛 | PASS（受下列具体阻塞约束） | 五章、8 项推导、10 项测试和 10 道综合题均保留；未发现以取消个人作答为由删减知识范围。 |
| 来源与推导边界 | PASS | 五章 sources 和推导区分 `PRIMARY_EXPLICIT`、`DIRECT_DERIVATION`、`PEDAGOGICAL`；未把 Levy/Lieb 冒充 HK 1964 的直接代数推论。 |
| 自学指南链接 | PASS | 指南 30/30 个本地链接存在；限定 43 个 Markdown 文档共 71/71 个本地链接存在。 |
| 严格 Pandoc 语法转换 | PASS | 43/43 文档用 `markdown+tex_math_single_backslash`、HTML5、MathML、`--fail-if-warnings` 转换退出码均为 0。 |
| MathML 语义覆盖 | BLOCKING | 指南和标签模板均产生 0 个 MathML 节点；两文件把应为数学的内容写成普通括号文本，模板还残留裸 `\times`、`\succ`。见 B01。 |
| 非法控制字符 | BLOCKING | 限定 43 个 Markdown 文档中发现 1 个问题：指南 byte offset 9416 的裸 `0x0D`，破坏 `\rho`。见 B01。 |
| `stageC-label-v1` 与实现 | PASS | 文档分组展开后与代码 `REQUIRED_PATHS` 的 67 路径一致；类型、shape、有限性、4 个内容哈希、14 个 `UNRESOLVED_M8` 哨兵和合成白名单均由实现检查。 |
| 67 删除/47 变异 | PASS | 两组 CLI 均报告 67/67 删除失败；47/47 变异被拒绝，分类为 type 9、shape 11、hash 8、M8 choice 19，错误见证含字段路径。 |
| M8/M9 边界 | PASS | requirements 仅含 NumPy/SciPy；代码只导入标准库、NumPy、SciPy。未发现 DeepH/DFT 调用、正式数据、正式标签或真实材料/后端选择；M8 冻结和 M9 二次授权保持独立。 |

## 4. D-C01—D-C08 逐项表

| ID | 结果 | 可定位入口与边界 |
|---|---|---|
| D-C01 | PASS | 第 5 章 5.1、`05_many_electron_mean_field.md` D-C01、Q5-01/Q5-02、C-C01；保留导数耦合、Berry 连接、Born–Huang、简并与单面近似条件。 |
| D-C02 | PASS | 第 5 章 5.2—5.5、同推导 D-C02、Q5-03—Q5-10、C-C01；区分 determinant、密度、1RDM、HF/KS，并限定单 determinant 1RDM 幂等性。 |
| D-C03 | PASS | 第 6 章 6.1—6.2、`06_kohn_sham_variation.md` D-C03、Q6-01—Q6-04、C-C02；正文/推导正确处理共同基态、简并、纯态/系综、内层 minimum、外层 infimum、Lieb 闭包与可表示性。 |
| D-C04 | PASS | 第 6 章 6.3—6.5、同推导 D-C04、Q6-05—Q6-10、C-C03；局域 KS、普通导数/次梯度、分数占据、Mermin/smearing 和本征值语义边界存在。 |
| D-C05 | PASS | 第 7 章、`07_scf_fixed_point.md`、T-C01—T-C04、C-C04/C-C05；谱半径仅作局部渐近结论，并覆盖非正规暂态、约束和双停止判据。 |
| D-C06 | PASS | 第 8 章 8.1—8.5、`08_representation_and_label_error.md` D-C06、T-C05/T-C06、C-C06；保留 `S=I` 的条件和非正交 `S\succ0` 边界。 |
| D-C07 | PASS（C-C07 题解对应另有 B02） | 第 8 章 8.6—8.8、同推导 D-C07、T-C07—T-C09、C-C07/C-C08；正交/非正交投影、回投、等谱与固定坐标标签均有完整推导。 |
| D-C08 | PASS | 第 10 章、`10_nearsightedness_sparsity.md`、T-C10、C-C09；区分近视性、1RDM 衰减和基依赖的 `H/S` 稀疏，并限定谱隙、温度、维数和长程扰动。 |

## 5. T-C01—T-C10 逐项表

固定解释器为 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0；`pip check` 报告 `No broken requirements found.`。9 项 unittest 全部通过。

| ID | 结果 | 独立证据摘要 |
|---|---|---|
| T-C01 | PASS | `status=pass`，发散注入 `detected=true`；独立复算 `x_*=(0.375,-0.4,1/14)`，谱半径 0.6/1.8，12 次更新末/初残差比 309.176191688。 |
| T-C02 | PASS | `status=pass`，两周期失败被捕获；归一化不被误当作固定点收敛。 |
| T-C03 | PASS | `status=pass`，缩放伪能量的 energy-only 误通过被捕获。 |
| T-C04 | PASS | `status=pass`，`max_iterations` 失败被捕获；同配置双跑 JSON 哈希一致。 |
| T-C05 | PASS | `status=pass`，正序列通过，局部假平台负序列被参考误差拒绝。 |
| T-C06 | PASS | `status=pass`，采样轴与固定 `10^-2` 基偏置分离。 |
| T-C07 | PASS | `status=pass`；广义谱最大误差 `6.66e-16`，最大归一残差 `1.49e-16`，`lambda_min(S')=1.21544`，忽略 overlap 的最大谱差 `0.967465`。 |
| T-C08 | PASS | `status=pass`；两配置丢失范数 `0.959859/0.983317`，等谱差 `4.44e-15`，固定坐标矩阵差 `0.233061/0.174520`。 |
| T-C09 | PASS | `status=pass`；67/67 删除和 47/47 变异均被拒绝，完整记录有效。 |
| T-C10 | PASS | `status=pass`；重算指标差为 0，指数斜率 `-0.5`，代数尾错误外推残差 `0.842970784`。 |

两组冻结 CLI 的独立双跑结果：

| seed/model/grid | 两次退出码 | `overall_pass` | T-C01—T-C10 | 每项 `expected_failure.detected` | 两次输出 SHA-256 |
|---|---|---|---|---|---|
| `20260805/12/64` | `0/0` | `true` | 全部 `pass` | 全部 `true` | `9aa7ccad03a3237056e122950f21ad44a2441933a63b6bfc82efe367eb0730ce`（两次相同） |
| `20260806/16/48` | `0/0` | `true` | 全部 `pass` | 全部 `true` | `ce52babd2b0c839646a0a28929dda87f26a2cb27b202fc50d28fd6cd4db4c5a4`（两次相同） |

## 6. C-C01—C-C10 逐项表

问题和解答的二级标题集合均严格为 C-C01—C-C10；五个章内问题/解答也分别为 Q5/Q6/Q7/Q8/Q10 的 01—10，编号无缺失。

| ID | 结果 | 判断 |
|---|---|---|
| C-C01 | PASS | 固定核保留/删除项、导数耦合、单面条件、占据 unitary 不变量和一般相关态非幂等边界对应完整。 |
| C-C02 | PASS | HK/共同基态/简并、四类可表示性、纯态/系综与 Lieb 闭包对应正确；解答以 infimum 作一般安全表述，章节、推导和 sources 则明确限定标准 Coulomb 域内层 minimum 与外层 infimum，未形成错误外推。 |
| C-C03 | PASS | 轨道正交约束、有效势、Hartree/xc 双计数、本征值和与总能量、辅助谱语义对应正确；章节/推导补足普通导数、系综与 generalized KS 边界。 |
| C-C04 | PASS | 固定点、误差矩阵、谱半径、12 次更新和第 0 步边界均与独立复算一致。 |
| C-C05 | PASS | 非线性两周期、双判据、伪能量和 `max_iter` 失败机制一一对应。 |
| C-C06 | PASS | 两序列的参考误差与相邻差准确；T-C06 的相邻采样差不能消除独立基偏置。 |
| C-C07 | BLOCKING | 广义谱和回投公式正确，但等谱反例的题面矩阵与解答/自动测试数值不是同一对象。见 B02。 |
| C-C08 | BLOCKING | 变异原因和 67/47 数量正确，但七层列表遗漏标签模板明确要求的独立语义验证层。见 B03。 |
| C-C09 | PASS | 三个截断指标、指数斜率、代数尾外推失败和三种局域性陈述均正确。 |
| C-C10 | PASS | 对象链、逐箭头误差/证据/失败样例和 M8/M9 双门槛完整。 |

## 7. 独立复算

### 7.1 C-C04

由 `(I-J)x_*=b` 得

```text
x_* = (0.375, -0.4, 0.0714285714286)
M_0.8 diagonal = (0.36, 0.60, -0.12), rho = 0.6
M_2.0 diagonal = (-0.6, 0, -1.8), rho = 1.8
12 updates: r_12/r_0 = 309.1761916881516
```

这些值与 C-C04 解答和 T-C01 一致。

### 7.2 C-C06

```text
q+ last-three reference errors = (0.008, 0.002, 0.0005)
q+ last-two adjacent differences = (0.006, 0.0015)
q- last-three reference errors = (0.002, 0.0015, 0.008)
q- last-two adjacent differences = (0.0005, 0.0065)
```

对 `exp(cos k)`，16/32/64 点采样误差均约为 `2.22e-16`；加入 `0.01` 固定基偏置后总误差约为 `0.01`。解答数值和机制正确。

### 7.3 C-C07 与 T-C07/T-C08

一致合同变换后的广义谱为 `(-1.2,-0.1,0.8,2.0)`；最大谱误差 `6.66e-16`，最大归一后向残差 `1.49e-16`，`S'` 最小本征值 `1.2154403466`；对 `H'` 错用普通谱的最大差 `0.9674651568`。这些值正确。

T-C08 的 `d=12, seed=20260805` 随机正交模型给出谱差 `4.44e-15`、固定坐标矩阵相对差 `0.2330607578`。但 C-C07 题面在同一节只给出了 4 维对角矩阵 `H=diag(-1.2,-0.2,1.2,4.6)`，再令标准基第 0、1 维旋转 0.37 rad。对该题面对象独立复算得到：

```text
spectrum difference = 2.220446049250313e-16
relative Frobenius matrix difference = 0.10421583493929089
```

因此解答中的 `0.233` 不是题面矩阵的结果，而是另一个 T-C08 随机模型的结果。

### 7.4 C-C09

对 `N=64` 指数族，`R_c=(2,4,8,16)` 的相对 Frobenius 误差为

```text
(0.263905900008, 0.0954651348485, 0.0124696360765, 0.000210934584215)
```

相对作用量误差为

```text
(0.268682171993, 0.0961926066125, 0.0122695559340, 0.000194418726938)
```

指数拟合斜率为 `-0.49999999999999994`；代数族 1—8 拟合后外推 16—31 的相对残差为 `0.8429707836304159`。解答中的关键数值正确。

## 8. 命令与结构证据

### 8.1 固定 Python 门控

```powershell
$py='C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -c "import sys,numpy,scipy; print(sys.version); print(numpy.__version__); print(scipy.__version__)"
& $py -m pip check
& $py -m unittest discover -s .\05_code_exercises\stageC_teaching_scf -p 'test_*.py' -v
& $py .\05_code_exercises\stageC_teaching_scf\run_experiments.py --format json --seed 20260805 --model-size 12 --grid-size 64
& $py .\05_code_exercises\stageC_teaching_scf\run_experiments.py --format json --seed 20260806 --model-size 16 --grid-size 48
```

结果：Python/NumPy/SciPy 精确为 `3.12.13/2.3.5/1.18.0`；`pip check` 通过；9 项 unittest 通过；两组 CLI 均为退出码 0 和 `overall_pass=true`。

### 8.2 Pandoc/MathML

```powershell
pandoc --from='markdown+tex_math_single_backslash' --to=html5 --mathml --fail-if-warnings -- <file>
```

43/43 文档转换成功。核心综合问题和解答分别产生 50 和 93 个 MathML 节点；自学指南和标签模板均为 0。成功退出只证明 Pandoc 接受语法，不能证明原本应为数学的普通文本被转换为 MathML。

### 8.3 链接与控制字符

链接检查按 Markdown 文件所在目录解析非 HTTP、非锚点目标：指南 30/30、限定范围 71/71 均存在。字节检查拒绝 C0 控制字符，并要求 CR 只能作为 CRLF 的一部分；限定 43 个 Markdown 文件仅指南 offset 9416 的 `0x0D` 失败。

## 9. BLOCKING 清单与逐文件修复要求

### M5-09-B01：自学指南和标签模板的数学内容未进入 MathML，且指南 `rho` 被非法 CR 实际破坏

证据：`03_textbook/chapters/stageC_self_study_guide.md` 没有任何 `\(` 内联数学起始符；第 62、64、74 行等把 `F_{mathrm L}`、谱半径和 `E_{xc}` 写成普通括号文本。byte offset 9416 为裸 `0x0D`，相邻字节解码为 `(<CR>ho(M_alpha)<1)`，原 `\rho(M_\alpha)<1` 已丢失反斜线和希腊字母语义。

标签模板还有同一类实际缺陷：`03_textbook/stageC_label_semantics_template.md` 没有任何 `\(`，Pandoc 产生 0 个 MathML 节点；第 30、32、121 行含裸 `3\times3`、`N\times3`、`S\succ0`，其余表格把 `E_{xc}`、`H,S`、`k`、`R` 等作为普通括号文本。

修复要求：在自学指南中把全部数学对象恢复为 Pandoc 可识别的 `\(...\)`，重点把损坏行恢复为 `\(\rho(M_\alpha)<1\)`，并处理 `F_{\mathrm L}`、`E_{xc}`、`H/S`、`S\succ0`、`k`、`alpha` 等同类表达；在标签模板中为 shape、正定条件、矩阵/索引/Fourier 变量补齐 `\(...\)`，代码值和 JSON 字符串继续使用反引号。修复后必须重新执行字节级控制字符扫描、MathML 节点检查和链接检查，不能只看 Pandoc 退出码。

### M5-09-B02：C-C07 题面与解答使用不同 Hamiltonian，数值和 T-C08 阈值不可对应

证据：`06_exercises/03-stageC/comprehensive/problem/readme.md` 第 112—122 行给出 4 维对角 `H` 后直接定义标准基 0、1 维旋转；该对象的相对矩阵差为 `0.1042158349`。`solution/readme.md` 第 165 行却给出约 `0.233`，这是 T-C08 的 `d=12` 随机 `Q diag(linspace) Q^dagger` 模型；前者也不满足 T-C08 的 `>0.15` 失败指标。

修复要求：同时修复综合问题和解答。若要保留 T-C08 数值，应在题面明确另行定义 T-C08 的 seed、维数、QR 规范和随机 Hamiltonian，并在解答说明它与前述 4 维广义谱对象不同；若坚持复用 4 维 `H`，则应把解答改为 `0.1042158349`，删除对 `>0.15` 自动门控的暗示，并提供另一个明确对应 T-C08 的入口。修复后独立复算两种对象，避免符号 `H` 偷换。

### M5-09-B03：C-C08 七层验证遗漏“语义一致性”层

证据：标签模板第 113—124 行的验证顺序在结构、身份、授权、数值之后单列语义验证：单位、轨道顺序、bra/ket、晶格位移方向、Fourier、规范和 overlap 处理；随后才是前向验证和独立审计。综合问题第 126 行及解答第 169 行把 type 与 shape 分拆为两层，却省略语义验证，导致七层列表与模板不一致。路径存在、类型/shape、哈希、授权、数值结构和前向谱均不能替代固定表示语义一致性。

修复要求：同时修复综合问题和解答。建议把 type 与 shape/关系合并为“结构验证”，按模板恢复路径、结构、身份、授权、数值、语义、前向七层，并把独立审计作为第八步；或保留 type/shape 分拆但明确列出八个技术层加独立审计。必须说明当前 47 个对抗变异的实际分类只有 type/shape/hash/M8 choice，不能把它们过度声明为已覆盖全部语义和前向物理验证。

## 10. NON_BLOCKING 清单

`NON_BLOCKING=0`。未登记仅影响措辞、风格或非关键定位的问题。

## 11. 关闭条件与门控决定

三项阻塞均需按上述逐文件要求修复，并由独立复核确认：

- 限定 Markdown 控制字符问题为 0；
- 自学指南和标签模板中的数学对象实际生成 MathML，不以 Pandoc 退出码代替覆盖检查；
- C-C07 题面、解答和 T-C08 数值使用明确且相同的对象；
- C-C08 的语义验证层与模板顺序一致；
- 30/30 指南链接、9 项 unittest、两组 CLI、67/67 删除和 47/47 变异仍通过。

在这些条件满足前，**M5-09 不得完成，M5-10 不得启动**。本审计没有授权 DeepH/DFT 安装、正式数据下载、正式标签生成或任何 M8 前真实实践选择；即使后续 M8 冻结，M9 外部动作仍需再次取得明确授权。
