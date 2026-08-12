# 第 20 章来源与论断边界

## 直接来源

| 来源 ID | 本章用途 | 本地证据 |
|---|---|---|
| E-FND-03 | \(SO(3)\)/\(SU(2)\)、自旋 \(1/2\)、宇称、反幺正时间反演与 Kramers 结论 | [MIT 8.321 第 20—23 讲](../../../01_sources/documentation/stageE/README.md) |
| E-FND-01/02 | 复表示、角动量基和耦合相位接口 | [DLMF 快照](../../../01_sources/documentation/stageE/README.md) |
| DH-02 | 论文中含 SOC 的等变 Hamiltonian 方法范围 | [DeepH-E3 论文快照](../../../01_sources/documentation/stageE/gong_2023_deeph_e3.pdf) |

## 论断边界

本章只建立高级物理接口。无自旋 \(\Theta=K\) 与自旋 \(1/2\) 的 \(\Theta=i\sigma_yK\) 按 [统一表示约定](../../stageE_representation_conventions.md) 固定。Kramers 简并要求时间反演不变且半整数自旋等条件，不能由 \(\Theta^2=-I\) 脱离 Hamiltonian 条件单独推出。DH-02 对 SOC 的论文级覆盖不等于首个正式实践必须包含 SOC；磁性、SOC、双群范围和软件对象均在 M8 冻结。

## 逐项定位

| 教材论断 | 直接位置 | 使用边界 |
|---|---|---|
| \(SU(2)\) 矩阵、\(j=1/2\) 旋转、\(2\pi\) 时 \(R=I_3\) 而 \(U=-I_2\) | MIT 8.321 第 20 讲，印刷页 88—89，式 (20.15)—(20.21) | 支持双值自旋表示；本项目主动旋转和数组顺序仍由统一约定固定 |
| \(SU(2)\) 是 \(SO(3)\) 双覆盖，\(U\) 与 \(-U\) 对应同一 \(R\)；整数/半整数表示边界 | MIT 8.321 第 21 讲，印刷页 90，式 (21.1)—(21.2) | 讲义式 (21.2) 固定群对象；不据此选择软件 Euler/四元数接口 |
| 时间反演反线性、位置/动量/角动量奇偶性、自旋 \(1/2\) 的 \(\Theta^2=-I\) | MIT 8.321 第 22 讲，印刷页 94—95，式 (22.20)—(22.39) | 讲义使用相位约定；代码矩阵采用统一约定的等价固定相位 \(J=i\sigma_y\) |
| 无自旋非简并态可选实；时间反演不变半整数自旋的 Kramers 成对 | MIT 8.321 第 23 讲，印刷页 97—98，Theorem 5/6、式 (23.1)—(23.11) | 必须保留 Hamiltonian 时间反演不变与半整数自旋条件；Bloch 语境还需区分 \(k\) 与 \(-k\) |
| 复球谐/角动量 component 的相位和 \(m\) 顺序 | E-FND-01/02；第 17—18 章已审接口 | \(J_\ell\) 数组公式是冻结约定上的直接推导，不冒充 DLMF 单独陈述 |
| SOC 等变 Hamiltonian 仅作为论文级方法范围 | DH-02 正文与补充快照 | 不授权安装、数据下载、材料/DFT 选择，也不决定 M8 是否纳入 SOC |

D-E08 完成 \(SU(2)\)、反幺正、时间反演 Hamiltonian 和 Kramers 接口；D-E09 只完成自旋扩维的解析成本子对象。T-E11/T-E12 的正式代码执行、失败矩阵和 A/B 证据见 [Stage E 代码说明](../../../05_code_exercises/stageE_synthetic_equivariance/README.md) 与 [M7-09 定点复核](../../../08_audits/M7_stageE_code_blocking_reaudit.md)。
