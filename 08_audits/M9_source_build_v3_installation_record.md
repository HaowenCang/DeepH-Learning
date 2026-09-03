# M9 source_build v3 主端安装记录

日期：2026-08-31。主agent执行记录，不替代独立安装事实审计。安装及执行前独立审计现已通过，编译permit已签发一次；随后唯一编译命令已启动，见[主执行记录](M9_source_build_v3_execution_record.md)。以下安装时点的等待表述保留其历史含义。

## 前置权威

D-019持续授权有效。[独立实施审计](M9_source_build_v3_implementation_audit.md) 已封存为PASS/BLOCKING=0/NON_BLOCKING=0，早检B01独立关闭。主端完整读回报告与严格七字段verdict，核验SHA后才执行。

| 对象 | SHA-256 |
| --- | --- |
| v3 frozen manifest | `01a2a8f438d27d582abcf4536775b54605051a3458b06f2bc29c2c56222d4e58` |
| installer | `98ad46b52931c658f5627912cd724932a4ace009cede006de15b4d96d61104e9` |
| consumer | `0e81f6748bfaf26edb752293b781a0992fe7e657b54ac74856fc4e0f28c06a17` |
| 实施报告 | `0b306f893d87aae84fae4c1d87bf0fb6d0875a32054918092e00ca64e39c87e4` |
| 实施verdict | `ef362e2b58385e84d833f389fc38d701651238af131a69929edc16862e9d908d` |

root启动采用旧替代consumer工作包中的唯一single-FD Python loader。先核验旧工作包SHA `dc1d0d992f7e1328f79a4436eb4535b79ba2ab48fcee1b44fa498c31c30e91a2`；提取块、规范CRLF后精确loader SHA `c68e43b5de4fdadb44254fbfdd543f5ba2a29b6e41994021c55a3287b5f7491f`。调用时再次核验loader字节，不从未验证源码启动。

## 实际调用

使用WSL Ubuntu-22.04 root和固定`/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B -c`。loader后的固定参数如下，ACTION依次为preflight和install，各调用一次：

```text
/mnt/e/Projects/Codex/DeepH/06_reproduction/controllers/m9_source_build_v3_install.py
98ad46b52931c658f5627912cd724932a4ace009cede006de15b4d96d61104e9
ACTION
0e81f6748bfaf26edb752293b781a0992fe7e657b54ac74856fc4e0f28c06a17
01a2a8f438d27d582abcf4536775b54605051a3458b06f2bc29c2c56222d4e58
ef362e2b58385e84d833f389fc38d701651238af131a69929edc16862e9d908d
0b306f893d87aae84fae4c1d87bf0fb6d0875a32054918092e00ca64e39c87e4
```

preflight宿主会话1439，轮询原会话后退出0；返回preflight_pass、writes=0、M9_NATIVE_EXIT=0。随后install宿主会话77825，轮询原会话后退出0；返回build_snapshot_and_readiness_installed、execution_permit_present=false、M9_NATIVE_EXIT=0。均未重启或重放动作。

两次输出的gate SHA均为 `d87228156b3a5c576658eb907f5edc0d6cf0fc89d423df6056f50a71f12f7329`，snapshot manifest SHA均为 `a2eea49fdf6853ccb76233c7bd14b1d08407046daf54d4b625c013f549cf000a`。安装器报告与预测一致，但不能以此替代实际UID1000独立验收。

## 后续门控与证据边界

已交独立审计员核验219对象安装后闭集、24文件snapshot及权限、四份runtime原字节、失败事务/旧permit/root-only历史、两棵源码树和真实UID1000入口。verify-ready应通过；verify-execution与新launcher在缺permit条件下应按预定负例拒绝且零写。完整证据与独立安装报告另行封存。

只有独立安装事实PASS后，才依据D-019签发新的单次编译permit；执行前仍由独立agent复核实际许可和实际入口。没有重置或增加CPU/GPU/存储预算，没有重放旧v2许可，没有运行source_build、HDF5自测、材料结构或训练。安装记录形成时尚待独立结论，后续事实如下；M9-DATA-B01继续OPEN。

## 独立安装结论与实际permit签发

[独立安装事实报告](M9_source_build_v3_installation_audit.md) 已封存为PASS/BLOCKING=0/NON_BLOCKING=0，报告SHA `bd84bbca67c2b0d1cae5865d7369462f2c94d75d659f85f895761997f317f181`，严格七字段verdict SHA `60b22f6a0a8ba2f756d4829aa461f6d0ffdcf79d681c4d15c22a5c3671abc755`，完整证据SHA `f47031c9909d1c66351406575b036edbc2ae6bd920253aabd060a04c9afc6534`。实际219对象、24文件快照、历史字节和真实UID1000入口均已独立核验；缺permit负例精确拒绝且前后零写。

主端完整读回报告/verdict并核验三份封存文件哈希后，使用同一已审核loader执行一次permit动作；前述固定参数中的ACTION改为permit，末尾依次追加安装verdict SHA和报告SHA。宿主会话97351，轮询原会话结束为0，返回build_execution_permit_installed、source_build_executed=false及M9_NATIVE_EXIT=0。安装器返回许可SHA `10d11a4bebc4f8d1595cfdb4bdd21d795848b643db556724ec57598a9d06c856`。没有重放preflight/install。

permit签发成功不等于允许省略执行前门控。现已交同一独立审计员复核实际220对象、许可绑定、真实UID1000固定入口、原运行态/两树和即时预算；通过后才启动唯一冻结source_build命令。
