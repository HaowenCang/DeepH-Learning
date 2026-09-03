# M9 source_build WSL shutdown recovery v2 独立定点复核

日期：2026-09-03。审计角色：独立子 agent。最终判定为 **PASS / BLOCKING=0 / NON_BLOCKING=0**。本复核只审查首轮 `FAIL/BLOCKING=2/NON_BLOCKING=1` 后的冻结修订，不覆盖或改写首轮报告与 verdict；未调用正式 `preflight`、`recover`、permit、capability、launcher 或构建入口，也未修改正式 WSL runtime、树、日志、gate 或 permit。

## 冻结对象与历史保持

修订控制器、测试、工作包和十二项 frozen manifest 的实际 SHA-256 分别为 `21cf81c6a63218a6e1de23bf14e2e9d928eb413fd5529a2d18d0b8859d3a1801`、`59226de82a9d87ac007315e04131bb6e5490e5edb115c83f028a684ec593d993`、`23a3df56569a6ce2197be927878e0b3a46cf9df172f67e7078b416864dacf318` 和 `139fb44a695873f1771fa05bd15bc28a9ac348ee2f6fc8a567080c7e920b1e62`，均与送审值一致。首轮 FAIL 报告和 verdict 仍分别为 `3d4d8c1316d0b76404b032393d2cc8dfc8213fe590a566b6c4184b01f37a886e` 与 `bae4b15404359c7e558650b4a73adb8c59e0c4cc0077c510853b1e27e0fd300b`，原字节未变。

## 首轮发现关闭情况

### B01：已关闭

进程封印现遍历可替换的 `/proc` 根，并对每个非空用户进程读取 NUL cmdline、cwd 与 executable。检测范围包括 capability 中的完整 consumer/launcher argv、包含固定 BUILD、LOGS、transaction、capability 或已安装 v4 consumer/launcher 锚点的 wrapper，以及 cwd/executable 位于 BUILD/LOGS 的 configure、make/gmake、编译器、链接器、HDF5、MPI wrapper 和 OpenMX 进程。cmdline、cwd 或 executable 出现 `PermissionError` 时均 fail-closed；仅已消失的进程按进程竞态跳过。

隔离回归真实构造了 wrapper、孤立 `make`、孤立 gcc 和无关目录中的 `make`，前三者被拒绝、无关进程不误拒。独立补充负例确认 cwd 与 executable 任一不可读时分别得到 `cannot prove process unrelated`。关键两 seal 测试在第一次 seal 后加入 cwd 位于 BUILD 的孤立 `make`，第二次首写前复核拒绝，PRIVATE、ARCHIVE 和 ledger 均保持零写。由此关闭 `M9-WSL-REC-V2-B01`。

### B02：已关闭

修订 authority 不再作含糊的一层历史递归。十二项直接恢复来源形成精确执行依赖闭集，其中当前 `BUDGET` SHA-256 为 `a94902a942f98217171be5d9967f469a4dd4563c80e6e6ef3d68e6cede71168d`，`RECEIPTS` SHA-256 为 `c2c235c444bae0f613078a060efa9733f869533385fa84268bfd2cc2b3c3ef55`；二者都从 single-FD 已固定原字节编译加载，不回退读取同名项目文件。v4 manifest 本身及其 22 个直接成员逐项 pin，旧 manifest 的二层叶仅作为历史摘要声明，不作为恢复执行依赖。

独立 trace 得到预期和实际 pin 集均为 35 个唯一对象，missing 与 unexpected 均为空；两次重复 pin 仅来自 D-019 和 RECEIPTS 同时属于恢复直接来源与 v4 直接成员。临时历史 manifest 负例证明其自身字节必须匹配，而其中故意漂移的可变历史叶不会被伪称为当前执行依赖。工作包明确保留三个不可重建旧治理文档版本的证据边界，不以当前同名文件替代。由此关闭 `M9-WSL-REC-V2-B02`。

### N01：已关闭

`formal_roots()` 现完全由可替换的 `ROOT` 与 `PRIVATE.parent` 派生；Fixture 同时替换 ROOT、PRIVATE、PROC 和测试身份，不再引用正式 `/root/deeph-m9-control`。固定 Python 3.9.23 `-I -S -B` 下，同一 21 项套件以 root 运行 21/21 OK，以真实 UID1000 `evan-williams` 运行亦为 21/21 OK。Fixture-local roots 断言和 UID1000 成功共同证明首轮正式 root-private 依赖已消除。由此关闭 `M9-WSL-REC-V2-N01`。

## 正式现场只读复核

采用固定 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B`，以 root 对修订控制器的 `verify_current` 做两次连续、非 action 的只读等价核验。两次 seal 完全相等：正式 namespace 为 275 项、canonical SHA-256 `8f904289db590a6bf68d7d62f0e13cda0893cec30321274d67559261758402b9`；BUILD 为 7,621 项、`25fa00697f192967f8adcc0656eea976eeb9839390a78757a04d00ac66796dc0`；日志为 4 项、`f1d69a2016dc0ae5df54519d4155a9b0317bcb7c4edf55cdea85c43d9a4b1db3`；clean 为 5,319 项、`060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`；旧 BUILD 归档为 7,640 项、`82bc6705ef8a507d2580630592f4903726622768aebb5bd7b1d22d93afa12515`；旧日志归档为 4 项、`5ea65a500eaadc665b4d282ce8b8c55019629b722020b7baa73259c9f862d4de`。

四份 runtime 原字节 SHA-256 分别为 state `b067c25dd9144fb7f40994b196b60a1f0cd4a22c4d72d558388f54ce5aa1259e`、workflow `deb554bc2df789ae56341f44045f861d026f1937375a6251ccc8871b8e6f1fe6`、transaction `d953bfb4c21e9dffdf945f7b5a7a610321d19a1a659e5f6d908185fab5f555db` 和 ledger `f3f44ee5169bbeb44d175ff0aa381cda70684ad66f11ce57725c2e774471d4c7`。capability 仍为已消费对象 `8d6aff34eec0ee29ce8a7b8e6a8fdf8a76b78ec1fe5a5bd584ee1e2587607204`，launcher receipt 缺席；v4 gate 与 permit 分别保持 `dcd0a0ed3307add49df5b7586ba0bf01b2fc55b0469a42067893e563ba2ff3c1` 和 `c3aae6ff0c5aaffb3d5a711b48e7dc505061959eb144509995f8e9890f5853d4`。当前未发现关联构建进程，1 GiB forecast 的 `violations=[]`；目标计量仍精确从 `7507.245045788001` 增至 `7645.646848354001`，保留既有抵扣、GPU 和历史，且 `source_build_authorized=false`。所有 recovery PRIVATE、SNAPSHOT、ARCHIVE、LOG_ARCHIVE、STAGING 目标均缺席。

真实 UID1000 从已安装 v4 snapshot 只读调用 `verify-execution`，退出 1，并以 `build historical namespace closure mismatch` 拒绝旧权限重放。调用后 275 namespace、四份 runtime、consumed capability、v4 gate 和旧 permit 的摘要均与调用前一致。因此，旧 v4 permit 与 capability 不能作为恢复后或当前状态下的新构建权限。

## 判定与边界

静态复核及 21 项双 UID 测试还确认：原锁内首写前完整二次 seal、138.401802566 秒保守计费、FAILED_COMMITTED/SOURCES_PREPARED 目标、ledger 原 inode 单行追加、原子归档、无硬链接 clone、普通文件与全部目录 fsync、九阶段 journal、pristine-only/no-resume、任一故障保留证据，以及禁止生成新 permit/build 的语义保持成立。`06_reproduction` 下 cache 对象为 0。

本复核仅证明修订实现满足执行恢复前技术门控，不证明 recovery 已执行，不授权重放 v4 构建，也不证明 OpenMX 构建通过。正式机械 preflight 和唯一 recover 仍须由主流程在本报告及严格 final verdict 固定后按既定 loader 执行，并在执行后接受独立事实审计。最终判定为 **PASS / BLOCKING=0 / NON_BLOCKING=0**。
