# M9 source_prepare Python 3.9 恢复 PID 复用定点复核

复核日期：2026-08-28；第二次定点复核：2026-08-28  
复核对象：`M9-SP-PY39-RCV-R02` 及既有 `M9-SP-PY39-RCV-B01`—`B04`、`M9-SP-PY39-RCV-R01` 回归边界  
执行方式：当前冻结闭集全量哈希、固定 Python 3.9 回归、系统临时目录合成 `/proc/<pid>/cmdline` 夹具、正式 WSL 失败现场前后只读 receipt 与 inventory 对照  
执行限制：未执行正式 `create-gate`、`recover`、`source_prepare`、`source_build`、安装或下载；未使用 `py_compile`；除本报告外未修改项目文件

## 第二次定点复核结论（当前正式结论）

**verdict：PASS。`BLOCKING=0`，`NON_BLOCKING=0`。**  
**`M9-SP-PY39-RCV-R02`：CLOSED。**  
**B01—B04、R01：CLOSED，无回归。**

当前 `process_matches_argv()` 在验证 PID 为正、argv 非空、全部字段为字符串且不含 NUL 后，按 `b"\0".join(item.encode("utf-8") for item in expected_argv) + b"\0"` 构造唯一 expected cmdline bytes，并与 `/proc/<pid>/cmdline` 原始 bytes 直接相等比较；实现不再删除或规范化空参数。固定 Python 3.9 系统临时夹具独立验证六个分支：普通不同 argv PID 复用返回 `False`；精确 argv 返回 `True`；末尾额外空参数返回 `False`；中间额外空参数返回 `False`；expected 含空参数时精确 cmdline 返回 `True`；expected 字段内嵌 NUL 抛出 `ValueError`。第一次复核发现的两个稳定反例均已关闭。

当前冻结专用测试包含相同六分支，并继续覆盖既有 14 个 atomic-json 崩溃窗口、snapshot、rename、partial ledger、retirement 四态、锁与 runtime receipt、phase-pair、terminal replay、预算历史、gate/scope 绑定及 build/input UTF-8/LF 路径。固定 Python 下 110/110 控制测试与 16/16 恢复测试均通过；代码复核未发现 R02 修订改变恢复状态机、锁边界或 post receipt 继承逻辑。因此 B01—B04 与 R01 保持 `CLOSED`，未发现新 BLOCKING 或 NON_BLOCKING。

### 当前冻结证据与测试结果

| 对象 | SHA-256 |
|---|---|
| 当前工作包 | `804406a561b7f86ce46321aa3286552ddeabf07b430e3f29736570f9b9f7a72d` |
| 当前恢复控制器 | `9a3adee564563a7c8e5d05c4378c5d288f60d41b39ce4aae132f0e838faa380c` |
| 当前 16 项专用测试 | `cbdaeab164496a8eac773ce4a376f53355a20976c55a7a7c11fb8c5e22ed02ab` |
| 当前 22 文件冻结 manifest | `9923f68e77e5ad63350af84ed42c9eac1826621f6c5a9a0c9b48df6d4c875d8d` |
| 19-receipt 恢复合同 | `c1583a02cc7e1d6393f015e9a5bff2165e62b0941ffa47d00694f5d002ed1d7b` |

```text
wsl.exe -u root -- /home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B /mnt/e/Projects/Codex/DeepH/06_reproduction/tests/test_m9_overlap_controls.py
Ran 110 tests in 34.389s — OK

wsl.exe -u root -- /home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B /mnt/e/Projects/Codex/DeepH/06_reproduction/tests/test_m9_source_prepare_py39_recovery.py
Ran 16 tests in 7.519s — OK

固定 Python stdin 合成 proc_root 独立穿透
unrelated_reused_pid=false；exact_argv=true；trailing_extra_empty=false；
middle_extra_empty=false；exact_expected_with_empty=true；embedded_nul_rejected=true
结果：PASS（6/6）
```

正式现场在复核前后均为：22/22 冻结成员匹配；19/19 预恢复 receipt 匹配；state/workflow 双 `HARD_STOP`；ledger 61,248 bytes、SHA-256 `a2170772c37b601112f0d957a18a6e9375dc7cf2eb22697a26b61a5db3ed770d`；预算及历史字段 canonical SHA-256 `f3cc3139da4f074a4c43882e6597cd312094e821f32842b9e764a0d1e9736f46`；staging 原位且 inventory 为 140 个目录、5,179 个普通文件、5,319 条记录、632,029,184 allocated bytes、SHA-256 `0c0389f29f3a87e26af3c884b13bcc7c6dc6f183b50d803b9affa5fbd4e3920e`。历史 PID 391 当前不是冻结 launcher；相关活动进程为 0；retired、recovery gate、journal、transaction、failure snapshot 与五项禁止产品缺席；cache 为 0。正式 WSL 运行态未发生写入。

本 PASS 仅适用于当前冻结闭集和上述正式失败现场，只授权后续由主 agent 机械创建一次 recovery gate 并执行一次 `recover`。它不授权 `source_prepare`、`source_build`、smoke、batch、GPU、Hamiltonian、SCF 或其他计算；恢复后仍须执行独立事实审计、重建并审计 consumer gate，并取得新的明确单次 `source_prepare` 授权。

## 第一次定点复核结论（历史，已由上方第二次定点复核结论取代）

**verdict：FAIL。`BLOCKING=1`，`NON_BLOCKING=0`。**  
**`M9-SP-PY39-RCV-R02`：OPEN。**  
**B01—B04、R01：CLOSED，无回归。**

当前实现已经把活动进程判据从单纯 `/proc/<pid>` 存在性收紧为 cmdline 与 consumed capability 中冻结 `launcher_argv` 的比较，普通“不同 argv PID 复用”与完全相同 argv 两个分支均按预期工作。然而，`process_matches_argv()` 使用 `[item for item in payload.split(b"\0") if item]` 解析当前 cmdline，删除了全部空参数。因此该实现不是工作包要求的完整逐参数、逐字节相等。

独立合成夹具得到稳定反例：冻结 argv 的精确 cmdline 返回 `True`，普通不同 argv 返回 `False`；但当前 cmdline 在末尾或中间额外包含一个空参数时仍返回 `True`，尽管实际 argv 已不同；当冻结 expected argv 本身合法包含空参数且当前 cmdline 完全相同时，函数反而返回 `False`。因此一个复用历史 PID 的无关进程只要 argv 与冻结 launcher 相同但多一个空参数，就会被误判为原 launcher 仍存活并阻塞恢复预检。该结果直接违反 R02 的关闭条件，现有第 16 项测试未覆盖空参数或原始 cmdline 字节规范化边界。

本轮不更新 `08_audits/M9_source_prepare_py39_recovery_final_verdict.json`。现存旧 PASS verdict 绑定旧报告、旧工作包哈希 `d3c768f635564a67134f25e54f0419fb873dfbfb0a90f3838150ca8cf805444c` 和旧冻结清单哈希 `a538b521e91fb171b6e844dcce25439ccf43bb4f2fe6f8c263e1f39cad5250dd`，与当前工作包和冻结清单不匹配，不能用于创建恢复 gate。

## 冻结证据

| 对象 | SHA-256 |
|---|---|
| 当前工作包 | `74ce60696ce1fde5588f31da6bf3647a0a0f4dee63e651163aac28a55db268f1` |
| 当前恢复控制器 | `1fffcae55906af0c78f63b4a16bfb20f2a1fc43be397d0b7ebc58d5263f64f90` |
| 当前 16 项专用测试 | `5ff0a38bd23af632567604b056a9113a6652a7b499bff7cb304f02be1e3d490b` |
| 当前 22 文件冻结 manifest | `1b3a55caddf0a440be410e47aa776d37bc5d77702561d0d759609b56c8b9427a` |
| 19-receipt 恢复合同 | `c1583a02cc7e1d6393f015e9a5bff2165e62b0941ffa47d00694f5d002ed1d7b` |
| 第二次定点复核 PASS 历史报告 | `9483249601b510ae0a58473223e6da1890df2787ba0d99d17dedf04b3b416cef` |
| 现存旧 verdict（本轮未修改） | `28f0369e02e28fb621ef0d0a15c31cf4708fe2232713369df07e055618f0bf7d` |

冻结 manifest 的 22 个成员逐文件重算为 22/22 匹配，无缺失或哈希漂移。控制器 R02 之外的阶段、锁、receipt 继承与 terminal 路径仍保持先前审计过的结构；完整恢复测试复验了 14 个 atomic-json 崩溃窗口、snapshot、rename、partial ledger、state/workflow 单边提交、phase-pair、terminal replay、链接和元数据漂移、预算历史、gate/scope 绑定及 build/input UTF-8/LF 写入路径，未发现 B01—B04 或 R01 回归。

## 测试与主动穿透

固定解释器为 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9`，全部命令均使用 `-I -S -B`：

```text
wsl.exe -u root -- /home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B /mnt/e/Projects/Codex/DeepH/06_reproduction/tests/test_m9_overlap_controls.py
Ran 110 tests in 33.338s — OK

wsl.exe -u root -- /home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B /mnt/e/Projects/Codex/DeepH/06_reproduction/tests/test_m9_source_prepare_py39_recovery.py
Ran 16 tests in 7.254s — OK

固定 Python stdin 合成 proc_root 定点夹具
unrelated_reused_pid=false
exact_argv=true
extra_empty_argument_at_end=true       # 应为 false
extra_empty_argument_in_middle=true    # 应为 false
exact_expected_includes_empty=false    # 应为 true
结果：FAIL
```

通过 110/110 与 16/16 只能证明现有冻结测试断言成立，不能推翻上述未覆盖的稳定反例。最小关闭条件是：拒绝 expected argv 中含 NUL 的字段，并直接构造唯一 canonical cmdline bytes `b"\0".join(item.encode("utf-8") for item in expected_argv) + b"\0"`，将其与 `/proc/<pid>/cmdline` 原始 bytes 完全相等比较，不得删除中间或额外空字段。冻结测试至少应加入末尾额外空参数、中间额外空参数、冻结 argv 含空参数的精确正例和含 NUL expected 字段的拒绝例；修订后须更新闭集并再次由独立审计复核。

## 正式现场零写入证据

正式现场在主动穿透前后均为：22/22 冻结文件匹配；19/19 预恢复 receipt 的 SHA-256、bytes、uid/gid、mode、nlink 及合同要求的 `st_dev/st_ino` 匹配；state 为 `hard_stopped=true`，workflow 为 `stage=HARD_STOP` 且 `hard_stopped=true`；失败 transaction 为 `FAILED_COMMITTED`；历史 PID 391 当前 cmdline 不与冻结 launcher argv 相等；相关 launcher、build、OpenMX、make、configure 活动进程为 0。

ledger 保持 61,248 bytes，SHA-256 `a2170772c37b601112f0d957a18a6e9375dc7cf2eb22697a26b61a5db3ed770d`。CPU、credit、GPU、wall-clock 与 storage 历史字段逐字节绑定在未变的 state receipt 中；staging 仍为 140 个目录、5,179 个普通文件、5,319 条记录、619,112,384 apparent bytes、632,029,184 allocated bytes，inventory SHA-256 `0c0389f29f3a87e26af3c884b13bcc7c6dc6f183b50d803b9affa5fbd4e3920e`。retired、正式 recovery gate、journal、recovery transaction、failure snapshot 及五项禁止产品均缺席；`06_reproduction` cache 为 0。全部破坏性数据仅位于系统临时目录并已随夹具销毁，正式 WSL 运行态没有写入。

## 适用范围与授权边界

本 FAIL 适用于当前 SHA-256 为 `1b3a55caddf0a440be410e47aa776d37bc5d77702561d0d759609b56c8b9427a` 的 22 文件闭集及当前正式失败现场。它不授权创建 recovery gate，不授权执行 `recover`，也不授权 `source_prepare`、`source_build` 或任何后续计算。只有 R02 经修订并由独立复核确认为 `CLOSED`，同时 `BLOCKING=0`、`NON_BLOCKING=0`，才可生成绑定新报告、当前工作包和当前冻结清单的结构化 PASS verdict；该 PASS 仍只授权主 agent 机械创建一次 recovery gate 并执行一次 `recover`，不构成任何 source prepare/build 授权。
