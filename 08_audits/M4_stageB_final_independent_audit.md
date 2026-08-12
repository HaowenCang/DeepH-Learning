# M4-09 阶段 B 正式独立材料总审计

## 1. 审计结论

**总判定：PASS。** 当前快照 `BLOCKING=0`，非阻塞项为 0。允许将 M4 标记为 `COMPLETED`，并允许将 M5 标记为 `READY`。

BLK-03 仍是跨阶段未决决策，但仅在 M5 继续限定为理论材料、后端无关推导、合成数据与可逆 Python 用户态实现时允许带入，不构成 M5 材料建设的阻塞项。该例外不授权安装 DeepH、下载正式训练数据、生成正式 DFT 标签，也不授权选择材料体系、DFT/数据后端或实践软件版本。

## 2. 独立性、门控依据与快照

本审计由未参与阶段 B 材料编写和既有分项审计的新独立子 agent 执行。审计过程没有修改教材、推导、例题、练习、代码、工作包、门控包或台账；本文件是唯一新增产物。既有分项审计仅用作定位信息，没有被机械相加为通过结论。

正式门控依据为：

- `08_audits/M4_stageB_gate_packet.md`，本次复算 SHA-256 为 `F97132B247E0FC6356E831967CC12A48175C6C55B1119D95E234B4114EEA222C`，与任务指定值一致；
- `08_audits/M4_stageB_work_package.md`，本次快照 SHA-256 为 `1CC2F1879344352231EBCCD503F93EBB8B16E979CA1A627633BEF3AD7DEB7351`；
- D-010 材料建设模式及 M8/M9 双重授权边界；
- 工作包 D-B01—D-B06、T-B01—T-B10 及四章知识范围、来源边界和公式条件。

## 3. 逐维度重新判定

| 审计维度 | 判定 | 当前快照证据与判断 |
|---|---|---|
| 阶段 B 统一约定 | PASS | `stageB_conventions.md` 明确冻结列基、bra/ket 方向、cell-phase Bloch 和、正变换 `exp(+ikR)`、逆变换 `exp(-ikR)/N`、有限 BvK 对、实空间共轭配对、中心规范及有限/无限边界；第 2、3、4、9 章未另立冲突约定。 |
| 第 2 章：态、算符与矩阵表示 | PASS | 对象层级、复比例等价类与归一化、矩阵元、Gram 矩阵、期望值、有限投影与完整问题的区别均明确；`Phi'=Phi A`、`c'=A^{-1}c`、`H'=A^dagger H A`、`S'=A^dagger S A` 的方向、形状和非 unitary 边界一致。解析例题同时覆盖正确合同变换与遗漏 overlap 的确定性失败。 |
| 第 3 章：Hermitian-definite 广义本征 | PASS | 主线始终限定 `H=H^dagger`、`S=S^dagger>0`。Gram 正定当且仅当有限基线性无关；投影与 Rayleigh 商两条推导闭合；实谱、不同本征值的 S 正交、简并边界、Cholesky 和对称正交化的变量替换与逆映射均成立。完整 S 正交本征基由标准 Hermitian 谱定理及可逆映射建立，而不是由逐对正交关系单独推出。 |
| 第 3 章：前后向误差 | PASS | 给出保持 Hermitian 结构的显式 `Delta H`，明确小归一化残差只提供附近矩阵束的后向解释；本征值包含界、谱分离量、向量角度界和 `sqrt(kappa_2(S))` 返回放大均写出适用条件。谱隙为零或很小时转为不变子空间比较，没有用小残差无条件推出小逐带误差。 |
| 第 4 章：周期、Bloch 与 Fourier | PASS | 主动平移本征值负号与坐标 Bloch 条件正号区分正确；有限角色正交、Bloch 和归一化、不同 k 块解耦、闭合正逆变换及 `1/N` 位置逐式成立。有限和、无限积分、有限采样和实空间截断分别标记。 |
| 实空间 Hermiticity | PASS | 从冻结的 `H_ab(R)=<a0|H|bR>` 推出 `H_ab(R)^*=H_ba(-R)`，矩阵 dagger 同时包含复共轭和指标交换；H 与 S 全程同步。非零块不被错误要求自身 Hermitian，缺少共轭块的失败由真实计算捕获。 |
| 中心规范与 `k+G` | PASS | cell-phase 中基严格倒格周期；中心规范以对角 unitary `U(k)` 同步作用于 H、S 和系数，并明确 `D_G`、单带整体相位及简并子空间幺正混合边界。只变 H 的错误不能被解释为规范自由。 |
| 第 9 章：实空间矩阵到能带 | PASS | `H(R),S(R) -> H(k),S(k) -> E_n(k),c_n(k)` 对象链完整；每个 k 点先检查 Hermiticity 与 `S(k)>0`，再求解并检查逐本征对归一化残差和 S 正交。逆变换、只保存本征值无法反演矩阵、截断与采样分离、简并带簇比较和矩阵扰动 `Delta H-E Delta S` 均有条件说明。 |
| 一般可逆与 unitary 残差边界 | PASS | 任意可逆合同变换保持广义谱、精确方程、S 正交性，残差向量按 `r'=U^dagger r` 协变；材料明确否定一般非 unitary 变换对冻结 Euclidean 归一化残差标量的不变性，并用 `diag(0.1,1)` 反例给出 `0.70710678 -> 0.09950372`。只有 unitary 情形保持该标量。 |
| 原始 DeepH 对象分工 | PASS | 第 9 章只对 DH-01 原始论文陈述：模型预测 H，S 由局域基函数重叠低成本获得，二者 Fourier 组装后求解广义本征问题；明确不自动推广到现代软件。独立从本地 DH-01 PDF 提取正文复核了该对象分工，PDF SHA-256 与来源台账一致。 |
| 来源与证据边界 | PASS | 四章 `sources.md` 对 `PRIMARY_EXPLICIT`、`DIRECT_DERIVATION`、`PEDAGOGICAL` 作出可辨区分。教学矩阵、条件数扫描、带差和截断差没有外推为真实材料统计；来源没有被用于猜测现代软件字段、文件格式、轨道排序、材料参数或误差分布。 |
| D-B01—D-B06 推导包 | PASS | 总索引能定位全部六项推导，条件、依赖和失败边界闭合。H/S 合同变换、Hermitian-definite 完整本征基、实空间共轭配对、Fourier 相位与 `1/N`、中心规范、截断/采样和残差边界跨文件一致。 |
| 四章分层练习与解答 | PASS | Q2-01—08、Q3-01—10、Q4-01—10、Q9-01—10 的问题/解答 ID 严格一一对应；条件、机制、误区和验证入口均可定位。参考解答没有省略非法 S、显式逆、简并、缺共轭块、忽略 S、同号逆变换或非 unitary 残差反例。 |
| 综合练习 | PASS | C-B01—C-B08 的问题/解答 ID 严格一一对应，完整覆盖对象语义、正定性、广义本征、一般可逆/unitary 边界、Fourier 闭合、中心规范、截断/采样、失败诊断、复现命令、来源和授权边界。 |
| 例题与失败样例 | PASS | 第 3、4、9 章嵌入式 Python 块均从当前 Markdown 直接提取执行，所有断言通过；失败样例通过数值下界或异常消息强制断言，不是只打印结果。 |
| T-B01—T-B10 代码门控 | PASS | 固定环境、5 项 unittest、两组 JSON CLI 全部实际通过；两组均包含版本、种子、维数、N_k、容差、全部测试、预期失败和 `conventions_version="stageB-v1"`，且 `overall_pass=true`。 |
| 可自学性 | PASS | `stageB_self_study_guide.md` 形成 B1—B4 的前置条件、正文、推导、例题、问题、答案、自动测试和失败诊断顺序；D-B/T-B/C-B 映射及答案定位闭合，不要求学习者提交闭卷、口头或阶段自测。取消本人作答没有缩减内容和验证强度。 |
| D-010 与授权边界 | PASS | `decisions.md`、`unresolved_decisions.md`、教材、代码说明和综合题一致保持 M8 前禁令及 M9 再授权点。阶段 B 依赖仅为固定 Python 用户态 NumPy/SciPy，输入均为解析或合成矩阵；未发现 DeepH 安装、正式数据、DFT 标签或隐含材料/后端/实践版本选择。 |

## 4. 实际执行的环境、测试与数值

固定解释器为：

```text
C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

实际版本为 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0；`requirements.txt` 精确固定 `numpy==2.3.5`、`scipy==1.18.0`。

实际执行：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m pip check
& $py -m unittest discover -s 05_code_exercises/stageB_periodic_nonorthogonal -p 'test_*.py' -v
& $py 05_code_exercises/stageB_periodic_nonorthogonal/run_experiments.py --format json --seed 20260803 --dimension 6 --nk 64
& $py 05_code_exercises/stageB_periodic_nonorthogonal/run_experiments.py --format json --seed 20260804 --dimension 4 --nk 32
```

结果：

- `pip check`：`No broken requirements found.`；
- unittest：5/5 通过；
- 两组 CLI：T-B01—T-B10 全部 `status=pass`，`overall_pass=true`。

两组关键指标如下：

| 指标 | seed 20260803, M=6, N_k=64 | seed 20260804, M=4, N_k=32 | 门控 |
|---|---:|---:|---:|
| T-B01 最大归一化残差 | `3.2146632447e-15` | `2.8994214283e-15` | `<=1e-12` |
| T-B02 S 正交 Frobenius 残差 | `1.9069866917e-14` | `1.4067253155e-14` | `<=1e-11` |
| T-B03 一致合同谱差 | `1.4210854715e-14` | `3.1974423109e-14` | `<=1e-11` |
| T-B05 最大块重建误差 | `4.4408920985e-16` | `2.2204460493e-16` | `<=1e-12` |
| T-B06 最大 k 空间反 Hermitian 残差 | `5.3971928267e-16` | `3.4233439371e-16` | `<=1e-12` |
| T-B07 最大能带归一化残差 | `5.4229969900e-16` | `4.3541041261e-16` | `<=1e-11` |
| T-B07 最小 S(k) 特征值 | `0.8275735931` | `0.8275735931` | `>1e-3` |
| T-B08 中心规范谱差 | `1.7763568394e-15` | `1.7763568394e-15` | `<=1e-11` |
| T-B10 unitary 变换谱差 | `8.8817841970e-16` | `2.2204460493e-16` | `<=1e-11` |

默认配置中实际执行并捕获的负例包括：非正定 S 被拒绝、非 Hermitian H 被拒绝、只变 H 的谱差 `10.0558014942`、小特征值诊断触发、同号 Fourier 逆变换误差 `0.4222916110`、缺共轭块残差 `0.6832032925`、忽略 S 的能量差 `0.2259113111`、单边中心规范谱差 `0.0201663515`、删除 `R=+/-2` 后 64/128 点带差分别为 `0.1611400516`/`0.1613526451`、单边置换反 Hermitian 残差 `1.6067066718`。第二配置的对应负例也全部实际达到下界并被断言捕获。

三份嵌入式确定性脚本的直接执行结果为：

- 第 3 章：广义谱 `(0.8452994616, 3.1547005384)`，`cond(S)=3`，结构保持后向扰动消去残差为 0，`||rho||=0.0444115592`，角度正弦 `0.0192343275`；
- 第 4 章：Fourier 重建误差 `4.0412728104e-16`，同号逆变换误差 `0.2336510054`，缺共轭块虚部 `0.2779946476`，同步规范谱差 `8.8817841970e-16`，只变 H 谱差 `0.0822892958`；
- 第 9 章：H/S 最大反 Hermitian残差 `1.6890185701e-16`/`1.6273148661e-17`，最小 S 特征值 `0.8479319626`，最大逐本征对归一化残差 `6.3936068976e-16`，S 正交残差 `1.2572532604e-15`，128 点截断差 `0.1613526451`，忽略 S 差 `0.1799426913`，缺共轭块残差 `0.1379651652`。

## 5. 35 份活动 Markdown 静态与实际渲染检查

活动集合按门控包口径组成：`stageB_conventions.md`、阶段 B 自学导航、四章各四份 Markdown、五份推导 Markdown、五组问题/解答、代码 README 和 M4 工作包，共 35 份。

本地链接检查使用各 Markdown 所在目录解析相对路径，并排除 HTTP(S)、`mailto:` 与纯锚点：

```text
files=35
local_links=70
broken_links=0
```

控制字符检查范围为 C0 控制字符（保留制表、换行和回车）及 DEL：

```text
control_files=0
```

实际 Pandoc 命令口径为：

```powershell
pandoc --from=markdown+tex_math_single_backslash+tex_math_double_backslash `
  --to=html5 --mathml --fail-if-warnings <file>
```

35/35 份文件退出码均为 0；对 HTML 实际统计 `<math>` 节点合计 1,574。第 2 章 `sources.md` 不含 TeX 数学表达，故其节点数为 0；其余文件均产生实际 MathML。不存在仅凭 Pandoc 退出码推断公式已渲染的情况。

问题/解答 ID 的程序化比对结果为：Q2 8/8、Q3 10/10、Q4 10/10、Q9 10/10、C-B 8/8，顺序与集合均严格相同。

## 6. 来源独立抽查

本地原始 DeepH 正文 `01_sources/papers/li_et_al_2022_deeph.pdf` 的 SHA-256 为 `92C5A783B46475634A17D2D5F6557D8DE68D2F789F8DFB66182F56862580EC61`，与 `01_sources/README.md` 冻结值一致。使用本地 `pdftotext` 对式 (7)—(9) 附近重新抽查，正文明确区分：DFT Hamiltonian 可由 DFT 自洽计算获得或由 DeepH 预测；overlap 由基函数内积以很低计算成本获得，无需神经网络学习；二者 Fourier 变换后求解广义本征问题。第 9 章对该来源的使用没有超出这一原始工作流，也明确阻止向现代软件任务分工泛化。

FND-01—FND-06 在四章 `sources.md` 中均以版本、章节或页码限制用途。当前材料把其支持的定义与问题类别和教材的直接代数推导分开；合成模型显式标为 `PEDAGOGICAL`。未发现把来源未支持的软件或材料结论写成事实的情况。

## 7. 当前审计快照 SHA-256

以下哈希覆盖 35 份活动 Markdown、门控包、三个 Python 源文件、精确依赖、D-010/BLK-03 决策边界和独立抽查的 DH-01 正文；不包含本审计报告自身。

| 文件 | SHA-256 |
|---|---|
| `00_scope/unresolved_decisions.md` | `92B403FE7B09A3BB1A3A7C45F355D3498198F5DB5F2E70B711D0FAB0E24C6A60` |
| `01_sources/papers/li_et_al_2022_deeph.pdf` | `92C5A783B46475634A17D2D5F6557D8DE68D2F789F8DFB66182F56862580EC61` |
| `03_textbook/stageB_conventions.md` | `66A135C38DBA8536D88701ED85DEBAE51D60A3E48CD0D09DFBBB463A2240B464` |
| `03_textbook/chapters/stageB_self_study_guide.md` | `4AABD96EE6154CBA163B7D4657C2AE4BDC23A791E3E22772E0285ACCE3DAA3F4` |
| `03_textbook/chapters/02_quantum_states_operators_matrices/sources.md` | `4CCC8273FFC9936B8BEC76F2994E0D443E3CDFCD5C29BB12AEDD210C3396220B` |
| `03_textbook/chapters/02_quantum_states_operators_matrices/outline.md` | `AF0FFCFC48C716A19DF3156B861F965D137157994A2ACE55E336E867BC437033` |
| `03_textbook/chapters/02_quantum_states_operators_matrices/chapter.md` | `58CC87B9E66399F3E8B1FFB202CCA6BBAFA2D3BCE2E8263CDF9F5A0AE53CE46D` |
| `03_textbook/chapters/02_quantum_states_operators_matrices/examples.md` | `2EC9C4EAA847DCEA7742E10D9C29EFFCA2943CB0B5B7F9E96C3D25DBFF495C55` |
| `03_textbook/chapters/03_nonorthogonal_generalized_eigen/sources.md` | `0042B83F9772E77590BC5C69F3F73CC79251A2A648DD67A734DA1B1FEE532F20` |
| `03_textbook/chapters/03_nonorthogonal_generalized_eigen/outline.md` | `F55F00EEA3D3ED8ED7F798B2D12FA9C13215A6F52878D9B6BEAD006EA1D92BEB` |
| `03_textbook/chapters/03_nonorthogonal_generalized_eigen/chapter.md` | `A00F0172280F02D3DD9553248A50492D08715FD31889A58BC11121DF3A2A5AD2` |
| `03_textbook/chapters/03_nonorthogonal_generalized_eigen/examples.md` | `716ED6531FAE27D18E6F4EA5B182D569C83A5120F56A85F77261D22EC0169E4A` |
| `03_textbook/chapters/04_periodicity_bloch_reciprocal/sources.md` | `FE3B31F4CE7FD46ECF83189BE4A1CE9BDE4960C0EBDDB749F81D90E2DC64A713` |
| `03_textbook/chapters/04_periodicity_bloch_reciprocal/outline.md` | `AB169D1B55DB1C2A08430D08E9EB562BAC720FBEC90EC7953D1484909AF6A736` |
| `03_textbook/chapters/04_periodicity_bloch_reciprocal/chapter.md` | `87CCA024540FAD83B3A361D6DCA3C146C755D9DA2B8F78E33E18FFE96640C536` |
| `03_textbook/chapters/04_periodicity_bloch_reciprocal/examples.md` | `B00858D4C8B4D8B065B2CE37455D0412F21917322C8E6D7D584C0D36CC2A02F4` |
| `03_textbook/chapters/09_realspace_hamiltonian_bands/sources.md` | `67E928397574EDEC2DFDCC70B4F88B785E5615F9DDDC3EB077B1504FA69BBAD8` |
| `03_textbook/chapters/09_realspace_hamiltonian_bands/outline.md` | `E4F9B0E97ACE5629FA1BD6B3CDA1BF4A438945AFF7828D775C46B4CCA0865B66` |
| `03_textbook/chapters/09_realspace_hamiltonian_bands/chapter.md` | `CC0FF72250FF2B534241E09EFE8FB1903FED5D17D2C4B2701C6BF0F429B842F2` |
| `03_textbook/chapters/09_realspace_hamiltonian_bands/examples.md` | `1248AF0EF3D7B81665EA801F9A448A5DACFA79232F303B8AD98C05E9A6F90565` |
| `04_derivations/stageB/README.md` | `EB7B76E52FF9ABB3FBC1CD17A4605DFFC115D7F400EA5342DFCF1D932C8EBD69` |
| `04_derivations/stageB/02_basis_representation.md` | `0859F50F9F84E31139FC8925A892DD817E57233F65D0552B1081AA828147D808` |
| `04_derivations/stageB/03_generalized_eigen.md` | `ECF2F635F709F0EEA55CB1E4D3D549599F1EC0315765E3F9455F443ED5AFF8DB` |
| `04_derivations/stageB/04_bloch_fourier.md` | `BC11144E9CF6279C04ED0708191FC34DCECD81508F5149CDD1CDF3D4A7653D42` |
| `04_derivations/stageB/09_realspace_to_bands.md` | `29073B18123E83ABE171B5C57ADEA0A99117EB4932F67D6FE3F834746CA8C43D` |
| `05_code_exercises/stageB_periodic_nonorthogonal/README.md` | `64A7D25D5F7A3573DAA11081544EB27E8F5D1A29881ADA996E8FE6CFA56D2E0A` |
| `05_code_exercises/stageB_periodic_nonorthogonal/requirements.txt` | `CC3EFBCD187C80ADDD5DB987EE90AD17BD481814985761D7B5CFAC3F0B5E10E4` |
| `05_code_exercises/stageB_periodic_nonorthogonal/stageb_models.py` | `AD3ED1BB247BEC85968D8579DFCE5A47969BBE7BB6A4CB561CD1E1CC8A48D9E7` |
| `05_code_exercises/stageB_periodic_nonorthogonal/run_experiments.py` | `2CC7495B4F82482E788CC1C6F37E50B5A425B8E27E9905953C0CE43652EA485C` |
| `05_code_exercises/stageB_periodic_nonorthogonal/test_stageb_models.py` | `BED69908166B2B1B900BBA63C58525AA33DF2710986315551CE2FF7B4D50F03A` |
| `06_exercises/02-stageB/02_basis/problem/readme.md` | `FB25D9B7DACD1E93F5FCACA2A3E492524EAC3FEF71B803BE9D671B84DF20C83A` |
| `06_exercises/02-stageB/02_basis/solution/readme.md` | `ACE6C6DF332625E0BC9A882B7EB70A856BD34BE4B3193E5BF30C63E12366F320` |
| `06_exercises/02-stageB/03_generalized_eigen/problem/readme.md` | `E91C44B303238CAE2E562FDCF469DDFC5AFD2E2205999C701FC153AD9ABF9D7A` |
| `06_exercises/02-stageB/03_generalized_eigen/solution/readme.md` | `71978C21FA8BE89CB274E8744998241171B52CAAD5A1DCE386D56195BB189027` |
| `06_exercises/02-stageB/04_bloch_fourier/problem/readme.md` | `639302138F7372F9C0EB683B6E61D0A908D6337066BAC39C93D250979C035F73` |
| `06_exercises/02-stageB/04_bloch_fourier/solution/readme.md` | `87914B10D9B66B31FD9C26BB61A216410A4033F9AA3A44F8D5906B6CC1396D77` |
| `06_exercises/02-stageB/09_realspace_bands/problem/readme.md` | `0EEC018076BADDC943E3F5BD8CF4235590628FF04549A518FA5B458C1A3BAB8C` |
| `06_exercises/02-stageB/09_realspace_bands/solution/readme.md` | `54A6BF3AF7EA5D2C487A2173CE3C558BE96BC2DCB83EFAF710B6161751A558DB` |
| `06_exercises/02-stageB/comprehensive/problem/readme.md` | `DE8BA796413AF298F76E80169D8EA4C1EEF15D80C16FFD020D09E81BB9C28160` |
| `06_exercises/02-stageB/comprehensive/solution/readme.md` | `DE0962FBDA3F1006EA488CA67492DC181FCA21061C7D7F2E89FBB81D328FB4C2` |
| `08_audits/M4_stageB_work_package.md` | `1CC2F1879344352231EBCCD503F93EBB8B16E979CA1A627633BEF3AD7DEB7351` |
| `08_audits/M4_stageB_gate_packet.md` | `F97132B247E0FC6356E831967CC12A48175C6C55B1119D95E234B4114EEA222C` |
| `decisions.md` | `072992EFCA9474B738CB48E7C18F85342FDDC4ABA7D25F62EB572552E429455C` |

## 8. 阻塞项、非阻塞项与阶段许可

### BLOCKING

无。`BLOCKING=0`。

### 非阻塞项

无。

### 允许带入的跨阶段缺口

BLK-03 的计算资源、DFT/数据后端、DeepH 软件对象、首个材料体系、时间与训练预算和高级物理范围仍未冻结。依据 D-010，该缺口可以带入 M5—M7 的理论、教材和合成数据材料建设；一旦工作内容需要安装 DeepH、正式数据、DFT 标签或隐含选择上述对象，BLK-03 立即恢复为阻塞，必须等到 M8 集中决策及 M9 前明确执行授权。

### 最终许可

- **允许 M4：`COMPLETED`。**
- **允许 M5：`READY`。**

