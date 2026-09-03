# M9 source_build v4 独立实施审计

日期：2026-09-01。审计角色：独立子 agent。结论为 **PASS / BLOCKING=0 / NON_BLOCKING=0**，两个问题计数均为整数。本结论只覆盖冻结的 v4 实施及当前只读父态，不是安装事实、机器 permit、编译或构建自测的通过结论。

## 冻结权威与闭集

独立重算 `m9_source_build_v4_frozen_hashes.json` 得到 SHA-256 `5862155306e595f268e996a9712194faabd2347e94b73a0118ebb403c763cf09`；schema 为 `m9-source-build-frozen-v4`，22 个成员全部逐字匹配。核心对象如下。

| 对象 | SHA-256 |
| --- | --- |
| consumer | `0466cb4d1ff5ef1f7b0fc4b20c45e9d249110a7ee36a2bde8f419c76968219ad` |
| installer | `ed775d8e3f492e80b323ca75fb23be1f22a499accf9fd0eab6a8021327e4a4e5` |
| launcher | `1a8b796edc482498dda8f3b196451f02c09f4693417689919ca12d4576edc1dd` |
| consumer tests | `b111c8f77972cb334d7ab304eb3e465d3212144745d98b1f6530bb415ee7988c` |
| chain tests | `df3a28952e6fb0107755350e75247ea0707992215accc59e2c67049b286fbe7d` |
| work package | `8d90fa95d2514229c5e2afe7b964c7f30b7f2ad643663ddcb2d3e601ec0bb377` |

consumer 还逐项固定并读取 7 份旧 manifest。独立展开得到成员数依次为 25、16、10、12、9、19、9，共 81 个不重复路径；所有成员哈希全等且无相互冲突。实施与安装 verdict 均要求严格七字段，`blocking` 和 `non_blocking` 使用 `type(value) is int` 排除布尔值替代。D-019 持续人工授权及其独立解释被纳入冻结闭集，但不替代实施、安装和执行前的独立 PASS，也不复用旧机器 permit 或 capability。

## 244 对象父态及历史转录差异

宿主关机恢复独立执行报告与完整机器证据分别固定为 `41fc9940fa8f7ac66b7d8978e429e7b41c3f3f1753e2b2c37c59148f36829c78` 和 `42e05a042ab66c41b31e03ee9a126eec58a1480c382834bd07cd9244f88d602a`。独立解码机器证据的 base64/gzip envelope，核验了解压字节数、原始 SHA、JSON canonical identity、`second_capture_equal=true` 及恰好 244 个 receipt。正式 WSL 的 manifests、controls 和 `/root/deeph-m9-control` 全量重采集也恰为 244 对象，与证据逐项全等，完整 canonical SHA-256 为 `b80ef48974aca25da529c8a1c81c5d1974dff91c03bb844ebd4e0090e42a0e22`。

旧独立执行报告第 30 行的显示字面量只有 62 个十六进制字符，少末尾 `22`；机器证据字段是完整 64 位值，且本轮现场重算与机器证据相同。v4 固定旧报告原字节用于历史不可改写证明，但不解析该行作为父态 identity；实际门控固定机器证据 SHA，解压后同时重算 payload SHA 与 canonical identity。工作包也显式披露该差异。因此，这是既有报告的显示转录边界，不会把旧 193/220/221 对象基线误认为当前父态，也不构成 v4 实施的 blocking 或 non-blocking 问题。

正式 state/workflow 均非 hard-stop、活动事务为空，stage 为 `SOURCES_PREPARED`，并包含恢复标记 `m9-source-build-host-shutdown-recovery-20260901-01`。事务仍是 `4d7808af7df9418518a59afeba766eb9` 的 `source_build/FAILED_COMMITTED`，reason 为 `host_shutdown_external_interruption`，没有伪造成构建成功。当前 BUILD 与退休失败树各 5319 个 receipt，canonical SHA-256 分别为 `411a8a674559723f0616deafbe67c93d3e31453461fa6b2af26d4135bb3e1705` 和 `060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`；禁用构建产物均缺席。

## 安装、许可与一次执行链

installer 的 preflight 只读核验冻结来源、完整 root/private 历史、当前 BUILD/退休树、旧预算派生、唯一 argv 和即时预算。安装为 pristine-only；snapshot、staging、gate、permit 及相应临时文件任一预存即拒绝。正式首次写前仍在原 `budget.lock` 内重验完整 244 对象父态和两棵树；snapshot payload 均以冻结哈希单文件固定读取，目录成员和 manifest 闭集随后再次核验。安装只产生 readiness gate，不产生 permit；permit 还需要独立安装 PASS 的严格 verdict/report，并再次执行完整 installed preflight。中断现场保留且不能自动重放。

consumer 仅接受实际 UID1000、固定 Python 3.9.23 `-I -S -B`、新 snapshot 路径和唯一完整 argv。v4 operation `bb0b7c8b982d4d72a66a1f01f95533da`、nonce `f6cbfb8b789687b250133b173e8ebf934e8ad3c2e5f8d5ed2baecf6d53c641d6`、gate schema 和 permit schema均与 v3 分离；旧 v3 gate、permit、operation 或 nonce不能通过。

预算代码只把旧 source_prepare 的 scope/action 唯一字面量替换为 v4 source_build，原文件 SHA-256 `a94902a942f98217171be5d9967f469a4dd4563c80e6e6ef3d68e6cede71168d` 精确派生为 `94050d73f498b84ab0054f64f1b04ea8667067f86a54ed3f352e6b926a9e691e`，其他预算字节及 CPU/GPU/存储、事务和失败提交逻辑不变。正式只读解析唯一请求得到 `source_build / overlap_build / 4294967296`；即时 `violations=[]`，有效 build CPU 为 `307.1697352600013` 秒，低于 7200 秒上限。

原预算的第一次 `atomic_json` 调用由 v4 guard 在持锁状态重新执行完整 `verify_gate(require_permit=True)`，因此首次预算状态写之前再次证明父态、两树、许可、argv 和预算权威。之后使用原生事务写入；子进程结束后的静态 `execution_binding` 不错误要求 RUNNING/终态 runtime 等于执行前父态。launcher 将 BOUND capability 精确绑定真实父/子 argv、PID、action、bucket、4 GiB forecast 和 v4 authority，消费后才加入冻结依赖路径；只加载 common 与经 MPI repair 精确派生的 build driver。父回执核验 consumed/receipt、隔离 bootstrap、来源闭集、原 driver SHA 与派生 SHA。事后权威异常被转换为原预算可捕获的 `ValueError`，保留 CPU 计量和失败 hard-stop 提交路径。

## 独立测试与正式只读证据

使用 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 独立运行：

- v4 consumer 42/42，v4 chain 15/15；
- v3 consumer 40/40，v3 chain 15/15；
- MPI 恢复 16/16，宿主关机恢复 17/17；
- overlap 控制回归 110/110。

共 255 项退出 0。v4 临时链以真实 UID1000 从临时 root-owned snapshot 运行实际 consumer/launcher，验证真实 common capability 上下文、MPI 派生 driver、PASS/FAIL receipt 和父 validator；计算叶仅执行只读工具链核验，没有调用 configure、make 或正式构建。机械安装、permit、故障注入和预算失败提交均只发生于临时隔离夹具；测试输出中的 installation/permit receipt 不是正式环境事实。

全部测试结束后，正式 244 对象再次全量重采集，仍与机器父态逐项相等，canonical SHA 保持 `b80ef48974aca25da529c8a1c81c5d1974dff91c03bb844ebd4e0090e42a0e22`；两棵 5319 对象树哈希不变。正式 v4 snapshot、staging、gate、permit及临时文件全部缺席。`06_reproduction` 下 `__pycache__` 目录和 `.pyc` 文件均为 0。

## 最终边界

该冻结实施满足进入主端既有 single-FD loader 的一次零写 preflight 和一次机械 install 的条件。本审计没有调用正式 preflight、install、permit、consumer main、launcher 或 source_build，也没有修改正式 WSL、源码树或旧审计对象。安装完成后仍须独立验收实际 273 对象闭集和真实 UID1000 入口；机器 permit、执行前独立 PASS 和唯一 source_build 执行属于后续门控。结构 smoke/batch、材料计算、GPU、训练及 M9-DATA-B01 均不在本结论范围内。
