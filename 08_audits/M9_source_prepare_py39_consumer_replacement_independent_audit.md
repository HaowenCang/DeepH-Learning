# M9 Python 3.9 recovery 后 active gate 与 UID1000 consumer 替代闭集第三次独立定点复核

审计日期：2026-08-29  
决策边界：`D-018-PY39-CONSUMER-REPLACEMENT`  
复核范围：`M9-SP-PY39-CONS-R03`，以及已关闭 `R01/R02`、`CONS-B01/B04/B05/B06` 的回归检查  
执行边界：固定 Python 3.9.23 的只读解析、临时目录测试和正式 WSL 只读核验；未执行 bootstrap、installer、`source_prepare`、`source_build`、smoke、batch、GPU 或任何正式运行态写入；未使用 `py_compile`

## 结论

**verdict：PASS。`BLOCKING=0`，`NON_BLOCKING=0`。**

`M9-SP-PY39-CONS-R03` 已关闭；`R01/R02` 与 `CONS-B01/B04/B05/B06` 未发现回归。当前工作包允许后续严格按照 single-FD loader 和 trusted installer 入口执行机械 bootstrap/install，并在安装后另行实施只读事实审计。

本 PASS 仅许可机械安装，不构成 `source_prepare` 授权。安装期间 single-run authorization object 必须保持缺席；安装事实审计通过后仍须取得新的明确用户授权，才可建立该对象。`source_build`、smoke、batch 与 GPU 继续不授权。

## R03 定点复核

### 首次写前 guard 顺序

`install_under_lock()` 仅由 trusted installer 在同一既存 `budget.lock` 的排他锁范围内调用。当前函数在调用 `prepare_snapshot_for_refresh()` 之前先执行：

```python
verify_installation_guard(historical, "before snapshot installation")
```

该 guard 调用 `consumer.verify_historical_consumer_evidence()`。后者不是只比较三个顶层哈希，而是：

- 稳定读取并验证历史 consumer gate；
- 逐成员读取历史 bootstrap receipt 所列 5 个成员，核对字节哈希、大小、root:group1000、`0440`、普通单链接文件，并核对目录闭集；
- 逐成员读取历史 snapshot manifest 所列 27 个成员，执行相同字节、大小、权限与目录闭集核对；
- 核对历史 bootstrap/snapshot 根目录为 root:group1000、`0550`。

随后 guard 使用 `os.path.lexists()` 核对 `overlap_source_prepare_py39_single_run_authorization.json` 缺席。因此 dangling symlink 也被视为 namespace 存在，不会被吸收为“缺席”。只有完整历史证据与 authorization 条件同时通过，才进入可能创建 pristine snapshot staging 的 `prepare_snapshot_for_refresh()`。

### 主动顺序与零写负例

审计侧使用固定解释器，以 mock 仅替代正式写函数并记录真实 `install_under_lock()` 调用顺序。结果为：

```json
{
  "pass": {
    "events": [
      "history", "authorization", "prepare_snapshot",
      "history", "authorization",
      "history", "authorization",
      "history", "authorization"
    ],
    "prepare_calls": 1
  },
  "history_drift": {
    "events": ["history"],
    "prepare_calls": 0,
    "write_marker": []
  },
  "authorization_present": {
    "events": ["history", "authorization"],
    "prepare_calls": 0,
    "write_marker": []
  }
}
```

历史闭集漂移和 authorization namespace 存在均在 `prepare_snapshot_for_refresh()` 之前拒绝；prepare 调用计数为 0，写入 marker 为空，因而 replacement snapshot、refresh journal、retired/staging gate 与 consumer gate 均不能由该路径产生。

### 写后重复 guard

相同 `verify_installation_guard()` 在以下边界重复执行：

- snapshot 安装或只读续提之后；
- active-gate refresh 及其 terminal preflight 之后；
- consumer-gate 安装及其 terminal preflight 之后。

因此首写前修复没有删去原有写后保护。23 项冻结 consumer 测试中的专门顺序测试同时证明正常路径的前三个事件严格为 `history -> authorization -> prepare_snapshot`，两类负例均未调用 prepare。

`M9-SP-PY39-CONS-R03`：**CLOSED**。

## 既有 finding 回归检查

### R01：无回归

adapter 仍只接受唯一 `--consumer-operation-id <32-lowercase-hex>`，并且只删除 adapter 自有 flag 与其 value 两个 token。真实冻结 `m9_budget.build_parser()` 解析后保持 `overlap_operation=true`、`overlap_action=source_prepare`、`command=[]`；真实 `validate_overlap_request()` 返回 `("source_prepare", "overlap_build", 1073741824)`。source build、重复/非法 id、缺少布尔开关、自由 argv 与 delimiter 负例继续拒绝。

### R02：无回归

`verify_recovered_core()`、`prepare_snapshot_for_refresh()`、strict journal reader 和 phase/path/inode validator 保持分离。固定测试以真实 post-rename 窗口确认以下三态继续收敛：

- `STAGED` 且旧 active 已 rename 到 retired；
- `OLD_RETIRED` 且 staging 已 rename 到 replacement active；
- `SUCCESS_COMMITTED` 且 consumer gate 尚未写入。

同字节 inode replacement、非法 `PREPARED + retired`、字段/phase/path 漂移继续在新写入前拒绝。R03 guard 位于 `prepare_snapshot_for_refresh()` 外层，没有重建旧 gate，也没有破坏 journal 重入。

### B01、B04、B05、B06：无回归

- B01：common、合同、预算控制器与 source launcher 继续统一读取 `m9_overlap_py39_recovery_frozen_hashes.json`；真实 `verify_frozen_project_files()` 正例通过。
- B04：bootstrap/installer 继续以 `O_NOFOLLOW` 打开既存 lock，并核对固定 recovery receipt、transaction 字段闭集、post state/workflow/ledger、immutable pre-runtime、预算语义和产品缺席；R03 guard 恢复了 pristine snapshot 首写前的完整历史闭集与 authorization 缺席门控。
- B05：old/staging/retired/active gate receipt 继续继承 dev/ino，rename 使用 inode-preserving primitive，same-byte inode swap 负例通过。
- B06：所有必须缺席的 replacement、authorization 与 refresh namespace 继续使用 `lexists`；dangling symlink 零写拒绝测试通过。

未发现新增问题。

## 冻结闭集、测试与文档

两个 manifest 均由审计侧逐成员重新计算：

- overlap frozen manifest：16/16 匹配，SHA-256 `8a3166d61c4f777424f0509ae2d9aae3cc0a6c7f90a725fb9126f5cc25147e3a`；
- consumer frozen manifest：25/25 匹配，SHA-256 `765dcf5c09c90ae8d9c2789df1c16f379eca397f18d1dade55167c1b5df207e7`；
- `06_reproduction` 下 `__pycache__`/`.pyc` 数量为 0。

全部回归使用 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B`：

```text
test_m9_uid1000_consumer.py: Ran 23 tests in 8.384s — OK
test_m9_overlap_controls.py: Ran 110 tests in 31.836s — OK
```

工作包、`master_execution_plan.md`、`progress_tracker.md`、`decisions.md` 与本报告均通过 Pandoc `markdown+tex_math_single_backslash -> html5 --mathml --fail-if-warnings`。

## 正式 WSL 零写证据

正式运行态在测试与主动穿透后保持安装前状态：

- state SHA-256 `f51960808c7e0c518972cd717ae94fbc2a070be57638862c4b143970f3223e73`，仍为 `UNLIMITED`、非 hard-stop、active transaction 为空；
- workflow SHA-256 `384a4de85803666e305ca55b38dd6966c40244f789ac887a52b5a282095e2492`，仍为 `AUDIT_PASSED`、非 hard-stop、active transaction 为空；
- ledger 为 61,826 bytes，SHA-256 `5253620510f84d1987874c5fa571f6016cedfbdabc6e80a4b126e724839b1ea9`；历史用量与预算没有重置或增加；
- 历史失败 transaction SHA-256 `0a982e876e43768c6069fdeafd07e6e43ae03be3b1a0abc8584aa8d137bbcae7`；
- 旧 active gate 仍为 inode `2096:153476`，SHA-256 `78311a978c2472c85b35a745d80e1f33724c1500cf8d7bd244cdbe83c3fa3698`；
- 旧 consumer gate SHA-256 `2ba96b8566f2ba38a528e4002dbaa0bebf4f9a7b8c5f10a92b89d643d11a85f2`；旧 bootstrap receipt 与 snapshot manifest 分别保持 `3172bf9516fed5dd2abb3669c705211428cbe6ebeea34fe96fcb6a3016d5f1ba`、`2d13e0c1fb1c1e635ad1730f44f21901340e7483d06356aa8eeb0e07f83dcec9`；
- replacement bootstrap、replacement snapshot、replacement consumer gate、single-run authorization、refresh journal、retired gate、staging gate 七个 namespace 全部按 `lexists` 缺席。

## 许可边界

本次独立实施审计达到精确 `PASS / BLOCKING=0 / NON_BLOCKING=0`。允许后续机械 bootstrap/install；安装完成后仍须执行独立事实审计。该结论不允许创建 single-run authorization object，也不授权运行 `source_prepare`。
