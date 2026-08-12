# 第 5 章资料包：多电子问题与平均场

## 核心来源

| ID | 固定范围 | 用途 | 证据边界 |
|---|---|---|---|
| FND-01 | Martin 2004，第 3 章第 52—70 页、第 5 章第 100—116 页 | 电子—核 Hamiltonian、Born–Oppenheimer、独立电子、Hartree–Fock、交换与关联的教材语境 | 不把平均场写成精确多体解；目录快照只核版本/页码 |
| FND-07 | [MIT 5.73, Section XII: Born–Oppenheimer Approximation](https://ocw.mit.edu/courses/5-73-introductory-quantum-mechanics-i-fall-2005/bf19f723f60f6baeba12abcb6b97f6f5_sec12.pdf)，Van Voorhis，2005，第 1—8 页 | 全电子—核 Hamiltonian、固定核电子方程、导数耦合与近简并失效边界 | 分子记号用于一般机制说明；不把质量尺度论证升级为所有材料和激发态上的严格误差界 |
| FND-08 | [MIT 10.675 Lecture 3](https://ocw.mit.edu/courses/10-675j-computational-quantum-mechanics-of-molecular-and-extended-systems-fall-2004/f2fc0576a08324375b77f6d47388bf2a_Lec3.pdf)，Rajter，2004，第 1—3 页 | Hartree 乘积、自洽场、Slater determinant、Coulomb/交换项与 Fock 算符 | 教学讲义不替代完整函数分析或基组极限证明；符号和个别排版须按本章统一重建 |
| C-FND-03 | [Kohn–Sham 1965](https://doi.org/10.1103/PhysRev.140.A1133) | 非相互作用参考体系的后续接口 | 本章不提前把 KS determinant 当作真实多体波函数；只有在非相互作用可表示且采用整数占据的常规零温情形才以单 determinant 表述，简并/分数占据或更一般情形须保留非相互作用系综边界 |
| DH-01 | 原始 DeepH 第 367—376 页 | 特定电子结构设置下单粒子 Hamiltonian 标签的对象边界 | 不支持基组无关精确多体 Hamiltonian |

## 来源—内容映射

| 内容 | 定位 | 标记 |
|---|---|---|
| 固定核电子问题与 BO 条件 | FND-01、FND-07；正文 5.1；D-C01 | `PRIMARY_EXPLICIT` + `DIRECT_DERIVATION` |
| 反对称性、Slater determinant、密度与一体密度矩阵 | FND-01、FND-08；正文 5.2—5.3；D-C02 | `PRIMARY_EXPLICIT` + `DIRECT_DERIVATION` |
| Hartree、Hartree–Fock、交换与关联区分 | FND-01、FND-08；正文 5.4—5.5 | `PRIMARY_EXPLICIT` + `DIRECT_DERIVATION` |
| 有限格点/矩阵平均场例题 | 例题与练习 | `PEDAGOGICAL` |

本章不主张用教学 determinant 恢复真实材料，不处理后端输入或正式标签。
