# M4 阶段 B 材料建设工作包

## 1. 目标与授权边界

M4 建设第 2—4、9 章，使读者能够从量子态和矩阵表示出发，推导非正交基中的广义厄米本征问题，并在一个明确的 Fourier 约定下完成实空间矩阵块、倒空间矩阵和能带之间的双向变换。

本阶段只使用解析模型、随机厄米/正定矩阵和合成周期模型。不安装 DeepH，不下载正式训练数据，不生成正式 DFT 标签，也不选择材料体系、DFT 后端或实践软件版本。Python 用户态依赖按 D-009 固定版本和复现命令。

## 2. 知识范围与完成证据

| 单元 | 必须覆盖 | 必须验证 |
|---|---|---|
| 第 2 章 | 态、算符、基、矩阵元、期望值、厄米性、基变换 | 二能级解析例题；一致/不一致基变换对照 |
| 第 3 章 | Gram 矩阵、对偶基、\(Hc=ESc\)、\(S\)-度量、Rayleigh 商、Cholesky 与对称正交化、病态性 | 残差、\(S\)-正交、谱不变性、条件数扫描和非正定失败样例 |
| 第 4 章 | 晶格平移、Bloch 定理、Bloch 和、倒格子、Fourier 正反变换、相位/规范约定 | 有限周期链的正反变换、相位约定同步变换和厄米关系 |
| 第 9 章 | 实空间 \(H(\mathbf R),S(\mathbf R)\)、截断、\(k\) 空间组装、广义本征、能带与重建 | 一维双轨道能带、截断误差、Hermiticity、逆变换和失败样例 |

每个单元都应形成教材正文、逐步推导、至少一个完整例题、分层练习与参考解答、自学检查题与误区分析、可执行代码、自动测试和失败样例。所有公式必须声明指标、形状、复共轭、正定性、相位和有限/无限周期条件。

## 3. 任务分解

| ID | 任务 | 状态 | 退出条件 |
|---|---|---|---|
| M4-01 | 冻结范围、来源覆盖、三级提纲和验证矩阵 | `COMPLETED` | 四章资料包与三级提纲完成内部检查并通过独立审计 |
| M4-02 | 第 2 章正文、例题与解答 | `COMPLETED` | 对象层级和一致基变换材料完整 |
| M4-03 | 第 3 章正文、推导与解答 | `COMPLETED` | M4-C3-B01—B02 经独立定点复核关闭，无新增 `BLOCKING` |
| M4-04 | 第 4 章正文、推导与解答 | `COMPLETED` | 独立审计通过，N01—N03 定点复核关闭，无新增 `BLOCKING` |
| M4-05 | 第 9 章正文、例题与解答 | `COMPLETED` | M4-C9-B01—B03 与 N01 经原独立审计子 agent 定点复核关闭，无新增 `BLOCKING` |
| M4-06 | 解析推导包 | `COMPLETED` | 独立审计判定 D-B01—D-B06 全部 `PASS`、`BLOCKING=0`；两项非阻塞显式性改进已实施并在定点复核中 |
| M4-07 | 数值实现、固定环境、测试与失败样例 | `COMPLETED` | 独立审计判定 T-B01—T-B10 全部 `PASS`、`BLOCKING=0`、无非阻塞缺陷 |
| M4-08 | 自学导航、能力—材料映射和综合练习 | `COMPLETED` | 独立材料审计判定全部映射和 C-B01—C-B08 题解通过，`BLOCKING=0`、非阻塞项 0 |
| M4-09 | 阶段 B 独立材料审计与阻塞复核 | `COMPLETED` | 新的独立子 agent 总审计判定 `PASS`、`BLOCKING=0`、非阻塞项 0，允许 M4 完成与 M5 启动 |

## 4. 来源边界

M4 的基础来源为 FND-01 第 4、14、15 章，FND-02 第 8.7 节，FND-03 第 5 章、FND-04 第 2 章第 35 页，以及 FND-06 的 MIT 8.04 固定讲义（Lecture 6 第 1—4 页、Lecture 8 第 4—5 页、Lecture 9 第 1—4 页）。DH-01 正文第 375—376 页仅用于确认原始 DeepH 的 \(H(\mathbf R),S(\mathbf R)\rightarrow H(\mathbf k),S(\mathbf k)\rightarrow E_{n\mathbf k}\) 工作流。标准定义后的代数步骤标记为 `DIRECT_DERIVATION`；教学模型标记为 `PEDAGOGICAL`。这些来源不支持任何具体软件接口、轨道排序或真实材料结论。

阶段 B 共用定义冻结在[统一表示与 Fourier 约定](../03_textbook/stageB_conventions.md)。第 4、9 章不得另立未映射的实空间矩阵方向、Fourier 相位或轨道中心规范。

## 5. 可执行建设与验证矩阵

### 5.1 固定产物路径

| 类型 | 冻结路径 |
|---|---|
| 正文 | `03_textbook/chapters/02_quantum_states_operators_matrices/chapter.md`；第 3、4、9 章同目录各自 `chapter.md` |
| 推导 | `04_derivations/stageB/02_basis_representation.md`、`03_generalized_eigen.md`、`04_bloch_fourier.md`、`09_realspace_to_bands.md` |
| 例题 | 各章 `examples.md` |
| 练习与解答 | `06_exercises/02-stageB/` 下按 `02_basis`、`03_generalized_eigen`、`04_bloch_fourier`、`09_realspace_bands` 分目录，每个单元含 `problem/readme.md` 与 `solution/readme.md` |
| 代码 | `05_code_exercises/stageB_periodic_nonorthogonal/stageb_models.py` 与 `run_experiments.py` |
| 测试与环境 | 同目录 `test_stageb_models.py`、`requirements.txt`、`README.md` |
| 自学导航 | `03_textbook/chapters/stageB_self_study_guide.md` |

固定环境沿用 D-009：Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0。当前工作区命令契约为：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -c "import sys; assert sys.version_info[:3] == (3, 12, 13)"
& $py -m pip install -r 05_code_exercises/stageB_periodic_nonorthogonal/requirements.txt
& $py -c "import numpy, scipy; assert numpy.__version__ == '2.3.5'; assert scipy.__version__ == '1.18.0'"
& $py -m unittest discover -s 05_code_exercises/stageB_periodic_nonorthogonal -p "test_*.py" -v
& $py 05_code_exercises/stageB_periodic_nonorthogonal/run_experiments.py --format json
```

其他机器必须把 `$py` 替换为本机 Python 3.12.13 的绝对路径；所有后续命令继续使用同一个 `$py`。

### 5.2 推导与材料验收

| ID | 能力/推导 | 正文与推导路径 | 例题/练习路径 | 解析验收与失败边界 |
|---|---|---|---|---|
| D-B01 | 态、算符、矩阵元和一致基变换 | 第 2 章 `chapter.md`；`04_derivations/stageB/02_basis_representation.md` | 第 2 章 `examples.md`；`06_exercises/02-stageB/02_basis/` | 明示 \(\Phi'=\Phi A,c'=A^{-1}c,H'=A^\dagger HA\)；非幺正时给出 \(S'=A^\dagger A\)，保留只变 \(H\) 或只变系数的反例 |
| D-B02 | 从投影与 Rayleigh 商推导 \(Hc=ESc\) | 第 3 章 `chapter.md`；`03_generalized_eigen.md` | `03_generalized_eigen/` | 每一步含指标和变分约束；若 \(S\not\succ0\) 不调用定广义谱结论 |
| D-B03 | Cholesky、对称正交化与 \(S\)-归一化 | 同上 | 同上 | 同时给出变量替换和逆映射；禁止以显式矩阵逆作为默认实现；含近线性相关失败边界 |
| D-B04 | 一般可逆基变换下广义谱不变 | 第 2、3 章；`02_basis_representation.md`、`03_generalized_eigen.md` | 第 2、3 章对应单元 | 证明 \(\det(H'-ES')=\lvert\det A\rvert^2\det(H-ES)\) 或等价论证，并给出不一致变换反例 |
| D-B05 | 实空间厄米关系 | 第 4、9 章；`04_bloch_fourier.md` | `04_bloch_fourier/` | 从冻结的 \(H_{ab}(\mathbf R)=\langle a0\vert H\vert b\mathbf R\rangle\) 推出指标交换与 \(-\mathbf R\)；缺共轭块为失败样例 |
| D-B06 | 周期 Fourier 正反变换及相位规范 | 第 4、9 章；`04_bloch_fourier.md`、`09_realspace_to_bands.md` | 第 4、9 章对应单元 | 复算离散正交关系、\(1/N\) 位置、\(S\) 同步变换和轨道中心 \(U(\mathbf k)\)；相位只改一侧必须失败 |

### 5.3 自动测试与数值容差

所有范数默认使用复数双精度下的 Frobenius 范数；归一化本征残差定义为

\[
r_n=\frac{\|Hc_n-E_nSc_n\|_2}
{\|H\|_2\|c_n\|_2+|E_n|\|S\|_2\|c_n\|_2}.
\]

| 测试 ID | 合成输入与代码入口 | 应保持的性质 | 通过标准 | 预期失败与断言 |
|---|---|---|---|---|
| T-B01 | 固定种子随机复厄米 \(H\)、\(S=Q\operatorname{diag}(s)Q^\dagger\succ0\)；`solve_generalized` | 广义本征残差 | \(\max_n r_n\le10^{-12}\)（\(\kappa_2(S)\le10^4\)） | 非正定 \(S\) 抛出 `ValueError`，消息含 `positive definite` |
| T-B02 | T-B01 本征矢 | \(C^\dagger SC=I\) | \(\lVert C^\dagger SC-I\rVert_F\le10^{-11}\) | 非厄米 \(H\) 抛出 `ValueError`，消息含 `Hermitian` |
| T-B03 | 随机可逆 \(A\)，同步变换 \(H,S\) | 广义谱不变 | 排序谱最大绝对差 \(\le10^{-11}\) | 只变换 \(H\) 的谱差 \(>10^{-4}\) |
| T-B04 | \(\kappa_2(S)=10^0,10^2,10^4,10^6,10^8\) 的构造族 | 残差与 \(S\)-正交性随条件数记录且输出有限 | 前四档 \(\max_n r_n\le10^{-10}\)、正交残差 \(\le10^{-8}\)；\(10^8\) 档只要求有限并标记 `ill_conditioned` | \(S\) 最小特征值低于固定阈值时必须诊断，不允许静默当作良态样例 |
| T-B05 | 有限 \(N\ge8\) 的复矩阵块，含完整 \(\pm\mathbf R\) 配对；`fourier_forward/inverse` | Fourier 正反变换 | 最大块误差 \(\le10^{-12}\) | 正反变换相位同号时重建误差 \(>10^{-6}\) |
| T-B06 | T-B05 的 \(H,S\) | 每个 \(k\) 上 Hermiticity | 最大 \(\max(\lVert H-H^\dagger\rVert_F,\lVert S-S^\dagger\rVert_F)\le10^{-12}\) | 删除一个非零共轭块后最大 Hermiticity 残差 \(>10^{-6}\) |
| T-B07 | 一维双轨道 \(H(0),H(\pm1),S(0),S(\pm1)\)，\(N\ge64\) | 全 \(k\) 广义残差和 \(S\succ0\) | 最大残差 \(\le10^{-11}\)，最小 \(S(k)\) 特征值 \(>10^{-3}\) | 忽略 \(S(k)\) 后至少一个能量差 \(>10^{-3}\) |
| T-B08 | cell-phase 与含轨道中心相位两套 \(U(k)\) | 规范变换谱不变 | 全 \(k\) 最大谱差 \(\le10^{-11}\) | 只变换 \(H\) 不变换 \(S\) 时谱差 \(>10^{-4}\) |
| T-B09 | 含 \(R=0,\pm1,\pm2\) 的已知模型 | 截断误差与 \(k\) 采样误差分离 | 完整块重建误差 \(\le10^{-12}\)；删除 \(\pm2\) 后误差 \(>10^{-6}\)，恢复后回到容差 | 不得把截断误差用增加同一离散对内的 \(k\) 点伪装为消失 |
| T-B10 | 轨道重排、单轨道相位翻转和子空间幺正混合 | 同步变换后的谱与残差不变 | 最大谱差 \(\le10^{-11}\)，最大残差 \(\le10^{-11}\) | 索引置换只作用一侧时 Hermiticity 或谱差断言失败 |

JSON CLI 必须输出 Python/NumPy/SciPy 版本、随机种子、矩阵维数、\(N_k\)、每个测试指标、所用容差、失败样例是否被拒绝以及 `conventions_version="stageB-v1"`。测试退出码为 0 表示正例达到容差且每个预期失败按指定方式被捕获；仅打印异常而未断言不算通过。

## 6. M4-01 独立审计问题

独立审计应检查：四章是否完整覆盖阶段 B；章节依赖顺序是否无循环；广义本征问题是否始终限定 \(H=H^\dagger,S=S^\dagger\succ0\) 或明确讨论例外；基变换的矩阵和系数方向是否一致；Fourier 正反变换、归一化和相位是否闭合；实空间厄米关系是否含正确的指标交换；验证矩阵是否含正例、反例和失败边界；是否越过 M8/M9 授权边界。
