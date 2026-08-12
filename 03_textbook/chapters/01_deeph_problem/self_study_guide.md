# 第 1 章自学导航与验证地图

## 1. 使用范围

本导航把第 1 章正文、解析推导、代码练习、分类型题目、参考解答和审计边界组织成一条可重复的自学路径。它不要求学习者提交闭卷作答；作用是保证每项阶段 A 能力都有可定位的讲解、练习、答案、自动验证和失败诊断。

本章使用合成矩阵，不安装 DeepH 本体、不读取正式训练数据、不生成正式 DFT 标签，也不选择材料体系、DFT 后端或实践软件版本。

## 2. 前置知识

开始前应熟悉复向量、矩阵乘法、厄米矩阵、本征值和基础量子力学术语。非正交基、周期 Fourier 表示和广义本征扰动会在本章给出最低必要解释；更系统的推导属于阶段 B。

## 3. 建议顺序

| 步骤 | 学习材料 | 目标产物或检查 | 验证入口 |
|---|---|---|---|
| 1 | [第 1 章正文](chapter.md) 1.1—1.2 | 区分算符、参考矩阵、预测矩阵、`S`、本征量和总能量 | 正文“本节核对”；基础题 B1—B3 |
| 2 | 正文 1.3—1.4 | 重建训练链、推理链与未被替代的步骤 | 综合门控题及参考对象图 |
| 3 | 正文 1.5—1.6 | 识别基、周期、旋转、数据和误差传播条件 | 推导题 D2—D5；等范数扰动实验 |
| 4 | 正文 1.7—1.8 | 区分方法、软件接口和复现门槛 | 基础题 B5、研究题 R1—R2、综合门控题 |
| 5 | [两轨道解析模型](../../../04_derivations/chapter1_two_orbital_nonorthogonal_model.md) | 复算闭式谱、`S`-归一化、基变换和扰动方向 | 固定样例与随机复算；编程题 P1 |
| 6 | [广义本征代码练习](../../../05_code_exercises/chapter1_generalized_eigen/README.md) | 运行残差、条件数、基变换、边界与失败样例 | 10 项自动测试、默认/JSON CLI |
| 7 | [章节练习](../../../06_exercises/01-deeph-problem/README.md) | 完成 5+5+3+2 题和综合对象图题 | 对应 `solution/`；3 项 Fourier 自动测试 |
| 8 | [来源包](sources.md) 与审计报告 | 核对证据边界和未决实践选择 | M3-07 全域审计、M3-08 材料审计及其阻塞定点复核 |

## 4. 能力—材料—验证映射

| 阶段 A 能力 | 核心材料 | 练习/解答 | 自动或结构验证 |
|---|---|---|---|
| 区分对象层级 | 正文 1.2、1.8 | B1、综合门控题 | 综合题关键错误量规 |
| 解释 SCF 替代边界 | 正文 1.1、1.4 | B3、综合门控题 | 训练/推理链逐箭头表 |
| 处理非正交广义本征问题 | 正文 1.2、解析模型 | B2、D1、D5、P1 | 残差、`S`-正交、最小维数和非法 `S` 测试 |
| 解释基与 Fourier 约定 | 正文 1.5、解析模型 | D2、D3、P1、P3 | 基变换谱差、Fourier 重建与相位失败测试 |
| 解释矩阵误差传播 | 正文 1.6、解析模型 | D5、P2 | 等范数方向、目标位移和二阶余项缩放 |
| 区分方法与软件角色 | 正文 1.7 | B5、R1、R2、综合题 | 角色表与来源映射审计 |
| 限定结论边界 | 正文 1.3、1.6、1.8 | P2、R1、R2 | 失败样例、研究题答案和独立来源审计 |

## 5. 自学检查题与答案位置

阶段 A 的三类检查问题继续保留，但不要求提交作答：

- 同一算符在不同基中为何有不同矩阵：正文 1.2、基础题 B1—B2、推导题 D2；
- 矩阵 MAE 为何不能单独保证目标能窗：正文 1.6、解析模型第 5—6 节、P2 参考解答；
- 泛函、赝势、基组和轨道顺序为何改变标签或表示：正文 1.2、1.5、基础题 B4。

综合训练链与推理链的完整参考结构位于 `06_exercises/01-deeph-problem/01.05-end-to-end-object-graph-gate/solution/readme.md`。应先阅读 problem，再核对 solution，以保留练习价值；是否实际提交答案不影响材料门控。

## 6. 复现命令

固定环境为 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0。本工作区使用下列绝对解释器；其他机器应把 `$py` 替换为本机 Python 3.12.13 的绝对路径。所有命令必须继续使用同一个 `$py`，不得切换为裸 `python`：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -c "import sys; assert sys.version_info[:3] == (3, 12, 13); print(sys.version)"
& $py -m pip install -r 05_code_exercises/chapter1_generalized_eigen/requirements.txt
& $py -c "import numpy, scipy; assert numpy.__version__ == '2.3.5'; assert scipy.__version__ == '1.18.0'; print('numpy=' + numpy.__version__); print('scipy=' + scipy.__version__)"
& $py -m unittest discover -s 05_code_exercises/chapter1_generalized_eigen -p "test_*.py" -v
& $py -m unittest discover -s 06_exercises/01-deeph-problem/01.03-numerical-programming/solution -p "test_*.py" -v
& $py 05_code_exercises/chapter1_generalized_eigen/experiment.py
& $py 05_code_exercises/chapter1_generalized_eigen/experiment.py --format json
& $py 05_code_exercises/chapter1_generalized_eigen/experiment.py --size 2 --format json
```

测试输出应分别显示 10 项广义本征测试和 3 项 Fourier 测试通过。`size=1` 是声明的失败边界；非正定 `S`、非厄米 `H`、只变换 `H`、缺共轭平移块和不同步 Fourier 相位均应被拒绝或产生可检测残差。

## 7. 失败诊断地图

| 现象 | 优先检查 | 对应材料 |
|---|---|---|
| 广义本征求解失败 | `S` 是否厄米正定、维数与有限性 | 正文 1.2；代码 `validate_problem`；B2、D1 |
| 基变换后谱改变 | 是否同时变换 `H` 与 `S`，系数关系是否一致 | 解析模型第 4 节；D2；失败样例 |
| `H(k)` 不厄米 | `H(R)^†=H(-R)`、平移配对和相位符号 | 正文 1.5；D3；P3 自动测试 |
| 目标能窗误差与矩阵 MAE 不一致 | 误差相对目标子空间的投影、谱隙和 `S` 条件数 | 正文 1.6；解析模型第 5 节；P2 |
| 旋转后轨道块不一致 | 主动/被动、轨道表示、局域坐标旋回和基排序 | 正文 1.5.4；D4；综合题 |
| 方法比较结论矛盾 | 标签语义、基组、数据划分、训练预算和指标是否对齐 | 正文 1.7；R1—R2 |

## 8. 完成边界

完成本导航对应的材料建设不等于完成真实 DeepH 复现。阶段 A 只证明问题定义、对象图、基础解析关系、合成数值实验和教学验证材料完整。计算资源、正式软件、数据、材料、DFT 后端、训练预算和高级物理范围统一留到 M8 决策；M8 冻结后，开始 M9 外部动作前仍需用户明确授权。
