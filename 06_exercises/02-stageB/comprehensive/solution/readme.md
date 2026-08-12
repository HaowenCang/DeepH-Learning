# 阶段 B 综合问题参考解答

## C-B01

冻结定义为

\[
H_{ab}(R)=\langle\phi_{a0}|\hat H|\phi_{bR}\rangle,
\qquad
S_{ab}(R)=\langle\phi_{a0}|\phi_{bR}\rangle.
\]

每块为 \(2\times2\)，一般 \(M\) 轨道时为 \(M\times M\)；\(H\) 具有能量单位，\(S\) 无量纲。利用 \(\hat H=\hat H^\dagger\) 与平移协变，

\[
H_{ab}(R)^*
=\langle\phi_{bR}|\hat H|\phi_{a0}\rangle
=H_{ba}(-R),
\]

故 \(H(R)^\dagger=H(-R)\)，\(S\) 同理。非零块的伴随位于负平移，因此 \(H(1)\) 本身无需 Hermitian。实际数据至少还应登记轨道排序、轨道相位、晶格平移方向、单位与原胞定义；缺少其中任何一项都可能造成不可检测的语义错配。

## C-B02

由

\[
H(k)^\dagger
=\sum_R e^{-ikR}H(R)^\dagger
=\sum_R e^{-ikR}H(-R)
=H(k)
\]

可得全 \(k\) Hermiticity，\(S(k)\) 同理。高对称点矩阵为

\[
H(k=0)=\begin{pmatrix}-0.72&0.46+0.02i\\0.46-0.02i&0.74\end{pmatrix},
\quad
S(k=0)=\begin{pmatrix}1.18&0.032+0.005i\\0.032-0.005i&1.116\end{pmatrix},
\]

\[
H(k=\pi)=\begin{pmatrix}0.88&0.16+0.02i\\0.16-0.02i&1.54\end{pmatrix},
\quad
S(k=\pi)=\begin{pmatrix}0.86&-0.028+0.005i\\-0.028-0.005i&0.916\end{pmatrix}.
\]

这里使用了 \(e^{\pm i\pi}=-1\)、\(e^{\pm2i\pi}=1\)。标准求解前仍须验证 \(\lambda_{\min}(S(k))>0\) 或 Cholesky 成功；Hermitian 矩阵仍可能具有零或负特征值。固定 129 点路径的最小 \(S(k)\) 特征值约为 \(0.84793196\)。

## C-B03

将 \(|\psi\rangle=\sum_b c_b|\phi_b\rangle\) 投影到每个 \(\langle\phi_a|\) 得

\[
\sum_b H_{ab}c_b
=E\sum_b S_{ab}c_b,
\]

即 \(Hc=ESc\)。等价地，对 \(c^\dagger Hc\) 在约束 \(c^\dagger Sc=1\) 下作复变分也得到该方程。规范化和残差为

\[
C^\dagger SC=I,
\qquad
r_n=\frac{\|Hc_n-E_nSc_n\|_2}
{(\|H\|_2+|E_n|\|S\|_2)\|c_n\|_2}.
\]

广义谱为

\[
E(0)\approx(-0.73728885,0.76771829),
\qquad
E(\pi)\approx(0.96124921,1.75714114).
\]

简并子空间内可作任意保持 \(S\)-内积的基混合，单列向量没有唯一标签；因此应比较分离能带簇的投影、子空间角度或谱集合。

## C-B04

同一态满足 \(\Phi c=\Phi A c'\)，故 \(c'=A^{-1}c\)。矩阵元含 bra 与 ket，所以

\[
H'=A^\dagger HA,
\qquad
S'=A^\dagger SA.
\]

进而

\[
\det(H'-ES')
=|\det A|^2\det(H-ES),
\]

可逆 \(A\) 不改变广义特征值零点。对题给非 unitary 反例，原归一化残差为

\[
\frac{\|(0,2)^T\|_2}{\|H\|_2\|(1,1)^T\|_2}
=\frac1{\sqrt2}\approx0.70710678,
\]

同步变换后为

\[
\frac1{\sqrt{101}}\approx0.09950372.
\]

一般可逆变换保持广义谱、精确零残差方程和 \(S\)-正交性，残差向量按 \(r'=A^\dagger r\) 协变；只有 unitary \(A\) 保持这里涉及的 Euclidean 2-范数，从而保持冻结的归一化残差标量。

## C-B05

完整有限离散对满足

\[
\frac1N\sum_k e^{ik(R-R')}=\delta_{RR'},
\]

故逆变换为

\[
H(R)=\frac1N\sum_k e^{-ikR}H(k),
\qquad
S(R)=\frac1N\sum_k e^{-ikR}S(k).
\]

题给 \(U(k)\) 为 unitary。同步合同变换与 \(c'=U^{-1}c=U^\dagger c\) 给出同一广义方程、能带和 \(S\)-范数；unitary 性还保证冻结的 Euclidean 归一化残差不变。只变 \(H\) 而保留原 \(S\) 会改变矩阵束，阶段 B 固定模型的全路径最大谱差约为 \(2.0\times10^{-2}\)，显著高于 \(10^{-4}\) 失败阈值。

## C-B06

在 \(k_j=2\pi j/N\) 的完整循环网格上，先按正变换组装全部 \(H(k_j),S(k_j)\)，再用 C-B05 的逆式恢复每个已知 \(R\) 块。固定实现中完整块的最大重建误差约为 \(4.44\times10^{-16}\)。

成对删除 \(R=\pm2\) 仍保持 Hermiticity，但改变矩阵函数和能带；64 与 128 点的最大带差分别约为 \(0.16114005\) 与 \(0.16135265\)，不会因加密采样而趋于零。只删除 \(R=-2\) 破坏共轭配对，固定第 9 章路径的反 Hermitian 残差约为 \(0.13797\)。恢复 \(\pm2\) 后重新组装和求解，谱差回到数值容差。可执行入口为 T-B05、T-B06 和 T-B09。

## C-B07

忽略 \(S(k)\) 是把非正交问题换成普通本征问题；约 \(0.18\) 的带差证明两种计算不等价，但该数值只属于合成模型。删除 \(H(-2)\) 后显著反 Hermitian 残差直接违反冻结的共轭配对，因此可以判定数据或索引实现错误，不应先重厄米化掩盖缺块。

条件数增大而后向残差仍小时，只能说明求得的本征对对当前矩阵束满足方程；\(S^{-1/2}\) 或 Cholesky 约化会放大小特征值方向，\(S\)-正交性可能退化。由此尚不能推出某条能带必然以固定速率变差。解释逐带前向误差还需要谱隙、简并结构、目标能窗和带匹配规则。诊断顺序应为：确认对象与约定，检查 Hermiticity/正定性，记录后向残差与 \(S\)-正交，再讨论前向物理量。

## C-B08

固定复现命令为：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
Set-Location 'E:\Projects\Codex\DeepH\05_code_exercises\stageB_periodic_nonorthogonal'
& $py -m unittest discover -s . -p 'test_*.py' -v
& $py .\run_experiments.py --format json --seed 20260803 --dimension 6 --nk 64
& $py .\run_experiments.py --format json --seed 20260804 --dimension 4 --nk 32
```

验收要求为 5 项单元测试通过，两组 CLI 均含 T-B01—T-B10、固定依赖版本、种子、维数、\(N_k\)、容差和预期失败字段，退出码为 0 且 `overall_pass=true`。负例必须真实执行并由异常消息或数值下界断言捕获。

这些结果验证有限维合成对象下的矩阵方向、Hermitian-definite 求解、Fourier 闭合、规范同步、截断/采样分离和失败检测；它们不能给出真实材料的误差分布，也不证明任何现代 DeepH 软件接口。M8 前禁止安装 DeepH、下载正式数据、生成 DFT 标签或选择材料与后端；M8 决策冻结后，在 M9 外部动作前仍须取得明确执行授权。

## 综合误区索引

| 误区 | 错误原因 | 证据入口 |
|---|---|---|
| 把非 unitary 合同变换当作普通相似变换 | 矩阵元含 bra/ket，且 overlap 必须同步 | C-B04；T-B03 |
| 用 Hermiticity 代替 \(S\succ0\) | Hermitian 允许零和负特征值 | C-B02；T-B01/T-B04 |
| 用同号 Fourier 正逆变换 | 角色正交无法恢复原块 | C-B05；T-B05 |
| 认为更多 \(k\) 点可恢复远程块 | 采样不创造被删模型信息 | C-B06；T-B09 |
| 静默重厄米化缺块数据 | 平均操作改变输入并掩盖上游错误 | C-B06/C-B07；T-B06 |
| 用小后向残差无条件保证小逐带误差 | 前向解释还依赖条件数、谱隙与带匹配 | C-B07；T-B04 |
