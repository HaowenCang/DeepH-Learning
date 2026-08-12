# 第 1 章代码练习：广义本征、基变换与扰动方向

## 练习目标

本练习用合成复厄米矩阵验证第 1 章的数值性质，不安装 DeepH，也不读取正式训练数据。交付物覆盖：

- 随机复厄米 \(H\) 与给定条件数的正定 \(S\)；
- 广义本征残差和 \(S\)-正交性；
- 一致可逆基变换下的谱不变性；
- 同 Frobenius 范数、不同目标能级后果的扰动；
- 一阶 \(\delta H-E\delta S\) 公式的二阶余项缩放；
- \(S\) 条件数扫描；
- 非正定 \(S\) 与只变换 \(H\) 的失败样例。

## 固定环境

- Python 3.12.13
- NumPy 2.3.5
- SciPy 1.18.0

本工作区审计使用下列绝对解释器路径。其他机器应把 `$py` 替换为本机 Python 3.12.13 的绝对路径；不得依赖裸 `python` 的 PATH 解析。先执行版本预检，再用同一个 `$py` 安装和运行：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -c "import sys; assert sys.version_info[:3] == (3, 12, 13); print(sys.version)"
& $py -m pip install -r 05_code_exercises/chapter1_generalized_eigen/requirements.txt
& $py -c "import numpy, scipy; assert numpy.__version__ == '2.3.5'; assert scipy.__version__ == '1.18.0'; print('numpy=' + numpy.__version__); print('scipy=' + scipy.__version__)"
```

## 运行

在项目根目录执行：

```powershell
& $py 05_code_exercises/chapter1_generalized_eigen/experiment.py
& $py 05_code_exercises/chapter1_generalized_eigen/experiment.py --format json
& $py 05_code_exercises/chapter1_generalized_eigen/experiment.py --size 2 --format json
```

默认 Markdown 输出四组结果：基线残差与基变换谱差、等范数误差传播表、一阶余项表和失败样例。JSON 输出还包含条件数扫描，以及随机种子、矩阵维数、NumPy 版本和 SciPy 版本元数据。`--seed` 与 `--size` 可以改变合成问题；默认种子为 `20260803`，默认维数为 6，支持的最小维数为 2。

## 自动测试

```powershell
& $py -m unittest discover -s 05_code_exercises/chapter1_generalized_eigen -p "test_*.py" -v
```

测试门槛包括：

- 归一化广义本征残差小于 \(10^{-13}\)；
- \(S\)-正交性 Frobenius 残差小于 \(10^{-12}\)；
- 一致基变换前后的最大谱差小于 \(10^{-12}\)；
- 一阶余项在步长连续减半时约缩小 4 倍；
- 两个扰动的 Frobenius 范数相同，但正交高能方向不移动目标最低本征值；
- 非正定 \(S\) 被拒绝；只变换 \(H\) 的错误操作产生可检测谱差。
- 最小支持维数 2 能完整运行，维数 1 在构造阶段被拒绝；
- 固定复数两轨道样例的闭式根与 SciPy 广义本征值一致，并通过非幺正一致基变换与非法 overlap 测试。

## 输入、输出与解释

`make_problem` 的输入是矩阵维数、随机种子和目标 \(S\) 条件数；输出为复厄米 \(H\) 和正定 \(S\)。`solve_generalized` 返回按升序排列的本征值与 \(S\)-正交归一本征矢。所有随机输入由显式种子生成。

误差传播表中的两个扰动具有相同全矩阵 Frobenius 范数。一个沿最低广义本征态方向，另一个沿与其 \(S\)-正交的最高能态方向。目标本征值位移不同，说明全矩阵范数不能单独确定能窗误差；这不表示矩阵误差指标无用，而是要求同时报告轨道/子空间和下游谱指标。

条件数扫描只检查求解残差和数值条件，不预设残差必须随条件数严格单调。实际误差还受矩阵尺度、舍入和求解器影响；高条件数结果应结合扰动敏感性解释。

## 失败样例

`failure_samples` 包含两个故意错误：

1. 使用 \(H'=A^\dagger H A\) 后仍保留旧 \(S\)。此时得到的谱与原谱不同，说明“基变换谱不变”要求 \(H,S\) 一致变换。
2. 构造含负本征值的 \(S\)。输入校验会在求解前拒绝该问题，避免把非定矩阵束误当作标准厄米定问题。

本练习完成 M3-05 的代码与测试交付物，但不替代 M3-07 的独立公式、物理、来源和代码审计。
