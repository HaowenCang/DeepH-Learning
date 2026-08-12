# M5-05 第 8 章阻塞项与非阻塞项独立定点复核

- 复核日期：2026-08-04
- 原审计：`08_audits/M5_chapter8_independent_content_audit.md`
- 定点对象：`M5-C8-B01`、`M5-C8-N01`、`M5-C8-N02`
- 复核范围：六个修订文件、原 finding 的最小修复要求及规定回归检查
- `M5-C8-B01`：`CLOSED`
- `M5-C8-N01`：`CLOSED`
- `M5-C8-N02`：`CLOSED`
- 新增 `BLOCKING`：0 项
- 剩余 `BLOCKING`：0 项
- 是否允许 M5-05 标记为 `COMPLETED`：**是**
- 是否允许启动 M5-06：**是**

本次只复核原审计冻结的三个 ID 及相关回归，不扩展为新的全章审计。六个文件的实际 SHA-256 与主 agent 提交的修订快照完全一致。除新增本报告外，未修改教材、推导、题目、解答、计划、追踪器或决策记录。

## 1. 修订快照

| 文件 | 复核时 SHA-256 |
|---|---|
| `03_textbook/chapters/08_basis_pseudopotential_errors/sources.md` | `18FCDFE53D44B1EF9217D2E9193A4C98817751EEB60D5FC4461397E5F11587B1` |
| `03_textbook/chapters/08_basis_pseudopotential_errors/chapter.md` | `CB8A8DC8B81705640487E0E9528C2699DF749AB3B9A72BEB3F8F640E11C2C85B` |
| `03_textbook/chapters/08_basis_pseudopotential_errors/examples.md` | `317DA0AFF7C10CA9F373D32766E261D37885C630694526635F36AC0C4105408A` |
| `04_derivations/stageC/08_representation_and_label_error.md` | `63E8F7D712F9ADCF57AAE7D46F1DC4F4C2A379344E5EE85D063637849C2CCBB8` |
| `06_exercises/03-stageC/08_basis_pseudopotential_errors/problem/readme.md` | `284BC3577F1DC1EAF84FC2C7B66FDCF07C6337022FDADF9AEF440EBA9F7E8179` |
| `06_exercises/03-stageC/08_basis_pseudopotential_errors/solution/readme.md` | `9B4FADC414A1FB1856C3BA4C72ECE08D1A42927098F38FB2A82E19EECB251076` |

## 2. ID 复核

### 2.1 M5-C8-B01：`CLOSED`

原问题要求闭合列满秩非正交目标空间的“投影—重建—损失”链。修订后的正文、D-C07 和 Q8-08 参考解答均先定义

\[
S_B=B^\dagger B,
\qquad
H_B=B^\dagger HB,
\qquad
P_B=B S_B^{-1}B^\dagger,
\]

再明确给出固定完整空间内积下的回投算符

\[
H_r^{(\mathrm{nonorth})}
=P_BHP_B
=B S_B^{-1}H_BS_B^{-1}B^\dagger.
\]

材料同步给出

\[
P_BH_r^{(\mathrm{nonorth})}P_B
=H_r^{(\mathrm{nonorth})}
\]

和

\[
\ell_H^{(\mathrm{nonorth})}
=\frac{\|H-H_r^{(\mathrm{nonorth})}\|_F}
{\max(\|H\|_F,10^{-15})}.
\]

成立条件被明确限定为 `B` 列满秩、完整空间内积固定且 `S_B` 正定。数值实现边界也已补全：病态 `S_B` 不得以显式逆实现，应使用 Cholesky、Hermitian-definite 求解或等价稳定分解完成线性求解，并登记条件数、阈值和删减子空间。

缩放反例完整且数值正确。取 `B=2e_1`、`H=h|e_1><e_1|`，有 `S_B=4`、`H_B=4h`；正确公式得到 `h|e_1><e_1|`，错误照搬正交公式 `BH_BB†` 得到 `16h|e_1><e_1|`。独立使用 `h=1.7` 复算得到：投影幂等残差 0、两种正确表达式之差 0、回投一致性残差 0、正确系数 1、错误系数 16。该反例直接证明遗漏两侧对偶度量会导致重建依赖基函数任意缩放。

Q8-08 题目已同步要求非正交投影、本征问题、完整空间回投、丢失范数和错误公式缩放反例；参考解答逐项作答。原报告要求的公式、条件、损失语义和可复核失败说明均已满足，因此 `M5-C8-B01=CLOSED`。

### 2.2 M5-C8-N01：`CLOSED`

章级 `sources.md` 已新增 C-FND-04 Mermin 1965，固定用途为“固定温度与化学势下的有限温度 DFT 理论边界”，并明确限制“数值 smearing 不自动等于目标物理温度”。该映射与正文和 Q8-09 解答的有限温度、熵项及能量口径表述一致，也没有把 Mermin 理论外推为任意数值宽化的物理解释。原章级来源追踪缺口已关闭，故 `M5-C8-N01=CLOSED`。

### 2.3 M5-C8-N02：`CLOSED`

`canonical_qr` 已改为

```python
q_canonical = q_matrix @ np.diag(phases)
r_canonical = np.diag(np.conj(phases)) @ r_matrix
```

并增加三类强制断言：`Q_canonical R_canonical` 对输入矩阵的相对 Frobenius 重构误差小于 `1e-12`；`R_canonical` 对角虚部小于 `1e-12`；对角实部不小于 `-1e-14`。这与 `phases=diag(R)/abs(diag(R))` 的标准复相位规范方向一致。

使用冻结解释器执行修订后的第四个 Python 块，两组 seed/维数均通过新断言和原 T-C08 的正交、回投、丢失范数、等谱及矩阵差断言。原先依赖固定 LAPACK 返回 `+1/-1` 对角相位的通用性缺口已消除，故 `M5-C8-N02=CLOSED`。

## 3. 回归检查

### 3.1 严格 Pandoc 与控制字符

对原审计的七个章节材料文件执行：

```text
pandoc <file> \
  --from markdown+tex_math_dollars+tex_math_single_backslash \
  --to html5 --mathml --fail-if-warnings
```

结果为 `7/7` 退出码 0。逐字符扫描 C0 控制字符、DEL 和 TAB，七文件的异常控制字符与 TAB 均为 0。修订没有引入 Markdown、数学公式或代码围栏回归。

### 3.2 四个 Python 代码块

`examples.md` 仍恰含 4 个 `python` 围栏。使用 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0，把每个代码块原样解析并作为独立程序执行，结果为 `4/4` 退出码 0。T-C05—T-C08 的既有数值门控未发生回归，修订后的 QR 规范断言亦通过。

### 3.3 定点代数复算

独立构造二维完整空间、单列 `B=(2,0)^T` 和 `H=diag(h,0)`，使用线性求解形成 `P_B` 及两侧度量回投。复算得到：

| 指标 | 结果 |
|---|---:|
| `S_B` | 4 |
| `H_B/h` | 4 |
| `||P_B^2-P_B||_F` | 0 |
| `||P_BHP_B-BS_B^{-1}H_BS_B^{-1}B†||_F` | 0 |
| `||P_BH_rP_B-H_r||_F` | 0 |
| 正确回投系数相对 `h` | 1 |
| 错误 `BH_BB†` 系数相对 `h` | 16 |

因此 B01 的关键条件分支不仅形式正确，而且具有可独立执行的反例证据。

## 4. 定点门控结论

本次独立定点复核冻结：

- `M5-C8-B01=CLOSED`；
- `M5-C8-N01=CLOSED`；
- `M5-C8-N02=CLOSED`；
- 新增 `BLOCKING=0`；
- 剩余 `BLOCKING=0`；
- **允许将 M5-05 标记为 `COMPLETED`；**
- **允许启动 M5-06。**

该结论只关闭原审计冻结的三个 ID，并确认相关回归检查通过；不改变 M8/M9 外部动作授权边界，也不提前审计 M5-06。
