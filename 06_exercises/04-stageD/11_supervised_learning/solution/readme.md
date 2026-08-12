# 第 11 章练习：参考解答

## A11-01

样本写为 \((x_s,y_s,g_s)\)，分别表示输入、标签和结构组。训练集用于参数更新及训练统计量拟合；验证集用于超参数、早停和模型选择；测试集只在流程冻结后进行最终评价。固定种子只保证某次随机过程可重现，不能排除组重叠、预处理泄漏或测试集被反复用于选择。

## A11-02

测试样本的组为 \(\{A,B,C,D\}\)。训练中仍有 A 的第 2、3 个样本、B 的第 5 个样本、C 的第 7、8 个样本和 D 的第 10 个样本，因此训练组同样为 \(\{A,B,C,D\}\)，交集非空，存在泄漏。

以组为单位可取 train=\(\{A,B,C\}\) 的全部样本、test=\(\{D\}\) 的全部样本，即测试样本为第 9、10 个。若需要验证集，应再从 A/B/C 中整组划出，不能拆帧。

## A11-03

令 \(r=Xw+b\mathbf1-y\)。有

\[
\mathrm dL
=\frac2M r^\mathsf T(X\,\mathrm dw+\mathbf1\,\mathrm db).
\]

所以

\[
\nabla_wL=\frac2M X^\mathsf Tr,
\qquad
\frac{\partial L}{\partial b}
=\frac2M\mathbf1^\mathsf Tr.
\]

若损失前系数为 \(1/(2M)\)，两个梯度都减少一半，成为 \(X^\mathsf Tr/M\) 和 \(\mathbf1^\mathsf Tr/M\)。

## A11-04

对 \(X\in\mathbb R^{M\times d}\)、\(W\in\mathbb R^{d\times q}\)、\(b,v\in\mathbb R^q\)、\(\widehat y,y\in\mathbb R^M\)，

\[
\delta_y=\frac2M(\widehat y-y)\in\mathbb R^M,
\]

\[
\delta_Z=(\delta_yv^\mathsf T)\odot(1-H\odot H)
\in\mathbb R^{M\times q},
\]

\[
\nabla_WL=X^\mathsf T\delta_Z\in\mathbb R^{d\times q},
\quad
\nabla_bL=\delta_Z^\mathsf T\mathbf1\in\mathbb R^q,
\]

\[
\nabla_vL=H^\mathsf T\delta_y\in\mathbb R^q,
\quad
\frac{\partial L}{\partial c}
=\mathbf1^\mathsf T\delta_y\in\mathbb R.
\]

## A11-05

严格收敛条件为 \(0<\eta<2/10=0.2\)。

- \(\eta=0.05\)：特征值 \(0.95,0.8,0.5\)，谱半径 \(0.95\)，收敛。
- \(\eta=0.19\)：特征值 \(0.81,0.24,-0.9\)，谱半径 \(0.9\)，收敛。
- \(\eta=0.2\)：出现 \(1-0.2\times10=-1\)，谱半径为 1，不严格收敛。
- \(\eta=0.25\)：出现 \(-1.5\)，发散。

## A11-06

中心差分的截断误差通常为 \(O(h^2)\)，但 \(h\) 太小时两次接近函数值相减会放大舍入误差。可扫描 \(h=10^{-3},10^{-4},10^{-5},10^{-6}\)，观察误差先降后升的稳定区。采用

\[
\frac{|g-g^{\mathrm{FD}}|}
{\max(1,|g|,|g^{\mathrm{FD}}|)}
\]

可避免两个梯度都接近零时分母失稳。

## A11-07

全数据标准化把验证/测试特征分布写入训练变换；每轮查看测试误差并选择最低轮次把测试集变成验证集；再次报告同一测试误差具有选择偏差。

正确流程是：先按组冻结 train/validation/test；只用训练集拟合标准化；用 train 更新参数，用 validation 选超参数和早停；恢复最优验证参数后只评价一次 test。若 test 结果触发修改，需要新的未触碰最终测试集。

## A11-08

总平方误差为

\[
1+1+8\times0.25=4.
\]

逐元素 MSE 为 \(4/10=0.4\)。结构 A 的内部 MSE 为 \(1\)，结构 B 为 \(0.25\)，逐结构等权 MSE 为

\[
\frac{1+0.25}{2}=0.625.
\]

前者让边数多的结构权重更大，后者让结构等权。二者都可使用，但必须匹配任务口径并明确报告。

## A11-09

忽略公共斜率误差，并使用题面给出的两项不相关条件，已见组误差包括组偏置估计均方和观测噪声：

\[
\mathbb E[e_{\mathrm{seen}}^2]
=\tau_g^2+\sigma_\varepsilon^2
=0.5+1=1.5.
\]

新组只能用总体组均值时，

\[
\mathbb E[e_{\mathrm{new}}^2]
=\sigma_b^2+\sigma_\varepsilon^2
=4+1=5.
\]

逐帧划分在该模型和不相关条件下低估 \(5-1.5=3.5\)。若 \(\delta_g\) 与测试噪声相关，已见组公式增加 \(-2\operatorname{Cov}(\delta_g,\varepsilon)\)；若新组 \(b_g\) 与测试噪声相关，新组公式增加 \(2\operatorname{Cov}(b_g,\varepsilon)\)。这些项可能改变差值甚至符号，因此结果不是任意数据集的通用差值。

## A11-10

合成回归只验证已知生成式上的梯度、划分和优化性质，不提供正式材料、DFT 标签或 DeepH 软件兼容性的证据。M7 完成且 M7-I 对 M3—M7 的全量独立总审计通过后，应当暂停并由用户冻结 M8 的资源、后端、软件对象、材料和预算方案；M8 冻结后，在 M9 开始 DeepH 安装、正式数据下载、正式标签生成或复现实验前，还须再次取得明确执行授权。
