# D-D01/D-D02：监督回归梯度与结构组泄漏

## D-D01：MSE 与一层 tanh 回归的梯度

设

\[
X\in\mathbb R^{M\times d},\quad
W\in\mathbb R^{d\times q},\quad
b,v\in\mathbb R^q,\quad
c\in\mathbb R,
\]

\[
Z=XW+\mathbf1b^\mathsf T,\qquad
H=\tanh Z,\qquad
\widehat y=Hv+c\mathbf1.
\]

损失固定为

\[
L=\frac1M(\widehat y-y)^\mathsf T(\widehat y-y).
\]

令 \(r=\widehat y-y\)。由微分

\[
\mathrm dL
=\frac2M r^\mathsf T\mathrm d\widehat y
\]

定义

\[
\delta_y=\frac2M r.
\]

输出层微分为

\[
\mathrm d\widehat y
=(\mathrm dH)v+H\,\mathrm dv+\mathbf1\,\mathrm dc.
\]

因此

\[
\nabla_vL=H^\mathsf T\delta_y,
\qquad
\frac{\partial L}{\partial c}
=\mathbf1^\mathsf T\delta_y,
\]

且传回隐藏层的伴随量为

\[
\frac{\partial L}{\partial H}
=\delta_yv^\mathsf T.
\]

逐元素使用

\[
\mathrm dH=(1-H\odot H)\odot\mathrm dZ
\]

得到

\[
\delta_Z
=(\delta_yv^\mathsf T)\odot(1-H\odot H).
\]

再由

\[
\mathrm dZ=X\,\mathrm dW+\mathbf1\,\mathrm db^\mathsf T
\]

得到

\[
\nabla_WL=X^\mathsf T\delta_Z,
\qquad
\nabla_bL=\delta_Z^\mathsf T\mathbf1.
\]

形状检查为

\[
\delta_y\in\mathbb R^M,\quad
\delta_Z\in\mathbb R^{M\times q},\quad
\nabla_WL\in\mathbb R^{d\times q},\quad
\nabla_bL,\nabla_vL\in\mathbb R^q.
\]

中心有限差分只用于检查上述实现。对每个参数分量采用

\[
\epsilon_k
=
\frac{|g_k-g_k^{\mathrm{FD}}|}
{\max(1,|g_k|,|g_k^{\mathrm{FD}}|)}
\]

并扫描 \(h\in\{10^{-3},10^{-4},10^{-5},10^{-6}\}\)。T-D02 要求至少一个冻结步长配置的最大 \(\epsilon_k\le10^{-5}\)，同时注入“输出梯度符号翻转”和“遗漏 \(1/M\)”两种失败实现。

该推导不使用自动微分库；它验证一个冻结教学网络的链式法则，不能替代任意框架或任意网络的梯度正确性。

## D-D02：为什么逐帧随机划分低估新组误差

考虑简化模型

\[
y_{g,t}=a x_{g,t}+b_g+\varepsilon_{g,t},
\]

其中

\[
\mathbb E[b_g]=0,\qquad
\operatorname{Var}(b_g)=\sigma_b^2,\qquad
\mathbb E[\varepsilon_{g,t}]=0,\qquad
\operatorname{Var}(\varepsilon_{g,t})=\sigma_\varepsilon^2.
\]

并假设不同组的 \(b_g\) 独立，测试帧噪声分别与已见组的估计误差以及新组的 \(b_g\) 不相关；独立性是这一不相关条件的充分条件。若这些条件不成立，后续均方分解必须保留协方差项。

假设模型在训练中能够为已见组估计 \(\widehat b_g\)。定义

\[
\delta_g=\widehat b_g-b_g,
\qquad
\tau_g^2:=\mathbb E[\delta_g^2].
\]

这里 \(\tau_g^2\) 是均方误差，不要求 \(\delta_g\) 无偏；若改用方差，还必须另加 \(\mathbb E[\delta_g]^2\)。若同一组在训练和测试同时出现，预测误差为 \(e_{\mathrm{seen}}=\delta_g-\varepsilon_{g,t}\)，所以一般有

\[
\mathbb E[e_{\mathrm{seen}}^2]
=\tau_g^2+\sigma_\varepsilon^2
-2\operatorname{Cov}(\delta_g,\varepsilon_{g,t}).
\]

在冻结的不相关条件下，交叉项为零，故

\[
\mathbb E[e_{\mathrm{seen}}^2]
=\tau_g^2+\sigma_\varepsilon^2.
\]

若测试组完全未见，而模型只能使用总体均值 \(0\) 作为组偏置，则预测误差为 \(e_{\mathrm{new}}=-b_g-\varepsilon_{g,t}\)，一般有

\[
\mathbb E[e_{\mathrm{new}}^2]
=\sigma_b^2+\sigma_\varepsilon^2
+2\operatorname{Cov}(b_g,\varepsilon_{g,t}).
\]

在冻结的不相关条件下，交叉项同样为零。此时若已见组估计有效，即 \(\tau_g^2<\sigma_b^2\)，逐帧随机划分的期望平方误差低于新组评价，且差为

\[
\mathbb E[e_{\mathrm{new}}^2]
-\mathbb E[e_{\mathrm{seen}}^2]
=\sigma_b^2-\tau_g^2>0.
\]

这一结论依赖上述随机效应模型、均方定义和不相关条件，不是所有数据集上的普遍定量界。若估计误差有任意均值，\(\tau_g^2\) 已把偏差平方包括在内；若任一协方差不为零，则差还要加入相应交叉项，符号可能改变，不能再无条件声称逐帧评价系统性偏低。该模型揭示的机制是：组共享潜变量同时进入训练和测试，使评价条件发生变化。

可执行泄漏检查只需要组集合：

\[
\mathcal G_{\mathrm{tr}}\cap\mathcal G_{\mathrm{va}},
\quad
\mathcal G_{\mathrm{tr}}\cap\mathcal G_{\mathrm{te}},
\quad
\mathcal G_{\mathrm{va}}\cap\mathcal G_{\mathrm{te}}.
\]

任一交集非空即判定显式组泄漏。该检查的失败边界是：错误或过细的 group ID 可以让同一物理母结构使用不同 ID，从而逃过集合检查。因此后续数据 schema 还必须保存母结构哈希和生成血缘。
