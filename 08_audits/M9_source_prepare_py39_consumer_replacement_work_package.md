# M9 Python 3.9 恢复后 active gate 与 UID1000 consumer 替代工作包

状态：`READY_FOR_INDEPENDENT_IMPLEMENTATION_AUDIT`  
决策边界：`D-018-PY39-CONSUMER-REPLACEMENT`  
前置事实：`M9_source_prepare_py39_recovery_execution_independent_audit.md` 已确认一次性 recovery 为 `PASS/0/0`。

## 1. 目标与不授权事项

本工作包只恢复“可在取得新的单次用户授权后执行一次 `source_prepare`”的可信消费链。它不构成新的用户执行授权，不允许 `source_prepare`、`source_build`、smoke、batch、GPU、Hamiltonian、SCF 或其他计算。正式安装与事实审计期间，`overlap_source_prepare_py39_single_run_authorization.json` 必须保持缺席；adapter 对其缺席执行零写拒绝。安装事实审计通过并取得用户新的明确单次授权后，才可另行建立 root 签发的 authorization object，使其绑定授权记录、consumer gate、active gate、当前 runtime、唯一 32 位 operation id、一次性 nonce 与唯一 action `source_prepare`。该对象不得扩展到 source build、smoke、batch 或 GPU。

Python 3.9 修复改变了 `m9_openmx_build.py`、`m9_openmx_input.py`、`m9_overlap_common.py` 及回归测试，旧 active overlap gate、旧冻结 manifest、旧 UID1000 snapshot 和旧 consumer gate 因而只能作为历史证据，不能再次消费。旧 root snapshot、bootstrap、consumer gate、D-017/D-018 gate、失败 transaction、consumed capability、FAIL receipt、recovery gate/journal/transaction/failure snapshot及全部 ledger/state 历史必须保持原路径、字节和权限。

## 2. 替代对象

项目侧新冻结对象为：

- `06_reproduction/manifests/m9_overlap_py39_recovery_frozen_hashes.json`；
- `06_reproduction/manifests/m9_source_prepare_py39_uid1000_consumer_frozen_hashes.json`；
- `06_reproduction/manifests/m9_source_prepare_py39_uid1000_consumer_contract.json`；
- 本工作包、独立实施报告与结构化 final verdict。

root 安装对象为：

- bootstrap：`/home/evan-williams/deeph-m9/controls/uid1000-consumer-py39-v2-bootstrap`；
- snapshot：`/home/evan-williams/deeph-m9/controls/uid1000-consumer-py39-v2`；
- consumer gate：`/home/evan-williams/deeph-m9/manifests/overlap_source_prepare_py39_uid1000_consumer_gate.json`；
- active gate 旧值退休路径：`overlap_work_package_audit_gate.pre-py39-recovery.retired.json`；
- active gate refresh journal：`/root/deeph-m9-control/source-prepare-py39-consumer-refresh.json`。

两个 root 目录均为 root:group1000、`0550`；成员均为 root:group1000、`0440`、普通单链接文件。新 consumer gate 与 active gate 均为 root:group1000、`0640`、普通单链接文件。旧 active gate 的 SHA-256 必须为 `78311a978c2472c85b35a745d80e1f33724c1500cf8d7bd244cdbe83c3fa3698`，只允许原子 rename 到固定退休路径，不得覆盖或删除。

## 3. 安装事务与崩溃续提

root bootstrap 继续使用既有 single-FD、`O_NOFOLLOW`、同一字节 SHA loader 模式，但安装到版本化的新目录。trusted installer 必须在既存 `budget.lock` 排他锁内完成 snapshot、active gate refresh 与 consumer gate 安装。

正式 bootstrap 的 `python -c` 源固定如下；其后依次传入项目 bootstrap 路径以及 bootstrap、installer、adapter、consumer frozen manifest、PASS verdict、独立报告六个 SHA-256：

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

active gate refresh 状态机为 `PREPARED -> STAGED -> OLD_RETIRED -> ACTIVE_REPLACED -> SUCCESS_COMMITTED`。先持久化 root-private journal，再写 root:group1000 `0640` staging gate；旧 active gate rename 到退休路径后，才把 staging rename 为 active。任一 rename 后必须 fsync manifest 目录。重入必须根据 journal 与 active/retired/staging 三路径的完整 receipt 收敛；不同字节、owner/group、mode、nlink、symlink、hardlink、非法相位或额外路径均拒绝。刷新不得改变 state、workflow、ledger、budget lock、失败/恢复事务、capability、receipt 或产品目录。

新 active gate 继续采用 `m9-overlap-audit-gate-v1`，但绑定本工作包、替代 final verdict、恢复执行事实报告和修复后的 overlap frozen manifest。`m9_budget.py` 与 source launcher 均只读取该新 manifest；manifest 必须覆盖 `06_reproduction/scripts` 的完整 Python 闭集及合同、source manifest 和测试。

## 4. UID1000 消费验证

新 snapshot 必须封存当前 adapter、bootstrap、installer、原预算控制器、source launcher、修复后的 build/input/common、合同、测试、工作包、恢复 PASS verdict 和恢复执行事实报告。root installer 必须读取 root-private recovery gate、SUCCESS recovery transaction 和 failure snapshot，确认 snapshot 与原失败 transaction 逐字节相等，再签发 consumer gate。旧 consumer gate、旧 bootstrap receipt 与旧 snapshot manifest 的 SHA-256 分别固定为 `2ba96b8566f2ba38a528e4002dbaa0bebf4f9a7b8c5f10a92b89d643d11a85f2`、`3172bf9516fed5dd2abb3669c705211428cbe6ebeea34fe96fcb6a3016d5f1ba`、`2d13e0c1fb1c1e635ad1730f44f21901340e7483d06356aa8eeb0e07f83dcec9`；旧两个目录的 owner/group/mode、成员闭集及全部成员字节必须在安装前、snapshot 后、active-gate refresh 后和 consumer-gate 安装后复核不变。

UID1000 不读取 root-private 对象。它从 root 签发的 consumer gate 验证 recovery gate/transaction 哈希、恢复事实报告、当前 active gate、历史 D-018 execution gate、当前九项可读 runtime、snapshot 闭集与冻结清单；在 `budget.lock` 内完成首次读取、语义验证、终态复读，并在第一次状态写入前再次全量验证。历史 execution gate 仅作为 D-018 历史证据，不再要求其旧 runtime 等于恢复后的 state/workflow/ledger；原控制器得到的代理 gate 必须使用当前 consumer runtime，scope 只为其既有内部分支提供兼容，不扩展实际 adapter 的 `source_prepare` 唯一 action 限制。

## 5. 测试与门控

固定解释器必须为 Python 3.9.23，全部测试使用 `-I -S -B`，禁止 `py_compile`。至少覆盖：新旧 root 路径不重叠；项目 installer 直接入口拒绝；bootstrap/snapshot rename 失败续提；active gate 五阶段及两个 rename 崩溃窗口续提；旧 gate 字节保留；staging/retired/active 路径漂移拒绝；新 gate 对 verdict、work package、恢复事实和 frozen manifest 的绑定；真实 UID1000 verifier；current runtime 复读和首次写入前复核；悬空产品、scope/source_build、symlink/hardlink/owner/group/mode/nlink 负例；现有 overlap 与 consumer 回归。

独立实施审计必须由独立子 agent 执行。只有 `PASS/BLOCKING=0/NON_BLOCKING=0` 才允许 root 机械安装；安装后还必须独立执行事实审计。事实审计通过前不得请求或执行新的 `source_prepare`；事实审计通过后必须向用户请求一次明确授权。

## 6. 首次独立审计后的强制修订

首次独立实施审计判定 `FAIL/BLOCKING=6/NON_BLOCKING=0`，冻结 `M9-SP-PY39-CONS-B01`—`B06`。修订闭集必须满足以下附加条件：

- common、合同、budget controller 与 source launcher 唯一读取 `m9_overlap_py39_recovery_frozen_hashes.json`，冻结正例必须真实调用 `verify_frozen_project_files()`；
- 安装事实阶段不得创建 `overlap_source_prepare_py39_single_run_authorization.json`。adapter 在该对象缺席时必须于任何状态写入前零写拒绝；对象只接受 `ALLOW_EXACTLY_ONE_SOURCE_PREPARE`，绑定未来授权记录、readiness consumer gate、active gate、当前 runtime、32 位 operation id 与 64 位 nonce；
- refresh journal 每一相位使用严格字段闭集。`PREPARED` 只能拥有旧 active；`STAGED` 继承 staging inode；`OLD_RETIRED` 继承旧 active 到 retired 的同一 inode；`ACTIVE_REPLACED/SUCCESS_COMMITTED` 继承 staging 到 active 的同一 inode。只允许 `STAGED` 与 `OLD_RETIRED` 两个真实 rename 后、journal 前崩溃窗口续提，其他 phase/path 组合零写拒绝；
- single-FD bootstrap 在 trust-root staging 前、trusted installer 在 snapshot staging 前，均以 `O_NOFOLLOW` 打开既存 budget lock 并在同一 FD 排他锁内核对 recovery gate/transaction/failure snapshot 固定哈希、transaction 完整字段闭集、post state/workflow/ledger inode receipt、全部 immutable pre-runtime receipt、历史证据、产品缺席和预算语义。snapshot、refresh、consumer-gate 的每一写入边界前后均复核相同 immutable receipt 与 lock；
- 所有必须缺席的目标使用 `lexists`。dangling symlink、symlink、hardlink、错误 owner/group/mode/nlink、额外路径、同字节新 inode 或非法 journal 字段均不得被覆盖或吸收为新事实。

修订后必须由同一审计链定点复核上述六项，并重新确认正式 WSL 仍为安装前零写状态。

## 7. 第一次定点复核后的 R01/R02 修订

同一独立审计员第一次定点复核确认 B01、B04、B05、B06 已关闭，但判定 `FAIL/BLOCKING=2/NON_BLOCKING=0`，冻结 `M9-SP-PY39-CONS-R01` 与 `M9-SP-PY39-CONS-R02`。R01 的原因是 adapter 曾把 32 位 operation id 置于冻结控制器的布尔 `--overlap-operation` 之后，真实 `argparse.REMAINDER` 因而会把该 id 及后续字段吸收为自由命令。修订后 operation id 只通过 adapter 专用 `--consumer-operation-id <32-lowercase-hex>` 进入；adapter 在任何授权读取或写入前严格验证该字段，将且仅将这两个 token 移除，再把原生 `--overlap-operation` 布尔开关、`--overlap-action source_prepare`、无 GPU bucket、固定 CPU bucket、forecast 和合同路径原样交给冻结 parser。真实 parser 与 `validate_overlap_request()` 必须证明 `command=[]`，source build、重复 id、非法 id、缺布尔开关及自由 argv 均拒绝。

R02 的原因是 refresh 内层状态机虽可续提 rename 后、journal 前窗口，但 installer 顶层总先要求旧 active gate 位于原路径，进程重启后无法到达内层续提。修订将恢复后不可变核心检查与 active-gate 相位检查分离：installer 在同一 `budget.lock` FD 下先验证完整 recovery/runtime 核心；若 refresh journal 已存在，则 replacement snapshot 必须已封存，installer 只读复核其闭集和 journal 严格字段，再按 phase/path/inode 矩阵选择续提。允许的重启态仅为 `STAGED` 的 old-active 已退休窗口、`OLD_RETIRED` 的 replacement 已激活窗口，以及 `SUCCESS_COMMITTED` 后 consumer gate 尚未写入的终态窗口；其他组合零写拒绝。顶层 `prepare_snapshot_for_refresh()` 与 `install_under_lock()` 必须覆盖这三种真实重入，不得通过重复 bootstrap 或重建旧 gate 恢复。

固定 Python 3.9.23 回归现在至少为 22 项 consumer 测试，并继续要求 110 项 overlap 控制回归、两个冻结闭集、严格 Markdown、缓存零新增与正式 WSL 零写。只有同一审计员关闭 R01/R02 并给出 `PASS/BLOCKING=0/NON_BLOCKING=0`，才允许执行 single-FD bootstrap 和 trusted installer；该 PASS 仍不授权 `source_prepare`。

## 8. 第二次定点复核后的 R03 修订

第二次定点复核确认 R01/R02 已关闭，但判定 `FAIL/BLOCKING=1/NON_BLOCKING=0`，冻结 `M9-SP-PY39-CONS-R03`：pristine 路径原先先调用 `prepare_snapshot_for_refresh()`，可能写入 replacement snapshot，随后才在锁内复核完整历史 consumer 闭集和 authorization 缺席；main 的锁外读取不能覆盖其间漂移。修订后的 `install_under_lock()` 必须在调用 `prepare_snapshot_for_refresh()` 之前，在已持有的同一 `budget.lock` FD 下执行 `verify_installation_guard()`，逐成员重放历史 bootstrap/snapshot 闭集与历史 consumer gate，并用 `lexists` 确认单次 authorization 对象缺席。任一历史漂移或 authorization namespace 存在都必须在 `prepare_snapshot_for_refresh()` 被调用前零写拒绝。

snapshot 安装或只读续提完成后、active-gate refresh 后及 consumer-gate 安装后仍须重复同一 guard；因此首写前检查不能以删去写后检查实现。R02 的三类 journal 重入继续按既有严格 phase/path/inode 矩阵执行。新增顺序测试必须主动记录 `history -> authorization -> prepare_snapshot`，并证明历史漂移和 authorization 存在时 prepare 函数零次调用。固定 Python 3.9.23 consumer 回归因此扩展为 23 项。只有原审计员关闭 R03、确认 R01/R02 与 B01/B04/B05/B06 无回归并给出 `PASS/0/0` 后，才允许机械安装；仍不授权 `source_prepare`。
