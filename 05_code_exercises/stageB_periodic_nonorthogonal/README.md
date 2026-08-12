# 阶段 B 数值实现与自动验收

## 1. 范围

本目录实现 M4 工作包的 T-B01—T-B10。全部输入均为固定种子生成的合成复矩阵或教材中的一维双轨道模型；不安装 DeepH、不下载正式训练数据、不生成 DFT 标签，也不选择材料体系或 DFT 后端。

`stageb_models.py` 提供 Hermitian-definite 广义本征求解、逐本征对归一化残差、\(S\)-正交残差、一致合同变换和阶段 B 正负号约定下的 Fourier 正逆变换。`run_experiments.py` 运行十项门控并输出单一 JSON；`test_stageb_models.py` 执行默认种子、第二种子、输入拒绝、Fourier 闭合和 unitary 残差回归。

## 2. 固定环境与复现命令

已验证环境为 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0。依赖版本冻结在 `requirements.txt`。若这些依赖缺失，可在项目固定用户态运行时执行：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m pip install --requirement .\requirements.txt
```

在本目录运行自动测试和 JSON 验收：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m unittest -v test_stageb_models.py
& $py .\run_experiments.py --format json --seed 20260803 --dimension 6 --nk 64
& $py .\run_experiments.py --format json --seed 20260804 --dimension 4 --nk 32
```

命令退出码为 0 才表示全部正例达到容差且每个预期失败均被断言捕获。仅打印数值或异常不构成通过。

## 3. 测试映射

| ID | 实现与指标 | 预期失败 |
|---|---|---|
| T-B01 | 随机复 Hermitian-definite 矩阵束与逐本征对归一化残差 | 非正定 \(S\) 被拒绝，错误含 `positive definite` |
| T-B02 | \(C^\dagger SC-I\) Frobenius 残差 | 非 Hermitian \(H\) 被拒绝，错误含 `Hermitian` |
| T-B03 | 一般可逆合同变换后的广义谱 | 只变 \(H\) 的谱差超过阈值 |
| T-B04 | \(\kappa_2(S)=10^0,10^2,10^4,10^6,10^8\) 扫描 | 最小特征值阈值触发 `ill_conditioned`，不得静默归为良态 |
| T-B05 | 完整 BvK 网格上的 Fourier 正反变换 | 逆变换使用同号相位时重建失败 |
| T-B06 | 完整 \(\pm R\) 配对的全 \(k\) Hermiticity | 删除一个共轭块后反 Hermitian 残差超过阈值 |
| T-B07 | 一维双轨道全 \(k\) 广义本征残差与 \(S(k)\succ0\) | 忽略 \(S(k)\) 后能量差超过阈值 |
| T-B08 | cell-phase 与轨道中心 unitary 规范 | 只变 \(H\) 不同步变 \(S\) 时谱发生变化 |
| T-B09 | 含 \(R=0,\pm1,\pm2\) 模型的重建与截断 | 64/128 点加密均不能消除删除 \(\pm2\) 的误差 |
| T-B10 | 轨道重排、相位翻转与 unitary 子空间混合 | 置换只作用矩阵一侧时 Hermiticity 失败 |

JSON 顶层固定输出 `conventions_version="stageB-v1"`、Python/NumPy/SciPy 版本、随机种子、矩阵维数、`N_k`、全部容差、逐测试指标、预期失败捕获结果与 `overall_pass`。

## 4. 数值解释边界

T-B04 的条件数扫描只证明给定合成族和固定环境下的残差、\(S\)-正交性与诊断逻辑；不能外推为任意真实材料的误差增长律。T-B07—T-B09 的带差和截断差只用于验证对象链与失败机制，也不是任何材料的物理参数。M4-07 只验收合成数值实现，不越过 M8/M9 的软件、数据和外部计算授权边界。
