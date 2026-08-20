# M9 source-control recovery 第八次阻塞项复核

## 结论

本轮结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。锁内动态 preflight、PREPARED journal、original receipt和terminal context均已实现，`M9-SPR-R3-B01` 接近关闭；但 journal恢复未校验schema及固定original/retired路径。`M9-SPR-R4-B01`仍OPEN：cleanup verifier只核runtime键闭集，不核五个值；独立穿透证明全零至重复数字的任意值均可通过。现有36项测试没有gate对抗矩阵。

当前不得创建cleanup PASS gate，不得执行cleanup、recovery或`source_prepare`。

## 冻结快照

- budget controller：`b82ad3c24c214b28daee88dd348d8576dbe63990fa54b68292d3d09fe3837434`；
- tests：`d415daf9df9b6f09955e77ba192bbfe4ec69ae232350582e83d4834e5d238adb`；
- source manifest：`21925297e06558a8b5100d7d9b25e559f126291dc695970e91692888288c663e`，`17/17`；
- cleanup manifest：`1dbaf9b1602b10cb1dc543f7217e5cf480074c71abf6fe7490c037ce35d57512`，`4/4`。

固定Python `-I -S -B`下36/36测试通过；测试前后正式runtime inventory SHA均为`da7a70872325012249580e0daf35f5c48badac055b5879505e80cdfeffc440518`。伪transaction仍为`2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`。

## 阻塞项

### M9-SPR-R3-B01：OPEN

本轮已把bootstrap、gate验证、五项runtime核验及artifact状态检查移入`budget.lock`；TOCTOU关闭。正常路径在rename前写PREPARED journal，保存original完整receipt、固定路径及cleanup context。resume和terminal均核context、runtime、retired receipt；terminal也要求active absent、retired/receipt存在。这些是实质修复。

剩余最小缺口：读取既有journal时没有核`schema_version`，也没有比较journal的`original_path`和`retired_path`与固定正式路径。攻击者若能留下同context、同original receipt但路径字段漂移的journal，恢复仍按全局常量执行并提交成功，receipt不会揭示journal路径声明不一致。context也没有直接包含journal schema/path。

最小关闭条件：resume前强制journal schema、original_path、retired_path及original receipt path分别等于固定常量；terminal receipt也应保存并比对journal SHA或固定journal identity。为错schema、错original/retired path、错original receipt path增加拒绝且零写入测试。

### M9-SPR-R4-B01：OPEN

gate现显式绑定artifact SHA、runtime map、source-control gate/parent absent；cleanup manifest闭集含controller、tests、授权及source manifest。decision/schema/闭集验证均保持。

但是verifier只要求`runtime_sha256`的键集合正确，并要求gate map等于manifest map；它不要求五个值等于代码冻结值，也不读取当前五文件。独立临时穿透构造runtime值为`00…`、`11…`、`22…`、`33…`、`44…`，同时让gate等于manifest；verifier成功返回。执行入口随后由`cleanup_runtime_receipt`核真实固定值，但这不能证明独立gate批准的值与实际执行合同相同。

现有tests仍只有常量断言和一个成功resume正例；没有gate decision/schema/闭集/artifact/runtime值、报告/授权、journal path或terminal context负例。

最小关闭条件：单一常量函数产生五项期望map，verifier、manifest检查和runtime preflight共同使用；verifier要求manifest/gate map逐值等于该map，并在锁内核当前文件。增加每个值变异及全部gate/journal字段对抗测试。

## 放行判断

当前`BLOCKING=2`、`NON_BLOCKING=0`，结论FAIL。修复后须再次独立复核；只有唯一结构化零问题PASS verdict后才允许创建一次性cleanup gate。实际cleanup仍须结果审计，不授权recovery或source动作。

## 报告终检

本报告定稿后执行严格Pandoc/MathML、链接、控制字符和SHA-256终检。
