# M6-09 阶段 D 当前总快照正式独立总审计

## 1. 审计结论

**最终判定：PASS。**

- BLOCKING：0
- NON_BLOCKING：0
- 新增问题：0
- 允许把 M6 更新为 COMPLETED：是
- 允许把 M7 更新为 IN_PROGRESS：是

阶段 D 当前快照已经满足材料完备性、可自学性、公式条件闭合、来源边界受控和技术验证可复现的总门控。第 11—14 章、D-D01—D-D07、T-D01—T-D10、五组题目与解答、综合 C-D01—C-D10、自学导航、张量追踪模板、合成代码、失败矩阵和来源台账形成了同一对象链，没有发现跨文件口径冲突或只能依赖既有分项审计才能成立的结论。

BLK-03 只涉及计算资源、正式 DFT/数据后端、DeepH 软件对象、首个材料、时间与训练预算和高级物理范围。M7 的群表示、表示推导、合成对象和随机变换验证不需要提前冻结这些实践对象，因此 BLK-03 可以安全带入 M7；它不得被解释为对任何实践方案的默许。

## 2. 独立性、权限和范围

本审计由新的独立审计 agent 执行。既有分项审计和 M6 门控包中的主 agent 预检只用于确定审计范围，没有被当作通过证据。本报告的结论来自对当前文件字节、公式、来源、代码和运行结果的重新检查。

审计期间没有修改教材、提纲、来源、推导、题解、代码、工作包、门控包、计划或进度台账；没有安装依赖、访问网络、下载数据、调用 DeepH 或 DFT 后端，也没有生成正式标签。本报告是唯一新增文件。

审计范围包括：

- M6_stageD_gate_packet.md 与 M6_stageD_work_package.md；
- 第 11—14 章各自的 sources.md、outline.md、chapter.md 和 examples.md；
- stageD_graph_conventions.md、stageD_self_study_guide.md 和 stageD_tensor_trace_template.md；
- 阶段 D 推导索引及四份推导文件，覆盖 D-D01—D-D07；
- 四章和 comprehensive 的五组成对 problem/solution，覆盖 Q11—Q14 各 10 题以及 C-D01—C-D10；
- stageD_synthetic_mpnn 下的实现、CLI、单元测试、说明和精确依赖；
- 阶段 D 五项来源快照、来源索引、中央 CSV 与 BibTeX；
- 材料建设模式、BLK-03、M8 决策停点和 M9 外部执行授权停点。

审计快照时间为 2026-08-09 22:00:23 +08:00。

## 3. 当前快照 SHA-256

### 3.1 门控、统一约定和自学材料

| 文件 | SHA-256 |
|---|---|
| 08_audits/M6_stageD_gate_packet.md | AEE30D41374A94A13BBEB7ACA968F05B967DAFA1D17E97B4DC13955626044C22 |
| 08_audits/M6_stageD_work_package.md | BF9B73A8B51F6A2FB90CE1AB88972BC0643C11D134D6F257C54F64E28488A6C7 |
| 03_textbook/stageD_graph_conventions.md | BEBC75E5390E078A523331837E667DEE532919F1620F4037E11059888D05D265 |
| 03_textbook/chapters/stageD_self_study_guide.md | 3F24ECB8B550A259C7004F3CE85CEE1A55E5E2921B60F59B3BD52524E6ED3F91 |
| 03_textbook/stageD_tensor_trace_template.md | 39C0423D7C09E7CDCC4D50FEA92F837FB5677C8D3C0A7467A98AA260A2CB51E0 |

### 3.2 第 11—14 章

| 文件 | SHA-256 |
|---|---|
| 11/sources.md | 1594B7537A4DE96C158D7F429A6F4DA6B005D86E90B2B4E40C0EADE018AE3DE4 |
| 11/outline.md | FF2D8F548CA54C88AF666B42C3E577367E6BB35C89337BE222D5E3C8FBBAC072 |
| 11/chapter.md | 4FB33A4E5CB49F4A4AC728958C047A3641D6C48600E1938E3CAF8DB268E75E88 |
| 11/examples.md | 8DD2EAC077C680F0A57BAA82265B4EFF604A9B3814C0E330F9534633C6CEBCEE |
| 12/sources.md | A237FB3F08BF68F69559E398DA31B275715DD4830E5DBE97C417CF180687F823 |
| 12/outline.md | E2E7A89994EB0F3349BE5D97A6F27E57AEF960403C73CE6D0537207F571D9E3D |
| 12/chapter.md | 6034592C3A3407DD90298B4C05C7BAD2E5464C7AEE87CDD72B698FFE03938880 |
| 12/examples.md | CC7CAE9B287A47BD42D925E5435CBC731B64C7281DA05A41C85A54C4A9DB0294 |
| 13/sources.md | A79575A44EFFB639F443F88D3A590B6442EBBE0879BCD42F362F5D1D7C2382EE |
| 13/outline.md | 984ECED6F0377B584C0B50ADF56034B77E84E0AAC321C41EA6754A160B6C9930 |
| 13/chapter.md | E613DE99535C43115873596D1F24F6A6ED6990555E9E6511960750640C8EFB61 |
| 13/examples.md | 281BFE61CFE5B35A81DEFA7DB369AD634B68AA03557FBAACE0B73D008940F248 |
| 14/sources.md | 56A8C1D49BC9586E5BB29CC1F6051F98AD6158841913531781B41E07CFCB3E52 |
| 14/outline.md | E761E53C209D6BBC4DD042F43065C03CED18BC9B2A384412A81CB168B71DBE7A |
| 14/chapter.md | F1C83F0F705C56760DDB6B17B82B19D93AFE6C46296534C39630079290BFF784 |
| 14/examples.md | 40DB4E50985E654DBFABD50DB9A1F4577AC7193AA5BFD1B85758909F7880CD80 |

### 3.3 推导和题解

| 文件 | SHA-256 |
|---|---|
| 04_derivations/stageD/README.md | AD2EDD36B524363B26EB7A8CBEEB1DD7D3629D17C5896D50BD4CE74B073A2F10 |
| 11_supervised_gradients_leakage.md | 1340AB3B01581429259BF7BC7AC13204D5CDD85854012DCC14C323099314D8CC |
| 12_permutation_aggregation.md | C550F89B728822F42693597CC7EBB27550488B9C3CBAE3D020B4C3333623EFB5 |
| 13_receptive_field_complexity.md | 94D36A0C9206D186E1D2B64AF8D3E4ED835DC2FEA2E6A9F2655F27FB67F50E93 |
| 14_periodic_enumeration_provenance.md | 18F0D6E0CD09FD510FB048B6CB05018A130C20E34DF6E2A0F0919BF3234C130F |
| 11 problem/readme.md | 424465AB60657BCD075F322D398861DA0AA07E918A08DCCB4706E6D3EA722A77 |
| 11 solution/readme.md | 7A2503ABAD80FE0091016407E90E9EF0A5EF977B3C974A01122478B60B5E45C5 |
| 12 problem/readme.md | A3A0413A7A4779683D3C547B47E35AF37EB0CD5D582F37336B7F65F983B0AFE5 |
| 12 solution/readme.md | 4F5A1FB2A93524C90D1D38943EC172BD9B19258CF0124E03CFA697D7C0AC2269 |
| 13 problem/readme.md | E2B23E61818CEB8546A7934E1AB51773230CB184D0C34B49068B1F88DEF37545 |
| 13 solution/readme.md | 059B15E8B6E124B82E7FA66B097147C76247D6496F068B96D00073E915800B9E |
| 14 problem/readme.md | 62A5377881814B91D166A9FABCC99C6768CD26040A1450C227A7B95293DBB0B5 |
| 14 solution/readme.md | 4E83D5FA6B846D5C52F9D996955AE11DE9814D3A4D013A97E32D55605B12FB88 |
| comprehensive problem/readme.md | DD7062CD0F6256CFF45E8E5DCF0F5A9F96EB6C56EAC43353D41A9B4AB267AD9C |
| comprehensive solution/readme.md | 6955546E126902C0FD0D710A9B8CB179ECD73C85AEAB838A882991BF2B00B7C2 |

### 3.4 代码、依赖和来源

| 文件 | SHA-256 |
|---|---|
| staged_models.py | B640F81C2DED530C53A42AB5D707685DBDD6A6C872687518C3CAF2C49739DDD5 |
| run_experiments.py | 32B0B8F725B8695C182D3EEA500D24708B240D74F95B2AB2AE8FFC73CFA44149 |
| test_staged_models.py | 611926403A3819DECFAD29C705AF696B0BA0EBDD3FC185549587CBE7B868F403 |
| stageD_synthetic_mpnn/README.md | A02493AEFE386C9E7823C5A8AA0C36EFC3C4F39B68823D6C87B350070FF398B8 |
| requirements.txt | CC3EFBCD187C80ADDD5DB987EE90AD17BD481814985761D7B5CFAC3F0B5E10E4 |
| 02_source_ledger/source_table.csv | 2B1BC9AA97669253F42B26790D82E38A971DA9588115763A4E1BFACAF6C4739C |
| 01_sources/bibliography.bib | D1293349ED30AACC9AEA8BAD47A443B1C75AE1746FA876B635E792FCFEBD8398 |
| stageD 来源 README | E757323A2E758275FEAD820A2FF5DEBF49CBF089226086B811394203CD3F18E3 |
| D-FND-01 本地快照 | 68FC979F3D654EEE97117BF3754BA3462D3E66FD2A9B31CCADC5F70422BC0968 |
| D-FND-02 本地快照 | 95F2810D0AB10E3934AD7DD858E816572B6A30893E7FCA19163B211F6DFE91A1 |
| D-GNN-01 本地快照 | 292E7AD701D545DADDDA470AC02C2D076F1B23D85D95589F31E6EE9EB6A9FDD8 |
| D-GNN-02 本地快照 | AE1E9A4655B8ADA5292B3DD3558DD7E18B05913106EBC36BF9F609C917F163C0 |
| D-PBC-01 本地快照 | E9B5693D1A5B4DAA25F7BF61C8F97D5F55657669581A8208E2E8637B226D0970 |

## 4. 静态、渲染和配对验证

使用 Pandoc 3.6.4，对门控冻结的 36 个核心 Markdown 逐个执行 markdown+tex_math_single_backslash 输入、HTML5/MathML 输出和 fail-if-warnings。输出保留在内存中，没有产生临时文件。

| 检查 | 独立结果 | 判定 |
|---|---:|---|
| 严格 Pandoc/MathML | 36/36 | PASS |
| MathML 节点 | 1,294 | PASS |
| 活动本地 Markdown 链接 | 59/59 存在 | PASS |
| 非法控制字符 | 0 | PASS |
| 第 11 章 outline/chapter 编号 | 28/28，同序 | PASS |
| 第 12 章 outline/chapter 编号 | 28/28，同序 | PASS |
| 第 13 章 outline/chapter 编号 | 28/28，同序 | PASS |
| 第 14 章 outline/chapter 编号 | 32/32，同序 | PASS |
| 第 11—14 章题目/解答 | 每章 10/10，一一配对 | PASS |
| C-D01—C-D10/A-D01—A-D10 | 10/10，一一配对 | PASS |

四章分别给出 6、8、8、8 个解析或手算例题，均超过至少两个例题的门槛。五组 problem 和 solution 目录均非空。检查没有把“标题存在”当作充分证据；参考解答中的公式、条件、数值阈值、失败解释和代码入口也逐项交叉核对。

## 5. 教材、对象链和来源边界

### 5.1 第 11—14 章

| 章节 | 独立判断 |
|---|---|
| 第 11 章 | 训练、验证、测试职责，结构组划分，MSE/MAE，批平均，解析梯度，有限差分，早停和新组泛化边界闭合。训练下降、逐帧低误差和合成阈值均没有被写成真实泛化或物理正确性的充分条件。 |
| 第 12 章 | 属性有向多重图、receiver-first、边与节点置换、sum/mean/max、padding、可变轨道块、完整边身份和输出 provenance 一致。节点重编号等变与三维旋转等变被明确区分。 |
| 第 13 章 | 一至三层同步普通 MPNN、消息/聚合/更新/边头、masked MSE、完整手写反向传播、感受野、置换和复杂度相互一致。全局状态、异步更新、聚合碰撞和旋转边界明确。 |
| 第 14 章 | 行晶格、规范分数坐标、周期有向多重边、逆晶格列范数界、病态晶胞阈值、最小镜像附加条件、换胞协变、完整键和 \(Lr_c\) 局部支持边界闭合。 |

跨章对象链为：结构组和帧 → 规范周期图与张量 → 同步消息传递 → 边级轨道块 → 分组评价与失败诊断。完整键、prediction、mask、block shape、局部轨道下标和实际轨道 ID 在教材、模板、题解和代码中均使用同一行映射，没有发现用浮点距离或原行号替代离散身份的回归。

### 5.2 直接来源和不得外推范围

五项阶段 D 新来源的本地快照 hash 与来源索引、中央 CSV 和 BibTeX 完全一致。对固定快照的文本抽查确认：

- D-FND-01 支持监督学习、训练/测试和泛化基础对象；
- D-FND-02 支持目标函数、梯度和优化诊断；
- D-GNN-01 支持消息函数、节点更新和读出的一般 MPNN 框架；
- D-GNN-02 支持集合函数和求和结构的置换性质，并明确其定理域条件；
- D-PBC-01 支持周期晶体的多重图动机；
- DH-01 只连接局域原子环境、原子对和 Hamiltonian 块任务。

材料没有把这些来源外推为本项目分组生成式、有限镜像盒、edge schema、轨道排序、材料体系、通用 cutoff、真实精度、DFT 后端或 DeepH 版本。有限镜像界、换胞回拉键、合成分组生成式、失败矩阵和 batch schema 均被标为直接推导或教学构造。现有证据只能支持冻结合成对象上的算法与 schema 结论，不能支持 DeepH 已安装、真实标签已验证或某材料方案已选择。

## 6. D-D01—D-D07 独立核对

| ID | 核对结果 | 关键条件和失败边界 |
|---|---|---|
| D-D01 | PASS | MSE 与 tanh MPNN 反传明确有效分量平均、矩阵形状和中心差分用途；数值梯度只作实现检查。 |
| D-D02 | PASS | 逐帧泄漏的随机效应分解保留不相关条件；协方差非零时不无条件声称误差差值符号固定；group ID 可信性另列边界。 |
| D-D03 | PASS | 求和聚合的边序不变和节点重编号等变要求参数共享、端点和边属性同步重标；不推出旋转等变。 |
| D-D04 | PASS | \(L\) 层有向前驱感受野依赖局部边、同步更新和无全局回灌；结构可达与实际非零影响分离。 |
| D-D05 | PASS | 有限镜像界要求 float64、有限正 cutoff、可逆 cell 和 \(\kappa_2(A)<10^8\)；固定小盒和一般最小镜像均被给出反例。 |
| D-D06 | PASS | 候选数、边数、MPNN 时间主项和显式 float64 激活数组分离；数组字节不冒充进程峰值。 |
| D-D07 | PASS | \(n'=n+q_i-q_j\)、回拉完整键、规范 JSON edge ID 和轨道 provenance 形成双射；原子对/距离/行号配对均被禁止。 |

推导索引可以从每项 D-D 定位到章节、例题、章节题解、综合题和 T-D 验证。七项推导的对象域、统计假设、几何条件和失效边界没有偷换。

## 7. C-D01—C-D10 完备性

| 综合题 | 独立核对 |
|---|---|
| C-D01 | 分组集合、泄漏反例、预处理边界和评价对象完整，答案给出交集算法和失败条件。 |
| C-D02 | masked MSE、全链反传、五类故障和 inactive 梯度完整；答案明确 NaN 不能靠末端乘零隔离。 |
| C-D03 | 冻结生成式、组计数、训练轨迹、test MSE/MAE、零基线、损坏目标和 CLI hash 均有答案。 |
| C-D04 | 置换方向、独立边行重排、唯一 payload/hash、完整 provenance 和旋转边界完整。 |
| C-D05 | 公共/逐原子代表变化、\(K_q\) 与逆映射、错误固定 shift 和多重边配对完整。 |
| C-D06 | 解析镜像盒、2000/5488 候选、固定小盒漏边、条件数和最小镜像边界完整。 |
| C-D07 | 八条跨原子/自镜像边、零自环、错误去重和完整 ID/几何/provenance 失败注入完整。 |
| C-D08 | 1/2/3 层同步支持、原地穿透、空入边策略和感受野失效条件完整。 |
| C-D09 | concat/padded shape、offset、NaN/大数隔离、首边双向追踪和至少十类 schema 变异完整。 |
| C-D10 | 候选、边、激活字节、T-D09/T-D10、证据边界、M8 停点和 M9 再授权完整。 |

## 8. 环境、单元测试和 CLI

固定解释器为：

- Python 3.12.13
- NumPy 2.3.5
- SciPy 1.18.0
- requirements.txt 精确固定 numpy==2.3.5、scipy==1.18.0

python -m pip check 的结果为 No broken requirements found。未安装新依赖。

独立运行 unittest discover 得到 13/13 通过，耗时约 6.1 秒。测试实际覆盖五类梯度故障、M8 边界、双配置十门控、edge ID、规范 JSON 字节、cell 条件数边界、子进程字节确定性、完整输出映射、cutoff、schema/padding/cache、版本、分组生成式和硬验证矩阵。

### 8.1 真实 stdout 字节

通过 Python subprocess.check_output 直接捕获原始 stdout bytes，而非对 PowerShell 文本重新编码：

| 配置 | 两次字节相等 | 字节数 | SHA-256 | overall_pass |
|---|---|---:|---|---|
| A / 20260806 | 是 | 12,316 | 2F45DC8C53C1E1D968B3F4633CCC8590540AB8E08667A340054F15F9F3CCA6EE | true |
| B / 20260817 | 是 | 12,373 | 88BF70A4218E2B10C8410644B7B899ECF50A6F6993E83E93C496450069693BD6 | true |

配置 A 使用 B 的 seed、配置 B 使用 A 的 seed 时均退出码 2，stdout 为空，stderr 明确指出配置要求的 seed。该行为防止改变随机对象后继续沿用冻结 hash 或阈值。

### 8.2 T-D01—T-D10 实际结果

| 测试 | A | B | 独立判断 |
|---|---|---|---|
| T-D01 | 三组交集全空；逐帧反例三组交集均含 12 个组 | 三组交集全空；逐帧反例三组交集均含 15 个组 | PASS |
| T-D02 | 132 坐标；最大相对误差 \(1.2662\times10^{-10}\) | 300 坐标；最大相对误差 \(1.1299\times10^{-10}\) | PASS；均远低于 \(10^{-5}\)，五类故障全部检出 |
| T-D03 | test MSE 0.00194424，零基线 0.151155，比例 0.01286 | test MSE 0.00501318，零基线 0.169820，比例 0.02952 | PASS；均低于 0.02 和零基线四分之一 |
| T-D04 | 节点/边残差 \(9.71\times10^{-17}/5.55\times10^{-17}\) | 均为 \(1.11\times10^{-16}\) | PASS；低于 \(10^{-12}\)，provenance 错行被拒绝 |
| T-D05 | 18 个完整键形成双射；错误固定 shift 残差 4.8 | 同左 | PASS |
| T-D06 | 解析盒和外扩盒均为 18 边；固定小盒漏 2 边 | 同左 | PASS |
| T-D07 | 8 边、4 条非零自镜像、零自环 0、按原子对仅剩 4 | 同左 | PASS |
| T-D08 | 支持集依次为 [0,1]、[0,1,2]、[0,1,2,3]；原地一层到达全部节点 | 同左 | PASS |
| T-D09 | 36/36 唯一失败；激活 2,304 bytes；NaN 哨兵 66 | 36/36 唯一失败；激活 4,608 bytes；NaN 哨兵 78 | PASS |
| T-D10 | 16/16 唯一失败；\(A_-\) 接受，\(A_0,A_+\) 拒绝 | 同左 | PASS |

T-D03 的 A 组数/样本数为 train 7/42、validation 2/12、test 3/18；B 为 9/45、3/15、3/15。A/B 初始到最终训练 MSE 分别为 0.220659→0.00222399 和 0.200629→0.00161790。损坏 test 目标的 MSE 分别为 0.989726 和 0.991141，不能被训练下降掩盖。

## 9. 独立几何、身份和 batch 复算

本节没有调用既有分项审计结论。主夹具和综合题使用另一段内存 NumPy/itertools 实现，从冻结 cell、fractional、cutoff 和 JSON 规则重新计算。

### 9.1 主夹具和镜像完备性

- 逆晶格列范数公式给出 bounds = (2,2,2)；
- 候选数为 \(4^2(2\cdot2+1)^3=2000\)；
- 距离过滤后为 18 条边；
- 外扩一层候选数为 \(4^2(2\cdot3+1)^3=5488\)，过滤后仍为 18 条边，完整键集合完全相同。

前两条稳定排序边为：

| 行 | \((i,j,n)\) | displacement | distance | edge ID |
|---:|---|---|---:|---|
| 0 | \((0,1,(-1,0,0))\) | \((-0.81,0.20,0.19)\) | 0.8556868586112564 | d54362d206f507e42d9f1b6101e590e4e837a55261f973720b5267863c0707dd |
| 1 | \((0,1,(0,0,0))\) | \((0.59,0.20,0.19)\) | 0.6513063795173513 | 38b0103093e5bd6fb440865ae7072e24e003a2d43cd50c60738ba2cc3b08e3bf |

C-D07 的两原子夹具独立枚举得到 8 条边：4 条距离 0.5 的跨原子边和 4 条距离 1 的非零自镜像边；两个零位移自环均排除。按 \((i,j)\) 去重只剩 4 条。

### 9.2 C-D04：置换和唯一身份

题面置换明确采用旧编号到新编号：

\[
\pi=[2,0,3,1].
\]

数组 new = old[order] 的取行顺序应为逆置换 order = [1,3,0,2]。旧边 \(0\leftarrow1\) 变为 \(2\leftarrow0\)，shift 和物理位移保持。规范 payload 和 SHA-256 独立重算为：

    ["stageD-edge-v1","stageD-main",2,0,-1,0,0]
    14dc675ce342830589c8b2687fbdcb4c3d88056164913163ff76a33c9812328f

代码 T-D04 中 permutation 数组采用“新行取旧行”语义，随后由 inverse 得到旧到新映射；综合解答已经明确这一方向差异，不存在同一数值数组被误当作同一映射方向的问题。

### 9.3 C-D05：换胞、符号和 \(K_q\)

对首边和题面 \(q_0=(1,-1,0),q_1=(-2,0,1)\)，独立计算：

\[
n'=(-1,0,0)+q_0-q_1=(2,-1,-1),
\]

\[
n^{\mathrm{can}}=n'-q_0+q_1=(-1,0,0).
\]

变换前后笛卡尔位移最大残差为 \(5.55\times10^{-17}\)。错误固定 shift 时分数误差为 \(q_1-q_0=(-3,1,1)\)，对应笛卡尔误差 \((-3.9,2.0,1.9)\)。因此工作包、教材、代码和答案中的符号一致。回拉完整键而非原行号、距离或 \((i,j)\) 是唯一无歧义配对。

### 9.4 轨道身份

默认有序轨道表为：

- 节点 0：syn:0:0；
- 节点 1：syn:1:0、syn:1:1；
- 节点 2：syn:2:0；
- 节点 3：syn:3:0、syn:3:1。

首边 block shape 为 (1,2)，Pmax=4 时 mask 为 [true,true,false,false]。row-major 反解得到有效局部下标 (0,0)、(0,1)，实际轨道对为 (syn:0:0,syn:1:0)、(syn:0:0,syn:1:1)。置换时搬移有序轨道表而不按新节点编号伪造轨道身份，代码和答案一致。

### 9.5 concat、padded 和污染隔离

主夹具 \((N,E)=(4,18)\) 与 C-D07 夹具 \((2,8)\) 组成 batch 后：

- concat：Ntot=6、Etot=26，第二图 offset=4；node_graph_id shape (6,)，edge_graph_id shape (26,)，prediction/component provenance shape (26,4)；
- padded：B=2、Nmax=4、Emax=18、Pmax=4；node features shape (2,4,3)，edge features shape (2,18,3)，prediction shape (2,18,4)。

对同一 padded batch 的 inactive 浮点区域分别填入 NaN、0 和 \(10^{300}\)，三次运行的两图有效 prediction 逐元素完全相同，loss 均为 0，归一化均值残差相同。把一个含 NaN 的 inactive 节点行改成 active 并同步计数后，validator 在前向读取前以 active padded fractional 非有限错误拒绝。该结果证明隔离来自 count/mask 前置切片，而不是末端乘零。

## 10. 梯度、分组评价和复杂度复核

前向层使用 receiver/sender/edge 三路消息，receiver 聚合，同步 tanh 更新；边头读取最终两端状态和边特征。反向传播按链式法则分别累积 head、update、aggregate、message 和两端节点梯度。中心差分覆盖 A/B 全部 132/300 个参数坐标；inactive 输出分量的解析梯度最大绝对值为 0。五类真实故障分别为：漏损失平均、scatter 到 sender、错误 tanh 导数、padding 梯度泄漏和输出符号翻转；两配置中均逐项超过 \(10^{-5}\) 并被检出。

分组生成式固定为 \(x=[u_g,\tau_t]+\xi\)、\(y=1.5u_g-0.7\tau_t+b_g+\epsilon\)，训练/验证/test 按结构组分开。绝对 test 阈值、零基线比例、损坏目标和 group 交集共同构成门控，避免用单一训练下降或逐帧表观误差放行。

激活估计按 \(8L(3Nd+2Ed)\) bytes 独立计算：

- A：\(8\cdot2(3\cdot4\cdot3+2\cdot18\cdot3)=2304\) bytes；
- B：\(8\cdot3(3\cdot4\cdot4+2\cdot18\cdot4)=4608\) bytes。

该口径只计算冻结的 float64 激活数组，不包含参数、输出、Python 对象或进程常驻内存。候选枚举成本、保留边数和网络成本在材料中也保持分离。

## 11. 可自学性和材料建设模式

stageD_self_study_guide.md 给出 D1—D4 依赖顺序，并实现“能力—教材—推导—代码—练习—失败样例”的正向表以及从梯度、分组、provenance、周期边、感受野、batch 和 benchmark 反查教材条件的反向表。D-D01—D-D07 和 T-D01—T-D10 均有教材、推导、题解、代码和失败入口，没有孤立能力。

stageD_tensor_trace_template.md 覆盖图对象总表、单边身份、主夹具、节点置换、边行重排、周期代表变化、concat/padded、MPNN 前后向和失败注入。模板要求先核对完整键、几何、轨道和 shape，再读取 prediction；数值接近不能替代身份一致。

材料明确说明公开参考解答不降低门控强度。学习者闭卷作答、口头解释和逐阶段自测不构成阻塞证据，但原知识范围、公式条件、题目数量、失败样例、可执行测试和独立审计均保留。因此 D-010 的模式变更在阶段 D 没有造成内容缩减。

## 12. M8/M9 边界和 BLK-03

静态扫描和运行行为均未发现 DeepH 导入、正式数据下载、DFT 标签生成、真实材料输入、DFT/数据后端选择或实践软件版本冻结。代码只依赖标准库、NumPy 和 SciPy；测试中的 subprocess 仅调用同一合成 CLI。

材料一致保留以下边界：

1. M8 前禁止安装 DeepH、下载正式训练数据、生成正式 DFT 标签或隐含选择材料体系、DFT/数据后端和 DeepH 软件对象；
2. M7 完成后还必须执行 gpt-5.6-sol、max 的 M3—M7 全量独立总审计并清零；
3. 准备进入 M8 时集中提交资源、后端、软件对象、首个材料、预算和高级物理范围，等待用户冻结；
4. M8 冻结后，在 M9 正式安装、下载、标签生成或复现实验前仍需再次取得明确执行授权。

M7 的必需范围是群作用、表示、球谐、Wigner 矩阵、张量积、轨道块协变、人工合成对象和随机变换测试。BLK-03 不改变这些理论对象的定义，也不需要真实数据或实践后端。因此它可以作为明确未决项带入 M7；任何把它在 M7 中提前具体化的实现均应视为授权边界回归。

## 13. 问题清单与门控决定

### BLOCKING

无。

### NON_BLOCKING

无。

### 新增问题

无。

### 正式门控决定

阶段 D 当前总快照满足 M6-09 的全部门控要求。正式允许：

- M6 状态由 IN_PROGRESS 更新为 COMPLETED；
- M7 状态由 PLANNED 更新为 IN_PROGRESS；
- BLK-03 以 UNRESOLVED_M8 状态带入 M7 的理论、教材、推导、合成代码和随机变换验证。

本结论不授权进入 M8，不授权任何 M9 外部动作，也不替代 M7 完成后的 M3—M7 全量独立总审计。
