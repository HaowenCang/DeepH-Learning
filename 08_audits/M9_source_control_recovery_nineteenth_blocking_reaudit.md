# M9 source-control recovery 第十九次阻塞项复核

## 结论

本轮结论为 **FAIL**：`BLOCKING=2`，`NON_BLOCKING=0`。`M9-SPR-R18-B01` 指出的 parent 与 artifact 权限迁移半提交缺口已由持久化 phase 和精确中间态续提关闭；root:1000、1770 sticky 终态也同时满足 cleanup 证据保护与 UID 1000 后续 runtime 原子替换语义。然而，迁移 journal 和 cleanup gate 在 parent 完成 root 所有权迁移前仍位于 UID 1000 所有、0755 的目录中。当前实现把“再次读取的当前 gate 文件 SHA”与“先前验证后保存在内存中的 gate 字段”拼接成迁移绑定，不能证明两者来自同一份已验证字节。独立穿透已使非 JSON、从未通过 verifier 的当前 gate 文件被接受为迁移 journal 的 `gate_sha256`。

因此不得创建或执行一次性 cleanup gate，不得执行 cleanup、source-control recovery 或 `source_prepare`。

## 冻结快照与独立复算

- `m9_budget.py`：`ee170cb3fd3ca82d1728221cc9a0538190031fae655ea4aa7ab86ef94da167eb`
- `test_m9_overlap_controls.py`：`a0f0740abc68864bcdc89a3081de8927117bdb22fbbe66b230baa342bcb3b2ee`
- source frozen manifest：`eca8dda39378ec44e9fbba04785d7308338b7be74edb0ec510d48a5a0876b2ca`，登记对象 `17/17` 匹配
- cleanup frozen manifest：`67836f79b5066f597da6fc2fdee8bd781b7d189f3bbfef09586aae22bd778ffc`，登记对象 `4/4` 匹配

冻结 Python 3.9 以 `-I -S -B` 独立运行正式测试，55/55 通过。测试后五项正式 runtime SHA-256 仍分别为：budget state `1a998b1383810df371cccb9d799d4ac91bb2023e539155eae782345700a4d7dc`、workflow `2dbad901ea059f7ab7ea766f1fdc933e4a95a40aeeded304258599dd4626685d`、transaction `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309`、ledger `25103d9a794a36a4e058a45ecb40b4b128dc3905d364a046640571684498da4f`、capability `0a4352dafb4718084ddac286fc24b05b863d284583741c67dffd356c7274e91e`。伪 transaction 仍为 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74`，1644 bytes、UID/GID 1000、mode 0644。retired、retirement receipt、cleanup journal、migration journal 和 cleanup gate 均不存在；控制目录未发现 `.pyc`、`.pyo` 或 `__pycache__`。

## M9-SPR-R18-B01：CLOSED

当前 migration journal 在任何 parent `chown`/`chmod` 前建立，绑定 parent 的 before、owner-only、hardened 状态以及 artifact 的 before、owner-only、hardened 状态。parent 的 `PREPARED`、`PARENT_OWNER`、`PARENT_HARDENED` 与 artifact 的 `ARTIFACT_OWNER`、`ARTIFACT_HARDENED` phase 均有精确文件系统状态检查；系统调用已成功而 journal 写入失败时，重入可按实测状态补提交 phase。外部状态不属于规定三种状态时拒绝，不执行后续迁移。

`atomic_root_private_json` 使用固定 `.tmp`、`O_EXCL`、可用时的 `O_NOFOLLOW`、root:root/0600/nlink=1 校验、文件 fsync、原子 replace、提交对象复核和目录 fsync。状态机在 `SUCCESS_COMMITTED` 前要求 hardened parent、root:root/0600/nlink=1 retired、cleanup receipt 和 cleanup journal 的一致终态；重复运行重新验证终态证据后返回。上述实现关闭了第十八次报告所指的单纯 chown 成功/chmod 失败不可恢复问题。

独立临时权限矩阵同时确认：在 root:1000、1770 sticky 目录中，UID 1000 删除 root:root、0600 cleanup 证据和为其创建硬链接均失败；同一 UID 能创建临时文件并原子替换其本人所有的 runtime 文件。因此 sticky 终态本身没有引入后续 `overlap_run` 写入回归。

## 阻塞项

### M9-SPR-R19-B01：迁移绑定可组合未验证 gate SHA 与旧内存字段

正式入口先调用 `verify_source_control_test_cleanup_gate()`，随后才调用 `prepare_cleanup_parent_security(gate)`。此时 manifests parent 仍为 UID/GID 1000、0755；即使 gate 文件本身由 root 所有，目录所有者仍可在两个调用之间删除或替换该目录项，advisory lock 也不能约束不配合的 UID 1000 进程。

`cleanup_security_migration_binding(gate)` 不重新解析并执行完整 gate verifier。它从当前路径重新读取字节并计算 `gate_sha256`，但 authorization、frozen、audit report、artifact 和 runtime 字段来自先前的内存对象。独立临时穿透把 gate 路径内容改为字节 `NOT-JSON-AND-NEVER-VERIFIED`，同时传入先前验证形态的内存 gate。函数成功返回，且绑定中的 `gate_sha256` 精确等于该无效字节的 SHA-256 `dcb5d4b44455df959796d4812233da4101f68d0539ff3f9305fe450ee05d3b81`。这证明 migration journal 可以记录一个从未通过 verifier 的 gate 文件哈希，并把其余证据字段错误归属于该哈希。

同一信任边界问题还影响 migration journal 的“root 私有”性质：首次 journal 写入和随后重新加载发生在 UID 1000 所有的 parent 完成 `chown` 前。root:root、0600 只保护文件内容访问，不保护由目录所有者控制的目录项。固定 `.tmp` 的元数据、内容、fsync 与 replace 检查能够拒绝若干单点替换，却不能把整个“验证 gate、建立 journal、迁移 parent 所有权”序列转化为同一不可替换证据对象。

最小关闭条件：在任何依赖 mutable manifests 目录项的操作前，把完整通过 verifier 的**精确 gate 字节**及其 SHA-256 固化到一个预先存在、非 UID 1000 可改名或删除的 root 私有目录，或建立等价的同 inode、同字节可信句柄合同。root 私有 migration journal 也应位于该可信目录，至少持续到 parent 已硬化。journal 绑定、cleanup context 和最终 receipt 必须全部引用同一 verified gate snapshot，而不得分别读取当前路径和旧内存字段。parent 硬化后应再次核对原 gate 路径未漂移；任何替换必须在 chown、chmod、rename、receipt 或正式 runtime 写入前零写入拒绝。应补充 verifier 返回后 gate 被替换、删除、改为无效 JSON、改为另一份结构合法 PASS，以及初始 journal `.tmp` 被 symlink/hardlink/rename/部分写入干扰的定向测试。

### M9-SPR-R9-B01：正式对抗测试仍未覆盖实际 gate/journal 信任边界

55 项测试覆盖 parent/artifact 权限系统调用失败与续提、PREPARED/RENAMED/SUCCESS 状态、symlink/hardlink、receipt 漂移和正式 runtime 不变性，但没有在 verifier 返回后、migration binding 建立前替换 gate 文件。现有迁移测试还 mock 了 `atomic_root_private_json`，因此没有实际执行固定 `.tmp` 的部分写入重入、恶意 symlink/hardlink、owner/mode 异常、文件 fsync 和目录 fsync 失败矩阵。55/55 PASS 因而没有发现本轮可重现穿透。

最小关闭条件：将 `M9-SPR-R19-B01` 的 gate snapshot/同 inode 约束加入正式临时文件状态树测试，并逐点注入 root 私有 journal create、truncate/write、file fsync、replace、target recheck 和 directory fsync 失败。每个失败点均应证明外部漂移零正式写入，受控半提交只能依据同一 verified snapshot 幂等续提；完整测试前后继续复算五项 runtime、伪 transaction、17/17、4/4 和 cache=0。

## 放行判断

当前为 `BLOCKING=2`、`NON_BLOCKING=0`、FAIL。只有 `M9-SPR-R19-B01` 与 `M9-SPR-R9-B01` 均由新的独立定点复核判定 CLOSED，且总计 `BLOCKING=0`、`NON_BLOCKING=0`，才允许创建一次性 cleanup gate。实际 cleanup 完成后仍须独立只读复核，不自动授权 source-control recovery 或 `source_prepare`。

## 报告终检

本报告定稿后执行严格 Pandoc/MathML、UTF-8、控制字符、本地链接及 SHA-256 终检。报告不含数学表达式或本地链接，MathML 与本地链接期望计数均为零。
