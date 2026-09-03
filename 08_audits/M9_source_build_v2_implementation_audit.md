# M9 source_build v2 独立实施审计

审计日期：2026-08-31。结论：PASS；blocking=0，non_blocking=0。独立审计员仅审阅、复验与新增本报告及配套verdict，未修改受审实现、冻结来源或正式运行态。

本结论仅证明本次v2实施满足进入机械预检与安装的条件，不是安装事实通过、执行许可或构建成功。v1安装的FAIL/1/0及其历史证据保持原结论；v2修正其权限分层机制，未放宽任何旧文件权限。

## 受审闭集与权限修复

新12-file frozen manifest SHA为 `bc80d1d939527818c7eec747a60cd17c6000f9015374ff33192f34c2f3ae7614`。已逐项重新计算12个成员，以及其绑定的旧25-file consumer、16-file overlap、10-file build-v1闭集，全部匹配。关键输入如下。

| 输入 | SHA-256 |
| --- | --- |
| v2 consumer | `1b425c04d98549a7a9a5ea502411379e36bee3968a0eec66f205796a222e36e4` |
| v2 installer | `fd6ceb70241053d1c07b7e895ab977941a3831d1c508a83835bf8a9a950c6453` |
| v2 tests | `eea395e5d5fdc4a7393aa0275aad17bc88ea9bf04a53f2373958099d2dad9b8b` |
| v2 work package | `b7cfa5adae5910662e1b76007984a9d965475229641d4540aa799ee6fc422d14` |
| v2 user authorization | `fc3031ea4c14d37c219002ea3eb534d80a39829c7b8243472acbcc68d1012e24` |
| v1安装后完整baseline | `0e125e288af8299fb3cf6447ac379e3b946bd042ddd705537dcd9cff11300f00` |

root私有验证路径对147对象、固定8项root:root/0600历史文件及`/root/deeph-m9-control`实际读取内容并计算哈希，不使用metadata-only替代。UID1000公共路径仅对`ROOT_ONLY_NAMES`明确列出的8个绝对路径采用两次lstat并核对类型、dev/ino、uid/gid/mode、nlink、大小和mtime/ctime；其他公共文件实际读取并哈希。没有动态权限筛选，也没有捕获未知PermissionError后跳过的分支。

`history_attestation_sha256`绑定baseline文件SHA、这8项完整receipt及/root历史集合，并经新snapshot/readiness绑定。UID1000对8项证明的是当前元数据与root封存receipt一致，不能表述为UID1000重新读取了其内容；内容证明依赖root安装与permit阶段的实际全量读取。root仍是既定信任根，本机制不声称抵御恶意root。正式现场所得attestation SHA为 `58deab7698c64d446f07a72ed744404f0fcc443370a1e14829267ab99012825a`。

## 安装、许可与单次动作隔离

新snapshot/gate/permit使用独立v2路径、schema、operation `a237ec1f2b404d898840c643e9ae501b`和nonce，保留v1 snapshot/gate及全部历史。snapshot严格17个普通单链接文件，目录root:1000/0550、文件0440；gate/permit为root:1000/0640。安装只接受pristine状态，不删除、续提或覆盖半安装；旧v1 permit及其tmp也必须缺席。预期安装新增19对象至166，permit另增1至167，仅允许规定父目录元数据变化。

实施PASS不能直接签发permit。permit要求新版本独立安装PASS并绑定安装报告/verdict、gate、operation与nonce；运行态漂移拒绝重放。完整argv仅允许工作包中固定source_build命令，不接受重复、缩写、附加参数、自由命令、结构id或其他动作。入口锁、原控制器锁及首次atomic_json前均重验；未完成事务进入原hard_stop_both的首写路径也不能绕过门控。

原budget SHA `a94902a942f98217171be5d9967f469a4dd4563c80e6e6ef3d68e6cede71168d`，派生SHA `94050d73f498b84ab0054f64f1b04ea8667067f86a54ed3f352e6b926a9e691e`，与v1相同。独立复核替换仅命中连续两行scope/action一次，反向字节恢复原文件；AST仅`command_overlap_run`变化。原事务、capability、launcher、CPU/GPU/存储计量、超时及失败停机逻辑保留。原编译链仍包括HDF5 make check、两次OpenMX构建、两处C文件补丁限制、产物允许清单和动态链接来源验证；本轮未运行该链。

## 独立测试与真实UID验证

全部测试使用WSL Ubuntu-22.04固定解释器 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B`。v2 40项、v1 32项、overlap 110项、UID1000 consumer 23项、completion 13项，共218项，全部rc0。

临时fixture验证实际8项root-only权限布局、真实UID1000安装入口verify-ready、缺permit明确拒绝及有permit通过、每项内容漂移、权限/链接/新inode漂移、未知不可读文件拒绝、root实际读取与UID替代隔离、attestation及旧v1权威拒绝。原真实未完成事务测试保留native hard_stop_both，另FD非阻塞锁竞争确认持锁，底层atomic及Popen不可到达。临时fixture中的安装及许可结果不作为正式部署成功证据。

正式只读probe在原budget.lock内，以root完成全量验证，并启动真实uid=gid=1000子进程，从已核SHA的项目v2源码仅调用`runtime_and_history(installed=False, private=False)`。观测包装器委托原函数实际执行：公共内容读取/哈希116文件，metadata-only恰为固定8项，无/root内容读取；结果PUBLIC_HISTORY_PASS，runtime canonical SHA与root一致。该结果验证真实现场的公共权限路径，不等同于尚不存在的正式v2安装入口verify-ready通过。

## 正式现场零写证据与预算

正式probe前后，controls、manifests及/root控制树147对象与已封存v1安装后baseline逐项全等，formal_delta=[]；准备树与失败退休树各5319 receipts前后全等。state/workflow/transaction/ledger四项原始字节还与baseline内保存字节逐项比较一致。D-017/D-018、旧失败/恢复、source_prepare成功及v1失败证据均在这些已核闭集中保留。

| 对象 | 数量或字节 | SHA-256 |
| --- | --- | --- |
| 正式namespace canonical | 147对象 | `78003a0d58a321e5e2a57bf76b1fd2106bed92d894433a43bfbb6f45943a150e` |
| 准备树canonical | 5319 receipts | `7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260` |
| 失败退休树canonical | 5319 receipts | `060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359` |
| runtime canonical | 5绑定项 | `e066af35757b5610dbeac189ad36a4cf6a9e1b0f89014e24f4bc573b0a655a29` |
| budget_state | 2202 bytes | `3c57eca541fde4f9d939766940459dac7ac7058a3af899ed79154d1cf852eb3e` |
| workflow | 816 bytes | `22cd75911994b708c19d1b7bfb1da84f264513dea59a9bd795a52e44933b0d32` |
| transaction | 2136 bytes | `2efb2729126903a1cd0d2f200565a225850e2fd3a0d10256f970b208318a75d6` |
| ledger | 64298 bytes | `0be27e9220b6597d47ee657bbe5169134118340c77a7a0af3722a4eb1ad885c2` |

原锁dev/ino=2096:50700，uid/gid=1000、mode0644、nlink1、空文件，身份保持。workflow仍SOURCES_PREPARED，事务`dc75dda112af553377a697f629801782`仍为source_prepare/SUCCESS_COMMITTED，无active transaction或hard stop。新v2 snapshot/staging/gate/permit/tmp及旧v1 permit均缺席。

原预算函数对4294967296 bytes预测返回violations=[]。overlap_build原始累计7212.901214103001秒、既有抵扣7200.075310528秒、有效12.825903575000666秒、剩余7187.174096424999秒，均未重置。GPU compatibility累计54.84820560599999秒，training和physical_validation均0。

probe时总apparent/allocated分别31131441821/31456890880 bytes，overlap增量1261962090/1287069696 bytes；VHDX 28064088064 bytes，自起始及overlap基线增长分别26575110144/1644167168 bytes；项目审计apparent/allocated为3428480/3792896 bytes。新增报告和后续snapshot仍计入存储，当前通过不能替代之后的即时预算检查。

## 最终边界

本轮未调用正式installer的preflight/install/permit动作，未调用consumer main/run，未启动构建、下载、结构计算或训练。正式运行态零写；M9缓存扫描为0，未使用py_compile。受审工作包、授权记录及本报告通过Pandoc严格Markdown检查，git diff --check通过。

本实施PASS允许主端按冻结single-FD loader与最终报告/verdict SHA执行零写预检，再机械安装一次。随后仍须独立安装事实审计，证明真实UID1000从root-owned已安装v2 snapshot的verify-ready通过、verify-execution因缺permit明确拒绝且零写；再签发及独立核验permit，才能执行已批准的唯一冻结编译自测。构建即使通过也不关闭M9-DATA-B01，不放行后续材料结构、smoke/batch、训练或其他未授权动作。
