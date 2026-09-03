# M9 Python 3.9 consumer gate completion 实施记录

日期：2026-08-30  
实施角色：主 agent；本文件不是独立执行事实审计  
状态：`COMPLETED_PENDING_INDEPENDENT_FACT_AUDIT`

## 执行依据与边界

独立定点复核已关闭 `M9-PY39-COMP-B01`，结论为 `PASS/BLOCKING=0/NON_BLOCKING=0`。使用最终报告与 verdict 哈希的 single-FD `preflight` 已由独立审计员执行，125 个正式三树对象前后逐项相等，consumer gate 与 authorization 均缺席。主 agent 随后仅执行一次 action=`complete`，未重跑旧 installer 的顶层入口，未创建单次 authorization，未调用 `source_prepare`、build、smoke、batch、GPU 或 DFT。

## 固定执行身份

入口为 WSL `Ubuntu-22.04` 的 root，解释器为 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9`，选项为 `-I -S -B`。loader 原文从 `M9_source_prepare_py39_consumer_replacement_work_package.md` 唯一 Python 代码块提取；先验证该工作包 SHA-256 为 `dc1d0d992f7e1328f79a4436eb4535b79ba2ab48fcee1b44fa498c31c30e91a2`，再验证 loader UTF-8 源 SHA-256 为 `c68e43b5de4fdadb44254fbfdd543f5ba2a29b6e41994021c55a3287b5f7491f`。loader 使用单一 no-follow FD 读取、校验并执行同一 controller 字节。

loader 后续参数按顺序为：

```text
/mnt/e/Projects/Codex/DeepH/06_reproduction/controllers/m9_py39_consumer_gate_completion.py
c2c235c444bae0f613078a060efa9733f869533385fa84268bfd2cc2b3c3ef55
complete
4ff45c308cc1f7b5dc9579d9617697ae6bc2e3fa9df65626a1f6967741b3ab84
48ddb4b760348e1a7f07572a8873b8e13df17983a9d338dfad5e909c6936eb7e
53ef0b0e1923b571b275affb91cdc944c6d363d3ae3a85b60997b2dd67bf830f
843122abdb878b40abd7da09b3689ee3e77e11271fe348b637519aeec3a6a400
05ae6f542c6c9ea22d38d4899298a3ccf16f4ed4c8763309737fedb22a34331a
```

## 实际返回

进程退出码为 `0`，状态为 `consumer_gate_completed`。返回 receipt：

```json
{
  "path": "/home/evan-williams/deeph-m9/manifests/overlap_source_prepare_py39_uid1000_consumer_gate.json",
  "bytes": 5535,
  "sha256": "520a8cffcab9c91400647e486de796853d8a00073892e3a4b0472cafbf9dd5c9",
  "uid": 0,
  "gid": 1000,
  "mode": 416,
  "nlink": 1
}
```

该 SHA 与独立 preflight 的确定性 gate SHA 完全一致。控制器已完成终态预检、历史闭集与 authorization 缺席复核，以及三树写集合检查。最终是否安装合格仍须独立审计员验证实际文件、完整历史/预算不变性和真实 UID1000 verifier；本实施成功不替代该结论。

## 下一门控

独立安装事实审计通过后，才请求新的单次 `source_prepare` 用户授权。CPU、GPU、存储预算及全部历史用量、失败事务、恢复事务和审计证据保持原约束；无总墙钟期限不改变这些条件。主计划、进度台账和决策记录的既有冻结字节尚未修改，避免使受审安装入口失去其来源绑定。
