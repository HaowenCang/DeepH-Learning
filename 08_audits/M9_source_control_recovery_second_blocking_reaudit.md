# M9 source-control recovery 第二次阻塞项复核

## 结论

本轮定点复核结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。上一报告的 `M9-SPR-IMP-B01`、`B02`、`B03` 与 `B06` 已关闭；`M9-SPR-IMP-B04` 与 `B05` 仍为 OPEN。当前不得创建 source-control recovery gate，不得执行 `overlap-recover-source-control-failure`，也不得重试 `source_prepare`。

## 冻结对象与只读边界

本轮最终送审对象及独立复算值为：

- `06_reproduction/scripts/m9_budget.py`：SHA-256 `3a7ac73ad26f08c90e31eadd58ea3de345b084816bb575350c5e4fa93192cb7d`；
- `06_reproduction/tests/test_m9_overlap_controls.py`：SHA-256 `cbafb788e2991ca66f4cd68cc1dfcdcaf40a5d1bc507dbabe3c76ed7917844d7`；
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：SHA-256 `9e21c5ee7c195c2bcd32ea5680a96d97d738012da5ea2147ee852272e9070b73`。

冻结清单登记的 17 个执行对象逐项复算为 `17/17` 匹配。固定 Python 3.9 以 `-I -S -B` 运行测试得到 `32/32` PASS，AST 解析 `2/2` PASS，控制目录未发现 `__pycache__`。这些结果说明冻结闭集和既有测试一致，但不能替代下述状态机穿透。

审计未创建 gate、recovery transaction 或 parent snapshot，未执行恢复 CLI，未改写 WSL 状态、capability、ledger、dpkg 数据库或 source/build 对象。对崩溃断点的复核全部在临时目录和 mock 状态上完成。

## 上轮阻塞项逐项复核

### M9-SPR-IMP-B01：CLOSED

source-control verifier 现将 `audit_report_path` 规范解析，并要求其直接位于项目 `08_audits` 目录且后缀为 `.json`；同时继续要求结构化 `verdict=PASS`、`blocking=0`、`non_blocking=0` 和报告 SHA。自由目录 JSON 不再能够充当 gate 审计证据。

### M9-SPR-IMP-B02：CLOSED

`SOURCE_RECOVERY_PRODUCTS` 已包含 `/home/evan-williams/deeph-m9/software/openmx-overlap-build.staging`，并保留最终 build root、HDF5 prefix 和三个 manifest；既有 `overlap-only-OpenMX` 与 `DeepH-pack` 输入仓库没有被误列为应不存在的产物。新增测试检查 staging 被包含而两个只读源码仓库被排除。当前失败事实下的只读 preflight 也已独立运行通过，固定事务、capability path/ID/bytes/SHA/UID/GID/mode 均可闭合。

### M9-SPR-IMP-B03：CLOSED

parent snapshot 现采用临时文件后原子替换；正式 snapshot 已存在时必须与固定父事务逐字节一致，不能静默覆盖。PREPARED journal 记录 snapshot SHA 与 bytes；resume 会核验正式 snapshot 存在、字节等于当前固定父事务、SHA 与 bytes 等于 journal。新增负例验证 snapshot 漂移被拒绝。该关闭结论限于 snapshot 本身；状态、workflow 和 ledger 的阶段提交问题归入 B04。

### M9-SPR-IMP-B04：OPEN

实现已增加父事务、parent snapshot 和 ledger event-set 核验，也允许 ledger 处于“父集合”或“父集合加唯一同载荷 recovery event”两种状态。但是四阶段状态机仍不能从所有自身可能产生的断点幂等恢复。

独立临时目录重放了如下合法断点：recovery 为 `SUCCESS_PENDING_COMMIT`，目标 ledger event 已提交，budget state 已从 HARD_STOP 恢复，而 workflow 仍保持父 HARD_STOP。这正是代码依次写 `STATE_PATH`、再写 `OVERLAP_WORKFLOW_STATE` 时可能发生的中断。`source_control_resume` 返回 125，并调用 hard stop，原因是 `source_control_recovery_state_drift`；它没有识别该合法半提交并完成 workflow。这仍违反“每个 journal 写入点中断后可重放”的最小关闭条件。

首次成功路径仍复制一套提交逻辑，而非调用 `source_control_resume` 或公共 commit 函数。首次路径不会记录 resume 路径产生的 `post_state_sha256`、`post_workflow_sha256` 和 `post_ledger_sha256`。因此同一 `SUCCESS_COMMITTED` 状态具有两种证据结构。终态重复执行虽调用 resume，但 resume 会重新写 CAPABILITY_RETIRED、SUCCESS_PENDING_COMMIT 和 SUCCESS_COMMITTED，而不是先验证完整终态 receipt 后只读返回；这削弱了 append-once 终态语义。

另一个主动穿透把 `SUCCESS_COMMITTED` 的 ledger 尾部改成非法 JSON。`ledger_event_ids` 抛出未捕获的 `ValueError: budget ledger contains invalid JSON`，`source_control_hard_stop` 未被调用。也就是说，终态重放对损坏 ledger 既未给出受控失败 receipt，也未保证双 HARD_STOP。

最小关闭条件：

- 将 state/workflow 提交细分为可识别阶段，或在 journal 中先记录预期 post state/workflow 哈希，使“仅 state 已提交”和“仅 workflow 已提交”都能按精确 receipt 幂等完成；
- 首次路径与 resume 使用同一个 commit 实现并产生相同 post receipts；
- `SUCCESS_COMMITTED` 重放只读验证 parent snapshot、retired receipt、唯一 ledger event、post state/workflow/ledger 后返回，不回退重写中间态；
- ledger 解析错误、额外 event、同 ID 异载荷及 state/workflow 漂移均应受控双硬停并提交明确失败原因，不得以未捕获异常退出。

### M9-SPR-IMP-B05：OPEN

测试数量由 29 增至 32，新增了 staging 闭集、PID receipt 身份及 parent snapshot 漂移测试。这些测试有效覆盖 B02、B03 和原 `process_matches_receipt` 相邻回归，但仍未覆盖恢复状态机主体。

测试文件没有调用 root 首次成功路径，也没有覆盖 PREPARED、CAPABILITY_RETIRED、SUCCESS_PENDING_COMMIT 和 SUCCESS_COMMITTED 的成功重放；没有注入 parent snapshot 与 PREPARED 之间、capability rename 后、ledger append 后、state 写后或 workflow 写后的中断；没有验证 ledger 额外 event/损坏 JSON、state/workflow 半提交、终态 receipt、真实 retired 文件不可被 launcher 消费或 UID 1000 新 source_prepare capability 创建与消费。

因此 `32/32 PASS` 无法发现本轮实际复现的 state/workflow 半提交失败和 ledger 损坏未捕获异常。

最小关闭条件：使用临时完整状态树对 B04 所列每个阶段执行成功、断点和重放测试；对每个失败例断言 state/workflow/ledger/capability 的精确不变或规定的双 HARD_STOP 终态；至少包含首次成功与 resume 结果结构一致、终态只读幂等、半提交恢复、ledger 额外/损坏/同 ID 异载荷，以及 retired 不可消费和 UID 1000 新 capability 生命周期。

### M9-SPR-IMP-B06：CLOSED

冻结 manifest 中上一轮手工抄写错误已修复。当前 manifest 本身 SHA 与送审值一致，17 个内部对象为 `17/17` 匹配；budget controller 和测试哈希也与当前文件一致。控制目录未发现 Python cache。

本项关闭不意味着可以使用当前 manifest 创建 gate：关闭 B04、B05 必然修改 controller、测试和 manifest，届时仍需对最终候选闭集重新执行 `N/N` 复算。

## 新问题与放行判断

本轮没有另立新的问题 ID；主动穿透发现的半提交与损坏 ledger 行为均属于上一轮 B04 的未完成最小关闭条件，测试遗漏属于 B05。

当前 `BLOCKING=2`、`NON_BLOCKING=0`，结论为 FAIL。不得创建 source-control recovery gate，不得执行 recovery CLI，不得重试 `source_prepare`。B04、B05 属于既有 D-017 授权内部的控制修复，不需要新增用户路线决策。

修复后应再次独立定点复核。只有 B04、B05 均关闭、无新增问题、最终冻结闭集逐项匹配并产生唯一结构化零问题 PASS verdict 后，主 agent 才可依据该 verdict SHA 创建一次性 gate。实际 recovery 成功仍应接受只读结果复核；该放行不包含 `source_build`。

## 报告终检

本报告定稿后执行严格 Pandoc/MathML 转换、活动本地 Markdown 链接检查、UTF-8 非法控制字符扫描和最终 SHA-256 复算；结果随交付消息报告。
