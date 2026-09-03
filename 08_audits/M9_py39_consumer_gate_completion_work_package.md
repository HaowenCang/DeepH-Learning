# M9 Python 3.9 consumer gate 一次性 completion 工作包

状态：`READY_FOR_INDEPENDENT_AUDIT`  
决策边界：`D-018-PY39-CONSUMER-GATE-COMPLETION`

## 1. 允许动作与禁止动作

本工作包只允许从已经封存的 v2 bootstrap/snapshot 和 `SUCCESS_COMMITTED` refresh 状态签发缺失的 readiness consumer gate。不得改写或删除 bootstrap、snapshot、active/retired gate、refresh journal、state、workflow、ledger、失败/恢复事务或历史 consumer 对象；不得创建单次 authorization；不得调用 `source_prepare`、build、smoke、batch、GPU 或任何 DFT/DeepH 计算。

## 2. 完成规则

控制器必须由固定 Python 3.9.23、`-I -S -B`、root 运行，并以独立 verdict 绑定的 single-FD SHA loader 执行。它只从已安装 root 信任根导入旧 trusted installer，重放 frozen manifest、PASS verdict/report、28-member snapshot、完整历史闭集、recovery transaction/failure snapshot、预算锁、state/workflow/ledger 和 `SUCCESS_COMMITTED` refresh 的全部既有验证。

在调用旧 installer 的 `prepare_snapshot_for_refresh()` 或 `refresh_active_overlap_gate()` 前，控制器必须先以只读稳定 FD 证明 replacement snapshot 已存在且为精确封存闭集、snapshot staging 缺席、refresh journal 已存在且字段闭合并精确处于 `SUCCESS_COMMITTED`、active/retired receipt 与 journal 的 inode 身份一致、refresh staging 缺席、authorization 缺席。缺失 snapshot/journal、任一非终态 phase 或非法 namespace 均须在潜在 mutator 调用前零写拒绝。

唯一语义修正是 receipt 域规范化：refresh active receipt 必须恰好比 runtime active receipt 多 `dev` 与 `ino` 两个字段；删除这两个字段后必须与 runtime receipt 全等，且 `dev/ino` 必须为正整数。任何其他字段缺失、额外字段、值漂移、authorization 存在或 consumer gate 不同均零写拒绝。原始 inode-rich refresh receipt 继续用于 terminal preflight；只有传给旧 `build_consumer_gate()` 的局部副本改为 runtime receipt，不能改写 journal。

`preflight` 动作必须在潜在 mutator 前捕获 manifests、controls 和 root-private control 三个正式树的闭合路径、类型、inode、安全 metadata、大小、时间与文件 SHA-256；终态重放及 gate 构造后，完整快照必须逐项全等，否则停止。`complete` 动作采用同一前置快照；若 gate 原先缺席，最终差异只允许新增 consumer gate 及其父目录的非安全目录 metadata，gate receipt 必须精确匹配；若 gate 已存在，只允许既有 `install_consumer_gate()` 验证同一字节并要求完整正式快照全等。任何第二路径变化均失败。成功后继续复核 immutable preflight、完整历史闭集、authorization 缺席和 gate 精确字节。

## 3. 审计和执行门控

独立子 agent 必须审计失败事实、控制器、测试和本工作包，并生成同时绑定 controller、test、failure-record、work-package 与 report 路径及 SHA-256 的结构化 verdict。只有 `PASS/BLOCKING=0/NON_BLOCKING=0` 才允许执行 `complete`。执行后必须进行新的独立事实审计；事实审计通过前不请求 `source_prepare` 授权。

专用测试除 receipt normalization 外，还必须覆盖：snapshot 缺失、refresh 非终态、authorization 存在时在任何潜在 mutator 前拒绝；`preflight` 全正式对象零写；终态重放发生任一写入时在 gate 动作前拒绝；`complete` 首次创建只允许 consumer gate；既有同字节 gate 只读重放；任何第二路径变化拒绝。

正式 single-FD loader 与前序工作包相同：以 `O_NOFOLLOW` 单 FD 读取控制器、复核 inode/metadata/size/SHA 后执行。参数依次为控制器路径、控制器 SHA、动作 `complete`、PASS verdict SHA、独立报告 SHA、本工作包 SHA、失败事实记录 SHA 和测试文件 SHA。
