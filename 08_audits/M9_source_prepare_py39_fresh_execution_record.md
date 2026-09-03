# M9 Python 3.9 恢复后单次源码准备执行记录

日期：2026-08-30。记录角色：主 agent；独立审计结论另见对应报告。

## 用户授权与签发

用户明确授权一次 `source_prepare`，范围见 [授权记录](M9_source_prepare_py39_fresh_user_authorization.md)，SHA-256 为 `258212b82ccf0fc6bcd23ce93486f692d2e092d11e502f8b09926f0575bbf368`。操作编号为 `f9824f0eb63e41f19699c1114b13537e`；它不是冻结预算控制器随后独立生成的 transaction id。

独立审计员保存的 [签发前完整基线](M9_source_prepare_py39_fresh_preexecution_baseline.json) SHA-256 为 `bac5fa6f486d2e77cde4fe83703fc1745880ae15c3c915e04ee833ad506766ac`，包含126项正式对象 receipt 和7项原始字节备份，包括61826-byte ledger。

主 agent 在独立签发前复核通过后，使用冻结 Python 3.9.23 `-I -S -B`、root 和既有 single-FD loader 执行一次机械签发。loader 从原替代工作包唯一 Python 代码块提取；工作包 SHA 为 `dc1d0d992f7e1328f79a4436eb4535b79ba2ab48fcee1b44fa498c31c30e91a2`，loader 源 SHA 为 `c68e43b5de4fdadb44254fbfdd543f5ba2a29b6e41994021c55a3287b5f7491f`，签发脚本 SHA 为 `b649d015d428e66ffa0ae86b182a569113912ca58b40078df445e2c6c654ad17`。

签发进程退出码为0，输出状态为 `authorization_issued_and_verified`。实际授权对象为885 bytes、root:1000、0640、单链接，SHA-256 为 `62bf44207a3f3338fce3f8b4476a0b37be97f7587d2f07148aa3978b9014b4ab`，与冻结的本地机械 payload 一致。对象绑定 runtime canonical SHA `24a952d229fb39fa0c0198b0361e5f02955cbff74182af97a7dfb24da9075db4`。

签发过程在原 budget lock 内校验冻结输入、记录、门控和实际运行状态；签发前后真实 UID1000 只读 verifier 均通过，runtime 相同。该脚本没有调用 adapter `main()`，没有执行源码动作。[独立签发与执行前审计](M9_source_prepare_py39_fresh_authorization_independent_audit.md) 已判定 `PASS/BLOCKING=0/NON_BLOCKING=0`，SHA-256 为 `2bc82001d681c8ac6ab0afd69ffe39d3d856381d264c2954c86b8dd0be8ebbde`，主 agent 随后才调用正式动作。

## 源码准备执行状态

以 `wsl -d Ubuntu-22.04 -u evan-williams --` 启动授权记录中的唯一完整命令，恰好调用一次，没有额外 cwd、log、structure id 或自由子命令。进程退出码为0，未超时。执行返回后已停止，没有再次调用或进入 source build。以下是主 agent 读取的实际状态，待独立执行事实审计确认。

| 项目 | 实际结果 |
| --- | --- |
| transaction id / 状态 | `dc75dda112af553377a697f629801782` / `SUCCESS_COMMITTED` |
| action / CPU bucket | `source_prepare` / `overlap_build` |
| capability id | `f58c6a5904391d5659201dabf22a787b` |
| launcher receipt | `PASS`，SHA `a7bf586c444f24d3393eec69970b69b74e7f758b672c5da78a83e2ed6f696803` |
| 计量开始 / 结束 UTC | `2026-08-30T03:47:13.870348Z` / `2026-08-30T03:47:20.102156Z` |
| 本次 CPU 子预算计量 | `6.231787957` 秒 |
| workflow | `SOURCES_PREPARED`；active transaction 为 null；hard_stopped 为 false |
| 原始 overlap_build 累计 | `7212.901214103001` 秒；既有抵扣仍为 `7200.075310528` 秒 |
| GPU | compatibility 仍为 `54.84820560599999` 秒，training/physical_validation 仍为0 |

实际 receipt：

```text
state     2202 bytes  3c57eca541fde4f9d939766940459dac7ac7058a3af899ed79154d1cf852eb3e
workflow   816 bytes  22cd75911994b708c19d1b7bfb1da84f264513dea59a9bd795a52e44933b0d32
tx        2136 bytes  2efb2729126903a1cd0d2f200565a225850e2fd3a0d10256f970b208318a75d6
ledger   64298 bytes  0be27e9220b6597d47ee657bbe5169134118340c77a7a0af3722a4eb1ad885c2
official 291096 bytes 00b244438bc8c66ab5daf208874c4fd1ed2ba5fc69ffd2dda87436eccc47f1a7
consumed  4523 bytes  3f0dc02a583c64dcedb160268bc0648fdcbc656b1fa395b98ebfb42adef3288e
```

官方来源清单记录1577条来源路径和92条官方补丁写入路径。ledger 最后一个事件为此 transaction 的 `OVERLAP_COMMAND`，记录退出码0和上述计量。原61826-byte前缀不变及恰好增加一个2472-byte事件，仍由独立审计逐字节确认，不以文件大小差单独推定。

ledger 记录本次操作结束时 combined apparent/allocated 为 `31129842816/31455227904` bytes，overlap 增量为 `1260363085/1285406720` bytes，VHDX overlap 增量为 `1207959552` bytes。它们是该次计量快照，不替代后续操作前的即时存储检查。历史失败原因字段仍保留，不能因其文字存在而误判当前 hard_stopped=true。

## 不变边界

本次授权不包括下载、编译、smoke、batch、GPU、训练、Hamiltonian/SCF 或其他 DFT 标签生成。D-018 仅取消总墙钟期限，CPU/GPU/存储约束继续执行，所有历史用量和失败证据保留。authorization 对象执行后保留，不因仍存在而重新取得执行资格；任何失败或拒绝后均不自动重试。
