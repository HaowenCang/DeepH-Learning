# M9 source_build v4：宿主关机恢复后的单次构建消费链

日期：2026-09-01。状态：`IMPLEMENTED_PENDING_INDEPENDENT_AUDIT`。本文件只定义 v4 实施与门控对象；当前没有正式 v4 snapshot、gate、permit，也没有启动新的编译。主端测试结果不能替代独立审计结论。

## 授权、范围与父态

本工作包采用 [D-019](../00_scope/D019_standing_execution_authorization.md)、[持续执行授权原文](M9_standing_execution_authorization_20260831.md)及其[独立解释复核](M9_standing_execution_authorization_20260831_independent_review.md)。授权覆盖本工作包的实施、独立审计、机械安装、机器 permit、一次 source_build 和适用的失败恢复；技术门控、失败停机、历史保留和预算核验均不因持续授权而取消。

唯一父态是宿主关机恢复 v1 的独立执行事实 `PASS / BLOCKING=0 / NON_BLOCKING=0`。报告 SHA-256 为 `41fc9940fa8f7ac66b7d8978e429e7b41c3f3f1753e2b2c37c59148f36829c78`，完整证据 SHA-256 为 `42e05a042ab66c41b31e03ee9a126eec58a1480c382834bd07cd9244f88d602a`。恢复后正式 namespace 恰为 244 对象；完整证据的 64 位 canonical SHA-256、压缩载荷解码值和 v4 重新计算值均为 `b80ef48974aca25da529c8a1c81c5d1974dff91c03bb844ebd4e0090e42a0e22`。旧独立报告第 30 行显示值少写末尾 `22`，这是待本轮独立审计明确分级的报告转录差异；v4 不依赖该显示字面量，而是同时固定报告字节、证据字节，并强制解码 244 项后核验字节数、SHA 和 canonical identity，不能退回旧 193/220/221 对象基线。

当前 state/workflow 均非 hard-stop，活动事务为空，workflow stage 为 `SOURCES_PREPARED`，并精确包含恢复标记 `m9-source-build-host-shutdown-recovery-20260901-01`。事务槽保留 `4d7808af7df9418518a59afeba766eb9` 的 `source_build/FAILED_COMMITTED`，reason 恰为 `host_shutdown_external_interruption`；不得伪造成功父事务或重用较早 MPI 恢复事务。

当前 BUILD 树 5,319 对象 canonical SHA-256 为 `411a8a674559723f0616deafbe67c93d3e31453461fa6b2af26d4135bb3e1705`。历史 CLEAN 树仍为 `060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`，两者 portable receipt 均为 `cf91d95aa8802925da676dab35fe5bb991a6061f809b871bca488f4c50347cc0`，5,179 个普通文件没有硬链接。中断 ARCHIVE、日志 ARCHIVE、PRIVATE、journal 和公开恢复 snapshot 全部属于父态历史，v4 只读核验，不改写或删除。

## v4 权限对象与拒绝边界

v4 使用全新的路径、schema、operation 和 nonce：

- snapshot：`/home/evan-williams/deeph-m9/controls/source-build-v4`
- readiness gate：`/home/evan-williams/deeph-m9/manifests/source_build_v4_gate.json`
- execution permit：`/home/evan-williams/deeph-m9/manifests/source_build_v4_execution_permit.json`
- operation_id：`bb0b7c8b982d4d72a66a1f01f95533da`
- nonce：`f6cbfb8b789687b250133b173e8ebf934e8ad3c2e5f8d5ed2baecf6d53c641d6`

旧 v3 snapshot、gate、permit、operation `7bc4139f7a9c4b768d3f9ec68c1d1048`、nonce `a930f2b8e7ac449bb251482012eb99d1c7032df764985aaac34519bf6db2013a`及已消费 capability 全部保留为历史证据，但不能构成 v4 权限。旧 v3 permit SHA-256 `10d11a4bebc4f8d1595cfdb4bdd21d795848b643db556724ec57598a9d06c856` 已被恢复后的 runtime 漂移和新事务事实双重失效。新 launcher receipt 必须绑定 `v4_binding`，缺失该字段或提供旧 binding 均拒绝。

v4 唯一动作仍为 overlap-only `source_build`。它不授权 source_prepare 重放、结构 500 smoke、450 结构 batch、训练、GPU、Hamiltonian/SCF、正式 DFT 标签或自由命令。当前数据门控 `M9-DATA-B01` 不因本构建工作包自动关闭。

## 实现、闭集与预算

新实现为 `m9_source_build_v4_consumer.py`、`m9_source_build_v4_install.py` 和 `m9_source_build_v4_launcher.py`。它们沿用已审计 v3 的单次 capability、source-only loader、原预算事务和失败提交机制，仅版本化权限链并将父态改为宿主关机恢复后的 244 对象及当前 BUILD。原 build driver SHA-256 `ab6632784a744fd3f66c95aac30a56767f67af3d8d81147df2fc0d72b67102ec` 仍按已审计 MPI 规则精确派生为 `5652ee35a3595f42bd3050e5825419175fc84526a421a0500559d4146f253d00`；common 模块不重载，预算 capability 上下文只安装一次。

原预算文件 SHA-256 为 `a94902a942f98217171be5d9967f469a4dd4563c80e6e6ef3d68e6cede71168d`，仍只进行 scope/action 两处已审计字面量派生，派生 SHA-256 为 `94050d73f498b84ab0054f64f1b04ea8667067f86a54ed3f352e6b926a9e691e`。不修改 CPU、GPU、存储上限，不重置或抵扣新增历史。2026-09-01 本工作包冻结前的只读即时检查得到：`effective_overlap_build=307.1697352600013` 秒，限额 7,200 秒，4 GiB forecast 的 `violations=[]`；combined allocated 32,208,130,048 bytes，overlap baseline 后增量 2,038,308,864 bytes，VHDX 增量 2,382,364,672 bytes。该读数仅证明当时可行，安装、permit 和执行前门控均须重新调用原预算函数。

冻结来源闭集恰为 22 个文件：三个 v4 controller、两个 v4 测试、本文、D-019/授权原文/授权解释报告、宿主关机恢复执行报告及证据、receipt 工具、MPI repair、旧 v1/v2/v3、MPI 恢复及宿主恢复五份 manifest、旧 consumer/overlap manifest，以及 v1/v3 安装 verdict。manifest 自身不作为其自身成员。

安装 snapshot 包含上述 22 项、新 frozen manifest、实施 report/verdict 和派生 budget，共 26 个成员，再加 `snapshot_manifest.json`，目录内恰为 27 个普通单链接文件。以 244 对象父态计算，安装新增 snapshot 目录、27 文件及 gate 共 29 项，正式 namespace 应为 273；permit 再新增 1 项至 274。只允许 controls/manifests 父目录发生安装规则规定的 metadata 变化，其他 244 个父对象必须按 receipt 保持。

## 测试与独立门控

主端临时测试必须使用固定 Python 3.9.23 `-I -S -B`，不得生成 bytecode。迁移回归覆盖 pristine-only 安装、零写 preflight、安装中断保留 staging、permit 不可重发、完整树和 root-only 历史核验、未知对象拒绝、首次正式写前重验、原预算失败提交以及真实 UID1000 临时安装入口。v4 新增负例覆盖：244 对象压缩 envelope 的 count/base64/bytes/SHA/canonical identity；新恢复执行证据和报告漂移；当前 BUILD 和恢复事务精确绑定；旧 v3 gate/permit/operation/nonce；缺失或伪造 v4 launcher binding。临时链测试的计算叶保持只读，不把测试 PASS 记作正式编译。

门控顺序不可合并：

1. 独立 agent 审计 v4 实现、冻结闭集、测试和本工作包，结论必须为 `PASS/0/0`。
2. 主端读回并核验实施报告/verdict 后，以已审核 single-FD loader 先执行一次零写 preflight，再执行一次机械 install；任一步失败即保留现场并停止。
3. 独立 agent 审计实际 273 对象、真实 UID1000 固定入口、缺 permit 负例和即时预算，必须 `PASS/0/0`。
4. 主端只执行一次 permit 动作；独立 agent 再审计实际 274 对象、permit、唯一 argv、当前 runtime/树和预算，必须 `PASS/0/0`。
5. 主端只执行一次冻结 source_build。无论成功、失败、超时或宿主异常均先保存事实，旧 permit 不得重放；执行后由独立 agent 审计构建、自测、记账、产物和失败边界。

实施 verdict schema 为 `m9-source-build-implementation-verdict-v4`，安装 verdict schema 为 `m9-source-build-installation-verdict-v4`。两者均为严格七字段 `schema/status/blocking/non_blocking/frozen_sha256/report_path/report_sha256`，问题数必须是整数 0。独立审计报告/verdict 尚不存在时不得创建正式 snapshot；安装事实报告/verdict 尚不存在时不得创建 permit。

## 唯一执行命令

门控全部通过后的唯一构建 argv 为：

```bash
/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B \
  /home/evan-williams/deeph-m9/controls/source-build-v4/m9_source_build_v4_consumer.py \
  run --build-operation-id bb0b7c8b982d4d72a66a1f01f95533da \
  --bucket none --cpu-bucket overlap_build --forecast-bytes 4294967296 \
  --overlap-operation --overlap-action source_build \
  --config /mnt/e/Projects/Codex/DeepH/06_reproduction/configs/m9_overlap_only_contract.json
```

解释器真实路径、UID1000、`-I/-S/-B`和逐 token argv 必须全等。root installer 仍由已审核 single-FD loader（SHA-256 `c68e43b5de4fdadb44254fbfdd543f5ba2a29b6e41994021c55a3287b5f7491f`）启动；参数依次绑定 installer 路径及 SHA、`preflight/install/permit`、consumer SHA、frozen SHA、实施 verdict/report SHA，permit 另加安装 verdict/report SHA。D-019 已覆盖人工授权，但任何技术门控失败仍必须停止。
