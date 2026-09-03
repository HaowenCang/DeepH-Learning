# M9 source_prepare 拒绝调用执行事实独立审计

审计日期：2026-08-21  
审计对象：首次从 installed UID1000 consumer adapter 发起、因缺少 `--bucket` 而被 argparse 拒绝的 source_prepare 调用  
审计方式：原控制器执行顺序与 argparse 静态审阅、隔离 parser 复算、consumer gate 真实 UID1000 复验、历史 13 项与安装新 3 项 SHA-256 核对、transaction/capability/receipt/product/process 零执行检查  
执行边界：本审计只读；未执行或重试 `source_prepare`、`source_build` 或其他 action；隔离 parser 复算只构造 Namespace，未调用任何 action handler

## 审计结论

拒绝事实审计为 **PASS**。`BLOCKING=0`，`NON_BLOCKING=0`。

该调用确实在原 controller 的 `argparse.ArgumentParser.parse_args()` 阶段以 rc=2 退出，直接原因是 `run` 子命令的必需参数 `--bucket` 缺失。此时尚未调用 `command_run()` 或 `command_overlap_run()`，没有取得 budget lock，没有执行 consumer verifier 代理，没有创建 transaction/capability，没有启动 source launcher，也没有产生 source/build 产品。

拒绝后，consumer gate、bootstrap receipt、snapshot manifest 与全部 13 项历史运行态 SHA-256 均保持上轮事实审计值。budget state 与 workflow 的 active transaction 仍为 null；capability 目录仍只有 D-017 历史 retired capability，不存在活动、consumed 或 launcher receipt；六项 source/build 产品缺席，相关进程为 0。真实 UID1000 verifier 仍对原 consumer gate 返回 PASS。

该失败没有消费技术意义上的 consumer gate、D-017 action capability、CPU/存储预算或底层 D-017/D-018 用户路线授权。但是，上轮独立事实审计授予的是“一次调用后立即停止并复核”的程序性门控；本次调用已触发并完成该门控，因此不得在不经本报告重新放行的情况下直接重试。

现有冻结材料已经足以机械确定唯一最小完整 argv，不需要新的用户路线决策、代码修复、consumer gate、WSL gate 或另一份 argv 实现工作包。本报告把两个既有冻结工作包组合为一个新的窄幅重试门控，并明确允许一次且仅一次使用下文完整命令。执行返回、失败、超时或拒绝后必须再次立即停止；不得自动进入 `source_build`。

## 被拒绝调用与拒绝层级

实际调用的 action argv 为：

```text
run --overlap-operation --overlap-action source_prepare
```

installed adapter 先完成自身 installed-path 检查，再执行 `require_source_prepare_argv()`。该前置检查只限定子命令、action 与自由 `--`，所以上述 argv 能进入未修改的 snapshot controller。adapter 随后安装三个只读 verifier proxy 和首次写入 guard，再调用原 `m9.main()`。

原 controller 的 `build_parser()` 对 `run` 定义：

- `--bucket`：`required=True`；
- `--cpu-bucket`：默认 `none`；
- `--forecast-bytes`：默认 `None`；
- `--overlap-operation`：布尔开关；
- `--overlap-action`：包含 `source_prepare`；
- `--config`、`--log`、`--cwd`、`--structure-id`：parser 层可选；
- 末尾 `command`：`argparse.REMAINDER`。

由于被拒绝 argv 缺少 parser 层唯一立即必需的 `--bucket`，`parse_args()` 在 dispatch 前返回 rc=2。独立只读 parser 复算得到：

```text
MISSING_PARSE_RC=2
MISSING_LAST=-c run: error: the following arguments are required: --bucket
```

`main()` 只有在 `parse_args()` 成功后才执行 `args.func(args)`；本次没有进入 `command_run()`。因此拒绝发生在 argparse，而不是 `validate_overlap_request()`、budget 预检、consumer gate 业务验证、source launcher 或 OpenMX/HDF5 实现中。

## 正式对象零变化

拒绝后独立重算 16 个门控与运行对象，16/16 与上轮安装事实审计值相等：

| 对象 | SHA-256 |
|---|---|
| bootstrap receipt | `3172bf9516fed5dd2abb3669c705211428cbe6ebeea34fe96fcb6a3016d5f1ba` |
| snapshot manifest | `2d13e0c1fb1c1e635ad1730f44f21901340e7483d06356aa8eeb0e07f83dcec9` |
| consumer gate | `2ba96b8566f2ba38a528e4002dbaa0bebf4f9a7b8c5f10a92b89d643d11a85f2` |
| budget state | `c56532b1f92573bd4324464d0b10004df4b5f8337d1e803fdcd80a2f320585a8` |
| workflow | `bd895b2831c805c44a180012ece64bdda00744340768c7062e33b856069fda8a` |
| ledger | `178106f0be9f80ff669ebd0865e214a4b9a60d115074ad0c97ae8de5f1ae33b7` |
| overlap transaction | `12f475b7468036e1bb1370506a0d7f71cb8db283cec2d21e356d3ce3e7b66309` |
| D-017 recovery transaction | `e9b8babcff8a2f42adea21d5cbce614b38f0854271d3389eae0bbcdd7d5e53bc` |
| D-017 gate | `8e66d65d17d3195f3df09db954afca4066c3ec91e2d8dad6d2aea06078d0d5ce` |
| active overlap gate | `78311a978c2472c85b35a745d80e1f33724c1500cf8d7bd244cdbe83c3fa3698` |
| retired overlap gate | `dbe4756142d0e921c3834330550310e85652503c04254b30bea1a069ff35377c` |
| D-018 migration gate | `286a0e409a80f85ca6bb39b76bdb977fc67ffa56f4646b00d3aad5943c98e880` |
| D-018 transaction | `41cbfbd4da1c3a0eea92731a00758355f46321d5b0a66260f53f628290d847ad` |
| D-018 execution-fact gate | `bc51209c13570839c08dd4fc304fe39865a98ade69caeb23886602de2d8be6e9` |
| D-018 journal | `27a92edded459948150c750a4339692434e08a84cbc8879c63c71b6c14cb0e8a` |
| D-018 pre-state snapshot | `00a32bd7f28ad26fa600c8abe9d0fa64efe57e410eacb82ad2d201fa9adc5439` |

root-private D-017 gate、D-018 journal 与 pre-state snapshot 仍为 root:root、`0600`、普通单链接文件。拒绝没有降低历史证据权限。

以真实 EUID 1000、冻结 Python `-I -S -B` 再次只读调用 installed adapter 的 `verify_consumer_gate()`，结果仍为：

```text
GATE_SHA=2ba96b8566f2ba38a528e4002dbaa0bebf4f9a7b8c5f10a92b89d643d11a85f2
STATUS=PASS
SCOPE=ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018
POST_VERIFY_RC=0
```

consumer gate 没有 consumed 字段或可变消费计数；实际一次性消费对象应当是预算事务签发的 capability。本次没有到达该阶段。

## Transaction、capability、产品与进程

拒绝后状态为：

```text
ACTIVE_STATE=None
ACTIVE_WORKFLOW=None
CAP_NAMES=f7c3b060e19e37e6da03f461d754d38c.retired.json
ACTIVE_CAPABILITY_ARTIFACTS=0
CONSUMED_OR_RECEIPT=0
PRODUCTS_ABSENT=6/6
PROCESS_HITS=0
```

现存 `overlap_transaction.json` 是 D-017 历史失败事务，SHA 保持 `12f475b7...b66309`；不能把它误记为本次调用创建的新事务。capability 目录中的唯一 `.retired.json` 同样是受保护的 D-017 历史证据。不存在新的活动 `.json`、`.consumed.json` 或 `.launcher-receipt.json`。

六项缺席产品为 OpenMX build root、build staging、HDF5 root、official tree manifest、overlap tree manifest 与 overlap build manifest。`/proc` 扫描没有 source launcher、OpenMX build 或 OpenMX 进程。由现有证据可以确定本次没有进入业务 action。

## 唯一最小完整 argv

原 `M9_overlap_only_openmx_work_package.md` 已冻结唯一调用骨架：

```text
run --bucket none --cpu-bucket BUCKET --forecast-bytes BYTES
--overlap-operation --overlap-action ACTION --config FROZEN_CONTRACT
```

原 controller 和 overlap contract 又唯一确定 source_prepare 的实例化参数：

- GPU bucket：必须为 `none`；
- CPU bucket：必须为 `overlap_build`；
- forecast：必须不低于 `1073741824` bytes，本门控采用唯一最小值 `1073741824`；
- action：必须为 `source_prepare`；
- config：必须是冻结绝对路径；
- structure ID：source_prepare 不接受，必须省略；
- free command 与 `--`：必须省略；
- `--cwd`：不必提供；省略时 controller 固定 child cwd 为 `/home/evan-williams/deeph-m9`；
- `--log`：不必提供；为减少新增写入，本门控要求省略。

consumer 工作包把原脚本入口替换为 root-owned installed adapter，并保持冻结 Python。因此新的唯一最小完整命令为：

```bash
/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B \
  /home/evan-williams/deeph-m9/controls/uid1000-consumer/m9_budget_uid1000_consumer.py \
  run --bucket none --cpu-bucket overlap_build --forecast-bytes 1073741824 \
  --overlap-operation --overlap-action source_prepare \
  --config /mnt/e/Projects/Codex/DeepH/06_reproduction/configs/m9_overlap_only_contract.json
```

独立 parser 只读复算该 argv 得到：

```text
CORRECTED_FUNC=command_run
bucket='none'
cpu_bucket='overlap_build'
forecast_bytes=1073741824
overlap_operation=True
overlap_action='source_prepare'
config='/mnt/e/Projects/Codex/DeepH/06_reproduction/configs/m9_overlap_only_contract.json'
cwd=None
log=None
structure_id=None
command=[]
```

该复算只调用 `parse_args()`，没有调用 `command_run()`，因此不是 source_prepare 重试。

## 授权消耗与下一门控

需要区分三种“一次性”：

- **上轮审计的一次调用程序性门控**：已经由本次 rc=2 调用触发并关闭；主 agent 按要求立即停止，处置正确。
- **consumer gate 与预算 capability**：均未消费；consumer gate 字节不变，capability 根本未签发。
- **用户的 D-017/D-018 路线授权**：未因 argparse 缺参而消耗或改变；本次没有发生预算事务或业务动作。

遗漏参数属于现有冻结材料可唯一解决的命令组装错误，不涉及材料体系、DFT 后端、软件版本、预算或路线选择。因此无需重新询问用户，也无需修改代码或现有 consumer gate。

本报告本身构成新的独立 argv 重试门控；不要求另建 WSL gate或另一份 argv 工作包。允许主 agent 使用上节命令**一次且仅一次**重试。以下条件不可变：

- 命令必须逐参数等于上节最小完整命令；不得加入 `--cwd`、`--log`、structure ID、自由 argv 或其他 action；
- 必须以真实 UID1000 启动；
- 执行返回、失败、超时、hard-stop 或拒绝后必须立即停止；
- 不得自动重试第二次；
- 不得自动进入 `source_build`；
- 停止后必须由同一独立审计员核对新 transaction、state/workflow、ledger exactly-once、capability/consumed/launcher receipt、六项产品、进程、CPU/存储用量与失败恢复边界。

本报告不授权 `source_build`、smoke、batch、GPU 或其他 M9 动作。
