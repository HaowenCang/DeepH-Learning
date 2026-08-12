# M4-05 第 9 章阻塞项独立定点复核

## 1. 复核结论

- 复核日期：2026-08-04
- 复核角色：原 M4 第 9 章独立审计子 agent
- 复核基准：`08_audits/M4_chapter9_independent_content_audit.md` 中 M4-C9-B01、B02、B03 与 N01
- 修改边界：本次复核只新增本报告，未修改被审计材料、`README`、工作包或进度台账
- 定点结论：**M4-C9-B01 `CLOSED`；M4-C9-B02 `CLOSED`；M4-C9-B03 `CLOSED`；M4-C9-N01 `CLOSED`。**
- 新增 `BLOCKING`：**0**
- 当前剩余 `BLOCKING`：**0**
- 门控判定：**允许将 `M4-05` 标记为 `COMPLETED`；允许将 `M4-06` 标记为 `READY`。** 本报告不代替主 agent 对工作包和进度台账的实际更新。

修复后的材料已经正确区分一般可逆变换与幺正规范下的残差性质；嵌入代码实际计算并断言全路径 \(H/S\) Hermiticity 与逐本征对归一化 2-范数残差；原始 DeepH 的 \(H/S\) 对象分工与 DH-01 一致；三级提纲也补齐了 \(R=\pm2\) 块。固定环境复算、原始来源定点核对以及 Markdown/MathML 回归均通过，未发现修复引入新的相位、矩阵方向、广义本征条件、来源越权或验证口径错误。

## 2. 修复后快照

| 文件 | 复核时 SHA-256 | 相对原审计快照 |
|---|---|---|
| `03_textbook/chapters/09_realspace_hamiltonian_bands/sources.md` | `67E928397574EDEC2DFDCC70B4F88B785E5615F9DDDC3EB077B1504FA69BBAD8` | 未变 |
| `03_textbook/chapters/09_realspace_hamiltonian_bands/outline.md` | `E4F9B0E97ACE5629FA1BD6B3CDA1BF4A438945AFF7828D775C46B4CCA0865B66` | 已修订 |
| `03_textbook/chapters/09_realspace_hamiltonian_bands/chapter.md` | `CC0FF72250FF2B534241E09EFE8FB1903FED5D17D2C4B2701C6BF0F429B842F2` | 已修订 |
| `03_textbook/chapters/09_realspace_hamiltonian_bands/examples.md` | `1248AF0EF3D7B81665EA801F9A448A5DACFA79232F303B8AD98C05E9A6F90565` | 已修订 |
| `04_derivations/stageB/09_realspace_to_bands.md` | `29073B18123E83ABE171B5C57ADEA0A99117EB4932F67D6FE3F834746CA8C43D` | 已修订 |
| `06_exercises/02-stageB/09_realspace_bands/problem/readme.md` | `0EEC018076BADDC943E3F5BD8CF4235590628FF04549A518FA5B458C1A3BAB8C` | 已修订 |
| `06_exercises/02-stageB/09_realspace_bands/solution/readme.md` | `54A6BF3AF7EA5D2C487A2173CE3C558BE96BC2DCB83EFAF710B6161751A558DB` | 已修订 |
| `03_textbook/stageB_conventions.md` | `66A135C38DBA8536D88701ED85DEBAE51D60A3E48CD0D09DFBBB463A2240B464` | 未变 |
| `08_audits/M4_stageB_work_package.md` | `A25CDA5731F31DCE5AD90A9EE796D03A3A72DD8D70ED00326AB40A573822689A` | 状态说明已修订 |
| `08_audits/M4_chapter9_independent_content_audit.md` | `B482ECA47D68EC07D94A09C78A4A43958601D37DABB630DE08844C32B86671D3` | 原审计基准未变 |

## 3. 阻塞项与非阻塞项逐项复核

### M4-C9-B01：`CLOSED`

**原问题。** 原推导和 Q9-08 把当前 Euclidean 归一化残差的不变性错误推广到任意可逆 \(U(k)\)。

**修复核查。** 推导 `04_derivations/stageB/09_realspace_to_bands.md:114-130` 现已分开陈述：

- 任意可逆 \(U\) 在同步合同变换 \(\bar H=U^\dagger HU\)、\(\bar S=U^\dagger SU\)、\(\bar C=U^{-1}C\) 下保持广义谱、精确广义本征方程和 \(S\)-正交性；
- 对任意试探对，残差向量满足 \(\bar r=U^\dagger r\)，因此零残差仍为零；
- 非幺正 \(U\) 一般改变残差向量、矩阵和系数的 Euclidean 2-范数，故不保持第 3 节定义的归一化残差标量；
- 当 \(U\) 为 unitary 时，相关 2-范数均由酉相似/酉作用保持，归一化残差才具有该不变性。

Q9-08 题目 `problem/readme.md:33-35` 已明确要求推导上述范围并给出非 unitary 反例；解答 `solution/readme.md:61-71` 给出完整对象变换、残差向量协变和数值反例，不再把 \(U^\dagger r\) 的协变误当作标量范数不变。

**独立复算。** 取解答中的 \(H=\operatorname{diag}(0,2)\)、\(S=I\)、\(E=0\)、\(c=(1,1)^T\)、\(U=\operatorname{diag}(0.1,1)\)：

| 检查 | 结果 |
|---|---:|
| 原 Euclidean 归一化残差 | `0.7071067811865475` |
| 非幺正同步变换后残差 | `0.09950371902099892` |
| 残差向量协变误差 \(\|\bar r-U^\dagger r\|_2\) | `0.0` |
| 广义谱最大差 | `0.0` |
| 精确本征方程残差 | `0.0` |
| 变换后 \(S\)-正交残差 | `2.220446049250313e-16` |

另以实正交旋转作为 unitary 正例，变换前后归一化残差差为 `1.1102230246251565e-16`。数值同时验证了“任意可逆时协变、unitary 时标量不变”的修订命题。B01 的数学错误和 Q9-08 验收缺口均已关闭。

### M4-C9-B02：`CLOSED`

**原问题。** 原嵌入脚本没有断言正确模型的全路径 \(H/S\) Hermiticity，且把未归一化整矩阵 Frobenius 残差当作正文定义的逐本征对归一化 2-范数残差。

**修复核查。** `examples.md:98-122` 现对 129 点路径执行：

- 分别累计 \(\|H(k)-H(k)^\dagger\|_F\) 与 \(\|S(k)-S(k)^\dagger\|_F\)，并各自断言小于 `1e-12`；
- 对每个 \((E_n,c_n)\) 按正文公式计算分子 \(\|Hc_n-E_nSc_n\|_2\) 和分母 \((\|H\|_2+|E_n|\|S\|_2)\|c_n\|_2\)，再断言全路径最大值小于 `1e-12`；
- 继续断言最小 \(S\) 特征值、\(S\)-正交、逆变换、64/128 点截断、忽略 \(S\)、缺共轭块、同步规范和单边规范失败。

`examples.md:51,166-176` 的文字与输出键已经使用明确口径；Q9-10 解答 `solution/readme.md:85-89` 同步登记 Hermiticity 的 Frobenius 残差和逐本征对归一化 2-范数残差。缺少 \(H(-2)\) 的现有负例继续以 `herm_failure > 1e-2` 断言捕获共轭块破坏，并未只打印结果。

直接执行 `examples.md:70-177` 的嵌入 PowerShell/Python，退出码为 0。源代码中的 12 个 `assert` 语句因两个逆变换循环和 64/128 截断循环共执行 21 次，全部通过。关键输出为：

| 指标 | 实际输出 | 文本口径 |
|---|---:|---|
| 最大 \(H\) 反 Hermitian Frobenius 残差 | `1.689018570094359e-16` | `<1.7e-16`，一致 |
| 最大 \(S\) 反 Hermitian Frobenius 残差 | `1.6273148661314594e-17` | `<1.7e-17`，一致 |
| 最小 \(S(k)\) 特征值 | `0.8479319626434149` | `0.84793196`，一致 |
| 最大逐本征对归一化 2-范数残差 | `6.39360689764203e-16` | `<6.4e-16`，一致 |
| 最大 \(S\)-正交 Frobenius 残差 | `1.2572532603548516e-15` | `<1.3e-15`，一致 |
| 128 点截断差 | `0.16135264514675407` | `0.16135`，一致 |
| 忽略 \(S\) 最大谱差 | `0.17994269127235052` | `0.17994`，一致 |
| 缺共轭块 Hermiticity 残差 | `0.13796516518563903` | `0.13797`，一致 |

代码、断言、打印键、例题文字与 Q9-10 解答现在使用同一冻结定义。B02 已关闭。

### M4-C9-B03：`CLOSED`

**原问题。** 原正文把 overlap 写入原始 DeepH 的预测对象，超出 DH-01 的直接陈述。

**修复核查。** `chapter.md:142-146` 现明确写为：原始 DeepH 模型预测实空间 \(H(\mathbf R)\)，\(S(\mathbf R)\) 由局域基函数重叠以较低代价计算；二者再分别组装到 \(k\) 空间并求解广义本征问题。正文同时限定该分工只适用于原始论文，不自动推广到现代软件，也不推断字段名、轨道顺序、单位或相位；M8 前的软件安装、正式数据、DFT 标签、材料和后端禁令保持不变。

独立复核本地 DH-01：`01_sources/papers/li_et_al_2022_deeph.pdf` 的 SHA-256 仍为 `92C5A783B46475634A17D2D5F6557D8DE68D2F789F8DFB66182F56862580EC61`。PDF 第 10 页、期刊第 376 页式 (7)—(9) 附近明确称 Hamiltonian 可由 DFT SCF 获得或由 DeepH 预测，overlap 由基函数内积获得且无须神经网络学习，随后 Fourier 变换并求解广义本征问题。修订正文与 `sources.md:9,19,24` 及该原始证据一致。B03 已关闭。

### M4-C9-N01：`CLOSED`

`outline.md:33-38` 的 9.5.1 现明确列出 \(H(0),H(\pm1),H(\pm2),S(0),S(\pm1),S(\pm2)\)，与 `chapter.md:132-138`、`examples.md:5-29` 和工作包 T-B09 完全一致。贯穿模型与删除 \(\pm2\) 的截断演示不再发生提纲遗漏。

## 4. 修复回归与新阻塞检查

定点检查未发现修订引入新的 `BLOCKING`：

- Fourier plus 正变换与带 \(1/N\) 的负号逆变换未改变；
- \(H(\mathbf R)^\dagger=H(-\mathbf R)\)、\(S(\mathbf R)^\dagger=S(-\mathbf R)\) 及每 \(k\) Hermiticity 保持一致；
- \(S(k)\succ0\)、广义本征方程、\(S\)-正交、简并边界和 \(\Delta H-E\Delta S\) 耦合未发生回归；
- 双轨道高对称点、能带范围、逆变换、截断和三类失败数值未改变；
- Q9-01—Q9-10 与十份解答仍严格一一对应；
- `PRIMARY_EXPLICIT`、`DIRECT_DERIVATION`、`PEDAGOGICAL` 标签和 M8 授权边界仍然成立。

Pandoc 3.6.4 对九个文件逐一执行：

```powershell
pandoc --from=markdown+tex_math_single_backslash+tex_math_double_backslash --to=html5 --mathml --fail-if-warnings <file>
```

九次退出码均为 0 且无 warning；实际 MathML 节点数依次为：

| 文件 | MathML 节点数 |
|---|---:|
| `sources.md` | 4 |
| `outline.md` | 12 |
| `chapter.md` | 45 |
| `examples.md` | 38 |
| `09_realspace_to_bands.md` | 56 |
| `problem/readme.md` | 28 |
| `solution/readme.md` | 67 |
| `stageB_conventions.md` | 40 |
| `M4_stageB_work_package.md` | 71 |

合计 361 个实际 `<math>` 节点，每个文件均大于 0。九个活动本地 Markdown 链接全部存在，控制字符为 0。修订新增的 `Euclidean`/`unitary` 说明、非幺正反例、Hermiticity 指标和 DH-01 对象分工均未产生渲染或链接回归。

## 5. 最终门控判定

| 项目 | 状态 |
|---|---|
| M4-C9-B01 | **`CLOSED`** |
| M4-C9-B02 | **`CLOSED`** |
| M4-C9-B03 | **`CLOSED`** |
| M4-C9-N01 | **`CLOSED`** |
| 新增 `BLOCKING` | **0** |
| 当前剩余 `BLOCKING` | **0** |
| 是否允许 `M4-05 COMPLETED` | **是** |
| 是否允许 `M4-06 READY` | **是** |

本结论只适用于第 2 节记录的修复后快照。主 agent 可据此更新 `M4_stageB_work_package.md` 和进度台账；若更新状态前再次修改第 9 章正文、例题、推导或题解，应重新核验相应哈希和受影响结论。
