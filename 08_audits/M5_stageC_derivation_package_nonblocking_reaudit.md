# M5-07 阶段 C 解析推导包非阻塞项独立定点复核

## 1. 复核结论

- 复核日期：2026-08-04
- 原正式审计：`08_audits/M5_stageC_derivation_package_independent_audit.md`
- 定点范围：`M5-C-D-N01`、`M5-C-D-N02` 及修订可能引入的回归
- `M5-C-D-N01`：`CLOSED`
- `M5-C-D-N02`：`CLOSED`
- 剩余 `BLOCKING`：0 项
- 新增 `BLOCKING`：0 项
- 新增 `NON_BLOCKING`：0 项
- 是否维持 M5-07 `COMPLETED`：**是**
- 是否维持 M5-08 可启动：**是**

三份推导文件现已直接建立来源—对象—证据状态映射，不再要求读者先经阶段 C README 间接跳转才能判断 D-C05—D-C08 的证据等级。D-C07.7 已固定 T-C08 等谱故障注入的旋转平面和角度；D-C07.8 已把 T-C09 的单一冻结来源、完整路径、数组内部成员、类型/形状、SHA-256、`UNRESOLVED_M8` 和逐路径删除失败规范直接写入推导接口。修订没有改变任何既有数学对象、数值阈值、失败语义或 M8/M9 边界。因此两项原非阻塞建议均已关闭，原 `PASS` 结论保持。

## 2. 复核范围与修订快照

本轮只读核查以下文件：

- `04_derivations/stageC/07_scf_fixed_point.md`；
- `04_derivations/stageC/08_representation_and_label_error.md`；
- `04_derivations/stageC/10_nearsightedness_sparsity.md`；
- 未改动的 `04_derivations/stageC/README.md`；
- 三章对应的 `sources.md`；
- T-C08/T-C09 的冻结依据 `08_audits/M5_stageC_work_package.md`。

字节快照如下。

```text
0353CCCA35D27E357604E189C139C8A1F2BDFC47D57B217C781516165FD138B7  04_derivations/stageC/07_scf_fixed_point.md
5B432FECE9975840EE655ED8CFD678BF5D54E4B7EE897F55F0D88380673C1CB7  04_derivations/stageC/08_representation_and_label_error.md
708603589DCEB4EC68B5A6C17B1012A97DB62AEB8834B2E8CE570BD255CD191B  04_derivations/stageC/10_nearsightedness_sparsity.md
8C0A8ED24C112233D8E5F8EBF25918DD58616A4B023F1463F5971CC7B6B00A1D  04_derivations/stageC/README.md
20CDDB92801D39E43854BF69A4E81A0392B2B21529178582FA7BB8FDCFD9267A  08_audits/M5_stageC_derivation_package_independent_audit.md
```

本次复核未修改推导、章节、工作包、计划、追踪器或决策文件；仅新增本报告。

## 3. `M5-C-D-N01` 来源直接可达性

判定：`CLOSED`。

### 3.1 D-C05

`07_scf_fixed_point.md` 新增“来源与证据状态”表，直接链接第 7 章 `sources.md`，并把来源分成：

- C-NUM-01 对 SCF 非线性固定点、密度混合、响应和病态语境的 `PRIMARY_EXPLICIT` 支持，同时保留“不支持任一混合器普遍最优”的边界；
- C-NUM-02/FND-01 对历史平面波迭代、成本与教材对象链的 `PRIMARY_EXPLICIT` 支持，不把历史对象推成现代后端接口；
- D-C05 的矩阵代数标为 `DIRECT_DERIVATION`；
- T-C01—T-C04 的有限维映射和故障注入标为 `PEDAGOGICAL`，明确不构成真实材料参数。

这与章级来源包原有用途和边界一致，没有新增来源越权。

### 3.2 D-C06/D-C07

`08_representation_and_label_error.md` 新增表格，直接定位 FND-01/C-NUM-02、C-NUM-03、C-FND-04 与 DH-07，并分别保留现代后端格式、ultrasoft/PAW、物理温度和 M8 软件可用性边界。Galerkin、合同变换和投影代数被明确标为 `DIRECT_DERIVATION`；T-C05—T-C09 的合成序列、矩阵和 schema 故障标为 `PEDAGOGICAL`。

该映射没有把 norm-conserving 条件推广到全部赝势形式，也没有把 PW 到 AO 的一般投影/重建原则写成 M8 前已经可用的软件接口。

### 3.3 D-C08

`10_nearsightedness_sparsity.md` 新增表格，分别定位 C-LOC-01、FND-01 和 DH-01，并保留三个关键证据边界：近视性不推出任意矩阵统一指数衰减；局域基不自动保证严格有限程；原始 DeepH 示例半径不外推为通用 cutoff。响应/矩阵/截断关系被标为 `DIRECT_DERIVATION`，T-C10 指数/代数族与错误外推标为 `PEDAGOGICAL`。

三文件现已达到与 D-C01—D-C04 同等级的文件内来源可达性。原 N01 的改善目标完全满足。

## 4. `M5-C-D-N02` T-C08/T-C09 直接可达性

判定：`CLOSED`。

### 4.1 T-C08

D-C07.7 现明确声明：故障注入的 unitary \(U\) 只在固定标准基前两维作 \(0.37\ \mathrm{rad}\) 的实正交旋转，其余维保持不变。该对象与阶段 C 工作包 T-C08 完全一致，同时保留

\[
H_2=U^\dagger H U
\]

的等谱关系及固定表示中相对矩阵差大于 0.15 的失败语义。没有改变先前复算通过的两组阈值。

### 4.2 T-C09

D-C07.8 现直接规定：

- `stageC-label-v1` 的完整必填路径集合以阶段 C 工作包第 8 节为单一冻结来源；
- 数组内部成员同属必填对象；
- 类型、数组形状、64 位十六进制 SHA-256 与全部 `UNRESOLVED_M8` 占位受冻结规范约束；
- 对每个必填路径分别删除后，必须抛出错误消息含缺失路径的 `ValueError`；
- 推导文件不复制整张 schema 表，以避免两份规范漂移。

新增链接能直接解析到 `08_audits/M5_stageC_work_package.md`，该工作包第 8 节确实包含被引用的完整路径表与数组成员要求。D-C07.8 仍明确保持“schema 完整不推出数值正确，数值正确不推出物理目标充分”的门控层次。原 N02 的直接可读性要求完全满足，且没有制造第二个 schema 真源。

## 5. 数学与授权回归

新增内容限于来源映射、T-C08 参数明示和 T-C09 冻结引用。逐项核对未发现以下回归：

- SCF 的局部谱条件没有被扩展为全局收敛或单调下降保证；
- 普通/广义谱、正交/非正交投影及两侧 \(S_B^{-1}\) 回投公式未变；
- T-C08 的 unitary 相似变换没有被误称为固定矩阵标签相同；
- schema、矩阵、谱和物性门控仍保持不同证据层次；
- 近视性、密度矩阵衰减和 \(H/S\) 稀疏性仍为三个对象；
- M8 前禁令及 M9 外部动作二次授权边界未改变。

## 6. Pandoc、控制字符与链接

对阶段 C 六个核心推导文件执行：

```powershell
pandoc <file> `
  --from markdown+tex_math_dollars+tex_math_single_backslash `
  --to html5 --mathml --fail-if-warnings
```

六文件全部退出码 0。实际 MathML 节点为：

```text
README.md                              17
05_many_electron_mean_field.md         89
06_kohn_sham_variation.md             149
07_scf_fixed_point.md                  83
08_representation_and_label_error.md  118
10_nearsightedness_sparsity.md         66
```

逐字符扫描结果为异常 C0、TAB、DEL 与 U+FFFD 均为 0。六文件活动 Markdown 链接为 `23/23` 存在；新增三个章级来源链接和一个工作包链接均可达。修订没有引入数学定界、表格、控制字符或路径回归。

## 7. 新增 findings

新增 `BLOCKING=0`，新增 `NON_BLOCKING=0`。本轮没有发现需要扩大修复范围的内容、数学、来源或制品问题。

最终判定：`M5-C-D-N01=CLOSED`、`M5-C-D-N02=CLOSED`；维持 M5-07 `COMPLETED` 和 M5-08 可启动。
