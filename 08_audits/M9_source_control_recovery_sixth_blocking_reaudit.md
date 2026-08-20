# M9 source-control recovery 第六次阻塞项复核

## 结论

本轮定点复核结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。`M9-SPR-R3-B01` 与 `M9-SPR-R4-B01` 均仍为 OPEN。cleanup 授权、frozen manifest 与 gate verifier 已开始建立，但 verifier 没有核对 decision ID、manifest schema、固定文件闭集、artifact SHA 或五项 runtime SHA；任意自选文件组成的 manifest 即可通过。cleanup 的 rename 后续提与 terminal replay 仍跳过五项 runtime 核验和完整 receipt 比对。

当前不得创建 cleanup gate，不得执行 `overlap-retire-source-control-test-artifact`，不得创建 source-control recovery gate，不得执行 recovery CLI，也不得重试 `source_prepare`。

## 冻结快照与只读边界

本轮送审对象独立复算为：

- `06_reproduction/scripts/m9_budget.py`：SHA-256 `b3b4f7291aa9eed000c21ad3c184af3575c139d85cb0c740f80d4298136fc2cb`；
- `06_reproduction/tests/test_m9_overlap_controls.py`：SHA-256 `13fe93c755e58ee4cc240591decb49e1aca28768ac8ec1994087ec5686435ca7`；
- `06_reproduction/manifests/m9_source_control_recovery_frozen_hashes.json`：SHA-256 `5d03edf293021fd7f894cad36ab6e62bc7fca5558ce232471555248b4daaf124`；
- `06_reproduction/manifests/m9_source_control_test_cleanup_frozen_hashes.json`：SHA-256 `a45c90798a0cddad78d49641ff8ce19906b7c2d72eefa95bda0fb7f5f08631ad`。

source frozen manifest 为 `17/17` 匹配；cleanup manifest 当前登记两项文件，均匹配。固定 Python 3.9 以 `-I -S -B` 运行得到 `36/36 PASS`。测试前后正式 manifests inventory 均为 16 个文件，inventory SHA 均为 `da7a70872325012249580e0daf35f5c48badac055b5879505e80cdfeffc440518`，字节完全一致。

审计没有创建 cleanup gate、没有执行正式清理、没有创建 source-control recovery gate、没有执行 recovery CLI或重试 `source_prepare`。全部穿透使用临时目录和 mock 路径。正式伪 transaction 仍保持 SHA-256 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`。

## 阻塞项复核

### M9-SPR-R3-B01：OPEN

正常清理分支仍能核对固定伪 artifact receipt和五个真实运行对象 SHA，并把这些哈希写入成功 receipt。但 rename 后续提分支和 terminal replay 分支仍位于 `fixed` 字典构造及五对象核验之前。

当 original 已不存在、retired 存在且 receipt 缺失时，入口只检查 retired SHA/bytes/UID/GID/mode，随后把同一个 retired receipt 同时写入 `original` 和 `retired`；它不检查五对象，不保存原 active path，也不写 `fixed_runtime_sha256` 或 cleanup gate SHA。当前测试继续 mock `file_stat_receipt`，没有建立五对象临时树，因而明确验证的是这一弱化路径，而不是完整合同。

当成功 receipt 已存在时，terminal replay只要求 `status=PASS`、retired 文件存在及当前 retired SHA/bytes/UID/GID/mode匹配硬编码值；它不比较 saved `original`/`retired` receipt，不检查 saved/current五对象哈希、不要求 original absent，也不验证 gate/parent 仍 absent。虽然本轮已把 mode 纳入当前 retired检查，修复了上一轮 0777 穿透，但运行态和 receipt 证据仍可漂移。

最小关闭条件保持为：所有阶段共用同一 preflight，核对五对象、gate/parent 状态、冻结对象和 cleanup gate；rename 前原子持久化 PREPARED journal，保存 original path与完整 receipt；resume不能用 retired receipt伪装 original；terminal replay必须精确比较 saved/current original、retired、五对象、gate与授权证据。新增真实临时状态树的 runtime 漂移、receipt 漂移、original/path 漂移、both/neither及终态重放测试。

### M9-SPR-R4-B01：OPEN

cleanup 专用授权记录和 frozen manifest 已存在。授权文字将范围限定为测试污染清理，并明确不授权 recovery、source_prepare、source_build、smoke、batch 或标签生成。gate verifier也要求结构化零问题 PASS JSON直接位于 `08_audits`、报告 SHA、授权 SHA和 frozen manifest SHA。这些是有效进展。

但 verifier 不检查 gate `decision_id`；不检查 frozen manifest 的 `schema_version`、`decision_id` 或固定文件闭集；也不读取和比较 frozen manifest 的 `artifact_sha256` 与 `runtime_sha256`。它只是迭代 manifest 自报的 `files`。独立临时穿透构造了一个没有 decision ID、manifest 仅含一个任意自选文件的 gate；`verify_source_control_test_cleanup_gate` 成功返回。由此，当前 gate不能证明审计批准的是这一个 artifact、这五项 runtime 和这版 controller。

现有 cleanup frozen manifest 的 `files` 也只有测试文件与授权记录，没有包含执行清理的 `m9_budget.py` 本身、source frozen manifest、cleanup manifest合同或相关工作包。虽然 gate绑定了 cleanup manifest SHA，但 manifest没有绑定controller，修改清理代码后仍可能沿用同一批准材料。

此外，cleanup gate不存在且本轮不能合法创建：当前唯一正式报告结论仍为 FAIL，并无结构化零问题 PASS verdict。任何主 agent自建 PASS JSON都不满足独立审计语义。

最小关闭条件：

- verifier强制 `decision_id=D-017-source-control-test-cleanup-v1`；
- 强制 cleanup manifest schema、decision ID、artifact SHA、完整五项 runtime SHA及固定执行闭集；闭集至少包括 `m9_budget.py`、测试、cleanup授权、source frozen manifest和cleanup manifest引用的相关合同对象；
- gate内再显式绑定 artifact receipt、五项 runtime SHA、source gate/parent absent及本轮唯一独立结构化 PASS verdict；
- verifier比较 manifest/runtime常量与真实当前对象，而非只迭代自报文件；
- 测试覆盖缺 decision ID、错 schema、删/加/换文件闭集、错 artifact/runtime SHA、自由报告、错误授权及controller漂移，全部在任何写入前拒绝。

## 测试与相邻回归

36项测试继续保持正式 runtime零写入；B04状态机与冻结解释器测试没有回归。但 cleanup相关测试只有常量名断言和弱化 resume-after-rename正例，没有 gate verifier 对抗矩阵或五对象状态树，因而未捕获本轮任意 manifest穿透。

本轮未发现其他稳定新问题 ID；发现均属于R3-B01/R4-B01尚未完成的最小关闭条件。

## 放行判断

当前为 FAIL，`BLOCKING=2`、`NON_BLOCKING=0`。不得创建或执行 cleanup gate/command。主 agent可修复R3-B01/R4-B01并冻结新快照；修复后必须再次独立复核。只有 cleanup工作包达到零问题PASS，才允许主 agent按独立 verdict SHA创建一次性 cleanup gate并执行一次清理；实际清理结果仍须独立只读审计。该许可不包含 source-control recovery、`source_prepare` 或 `source_build`。

## 报告终检

本报告定稿后执行严格Pandoc/MathML转换、活动本地Markdown链接检查、UTF-8非法控制字符扫描和最终SHA-256复算；结果随交付消息报告。
