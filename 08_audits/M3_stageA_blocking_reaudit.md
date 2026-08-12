# M3-07 B-01—B-04 独立定点复核报告

## 1. 最终结论

**结论：通过。M3-07 原审计 B-01—B-04 已全部关闭，未发现新增 `BLOCKING`，允许进入 M3-08。**

本次复核不重新替代 `M3_stageA_independent_audit.md` 对正文、解析推导、物理边界和来源映射的全域审计，只独立核验其 4 项阻塞修复及必要回归。size 2 的完整 CLI 和 JSON 路径已经恢复，size 1 按已声明边界被拒绝；固定复数两轨道闭式根、SciPy 广义本征值、非幺正一致基变换和非法 overlap 均有可执行测试；P3 已形成独立可执行 Fourier 参考模块及正确重建、缺共轭配对、相位不同步三类自动测试；M3-01—06 已统一改为 `REVIEW`。两套测试共 13 项全部通过，未发现修复引入的数值、链接或状态回归。

`08_audits/progress_tracker.md` 可据本报告把 M3-07 更新为 `COMPLETED`、把 M3-01—06 恢复为 `COMPLETED`，并将 M3-08 置为 `READY`。这些状态更新不属于本次只写复核报告的权限，故本报告未代改台账。

## 2. 独立性、范围与隔离声明

复核由原 M3-07 独立审计 agent 执行；该 agent 未实施 B-01—B-04 的任何修复。只审查以下受影响文件及必要基线：

- `05_code_exercises/chapter1_generalized_eigen/experiment.py`；
- `05_code_exercises/chapter1_generalized_eigen/test_experiment.py`；
- `05_code_exercises/chapter1_generalized_eigen/README.md`；
- `05_code_exercises/chapter1_generalized_eigen/requirements.txt`；
- `06_exercises/01-deeph-problem/01.03-numerical-programming/problem/readme.md`；
- `06_exercises/01-deeph-problem/01.03-numerical-programming/solution/readme.md`；
- `06_exercises/01-deeph-problem/01.03-numerical-programming/solution/fourier_reference.py`；
- `06_exercises/01-deeph-problem/01.03-numerical-programming/solution/test_fourier_reference.py`；
- `08_audits/progress_tracker.md`；
- `00_scope/master_execution_plan.md`；
- 原审计 `08_audits/M3_stageA_independent_audit.md`。

没有修改上述文件。所有 Python 命令均设置 `PYTHONDONTWRITEBYTECODE=1` 并使用 `-B`，避免生成或更新字节码缓存。工作区不是 Git 仓库；本次项目内容写入仅限本报告。

## 3. 输入文件 SHA-256

| 文件 | SHA-256 |
|---|---|
| `05_code_exercises/chapter1_generalized_eigen/experiment.py` | `F27F1D32B88034CBFE543A07E27108AF80E4D86FA9FC7B927BEB60AA53AD363F` |
| `05_code_exercises/chapter1_generalized_eigen/test_experiment.py` | `F31DCB4642B5E7FAAB2A3A836E04427C183133657D4A7A0210F9078A53D5F701` |
| `05_code_exercises/chapter1_generalized_eigen/README.md` | `3C69FE018C8CB3784C94EA4DDE3EE5BFDDAA7418856210E90581FEB8E6F6904A` |
| `05_code_exercises/chapter1_generalized_eigen/requirements.txt` | `CC3EFBCD187C80ADDD5DB987EE90AD17BD481814985761D7B5CFAC3F0B5E10E4` |
| `06_exercises/01-deeph-problem/01.03-numerical-programming/problem/readme.md` | `C3C9A486D45ED0CFD588258683A615A983422A57B7525DDAA8289A9DD02762D7` |
| `06_exercises/01-deeph-problem/01.03-numerical-programming/solution/readme.md` | `9BBAFD0941A62DE03F8C63002F70C4AFE2C4B04ECB8C794EA857B2649865F3FE` |
| `06_exercises/01-deeph-problem/01.03-numerical-programming/solution/fourier_reference.py` | `06FDD05E8FE194D2BECA7E4DE668A2814F4AD71AF22DA4304ECC77AA35DE25E1` |
| `06_exercises/01-deeph-problem/01.03-numerical-programming/solution/test_fourier_reference.py` | `4DAD587EEA243658A048EF746EE666B4113A6F3175BB2BD9B3DF6483FB47FC30` |
| `08_audits/progress_tracker.md` | `E3C7212FC2F4C08EBD7FB7D37C96F1099787A20475D8BBD30561409F9B5CF62A` |
| `00_scope/master_execution_plan.md` | `ABAC3BF730D95D9B9E9C110471B04BAF4DABE8D8FC9A0E57A76848258689F8B0` |
| `08_audits/M3_stageA_independent_audit.md` | `2075D0B8716784BF85DB82FCA1F678D150BAF2CB4B60DD5BC18E462C86FCEDA9` |

测试完成后再次计算全部受影响源文件哈希，与本表一致。

## 4. 复现环境与命令

### 4.1 环境

```text
Python 3.12.13
NumPy 2.3.5
SciPy 1.18.0
```

该环境与 `README.md:15-19` 及 `requirements.txt` 一致。

### 4.2 全部自动测试

执行：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
& $py -B -m unittest discover -s 05_code_exercises/chapter1_generalized_eigen -p "test_*.py" -v
& $py -B -m unittest discover -s 06_exercises/01-deeph-problem/01.03-numerical-programming/solution -p "test_*.py" -v
```

结果：

- 广义本征测试：`Ran 10 tests in 0.012s`，`OK`；
- Fourier 参考测试：`Ran 3 tests in 0.001s`，`OK`；
- 两条命令退出码均为 0。

10 项广义本征测试包括原有残差、\(S\)-正交、基变换、等范数扰动、一阶余项、条件数扫描、失败样例、非厄米拒绝和全实验契约，并新增最小维数及固定两轨道闭式根测试。3 项 Fourier 测试分别覆盖正确重建、缺共轭配对和相位不同步。

### 4.3 默认 CLI 与 JSON

执行：

```powershell
& $py -B 05_code_exercises/chapter1_generalized_eigen/experiment.py
& $py -B 05_code_exercises/chapter1_generalized_eigen/experiment.py --format json
```

两条命令退出码均为 0。JSON 经 `ConvertFrom-Json` 解析，元数据为 seed `20260803`、size `6`、NumPy `2.3.5`、SciPy `1.18.0`。代表性回归结果为：

| 指标 | 结果 |
|---|---:|
| 最大归一化残差 | `2.05264214645165e-16` |
| \(S\)-正交残差 | `1.9308100497472e-15` |
| 一致基变换最大谱差 | `1.11022302462516e-16` |
| 一阶检查索引 | `2` |
| 非正定 \(S\) 拒绝 | `True` |

默认 Markdown 输出中的等范数扰动、二阶余项缩放和两类失败样例与原审计基线一致，未出现修复回归。

## 5. B-01—B-04 逐项复核

### B-01：`--size 2` 公开边界越界

**修复核对。** `experiment.py:419-425` 将一阶检查索引改为 `min(2, size - 1)`；`first_order_remainders` 返回实际 `eigenvalue_index`。`test_experiment.py:126-133` 覆盖 size 2 成功和 size 1 拒绝；`README.md:36, 52-53` 明确最小支持维数为 2。

**实际复现。**

```powershell
& $py -B 05_code_exercises/chapter1_generalized_eigen/experiment.py --size 2 --format json
& $py -B 05_code_exercises/chapter1_generalized_eigen/experiment.py --size 1 --format json
```

size 2 退出码为 0，JSON 可解析；size 为 2，一阶检查索引为 1，最大归一化残差 `9.83072588619945e-17`，\(S\)-正交残差 `8.11257302121669e-16`，基变换谱差 `1.11022302462516e-16`，两次余项比例为 `4.001125086714941` 和 `4.000563043456393`，非正定 \(S\) 被拒绝。size 1 退出码为 1，并明确给出 `ValueError: size must be at least 2`。

另对 size 2 执行 50 个种子回归：最大归一化残差 `4.0711783701309966e-16`，最大 \(S\)-正交残差 `1.1853938111129682e-15`，最大基变换谱差 `3.885780586188048e-15`，余项比例相对 4 的最大偏差 `0.006612044184280297`；全部完成。

**判定：关闭。** 最小支持维数能完整运行，最小不支持维数有明确拒绝路径，并有自动测试。

### B-02：P1 缺少闭式根—数值根可执行比较

**修复核对。** `experiment.py:81-111` 新增复数两轨道闭式根函数，保留 \(2\operatorname{Re}(ts^*)\) 和 \(|s|<1\) 条件；`test_experiment.py:135-181` 固定复数样例，比较闭式根与 SciPy，执行非幺正一致基变换，并拒绝 \(|s|=1\)。`solution/readme.md:3-11` 给出固定参数、容差和运行命令。

**实际复现。** 对 \(\varepsilon_1=-0.8\)、\(\varepsilon_2=1.1\)、\(t=0.25+0.08i\)、\(s=0.18-0.04i\) 得到：

| 检查 | 结果 |
|---|---:|
| 闭式根 | `[-0.8854103826728702, 1.109426945819868]` |
| SciPy 根 | `[-0.8854103826728702, 1.1094269458198673]` |
| 最大根差 | `6.661338147750939e-16` |
| 非幺正一致基变换最大谱差 | `6.661338147750939e-16` |
| 最大广义本征残差 | `6.754648797867556e-16` |
| \(S\)-正交残差 | `1.6113797719823678e-16` |

输入 `overlap_value=1.0` 时明确抛出 `ValueError: two-orbital overlap requires abs(overlap_value) < 1`。另对 500 组随机复数两轨道模型复算，闭式根与 SciPy 的最大差为 `3.552713678800501e-14`。

**判定：关闭。** 固定输入、闭式根、数值根、基变换、非法 overlap、命令和自动测试均达到原审计最小验收标准。

### B-03：P3 缺少相位不同步失败测试和自动测试

**修复核对。** `fourier_reference.py` 明确定义带 `phase_sign` 的有限群正反变换和固定 \(n_k=8\) 样例；`test_fourier_reference.py` 有三个独立测试；`solution/readme.md:28-40` 给出约定、文件链接、命令、三类测试和适用边界。

**实际复现。**

| 检查 | 结果 | 门槛 |
|---|---:|---:|
| 正确变换最大 \(k\) 空间厄米残差 | `4.4019612280171296e-16` | `< 1e-12` |
| 正确反变换最大重建误差 | `1.8427303745251896e-16` | `< 1e-12` |
| 删除共轭配对后的最大厄米残差 | `0.14282856857085702` | `> 1e-6` |
| 正反相位未同步的重建误差 | `0.040000000000000015` | `> 1e-6` |

新 README 中 4 个本地链接均存在，未发现断链。

**判定：关闭。** 题面规定的正确重建、缺共轭配对失败和相位不同步失败均由独立自动测试覆盖。

### B-04：M3-01—06 提前标为 `COMPLETED`

**修复核对。** `progress_tracker.md:65-70` 中 M3-01、M3-02、M3-03、M3-04、M3-05、M3-06 六项状态均为 `REVIEW`；M3-07 为 `IN_PROGRESS`，M3-08 为 `PLANNED`。`progress_tracker.md:79-82` 将四项阻塞明确记为“已修复，待独立复核”；`master_execution_plan.md:79` 也明确复核通过前不得进入 M3-08。

**判定：关闭。** 状态已重新符合 `master_execution_plan.md:20-27, 297-304` 的统一完成定义和审计纪律。复核通过后的下一次状态更新可以基于本报告进行，不构成提前完成。

## 6. 必要回归检查

| 回归项 | 结果 |
|---|---|
| 固定 Python/NumPy/SciPy 版本 | 与依赖声明一致 |
| 原广义本征 8 项测试 | 全部继续通过 |
| 新增 B-01/B-02 测试 | 2 项通过，测试总数增至 10 |
| 默认 Markdown CLI | 退出码 0，核心指标与原审计一致 |
| 默认 JSON 契约 | 可解析，元数据和结果字段完整 |
| size 2 JSON | 退出码 0，一阶索引合法、数值门槛通过 |
| size 1 | 退出码 1，明确拒绝为最小维数不足 |
| P1 固定复数样例 | 根、残差、基变换和拒绝路径通过 |
| P1 随机复数扩展 | 500 例通过 |
| P3 正确与失败路径 | 3 项测试和独立数值复算通过 |
| 新增练习链接 | 4 个本地链接全部存在 |
| M3-01—06 状态 | 全部为 `REVIEW` |
| 输入文件哈希稳定性 | 测试前后一致 |

## 7. 新增问题

**新增 `BLOCKING`：无。**

记录 1 项不阻塞建议：CLI 对 size 1 的拒绝目前以 Python traceback 呈现。其错误类型和消息明确，且 README 已声明最小维数、自动测试也验证拒绝，因此不影响 B-01 关闭；后续可选用 `argparse` 参数类型或 `parser.error` 把它改为更简洁的命令行错误信息。

## 8. M3-08 进入判定

原审计要求的四项条件均已满足：B-01—B-03 的实现与自动证据完整，B-04 的状态纪律恢复，必要回归通过，且无新增 `BLOCKING`。因此，**允许进入 M3-08 阶段 A 自测和口头解释门控**。

本报告只解除 M3-07 的局部阻塞，不预判 M3-08 的闭卷流程图、逐箭头审计表、口头说明记录和修订日志是否通过。M3 整体仍应保持 `IN_PROGRESS`，直至 M3-08 形成独立门控记录并满足主计划完成定义。
