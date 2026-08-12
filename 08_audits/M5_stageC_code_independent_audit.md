# M5-08 阶段 C 教学 SCF 代码独立门控审计

**审计结论：FAIL（BLOCKING=1，NON_BLOCKING=0）。** 两组冻结 CLI、八项 `unittest`、依赖环境以及 T-C01—T-C08、T-C10 的数值与预期失败门槛均通过独立复现；T-C09 的 67 条必填路径及逐路径删除也确实执行并全部拒绝。然而，`stageC-label-v1` 验证器没有完成工作包冻结的标量类型、数组形状及全部 M8 前实践选择检查，多组无效记录和提前真实选择被错误接受。因此 M5-08 当前不得标记为 `COMPLETED`，不得启动 M5-09。修复后应由独立审计员对本报告的 B01 作定点复核。

## 1. 审计身份、范围与限制

本次审计以当前工作区文件和指定解释器的实际执行结果为唯一实现证据，不采用主实现者先前报告的通过结论或输出哈希。审计只读取下列被审对象：

- `08_audits/M5_stageC_work_package.md` 中 M5-08、T-C01—T-C10、`stageC-label-v1`、M8/M9 边界和复现命令；
- `05_code_exercises/stageC_teaching_scf/README.md`；
- `05_code_exercises/stageC_teaching_scf/requirements.txt`；
- `05_code_exercises/stageC_teaching_scf/teaching_scf.py`；
- `05_code_exercises/stageC_teaching_scf/run_experiments.py`；
- `05_code_exercises/stageC_teaching_scf/test_teaching_scf.py`。

未修改上述实现、教材、工作包或进度台账；未安装包、未访问网络、未调用 DFT/DeepH 后端、未下载数据、未生成正式标签。本报告是唯一审计产物。审计快照时间为 2026-08-04 05:44:37（Asia/Shanghai）。

## 2. 被审快照 SHA-256

| 文件 | 字节数 | SHA-256 |
|---|---:|---|
| `08_audits/M5_stageC_work_package.md` | 22,270 | `c9355d9660757d9f8dfd0ac07b023113619b437c049063f824e60469c69f5ebf` |
| `05_code_exercises/stageC_teaching_scf/README.md` | 4,892 | `b6786d4e1c2eecfc7525579467dfac3e11af1171d53bec681171837d5567991d` |
| `05_code_exercises/stageC_teaching_scf/requirements.txt` | 27 | `cc3efbcd187c80addd5db987ee90ad17bd481814985761d7b5cfac3f0b5e10e4` |
| `05_code_exercises/stageC_teaching_scf/teaching_scf.py` | 26,918 | `6c7c5adb51af28c8a2019d1c962be0cdde3abdf4876af84d00c3505dd07bb280` |
| `05_code_exercises/stageC_teaching_scf/run_experiments.py` | 18,936 | `820f5a1ed17a7ffbfac6dd9b01c81b9c99fd7287c660d213e7fffb6b2c38cb21` |
| `05_code_exercises/stageC_teaching_scf/test_teaching_scf.py` | 3,660 | `35cec382faf2c10d960d4ec078e7f99dbfb3bb506034f204e4e1b0b3b2d44a01` |

报告自身的哈希不写入本文件，以避免自指；由完成消息单独给出。

## 3. 独立复现环境与精确命令

固定解释器：

```text
C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

实际执行的 PowerShell 命令如下：

```powershell
$py='C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -c "import sys; assert sys.version_info[:3] == (3, 12, 13); print(sys.version)"
& $py -c "import numpy, scipy; assert numpy.__version__ == '2.3.5'; assert scipy.__version__ == '1.18.0'"
& $py -m pip check
& $py -m py_compile .\05_code_exercises\stageC_teaching_scf\teaching_scf.py .\05_code_exercises\stageC_teaching_scf\run_experiments.py .\05_code_exercises\stageC_teaching_scf\test_teaching_scf.py
& $py -m unittest discover -s .\05_code_exercises\stageC_teaching_scf -p 'test_*.py' -v
& $py .\05_code_exercises\stageC_teaching_scf\run_experiments.py --format json --seed 20260805 --model-size 12 --grid-size 64
& $py .\05_code_exercises\stageC_teaching_scf\run_experiments.py --format json --seed 20260806 --model-size 16 --grid-size 48
```

结果如下：

| 检查 | 结果 | 退出码/证据 |
|---|---|---|
| Python 版本断言 | PASS | `3.12.13`，退出码 0 |
| NumPy/SciPy 版本断言 | PASS | `2.3.5` / `1.18.0`，退出码 0 |
| `pip check` | PASS | `No broken requirements found.`，退出码 0 |
| `py_compile` | PASS | 三个 Python 文件均通过，退出码 0 |
| `unittest discover` | PASS | 8 项测试全部 `ok`，`Ran 8 tests`，退出码 0 |
| 冻结 CLI 1 | PASS（程序自报） | 退出码 0，`overall_pass=true`，T-C01—T-C10 均自报 `status=pass` 且 `expected_failure.detected=true` |
| 冻结 CLI 2 | PASS（程序自报） | 退出码 0，`overall_pass=true`，T-C01—T-C10 均自报 `status=pass` 且 `expected_failure.detected=true` |

每组 CLI 均另外独立重复一次。捕获的 UTF-8 标准输出逐字节相同：

| 配置 | 第一次 SHA-256 | 第二次 SHA-256 | 完全相同 |
|---|---|---|---|
| seed 20260805 / model 12 / grid 64 | `d28479d1dc012848d2fdb859d110b4f9c1c576d7ceab9f04f5ee042071e0969b` | 同左 | 是 |
| seed 20260806 / model 16 / grid 48 | `c915616e7c35f8a473c073ff7906d3d9dd198a6445faf51cd0d3fe10d56172b8` | 同左 | 是 |

输出可由严格 JSON 解析，顶层版本、seed、维数、`conventions_version="stageC-v1"`、`backend="synthetic"` 和 `overall_pass` 均存在；`allow_nan=False` 阻止 NaN/Infinity 进入输出，实际两组输出均可序列化。

## 4. T-C01—T-C10 逐项独立判定

表中的 PASS/FAIL 是独立审计判定，不等同于程序自报状态。

| ID | 判定 | 正例、阈值与预期失败证据 |
|---|---|---|
| T-C01 | PASS | 正例最终误差 `6.92971235949594e-11 < 1e-10`；估计率 `0.5999999999238534`，独立复算谱半径 `0.6000000000000001`，差远小于 `5e-3`。`x0=x*` 在第 0 步返回、`estimated_rate=null`；实测残差 `5.721958498152797e-17`，属于 float64 机器舍入零并满足实现的 `<1e-15` 检查。故障运行保存 `x0` 至 `x12` 共 13 个残差，即恰好 12 次更新；谱半径 1.8，末/初残差比 `309.1761916881516 > 10`。 |
| T-C02 | PASS | `alpha=0.25` 正例最终残差 `8.61382005058277e-10 < 1e-9`，归一化误差 0，最小密度为正；逐步形状、有限性、归一化和正性由运行时断言执行。`alpha=1` 的 20 步失败样例最终残差 `1.3531192579224054 > 1.3`，以 `oscillation_or_divergence` 捕获。 |
| T-C03 | PASS | 正例最终密度残差 `8.61382005058277e-10 < 1e-9`，相对能量变化 `2.0285496026449e-11 < 1e-9`；轨迹逐步记录密度、映射输出、残差和能量。错误能量见证为密度残差 `1.316815663204585 > 1`、伪能量变化 `3.4980818644017e-13 < 1e-10`，energy-only 会误通过而双判据拒绝。 |
| T-C04 | PASS | 五个混合参数均生成初值、迭代数、最终残差、终止原因和规范轨迹摘要；内部两次规范 JSON 哈希均为 `a41dc92a8de6d589d0b6e0ad45e8083010ea25ed04218540e78924a59db83c04`。`alpha=1,max_iter=20` 返回 `converged=false`、`max_iterations`。扫描中 `alpha=0.60` 和 `1.00` 达到 80 次更新但未被误报为收敛。 |
| T-C05 | PASS | 正序列末三个参考误差均小于 `1e-2`，末级误差 `4.999999999999449e-4 < 1e-3`，末两相邻差均小于 `1e-2`。负例 32/64 单对差为 `5e-4 < 1e-3`，但末级参考误差 `0.008000000000000007 > 0.005`，多层判据拒绝。 |
| T-C06 | PASS | `N_k=16,32,64` 的采样误差均小于 `1e-12`；独立参考 `iv(0,1)=1.2660658777520084`。采样轴与固定 `1e-2` 基误差轴分别报告；带偏置末级总误差 `0.009999999999999787 > 0.005`，错误归因被拒绝。 |
| T-C07 | PASS | 独立复算广义谱为 `[-1.2,-0.10000000000000003,0.7999999999999998,1.9999999999999993]`，最大谱差 `6.66133814775094e-16 < 1e-11`；最大归一残差 `1.49373566324221e-16 < 1e-12`，`S'` 最小本征值 `1.2154403466447898 > 0`。忽略 `S` 的谱差 `0.9674651567663939 > 0.1`，以 `overlap_ignored` 拒绝。 |
| T-C08 | PASS | 实现采用复高斯 QR 并对 `R` 对角相位规范化，投影的 `p=max(5,floor(d/3))`、`q=floor((d-p)/2)` 与冻结定义一致；旋转固定为标准基 0/1 平面、0.37 rad。两配置正交残差分别 `1.4324e-15`、`7.2340e-16`，回投残差分别 `5.7679e-16`、`5.6445e-16`；丢失范数分别 `0.95985867258085`、`0.9833167163767138`，均大于 0.9。等谱差均约 `4.44e-15 < 1e-12`，相对矩阵差分别 `0.23306075775057758`、`0.17451989619254055`，均大于 0.15。`model_size<12` 被拒绝。 |
| T-C09 | **FAIL** | 单一 `REQUIRED_PATHS` 确为 67 条且无重复；完整内置记录通过；67 条路径分别删除均抛出包含完整路径的 `ValueError`；坏制品哈希和 `backend.name` 提前选择也被拒绝。但是完整类型/shape/M8 边界验证不成立：多组明确无效或提前选择的记录被接受，见第 5 节和 B01。 |
| T-C10 | PASS | `grid_size` 64 与 48 均独立从原矩阵和截断矩阵复算全部三类指标，报告值最大差均为 0，小于 `1e-14`。指数拟合斜率 `-0.49999999999999994`，与 `-0.5` 的差小于 `1e-12`。代数尾指数外推相对误差 `0.8429707836304159 > 0.8`，失败声明被拒绝。`grid_size<48` 被拒绝。 |

## 5. 失败样例与阻塞证据

### M5-CODE-B01：T-C09 未实现完整类型/形状验证，也未普遍拒绝提前 M8 实践选择

**等级：BLOCKING。** 工作包 `M5_stageC_work_package.md:107` 明确要求标量类型、数组形状、64 位十六进制 SHA-256 和所有 `UNRESOLVED_M8` 占位均须检查；第 7、114 行又禁止 M8 前隐含选择真实材料、基、采样、投影软件等实践对象。当前 `teaching_scf.py:584-630` 只执行 67 条路径存在性、少数形状、四个实际哈希和一份有限的 `unresolved_paths` 列表。`test_teaching_scf.py:79-84` 的提前选择测试只变异 `backend.name`，不能证明其他实践选择受保护。

在完整合成记录的深拷贝上逐项施加下列单一变异，`validate_label_record` 均无异常返回，即错误接受：

| 对抗变异 | 违反的契约 | 实际结果 |
|---|---|---|
| `convergence.max_iterations = "eighty"` | 标量类型错误 | ACCEPTED |
| `structure.lattice = [["x"]*3]*3` | 形状虽为 3×3，但元素非数值 | ACCEPTED |
| `sampling.k_mesh = [1,1]` | 网格数组形状错误 | ACCEPTED |
| `sampling.k_shift = [0.0,0.0]` | 位移数组形状错误 | ACCEPTED |
| `structure.boundary_conditions = ["periodic"]` | 边界条件数组形状错误 | ACCEPTED |
| `representation.output_object = "H,S"` | 数组字段被替换为字符串 | ACCEPTED |
| `structure.id = "silicon"` | M8 前提前选择真实材料身份 | ACCEPTED |
| `basis.type = "plane_wave"` | M8 前提前选择实践基类型 | ACCEPTED |
| `sampling.kind = "monkhorst_pack"` | M8 前提前选择实践采样方案 | ACCEPTED |
| `projection.method = "HPRO"` | M8 前提前选择实践投影方法/软件对象 | ACCEPTED |

作为对照，`artifacts.inputs[0].sha256="bad"` 会以 `invalid SHA-256` 拒绝，`backend.name="bad"` 会以 `M8 choice was resolved early` 拒绝；这证明测试调用了真实验证器，问题不是测试脚本未执行，而是验证覆盖范围不足。由于类型、形状和提前真实选择都是冻结门槛，B01 不能降为非阻塞问题。

**逐文件修复要求：**

- `05_code_exercises/stageC_teaching_scf/teaching_scf.py`：为 `stageC-label-v1` 建立与 67 条路径同源或明确关联的类型、形状和值约束；至少覆盖所有标量、所有数组/映射、数值元素、数组间长度关系、哈希字段和全部 M8 前实践哨兵。对合成记录，应明确锁定 `structure.id="SYNTHETIC"`、合成 basis/sampling/projection 语义，或采用等价的统一 `UNRESOLVED_M8`/合成值白名单，确保真实材料、基、采样或投影选择不能通过。
- `05_code_exercises/stageC_teaching_scf/test_teaching_scf.py`：增加参数化负例，分别覆盖每类错误标量、非数值数组、每个冻结数组的错误形状、每个实际 SHA-256 字段以及所有实践选择分组；断言每个样例确实抛错且错误消息定位字段。现有 67 条逐路径删除和 `backend.name` 测试应保留。
- `05_code_exercises/stageC_teaching_scf/run_experiments.py`：扩展 T-C09 的故障注入证据，使 JSON 分别报告路径删除、类型、形状、哈希和提前 M8 选择的捕获计数/见证；任一类未拒绝时必须使 CLI 非零退出，不得仅以 `captured_count == 67` 宣告 T-C09 通过。
- `05_code_exercises/stageC_teaching_scf/README.md`：在实现修复后，按实际验证范围更新 schema 与测试说明；当前第 71 行后的“验证器检查”声明在类型/形状和全部实践选择方面超过实际能力，修复前不得继续作为已实现事实。
- `05_code_exercises/stageC_teaching_scf/requirements.txt`：无需修改。
- `08_audits/M5_stageC_work_package.md`：冻结契约本身清楚，无需修改。

**定点复核验收：** 原 8 项测试和两组冻结 CLI 继续通过且输出确定；新增负例矩阵全部真实失败；67 条删除仍逐条失败；上述十个审计见证至少均被拒绝；修复后的 JSON 对每类 schema 失败给出可审计证据；依赖和 M8/M9 边界不回归。

## 6. 依赖、静态边界、JSON 与退出码

`requirements.txt` 只有 `numpy==2.3.5` 和 `scipy==1.18.0`，均为精确固定；指定解释器实际版本完全匹配，`pip check` 通过。README 提供与工作包一致的 PowerShell 版本断言、安装入口、`pip check`、unittest 和两组冻结 CLI，并明确记录本次实现未安装新增包。本次独立审计也没有执行安装。

三个 Python 文件的导入仅涉及标准库、NumPy 和 SciPy。静态检索未发现 subprocess、网络客户端、下载、文件写出、DeepH、真实 DFT 后端或其 SDK 调用。所有计算对象均为解析、有限维或合成数组；没有正式数据、正式标签或真实材料输入。M7-I 后才准备 M8 决策、M8 冻结后 M9 外部动作仍需再次明确授权的边界在 README 中保持明确。B01 表明 schema 验证器尚不能强制执行全部提前选择禁令，但当前内置合成记录本身没有作出真实材料、泛函、赝势、后端或版本选择。

CLI 边界行为独立检查如下：

| 输入 | 退出码 | 结果 |
|---|---:|---|
| `--model-size 11 --grid-size 48` | 1 | `AssertionError: model_size must be at least 12` |
| `--model-size 12 --grid-size 47` | 1 | `AssertionError: grid_size must be at least 48` |
| `--format yaml` | 2 | argparse 拒绝非 JSON 格式 |

有效 CLI 退出码 0、输出可严格解析为 JSON，且所有十项均有 `status`、`tolerances` 和 `expected_failure`。无效维数和格式为非零退出。测试并非仅断言硬编码的 `pass`：T-C01—T-C08、T-C10 的状态在计算与 `require` 断言通过后才构造，故障指标来自实际故障运行；T-C09 的路径删除也是真实执行。B01 的对抗性测试则证明，现有 T-C09 测试集合覆盖不足。

## 7. 问题计数与最终许可

| 类别 | 数量 | 编号 |
|---|---:|---|
| BLOCKING | 1 | M5-CODE-B01 |
| NON_BLOCKING | 0 | 无 |

最终判定为 **FAIL**。T-C09 是冻结门槛的一部分；其完整类型/形状验证和 M8 前实践选择拒绝未满足，足以否决 M5-08，而不能由两组 CLI 自报 10/10 通过替代。因此：

- **不允许**将 M5-08 标记为 `COMPLETED`；
- **不允许**启动 M5-09；
- B01 按上述逐文件要求修复并经独立定点复核达到 `BLOCKING=0` 后，方可重新申请上述许可；
- 本审计不授权任何 M8/M9 外部实践动作。
