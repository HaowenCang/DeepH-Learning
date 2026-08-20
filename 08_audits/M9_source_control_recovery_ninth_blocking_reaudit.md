# M9 source-control recovery 第九次阻塞项复核

## 结论

本轮结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。`M9-SPR-R4-B01` 的runtime值静态绑定已关闭；`M9-SPR-R3-B01`仍OPEN，因为PREPARED重放在rename前不复核当前active artifact是否仍等于journal original receipt，拒绝时会先移动漂移对象。测试矩阵仍不足，保留第二项阻塞`M9-SPR-R9-B01`。

不得创建或执行cleanup gate，不得执行recovery或`source_prepare`。

## 冻结快照

- budget：`dbe76fff3b185d5ab111d8f9069ecba6be7c8d539f9736fc4a22839f45095d5f`；
- tests：`adbf3bc06db1022261339dae104a3fc17d93cf65368d1777644205047461df76`；
- source manifest：`c36410b977c9962046945ccb85ec96dcbcdf707957feb00785f316fb5dd7e943`，17/17；
- cleanup manifest：`0f4f419a45210ac653636e46678cdc5d3943297d831bb9eda8b1417fe941ea24`，4/4。

固定Python `-I -S -B`下38/38测试通过；测试前后正式runtime inventory SHA均为`da7a70872325012249580e0daf35f5c48badac055b5879505e80cdfeffc440518`。伪transaction仍为`2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`。

## 逐项复核

### M9-SPR-R4-B01：CLOSED

单一`cleanup_expected_runtime_hashes()`现供gate verifier和执行preflight共同使用。verifier要求cleanup manifest及gate的五项runtime map逐值等于固定map，保留decision/schema、artifact SHA、文件闭集、报告、授权及absence绑定。上一轮任意00/11/22/33/44值穿透已被关闭。

### M9-SPR-R3-B01：OPEN

journal resume现校验schema、固定original/retired path及original receipt path；terminal也校验saved original path、current retired完整receipt和context。正常证据链明显增强。

但是当journal为PREPARED且active artifact存在时，代码直接`os.replace(active, retired)`，没有先对active执行`file_stat_receipt`并与journal的`original_receipt`逐项比较。临时穿透在PREPARED后把active内容改为`DRIFTED`，重放结果先把active移动到retired，再因retired receipt不匹配而拒绝。现场结果为active absent、retired present。这违反“漂移必须拒绝且不改变artifact状态”的最小条件，也会把可恢复的PREPARED状态推进为异常rename状态。

最小关闭条件：PREPARED分支rename前核当前active path/bytes/SHA/UID/GID/mode严格等于journal original receipt；不符时零写入拒绝。若active absent而retired存在，才按RENAMED崩溃恢复核retired。terminal还应比较journal保存的`retired_receipt`与current retired及saved receipt，避免journal内部retired证据漂移。

### M9-SPR-R9-B01：cleanup对抗测试不足

测试从36增至38，但新增项仅断言runtime map含5个合法形态SHA以及journal常量文件名。它们没有逐值变异gate/runtime，没有错schema/path/receipt path、PREPARED active漂移、terminal journal retired receipt漂移、锁内absence变化或gate context漂移测试。

现有成功resume正例继续mock `file_stat_receipt`和gate/runtime verifier，无法捕获真实文件在rename前漂移。本轮实际穿透正是38/38未发现的路径。

最小关闭条件：增加真实临时文件状态树的PREPARED active内容/owner/mode漂移零写入测试；补全gate每字段、runtime五值、journal schema/path/original/retired receipt、terminal context及both/neither矩阵。完整测试前后继续断言正式runtime inventory不变。

## 放行判断

当前`BLOCKING=2`、`NON_BLOCKING=0`，FAIL。修复R3-B01与R9-B01并再次独立复核前，不得执行cleanup。PASS后仅可创建一次性cleanup gate；实际清理仍需独立结果审计，不授权后续recovery/source动作。

## 报告终检

本报告定稿后执行严格Pandoc/MathML、链接、控制字符和SHA-256终检。
