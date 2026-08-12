# 第 6 章例题：密度—势映射、KS 分解与占据口径

本文件给出四个后端无关例题。前两个使用解析模型，后两个使用有限维合成数据；它们用于检验定理条件和能量口径，不代表真实材料、泛函、赝势或 DFT 后端。

## 例 6-1 两站点单电子模型中的势—密度映射

考虑一个电子、两个正交站点基的 Hamiltonian

\[
H(v,C)=
\begin{pmatrix}
C+v/2 & -t\\
-t & C-v/2
\end{pmatrix},
\qquad t>0.
\]

这里 \(v=v_1-v_2\) 是势差，\(C=(v_1+v_2)/2\) 是共同势移。定义密度差

\[
m=n_1-n_2,
\qquad n_1+n_2=1.
\]

### 基态能量和密度差

本征值为

\[
E_\pm=C\pm\sqrt{t^2+\frac{v^2}{4}}.
\]

在 \(t>0\) 时基态非简并。由 Hellmann–Feynman 关系，

\[
\frac{\partial E_-}{\partial v}
=\left\langle\frac{\partial H}{\partial v}\right\rangle
=\frac12(n_1-n_2)=\frac m2.
\]

因此

\[
m(v)=-\frac{v}{\sqrt{4t^2+v^2}}.
\]

对 \(|m|<1\)，映射可逆：

\[
v(m)=-\frac{2tm}{\sqrt{1-m^2}}.
\]

共同势移 \(C\) 只把两个本征值都平移 \(C\)，不改变本征矢与密度。这是“密度确定势到加法常数”的有限维实例。

### 条件和失效边界

- 当 \(t=0\) 且 \(v=0\) 时基态简并，任意站点线性组合都可以是基态；单个基态密度不再给出上述一一映射。
- \(|m|=1\) 只在 \(|v|/t\to\infty\) 的极限达到，不对应有限势差。
- 该模型展示 HK 结构，但不证明连续 Coulomb 体系的函数空间定理。

### 可执行复算

```python
import numpy as np

t = 1.0
for v in [-3.0, -0.4, 0.0, 0.7, 2.5]:
    h = np.array([[v / 2.0, -t], [-t, -v / 2.0]])
    values, vectors = np.linalg.eigh(h)
    psi = vectors[:, 0]
    m_numeric = abs(psi[0]) ** 2 - abs(psi[1]) ** 2
    m_exact = -v / np.sqrt(4.0 * t**2 + v**2)
    assert np.isclose(values[0], -np.sqrt(t**2 + v**2 / 4.0))
    assert np.isclose(m_numeric, m_exact)
    if abs(m_numeric) > 1e-14:
        v_back = -2.0 * t * m_numeric / np.sqrt(1.0 - m_numeric**2)
        assert np.isclose(v_back, v)

c = 4.2
assert np.allclose(
    np.linalg.eigvalsh(np.array([[c, -t], [-t, c]])),
    np.linalg.eigvalsh(np.array([[0.0, -t], [-t, 0.0]])) + c,
)
```

## 例 6-2 单电子体系的精确 Hartree 自相互作用抵消

对归一化单电子密度 \(n\)，真实电子—电子相互作用严格为零。因此在该密度属于所声明的 KS 表示域时，

\[
F[n]=T[n]=T_s[n].
\]

由 KS 恒等分解

\[
E_{xc}[n]=F[n]-T_s[n]-E_H[n]
\]

立即得到

\[
E_{xc}[n]=-E_H[n].
\]

固定 \(\int n=1\) 时，允许变化满足 \(\int\delta n=0\)。若两者在该约束流形上可微，则

\[
v_{xc}(\mathbf r)=-v_H(\mathbf r)+C.
\]

常数 \(C\) 是固定粒子数受限导数的势零点自由度；选定相同势规范后可令 \(C=0\)。于是 KS 有效势中的 \(v_H+v_{xc}\) 在物理上正好抵消，剩余常数只整体平移本征值，不改变轨道与密度。该结论是精确泛函必须满足的约束；近似 LDA/GGA 一般不能对任意单电子密度精确实现该抵消，这称为单电子自相互作用误差的一种表现。

该推论不应外推为多电子体系中 \(E_{xc}=-E_H\)，也不意味着任意近似泛函都满足精确抵消。

## 例 6-3 从 KS 本征值和重建总能量

对常规局域 KS 方程，设某个合成密度给出

\[
\sum_i f_i\varepsilon_i=-6.20,
\qquad
E_H=1.10,
\qquad
E_{xc}=-0.65,
\qquad
\int v_{xc}n=-0.92.
\]

总能量应按

\[
E=\sum_i f_i\varepsilon_i-E_H+E_{xc}-\int v_{xc}n
\]

计算，因此

\[
E=-6.20-1.10-0.65+0.92=-7.03.
\]

若错误地直接报告本征值和，则误差为 \(0.83\)。若只减去 Hartree 能而漏掉 \(E_{xc}-\int v_{xc}n\)，则得到 \(-7.30\)，仍不正确。这个数值例只验证代数和口径；四个输入量不是任何真实材料的计算结果。

## 例 6-4 两能级 Fermi–Dirac 占据与 smearing 口径

取两个无自旋能级

\[
\varepsilon_1=-0.4,
\qquad
\varepsilon_2=0.4,
\qquad
\mu=0,
\]

并用能量单位表示的宽化参数 \(\tau>0\)：

\[
f_i(\tau)=\frac{1}{1+\exp[(\varepsilon_i-\mu)/\tau]}.
\]

粒子—空穴对称性保证 \(f_1+f_2=1\)。在 \(\tau=0.1\) 时，

\[
f_1\approx0.982014,
\qquad
f_2\approx0.017986.
\]

在 \(\tau=0.4\) 时，

\[
f_1\approx0.731059,
\qquad
f_2\approx0.268941.
\]

增大 \(\tau\) 会平滑占据，但仅由该公式不能判定 \(\tau\) 是真实电子温度还是数值积分参数。若将其解释为 Mermin 温度，还必须说明系综、熵项和报告的是自由能还是内能；若仅作数值 smearing，则必须登记最终零温外推或熵修正口径。

```python
import numpy as np

eps = np.array([-0.4, 0.4])
for tau, expected in [
    (0.1, np.array([0.9820137900379085, 0.01798620996209156])),
    (0.4, np.array([0.7310585786300049, 0.2689414213699951])),
]:
    occ = 1.0 / (1.0 + np.exp(eps / tau))
    assert np.allclose(occ, expected)
    assert np.isclose(occ.sum(), 1.0)
```

## 失败样例清单

以下表述均应判为失败：

| 失败表述 | 失败原因 |
|---|---|
| “任意非负归一化函数都是某个基态密度” | 混淆归一化与 \(N\)-/\(v\)-representability |
| “HK 定理给出了精确泛函的闭式表达” | 唯一性和变分结构不等于可计算闭式 |
| “所有 KS 本征值都是真实加电子或激发能” | 辅助体系谱不具有该普遍解释 |
| “一个电子也应保留正的 Hartree 自排斥能” | 精确 \(E_{xc}\) 必须抵消单电子 Hartree 项 |
| “采用 0.1 eV smearing 就等于物理体系温度为 0.1 eV” | 数值宽化与 Mermin 物理温度需要独立语义声明 |
| “选择 hybrid 仍必然得到纯局域乘法 \(v_{xc}(\mathbf r)\)” | generalized KS 可能包含非局域算符 |

## 例题结论

四个例题分别验证：外势只确定到常数且简并需要单独处理；精确 KS 分解对单电子自相互作用有强约束；总能量必须从本征值和中修正双计数；占据参数的数值作用不能替代温度和能量口径声明。
