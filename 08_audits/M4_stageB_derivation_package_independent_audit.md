# M4-06 阶段 B 解析推导包独立内容审计

## 1. 审计结论

审计日期：2026-08-04。

结论：`PASS`。本次独立审计未发现 `BLOCKING`。D-B01—D-B06 均能从统一索引定位到条件明确、代数闭合的推导；矩阵束合同变换、正交化约化、Hermitian-definite 性质、有限 Fourier 对、实空间厄米关系及实空间到能带对象链在被审文件之间一致。一般可逆合同变换与幺正变换下的残差边界已经被正确区分。

因此允许：

- M4-06 由 `REVIEW` 转为 `COMPLETED`；
- M4-07 转为 `READY` 并开始固定数值实现、环境、批量测试和失败样例；
- 不得把本报告解释为 M4-07 自动测试已经完成，也不得据此提前通过 M4-09 阶段 B 总门控。

## 2. 审计范围与判定口径

核心被审对象为：

- `04_derivations/stageB/README.md`；
- `04_derivations/stageB/02_basis_representation.md`；
- `04_derivations/stageB/03_generalized_eigen.md`；
- `04_derivations/stageB/04_bloch_fourier.md`；
- `04_derivations/stageB/09_realspace_to_bands.md`；
- `03_textbook/stageB_conventions.md`；
- `08_audits/M4_stageB_work_package.md`。

同时只读核对四章 `sources.md` 的来源—推导定位表，用于判断 FND-01—FND-06、DH-01、`DIRECT_DERIVATION` 与 `PEDAGOGICAL` 的证据边界。M4-07 尚未建设统一代码目录、固定 JSON 输出与批量测试不构成本次阻塞；本次只检查解析推导包是否正确把这些数值验收留给 M4-07。

## 3. D-B01—D-B06 逐项判定

| ID | 判定 | 核查结果 |
|---|---|---|
| D-B01 | `PASS` | 从同一有限维子空间中的列基关系 \(\Phi'=\Phi A\) 逐步推出 \(c'=A^{-1}c\)、\(H'=A^\dagger HA\)、\(S'=A^\dagger SA\)，并验证物理范数和期望值不变。奇异 \(A\)、子空间改变及只变单个对象均被明确排除。矩阵元的合同变换未与线性映射坐标的相似变换混用。 |
| D-B02 | `PASS` | Gram 矩阵满足“基线性无关当且仅当 \(S\succ0\)”的双向证明；投影矩阵元和带 \(c^\dagger Sc=1\) 约束的复变量 Rayleigh 变分均导出 \(Hc=ESc\)。实谱、异值本征矢的 \(S\)-正交及简并子空间内的 \(S\)-正交化边界正确；\(S\) 奇异、非 Hermitian 或不定时未误用 Hermitian-definite 结论。 |
| D-B03 | `PASS` | 对 \(S=LL^\dagger\) 使用 \(y=L^\dagger c\)、\(c=L^{-\dagger}y\)，得到 \(L^{-1}HL^{-\dagger}y=Ey\)；对称正交化使用 \(y=S^{1/2}c\)、\(c=S^{-1/2}y\)。两条逆映射、Hermiticity 和 \(S\)-归一化均闭合。正文明确要求三角求解而非默认显式逆，并说明删除小特征值方向会改变有效子空间。 |
| D-B04 | `PASS` | 一般可逆 \(A\) 下，\(H,S,c\) 同步变换；广义方程和 \(\det(H'-ES')=|\det A|^2\det(H-ES)\) 的证明正确，保留代数重数。README 与第 9 章明确指出残差向量按 \(r'=A^\dagger r\) 协变，但任意 Euclidean 矩阵范数或归一化残差标量不由一般可逆变换保持；只有 unitary 特例保持当前 Euclidean 归一化残差。 |
| D-B05 | `PASS` | 从冻结定义 \(H_{ab}(R)=\langle\phi_{a0}|\hat H|\phi_{bR}\rangle\) 逐指标推出 \(H_{ab}(R)^*=H_{ba}(-R)\)，即 \(H(R)^\dagger=H(-R)\)；\(S\) 同理。再通过 \(R\mapsto-R\) 重标记推出每个 \(k\) 上 Hermiticity。材料正确指出非零 \(R\) 块无需自身 Hermitian，且 Hermiticity 不推出 \(S(k)\succ0\)。 |
| D-B06 | `PASS` | 有限 BvK 平移群和对偶 \(k\) 网格的角色正交关系由几何级数推出；cell-phase Bloch 和与冻结的 bra/ket 方向给出 \(H(k)=\sum_R e^{+ikR}H(R)\)，逆式为 \(H(R)=N^{-1}\sum_k e^{-ikR}H(k)\)，\(S\) 全程同步。中心规范采用 unitary \(U(k)\) 同步作用于 \(H,S,c\)。材料严格区分有限离散恒等式、无限 BZ 积分极限、有限采样与实空间截断，并闭合到逐 \(k\) Hermitian-definite 求解、残差、逆变换和能带误差边界。 |

## 4. 专项数学核查

### 4.1 Hermitian-definite 与误差边界

第 3 章的 Cholesky 和对称正交化矩阵方向正确，且标准问题均为 Hermitian。病态性部分只从较小的 \(\lambda_{\min}(S)\) 推出误差放大风险，没有把较大条件数误写成某条能带必然按固定速率恶化。

结构保持后向扰动

\[
\Delta H=pu^\dagger+up^\dagger-\alpha uu^\dagger
\]

满足 \(\Delta H=\Delta H^\dagger\)、\(\Delta H\widehat c=-q\) 及 \(\|\Delta H\|_2\le 3\|q\|_2/\|\widehat c\|_2\)；Rayleigh 商情形的系数可降为 2。经 \(S^{-1/2}\) 约化后的本征值包含界、谱隙角度界及含 \(\sqrt{\kappa_2(S)}\) 的原系数相对界，其条件和失效情形均已声明。近简并时转向能带簇或不变子空间的说明正确。

### 4.2 一般可逆与幺正残差边界

被审材料没有重复此前“任意可逆变换保持 Euclidean 归一化残差”的错误。独立数值复算使用

\[
H=\operatorname{diag}(0,2),\quad S=I,\quad E=0,\quad c=(1,1)^T,
\quad A=\operatorname{diag}(0.1,1),
\]

得到变换前后的归一化残差分别为 `0.7071067811865475` 与 `0.09950371902099892`，与 README 和第 9 章当前边界一致。轨道重排、纯相位、中心相位和 unitary 子空间混合属于 Euclidean 范数不变的特例。

### 4.3 Fourier、Hermiticity 与能带对象链

主动平移本征值 \(e^{-ik\cdot R}\) 与坐标 Bloch 条件 \(\psi(r+R)=e^{+ik\cdot R}\psi(r)\) 的符号差异解释正确。由 Bloch 和展开得到的正变换、由有限角色正交关系得到的逆变换及 \(1/N\) 位置均与统一约定一致。第 9 章对 \(H(R),S(R)\rightarrow H(k),S(k)\rightarrow E_n(k)\) 的链条没有越过来源边界，也没有把只保存本征值误写为足以反演矩阵块。

## 5. 来源、教学边界与 M4-07 分工

四章 `sources.md` 将基础对象和算法类别分别锚定到 FND-01—FND-06，将原始 DeepH 对象链接口限定到 DH-01 第 375—376 页，并把定义后的代数步骤标为 `DIRECT_DERIVATION`。解析/合成模型、条件数扫描、截断演示和故障注入均标为 `PEDAGOGICAL`，未外推成真实材料统计规律、软件字段或现代 DeepH 实现事实。

`04_derivations/stageB/README.md` 明确把固定 Python/NumPy/SciPy 环境、统一容差、随机种子、JSON 字段、批量测试和失败断言留给 M4-07。因此，M4-07 尚未存在其完整代码产物不会阻塞 M4-06；反之，本报告也不为这些尚未执行的数值验收背书。

## 6. 非阻塞项

### M4-D-N01：完整 \(S\)-正交本征基的存在性目前依赖标准 Hermitian 谱定理的隐式调用

`03_generalized_eigen.md` 第 5—7 节的结论是正确的：正交化后的标准矩阵 Hermitian，因此存在完整正交本征基，逆映射后得到完整 \(S\)-正交本征基。当前材料推导了实谱、异值正交、简并子空间正交化和两种约化，但没有用一句话显式连接“标准 Hermitian 谱定理”与“完整本征基存在”。这不改变任何公式或本次门控结论，建议后续编辑时补出该连接，以降低初学者把逐个归一化误当作完备性证明的风险。

### M4-D-N02：中心规范段落中的“残差”宜显式限定为 unitary 情形

`04_bloch_fourier.md` 第 7 节的 \(U(k)\) 是对角 unitary，因此其“同步变换保持……残差”在当前语境下成立。README 第 4 节及 `09_realspace_to_bands.md` 第 6 节已准确区分一般可逆和 unitary 情形。建议后续把该处简写改为“因当前 \(U(k)\) 为 unitary，Euclidean 归一化残差也保持”，以避免脱离上下文阅读时被误推广。此项不构成数学错误。

## 7. 自动核查命令与实际结果

### 7.1 本地 Markdown 链接与控制字符

对七个核心被审文件解析 Markdown 本地链接并相对其所在目录解析路径，同时扫描除 TAB、LF、CR 外的 C0 控制字符及 DEL。实际结果：

```text
LINKS=15 BROKEN=0
CONTROL=0
```

### 7.2 公式定界与实际 MathML 节点

执行命令模板：

```powershell
pandoc <file> --from=markdown+tex_math_single_backslash+tex_math_double_backslash --to=html5 --mathml --fail-if-warnings
```

实际结果：七个文件退出码均为 0；实际 `<math>` 节点分别为 `46, 34, 139, 57, 56, 40, 71`，合计 `443`。公式定界符计数如下：

```text
README.md                         INLINE=42/42  DISPLAY=4/4
02_basis_representation.md       INLINE=23/23  DISPLAY=11/11
03_generalized_eigen.md          INLINE=85/85  DISPLAY=54/54
04_bloch_fourier.md              INLINE=31/31  DISPLAY=26/26
09_realspace_to_bands.md         INLINE=43/43  DISPLAY=13/13
stageB_conventions.md            INLINE=28/28  DISPLAY=12/12
M4_stageB_work_package.md        INLINE=70/70  DISPLAY=1/1
```

### 7.3 独立数值复算

使用固定环境：

```text
C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
Python 3.12.13, NumPy 2.3.5, SciPy 1.18.0
random seed = 20260804
```

对固定种子的复 Hermitian-definite 矩阵束、一般可逆合同变换、两种正交化及有限 \(N=8\) Fourier 对执行独立复算，得到：

```text
generalized_spectrum_diff                 3.985700658404312e-14
S_orth_residual                           2.14596793049778e-15
cholesky_spectrum_diff                    1.1102230246251565e-15
symmetric_spectrum_diff                   4.6629367034256575e-15
nonunitary_normalized_residual_before     0.7071067811865475
nonunitary_normalized_residual_after      0.09950371902099892
fourier_reconstruction_error              3.397933197783835e-15
k_hermiticity_error                       3.1216028465745846e-14
```

这些数值只用于独立交叉核查解析公式，不替代 M4-07 冻结测试套件及其门控容差。

## 8. SHA-256 审计快照

```text
EB7B76E52FF9ABB3FBC1CD17A4605DFFC115D7F400EA5342DFCF1D932C8EBD69  04_derivations/stageB/README.md
0859F50F9F84E31139FC8925A892DD817E57233F65D0552B1081AA828147D808  04_derivations/stageB/02_basis_representation.md
6AFF3009B5E0DDFD596D20B70C6110190EB5FCDE31751A6817991DF1564A36CC  04_derivations/stageB/03_generalized_eigen.md
AF4C4D07DE175324271DAAED14864CAFA521720C2DCB3D4E4FFABD186434BAA4  04_derivations/stageB/04_bloch_fourier.md
29073B18123E83ABE171B5C57ADEA0A99117EB4932F67D6FE3F834746CA8C43D  04_derivations/stageB/09_realspace_to_bands.md
66A135C38DBA8536D88701ED85DEBAE51D60A3E48CD0D09DFBBB463A2240B464  03_textbook/stageB_conventions.md
90D91B0ECA0D0317954034A9985DBA39FC1F0420F0BA8E0C111EEB8BBB242BCA  08_audits/M4_stageB_work_package.md
```

最终判定：M4-06 `PASS`，`BLOCKING=0`，允许 `M4-06 COMPLETED` 与 `M4-07 READY`。两项非阻塞建议只改善显式性，不要求阻塞当前依赖链。
