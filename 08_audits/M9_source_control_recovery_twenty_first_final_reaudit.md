# M9 source-control test cleanup 第二十一次最终定点复核

## 结论

本轮结论为 **PASS**：`BLOCKING=0`，`NON_BLOCKING=0`。第二十次报告唯一剩余问题 `M9-SPR-R9-B01` 已关闭。冻结正式测试现已准确覆盖真实 directory fsync、committed target file fsync、replace 后 target metadata recheck、固定 `.tmp` wrong-owner 以及字段完整但 evidence binding 不同的另一份结构合法零问题 PASS gate；各中断点均断言首次停止后的精确文件系统状态和第二次调用的幂等续提终态。独立 root 临时复现与正式测试结果一致。

依据本轮明确放行条件，主 agent 现在**仅可创建一次性 cleanup gate**。本 PASS 不授权执行该 gate，不授权 cleanup、source-control recovery、`source_prepare` 或任何其他运行时动作。

## 冻结对象与测试结果

独立复算的四项 SHA-256 与指定新冻结值完全一致：

- `06_reproduction/scripts/m9_budget.py`：`cbc3ee8aadb6f9494af4fc870fff392d53bcb72b45fa91de90f546f51f7deb5c`
- `06_reproduction/tests/test_m9_overlap_controls.py`：`0f2c86a13637ff4cec376d287e387e5dc1d317219e6afdc33cfce6812a96b91a`
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：`795a6f3816862920286f7b47ba1a7cd9b5313a1d3a4fa7ec775e37686f3bc57c`
- `06_reproduction/manifests/m9_source_control_test_cleanup_frozen_hashes.json`：`e7fd76bd71f421ab10ad44b67efb0bfc6182dc1c0014a85b01cdde34b989472b`

source frozen manifest 在测试前后均为 `17/17`，cleanup frozen manifest 在测试前后均为 `4/4`。冻结 Python `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9` 以 `-I -S -B` 运行完整测试，结果为 `61/61` 通过。

## M9-SPR-R9-B01：CLOSED

冻结测试的持久化故障矩阵将三个 `fsync` 调用明确区分：第一次为固定 `.tmp` 文件，第二次为 replace 后的 committed target file，第三次为 parent directory file descriptor。replace 后 target metadata recheck 通过在 target 已存在时令 `lstat(target)` 中断而单独覆盖。测试对每一项均先要求第一次调用停止，再核对以下现场并执行第二次调用：

- 临时文件 `fsync` 或 replace 中断：target 缺席，固定 `.tmp` 存在且保存完整 payload；第二次调用从该受控半提交状态完成 replace。
- target metadata recheck、target file `fsync` 或 directory `fsync` 中断：target 已保存完整 payload，固定 `.tmp` 缺席；第二次调用重新提交并完成持久化序列。

独立 root 临时复现分别在 `fsync` 调用计数 1、2、3 注入中断，并单独注入 replace 和 target recheck 中断。五项首次现场均与上述状态划分一致；五项第二次调用均收敛为 payload 精确匹配、root:root、mode 0600、nlink 1、固定 `.tmp` 缺席。因此测试名称、实际系统调用位置、首次状态和续提终态之间不存在错位。

wrong-owner 冻结测试通过异常 `fstat` receipt 证明函数在 truncate 前拒绝，不建立 target，并保持固定 `.tmp` 原始部分内容。独立 root 临时复现进一步使用实际 UID 1000、mode 0600、nlink 1 的 `.tmp`，相对于预期 root:root receipt 得到 `root-private atomic temporary file mismatch`；target 保持缺席，`.tmp` 的 owner 和部分内容不变。

gate replacement 矩阵现包含 non-JSON、不完整 PASS、字段完整的 alternate PASS 和删除。alternate PASS 保留原 gate 的全部合同字段，仅将 `audit_report_sha256` 改为另一 64 字符值。由于 verified inode receipt 和精确 bytes 已变化，`stage_cleanup_gate_snapshot()` 在 root 私有目录建立和 snapshot writer 调用前以 `cleanup verified gate path drift` 停止。独立临时复现确认 trust root 不存在、writer 调用次数为零。

以上新增覆盖精确满足第二十次报告对 `M9-SPR-R9-B01` 的四项最小关闭条件；实现文件本轮未变，第二十次报告已经关闭的 `M9-SPR-R19-B01` 不受影响。

## 正式现场前后不变性

完整测试和全部独立临时复现前后，五项正式 runtime SHA-256 保持：

- budget state：`1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`
- workflow：`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`
- transaction：`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`
- ledger：`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`
- capability：`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`

伪 transaction 前后均为 SHA-256 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`、1644 bytes、UID/GID 1000、mode 0644、nlink 1。retired、retirement receipt、cleanup journal、cleanup gate、source-control gate 和 source-control parent 均保持不存在。正式 `/root/deeph-m9-control/source-control-test-cleanup` 在初检和终检均不存在。控制脚本目录中的 `.pyc`、`.pyo` 和 `__pycache__` 合计为零。

## 放行边界

稳定问题 `M9-SPR-R9-B01` 为 CLOSED，审计总计 `BLOCKING=0`、`NON_BLOCKING=0`。主 agent 可以依据本报告创建一次性 cleanup gate，但本报告自身没有创建或执行 gate。gate 创建后仍须遵守其冻结绑定和一次性用途；任何 cleanup 执行及其后续独立审计均是另一个明确授权阶段。本 PASS 不扩展到 source-control recovery、`source_prepare` 或其他运行时动作。

本轮除新增本报告外未修改任何被审对象；未创建或执行 gate，未整理、移动或写入正式运行时对象。全部故障恢复复现均位于自动删除的临时目录。
