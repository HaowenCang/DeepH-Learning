# M9 Python 3.9 单次 source_prepare 独立执行事实审计

审计日期：2026-08-30  
授权 operation id：`f9824f0eb63e41f19699c1114b13537e`  
实际 transaction id：`dc75dda112af553377a697f629801782`  
实际 capability id：`f58c6a5904391d5659201dabf22a787b`  
结论：**PASS / BLOCKING=0 / NON_BLOCKING=0**

## 当前结论与限制

本次已授权的唯一 `source_prepare` 成功完成。实际事务为 `SUCCESS_COMMITTED`，launcher receipt 为 `PASS`，退出码0、未超时；workflow 为 `SOURCES_PREPARED`，state/workflow 均非 hard-stop，active transaction 均为空。新准备树与冻结 OpenMX 3.9、官方3.9.9补丁、HDF5 1.12.1源码包的逐成员组合结果完全相符，makefile 与来源清单通过独立重算。

此次只完成源码准备，不等于编译成功、overlap生成、数据合同通过或训练就绪。现有 source_prepare-only adapter 和授权对象不能用于 `source_build`；编译需要另行建立并审计对应门控，且不得把本次单次授权扩展到编译、smoke、batch、GPU、训练或其他DFT动作。`M9-DATA-B01` 仍为 `OPEN`。

审计只执行实际文件读取、归档成员读取、哈希和字段比较，以及明确的只读 verifier；未执行 issuer、adapter `main()`、source动作、重新解包、编译或计算。归档组合与makefile验证仅在内存中进行，没有在正式WSL目录重建实验。

## 证据来源与持久化

签发前完整基线为 `M9_source_prepare_py39_fresh_preexecution_baseline.json`，SHA-256 `bac5fa6f486d2e77cde4fe83703fc1745880ae15c3c915e04ee833ad506766ac`。它包含126项签发前正式对象receipt和7项原始字节，包括61826-byte ledger。签发及执行前独立报告为 `M9_source_prepare_py39_fresh_authorization_independent_audit.md`，SHA-256 `2bc82001d681c8ac6ab0afd69ffe39d3d856381d264c2954c86b8dd0be8ebbde`。

执行后独立证据为 `M9_source_prepare_py39_fresh_postexecution_evidence.json`，SHA-256 `ee4d593ddb277a252cbd3a90b0e59f94b96fc1d614e2544dde22bb5b217f8455`。该文件保存130项正式对象完整receipt、7项执行后原始字节，以及归档组合、历史退休树、账本/事务和UID1000边界验证结果。

主实施记录 `M9_source_prepare_py39_fresh_execution_record.md` 的SHA-256为 `97779de6e5b30133429a505bef87aaca10663cce40226cbfa83bfa74b71ac0f8`，已独立重算，只用于执行参数与时间线索，不作为通过结论的自证。以上基线、授权记录、payload、issuer和既有审计报告均未被本审计修改。

## 唯一事务、capability与launcher

新capability的 `budget_argv` 与用户授权记录中的完整实际命令逐token相等：固定Python3.9.23 `-I -S -B`、已安装root-owned adapter、专用operation id、`--bucket none`、`--cpu-bucket overlap_build`、1 GiB预测、布尔 `--overlap-operation`、唯一 `--overlap-action source_prepare` 和固定合同路径。没有自由子命令、结构编号、额外cwd或log参数。

capability状态为 `CONSUMED`，未消费的同id `.json` 路径缺席；capability目录相对基线只新增该id的 `.consumed.json` 与 `.launcher-receipt.json` 两文件，没有第二个新capability。两文件为UID/GID1000、0600、普通单链接文件。transaction、capability、receipt和ledger事件的事务id、capability id、action、bucket、child PID376、forecast和command SHA交叉匹配。

launcher receipt的SHA-256为 `a7bf586c444f24d3393eec69970b69b74e7f758b672c5da78a83e2ed6f696803`；已消费capability的SHA-256为 `3f0dc02a583c64dcedb160268bc0648fdcbc656b1fa395b98ebfb42adef3288e`。真实只读 `validate_launcher_receipt()` 通过。加载源恰为 `m9_openmx_build` 与 `m9_overlap_common`，均为 `FrozenSourceLoader`、`bytecode_consulted=false`，实际源码SHA与receipt及冻结清单一致。预算和launcher的isolated/no_site/dont_write_bytecode provenance相符；依赖目录在capability消费后加入，未处理 `.pth`。

计量开始UTC为 `2026-08-30T03:47:13.870348Z`，capability消费为 `03:47:14.433217Z`，launcher完成为 `03:47:20.054927Z`，计量结束为 `03:47:20.102156Z`。prepared、start、issued、consumed、completed、end顺序正确；单调钟记录的命令墙钟用时为 `6.231787957` 秒，UTC差值与其一致到正常采样偏差范围。该用时计入CPU子预算，不是对进程实际CPU指令时间的测量。

## Ledger与预算状态

独立从基线Base64恢复原61826字节ledger，与当前文件前61826字节逐字节全等；不是仅比较文件长度。尾部恰有一条2472-byte、LF结束的JSON记录，为上述唯一事务的 `OVERLAP_COMMAND/source_prepare`，退出码0。ledger当前64298 bytes，SHA-256 `0be27e9220b6597d47ee657bbe5169134118340c77a7a0af3722a4eb1ad885c2`，原inode `2096:50691` 保留，没有删除旧事件或新增第二个动作事件。

state与基线相比，仅按冻结控制器语义增加overlap_build计量和更新last_event_utc；workflow仅转为 `SOURCES_PREPARED` 并新增official manifest SHA。原控制器JSON读写对部分等值数字的int/float表现进行了规范化，不改变其数值。历史CPU抵扣、GPU用量、offline recovery用量、墙钟历史、存储基线、恢复标识、失败原因及其余字段均保留。

原始overlap_build累计从 `7206.669426146001` 增至 `7212.901214103001` 秒，增量精确对应 `6.231787957` 秒。既有非计算apt超时抵扣仍为 `7200.075310528` 秒；有效累计为 `12.825903575000666` 秒，7200秒子预算剩余 `7187.174096424999` 秒。其余overlap CPU bucket仍为0；GPU compatibility仍为 `54.84820560599999` 秒，training和physical_validation仍为0。总墙钟策略仍为 `UNLIMITED`，未重置或增加任何预算。

ledger保存的操作结束存储快照为combined apparent/allocated `31129842816/31455227904` bytes，overlap增量 `1260363085/1285406720` bytes，VHDX overlap增量 `1207959552` bytes。执行后独立UID1000只读预算检查仍无违规项；其稍后VHDX overlap读数为 `1610612736` bytes。VHDX可延迟增长，因此两个时间点不应混用；它们均低于既有10 GiB overlap增量限制。新增审计文件计入项目侧预算，以上快照不替代后续动作前的即时存储与预测检查。

## 正式命名空间与历史保留

签发前126项基线与执行后130项清单逐字段比较，差异严格为：authorization新增（已由前一签发审计确认）、official tree manifest新增、本次consumed capability与PASS receipt新增；state、workflow和当前transaction按成功事务改写；ledger追加；manifests及capability父目录时间更新。目录安全身份不变，其余所有正式对象receipt全等。授权文件自签发后未改写，仍为885 bytes、root:1000/0640、单链接、SHA `62bf44207a3f3338fce3f8b4476a0b37be97f7587d2f07148aa3978b9014b4ab`。

执行后130项完整receipt清单SHA-256为 `af17d9e05e68c30d928db3c587d58dfd80e0c69cfbc99544fa6d8edd09dc3ed9`。审计各只读阶段前后均保持该清单不变。关键执行后文件为：

| 对象 | bytes | SHA-256 |
| --- | --- | --- |
| state | 2202 | 3c57eca541fde4f9d939766940459dac7ac7058a3af899ed79154d1cf852eb3e |
| workflow | 816 | 22cd75911994b708c19d1b7bfb1da84f264513dea59a9bd795a52e44933b0d32 |
| 当前transaction | 2136 | 2efb2729126903a1cd0d2f200565a225850e2fd3a0d10256f970b208318a75d6 |
| official manifest | 291096 | 00b244438bc8c66ab5daf208874c4fd1ed2ba5fc69ffd2dda87436eccc47f1a7 |

`/manifests/overlap_transaction.json` 是滚动的当前事务槽，现已保存新SUCCESS事务，不能声称旧失败事务的原路径和inode不变。旧失败事务的2347原始字节仍完整保存在root-private recovery failure snapshot及已落盘preexecution baseline中，SHA保持 `0a982e876e43768c6069fdeafd07e6e43ae03be3b1a0abc8584aa8d137bbcae7`；二者与本轮执行前的失败事务逐字节相等。旧已消费capability、FAIL launcher receipt、recovery gate/journal/transaction及D-017/D-018历史证据的正式receipt均不变。

旧失败退休树 `/home/evan-williams/deeph-m9/software/openmx-overlap-build.failed-80e28da82f076f4f7b1811f5897216bd.retired` 已重新逐文件哈希：140目录、5179普通文件、5319记录、619112384 apparent bytes、632029184 allocated bytes，规范inventory SHA为 `0c0389f29f3a87e26af3c884b13bcc7c6dc6f183b50d803b9affa5fbd4e3920e`，与recovery transaction封存值完全一致。新源码准备没有清理或覆盖该失败现场。

历史bootstrap/snapshot的5/27声明成员闭集、v2 bootstrap/snapshot的5/28声明成员闭集及成员字节继续通过。refresh journal仍为 `SUCCESS_COMMITTED`，active/retired receipt与签发前值完全一致。25-file consumer与16-file overlap来源清单及实际文件SHA全部复核通过；主计划、进度台账和decisions等旧冻结成员没有修改。

## 实际源码树、官方补丁与makefile

审计重新读取三个本地归档，逐一核验固定大小与SHA；没有解包或写入正式WSL。OpenMX基础包含1574普通成员，HDF5包含3602普通成员，官方补丁含92普通成员。拒绝归档绝对路径、越界路径、重复规范路径、链接及特殊成员，按基础包、HDF5子目录和官方补丁目标规则在内存建立预期文件/目录闭集；补丁 `kpoint.in` 映射到 `work/kpoint.in`，其他补丁成员映射到 `source`。

makefile以归档组合后的原始文本为输入，仅按冻结合同替换唯一活动CC/FC/LIB定义，使用LF结尾构建预期字节。实际makefile与该独立结果逐字节相符，SHA-256为 `1c183f9a0f69ccb2beaff4c15594ae46567c7224e42c5302f5ac96d8be6f8be2`；CC/FC中的 `-fcommon`、`-fallow-argument-mismatch`、固定MPI包装器和HDF5路径均一致。

实际 `/home/evan-williams/deeph-m9/software/openmx-overlap-build` 包含140目录、5179普通单链接文件、619112473 apparent bytes。完整文件与目录集合、每个文件大小/SHA/mode及UID/GID1000全部符合归档组合预期，没有额外或遗漏路径。全树receipt两次采集相等，SHA-256为 `7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260`；归档组合预期内容映射SHA为 `d8e6fc26b4980e4e6f8faa9233376395dc353ea145aaee3a9d289351f545b212`。

official manifest的1577条OpenMX来源路径及其字节/SHA、92条补丁写入路径、application_order、source identity与独立归档组合结果全等，并与workflow绑定SHA一致。overlap-only仓库仍为提交 `c8bd8f4e01f9f19868bf2928671c21b12272a6f7`、工作区clean；检查以实际UID1000并禁用Git可选写锁执行，没有修改safe.directory或Git配置。

完整新树中没有 `.o/.a/.so/.mod` 或 `openmx/openmx.official-3.9.9` 编译产物；HDF5安装prefix、overlap tree manifest、build manifest、OpenMX binary、结构run root及活动staging均缺席。结合已冻结source_prepare分派代码、完整实际argv、唯一ledger动作与全树精确组合，证据支持本次只执行本地源码准备，没有进入下载、编译或结构计算路径；不将该判断扩展为对整个操作系统其他进程的全局追踪结论。

## 授权终态与后续门控

执行后再次以真实UID1000、冻结Python3.9.23 `-I -S -B` 在原budget lock内调用只读授权verifier，旧参数被拒绝，原因是 `Python-3.9 recovery consumer runtime drift`；调用前后runtime不变。这是原授权绑定的preexecution runtime已被成功动作推进后的预期结果，不是对本次成功事实的否定。授权文件应保留为历史证据，不能因为它仍存在而重新执行。

另对真实adapter的纯argv解析器给入 `source_build`，被明确拒绝：`consumer adapter authorizes only source_prepare`。未调用adapter main或任何动作来测试拒绝。下一阶段不能沿用本授权或source_prepare-only adapter；应先另行设计、独立审计并取得适用授权的编译消费门控，再按既定顺序推进。

本报告和证据JSON通过结构、原始字节SHA、严格Markdown及 `git diff --check` 检查；M9源码和控制树缓存数量为0，未运行 `py_compile`。本次事实审计到 `source_prepare` 成功为止，未放行后续动作。
