# M4-C4-N01—N03 独立定点复核

## 1. 复核结论

- 复核日期：2026-08-04
- 复核角色：独立子 agent
- 复核范围：`M4_chapter4_independent_content_audit.md` 所列 M4-C4-N01—N03；只检查对应修订及其回归风险
- 修改边界：本次复核只新增本报告，未修改任何被审计材料、`README`、工作包或进度台账
- M4-C4-N01：**关闭**
- M4-C4-N02：**关闭**
- M4-C4-N03：**关闭**
- 新增 `BLOCKING`：**0**
- 门控判定：**维持 `M4-04 COMPLETED / M4-05 READY`。**

三项修订均达到原独立审计给出的最小修复要求。两处 `\qquad` 已产生实际 MathML 间距节点，不再产生 `q`、`q`、`u`、`a`、`d` 变量序列；正文、例题和 Q4-09 解答均已补齐 \(D_G\) 基规范、非简并带整体相位以及简并子空间投影/对齐边界；固定 Python 脚本新增五个 \(k+G\) 断言，连同原八个断言共 13/13 通过。没有发现修订导致的相位、合同变换、Hermiticity 或广义谱回归。

## 2. 修订快照

三份修订文件及四份声明不变的固定送审文件，其 SHA-256 均与复核任务给定值匹配。

| 文件 | 复核时 SHA-256 | 结果 |
|---|---|---|
| `03_textbook/chapters/04_periodicity_bloch_reciprocal/chapter.md` | `87CCA024540FAD83B3A361D6DCA3C146C755D9DA2B8F78E33E18FFE96640C536` | 修订快照匹配 |
| `03_textbook/chapters/04_periodicity_bloch_reciprocal/examples.md` | `B00858D4C8B4D8B065B2CE37455D0412F21917322C8E6D7D584C0D36CC2A02F4` | 修订快照匹配 |
| `06_exercises/02-stageB/04_bloch_fourier/solution/readme.md` | `87914B10D9B66B31FD9C26BB61A216410A4033F9AA3A44F8D5906B6CC1396D77` | 修订快照匹配 |
| `03_textbook/chapters/04_periodicity_bloch_reciprocal/sources.md` | `FE3B31F4CE7FD46ECF83189BE4A1CE9BDE4960C0EBDDB749F81D90E2DC64A713` | 未变快照匹配 |
| `03_textbook/chapters/04_periodicity_bloch_reciprocal/outline.md` | `AB169D1B55DB1C2A08430D08E9EB562BAC720FBEC90EC7953D1484909AF6A736` | 未变快照匹配 |
| `04_derivations/stageB/04_bloch_fourier.md` | `AF4C4D07DE175324271DAAED14864CAFA521720C2DCB3D4E4FFABD186434BAA4` | 未变快照匹配 |
| `06_exercises/02-stageB/04_bloch_fourier/problem/readme.md` | `639302138F7372F9C0EB683B6E61D0A908D6337066BAC39C93D250979C035F73` | 未变快照匹配 |

上下文文件 `03_textbook/stageB_conventions.md` 和 `08_audits/M4_stageB_work_package.md` 的审计时 SHA-256 仍分别为 `66A135C38DBA8536D88701ED85DEBAE51D60A3E48CD0D09DFBBB463A2240B464` 与 `C479CCE2F40C4865301329C3A61E297B6D7B768B09202C3867BDB6677A212E32`。

## 3. M4-C4-N01 定点复核

### 3.1 文本修订

`examples.md:78` 和 `examples.md:84` 现分别为：

```text
0.91976160,\qquad 2.03857173.
0.88407490,\qquad 2.12086103,
```

两处均已恢复反斜杠和数值间空格。

### 3.2 实际 MathML 语义

使用 Pandoc 3.6.4 和任务指定扩展实际转换后，两式的 MathML 主体分别包含：

```html
<mn>0.91976160</mn><mo>,</mo><mspace width="2.0em"></mspace><mn>2.03857173</mn>
<mn>0.88407490</mn><mo>,</mo><mspace width="2.0em"></mspace><mn>2.12086103</mn>
```

对转换结果检索连续序列

```html
<mi>q</mi><mi>q</mi><mi>u</mi><mi>a</mi><mi>d</mi>
```

命中数为 0。`examples.md` 的 Pandoc 退出码为 0，实际 `<math>` 节点数为 30。因此 N01 的文本和渲染语义均已修复，判定关闭。

## 4. M4-C4-N02 定点复核

修订已在三个要求位置形成一致边界：

- `chapter.md:255-261` 定义 \(D_G=\operatorname{diag}(e^{i\mathbf G\cdot\boldsymbol\tau_a})\)，要求系数比较先按 \(D_G\) 对齐基规范，并明确非简并带的任意整体相位与简并子空间内的幺正混合；简并处应比较投影算符或先对齐整个子空间。
- `examples.md:89-112` 先给出 cell-phase 严格周期性和中心规范的轨道相位，再以同一 \(D_G\) 说明基规范对齐；非简并和简并边界均被明确写入例题结论。
- Q4-09 解答 `solution/readme.md:149-155` 明确中心规范矩阵和系数由 \(D_G\) 联系，同时要求非简并带作整体相位对齐、简并处比较投影算符或对齐整个子空间，不再要求逐带逐元素相等。

上述表述与

\[
\bar\Phi_{\mathbf k+\mathbf G}=\bar\Phi_{\mathbf k}D_G,
\qquad
\bar H(\mathbf k+\mathbf G)=D_G^\dagger\bar H(\mathbf k)D_G,
\qquad
\bar S(\mathbf k+\mathbf G)=D_G^\dagger\bar S(\mathbf k)D_G
\]

一致。对固定同一抽象态，系数还需按逆基变换方向对齐；非简并本征矢的整体相位和简并子空间自由度已被单独区分。因此 N02 判定关闭。

## 5. M4-C4-N03 定点复核

### 5.1 固定环境与整段脚本执行

使用工作包固定解释器直接提取并执行 `examples.md:120-190` 的嵌入 Python 程序：

```text
Python 3.12.13
NumPy 2.3.5
SciPy 1.18.0
显式 assert 数：13
退出码：0
```

原八个断言全部继续通过。原指标无回归：Fourier 重建误差为 `4.0412728104402656e-16`，同号逆变换错误为 `0.23365100538519054`，缺共轭块最大虚部为 `0.2779946475932199`，同步规范谱差为 `8.881784197001252e-16`，只变 \(H\) 的谱差为 `0.08228929584172562`。

### 5.2 新增 \(k+G\) 断言

脚本固定 \(a=1\)、\(G=2\pi\)，新增并实际通过以下五项：

| 断言对象 | 最大误差 | 阈值 |
|---|---:|---:|
| \(e^{iGR}=1\)，\(R=0,\ldots,7\) | `1.7145055188062944e-15` | `1e-12` |
| \(U(k+G)=U(k)D_G\) | `4.0029660424867215e-16` | `1e-12` |
| \(\bar H(k+G)=D_G^\dagger\bar H(k)D_G\) | `2.220446049250313e-16` | `1e-12` |
| \(\bar S(k+G)=D_G^\dagger\bar S(k)D_G\) | `1.1102230246251565e-16` | `1e-12` |
| 广义谱相对原矩阵束不变 | `0.0` | `1e-12` |

五项断言同时覆盖 cell-phase 严格周期性、中心规范的 \(U\) 关系、\(H/S\) 同步合同变换和广义谱不变性。N03 判定关闭。

## 6. Pandoc 与回归检查

对原审计范围九个 Markdown 文件逐一执行：

```powershell
pandoc --from=markdown+tex_math_single_backslash+tex_math_double_backslash --to=html5 --mathml --fail-if-warnings <file>
```

九个文件退出码均为 0，实际 MathML 节点数依次为：

| 文件 | MathML 节点数 |
|---|---:|
| `sources.md` | 1 |
| `outline.md` | 10 |
| `chapter.md` | 73 |
| `examples.md` | 30 |
| `04_bloch_fourier.md` | 57 |
| `problem/readme.md` | 37 |
| `solution/readme.md` | 63 |
| `stageB_conventions.md` | 40 |
| `M4_stageB_work_package.md` | 71 |

每个文件的实际 MathML 节点数均大于 0；九文件中裸 `qquad` 字母 MathML 序列命中数均为 0。修订新增的 \(D_G\) 公式和说明未产生 Pandoc warning。

## 7. 最终判定

| 项目 | 复核结果 |
|---|---|
| M4-C4-N01 | **关闭** |
| M4-C4-N02 | **关闭** |
| M4-C4-N03 | **关闭** |
| 原八个 Python 断言 | **8/8 通过，无回归** |
| 新增 \(k+G\) 断言 | **5/5 通过** |
| 新增 `BLOCKING` | **0** |
| 是否维持 `M4-04 COMPLETED` | **是** |
| 是否维持 `M4-05 READY` | **是** |

本次定点复核未扩展为新的全章内容审计；结论只适用于第 2 节所列快照。若这些文件后续再次修改，应按受影响范围重新核验。
