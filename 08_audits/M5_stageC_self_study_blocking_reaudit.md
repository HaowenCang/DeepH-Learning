# M5-09 阶段 C 自学材料阻塞项定点复核

## 1. 复核身份、范围与结论

- 复核时间：2026-08-04 06:28:17 +08:00。
- 复核角色：`M5_stageC_self_study_independent_audit.md` 的原独立审计员。
- 复核范围：仅复核原报告 M5-09-B01—B03，不扩展为 M5-10 阶段 C 总审计。
- 只读约束：未修改教材、推导、代码、练习、README、工作包、决策记录或进度台账；本文件是唯一新增文件。

**复核结论：M5-09-B01=`CLOSED`，M5-09-B02=`CLOSED`，M5-09-B03=`CLOSED`。新增 `BLOCKING=0`，新增 `NON_BLOCKING=0`。允许将 M5-09 标记为完成，并允许启动 M5-10。**

该许可只解除 M5-09 的三个材料阻塞项，不替代 M5-10 正式独立材料总审计，也不构成 M6、M8 或 M9 的提前授权。

## 2. 复核快照

| 文件 | SHA-256 |
|---|---|
| `08_audits/M5_stageC_self_study_independent_audit.md` | `bdaac96f08f3a4e486b3075a62cded99e3eaccb86e8a81cafcc1529303e301dd` |
| `03_textbook/chapters/stageC_self_study_guide.md` | `6ee83c5c64ac8b095ae742f657a264d78755d2a3c83d776e7b0aa6af0c6b48af` |
| `03_textbook/stageC_label_semantics_template.md` | `5cc2b7778739f7d46e9fab64f8a9605f0d7abfc0a5d107f2a0746d78569438cc` |
| `06_exercises/03-stageC/comprehensive/problem/readme.md` | `6a93b0a90521df3f4514ba387cd0426c451b9122c5949b447c2536a21c3947f6` |
| `06_exercises/03-stageC/comprehensive/solution/readme.md` | `5f7e33ba67e0951eb025f50139227cb848e8c59b6ffb451a93c270b2a7ec2ff2` |
| `05_code_exercises/stageC_teaching_scf/teaching_scf.py` | `597af234a2688cd9cf71d2c501514ee07700a2fb0361026aef4be0221bebd867` |
| `05_code_exercises/stageC_teaching_scf/run_experiments.py` | `746681fc4bba4eee98b89870c6683c6a8251eea28be01b1d8d5fa0d81b1128e9` |
| `05_code_exercises/stageC_teaching_scf/test_teaching_scf.py` | `688956a996a48d4a04280f3a45735b47c5d19cbc21ac9576c73c9b2057ddd59b` |

三个代码文件的哈希与原独立审计快照相同；本轮引用数值的变化来自材料修复，不来自代码门控变更。

## 3. M5-09-B01 定点复核：CLOSED

### 3.1 严格 Pandoc/MathML

对原限定 43 个 Markdown 文档执行：

```powershell
pandoc --from='markdown+tex_math_single_backslash' --to=html5 --mathml --fail-if-warnings -- <file>
```

结果为 43/43 退出码 0、无 warning。除退出状态外，还独立统计 HTML5 中的 `<math>` 节点及 `application/x-tex` annotation：

| 核心文件 | MathML 节点数 | 节点级覆盖证据 |
|---|---:|---|
| `stageC_self_study_guide.md` | 15 | annotation 中可定位 `E_{xc}`、`S`、`H/S`、`\alpha=2`、`\alpha=1`、`k`、`F_{\mathrm L}`、`\rho(M_\alpha)<1`、`H`、`S\succ0`。 |
| `stageC_label_semantics_template.md` | 12 | annotation 中可定位 `E_{xc}`、`k`、`H,S`、`3\times3`、`N`、`N\times3`、`l,m`、`R`、`S`、`S\succ0`。 |
| 综合问题 | 53 | C-C01—C-C10 的行间和行内公式均被转换。 |
| 综合解答 | 98 | C-C01—C-C10 的行间和行内公式均被转换。 |

指南要求复核的 `F_L`、谱半径、`E_xc`、`H/S`、正定 `S`、`k` 和 `alpha` 均形成实际 MathML。模板中的 shape、矩阵、索引及 Fourier 相关变量也形成 MathML；`UNRESOLVED_M8`、字段路径、枚举值、JSON 字符串和命令仍使用反引号或 JSON 代码块，没有被误改为数学对象。

### 3.2 控制字符与链接

字节扫描拒绝除 TAB/LF/CRLF 外的 C0 控制字符，并把不属于 CRLF 的裸 `0x0D` 单列为错误。结果：限定 43 个 Markdown 文档的非法控制字符和裸 CR 均为 0。原先破坏 `\rho` 的裸 CR 已不存在。

本地链接按源文件所在目录解析活动 Markdown 链接；结果为指南 30/30 有效、限定范围 71/71 有效、断链 0。

因此 B01 的节点覆盖、字节和链接三个关闭条件均满足，判定 `CLOSED`。

## 4. M5-09-B02 定点复核：CLOSED

综合问题 C-C07 已明确把两个对象分开：

- 题首四维对角 `H` 只用于 T-C07 广义谱、合同变换和 overlap 失败；
- 等谱矩阵反例另行定义为 `d=12`、seed `20260805` 的复高斯 canonical-QR 模型，并明确给出 QR 对角相位规范、`linspace(-3,3,12)` 和标准基 0、1 维的 0.37 rad 旋转。

使用 `numpy.random.default_rng(20260805)` 独立重建 canonical QR 和两个 Hamiltonian 后得到：

```text
d=12 T-C08 spectral difference = 4.440892098500626e-15
d=12 T-C08 relative matrix difference = 0.23306075775057758 > 0.15

direct rotation of the four-dimensional diagonal H:
spectral difference = 2.220446049250313e-16
relative matrix difference = 0.10421583493929089 < 0.15
```

题面要求说明四维直接旋转不能引用 T-C08 阈值；解答明确报告约 `0.10421583`，并声明两个模型的数值不得互换。解答中冻结 T-C08 的 `4.44e-15` 和 `0.23306076` 与独立复算及 CLI 完全一致。

因此对象偷换和错误阈值引用已消除，B02 判定 `CLOSED`。

## 5. M5-09-B03 定点复核：CLOSED

综合问题 C-C08 和参考解答现均按同一顺序组织：

1. 路径存在；
2. 结构验证：type、shape、数值有限性和数组关系；
3. 内容身份；
4. M8 哨兵和合成白名单授权；
5. 数值结构；
6. 固定表示语义一致性；
7. 前向物理量；
8. 独立审计。

问题和解答均把独立审计明确列为第八步，并说明主实现自报 `pass` 不能替代。语义层明确覆盖单位、轨道顺序、bra/ket、晶格位移方向、Fourier、规范和 overlap 处理；前向层与语义层没有互相替代。

问题明确要求说明当前 47 个对抗变异只直接分类为 type、shape、hash 和 M8 choice。解答准确给出 type 9、shape 11、hash 8、M8 choice 19，并明确这些变异不等于穷尽语义层或前向层，后两层仍需专门验证。该表述与实现和 JSON 证据一致，没有过度声明。

因此 B03 的实际验证顺序缺口已关闭，判定 `CLOSED`。

## 6. 回归检查

### 6.1 标题与阶段边界

- 综合问题二级标题严格为 C-C01—C-C10，共 10 项；
- 综合解答二级标题严格为 C-C01—C-C10，共 10 项；
- 两组标题顺序与集合完全相同；
- 自学指南、标签模板、综合问题/解答、工作包和 D-010 继续禁止 M8 前安装/调用真实 DeepH 或 DFT、正式数据下载、正式标签生成及真实材料/后端/版本选择；
- M7-I 后才准备 M8 集中冻结；M8 已冻结后，M9 外部安装、下载、DFT 计算或复现实验仍需再次取得明确授权。

未发现 C-C01—C-C10 标题回归或 M8/M9 双门槛弱化。

### 6.2 代码门控

虽三个代码文件均未改变，仍复跑固定环境门控：

```powershell
$py='C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m unittest discover -s .\05_code_exercises\stageC_teaching_scf -p 'test_*.py' -v
& $py .\05_code_exercises\stageC_teaching_scf\run_experiments.py --format json --seed 20260805 --model-size 12 --grid-size 64
& $py .\05_code_exercises\stageC_teaching_scf\run_experiments.py --format json --seed 20260806 --model-size 16 --grid-size 48
```

结果：9 项 unittest 全部通过；两组 CLI 均退出码 0、`overall_pass=true`、T-C01—T-C10 全部 `status=pass`、全部 `expected_failure.detected=true`。两组 T-C08 矩阵差分别为 `0.23306075775057758` 和 `0.17451989619254055`，谱差均为 `4.440892098500626e-15`。

## 7. 新增问题与门控决定

- 原阻塞关闭：3/3。
- 新增 `BLOCKING=0`。
- 新增 `NON_BLOCKING=0`。
- 剩余 M5-09 阻塞：0。

**门控决定：允许 M5-09 完成，并允许启动 M5-10。** M5-10 仍必须由新的独立子 agent 对阶段 C 当前总快照执行正式材料总审计；本定点复核不预判其结论，也不授权 M6 或任何 M8/M9 外部动作。
