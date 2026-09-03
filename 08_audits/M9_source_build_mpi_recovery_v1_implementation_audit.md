# M9 OpenMPI修复与一次性恢复独立实施审计

审计日期：2026-08-31。结论：PASS；blocking=0，non_blocking=0。结论限定于精确版本化修复、真实只读工具链回归和pristine-only恢复实现，可进入主端机械零写预检及一次恢复；不表示正式恢复已执行，不授权重新编译。旧v2执行FAIL报告及全部旧证据保持原结论和SHA。

## 冻结输入与修复范围

独立逐项复核新9-file manifest及其原v2 consumer所绑定的旧12/25/16/10来源闭集，全部匹配。关键SHA如下。

| 输入 | SHA-256 |
| --- | --- |
| 新frozen manifest | `743e3e596d816a7c316a2f7c901b812c650f72bb926aa6698f3c7f72e40818bc` |
| recovery controller | `2df09743fbcab63824cec6d3768e10df3ace7b53af8167080c07a946f2927aa9` |
| read-only adapter | `e7b9f13ced60697e62417128c0145d98b9262b614671f4247bcbde19a1f6b027` |
| recovery tests | `44dc10b6e4c42e619973a151672d5e60e607c2cc3f3d004dd941b1c8d98854b4` |
| adapter tests | `6634185a53bc5f31a863ba97c0a745cea172d953d1b6bc761797a7c50f3b950c` |
| work package | `7dae7ae0061dd28a2146ecd0a51161f3ae6d01e8fb8e71724afeb48654a687c0` |
| user authorization | `5b62617dd9a236c062c1df6a95ccb245484634518d0fbfa029d82f1ca081ac83` |
| 169对象失败baseline | `e6f02744745837ae200998cf6d1e7701283721e8ed64c550e98d58b416f5f325` |

适配器从原build driver SHA `ab6632784a744fd3f66c95aac30a56767f67af3d8d81147df2fc0d72b67102ec`精确替换一处比较行。仅对固定OpenMPI分支，在命令路径和原合同完整字符串均符合时构造绝对路径前缀expected，其余版本检查和构建字节不变。反向替换恢复原始全部字节，AST仅verify_packages变化；派生SHA为 `5652ee35a3595f42bd3050e5825419175fc84526a421a0500559d4146f253d00`。

独立以真实UID1000和固定Python3.9.23 `-I -S -B`复现旧driver的同一B01，再验证派生driver的完整verify_packages通过，包含14包、gcc/gfortran、两个wrapper及9工具路径。错误MPI版本、程序名前缀、Language、额外文本、合同、路径和wrapper仍拒绝。只读CLI仅接受verify-toolchain；未安装capability时原build_sources守卫拒绝。此次修复通过不等于尚未执行的configure/make、构建自测或产物验收通过。

## 恢复权威、首写和写集合

恢复器仅允许固定五参数preflight/recover；严格九来源闭集、self SHA、历史baseline/失败报告/原consumer SHA及七字段独立PASS/整数零verdict都在加载消费逻辑前验证。原锁以O_NOFOLLOW和LOCK_NB打开，验证dev/ino及完整receipt；完整父态、四份raw runtime、两树、禁止对象缺席、原budget/launcher完整argv不存活、真实预算和UID工具链均须在首次mkdir前通过。首写前再次读取全部冻结输入与旧闭集；Guard每次操作前后验证完整formal namespace和锁FD/路径身份。

pristine-only条件明确：新private、public snapshot/staging和state/workflow固定tmp任一已存在即拒绝；不提供resume、permit、run、build入口。恢复目标从失败raw对象复制，仅修改工作包列明的hard-stop、阶段、恢复标记与时间字段，CPU/GPU、credits、预算策略及其他字段保持精确相等。失败transaction、consumed、FAIL receipt、旧snapshot/gate/permit及两树原位、原身份保留。

允许新建private目录及17个0600文件、public snapshot目录及5个0440文件，预计169增至193对象。目录分别root:root/0700和root:1000/0550。旧成员只有ledger、state、workflow及指定父目录允许变化。写入采用O_EXCL/O_NOFOLLOW、完整短写循环、fsync、固定tmp和原子替换，提交receipt与实际写FD的dev/ino绑定。ledger使用已绑定原inode，只追加一次固定事件，不截断、不重建；部分尾部保留且不自动补齐。

PREPARED、SNAPSHOT_COMMITTED、LEDGER_COMMITTED、STATE_COMMITTED、WORKFLOW_COMMITTED、SUCCESS_COMMITTED按固定顺序推进；每阶段journal记录四项post-runtime receipt，Guard继承先前已提交身份，不以同字节新inode重新绑定。UTC、event、目标bytes在首次写前生成一次。public snapshot封存后真实UID1000完整只读检查成功，才允许追加事件和解除hard-stop。

任何异常保留private、部分事件或tmp并退出；下一次因非pristine零写拒绝，不自动回滚或续提。若异常发生在state/workflow已解除硬停但SUCCESS_COMMITTED尚未持久化的窗口，不能宣布恢复成功，需另行独立复核和授权；布尔状态不是放行凭据。即使恢复成功，原transaction仍FAILED_COMMITTED且runtime已改变，旧v2 consumer/permit仍不可使用。

## 独立测试及安装路径边界

独立复跑adapter 9项与root恢复16项全部rc0，分别0.949秒和6.519秒。恢复测试包含29个持久文件窗口、目录/封存/追加/安装验证故障、部分ledger、短写、零写、残留tmp、额外对象、未知尾部、锁替换、同字节新inode、目标白名单、阶段错序和终态漂移；全部仅在临时隔离fixture中运行。

另做独立权威validator临时fixture：实际authority函数的有效七字段通过，boolean计数、错误schema、错误report_path、额外字段及FAIL状态均拒绝；没有调用恢复main/run。临时PASS对象仅用于验证器测试，不是正式授权。

另建root-owned五文件临时snapshot，由真实UID1000读取未修改adapter源码，仅将SNAPSHOT路径常量指向临时目录以测试已安装分支。完整工具链检查通过；临时原driver字节漂移、额外成员和adapter权限变化分别拒绝。该测试补足项目入口与snapshot来源选择的区别，但不是正式snapshot已安装事实；正式恢复后仍须从固定安装路径验证真实UID1000消费，不得以本fixture代替。

## 正式只读父态及预算

在原锁内用只读模块函数核验，并在真实项目适配器verify-toolchain后复读：正式169对象与失败baseline逐项全等，canonical SHA `417101edb36bd11ad652e18d5fd4f6b86f36844743d330970cc4a2d051497c7c`，formal_delta=[]；四份失败runtime原字节相同。ledger仍65261 bytes、SHA `50334d8f6748816da3910e13fb31e12f5c31dbb9048871b2493a17785802b706`，失败事务仍 `38a891fff6fd07675581b891766e02c6` / FAILED_COMMITTED，双HARD_STOP保留。

准备树和失败退休树各5319 receipts前后全等，canonical SHA分别为 `7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260`、`060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`。固定8项root-only及/root历史均由root实际读取，不以metadata-only代替。新private/snapshot/staging及其他禁止产品缺席。

原预算函数对1048576 bytes恢复预测只返回 `ledger_already_hard_stopped`，没有其他超限。CPU有效累计14.393832060000932秒，余额7185.606167939999秒；原始7214.469142588001秒及既有抵扣7200.075310528秒不变。采集时总apparent/allocated为31133155307/31458697216 bytes，overlap增量1263675576/1288876032 bytes，项目审计apparent/allocated为4066679/4472832 bytes，VHDX为28064088064 bytes。新增报告/snapshot仍计入预算，主端正式预检应重测，不沿用这些读数代替即时检查。

M9缓存扫描为0，未使用py_compile。工作包、授权记录及本报告Pandoc严格Markdown检查通过，git diff --check通过。本轮没有调用正式恢复main、run、preflight或recover，没有编译或运行态写入。

## 放行范围

此实施PASS仅允许主端使用既有精确single-FD loader，绑定本报告/verdict与新frozen SHA，先机械零写preflight，再recover一次。恢复后必须独立事实核验193对象写集合、原失败证据身份、唯一恢复事件、目标白名单、预算、两树、实际固定snapshot的UID1000只读消费和最终journal，方可报告恢复完成。

当前授权不包含重编译。未来新consumer/launcher应明确绑定派生driver及恢复事实，重新独立审计门控，并取得新的单次source_build授权；旧v2许可不得重放。M9-DATA-B01仍OPEN，材料结构、smoke/batch、GPU、训练及其他未授权动作保持禁止。
