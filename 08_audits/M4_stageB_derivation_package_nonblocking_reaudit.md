# M4-06 阶段 B 解析推导包非阻塞项定点复核

## 1. 复核结论

复核日期：2026-08-04。

结论：`PASS`。原独立审计报告中的 M4-D-N01 与 M4-D-N02 均已 `CLOSED`，修订未引入新的 `BLOCKING` 或非阻塞问题。维持以下状态判定：

- M4-06：`COMPLETED`；
- M4-07：`READY`。

本报告只复核两项定点修订，不扩大为 M4-07 数值实现或 M4-09 阶段总审计。

## 2. 复核范围

- 原报告：`08_audits/M4_stageB_derivation_package_independent_audit.md`；
- M4-D-N01 修订：`04_derivations/stageB/03_generalized_eigen.md` 第 7 节；
- M4-D-N02 修订：`04_derivations/stageB/04_bloch_fourier.md` 第 7 节；
- 一致性对照：`04_derivations/stageB/README.md` 第 4 节、`04_derivations/stageB/09_realspace_to_bands.md` 第 6 节。

## 3. 定点判定

### M4-D-N01：`CLOSED`

修订已显式说明：第 5 节的逐对正交关系本身不足以证明完整本征基存在；有限维 Hermitian 矩阵 \(\widetilde H_{\mathrm C}\) 或 \(\widetilde H_{\mathrm S}\) 由 Hermitian 谱定理具有 \(M\) 个正交完备本征矢。映射

\[
c=L^{-\dagger}y
\qquad\text{或}\qquad
c=S^{-1/2}y
\]

在 \(S\succ0\) 条件下可逆，因此把标准问题的完备基双射到原广义问题，并保持 \(C^\dagger SC=I\)。该补充的逻辑方向、映射方向和条件均正确，没有把简并本征矢的逐列唯一性作为前提，也没有削弱近简并时比较子空间的既有边界。

### M4-D-N02：`CLOSED`

修订已显式使用中心规范矩阵

\[
U(\mathbf k)^\dagger U(\mathbf k)=I
\]

并把结论限定为同步 unitary 合同变换。此时

\[
\bar H=U^\dagger HU,
\quad
\bar S=U^\dagger SU,
\quad
\bar c=U^{-1}c=U^\dagger c,
\quad
\bar r=U^\dagger r,
\]

向量 2-范数、矩阵 2-范数和系数 2-范数均保持，因此阶段 B 定义的 Euclidean 归一化残差标量保持不变。相邻句同时指出，一般非 unitary 可逆合同变换只保持广义谱、精确零残差方程和残差向量协变，不保持该标量。该边界与 README 及第 9 章一致，未重新引入此前的一般可逆残差不变量错误。

## 4. 新问题检查

未发现新 `BLOCKING`。两处新增文字未改变已有 Fourier 正负号、\(1/N\)、矩阵合同方向、Cholesky/对称正交化逆映射、Hermitian-definite 条件或 M4-06/M4-07 分工。

## 5. 渲染与文本完整性复核

使用：

```powershell
pandoc <file> --from=markdown+tex_math_single_backslash+tex_math_double_backslash --to=html5 --mathml --fail-if-warnings
```

实际结果：

```text
04_derivations/stageB/03_generalized_eigen.md
  PANDOC=0  MATHML=146  CONTROL=0  INLINE=92/92  DISPLAY=54/54

04_derivations/stageB/04_bloch_fourier.md
  PANDOC=0  MATHML=59   CONTROL=0  INLINE=33/33  DISPLAY=26/26
```

两文件均实际产生 MathML 节点，公式定界符成对，且不存在除 TAB、LF、CR 外的 C0 控制字符或 DEL。

## 6. SHA-256 复核快照

```text
ECF2F635F709F0EEA55CB1E4D3D549599F1EC0315765E3F9455F443ED5AFF8DB  04_derivations/stageB/03_generalized_eigen.md
BC11144E9CF6279C04ED0708191FC34DCECD81508F5149CDD1CDF3D4A7653D42  04_derivations/stageB/04_bloch_fourier.md
387ED757390868A0924870BBBDE8AB26F0493D57548F1A6AE8A0CA4002E29428  08_audits/M4_stageB_derivation_package_independent_audit.md
```

最终判定：M4-D-N01 `CLOSED`，M4-D-N02 `CLOSED`，新增 `BLOCKING=0`；维持 M4-06 `COMPLETED` 与 M4-07 `READY`。
