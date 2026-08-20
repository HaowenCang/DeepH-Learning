# M9 source-control recovery 第七次阻塞项复核

## 结论

本轮结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。`M9-SPR-R3-B01` 与 `M9-SPR-R4-B01` 仍为 OPEN。cleanup gate verifier 的 decision、schema、闭集、artifact 与 runtime manifest 结构已明显加强，但动态 preflight 在取得 `budget.lock` 之前执行，存在检查后竞态；rename 后续提仍无法证明 original receipt，terminal receipt 也未绑定 cleanup gate/frozen/auth SHA。现有测试没有覆盖这些条件。

不得创建 cleanup PASS gate，不得执行 `overlap-retire-source-control-test-artifact`，不得执行 source-control recovery 或重试 `source_prepare`。

## 冻结快照

- `m9_budget.py`：`d9a25ca72c7df01efbbfb6d35fa81bf71a158eb744e2b47d4a30d3ba3d7a8944`；
- `test_m9_overlap_controls.py`：`13fe93c755e58ee4cc240591decb49e1aca28768ac8ec1994087ec5686435ca7`；
- source frozen manifest：`bef1bcc3086a40fd9c9a05744670ee24e953f6d4b419efd70a1518b123451ef4`，内部 `17/17`；
- cleanup frozen manifest：`3d5c408511ca191fcd136d45b682359aa4d63be4f966705585a65f8ca7b54675`，内部 `4/4`。

固定 Python `-I -S -B` 下 `36/36` 测试通过；测试前后正式 manifests inventory 均为16文件、SHA `da7a70872325012249580e0daf35f5c48badac055b5879505e80cdfeffc440518`。正式伪 transaction 仍为 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`，未移动。

## 阻塞项

### M9-SPR-R3-B01：OPEN

`cleanup_runtime_receipt()` 现集中核对五项真实 runtime SHA及 source gate/parent absent；正常、续提和 terminal 分支都会在进入锁之前调用它。这修复了第六次报告中的静态绕过，但引入检查后竞态：gate、五对象和 absent 条件均在 `budget.lock` 取得前核验，随后才加锁并迁移。另一个遵守同一锁的正式控制器可以在 preflight 与加锁之间改变这些对象，而 cleanup 不会在锁内复核。

rename 后续提仍把当前 retired receipt 同时写入 `original` 与 `retired`，无法证明原 active 路径。没有 PREPARED journal 保存 original receipt；因此一旦 rename 与 receipt 间崩溃，原路径证据不可恢复。

terminal replay虽核对当前 retired receipt和 `fixed_runtime_sha256`，但不比较 saved `original`/`retired` 完整对象，不要求 original absent，也不绑定执行时 cleanup gate SHA、cleanup frozen SHA、authorization SHA或 audit verdict SHA。替换 gate 后仍可沿用旧 receipt返回成功。

最小关闭条件：冻结解释器可在锁外验证，但 cleanup gate、五对象、source gate/parent absent及 artifact状态必须在取得锁后重新核验；rename前持久化绑定 original完整receipt和gate/frozen/auth SHA的PREPARED journal；resume依据journal而非retired伪造original；terminal replay精确核对saved/current original absent、retired完整receipt、五对象及gate证据。

### M9-SPR-R4-B01：OPEN

verifier现强制 gate decision ID、cleanup manifest schema/decision、artifact SHA、五项 runtime键闭集和4项文件闭集；controller也纳入manifest。这关闭了上一轮任意单文件manifest穿透。

但 verifier只检查 `runtime_sha256` 的键闭集，不比较其值与冻结的五个期望SHA或当前文件；值可任意。实际runtime由controller硬编码另行检查，因而gate/frozen manifest并未证明独立审计批准的runtime值与执行值相同。gate本身也不显式绑定artifact receipt和runtime map，只间接绑定manifest SHA。

更关键的是，现有36项测试未增加cleanup gate对抗测试。cleanup相关测试仍只有常量名断言及mock掉gate verifier的弱化resume正例；没有decision/schema/闭集/artifact/runtime值、报告路径、授权、controller漂移或锁内复核负例。因此 strengthened verifier没有自动证据。

最小关闭条件：verifier比较cleanup manifest `runtime_sha256` 全部值与固定期望及当前对象；gate显式绑定artifact完整receipt与runtime map；测试逐项变异decision、schema、闭集、artifact/runtime值、报告/授权/controller及锁前竞态，并证明全部在任何rename/receipt写入前拒绝。

## 放行判断

当前 `BLOCKING=2`、`NON_BLOCKING=0`，结论FAIL。修复后须再次独立复核。只有得到唯一结构化零问题PASS verdict后，主agent才可创建一次性cleanup gate；实际cleanup后仍须独立结果审计。该许可不包含recovery、`source_prepare`或`source_build`。

## 报告终检

本报告定稿后执行严格Pandoc/MathML、链接、控制字符和SHA-256终检。
