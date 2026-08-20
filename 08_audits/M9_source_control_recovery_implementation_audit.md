# M9 source-control recovery 实现定点审计

## 结论

本轮实现审计结论为 **FAIL**：`BLOCKING=6`，`NON_BLOCKING=0`。普通 overlap 入口新增的 UID 1000 前置约束方向正确，但当前 `overlap-recover-source-control-failure` 仍不足以安全、可审计地解除 `HARD_STOP`。不得创建 recovery gate，不得执行该 CLI，也不得重试 `source_prepare`。

## 稳定阻塞项

### M9-SPR-IMP-B01：恢复入口没有独立 gate

当前 CLI 只检查 EUID 为 root，未要求独立结构化 PASS verdict、用户授权边界、失败事务哈希、完整冻结执行闭集或一次性 recovery gate。任何能够调用冻结 Python 和脚本的 root 均可进入恢复逻辑。最小关闭条件是新增仅适用于该固定失败事实的一次性 gate，并在获取锁及任何写入之前校验 gate 状态、结构化 verdict SHA、授权记录、脚本/测试/合同/manifest 完整闭集以及固定失败对象哈希。

### M9-SPR-IMP-B02：preflight 未绑定实际失败事实闭集

现有 preflight 只检查 workflow stage、事务 state/action/reason，以及 capability 的 transaction ID。它没有强制核对：

- 失败事务固定 SHA、transaction ID、`exit_code=1`、`timed_out=false`、forecast、CPU bucket、command hash 和耗时；
- budget/workflow 均 hard-stopped、active transaction 为空、apt 完成、D-017 recovery 为 `SUCCESS_COMMITTED`；
- budget state、workflow、ledger 字节数/SHA/末事件及失败 event 的唯一性；
- CPU 原始值、adjustment 和有效用量；
- capability 的固定 ID/SHA、`BOUND`、action、child/budget PID、UID/GID、0600 mode、PID 已死亡；
- 对应 consumed 和 launcher receipt 不存在；
- build root、staging、official tree manifest、HDF5 prefix 均不存在；
- 45 个 pinned 包仍保持精确版本和 installed 状态。

这些条件必须逐项成为 fail-closed preflight 和 recovery receipt，而不能依赖人工观察。

### M9-SPR-IMP-B03：retirement 不可验证

当前代码将 `cap.json` 重命名为 `cap.json.retired`，但 recovery 对象只记录旧 SHA，不记录原/新路径、原/新 bytes、owner、mode 或重命名后 SHA，也没有验证字节不变。它还没有保存失败事务的独立父快照和 retirement receipt。

最小关闭条件是使用明确不会匹配活动 `*.json` 的固定 `.retired.json` 路径；重命名前后验证 bytes 与 SHA 完全一致，记录并验证 UID/GID/mode；保存失败事务字节级父快照，并将这些证据绑定到 recovery transaction。

### M9-SPR-IMP-B04：提交顺序不具备崩溃恢复与原子性

当前顺序是：rename capability、写 PREPARED recovery、清 budget hard stop、清 workflow hard stop、append ledger、再写 `SUCCESS_COMMITTED`。任一中间点崩溃都可能产生：旧 capability 已消失但无可重放状态、budget 与 workflow 分叉、hard stop 已解除但 ledger 尚未提交，或 ledger 已追加而 recovery 尚未终态。CLI 没有检测和恢复这些中间状态；重复执行只会因活动 capability 数量变化而失败。

最小关闭条件是实现 journaled 状态机，例如 `PREPARED -> CAPABILITY_RETIRED -> SUCCESS_PENDING_COMMIT -> SUCCESS_COMMITTED`。必须先持久化包含所有父哈希、固定 event 与 retirement 计划的 PREPARED journal；每一步可按 receipt 幂等恢复；ledger event 经 payload hash 验证后，才提交 budget/workflow 恢复；最终提交后重复调用只返回既有成功结果，不重复 event 或重新清状态。任何不一致必须双 hard-stop。

### M9-SPR-IMP-B05：缺少恢复测试

送审测试文件 SHA 仍为 `2876ae64...`，没有新增 source-control recovery、UID 约束或崩溃恢复测试。至少应覆盖：非 root recovery 拒绝、root 普通 overlap 无状态拒绝、所有 B02 preflight 漂移、活动 PID、capability owner/mode/state/receipt 穿透、source 产物存在、每个 journal 写入点中断后重放、ledger 同 ID 异载荷、重复成功调用、retired capability 不可消费、CPU/state/ledger 不变性，以及 UID 1000 新 capability 的成功消费路径。

### M9-SPR-IMP-B06：冻结链和旧 gate 已失效

当前脚本 SHA 为 `a2d5288610807c3501996fea79945825efb2bf6008f181a16d0ee4f196f61777`；测试 SHA 为 `2876ae64ebea87934a4a490554aba70bf15ab8e0951741f6c1001b899a7ff642`；更新后的 offline recovery frozen manifest 实际 SHA 为 `c9dce5130fd378af31c1dd2bd5c7426ee480a965e7202c1d4fc637050654557c`。此前 gate 绑定的 frozen manifest SHA 为 `faefb243...`，因此已失效。原 `m9_overlap_frozen_hashes.json` 仍为旧闭集。

代码和测试完成后，必须更新完整 recovery/follow-up 冻结闭集，由独立审计复算每个对象，再生成新的结构化 verdict 和一次性 source-control recovery gate。旧 gate 不得复用。

## 已确认的正确部分

`command_overlap_run` 在 bootstrap、gate 验证、锁和状态写入之前要求 EUID 为 1000；因此 root 普通 overlap 会无状态拒绝，而 root-only offline apt recovery 保持独立入口。这一边界应保留。

现有运行时仍处于原 hard stop；旧 capability、失败事务、budget、workflow 和 ledger 未被本轮审计修改。当前 source build root、staging、official tree manifest 和 HDF5 prefix仍不存在。

## 放行判断

当前不允许执行 recovery CLI。主 agent 可以按 B01 至 B06 实施修复；修复对象冻结后须再次独立定点审计。只有达到 `BLOCKING=0/NON_BLOCKING=0`、新 gate 校验通过后，才允许执行一次 source-control recovery；实际 recovery 成功还须再做结果复核，之后才能以 UID 1000 和全新 transaction/capability 重试 `source_prepare`。

## 报告终检

本报告定稿后执行 UTF-8 控制字符扫描、活动本地 Markdown 链接检查，以及 Pandoc 严格转换。最终 SHA-256 随交付消息报告。
