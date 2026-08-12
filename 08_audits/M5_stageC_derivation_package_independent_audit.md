# M5-07 阶段 C 解析推导包独立正式审计

## 1. 审计结论

- 审计日期：2026-08-04
- 审计性质：独立解析推导、对象接口、来源边界、失败语义与制品可验证性审计
- 总体结论：`PASS`
- `BLOCKING`：0 项
- `NON_BLOCKING`：2 项
- 是否允许 M5-07 标记为 `COMPLETED`：**是**
- 是否允许 M5-08 启动：**是**

阶段 C 的 D-C01—D-C08 已形成从固定核多电子问题到局域 Hamiltonian 标签截断验证的闭合对象链。纯态/系综、interacting/noninteracting 的 \(N\)-/\(v\)-representability、固定密度内层 minimum 与密度外层 infimum、普通导数与次梯度、局部 Jacobian 谱与全局收敛、普通/广义本征问题、正交/非正交投影、schema/数值/物性门控，以及近视性/密度矩阵衰减/\(H,S\) 稀疏性均被明确分离。未发现公式错误、对象偷换、来源越权、测试失败语义错配或 M8/M9 授权边界回归。

本结论只允许解析推导任务 M5-07 完成并启动 M5-08。它不证明 M5-08 的正式代码、统一 JSON CLI、T-C01—T-C10 自动测试或失败样例已经完成，也不授权任何真实 DFT、DeepH、正式数据或材料实践动作。

## 2. 审计范围与只读原则

核心被审对象为：

- `04_derivations/stageC/README.md`；
- `04_derivations/stageC/05_many_electron_mean_field.md`；
- `04_derivations/stageC/06_kohn_sham_variation.md`；
- `04_derivations/stageC/07_scf_fixed_point.md`；
- `04_derivations/stageC/08_representation_and_label_error.md`；
- `04_derivations/stageC/10_nearsightedness_sparsity.md`；
- `08_audits/M5_stageC_work_package.md` 的 D-C01—D-C08、T-C01—T-C10 与标签最低模板。

同时只读核对第 5、6、7、8、10 章的 `sources.md`、正文、例题、问题与参考解答，以及 `decisions.md` 的 D-009—D-011，用于确认来源等级、冻结数值、练习入口和 M8/M9 边界。本次审计未修改任何被审推导、章节、计划、追踪器或决策文件；仅新增本报告。

## 3. D-C01—D-C08 逐项判定

| ID | 判定 | 核查结果 |
|---|---|---|
| D-C01 | `PASS` | 从电子—核 Hamiltonian、固定核电子本征问题和绝热基展开逐项产生一阶导数耦合与二阶耦合；单面方程保留 Berry 连接与 Born–Huang 修正，并把非对角面间耦合、局部平行输运规范和删除对角修正分成三个独立操作。近简并分母、矩阵值简并子空间、质量尺度不是普适误差界等边界完整。 |
| D-C02 | `PASS` | determinant 的反对称性、正交条件下归一化、occupied-unitary 整体相位、1RDM 的 trace/Hermiticity/正性、单 determinant 幂等性、相关纯态非幂等反例及 HF 双计数均闭合；自旋轨道 0/1 占据与闭壳层空间轨道约定没有混用。 |
| D-C03 | `PASS` | HK 问题族固定 \(N,\hat T,\hat W\) 和边界条件，势按加法常数取等价类；共同基态步骤、非简并与简并纯态边界均明确。Levy 纯态 constrained-search 在标准三维 Coulomb 条件下使用内层 minimum，外层保持 infimum；Lieb 形式明确 \(X=L^1\cap L^3\)、\(X^*=L^\infty+L^{3/2}\)、范数拓扑、扩展值、系综对象及闭凸关系。普通导数与次梯度没有互换。 |
| D-C04 | `PASS` | \(T_s^{\mathrm{pure}}\) 与 \(T_s^{\mathrm{ens}}\) 的状态类分别定义，noninteracting \(N\)-representability 与局域势 \(v\)-representability 分离；Hartree 因子、\(E_{xc}\) 恒等定义、正交约束变分、分数占据接口、单电子势抵消到加法常数和局域 KS 总能重建均正确。 |
| D-C05 | `PASS` | \(F[n]\)、原始残差、混合映射与约束域明确；\(M_\alpha=(1-\alpha)I+\alpha J_*\) 从 Fréchet 线性化推出，谱半径结论限制在有限维、可微、初值足够近的局部邻域。实/复特征值稳定条件、非正规瞬态、预条件约束、能量伪收敛和最大步数失败均有可验证边界。 |
| D-C06 | `PASS` | 从 Galerkin 条件得到 \(Hc=ESc\)，\(H,S,c\) 的形状、Hermiticity、\(S\succ0\) 与 \(S\)-归一化完整；平面波 \(S=I\) 被限定到正交平面波、标准内积和普通范数形式，ultrasoft/PAW 等广义 overlap 边界保留。可逆基变换同步作用于 \(H,S,c\)。 |
| D-C07 | `PASS` | 基/网格、采样、smearing、SCF、投影与表示被分为独立误差轴；正交目标空间使用 \(PHP\)，非正交目标空间使用 \(B S_B^{-1}H_BS_B^{-1}B^\dagger\)，并给出错误正交回投的缩放反例。合同变换、等谱不等矩阵、标签身份和 schema/矩阵/谱/物性三层门控均正确。 |
| D-C08 | `PASS` | 局部响应近视性、独立粒子密度矩阵核衰减和局域基 \(H/S\) 块稀疏性是三个不同对象；绝缘体/金属、温度、维数、边界、带电扰动、长程静电和表示变换边界均保留。截断三指标、共轭块配对、\(S(k)\succ0\) 及图/标签/后处理三种 cutoff 分离完整。 |

## 4. 跨推导对象链核查

统一链条为

\[
\text{电子—核问题}
\to\text{固定核多电子问题}
\to\{\Psi,n,\gamma\}
\to F[n]
\to h_{\mathrm{KS}}[n]
\to n_*=F[n_*]
\to Hc=ESc
\to\{H,S,\mathcal I,\mathcal G,\mathcal P,\mathcal C\}
\to\text{固定表示中的截断验证}.
\]

专项核查结果如下。

- BO 近似没有被写成从质量比较自动得到的无条件误差界；固定核电子 Hamiltonian 也没有与后续 KS 辅助单粒子 Hamiltonian 混为同一对象。
- 多体态、密度、1RDM、HF determinant 和 KS 辅助 determinant 分开；1RDM 只能闭合一体算符期望的边界被保留。
- HK 的外势—基态密度命题、Levy 的纯态受限搜索和 Lieb 的凸对偶形式没有互相冒名；标准条件外的函数空间与相互作用未被无条件外推。
- KS 轨道方程只在所声明的局域乘法势、可微或相应次微分条件下使用；一次冻结密度本征求解没有被当作完整 SCF。
- SCF 谱半径只用于局部渐近稳定性；非正规瞬态反例明确排除了“\(\rho<1\) 因而每步单调下降”这一错误推断。
- 连续算符到有限矩阵的投影保留了 overlap；普通谱、广义谱和一致合同变换没有错配。
- 非正交目标空间的投影/回投同时保留两侧对偶度量，避免了基缩放依赖；schema 完整性没有被当作数值或物性正确性的充分条件。
- 近视性、密度矩阵衰减和矩阵稀疏性分别依赖响应对象、谱/温度条件与基表示；T-C10 合成指数族没有被外推为真实材料 cutoff。

## 5. T-C01—T-C10 与失败语义

| 范围 | 判定 | 独立核查 |
|---|---|---|
| T-C01—T-C04 | `PASS` | D-C05 的固定点、谱映射、约束与双停止条件和工作包一致。独立复算得到 \(\alpha=0.8\) 时 \(\rho=0.6\)；\(\alpha=2\) 时 \(\rho=1.8\)，固定 12 次更新的末/初残差比约为 `171.76`。零误差返回 null 速率、两周期拒绝、fake energy 伪通过和 `max_iterations` 失败语义均未错配。 |
| T-C05—T-C06 | `PASS` | 正序列后三层误差及最后两相邻差满足冻结阈值，非单调序列的 32/64 单对小差不掩盖 128 参考误差；周期积分的采样轴与固定 \(10^{-2}\) 基偏置轴分离。 |
| T-C07 | `PASS` | 独立构造冻结复上三角 \(A\) 后，广义谱为 `(-1.2,-0.1,0.8,2.0)`；忽略 \(S'\) 的普通谱最大差为 `0.9674651567663939`，满足 `overlap_ignored` 强制拒绝条件。 |
| T-C08 | `PASS` | 两个冻结配置 \(d=12,16\) 的投影丢失范数独立复算约为 `0.9598586726` 与 `0.9833167164`，均大于 0.9；标准基前两维 0.37 rad 旋转的相对矩阵差约为 `0.2330607578` 与 `0.1745198962`，均大于 0.15，而谱保持。 |
| T-C09 | `PASS` | D-C07.8 与工作包第 8 节共同保持标签身份、`stageC-label-v1`、完整必填路径、类型/形状/SHA-256/`UNRESOLVED_M8` 语义，以及逐路径删除必须抛出含缺失路径 `ValueError` 的失败要求；schema 通过不替代矩阵、谱或物性门控。 |
| T-C10 | `PASS` | D-C08 的 \(A_{\exp}\)、\(A_{\mathrm{alg}}\)、四个截断半径和三项指标与工作包一致。指数斜率解析值为 \(-0.5\)；代数族短窗指数外推到 16—31 的相对残差独立复算为 `0.8429707836304159`，满足大于 0.8 的强制拒绝条件。 |

上述复算只交叉验证解析对象与冻结阈值，不替代 M5-08 尚待建设的正式测试实现和规范 JSON CLI。

## 6. 来源等级与授权边界

第 5、6 章推导文件直接给出来源—内容—状态表；第 7、8、10 章通过 README 的章节入口与各章 `sources.md` 建立来源边界。可复核映射为：来源直接陈述的理论/算法对象标为 `PRIMARY_EXPLICIT`，由已声明定义完成的代数标为 `DIRECT_DERIVATION`，冻结有限维/离散/合成验证标为 `PEDAGOGICAL`。未发现把历史论文解释成现代软件接口、把 norm-conserving 条件推广到所有赝势、把 Prodan–Kohn 近视性推广为任意矩阵统一指数稀疏，或把教学数值变成实践默认的情况。

D-009—D-011 与推导包一致：Python 用户态依赖可按精确版本记录安装；M8 前不得安装 DeepH 本体、下载正式训练数据、生成正式 DFT 标签或隐含选择材料体系、DFT/数据后端和实践软件版本；M7-I 全量审计通过后才准备 M8 决策冻结；M8 冻结后，在 M9 正式安装、数据下载或复现实验前仍需再次取得明确执行授权。

## 7. 制品与链接验证

使用 Pandoc 3.6.4 执行：

```powershell
pandoc <file> `
  --from markdown+tex_math_dollars+tex_math_single_backslash `
  --to html5 --mathml --fail-if-warnings
```

六文件均退出码 0，实际 MathML 节点如下。

| 文件 | MathML 节点 | 行内定界 | 展示定界 | 异常控制字符/TAB/DEL/U+FFFD |
|---|---:|---:|---:|---:|
| `README.md` | 17 | 15/15 | 2/2 | 0 |
| `05_many_electron_mean_field.md` | 89 | 52/52 | 37/37 | 0 |
| `06_kohn_sham_variation.md` | 149 | 98/98 | 51/51 | 0 |
| `07_scf_fixed_point.md` | 82 | 49/49 | 33/33 | 0 |
| `08_representation_and_label_error.md` | 114 | 69/69 | 45/45 | 0 |
| `10_nearsightedness_sparsity.md` | 66 | 40/40 | 26/26 | 0 |

对六文件的活动 Markdown 链接逐一相对源文件目录解析，结果为 `LINKS=19`、`BROKEN=0`。README 的 D-C01—D-C08、五章正文/例题目录、五章练习/参考解答目录和阶段 C 工作包入口均可达。

## 8. NON_BLOCKING findings

### M5-C-D-N01：D-C05—D-C08 的来源等级依赖 README 到章级 `sources.md` 的间接跳转

第 7、8、10 章 `sources.md` 已分别给出 SCF、离散表示/投影和近视性/局域性的来源用途及 `PRIMARY_EXPLICIT`、`DIRECT_DERIVATION`、`PEDAGOGICAL` 边界；README 第 3、5 节也建立了有效入口。因此当前来源可以追溯，且未发现事实越权，不构成阻塞。

相比之下，`05_many_electron_mean_field.md` 和 `06_kohn_sham_variation.md` 在文件末尾直接列出来源—内容—状态表，而 `07_scf_fixed_point.md`、`08_representation_and_label_error.md` 与 `10_nearsightedness_sparsity.md` 没有同层级直接表格。后续编辑宜在三文件末尾补充对应表或精确链接到各章 `sources.md`，以减少脱离 README 单独阅读时的追溯成本。

### M5-C-D-N02：T-C08 的完整旋转参数与 T-C09 的逐路径删除规范只在工作包/题解中完整展开

`08_representation_and_label_error.md` 正确给出 T-C08 的投影、等谱不等矩阵及阈值结论，也在 D-C07.8 给出标签身份与验证层次；README 第 6 节明确把 D-C06—D-C07 映射到 T-C05—T-C09，并链接冻结工作包。工作包与第 8 章题解进一步提供标准基前两维 0.37 rad 旋转、`stageC-label-v1` 必填路径、逐路径删除和错误消息要求。因此整体规范闭合且没有错配，不构成阻塞。

为提高推导文件的独立可读性，后续可在 D-C07.7 明示旋转平面与角度，并在 D-C07.8 增加一句指向工作包第 8 节的 T-C09 完整路径/删除规范；无需在推导文件重复整张 schema 表。

## 9. SHA-256 审计快照

```text
8C0A8ED24C112233D8E5F8EBF25918DD58616A4B023F1463F5971CC7B6B00A1D  04_derivations/stageC/README.md
01385729D1D0DF6B50B3E4EF0E9624959845D2FD55E2A49D0D28E1009B7F64D2  04_derivations/stageC/05_many_electron_mean_field.md
9986FCE7FACDEABE55CBF6DCC8E5C1DD6C86E0BB7AB7ECFDD0BA7A5D16975335  04_derivations/stageC/06_kohn_sham_variation.md
73156809A651ED21122A1190D4F5BD2A801563D319B848C50CB30106F2C6D422  04_derivations/stageC/07_scf_fixed_point.md
63E8F7D712F9ADCF57AAE7D46F1DC4F4C2A379344E5EE85D063637849C2CCBB8  04_derivations/stageC/08_representation_and_label_error.md
F72E9C78EB0D7B0D566D0388DCA88649BD2BFBCD1472775F37A081B604F929E4  04_derivations/stageC/10_nearsightedness_sparsity.md
4E1D6E473CDA1D20328F24FA50734BA3B3EBAF8FE1AFC99AF3B0A5D4F75CD2BD  08_audits/M5_stageC_work_package.md
272AED3AD8B771EA0D80FD1C06BECEDB9694A29A994323F820C61E9B2C0CE318  decisions.md
```

最终判定：M5-07 `PASS`，`BLOCKING=0`、`NON_BLOCKING=2`；允许 M5-07 标记为 `COMPLETED` 并启动 M5-08。两项非阻塞建议只改善来源和测试规范的直接可达性，不降低当前解析门控结论。
