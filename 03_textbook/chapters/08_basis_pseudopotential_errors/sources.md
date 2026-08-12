# 第 8 章资料包：基、赝势、采样与表示误差

## 核心来源

| ID | 固定范围 | 用途 | 证据边界 |
|---|---|---|---|
| FND-01 | Martin 2004，第 11—15 章第 204—311 页 | 赝势、平面波/网格、局域轨道和 KS 离散 | 不支持具体后端格式或元素文件 |
| C-FND-04 | [Mermin 1965](https://doi.org/10.1103/PhysRev.137.A1441) | 固定温度与化学势下的有限温度 DFT 理论边界 | 数值 smearing 不自动等于目标物理温度 |
| C-NUM-02 | [Payne et al. 1992](https://doi.org/10.1103/RevModPhys.64.1045) | 平面波赝势总能、cutoff 与迭代数值背景 | 不代表所有现代方法或默认参数 |
| C-NUM-03 | [Hamann et al. 1979](https://doi.org/10.1103/PhysRevLett.43.1494) | norm-conserving 条件和 transferability 原始语境 | 不推广到 ultrasoft/PAW 或具体赝势质量 |
| DH-07 | HPRO/CLM-006 既有台账 | 平面波结果到选定 AO \(H/S\) 的投影/重建原则 | M8 前不冻结软件支持或转换命令 |

## 来源—内容边界

表示定义与赝势原始条件为 `PRIMARY_EXPLICIT`；正交/非正交矩阵离散和误差分解为 `DIRECT_DERIVATION`；网格、cutoff、采样和投影的合成收敛序列为 `PEDAGOGICAL`。后端字段全部保持未决。
