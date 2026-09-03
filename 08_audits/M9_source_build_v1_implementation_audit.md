# M9 source_build v1 独立实施审计

审计日期：2026-08-30  
结论：**PASS / BLOCKING=0 / NON_BLOCKING=0**  
审计对象：`m9-source-build-frozen-v1` 的10文件闭集  
冻结manifest SHA-256：`b3a344e00d3cac19edcf23c69a2631307d6e08714c3a85c85eca8572f2496641`

## 结论及权限边界

本次版本化source_build门控实施通过独立代码审查、178项独立回归及正式环境只读前置核验。证据支持按已冻结single-FD loader进行零写preflight及新snapshot/readiness安装；本报告不是安装执行事实审计，不证明正式snapshot已经安装，也不允许跳过安装事实审计直接签发执行许可或编译。

用户批准记录只授权建立并独立审计编译门控，通过后执行一次冻结版本编译及构建自测。安装事实还须另有PASS/0/0报告及严格verdict，随后才可机械签发绑定该事实和readiness gate的permit；真实UID1000执行验证通过后，主agent才可调用唯一source_build命令一次。任何拒绝、失败、超时或异常后停止，不能自动重试或重置预算。

本次范围不包含下载、材料结构计算、overlap数据生成、smoke、batch、GPU、训练或DFT标签生成。HDF5库自测和OpenMX编译链接不构成材料结构smoke。`M9-DATA-B01` 仍为OPEN，source_build成功也不会自动关闭该问题。

## 冻结输入与独立性

审计员仅新增本报告和对应实施verdict，未修改受审实现、测试、工作包、授权或旧冻结成员。主实施者的测试结果不作为独立通过的替代依据；下列测试均由本审计重新执行。

| 输入 | SHA-256 |
| --- | --- |
| consumer | 2dc69a146221016136862e84227222424bca8552a2590020f06a155b775931b9 |
| installer | f6c0f0e1edfa1aa6167ffa540e90c98b7378bb60d79567597f93cdc3c5c18cf5 |
| 新增测试 | 4b3ed95623ff3af62a6c6c34161eca87811e1eee78f880181f58d6478215798a |
| 工作包 | a930498f59cbd35e98552caf4c55f39f8ed3f919d211a9869687b18bc3742ca9 |
| 用户批准记录 | d0582a1b2a581ddd990f1114e8742f70e3b0afee2fa57b6a5142c859f3db9d1b |
| source_prepare最终事实审计 | 89418b784d800e25d895b05360ecd086be217e5a820dcdca526ef0205b1cde71 |
| source_prepare完整post evidence | ee4d593ddb277a252cbd3a90b0e59f94b96fc1d614e2544dde22bb5b217f8455 |
| 固定receipt工具 | c2c235c444bae0f613078a060efa9733f869533385fa84268bfd2cc2b3c3ef55 |
| 旧25-file consumer manifest | 765dcf5c09c90ae8d9c2789df1c16f379eca397f18d1dade55167c1b5df207e7 |
| 旧16-file overlap manifest | 8a3166d61c4f777424f0509ae2d9aae3cc0a6c7f90a725fb9126f5cc25147e3a |

新manifest的schema及文件路径集合严格验证为10项；两个旧manifest的全部25及16成员重新逐文件SHA核验通过。主计划、进度台账、decisions和旧控制代码均保持冻结字节。README和当前状态补充不在这些冻结闭集中。

## 精确派生与原launcher兼容性

原root-owned v2预算文件SHA为 `a94902a942f98217171be5d9967f469a4dd4563c80e6e6ef3d68e6cede71168d`。实际读取其字节后，独立确认指定OLD_BLOCK恰出现一次，替换结果SHA为 `94050d73f498b84ab0054f64f1b04ea8667067f86a54ed3f352e6b926a9e691e`；反向替换与原字节全等。独立AST比较仅发现 `command_overlap_run` 改变，对应D-018判断中的scope和action两行，没有其他顶层函数变化。

新scope为 `ALLOW_ONE_SOURCE_BUILD_AFTER_PREPARED`，唯一action为 `source_build`。原CPU/GPU/存储限制、抵扣历史、超时、事务、hard-stop、capability和launcher receipt处理未改写。原预算parser实际解析新adapter剥离专用operation参数后的argv，得到 `command=[]`，原 `validate_overlap_request()` 实际返回 `source_build/overlap_build/4294967296`。

原launcher核验capability中的budget_pid/child_pid、实际父进程 `/proc` 完整argv、launcherargv及原冻结来源，而非硬编码旧预算入口路径；新adapter没有改变实际进程argv，原预算仍从 `/proc` 取得它用于capability绑定。因此此次仅派生scope/action与现有launcher机制兼容。此判断依据真实源码、实际parser/validator及旧launcher回归，不冒充本轮已经正式启动构建子进程。

正式构建继续通过旧16-file source-only launcher载入原build/common，不向原scripts目录添加文件；正式控制目录实际闭集检查通过。snapshot内派生budget及receipt工具从核验后的字节compile/exec，不查询项目字节码。

## 首次写入前验证与单次执行

新consumer逐token接受唯一RUN_ARGV，拒绝重复参数、缩写、自由argv、结构id、额外cwd/log、旧source_prepare及其他动作。operation为 `72cefbe283654fd5b85fb2e66d9c2dfb`，nonce为 `3bd3367fc192e9485bfa3c68679ab6636fb6af6d86e5f48bf848e96494c84f83`；固定Python3.9.23、`-I -S -B`、真实UID1000及安装路径均有守卫。

gate、snapshot、冻结来源、授权记录、runtime、完整准备树和退休树均验证。readiness与permit采用不同schema和固定路径；permit绑定gate SHA、operation/nonce、独立安装报告与verdict。verdict字段闭集固定为7项，问题数要求真实整数0，不接受bool等值替代。

入口以O_NOFOLLOW打开原budget.lock并验证 `2096:50700` 身份；原预算重新进入同一锁后，D-018代理及首次atomic_json守卫重新执行完整验证。首次写入成功后不再拿旧preexecution runtime阻断该事务内部的正常状态推进；成功或失败已经改变runtime，因此旧许可不能再次进入相同动作。

新增真实未完成事务用例从临时JSON进入派生 `command_overlap_run -> hard_stop_both -> guarded_atomic`，未mock掉hard_stop_both或真实verifier。独立第二FD申请LOCK_NB失败，证明检查位于实际排他锁中；底层atomic及Popen均不可到达，临时正式树前后全等。这覆盖了原D-018检查之前可能写失败事务的分支，而非只依赖直接调用guard的单元测试。

完整源码检查位于所有首次预算状态写入之前，补足冻结build_sources先写HDF5、后检查official manifest的顺序风险。检查不是只核对official manifest的1577个OpenMX文件，还覆盖HDF5源码/configure、全部目录、额外成员、inode、权限、大小及时间戳。禁止预存HDF5 prefix、build/overlap manifest、构建日志、结构run root和活动staging。

## 安装与许可分离

root installer先核验精确self/consumer/frozen/verdict/report哈希，再加载consumer；在原budget.lock内检查包括root-private证据的正式闭集、两棵树、原预算及4 GiB预测。首次staging写入前再次验证历史和准备树。新snapshot root:1000/0550，成员root:1000/0440且单链接；readiness/permit为root:1000/0640。

实际snapshot目录成员须与manifest集合相等，14个封存成员另加snapshot_manifest.json共15项；成员包含10个冻结输入、新frozen、实施report/verdict及派生budget。拒绝额外文件、symlink/hardlink、错误权限及字节变化。安装后的旧父目录只允许预定metadata变化和controls增加一个子目录造成的nlink增量；旧对象字节及身份不变。

installer采用pristine-only策略；snapshot/staging/gate/permit或固定tmp预存即停止。合成机械安装使用真实new_file、rename、fsync、原atomic_owned_durable_bytes、snapshot验证和命名空间比较；正式预算预检及root-private路径仅在临时夹具中替代。该测试证明代码路径，不代表正式部署事实。安装后permit缺席，verify-execution拒绝；中断保留staging且重入零写拒绝；缺少独立安装事实不能签发permit；签发后再次调用被拒绝。

安装、permit均不调用adapter动作或启动构建。旧gate/snapshot/授权不覆盖、不删除，半安装不自动恢复；主agent必须先审计失败现场再提出任何恢复方案。

## 独立测试与正式只读核验

四组测试分别以WSL Ubuntu-22.04、root、固定 `/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B` 执行：新增source_build 32项、原overlap 110项、原consumer 23项、原completion 13项，均rc0。共178项。新增测试内还通过runuser以真实evan-williams UID1000对完整临时fixture调用真实verifier，结果PASS。

测试中的installed/permit/preflight输出均为临时目录结果，不能用其gate SHA证明正式安装。本轮正式snapshot、staging、readiness、permit及其tmp全部缺席；尚不能运行“已安装正式consumer”的UID1000验证，该验证属于之后的安装事实阶段。

另以固定解释器和真实root在原budget.lock内，直接进行只读来源验证、完整对象采集、预算parser/validator和预算检查；未调用consumer.main、installer install/permit、预算run或任何构建动作。采集与复读得到：

| 正式证据集合 | 数量 | canonical SHA-256 |
| --- | --- | --- |
| manifests、controls及root-private历史 | 130对象：121文件、9目录 | af17d9e05e68c30d928db3c587d58dfd80e0c69cfbc99544fa6d8edd09dc3ed9 |
| 完整已准备源码树 | 5319对象：5179文件、140目录 | 7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260 |
| 原失败退休树 | 5319对象：5179文件、140目录 | 060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359 |

130项与已封存post evidence逐项全等；两棵树前后完整receipt全等。此处退休树SHA是完整filesystem receipt口径，与较早只记录内容/分配字节的inventory SHA不是同一对象，不混用。root-private失败快照、D-017/D-018、旧snapshot/gate/refresh、旧capability及当前成功事务均在不变闭集中。

当前runtime五项canonical SHA为 `e066af35757b5610dbeac189ad36a4cf6a9e1b0f89014e24f4bc573b0a655a29`。workflow仍为SOURCES_PREPARED，当前事务仍为 `dc75dda112af553377a697f629801782/SUCCESS_COMMITTED/source_prepare`，双方无hard-stop及active transaction。ledger仍为64298 bytes，SHA `0be27e9220b6597d47ee657bbe5169134118340c77a7a0af3722a4eb1ad885c2`，未追加事件。

原始overlap_build CPU累计仍为7212.901214103001秒，有效累计12.825903575000666秒，剩余7187.174096424999秒。既有抵扣及历史字段随state全字节绑定保持不变；GPU compatibility仍为54.84820560599999秒，training/physical_validation均为0。D-018总墙钟UNLIMITED不改变任何其他额度。

本轮只读存储快照：combined apparent/allocated为31130105264/31455502336 bytes，overlap增量为1260625533/1285681152 bytes，VHDX overlap增量1644167168 bytes。原预算 `violations(state, 4294967296)` 返回空列表。审计文件增长和VHDX延迟增长使即时数值可能变化，安装及执行前仍须即时复验，不能用本快照增加预算。

## 最终机械检查与交接

新工作包、授权记录及本报告使用Pandoc严格检查；JSON字段和SHA绑定按consumer的严格verdict验证；`git diff --check`通过。M9源码及controls缓存数为0，未运行py_compile。正式环境未执行安装、许可、编译或其他动作；仅有允许的读取及锁操作，receipt口径不包括读取可变的atime。

本报告/verdict完成并冻结SHA后，正式installer的action=preflight只能通过旧替代工作包的single-FD loader运行。该工作包SHA为 `dc1d0d992f7e1328f79a4436eb4535b79ba2ab48fcee1b44fa498c31c30e91a2`；preflight回执应另外保留，不能为补充其结果回改已绑定报告。preflight若失败，不能据本报告继续安装，应保留现场并返回独立复核。

实施剩余问题数为0。后续仍有明确阶段门：机械preflight及安装、独立安装事实PASS、机械permit、真实UID1000验证、唯一source_build、独立构建事实审计。当前PASS不跳过其中任何一项，也不放行后续科学计算。
