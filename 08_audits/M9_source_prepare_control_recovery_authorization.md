# M9 source_prepare 控制失败恢复授权记录

本记录绑定 D-017 的已授权 overlap-only OpenMX 路线及其一次性受控执行。它只允许修复一次由冻结预算入口产生的 `source_prepare` capability owner/mode 控制失败：保存父事务与账本证据、退役不可消费的 stale capability、恢复双重状态机后重新创建 UID 1000 的全新 source_prepare transaction。

本记录不授权 source build、OpenMX smoke、批量 overlap、正式 DFT 标签或 M9-05。恢复必须由独立审计通过、使用一次性 source-control recovery gate，并在失败时保持或重新提交 `HARD_STOP`。

2026-08-19，用户再次明确授权执行一次性 source-control recovery。该次执行在退役 stale capability 后，因 Linux `fs.protected_regular=2` 拒绝带 `O_CREAT` 的既存账本追加而受控失败；未创建源码或构建产物。授权的剩余效力仅允许修复账本既存文件追加语义、以专用审计门控迁移旧 gate receipt，并续提同一恢复事务 `4783a27441019358a0f15127f26d957d` 及同一事件 `4783a27441019358a0f15127f26d957d:source-control-recovery`。不得新建第二个恢复事务、第二个恢复事件，不得回退或删除原失败证据，也不得以该迁移直接执行 `source_prepare`。

授权记录 ID：`AUTH-M9-SOURCE-CONTROL-RECOVERY-2026-08-14-01`
