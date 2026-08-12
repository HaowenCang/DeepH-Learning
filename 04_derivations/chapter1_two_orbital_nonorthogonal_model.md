# 第 1 章解析例子：两轨道非正交广义本征模型

## 1. 目的与证据边界

本例用于验证第 1 章中的四个判断：非正交基需要保留重叠矩阵；广义谱在一致可逆基变换下不变；矩阵误差的物理后果取决于扰动方向；病态重叠矩阵会降低数值稳定性。

模型、参数和反例均为 `【教学补充】`，不归因于 DeepH 论文。广义厄米本征问题与正交化背景见 FND-02—04；简单特征值的一阶扰动背景见 FND-05。DeepH 特定软件、材料或性能结论不由本例支持。

## 2. 模型定义与成立条件

定义

\[
H(x)=
\begin{pmatrix}
\varepsilon_1(x) & t(x)\\
t(x)^* & \varepsilon_2(x)
\end{pmatrix},
\qquad
S(x)=
\begin{pmatrix}
1 & s(x)\\
s(x)^* & 1
\end{pmatrix},
\]

其中 \(\varepsilon_1,\varepsilon_2\in\mathbb R\)，\(t,s\in\mathbb C\)。参数 \(x\) 可以表示键长、应变或其他结构坐标，本例只在固定 \(x\) 上求解，因此下文暂时省略 \(x\)。

矩阵 \(H=H^\dagger\)、\(S=S^\dagger\)。\(S\) 的两个本征值为

\[
\lambda_\pm(S)=1\pm|s|.
\]

因而

\[
S\succ0
\quad\Longleftrightarrow\quad
|s|<1.
\]

在该条件下，两个基函数线性无关，广义厄米本征问题

\[
Hc=ESc
\]

具有实本征值，并可选择满足 \(c_m^\dagger S c_n=\delta_{mn}\) 的本征矢。重叠矩阵的二范数条件数为

\[
\kappa_2(S)=\frac{1+|s|}{1-|s|}.
\]

当 \(|s|\to1^-\) 时，\(S\) 仍可能在精确算术中正定，但条件数发散；标签噪声、舍入误差和本征矢误差会更容易被放大。

## 3. 闭式广义本征谱

特征方程为

\[
\det(H-ES)=0.
\]

直接展开得到

\[
(\varepsilon_1-E)(\varepsilon_2-E)
-(t-Es)(t^*-Es^*)=0,
\]

即

\[
(1-|s|^2)E^2
-\left[\varepsilon_1+\varepsilon_2
-2\operatorname{Re}(ts^*)\right]E
+(\varepsilon_1\varepsilon_2-|t|^2)=0.
\]

定义

\[
a=1-|s|^2>0,
\qquad
b=\varepsilon_1+\varepsilon_2-2\operatorname{Re}(ts^*),
\qquad
d=\varepsilon_1\varepsilon_2-|t|^2,
\]

则

\[
E_\pm=\frac{b\pm\sqrt{b^2-4ad}}{2a}.
\]

由于 \((H,S)\) 是厄米定矩阵束，判别式非负。数值实现不应以这条二次公式替代稳定的广义本征求解器；闭式表达式只用于展示 \(t\)、\(s\) 与对角项如何共同决定谱。

对一个不使分量同时为零的本征值 \(E\)，可以取未归一化向量

\[
\widetilde c(E)=
\begin{pmatrix}
t-Es\\
-(\varepsilon_1-E)
\end{pmatrix}.
\]

它满足第一行方程；当 \(E\) 是特征根时也满足第二行。最终本征矢应按

\[
c(E)=
\frac{\widetilde c(E)}
{\sqrt{\widetilde c(E)^\dagger S\widetilde c(E)}}
\]

作 \(S\)-归一化，而不是默认使用欧氏归一化。

### 3.1 实对称等价轨道特例

若 \(\varepsilon_1=\varepsilon_2=\varepsilon_0\)，且 \(t,s\in\mathbb R\)，则对称与反对称组合分别给出

\[
E_{\mathrm{sym}}=\frac{\varepsilon_0+t}{1+s},
\qquad
E_{\mathrm{anti}}=\frac{\varepsilon_0-t}{1-s}.
\]

该式直接显示：即使 \(H\) 固定，忽略非零 \(s\) 也会改变能级；当 \(s\) 接近 \(\pm1\) 时，相应分母揭示基函数近线性相关带来的敏感性。

## 4. 一致基变换下的谱不变性

采用有序基矢行约定

\[
\boldsymbol\Phi' = \boldsymbol\Phi A,
\qquad
A\in\mathbb C^{2\times2},
\qquad
\det A\ne0.
\]

同一态的系数及矩阵表示为

\[
c'=A^{-1}c,
\qquad
H'=A^\dagger H A,
\qquad
S'=A^\dagger S A.
\]

代入可得

\[
H'c'
=A^\dagger HAA^{-1}c
=A^\dagger Hc
=E A^\dagger Sc
=E S'c'.
\]

从特征行列式也可直接证明

\[
\begin{aligned}
\det(H'-ES')
&=\det\!\left[A^\dagger(H-ES)A\right]\\
&=\det(A^\dagger)\det(H-ES)\det(A)\\
&=|\det A|^2\det(H-ES).
\end{aligned}
\]

因为 \(|\det A|^2\ne0\)，两者具有完全相同的特征根。\(S\)-归一化也保持：

\[
c'^\dagger S'c'=c^\dagger Sc.
\]

该证明依赖三个不可删去的条件：\(A\) 可逆；\(H\) 与 \(S\) 使用同一个 \(A\) 一致变换；新旧基张成同一子空间。只变换 \(H\) 而不变换 \(S\)，或改变基子空间，均不属于同一表示下的谱不变性。

## 5. 等范数扰动的方向反例

令 \(c_-\) 和 \(c_+\) 是未扰动问题的两个 \(S\)-正交归一本征矢，满足

\[
c_m^\dagger S c_n=\delta_{mn}.
\]

定义两个厄米秩一矩阵

\[
P_-=Sc_-c_-^\dagger S,
\qquad
P_+=Sc_+c_+^\dagger S,
\]

并令

\[
\delta H_- = \eta\frac{P_-}{\|P_-\|_F},
\qquad
\delta H_+ = \eta\frac{P_+}{\|P_+\|_F},
\qquad \eta>0.
\]

两者具有相同 Frobenius 范数：

\[
\|\delta H_-\|_F
=\|\delta H_+\|_F
=\eta.
\]

然而，对目标低能态 \(c_-\)，有

\[
c_-^\dagger\delta H_-c_-
=\frac{\eta}{\|P_-\|_F},
\qquad
c_-^\dagger\delta H_+c_-=0.
\]

第二个等式来自 \(c_+^\dagger S c_-=0\)。事实上，这两个扰动沿广义本征投影方向构造，因此结果不仅是一阶关系：\(\delta H_-\) 精确移动低能本征值 \(\eta/\|P_-\|_F\)，而 \(\delta H_+\) 保持低能本征值不变。该反例证明，相同全矩阵范数不能确定目标能级误差；误差相对于目标本征子空间的方向同样重要。

## 6. 固定数值样例

采用

\[
\varepsilon_1=-0.8,
\quad
\varepsilon_2=1.1,
\quad
t=0.25+0.08i,
\quad
s=0.18-0.04i.
\]

此时

\[
|s|=0.1843908891,
\qquad
\lambda(S)=(0.8156091109,\ 1.1843908891),
\qquad
\kappa_2(S)=1.4521550500.
\]

二次方程系数与闭式谱为

\[
a=0.966,
\quad b=0.2164,
\quad d=-0.9489,
\quad
(E_-,E_+)=(-0.8854103827,\ 1.1094269458).
\]

选择

\[
A=
\begin{pmatrix}
1 & 0.2+0.1i\\
-0.1+0.05i & 1.15
\end{pmatrix},
\qquad
\det A=1.175,
\]

并同时变换 \(H,S\) 后，广义谱保持到双精度舍入误差：最大差为 \(4.44\times10^{-16}\)。原问题的最大广义本征残差为 \(6.81\times10^{-16}\)，\(\|C^\dagger SC-I\|_F=1.61\times10^{-16}\)。

取 \(\eta=0.02\) 构造第 5 节的两个扰动，得到

\[
\|\delta H_-\|_F
=\|\delta H_+\|_F=0.02.
\]

低能本征值的变化分别为

\[
\Delta E_-^{(-)}=0.0207919669,
\qquad
\Delta E_-^{(+)}\approx-1.11\times10^{-16}.
\]

该数值样例同时验证闭式根、Cholesky 约化求解、基变换谱不变性、\(S\)-正交性和等范数方向反例。

## 7. 失效条件与常见错误

- 若 \(|s|\ge1\)，\(S\) 不再正定，不能继续套用厄米定广义本征问题的标准结论。
- 若 \(|s|\) 接近 1，应报告条件数并采用稳定求解器，不能只凭闭式根看似有限判定问题良态。
- 若判别式接近 0，两个本征值近简并；逐个本征矢和一阶非简并公式可能不稳定，应改为子空间分析。
- 复数 \(t,s\) 的展开必须保留共轭；把 \(ts^*+t^*s\) 错写成 \(2ts\) 会破坏系数的实性。
- 基变换必须同时作用于 \(H\)、\(S\) 和系数；只改一个对象得到的谱变化不是物理反例，而是表示不一致。
- 本征矢应采用 \(S\)-归一化；普通欧氏归一化不能替代 \(c_m^\dagger S c_n=\delta_{mn}\)。
- 等范数反例只否定“单一全矩阵误差足以决定物理误差”，不否定分块、轨道分辨和能窗相关矩阵指标的诊断价值。

## 8. 验收清单

- [x] 给出 \(S\succ0\) 的充要条件与条件数；
- [x] 从 \(\det(H-ES)=0\) 推导闭式本征值；
- [x] 给出 \(S\)-归一化本征矢构造；
- [x] 用系数关系和行列式两种方式证明一致基变换的谱不变性；
- [x] 构造同 Frobenius 范数、不同低能影响的两个扰动；
- [x] 固定数值参数并记录残差、正交性和谱差；
- [x] 明确正定性、病态、近简并和表示不一致等失效条件。

本文件完成 M3-04 的解析交付物，但不替代 M3-05 的独立代码与自动测试，也不替代 M3-07 的正式公式和物理审计。
