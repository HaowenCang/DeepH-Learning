# 第 17 章练习：参考解答

## A17-01

顺序为

\[
m=-\ell,-\ell+1,\ldots,\ell.
\]

正交归一和共轭关系分别是

\[
\int_{S^2}Y_{\ell m}^*Y_{\ell' m'}\,d\Omega
=\delta_{\ell\ell'}\delta_{mm'},
\]

\[
Y_{\ell,-m}=(-1)^mY_{\ell m}^*.
\]

对 \(\ell=1,m=1\)：

\[
Y_{1,-1}
=-Y_{1,1}^*
=-\left[-(p_x-i p_y)/\sqrt2\right]
=(p_x-i p_y)/\sqrt2.
\]

漏掉 \((-1)^m\) 会翻转负 \(m\) 与正 \(m\) 的相对相位，并改变 \(C_1\)、Wigner 相似变换和后续 CG 规范表。

## A17-02

\[
\begin{aligned}
[U(R_2)U(R_1)f](\widehat r)
&=[U(R_1)f](R_2^{-1}\widehat r)\\
&=f(R_1^{-1}R_2^{-1}\widehat r)\\
&=f((R_2R_1)^{-1}\widehat r)\\
&=[U(R_2R_1)f](\widehat r).
\end{aligned}
\]

在固定球谐基中取矩阵便有

\[
D(R_2R_1)=D(R_2)D(R_1).
\]

若写成 \(f(R\widehat r)\)，则它等于当前定义的 \(U(R^{-1})f\)，会得到逆旋转矩阵并颠倒主动作用方向。

## A17-03

\[
D^{(1)}(R_z(\pi/2))
=\operatorname{diag}(i,1,-i),
\]

\[
D^{(2)}(R_z(\pi/2))
=\operatorname{diag}(-1,i,1,-i,-1).
\]

每个对角元模为 1，故矩阵幺正。其复共轭把 \(e^{-im\alpha}\) 改为 \(e^{+im\alpha}\)，对应

\[
R_z(-\pi/2)=R_z(\pi/2)^{-1}.
\]

## A17-04

\[
C_1=
\begin{pmatrix}
s&-is&0\\
0&0&1\\
-s&-is&0
\end{pmatrix},
\qquad
s=1/\sqrt2.
\]

各行归一，第一和第三行内积为 0，中间行与其余行正交，故 \(C_1C_1^\dagger=I\)；方阵因此也满足 \(C_1^\dagger C_1=I\)。

若实基函数行是 \(\Phi_{\mathrm r}\)，则

\[
\Phi_{\mathrm c}=\Phi_{\mathrm r}C_1^{\mathsf T}.
\]

同一函数满足

\[
\Phi_{\mathrm r}c_{\mathrm r}
=\Phi_{\mathrm c}c_{\mathrm c}
=\Phi_{\mathrm r}C_1^{\mathsf T}c_{\mathrm c},
\]

所以

\[
c_{\mathrm r}=C_1^{\mathsf T}c_{\mathrm c},
\qquad
c_{\mathrm c}=C_1^*c_{\mathrm r}.
\]

\(C_1\) 映射同一点上的函数值列，\(C_1^*\) 映射展开系数；直接混用会改变共轭方向。

## A17-05

\[
C_2=
\begin{pmatrix}
-is&0&0&s&0\\
0&-is&s&0&0\\
0&0&0&0&1\\
0&-is&-s&0&0\\
is&0&0&s&0
\end{pmatrix},
\qquad
K_2=C_2^*.
\]

规范复矩阵为

\[
D_{\mathrm c}
=\operatorname{diag}(-1,i,1,-i,-1).
\]

直接乘法给出

\[
K_2^\dagger D_{\mathrm c}K_2
=
\begin{pmatrix}
-1&0&0&0&0\\
0&0&1&0&0\\
0&-1&0&0&0\\
0&0&0&-1&0\\
0&0&0&0&1
\end{pmatrix}.
\]

它与第 16 章从 \(RB_aR^{\mathsf T}\) 得到的冻结矩阵逐项相同。

## A17-06

由

\[
U(R)Y_{\ell m}
=\sum_{m'}Y_{\ell m'}D_{m'm}
\]

在 \(\widehat r\) 处取值：

\[
Y_{\ell m}(R^{-1}\widehat r)
=\sum_{m'}Y_{\ell m'}(\widehat r)D_{m'm}.
\]

把所有输入 \(m\) 组成列：

\[
y_\ell(R^{-1}\widehat r)
=D^{\mathsf T}y_\ell(\widehat r).
\]

替换 \(\widehat r\leftarrow R\widehat r\)，并用幺正性：

\[
y_\ell(R\widehat r)
=D^{-\mathsf T}y_\ell(\widehat r)
=D^*y_\ell(\widehat r).
\]

展开系数来自

\[
U(R)\sum_m c_mY_{\ell m}
=\sum_{m'}Y_{\ell m'}(Dc)_{m'},
\]

所以使用 \(D\)。只有 \(m=0\) 分量、实对角矩阵或某些对称点可能使 \(D=D^*\) 在所见子空间上成立，从而让漏共轭偶然通过。

## A17-07

记

\[
\kappa=\sqrt{\frac{3}{4\pi}}.
\]

由低阶恒等式，

\[
y_1(\widehat r)
=\kappa
\begin{pmatrix}
(1-2i)/(3\sqrt2)\\
2/3\\
-(1+2i)/(3\sqrt2)
\end{pmatrix}.
\]

\[
R\widehat r=(-2,1,2)^{\mathsf T}/3,
\]

故

\[
y_1(R\widehat r)
=\kappa
\begin{pmatrix}
(-2-i)/(3\sqrt2)\\
2/3\\
(2-i)/(3\sqrt2)
\end{pmatrix}.
\]

又

\[
D^{(1)}(R)^*
=\operatorname{diag}(-i,1,i).
\]

逐分量相乘得到上式，因而点值协变成立。

## A17-08

对 \(\ell=1\)：

\[
y_1(-\widehat r)=-y_1(\widehat r);
\]

对 \(\ell=2\)：

\[
y_2(-\widehat r)=+y_2(\widehat r).
\]

这是球谐轨道型方向函数的宇称。一般网络特征类型需要独立标签 \((\ell,p)\)；轴向量是 \((1,+)\)，所以不能从 \(\ell=1\) 单独推出奇宇称。

方向输入还必须携带有限且严格为正的特征长度 \(s\)。定义

\[
\zeta_d=\frac{\lVert d\rVert_2}{s}.
\]

float64/32 分别取 \(\tau_0=10^{-12}\) 与 \(10^{-5}\)，只有 \(\zeta_d>\tau_0\) 才接受，等于阈值时拒绝。冻结

\[
d_\varepsilon=(\varepsilon s,0,0),
\qquad
\varepsilon\in\{0,\tfrac12\tau_0,\tau_0,2\tau_0\};
\]

前三项拒绝，最后一项接受。非有限 \(d/s\)、\(s\le0\)、错误 shape 也拒绝。这只复用局部架合同的单向量零长度子规则，不需要第二向量或共线检查。

若 \(d=0\)，则 \(d/\lVert d\rVert\) 未定义。任意后备轴选择依赖实验室坐标，并且不同旋转路径可给不同极限，不能构成唯一连续等变映射。

## A17-09

规范 \(D\) 为

\[
D=\operatorname{diag}(i,1,-i).
\]

反序矩阵满足

\[
JDJ=D^*.
\]

故

\[
\begin{aligned}
D_{\mathrm{wrong}}
&=(JK_1)^\dagger D(JK_1)\\
&=K_1^\dagger JDJK_1\\
&=K_1^\dagger D^*K_1\\
&=R_z(\pi/2)^{\mathsf T}.
\end{aligned}
\]

两矩阵之差的 Frobenius 范数为 \(2\sqrt2\)，各自范数为 \(\sqrt3\)，所以

\[
\rho
=\frac{2\sqrt2}{\sqrt3}
=2\sqrt{\frac23}
\approx1.632993162.
\]

若所有点值、系数、矩阵和元数据都同步以 \(J\) 变换，则只是合法重排；这里失败源于只改系数接口。

## A17-10

幺正性只证明该矩阵保持复内积；随机点范数不变是更弱的不变量。完整门控应至少包括：

- 将 DLMF/Condon--Shortley、\(m=-2,\ldots,2\) 顺序和低阶函数定义写入元数据；
- 用 \(U(R)f=f(R^{-1}\widehat r)\) 固定主动方向；
- 对任何 Euler API 独立核对轴序、内/外禀、角顺序、主动/被动和共轭；
- 检查 \(D(I)=I\)、幺正、逆和非交换群律；
- 检查 \(R_z(\pi/2)\) 的复对角锚点；
- 检查 \(C_2\) 幺正、\(K_2=C_2^*\) 和
  \[
  D^d=K_2^\dagger D^{(2)}K_2;
  \]
- 从 \(B_a\) 共轭和复 Wigner 两条路线独立得到同一 \(D^d\)；
- 区分系数 \(c'=Dc\) 与点值 \(y(Rr)=D^*y(r)\)；
- 检查反演 \((-1)^\ell\)，并对方向输入携带有限正 \(s\)、计算 \(\zeta_d=\lVert d\rVert/s\)、按 float64/32 的 \(10^{-12}/10^{-5}\) 阈值执行等号拒绝和两侧夹具；
- 硬验证 complex64/128、rank、shape、finite、顺序、provenance 和禁止广播；
- 对 Hamiltonian 基变换只接受完整活动 \(2\ell+1\) shell 和完整 shell-pair 子块；全假 padding 在稠密 \(K_\ell\) 作用前切除，部分 component mask 必须拒绝；
- 保持 stageD-edge-v1 的 structure ID、receiver、sender、周期 shift、完整 edge key 和 edge 行序不变，并要求 Hamiltonian、表示、mask 与 provenance 共享同一块轴映射；
- 对复组件记录 shell/multiplicity、\(\ell\)、宇称、complex-dlmf-cs-v1、递增 \(m\)、完整源实 component 集合和 stageE-K-coeff-v1 的哈希；不得沿用单个实 orbital component ID；
- 核对 \(K_1/K_2\) 规范载荷 SHA-256 分别为 347E352605A3F4F3CCB078B6CEDF5C755FDC6AA3527EA41A8EA3E93D076972A2 与 5E783D9CDFE025238977F9E92D64D8B46E9A0E79EB8C9DEBA1AF116AAAFC7B82；
- 注入 \(m\) 逆序、漏相位、漏共轭、逆旋转和错实轨道顺序；
- 存储报告区分逐元素 nbytes 与完整数组 total/peak，不把复数组乘 2 关系冒充端到端结论；
- 保持 M8 前不安装 DeepH/e3nn、不使用正式数据/DFT 标签、不选择材料/后端/软件对象，M9 外部执行仍需二次授权。

只有上述对象同时通过，才有证据支持该库输出与项目规范相容；库名称和少量随机样例不能替代这些检查。
