# M3-08 材料审计 B-01/B-02 独立定点复核报告

## 1. 最终结论

**结论：通过。M3-08 材料审计 B-01、B-02 已全部关闭，未发现新增 `BLOCKING`。允许把 M3-08 与 M3 标记为 `COMPLETED`，并允许把 M4 置为 `READY`。**

B-01 的修复保留了阶段 C 的 SCF、自洽迭代、离散/基组、采样、收敛和失败诊断知识范围，同时把 M5 必做实现严格限定为后端无关的教学模型与合成收敛实验；真实 DFT 后端、真实材料、后端专用输入和正式标签均明确后置到 M8 冻结及 M9 再次授权之后。

B-02 的修复为本工作区指定了 Python 3.12.13 绝对解释器，并要求其他机器显式替换为本机 Python 3.12.13 绝对路径；版本预检、固定依赖安装、包版本断言、测试和 CLI 均使用同一个 `$py`。按文档顺序执行的全部命令退出码为 0，10 项广义本征测试、3 项 Fourier 测试、默认 Markdown CLI、默认 JSON 和 `size=2` JSON 均通过。

改动后的活动材料未发现未绑定裸 `python` 命令；全项目既有 Markdown 本地链接无断链；D-010 在八个管理文件中的材料模式、M8 决策暂停和 M9 再授权边界语义一致。

## 2. 独立性、权限与复核范围

本复核由原 M3-08 材料审计子 agent 执行；该 agent 未实施 B-01、B-02 修复。没有修改计划、路线、台账、教材、练习、代码、测试、依赖声明或既有审计报告。本次项目内容写入仅限新增本报告。

定点复核直接检查：

- `00_scope/learning_route.md`；
- `00_scope/unresolved_decisions.md`；
- `05_code_exercises/chapter1_generalized_eigen/README.md`；
- `03_textbook/chapters/01_deeph_problem/self_study_guide.md`；
- `06_exercises/01-deeph-problem/01.03-numerical-programming/solution/readme.md`；
- 根 `README.md`；
- `00_scope/master_execution_plan.md`；
- `decisions.md`；
- `08_audits/progress_tracker.md`；
- 原审计 `08_audits/M3_stageA_material_completeness_audit.md`；
- 执行命令所依赖的 requirements、广义本征实现/测试和 Fourier 实现/测试；
- 为核对 D-010 八文件一致性而读取的阶段门控模板和 M3-08 门控简报。

本次依赖安装命令只确认用户已授权且已经固定的 Python 用户态包；输出为 `Requirement already satisfied`。未安装 DeepH 或正式 DFT 软件，未下载正式数据，未生成正式 DFT 标签，也未选择材料体系、DFT 后端或实践软件版本。

## 3. 输入文件 SHA-256

| 文件 | SHA-256 |
|---|---|
| `00_scope/learning_route.md` | `352C853017F6E84F26B59023E5432D611BC18F48E6ED7E0E853AF809A531BACA` |
| `00_scope/unresolved_decisions.md` | `92B403FE7B09A3BB1A3A7C45F355D3498198F5DB5F2E70B711D0FAB0E24C6A60` |
| `05_code_exercises/chapter1_generalized_eigen/README.md` | `32B8DF470E0EE5DBCD41BE8A076417514996752BDEBF5263A230E4B527886B28` |
| `03_textbook/chapters/01_deeph_problem/self_study_guide.md` | `3CB76E9A6FBA6A69B30AE74A56819F36B76D61D84EE17F05FBF2D67C5ABAC3E9` |
| `06_exercises/01-deeph-problem/01.03-numerical-programming/solution/readme.md` | `82ED01A0B28F3414CA2B02559913889A0F76FFA1CB08D5F98E0AC3DF2AD15C82` |
| `README.md` | `B783D4177BFD1FFD2C6A5C8B71ABC1B75A862DC6B10DD55658A0551865DC5F76` |
| `00_scope/master_execution_plan.md` | `CEAD1FA7389057A6CD899E20DCDC1EA21AF2204AE06B7F5950E3928E68E8FE12` |
| `decisions.md` | `072992EFCA9474B738CB48E7C18F85342FDDC4ABA7D25F62EB572552E429455C` |
| `08_audits/progress_tracker.md` | `A26F533510609D3AAC20681AC2DA75D57CC594DD8F75049B16F071578BD3A926` |
| `08_audits/M3_stageA_material_completeness_audit.md` | `9E8E0CE13EC01C96EA0E426D1656A16EFA830EB28CED315D02C80991345D2802` |
| `05_code_exercises/chapter1_generalized_eigen/requirements.txt` | `CC3EFBCD187C80ADDD5DB987EE90AD17BD481814985761D7B5CFAC3F0B5E10E4` |
| `05_code_exercises/chapter1_generalized_eigen/experiment.py` | `F27F1D32B88034CBFE543A07E27108AF80E4D86FA9FC7B927BEB60AA53AD363F` |
| `05_code_exercises/chapter1_generalized_eigen/test_experiment.py` | `F31DCB4642B5E7FAAB2A3A836E04427C183133657D4A7A0210F9078A53D5F701` |
| `06_exercises/01-deeph-problem/01.03-numerical-programming/solution/fourier_reference.py` | `06FDD05E8FE194D2BECA7E4DE668A2814F4AD71AF22DA4304ECC77AA35DE25E1` |
| `06_exercises/01-deeph-problem/01.03-numerical-programming/solution/test_fourier_reference.py` | `4DAD587EEA243658A048EF746EE666B4113A6F3175BB2BD9B3DF6483FB47FC30` |
| `08_audits/stage_gate_template.md` | `D2591764CECCEF66EA14B2A71F06D92A9221610A6B5C059FD23A24B35852A98F` |
| `08_audits/M3_stageA_gate_packet.md` | `A65C69D84BE7A29D7A88BCCCA1EB40E87D928988AF2AFA085378EAEB6E5D19EA` |

测试后再次计算受执行影响的源码和文档哈希，与本表一致。

## 4. B-01 定点复核：M5 与 M8/M9 授权边界

### 4.1 修复内容

`00_scope/learning_route.md:86` 现在把最终 DFT 后端的官方理论、输出文档和后端专用细节明确归为“M8 冻结、M9 再授权后的实践扩展”，不再作为 M5 完成门槛。

`00_scope/learning_route.md:98` 现在规定：

- 必做实现是后端无关的教学级一维自洽模型；
- 必须记录迭代残差与混合参数关系；
- 用可控合成离散基/网格和有限采样点模拟基组/截断、k 点或等价采样收敛；
- 必须保留未收敛、振荡和阈值误判三类失败样例；
- M5 不选择、安装或运行真实 DFT 后端，不使用真实材料结构，不生成正式标签；
- 真实 DFT 教程和后端专用收敛研究仅属于 M8 冻结、M9 再授权后的实践扩展。

`00_scope/learning_route.md:102` 仍要求完整标签模板、教学 SCF/收敛实现、自动测试、失败样例、参考解答和独立审计。这证明修复改变的是实践授权边界，而不是降低 SCF、离散、采样、收敛和误差归因的知识或验收强度。

`00_scope/unresolved_decisions.md:3` 已增加 D-010 显式交叉引用，并把 M8 前允许范围限定为理论材料、后端无关教学实现和小型合成代码。主计划 `:159-161, 203-216`、D-010 `decisions.md:84-93`、台账 `:18, 78-86` 和根 README `:7-9` 与上述边界一致。

### 4.2 B-01 判定

**判定：关闭。** M5 不再要求 M8 前选择或运行真实 DFT 后端；SCF、离散/采样、收敛、自动测试和失败验证要求没有减少。真实后端只有在 M8 集中冻结方案并于 M9 前再次取得明确执行授权后才能进入实践。

## 5. B-02 定点复核：固定解释器与完整命令链

### 5.1 文档契约

`05_code_exercises/chapter1_generalized_eigen/README.md:15-27` 和 `self_study_guide.md:48-61` 均声明：

- Python 3.12.13；
- NumPy 2.3.5；
- SciPy 1.18.0；
- 当前工作区的 Python 绝对解释器；
- 其他机器必须替换为本机 Python 3.12.13 绝对路径；
- 不得依赖裸 `python` 的 PATH 解析；
- 版本预检、pip 安装、包版本断言、测试和 CLI 使用同一个 `$py`。

P1/P2/P3 参考解答 `solution/readme.md:7-12, 34-38` 也使用同一绝对解释器变量和版本断言，没有重新引入裸 `python`。

### 5.2 按文档顺序执行

执行：

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

全部命令退出码为 0。环境输出：

```text
Python 3.12.13, MSC v.1944, 64 bit AMD64
numpy=2.3.5
scipy=1.18.0
```

pip 输出确认 `numpy==2.3.5` 与 `scipy==1.18.0` 均已满足，没有解析为其他版本。

### 5.3 测试结果

- 广义本征测试：`Ran 10 tests in 0.011s`，`OK`；
- Fourier 测试：`Ran 3 tests in 0.001s`，`OK`。

10 项测试继续覆盖残差、S-正交、基变换、等范数不同方向、一阶余项、条件数、非法 overlap、非厄米 H、最小维数、两轨道闭式根和完整结果契约。3 项 Fourier 测试继续覆盖正确重建、缺共轭配对和相位不同步。

### 5.4 默认 CLI 与 JSON

默认 Markdown CLI 的代表性输出：

| 指标 | 结果 |
|---|---:|
| 最大归一化残差 | `2.052642e-16` |
| S-正交 Frobenius 残差 | `1.930810e-15` |
| overlap 条件数 | `1.000000e+01` |
| 一致基变换最大谱差 | `1.110223e-16` |
| 两个扰动的 Frobenius 范数 | 均为 `2.000000e-02` |
| 低能目标方向位移 | `8.889209e-03` |
| 高能正交方向位移 | `-1.110223e-16` |
| 只变换 H 的谱差 | `2.067246e+00` |
| 非正定 S | 被拒绝 |

默认 JSON 经 `ConvertFrom-Json` 解析：seed `20260803`、size `6`、NumPy `2.3.5`、SciPy `1.18.0`，最大归一化残差 `2.05264214645165e-16`，S-正交残差 `1.9308100497472e-15`，基变换谱差 `1.11022302462516e-16`，非正定 S 被拒绝。

`size=2` JSON 同样可解析：seed `20260803`、size `2`、NumPy `2.3.5`、SciPy `1.18.0`，最大归一化残差 `9.83072588619945e-17`，S-正交残差 `8.11257302121669e-16`，基变换谱差 `1.11022302462516e-16`，一阶检查索引为 `1`，非正定 S 被拒绝。

### 5.5 裸 Python 检查

对根 README、`00_scope/`、`03_textbook/`、`04_derivations/`、`05_code_exercises/` 和 `06_exercises/` 中的活动 Markdown 执行命令形态搜索，未发现以裸 `python`、`python -m pip`、`python -m unittest` 或 `python 05_code_exercises/...` 调用的活动命令。代码语言围栏和关于 Python 的普通说明不属于命令。历史审计报告中保留的旧反例是审计证据，不是活动运行指令。

### 5.6 B-02 判定

**判定：关闭。** 固定 Python 版本、绝对解释器、依赖安装、包版本断言、测试和 CLI 已形成同一可执行链，消除了 PATH 隐式状态；所有要求的实际输出均通过。

## 6. 链接与 D-010 八文件一致性

### 6.1 Markdown 链接

以 UTF-8 扫描新增本报告前全项目除 `tmp/` 外的 45 个既有 Markdown 文件。排除外部 URL、页内锚点及 2 个 LaTeX 正则假阳性后，共检查 55 个真实本地链接，断链数为 0。

### 6.2 D-010 语义一致性

八个管理文件的当前语义一致：

- 主计划与学习路线均把 M3—M7 定义为材料建设模式，不要求学习者个人闭卷、口头或逐阶段自测；
- 台账、阶段门控模板、M3-08 门控简报和 D-010 均要求材料、参考解答、自动测试、失败样例和独立审计，不降低原知识与验证强度；
- 未决事项和根 README 允许后端无关教学实现及固定 Python 用户态依赖，但继续禁止 M8 前的 DeepH/正式 DFT 实践、正式数据/标签和隐含实践选择；
- M3—M7 完成后必须在进入 M8 时暂停并由用户冻结集中方案；M8 冻结后，M9 的正式安装、数据下载、标签生成或复现实验前仍需再次取得明确授权。

未发现修复引入的状态、范围或授权冲突。

## 7. 新增问题与剩余问题

**新增 `BLOCKING`：无。**

**剩余 `BLOCKING`：无。**

原全域材料审计的非阻塞来源导航建议不属于 B-01/B-02，也不影响本次通过结论；动态软件接口继续由 M8 的版本冻结处理。

## 8. 状态更新许可

原审计的两项最小验收标准均已满足，并由独立复核实际重跑。故允许主 agent：

1. 把 M3-MAT-B01、M3-MAT-B02 记录为已关闭；
2. 把 M3-08 标记为 `COMPLETED`；
3. 把 M3 标记为 `COMPLETED`；
4. 按依赖顺序把 M4 置为 `READY` 并继续材料建设模式。

本结论不授权任何 M8/M9 外部实践动作，也不改变进入 M8 时的集中决策暂停或 M9 前的再次执行授权要求。
