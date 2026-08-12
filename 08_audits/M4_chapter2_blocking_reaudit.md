# M4-02 第 2 章阻塞项独立定点复核

## 1. 复核对象与结论

- 复核日期：2026-08-03
- 复核角色：独立子 agent
- 原审计：`08_audits/M4_chapter2_independent_content_audit.md`
- 定点范围：`M4-C2-B01`（公式转义与可渲染性）、`M4-C2-B02`（一般矩阵形状契约），并检查原通过项是否回归
- 修改边界：本次复核只新增本报告，未修改被审计材料或原审计报告
- 总结论：**两项 `BLOCKING` 全部关闭，无新增 `BLOCKING`。**

因此，当前证据允许将 `M4-02` 标记为 `COMPLETED`，并将 `M4-03` 标记为 `READY`。M4-07 仍需按工作包固化自动测试和 JSON 证据，但不阻塞第 3 章材料建设。

## 2. `M4-C2-B01` 复核：公式转义、控制字符与实际渲染

### 2.1 控制字符与定界符扫描

逐字符检查以下五个核心文件：

1. `03_textbook/chapters/02_quantum_states_operators_matrices/chapter.md`
2. `03_textbook/chapters/02_quantum_states_operators_matrices/examples.md`
3. `04_derivations/stageB/02_basis_representation.md`
4. `06_exercises/02-stageB/02_basis/problem/readme.md`
5. `06_exercises/02-stageB/02_basis/solution/readme.md`

结果如下：

| 文件 | 非 CR/LF 控制字符 | `\(` | `\)` | 前缀最小余额 | 最终余额 |
|---|---:|---:|---:|---:|---:|
| `chapter.md` | 0 | 63 | 63 | 0 | 0 |
| `examples.md` | 0 | 14 | 14 | 0 | 0 |
| `02_basis_representation.md` | 0 | 23 | 23 | 0 | 0 |
| `problem/readme.md` | 0 | 32 | 32 | 0 | 0 |
| `solution/readme.md` | 0 | 41 | 41 | 0 | 0 |

不存在 U+0008 退格、U+0009 制表符或其他异常控制字符。按文本顺序检查全部 `\(`/`\)` token，任何位置均未出现先闭后开的负余额，文件末尾余额均为 0。

针对原审计列出的命令执行反向扫描，未发现未转义的 `boldsymbol`、`theta`、`hat`、`langle`、`mathcal`、`pm`；扩大到 `rangle`、`mathbb`、`dagger`、`sqrt` 等公式命令后，未发现公式正文中的命令丢失。原错误字面量 `(pm\sqrt5)` 已不存在，例题与解答均恢复为有效的 `\(\pm\sqrt5\)` 或等价公式。

### 2.2 Pandoc 实际渲染

使用 Pandoc 3.6.4 对五个核心文件逐一执行：

```powershell
pandoc -f 'markdown+tex_math_single_backslash' -t html5 --mathml --fail-if-warnings <file>
```

五次转换退出码均为 0，且 `--fail-if-warnings` 未触发。该路径把 TeX 数学实际转换为 MathML，而不只是检查 Markdown 链接或字符计数；因此能够确认当前行内与块级公式可被 Pandoc 数学解析器接受。

**判定：`M4-C2-B01` 关闭。**

## 3. `M4-C2-B02` 复核：一般形状与乘法相容性

正文已在首次建立有限基表示时明确声明：

\[
c\in\mathbb C^{M\times1},\qquad
H,S\in\mathbb C^{M\times M},
\]

并把 \(\boldsymbol\Phi\) 说明为由 \(M\) 个 ket 构成的有序基对象，等价地视为从 \(\mathbb C^{M\times1}\) 到所选子空间的线性映射。正文同时给出最小相容性检查

\[
Hc,Sc\in\mathbb C^{M\times1}.
\]

谱分解处已声明

\[
V=(v_1,\ldots,v_M)\in\mathbb C^{M\times M},
\qquad v_n\in\mathbb C^{M\times1},
\]

投影本征方程处另声明 \(c_n\in\mathbb C^{M\times1}\)。基变换处声明

\[
A\in\mathbb C^{M\times M},\qquad
c,c'\in\mathbb C^{M\times1},
\]

并明确检查 \(Ac'\) 与 \(A^{-1}c\) 的乘法形状。由此，\(H'=A^\dagger H A\)、\(S'=A^\dagger S A\)、\(V^\dagger H V\) 和 \(Hc_n=E_nc_n\) 的一般维数均可直接核对，不再依赖读者从二维例题反推。

**判定：`M4-C2-B02` 关闭。**

## 4. 原 `NON_BLOCKING` 项复核

### 4.1 `M4-C2-N01` 已落实

章节状态已改为“正文、D-B01 推导、二能级例题、分层练习和参考解答均已形成，等待阻塞项定点复核”，不再使用“尚需形成参考解答”的过时时态。

正文 5 道检查题已经显式映射为：检查题 1—5 分别对应 Q2-02、Q2-03、Q2-04、Q2-05、Q2-07，并给出参考解答的稳定路径。自学者不再需要仅凭题意猜测答案位置。

### 4.2 `M4-C2-N02` 保持后续实施项

固定 Python 数值复算仍应在 M4-07 固化为自动测试和 JSON 证据。该事项的任务归属和验收边界未改变，不构成 M4-02 阻塞项。

## 5. 回归检查

### 5.1 数学与算术

使用工作包固定解释器

`C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`

在 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0 下重新计算，得到：

| 指标 | 复核结果 |
|---|---|
| 原始谱 | \((-2.23606797749979,\ 2.23606797749979)\) |
| 原始、相位翻转、重排后的期望值 | 均为 \(0\) |
| 相位翻转与重排后的谱 | 均与原始谱相同 |
| \(c'^\dagger S'c'\) | \(0.9999999999999998\) |
| \(c'^\dagger H'c'\) | \(0\) |
| 非幺正变换后的正确广义谱 | \((-2.23606797749979,\ 2.23606797749979)\) |
| 忽略 \(S'\) 的错误普通谱 | \((-1.3781230493125982,\ 3.6281230493125984)\) |
| Q2-02 的两个 \(X\) 期望值 | \((0.9999999999999998,\ 0)\) |
| Q2-03 Hermiticity 残差 | \(0\) |

对象层级、整体/相对相位、Hermitian 与定义域边界、有限投影、列基与系数方向、合同变换、非幺正 overlap、期望值/广义谱不变、行列式证明均未出现内容回归。

### 5.2 题解、来源与链接

练习文件仍有 Q2-01—Q2-08 共 8 题，解答文件仍有同编号 8 个答案，编号集合一一对应。各题的机制解释与失败诊断仍在。

`sources.md`、`outline.md`、阶段 B 统一约定、工作包、FND-06 来源登记和三个 PDF 快照的哈希均与原审计时相同。FND-06 页码与论断强度没有回归。检查本次范围内 12 个 Markdown 文件的 6 个活动本地链接，断链数为 0；外部 URL 不计入本地断链判定。

## 6. 最终门控判定

| 项目 | 判定 |
|---|---|
| `M4-C2-B01` | **关闭** |
| `M4-C2-B02` | **关闭** |
| 新增 `BLOCKING` | 无 |
| `M4-C2-N01` | 已落实 |
| `M4-C2-N02` | 保留至 M4-07，不阻塞 M4-02 |
| 数学、算术与失败样例回归 | 通过 |
| Q2-01—Q2-08 题解对应 | 通过 |
| 来源、快照哈希与本地链接 | 通过 |
| Pandoc MathML 实际渲染 | 5/5 通过 |

最终结论：**允许 `M4-02 COMPLETED / M4-03 READY`。**

## 7. 输入文件 SHA-256

| 文件 | SHA-256 |
|---|---|
| `08_audits/M4_chapter2_independent_content_audit.md` | `F6D140A5DCBDC86D7A9879AACDAD6181C0E2C3E40B70FC60B23134A754D3D76E` |
| `03_textbook/chapters/02_quantum_states_operators_matrices/sources.md` | `4CCC8273FFC9936B8BEC76F2994E0D443E3CDFCD5C29BB12AEDD210C3396220B` |
| `03_textbook/chapters/02_quantum_states_operators_matrices/outline.md` | `209405686CAB6C6742A1296E78223CD1D2DCDBB9B0BE283323D98660CB704BFD` |
| `03_textbook/chapters/02_quantum_states_operators_matrices/chapter.md` | `669CBAC8FC9E19847BC0A0564BC7AF3F687EC3CE774E14DC7C4AC11FE878550A` |
| `03_textbook/chapters/02_quantum_states_operators_matrices/examples.md` | `2EC9C4EAA847DCEA7742E10D9C29EFFCA2943CB0B5B7F9E96C3D25DBFF495C55` |
| `04_derivations/stageB/02_basis_representation.md` | `D7AEC07F186E59FC0862E54BE14CAC82678F32AB7B2BAE02CA7913E02B7786B9` |
| `06_exercises/02-stageB/02_basis/problem/readme.md` | `FB25D9B7DACD1E93F5FCACA2A3E492524EAC3FEF71B803BE9D671B84DF20C83A` |
| `06_exercises/02-stageB/02_basis/solution/readme.md` | `ACE6C6DF332625E0BC9A882B7EB70A856BD34BE4B3193E5BF30C63E12366F320` |
| `03_textbook/stageB_conventions.md` | `F13A9E5E6FC3FC51D18E6E361B5C0CB84A2FD56FE2431915079CE2693E9F7AAE` |
| `08_audits/M4_stageB_work_package.md` | `3DFE3F0023E77CA340089B9D06940EAD62EFEE4123FC043CFBE0C7AFA7D75462` |
| `08_audits/M4_stageB_work_package_blocking_reaudit.md` | `3AB104D6AFBCDB3BC903A18DD2E8C25CFAD1342985519C9B8C7E54FC71011409` |
| `01_sources/README.md` | `96CDEC62825A7C4A69F8D481AF05D09A58667B3D6EF66BDD52881EC2CD38C93A` |
| `01_sources/documentation/mit_8_04_2016_lecture06.pdf` | `94BDB289652D5AD03F217F451BA144519884F0359414F1E2530E3015A54FA5DD` |
| `01_sources/documentation/mit_8_04_2016_lecture08.pdf` | `211EC0D365577E50D59D325F8285DCBB48A364AC5C85E95D2DF607A720BF54CC` |
| `01_sources/documentation/mit_8_04_2016_lecture09.pdf` | `CDE42766358A0AC3A2E862273522F35B1A4A9652145FE9AB563706AB9CF1C001` |
