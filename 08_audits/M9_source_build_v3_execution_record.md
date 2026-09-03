# M9 source_build v3 主端执行记录

日期：2026-08-31至2026-09-01。主端执行记录，不替代独立执行事实审计。唯一编译命令提交至宿主会话61603，随后因宿主整机关机而外部中断；不宣称编译通过，也不把非终态运行态误记为控制器已提交失败。

## 执行前权威

D-019持续授权有效，v3独立实施、安装事实及执行前复核均已封存PASS/BLOCKING=0/NON_BLOCKING=0。主端完整读回最新[执行前独立报告](M9_source_build_v3_preexecution_audit.md)，核验报告SHA `812294edd8c5f750b578109a693982e8a620a5bee9500dd58a2948d8991ede58` 及完整220对象证据SHA `822e0fc61599db3b1b1135b2e384050ca373f0c4c08aea84bee70d7a3cee3b43`。独立审计员确认采集会话35575已结束且无其他采集进程，主端才提交正式动作。

实际permit SHA `10d11a4bebc4f8d1595cfdb4bdd21d795848b643db556724ec57598a9d06c856`；operation为`7bc4139f7a9c4b768d3f9ec68c1d1048`。执行前CPU build有效用量14.393832060000932秒、余额7185.606167939999秒；全部历史原始计数及既有抵扣保持，4GiB预测检查通过。这些历史读数不替代原控制器执行时即时检查。

## 唯一实际命令

WSL Ubuntu-22.04，真实用户evan-williams。冻结Linux argv如下，主端仅提交一次：

```bash
/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B \
  /home/evan-williams/deeph-m9/controls/source-build-v3/m9_source_build_v3_consumer.py \
  run --build-operation-id 7bc4139f7a9c4b768d3f9ec68c1d1048 \
  --bucket none --cpu-bucket overlap_build --forecast-bytes 4294967296 \
  --overlap-operation --overlap-action source_build \
  --config /mnt/e/Projects/Codex/DeepH/06_reproduction/configs/m9_overlap_only_contract.json
```

完整argv规范JSON SHA `54afa7e90d59b43105291fed35e781db6f10a54a383f449bc8a7481686034ede`。未附加log/cwd参数或自由命令。宿主会话61603首次返回运行中；初次只读观察到正式consumer PID294，尚无终态。后续只轮询原会话，不因工具等待超时重新启动。

范围仅为冻结source_build：HDF5配置、构建、自测与安装，官方OpenMX构建及来源校验，限定两文件overlap补丁、重构建、库来源和产物清单。没有授权扩大到Hamiltonian、SCF或其他DFT标签；smoke、batch及训练仍依赖各自门控。

## 终态与后续

原会话在对话中断后不可恢复；`write_stdin`报告Unknown process id。只读进程检查显示WSL已重新启动，原consumer PID294与launcher PID396均不存在。Windows System事件1074明确记录2026-08-31 23:23:35+08:00由`C:\WINDOWS\Explorer.EXE`代表当前用户发起“关闭电源”；EventLog 6006为23:24:35，Kernel-General 13为23:24:41.986，下一次系统启动为2026-09-01 14:02:44.500。没有证据支持WSL自身崩溃或预算超时。

正式日志仅有hdf5-configure.log、hdf5-make.log和未完成的hdf5-check.log；末尾为`Testing: btree2`后`make: *** [Makefile:715: check-recursive] Terminated`，时间23:23:45。HDF5安装prefix、OpenMX官方/overlap构建日志、overlap树manifest、build manifest及材料run root均缺席。因此实际动作越过了旧OpenMPI检查，完成HDF5配置与编译，但没有完成HDF5自测或任何OpenMX构建。

运行态现为：transaction `4d7808af7df9418518a59afeba766eb9`/source_build/RUNNING，child_pid保留历史396；state/workflow的active transaction均为该ID且尚未hard-stop。capability `3cd45d83e11ec6fe0e39725dfe7c6d79`已消费，SHA `f8bcb3463c32286899a3a8b2461f820f8ed7e15e668da5b381bffc8df1c52721`，对应launcher receipt缺席。ledger仍为执行前66755 bytes/SHA `8dfbb2bb9f23ac9066b457553c2bccfa94a2ab7dde5d66f6315595caaa793421`，故此次用时尚未由原控制器提交。

现已交独立子agent封存中断事实。旧permit、operation和已消费capability不得重放；恢复应保留中断源码树与日志、保守补记外部中断用时、从已验证干净树重建工作副本，并建立新的单次机器许可和独立执行前门控。本记录不提前批准该技术门控，不关闭M9-DATA-B01。
