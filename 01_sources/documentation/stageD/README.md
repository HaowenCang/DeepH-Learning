# 阶段 D 本地来源快照

本目录保存阶段 D 的直接来源快照。它们只服务于监督学习、普通 MPNN、集合聚合和周期晶体图的教材建设，不是正式训练数据，也不构成对 M8 实践对象的选择。

| 文件 | 来源 ID | 用途 | SHA-256 |
|---|---|---|---|
| `goodfellow_ch05_machine_learning.html` | D-FND-01 | 监督学习、泛化、数据划分与评价 | `68FC979F3D654EEE97117BF3754BA3462D3E66FD2A9B31CCADC5F70422BC0968` |
| `goodfellow_ch08_optimization.html` | D-FND-02 | 梯度训练、优化与诊断 | `95F2810D0AB10E3934AD7DD858E816572B6A30893E7FCA19163B211F6DFE91A1` |
| `gilmer_2017_mpnn.pdf` | D-GNN-01 | MPNN 的消息、更新与读出框架 | `292E7AD701D545DADDDA470AC02C2D076F1B23D85D95589F31E6EE9EB6A9FDD8` |
| `zaheer_2017_deep_sets.pdf` | D-GNN-02 | 集合函数与求和聚合的置换不变性 | `AE1E9A4655B8ADA5292B3DD3558DD7E18B05913106EBC36BF9F609C917F163C0` |
| `xie_grossman_2018_cgcnn_arxiv.pdf` | D-PBC-01 | 周期晶体多重图与邻居边接口 | `E9B5693D1A5B4DAA25F7BF61C8F97D5F55657669581A8208E2E8637B226D0970` |

访问日期为 2026-08-04。书籍章节为作者维护的官方 HTML，论文为 PMLR、NeurIPS Proceedings 或 arXiv 的固定 PDF。完整书目信息、适用范围和禁止外推项见 [中央来源台账](../../../02_source_ledger/source_table.csv)。

来源 ID 与 BibTeX 键的显式映射为：D-FND-01 → `goodfellow2016chapter5`，D-FND-02 → `goodfellow2016chapter8`，D-GNN-01 → `gilmer2017mpnn`，D-GNN-02 → `zaheer2017deepsets`，D-PBC-01 → `xie2018cgcnn`。两个 Goodfellow 章节来自同一专著，但使用不同章节级条目和固定 URL，不能只凭作品级书目把两个快照混为一项来源。

## 完整性复核

复核命令：

    Get-ChildItem -LiteralPath 01_sources\documentation\stageD -File |
      Where-Object Name -ne README.md |
      Get-FileHash -Algorithm SHA256

若上表哈希与实测不一致，应当先查明快照是否变化，不得静默用新内容替代既有证据。
