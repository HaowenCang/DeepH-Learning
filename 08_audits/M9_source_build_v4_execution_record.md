# M9 source_build v4 主端执行记录

日期：2026-09-01 至 2026-09-02。记录角色：主 agent。本文记录唯一调用、可观察进程和恢复后的持久状态，不替代独立执行事实审计，也不授权重试或恢复。

## 执行前权威

[独立执行前审计](M9_source_build_v4_preexecution_audit.md) 为 `PASS/BLOCKING=0/NON_BLOCKING=0`，报告 SHA-256 `b817c7505b5b667dbb990cdfcc5687c87cffd9170f45cef4539096f63b02b727`，完整 274 对象证据 SHA-256 `11c20faeb1069d29804d6ffa5b98705ab6579ced0a62ca7d2b0583eb1c7ecc70`。主端完整读回并重算两份文件哈希。该审计只允许固定 Python 3.9.23、已安装 v4 consumer 和冻结逐 token argv调用一次，不允许重试。

## 唯一调用

主端于 2026-09-01 以 WSL root 启动 `runuser -u evan-williams`，实际 UID1000 命令为：

```bash
/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B \
  /home/evan-williams/deeph-m9/controls/source-build-v4/m9_source_build_v4_consumer.py \
  run --build-operation-id bb0b7c8b982d4d72a66a1f01f95533da \
  --bucket none --cpu-bucket overlap_build --forecast-bytes 4294967296 \
  --overlap-operation --overlap-action source_build \
  --config /mnt/e/Projects/Codex/DeepH/06_reproduction/configs/m9_overlap_only_contract.json
```

这是 v4 source_build 的唯一调用。Codex 宿主会话 ID 为 `74345`。首次 30 秒返回“会话仍运行”且无 stdout/stderr；其后同一会话轮询继续无输出。只读进程快照确认预算 consumer PID 394、launcher PID 397、HDF5 `make -j2` 和 GCC 子进程在运行，实际进入 HDF5 编译。没有启动第二个 consumer 或重试。

## 重新进入工作区后的持久事实

2026-09-02 继续目标时，原会话句柄 `74345` 已不存在。没有据此判定终态或重启；只读检查得到：

- 当前没有 v4 consumer、launcher、make、GCC、Fortran、MPI 或 OpenMX 构建进程；
- WSL `last -x` 记录该实例于 2026-09-01 22:45 启动，22:49 `shutdown system down`；当前新实例启动时间为 2026-09-02 16:07:56，boot ID `cf793119-9460-4255-990b-0824289f7b15`；
- Windows System 日志显示整机由 Explorer 发起的关机在 2026-09-02 00:58:00，EventLog 于 00:58:50 停止，操作系统于 00:58:57 关闭；该整机关机晚于 WSL 22:49 停止约两小时，不能解释为同一时刻的宿主整机关机；
- `budget_state.json` 仍非 hard-stop，但 `active_overlap_transaction=d52575f446d3c62f0fc93c3c65f3c959`；
- `overlap_workflow_state.json` 仍非 hard-stop、stage=`SOURCES_PREPARED`，但 `active_transaction` 同为该 ID；
- `overlap_transaction.json` 仍为 `source_build/RUNNING`，transaction ID `d52575f446d3c62f0fc93c3c65f3c959`，child PID 397，prepared UTC `2026-09-01T14:46:32.118063Z`，start UTC `2026-09-01T14:46:52.111163Z`；
- capability `c68a261b9f1e95c692a3b4241360440e` 已为 `CONSUMED`，SHA-256 `8d6aff34eec0ee29ce8a7b8e6a8fdf8a76b78ec1fe5a5bd584ee1e2587607204`；对应 launcher receipt 缺席；
- state CPU、GPU 和 ledger 尚保持执行前值：`overlap_build=7507.245045788001`，ledger 68,599 bytes、SHA-256 `f3f44ee5169bbeb44d175ff0aa381cda70684ad66f11ce57725c2e774471d4c7`。因此未形成原预算的 SUCCESS/FAIL/HARD_STOP 终态记账；
- 日志目录已经创建。`hdf5-configure.log` 为 25,508 bytes，`hdf5-make.log` 为 190,832 bytes，`hdf5-check.log` 为 19,602 bytes。`hdf5-check.log` 末尾在 `cache_image` 测试处记录 `Terminated`，上级 make 同时终止；没有 OpenMX 构建成功证据。

当前事实属于“外部 WSL 实例停止后遗留的非终态 RUNNING 事务”候选，不是构建 PASS，也不是原预算正常提交的 FAIL。WSL 停止的具体发起者尚无直接证据；现有 Windows 整机关机事件发生在其后，不应将两者混同。

## 当前边界与下一门控

不重放 v4 permit、operation、capability 或唯一命令，不删除或覆盖 BUILD、日志、事务、snapshot、gate、permit及历史证据。下一步由独立子 agent 只读审计完整 namespace、执行前 274 对象差异、运行态、capability、日志、构建树与 Windows/WSL 时间线，判定中断事实及阻塞项。若确认为非终态外部中断，必须另建版本化恢复实现、独立实施审计和一次恢复提交；恢复完成及执行事实再审计之前，不得构造新的构建许可。
