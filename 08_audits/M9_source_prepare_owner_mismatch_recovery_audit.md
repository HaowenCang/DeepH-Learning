# M9 source_prepare owner mismatch 专项追加审计

## 结论

当前结论为 **FAIL**：`BLOCKING=1`，`NON_BLOCKING=0`。现有状态机已经正确将首次 `source_prepare` 失败提交为 `FAILED_COMMITTED/HARD_STOP`，后续以 UID 1000 直接重试被拒绝也是正确行为；但是当前冻结控制代码不存在面向该控制层失败的合法恢复入口。因此现在不得手工清除 hard stop、删除或复用旧 capability，也不得直接重试 `source_prepare`。

稳定阻塞项为：

- `M9-SPR-B01`：缺少绑定失败事实、旧 capability、ledger 与无 source 产物证据的一次性 `source_prepare` 控制失败恢复合同和独立 gate。

这不是新的用户路线选择，也不改变 D-017、OpenMX/HDF5 版本、材料体系或 overlap-only 范围；属于当前受限工作包内部的控制实现修复。

## 失败状态链

失败事务 ID 为 `e5bfc046d4d5a1bd97507d37b40f1e0c`，动作是 `source_prepare`，forecast 为 `1073741824` bytes，CPU bucket 为 `overlap_build`。事务最终状态为 `FAILED_COMMITTED`，返回码 1，未超时，实际耗时 `0.715775579 s`，失败原因是 `overlap_command_failed`。

当前对象哈希如下：

- `overlap_transaction.json`：`12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`；
- `overlap_workflow_state.json`：`2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`；
- `budget_state.json`：`1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`；
- `budget_ledger.jsonl`：`25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`；
- 旧 capability：`0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`。

budget state 与 workflow 均为 hard-stopped，workflow stage 为 `HARD_STOP`，active transaction 均为空。ledger 仅包含一条绑定该事务的 `OVERLAP_HARD_STOP` 事件；失败 CPU 已追加到原始 `overlap_build`，使原始值从 `7200.075310528 s` 增至 `7200.791086107 s`。先前 D-017 adjustment 仍仅抵扣 apt 超时的 `7200.075310528 s`，因此本次失败的有效 CPU 用量为 `0.715775579 s`。该用量必须保留，不得抵扣或回滚。

## 根因与执行边界

budget 进程以 root 执行。`atomic_private_json` 写入 capability 后调用 `preserve_owner`，在 root 情形下将文件所有者改为 UID 1000。随后由同一 root budget 产生的 launcher 仍以 UID 0 运行，而 launcher 在消费前要求 capability 的 `st_uid == os.getuid()`。因此 capability 的 UID 1000 与 launcher UID 0 必然触发 `capability owner/mode mismatch`。

旧 capability ID 为 `f7c3b060e19e37e6da03f461d754d38c`。其状态仍为 `BOUND`，所有者 UID/GID 为 1000/1000，mode 为 0600；绑定的 budget PID 294 与 child PID 373 均已不存在。capability 目录中不存在对应 `.consumed.json` 或 `.launcher-receipt.json`。这表明失败发生在 capability 消费和 controller dispatch 之前。

进一步只读检查确认以下正式 source 产物均不存在：

- `/home/evan-williams/deeph-m9/software/openmx-overlap-build`；
- 同路径 `.staging`；
- `openmx_official_3.9.9_tree_manifest.json`；
- `/home/evan-williams/deeph-m9/env/hdf5-1.12.1`。

因此没有证据表明 HDF5/OpenMX 归档被本次动作解压，也没有进入 makefile 改写、补丁应用或编译阶段。

## 不允许的处理

下列处理均不满足可验证状态机合同：

- 直接编辑 `budget_state.json` 或 `overlap_workflow_state.json` 清除 hard stop；
- 删除 `overlap_transaction.json` 或覆盖失败事务；
- 删除旧 capability 以掩盖失败事实；
- 改写旧 capability 的 owner、PID、transaction ID 或状态并再次交给 launcher；
- 复用旧 capability ID 或旧事务 ID；
- 抵扣或减去本次 `0.715775579 s` CPU；
- 绕过冻结 gate 直接以 UID 1000 再次运行。

## 最小恢复合同

主 agent 可以在 D-017 受限工作包内部新增一个一次性 `source_prepare` 控制失败恢复入口，但必须先完成代码、测试、冻结哈希和新的独立 gate。恢复入口应至少满足以下条件。

恢复 preflight 必须精确绑定：

- 失败事务 ID、事务 SHA、动作 `source_prepare`、`FAILED_COMMITTED`、返回码 1、未超时和唯一失败原因；
- budget state、workflow state、ledger 字节数、SHA 和末事件；
- 当前无 active transaction，workflow 为 `HARD_STOP`；
- D-017 recovery 仍为 `SUCCESS_COMMITTED`，45 包状态仍有效；
- 旧 capability 的 ID、字节、SHA、UID/GID、mode、`BOUND` 状态、父子 PID 已死亡；
- 对应 consumed/launcher receipt 均不存在；
- build root、staging、official tree manifest 和 HDF5 prefix 均不存在。

旧 capability 不得删除。恢复事务应将其原子重命名为同目录下不可被 launcher 当作活动 capability 解析的 `.retired.json`，并验证重命名前后字节和 SHA 不变；retirement receipt 应记录原路径、新路径、owner/mode、失败事务 ID、原因和时间。恢复还应保存失败事务的只读父快照。

恢复应使用新的 recovery transaction ID 和 append-once event ID。只有 retirement、父快照与 ledger event 全部持久化成功后，才能原子提交：

- budget `hard_stopped=false`、active transaction 为空；
- workflow stage 回到 `AUDIT_PASSED`、`hard_stopped=false`、active transaction 为空；
- `apt_install_completed=true` 保持不变；
- 新增明确的 `recovered_from_source_prepare_control_failure` 字段绑定失败事务；
- 原 `hard_stop_reason` 与时间保留为历史字段，不应伪装为从未失败。

CPU 原始值和 D-017 adjustment 必须逐字保持；恢复不得新增 CPU credit。失败 source_prepare 的 `0.715775579 s` 继续计入有效 `overlap_build`。

## 防止再次发生

普通 overlap 执行入口应在 gate 验证之后、任何 transaction/state/capability 写入之前，强制要求实际 EUID 为冻结的运行用户 UID 1000；root 或其他 UID 必须无状态拒绝。这样 budget、launcher 与 capability owner 保持同一身份。离线 apt recovery 的 root-only 入口应继续独立存在，不得因这一修复放宽其 root 和 network namespace 约束。

新的 `source_prepare` 必须生成新的 transaction ID 和 capability ID。旧 retired capability 必须保留且不能被新 launcher 消费。应新增端到端负例覆盖：root 普通 overlap 无状态拒绝、旧 capability 复用拒绝、PID 存活拒绝、任一 source 产物存在拒绝、ledger/state/hash 漂移拒绝、重复 recovery 拒绝、失败后 hard-stop，以及 UID 1000 新 capability 的 owner/mode/消费/receipt 成功路径。

## 放行条件

只有在以下条件全部满足后，独立复核才可放行一次新的 `source_prepare`：

- 新恢复入口和 EUID 约束完成并通过负例测试；
- 控制脚本、测试和完整执行闭集重新冻结；
- 独立 recovery gate 绑定本报告后续的零问题 PASS 复核、失败事务和旧 capability；
- 恢复实际执行形成 `SUCCESS_COMMITTED` receipt，旧 capability 已 retired 且字节不变；
- hard stop 仅通过该入口解除，CPU 和 ledger 历史保持；
- 新的 follow-up gate 绑定恢复后的状态；
- 新 source_prepare 以 UID 1000、全新事务和 capability 通过唯一冻结入口启动。

当前最终判断：**不得重试 source_prepare；允许主 agent 实施上述最小控制恢复，但实施后必须再次独立审计。**

## 报告终检

本报告定稿后执行 UTF-8 控制字符扫描、活动本地 Markdown 链接检查，以及 Pandoc `markdown+tex_math_single_backslash` 到 HTML5 MathML 的 `--fail-if-warnings` 严格转换。最终 SHA-256 随交付消息报告。
