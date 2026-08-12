# M3-08 阶段 A 材料完备性、可自学性与可验证性审计简报

> 门控状态：`COMPLETED`。首次独立材料审计有条件通过；B-01、B-02 经主 agent 修复后，由独立定点复核确认全部关闭，无新增或剩余 `BLOCKING`。通过证据为 `M3_stageA_material_completeness_audit.md` 与 `M3_stageA_material_blocking_reaudit.md`。

## 1. 门控目标

本门控依据 D-010 审查阶段 A 材料包是否足以支持系统自学并可由第三方复核。学习者本人闭卷作答、15 分钟口头解释和修订日志不再是通过条件；原有对象图、误差链和综合题要求全部保留，并转化为对教材、例题、练习、参考解答、代码和验证入口的覆盖要求。

M3-07 已完成正文、公式、物理、来源和代码的全域审计及阻塞定点复核。M3-08 不降低这些结论的强度，而是补充检查内容组织、学习路径、答案可定位性、失败诊断和从零复现说明。

## 2. 审计输入

独立审计者至少检查：

- `03_textbook/chapters/01_deeph_problem/chapter.md`；
- `03_textbook/chapters/01_deeph_problem/self_study_guide.md`；
- `03_textbook/chapters/01_deeph_problem/outline.md` 与 `sources.md`；
- `04_derivations/chapter1_two_orbital_nonorthogonal_model.md`；
- `05_code_exercises/chapter1_generalized_eigen/`；
- `06_exercises/01-deeph-problem/` 的全部 problem/solution 单元；
- `08_audits/M3_stageA_independent_audit.md` 与 `M3_stageA_blocking_reaudit.md`；
- `00_scope/master_execution_plan.md`、`learning_route.md`、`decisions.md` 和 `progress_tracker.md` 中 D-010 模式变更的一致性。

## 3. 必须通过的材料维度

### 3.1 知识范围与对象图

- 训练链、推理链、SCF 替代边界和逐箭头误差链在正文、综合题与参考解答中均完整；
- 算符、参考矩阵、预测矩阵、重叠矩阵、本征量和进一步物理量严格区分；
- HPRO、DeepH-dock、DeePTB 和 DeepH-R 的工作流位置与证据边界可定位；
- 原闭卷门控中的所有关键错误仍由材料量规覆盖，不因模式变更删除。

### 3.2 公式、推导与例题

- 广义厄米本征问题、`S`-归一化、基变换、Fourier、旋转协变和一阶扰动均声明成立条件；
- 两轨道非正交模型包含闭式谱、复数共轭、归一化、基变换、扰动方向与失效条件；
- 每个关键公式能够映射到来源、直接推导或明确标记的教学补充。

### 3.3 练习与参考解答

- 5 道基础题、5 道推导题、3 道编程题、2 道研究讨论题和综合门控题齐全；
- problem 与 solution 一一对应，参考解答说明机制、条件、失败边界和可执行验证；
- 自学检查题可从导航找到题目、答案和相关正文，不要求学习者提交作答；
- 参考解答不把版本相关实现外推为所有 DeepH 方法共有属性。

### 3.4 代码、自动测试与失败样例

- Python、NumPy、SciPy 版本和安装声明固定；
- 广义本征测试覆盖残差、`S`-正交、基变换、条件数、两轨道闭式根、最小维数和非正定/非厄米失败；
- Fourier 测试覆盖正确重建、缺共轭配对和相位不同步；
- 默认 CLI、JSON、边界输入和 README 命令可复现；
- 输出解释不把合成矩阵结果外推为真实材料性能。

### 3.5 可自学性与失败诊断

- 自学导航声明前置知识、顺序、每步产物、预计检查点和答案位置；
- 能力—材料—验证映射不存在孤立目标；
- 常见误解、失败样例、错误机制和修复入口可定位；
- 不依赖未安装的 DeepH 本体、正式训练数据、正式 DFT 标签或未决实践选择。

### 3.6 模式与授权边界

- M3—M7 的本人作答门槛已在计划、路线、台账、模板和决策中一致取消；
- 材料门控没有降低原知识范围和验证强度；
- M8 前禁止外部实践动作；进入 M8 与开始 M9 分别保留一次明确用户决策/执行授权。

## 4. 独立审计要求

审计必须由未实施本次模式变更的子 agent 执行。审计者只允许新增 `08_audits/M3_stageA_material_completeness_audit.md`，不得修改被审计材料。报告至少包含：

- 审计范围与独立性声明；
- 输入文件 SHA-256；
- 实际执行的测试、CLI、链接和结构检查；
- 上述六个维度的逐项判定；
- `BLOCKING` 与 `NON_BLOCKING` 列表；
- 最终结论及是否允许 M3 完成、M4 转为 `READY`。

结论为“有条件通过”时，所有 `BLOCKING` 必须由主 agent 修复，再由独立子 agent 定点复核。主 agent 不得自行把材料自检写成独立通过结论。

## 5. 通过标准

仅当材料范围完整、关键内容有参考解答、代码和失败样例可重复验证、来源与公式边界一致、D-010 在全部管理文件中无冲突，且独立报告明确给出“通过、无剩余 `BLOCKING`”时，M3-08 才能标记为 `COMPLETED`。通过后 M3 完成，按依赖顺序自主进入 M4。
