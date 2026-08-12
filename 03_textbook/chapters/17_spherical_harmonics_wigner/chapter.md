# 第 17 章 球谐函数、Wigner \(D\) 与实—复基变换

## 17.1 球面函数与角动量基

### 17.1.1 单位球面与内积

单位方向写成

\[
\widehat r
=(\sin\theta\cos\phi,\sin\theta\sin\phi,\cos\theta),
\]

其中 \(0\le\theta\le\pi\)、\(0\le\phi<2\pi\)。复值球面函数的内积为

\[
\langle f,g\rangle
=\int_0^{2\pi}\!\int_0^\pi
f(\theta,\phi)^*g(\theta,\phi)
\sin\theta\,d\theta\,d\phi.
\]

球谐函数 \(Y_{\ell m}\) 构成该空间的正交归一基：

\[
\langle Y_{\ell m},Y_{\ell' m'}\rangle
=\delta_{\ell\ell'}\delta_{mm'}.
\]

第 16 章的实 \(p,d\) 函数是 \(\ell=1,2\) 子空间中的另一组正交归一基。

### 17.1.2 DLMF 归一化与 Condon--Shortley 相位

本项目采用 DLMF 14.30 的复球谐归一化和 Condon--Shortley 相位。数组顺序固定为

\[
m=-\ell,-\ell+1,\ldots,\ell.
\]

具体定义为

\[
Y_{\ell,m}(\theta,\phi)
=
\left[
\frac{(\ell-m)!(2\ell+1)}
{4\pi(\ell+m)!}
\right]^{1/2}
e^{im\phi}
\mathsf P_\ell^m(\cos\theta),
\]

其中 \(\mathsf P_\ell^m\) 是 DLMF 约定的 Ferrers 函数；不得在未核对其定义时再额外乘一个经验 \((-1)^m\)。

共轭关系为

\[
Y_{\ell,-m}
=(-1)^mY_{\ell m}^*
\qquad(m\ge0).
\]

相位本身属于基约定；只要全部对象同步变换，另一套相位也可描述同一表示。但本项目的序列化、CG 表和复—实矩阵必须坚持这一固定约定，不能在比较前静默改相位。

### 17.1.3 低阶显式函数

采用

\[
p_a(\widehat r)
=\sqrt{\frac{3}{4\pi}}\,\widehat r_a
\]

和第 16 章的单位球面归一化实 \(d\) 函数。低阶恒等式固定为

\[
\begin{aligned}
Y_{1,-1}&=(p_x-i p_y)/\sqrt2,&
Y_{1,0}&=p_z,&
Y_{1,1}&=-(p_x+i p_y)/\sqrt2,\\
Y_{2,-2}&=(d_{x^2-y^2}-i d_{xy})/\sqrt2,&
Y_{2,-1}&=(d_{zx}-i d_{yz})/\sqrt2,&
Y_{2,0}&=d_{3z^2-r^2},\\
Y_{2,1}&=-(d_{zx}+i d_{yz})/\sqrt2,&
Y_{2,2}&=(d_{x^2-y^2}+i d_{xy})/\sqrt2.
\end{aligned}
\]

这些等式同时固定 \(m\) 顺序、实轨道顺序、相位和复共轭方向。

## 17.2 主动旋转与 Wigner \(D\)

### 17.2.1 函数空间上的主动作用

对主动旋转 \(R\)，函数作用定义为

\[
[U(R)f](\widehat r)
=f(R^{-1}\widehat r).
\]

该逆矩阵保证

\[
U(R_2)U(R_1)=U(R_2R_1).
\]

若误写成 \(f(R\widehat r)\)，所得矩阵对应逆旋转，并与第 15 章的主动系数约定冲突。

### 17.2.2 Wigner \(D\) 的操作性定义

固定 \(\ell\) 后，

\[
U(R)Y_{\ell m}
=\sum_{m'=-\ell}^{\ell}
Y_{\ell m'}D^{(\ell)}_{m'm}(R).
\]

矩阵列标识输入 \(m\)，行标识输出 \(m'\)。展开

\[
f=\sum_m c_mY_{\ell m}
\]

在主动旋转后具有系数

\[
c'=D^{(\ell)}(R)c.
\]

这一定义不依赖某个 Euler 角库的参数顺序。

### 17.2.3 幺正性、逆与群律

旋转保持球面积分和内积，因此

\[
D^{(\ell)}(R)^\dagger D^{(\ell)}(R)=I,
\]

\[
D^{(\ell)}(R^{-1})
=D^{(\ell)}(R)^{-1}
=D^{(\ell)}(R)^\dagger,
\]

\[
D^{(\ell)}(R_2R_1)
=D^{(\ell)}(R_2)D^{(\ell)}(R_1).
\]

幺正性、逆关系和群律是不同检查；单个矩阵幺正不能证明它对应正确旋转或正确复合顺序。

### 17.2.4 绕 \(z\) 轴的解析锚点

由 \(\phi\mapsto\phi-\alpha\)，

\[
U(R_z(\alpha))Y_{\ell m}
=e^{-im\alpha}Y_{\ell m}.
\]

故在 \(m\) 递增顺序中

\[
D^{(\ell)}_{m'm}(R_z(\alpha))
=\delta_{m'm}e^{-im\alpha}.
\]

对 \(\ell=1\)，对角元依次为

\[
(e^{i\alpha},1,e^{-i\alpha});
\]

对 \(\ell=2\)，依次为

\[
(e^{2i\alpha},e^{i\alpha},1,e^{-i\alpha},e^{-2i\alpha}).
\]

### 17.2.5 Euler 角接口的风险

同样三个角可能因下列约定给出不同数组：

- 主动旋转或被动换基；
- 内禀轴或外禀轴；
- 轴序，例如 \(ZYZ\) 或 \(XYZ\)；
- 矩阵乘法顺序、复共轭方向和 \(m\) 顺序。

因此，使用 Euler 角公式时必须先通过 \(R_z(\alpha)\)、非交换双旋转、点值关系和实—复相似变换，不能只核对 shape。

## 17.3 \(\ell=1\) 的复—实映射

### 17.3.1 函数值映射 \(C_1\)

定义实函数值列

\[
r_1=(p_x,p_y,p_z)^{\mathsf T}
\]

和复函数值列

\[
y_1=(Y_{1,-1},Y_{1,0},Y_{1,1})^{\mathsf T}.
\]

上述恒等式写成

\[
y_1=C_1r_1,
\]

\[
C_1=
\begin{pmatrix}
1/\sqrt2&-i/\sqrt2&0\\
0&0&1\\
-1/\sqrt2&-i/\sqrt2&0
\end{pmatrix}.
\]

直接计算

\[
C_1C_1^\dagger=C_1^\dagger C_1=I_3.
\]

### 17.3.2 函数映射与系数映射不能混用

函数基恒等式使用 \(C_1\)，但同一函数的展开系数满足

\[
c_{\mathrm{complex}}
=K_1c_{\mathrm{real}},
\qquad
K_1=C_1^*.
\]

其原因是基函数按 \(y_1=C_1r_1\) 变换，而系数必须用逆转置保持函数本身不变。由于 \(C_1\) 幺正，逆转置正是 \(C_1^*\)。

因此表示矩阵满足

\[
D^{(1)}_{\mathrm{complex}}(R)
=K_1D^p(R)K_1^\dagger
=C_1^*R C_1^{\mathsf T},
\]

\[
D^p(R)
=K_1^\dagger
D^{(1)}_{\mathrm{complex}}(R)K_1
=C_1^{\mathsf T}
D^{(1)}_{\mathrm{complex}}(R)C_1^*.
\]

若把函数值矩阵 \(C_1\) 误用于系数映射，会得到逆转置方向。

### 17.3.3 \(D^p=R\) 的复核

对 \(R_z(\pi/2)\)，复表示为

\[
\operatorname{diag}(i,1,-i).
\]

代入相似变换：

\[
C_1^{\mathsf T}
\operatorname{diag}(i,1,-i)
C_1^*
=
\begin{pmatrix}
0&-1&0\\
1&0&0\\
0&0&1
\end{pmatrix}
=R_z(\pi/2).
\]

这同时验证相位、\(m\) 顺序和系数映射方向。

## 17.4 \(\ell=2\) 的复—实映射

### 17.4.1 映射矩阵 \(C_2\)

令实函数值列按

\[
r_2=(d_{xy},d_{yz},d_{zx},d_{x^2-y^2},d_{3z^2-r^2})^{\mathsf T},
\]

复函数值列按 \(m=-2,-1,0,1,2\) 排列。则

\[
y_2=C_2r_2,
\]

\[
C_2=
\begin{pmatrix}
-i/\sqrt2&0&0&1/\sqrt2&0\\
0&-i/\sqrt2&1/\sqrt2&0&0\\
0&0&0&0&1\\
0&-i/\sqrt2&-1/\sqrt2&0&0\\
i/\sqrt2&0&0&1/\sqrt2&0
\end{pmatrix}.
\]

每一行和每一列均归一且两两正交，故

\[
C_2C_2^\dagger=C_2^\dagger C_2=I_5.
\]

### 17.4.2 系数映射与相似变换

定义

\[
K_2=C_2^*,
\qquad
c_{\mathrm{complex}}=K_2c_{\mathrm{real}}.
\]

则

\[
D^{(2)}_{\mathrm{complex}}(R)
=K_2D^d(R)K_2^\dagger,
\]

\[
D^d(R)
=K_2^\dagger
D^{(2)}_{\mathrm{complex}}(R)K_2.
\]

因此第 16 章的对称无迹张量构造与复 Wigner 构造描述同一个 \(\ell=2\) 表示。

### 17.4.3 \(R_z(\pi/2)\) 的双路线锚点

复表示为

\[
\operatorname{diag}(-1,i,1,-i,-1).
\]

通过 \(K_2^\dagger D^{(2)}K_2\) 得到

\[
\begin{pmatrix}
-1&0&0&0&0\\
0&0&1&0&0\\
0&-1&0&0&0\\
0&0&0&-1&0\\
0&0&0&0&1
\end{pmatrix},
\]

与第 16 章从 \(B_a\) 共轭得到的 \(D^d\) 完全一致。

## 17.5 点值与系数协变

### 17.5.1 复球谐点值关系

令

\[
y_\ell(\widehat r)
=(Y_{\ell,-\ell},\ldots,Y_{\ell,\ell})^{\mathsf T}.
\]

由操作性定义逐分量得到

\[
y_\ell(R^{-1}\widehat r)
=D^{(\ell)}(R)^{\mathsf T}y_\ell(\widehat r).
\]

等价地，

\[
y_\ell(R\widehat r)
=D^{(\ell)}(R)^*y_\ell(\widehat r).
\]

点值列使用 \(D^*\)，展开系数使用 \(D\)。二者对象不同，漏掉共轭会在一般复旋转上失败。

### 17.5.2 实函数点值关系

对实 \(p,d\) 函数值列，

\[
r_\ell(R\widehat r)
=D_{\mathrm{real}}^{(\ell)}(R)r_\ell(\widehat r),
\]

因为实表示正交且函数值与笛卡尔张量直接对应。这一关系与

\[
y_\ell=C_\ell r_\ell
\]

及复相似变换相容。

### 17.5.3 数值求积和随机点的证据边界

解析正交关系给出连续球面的精确结论；有限求积只能在其精度和可积函数范围内提供数值证据。随机点协变测试可暴露相位、顺序和共轭错误，但有限样本不能证明全域恒等式。阶段 E 应同时保留：

- 低阶解析恒等式；
- 复—实矩阵幺正性；
- 表示群律；
- 固定与随机球面点的点值协变；
- 定向错误夹具。

## 17.6 球谐方向特征

### 17.6.1 相对位移与零长度

球谐方向输入必须同时携带相对位移 \(d\) 和显式特征长度 \(s\)。要求 \(d\) 有限，且 \(s\) 有限并严格大于 0。先计算无量纲长度

\[
\zeta_d=\frac{\lVert d\rVert_2}{s}.
\]

float64 使用 \(\tau_0=10^{-12}\)，float32 使用 \(\tau_0=10^{-5}\)。若

\[
\zeta_d\le\tau_0,
\]

则拒绝；等于阈值时也拒绝。只有通过后才定义

\[
\widehat d=\frac d{\lVert d\rVert_2}.
\]

阈值夹具固定

\[
d_\varepsilon=(\varepsilon s,0,0),
\qquad
\varepsilon\in\{0,\tfrac12\tau_0,\tau_0,2\tau_0\}.
\]

前三项必须拒绝，最后一项必须接受，并记录实际 \(\zeta_d\)。NaN、无穷、\(s\le0\)、错误 rank/shape 也必须拒绝。这里仅复用统一局部架合同的“单向量零长度子规则”，不要求第二参考向量，也不执行共线指标 \(\eta\)；本对象映射到 T-E04 的方向求值和 T-E12 的 schema/失败矩阵。

### 17.6.2 径向与角向分工

球谐只描述方向。典型方向特征写成

\[
\phi_{\ell m}(d)
=g_\ell(\lVert d\rVert)Y_{\ell m}(\widehat d),
\]

其中 \(g_\ell\) 是旋转不变的径向标量。若径向函数错误依赖实验室坐标分量，它会破坏整体等变性。

### 17.6.3 反演宇称

\[
Y_{\ell m}(-\widehat d)
=(-1)^\ell Y_{\ell m}(\widehat d).
\]

因此球谐方向通道的轨道型宇称为 \((-1)^\ell\)。一般网络特征仍需显式记录 \((\ell,p)\)，不能把所有同 \(\ell\) 通道都默认为球谐轨道宇称。

## 17.7 例题、失败样例与验证

### 17.7.1 例题入口

[examples.md](examples.md) 包含：

1. \(z\) 轴旋转的复 Wigner 对角矩阵；
2. \(C_1,K_1\) 与 \(D^p=R\)；
3. \(C_2,K_2\)、\(D^d\) 与非 \(z\) 轴 \(R_x(\pi/2)\) 的复矩阵；
4. 固定球面点的点值协变；
5. 实—复系数往返；
6. 反演宇称；
7. 零长度方向拒绝；
8. 未同步 \(m\) 逆序的定量失败。

### 17.7.2 验证矩阵

至少检查：

- \(C_\ell\) 和 \(K_\ell\) 的 dtype、shape、有限性与幺正性；
- \(m\) 顺序、实轨道顺序及低阶函数恒等式；
- \(D^{(\ell)}\) 的幺正性、逆和非交换群律；
- 实—复相似变换与实 \(p,d\) 锚点；
- 复点值 \(D^*\) 和系数 \(D\) 的不同方向；
- 反演宇称、零长度拒绝和 float64/32 阈值；
- \(m\) 逆序、漏 Condon--Shortley 相位、漏共轭和错误 Euler 方向的失败样例。

### 17.7.3 精度与存储边界

complex128 每个元素为 16 bytes，complex64 为 8 bytes；相同分量数的复数组裸值字节是 float64/32 实数组的两倍。该结论只描述数组元素存储，不含库临时量、FFT、球谐生成器或图 contraction。T-E10 的完整 total/peak 和 FLOP 已由 M7-09 的冻结 kernel 给出，见 [代码说明](../../../05_code_exercises/stageE_synthetic_equivariance/README.md)。

### 17.7.4 推导、练习与测试入口

D-E03 与本章 D-E09 子对象见 [解析推导](../../../04_derivations/stageE/17_spherical_harmonics_wigner.md)。Q17-01—Q17-10 与 A17-01—A17-10 覆盖相位、函数/系数映射、相似变换、点值、宇称与验证边界。T-E04 负责复—实、点值和无量纲方向 validator，T-E06 负责 Hamiltonian 块身份接口，T-E07 负责宇称，T-E10 负责成本口径，T-E12 负责 schema、mask 和失败矩阵；实际 A/B 证据见 [Stage E 代码说明](../../../05_code_exercises/stageE_synthetic_equivariance/README.md) 与 [M7-09 定点复核](../../../08_audits/M7_stageE_code_blocking_reaudit.md)。

## 17.8 与张量积和 Hamiltonian 的接口

### 17.8.1 CG 相位依赖

第 18 章的 CG 系数在复球谐基中定义。若对某个 \(\ell\) 基改变相位，所有含该输入或输出的 CG 张量都必须同步变换。整条不可约输出通道的共同相位是合法基自由；局部 \(m\) 系数的未同步变化通常破坏规范表或 intertwiner。

### 17.8.2 Hamiltonian 的基变换

若节点两端的系数基变换分别为 \(K_i,K_j\)，Hamiltonian 表示需同步变换：

\[
H_{\mathrm{complex}}
=K_iH_{\mathrm{real}}K_j^\dagger.
\]

表示矩阵也按同一 \(K\) 相似变换。只转换 Hamiltonian 而不转换 \(D_i,D_j\)、轨道顺序和 provenance，不能保持协变关系。

该式只能在完整有效的不可约 shell 块上执行。对节点 \(i\)，

\[
K_i=\bigoplus_{\alpha\in\mathcal S_i^{\mathrm{active}}}
K_{\ell_\alpha},
\]

其中 \(\alpha\) 保留 shell ID 与 multiplicity ID，每个活动 shell 必须包含完整 \(2\ell_\alpha+1\) 个分量。component mask 对一个 shell 只能全真或全假；部分分量有效的 shell 必须拒绝基变换。padding shell 在稠密 \(K_\ell\) 作用前切除，变换完成后按原槽位重新填回并保持全假 mask，禁止让稠密矩阵穿过有效—padding 边界。

对 Hamiltonian 的一对 shell，只有对应的

\[
(2\ell_i+1)\times(2\ell_j+1)
\]

子块全部有效时才执行 \(K_{\ell_i}H K_{\ell_j}^\dagger\)。部分有效子块不得通过填零后变换来伪造完整信息。

纯轨道基变换不改变结构与边身份。以下字段及 edge 行序必须逐行保持：

\[
(\text{stageD-edge-v1},\text{structure ID},
\text{receiver},\text{sender},n_x,n_y,n_z).
\]

Hamiltonian、表示矩阵、component mask 与 provenance 必须使用同一 shell-pair 块轴映射。复基分量的 provenance 至少记录：structure/atom/edge key、shell ID、multiplicity ID、\(\ell\)、宇称、目标 basis family、递增 \(m\) component、源实分量顺序以及 \(K\) 的版本和哈希。复分量是多个实轨道分量的线性组合，不得继续伪装成一个未变化的实 orbital component ID。

系数映射的规范版本为 stageE-K-coeff-v1。其精确符号 JSON 载荷与哈希在 D-E03 第 12 节冻结：

| \(\ell\) | 实分量顺序 | 复分量顺序 | SHA-256 |
|---:|---|---|---|
| 1 | \(p_x,p_y,p_z\) | \(m=-1,0,1\) | 347E352605A3F4F3CCB078B6CEDF5C755FDC6AA3527EA41A8EA3E93D076972A2 |
| 2 | \(d_{xy},d_{yz},d_{zx},d_{x^2-y^2},d_{3z^2-r^2}\) | \(m=-2,-1,0,1,2\) | 5E783D9CDFE025238977F9E92D64D8B46E9A0E79EB8C9DEBA1AF116AAAFC7B82 |

### 17.8.3 章节门控与授权边界

本章完成必须同时满足：

- DLMF/Condon--Shortley、\(m\) 顺序和主动函数作用唯一；
- \(C_1,C_2\) 与系数映射 \(K_1,K_2\) 不混用；
- \(p,d\) 两条相似变换与第 16 章实表一致；
- 点值 \(D^*\) 和系数 \(D\) 的对象边界明确；
- 零长度、宇称、错顺序、错相位、漏共轭与 Euler 风险均有失败入口；
- D-E03/D-E09 子推导、八个例题、10 道题解、严格格式和独立审计通过。

本章不安装或调用 e3nn/DeepH，不使用正式数据或 DFT 标签，不选择 Euler 软件接口、材料、后端、DeepH 软件对象、实践版本或高级物理范围。

### 17.8.4 章节小结

Wigner \(D\) 由主动函数作用 \(f(R^{-1}\widehat r)\) 唯一定义。复球谐点值、展开系数和实轨道系数虽然描述同一表示，却分别使用 \(D^*\)、\(D\) 和经 \(K_\ell\) 相似变换后的实矩阵；把这些对象的转置或共轭方向混用会产生稳定非零残差。

\(C_1,C_2\) 固定函数值基关系，\(K_\ell=C_\ell^*\) 固定系数关系。它们把 DLMF 复球谐与第 16 章实 \(p,d\) 张量表示连接起来，并为第 18 章 CG 相位规范和第 19 章 Hamiltonian 复—实基变换提供唯一接口。
