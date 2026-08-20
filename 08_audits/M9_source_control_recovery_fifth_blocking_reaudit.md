# M9 source-control recovery 第五次阻塞项复核

## 结论

本轮定点复核结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。`M9-SPR-R3-B01` 与 `M9-SPR-R4-B01` 均仍为 OPEN。测试隔离和基础 rename 后续提已经改善，但 cleanup resume 会跳过真实五对象哈希核验，成功重放 receipt 缺少原始路径与固定运行态证据，终态重放也接受 retired owner/mode 漂移。独立 cleanup 授权、结构化 verdict 与一次性 gate 尚未实现。

当前不得执行 `overlap-retire-source-control-test-artifact`，不得创建 source-control recovery gate，不得执行 recovery CLI，也不得重试 `source_prepare`。

## 冻结快照与只读边界

本轮送审对象独立复算为：

- `06_reproduction/scripts/m9_budget.py`：SHA-256 `908994558513554cb1fcb78f0a51381c61b23ba096f54212ce4c37022200bedd`；
- `06_reproduction/tests/test_m9_overlap_controls.py`：SHA-256 `92477ac1b791a24814397ce58194bc71d81a9980b2bbb8fb2421532cdc2cc3b4`；
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：SHA-256 `546ea395c9cf9f4901eda90b1aa3e040c3ca39e5ef66e86cd7828a3a6bac8476`。

冻结清单登记的 17 个对象为 `17/17` 匹配。固定 Python 3.9 以 `-I -S -B` 运行得到 `36/36 PASS`。测试前后正式 manifests 两层 inventory 均为 16 个文件，inventory SHA 均为 `da7a70872325012249580e0daf35f5c48badac055b5879505e80cdfeffc440518`，字节完全一致。控制目录未发现 `__pycache__`。

审计没有执行正式污染清理、没有创建 gate、没有执行 recovery CLI、没有重试 `source_prepare`。所有 cleanup 穿透均在临时目录和 mock 路径下完成。正式伪 transaction 保持 SHA-256 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`。

## 阻塞项复核

### M9-SPR-R3-B01：OPEN

入口现调用 `isolated_bootstrap_provenance()`，因而冻结 Python 3.9、`-I -S -B`、no-site 和 bootstrap 路径边界已覆盖。若 original 已被 rename、retired 存在而 receipt 缺失，入口也可以校验 retired 基础 receipt 后补写 receipt；新增测试验证该基本续提路径。此前“rename 后永远不可重入”的缺口已缩小。

但是 resume 分支位于真实五对象 `fixed` 字典构造与核验之前。只要 retired 的 SHA/bytes/UID/GID/mode 匹配，它便直接写成功 receipt；budget state、workflow、failed transaction、ledger 和 stale capability 是否仍保持固定 SHA 完全不再检查。临时目录主动穿透在没有任何五对象证据的情况下返回 0，证明 cleanup 可在 runtime 已漂移时补提交成功。

该 resume receipt 还把 `original` 与 `retired` 都写成 retired 当前 receipt，因此丢失 original path；同时不记录 `fixed_runtime_sha256`。这不能证明从正式 active 文件到 retired 文件发生了哪一次迁移。正常成功分支虽然记录五对象哈希，但 terminal replay 只检查 retired SHA 与 bytes，不比较 saved original/retired receipt、UID/GID/mode、五对象哈希、bootstrap 或 gate/parent absent。

独立临时穿透在成功 receipt 形成后把 retired mode 改为 0777；重复调用仍返回 0 和 `test_artifact_already_retired`。因此终态 receipt 不能检测 owner/mode 证据漂移。

最小关闭条件：

- 将固定五对象核验、gate/parent absent 和冻结代码/manifest/授权核验提取为所有阶段共用的 preflight，包括 retired-exists/receipt-missing resume 与 terminal replay；
- rename 前原子持久化 PREPARED journal，记录 original path/bytes/SHA/UID/GID/mode、retired 目标、五对象 SHA、bootstrap、冻结对象与 cleanup gate；rename 后据此补提交，不能用 retired receipt 伪装 original receipt；
- terminal replay 精确比较 saved original/retired path、bytes、SHA、UID/GID/mode、五对象哈希、授权/gate 和当前 retired receipt，且要求 original、source gate、source parent 仍 absent；
- 任一 owner/mode、路径、runtime SHA、receipt 或阶段漂移必须拒绝且不改写真实五对象；
- 增加 runtime 漂移 resume、original-path 保存、terminal mode/owner 漂移、both/neither、receipt 异载荷及重复成功的临时状态树测试。

### M9-SPR-R4-B01：OPEN

当前代码和工作区仍没有 cleanup-specific authorization record、cleanup frozen manifest、结构化独立 PASS verdict verifier 或一次性 cleanup gate。`overlap-retire-source-control-test-artifact` 只要求 root、冻结解释器和内置固定哈希即可迁移正式 recovery transaction。

硬编码 artifact/runtime 哈希只能证明“对象长什么样”，不能证明用户授权了哪个清理动作、独立审计批准了哪一版 controller/test/manifest，也不能限定该动作只执行一次且不授权后续 recovery。当前 36 项测试同样没有 cleanup gate 的缺失、错误 decision ID、报告目录、报告 SHA、授权 SHA、controller/frozen hash 或 gate replay 负例。

最小关闭条件：

- 建立 cleanup 专用授权记录，明确只允许处理 SHA 为 `2e0aa636...` 的测试污染，不授权 source-control recovery、`source_prepare` 或 `source_build`；
- 建立 cleanup 专用完整 frozen manifest和结构化独立零问题 PASS verdict；
- 建立一次性 cleanup gate，绑定 decision ID、授权 SHA、审计报告规范路径/SHA/结构化结论、controller/test/cleanup manifest SHA、伪 artifact receipt、真实五对象 SHA及 source gate/parent absent；
- 清理入口在获取锁和任何写入前验证 gate；成功 receipt 绑定 gate SHA，并使 gate 不可被另一个 artifact 或 controller 复用；
- 对全部 gate 字段和路径穿透增加失败且零写入测试。

## 测试与相邻回归

36 项测试的正式 runtime 零写入门控独立通过，B04 状态机测试未回归。新增 resume-after-rename 测试只 mock `file_stat_receipt` 并确认生成 `status=PASS`；它没有建立真实五对象临时树，也没有断言 receipt 保存 original path、runtime SHA 或 terminal replay，因此未捕获本轮两个实际穿透。

本轮未发现 B01—B04、B06 的相邻回归。R3-B01/R4-B01 的最小关闭条件仍需实现后再复核。

## 放行判断

当前为 FAIL，`BLOCKING=2`、`NON_BLOCKING=0`。不得执行 cleanup。主 agent 可在当前 D-017 范围内修复 R3-B01，并准备 R4-B01 的 cleanup 专用授权与 gate 材料；完成后须再次独立定点复核。只有 cleanup 工作包达到零问题 PASS 后，才允许执行一次清理；实际清理结果仍须独立只读审计。该许可不包含 source-control recovery、`source_prepare` 或 `source_build`。

## 报告终检

本报告定稿后执行严格 Pandoc/MathML 转换、活动本地 Markdown 链接检查、UTF-8 非法控制字符扫描和最终 SHA-256 复算；结果随交付消息报告。
