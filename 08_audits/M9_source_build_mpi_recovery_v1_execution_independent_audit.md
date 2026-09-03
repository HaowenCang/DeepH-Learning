# M9 OpenMPI修复恢复独立执行事实审计

审计日期：2026-08-31。结论：PASS；blocking=0，non_blocking=0。一次性恢复已达到SUCCESS_COMMITTED，精确目标、失败证据保留、预算及实际安装只读消费均通过。此结论不是构建成功或新的编译授权；source_build_authorized=false，旧v2许可不可重放。

正式只读采集于2026-08-31T08:10:43.359088+00:00结束。本轮只新增本报告与postexecution evidence，未调用run、recover、preflight、permit或其他正式写入，未修改已冻结实施报告/verdict。两次UID入口验证均为预定只读动作。

## 193对象及安装闭集

以169对象失败baseline（SHA `e6f02744745837ae200998cf6d1e7701283721e8ed64c550e98d58b416f5f325`）逐项比较，实际193对象新增恰24项：private目录及17文件、public snapshot目录及5文件；无删除和未知新增。旧对象仅state、workflow、ledger及controls、manifests、/root控制根三个父目录发生规定变化。两个新增子目录的父目录nlink各加1，manifests nlink不变；其余父目录变化仅时间/大小。

private固定为 `/root/deeph-m9-control/source-build-mpi-recovery-v1`，root:root/0700，17个普通单链接文件均0600；保存九冻结来源、新manifest、实施报告/verdict、四份before-runtime和journal。每份来源逐字匹配项目冻结输入，四份before-runtime逐字匹配失败baseline。

public snapshot固定为 `/home/evan-williams/deeph-m9/controls/source-build-mpi-repair-v1`，root:1000/0550、dev:ino=2096:167879、nlink2；恰四份来源文件及snapshot_manifest，均root:1000/0440、普通单链接。manifest SHA `90541ee5d29ca5032868dc6461a6691b1e49b11fc3a4b6f7999427f7448a63e4`，全部成员字节、大小及哈希与manifest和已冻结源一致。新9项及旧12/25/16/10来源闭集再次核验通过。

原失败transaction `38a891fff6fd07675581b891766e02c6`、consumed capability、FAIL receipt、旧v2 permit/gate及所有旧snapshot均保持原inode和完整receipt；固定8项root-only及/root旧历史也原身份不变。正式193对象canonical SHA为 `ea1c2bf5ba92b11d96f59ed7b74af8e302c368418122c468fb889a6fa030c5f1`。

## Journal、唯一事件与精确目标

journal为root:root/0600、nlink1，26271 bytes，SHA `31d27bc69268a78f8093492e352d7af759162161df82dfe30e647bfeebad2fe2`。recovery_id为`m9-source-build-mpi-recovery-20260831-01`，父事务、baseline SHA、授权记录、新frozen、实施report/verdict及snapshot/派生driver全部绑定正确。六阶段依次为PREPARED、SNAPSHOT_COMMITTED、LEDGER_COMMITTED、STATE_COMMITTED、WORKFLOW_COMMITTED、SUCCESS_COMMITTED；每阶段四项post-runtime receipt均按实际首次提交阶段核对，既有receipt没有同字节换inode重绑定。终态记录source_build_authorized=false，控制过程耗时8.527947249000135秒，不新增CPU抵扣。

ledger原65261 bytes完整前缀与失败baseline相同，SHA `50334d8f6748816da3910e13fb31e12f5c31dbb9048871b2493a17785802b706`。在原ledger inode上恰追加1494 bytes、一个SOURCE_BUILD_MPI_RECOVERY事件；event_id唯一，绑定父事务及其哈希、原ledger前缀、授权/独立权威、全部CPU/GPU及credits，明确不授权source_build。当前ledger共66755 bytes，没有其他新增事件。

独立从失败raw对象和journal固定UTC/权威重新计算目标bytes，与实际state/workflow/ledger完全一致。state仅解除hard-stop、更新last_event_utc并新增恢复标记；workflow仅解除hard-stop、改为SOURCES_PREPARED并新增恢复标记。历史hard_stop_reason/utc保留，活动事务为空；失败transaction原文件仍FAILED_COMMITTED，没有改成成功事务。

| 当前对象 | bytes | SHA-256 |
| --- | --- | --- |
| budget_state | 2291 | `3523f0d17ccc2168289c5992db691441dd68eb3f09dde3e73de12a4a2ec80560` |
| workflow | 905 | `4438c7fce6b5d94268b12d9f2c17876bf6b4f100c22c4610ba215b3c6d1862fa` |
| 失败transaction | 2345 | `2920d80e431992cc8a23abe409d2d513b7a567e44651382d09a82b8af085161d` |
| ledger | 66755 | `8dfbb2bb9f23ac9066b457553c2bccfa94a2ab7dde5d66f6315595caaa793421` |

## 实际UID1000与前后零写

通过runuser真实UID1000、冻结Python3.9.23 `-I -S -B`，从正式固定snapshot路径执行adapter的verify-toolchain，退出0、stderr为空、status=PASS、build_executed=false。实际读取root-owned snapshot中的原driver/common/合同并精确派生，SHA为 `5652ee35a3595f42bd3050e5825419175fc84526a421a0500559d4146f253d00`；完整14包、gcc/gfortran、两个wrapper和9工具路径检查通过。此处没有临时路径覆盖或项目副本替代正式安装入口。

按预定负例，从旧v2正式consumer执行verify-execution，退出1、stdout为空，stderr明确为`build historical namespace closure mismatch`。这证明旧v2不能消费恢复后的namespace，不是恢复失败；未调用旧consumer run，也未尝试重签许可。

每条UID命令后都重新持原budget.lock核验193对象，与命令前完整字典相等；最终四份runtime字节、journal及两棵树也不变。原锁身份保持，恢复残留tmp/staging均缺席。没有新编译permit，原v2 permit仅作历史保留。

## 预算、源码与证据边界

CPU/GPU、credits和其他预算字段逐项保持失败父态：overlap_build原始7214.469142588001秒、原抵扣7200.075310528秒、有效14.393832060000932秒、余额7185.606167939999秒；smoke/batch为0，GPU compatibility=54.84820560599999秒、training/physical_validation为0。原预算函数对1MiB预测返回violations=[]，没有因恢复重置或扩大上限。

采集时总apparent/allocated为31133232364/31458787328 bytes，overlap增量1263752633/1288966144 bytes，项目审计apparent/allocated为4075227/4481024 bytes，VHDX为28064088064 bytes。后续新增审计文件仍属于预算范围；这些读数不代替未来新门控的即时检查。

准备树与失败退休树各5319 receipts，前后完整字典及父态哈希全等，canonical分别为 `7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260`、`060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`。HDF5安装prefix、编译日志、构建/overlap产物manifest、材料运行root均缺席。未执行configure/make、自测、材料结构或训练；M9缓存扫描为0。

完整193项receipt、四份当前runtime原始字节（含完整ledger）、journal对象及原字节、唯一恢复事件、snapshot manifest、两树核验及两条真实UID命令的完整argv/stdout/stderr/退出码，保存于 `M9_source_build_mpi_recovery_v1_postexecution_evidence.json`，255850 bytes，SHA `177390748086e678d22c3f24531c5a9b326889e5acb7f3931275262cf27b2ed2`。保存后重新验证canonical及所有raw字节哈希，纳秒整数无浮点损失；可作为未来门控的独立父态证据。本报告Pandoc严格Markdown及git diff --check通过。

## 最终边界

本次最小版本化修复与一次性恢复已完成事实审计。旧v2执行FAIL及历史报告仍保持原结论；构建尚未成功，新编译consumer/launcher尚需明确绑定派生driver和恢复事实并独立审计。重新source_build必须另行取得新的单次授权，不能复用旧permit或重放pristine-only恢复。M9-DATA-B01仍OPEN，不放行材料结构、smoke/batch、GPU、训练或其他未授权动作。
