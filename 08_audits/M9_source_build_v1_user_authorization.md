# M9 source_build v1 单次编译用户授权

日期：2026-08-30。任务：`019fc7b8-cd95-7d20-84d0-229e2a73749e`。

用户在“恢复前需批准：建立并独立审计编译门控，通过后执行一次冻结版本编译及构建自测，不含下载、结构计算或训练”之后明确回复“批准”。该批准解除的是本次编译门控建设与一次编译执行的授权阻塞，不改变完整 DeepH 学习路径，也不构成后续 smoke、batch、GPU或训练授权。

允许主 agent 实施版本化 `source_build` 消费门控、必要的合成测试和只读预检；独立子 agent 完成实施审计及安装事实审计。两者均为 `PASS/BLOCKING=0/NON_BLOCKING=0` 后，允许签发绑定当前状态的执行许可，并以真实 UID1000 执行一次冻结 `source_build`。任何拒绝、失败、超时或异常后均停止，保留现场，不自动重试。

编译对象及验收强度沿用冻结合同：HDF5 1.12.1 configure、make、make check、install；OpenMX 3.9加官方3.9.9补丁的构建和受控源码不变核验；仅应用已冻结 overlap-only 补丁的两个C文件，再构建overlap版本；核验产物允许清单、HDF5安装文件、动态链接依赖、日志及来源哈希。构建过程中必要的库自测不等同于材料结构smoke。

不允许下载、更换软件版本或材料体系、运行OpenMX材料结构、生成Hamiltonian/SCF/其他DFT标签、生成overlap数据、使用GPU或训练。现有源包、环境、失败目录、旧事务快照、授权与所有历史审计均保留；不覆盖旧gate/snapshot或旧冻结来源。

D-018无总墙钟期限保持生效，CPU/GPU/存储预算不重置或增加。本次使用原 `overlap_build` 子预算、GPU bucket=`none`、存储预测下限4294967296 bytes；所有即时预测仍应通过原预算控制器。已有非计算apt超时抵扣不得增加或重新解释。

固定 operation id 为 `72cefbe283654fd5b85fb2e66d9c2dfb`，nonce 为 `3bd3367fc192e9485bfa3c68679ab6636fb6af6d86e5f48bf848e96494c84f83`，scope 为 `ALLOW_ONE_SOURCE_BUILD_AFTER_PREPARED`。本记录、源码准备最终PASS及执行后证据、当前runtime、新snapshot、独立实施和安装结论共同绑定这一次动作。本记录冻结后不改写，执行结果另存。
