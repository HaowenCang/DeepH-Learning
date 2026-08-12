# 阶段 D 统一图、周期与张量约定

本文件是第 11—14 章、D-D01—D-D07、T-D01—T-D10 和综合练习的共同契约。完整定义与门控见 [M6 工作包](../08_audits/M6_stageD_work_package.md)。

## 坐标与边

- \(A\in\mathbb R^{3\times3}\) 的行是晶格矢量。任意有限代表 \(\widetilde f_i\in\mathbb R^3\) 分解为规范存储 \(f_i=\widetilde f_i-\lfloor\widetilde f_i\rfloor\in[0,1)^3\) 与整数 \(q_i=\lfloor\widetilde f_i\rfloor\)，且 \(r_i=f_iA\)。
- float64 下要求 \(\sigma_{\min}(A)>0\) 且 \(\kappa_2(A)<10^8\)；数学奇异或达到/超过该条件数阈值的教学输入拒绝。
- 有向边 `(i,j,n)` 中 \(i\) 为接收节点、\(j\) 为发送节点、\(n\in\mathbb Z^3\) 为发送节点镜像。
- \(d_{ijn}=(f_j+n-f_i)A\)，保留 \(0<\lVert d_{ijn}\rVert_2\le r_c\) 的全部边。
- 零位移自环排除；非零自镜像边保留；稳定排序键为 `(i,j,n_x,n_y,n_z)`。
- 不按 `(i,j)` 去重，不把最小镜像当作任意晶胞和 cutoff 下的通用算法。

## 周期代表与置换

逐原子换胞 \(\widetilde f_i=f_i+q_i\) 时，同一物理边采用 \(n'=n+q_i-q_j\)。匹配时回拉 \(n^{\mathrm{can}}=n'-q_i+q_j\)，以 `(structure_id,i,j,nx,ny,nz)` 精确配对；edge ID 为 JSON 数组 `["stageD-edge-v1",structure_id,i,j,nx,ny,nz]` 在 `ensure_ascii=false`、`separators=(",",":")`、UTF-8 下的 SHA-256。配对后以 `rtol=0, atol=1e-12` 比较位移和距离。节点置换必须同时作用于节点张量、边端点与输出索引；镜像整数向量作为晶格坐标不随节点编号置换。

## MPNN 与张量

\[
m_{ijn}^{(t)}=\phi_m^{(t)}(h_i^{(t)},h_j^{(t)},e_{ijn}),\quad
\bar m_i^{(t)}=\sum_{(i,j,n)\in E}m_{ijn}^{(t)},\quad
h_i^{(t+1)}=\phi_u^{(t)}(h_i^{(t)},\bar m_i^{(t)}).
\]

边输出必须保留结构、原子对、镜像、轨道对、块形状和唯一边实例 ID。阶段 D 只验证节点重编号与周期代表的一致性，不宣称普通 MPNN 具有三维旋转等变性。

## 数值环境与授权

阶段 D 使用 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0 和合成数据。缺失的普通 Python 用户态依赖可按 D-009 固定版本安装并记录命令；M8 前不得安装 DeepH、获取正式训练数据、生成 DFT 标签或隐含选择实践对象。
