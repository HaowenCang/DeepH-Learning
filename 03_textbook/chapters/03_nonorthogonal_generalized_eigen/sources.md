# 第 3 章资料包：非正交基与广义本征值问题

| ID | 固定范围 | 本章用途 | 限制 |
|---|---|---|---|
| FND-01 | Martin 2004，第 14—15 章第 272—312 页 | 局域轨道、非正交性与电子结构表示 | 不支持具体数值算法的默认选择 |
| FND-02 | Golub–Van Loan 2013，第 8.7 节第 497—512 页 | 对称定广义本征问题与数值算法边界 | 复数记号结合 FND-03 |
| FND-03 | Gu et al. 2000，第 109—133 页 | \(Ax=\lambda Bx\) 的广义厄米定问题 | 不支持 DeepH 标签约定 |
| FND-04 | Higham 2008，第 2 章第 35—53 页，重点第 35 页 | \(S^{-1/2}HS^{-1/2}\) 与 Cholesky 约化 | 不把显式形成逆平方根规定为默认稳定实现 |

Gram 矩阵正定性、投影方程、Rayleigh 商、基变换谱不变性和条件数影响均应由定义逐步推导并标记为 `DIRECT_DERIVATION`。病态矩阵扫描和故障输入为 `PEDAGOGICAL`，不得外推为真实基组的统计规律。

## 来源—推导定位

| 内容 | 来源锚点 | 教材定位 | 证据类型 |
|---|---|---|---|
| Gram 矩阵与非正交局域基语境 | FND-01 | `chapter.md` 3.1.1—3.1.3；`03_generalized_eigen.md` 第 2 节 | 定义后 `DIRECT_DERIVATION` |
| Hermitian-definite 广义本征问题 | FND-02、FND-03 | `chapter.md` 3.2；推导第 3—5 节 | 定义/算法类别后 `DIRECT_DERIVATION` |
| Cholesky 与对称正交化 | FND-02、FND-04 | `chapter.md` 3.3；推导第 6—7 节 | 来源支持的约化配合 `DIRECT_DERIVATION` |
| 一般可逆基变换的谱不变性 | FND-03 的矩阵束对象 | `chapter.md` 3.4；推导第 8 节 | `DIRECT_DERIVATION` |
| 残差、后向扰动与前向界 | FND-02—FND-04 的定问题和正交化对象 | `chapter.md` 3.5；推导第 9—10 节 | 声明条件后的 `DIRECT_DERIVATION` |
| 两轨道、病态扫描和非法输入 | 不主张来自真实体系 | `examples.md`；练习 Q3-09—Q3-10 | `PEDAGOGICAL` |

表中“来源锚点”限定定义、问题类别与正交化对象；具体公式链由教材逐式推出，不把未在来源中逐字出现的推导冒充原文结论。
