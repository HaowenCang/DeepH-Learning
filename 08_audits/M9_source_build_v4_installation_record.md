# M9 source_build v4 主端安装记录

日期：2026-09-01。记录角色：主 agent。本文记录调用与返回值，不替代独立安装事实审计，也不构成 execution permit。

## 输入权威

独立实施审计结论为 `PASS / BLOCKING=0 / NON_BLOCKING=0`：

| 对象 | SHA-256 |
| --- | --- |
| frozen manifest | `5862155306e595f268e996a9712194faabd2347e94b73a0118ebb403c763cf09` |
| implementation report | `4309fde795eadfae3878db9563223ec8b40b2dbd40290e89734e640ced947795` |
| implementation verdict | `a1878a1121ff361e8aba3571d405e032d6d97ddb32ab51d04ee0ba803fcd2d78` |
| installer | `ed775d8e3f492e80b323ca75fb23be1f22a499accf9fd0eab6a8021327e4a4e5` |
| consumer | `0466cb4d1ff5ef1f7b0fc4b20c45e9d249110a7ee36a2bde8f419c76968219ad` |

主端完整读回报告与严格七字段 verdict，并重算上述哈希。verdict 精确绑定 frozen SHA、报告路径和报告 SHA，问题数为整数 0。

root 启动采用既有已审核 single-FD loader。来源工作包 SHA 为 `dc1d0d992f7e1328f79a4436eb4535b79ba2ab48fcee1b44fa498c31c30e91a2`；提取 Python 块并规范 CRLF 后 loader SHA 为 `c68e43b5de4fdadb44254fbfdd543f5ba2a29b6e41994021c55a3287b5f7491f`。每次调用前均在内存中重算并要求该 SHA 全等。

## 实际调用与返回

固定解释器为 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B`，WSL 用户为 root。loader 后参数依次为：

```text
/mnt/e/Projects/Codex/DeepH/06_reproduction/controllers/m9_source_build_v4_install.py
ed775d8e3f492e80b323ca75fb23be1f22a499accf9fd0eab6a8021327e4a4e5
ACTION
0466cb4d1ff5ef1f7b0fc4b20c45e9d249110a7ee36a2bde8f419c76968219ad
5862155306e595f268e996a9712194faabd2347e94b73a0118ebb403c763cf09
a1878a1121ff361e8aba3571d405e032d6d97ddb32ab51d04ee0ba803fcd2d78
4309fde795eadfae3878db9563223ec8b40b2dbd40290e89734e640ced947795
```

`ACTION=preflight` 恰调用一次，退出码 0，返回：

```json
{"gate_sha256":"dcd0a0ed3307add49df5b7586ba0bf01b2fc55b0469a42067893e563ba2ff3c1","snapshot_sha256":"210d00c6f1d145adbc71c362261e2607faa8066a58c6f4f1d63aa423c8e9b0c7","status":"preflight_pass","writes":0}
```

`ACTION=install` 随后恰调用一次，退出码 0，返回：

```json
{"status":"build_snapshot_and_readiness_installed","gate_sha256":"dcd0a0ed3307add49df5b7586ba0bf01b2fc55b0469a42067893e563ba2ff3c1","snapshot_sha256":"210d00c6f1d145adbc71c362261e2607faa8066a58c6f4f1d63aa423c8e9b0c7","execution_permit_present":false}
```

实际 gate 与 snapshot manifest SHA 均与零写预测全等。安装器在返回前已经从 root-owned snapshot 重新执行自身 `verify_gate(require_permit=False)` 和完整父态检查；该内部自检不替代独立安装事实审计。

## 机械安装时点的门控边界

机械安装时只创建 v4 snapshot 和 readiness gate，没有创建 permit，没有调用 v4 consumer main、launcher、预算 `run` 或 source_build，也没有开始 HDF5/OpenMX 构建、材料结构计算或训练。其后必须由独立 agent 核验实际 273 对象、snapshot/gate 闭集与权限、真实 UID1000 `verify-ready`、缺 permit 精确负例、244 对象历史保持、两棵源码树和即时预算。只有独立安装事实审计为 `PASS/0/0` 后，主端才可执行一次 permit 动作。

## 独立安装 PASS 后的 permit 签发

[独立安装事实审计](M9_source_build_v4_installation_audit.md) 随后封存为 `PASS/BLOCKING=0/NON_BLOCKING=0`，报告 SHA `8dde4b7594598c8f58381b6e675200b3587da7be0d97c3898418f701e846c8dc`，严格安装 verdict SHA `fae99d0d4cda77565f1bbccfe9d04630ff60be3b7026d4c82649a72880dc4b56`，完整 273 对象证据 SHA `aadf3801eaf50a0861bd330bb9f865758047d08749348e79d399c2f59cf7d3d3`。主端完整读回三份文件并重算哈希，verdict 精确绑定 frozen SHA、报告路径和报告 SHA。

主端随后使用同一固定解释器、同一已审核 loader 与同一实施权威，执行一次 `ACTION=permit`，末尾追加上述安装 verdict SHA 与安装报告 SHA。调用退出码 0，返回：

```json
{"status":"build_execution_permit_installed","permit_sha256":"c3aae6ff0c5aaffb3d5a711b48e7dc505061959eb144509995f8e9890f5853d4","source_build_executed":false}
```

未重放 preflight 或 install，未调用 consumer `run`、launcher 或 source_build。permit 签发成功仍不是执行前门控通过；当前必须独立复核实际 274 对象、permit 绑定、真实 UID1000 `verify-execution`、当前 runtime/两树、即时预算与唯一 argv，结论为 `PASS/0/0` 后才可执行一次冻结构建命令。
