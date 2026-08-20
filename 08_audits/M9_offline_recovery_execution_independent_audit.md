# M9 D-017 离线恢复执行独立审计

## 审计结论

本次只读审计结论为 **PASS**。`BLOCKING=0`，`NON_BLOCKING=0`。D-017 离线恢复事务已经以 `SUCCESS_COMMITTED` 完成；恢复结果满足先前冻结的包集合、预算抵扣、无网络执行、状态提交和可追溯性合同。当前允许进入受控 `source_prepare`，但本结论不授权执行 `source_build`、OpenMX smoke、批量 overlap、M9-05 或其他标签生成。

## 送审对象与边界

复核对象包括：

- `/home/evan-williams/deeph-m9/manifests/overlap_offline_recovery_transaction.json`，SHA-256 `faa7465df21dec7a98bdb1f18691d0946a497c64476300a5fa42414ca21cb24e`；
- `/home/evan-williams/deeph-m9/manifests/overlap_offline_recovery_parent.json`，SHA-256 `0edf3486a1aa1f6efa1f616ad675dff043663f6066905f60e20ec13996825a19`；
- `/home/evan-williams/deeph-m9/manifests/budget_state.json`，SHA-256 `8cfc897a7ad8ab7be509df7afa6c49d55e8b81112e3538fb58706993be7826f6`；
- `/home/evan-williams/deeph-m9/manifests/budget_ledger.jsonl`，SHA-256 `cac72ff3cd4bdcf3f1fc6f594fe9203bd29615ebb54e113a5482c0f7066076bb`；
- `/home/evan-williams/deeph-m9/manifests/overlap_workflow_state.json`，SHA-256 `82700a4f38a5e962416ef68d4465deb0da2511ee2e5c3976a24d150a29ac1def`；
- `/home/evan-williams/deeph-m9/logs/overlap_offline_apt_recovery.log`，SHA-256 `a7da2f0ee0246196e7759852870e6a2f16f01b397cbafd54c597f2c924539d1d`；
- 冻结包清单 SHA-256 `f54d61cbf4f6cb82dcd1cd0daa17ff2cf013f328b19d3222cff1a37dba637616`；
- 恢复控制脚本 SHA-256 `d8530d9d1a46ce7fc9b22d769948bbfaf704c416db9960a61f3852441ea17c14`。

本审计没有执行 `source_prepare`，没有解压或编译 HDF5/OpenMX，也没有运行 OpenMX。对包数据库执行的命令限于只读 `dpkg-query` 和 `dpkg --audit`。

## 事务与状态链

恢复事务 ID 为 `c40319013aa240c591c47471dfed6bd9`。状态历史严格为：

`PREPARED -> OFFLINE_APT_RUNNING -> RUNNING -> SUCCESS_PENDING_COMMIT -> SUCCESS_COMMITTED`。

父事务 ID 为 `d35cd6668a3c6bee74bd2fdc5ac82101`，父快照与原 `overlap_transaction.json` 字节完全一致，二者 SHA-256 均为 `0edf3486...a19`。父事务保持 `FAILED_COMMITTED`，包含 `command_timeout`、`cpu_bucket_overlap_build` 和 `overlap_command_failed` 三项原因；恢复没有改写失败历史。

最终 workflow 为 `AUDIT_PASSED`，`apt_install_completed=true`，`hard_stopped=false`，无 active transaction，且 `recovered_from_hard_stop` 精确绑定父事务。恢复事务自身记录 `exit_code=0`、`timed_out=false`、执行耗时 `7.839054273 s`，低于冻结的 `300 s` 恢复上限。

## 包数据库与安装结果

独立读取冻结 manifest 并重新运行组合 `dpkg-query` 后，45 个目标包均满足：

- 包名与 manifest 精确一致；
- 版本逐项精确一致，包括 automake 的 epoch 版本 `1:1.16.5-1.3`；
- 状态均为 `install ok installed`；
- 无缺失、额外或畸形目标记录。

重新计算全局 dpkg receipt 得到 682 项、SHA-256 `d07bfbbfe36e27b3d64b9c3c75105498a0138165c54066638d06b98f88d4ac95`，与事务 post receipt 完全一致。去除 45 个目标包后，剩余 637 个非目标包的 `package/version/status` 映射与 pre receipt 逐项完全一致。因此没有发现通过依赖求解静默升级或改写既有非目标包的路径。

独立执行 `dpkg --audit` 返回码为 0，stdout 和 stderr 均为空；`/var/lib/dpkg/updates` 为空，且其规范 receipt 与事务记录一致。

## solver、命令与无网络证据

恢复日志包含六条命令：本地 `.deb` 的 apt 模拟求解、dpkg no-act、dpkg unpack、dpkg configure、dpkg audit 和 apt check。六条命令均以固定前缀 `/usr/bin/unshare --net --` 执行。由日志重新解析出的完整 argv 列表，其规范哈希为 `0c32b89770602319765e66a2e6f75d8336d65084d63b390b5139db325057bca4`，与事务 receipt 完全一致。

独立网络 receipt 记录新网络命名空间内不存在非 loopback 路由；stdout 为空，其 SHA-256 为标准空串哈希。apt 模拟同时固定空 source list、空 source-parts、`Acquire::Retries=0`、HTTP/HTTPS proxy 为 false，并使用 `--no-download`。日志中未出现远端 URI 获取或下载记录。

从日志字节边界重建的 solver 输出 SHA-256 为 `ad9a9c55d82f95c1b4d050c63f4a4710d575b9b16003f224f4255bae96714c7a`，与事务记录一致；输出明确为 `0 upgraded, 45 newly installed, 0 to remove`，并将全部对象标记为 `local-deb`。日志本体的字节数和 SHA-256 也与事务 receipt 一致。

这里的“无网络”结论是对冻结执行合同的验证：网络命名空间、无非 loopback 路由、空源配置和日志证据相互一致。本次审计没有另行进行内核级 packet capture，因此不把该结论扩展为对宿主机同期所有进程网络活动的陈述。

## 预算、抵扣与 ledger

原始 `overlap_build` CPU 账面值继续保留为 `7200.075310528 s`。唯一 adjustment 将同一父 apt 超时的 `7200.075310528 s` 记为 `noncompute_apt_timeout` credit，并通过

\[
\max(0, 7200.075310528-7200.075310528)=0
\]

得到有效 `overlap_build` 用量 `0 s`。恢复耗时另记为 `offline_recovery_seconds=7.839054273`，没有覆盖原始 CPU 值。

ledger 的前 56,667 字节、57 行及末事件哈希均与事务保存的 pre-ledger receipt 匹配。恢复追加的 CPU adjustment 与 recovery 两个 event ID 各出现一次，载荷与事务 `commit_events` 精确相等；全 ledger 不存在重复 event ID。状态中的 adjustment ID 也仅出现一次。因此抵扣保持 append-only、幂等且可回溯到父事务 SHA。

按当前冻结代码重新计算，三个 CPU 桶的有效用量均为 0，预算 `violations=[]`。这只说明当前状态满足门控；后续 `source_prepare` 仍须使用冻结入口、正确 CPU bucket 和不低于 `1 GiB` 的 forecast，并在动作开始和结束时重新执行预算检查。

## 进入 source_prepare 的判定

当前满足 `source_prepare` 的状态前提：

- recovery gate 和 recovered follow-up frozen hashes 校验通过；
- workflow stage 为 `AUDIT_PASSED`；
- `apt_install_completed=true`；
- budget 与 workflow 均未 hard-stop；
- 无 active transaction；
- 当前预算无违规。

因此允许主 agent 通过唯一冻结入口启动一次受控 `source_prepare`。该动作必须保持 `overlap_action=source_prepare`、`cpu_bucket=overlap_build`、冻结 config、冻结 Linux 工作根、无自由 argv，并使用至少 `1073741824` bytes 的 forecast。若 source_prepare 失败，必须按原状态机提交失败和 hard-stop，不得手工跳至 `SOURCES_PREPARED`。

## 稳定问题清单

- BLOCKING：0。
- NON_BLOCKING：0。
- 新问题：无。

最终判断：**允许进入 source_prepare；不允许据此直接进入 source_build 或后续运行阶段。**

## 报告终检

本报告定稿后执行 UTF-8 控制字符扫描、活动本地 Markdown 链接检查，以及 Pandoc `markdown+tex_math_single_backslash` 到 HTML5 MathML 的 `--fail-if-warnings` 严格转换。最终 SHA-256 随交付消息报告。
