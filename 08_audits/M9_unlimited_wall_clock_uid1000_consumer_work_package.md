# M9 D-018 UID1000 消费证明工作包

状态：`READY_FOR_THIRD_TARGETED_REAUDIT`  
适用问题：`D018-EGF-B01`、`D018-UID-B01`—`D018-UID-B06`、`D018-UID-B02-R01`  
授权来源：D-018 无时限总墙钟授权；CPU、GPU、存储预算与全部历史用量保持不变。

## 1. 问题与修复边界

D-018 迁移及其执行事实已经分别通过独立审计。现行 execution-fact gate 可由 root 验证，但普通 overlap 动作必须以 UID1000 执行；原完整验证器需要读取 root:root、`0600` 的 D-017 recovery gate、D-018 journal 与迁移前快照，因此真实 UID1000 必然失败。降低历史证据权限会扩大攻击面并改变既有证据合同，不属于本修复范围。

本工作包新增 root 签发、UID1000 消费证明层。root-private 历史对象保持原路径、原字节、owner、mode 与 link count。项目侧冻结源先由 root-only 安装器复制到 `/home/evan-williams/deeph-m9/controls/uid1000-consumer` 的只读快照；正式适配器和未修改控制器均从该快照加载。新层只绑定已独立审计的 execution-fact gate，并在预算锁内重新核验 UID1000 可读的全部终态对象。

原 `06_reproduction/scripts/` 控制目录、`m9_budget.py`、source launcher、overlap contract、原测试与 `m9_overlap_frozen_hashes.json` 必须逐字节保持 D-018 迁移时的冻结值。项目侧适配器为 `06_reproduction/controllers/m9_budget_uid1000_consumer.py`，root bootstrap 为 `06_reproduction/controllers/m9_uid1000_consumer_bootstrap.py`，安装器为 `06_reproduction/controllers/m9_uid1000_consumer_install.py`。适配器只在原控制器取得 `budget.lock` 后替换三个只读验证回调；原事务、预算、capability、launcher 与失败提交实现不变。

## 2. 新对象与权限合同

独立审计通过后才允许生成和安装下列对象：

- 首次定点复核失败报告：`08_audits/M9_unlimited_wall_clock_uid1000_consumer_targeted_reaudit.md`，保持只读；
- 第二次定点复核失败报告：`08_audits/M9_unlimited_wall_clock_uid1000_consumer_second_targeted_reaudit.md`，保持只读；
- 第三次定点复核报告：`08_audits/M9_unlimited_wall_clock_uid1000_consumer_third_targeted_reaudit.md`；
- verdict：`08_audits/M9_unlimited_wall_clock_uid1000_consumer_final_verdict.json`；
- bootstrap 信任目录：`/home/evan-williams/deeph-m9/controls/uid1000-consumer-bootstrap`，root:group1000、`0550`，三份代码、PASS verdict、第三次复核报告及 receipt 均为 root:group1000、`0440`、`nlink=1`；
- 快照目录：`/home/evan-williams/deeph-m9/controls/uid1000-consumer`，root:group1000、`0550`；
- 快照成员：root:group1000、`0440`、普通文件、`nlink=1`；
- consumer gate：`/home/evan-williams/deeph-m9/manifests/overlap_unlimited_wall_clock_uid1000_consumer_gate.json`，root:group1000、`0640`、普通文件、`nlink=1`；
- gate schema：`m9-unlimited-wall-clock-uid1000-consumer-gate-v1`；
- 唯一 scope：`ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018`。

适配器合同为 `06_reproduction/manifests/m9_uid1000_consumer_contract.json`。bootstrap 只允许由 root 使用冻结 Python 的 `-I -S -B`，通过审计后固定的单文件描述符 loader 执行：loader 以 `O_RDONLY|O_NOFOLLOW` 打开项目 bootstrap，`fstat` 要求普通单链接文件，从同一描述符读取全部字节并核对第三次 PASS 审计冻结的 bootstrap SHA-256，再以这些同一字节 `compile/exec`。传给 bootstrap 的六个固定哈希依次为 bootstrap、installer、adapter、冻结清单、PASS verdict 与第三次复核报告的 SHA-256。bootstrap 再用同一文件描述符算法核验这些项目对象，随后安装 root-owned 闭集。项目侧 bootstrap、installer 或 adapter 均不得直接作为正式 Python 文件入口；项目 installer 作为 `__main__` 启动时，必须在选择或执行任何 adapter loader 之前按实际 `__file__` 拒绝。

快照与 gate 的后续安装必须从 root-owned bootstrap 目录内的 installer 执行。正式消费同样必须使用冻结 Python 的 `-I -S -B`，入口必须是快照内适配器，EUID 必须为 1000，且 argv 只允许原 `run --overlap-operation --overlap-action source_prepare` 形态。其他子命令、其他 action 与自由 `--` argv 均拒绝。

正式 bootstrap 的 `python -c` 源必须逐字节采用下列 loader；命令参数为项目 bootstrap 路径，随后是上述六个哈希：

```python
import hashlib, os, stat, sys
path, expected = sys.argv[1], sys.argv[2]
flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
descriptor = os.open(path, flags)
try:
    before = os.fstat(descriptor)
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise SystemExit("bootstrap loader metadata mismatch")
    chunks = []
    while True:
        chunk = os.read(descriptor, 1024 * 1024)
        if not chunk:
            break
        chunks.append(chunk)
    payload = b"".join(chunks)
    after = os.fstat(descriptor)
    linked = os.lstat(path)
    fields = ("st_dev", "st_ino", "st_mode", "st_uid", "st_gid", "st_nlink", "st_size")
    if (any(getattr(before, key) != getattr(after, key) for key in fields)
            or any(getattr(after, key) != getattr(linked, key) for key in fields)
            or stat.S_ISLNK(linked.st_mode) or len(payload) != after.st_size
            or hashlib.sha256(payload).hexdigest() != expected):
        raise SystemExit("bootstrap loader receipt mismatch")
finally:
    os.close(descriptor)
sys.argv = [path, expected, *sys.argv[3:]]
scope = {"__name__": "__main__", "__file__": path, "__builtins__": __builtins__}
exec(compile(payload, path, "exec"), scope, scope)
```

gate 必须绑定独立 verdict、第三次定点复核报告、当前工作包、D-018 授权、专用冻结清单、root bootstrap receipt、root 快照 manifest、既有 execution-fact gate 的实际 SHA-256、D-018 transaction SHA-256，以及签发时 UID1000 可读运行态的完整收据。快照 manifest 以项目侧绝对源路径为键，逐项绑定快照路径、字节数与 SHA-256；两个 root 目录内均不得存在未登记成员。

## 3. 信任边界与运行态闭集

完整 root 审计验证器仍是迁移执行事实的权威验证器。UID1000 消费验证器不读取 root-private 对象，而把既有 execution-fact gate 视为 root 签发的历史证据封装。该 gate 必须保持 root:group1000、`0640`、`nlink=1`，且 SHA-256 与 consumer gate 一致。

UID1000 必须在 `budget.lock` 排他锁内重新计算 budget state、workflow state、ledger 及字节数、overlap transaction、source-control recovery transaction、D-018 migration gate、D-018 transaction、execution-fact gate、当前 active overlap gate，以及 source/build 产品缺席集合。UID1000 所有的五个运行态对象必须精确为 UID1000:UID1000、`0644`、`nlink=1`；四个 root 控制对象必须精确为 root:group1000、`0640`、`nlink=1`。所有与 execution-fact gate runtime 重叠的字段逐项相等。

消费前还必须满足：墙钟策略为 `UNLIMITED`；budget 与 workflow 均未 hard-stop；活动事务均为空；workflow stage 为 `AUDIT_PASSED`；D-018 transaction 为 `SUCCESS_COMMITTED`；source/build 产品集合为空。产品缺席使用目录项语义 `lexists` 判定，悬空 symlink 也属于已存在并必须拒绝。语义解析使用与收据同次读取的字节，完成后再次读取全部运行态并要求收据逐项相等；第一次正式状态写入前还须再次执行完整验证。任何字段、哈希、文件类型、owner、group、mode、link count、scope、闭集或跨读取漂移均拒绝。

## 4. 行为限制

快照内适配器把快照内原控制器的 root 完整验证回调替换为 UID1000 消费验证回调，然后委托原控制器的未修改 `main()`。回调由原 `command_overlap_run` 在 `budget.lock` 内调用；适配器还包装原 `atomic_json`，在第一次状态写入边界再次完成全量验证。通过 gate 也只允许 action=`source_prepare`。`source_build`、smoke、batch、GPU、通用 `run` 与任意 shell 命令均不获授权。

该修复不得重置或增加任何 CPU、GPU、存储预算，不得删除、改写或抵扣历史用量，不得更改 D-018 migration transaction、journal、snapshot、旧/新 overlap gate、execution-fact gate 或既有 ledger 字节。

## 5. 测试与独立审计门控

固定 Python 为 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B`。测试至少覆盖：

1. root 创建的临时快照和 consumer gate 在真实 `setuid(1000)` 子进程中验证通过；
2. 同一子进程不读取 root:root、`0600` 的 D-017 gate、D-018 journal 与 snapshot；
3. consumer gate、execution-fact gate、冻结清单、verdict、报告、工作包、授权、快照成员和可读 runtime 任一字节或元数据漂移均拒绝；
4. 快照成员 symlink、hardlink、错误 owner、group 或 mode 均拒绝，快照目录为严格闭集；
5. 项目侧 installer 必须在任何 adapter `exec_module` 前拒绝，项目侧 adapter 直接执行也拒绝；single-FD bootstrap 只安装审计冻结字节，root bootstrap 目录为严格闭集；
6. 悬空 source/build 产品 symlink 被判定为存在并拒绝；
7. bootstrap 与 snapshot 在完成 `0550` 封存后、最终 rename 失败时均可幂等续提，且不重新读取未冻结项目代码；
8. scope 不能授权 `source_build`；
9. 原 controller、launcher、contract、原测试、overlap frozen manifest 与 active gate 仍形成可执行闭集；
10. 所有验证位于预算锁内，跨读取漂移被终态复读拒绝，第一次状态写入边界再次全量验证；
11. 原 109 项回归与适配器测试、AST、严格 Markdown/MathML、JSON、控制字符、链接、缓存及正式运行态前后哈希检查通过。

正式独立审计必须由原独立审计 agent 执行。只有定点复核同时为 `PASS`、`BLOCKING=0`、`NON_BLOCKING=0` 时，主 agent 才可由 root 机械创建一次快照和 consumer gate。快照与 gate 创建后还应以真实 UID1000 调用实际 verifier，并由同一独立 agent 进行事实复核；在该复核明确放行前，不执行 `source_prepare`。
