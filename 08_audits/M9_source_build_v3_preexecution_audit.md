# M9 source_build v3 独立执行前复核

日期：2026-08-31。结论：PASS；blocking=0，non_blocking=0，均为整数。新单次permit、实际安装入口、运行态与即时预算通过，可以按下述唯一argv执行一次source_build。D-019提供人工授权，但本次通过不是编译或自测成功结论。

正式只读采集于2026-08-31T15:16:31.504748+00:00结束，进程退出0；不存在尚在运行的采集进程。本轮未调用run、installer、permit或任何编译动作，未消费capability，仅新增本报告与完整执行前证据。

## 220对象、许可及原状态

与安装后219对象证据（SHA `f47031c9909d1c66351406575b036edbc2ae6bd920253aabd060a04c9afc6534`）逐项比较，实际220对象仅新增source_build_v3_execution_permit.json；旧219对象只有manifests父目录mtime/ctime变化，其inode、owner、mode、nlink及大小不变。全部旧历史、root-only、root-private、失败事务、consumed/FAIL receipt、旧permit、恢复journal及所有snapshot均原receipt不变。

新permit为447 bytes、dev:ino=2096:167860、普通单链接、root:1000/0640。实际原始字节SHA为 `10d11a4bebc4f8d1595cfdb4bdd21d795848b643db556724ec57598a9d06c856`。六字段严格等于预期：schema=m9-source-build-execution-permit-v3，operation为`7bc4139f7a9c4b768d3f9ec68c1d1048`，nonce为`a930f2b8e7ac449bb251482012eb99d1c7032df764985aaac34519bf6db2013a`，其余三项绑定如下。

| 许可绑定 | SHA-256 |
| --- | --- |
| readiness gate | `d87228156b3a5c576658eb907f5edc0d6cf0fc89d423df6056f50a71f12f7329` |
| 安装独立报告 | `bd84bbca67c2b0d1cae5865d7369462f2c94d75d659f85f895761997f317f181` |
| 安装独立verdict | `60b22f6a0a8ba2f756d4829aa461f6d0ffdcf79d681c4d15c22a5c3671abc755` |

安装verdict严格七字段PASS/0/0，并绑定新19文件manifest `01a2a8f438d27d582abcf4536775b54605051a3458b06f2bc29c2c56222d4e58`。snapshot manifest仍为 `a2eea49fdf6853ccb76233c7bd14b1d08407046daf54d4b625c013f549cf000a`；全部来源及旧9/12/10/25/16闭集重验通过。permit.tmp、gate.tmp和snapshot staging缺席。

四份runtime原字节与安装基线完全一致。state为2291 bytes/SHA `3523f0d17ccc2168289c5992db691441dd68eb3f09dde3e73de12a4a2ec80560`；workflow为905 bytes/SHA `4438c7fce6b5d94268b12d9f2c17876bf6b4f100c22c4610ba215b3c6d1862fa`；失败transaction为2345 bytes/SHA `2920d80e431992cc8a23abe409d2d513b7a567e44651382d09a82b8af085161d`；完整ledger为66755 bytes/SHA `8dfbb2bb9f23ac9066b457553c2bccfa94a2ab7dde5d66f6315595caaa793421`，没有新增事件。

state/workflow非hard-stop、活动事务为空，workflow=SOURCES_PREPARED，MPI恢复标记保持；旧失败事务仍为38a891fff6fd07675581b891766e02c6的FAILED_COMMITTED。准备树与退休树各5319 receipts，完整前后字典相等，canonical SHA分别保持 `7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260`、`060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`。编译prefix、日志、产物manifest及材料运行目录仍缺席。

## 实际UID1000与预算

使用真实UID1000、固定Python3.9.23 -I -S -B执行正式source-build-v3目录中的consumer verify-execution，退出0、stderr为空、status=PASS、source_build_executed=false，runtime SHA为 `354888ae6331993a9b28952a146006a3d96e61788965518f79f57b9f11392263`。

另以相同真实UID与解释器从正式snapshot加载实际launcher并仅调用installed_authority，退出0、stderr为空。返回的新consumer/launcher、gate、permit、snapshot及原/派生driver哈希全部准确，其中派生driver为 `5652ee35a3595f42bd3050e5825419175fc84526a421a0500559d4146f253d00`。没有调用launcher.main、wait_and_consume_capability、dispatch或构建函数。

每条命令后重新持原budget.lock比较220完整字典、四份runtime原字节、permit原字节及两树，全等。正式namespace canonical SHA为 `99b4d9f3750e4abace89ca35cde0dc4640181a8355b8fa18bdbf5c8b2867555f`。M9控制器/脚本/测试及正式controls缓存扫描为0。

原预算函数对4294967296 bytes预测返回violations=[]；原始CPU build为7214.469142588001秒，原抵扣7200.075310528秒，有效14.393832060000932秒，余额7185.606167939999秒。CPU smoke/batch为0；GPU compatibility=54.84820560599999秒，training/physical_validation为0，全部预算及历史抵扣保持原值。采集时总apparent/allocated为31134643310/31460294656 bytes，overlap增量1265163579/1290473472 bytes，VHDX为28131196928 bytes。实际run仍应使用原控制器再次即时核验，不以本报告读数替代。

## 唯一命令与封存证据

仅由主端以WSL真实evan-williams执行以下完整argv一次，不附加cwd/log、缩写参数、自由命令或其他动作：

```bash
/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B \
  /home/evan-williams/deeph-m9/controls/source-build-v3/m9_source_build_v3_consumer.py \
  run --build-operation-id 7bc4139f7a9c4b768d3f9ec68c1d1048 \
  --bucket none --cpu-bucket overlap_build --forecast-bytes 4294967296 \
  --overlap-operation --overlap-action source_build \
  --config /mnt/e/Projects/Codex/DeepH/06_reproduction/configs/m9_overlap_only_contract.json
```

上述argv数组的规范JSON SHA为 `54afa7e90d59b43105291fed35e781db6f10a54a383f449bc8a7481686034ede`。一次执行后无论成功或失败均保存现场并交独立事实审计；失败不得直接重放旧permit/capability。后续恢复和重试仍须适用的版本化门控，D-019不取消这些条件，也不在此放行材料计算、smoke/batch、GPU或训练。

M9_source_build_v3_preexecution_evidence.json保存全部220 receipts、父目录变化、permit原字节、四份完整runtime Base64（含全部66755字节ledger）、两条真实命令及stdout/stderr/rc、预算和唯一argv。文件223614 bytes，SHA `822e0fc61599db3b1b1135b2e384050ca373f0c4c08aea84bee70d7a3cee3b43`；落盘后重算canonical和所有raw哈希通过，纳秒整数未损失，可用于执行后前缀及逐项比较。本报告Pandoc严格Markdown及git diff --check通过；两份文件封存后不回写。
