# 第 14 章资料包：周期图、邻居表与截断半径

| 来源 | 定位 | 本章用途 | 边界 |
|---|---|---|---|
| D-PBC-01 | Xie 与 Grossman，正文 p. 2（期刊页 145301-2），Fig. 1(a) 前的 undirected multigraph 定义；补充材料“Construction of crystal graphs” | 周期材料需要表示重复晶胞与多重邻接 | 不采用其实现作为唯一算法或通用 cutoff |
| D-GNN-01 | Gilmer 等，第 2 节，PMLR pp. 1264—1265 | 周期边进入普通消息传递的通用接口 | 原文不定义晶格镜像枚举 |
| DH-01 | 补充材料 pp. 2—4 | 原子对、局域环境与矩阵块关系 | 不选择正式材料、训练数据或 DeepH 版本 |
| 阶段 B 统一约定 | `stageB_conventions.md` | 行晶格矩阵、周期索引与实空间表示 | 本章新增边实例而不改变阶段 B Fourier 约定 |

有限枚举界、逐原子换胞的镜像协变式和完整性测试为本项目直接推导。来源快照见 [阶段 D 来源目录](../../../01_sources/documentation/stageD/README.md)。
