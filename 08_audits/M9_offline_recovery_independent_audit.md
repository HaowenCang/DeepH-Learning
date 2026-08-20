# M9 overlap-only 离线 apt 恢复定点独立审计

## 审计结论

本次定点复核结论为 `FAIL`。当前统计为 `BLOCKING=7`、`NON_BLOCKING=0`。不得建立状态为 `PASS` 的 `overlap_offline_recovery_gate.json`，不得执行 `overlap-recover-offline-apt`，也不得以当前对象进入安装、HDF5/OpenMX 构建或结构 smoke。

45 个本地 Debian 归档本身、用户授权记录、无网络命名空间能力和离线求解结果均已得到较强支持，但当前运行时合同仍不能保证从签名来源、恢复门、失败提交、CPU 调整到账本和后续普通动作形成不可穿透的状态链。七项问题均可在 D-017 已批准的恢复范围内通过控制实现修复；不需要改变材料、DeepH/OpenMX/HDF5 版本、允许输出或物理范围。

本轮送审快照的主要 SHA-256 为：

- `m9_budget.py`：`3be0b4d6bbd1d7019adb2bac180d0d8f444e5eb06436cd5c14ddae7efc8f978c`；
- `m9_offline_apt_manifest.json`：`f54d61cbf4f6cb82dcd1cd0daa17ff2cf013f328b19d3222cff1a37dba637616`；
- `budget_contract.json`：`088597e092755dae9b25af1377ea72d70e140e5aa2822155b7b489ababfe8c62`；
- `m9_overlap_only_contract.json`：`327e37d130504944babf6a9c3ed5d4dcc0e8b05b2b04979300ac12cfaf3377ea`；
- `test_m9_overlap_controls.py`：`bfb5f20bb6f1a69cf091839421890ea5838ebebf78458b8093d4cc4fb806b1bf`；
- `M9_offline_recovery_authorization.md`：`ce2c61035c7ee1e99f178f43ae51073dd8895bd892e8e1e31e4e813326c5e1cc`；
- 旧 `m9_overlap_frozen_hashes.json`：`365547aa3107de393eefa6767c4f44e90e54b2490b174546c9f825c211db57af`。

## 边界和独立方法

本次只读核对项目文件、现有 WSL 状态、Ubuntu APT 索引和本地归档；执行了无安装作用的求解模拟、哈希复算、签名和索引记录核对、网络命名空间检查及冻结 Python 测试。没有安装或配置任何包，没有创建 recovery gate，没有重置预算或 workflow，没有解压或编译 HDF5/OpenMX，也没有运行 OpenMX。唯一新增项目文件为本报告。

独立核验得到以下正面证据：

- 45/45 归档的 bytes、MD5、SHA-256、package、version 和 architecture 与清单一致，总字节数为 17,693,344；
- 45/45 的 package/version/architecture/SHA-256 可在四个冻结 Packages 索引之一找到；四个 Packages 文件的 SHA-256 和字节数均可在相应、通过 Ubuntu archive keyring 验签的 InRelease 的 `SHA256` 段找到；
- root 下的 `/usr/bin/unshare --net` 仅产生关闭的 loopback 且无路由；正式命令构造对 solver、unpack、configure、audit 和 `apt-get check` 均加该隔离层；
- 禁用软件源、禁用代理并使用 `--no-download` 时，独立 solver 重放为 `0 upgraded, 45 newly installed, 0 to remove`，45 个 `Inst` 对象均来自 `local-deb`；
- 当前 `dpkg --audit` 和 `/var/lib/dpkg/updates` 为空，目标包尚未安装；
- 授权记录给出唯一 ID、原始 CPU 保留、仅父 apt timeout 可获 credit、300 秒恢复限额和失败重回双 HARD_STOP 的边界；恢复门代码核对其固定路径和 SHA-256；
- `m9_budget.py` 使用固定 Python `-I -S -B`、固定 PATH、root 前置检查、新进程组和 SIGTERM 后升级 SIGKILL；原失败 transaction 不由恢复失败函数覆盖。

上述证据不足以抵消下述运行时阻塞。

## 稳定阻塞项

### `M9-REC-B01`：签名来源链的运行时实现仍失败

`verify_recovery_source_indices()` 现已尝试把逐包记录绑定到 Packages，但把 `(Package, Version, Architecture)` 映射为单个记录；相同身份在多个组件出现时，后读记录覆盖前读记录。当前 `ocl-icd-libopencl1` 同身份、同 SHA-256 可见于不止一个索引，而清单 URL 指向 `universe`，单值覆盖后取到 `main`，因此正式测试在该包上退出。

独立以冻结 Python 运行 22 项测试，结果为 21 项通过、1 项错误：`test_offline_recovery_manifest_and_source_chain` 报告 `offline package index record mismatch`。这不是归档哈希错误，而是多记录建模错误。

此外，运行时仅核对 InRelease 签名和 Packages 自身哈希，尚未解析 InRelease 的 `SHA256` 段，核对每个 Packages 的相对路径、字节数和摘要。独立审计证明当前四条关系成立，但执行入口本身没有强制该关系。

最小关闭条件：索引表应保留同键的记录集合，并要求至少一条记录同时匹配规范化 Filename 和 SHA-256；不得依赖遍历覆盖顺序。执行入口还必须从已验签 InRelease 中解析 `SHA256` 段，逐项核对四个 Packages 的 suite/component 相对路径、bytes 和 SHA-256。补充重复身份、错误 component、错误 InRelease 摘要和错误索引长度负例，并使冻结 Python 全部测试通过。

### `M9-REC-B02`：recovery gate 不具有强制闭集

`verify_recovery_gate_and_hashes()` 只要求 `files` 是非空映射，然后核对映射中主动列出的文件；它不要求关键对象必然出现。因此，一个结构合法但只列授权记录或其他单个文件的 gate 可以绕过 `m9_budget.py`、offline manifest、budget contract、overlap contract、测试和冻结清单的绑定。函数也不要求固定审计报告路径、D-017 recovery decision ID 或本报告身份。

最小关闭条件：代码内定义 recovery gate 的必需对象闭集和唯一审计报告路径，至少绑定本报告、授权记录、`m9_budget.py`、offline manifest、budget contract、overlap contract、测试、工作包及新的完整冻结清单；要求集合精确相等或明确的受审 allowlist 精确相等，并核对 schema、decision ID、报告 `PASS/BLOCKING=0/NON_BLOCKING=0` 及全部 SHA-256。增加缺一文件、额外文件、旧报告替换和路径别名负例。

### `M9-REC-B03`：非终态恢复不能在重启后自动提交 HARD_STOP

入口先把 recovery transaction 写为 `PREPARED`，workflow 写为 `RECOVERY_AUTHORIZED`，随后在锁外创建临时目录、命令和日志。该区域不在覆盖全部异常的事务保护内；进程崩溃、kill 或临时目录创建失败会遗留非终态 transaction 和非 `HARD_STOP` workflow。

再次调用入口时，代码先要求 workflow 已为 `HARD_STOP`，随后才检查 recovery transaction 是否存在。因此它不会把遗留的 `PREPARED`、`OFFLINE_APT_RUNNING` 或 `RUNNING` 恢复为双 HARD_STOP，只会在前置条件处退出。

最小关闭条件：入口在任何新 preflight 之前识别 recovery transaction；若为非终态且无合法活动子进程，应在同一预算锁下调用专用恢复提交，把预算、workflow 和 transaction 原子序列化为 `FAILED_COMMITTED/HARD_STOP` 并写 ledger 事件。覆盖 PREPARED 后异常、RUNNING 后 kill、过期子 PID、活动子 PID 和再次调用的真实负例。

### `M9-REC-B04`：CPU credit、状态解除和 ledger 事件不是可恢复提交

成功路径先把 `cpu_adjustments` 写入 state、清除 `hard_stopped`、把 workflow 改为 `AUDIT_PASSED`，再把 recovery transaction 写为 `SUCCESS_COMMITTED`，最后追加两个 ledger 事件。若在 state/workflow 写入后、ledger append 前崩溃，credit 已生效且普通动作可能继续，但 append-only ledger 缺失 CPU adjustment 或恢复完成事件。当前没有基于 transaction ID 的幂等补提交或一致性核对。

最小关闭条件：引入明确的 `SUCCESS_PENDING_COMMIT`，使 adjustment ID、两项事件的规范载荷和哈希先写入 recovery journal；恢复入口应能按 transaction ID 幂等检查和补写 ledger，确认 ledger 已包含精确事件后才解除 HARD_STOP 并允许普通动作。重复 ledger、缺一事件、state 已 credit 但 ledger 缺失、ledger 已写但 state 未完成的崩溃点均须有负例。

### `M9-REC-B05`：post-state 不能证明既有 dpkg 状态不变或目标版本精确

pre/post 全局状态函数生成了含 version/status 的规范文本和 SHA-256，但 transaction 丢弃 `text`，只保存 hash、count 和包名列表。成功检查仅验证 `post_names - pre_names == target_names`，无法发现既有包的 version 或 dpkg Status 被改变。

目标包检查只要求 45 项均为 `install ok installed`，没有把返回 version 与 manifest 逐项比较。现有固定归档使错误版本不太可能自然产生，但验收合同要求由 post-state 直接证明，而不是依赖推断。

最小关闭条件：transaction 保存可复核的 pre-state 规范映射或内容寻址快照；postcheck 要求所有非目标包的 version/status 与 pre 精确相等，并要求 45 个目标的 version/status 与 manifest 精确相等。记录完整 diff 和哈希，增加既有包版本漂移、既有包状态漂移、目标版本错误和额外新增包负例。

### `M9-REC-B06`：恢复父证据未绑定 pre-ledger，父快照也不保持原字节

recovery transaction 绑定了 parent transaction、pre state 和 pre workflow 的 SHA-256，但没有记录 pre-ledger SHA-256、字节数或最后事件身份。因而不能证明 credit 是从哪一个 append-only 账本前缀开始派生。

代码把解析后的父 transaction 通过 `atomic_json()` 重序列化到 `overlap_offline_recovery_parent.json`；该文件不保证与原父文件字节相同，而 recovery 中记录的是原文件 SHA-256。当前原父文件没有被覆盖，但所谓父快照自身不能用记录的摘要验证。

最小关闭条件：在锁内记录 ledger 的前置 SHA-256、bytes、行数和最后事件规范哈希；父快照应按原字节复制并验证等于 `parent_transaction_sha256`，或明确记录规范化快照的独立 SHA-256。gate 和 transaction 还应绑定原 state/workflow/ledger/parent 的共同恢复起点。增加父快照重序列化差异和 ledger 前缀替换负例。

### `M9-REC-B07`：成功恢复后没有可用的后续 gate 链

当前恢复入口使用新 recovery gate，但成功后把 workflow 恢复为 `AUDIT_PASSED`；下一步 `source_prepare` 仍进入 `command_overlap_run()`，该函数只验证旧 `overlap_work_package_audit_gate.json` 和旧冻结清单。

旧冻结清单登记的 `m9_budget.py` SHA-256 为 `b4573997...`，当前文件为 `3be0b4d6...`，已经不一致。如果更新冻结清单，旧 gate 记录的冻结清单 SHA-256 `365547aa...` 又会不一致。因此在不伪造哈希的条件下，当前成功恢复也无法进入 `source_prepare`。

最小关闭条件：明确后续 gate 迁移合同。推荐让新的 recovery gate 同时绑定原第五次 PASS、当前 recovery PASS 和更新后的完整冻结对象，并在 `recovered_from_hard_stop` 状态下由普通 overlap 动作验证该 gate；旧 gate 只保留历史证据，不再单独证明已修改的控制代码。补充恢复成功后 `source_prepare` gate 正例，以及旧 gate、旧 frozen manifest、缺 recovery report 和混合新旧哈希负例。

## 状态机、预算和授权判断

用户授权记录已足以说明允许一次性、300 秒、无网络的离线恢复，并允许把精确父 timeout 作为 append-only credit；当前问题不是缺少新的路线决策，而是实现尚未满足该授权的审计强度。原始 `cpu_seconds.overlap_build=7200.075310528` 必须继续保留，effective 仅可按

\[
\operatorname{effective}=\max(0,\operatorname{raw}-\operatorname{approved\ credit})
\]

计算。当前代码实现了该算式，但 B04 和 B06 表明其状态与账本提交尚不可恢复验证。

本轮不允许建立 PASS recovery gate。主 agent 可以按七项最小条件修复代码、合同、测试和冻结清单，并生成新的候选哈希；修复后必须由同一独立审计员定点复核，达到 `BLOCKING=0`、`NON_BLOCKING=0` 后才允许创建 gate。该 gate 只允许一次受控离线安装；不授权 M9-05、批量结构计算或任何额外 DFT 标签。

## 报告终检

本报告定稿后执行 UTF-8 控制字符扫描、活动本地 Markdown 链接检查，以及 Pandoc `markdown+tex_math_single_backslash` 到 HTML5 MathML 的 `--fail-if-warnings` 严格转换。用于验证 MathML 的恒等式为 \(45=45\)。最终 SHA-256 在交付消息中报告，以避免正文自引用改变哈希。
