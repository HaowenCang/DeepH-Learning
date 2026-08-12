# 阶段 C 教学 SCF、表示与局域性自动验收

## 1. 范围

本目录实现 M5 工作包冻结的 T-C01—T-C10。全部输入均为解析、有限维或合成对象；不安装或调用真实 DFT/DeepH 后端，不下载正式数据，不生成正式标签，不选择材料、泛函、赝势、基、投影软件或实践版本。

- teaching_scf.py：固定点、非线性教学密度、广义谱、投影、schema 和局域矩阵原语；
- run_experiments.py：十项门控、正例/故障注入强制断言和单一确定性 JSON；
- test_teaching_scf.py：两组冻结配置、确定性、精确 12 步、最大迭代失败、逐路径删除，以及类型/形状/哈希/提前 M8 选择负例矩阵；
- requirements.txt：精确固定的 Python 用户态依赖。

## 2. 固定环境与依赖

已验证环境：

- Python 3.12.13；
- NumPy 2.3.5；
- SciPy 1.18.0。

缺失依赖时，按用户授权使用同一用户态解释器安装。复现命令为：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -c "import sys; assert sys.version_info[:3] == (3, 12, 13)"
& $py -m pip install --requirement .\05_code_exercises\stageC_teaching_scf\requirements.txt
& $py -c "import numpy, scipy; assert numpy.__version__ == '2.3.5'; assert scipy.__version__ == '1.18.0'"
& $py -m pip check
```

本次实现未安装新增包；现有固定环境已满足 requirements。若未来增加依赖，必须使用精确双等号版本并把实际安装命令、版本断言和 pip check 结果追加到本文件。

## 3. 自动测试与两组冻结 CLI

在项目根目录执行：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m unittest discover -s .\05_code_exercises\stageC_teaching_scf -p 'test_*.py' -v
& $py .\05_code_exercises\stageC_teaching_scf\run_experiments.py --format json --seed 20260805 --model-size 12 --grid-size 64
& $py .\05_code_exercises\stageC_teaching_scf\run_experiments.py --format json --seed 20260806 --model-size 16 --grid-size 48
```

三条命令均须以退出码 0 结束。JSON 顶层固定输出：

- conventions_version = stageC-v1；
- backend = synthetic；
- Python/NumPy/SciPy 版本；
- seed、model_size、grid_size；
- T-C01—T-C10 的模型参数、实际指标、容差和预期失败证据；
- overall_pass。

墙钟时间、临时路径、随机 UUID 和无序对象不进入规范 JSON。相同配置的排序键 JSON SHA-256 必须完全一致。

## 4. T-C01—T-C10 映射

| ID | 正例 | 强制失败 |
|---|---|---|
| T-C01 | 三维线性映射、\(\alpha=0.8\)、速率 0.6、零误差第 0 步 | \(\alpha=2\) 恰执行 12 次更新，谱半径 1.8，残差增长 |
| T-C02 | 两分量密度、\(\alpha=0.25\)、约束与残差 | \(\alpha=1\) 两周期，归一化保持也不得通过 |
| T-C03 | 密度残差与能量变化双判据 | \(10^{-12}\) 能量缩放使 energy-only 误通过 |
| T-C04 | 五个 \(\alpha\) 扫描与规范 JSON 哈希 | 20 步后返回 max_iterations，不得静默收敛 |
| T-C05 | 五层正收敛序列 | 32/64 局部假平台被多层参考误差拒绝 |
| T-C06 | 周期积分的采样轴 | 固定 \(10^{-2}\) 基偏置不能被采样收敛掩盖 |
| T-C07 | 一致合同变换后的广义谱与残差 | 忽略 overlap 的普通谱被拒绝 |
| T-C08 | 正交投影、回投与丢失范数 | 等谱但固定坐标矩阵差大于 0.15 |
| T-C09 | stageC-label-v1 完整合成记录 | 67 条路径逐条删除均失败；47 个类型/形状/哈希/M8 选择对抗变异均被拒绝并定位字段 |
| T-C10 | 指数/代数族的截断三指标与指数斜率 | 短窗指数拟合外推代数尾残差大于 0.8 |

## 5. T-C09 schema 边界

REQUIRED_PATHS 是正式实现中的单一必填路径集合，包含数组内部的 uri_or_path 与 sha256 成员。验证器检查：

- 顶层、后端、制品、结构、理论、基、自旋、采样、占据、收敛、表示、投影和验证字段；
- 全部标量、数组和映射的类型；数值数组的有限性；lattice、positions、边界、采样、表示、投影窗口等形状及数组间长度关系；
- 四个实际制品/结构/基身份字段的真实 64 位小写十六进制 SHA-256，并与冻结的合成内容逐项重算一致；
- 后端、理论、自旋和占据实践字段保持 UNRESOLVED_M8；结构身份与占位物种、基、采样和投影字段只能取冻结的合成白名单值；
- 每条路径删除后必须失败，错误消息包含完整缺失路径。

T-C09 还实际执行 47 个对抗变异：9 个错误类型、11 个错误形状或数组关系、8 个坏格式/内容哈希以及 19 个提前 M8 选择。JSON 分别报告各类期望数、捕获数、字段路径和错误见证；任一变异被接受都会使 CLI 非零退出。

schema 通过只证明语义字段存在，不证明矩阵、能带或物性正确。

## 6. 失败与授权边界

退出码 0 只表示全部正例达到冻结阈值且全部预期失败真实执行并被捕获。出现以下任一情况必须非零退出：

- 正例超出容差；
- 预期失败未被拒绝；
- JSON 含 NaN/Infinity 或不确定字段；
- schema 删除样例或类型/形状/哈希/M8 选择变异被接受；
- model_size 小于 12 或 grid_size 小于 48；
- 任何实践字段在 M8 前被改成真实选择。

M7-I 全量审计通过后才准备 M8 决策。M8 冻结后，在 M9 正式安装 DeepH、下载正式数据或开始复现实验前仍需明确执行授权。
