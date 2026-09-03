# M9 source_build v5 实施工作包

日期：2026-09-03。状态：`PENDING_INDEPENDENT_IMPLEMENTATION_AUDIT`。本工作包完成恢复后下一版 source-build 消费链的实施与冻结准备，但尚未取得独立实施审计结论，未安装 snapshot/gate，未签发 permit，未调用正式 source_build。用户要求在当前工作收尾后暂停，因此本轮不得继续独立审计、安装、执行前复核、编译或后续数据与训练工作。

## 父态与证据边界

v4 唯一 source_build 在 HDF5 `make check` 期间受 WSL 实例 shutdown 外部中断。恢复 v2 已机械提交，事实更正版独立审计为 `PASS/BLOCKING=0/NON_BLOCKING=0`：报告 SHA-256 `4d1d8b20327256b807203861f69e850d104858bc86a13e77dde77dff8f2c9e4b`，postexecution evidence SHA-256 `b3477ede6590cda56d5cf45bb1a16809e591d6aa5858531807f5cc1513eaca36`。正式 state/workflow 非 hard-stop、active 为空、stage 为 `SOURCES_PREPARED`；事务 `d52575f446d3c62f0fc93c3c65f3c959` 已按 `138.401802566` 秒保守墙钟上界提交为 `FAILED_COMMITTED`，reason 为 `wsl_shutdown_external_interruption`。

恢复事实 evidence 只含 301 项正式 namespace 的摘要，不含 UID1000 后续验证所需的完整 root-only receipt 载荷。因此，主端在固定 Python 3.9.23 `-I -S -B`、root 和 `budget.lock` 共享锁内连续捕获两次正式 namespace 与 BUILD，生成 `M9_source_build_v5_parent_namespace_evidence.json`。该证据 SHA-256 为 `8a02bc5650cf75e9e86f200204e9fe449c516c5693ff98b526ae8d45243506be`，正式 namespace 为 301 项、canonical SHA-256 `5153de04dd6a33f8851cd898d8af9c8e655a57a161d31f70a7f60dc8032c0f42`；完整 canonical JSON 为 127,202 bytes，以确定性 gzip/base64 封装。BUILD 为 5,319 项、canonical SHA-256 `c9ac7a5cb34ef582ce06965d568a6fe0ded9ef4f2a51e2c07ab1e5e1898f1521`。该父证据由主端生成，仍须在 v5 独立实施审计中从正式对象重新验证，不得把其自述当成独立证明。

## 版本化消费链

新对象为：

- `m9_source_build_v5_consumer.py`：UID1000 唯一 action consumer；
- `m9_source_build_v5_launcher.py`：消费单次 capability 并通过 source-only loader 运行冻结 build driver；
- `m9_source_build_v5_install.py`：仅在独立实施 verdict 精确 PASS 后允许机械 preflight/install/permit；
- `test_m9_source_build_v5_consumer.py` 与 `test_m9_source_build_v5_chain.py`：合成、真实 UID1000 临时 fixture 与完整链路负例；
- `m9_source_build_v5_frozen_hashes.json`：本工作包与上述对象的完整来源闭集。

全新 operation 为 `c35a556951014126894fda5a99e5c101`，nonce 为 `4bf38debe62983e08de29305b48483066a876c190de0c2b170d9ed61fb141cc0`。正式目标路径版本化为 `controls/source-build-v5`、`source_build_v5_gate.json` 和 `source_build_v5_execution_permit.json`；旧 v4 snapshot、gate、permit、operation、nonce 与 consumed capability 只作为历史证据，不能成为 v5 authority。

consumer 严格绑定恢复事实更正版、postexecution evidence、301 项父 namespace 载荷、四份恢复后 runtime、5,319 项 BUILD、D-019、既有授权解释、全部历史 consumer/build/recovery manifests 及旧 v1/v3/v4 安装 verdict。父证据还固定已消费 v4 capability SHA `8d6aff34eec0ee29ce8a7b8e6a8fdf8a76b78ec1fe5a5bd584ee1e2587607204`、旧 gate/permit 摘要和缺失 launcher receipt。任何父 namespace、runtime、BUILD、root-only receipt、历史 manifest、旧权限对象、产品缺席或锁 receipt 漂移均应在首次写入前拒绝。

OpenMPI 修复与实际构建逻辑不变。原 `m9_openmx_build.py` SHA-256 `ab6632784a744fd3f66c95aac30a56767f67af3d8d81147df2fc0d72b67102ec` 仍由冻结 `m9_openmx_mpi_repair_v1.py` 精确派生为 `5652ee35a3595f42bd3050e5825419175fc84526a421a0500559d4146f253d00`。原 budget 模块 `a94902a942f98217171be5d9967f469a4dd4563c80e6e6ef3d68e6cede71168d` 仍只作既有两字面量派生，得到 `94050d73f498b84ab0054f64f1b04ea8667067f86a54ed3f352e6b926a9e691e`；预算上限、D-017 抵扣、D-018 无总墙钟策略、GPU 与存储约束不变。

## 已完成的非正式验证

固定 Python 3.9.23 `-I -S -B` 下，consumer 套件 42/42 通过，chain 套件 15/15 通过。测试仅写临时 fixture，不创建正式 v5 snapshot、gate、permit、capability、transaction、日志或构建产物，不运行 compiler、HDF5、OpenMX、下载、结构计算或训练。

测试覆盖新的 301 项父 namespace envelope 与其恢复事实绑定、恢复后 marker/事务/计量、26 项来源闭集、旧 v4 权限隔离、真实 UID1000 verifier、root-only 内容与 metadata 漂移、unknown unreadable 对象、snapshot/gate/permit 字节绑定、budget 首写复核、capability argv、launcher receipt、source-only module provenance、成功/失败 post-child 路径和禁止产物。v5 保留 v4 已审计的 native transaction、失败提交与预算计量逻辑，不以测试 fixture 替代正式安装或执行事实。

## 后续门控与暂停点

恢复工作时应从本冻结实现的独立实施审计开始。只有独立子 agent 给出严格 `PASS/BLOCKING=0/NON_BLOCKING=0` 并生成匹配 schema 的 implementation verdict，主端才可各执行一次机械 preflight 和 install。安装后还须独立事实审计；该审计通过后才能签发单次 permit，并在独立执行前复核通过后调用唯一 source_build。任何阶段失败均保留现场并停止，不自动重放。

当前暂停点不改变 D-019 已有人工授权，但技术门控仍关闭。恢复 PASS 与本实施包完成均不等于 OpenMX 构建 PASS；structure 500 smoke、450 结构 batch、overlap 生成、训练和物理验证仍未放行，`M9-DATA-B01` 继续 OPEN。
