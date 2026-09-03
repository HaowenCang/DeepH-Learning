# M9 source_build v3 独立安装事实审计

日期：2026-08-31。结论：PASS；blocking=0，non_blocking=0，均为整数。实际安装及缺permit的拒绝行为通过验收；本结论不表示已签发执行许可或已完成编译。

正式只读采集于2026-08-31T15:06:11.162370+00:00结束。本轮未调用installer、preflight、permit、consumer run或构建；仅新增本报告、安装verdict及完整安装后证据，不修改既有封存来源和报告。主端执行记录未被用作安装成功的自证。

## 实际闭集、身份与绑定

以MPI恢复后的193对象证据（SHA `177390748086e678d22c3f24531c5a9b326889e5acb7f3931275262cf27b2ed2`）为基线，实际219对象恰新增26项：source-build-v3目录、24个snapshot文件及readiness gate。无删除、未知新增或其他旧成员变化。controls父目录原inode/权限保持，nlink由9增至10；manifests父目录nlink仍为3，两者仅另有mtime/ctime变化，大小均仍4096 bytes。

snapshot固定为 `/home/evan-williams/deeph-m9/controls/source-build-v3`，dev:ino=2096:162442，root:1000/0550、nlink2；24文件全部普通单链接、root:1000/0440。逐项读取实际字节并核对大小、SHA与manifest，精确覆盖19冻结来源、新frozen、实施report/verdict、派生budget及snapshot_manifest。实施报告/verdict保持原哈希，新19文件及递归旧9/12/10/25/16闭集再次逐字通过。

| 安装对象 | SHA-256 |
| --- | --- |
| 新frozen manifest | `01a2a8f438d27d582abcf4536775b54605051a3458b06f2bc29c2c56222d4e58` |
| snapshot_manifest | `a2eea49fdf6853ccb76233c7bd14b1d08407046daf54d4b625c013f549cf000a` |
| 实际readiness gate | `d87228156b3a5c576658eb907f5edc0d6cf0fc89d423df6056f50a71f12f7329` |
| 实施报告 | `0b306f893d87aae84fae4c1d87bf0fb6d0875a32054918092e00ca64e39c87e4` |
| 实施verdict | `ef362e2b58385e84d833f389fc38d701651238af131a69929edc16862e9d908d` |

gate为3259 bytes、dev:ino=2096:167910、root:1000/0640、nlink1。schema/scope/action、operation `7bc4139f7a9c4b768d3f9ec68c1d1048`、nonce、持续授权、独立实施权威、snapshot、新frozen及执行前runtime绑定均核验通过。历史attestation SHA为 `ed64beb94a892e5a65789894b64ae5670879b7a3ed5f32200c05d76a3ff260e0`。新permit、permit.tmp、gate.tmp及snapshot staging全部缺席。

## 历史、预算与两树

root逐字读取全部正式历史，包括/root private和固定8项root-only，旧receipt完整匹配。失败事务38a891fff6fd07675581b891766e02c6、已消费capability、FAIL receipt、旧v2 permit/gate、所有旧snapshot及MPI恢复journal均原inode、权限及字节不变。四份runtime与基线保存的原始字节逐字相等；ledger没有新增事件。

| 正式runtime | bytes | SHA-256 |
| --- | --- | --- |
| state | 2291 | `3523f0d17ccc2168289c5992db691441dd68eb3f09dde3e73de12a4a2ec80560` |
| workflow | 905 | `4438c7fce6b5d94268b12d9f2c17876bf6b4f100c22c4610ba215b3c6d1862fa` |
| 失败transaction | 2345 | `2920d80e431992cc8a23abe409d2d513b7a567e44651382d09a82b8af085161d` |
| 完整ledger | 66755 | `8dfbb2bb9f23ac9066b457553c2bccfa94a2ab7dde5d66f6315595caaa793421` |

state/workflow非hard-stop、活动事务为空，workflow=SOURCES_PREPARED；失败事务仍为FAILED_COMMITTED，恢复标记保留。CPU原始7214.469142588001秒、抵扣7200.075310528秒、有效14.393832060000932秒、余额7185.606167939999秒。GPU compatibility=54.84820560599999秒，training/physical_validation及CPU smoke/batch仍为0。原预算对4GiB预测返回violations=[]，未改变用量、credits或上限。

采集时总apparent/allocated为31134399759/31460036608 bytes，overlap增量1264920028/1290215424 bytes，VHDX为28097642496 bytes；后续执行前仍需即时核验。准备树、退休树各5319项，完整前后字典相等，canonical SHA分别为 `7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260`、`060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`。HDF5 prefix、编译日志、构建manifest及材料运行目录仍缺席。

## 真实UID1000固定入口

通过runuser真实UID1000、固定Python3.9.23 -I -S -B，从正式source-build-v3路径执行以下预定只读检查；未使用项目副本或临时路径替代安装入口。

| 实际入口和参数 | 结果 |
| --- | --- |
| m9_source_build_v3_consumer.py verify-ready | rc0，status=PASS，source_build_executed=false，stderr为空 |
| m9_source_build_v3_consumer.py verify-execution | rc1，stdout为空，精确FileNotFoundError指向新permit |
| m9_source_build_v3_launcher.py --capability-id 00000000000000000000000000000000 | rc1，stdout为空，installed_authority调用execution_binding时精确FileNotFoundError指向新permit |

两项拒绝的最后错误行均为缺少 `/home/evan-williams/deeph-m9/manifests/source_build_v3_execution_permit.json`，不是其他权限或来源错误。launcher在等待/消费capability之前已拒绝，没有产生BOUND、CONSUMED或launcher receipt。verify-ready返回runtime SHA `354888ae6331993a9b28952a146006a3d96e61788965518f79f57b9f11392263`。

每条命令后重新持原budget.lock比较完整219字典、四份runtime原字节及两树，均与命令前全等。正式namespace canonical SHA为 `b882a0671373483cbf6e4719c7e4aa609b5abc4c1ba7b82df697e9617f97f573`。固定8项旧权限未放宽，M9控制器/脚本/测试及正式controls缓存扫描为0。

## 保存的证据及放行边界

M9_source_build_v3_installation_postexecution_evidence.json保存全部219项完整receipt、26项新增和两个父目录前后receipt、四份runtime原始Base64字节（含完整ledger）、gate和snapshot manifest、预算、两树核验及三条真实命令的完整argv/stdout/stderr/rc。文件233768 bytes，SHA `f47031c9909d1c66351406575b036edbc2ae6bd920253aabd060a04c9afc6534`；落盘后重新计算namespace canonical与所有raw哈希通过，纳秒整数未损失。本报告Pandoc严格Markdown和git diff --check通过。

该安装事实PASS足以进入工作包规定的新单次permit签发流程，但当前permit仍缺席，不能执行source_build。签发后须独立复核实际permit、运行态、即时预算和唯一argv，再按门控执行一次。D-019持续人工授权不替代这些技术条件，不允许复用旧token；本PASS不构成编译、自测、材料结构、GPU或训练结果。报告、verdict与证据封存后不回写。
