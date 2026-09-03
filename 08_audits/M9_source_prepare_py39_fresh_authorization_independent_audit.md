# M9 Python 3.9 单次 source_prepare 授权签发与执行前独立审计

审计日期：2026-08-30  
operation id：`f9824f0eb63e41f19699c1114b13537e`  
审计范围：实际 root authorization、签发唯一写集合、原 runtime/历史不变性、真实 UID1000 授权 verifier 及完整 argv  
结论：**PASS / BLOCKING=0 / NON_BLOCKING=0**

## 执行前结论

用户已明确授权一次 `source_prepare`。主 agent 签发的实际 authorization 与已审查 payload、用户授权记录及当前 readiness/runtime 全部一致，独立只读验收通过。主 agent 可以使用下方唯一完整参数执行一次源码准备；该许可不包含下载、source build、smoke、batch、GPU、训练、Hamiltonian、SCF 或其他 DFT 标签生成。执行返回后应停止并进行新的独立事实审计；失败、超时或拒绝不允许自动重试。

本报告记录授权签发与执行前验证，不声称源码准备已成功，也不替代执行后的预算、事务及实际产物审计。审计 agent 没有运行 issuer、adapter `main()` 或任何 source 动作，只读取正式对象并新增本报告。

## 已固化的来源

用户授权记录为 `08_audits/M9_source_prepare_py39_fresh_user_authorization.md`，SHA-256 `258212b82ccf0fc6bcd23ce93486f692d2e092d11e502f8b09926f0575bbf368`。该记录明确将用户“授权”绑定到前一条一次性、仅本地源码准备的请求，且保留原预算与失败停机规则。

机械签发脚本为 `06_reproduction/controllers/m9_source_prepare_py39_issue_authorization.py`，签发前独立只读审查和 SHA 重算通过，SHA-256 为 `b649d015d428e66ffa0ae86b182a569113912ca58b40078df445e2c6c654ad17`。本地 payload 为 `06_reproduction/manifests/m9_source_prepare_py39_fresh_authorization_payload.json`，SHA-256 为 `62bf44207a3f3338fce3f8b4476a0b37be97f7587d2f07148aa3978b9014b4ab`。本轮不改变原 25-file consumer 冻结闭集或 16-file overlap 冻结输入。

前置安装执行事实报告 `M9_py39_consumer_gate_completion_execution_independent_audit.md` 保持 SHA-256 `798ada7ed0c8835cc56b28d168188d61688e21d2ecdfacfb4d56ac6da660bcdc`。

## 签发前完整基线与正式差异

独立审计在签发前保存了 `08_audits/M9_source_prepare_py39_fresh_preexecution_baseline.json`，SHA-256 为 `bac5fa6f486d2e77cde4fe83703fc1745880ae15c3c915e04ee833ad506766ac`。该文件包含126项正式对象完整 receipt，以及 state、workflow、ledger、overlap transaction、consumer gate、recovery failure snapshot、recovery transaction 七项原始字节的 Base64。其中 ledger 为61826 bytes，可供后续检查精确前缀和新增事件。

基线已从实际落盘文件重新读取，逐项复核其 receipt、Base64 长度和 SHA，并确认与签发前正式 WSL 对象全等。采集范围为 manifests、controls、root-private control 三个正式树，包含无跟随路径、类型、dev/ino、安全 metadata、大小、mtime/ctime、文件 SHA 或 symlink target；atime 不在零写比较口径内。

签发后独立采集127项清单，与上述已落盘126项基线逐字段比较，差异严格限于新授权文件和 manifests 父目录 mtime/ctime。其余文件、目录、inode、权限、字节、大小及时间均相等。父目录保持 `2096:50688`、`0:1000/01770`、nlink=3、4096 bytes；mtime_ns/ctime_ns 从 `1788060325545677975` 变为 `1788061384061895962`。没有其他正式路径变化，授权 `.json.tmp` 缺席。

签发后127项清单的紧凑、排序 JSON SHA-256 为 `16e447bb25303d2f6490396800fb719ed154bbaa68e08e995099ae2d0e4e9d7f`。真实 UID1000 verifier 执行前后该完整清单逐项相等。七项原始字节也与基线 Base64 全等，ledger 没有新增事件。

## 实际授权对象与绑定

固定路径：`/home/evan-williams/deeph-m9/manifests/overlap_source_prepare_py39_single_run_authorization.json`。

实际对象为885-byte普通单链接文件，owner/group=`0:1000`，mode=`0640`，device/inode=`2096:154203`，SHA-256=`62bf44207a3f3338fce3f8b4476a0b37be97f7587d2f07148aa3978b9014b4ab`。mtime_ns=`1788061384058114805`，ctime_ns=`1788061384061895962`。实际字节与已冻结本地 payload 逐字节相等，JSON与基线保存的12字段对象全等。

schema 为 `m9-source-prepare-py39-single-run-authorization-v1`，decision 为 `D-018-PY39-CONSUMER-REPLACEMENT`，status 为 `AUTHORIZED`，scope 为 `ALLOW_EXACTLY_ONE_SOURCE_PREPARE`，action 为 `source_prepare`。operation id 为 `f9824f0eb63e41f19699c1114b13537e`；nonce 为 `2c1c2cd40cdd5d0823fb7ad7f6ac5d6f9d39d4fa762f9d7588a5e1ebe92f1c33`。严格字段闭集、32/64位小写十六进制身份、固定授权记录路径及记录 SHA 均通过。

实际绑定值为：

```text
consumer_gate_sha256 520a8cffcab9c91400647e486de796853d8a00073892e3a4b0472cafbf9dd5c9
active_overlap_gate_sha256 229f0846c3d22917ccb955729a577168880bca6a53ad07f32502b0ae4a4e27ab
runtime_sha256 24a952d229fb39fa0c0198b0361e5f02955cbff74182af97a7dfb24da9075db4
```

root 侧独立只读复核了 trusted bootstrap、snapshot、历史闭集、recovery core 及 `SUCCESS_COMMITTED` refresh；它们与基线中的历史、core、refresh 和 runtime 对象全等。此次授权签发没有重置预算、消费旧 capability 或改变失败/恢复记录。

## 真实 UID1000 授权验收与唯一 argv

独立审计通过 `/usr/sbin/runuser -u evan-williams` 启动冻结 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B`，实测 UID/GID 为1000、Python版本为3.9.23。从 root-owned v2 snapshot 载入实际 adapter 和原预算控制器，在以 `O_NOFOLLOW` 打开的原 budget lock `2096:50700` 同一 FD 排他锁内，使用以下完整参数调用只读 `verify_source_prepare_authorization()`：

```bash
/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B \
  /home/evan-williams/deeph-m9/controls/uid1000-consumer-py39-v2/m9_budget_uid1000_consumer.py \
  run --consumer-operation-id f9824f0eb63e41f19699c1114b13537e \
  --bucket none --cpu-bucket overlap_build --forecast-bytes 1073741824 \
  --overlap-operation --overlap-action source_prepare \
  --config /mnt/e/Projects/Codex/DeepH/06_reproduction/configs/m9_overlap_only_contract.json
```

实际 verifier 返回 `uid1000_source_prepare_authorization_verified`，退出码0、stderr为空。原生 parser 的自由 argv 为 `[]`，`validate_overlap_request()` 返回 `source_prepare / overlap_build / 1073741824`。runtime 验证前后全等；`main_called=false`、`source_prepare_executed=false`。`--overlap-operation` 仅为布尔开关，operation id 只经专用 `--consumer-operation-id` 传入，不能作为原生布尔开关的值。

签发前真实 UID1000 的纯只读预算检查 `violations(state, 1073741824)` 返回空列表；有效 overlap_build 用量为 `6.594115618000615` 秒，剩余 `7193.405884381999` 秒，原始历史计量及既有抵扣未变。签发前测得 combined apparent/allocated 分别为 `30510202276/30823309312` bytes，overlap 增量分别为 `640722545/653488128` bytes，VHDX overlap 增量为 `1207959552` bytes；加1 GiB预测未触发既有上限。这些数值是只读快照，不能替代正式入口的即时预算检查。

## 一次性与执行后审计要求

authorization 文件本身不会被 adapter 删除或 rename；一次性限制来自其与当前 runtime 的严格绑定、原 budget lock、首次状态写入前再验证及预算事务/子进程 capability。正式调用导致状态改变后，保留的授权对象属于历史证据，不表示仍可再次消费。授权 operation id 与预算控制器另行生成的 transaction id 也不应假定相等。

正式入口的预算预检失败可能提交硬停状态，即使子进程尚未执行；任何拒绝或失败均不能通过再次调用来试探恢复。执行后应使用本报告和完整基线，独立核验唯一新事务、ledger 原字节前缀与新增计量、状态转换、实际准备树及来源清单、已消费 capability、launcher receipt，并确认未发生编译、下载或结构计算。

严格 Markdown、`git diff --check` 和 M9缓存零新增检查通过。本次 `PASS/0/0` 仅允许落实用户已经给出的这一次 `source_prepare` 授权；不预先判定执行结果，不放行任何后续动作。
