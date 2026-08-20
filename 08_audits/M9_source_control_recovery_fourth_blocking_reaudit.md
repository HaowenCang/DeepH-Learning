# M9 source-control recovery 第四次阻塞项复核

## 结论

本轮定点复核结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。`M9-SPR-IMP-B05` 已关闭：35 项测试现在能够在不改变正式 manifests inventory 的条件下完成。`M9-SPR-R3-B01` 仍为 OPEN，因为新增污染清理入口不具备 rename 后崩溃重入能力，未强制冻结解释器身份，并缺少对清理合同本身的实质测试。新增 `M9-SPR-R4-B01`：清理 receipt 没有绑定独立授权或审计 gate，root 可直接执行该破坏性状态迁移。

当前不得执行 `overlap-retire-source-control-test-artifact`，不得创建 source-control recovery gate，不得执行 recovery CLI，也不得重试 `source_prepare`。

## 冻结快照与只读边界

本轮送审对象独立复算为：

- `06_reproduction/scripts/m9_budget.py`：SHA-256 `1577296d771a014c762b19027ad55e06f42314ff0a30cf16077f43cb1e86925e`；
- `06_reproduction/tests/test_m9_overlap_controls.py`：SHA-256 `9b44c42a7cdab25635fa501c8a0cfc4b7a411fffce40dd12a7cd6efc51b966c0`；
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：实测 SHA-256 `fb6b55a07a36976a439de56335f5809a42843ce91e55b3acc9485da4a64b4460`。

冻结清单登记的 17 个对象为 `17/17` 匹配。审计未执行正式污染清理、未创建 gate、未执行 recovery CLI、未重试 `source_prepare`。清理崩溃穿透完全在临时目录中完成。

## 原阻塞项复核

### M9-SPR-IMP-B05：CLOSED

两个直接调用 `source_control_resume` 的测试现在都把 `SOURCE_CONTROL_RECOVERY_TRANSACTION` 指向临时目录；其中会执行真实写入的半提交测试不再触及正式 transaction。

本轮在运行完整 35 项测试前，独立枚举 `/home/evan-williams/deeph-m9/manifests` 两层内全部普通文件并记录排序后的路径与 SHA。基线为 16 个文件，inventory SHA-256 为 `da7a70872325012249580e0daf35f5c48badac055b5879505e80cdfeffc440518`。固定 Python 3.9 以 `-I -S -B` 运行得到 `35/35 PASS`；测试后重新枚举仍为 16 个文件，inventory SHA 相同，前后清单字节完全一致。正式伪 transaction 也保持原 SHA，未再次被测试覆盖。

因此，上轮“测试自身写入正式 runtime”的隔离缺口已关闭。该结论只针对当前 35 项测试；后续新增任何调用 mutation helper 的测试仍应维持测试前后正式 inventory 不变门控。

### M9-SPR-R3-B01：OPEN

新增 `overlap-retire-source-control-test-artifact` 具备若干正确约束：root-only、`budget.lock` 排他锁、固定伪文件 SHA/bytes/UID/GID/mode、正式 source gate/parent snapshot absent、五个真实运行对象固定 SHA、同目录原子 rename、retired SHA/bytes 核验及私有 receipt。这些约束能拒绝普通漂移。

但清理事务仍不是崩溃可重放的。当前顺序是先 `os.replace(artifact, retired)`，再写 retirement receipt；入口开头又规定 retired 或 receipt 任一存在即拒绝。临时目录主动注入“rename 成功后 receipt 写入抛出 OSError”，实际得到：原 artifact 不存在、retired 存在、receipt 不存在；再次执行立即报 `test-artifact retirement is one-shot and already recorded`。该状态既不能自动补写 receipt，也不能证明清理完整，恰好重现上一报告要求避免的 rename/receipt 窗口。

入口还没有调用 `isolated_bootstrap_provenance()`。因此只要 EUID 为 root，系统其他 Python 即可运行此公开子命令；它不受 D-017 已冻结的 Python 3.9 `-I -S -B` 身份、no-site 和 sys.path 约束。对修改正式运行态的清理入口，这一差异不能接受。

新增测试 `test_source_control_artifact_retirement_requires_exact_receipt` 只断言两个常量文件名，不调用清理函数，也没有验证 root、锁、精确伪 receipt、五对象漂移、gate/parent present、rename receipt、崩溃重入或重复成功。因此当前 35/35 不能支撑清理合同。

最小关闭条件：

- 在锁内、任何状态读取或写入前调用冻结解释器公共 bootstrap，严格要求 Python 3.9 `-I -S -B`；
- 引入 journaled `PREPARED -> ARTIFACT_RETIRED -> SUCCESS_COMMITTED` 清理事务，或使“retired 存在且 receipt 缺失”可按精确原 receipt、retired receipt 和五对象 SHA 幂等补提交；
- 若 original 与 retired 同时存在、两者均不存在、retired 内容漂移或 receipt 同 ID 异内容，必须拒绝且不改变真实五对象；
- 成功 receipt 绑定 original/retired path、bytes、SHA、UID/GID/mode、五对象 SHA、gate/parent absent、冻结代码/manifest/授权 SHA、阶段和时间；重复调用在验证完整成功 receipt 后只读返回；
- 用完整临时 manifests 树执行成功、全部漂移、rename 后崩溃重入、receipt 写后重放和错误解释器零写入测试，并继续执行正式 inventory 前后不变门控。

## 新增阻塞项

### M9-SPR-R4-B01：清理动作缺少独立授权与审计 gate

清理入口是对正式运行态的不可忽略迁移：它将占用正式 recovery transaction 文件名的对象移走，并创建新的正式 retired 与 receipt 对象。当前入口只要求 root 和内置固定散列，不校验独立结构化 PASS verdict、一次性清理 gate 或明确的清理授权记录。任何能以 root 调用当前脚本的人都可触发迁移；代码中的硬编码 receipt 不能替代“谁授权、独立审计批准了哪个 controller/hash、允许执行一次什么动作”的证据链。

最小关闭条件：新增仅适用于 `M9-SPR-R3-B01` 测试污染的授权记录、结构化零问题 PASS verdict 和一次性 cleanup gate。入口必须在获取锁及任何写入前验证：decision ID、授权 SHA、审计报告位于 `08_audits` 且 SHA/结构化结论匹配、当前 controller/test/frozen manifest SHA、伪 artifact 固定 receipt、真实五对象 SHA、gate/parent absent。cleanup gate 不得复用 source-control recovery gate，也不得授权 recovery 或 source_prepare。

清理成功后应由独立只读审计核对 retired/receipt、五对象哈希、正式 recovery transaction absent、source gate/parent absent及 ledger 零新增。只有该结果复核通过，才可回到 source-control recovery gate 的正常冻结流程。

## 当前现场与放行判断

正式伪 transaction 仍存在，SHA-256 保持为 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`。本轮测试没有改变它，也没有创建 retired 或 cleanup receipt。

当前结论为 FAIL，`BLOCKING=2`、`NON_BLOCKING=0`。不得执行清理入口。主 agent可在现有范围内修复 R3-B01 并建立 R4-B01 的授权/gate 合同；完成后须再次独立定点复核。只有清理实现与 gate 达到零问题 PASS，才允许执行一次清理；清理结果还须独立复核。该许可不包含 source-control recovery、`source_prepare` 或 `source_build`。

## 报告终检

本报告定稿后执行严格 Pandoc/MathML 转换、活动本地 Markdown 链接检查、UTF-8 非法控制字符扫描和最终 SHA-256 复算；结果随交付消息报告。
