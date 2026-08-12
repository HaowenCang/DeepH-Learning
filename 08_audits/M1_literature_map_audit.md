# M1 文献地图审计记录

## 审计结论

结论为 **有条件通过**。当前资料足以支持教材第 1 章“DeepH 所求解的问题”的三级提纲和概念性正文，也足以建立方法谱系与版本分流；但不足以冻结复现实验，因为多个现代方法尚未定位到可独立获取的代码或权重，现代 DeepH-pack 的实际软件获取方式也需要在实践前确认。

## 覆盖范围

- 核心方法论文：DeepH、DeepH-E3、xDeepH、DeepH-DFPT、DeepH-2、DeepH-hybrid、HPRO、DeepH-UMM、DeepH-Zero/neural-network DFT、DeepH-R。
- 软件对象：旧版 `mzjb/DeepH-pack`、DeepH-E3、现代 DeepH-pack、DeepH-dock、HPRO。
- 外部对照：SchNOrb、QHNet、HamGNN、DeePTB、Uni-HamGNN。
- 台账结果：17 条结构化来源记录、16 条 BibTeX 记录、12 条关键论断登记。

## 已执行检查

- [x] 关键论文题名、作者、年份、期刊、DOI 或 arXiv 编号由期刊、arXiv 或官方仓库核验。
- [x] 同行评议论文、预印本、官方软件资料和代码仓库已区分。
- [x] 旧版 PyTorch/INI/legacy 数据与现代 JAX/Flax/TOML/新数据布局已分开登记。
- [x] “DeepH-Zero”项目标签与同行评议论文实际题名已建立对应，不把它们列成两项方法。
- [x] DeepH-R 和 2026 年现代 DeepH-pack 已纳入，不沿用过时的“最新版本”判断。
- [x] 相关 Hamiltonian 预测方法与经典动力系统意义下的 Hamiltonian neural network 已在任务定义上区分。
- [x] CSV 列数、ID 唯一性、BibTeX 键唯一性与花括号平衡通过自动检查。
- [x] 来源地图 ID 与 CSV ID 一一对应。

## 未解决问题

| 问题 | 状态 | 是否阻塞下一步教材提纲 | 是否阻塞复现 |
|---|---|---|---|
| DeepH-2 尚未定位独立公开代码仓库，且当前登记为预印本 | `UNVERIFIED` | 否；提纲中保留证据层级 | 是，若选择其作为基线 |
| DeepH-DFPT 尚未定位独立官方代码仓库 | `UNVERIFIED` | 否 | 是，若复现 DFPT 分支 |
| DeepH-UMM 对应权重与独立实现尚未定位 | `UNVERIFIED` | 否 | 是，若复现通用模型 |
| AI2DFT/DeepH-Zero 公开代码尚未定位 | `UNVERIFIED` | 否 | 是，若复现变分无监督方法 |
| DeepH-R 刚于 2026 年 7 月发表，代码与复现路径尚未定位 | `UNVERIFIED` | 否 | 是，若选择其实践路线 |
| 现代 DeepH-pack 官方页面要求申请获取实际软件，未定位公开主源码仓库 | `PARTIAL` | 否 | 是；需先确认可获取性和许可证 |
| 当前现代接口列表没有直接支持 VASP Hamiltonian 转换的充分证据 | `UNVERIFIED` | 否 | 是，若采用 VASP 路线 |

## 允许带入 M2 的边界

教材第 1 章可以使用 DH-01、DH-02、SW-01 与 DH-10 建立“为何预测 Hamiltonian、表示依赖、方法演化与当前边界”的框架。具体软件命令、配置字段、训练数据格式和性能数字不进入该章正文；这些内容应等到代码与版本审计完成后再写。任何跨论文的性能比较必须同时列出数据、标签、划分、硬件与评价口径，否则只作定性说明。

