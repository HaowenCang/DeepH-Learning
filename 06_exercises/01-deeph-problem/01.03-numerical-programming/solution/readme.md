# 01.03 数值编程题参考解答

## P1 与 P2

两轨道闭式推导、固定复数样例和随机复算见[两轨道非正交解析模型](../../../../04_derivations/chapter1_two_orbital_nonorthogonal_model.md)。可执行的广义本征求解、闭式根、可逆基变换、等范数本征投影扰动、一阶余项和失败样例见[代码练习说明](../../../../05_code_exercises/chapter1_generalized_eigen/README.md)及其 `experiment.py`、`test_experiment.py`。测试 `test_two_orbital_closed_form_and_failures` 固定使用 \(\varepsilon_1=-0.8\)、\(\varepsilon_2=1.1\)、\(t=0.25+0.08i\)、\(s=0.18-0.04i\)，要求闭式根与 SciPy 结果在绝对容差 \(10^{-12}\) 内一致，并同时检查非幺正一致基变换和 \(|s|\ge1\) 的拒绝路径。

在项目根目录运行 P1/P2 自动测试：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -c "import sys, numpy, scipy; assert sys.version_info[:3] == (3, 12, 13); assert numpy.__version__ == '2.3.5'; assert scipy.__version__ == '1.18.0'"
& $py -m unittest discover -s 05_code_exercises/chapter1_generalized_eigen -p "test_*.py" -v
```

最低核验逻辑如下：

```python
e, c = scipy.linalg.eigh(H, S)
assert np.linalg.norm(H @ c - (S @ c) * e[None, :]) < tolerance
assert np.linalg.norm(c.conj().T @ S @ c - np.eye(len(e))) < tolerance

Hp = A.conj().T @ H @ A
Sp = A.conj().T @ S @ A
ep = scipy.linalg.eigh(Hp, Sp, eigvals_only=True)
assert np.allclose(e, ep, atol=tolerance, rtol=0.0)
```

P2 的两个扰动具有相同全矩阵范数，但对目标态投影不同。因此，结果支持“全矩阵范数不足以单独决定目标能窗误差”；它不支持“矩阵误差指标无用”，也不构成真实材料、真实模型或任意扰动幅度下的普遍性能结论。

## P3 参考实现

可执行实现见 [`fourier_reference.py`](fourier_reference.py)，自动测试见 [`test_fourier_reference.py`](test_fourier_reference.py)。它采用 \(H(k)=\sum_R e^{ikR}H(R)\) 与 \(H(R)=N_k^{-1}\sum_k e^{-ikR}H(k)\)；`real_space` 的键按长度为 `n_k` 的有限周期群取模，负平移 `-1` 与键 `n_k - 1` 等价。

在项目根目录执行：

```powershell
& $py -m unittest discover -s 06_exercises/01-deeph-problem/01.03-numerical-programming/solution -p "test_*.py" -v
```

三项自动测试分别验证正确变换的 \(k\) 空间 Hermiticity 与反变换重建、删除 \(H(-R)=H(R)^\dagger\) 配对后必然失败，以及正反变换都错误使用正相位时重建必然失败。最后一项把“单独看两个函数都能运行”与“相位约定成对一致”区分开。

此例验证离散变换约定与 Hermiticity 关系，不验证连续 Brillouin 区收敛、真实轨道索引、晶格规范或 DeepH 文件接口。这些内容属于后续阶段 B 和阶段 F。
