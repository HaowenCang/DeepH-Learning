# M4-09 阶段 B 材料完备性、可自学性与可验证性总门控包

> 当前状态：`REVIEW`。本文件是独立总审计的输入与证据索引，不自行给出 M4 通过结论。只有新的独立子 agent 明确判定 `BLOCKING=0` 且允许进入 M5，主 agent 才能把 M4 标为 `COMPLETED`。

## 1. 门控目标与范围

阶段 B 覆盖第 2、3、4、9 章，目标是从有限维量子态和矩阵表示出发，完整建立非正交基中的 Hermitian-definite 广义本征问题、周期 Bloch/Fourier 表示、实空间矩阵块到 \(k\) 空间矩阵和能带的对象链，并提供可复现的正例、边界和失败样例。

依据 D-010 材料建设模式，学习者本人闭卷作答、口头解释和逐阶段自测不属于阻塞证据；原有知识范围、推导条件、来源边界、练习强度和技术验证全部保留。总审计应判断材料是否足以支持系统自学且可由第三方复核，而不是审查个人学习表现。

## 2. 冻结对象与共同约定

- [阶段 B 工作包](M4_stageB_work_package.md)：范围、路径、D-B01—D-B06 和 T-B01—T-B10 门控矩阵；
- [统一表示与 Fourier 约定](../03_textbook/stageB_conventions.md)：列基、bra/ket 方向、cell-phase、正负号、\(1/N\)、中心规范；
- [阶段 B 自学导航](../03_textbook/chapters/stageB_self_study_guide.md)：B1—B4 顺序、能力映射、答案定位和失败诊断；
- 第 2、3、4、9 章各自的 `sources.md`、`outline.md`、`chapter.md`、`examples.md`；
- [D-B01—D-B06 解析推导包](../04_derivations/stageB/README.md)及其四份逐式推导；
- `06_exercises/02-stageB/` 下五个单元的 problem/solution，包括 C-B01—C-B08 综合题解；
- [M4-07 代码说明](../05_code_exercises/stageB_periodic_nonorthogonal/README.md)、`stageb_models.py`、`run_experiments.py`、`test_stageb_models.py` 与 `requirements.txt`。

标准主线限定为有限维复内积空间、线性无关基、\(H=H^\dagger\) 和 \(S=S^\dagger\succ0\)。周期推导先在完整有限 Born–von Karman 晶格及其对偶网格上成立；无限积分、有限采样和实空间截断必须分别标记。

## 3. 知识范围与来源证据

| 维度 | 必须通过的内容 | 主要证据 |
|---|---|---|
| 量子态与矩阵表示 | 态、基、系数、矩阵元、Gram 矩阵、期望值和一致换基无对象混淆 | 第 2 章；D-B01；第 2 章题解；T-B03/T-B10 |
| 非正交广义本征 | 投影与 Rayleigh 商、Gram 正定、实谱、完整 \(S\)-正交基、Cholesky/对称正交化、条件数与误差边界 | 第 3 章；D-B02—D-B04；T-B01—T-B04 |
| 周期与 Fourier | BvK 角色正交、Bloch 和、闭合正逆变换、实空间厄米关系、\(k+G\) 与中心规范 | 第 4 章；D-B05/D-B06；T-B05/T-B06/T-B08 |
| 实空间到能带 | \(H(R),S(R)\to H(k),S(k)\to E_n(k),c_n(k)\)，逆变换、截断/采样、简并与前向解释 | 第 9 章；D-B06；T-B07—T-B10 |
| 来源边界 | `PRIMARY_EXPLICIT`、`DIRECT_DERIVATION`、`PEDAGOGICAL` 可区分；原始 DeepH 预测 \(H\)，\(S\) 由基函数重叠获得，不泛化现代软件 | 四章 `sources.md`；第 9 章 9.6；DH-01 固定本地快照 |

基础来源冻结为 FND-01—FND-06 与 DH-01 的指定章节/页码。来源不支持具体现代软件字段、文件格式、轨道排序、材料参数或误差统计；这些内容不得由教学模型推断。

## 4. 推导、题解与自学性证据

独立总审计至少应确认：

- D-B01—D-B06 均能从总索引定位到条件明确、方向一致的逐式推导；
- 一般可逆合同变换保持广义谱、精确方程和残差向量协变，但冻结的 Euclidean 归一化残差标量只在 unitary 情形保持；
- 完整 \(S\)-正交本征基由标准 Hermitian 谱定理与可逆逆映射建立，不由逐对正交关系单独推出；
- Fourier 正变换为 \(e^{+ikR}\)，逆变换为 \(e^{-ikR}/N\)，\(H/S\) 全程同步；
- 四章分层练习和 C-B01—C-B08 综合题均有一一对应参考解答、条件、机制、误区和验证入口；
- 自学导航从前置知识到正文、推导、例题、练习、解答、代码和失败诊断的顺序闭合，不要求学习者提交作答。

## 5. 代码、环境与失败样例

固定环境为 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0；`requirements.txt` 使用精确版本。总审计应从项目根目录实际执行：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m pip check
& $py -m unittest discover -s 05_code_exercises/stageB_periodic_nonorthogonal -p 'test_*.py' -v
& $py 05_code_exercises/stageB_periodic_nonorthogonal/run_experiments.py --format json --seed 20260803 --dimension 6 --nk 64
& $py 05_code_exercises/stageB_periodic_nonorthogonal/run_experiments.py --format json --seed 20260804 --dimension 4 --nk 32
```

预期结果为 5 项单元测试通过，两组 CLI 均含 T-B01—T-B10 且 `overall_pass=true`。JSON 必须记录版本、种子、维数、\(N_k\)、容差、指标、预期失败和 `conventions_version="stageB-v1"`。非正定 \(S\)、非 Hermitian \(H\)、只变 \(H\)、同号 Fourier 逆变换、缺共轭块、忽略 \(S(k)\)、单边中心规范、删除 \(\pm2\) 和单边置换必须由真实计算与强制断言捕获。

## 6. 已有独立分项审计

| 工作项 | 独立结论与冻结证据 |
|---|---|
| M4-01 工作包 | B01—B03 经 `M4_stageB_work_package_blocking_reaudit.md` 关闭，SHA `3AB104D6...0111409` |
| M4-02 第 2 章 | B01—B02 经 `M4_chapter2_blocking_reaudit.md` 关闭，SHA `04C4BF98...1E5C97` |
| M4-03 第 3 章 | B01—B02 经 `M4_chapter3_blocking_reaudit.md` 关闭，SHA `73271908...5683B1` |
| M4-04 第 4 章 | 内容审计通过，N01—N03 经 `M4_chapter4_nonblocking_reaudit.md` 关闭，SHA `5DAA7A46...19A666` |
| M4-05 第 9 章 | B01—B03 与 N01 经 `M4_chapter9_blocking_reaudit.md` 关闭，SHA `59A7E05B...89C64C` |
| M4-06 推导包 | D-B01—D-B06 `PASS`；N01/N02 经 `M4_stageB_derivation_package_nonblocking_reaudit.md` 关闭，SHA `41588A54...BE8571` |
| M4-07 代码 | T-B01—T-B10 `PASS`、`BLOCKING=0`、无非阻塞项，`M4_stageB_code_independent_audit.md` SHA `2BAD93B0...34FB63` |
| M4-08 自学材料 | B1—B4、D-B/T-B/C-B 映射 `PASS`、`BLOCKING=0`、无非阻塞项，`M4_stageB_self_study_independent_audit.md` SHA `D3471EAF...ABADE85` |

分项审计只能作为证据，不能替代 M4-09 对跨文件一致性、材料总完备性和当前快照的重新判断。

## 7. 主 agent 内部预检

当前内部预检记录为：

- 阶段 B 活动材料共 35 个 Markdown 文件；
- 70 个活动本地 Markdown 链接全部存在；
- Pandoc 严格模式全部退出 0，实际 `<math>` 节点合计 1,574；
- 控制字符为 0；
- C-B01—C-B08 的 problem/solution ID 严格一一对应；
- 5 项单元测试和两组 JSON CLI 通过，20 个预期失败标志均由先行计算和断言支持；
- `pip check` 报告 `No broken requirements found`。

这些是主 agent 的预检结果，不构成独立通过结论。审计者应当重新运行关键命令并冻结自己的哈希快照。

## 8. 已知缺口与授权边界

唯一跨阶段未决项为 BLK-03：计算资源、DFT/数据后端、DeepH 软件对象、首个材料体系、时间与训练预算和高级物理范围尚未冻结。该项必须在准备进入 M8 时集中提交用户决策，但不阻塞 M5—M7 的理论、教材和合成数据材料建设。

M8 前继续禁止安装 DeepH 本体、下载正式训练数据、生成正式 DFT 标签或隐含选择材料体系、DFT 后端和实践软件版本。M8 方案冻结后，在 M9 的正式安装、数据下载或复现实验前仍须再次请求明确执行授权。阶段 B 的全部实现只使用固定 Python 用户态依赖和合成矩阵。

## 9. M4-09 独立审计要求与通过标准

新的独立审计子 agent 应只新增正式报告，不修改被审材料。报告至少包含：

- 独立性声明和当前文件 SHA-256；
- 知识范围、来源、公式条件、跨章约定、推导、例题、练习、解答、代码、自学导航和授权边界的逐项判定；
- 实际运行的 unittest、两组 JSON CLI、链接、控制字符和 MathML 结果；
- `BLOCKING` 与非阻塞项列表，以及已知缺口能否安全带入 M5 的判断；
- 是否允许 M4 `COMPLETED`、M5 `READY` 的明确结论。

只有 `BLOCKING=0` 且报告明确允许进入 M5 时通过。若发现阻塞项，主 agent 实施修复后必须由独立子 agent 定点复核；主 agent不得以内部预检或既有分项审计替代该结论。
