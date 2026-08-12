# M7-10 阶段 E 自学材料第一次定点复核

## 1. 复核结论

**结论：PASS。** 原稳定问题 `M7-SESS-B01`—`M7-SESS-B05` 均为 **CLOSED**。本次相邻合同检查发现新增 `BLOCKING=0`、新增 `NON_BLOCKING=0`；最终剩余问题为 0。

因此允许将 M7-10 标记为 `COMPLETED`，并允许启动 M7-11 阶段 E 总审计。本结论只关闭 M7-10 材料完备性、可自学性和可验证性门控；不替代 M7-11、D-011 指定的 M3—M7 全量独立审计，也不改变 M8/M9 的决策与再次授权边界。

## 2. 独立性、范围与送审快照

本复核由原 M7-10 独立审计员执行。复核期间未修改教材、推导、代码、题目、解答、台账、工作包或既有审计；唯一新增文件为本报告。

原审计报告 `08_audits/M7_stageE_self_study_independent_audit.md` 的稳定 SHA-256 为 `B5E42923B490528ABEB39DFA716BCA04499EE2EA53355C356B96B13EC5EF66F1`。当前四份核心材料 SHA-256 为：

| 文件 | 当前 SHA-256 |
|---|---|
| `03_textbook/chapters/stageE_self_study_guide.md` | `3E253D9B35D58E0D57BE6FA0C7DBFEBE59144AF38BA8D2CE22ADC5E220764B3D` |
| `03_textbook/stageE_representation_trace_template.md` | `56A93A8E4BC6072FF6E3CBDAB03F16570B8E0C51D48589B7E571F7B5A32449DD` |
| `06_exercises/05-stageE/comprehensive/problem/readme.md` | `6DBDF4D3E1CAECB2071309DD1577E12623B98BAACBEED2528BD575D1FE931C1D` |
| `06_exercises/05-stageE/comprehensive/solution/readme.md` | `C752A39FA588B1C324A4E4766EBF9076200211BD9378C56054FE369F9C70DC06` |

阶段 E 代码送审 SHA-256 为：

| 文件 | 当前 SHA-256 |
|---|---|
| `stagee_models.py` | `09BC05AF29DA3C7559D1DA7623257FCA01A319130CCD0ACF0DE46E330A26A535` |
| `run_experiments.py` | `9D62BB9C24EAA09D44032D97A7F9E36324AE81283474569ABE71146BB630D7E5` |
| `test_stagee_models.py` | `DA20B8DF59C1EBCA0BACC68B7AFDCF5D7732310C31F4A7209D491A24D9E9D33A` |
| `README.md` | `0339ED7021AA84A493FCC1130BD76EAFFC55E0DE324D3F811009119B6EC580F3` |

复核对象还包括统一表示约定、D-E01—D-E09 推导索引及六份推导、第 15—20 章教材/例题/章节题解、M7 工作包、M7-09 PASS 报告和原 M7-10 FAIL 报告。

## 3. 稳定问题逐项复核

### M7-SESS-B01：`CLOSED`

原问题是自学导航使用了与工作包/推导索引不同的 D-E 编号，并把若干能力指向错误章节小节。当前修订已统一为：

| ID | 当前唯一能力对象 | 当前主要入口 |
|---|---|---|
| D-E01 | 主动/被动、复合、scalar/polar/axial/tensor 的 (SO(3)/O(3)) 作用 | 第 15 章与 `15_group_actions_equivariance.md` |
| D-E02 | 实 (s,p,d)、STF、直和/multiplicity 与轨道宇称 | 第 16 章与 `16_real_spd_representations.md` |
| D-E03 | DLMF-CS 球谐、Wigner、点值/coefficient 与复—实桥 | 第 17 章与 `17_spherical_harmonics_wigner.md` |
| D-E04 | CG、选择定则、intertwiner、交换和相位自由 | 第 18 章与 `18_tensor_products_clebsch_gordan.md` |
| D-E05 | Hamiltonian 双侧作用、Hermiticity、逆边与轨道身份 | 第 19 章推导 |
| D-E06 | coefficient filter、CG 消息、receiver sum、同型混合与门控 | 第 18/19 章推导 |
| D-E07 | 非退化局部架、回拉/推出与退化边界 | 第 19 章推导 |
| D-E08 | SU(2)、反幺正时间反演、H/S partner 与 Kramers/TRIM | 第 20 章推导 |
| D-E09 | 维数、残差、dtype、MAC/FLOP、数组字节与 144 点扫描 | 推导总索引第 4 节及分章子节 |

导航的单元表、12 行正向矩阵、代码/症状反向索引和能力边界表均采用上述同一编号。逐行检查没有再发现把 STF/Wigner/CG/Hamiltonian/message/local-frame/time-reversal 依次错移一位的情况。章节定位也已修正为 polar/axial 的 16.5、局部架的 19.6、残差与成本的 19.7；C-E09/C-E10 的教材、推导、代码和题解均由这些正确入口继续追踪。

关闭条件满足，未发现相邻编号或反向索引回归。

### M7-SESS-B02：`CLOSED`

C-E08 题面和 A-E08 现在均冻结：节点 coefficient 为 ((1,-))，polar 方向 coefficient filter 为 ((1,-))，所以

\[
(1,-)\otimes(1,-)
\longrightarrow
(0,+)\oplus(1,+)\oplus(2,+).
\]

题面要求显式写出 \(p_{\mathrm{out}}=p_{\mathrm{in}}p_{\mathrm{filter}}\) 并用空间反演核对三条输出；解答明确说明 input 与 filter 在反演下各乘 (-1)，输出为偶宇称。导航 C-E08 行、代码说明、`make_message_provenance` 和 validator 均使用：

```text
input_irrep = [1,-1]
filter_irrep = [1,-1]
output_irreps_with_parity = [[0,1],[1,1],[2,1]]
```

独立运行 A/B 时，T-E08 的空间反演正例最大残差均为 0；把偶输出错误解释成奇输出的残差均为 `2.0`。`wrong_irrep_parity_metadata` 在进入 contraction 前实际抛出异常；unit test 还直接核对三组 provenance 字段，并分别篡改 input parity 和一个 output parity，二者都被 validator 拒绝。该复核不是只测 (SO(3))，已实际使用 (Q=-I) 的 (O(3)) 反演。

关闭条件满足；题面、解答、导航、代码 provenance、正例和失败样例一致。

### M7-SESS-B03：`CLOSED`

表示追踪模板和 A-E09 已与统一约定/代码统一为：

\[
\zeta_u=\frac{\lVert u\rVert}{s},\qquad
\zeta_v=\frac{\lVert v\rVert}{s},\qquad
\eta=\lVert\widehat u\times\widehat v\rVert_2.
\]

两项 (zeta) 必须先通过零长度检查，之后才能归一化并计算无量纲角退化度。float64 的零长度/架阈值为 (10^{-12}/10^{-8})，float32 为 (10^{-5}/10^{-4})，等号均在拒绝侧。

题面、解答和模板均加入冻结幅值反例：float64、(s=1)、(u=(1,0,0))、\(v=(2,1.5\times10^{-8},0)\)。独立复算得到：

```text
normalized eta = 7.5e-9
unnormalized projected length = 1.5e-8
```

规范指标落在拒绝侧，而旧未归一化公式会错误接受。实际调用 `local_frame` 返回 `ValueError: local frame is on the collinear rejection side`，与修订后的材料一致。原来遗漏的 (zeta_v) 也已补入模板。

关闭条件满足；幅值无关性、dtype 阈值和等号方向没有相邻回归。

### M7-SESS-B04：`CLOSED`

导航第 3 节现有 C-E01—C-E12 共 12 行正向矩阵。每一行均分别给出：

1. 可点击教材和规范 D-E 推导；
2. 可点击的具体章节例题并在链接文字中列出例题编号；
3. 代码函数/T-E ID 及对应失败症状；
4. 可点击章末问题与章末参考解答，并列出 Q/A 编号；
5. 可点击综合问题 C-E 与综合解答 A-E。

以 Pandoc AST 对每行解析目标并按路径分类，12/12 行均同时具有 `chapter`、`derivation`、`examples.md`、非 comprehensive 的 `problem/readme.md`、非 comprehensive 的 `solution/readme.md`、`comprehensive/problem/readme.md` 和 `comprehensive/solution/readme.md`；全部七类布尔检查均为 true。矩阵中的所有具体 Q/A 编号也都能在相应文件的二级标题集合中找到。

关闭条件满足。由能力到教材、推导、例题、代码、失败、章末练习/解答和综合题/解答的路径已经可直接执行。

### M7-SESS-B05：`CLOSED`

表示追踪模板第 10 节保留算符层记录，并新增独立 H/S partner 表。新增字段覆盖：

- `schema_version`、real/complex dtype、`k_id/minus_k_id` 和两 k 点坐标；
- `partner_map`、orbital IDs、partner orbital IDs、basis/component 顺序；
- H/S k/-k 的独立 row provenance；
- `J` 的 shape/dtype/hash 和 (Theta^2)；
- `H_k/H_minus_k`、`S_k/S_minus_k` 的 shape、complex dtype、Hermiticity、有限性和 \(S\succ0\)；
- bool `[2,2]` active mask；
- H 与 S 各自的 partner 关系残差；
- TRIM 的 (k=-k+G)、一般 k 非 TRIM、Kramers 的完整先决条件；
- T-E11 pair identity、array summary 及六项 partner 故障。

该表可直接承接 A/B 实际输出。复核中 A/B 的 `pair_identity` 均为 schema `stageE-time-reversal-pair-v1`、一般 k/minus-k 两个独立 ID、`partner_map=[1,0]` 和两条冻结 orbital row；TRIM 广义本征值分别保持成对。六项 wrong ID、wrong map、partial mask、orbital row drift、missing H conjugation 和 wrong S partner 均实际拒绝。

关闭条件满足；算符平方不能再替代 H/S partner provenance、mask 和数组身份记录。

## 4. 代码、确定性与数值回归

固定环境与命令为：

```powershell
$python = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python --version
& $python -c "import numpy, scipy; print(numpy.__version__, scipy.__version__)"
& $python -m pip check
& $python -m unittest discover -s .\05_code_exercises\stageE_synthetic_equivariance -p 'test_*.py' -v
& $python .\05_code_exercises\stageE_synthetic_equivariance\run_experiments.py --config A --seed 20260809
& $python .\05_code_exercises\stageE_synthetic_equivariance\run_experiments.py --config B --seed 20260810
& $python .\05_code_exercises\stageE_synthetic_equivariance\run_experiments.py --scan
```

实测 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0；`pip check` 无破损依赖；17/17 unittest 通过。A、B、scan 各在两个独立子进程中执行，stdout 逐字节相同，SHA-256 为：

```text
A    6a656a18bbfef042cbcd3049278c15fd0644f4b593d06e44a2b63c5fc78be856
B    b9e4ca3de9e671f4f9b674e40b5f62068f3a91e6ba886d4640d3b90aa6fd82d1
scan c13944029e29ef6b47919646952a5d9bdf6a018cee3f101429fab09967982a81
```

A/B 的 T-E01—T-E12 均 `pass=true`、`overall_pass=true`。T-E12 均为 `rejected=63`、`total=63`、`unique_failure_names=63`；三个 inactive padding 探针 NaN、0、`1e300` 的活动残差和 loss 均为 0，active NaN 仍拒绝。scan 仍为 144 个唯一 case，摘要为：

```text
max_residual = 1.9468769400071583e-07
worst_case = float32-s20260809-r257-m1-a1e+03
worst_rotation = 189
worst_ell = 2
canonical_case_digest = 5317a387bfb026e53dceb31a85074d52ff520448c2fbac9649cb8013064cca7e
```

成本锚点无回归：G_A 为 `168/52/2728/2280`，G_B 为 `378/143/5584/4576`，依次表示每旋转 MAC、每旋转聚合加法、完整物化数组字节和参考流式 peak 字节。

## 5. 严格格式、链接与控制字符

对四份核心材料、统一约定、推导索引/六份推导、六章教材/例题、六组章末题解、代码说明、工作包、M7-09 PASS 报告和原 M7-10 审计共 41 个输入运行：

```powershell
pandoc --from=markdown+tex_math_single_backslash --to=html5 --mathml --fail-if-warnings <file>
```

结果为 41/41 返回 0。另对 40 个唯一 Markdown 文件解析 Pandoc JSON AST：活动本地链接共 191 个，断链 0；非法控制字符 0。四份核心材料仍有 C-E01—C-E12/A-E01—A-E12 各 12 个唯一标题并按 01—12 一一对应。

## 6. 授权与证据边界

固定 Python 环境未安装 DeepH、e3nn、ASE 或 pymatgen；阶段 E `requirements.txt` 仍只包含精确固定的 `numpy==2.3.5` 与 `scipy==1.18.0`。代码和四份核心材料继续保持：

- M8 前不安装 DeepH/e3nn；
- 不下载正式训练数据，不生成 DFT 标签；
- 不选择材料体系、DFT/数据后端、DeepH 软件对象/实践版本、训练预算或高级物理实践范围；
- 上述字段维持 `UNRESOLVED_M8`；
- M8 集中冻结后，M9 正式安装、数据下载或复现实验前仍需用户再次明确授权。

本轮通过只证明冻结的阶段 E 教材—推导—题解—合成代码—失败样例对象链达到材料完备、可自学和可验证。它不能外推为真实 DeepH、材料、DFT、正式标签、实践 cutoff、真实训练成本、SOC/磁性或硬件方案已经验证。

## 7. 最终许可

| 稳定问题 ID | 原严重度 | 当前状态 | 新增问题 |
|---|---|---|---|
| `M7-SESS-B01` | BLOCKING | CLOSED | 无 |
| `M7-SESS-B02` | BLOCKING | CLOSED | 无 |
| `M7-SESS-B03` | BLOCKING | CLOSED | 无 |
| `M7-SESS-B04` | BLOCKING | CLOSED | 无 |
| `M7-SESS-B05` | BLOCKING | CLOSED | 无 |

最终计数：`BLOCKING=0`、`NON_BLOCKING=0`、新增问题 0、剩余问题 0。

因此第一次定点复核判定 **PASS**，明确允许将 M7-10 标记为 `COMPLETED`，并允许启动 M7-11。后续审计仍应继续维持同一零问题门控及 M8/M9 禁止项。
