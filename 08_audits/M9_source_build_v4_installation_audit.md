# M9 source_build v4 独立安装事实审计

日期：2026-09-01。审计角色：独立子 agent。结论为 **PASS / BLOCKING=0 / NON_BLOCKING=0**，两个问题计数均为整数。本结论只证明 v4 snapshot 与 readiness gate 的实际安装事实，不是 execution permit、source_build、构建产物或自测的通过结论。主端安装记录仅用于定位调用线索，没有作为 PASS 的自证。

## 安装权威

独立重算并核验以下输入：frozen manifest `5862155306e595f268e996a9712194faabd2347e94b73a0118ebb403c763cf09`，实施报告 `4309fde795eadfae3878db9563223ec8b40b2dbd40290e89734e640ced947795`，严格实施 verdict `a1878a1121ff361e8aba3571d405e032d6d97ddb32ab51d04ee0ba803fcd2d78`。verdict 为严格七字段 `m9-source-build-implementation-verdict-v4`，精确绑定 frozen SHA、报告绝对 WSL 路径及报告 SHA，问题数是整数 0。

主记录称 single-FD loader 分别调用一次零写 preflight 和一次 install，二者退出 0。正式持久对象可以证明一次成功安装提交：只有一个新 v4 snapshot 和一个 readiness gate，gate 不可覆盖，pristine-only installer 在这些目标存在时不能再次成功安装。零写 preflight 不产生持久调用计数，因此正式 namespace 不能独立证明其历史调用恰为一次；该限制不影响本报告对当前安装事实的判定。

## 273 对象闭集与旧历史

以宿主关机恢复独立证据中的完整 244 对象为父态，root 对 manifests、controls 与 `/root/deeph-m9-control` 重新进行两次全量 receipt 采集。安装后恰为 273 对象，canonical SHA-256 为 `125eb54b21a7f0b23d558c32b88328544d8093f56f4fcf5e4f10e6c3d5935446`。相对父态没有删除，恰新增 29 项：v4 snapshot 目录、目录内 27 个文件和 v4 gate。

旧 244 对象中仅 `/home/evan-williams/deeph-m9/controls` 与 `/home/evan-williams/deeph-m9/manifests` 两个父目录的允许 metadata 发生变化；其余旧对象 receipt 逐项全等。controls 的目录链接计数按新增 snapshot 子目录增加 1；manifests 只新增普通 gate 文件。root-private 历史及 8 个 root-only 历史文件由 root 实际读取并哈希，未使用 UID1000 的 metadata 替代；未知正式对象为 0。

完整 273 receipt 的可逆 gzip/base64 载荷、四份原始 runtime 的压缩载荷及命令结果摘要已封存于 [postexecution evidence](M9_source_build_v4_installation_postexecution_evidence.json)，SHA-256 为 `aadf3801eaf50a0861bd330bb9f865758047d08749348e79d399c2f59cf7d3d3`。独立解压复核得到 273 项、114969 canonical JSON bytes 和同一 canonical SHA。

## Snapshot、gate 与许可分离

`/home/evan-williams/deeph-m9/controls/source-build-v4` 是 root:1000、0550、nlink 2 的真实目录。目录中恰有 27 个成员，全部是 root:1000、0440、nlink 1 的普通文件，没有 symlink、hardlink、子目录、缓存或额外对象。`snapshot_manifest.json` 为 4324 bytes，SHA-256 `210d00c6f1d145adbc71c362261e2607faa8066a58c6f4f1d63aa423c8e9b0c7`，其 schema 正确并精确列出其余 26 个 payload；逐个成员的字节数和 SHA 均与 manifest、22 项 frozen closure、实施报告/verdict及派生预算相符。

readiness gate 为 root:1000、0640、nlink 1 的普通文件，SHA-256 `dcd0a0ed3307add49df5b7586ba0bf01b2fc55b0469a42067893e563ba2ff3c1`。它精确绑定：

- schema `m9-source-build-readiness-v4`、scope `ALLOW_ONE_SOURCE_BUILD_AFTER_PREPARED`、action `source_build`；
- operation `bb0b7c8b982d4d72a66a1f01f95533da` 与 nonce `f6cbfb8b789687b250133b173e8ebf934e8ad3c2e5f8d5ed2baecf6d53c641d6`；
- frozen、snapshot、实施报告/verdict、D-019 授权、root 历史 attestation 和安装时完整 runtime receipt。

`source_build_v4_execution_permit.json` 及其临时路径均缺席。v3 gate、permit、operation、nonce及 capability 不能满足 v4 schema 或 binding；readiness 安装没有隐式签发执行许可。

## Runtime、源码树、预算与禁用对象

gate 中的五项 runtime receipt 与安装后实际字节、inode、owner、mode、链接计数和时间戳全等。四份可变 runtime 在真实 UID1000 验证前后逐字不变：ledger SHA-256 `f3f44ee5169bbeb44d175ff0aa381cda70684ad66f11ce57725c2e774471d4c7`，state `cdfcf813f1e6c4759b0a8ef93a76d95a50d6e586ba5f4652908f6b1dd375dd7b`，workflow `271bd1c756b55db52b7cb479a7d679edb95e2d3bd33b21cfff88122f40459b34`，失败 transaction `433462132e40fd9f160bce150e20a7c3149227ad8bf4957e8d19d71e389ddb58`。state/workflow 均非 hard-stop且活动事务为空，stage 仍为 `SOURCES_PREPARED`；旧宿主关机失败事务和恢复标记保持。

BUILD 与退休失败树各 5319 个 receipt，前后完整字典相等，canonical SHA-256 分别为 `411a8a674559723f0616deafbe67c93d3e31453461fa6b2af26d4135bb3e1705` 和 `060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`。HDF5/OpenMX 安装 prefix、构建产物 manifest、编译日志及材料、训练输出等禁用对象均缺席；进程快照中没有 consumer、launcher、compiler、make、HDF5 或 OpenMX 构建进程。

安装 snapshot 中的派生预算 SHA-256 为 `94050d73f498b84ab0054f64f1b04ea8667067f86a54ed3f352e6b926a9e691e`。只读解析唯一请求得到 `source_build / overlap_build / 4294967296`，即时 `violations=[]`；有效 build CPU 为 `307.1697352600013` 秒，低于 7200 秒上限。预算历史、GPU 用量、存储基线和抵扣记录未被安装或只读验证改变。

## 真实 UID1000 验收与零写负例

实际用户 `evan-williams` 的 euid 为 1000。固定解释器 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 报告 Python 3.9.23，isolated/no_site/dont_write_bytecode 均为 true。入口使用实际已安装 snapshot，不是项目副本或临时夹具。

`verify-ready` 退出 0、stderr 为空，返回 `status=PASS`、`action=source_build`、`source_build_executed=false`，runtime identity 为 `c042a2107e8f90782f295ded5f3eca7d81338bee597087d0c0d64549b42e1446`。`verify-execution` 退出 1、stdout 为空，并精确在读取 `/home/evan-williams/deeph-m9/manifests/source_build_v4_execution_permit.json` 时抛出 `FileNotFoundError`；没有到达 capability 消费、launcher 或预算事务写入。

为分别取得命令回执、验证证据封装及最终基线，审计期间共执行四组相同的只读 `verify-ready`/`verify-execution`，结果一致。每组前后完整 273 namespace、四份 runtime 与两棵 5319 对象树均全等。这些调用只获取原 `budget.lock` 进行验证，不写正式状态。首次组合采集脚本还曾在调用 consumer 前因审计器自身的路径类型错误退出；它没有执行任何被审入口或改变正式对象。

测试后项目 `06_reproduction` 及已安装 snapshot 中的 `__pycache__`、`.pyc`、`.pyo` 数量均为 0。`git diff --check` 与本报告的 Pandoc strict Markdown 检查通过。

## 最终边界

v4 机械安装事实满足 **PASS / BLOCKING=0 / NON_BLOCKING=0**。该结果足以让主端按已冻结 installer 的独立安装 verdict 绑定流程签发一次新的 v4 machine permit；它本身不是 permit，也不允许直接绕过执行前独立核验。permit 安装后应以本报告保存的 273 对象基线证明只新增许可文件及允许的 manifests 父目录 metadata 变化，并再次执行真实 UID1000 `verify-execution` 零写验收。只有后续执行前 PASS 才能启动唯一 source_build；结构 smoke/batch、材料计算、GPU、训练和 M9-DATA-B01 仍不在本结论范围内。
