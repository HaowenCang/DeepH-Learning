# 第 19 章来源与论断边界

## 直接来源

| 来源 ID | 本章用途 | 本地证据 |
|---|---|---|
| E-GNN-01 | 球谐滤波、CG 张量积与旋转/平移等变消息 | [TFN 快照](../../../01_sources/documentation/stageE/thomas_2018_tensor_field_networks.pdf) |
| E-GNN-02 | \(E(3)\) 表示型特征、tensor product、门控和网络构件 | [e3nn 论文快照](../../../01_sources/documentation/stageE/geiger_2022_e3nn.pdf) |
| DH-02 | DeepH-E3 的 Hamiltonian 表示任务和等变方法对象 | [DeepH-E3 论文快照](../../../01_sources/documentation/stageE/gong_2023_deeph_e3.pdf) |
| 阶段 B/D | 轨道块、周期图、完整边键、batch/mask 和 provenance | [阶段 D 门控包](../../../08_audits/M6_stageD_gate_packet.md) |

## 论断边界

本章以合成 \(s,p,d\) 表和合成图验证机制，不实现或安装 DeepH-E3/e3nn。DH-02 支持论文级 Hamiltonian 等变任务联系，不授权其仓库、数据、配置或 SOC 对象。局部坐标与显式等变的比较限于机制、条件和失败边界；现有证据不足以在未匹配数据、硬件、精度和实现的情况下宣称一种方案普遍更准确或更高效。

## 来源—论断定位

| 对象 | 来源 | 教材定位 | 推导/题解 | 边界 |
|---|---|---|---|---|
| 表示型消息、球谐 filter、CG 路径和门控 | E-GNN-01/E-GNN-02 | 19.1—19.3 | D-E06 第 2—3 节；A19-01—A19-03 | 支持一般机制，不证明未来实现正确 |
| Hamiltonian 轨道块双侧等变任务 | DH-02 与统一表示约定 | 19.4、19.8.1—19.8.2 | D-E05 第 4、6 节；A19-04—A19-06 | 论文级对象联系；固定 \(4\times8\) 数值是项目合成夹具 |
| 周期边、逆边 Hermiticity、batch/mask/provenance | 阶段 B/D 已审材料 | 19.5 | D-E05 第 5、7 节；A19-06/A19-07 | 几何/身份正确不自动证明标签物理正确 |
| 局部坐标、退化合同与显式等变比较 | E-GNN-02 与项目冻结约定 | 19.6 | D-E07 第 8 节；A19-08 | 阈值与夹具是教学冻结；不支持普遍优劣结论 |
| D-E05/T-E06 | 上述来源 | 19.4—19.5、19.8 | 推导第 4—6、10 节 | 双侧、实/复、逆边和完整身份均须实际测试 |
| D-E06/T-E08 | E-GNN-01/E-GNN-02 | 19.2—19.3 | 推导第 3、10 节 | 逐层和端到端证据不能由架构名替代 |
| D-E07/T-E09 | 项目统一约定 | 19.6 | 推导第 8、10 节 | 只在非退化定义域给出保证 |
| D-E09/T-E10/T-E12 | 项目教学构造与阶段 D schema | 19.7—19.8 | 推导第 7、9—10 节；A19-07/A19-09/A19-10 | 144 点、成本和失败矩阵已由 M7-09 正式执行；见 [代码说明](../../../05_code_exercises/stageE_synthetic_equivariance/README.md) 与 [定点复核](../../../08_audits/M7_stageE_code_blocking_reaudit.md) |

## 复现与授权边界

本章仅需固定 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0 复算合成矩阵，不需要新增依赖。所有真实软件、数据、材料、DFT 和训练选择继续保留到 M8/M9 双授权。
