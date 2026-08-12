# 第 17 章例题

## 例题 1：绕 \(z\) 轴的 Wigner 对角矩阵

对

\[
R=R_z(\pi/2),
\]

操作性定义给出

\[
D^{(1)}(R)=\operatorname{diag}(i,1,-i)
\]

和

\[
D^{(2)}(R)=\operatorname{diag}(-1,i,1,-i,-1),
\]

其中顺序分别为 \(m=-1,0,1\) 和 \(m=-2,-1,0,1,2\)。两矩阵均幺正。

若把主动作用误写为 \(f(R\widehat r)\)，指数变为 \(e^{+im\alpha}\)，这里会得到上述矩阵的共轭，也就是逆旋转表示。

## 例题 2：\(C_1\)、\(K_1\) 与实 \(p\) 表

函数值关系为

\[
y_1=C_1r_1,
\qquad
C_1=
\begin{pmatrix}
s&-is&0\\
0&0&1\\
-s&-is&0
\end{pmatrix},
\qquad
s=\frac1{\sqrt2}.
\]

系数关系则是

\[
c_{\mathrm c}=K_1c_{\mathrm r},
\qquad
K_1=C_1^*.
\]

对例题 1 的 \(D^{(1)}\)，

\[
K_1^\dagger D^{(1)}K_1
=
\begin{pmatrix}
0&-1&0\\
1&0&0\\
0&0&1
\end{pmatrix}.
\]

这正是 \(D^p(R_z(\pi/2))\)。若用 \(C_1\) 代替 \(K_1\) 转换系数，会得到相反旋转。

## 例题 3：\(C_2\) 与实 \(d\) 表

按冻结实 \(d\) 顺序，

\[
C_2=
\begin{pmatrix}
-is&0&0&s&0\\
0&-is&s&0&0\\
0&0&0&0&1\\
0&-is&-s&0&0\\
is&0&0&s&0
\end{pmatrix}.
\]

直接计算

\[
C_2C_2^\dagger=I_5.
\]

令 \(K_2=C_2^*\)，则

\[
K_2^\dagger D^{(2)}(R_z(\pi/2))K_2
=
\begin{pmatrix}
-1&0&0&0&0\\
0&0&1&0&0\\
0&-1&0&0&0\\
0&0&0&-1&0\\
0&0&0&0&1
\end{pmatrix},
\]

与对称无迹张量路线完全一致。

### 非 \(z\) 轴工作例：\(R_x(\pi/2)\)

取

\[
R_x(\pi/2)=
\begin{pmatrix}
1&0&0\\
0&0&-1\\
0&1&0
\end{pmatrix}.
\]

第 16 章张量公式先给出

\[
D^d_{\mathrm r}(R_x)=
\begin{pmatrix}
0&0&-1&0&0\\
0&-1&0&0&0\\
1&0&0&0&0\\
0&0&0&1/2&-\sqrt3/2\\
0&0&0&-\sqrt3/2&-1/2
\end{pmatrix}.
\]

两条系数相似变换得到

\[
D^{(1)}_{\mathrm c}(R_x)
=K_1R_xK_1^\dagger
=
\begin{pmatrix}
1/2&-i/\sqrt2&-1/2\\
-i/\sqrt2&0&-i/\sqrt2\\
-1/2&-i/\sqrt2&1/2
\end{pmatrix},
\]

\[
D^{(2)}_{\mathrm c}(R_x)
=K_2D^d_{\mathrm r}(R_x)K_2^\dagger
=
\begin{pmatrix}
1/4&-i/2&-\sqrt6/4&i/2&1/4\\
-i/2&-1/2&0&-1/2&i/2\\
-\sqrt6/4&0&-1/2&0&-\sqrt6/4\\
i/2&-1/2&0&-1/2&-i/2\\
1/4&i/2&-\sqrt6/4&-i/2&1/4
\end{pmatrix}.
\]

直接乘法满足

\[
D^{(1)}_{\mathrm c}(R_x)^4=I_3,
\qquad
D^{(2)}_{\mathrm c}(R_x)^4=I_5,
\]

并且用 \(K_\ell^\dagger D_{\mathrm c}^{(\ell)}K_\ell\) 分别回到 \(R_x\) 与上述实 \(D^d_{\mathrm r}(R_x)\)。这给出不依赖 \(z\) 轴对角化的可复算工作例。

## 例题 4：复球谐点值使用 \(D^*\)

取单位方向

\[
\widehat r=(1,2,2)^{\mathsf T}/3
\]

以及 \(R=R_z(\pi/2)\)。记

\[
\kappa=\sqrt{\frac{3}{4\pi}}.
\]

原点值为

\[
y_1(\widehat r)
=\kappa
\begin{pmatrix}
(1-2i)/(3\sqrt2)\\
2/3\\
-(1+2i)/(3\sqrt2)
\end{pmatrix}.
\]

旋转方向为

\[
R\widehat r=(-2,1,2)^{\mathsf T}/3,
\]

直接代入球谐恒等式得到

\[
y_1(R\widehat r)
=\kappa
\begin{pmatrix}
(-2-i)/(3\sqrt2)\\
2/3\\
(2-i)/(3\sqrt2)
\end{pmatrix}.
\]

例题 1 的 \(D^{(1)}(R)^*=\operatorname{diag}(-i,1,i)\) 乘原点值给出同一结果。若使用 \(D\) 而非 \(D^*\)，第一和第三分量失败。

## 例题 5：实—复系数往返

取实 \(p\) 系数

\[
c_{\mathrm r}=(1,2,-1)^{\mathsf T}.
\]

复系数为

\[
c_{\mathrm c}=K_1c_{\mathrm r}
=
\begin{pmatrix}
(1+2i)/\sqrt2\\
-1\\
(-1+2i)/\sqrt2
\end{pmatrix}.
\]

由于 \(K_1\) 幺正，

\[
K_1^\dagger c_{\mathrm c}=c_{\mathrm r},
\qquad
\lVert c_{\mathrm c}\rVert_2^2
=\lVert c_{\mathrm r}\rVert_2^2
=6.
\]

若函数值矩阵与系数矩阵混用，往返一般不再恢复原列向量。

## 例题 6：反演宇称

空间反演把方向变为 \(-\widehat r\)。球谐满足

\[
Y_{\ell m}(-\widehat r)
=(-1)^\ell Y_{\ell m}(\widehat r).
\]

因此

\[
y_1(-\widehat r)=-y_1(\widehat r),
\qquad
y_2(-\widehat r)=+y_2(\widehat r).
\]

这与实 \(p\) 的奇宇称和实 \(d\) 的偶宇称一致。该结论只针对球谐轨道型通道；一般轴向 \((1,+)\) 特征不是 \(Y_{1m}\) 方向函数。

## 例题 7：零长度位移没有球谐方向

球谐方向输入为 \((d,s,\mathrm{dtype})\)，其中 \(s\) 必须有限且严格为正。定义

\[
\zeta_d=\frac{\lVert d\rVert_2}{s}.
\]

float64/float32 分别使用

\[
\tau_0=10^{-12},
\qquad
\tau_0=10^{-5}.
\]

若 \(\zeta_d\le\tau_0\) 则拒绝，等于阈值时拒绝。取 \(s=2\) 和

\[
d_\varepsilon=(2\varepsilon,0,0),
\qquad
\varepsilon\in\{0,\tfrac12\tau_0,\tau_0,2\tau_0\}.
\]

前三个夹具的 \(\zeta_d\) 分别为 \(0,\tau_0/2,\tau_0\)，必须拒绝；第四个为 \(2\tau_0\)，必须接受并得到 \(\widehat d=e_x\)。把 \(s\) 和 \(d\) 同时缩放同一正因子不改变 \(\zeta_d\)，因此判定不依赖长度单位。

该合同只复用局部架的单向量零长度规则，不需要第二参考向量或共线检查。若 \(s\) 非有限、非正，或 \(d\) 含 NaN/无穷，也必须在归一化前拒绝。任意后备轴会引入依赖实验室坐标的方向，不能作为等变修复。

## 例题 8：未同步 \(m\) 逆序的定量失败

令 \(J\) 为反转 \(m\) 顺序的置换矩阵。如果把系数映射错误改为

\[
K_{\mathrm{wrong}}=JK_1,
\]

却仍把规范顺序的

\[
D^{(1)}(R_z(\pi/2))
=\operatorname{diag}(i,1,-i)
\]

直接传入，则恢复的实矩阵是

\[
D_{\mathrm{wrong}}
=K_{\mathrm{wrong}}^\dagger
D^{(1)}K_{\mathrm{wrong}}
=R_z(\pi/2)^{\mathsf T}.
\]

与正确 \(R_z(\pi/2)\) 的归一化 Frobenius 残差为

\[
\rho
=\frac{\lVert R-R^{\mathsf T}\rVert_F}{\sqrt3}
=2\sqrt{\frac23}
\approx1.632993162.
\]

该错误远大于 \(10^{-4}\)。如果同时用 \(J\) 相似变换所有矩阵、点值、系数和元数据，则只是合法基重排；这里失败的原因是只改了一个接口。
