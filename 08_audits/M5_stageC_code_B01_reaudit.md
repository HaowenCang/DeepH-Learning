# M5-08 M5-CODE-B01 独立定点复核

**复核结论：M5-CODE-B01 = CLOSED。** 修复后的 `stageC-label-v1` 验证器已拒绝初审列出的十个原始见证；67 条必填路径逐条删除继续全部失败；47 个对抗变异由真实验证器逐项执行并全部拒绝，分类精确为 `type=9`、`shape=11`、`hash=8`、`m8_choice=19`。两组冻结 CLI、确定性、依赖、编译、9 项单元测试以及 T-C01—T-C08、T-C10 均无回归。本次复核 `新增 BLOCKING=0`、`新增 NON_BLOCKING=0`；初审唯一阻塞关闭后，允许 M5-08 标记为 `COMPLETED`，允许启动 M5-09。

## 1. 复核范围、独立性与快照

本次复核只针对 `08_audits/M5_stageC_code_independent_audit.md` 的唯一阻塞 M5-CODE-B01，不扩展到工作包外的额外研究。证据来自当前工作区源码、指定解释器的实际执行以及审计员独立构造的内存变异；未采用修复者口头结论或先前输出哈希。未修改 `teaching_scf.py`、`run_experiments.py`、`test_teaching_scf.py`、README、requirements、工作包或进度台账；本报告是唯一新增项目文件。复核快照时间为 2026-08-04 05:57:50（Asia/Shanghai）。

| 文件 | 字节数 | SHA-256 |
|---|---:|---|
| `08_audits/M5_stageC_code_independent_audit.md` | 15,289 | `0fec9083d76a6fabbef8c49ce44617fd2e4012ce1981701a58771ab7ea272f99` |
| `05_code_exercises/stageC_teaching_scf/README.md` | 5,591 | `ff82358bd8422a6a457764c0d308bbd3f8c09d78e559567b5283eeeaff4dce70` |
| `05_code_exercises/stageC_teaching_scf/requirements.txt` | 27 | `cc3efbcd187c80addd5db987ee90ad17bd481814985761d7b5cfac3f0b5e10e4` |
| `05_code_exercises/stageC_teaching_scf/teaching_scf.py` | 42,027 | `597af234a2688cd9cf71d2c501514ee07700a2fb0361026aef4be0221bebd867` |
| `05_code_exercises/stageC_teaching_scf/run_experiments.py` | 20,092 | `746681fc4bba4eee98b89870c6683c6a8251eea28be01b1d8d5fa0d81b1128e9` |
| `05_code_exercises/stageC_teaching_scf/test_teaching_scf.py` | 5,282 | `688956a996a48d4a04280f3a45735b47c5d19cbc21ac9576c73c9b2057ddd59b` |

报告自身哈希不写入本文件，以避免自指；由完成消息单独给出。

## 2. 独立命令与执行结果

固定解释器为：

```text
C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

在项目根目录实际执行：

```powershell
$py='C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -c "import sys; assert sys.version_info[:3] == (3, 12, 13); import numpy, scipy; assert numpy.__version__ == '2.3.5'; assert scipy.__version__ == '1.18.0'"
& $py -m pip check
& $py -m py_compile .\05_code_exercises\stageC_teaching_scf\teaching_scf.py .\05_code_exercises\stageC_teaching_scf\run_experiments.py .\05_code_exercises\stageC_teaching_scf\test_teaching_scf.py
& $py -m unittest discover -s .\05_code_exercises\stageC_teaching_scf -p 'test_*.py' -v
& $py .\05_code_exercises\stageC_teaching_scf\run_experiments.py --format json --seed 20260805 --model-size 12 --grid-size 64
& $py .\05_code_exercises\stageC_teaching_scf\run_experiments.py --format json --seed 20260806 --model-size 16 --grid-size 48
```

| 检查 | 结果 | 证据 |
|---|---|---|
| Python/NumPy/SciPy 断言 | PASS | `3.12.13 / 2.3.5 / 1.18.0`，退出码 0 |
| `pip check` | PASS | `No broken requirements found.`，退出码 0 |
| `py_compile` | PASS | 三个 Python 文件全部通过，退出码 0 |
| `unittest discover` | PASS | 9 项测试全部 `ok`，`Ran 9 tests in 0.150s`，退出码 0 |
| 冻结 CLI 1 | PASS | 退出码 0，T-C01—T-C10 均为 `status=pass`、`expected_failure.detected=true`，`overall_pass=true` |
| 冻结 CLI 2 | PASS | 退出码 0，T-C01—T-C10 均为 `status=pass`、`expected_failure.detected=true`，`overall_pass=true` |

每组 CLI 另外重复一次并比较捕获的 UTF-8 标准输出：

| 配置 | 第一次 SHA-256 | 第二次 SHA-256 | 逐字节相同 |
|---|---|---|---|
| seed 20260805 / model 12 / grid 64 | `b8470284ad0ce79068da8f75fb30712abaf9ffe916a6671ed6c079277a0c1376` | 同左 | 是 |
| seed 20260806 / model 16 / grid 48 | `6893201de85f5718e9346a482750977a172f36d9f33523479f38667c6e852e3d` | 同左 | 是 |

两组 JSON 均报告 `required_path_count=67`、路径删除捕获数 67、`schema_negative_case_count=47`、四类期望/捕获数分别为 9/11/8/19、见证总数 47。墙钟时间、临时路径和无序对象未进入输出。

## 3. 初审十个阻塞见证复现

下表变异均由审计员在完整合成记录的独立深拷贝上重新构造，并直接调用 `validate_label_record`；全部抛出 `AssertionError`，错误消息包含目标字段路径。

| 原始见证 | 结果 | 实际定位错误 |
|---|---|---|
| `convergence.max_iterations="eighty"` | REJECTED | `expected positive integer: convergence.max_iterations` |
| `structure.lattice` 为非数值 3×3 字符串数组 | REJECTED | `non-numeric array: structure.lattice` |
| `sampling.k_mesh=[1,1]` | REJECTED | `expected three positive integers: sampling.k_mesh` |
| `sampling.k_shift=[0.0,0.0]` | REJECTED | `wrong array shape: sampling.k_shift` |
| `structure.boundary_conditions=["periodic"]` | REJECTED | `expected three-string array: structure.boundary_conditions` |
| `representation.output_object="H,S"` | REJECTED | `wrong array value: representation.output_object` |
| `structure.id="silicon"` | REJECTED | `M8 choice was resolved early: structure.id` |
| `basis.type="plane_wave"` | REJECTED | `M8 choice was resolved early: basis.type` |
| `sampling.kind="monkhorst_pack"` | REJECTED | `M8 choice was resolved early: sampling.kind` |
| `projection.method="HPRO"` | REJECTED | `M8 choice was resolved early: projection.method` |

初审 B01 的直接反例已全部消失，且错误不仅拒绝输入，还可定位到被变异字段。因此原阻塞的核心退出条件满足。

## 4. 67 条路径与 47 个对抗变异

`REQUIRED_PATHS` 仍为单一元组，共 67 条且集合大小同为 67。对完整记录逐路径深拷贝并删除后，67 个样例均抛出包含完整缺失路径的 `ValueError`；`67/67` 删除负例无回归。

`SCHEMA_NEGATIVE_MUTATIONS` 的实际分类和执行结果如下：

| 分类 | 冻结期望数 | 源码实际数 | 验证器捕获数 | 判定 |
|---|---:|---:|---:|---|
| `type` | 9 | 9 | 9 | PASS |
| `shape` | 11 | 11 | 11 | PASS |
| `hash` | 8 | 8 | 8 | PASS |
| `m8_choice` | 19 | 19 | 19 | PASS |
| 合计 | 47 | 47 | 47 | PASS |

`schema_failure_witnesses` 对每个元组实际创建变异记录并调用验证器；只有捕获 `AssertionError`/`ValueError` 且错误含完整字段路径才记录见证，接受任一变异会立即抛出 `schema mutation was accepted`。单元测试再次逐项直接调用验证器，不只核对 JSON 中的计数。审计还以内存追加一个验证器本应接受的探针 `occupation.electron_count=2.0`，T-C09 随即以 `schema mutation was accepted: occupation.electron_count` 失败，证明未捕获样例不会被计数逻辑静默掩盖。

四个实际哈希字段均分别验证了两类失败：

| 哈希字段 | 坏格式 `"bad"` | 合法格式但内容错误 `"0"*64` |
|---|---|---|
| `artifacts.inputs[0].sha256` | REJECTED，`invalid SHA-256` | REJECTED，`content hash mismatch` |
| `artifacts.outputs[0].sha256` | REJECTED，`invalid SHA-256` | REJECTED，`content hash mismatch` |
| `structure.sha256` | REJECTED，`invalid SHA-256` | REJECTED，`content hash mismatch` |
| `basis.sha256` | REJECTED，`invalid SHA-256` | REJECTED，`content hash mismatch` |

内容哈希依据 `validation.seed` 和冻结合成内容重新计算，不再只验证 64 位小写十六进制外形。

M8 前选择保护包括 14 条 `M8_UNRESOLVED_PATHS`：后端 3 条、理论 6 条、自旋 3 条、占据 2 条。审计逐条替换为真实选择文本，14/14 均被拒绝并定位字段。合成白名单另外锁定 7 个值：`structure.id`、占位 `structure.species`、`basis.type/definition/id`、`sampling.kind`、`projection.method`；审计逐条替换，7/7 均被拒绝并定位字段。冻结的 19 个 `m8_choice` 变异由上述 14 条占位路径和结构 id、占位物种、基类型、采样类型、投影方法 5 条代表性白名单路径构成；其余两个 basis 白名单值由验证器静态等值约束和本次附加独立变异共同覆盖。

## 5. 静态 schema 完整性与 JSON 失败语义

`teaching_scf.py:666-897` 对 67 条路径先统一执行存在性检查，再按字段语义执行以下约束：

- 根对象、artifacts、basis cutoff、achieved metrics、轨道索引映射、投影验证对象必须为映射；输入/输出 artifacts 必须各为一个映射元素；
- 字符串标量必须非空，数值标量排除 bool、要求有限，并对电子数、容差、迭代数、维数和损失范围施加正值、整数、次序或区间约束；
- lattice、positions、k shift、k weights、projection window 必须是有限数值数组，并分别检查秩和形状；附加检查 lattice 非奇异、物种数与位置数一致、采样长度和值、投影窗口次序和源/目标维数次序；
- species、boundary、k mesh、output object、orbital ordering、atom-orbital map 和 validation commands 分别检查列表类型、元素类型、长度、唯一性或索引覆盖关系；
- 四个实际 SHA-256 同时检查格式与冻结内容重算；14 个实践字段必须为 `UNRESOLVED_M8`，真实结构/占位物种、basis、sampling、projection 受合成白名单约束；表示、环境版本和审计状态受冻结值约束。

除冻结 47 项外，本次另行注入 `NaN/Infinity` 到电子数、lattice、k weights、achieved residual 和 projection window，5/5 均被拒绝且定位字段。现有标量、数组/映射类型、数值有限性、关键形状和数组关系未发现覆盖缺口。

`run_experiments.py:370-423` 在 T-C09 JSON 中分别输出：

- 67 条路径的期望数、捕获数和完整缺失路径；
- 47 项 schema 负例总数；
- 四类 `expected_counts` 与 `captured_counts`；
- 每一项的 category、path 和实际错误见证；
- 汇总 `detected`。

任一路径删除未失败会使 `missing_path_failures` 抛错；任一 schema 变异未失败或错误未定位会使 `schema_failure_witnesses` 抛错；分类捕获数不等于期望数还会触发 `_tc09` 的显式 `require`。异常传播到 CLI，因而不能输出成功 JSON或退出码 0。该语义满足“任一未捕获即非零退出”的门槛。

## 6. T-C01—T-C08、T-C10 回归检查

两组 CLI 的十项状态与故障捕获均为真。与初审冻结证据比较，非 T-C09 指标保持一致：

| ID | 回归证据 | 判定 |
|---|---|---|
| T-C01 | 失败运行仍恰执行 12 次更新；末/初残差比 `309.1761916881516 > 10` | PASS |
| T-C02 | 振荡失败末残差 `1.3531192579224054 > 1.3` | PASS |
| T-C03 | 假能量见证密度残差 `1.316815663204585 > 1`，双判据拒绝 | PASS |
| T-C04 | 强制 20 步返回 `max_iterations`；规范扫描确定性通过 | PASS |
| T-C05 | 负例末级参考误差 `0.008000000000000007 > 0.005` | PASS |
| T-C06 | 基偏置总误差 `0.009999999999999787 > 0.005` | PASS |
| T-C07 | 忽略 overlap 的谱差 `0.9674651567663939 > 0.1` | PASS |
| T-C08 | 两配置丢失范数 `0.95985867258085`、`0.9833167163767138 > 0.9`；矩阵差 `0.23306075775057758`、`0.17451989619254055 > 0.15` | PASS |
| T-C10 | 代数尾外推误差 `0.8429707836304159 > 0.8`，直接复算与拟合门槛继续通过 | PASS |

未发现 B01 修复对原数值模型、阈值、精确更新次数、最大迭代语义、广义谱、投影或局域性测试造成回归。

## 7. README、依赖与授权边界

README 现在准确说明 67 条逐路径删除以及 47 个类型/形状/哈希/M8 选择负例，并准确给出 9/11/8/19 分类、JSON 期望数/捕获数/见证和任一接受导致非零退出的语义。其 PowerShell 解释器、版本断言、`pip check`、unittest 和两组冻结 CLI 与实际执行一致。

`requirements.txt` 仍只含 `numpy==2.3.5`、`scipy==1.18.0`，哈希与初审相同；没有新增依赖，本次复核也未安装任何包。源码仍仅使用标准库、NumPy 和 SciPy，没有 DeepH/DFT 后端调用、网络下载、正式数据或正式标签生成。README 继续明确：M7-I 通过后才准备 M8 决策，M8 冻结后，M9 正式安装、数据下载或复现实验前仍需明确授权。修复通过合成白名单加强而非放宽了该边界。

## 8. 问题计数与最终许可

| 项目 | 数量/状态 |
|---|---|
| 原阻塞 M5-CODE-B01 | `CLOSED` |
| 原审计剩余 BLOCKING | 0 |
| 本次新增 BLOCKING | 0 |
| 本次新增 NON_BLOCKING | 0 |

最终判定为 **PASS**。M5-CODE-B01 已按初审逐文件验收要求关闭，未发现回归或新缺口。因此允许 M5-08 标记为 `COMPLETED`，允许启动 M5-09。本结论仅解除 M5-08 内部门控，不授权任何 M8/M9 外部实践动作。
