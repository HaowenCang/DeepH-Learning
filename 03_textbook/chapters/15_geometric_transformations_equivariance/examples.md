# 第 15 章例题

## 例题 1：主动与被动 \(90^\circ\) 旋转

取

\[
R=
\begin{pmatrix}
0&-1&0\\
1&0&0\\
0&0&1
\end{pmatrix},
\qquad
v=e_x.
\]

主动旋转给出

\[
Rv=e_y.
\]

若同一个 \(R\) 描述新坐标基相对旧基的旋转，则同一物理向量在新基中的坐标是

\[
R^{\mathsf T}v=-e_y.
\]

两结果符号相反不是矛盾，而是作用对象不同。失败样例是把主动任务的期望值写成 \(R^{\mathsf T}v\)。

## 例题 2：行晶格的主动旋转

设

\[
A=
\begin{pmatrix}
2&0&0\\
0&1&0\\
0&0&3
\end{pmatrix},
\qquad
f=(1/4,1/2,1/3),
\]

仍取例题 1 的 \(R\)。行存储的主动旋转是

\[
A'=AR^{\mathsf T}
=
\begin{pmatrix}
0&2&0\\
-1&0&0\\
0&0&3
\end{pmatrix}.
\]

原笛卡尔行坐标为

\[
r=fA=(1/2,1/2,1),
\]

旋转后

\[
r'=fA'=(-1/2,1/2,1)=rR^{\mathsf T}.
\]

若写成 \(RA\)，矩阵左乘会混合晶格行索引，不能表示对每条行晶格矢量施加同一物理旋转。

## 例题 3：距离和点积不变

取

\[
u=(1,2,-1)^{\mathsf T},
\qquad
v=(2,-1,3)^{\mathsf T},
\]

以及任意 \(Q\in O(3)\)。有

\[
(Qu)^{\mathsf T}(Qv)
=u^{\mathsf T}Q^{\mathsf T}Qv
=u^{\mathsf T}v=-3,
\]

\[
\lVert Qu-Qv\rVert_2
=\lVert Q(u-v)\rVert_2
=\lVert u-v\rVert_2
=\sqrt{26}.
\]

其中 \(u-v=(-1,3,-4)^{\mathsf T}\)，故平方距离严格为 \(1+9+16=26\)。该整数等式也是防止距离锚点回归的直接检查。

该证明同时适用于反射，因为只使用 \(Q^{\mathsf T}Q=I\)，没有使用 \(\det Q=1\)。

## 例题 4：叉积为何是轴向量

取空间反演 \(Q=-I\)、\(u=e_x\)、\(v=e_y\)。则

\[
Qu=-e_x,\qquad Qv=-e_y,
\]

\[
(Qu)\times(Qv)=e_z.
\]

若把 \(u\times v=e_z\) 当作极向量，应得到

\[
Qe_z=-e_z,
\]

与直接计算冲突。正确公式是

\[
(Qu)\times(Qv)=\det(Q)Q(u\times v)
=(-1)(-I)e_z=e_z.
\]

## 例题 5：二阶张量协变

令

\[
T=
\begin{pmatrix}
2&1&0\\
1&-1&2\\
0&2&3
\end{pmatrix},
\]

并用例题 1 的 \(R\)。直接计算

\[
T'=RTR^{\mathsf T}
=
\begin{pmatrix}
-1&-1&-2\\
-1&2&0\\
-2&0&3
\end{pmatrix}.
\]

检查

\[
\operatorname{tr}(T')=4=\operatorname{tr}(T),
\]

且 \(\lVert T'\rVert_F=\lVert T\rVert_F\)。只左乘 \(RT\) 一般既不保持对称性，也不是二阶张量的正确作用。

## 例题 6：向量线性映射何时旋转等变

设 \(F(v)=Mv\)，要求对所有 \(R\in SO(3)\)

\[
F(Rv)=RF(v).
\]

等价于

\[
MR=RM
\quad\text{对所有 }R\in SO(3).
\]

在实三维标准不可约表示上，这迫使

\[
M=\lambda I.
\]

例如 \(M=\operatorname{diag}(1,2,3)\) 对绕 \(z\) 轴 \(90^\circ\) 旋转不交换。取 \(v=e_x\)：

\[
F(Rv)=F(e_y)=2e_y,
\qquad
RF(v)=R e_x=e_y.
\]

残差非零。各向同性线性缩放才对所有旋转等变。

## 例题 7：周期边身份与位移

设行晶格 \(A=I\)，

\[
f_i=(0.9,0.2,0.1),
\qquad
f_j=(0.1,0.2,0.1),
\qquad
n=(1,0,0).
\]

边位移为

\[
d_{\mathrm{row}}
=(f_j+n-f_i)A=(0.2,0,0).
\]

用例题 1 的 \(R\) 主动旋转：

\[
A'=AR^{\mathsf T},
\qquad
d'_{\mathrm{row}}
=(f_j+n-f_i)A'=(0,0.2,0).
\]

完整键仍为 \((i,j,1,0,0)\)，距离仍为 0.2。把旋转解释为重新选择周期镜像并修改 \(n\) 是错误的。

## 例题 8：归一化残差与错误转置

取非对称向量

\[
v=(1,2,4)^{\mathsf T},
\]

以及绕 \(z\) 轴 \(60^\circ\) 的主动旋转 \(R\)。正确目标是 \(a=Rv\)。错误实现给出 \(b=R^{\mathsf T}v\)。两者的第三分量相同，但平面分量不同：

\[
a=
\begin{pmatrix}
\tfrac12-\sqrt3\\
\tfrac{\sqrt3}{2}+1\\
4
\end{pmatrix},
\qquad
b=
\begin{pmatrix}
\tfrac12+\sqrt3\\
-\tfrac{\sqrt3}{2}+1\\
4
\end{pmatrix}.
\]

差的范数为

\[
\lVert a-b\rVert_2=2\sqrt{15/4}=\sqrt{15}.
\]

按统一残差

\[
\rho(a,b)
=\frac{\sqrt{15}}{\max(1,\lVert a\rVert_2,\lVert b\rVert_2)}
=\frac{\sqrt{15}}{\sqrt{21}}
=\sqrt{\frac57},
\]

远大于 \(10^{-4}\)。非对称夹具能稳定识别主动/被动混淆。
