# M7-06 第 19 章正式独立内容审计

## 1. 审计结论

**结论：FAIL。** 当前快照存在 `BLOCKING=2`、`NON_BLOCKING=0`。因此不允许将 M7-06 标记为 `COMPLETED`，也不允许启动 M7-07。主 agent 修订后，必须由本独立审计员对稳定问题 ID 执行定点复核；主 agent 的内部验证不能替代该结论。

第 19 章已经正确建立周期 receiver→sender 位移、完整边键、表示型 tensor schema、实基 Hamiltonian 双侧作用、多壳层身份、逆边 Hermiticity、concat/padded 行映射、局部架回拉、误差分层和 M8/M9 授权边界。固定非方块及多数数值锚点可独立复现。但是，复球谐点值与 coefficient 表示之间的接口在消息公式中没有被真正定义，导致按当前公式字面执行时一般复旋转不等变；此外，D-E05—D-E07 合并推导没有满足工作包对“每项推导”的结构门控，尤其缺少统一符号—维度表，以及 D-E06/D-E07 各自可独立复算的解析正例和定量失败例。现有材料尚不能通过材料完备性、可自学性和可验证性门控。

## 2. 独立性、范围与方法

本审计由新的独立子 agent 完成。被审材料全程只读；本次唯一新增文件为本报告。审计范围为：

- `03_textbook/chapters/19_equivariant_graph_hamiltonian/{sources.md,outline.md,chapter.md,examples.md}`；
- `04_derivations/stageE/19_equivariant_graph_hamiltonian.md`；
- `06_exercises/05-stageE/19_equivariant_graph_hamiltonian/{problem,solution}/readme.md`；
- `08_audits/M7_stageE_work_package.md`、`03_textbook/stageE_representation_conventions.md`；
- 阶段 D 总门控和周期图接口；
- 第 15—18 章教材、推导及已审接口；
- 阶段 E 直接来源快照、来源台账和 DeepH-E3 论文快照。

独立检查包括：

- D-E05—D-E07/D-E09 到 T-E06/T-E08—T-E10/T-E12 的可定位性和条件一致性；
- 固定 \(4\times8\) 非方 Hamiltonian、错误左右作用、逆边、实—复基相似变换；
- 两边消息、200 个一般轴旋转、反演、节点置换和局部架回拉；
- float64/float32 零长度与近共线阈值两侧、等号方向和任意后备轴故障；
- 七文件严格 Pandoc/MathML、Pandoc AST 活动链接、Raw TeX、控制字符、三级标题和题解配对；
- 阶段 E 11 个固定来源快照的 SHA-256；
- DeepH-E3/e3nn、数据、材料、DFT、SOC 和 M8/M9 授权边界。

复算环境为 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0；没有安装或导入 DeepH/e3nn，没有下载正式数据，也没有生成 DFT 标签。

## 3. 当前送审快照

| 文件 | SHA-256 |
|---|---|
| `sources.md` | `C5DFA7DCECE7E32326BF681BE61F2864ACE80C8C82EC08D51AC2ABF7606615D9` |
| `outline.md` | `3A7F34120FD10AF1F9504386E1BFA271CB66C06CE662666572CA82898B523502` |
| `chapter.md` | `28D45C3D3BC35620F78D9EA83FEA49428DA38DEBAB48F62FC093B467D83DEAFF` |
| `examples.md` | `CD9CB2C21B1938D38978F91A3C946E7FA0EEFB059E631102A7EC314A39A0F605` |
| `19_equivariant_graph_hamiltonian.md` | `A77DE07196ECF29D0337414779D2C60EAE30619608D8185CDAAF9AC259DC274B` |
| `problem/readme.md` | `7326494AF5ECA7151B94AFF1456C97C36F495EB41B86C32E5F208A2EA0A03B37` |
| `solution/readme.md` | `E54A3C68BC964539F6F24381FE89CEFDD0DEE5862A356E4C7B50F78306086609` |

## 4. 独立复算结果

### 4.1 周期方向、完整键和统一行

材料一致采用 (e=(i,j,n))，其中 (i) 为 receiver、(j) 为 sender，行位移为

\[
d_e=(f_j+n-f_i)A,
\]

主动旋转后 \(A'=AR^{\mathsf T}\)、\(d_e'=d_eR^{\mathsf T}\)，完整离散 payload

\[
[\text{stageD-edge-v1},\text{structure ID},i,j,n_x,n_y,n_z]
\]

保持不变。prediction、target、mask、shell pair、实际轨道、edge key/ID、位移和 provenance 共享同一长度 (E) 的行轴；concat/padded、prefix mask、完整 irrep shell 全真/全假及 inactive 值先切除规则与阶段 D 和第 16—18 章接口一致。

### 4.2 固定 \(4\times8\) Hamiltonian 与故障

独立按 Rodrigues 公式、冻结的五个 STF 基矩阵和

\[
D^d_{ab}(R)=\operatorname{tr}(B_a^{\mathsf T}RB_bR^{\mathsf T})
\]

复算例 19-3。教材中八位小数 (R) 与全精度结果的最大差为 \(4.21\times10^{-9}\)，所列 \(H'=D_iHD_j^{\mathsf T}\) 与全精度结果的最大差为 \(4.47\times10^{-9}\)，属于显示舍入。三种错误对象相对正确结果的归一化残差分别为：

\[
0.5461588700222612,
\quad 0.05995264976907191,
\quad 0.9216691727258702,
\]

与材料一致，且均远大于 (10^{-4})。左右正交作用下奇异值最大变化为 \(3.55\times10^{-15}\)。逆边旋转结果与正向块转置的最大逐元素差为 \(8.88\times10^{-16}\)。

采用第 17 章冻结的 (K_1,K_2) 组成 (K_i,K_j)，实路线和复路线的归一化残差为 \(3.39\times10^{-16}\)；在复路线把右侧共轭转置错误替换为普通转置时，残差为 (1.1077294836526819)。200 个随机一般轴旋转中，实—复路线最大残差为 \(4.74\times10^{-16}\)。因此 D-E05 的核心双侧公式、非方 shape、多壳层、实复基和逆边主结论正确。

### 4.3 消息、反演和置换

以固定 (G_A) 的八条有向边构造偶标量 sender 特征和径向偶权重，并采用 \(0\otimes1\to1\) 的等价实笛卡尔消息。200 个随机一般轴旋转的端到端最大残差为 \(7.19\times10^{-16}\)；整体反演下极向量输出残差为 0；固定节点置换及同步端点重标记后的残差为 0。例 19-13 的两条入边给出

\[
a_i=(2,3/2,0)^{\mathsf T},
\qquad
a_i'=(-3/2,2,0)^{\mathsf T}=R_z(\pi/2)a_i,
\]

数值正确。偶标量门控保持宇称、伪标量门控翻转宇称以及 (1+s_-) 没有确定宇称的判断也正确。

但上述实基测试不能关闭第 6.1 节的复基公式问题。

### 4.4 局部架与回拉

对两个独立局部架、非方 \(4\times8\) 块和 200 个随机一般轴旋转，(F(RX)=RF(X)) 最大残差为 \(7.21\times10^{-16}\)，局部不变预测回拉到全局块的最大残差为 \(1.42\times10^{-15}\)。固定块局部化—回拉往返残差为 \(3.95\times10^{-16}\)。

float64 的 \(\tau_0=10^{-12}\)、\(\tau_{\mathrm{frame}}=10^{-8}\) 与 float32 的 \(10^{-5},10^{-4}\) 均按实际计算指标给出正确接受方向：\(0,0.5\tau_0,\tau_0\) 拒绝，\(2\tau_0\) 接受；\(\varepsilon=0,\tau/4,\tau/2,\tau\) 拒绝，\(2\tau,4\tau\) 接受。等号拒绝。对固定全局 \(y\) 后备轴施加 \(R_x(\pi/2)\) 时，后备轴与应有 \(R e_y\) 的差范数为 \(\sqrt2\)，验证了任意后备轴不协变。

### 4.5 成本和授权边界

D-E09 已把消息路径、同型混合、receiver 聚合、Hamiltonian 双侧乘法和局部架分成不同操作图；实 MAC/FLOP、complex 展开、逐数组 bytes、完整物化 total、参考流式 peak 和 wall-time 也没有混写。144 点扫描被明确留给 M7-09，没有把章内解析计数冒充正式执行证据。

来源文件和正文均将 TFN/e3nn/DeepH-E3 限定为论文级机制证据。DeepH-E3 快照实际 SHA-256 为 `379B288B66365D5202A481923746D5F01D8EB03433D2C67EA3E5E7261074596E`，与登记一致；论文确实讨论 E(3) 等变 Hamiltonian、球谐/tensor product 消息和局部坐标对比。材料没有据此选择仓库 commit、软件版本、材料、DFT/数据后端、SOC 实践或训练预算。M8 集中决策和 M9 二次执行授权边界保持正确。

## 5. 文档、来源和导航验证

七文件均以 `markdown+tex_math_single_backslash`、HTML5 MathML、`--fail-if-warnings` 严格通过，MathML 数分别为 `3/4/137/83/103/16/70`，合计 416。Pandoc AST 中共有 5 个活动本地链接，全部存在；Raw TeX 节点为 0；非法控制字符为 0。

`outline.md` 与 `chapter.md` 的三级标题均为 35 个，文本和顺序 35/35 完全一致。Q19-01—Q19-10 与 A19-01—A19-10 为 10/10 严格配对。阶段 E README 登记的 11 个来源快照实际 SHA-256 全部一致；E-GNN-01、E-GNN-02、DH-02 的来源用途和限制与中央台账相容。

## 6. 问题清单

### M7-C19-B01：复球谐点值未经明确定义的 coefficient 映射即进入规范 CG，当前复基消息公式不等变

**严重度：BLOCKING。**

**证据：**

- `chapter.md` 19.2.2 正确写出复球谐点值 \(y(R\widehat d)=D(R)^*y(\widehat d)\)，并称进入 coefficient contraction 前必须使用第 17 章映射；
- 紧接着 19.2.3 的实际公式仍直接使用 \(y_{\ell_fm_f}(\widehat d_e)\)，没有定义映射后的 filter 变量；19.3.2 却直接调用只适用于两个 coefficient 表示输入的 \(C(D_{\mathrm{in}}\otimes D_f)=D_LC\)；
- `04_derivations/stageE/19_equivariant_graph_hamiltonian.md` 3.1 同样直接把 (y) 写入 CG，3.2 直接假设 filter 按 (D_f) 变换；A19-03 也重复该跳步；
- 七文件没有给出“点值 (D^*) → coefficient (D)”在消息路径中的具体数组、公式、shape、共轭方向或 provenance 身份。第 17 章区分 \(C_\ell\) 函数值映射和 \(K_\ell=C_\ell^*\) 系数映射，并不能自动补全第 19 章到底对边 filter 执行了什么操作。

取最简单的 \(0\otimes1\to1\) 路径、冻结 (K_1)、一般复 Wigner 旋转和非轴向单位向量。按当前公式字面令输出 \(m=y_1(\widehat d)\)，则旋转后的点值为 (D^*m)，而材料声称输出应为 (Dm)。独立复算得到归一化残差

\[
\rho\!\left(y_1(R\widehat d),D^{(1)}(R)y_1(\widehat d)\right)
=1.7576804786090063.
\]

若明确使用共轭后的 coefficient filter (z=y^*)，则

\[
z(R\widehat d)=D(R)z(\widehat d)
\]

的残差为 \(1.11\times10^{-16}\)。这表明问题不是浮点误差，而是公式对象缺失。当前全部消息数值例使用等价实笛卡尔基，因 (D^*=D) 而无法暴露该问题。

**影响：** D-E06 的逐层 intertwiner 证明在复基下没有成立；同一章同时宣称支持 \(mathbb R/\mathbb C\) 表示和实复 Hamiltonian 路线，因此不能把该缺口降为仅限未来代码的实现细节。第三方按公式直接实现会在一般轴复旋转下稳定失败，同时仍可能通过全部实基、z 轴或 shape 测试。

**最小关闭条件：** 在正文、D-E06 推导、至少一个一般轴复数例题和 A19-03/A19-10 中显式定义进入 CG 的 coefficient filter。可以定义并验证 \(z_\ell(\widehat d)=y_\ell(\widehat d)^*\) 及 \(z(R\widehat d)=D(R)z(\widehat d)\)，也可以给出另一条与冻结 CG 表严格相容的显式 intertwiner；不得仅写“使用映射”。同步给出 dtype/shape、(m) 顺序、宇称、basis family、版本/hash 和 edge-row provenance，修改消息公式及逐层证明，并加入一般复轴正例与“直接把 (D^*) 点值送入 coefficient CG”定向失败，映射到 T-E08/T-E12。

### M7-C19-B02：D-E05—D-E07 合并推导未满足逐项解析推导结构门控

**严重度：BLOCKING。**

**证据：** `M7_stageE_work_package.md` 第 5 节明确要求每一项推导均包含符号表、输入/输出维度、逐步推导、成立条件、至少一个解析例、至少一个失败样例、T-E 映射和可独立复算的最终不变量。当前 `19_equivariant_graph_hamiltonian.md`：

- 没有符号—维度表；D-E06 的 (x,y,w,C,m,a,W,h) 和 D-E07 的 \(u,v,s,F,U_i,U_j,\overline H,H\) 的完整 rank/shape、基和 dtype 只能由分散下标推测；
- 没有按 D-E05、D-E06、D-E07 分列成立条件。特别是 D-E06 没有把复点值/系数接口列为证明前提，已经实际导致 B01；
- D-E05 有固定 \(4\times8\) 解析锚点和定量错误残差，但 D-E06 推导文件内没有完整数值消息例或独立定量失败例；两边消息只在 `examples.md` 中出现；
- D-E07 推导文件内没有完整数值局部化—回拉例。其失败域只是清单，没有给出任意后备轴的定量协变残差，也没有用 \(\varepsilon\to0^+\) 与 \(\varepsilon\to0^-\) 显示近共线架的有限跳变；当前正 \(\varepsilon\) 阈值表只说明接受/拒绝，不等价于“近退化不连续”的可复算失败例；
- 第 11 节结论是定性总结，没有按三项列出最终可复算不变量、残差对象和适用定义域。

**影响：** 章内例题能够补充教学材料，但不能替代工作包对“每项推导”的显式结构要求。当前第三方无法仅从 D-E05—D-E07 推导文件唯一恢复全部数组合同，也无法逐项判断哪些条件是数学前提、哪些只是未来 T-E 执行要求。该缺陷同时削弱 D-E06 的复基审查和 D-E07 的定义域审查。

**最小关闭条件：** 在推导文件中增加覆盖 D-E05—D-E07 的统一符号—维度—dtype—基—身份表，并按每个 D-E 项分别列出成立条件、输入/输出、最终不变量和 T-E 入口。把例 19-13 的两边消息或等强度一般轴消息完整纳入 D-E06，给出逐层数值残差及至少一个定量错误；把非退化局部架、局部块不变和 \(4\times8\) 回拉完整纳入 D-E07，并给出阈值等号、任意后备轴以及正/负近共线扰动导致的定量失败。引用章外例题可以保留，但推导文件自身必须包含可独立复算的对象和结果。

## 7. 退出判断

当前 `BLOCKING=2`、`NON_BLOCKING=0`。D-E05 的实/复 Hamiltonian 双侧路线、周期逆边、行映射、mask/batch、局部架阈值、成本分层和来源/授权边界均未发现其他问题；严格文档验证也全部通过。但 B01 使 D-E06 复基公式的核心证明不成立，B02 违反已冻结的逐项解析推导结构门控。

因此：

- M7-06 不得完成；
- M7-07 不得启动；
- 主 agent 应按最小关闭条件修订；
- 修订后须由本独立审计员复核 `M7-C19-B01`、`M7-C19-B02` 及相邻回归，只有问题总数为 0 才可放行。
