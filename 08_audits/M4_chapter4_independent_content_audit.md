# M4-04 第 4 章独立正式内容审计

## 1. 审计结论

- 审计日期：2026-08-04
- 审计角色：独立子 agent
- 审计对象：第 4 章资料包、三级提纲、正文、四个例题，D-B05/D-B06 逐步推导，Q4-01—Q4-10 练习与参考解答，阶段 B 统一约定和 M4 工作包
- 修改边界：本次审计只新增本报告，未修改任何被审计材料、`README`、工作包或进度台账
- 总体结论：**通过；剩余 `BLOCKING` 为 0，记录 3 项 `NON_BLOCKING`。**
- 门控判定：**允许主 agent 将 `M4-04` 标记为 `COMPLETED`，并将 `M4-05` 标记为 `READY`。** 本报告不代替主 agent 对进度台账的实际更新。

第 4 章已经形成闭合且相互一致的数学链条：直接/倒格定义、Born–von Karman 有限群角色、主动平移符号、cell-phase Bloch 和、实空间矩阵方向、离散 Fourier 正反变换、不同 \(\mathbf k\) 块解耦、实空间共轭配对、\(k\) 空间 Hermiticity、overlap 正定性边界以及轨道中心规范均满足工作包要求。四个例题的解析结论正确；固定 Python 环境中的八个现有断言全部通过；十道题与十份解答一一对应。三项非阻塞问题分别是两处 `\qquad` 转义缺失、系数倒格周期性陈述尚可增加本征矢相位/简并限定，以及例 4.4 尚未进入嵌入式 Python 断言。这些问题不改变 Fourier 符号、广义谱或门控所需的核心结论，但应在后续修订中关闭。

## 2. 审计快照

七个用户给定的固定 SHA-256 全部匹配；两个上下文文件另行记录审计时哈希。

| 文件 | 审计时 SHA-256 | 固定快照匹配 |
|---|---|---|
| `03_textbook/chapters/04_periodicity_bloch_reciprocal/sources.md` | `FE3B31F4CE7FD46ECF83189BE4A1CE9BDE4960C0EBDDB749F81D90E2DC64A713` | 是 |
| `03_textbook/chapters/04_periodicity_bloch_reciprocal/outline.md` | `AB169D1B55DB1C2A08430D08E9EB562BAC720FBEC90EC7953D1484909AF6A736` | 是 |
| `03_textbook/chapters/04_periodicity_bloch_reciprocal/chapter.md` | `B2B9DA58AD6E02A22985BD2E9C68117EC7A0652C992E3E67C849DA65FEB5EEE2` | 是 |
| `03_textbook/chapters/04_periodicity_bloch_reciprocal/examples.md` | `899A8EBB2D61D67557D5ABBF95FA8E398DD8799B0C017890DE84FC51499B7597` | 是 |
| `04_derivations/stageB/04_bloch_fourier.md` | `AF4C4D07DE175324271DAAED14864CAFA521720C2DCB3D4E4FFABD186434BAA4` | 是 |
| `06_exercises/02-stageB/04_bloch_fourier/problem/readme.md` | `639302138F7372F9C0EB683B6E61D0A908D6337066BAC39C93D250979C035F73` | 是 |
| `06_exercises/02-stageB/04_bloch_fourier/solution/readme.md` | `8083674BDC9344E3501B159AF1042D80AFEDA9763A81AD89EF200944E4C32205` | 是 |
| `03_textbook/stageB_conventions.md` | `66A135C38DBA8536D88701ED85DEBAE51D60A3E48CD0D09DFBBB463A2240B464` | 上下文快照 |
| `08_audits/M4_stageB_work_package.md` | `C479CCE2F40C4865301329C3A61E297B6D7B768B09202C3867BDB6677A212E32` | 上下文快照 |

## 3. 核心内容逐项核查

| 审计项 | 判定 | 主要证据与独立核查结果 |
|---|---|---|
| 1. 直接/倒格、BvK 有限集合与有限角色正交 | 通过 | `chapter.md:13-58` 和推导 `04_bloch_fourier.md:7-60` 给出 \(\mathbf b_i\cdot\mathbf a_j=2\pi\delta_{ij}\)、\(\mathcal R_N\)、\(\mathcal K_N\) 及两组有限角色正交关系；几何级数证明正确，Kronecker delta 明确按超胞等价类理解。 |
| 2. 主动平移与 Bloch 条件符号 | 通过 | `chapter.md:64-88`、推导 `04_bloch_fourier.md:66-87` 和 Q4-03 一致采用 \((\hat T_{\mathbf R}\psi)(\mathbf r)=\psi(\mathbf r-\mathbf R)\)。将 \(\mathbf r\) 换为 \(\mathbf r+\mathbf R\) 后，\(e^{-i\mathbf k\cdot\mathbf R}\) 本征值确实等价于 \(\psi(\mathbf r+\mathbf R)=e^{+i\mathbf k\cdot\mathbf R}\psi(\mathbf r)\)。 |
| 3. Plus cell-phase 与 Fourier 正反变换 | 通过 | 由 `chapter.md:107-149` 和推导 `04_bloch_fourier.md:93-147` 的正号 Bloch 和及 \(H_{ab}(\mathbf D)=\langle a\mathbf0|\hat H|b\mathbf D\rangle\)，正确得到 \(H(\mathbf k)=\sum_{\mathbf R}e^{+i\mathbf k\cdot\mathbf R}H(\mathbf R)\)；`chapter.md:157-169` 和推导 `:153-175` 用有限正交关系得到带 \(1/N\) 的负号逆变换。 |
| 4. 不同 \(\mathbf k\) 块解耦 | 通过 | 推导 `04_bloch_fourier.md:120-138` 保留了 \(\mathbf R,\mathbf R'\) 两个指标，令 \(\mathbf D=\mathbf R'-\mathbf R\) 后，对 \(\mathbf R\) 的和产生 \(\delta_{\mathbf k,\mathbf k'}\)，剩余指数为 \(e^{+i\mathbf k\cdot\mathbf D}\)。没有静默交换 bra/ket 或丢失 \(1/N\)。 |
| 5. 实空间厄米关系与 \(H(\mathbf k)\) Hermiticity | 通过 | 推导 `04_bloch_fourier.md:181-207` 从复共轭后的 bra/ket 交换和整体平移 \(-\mathbf R\) 得到 \(H_{ab}(\mathbf R)^*=H_{ba}(-\mathbf R)\)，并经 \(\mathbf D=-\mathbf R\) 重标记得到 \(H(\mathbf k)^\dagger=H(\mathbf k)\)。指标交换与负平移均未遗漏。 |
| 6. \(S(\mathbf k)\) Hermitian 与正定性 | 通过 | `chapter.md:209-217`、阶段 B 约定 `stageB_conventions.md:88` 和 Q4-06 解答明确区分共轭配对推出的 Hermiticity 与广义 Hermitian-definite 问题另需的 \(S(\mathbf k)\succ0\)；同时给出最小特征值或 Cholesky 检查入口。 |
| 7. \(\mathbf k+\mathbf G\) 的规范边界 | 通过，见 N02 | Cell-phase 基严格满足 \(|\phi_{a,\mathbf k+\mathbf G}\rangle=|\phi_{a\mathbf k}\rangle\)；中心规范多出 \(e^{i\mathbf G\cdot\boldsymbol\tau_a}\)。矩阵以对角幺正合同变换相联系而广义谱周期。关于数值本征矢还可补充任意带相位和简并子空间混合限定，见 N02。 |
| 8. \(U(\mathbf k)\) 同步变换与单边失败 | 通过 | `chapter.md:223-253`、推导 `04_bloch_fourier.md:223-251` 和 Q4-08 均正确采用 \(\bar\Phi=\Phi U\)、\(\bar H=U^\dagger HU\)、\(\bar S=U^\dagger SU\)、\(\bar c=U^{-1}c\)。固定数值例证明同步变换保持谱，只变 \(H\) 时最大谱差为 \(0.0822892958\)。 |
| 9. 有限离散、采样、截断和无限积分测度 | 通过 | `chapter.md:171-187`、`stageB_conventions.md:90-99,130-132` 和推导 `04_bloch_fourier.md:253-266` 区分完整有限 DFT、改变 \(\mathcal K_N\) 的采样、删除 \(H(\mathbf R)\) 的截断和 \(N_i\to\infty\) 的积分极限；积分测度 \(V_{\mathrm{BZ}}^{-1}=\Omega_c/(2\pi)^d\) 正确。 |
| 10. 四个例题和固定 Python 断言 | 通过，见 N01、N03 | 例 4.1 的色散、例 4.2 的 DFT 数值、例 4.3 的广义谱及单边失败值、例 4.4 的两种规范关系均正确。固定环境运行八个现有断言全部通过；例 4.3 的展示式有两处转义排版缺陷，例 4.4 尚无独立断言。 |
| 11. 十道题与十份解答 | 通过 | 自动提取的问题编号与解答编号均严格为 `01,02,03,04,05,06,07,08,09,10`，无缺号、重号或错序；逐题内容与题意对应。 |
| 12. 来源—推导映射与证据边界 | 通过 | `sources.md:10-21` 将 FND-01、DH-01、实空间厄米关系、阶段 B 约定和教学模型映射到正文/推导小节；正文和推导在具体公式链附近使用 `DIRECT_DERIVATION`，例题明确为 `PEDAGOGICAL`。DH-01 只支持对象接口，不被用于声称本章正号相位是唯一外部约定。 |
| 13. M8/M9 授权边界 | 通过 | 被审材料只使用解析链、有限循环晶格和合成矩阵；没有安装 DeepH、下载正式训练数据、生成 DFT 标签、选择材料体系/DFT 后端/软件版本，也没有声称具体软件格式或真实材料参数。随机批量测试明确留给 M4-07。 |
| 14. 控制字符、链接、表格、定界符与 MathML | 通过，见 N01 | 九文件控制字符为 0；10 个活动本地链接全部存在；Pandoc 实际解析 8 个表格；行内 \(\backslash(\cdots\backslash)\) 为 283/283，展示 \(\backslash[\cdots\backslash]\) 为 96/96；指定 Pandoc 命令九文件均成功且 MathML 节点均大于 0。Pandoc 不会把裸 `qquad` 判为 warning，故 N01 由实际 MathML 语义检查发现。 |

## 4. 解析与数值复算

使用工作包固定解释器：

```text
Python 3.12.13
NumPy 2.3.5
SciPy 1.18.0
```

独立逐句复算 `examples.md:118-172`，全部八个 `assert` 通过。关键结果如下。

| 检查 | 独立复算结果 | 文本结果 |
|---|---:|---:|
| 正反 Fourier 最大块误差 | \(4.0412728104402656\times10^{-16}\) | \(4.1\times10^{-16}\) |
| 正确 \(H(k)\) 最大虚部 | \(1.2212453270876722\times10^{-15}\) | 解答约 \(1.3\times10^{-15}\) |
| 同号逆变换最大误差 | \(0.23365100538519054\) | 约 \(0.233651\) |
| 缺失 \(-1\) 块后的最大虚部 | \(0.2779946475932199\) | 约 \(0.277995\) |
| 原矩阵束广义谱 | \((0.9197616007,\ 2.0385717326)\) | \((0.91976160,\ 2.03857173)\) |
| 同步规范变换后的最大谱差 | \(8.881784197001252\times10^{-16}\) | 低于 \(10^{-12}\) |
| 只变 \(H\) 的错误谱 | \((0.8840748992,\ 2.1208610284)\) | \((0.88407490,\ 2.12086103)\) |
| 只变 \(H\) 的最大谱差 | \(0.08228929584172562\) | 约 \(0.0822893\) |

例 4.1 的解析式

\[
H(k)=\varepsilon+t e^{i(k+\varphi)}+t e^{-i(k+\varphi)}
=\varepsilon+2t\cos(k+\varphi)
\]

与冻结的正号 Fourier 变换一致。例 4.4 的基变换也可直接由

\[
U(\mathbf k+\mathbf G)=U(\mathbf k)
\operatorname{diag}\!\left(e^{i\mathbf G\cdot\boldsymbol\tau_a}\right)
\]

推出；该解析关系正确，但当前嵌入式脚本尚未对其作数值断言，见 N03。

## 5. 自动格式与结构核验

Pandoc 版本为 3.6.4。对九个文件逐一执行以下命令，文件路径附在命令末尾：

```powershell
pandoc --from=markdown+tex_math_single_backslash+tex_math_double_backslash --to=html5 --mathml --fail-if-warnings <file>
```

结果如下。

| 文件 | 退出码 | 实际 MathML 节点数 |
|---|---:|---:|
| `sources.md` | 0 | 1 |
| `outline.md` | 0 | 10 |
| `chapter.md` | 0 | 72 |
| `examples.md` | 0 | 29 |
| `04_bloch_fourier.md` | 0 | 57 |
| `problem/readme.md` | 0 | 37 |
| `solution/readme.md` | 0 | 62 |
| `stageB_conventions.md` | 0 | 40 |
| `M4_stageB_work_package.md` | 0 | 71 |

九文件共生成 379 个实际 `<math>` 节点，每个文件均大于 0。控制字符扫描为 0；活动本地链接检查为 10/10 有效；Pandoc AST 实际解析表格 8 个，其中资料包 2 个、解答 1 个、工作包 5 个。公式定界符成对且没有混入 `$$` 展示式。

## 6. `BLOCKING`

**无。剩余 `BLOCKING` 数：0。**

未发现 Fourier 相位闭合错误、bra/ket 指标方向错误、厄米指标交换缺失、将 Hermitian overlap 误判为正定、规范变换只作用一侧却声称等价、有限/无限测度混写、习题缺解答或来源越权等会阻止本章进入下一门控的问题。

## 7. `NON_BLOCKING`

### M4-C4-N01：例 4.3 两处 `\qquad` 丢失反斜杠，实际 MathML 把它解析为变量字母

**位置与证据。** `examples.md:78` 为 `0.91976160,qquad2.03857173.`，`examples.md:84` 为 `0.88407490,qquad2.12086103,`。指定 Pandoc 命令虽以退出码 0 完成，但实际 MathML 分别产生连续的 `<mi>q</mi><mi>q</mi><mi>u</mi><mi>a</mi><mi>d</mi>`，而不是数学间距。数值本身经固定 Python 复算正确，因此该缺陷没有改变广义谱或失败阈值，但当前渲染语义不是预期公式。

**最小修复要求。** 将两处分别改为 `0.91976160,\qquad 2.03857173.` 和 `0.88407490,\qquad 2.12086103,`，然后重跑本报告所列 Pandoc 命令，并检查对应 MathML 不再含表示 `qquad` 五个字母的 `<mi>` 序列。

### M4-C4-N02：\(k+G\) 处的系数关系尚未显式包含本征矢相位和简并子空间自由度

**位置与证据。** `chapter.md:255` 正确指出系数逐元素周期性依赖规范；`examples.md:106` 进一步称“同一带的轨道系数在两个端点相差轨道依赖相位”；Q4-09 解答 `solution/readme.md:149` 称中心规范的系数由对角幺正规范联系。对于固定的同一抽象态和人为对齐的本征矢相位，该关系正确；但数值对角化输出还允许每条非简并带具有任意整体相位，简并处允许简并子空间内的幺正混合。现有正文在 `chapter.md:70` 提到简并共同本征基不唯一，却没有在端点系数比较处把该限定重新接上。

**最小修复要求。** 在 `chapter.md:255`、`examples.md:106` 和 Q4-09 解答附近说明：先按 \(D_G=\operatorname{diag}(e^{i\mathbf G\cdot\boldsymbol\tau_a})\) 对齐基规范；非简并本征矢还需对齐任意带相位；简并处只能比较投影算符或先对齐简并子空间，不能要求逐带逐元素相等。

### M4-C4-N03：例 4.4 的解析规范关系尚未进入嵌入式固定 Python 断言

**位置与证据。** `examples.md:108-174` 的固定脚本含八个显式断言，覆盖例 4.1—4.3 的 Fourier 重建、正确虚部、同号逆变换失败、缺共轭块失败、Hermiticity、同步规范谱不变和单边失败；脚本没有构造倒格矢 \(G\)，也没有断言例 4.4 的 \(U(k+G)=U(k)D_G\)、中心规范矩阵合同关系或 cell-phase 严格周期性。例 4.4 的解析式本身正确，且 Q4-09 已有对应推导，故不阻塞本章内容门控。

**最小修复要求。** 在现有固定脚本中增加一个确定性 \(G=2\pi/a\) 样例，至少断言 cell-phase 因子在 \(R\in\mathbb Z a\) 上不变、`U(k+G) == U(k) @ D_G`，以及由此得到的中心规范矩阵满足对应合同关系；容差应与现有复双精度断言一致。

## 8. 最终门控判定

| 判定项 | 结果 |
|---|---|
| 核心数学链条 | 通过 |
| 四例解析/数值正确性 | 通过 |
| 固定 Python 现有断言 | 8/8 通过 |
| 十道题与十份解答 | 10/10 对应 |
| 来源—推导与证据边界 | 通过 |
| M8/M9 授权边界 | 通过 |
| Pandoc `--fail-if-warnings` | 9/9 通过 |
| 实际 MathML | 9/9 文件节点数大于 0 |
| 剩余 `BLOCKING` | **0** |
| 是否允许 `M4-04 COMPLETED` | **是** |
| 是否允许 `M4-05 READY` | **是** |

最终判定以本报告第 2 节固定快照为对象。N01—N03 应当进入后续修订清单，但不构成保持 `M4-04 REVIEW` 的理由；若主 agent 在更新状态前修改了任一固定送审文件，应重新核验相应哈希和受影响结论。
