# M6-08 阶段 D 自学材料定点复核

## 1. 复核范围与独立性

- 复核对象：首次独立审计报告 `M6_stageD_self_study_independent_audit.md` 中的 B01、N01、N02、N03 及其相邻回归。
- 复核角色：原独立审计员；未参与四份受审计材料的修订。
- 写入边界：除本报告外，未修改教材、推导、代码、计划、tracker 或其他状态文件。
- 放行规则：B01、N01—N03 全部关闭，且无新增 `BLOCKING` 或 `NON_BLOCKING`，才允许完成 M6-08 并启动 M6-09。
- 复核日期：2026-08-09。

本轮修订快照如下：

| 文件 | SHA-256 |
|---|---|
| `03_textbook/chapters/stageD_self_study_guide.md` | `3F24ECB8B550A259C7004F3CE85CEE1A55E5E2921B60F59B3BD52524E6ED3F91` |
| `03_textbook/stageD_tensor_trace_template.md` | `39C0423D7C09E7CDCC4D50FEA92F837FB5677C8D3C0A7467A98AA260A2CB51E0` |
| `06_exercises/04-stageD/comprehensive/problem/readme.md` | `DD7062CD0F6256CFF45E8E5DCF0F5A9F96EB6C56EAC43353D41A9B4AB267AD9C` |
| `06_exercises/04-stageD/comprehensive/solution/readme.md` | `6955546E126902C0FD0D710A9B8CB179ECD73C85AEAB838A882991BF2B00B7C2` |

## 2. 总结论

**结论：`PASS`。**

- B01：`CLOSED`
- N01：`CLOSED`
- N02：`CLOSED`
- N03：`CLOSED`
- 新增 `BLOCKING=0`
- 新增 `NON_BLOCKING=0`
- 剩余 `BLOCKING=0`
- 剩余 `NON_BLOCKING=0`

**明确允许完成 M6-08。**

**明确允许启动 M6-09。**

## 3. 原问题定点关闭证据

### B01：C-D04 的 structure ID 与 edge ID 未冻结为唯一答案

**状态：`CLOSED`。**

参考答案现已明确：题面没有规定重命名结构，因此 structure ID 唯一保持为 `stageD-main`；旧边 `0 <- 1` 在题面旧编号到新编号的置换下变成 `2 <- 0`，shift 保持 `(-1,0,0)`。答案给出完整键

```text
(stageD-main,2,0,-1,0,0)
```

以及唯一紧凑 JSON：

```text
["stageD-edge-v1","stageD-main",2,0,-1,0,0]
```

独立按 UTF-8 字节复算 SHA-256 为

```text
14dc675ce342830589c8b2687fbdcb4c3d88056164913163ff76a33c9812328f
```

与修订答案完全一致。张量模板也已冻结：当前 C-D04/T-D04 保持 structure ID 不变，只用同一 ID、新端点和 shift 重算；“结构同时改名”被明确分离为不属于当前门控的扩展变体。

置换方向现已无歧义。题面 `pi=[2,0,3,1]` 表示旧编号到新编号；若数组操作写成 `new=old[order]`，则 `order=[1,3,0,2]` 表示新行到旧行。T-D04 代码的 `permutation=[2,0,3,1]` 使用后者语义，并由 `inverse=[1,3,0,2]` 得到旧编号到新编号。修订答案明确说明与综合题比较时应交换这两个数组的角色，未把相同数值数组误当成相同映射方向。

### N01：章节定位偏移

**状态：`CLOSED`。**

自学导航已将周期代表变换两处定位修正为第 14 章 14.5。多重边与完整身份定位现为第 12 章 12.1.3、12.5.3、12.6.2，以及第 14 章 14.4.2—14.4.3。batch/NaN padding 定位现为第 12 章 12.2.2—12.2.3，并保留第 13 章 13.1 的前向读取边界。

独立核对章节标题确认上述各节均存在，且内容分别直接覆盖多重边、自镜像、edge instance 回溯、重复边、等距多镜像、规范边身份、类型/有限性和 padding/mask；没有以相邻章节代替直接论证。

### N02：模板的 structure ID 批内唯一性与代码契约不一致

**状态：`CLOSED`。**

模板已改为：“逐图检查非空；batch 内允许重复，须结合 batch 槽位/graph ID 定位”。该表述与冻结实现一致。独立把两个相同 `stageD-main` 图分别传给 `make_concat_batch` 和 `make_padded_batch`，两者均接受 `['stageD-main','stageD-main']`，并以 `graph_count=2` 及相应图槽位保持批内分区。修订材料不再声称 validator 执行未冻结的全局唯一约束。

### N03：padding 探针运行次数矛盾

**状态：`CLOSED`。**

模板现明确写为“记录三次运行”，表格仍为有限零、NaN、`10^300` 三种探针，且要求有效 prediction 与 loss 相对有限 padding 的残差均为零；与 C-D09 题目及参考答案一致。

## 4. 相邻回归验证

### 4.1 严格 Markdown、MathML、链接与控制字符

四份文件均使用以下严格输入口径转换：

```text
pandoc --from markdown+tex_math_single_backslash --to html5 --mathml --fail-if-warnings
```

四次退出码均为 0；MathML 节点数依次为 13、88、46、147。独立解析的 Markdown 本地链接数依次为 28、4、0、2，全部目标存在且均位于工作区内。四文件非法 C0 控制字符均为 0。

C-D01—C-D10 与 A-D01—A-D10 仍为 10/10 精确配对；`problem/` 与 `solution/` 均非空。修订没有破坏双向能力映射、张量 shape、轨道身份、换胞符号、主夹具 18 边/2000 候选、C-D07 八边、复杂度或 M8/M9 授权边界。

### 4.2 自动测试与固定环境

```text
Python 3.12.13
NumPy 2.3.5
SciPy 1.18.0
pip check: No broken requirements found.
```

本轮未安装任何依赖。

执行

```text
python -m unittest discover -s 05_code_exercises/stageD_synthetic_mpnn -p test_*.py -v
```

结果为 13/13 通过。

### 4.3 A/B CLI、字节确定性与错误 seed

- 配置 A、seed `20260806`：退出码 0，T-D01—T-D10 全部 `pass=true`，`overall_pass=true`；两次真实 stdout 字节完全一致，SHA-256 为 `2F45DC8C53C1E1D968B3F4633CCC8590540AB8E08667A340054F15F9F3CCA6EE`。
- 配置 B、seed `20260817`：退出码 0，T-D01—T-D10 全部 `pass=true`，`overall_pass=true`；两次真实 stdout 字节完全一致，SHA-256 为 `88BF70A4218E2B10C8410644B7B899ECF50A6F6993E83E93C496450069693BD6`。
- 配置 A、错误 seed `0`：退出码 2，stdout 长度为 0，stderr 明确包含 `requires seed 20260806`。

## 5. 最终放行判定

首次审计中的 B01、N01、N02、N03 均满足各自最小关闭条件；定点复核未发现相邻回归或新增问题。当前问题计数为 `BLOCKING=0`、`NON_BLOCKING=0`。

因此，本独立复核明确允许完成 M6-08，并明确允许启动 M6-09 阶段 D 正式独立材料总审计。
