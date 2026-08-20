# M9 source-control recovery 第十次阻塞项复核

## 结论

本轮结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。PREPARED active漂移已能在rename前零写入拒绝，但真实的“PREPARED journal已落盘、rename已完成、RENAMED journal尚未落盘”崩溃窗口仍不可恢复。39项测试没有覆盖该窗口，且新增漂移测试没有调用cleanup命令主体。

不得创建或执行cleanup gate，不得执行recovery或`source_prepare`。

## 冻结快照

- budget：`5c47e6eb6647fb0c75dca7d98ddf8395329fd6b26d0b2b1caf675b5af4adcef4`；
- tests：`23b2e8781d4c4be1dd6bc2a530e0c9c87a13271e01d8e234fd1a6eda525fbc33`；
- source manifest：`dc3f86b23bf488ac768856c5a39197736c935f6251f60828e57da745dee48f37`，17/17；
- cleanup manifest：`156a34dc42dc6f35fe66c86bd04e1512e3b9eb1b84ea3cb9e381f5c2031500fe`，4/4。

固定Python `-I -S -B`下39/39测试通过；测试前后正式runtime inventory SHA均为`da7a70872325012249580e0daf35f5c48badac055b5879505e80cdfeffc440518`。伪transaction保持`2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`。

## 阻塞项

### M9-SPR-R3-B01：OPEN

当journal为PREPARED且active存在时，代码现先取active receipt并严格比较journal original receipt；漂移时在rename前拒绝。上一轮“先移动漂移对象再拒绝”已关闭。

但正常执行顺序仍是：写PREPARED journal、`os.replace(active, retired)`、取retired receipt、写RENAMED journal。若在replace之后、RENAMED journal之前崩溃，重入现场为journal PREPARED、active absent、retired present。当前PREPARED分支要求active必须存在且retired必须不存在，直接报`cleanup PREPARED artifact paths mismatch`。

独立临时重放准确构造该现场，结果为退出失败，journal仍PREPARED、active absent、retired present、receipt absent。该状态不能补提交，因而cleanup仍不具备对自身真实写入序列的崩溃恢复能力。

最小关闭条件：PREPARED重放区分两种精确状态：active存在/retired不存在时核original receipt后rename；active不存在/retired存在时把它视为rename后崩溃，核retired完整receipt与journal original除path外一致，再推进RENAMED。both/neither或receipt漂移必须零写入拒绝。terminal还应比较journal `retired_receipt`与current retired及saved receipt。

### M9-SPR-R9-B01：OPEN

新增`test_cleanup_prepared_active_drift_is_zero_write`只直接mock并比较`file_stat_receipt(active)`与original字典，然后断言两个路径未变化；它没有调用`command_retire_source_control_test_artifact`，因此不能证明命令在完整gate/context/journal分支中零写入拒绝。

测试仍没有构造PREPARED+active absent+retired present的真实崩溃窗口，也没有terminal journal retired receipt漂移、gate字段矩阵、both/neither或receipt异载荷矩阵。本轮39/39无法发现实际重放失败。

最小关闭条件：使用完整临时gate、runtime、journal和artifact路径调用命令主体，覆盖PREPARED正常、active漂移零写入、rename后崩溃续提、both/neither、retired漂移、RENAMED、SUCCESS terminal及journal retired receipt漂移；断言每条路径的文件inventory和receipt。

## 放行判断

当前`BLOCKING=2`、`NON_BLOCKING=0`，FAIL。修复并再次独立复核前不得cleanup。零问题PASS后只允许一次性cleanup；结果仍须独立审计，不授权recovery/source动作。

## 报告终检

本报告定稿后执行严格Pandoc/MathML、链接、控制字符和SHA-256终检。
