# 第 5 章例题：绝热失效、determinant 与平均场双计数

本文件给出三个后端无关例题。例题使用解析矩阵、正交自旋轨道和两站点教学模型，不代表任何真实材料、DFT 后端或 M8 实践设置。

## 例 5-1 两能级避免交叉与 BO 失效指标

考虑随核坐标 \(R\) 变化的实对称电子 Hamiltonian

\[
H_{\mathrm e}(R)=
\begin{pmatrix}
aR & \Delta \\
\Delta & -aR
\end{pmatrix},
\qquad a>0,\quad \Delta>0.
\]

### 电子能量与最小能隙

本征值为

\[
E_\pm(R)=\pm\sqrt{a^2R^2+\Delta^2}.
\]

两条绝热能量曲线的间隙为

\[
g(R)=E_+(R)-E_-(R)=2\sqrt{a^2R^2+\Delta^2},
\]

在 \(R=0\) 取得最小值 \(2\Delta\)。\(\Delta=0\) 时成为真实交叉；\(\Delta>0\) 时是避免交叉。

### 电子态旋转与导数耦合

令混合角满足

\[
\tan 2\theta(R)=\frac{\Delta}{aR}.
\]

在连续规范中，两个绝热态之间的一阶导数耦合的大小与 \(|d\theta/dR|\) 相同：

\[
\left|\frac{d\theta}{dR}\right|
=\frac{a\Delta}{2(a^2R^2+\Delta^2)}.
\]

在 \(R=0\)，

\[
\left|\frac{d\theta}{dR}\right|_{R=0}
=\frac{a}{2\Delta}.
\]

因此，当最小能隙 \(2\Delta\) 变小时，电子态对核坐标的变化率增大。该例没有给出完整非绝热跃迁概率，但明确展示了“核较重”之外仍需能隙和运动尺度条件。

### 数值核查

取 \(a=1.5\)、\(\Delta=0.2\)。则

\[
g(0)=0.4,
\qquad
|d\theta/dR|_{R=0}=3.75.
\]

若把 \(\Delta\) 减半为 0.1，最小能隙减半，而中心导数耦合指标加倍为 7.5。

## 例 5-2 两电子 Slater determinant 与 1RDM

设 \(\chi_a(x)\)、\(\chi_b(x)\) 是正交归一自旋轨道。两电子 determinant 为

\[
\Phi(x_1,x_2)
=\frac1{\sqrt2}
[\chi_a(x_1)\chi_b(x_2)-\chi_b(x_1)\chi_a(x_2)].
\]

### 反对称性与归一化

交换 \(x_1\) 与 \(x_2\) 后两项互换，因此

\[
\Phi(x_2,x_1)=-\Phi(x_1,x_2).
\]

展开 \(\langle\Phi|\Phi\rangle\) 时，两个直接项各为 1，两个交叉项因 \(\langle\chi_a|\chi_b\rangle=0\) 而为 0，故

\[
\langle\Phi|\Phi\rangle
=\frac12(1+1)=1.
\]

### 1RDM 与密度

按定义积分掉第二个电子：

\[
\gamma(x,x')
=2\int \Phi(x,x_2)\Phi^*(x',x_2),dx_2
=\chi_a(x)\chi_a^*(x')
+\chi_b(x)\chi_b^*(x').
\]

于是

\[
n(x)=\gamma(x,x)
=|\chi_a(x)|^2+|\chi_b(x)|^2,
\qquad
\operatorname{Tr}\gamma=2.
\]

利用轨道正交性可直接验证

\[
\gamma^2=\gamma.
\]

若占据轨道变为

\[
\begin{pmatrix}\widetilde\chi_a&\widetilde\chi_b\end{pmatrix}
=\begin{pmatrix}\chi_a&\chi_b\end{pmatrix}U,
\qquad U^\dagger U=I,
\]

则 \(\widetilde\gamma=\gamma\)。这比“每条轨道都不变”更准确：轨道可以变化，占据投影不变。

### Coulomb 与交换的自旋选择

相互作用期望值为

\[
\langle\Phi|r_{12}^{-1}|\Phi\rangle=J_{ab}-K_{ab}.
\]

若 \(\chi_a=u(\mathbf r)\alpha(s)\)、\(\chi_b=v(\mathbf r)\beta(s)\)，由于 \(\langle\alpha|\beta\rangle=0\)，交换积分 \(K_{ab}=0\)，但 Coulomb 积分一般非零。若两轨道具有相同自旋，交换项一般非零。由此可见，交换来自反对称性与自旋轨道重叠，不是经验附加常数。

## 例 5-3 两站点 Hartree 教学模型与双计数

考虑自旋平衡的两站点 Hubbard 型教学 Hamiltonian

\[
\hat H=
-t\sum_\sigma
(c_{1\sigma}^\dagger c_{2\sigma}
+c_{2\sigma}^\dagger c_{1\sigma})
+U\sum_{i=1}^{2}n_{i\uparrow}n_{i\downarrow},
\qquad t>0.
\]

它只是展示自洽依赖与双计数的有限维模型，不作为真实材料标签。

### Hartree 解耦

忽略自旋翻转并作密度平均场解耦：

\[
n_{i\uparrow}n_{i\downarrow}
\approx
n_{i\uparrow}\bar n_{i\downarrow}
+\bar n_{i\uparrow}n_{i\downarrow}
-\bar n_{i\uparrow}\bar n_{i\downarrow}.
\]

给定相反自旋密度，单自旋有效矩阵为

\[
h_\sigma(\bar n_{\bar\sigma})=
\begin{pmatrix}
U\bar n_{1\bar\sigma}&-t \\
-t&U\bar n_{2\bar\sigma}
\end{pmatrix}.
\]

对两个电子的自旋平衡对称解，令

\[
\bar n_{1\uparrow}=\bar n_{2\uparrow}
=\bar n_{1\downarrow}=\bar n_{2\downarrow}=\frac12.
\]

则

\[
h_\sigma=
\begin{pmatrix}
U/2&-t \\
-t&U/2
\end{pmatrix}.
\]

占据每个自旋的成键态 \((1,1)^T/\sqrt2\)，输出密度仍为每站点每自旋 \(1/2\)，因此这是自洽固定点。

### 本征值和与总能量

占据本征值为 \(\varepsilon_b=U/2-t\)。两自旋本征值和是

\[
\sum_{\sigma\in\{\uparrow,\downarrow\}}
\varepsilon_{b\sigma}=U-2t.
\]

但物理平均场能量为动能加一次相互作用：

\[
E_{\mathrm{MF}}
=-2t
+U\sum_i\bar n_{i\uparrow}\bar n_{i\downarrow}
=-2t+\frac U2.
\]

差值 \(U/2\) 是相互作用在有效一体本征值和中的重复计数。等价地，

\[
E_{\mathrm{MF}}
=\sum_{\mathrm{occ}}\varepsilon_p
-U\sum_i\bar n_{i\uparrow}\bar n_{i\downarrow}.
\]

该结果表明，“已知自洽 Hamiltonian 的占据本征值”仍不足以在没有能量泛函口径时唯一解释总能量。

### 可执行复算

以下代码只使用 NumPy，并对两组 \((t,U)\) 强制验证自洽密度、谱和双计数：

```python
import numpy as np

for t, U in [(1.0, 2.0), (0.7, 3.2)]:
    h = np.array([[U / 2.0, -t], [-t, U / 2.0]], dtype=float)
    eigvals, eigvecs = np.linalg.eigh(h)
    bonding = eigvecs[:, 0]
    density_per_spin = np.abs(bonding) ** 2

    assert np.allclose(density_per_spin, [0.5, 0.5], atol=1e-14)
    assert np.allclose(eigvals, [U / 2.0 - t, U / 2.0 + t])

    eigenvalue_sum = 2.0 * eigvals[0]
    double_counting = U * np.sum(density_per_spin**2)
    mean_field_energy = eigenvalue_sum - double_counting
    assert np.isclose(mean_field_energy, -2.0 * t + U / 2.0)
```

## 例题结论

三个例题分别冻结了三条后续会反复使用的判断：

- BO 的可靠性取决于导数耦合、能隙和核运动尺度，而不只取决于质量比；
- 单 determinant 的基本一体对象是占据子空间投影，轨道规范变化不等于物理态变化；
- 自洽有效 Hamiltonian 的本征值和一般包含双计数，总能量口径必须单独登记。
