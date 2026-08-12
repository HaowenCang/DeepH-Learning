# M7-07 第 20 章第一次定点复核

## 1. 复核结论

**结论：PASS。** 稳定问题 `M7-C20-B01` 与 `M7-C20-N01` 均为 **CLOSED**。本次复核发现 `BLOCKING=0`、`NON_BLOCKING=0`、新增问题 0、剩余问题 0。

因此允许将 M7-07 标记为 `COMPLETED`，并允许启动 M7-08 阶段 E 解析推导包。该放行只适用于阶段 E 内部材料建设，不改变 M8/M9 授权边界。

## 2. 独立性、范围与快照

本复核由原第 20 章独立审计员执行。复核范围只包括：

- `M7-C20-B01`、`M7-C20-N01` 的最小关闭条件；
- 两处修订的相邻 Pauli、Kronecker、dtype/shape 和表示语义；
- 七文件严格 Pandoc/MathML、活动链接、Raw TeX、控制字符、三级标题和 Q/A 配对回归；
- 原独立数值夹具的核心回归；
- 是否出现修复引入的新问题。

七个被审材料保持只读；本次唯一新增文件为本报告。修订快照 SHA-256 为：

| 文件 | SHA-256 | 相对原审计 |
|---|---|---|
| `sources.md` | `D6425F7603C9DFA208F11F1B79AC7C904A7C9A3BA060DA06A7A36BBB1DE9F965` | 未改 |
| `outline.md` | `C76CC2F8A59E6E6C47F6F8B5EDA096FAE8F36A61780AE82267FF8705C843339B` | 未改 |
| `chapter.md` | `8B850FABCDDADC5F39E93142EB01CE2A0F75B29520F8C8F3611F26444EE72E57` | 仅 B01 修订 |
| `examples.md` | `355EEC994F537CE2A06FD2F8880DEE9E8B80918EEA3CBD98F80A2827C5745CB6` | 仅 N01 修订 |
| `20_spin_time_reversal_complex.md` | `E3397B367E8AE477B2026AA6935240FC811C458AAAEEBB435621904FA337BE96` | 未改 |
| `problem/readme.md` | `4BCBFE4AF887DC6A545CD6F6EDE870668D84E746A5869B9966660F0ECF694232` | 未改 |
| `solution/readme.md` | `017B893B5BE3F201FB899C161518C818AA0BF0B9BAA823D3912328D07E7D37E8` | 未改 |

哈希证明修订严格限定在原报告指定的两个文件；其余五个核心文件与原审计快照完全相同。

## 3. 稳定问题复核

### 3.1 M7-C20-B01：CLOSED

`chapter.md:332` 当前为

\[
H(\boldsymbol k)=\varepsilon(\boldsymbol k)I
+\boldsymbol b(\boldsymbol k)\cdot\boldsymbol\sigma.
\]

逐码点扫描七文件后，U+000B 及其他非法 C0/DEL 控制字符总数为 0。原 `arepsilon` 损坏对象不再存在。

本复核没有只依赖 Pandoc 退出码。将 `chapter.md` 转为 HTML5 MathML 后，目标 Pauli 分解节点包含：

- `<mi>ε</mi>`；
- annotation 中的字面 TeX `\varepsilon(\boldsymbol k)`；
- 与 \(H\)、\(I\)、\(\boldsymbol b\cdot\boldsymbol\sigma\) 位于同一 display-math 节点。

同节后续 scalar 偶性公式也继续生成 \(\varepsilon(-k)=\varepsilon(k)\)。因此修订同时关闭了非法字符门控和公式对象语义，不是仅删除控制字符后保留错误普通字母。

相邻内容没有变化：\(\varepsilon,\boldsymbol b\) 仍明确为实函数，\(J_s\sigma_a^*J_s^\dagger=-\sigma_a\)，scalar 偶、Pauli vector 奇及同号 Zeeman/交换场破缺条件全部一致。故 `M7-C20-B01=CLOSED`。

### 3.2 M7-C20-N01：CLOSED

`examples.md:44` 当前为

\[
D_{p\otimes s}
=R\otimes U_{1/2}
\in\mathbb C^{6\times6}.
\]

HTML5 MathML 的目标节点包含 `<mo>∈</mo>`，而不是普通 `<mi>i</mi><mi>n</mi>`。同一节点继续包含 \(R\otimes U_{1/2}\)、\(\mathbb C\) 和上标 \(6\times6\)。

例 20-2 的 orbital-major/spin-minor component 顺序、\(6\times6\) shape、spin-major 显式置换以及 provenance 警告均未改变；A20-02 的正确公式仍与例题一致。故 `M7-C20-N01=CLOSED`。

## 4. 文档与结构回归

七文件均以 `markdown+tex_math_single_backslash`、HTML5 MathML 和 `--fail-if-warnings` 返回 0。MathML 节点数仍为 `25/18/207/75/143/31/52`，合计 551。Pandoc JSON AST 共解析 5 个活动本地链接，断链 0；RawInline/RawBlock TeX 节点 0；非法控制字符 0。

`outline.md` 与 `chapter.md` 的三级标题仍为 29/29，文本和顺序完全一致。Q20-01—Q20-10 与 A20-01—A20-10 仍为 10/10 严格配对。12 个例题的编号、范围和内容没有因修订发生缺失。

两个修订只恢复一个希腊标量符号和一个集合关系算符，没有改变来源引用、payload、basis 顺序、公式条件、数值锚点、授权声明或 D-E08/D-E09 到 T-E11/T-E12 的映射。

## 5. 核心数值回归

使用原审计的 Python 3.12.13、NumPy 2.3.5、seed 20260810 夹具重新执行 200 组一般四元数：

| 对象 | 最大残差 |
|---|---:|
| Pauli 迹公式 \(U\to R\) | \(4.10\times10^{-16}\) |
| \(U(q_2q_1)=U(q_2)U(q_1)\) | \(2.09\times10^{-16}\) |
| \(R(q_2q_1)=R(q_2)R(q_1)\) | \(8.53\times10^{-16}\) |
| \(J_sU^*J_s^\dagger=U\) | 0 |

含 \(\sigma_y\) 的 200 个复杂 Pauli \(k\)-pair 正向最大残差仍为 0；漏复共轭的最小定向残差为 \(2.59\times10^{-4}>10^{-4}\)。固定复向量的 \(\Theta^2=-I\) 和 Kramers 自正交残差均为 0；错误 \(J_1=K_1K_1^\dagger\) 的残差仍为 \(1.1547005383792515\)；Zeeman 夹具残差仍为 2。

三个规范 payload SHA-256 仍为：

- `56342DB661DA6F8D9CC8C3BF6E241DCB9817F42E63A33CAD9AF9364BCC8DF6EC`；
- `F8B5E9591B791A2DBD9B262736718C8B391B75DE6CE720335D1AD5B8F1AFF444`；
- `230AA31FC0201B4F2D7F8981A3244049C280F75CB2C753F38F9CE9D86A250980`。

因此两处文本修订没有使 \(SU(2)\)、反幺正、basis route、Hamiltonian 时间反演、Kramers 或失败矩阵发生回归。

## 6. 新增问题与退出判断

未发现修订引入的新问题。当前稳定问题状态为：

| 问题 ID | 原严重度 | 状态 | 剩余条件 |
|---|---|---|---|
| `M7-C20-B01` | BLOCKING | **CLOSED** | 无 |
| `M7-C20-N01` | NON_BLOCKING | **CLOSED** | 无 |

最终计数：`BLOCKING=0`、`NON_BLOCKING=0`、新增问题 0、剩余问题 0。

因此本次定点复核判定 **PASS**，允许完成 M7-07 并启动 M7-08。后续仍须执行 M7-08—M7-11 及 D-011 指定的 M3—M7 全量独立总审计；本次通过不授权安装 DeepH/e3nn、下载正式数据、生成 DFT 标签或选择材料/DFT/数据后端/SOC/磁性实践，也不替代 M9 前的再次明确执行授权。

本报告写入后将独立执行严格 Pandoc/MathML 与控制字符检查；稳定 SHA-256 作为交付元数据回报，避免正文自指 hash。
