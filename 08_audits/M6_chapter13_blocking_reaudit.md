# M6-04 第 13 章阻塞项定点复核

- 复核日期：2026-08-04
- 复核角色：原独立内容审计子 agent
- 原报告：`08_audits/M6_chapter13_independent_content_audit.md`
- 复核对象：`M6-CH13-B01`
- 总结论：`PASS`
- 原阻塞项：`CLOSED=1`、`OPEN=0`
- 新增 `BLOCKING=0`
- 新增 `NON_BLOCKING=0`
- 剩余问题总数：`0`
- M6-04：**允许完成**
- M6-05：**允许启动**

主 agent 的修订已经无歧义地区分局部轨道下标与实际轨道身份，冻结逐分量身份解析、padding 哨兵和全 provenance 同步映射规则，并在 Q13-06/A13-06 中加入非平凡轨道 ID 表及三类语义失败条件。原报告列出的四项关闭条件全部满足，未发现修订引入新的形状、mask、置换、来源或授权边界问题。

## 1. 定点复核范围与快照

本次只复核以下修订文件：

| 文件 | 当前 SHA-256 |
|---|---|
| `03_textbook/chapters/13_message_passing_networks/chapter.md` | `E613DE99535C43115873596D1F24F6A6ED6990555E9E6511960750640C8EFB61` |
| `06_exercises/04-stageD/13_mpnn/problem/readme.md` | `E2B23E61818CEB8546A7934E1AB51773230CB184D0C34B49068B1F88DEF37545` |
| `06_exercises/04-stageD/13_mpnn/solution/readme.md` | `059B15E8B6E124B82E7FA66B097147C76247D6496F068B96D00073E915800B9E` |

必要对照为原报告 `M6-CH13-B01` 的四项关闭条件、第 12 章已冻结的 `node_orbitals`/局部 index 契约和 M6 工作包的轨道 provenance 要求。未扩大到 M6-07 的正式代码实现审计，也未修改任何被审材料、计划、台账或代码；唯一写入为本复核报告。

## 2. M6-CH13-B01 关闭条件逐项判定

### 条件 1：冻结无歧义的实际轨道身份 schema

**判定：`PASS`。**

`chapter.md:170-179` 现在同时要求输出携带：

- 局部整数下标 `orbital_i_index`、`orbital_j_index`；
- 两端节点的有序合成轨道 ID 表；
- 逐分量实际身份 `orbital_i_id`、`orbital_j_id`；
- 结构、端点、shift、edge ID、block shape、mask、单位与 schema 版本。

`chapter.md:181-197` 明确指出局部整数下标与实际轨道身份是不同对象。若实现选择不重复存储逐分量 ID，也必须通过 `structure_id`、端点和冻结 schema 版本稳定引用同一有序轨道表，并在读取时执行身份等式；只保存局部下标不再是合格 schema。该双方案与原报告允许的“直接携带”或“稳定引用并可解析”两种关闭路径一致。

### 条件 2：逐有效位置解析和 padding 哨兵可执行

**判定：`PASS`。**

`chapter.md:181-197` 对每个有效展平位置冻结

\[
\alpha=\left\lfloor a/p_j\right\rfloor,
\qquad
\beta=a\bmod p_j,
\]

以及

\[
(\texttt{orbital\_i\_id}_{ea},\texttt{orbital\_j\_id}_{ea})
=
(\texttt{node\_orbitals}[\texttt{structure\_id}][i][\alpha],
\texttt{node\_orbitals}[\texttt{structure\_id}][j][\beta]).
\]

逐分量实际 ID 的逻辑 shape 为 \((E,P_{\max})\)；padding 同时要求 `mask=false`、两个局部下标为 `-1`、两个实际 ID 为空字符串。正文由此闭合了有效分量、右侧连续 mask、局部位置和实际身份之间的可执行关系。

### 条件 3：预测与全部 provenance 采用同一行映射

**判定：`PASS`。**

`chapter.md:199` 明确要求预测数组、完整边键、mask、局部下标、实际轨道身份、有序轨道表引用和 schema 版本采用同一边行映射；排序、拼接批处理和节点置换后的逆映射必须同步作用于这些对象。正文还明确拒绝轨道表缺失、端点引用错误、表内顺序漂移或实际 ID 与局部下标解析不一致的记录，即使其 shape、mask 和数值合法。该规则满足原报告对排序、批处理和反置换一致映射的要求。

### 条件 4：非平凡轨道 ID 例题/题解与强制失败样例

**判定：`PASS`。**

`problem/readme.md:23-27` 在 Q13-06 中加入 receiver 轨道表 `['r0','r1']`、sender 轨道表 `['s0','s1']` 和 \((2,2)\) 块，要求逐位置恢复实际轨道对，并解释轨道表遗漏、顺序交换和端点错绑为何必须失败。

`solution/readme.md:70-92` 正确列出行优先映射：

| \(a\) | \((\alpha,\beta)\) | 实际轨道对 |
|---:|---:|---|
| 0 | \((0,0)\) | `('r0','s0')` |
| 1 | \((0,1)\) | `('r0','s1')` |
| 2 | \((1,0)\) | `('r1','s0')` |
| 3 | \((1,1)\) | `('r1','s1')` |

答案还给出可定向诊断的失败机制：若 receiver 表交换为 `['r1','r0']` 而局部下标与缓存实际 ID 不变，则 \(a=0\) 的重算身份变为 `('r1','s0')`，与缓存 `('r0','s0')` 不一致，validator 必须拒绝；轨道表遗漏和错误端点绑定同样失败。padding 与同步映射规则也在答案中复述。因此练习链已经能够独立恢复具体预测分量的端点和实际轨道对。

## 3. 独立只读验证

为避免仅依赖文字复述，复核中独立写出最小内存 validator，并对 Q13-06 的记录执行以下检查：

| 夹具 | 结果 |
|---|---|
| 正确有序轨道表、局部下标、实际 ID 和 padding | `PASS` |
| 删除 `node_orbitals` | 按预期拒绝 |
| receiver 轨道表交换顺序 | 按预期拒绝 |
| sender 轨道表绑定错误身份 | 按预期拒绝 |
| padding 位置携带非空实际 ID | 按预期拒绝 |

正确记录独立恢复的四个轨道对为 `('r0','s0')`、`('r0','s1')`、`('r1','s0')`、`('r1','s1')`，与 A13-06 完全一致。

只读文档回归结果：

- 三份修订文件使用 Pandoc `markdown+tex_math_single_backslash`、MathML 与 `--fail-if-warnings` 检查，3/3 通过，共 134 个 MathML 节点；未使用 `-o`、`--output` 或输入覆盖方式。
- Q13/A13 保持 10/10 一一对应；正文与三级提纲的 28 个二/三级标题仍逐项、逐序一致。
- 非法控制字符和 Unicode replacement character 均为 0。
- 修订只扩充合成轨道 provenance；没有引入真实元素轨道基、材料体系、DeepH 软件对象、正式数据、DFT 后端或版本选择。M8/M9 授权边界未回归。

## 4. 新增与剩余问题

- `M6-CH13-B01`：`CLOSED`
- 新增 `BLOCKING`：0
- 新增 `NON_BLOCKING`：0
- 剩余 `BLOCKING`：0
- 剩余 `NON_BLOCKING`：0

## 5. 最终门控结论

定点复核结论为 `PASS`。原报告的唯一阻塞项 M6-CH13-B01 已满足全部四项关闭条件，未发现新增或剩余问题。

因此：

- 允许将 M6-04 标记为完成；
- 允许启动 M6-05；
- 本结论只关闭第 13 章内容审计门控，不替代 M6 后续推导、代码、自学材料和阶段总审计。
