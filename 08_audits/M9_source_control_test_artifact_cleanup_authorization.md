# M9 测试污染伪对象清理授权记录

本记录仅授权一次性、锁内、哈希绑定的测试污染伪对象留痕式清理：将固定 SHA-256 为 `2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74` 的测试生成 `overlap_source_control_recovery.json` 原子改名为 `.test-artifact.retired.json`，并写入清理 receipt。

为保证跨 UID 清理过程及其证据不可被并发替换，本授权同时覆盖在 `/root/deeph-m9-control/source-control-test-cleanup` 建立 root:root、`0700` 的可信目录，并在其中保存 verifier 首次完整验证所得精确 gate 字节快照和 root 私有安全迁移 journal；覆盖把 manifests 目录从 UID/GID 1000、`0755` 幂等迁移为 root:1000、`1770` sticky 终态；覆盖把伪对象、retired 对象、清理 journal、receipt、可信 gate 快照和安全迁移 journal 固定为 root:root、`0600`。所有权限迁移必须在 journal 中绑定同一 gate inode、精确字节快照、授权、独立审计 verdict、冻结清单、伪对象哈希和五项正式 runtime 哈希，并支持每个系统调用中断后的精确续提。该 sticky 终态必须继续允许 UID 1000 原子更新其本人所有的正式 runtime 文件。

清理不得删除或覆盖真实预算状态、workflow、失败事务、ledger、stale capability、source-control gate 或 parent snapshot；不得执行 source recovery、source_prepare、source_build、smoke、batch 或数据标签生成。清理命令还必须通过冻结 Python、独立结构化 PASS verdict、冻结清单和一次性 cleanup gate。
