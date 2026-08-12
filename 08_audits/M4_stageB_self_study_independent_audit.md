# M4-08 阶段 B 自学导航与综合练习独立材料审计

## 1. 审计结论

**正式结论：PASS。** 本次审计未发现 `BLOCKING`，也未登记非阻塞缺陷。M4-08 可以由 `REVIEW` 转为 `COMPLETED`，M4-09 可以转为 `READY`。

被审材料已经把第 2、3、4、9 章组织为 B1—B4 的单向依赖链，并明确将完成证据限定为材料覆盖、参考解答、可执行代码、失败样例和独立审计，不把学习者闭卷作答、口头解释或自测结果设为门槛。D-B01—D-B06、T-B01—T-B10 和 C-B01—C-B08 均有可定位入口；综合问题与参考解答按同一编号一一对应，误区、失败机制和自动验证入口能够经自学指南、解答末尾索引与代码说明交叉定位。

独立复算确认了高对称点矩阵与广义谱、一般非 unitary 合同变换的 Euclidean 残差反例、unitary 中心规范、Fourier 正反变换、截断与采样边界以及条件数/后向—前向误差边界。5 项单元测试全部通过；两组 JSON CLI 均以退出码 0 返回，T-B01—T-B10 全部为 `pass`，预期失败字段非空，`overall_pass=true`。来源表述正确区分原始 DeepH 预测的 Hamiltonian 与由基函数内积低成本获得的 overlap，且没有把该原始分工推广为现代软件事实。M8/M9 的外部动作和版本/材料/后端选择禁令继续保留。

## 2. 审计范围与独立性

核心对象：

- `03_textbook/chapters/stageB_self_study_guide.md`
- `06_exercises/02-stageB/comprehensive/problem/readme.md`
- `06_exercises/02-stageB/comprehensive/solution/readme.md`

交叉核对对象：

- 第 2、3、4、9 章各自的 `chapter.md`、`examples.md` 与 `sources.md`
- `04_derivations/stageB/README.md`
- `05_code_exercises/stageB_periodic_nonorthogonal/README.md`
- `05_code_exercises/stageB_periodic_nonorthogonal/run_experiments.py`
- `08_audits/M4_stageB_work_package.md`
- 原始来源 `01_sources/papers/li_et_al_2022_deeph.pdf` 的指定页

本次审计只读取和执行被审材料，没有修改教材、推导、练习、参考解答或阶段 B 代码。唯一新增文件为本审计报告。

## 3. 材料快照哈希

算法：SHA-256。

| 文件 | SHA-256 |
|---|---|
| `03_textbook/chapters/stageB_self_study_guide.md` | `4AABD96EE6154CBA163B7D4657C2AE4BDC23A791E3E22772E0285ACCE3DAA3F4` |
| `06_exercises/02-stageB/comprehensive/problem/readme.md` | `DE8BA796413AF298F76E80169D8EA4C1EEF15D80C16FFD020D09E81BB9C28160` |
| `06_exercises/02-stageB/comprehensive/solution/readme.md` | `DE0962FBDA3F1006EA488CA67492DC181FCA21061C7D7F2E89FBB81D328FB4C2` |
| `04_derivations/stageB/README.md` | `EB7B76E52FF9ABB3FBC1CD17A4605DFFC115D7F400EA5342DFCF1D932C8EBD69` |
| `05_code_exercises/stageB_periodic_nonorthogonal/README.md` | `64A7D25D5F7A3573DAA11081544EB27E8F5D1A29881ADA996E8FE6CFA56D2E0A` |
| `05_code_exercises/stageB_periodic_nonorthogonal/run_experiments.py` | `2CC7495B4F82482E788CC1C6F37E50B5A425B8E27E9905953C0CE43652EA485C` |
| `08_audits/M4_stageB_work_package.md` | `56B1E91AFBE1E22C272AD55C1A82B1EBD0908B3573AE56089315A12962137D4A` |
| 第 2 章 `chapter.md` | `58CC87B9E66399F3E8B1FFB202CCA6BBAFA2D3BCE2E8263CDF9F5A0AE53CE46D` |
| 第 2 章 `examples.md` | `2EC9C4EAA847DCEA7742E10D9C29EFFCA2943CB0B5B7F9E96C3D25DBFF495C55` |
| 第 2 章 `sources.md` | `4CCC8273FFC9936B8BEC76F2994E0D443E3CDFCD5C29BB12AEDD210C3396220B` |
| 第 3 章 `chapter.md` | `A00F0172280F02D3DD9553248A50492D08715FD31889A58BC11121DF3A2A5AD2` |
| 第 3 章 `examples.md` | `716ED6531FAE27D18E6F4EA5B182D569C83A5120F56A85F77261D22EC0169E4A` |
| 第 3 章 `sources.md` | `0042B83F9772E77590BC5C69F3F73CC79251A2A648DD67A734DA1B1FEE532F20` |
| 第 4 章 `chapter.md` | `87CCA024540FAD83B3A361D6DCA3C146C755D9DA2B8F78E33E18FFE96640C536` |
| 第 4 章 `examples.md` | `B00858D4C8B4D8B065B2CE37455D0412F21917322C8E6D7D584C0D36CC2A02F4` |
| 第 4 章 `sources.md` | `FE3B31F4CE7FD46ECF83189BE4A1CE9BDE4960C0EBDDB749F81D90E2DC64A713` |
| 第 9 章 `chapter.md` | `CC0FF72250FF2B534241E09EFE8FB1903FED5D17D2C4B2701C6BF0F429B842F2` |
| 第 9 章 `examples.md` | `1248AF0EF3D7B81665EA801F9A448A5DACFA79232F303B8AD98C05E9A6F90565` |
| 第 9 章 `sources.md` | `67E928397574EDEC2DFDCC70B4F88B785E5615F9DDDC3EB077B1504FA69BBAD8` |
| `01_sources/papers/li_et_al_2022_deeph.pdf` | `92C5A783B46475634A17D2D5F6557D8DE68D2F789F8DFB66182F56862580EC61` |

## 4. 逐项门控判定

| 审计项 | 判定 | 独立核对结果 |
|---|---|---|
| B1—B4 顺序与依赖闭合 | `PASS` | B1 冻结有限基对象与一致变换；B2 在 B1 上建立 Gram 矩阵和 Hermitian-definite 广义本征；B3 建立有限 BvK/Fourier 与实空间共轭配对；B4 合并 B2、B3 得到实空间矩阵—逐 (k) 广义本征—能带链。没有反向依赖或循环。 |
| 材料建设模式 | `PASS` | 指南明确“不要求学习者提交闭卷作答、口头解释或阶段自测”，并以材料覆盖、解答、代码、失败样例和独立审计作为完成证据。综合问题也明确不要求提交个人作答。 |
| D-B01—D-B06 定位 | `PASS` | 指南能力表与推导总索引均逐项列出主推导、条件、正例和失败边界；D-B06 在第 4、9 章分担 Fourier 闭合与完整对象链，角色不冲突。 |
| T-B01—T-B10 定位 | `PASS` | 指南 B1—B4 表和能力表覆盖全部十项测试；代码 README 给出十项一一对应的正例、指标和预期失败；JSON 使用同名键输出。 |
| C-B01—C-B08 一一对应 | `PASS` | 问题文件包含且仅包含 C-B01—C-B08，解答文件用相同八个标题逐项作答。覆盖对象/共轭配对、矩阵与谱、广义本征、一般可逆变换、Fourier 与中心规范、截断/采样、失败诊断、复现与授权边界。 |
| 问题—答案—误区—验证入口 | `PASS` | 问题文件链接参考解答、推导索引和代码说明；解答保留 C-B 编号、数值判据和误区索引；指南把各误区连接到 D-B/T-B；代码 README 给出实际执行入口。 |
| 矩阵方向与共轭配对 | `PASS` | \(H_{ab}(R)=\langle\phi_{a0}|\hat H|\phi_{bR}\rangle\) 与 (S) 的方向一致；逐指标推导得到 \(H(R)^\dagger=H(-R)\)、\(S(R)^\dagger=S(-R)\)，没有把非零块误设为自身 Hermitian。 |
| 高对称点矩阵与广义谱 | `PASS` | 独立复算与 C-B02/C-B03 数值一致，见第 5 节。 |
| 一般可逆与 unitary 边界 | `PASS` | 材料正确限定：一般可逆合同变换保持广义谱、精确方程和 (S)-正交性，但不保持冻结的 Euclidean 归一化残差；unitary 情形保持该残差。定量反例复算一致。 |
| Fourier 符号与 (1/N) | `PASS` | 正变换为 (e^{+ikR})，逆变换为 (e^{-ikR}/N)；S 同步。T-B05 实际验证闭合，同号逆变换按预期失败。 |
| 中心规范 | `PASS` | \(U(k)=\operatorname{diag}(1,e^{0.37ik})\) 与统一约定一致；同步变换 (H,S,c) 保谱且保持 unitary Euclidean 残差，只变 H 的负例被捕获。 |
| 截断与采样 | `PASS` | 成对删除 \(R=\pm2\) 保持 Hermiticity但改变模型；64/128 点加密不恢复缺失块；单边删除破坏 Hermiticity；恢复块后谱回到容差。 |
| 条件数与前向边界 | `PASS` | 材料没有从小后向残差直接推出小逐带前向误差；明确要求谱隙、简并结构、目标能窗和带匹配信息。T-B04 扫描记录残差与 (S)-正交退化并标记 (10^8) 档为 `ill_conditioned`。 |
| 来源与证据边界 | `PASS` | 标准来源只锚定对象和算法条件；后续代数标 `DIRECT_DERIVATION`，合成模型和故障注入标 `PEDAGOGICAL`；未外推真实材料误差或现代软件字段。 |
| 原始 DeepH 的 H/S 分工 | `PASS` | 本地 DH-01 指定页明确：Hamiltonian 可由 DFT SCF 得到或由 DeepH 预测；overlap 由基函数内积低成本得到，无需神经网络学习；两者 Fourier 后解广义本征。第 9 章和自学指南的表述与此一致，且明确不推广至现代软件。 |
| M8/M9 授权禁令 | `PASS` | 指南保留 M8 前不得安装 DeepH、下载正式数据、生成 DFT 标签、隐含选择材料/DFT 后端/实践版本；C-B08 解答进一步保留“M8 决策冻结后，M9 外部动作前仍需明确执行授权”。 |
| 固定环境与复现命令 | `PASS` | Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0 一致；README 给出固定依赖安装与复现命令。 |
| Markdown、控制字符与 MathML | `PASS` | 22 个核对文件共发现 63 个活动本地 Markdown 链接，缺失 0；非法控制字符 0。Pandoc 严格转换退出码均为 0，合计 793 个实际 `<math>` 节点。 |

## 5. 独立解析与数值复算

### 5.1 高对称点矩阵和广义谱

审计脚本独立构造题给 \(R=0,\pm1,\pm2\) 块，没有导入项目模型实现。结果为：

```text
k=0:
H = [[-0.72+0.j,  0.46+0.02j],
     [ 0.46-0.02j, 0.74+0.j]]
S = [[1.18+0.j,  0.032+0.005j],
     [0.032-0.005j, 1.116+0.j]]
E = [-0.73728885, 0.76771829]

k=pi:
H = [[0.88+0.j,  0.16+0.02j],
     [0.16-0.02j, 1.54+0.j]]
S = [[0.86+0.j, -0.028+0.005j],
     [-0.028-0.005j, 0.916+0.j]]
E = [0.96124921, 1.75714114]
```

采用第 9 章代码冻结的 `np.linspace(-pi, pi, 129, endpoint=False)`，得到

```text
minimum eigenvalue of S(k) = 0.8479319626434149
```

与参考解答 `0.84793196` 一致。

### 5.2 非 unitary 残差反例

对 \(H=\operatorname{diag}(0,2)\)、(S=I)、(E=0)、(c=(1,1)^T)、\(A=\operatorname{diag}(0.1,1)\)，独立计算冻结残差：

```text
rho_original    = 0.7071067811865475
rho_transformed = 0.09950371902099892
```

因此一般可逆合同变换并不保持该 Euclidean 标量；材料给出的 \(1/\sqrt2\) 与 \(1/\sqrt{101}\) 正确。

### 5.3 unitary 中心规范、截断和失败样例

在 129 点路径上独立组装题给完整双轨道模型，得到：

```text
unitary gauge maximum spectrum difference = 1.7763568394002505e-15
unitary gauge maximum normalized residual = 5.501123078150691e-16
H-only gauge spectrum difference           = 2.2711816789585004e-02
truncation band error, N_k=64              = 1.611400515759126e-01
truncation band error, N_k=128             = 1.6135264514675407e-01
ignore-S maximum energy difference         = 1.7994230643057008e-01
missing H(-2) Hermiticity residual          = 1.3796516518563903e-01
```

这些结果支持参考解答的“约 \(2.0\times10^{-2}\)”、“约 (0.18)”、“约 (0.138)”和两组截断误差；增加采样点没有恢复已删除的 \(R=\pm2\) 信息。

## 6. 自动测试与两组 CLI 审计

固定解释器：

```text
C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

执行命令：

```powershell
Set-Location 'E:\Projects\Codex\DeepH\05_code_exercises\stageB_periodic_nonorthogonal'
& $py -m unittest -v test_stageb_models.py
& $py .\run_experiments.py --format json --seed 20260803 --dimension 6 --nk 64
& $py .\run_experiments.py --format json --seed 20260804 --dimension 4 --nk 32
```

单元测试结果：

```text
Ran 5 tests in 0.107s
OK
exit code = 0
```

两组 CLI 的必要字段独立解析结果：

| 配置 | 退出码 | 顶层缺失字段 | 缺失 T-B ID | 非 pass ID | 空 expected_failures | 版本 | 容差字段数 | overall_pass |
|---|---:|---:|---:|---:|---:|---|---:|---|
| seed 20260803, dim 6, N_k 64 | 0 | 0 | 0 | 0 | 0 | 3.12.13 / 2.3.5 / 1.18.0 | 13 | `true` |
| seed 20260804, dim 4, N_k 32 | 0 | 0 | 0 | 0 | 0 | 3.12.13 / 2.3.5 / 1.18.0 | 13 | `true` |

必要顶层集合为 `conventions_version`、`versions`、`seed`、`matrix_dimension`、`N_k`、`tolerances`、`tests`、`overall_pass`；两组均满足 `conventions_version="stageB-v1"`。十项正例全部达到各自阈值，十项均包含实际执行的预期失败结果。

两组关键数值范围包括：

- T-B01 最大归一化残差：`3.214663244683401e-15`、`2.8994214282688813e-15`；
- T-B02 (S)-正交 Frobenius 残差：`1.90698669170032e-14`、`1.4067253155142707e-14`；
- T-B05 重建误差：`4.440892098500626e-16`、`2.220446049250313e-16`；
- T-B07 最大能带残差：`5.422996990019306e-16`、`4.354104126145266e-16`；
- T-B08 中心规范谱差不超过 `1.7763568394002505e-15`；
- T-B09 恢复块后的谱误差均为 `0.0`；
- T-B10 unitary 变换谱差不超过 `8.881784197001252e-16`。

## 7. 链接、控制字符和 MathML

链接与控制字符脚本对 3 个核心文件、推导/代码/工作包 README 以及四章的 `chapter/examples/sources` 共 22 个文件扫描：

```text
files = 22
active local markdown links = 63
missing links = 0
invalid control characters = 0
```

严格渲染命令：

```powershell
pandoc <file> `
  --from=markdown+tex_math_single_backslash+tex_math_double_backslash `
  --to=html5 --mathml --fail-if-warnings
```

核心文件实际 MathML 节点：

| 文件 | 退出码 | `<math>` 节点 |
|---|---:|---:|
| 自学指南 | 0 | 35 |
| 综合问题 | 0 | 41 |
| 综合解答 | 0 | 68 |
| 推导总索引 | 0 | 46 |
| 代码 README | 0 | 16 |
| M4 工作包 | 0 | 71 |

22 个核对文件总计 793 个实际 `<math>` 节点，全部转换命令退出码为 0。第 2 章 `sources.md` 没有数学公式，因而节点数为 0；这不构成渲染失败。

## 8. 来源定点核验

对 SHA-256 为 `92C5A783...580EC61` 的本地 DH-01 执行：

```powershell
pdftotext -f 10 -l 10 -layout `
  '01_sources/papers/li_et_al_2022_deeph.pdf' -
```

PDF 第 10 页、期刊第 376 页式 (8)—(9) 附近明确给出 overlap 为基函数内积，并说明 DFT Hamiltonian 可由自洽计算获得或由 DeepH 预测，overlap 计算代价很低而无需神经网络学习；随后对 Hamiltonian 和 overlap 作 Fourier 变换并求解广义本征问题。自学指南指向的第 9 章 9.6 节准确复述了该边界，并明确禁止将原始论文对象分工自动推广到现代软件。

## 9. 阻塞项、非阻塞项与状态建议

- `BLOCKING`: 0
- 非阻塞项：0
- M4-08：允许 `COMPLETED`
- M4-09：允许 `READY`

本结论仅允许进入 M4-09 阶段 B 独立材料总审计，不等价于 M4 总体完成，也不解除 M8/M9 的决策、安装、数据和外部计算授权限制。
