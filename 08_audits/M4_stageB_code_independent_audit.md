# M4-07 阶段 B 数值实现独立代码与验证审计

## 1. 审计结论

审计日期：2026-08-04。

结论：`PASS`。本次独立审计未发现 `BLOCKING` 或需要在进入下一任务前关闭的非阻塞缺陷。固定环境、文件名和 JSON CLI 已与 M4 工作包一致；默认配置 `seed=20260803, dimension=6, N_k=64`、第二配置 `seed=20260804, dimension=4, N_k=32` 及 `unittest` 均以退出码 0 完成。T-B01—T-B10 的正例达到冻结容差，负例均实际执行并由异常消息或数值阈值断言捕获，而不是仅以未绑定计算过程的布尔量宣告通过。

因此允许：

- M4-07 由 `REVIEW` 转为 `COMPLETED`；
- M4-08 转为 `READY`；
- 不得把本报告解释为 M4-08 自学导航已经完成，也不得据此提前通过 M4-09 阶段 B 总门控。

## 2. 审计范围与规范

核心被审对象为：

- `05_code_exercises/stageB_periodic_nonorthogonal/stageb_models.py`；
- `05_code_exercises/stageB_periodic_nonorthogonal/run_experiments.py`；
- `05_code_exercises/stageB_periodic_nonorthogonal/test_stageb_models.py`；
- `05_code_exercises/stageB_periodic_nonorthogonal/requirements.txt`；
- `05_code_exercises/stageB_periodic_nonorthogonal/README.md`。

判定依据为 `08_audits/M4_stageB_work_package.md` 第 5.3 节 T-B01—T-B10、`03_textbook/stageB_conventions.md` 和 `04_derivations/stageB/README.md`。审计同时核查固定产物路径、复现命令、依赖版本、JSON 字段、退出码以及 M8/M9 边界。

## 3. 环境、命令与退出码

实际使用：

```text
C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
Python 3.12.13
NumPy 2.3.5
SciPy 1.18.0
```

`requirements.txt` 精确冻结 `numpy==2.3.5` 与 `scipy==1.18.0`。执行命令：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m unittest discover -s 05_code_exercises/stageB_periodic_nonorthogonal -p "test_*.py" -v
& $py 05_code_exercises/stageB_periodic_nonorthogonal/run_experiments.py --format json --seed 20260803 --dimension 6 --nk 64
& $py 05_code_exercises/stageB_periodic_nonorthogonal/run_experiments.py --format json --seed 20260804 --dimension 4 --nk 32
```

实际结果：`unittest=0`、`default JSON=0`、`second JSON=0`。五项单元测试全部 `ok`，两组 JSON 均含十项测试、`overall_pass=true` 和 `conventions_version="stageB-v1"`。默认配置连续运行两次所得 stdout 字节完全一致，证明固定环境中的随机种子复现有效。

## 4. JSON 契约核查

两组输出的顶层字段均严格为：

```text
conventions_version, versions, seed, matrix_dimension, N_k,
tolerances, tests, overall_pass
```

`versions` 正确记录 Python、NumPy 和 SciPy 版本；配置字段分别回显 `20260803/6/64` 与 `20260804/4/32`；`tests` 按顺序包含 T-B01—T-B10。每项测试均含 `status`、`metrics` 和 `expected_failures`。

代码中的部分 `*_failure_detected` 字段在阈值断言成功后写为字面量 `True`，但相应失败样例并非硬编码：T-B03、T-B05、T-B06、T-B07、T-B08 和 T-B10 均先实际构造错误对象、复算数值差，再以 `_require` 对报告中的同一数值执行下界断言；未达到失败阈值时函数会抛出 `AssertionError`，不会生成通过 JSON。T-B01、T-B02 使用捕获 `ValueError` 及消息片段的真实布尔结果；T-B04 的诊断布尔量由五档扫描记录计算；T-B09 的 64/128 点截断差由两次独立能带计算得到。故这些标记具有执行证据，不属于仅打印异常或伪造布尔通过。

`overall_pass` 虽由各项 `status` 汇总，但任一正例超差或负例未触发时，前置 `_require` 会中止套件并使 CLI 非零退出；因此退出码 0 的语义符合工作包。

## 5. T-B01—T-B10 逐项判定

下表数值按“默认配置；第二配置”给出。T-B09 按工作包固定使用 64/128 点分离截断与采样，因此不随 CLI 的 `N_k` 改变。

| ID | 判定 | 独立核查结果 |
|---|---|---|
| T-B01 | `PASS` | 使用逐本征对归一化 2-范数残差。最大残差为 `3.214663244683401e-15；2.8994214282688813e-15`，均低于 `1e-12`。非正定 (S) 实际抛出 `ValueError: overlap must be positive definite`。 |
| T-B02 | `PASS` | \(\lVert C^\dagger SC-I\rVert_F\) 为 `1.90698669170032e-14；1.4067253155142707e-14`，均低于 `1e-11`。非 Hermitian (H) 实际抛出消息含 `Hermitian` 的 `ValueError`；另行探测非 Hermitian (S) 得到 `overlap must be Hermitian and positive definite`。 |
| T-B03 | `PASS` | 一般可逆非 unitary 合同变换的谱差为 `1.4210854715202004e-14；3.197442310920451e-14`，低于 `1e-11`；只变 (H) 的谱差为 `10.055801494206532；1.55678943810668`，高于 `1e-4`。变换条件数均约 `2.0769230769`，不是退化的 unitary 特例。 |
| T-B04 | `PASS` | 五档目标条件数严格为 (10^0,10^2,10^4,10^6,10^8)。默认配置前四档最大归一化残差依次为 `4.589e-16, 1.664e-15, 7.024e-14, 5.854e-13`，正交残差为 `1.827e-15, 4.172e-15, 3.232e-13, 2.358e-11`；第二配置对应最大值为 `9.006e-13` 与 `5.955e-12`。均满足 `1e-10/1e-8`。两配置仅 (10^8) 档标记 `ill_conditioned=true`，全部指标有限。 |
| T-B05 | `PASS` | 正变换使用 (e^{+ikR})，逆变换使用 (e^{-ikR}/N)，同时作用于 (H,S)。最大块重建误差为 `4.440892098500626e-16；2.220446049250313e-16`，低于 `1e-12`；同号逆变换误差为 `0.4222916110123783；0.3951893637344963`，高于 `1e-6`。独立手算正变换最大差为 0，逆变换误差 `1.303699802838727e-16`。 |
| T-B06 | `PASS` | 完整 \(\pm R\) 配对后，全 (k) 的 (H,S) Hermiticity 均被逐点检查；二者合并最大残差为 `5.397192826725477e-16；3.4233439370878777e-16`，低于 `1e-12`。删除 (H(-2)) 后残差为 `0.6832032924733943；0.45371902761591626`，高于 `1e-6`。 |
| T-B07 | `PASS` | 双轨道模型逐 (k) 使用 Hermitian-definite 广义求解。最大归一化带残差为 `5.422996990019306e-16；4.354104126145266e-16`；最小 (S(k)) 特征值均为 `0.8275735931288073`。忽略 (S(k)) 的最大能量差均为 `0.22591131112434226`，满足失败下界。 |
| T-B08 | `PASS` | 中心相位 (U(k)) 为对角 unitary，并同步合同变换 (H,S)，系数使用 \(U^\dagger c\)。最大谱差为 `1.7763568394002505e-15；1.7763568394002505e-15`，变换后最大归一化残差为 `5.795543898561553e-16；4.577432594904002e-16`。只变 (H) 的谱差为 `0.020166351535514937；0.019932499680501037`。 |
| T-B09 | `PASS` | 完整 \(R=0,\pm1,\pm2\) 块的逆变换误差为 `4.440892098500626e-16`。删除 \(\pm2\) 后，64/128 点带差分别为 `0.16114005157591293` 和 `0.16135264514675396`，加密未消除截断误差。恢复步骤重新建立包含 \(\pm2\) 的独立字典、重新求解能带，再与完整模型比较，恢复误差为 0；不是把同一数组与自身比较。 |
| T-B10 | `PASS` | 轨道置换、单轨道相位翻转和随机 unitary 子空间混合均实际执行。三类同步变换的合并最大谱差为 `8.881784197001252e-16；2.220446049250313e-16`，最大归一化残差为 `2.96301429655781e-16；2.230583491048002e-16`。置换仅左作用于 (H) 后 Hermiticity 残差均为 `1.6067066718012422`。 |

## 6. 实现正确性与边界

`solve_generalized` 在调用 `scipy.linalg.eigh(H,S)` 前检查方阵、有限值、形状、按尺度的 Hermiticity 以及 (S) 的最小特征值；独立故障探测还确认奇异合同变换抛出 `transform must be invertible`。归一化残差实现逐列计算

\[
r_n=\frac{\lVert Hc_n-E_nSc_n\rVert_2}
{(\lVert H\rVert_2+|E_n|\lVert S\rVert_2)\lVert c_n\rVert_2},
\]

与工作包冻结定义完全一致，不是整矩阵 Frobenius 残差。

Fourier 正逆变换的相位和 (1/N) 与 `stageB_conventions.md` 一致；T-B06 同时覆盖 (H,S) 的全 (k) Hermiticity；T-B08 和 T-B10 仅在 unitary 变换下要求当前 Euclidean 归一化残差保持；T-B03 对一般可逆变换只要求广义谱不变，未重复把残差标量误推广为不变量。

代码只导入 Python 标准库、NumPy 与 SciPy，只构造固定种子随机矩阵和教材双轨道合成模型。未发现 DeepH 安装、网络或数据下载、DFT 标签生成、材料体系选择、DFT 后端选择、训练或外部计算调用，因此未越过 M8/M9 边界。

## 7. `unittest` 覆盖

五项测试全部通过：

```text
test_fourier_pair_uses_opposite_sign_and_one_over_n ... ok
test_full_acceptance_suite_default_seed ... ok
test_full_acceptance_suite_second_seed_and_shape ... ok
test_solver_rejects_invalid_pencils ... ok
test_unitary_transform_preserves_frozen_residual ... ok
Ran 5 tests ... OK
```

单元测试既运行完整十项门控的两个种子/形状，也对 Fourier 正反号与 (1/N)、非法矩阵束拒绝、unitary 变换后的冻结残差进行定点回归；完整负例覆盖仍由 `run_experiments.py` 内部的强制断言承担。

## 8. 阻塞项与非阻塞项

`BLOCKING=0`。

非阻塞项：无。JSON 中的失败标记已有前置计算值与强制断言作为可验证依据，不将字面量 `True` 本身列为缺陷；若未来重构，应当继续保持“先计算并断言，再生成标记”的顺序。

## 9. SHA-256 审计快照

```text
AD3ED1BB247BEC85968D8579DFCE5A47969BBE7BB6A4CB561CD1E1CC8A48D9E7  05_code_exercises/stageB_periodic_nonorthogonal/stageb_models.py
2CC7495B4F82482E788CC1C6F37E50B5A425B8E27E9905953C0CE43652EA485C  05_code_exercises/stageB_periodic_nonorthogonal/run_experiments.py
BED69908166B2B1B900BBA63C58525AA33DF2710986315551CE2FF7B4D50F03A  05_code_exercises/stageB_periodic_nonorthogonal/test_stageb_models.py
CC3EFBCD187C80ADDD5DB987EE90AD17BD481814985761D7B5CFAC3F0B5E10E4  05_code_exercises/stageB_periodic_nonorthogonal/requirements.txt
64A7D25D5F7A3573DAA11081544EB27E8F5D1A29881ADA996E8FE6CFA56D2E0A  05_code_exercises/stageB_periodic_nonorthogonal/README.md
31661F5AED6B13151D61C49D0A5EAA628B04D2949483DBF529DC2B0AB91FC885  08_audits/M4_stageB_work_package.md
66A135C38DBA8536D88701ED85DEBAE51D60A3E48CD0D09DFBBB463A2240B464  03_textbook/stageB_conventions.md
EB7B76E52FF9ABB3FBC1CD17A4605DFFC115D7F400EA5342DFCF1D932C8EBD69  04_derivations/stageB/README.md
```

最终判定：M4-07 `PASS`，`BLOCKING=0`，允许 `M4-07 COMPLETED` 与 `M4-08 READY`。
