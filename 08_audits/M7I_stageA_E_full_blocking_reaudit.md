# M7-I 阶段 A—E 全量独立总审计第一次定点复核报告

- 复核日期：2026-08-11
- 复核角色：D-011 指定的 M3—M7 唯一独立跨阶段总审计员
- 复核轮次：M7-I 第一次定点复核
- 原审计报告：`08_audits/M7I_stageA_E_full_independent_audit.md`
- 原审计报告实测 SHA-256：`A2F8601962AE0DE7EDD3E9F6922947BBC33356CC171CF85EE1F7DAF78CB414B0`
- 历史格式勘误台账：`08_audits/M7I_historical_audit_format_corrections.md`
- 勘误台账实测 SHA-256：`B012DAE1F26A2D5AB458BEBB72CF071A3B57E6A712F6FFECACA7CB64EF1A3234`
- 被审快照：除本报告外 427 个文件，其中 Markdown 294 份
- 快照清单算法：相对 POSIX 路径、制表符、文件大写 SHA-256、LF，按相对路径升序，以 UTF-8 汇总后再次计算 SHA-256
- 被审快照清单 SHA-256：`72064C5EEF56AA553CA99F0F6807912B69055832E7A42690D1031296EF2C274B`

## 1. 最终结论

**最终判定：PASS。**

- `M7I-N01`：`CLOSED`
- `M7I-N02`：`CLOSED`
- `M7I-N03`：`CLOSED`
- `BLOCKING=0`
- `NON_BLOCKING=0`
- 真实数学、物理、数值、代码、来源或授权边界回归：0
- 新发现问题：0
- 新增及剩余问题：0

三项原问题均满足首次审计规定的全部最小关闭条件。全工作区 294/294 份活动 Markdown 的 Pandoc JSON AST 与 HTML5 MathML 严格转换通过，Math 节点为 12,174，Raw TeX 节点和非法控制字符均为 0；当前 AST 本地文件链接为 617 个，文件断链和片段断链均为 0。固定环境、57 项自动测试、全部冻结 CLI、来源快照、schema、provenance、payload、哈希、确定性、失败矩阵和跨阶段高风险数学对象均未见回归。

因此，M7-I 可以完成，并且只允许进入 M8 候选方案的集中提交。该结论不冻结任何 M8 选择；计算资源、DFT/数据后端、DeepH 软件对象、首个材料体系、时间与训练预算和高级物理范围仍须由用户明确冻结。即使用户完成 M8 冻结，M9 的 DeepH 或正式 DFT 软件安装、正式数据下载、DFT 标签生成和复现实验仍须另行取得第二次明确授权。

## 2. 独立性、范围与只读边界

本轮没有用主 agent 的修复自检代替定点复核，也没有用 M3—M7 的既有 `PASS` 代替相邻回归检查。复核逐项覆盖：

- N01 的四个文件、六个表达式、Raw TeX AST 和目标 MathML token；
- N02 的 17 份历史审计、旧/新 SHA-256、公式语义、稳定问题 ID、结论、许可和迁移链；
- N03 的来源数量、M3/M5/M6/M7-09 状态、28 处阶段 E 同义未来时态、根导航和活动台账；
- 294 份 Markdown 的严格转换、数学节点、链接、UTF-8 和非法控制字符；
- 中央 CSV、BibTeX、23 个来源快照及其哈希、PDF 可读性和来源边界；
- 固定解释器、五份 requirements、57 项测试、12 个冻结 CLI、失败矩阵和确定性输出；
- 广义本征与非正交基、Bloch/Fourier/规范、标签 provenance、周期图/普通 MPNN、实表示/复表示/CG、Hamiltonian/局部架、SU(2)/时间反演；
- D-010 材料建设强度、D-011 总门控、BLK-03 及 M8/M9 双授权边界。

工作区不是 Git 仓库，故采用全文件内容清单控制只读边界。本报告写入前，按报告首页所列算法得到 427 文件清单 SHA-256 `72064C5EEF56AA553CA99F0F6807912B69055832E7A42690D1031296EF2C274B`。本轮没有修改任何被审材料、代码、状态文件、初审报告、勘误台账或依赖；唯一新增文件为本报告。

## 3. M7I-N01 定点复核：CLOSED

四个文件中的六个原缺陷位置现为：

| 文件与位置 | 当前表达式 | AST/MathML 结果 |
|---|---|---|
| `00_scope/master_execution_plan.md:245` | \(H=H^\dagger\) | Math 节点；`<mo>†</mo>` 存在 |
| `00_scope/master_execution_plan.md:246` | \(S\succ0\) | Math 节点；`<mo>≻</mo>` 存在 |
| `03_textbook/chapters/13_message_passing_networks/chapter.md:197` | \((E,P_{\max})\) | Math 节点；`<mi>max</mi>` 存在 |
| 同文件 `:240` | \(Y=\tanh Z\) | Math 节点；`<mi>tanh</mi>` 存在 |
| `05_code_exercises/stageD_synthetic_mpnn/README.md:28` | \(2\times10^{-2}\) | Math 节点；`<mo>×</mo>` 存在 |
| `06_exercises/04-stageD/13_mpnn/solution/readme.md:74` | \(2\times2\) | Math 节点；`<mo>×</mo>` 存在 |

四文件分别以 Pandoc 3.6.4、`markdown+tex_math_single_backslash`、JSON AST 和 HTML5 `--mathml --fail-if-warnings` 独立转换，退出码均为 0；四文件 Raw TeX 总数为 0。逐个依据 `application/x-tex` annotation 锁定目标 Math 节点后，上表五类 token 全部存在。公式的 TeX annotation 与首次审计读取的原表达式一致，修订只增加合法数学定界，没有改变等式、关系、shape、指数、阈值或矩阵尺寸。N01 的表现层丢义已经消除，故判定 `CLOSED`。

## 4. M7I-N02 定点复核：CLOSED

### 4.1 旧/新哈希与活动身份

勘误台账自身实测 SHA-256 与送审值完全一致。对台账 17 行逐行解析，并直接重算当前文件字节哈希，得到 17/17 匹配：

| 文件 | 首次审计历史字节 SHA-256 | 当前规范 SHA-256 | 当前复算 |
|---|---|---|---|
| `M7_chapter19_independent_content_audit.md` | `B1F73448945E366DA756AB65168D3F0BCA62C3CC126CCD3756E96D33CB6703EA` | `8F2F2717B5994694FE3413CB62AA8D40734AE0BBF999336EDDBF279818F8ED81` | 匹配 |
| `M7_stageE_work_package_second_reaudit.md` | `C1DADFEB238F351167B047070159982CE9C5806185B039BD50D410AB7C66D003` | `AD85EED908F5015A18156785B10CA6E3303EA14C7ED5F2F2BC1A2B0EFEC4C858` | 匹配 |
| `M7_stageE_work_package_independent_audit.md` | `58BB3A2C91A49B8DE8938C22C2DD4ECDA5332E59050EE0783CEBCB68BF0781E5` | `FC814A560AB80CBD38FFB0CEA7B273E6747EDEAB4149D4726C766A9AABDD1D9D` | 匹配 |
| `M4_stageB_work_package_independent_audit.md` | `6D2FF43BBC3A9E36218D9820E8E4F59EB0F7A2DAE98918EC66667F95D1965A3D` | `DD49D3DD6ADA8F9A349C37522D76BBECA85EF5EA5291B83AB47A43A804BBE78C` | 匹配 |
| `M6_stageD_work_package_blocking_reaudit.md` | `A2D1EC1DFC81FF6E5F4D94E86222FDDC41EE6CDCB34E35FEEE7B5866ACF94D99` | `35927C808E912283B897219BF5A4FB4639F7446A3E061B69A143BAA261F33F4D` | 匹配 |
| `M2I_chapter1_independent_content_audit.md` | `41A2F0C31C1A285F819BF63872DF9DA1F93888E502449554B5117BE660656F4C` | `64146624C085AB71C1B705693527AD8645FFE5DC8657B3FCFF4933E68E1CB526` | 匹配 |
| `M7_stageE_work_package_blocking_reaudit.md` | `69B3B7DBD9349C6BA68EF136D89DCECAFBBD41ED6367797B137F59582FDA87BB` | `78CC977013F9335299F8E30B98337F0E84438E2A8759C8D994E1BD40EF27B6A9` | 匹配 |
| `M7_stageE_self_study_independent_audit.md` | `B5E42923B490528ABEB39DFA716BCA04499EE2EA53355C356B96B13EC5EF66F1` | `DB770870B98B1D96810FD35DE6139086489F74313FB19F1FB9CFACDE27D3058E` | 匹配 |
| `M4_stageB_work_package_blocking_reaudit.md` | `3AB104D6AFBCDB3BC903A18DD2E8C25CFAD1342985519C9B8C7E54FC71011409` | `A735EC4D6EEE9B06335A34488647EDB2AC53990EE04EE442338988A1BC426342` | 匹配 |
| `M4_stageB_self_study_independent_audit.md` | `D3471EAF5F73E31A35CC91EB6EFDF1B5EB90ED59926BBC02A92DF3FAFABADE85` | `E295F7F9002735C915476C27E040616C7034A2949E5B28E17EF9BFDAE0C03134` | 匹配 |
| `M4_stageB_code_independent_audit.md` | `2BAD93B07EF77BE83B7B50C46247B0FA4310751FB7804D712E16FC66EC34FB63` | `9D83F3C437ABD8D5007A9FFA77BD7C28338BE152AEAA9154536BCBD351465BBD` | 匹配 |
| `M7_stageE_self_study_blocking_reaudit.md` | `7FDD7F3ED4A1DD8855839D3EC4C5A5EE87A3D0652EE726949BE34F2338D86B14` | `19454ED77B4EFA9F7C0C3C87E5777737C2C1B4CF16B44A9DA1BA863CAB1F02D0` | 匹配 |
| `M4_chapter3_independent_content_audit.md` | `85B18C46B968A311C391CD3E3B288AF48C67A758F719AC5DDD94661EA01E36B2` | `B404C62518FBF82FCA77587FFBDCDB89D330D3A85D404F743E26350D75FBF2AF` | 匹配 |
| `M5_stageC_final_blocking_reaudit.md` | `424EE8199A68B02C7DA74B7FA1298347AFB193C4658CEAA683365777F24C60AB` | `BEF823F47EFC89A093F1465159E78BCA7296E52A4D630F5D92CD51E0412C5283` | 匹配 |
| `M6_stageD_work_package_independent_audit.md` | `08919E2AC20B46D9286ABD0E3C1F8F9D93958546103ABD9283DA4A8D6FD67F0A` | `D7791462F33CAD1F6E2639EDC14FB60EC07FF03F99B6BCAE3C11342157F0F839` | 匹配 |
| `M6_chapter12_blocking_reaudit.md` | `780B1C89630AC0C3F70876EF9D0856AD0B6E55817345CFE8837F2A50F17AEAB1` | `E21464380C61DCD65AD9DE7BE57BBFFCB55E9A0B50D78594DE8A48204AE78124` | 匹配 |
| `M6_chapter12_independent_content_audit.md` | `BE571B767367B91BB3471C3F6D0BA14FBB5CDF181C215C7E0397BFB4C72C7EC0` | `2DD0A297496518BC76F34374B816173D32028BF8BD4CD98758F60525F9CB970E` | 匹配 |

17 个历史哈希与本审计员首次审计时的逐文件读取记录一致；其中 7 个还可由现行进度台账或后续审计中的完整哈希独立交叉锚定。当前活动身份均与台账的“当前规范 SHA-256”一致。根 README 直接链接勘误台账；台账再由每一当前规范身份映射到首次审计历史字节身份，故活动状态可以无歧义回溯旧字节快照。

### 4.2 语义、问题 ID 与结论保持

逐份抽取 17 个报告的标题、总结论、`BLOCKING`/`NON_BLOCKING`、稳定问题 ID、问题状态和门控许可，并与首次审计读取记录及其后续关闭链交叉比较，未发现变化。代表性结论签名包括：M7-06 初审 `FAIL/BLOCKING=2`；M7-01 初审 `FAIL/2/1`、第一次复核仍有 B02、第二次复核 `PASS/0/0`；M6-01 初审 `FAIL/3/2`、复核 `PASS/0/0`；M7-10 初审 `FAIL/5/0`、复核 `PASS/0/0`；M5 总审计复核 `PASS/0/0`；M6 第 12 章初审 `FAIL/3/0`、第一次复核 `FAIL/1/1`。这些签名及相应稳定 ID 均保持原值。

公式抽查确认，勘误只涉及数学定界、`\rm` 到 `\mathrm`、`psmallmatrix` 到 `smallmatrix` 和唯一 U+0008 到反斜杠。原 U+0008 位置现正确解析为 \(\bar\Phi_{\mathbf k}=\Phi_{\mathbf k}U(\mathbf k)\)；两份第 12 章报告中的 \(\deg_{\mathrm{in}}\)、\(N_{\mathrm{tot}}\) 和 \(E_{\mathrm{tot}}\) 均生成 MathML。17 个活动报告中不再存在旧 `\rm` 或 `psmallmatrix` 数学命令。未发现数值、符号、索引、单位、dtype、shape、稳定 ID、结论或权限被表现层勘误改变。

### 4.3 活动审计链严格格式

全工作区 294 份 Markdown 的 JSON AST 和 HTML5 MathML 严格转换均为 294/294，Raw TeX 为 0，非法控制字符为 0。因此，不仅 17 份勘误报告，而且首次审计报告、迁移台账、全部阶段审计与活动状态台账均达到零格式缺陷。N02 判定 `CLOSED`。

## 5. M7I-N03 定点复核：CLOSED

根 README 现明确区分“M1 完成时 22 条历史基线”和“当前 CSV/BibTeX 46 条”，并直接导航 M4、M6、M7 最终审计、M7-I 首次审计和历史格式迁移台账。五个目标链接均存在，并已纳入 AST 断链验证。

主执行计划原“当前进入 M5”和“M6 当前推进”已改为带日期的历史执行说明，同时保持 M3—M7 为 `COMPLETED`、M7-I 为 `IN_PROGRESS`、M8/M9 为 `PLANNED`。第 1 章现明确 M3-07、M3-08 及其定点复核均通过；Stage E 代码 README 现以历史顺序说明 B01—B05，并直接链接 `M7_stageE_code_blocking_reaudit.md`，同时保留“主 agent 验证不替代独立审计”的治理边界。第 20 章现明确 T-E11/T-E12、A/B 和失败矩阵已经执行，并链接代码说明与独立放行报告。

对首次审计登记的 28 处阶段 E 同义未来时态逐处交叉核对，当前均已改成“已完成的解析子对象”和“现有 M7-09 代码/独立复核证据”的静态边界。对 `留待 M7-09`、`待 M7-09`、`尚未执行`、`M7-09 将/再/完成后/通过后`、`等待原审计员`、`未来独立`、`执行证据留待` 和 `代码证据留待` 的定向扫描命中均为 0。保留下来的“本推导文件自身不执行 A/B”只是在区分解析文件与既有代码证据，并非声称代码尚未执行。

当前 AST 本地文件链接实测为 617，而主 agent 修复摘要记录 616。差值恰为随后补入根 README 的“历史审计格式勘误与哈希迁移台账”直接导航；该目标存在、解析成功，当前 617 个文件链接和全部片段链接均无断链。因此，这是验证时间顺序造成的合法加一，不是状态、导航或链接回归，不登记问题。N03 判定 `CLOSED`。

## 6. 全域格式、结构、来源与材料强度回归

当前 294 份 Markdown 均可严格 UTF-8 解码；Pandoc 3.6.4 的 JSON AST 与 HTML5 `--mathml --fail-if-warnings` 均为 294/294；JSON AST 与 HTML 输出的 Math 节点数均为 12,174；Raw TeX、非法控制字符、文件断链和片段断链均为 0。

中央来源表仍为 46 行、17 列，46 个 `source_id` 唯一，11 个必填字段逐列缺失均为 0；证据状态为 45 个 `PRIMARY_EXPLICIT` 和 1 个 `SUPPLEMENTAL_ARCHIVE`。BibTeX 有 46 个唯一键，46 键一次性经 citeproc 和 `--fail-if-warnings` 载入，退出码为 0。规范材料使用 39 个来源 ID，未知来源式 ID 为 0。三个来源 README 登记的 23 个快照全部存在且 SHA-256 匹配；18 个 PDF 的 `pdfinfo` 均退出 0、有正页数且未加密，5 个 HTML 可严格 UTF-8 读取。

材料范围未因 D-010 缩减：20/20 章各有 `sources.md`、`outline.md` 和 `chapter.md`，第 2—20 章有 19 份独立 `examples.md`；阶段推导文件 20 份，练习 Markdown 57 份，空 Markdown 为 0。阶段 B—E 的 23 组问题/解答文件含 228/228 个规范化 ID，阶段数分别为 46、60、50、72，逐对零缺失、零额外。N03 的状态性改写没有删除成立条件、解析推导、例题、正反例、章末题、综合题、参考解答、自学导航或自动门控，故 D-010 的知识范围和验收强度保持不变。

## 7. 固定环境、自动测试、CLI 与失败矩阵回归

唯一送审解释器仍为 `C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`。实测 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0；`pip check` 输出 `No broken requirements found.`。五份 requirements 内容均为 `numpy==2.3.5` 和 `scipy==1.18.0`，SHA-256 均为 `CC3EFBCD187C80ADDD5DB987EE90AD17BD481814985761D7B5CFAC3F0B5E10E4`。16 个 Python 文件的 AST 导入面只有标准库、项目模块、NumPy 和 SciPy。

六组测试均以 `-B` 和禁写 bytecode 环境运行：阶段 A 广义本征 10/10、阶段 A Fourier 3/3、阶段 B 5/5、阶段 C 9/9、阶段 D 13/13、阶段 E 17/17，总计 57/57。

每个冻结 CLI 均在两个独立真实子进程中运行，两次退出码均为 0，stdout 字节完全相同，并与冻结 SHA-256 一致：

| CLI | 字节 | SHA-256 |
|---|---:|---|
| A 默认 Markdown | 1,036 | `F13BEBB81BBDAC1D625B173FADBF5610DB6AC70C748B9A28FBCFB4847B68566F` |
| A 默认 JSON | 3,131 | `49ED744484E9D23E0341FA0F33E9F5BCB45BA980C1E7398643C91AEAA41EC187` |
| A size 2 JSON | 3,125 | `CDA2178591F94C94B0432BA05443F1799B9E1A555062A40F8730EF09868AEB39` |
| B 配置 1 | 5,851 | `CDFC94EE71D5B1B2217CF7A045C882C3E302BEAAF62DB0F543834D6E1B8E987E` |
| B 配置 2 | 5,847 | `DA0E815E88958B80253FF00E39B553FB7EF81A986623D0FCB2985C9BBFA261B6` |
| C 配置 1 | 90,083 | `B8470284AD0CE79068DA8F75FB30712ABAF9FFE916A6671ED6C079277A0C1376` |
| C 配置 2 | 90,125 | `6893201DE85F5718E9346A482750977A172F36D9F33523479F38667C6E852E3D` |
| D 配置 A | 12,316 | `2F45DC8C53C1E1D968B3F4633CCC8590540AB8E08667A340054F15F9F3CCA6EE` |
| D 配置 B | 12,373 | `88BF70A4218E2B10C8410644B7B899ECF50A6F6993E83E93C496450069693BD6` |
| E 配置 A | 21,247 | `6A656A18BBFEF042CBCD3049278C15FD0644F4B593D06E44A2B63C5FC78BE856` |
| E 配置 B | 21,301 | `B9E4CA3DE9E671F4F9B674E40B5F62068F3A91E6BA886D4640D3B90AA6FD82D1` |
| E 144 点扫描 | 62,206 | `C13944029E29EF6B47919646952A5D9BDF6A018CEE3F101429FAB09967982A81` |

阶段 C 仍实际拒绝 67/67 个必填路径删除和 47/47 个 schema 负例；阶段 D 的 T-D09/T-D10 分别拒绝 36/36 和 16/16 个故障；阶段 E 的 T-E12 拒绝 63/63 个唯一故障。E 扫描为 144/144 通过，规范 case digest 为 `5317a387bfb026e53dceb31a85074d52ff520448c2fbac9649cb8013064cca7e`，最大残差为 \(1.9468769400071583\times10^{-7}\)，最坏 case 为 `float32-s20260809-r257-m1-a1e+03` 的 rotation 189、\(\ell=2\)。schema、provenance、payload、hash、dtype、shape、mask、padding、H/S partner 和 M8 sentinel 均由实际负例约束，未出现仅靠布尔声明的门控。

## 8. 高风险数学对象独立复算

本轮使用与项目单元测试不同的随机夹具和解析实现复算相邻对象。主要结果如下：

| 对象 | 独立方法与结果 |
|---|---|
| 广义厄米本征 | 复 Hermitian-definite 矩阵束：最大归一化本征残差 \(1.29\times10^{-15}\)，\(S\)-正交残差 \(1.71\times10^{-15}\)，一般可逆合同变换谱差 \(3.11\times10^{-15}\)，中心差分与一阶公式差 \(3.42\times10^{-11}\) |
| 周期 Fourier/规范 | 七点有限循环群正逆误差 \(3.46\times10^{-16}\)，Hermiticity 残差 \(9.35\times10^{-16}\)，最小 \(S(k)\) 本征值 1.8276，轨道中心同步规范谱差 \(4.44\times10^{-16}\)；只改单侧和删除共轭配对的故障分别为 1.744 和 0.428 |
| 周期图/普通消息 | 独立宽盒暴力枚举得到 18 条完整 \((i,j,n)\) 键，与生产图逐键、逐位移一致；代表变换残差 \(4.44\times10^{-16}\)，独立 receiver 聚合普通消息层的节点重编号残差为 0 |
| \(SO(3)\) 实表示 | 独立 STF 基 Gram 误差 \(2.22\times10^{-16}\)，独立二阶张量投影与生产 \(d\) 表逐元素差为 0，群律残差 \(3.36\times10^{-16}\)，实球谐作用残差不超过 \(9.21\times10^{-17}\) |
| CG | 以独立总角动量 \(J^2\) 最高权态和总降算符构造整通道相位；与生产 \(1\otimes1\)、\(1\otimes2\) 表按整通道相位对齐后的差分别为 \(7.77\times10^{-16}\)、\(6.66\times10^{-16}\)，独立 intertwiner 残差分别为 \(2.30\times10^{-16}\)、\(3.05\times10^{-16}\) |
| Hamiltonian/宇称/局部架 | \(4\times8\) 双侧作用与逆边转置残差 \(1.12\times10^{-16}\)，只左作用故障 0.834；反射下极/轴叉积恒等式残差 0；归一化局部架旋转协变误差 \(2.29\times10^{-16}\) |
| \(SU(2)\)/时间反演 | Pauli 旋转误差 \(1.75\times10^{-16}\)；\(\Theta^2=-I\)、Kramers 正交、H/S 的 \(k/-k\) partner 和 \(2\pi/4\pi\) 锚点残差均为 0，广义谱配对差 \(7.85\times10^{-17}\) |

这些结果同时检查了跨阶段公式适用条件、符号/索引、相位/规范身份、dtype/shape 与故障方向；未发现首次审计已经关闭的非正交合同变换、Fourier 相位、周期代表、CG 通道相位、Hamiltonian 两侧作用、局部架归一化或时间反演 partner 问题重新出现。

## 9. 状态关闭链与 M8/M9 授权边界

当前阶段放行证据实测哈希为：M3 `B72215B708D5066413DACF3C136EB5BCABB745A949A717F00406A3A868B0802B`；M4 `534AE8085CF6BCF3B684E59C836B23B0E996E3CF01B3E184DCD62FED623A752B`；M5 当前规范身份 `BEF823F47EFC89A093F1465159E78BCA7296E52A4D630F5D92CD51E0412C5283`，可由迁移表回溯历史身份 `424EE8199A68B02C7DA74B7FA1298347AFB193C4658CEAA683365777F24C60AB`；M6 `2254A958FFD5A132A68DCE9D4C1C3D79F7663EBB1A3E4C7D0013280E5E291E27`；M7 `82954A441DC888C56E2D0F9CB093FADE2C9D9D5247AFD880D8560A4D20D6BC51`。进度台账与这些放行结论一致。

BLK-03 仍在活动阻塞表中，`00_scope/unresolved_decisions.md` 的六类实践选择均未冻结。主计划明确规定 M8 前置条件为 M7-I 通过和向用户集中提交候选；M8 只能由用户确认完成；M9 又要求 M8 已由用户冻结并再次取得正式执行授权。阶段 C/D/E 代码中的实践字段保持 `UNRESOLVED_M8`，真实选择字符串只出现在必须被拒绝的故障注入或禁止名单中。`06_reproduction/` 与 `07_research_ideas/` 均无文件。没有状态、导航、代码或测试绕过 D-011、BLK-03 或 M8/M9 双授权边界。

## 10. 既有关闭事项、真实回归与新增问题

| 类别 | 结果 |
|---|---|
| 首次审计稳定问题 | `M7I-N01`—`M7I-N03` 全部 `CLOSED` |
| M3—M7 既有关闭事项 | 保持 `CLOSED` |
| 真实数学/代码/来源/授权回归 | 0 |
| 新增 `BLOCKING` | 0 |
| 新增 `NON_BLOCKING` | 0 |
| 新增及剩余问题 | 0 |

## 11. BLOCKING

无。`BLOCKING=0`。

## 12. NON_BLOCKING

无。`NON_BLOCKING=0`。

## 13. 门控许可

M7-I 第一次定点复核达到 D-011 的零问题门槛，允许将 M7-I 标记为完成，并进入 M8 候选方案的集中提交与用户决策等待。该许可不等同于 M8 冻结，不代替用户在任何候选之间作出选择，也不授权 M9 的安装、正式数据下载、DFT 标签生成或复现实验。

本报告完成后还须单独执行报告自身的 strict Pandoc/MathML、Raw TeX、非法控制字符、结构和 SHA-256 终检；最终文件 SHA-256 只在审计员回报中给出，避免报告自包含哈希造成自指不可能。
