# DeepH 系统学习项目

本目录用于组织从电子结构基础、几何深度学习到 DeepH 方法复现与研究改进的系统学习。M3—M7 采用“材料建设模式”：只有在教材、推导、例题、练习与参考解答、代码、自动测试、失败样例和独立审计达到明确标准后，才进入依赖阶段；学习者闭卷作答、口头解释和逐阶段自测不再构成阻塞门槛。

## 当前状态

2026-09-03最新事实：v4唯一`source_build`在HDF5 `make check`期间受WSL实例shutdown外部中断；独立中断审计已将该非终态事实冻结为`FAIL/BLOCKING=1/NON_BLOCKING=0`，旧v4 permit、operation和consumed capability均不得重放。恢复v2实施经修复后由独立子agent定点复核为`PASS/0/0`；主端随后各执行一次零写preflight和机械recover，recover返回`RECOVERY_SUCCESS_COMMITTED`且`source_build_authorized=false`。恢复执行事实独立审计的事实更正版为`PASS/0/0`：事务已按`138.401802566`秒保守墙钟上界提交为`FAILED_COMMITTED`，state/workflow恢复为非hard-stop的`SOURCES_PREPARED`，7,621项中断BUILD和4项日志完成归档，5,319项干净BUILD得到重建，预算、抵扣及全部历史证据保留。当前下一门控是建立全新的版本化source-build消费链并接受独立审计；尚未签发或消费新构建许可。见[恢复主端执行记录](08_audits/M9_source_build_wsl_shutdown_recovery_v2_execution_record.md)和[恢复执行事实独立审计](08_audits/M9_source_build_wsl_shutdown_recovery_v2_execution_independent_audit.md)。

收尾状态：v5 source-build 消费链实施包已经完成并冻结，26成员清单 SHA 为`124beb3e1734caf7e4660b7377f5b3187b3932b74fa6edfd74acb3d72b2ebe40`，主端自动测试57/57通过。依用户关于套餐额度的暂停要求，当前固定为`PENDING_INDEPENDENT_IMPLEMENTATION_AUDIT`；尚未启动独立实现审计，正式WSL中未创建v5 snapshot、gate或permit，也未执行新的source_build、结构计算、数据生成或训练。后续恢复点是对[v5冻结清单](06_reproduction/manifests/m9_source_build_v5_frozen_hashes.json)和[v5工作包](08_audits/M9_source_build_v5_work_package.md)进行独立实现审计。

历史事实：v3独立实施、安装及[执行前复核](08_audits/M9_source_build_v3_preexecution_audit.md) 均通过PASS/0/0。唯一冻结source_build在HDF5 `make check -j1`期间因宿主整机关机而外部中断：Windows事件1074记录2026-08-31 23:23:35由Explorer发起关机，HDF5日志于23:23:45以`Terminated`截止。该中断已由独立子代理封存（[中断事实审计](08_audits/M9_source_build_v3_interruption_independent_audit.md)），不作为构建PASS或普通FAIL。见[上次执行记录](08_audits/M9_source_build_v3_execution_record.md)。

当前实施进展：v3编译消费链及19文件来源清单已通过 [独立实施审计](08_audits/M9_source_build_v3_implementation_audit.md)，零问题；一次零写预检及机械安装均退出0，正在进行独立安装事实审计。尚未签发编译许可或启动编译。详见 [主安装记录](08_audits/M9_source_build_v3_installation_record.md) 和 [当前执行状态](08_audits/M9_current_execution_status.md)。机械安装成功不能替代真实UID1000入口的独立验收。

2026-08-31最新授权更新：用户已批准本任务后续所需执行权限及新增权限需求，同时明确保留按程序独立审核的阶段门控。[D-019持续授权](00_scope/D019_standing_execution_authorization.md) 及 [授权解释独立复核](08_audits/M9_standing_execution_authorization_20260831_independent_review.md) 已登记；解释复核PASS不代表编译门控PASS。当前不再等待人工编译批准，而是建立和独立验收新的编译消费链。后续恢复、重试不重复申请人工权限，仍保留停机、修复、独立复核、新单次机器许可及全部历史计量。以下早期记录中的“需另行授权”描述其历史时点，当前人工授权以D-019为准。

**M0：范围与前置知识基线**、**M1：可审计文献地图**、**M2：第 1 章资料包与三级提纲**和 **M2-I：第 1 章独立内容审计**已经完成。项目已建立学习目标、七阶段能力路线、46 条结构化来源记录、DeepH 问题演化树、版本注册表、关键论断台账，以及第 1 章的论证结构、公式审计项、解析例子和练习设计；其中 22 条是 M1 完成时的历史基线，后续阶段已扩展至当前 46 条。第 1 章所需的电子结构教材、广义厄米本征问题、正交化、一阶微扰资料以及原始 DeepH 正文与补充材料页码已经核定。

**M3：阶段 A 定稿与门控**已经完成。1.1—1.8 节正文、两轨道非正交解析模型、广义本征数值实验、15 道分类型练习、端到端综合材料题和自学导航均已形成。修订后的 M3-08 独立材料审计提出的两项阻塞均已由主 agent 修复并经独立定点复核关闭；无剩余 `BLOCKING`。

**M4：非正交基与周期表示**、**M5：DFT 与标签语义**、**M6：普通 MPNN 与周期图**和 **M7：群表示与等变网络**已经完成。M7-11 阶段 E 正式独立总审计为 `PASS`、问题为 0；D-011/M7-I 的全量审计经修复和同一审计员定点复核后也为 `PASS`。M8 已按 D-013 冻结，M9 已由 D-014 单独取得执行授权；M9-01—03 已通过，WSL、DeepH 环境及官方 graphene 发布数据已经就位。

截至 **2026-08-30**，M9-04 的官方 ZIP、安全解包、逐文件清单和 450 结构合同已经完成，但发布包缺少 overlap，`M9-DATA-B01` 仍为 `OPEN`，尚不能进入正式训练与物理验收。D-017 仅授权受限 overlap-only OpenMX 路线；D-018 已将总墙钟策略改为 `UNLIMITED`，不重置或增加 CPU、GPU、存储预算，保留全部历史用量和证据。Python 3.9 源码准备失败后的恢复及替代 consumer 安装均已通过独立审计。用户随后明确授权一次 `source_prepare`，签发与执行前独立验收通过后已执行一次，退出码0，事务为 `SUCCESS_COMMITTED`，工作流为 `SOURCES_PREPARED`；[执行后独立事实审计](08_audits/M9_source_prepare_py39_fresh_execution_independent_audit.md) 为 `PASS/BLOCKING=0/NON_BLOCKING=0`。该次计量6.231787957秒，当时尚未开始后续编译、结构计算或训练。该次源码准备授权不包括 `source_build`；Hamiltonian、SCF 和其他 DFT 标签生成仍未授权。

此后用户批准建立编译门控，通过审计后执行一次冻结编译及自测。v1安装事实审计因8项root-only权限验证问题为FAIL/1/0。用户随后明确批准保留v1及旧权限，建立v2修复门控。截至2026-08-31，v2实施、[独立安装事实审计](08_audits/M9_source_build_v2_installation_audit.md) 和 [执行前复核](08_audits/M9_source_build_v2_preexecution_audit.md) 均为PASS/0/0，218项独立测试通过。主端随后执行唯一冻结命令一次，但在OpenMPI完整版本字符串比较处失败：绝对路径调用输出`/usr/bin/mpicc:`，合同预期`mpicc:`，版本均为4.1.2。未进入HDF5配置或编译，事务为FAILED_COMMITTED，工作流HARD_STOP；[执行记录](08_audits/M9_source_build_v2_execution_record.md) 保留完整事实。此次计量1.567928485秒，全部历史用量和证据保留，不重置预算、不自动恢复或重试。当时按失败规则暂停，随后经另行授权完成下述修复与恢复；新的编译执行仍需单独申请授权，下载、结构计算或训练未放行。

该次 [v2执行事实独立审计](08_audits/M9_source_build_v2_execution_independent_audit.md) 为FAIL/BLOCKING=1/NON_BLOCKING=0，问题编号`M9-SB-V2-EXEC-B01`；此历史结论及失败证据保持不变。用户随后明确批准最小版本化修复、真实工具链回归与一次性恢复，现已完成，独立实施审计和 [恢复执行事实审计](08_audits/M9_source_build_mpi_recovery_v1_execution_independent_audit.md) 均为PASS/0/0。当前state/workflow不再hard-stop，workflow=SOURCES_PREPARED，原失败事务原位保留；193对象、两树、账本原前缀及预算历史均已独立核验，实际已安装修复snapshot的真实UID1000完整工具链检查通过。

本次没有重编译。新的编译consumer/launcher尚需绑定修复后driver和恢复事实并独立验收；依据D-019可在门控通过后签发新单次机器许可并执行source_build，无须再次人工批准。旧v2许可和一次性恢复不得重放。M9及M9-DATA-B01尚未完成。当前执行状态以 [M9 当前状态补充记录](08_audits/M9_current_execution_status.md) 及其引用的独立事实审计为准。主执行计划、进度台账和decisions已作为consumer来源证据冻结，暂保留其历史字节；D-019追加记录新的人工授权，但不自动修改预算或技术合同。

## 导航

- [D-019持续执行授权与独立门控边界](00_scope/D019_standing_execution_authorization.md)
- [D-019授权解释独立复核](08_audits/M9_standing_execution_authorization_20260831_independent_review.md)
- [M9 当前执行状态与授权边界](08_audits/M9_current_execution_status.md)
- [M9 OpenMPI修复及恢复独立事实审计](08_audits/M9_source_build_mpi_recovery_v1_execution_independent_audit.md)
- [M9 OpenMPI修复及一次性恢复主执行记录](08_audits/M9_source_build_mpi_recovery_v1_execution_record.md)
- [M9 v2 单次编译前置失败执行记录](08_audits/M9_source_build_v2_execution_record.md)
- [M9 单次源码准备独立执行事实审计](08_audits/M9_source_prepare_py39_fresh_execution_independent_audit.md)
- [M9 consumer gate 安装独立执行事实审计](08_audits/M9_py39_consumer_gate_completion_execution_independent_audit.md)
- [学习目标](00_scope/learning_goal.md)
- [主执行计划](00_scope/master_execution_plan.md)
- [前置知识依赖图](00_scope/prerequisite_map.md)
- [分阶段学习路线](00_scope/learning_route.md)
- [本地来源快照与出处](01_sources/README.md)
- [未决事项](00_scope/unresolved_decisions.md)
- [决策记录](decisions.md)
- [来源台账模板](02_source_ledger/source_table.csv)
- [DeepH 方法谱系与文献地图](02_source_ledger/literature_map.md)
- [论断与来源登记](02_source_ledger/claims_and_sources.md)
- [软件版本注册表](02_source_ledger/version_registry.md)
- [教材目录](03_textbook/outline.md)
- [第 1 章资料包](03_textbook/chapters/01_deeph_problem/sources.md)
- [第 1 章三级提纲](03_textbook/chapters/01_deeph_problem/outline.md)
- [第 1 章正文工作稿](03_textbook/chapters/01_deeph_problem/chapter.md)
- [第 1 章自学导航与验证地图](03_textbook/chapters/01_deeph_problem/self_study_guide.md)
- [第 1 章两轨道非正交解析模型](04_derivations/chapter1_two_orbital_nonorthogonal_model.md)
- [第 1 章广义本征与扰动代码练习](05_code_exercises/chapter1_generalized_eigen/README.md)
- [第 1 章练习与参考解答](06_exercises/01-deeph-problem/README.md)
- [第 1 章独立审计简报](03_textbook/chapters/01_deeph_problem/independent_audit_brief.md)
- [统一记号](03_textbook/notation.md)
- [阶段门控记录模板](08_audits/stage_gate_template.md)
- [项目进度台账](08_audits/progress_tracker.md)
- [M1 文献地图审计](08_audits/M1_literature_map_audit.md)
- [M2 第 1 章提纲就绪审计](08_audits/M2_chapter1_outline_readiness_audit.md)
- [M2 资料缺口关闭记录](08_audits/M2_source_gap_closure.md)
- [M2-I 独立审计送审前检查](08_audits/M2I_independent_audit_preflight.md)
- [M2-I 第 1 章独立内容审计报告](08_audits/M2I_chapter1_independent_content_audit.md)
- [M2-I B-01 独立定点复核报告](08_audits/M2I_B01_targeted_reaudit.md)
- [M3-07 阶段 A 独立审计报告](08_audits/M3_stageA_independent_audit.md)
- [M3-07 阻塞项独立定点复核](08_audits/M3_stageA_blocking_reaudit.md)
- [M3-08 阶段 A 材料审计简报](08_audits/M3_stageA_gate_packet.md)
- [M3-08 阶段 A 材料独立审计报告](08_audits/M3_stageA_material_completeness_audit.md)
- [M3-08 阻塞项独立定点复核](08_audits/M3_stageA_material_blocking_reaudit.md)
- [M4 阶段 B 材料建设工作包](08_audits/M4_stageB_work_package.md)
- [M4-01 工作包独立审计](08_audits/M4_stageB_work_package_independent_audit.md)
- [M4 阶段 B 正式总审计](08_audits/M4_stageB_final_independent_audit.md)
- [M6 阶段 D 正式总审计](08_audits/M6_stageD_final_independent_audit.md)
- [M7 阶段 E 正式总审计](08_audits/M7_stageE_final_independent_audit.md)
- [M7-I 阶段 A—E 全量独立总审计](08_audits/M7I_stageA_E_full_independent_audit.md)
- [M7-I 历史审计格式勘误与哈希迁移台账](08_audits/M7I_historical_audit_format_corrections.md)
- [M7-I 全量独立定点复核](08_audits/M7I_stageA_E_full_blocking_reaudit.md)
- [M9-04 官方 graphene 数据契约独立审计](08_audits/M9_data_contract_independent_audit.md)
- [M8 实践方案集中决策包](00_scope/M8_decision_package.md)
- [阶段 B 统一表示与 Fourier 约定](03_textbook/stageB_conventions.md)
- [第 2 章资料包与三级提纲](03_textbook/chapters/02_quantum_states_operators_matrices/outline.md)
- [第 2 章正文工作稿](03_textbook/chapters/02_quantum_states_operators_matrices/chapter.md)
- [第 2 章二能级解析例题](03_textbook/chapters/02_quantum_states_operators_matrices/examples.md)
- [第 2 章练习与参考解答](06_exercises/02-stageB/02_basis/problem/readme.md)
- [第 2 章参考解答](06_exercises/02-stageB/02_basis/solution/readme.md)
- [M4-02 第 2 章独立内容审计](08_audits/M4_chapter2_independent_content_audit.md)
- [M4-02 阻塞项独立定点复核](08_audits/M4_chapter2_blocking_reaudit.md)
- [第 3 章资料包与三级提纲](03_textbook/chapters/03_nonorthogonal_generalized_eigen/outline.md)
- [第 3 章广义本征与正交化核心推导](04_derivations/stageB/03_generalized_eigen.md)
- [第 3 章正文](03_textbook/chapters/03_nonorthogonal_generalized_eigen/chapter.md)
- [第 3 章例题](03_textbook/chapters/03_nonorthogonal_generalized_eigen/examples.md)
- [第 3 章练习](06_exercises/02-stageB/03_generalized_eigen/problem/readme.md)
- [第 3 章参考解答](06_exercises/02-stageB/03_generalized_eigen/solution/readme.md)
- [M4-03 第 3 章独立内容审计](08_audits/M4_chapter3_independent_content_audit.md)
- [M4-03 阻塞项独立定点复核](08_audits/M4_chapter3_blocking_reaudit.md)
- [第 4 章正文](03_textbook/chapters/04_periodicity_bloch_reciprocal/chapter.md)
- [第 4 章例题](03_textbook/chapters/04_periodicity_bloch_reciprocal/examples.md)
- [第 4 章 Bloch/Fourier 推导](04_derivations/stageB/04_bloch_fourier.md)
- [第 4 章练习](06_exercises/02-stageB/04_bloch_fourier/problem/readme.md)
- [第 4 章参考解答](06_exercises/02-stageB/04_bloch_fourier/solution/readme.md)
- [M4-04 第 4 章独立内容审计](08_audits/M4_chapter4_independent_content_audit.md)
- [M4-04 非阻塞项独立定点复核](08_audits/M4_chapter4_nonblocking_reaudit.md)
- [第 9 章正文](03_textbook/chapters/09_realspace_hamiltonian_bands/chapter.md)
- [第 9 章例题](03_textbook/chapters/09_realspace_hamiltonian_bands/examples.md)
- [第 9 章实空间到能带推导](04_derivations/stageB/09_realspace_to_bands.md)
- [第 9 章练习](06_exercises/02-stageB/09_realspace_bands/problem/readme.md)
- [第 9 章参考解答](06_exercises/02-stageB/09_realspace_bands/solution/readme.md)
- [第 4 章资料包与三级提纲](03_textbook/chapters/04_periodicity_bloch_reciprocal/outline.md)
- [第 9 章资料包与三级提纲](03_textbook/chapters/09_realspace_hamiltonian_bands/outline.md)
- [M5 阶段 C 材料建设工作包](08_audits/M5_stageC_work_package.md)
- [M5 阶段 C 正式总审计定点复核](08_audits/M5_stageC_final_blocking_reaudit.md)
- [M6 阶段 D 材料建设工作包](08_audits/M6_stageD_work_package.md)
- [M7 阶段 E 材料建设工作包](08_audits/M7_stageE_work_package.md)
- [阶段 E 统一表示约定](03_textbook/stageE_representation_conventions.md)
- [阶段 E 自学导航](03_textbook/chapters/stageE_self_study_guide.md)
- [阶段 E 表示追踪模板](03_textbook/stageE_representation_trace_template.md)
- [阶段 E 推导总索引](04_derivations/stageE/README.md)
- [阶段 E 合成代码说明](05_code_exercises/stageE_synthetic_equivariance/README.md)
- [阶段 E 综合问题](06_exercises/05-stageE/comprehensive/problem/readme.md)
- [阶段 E 综合参考解答](06_exercises/05-stageE/comprehensive/solution/readme.md)
- [阶段 D 统一图、周期与张量约定](03_textbook/stageD_graph_conventions.md)
- [阶段 D 本地来源快照](01_sources/documentation/stageD/README.md)
- [阶段 C 自学导航](03_textbook/chapters/stageC_self_study_guide.md)
- [阶段 C 标签语义模板](03_textbook/stageC_label_semantics_template.md)
- [阶段 C 推导总索引](04_derivations/stageC/README.md)
- [阶段 C 自动验收说明](05_code_exercises/stageC_teaching_scf/README.md)
- [阶段 C 综合问题](06_exercises/03-stageC/comprehensive/problem/readme.md)
- [阶段 C 综合参考解答](06_exercises/03-stageC/comprehensive/solution/readme.md)

## 推进原则

项目中的内容应区分五类证据状态：原始资料明确陈述、由已列公式直接推出、教学性补充、实现层面的推测、尚待验证。软件命令、配置字段、数据格式和版本兼容性必须以所针对的仓库提交或发布版本为边界，不混用旧版 PyTorch 实现与新版实现。

教材章节按“资料定位 → 概念依赖检查 → 三级提纲 → 初稿 → 公式与物理审计 → 代码审计 → 练习 → 定稿”推进。训练损失下降不能单独构成复现成功；最终验证至少应覆盖矩阵性质、对称性、下游能带误差、数据划分和计算成本。
