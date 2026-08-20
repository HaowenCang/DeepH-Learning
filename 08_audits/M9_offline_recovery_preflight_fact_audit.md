# M9 离线恢复 preflight 新事实追加独立审计

## 结论

实际系统状态不支持“autoconf、automake 已安装，其他 43 包未安装”这一描述。独立核对表明：45 个 manifest 包全部未安装；`autoconf` 与 `automake` 只是 `dpkg-query -W` 在显式查询包名时返回的占位记录，version 为空且 status 为 `unknown ok not-installed`。其余 43 包没有查询记录。

因此，不允许把冻结合同改为 `43 new + 2 unchanged`。正确的最小修复是保留 `0 upgraded, 45 newly installed, 0 removed` 合同，并修正 preflight 对 dpkg status 的解释。该修复不扩展 D-017 用户授权，不改变包集合、版本、来源、预算或允许输出。

当前结论为 `BLOCKING=1`、`NON_BLOCKING=0`。修复、重哈希和独立定点复核完成前不得重试恢复安装。

## 独立事实核对

对 manifest 的全部 45 个包执行显式 `dpkg-query -W`：

- `autoconf` 返回空 version 与 `unknown ok not-installed`；
- `automake` 返回空 version 与 `unknown ok not-installed`；
- 其余 43 项由 dpkg-query 报告无匹配包；
- 命令整体返回码为 1，这是混合存在占位记录和不存在记录时的预期结果。

进一步执行 `dpkg -s autoconf automake`，两项均明确报告 package not installed and no information is available。`/var/lib/dpkg/status` 中也不存在二者的已安装 stanza。

在 root、`unshare --net`、空 sources、禁用代理、`--no-download --simulate --no-install-recommends` 条件下，独立重放冻结的 45 个本地归档，APT 输出为：

```text
0 upgraded, 45 newly installed, 0 to remove and 0 not upgraded.
Inst autoconf (2.71-2 local-deb [all])
Inst automake (1:1.16.5-1.3 local-deb [all])
Conf autoconf (2.71-2 local-deb [all])
Conf automake (1:1.16.5-1.3 local-deb [all])
```

这同时证明二者不是 unchanged baseline，并证明原 45-new solver 合同仍与实际系统一致。

## 根因

`recovery_dpkg_query()` 当前把 dpkg-query stdout 中每个三字段行都加入结果，而 preflight 采用：

```text
if pre:
    refuse already-installed target packages
```

该判断把“有查询记录”错误等同于“已安装”。dpkg 的 status 是多字段状态机；`unknown ok not-installed` 明确不是 `install ok installed`。因此本次拒绝是保守的零写入拒绝，但错误文本与分类逻辑不准确。

运行时 recovery gate 已存在，但 recovery transaction 和 recovery parent snapshot 均不存在。预算 state、workflow、原 apt transaction 和 ledger 仍保持原 HARD_STOP 证据；没有发生 dpkg unpack/configure，也没有应用 CPU credit。拒绝发生在 recovery transaction 写入之前。

## 阻塞项

### `M9-REC-PREFLIGHT-B01`：dpkg 占位记录被误判为已安装

最小关闭条件如下：

- preflight 必须逐项解析 package、version 与完整 Status，不得以 stdout 是否非空判断安装状态；
- `install ok installed` 以及其他非 `not-installed` 的部分安装、unpacked、half-configured、config-files 等状态应拒绝；
- 只有无记录或严格的 `unknown ok not-installed` 占位状态可视为未安装；占位记录的 version 必须为空；
- preflight receipt 应显式记录 45 项分类，例如 `absent=43`、`not_installed_placeholder=2`、`installed=0`、`unsafe_partial=0`，并绑定规范哈希；
- solver 合同继续要求 `0 upgraded, 45 newly installed, 0 removed` 和 45 个 `local-deb` 安装对象；不得改成 43-new；
- postcheck 继续要求 45 项逐一等于 manifest version 与 `install ok installed`，所有既有非目标包保持不变；
- 新增负例覆盖 exact installed、错误版本 installed、config-files、unpacked、half-configured、空 version 占位和完全 absent；
- 更新 `m9_budget.py`、测试、frozen manifest 与结构化 PASS verdict 的哈希，重新创建 recovery gate。旧 gate 绑定旧脚本，不能继续使用。

不建议通过删除 dpkg 的占位记录、清理 selections 或手工编辑 `/var/lib/dpkg/status` 解决；这些动作没有必要，且会引入额外系统状态变更。

## 授权与门控判断

上述修改只是修复 Debian 状态解释，不增加软件包、不改变版本、不增加网络访问，也不放宽安装后的精确状态检查，属于 D-017 内部控制修复。无需新的用户路线决策。

当前不得执行 43-new+2-unchanged，也不得绕过 preflight。主 agent 可以按上述最小条件修改控制代码和测试；新的独立审计达到 `BLOCKING=0` 后，才能用新的 verdict 和 frozen hashes 重建一次性 recovery gate并重试。

## 报告终检

本报告定稿后执行 UTF-8 控制字符扫描、活动本地 Markdown 链接检查，以及 Pandoc `markdown+tex_math_single_backslash` 到 HTML5 MathML 的 `--fail-if-warnings` 严格转换。用于验证 MathML 的恒等式为 \(45=45\)。最终 SHA-256 在交付消息中报告。
