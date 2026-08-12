# 阶段 D 合成周期图与普通 MPNN 自动验收

## 1. 范围与文件

本目录实现 M6 工作包冻结的 T-D01—T-D10。输入仅包括确定性合成晶胞、合成坐标、合成结构组、合成轨道表和合成监督目标；实现不安装或调用 DeepH，不下载正式训练数据，不生成 DFT 标签，也不选择材料体系、DFT/数据后端或实践软件版本。

- `staged_models.py`：周期有向多重图、规范边身份、普通 NumPy MPNN、解析及故障反向传播、统一边输出 schema、完整 concat/padded 批、聚合策略和输入验证原语；
- `run_experiments.py`：两组冻结配置、T-D01—T-D10、正例断言、故障注入、确定性 JSON 与非规范计时模式；
- `test_staged_models.py`：双配置、字节确定性、边身份、病态晶胞边界、schema 版本、mask/padding/cache 失败矩阵和 M8 授权边界；
- `requirements.txt`：精确固定的 Python 用户态依赖。

## 2. 固定环境与复现命令

已验证环境为 Python 3.12.13、NumPy 2.3.5 和 SciPy 1.18.0。缺失依赖时，按用户授权使用同一用户态解释器安装：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -c "import sys; assert sys.version_info[:3] == (3, 12, 13)"
& $py -m pip install --requirement .\05_code_exercises\stageD_synthetic_mpnn\requirements.txt
& $py -c "import numpy, scipy; assert numpy.__version__ == '2.3.5'; assert scipy.__version__ == '1.18.0'"
& $py -m pip check
```

本次实现未安装新增依赖；现有固定运行时已满足 `requirements.txt`。以后若确需新增 Python 用户态依赖，应当使用精确 `==` 版本，并记录实际安装命令、版本断言和 `pip check` 结果。

## 3. 冻结配置、测试与 CLI

配置 A/B 的网络规模和预算沿用 M6 工作包。首轮独立审计登记 B02 后，修复版把第 11 章生成式、噪声尺度与绝对阈值共同冻结为一个新验收对象；阈值固定为 \(2\times10^{-2}\)，随后通过改正特征构造使结果达到阈值，未按输出结果放宽阈值：

| 配置 | seed | 层数 | 隐藏宽度 | 边宽度 | 输出宽度 | 结构组 | 每组帧数 | 步数 | 学习率 | 测试 MSE 上限 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 20260806 | 2 | 3 | 2 | 4 | 12 | 6 | 500 | 0.08 | \(2\times10^{-2}\) |
| B | 20260817 | 3 | 4 | 3 | 4 | 15 | 5 | 700 | 0.06 | \(2\times10^{-2}\) |

T-D03 使用

\[
x_{g,t}=[u_g,\tau_t]^\mathsf T+\xi_{g,t},\qquad
y_{g,t}=1.5u_g-0.7\tau_t+b_g+\varepsilon_{g,t},
\]

其中 `xi_std=0.005`、`bias_std=0.03`、`epsilon_std=0.002`。层数、隐藏宽度、边宽度和输出宽度真实参与冻结消息传递特征提取器，`Wo/bo` 按固定学习率与步数训练。输出保存三个集合的组 ID、组数/样本数、交集、训练—验证轨迹、冻结模型 MSE/MAE，以及带组哑变量的逐帧泄漏表观误差。该阈值只验收这一合成族，不能外推到正式标签。

在项目根目录执行：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m unittest discover -s .\05_code_exercises\stageD_synthetic_mpnn -p 'test_*.py' -v
& $py .\05_code_exercises\stageD_synthetic_mpnn\run_experiments.py --format json --config A --seed 20260806
& $py .\05_code_exercises\stageD_synthetic_mpnn\run_experiments.py --format json --config B --seed 20260817
```

三条命令均应以退出码 0 结束。CLI 拒绝配置与 seed 不一致的组合。规范 JSON 使用排序键、紧凑分隔符和 `allow_nan=False`；墙钟时间不进入规范输出，因此同一配置重复运行必须字节完全一致。

## 4. T-D01—T-D10 证据映射

| ID | 成功证据 | 强制失败证据 |
|---|---|---|
| T-D01 | train/validation/test 的结构组两两不相交 | 逐帧随机划分使三个交集均非空 |
| T-D02 | 132/300 个参数中心差分最大相对误差不超过 \(10^{-5}\)，padding 梯度严格为零 | 实际执行漏 `1/S`、receiver scatter 改 sender、错误 tanh 导数、padding 梯度泄漏和输出符号翻转五种错误反传，逐项给出检测量 |
| T-D03 | 冻结组生成式、MPNN 规模与预算下训练损失下降，独立组测试 MSE 低于 \(2\times10^{-2}\) 且低于零预测基线的四分之一，同时报告 MSE/MAE、组 ID、计数、交集和轨迹 | 目标加 1 后 MSE 约为 1；逐帧带组身份模型显示较低表观误差，不能替代新组评价 |
| T-D04 | 非对称图经节点置换和独立边行倒序后，预测、完整键、edge ID、mask、块形状和实际轨道身份统一映射，残差不超过 \(10^{-12}\) | 端点未重标、预测行错位或 mask 行错位分别被拒绝 |
| T-D05 | 公共及逐原子整数代表变换经完整 \(K_q\) 字典、排序和双射配对，位移/距离残差不超过 \(10^{-12}\) | 错误固定 shift、按原子对折叠和按原行号读取倒序输出均产生失败证据 |
| T-D06 | 解析镜像界与外扩一层暴力枚举得到相同边键 | 固定小镜像盒漏边，最小镜像丢失多重边 |
| T-D07 | 不同镜像边及非零自镜像边全部保留，零位移自环排除 | 仅按原子对去重会减少边数 |
| T-D08 | 一至三层同步传播的受影响节点集合与有向前驱距离一致 | 原地异步更新在一层内越过三条边 |
| T-D09 | `stageD-edge-output-v1` 与 `stageD-batch-v1` 覆盖预测、完整边键、轨道 provenance、特征、几何、逐图计数和单位；NaN padding 在读取前切除，并实际经过前向、归一化和 masked loss；sum/mean 空入边为零且 mean 返回 `has_incoming=false`，max 拒绝空集 | 36 个变异覆盖 src/dst、shift、edge ID、边级数组增删行、几何/特征行滚动、prediction 宽度、cell/cutoff、规范 fractional、完整张量 rank、块/轨道行、mask 类型/形状/位置、负 graph ID、计数、padding、跨图边、版本和 cache |
| T-D10 | 16 个失败实际拒绝非有限坐标、奇异或阈值病态晶胞、非法 cutoff、越界端点、重复记录、分组污染、空结构 ID、float32 核心 schema 和不一致枚举元数据；\(A_-\) 被接受 | 任一非法输入静默穿透即使总测试失败 |

规范边身份的 JSON 字节为 UTF-8 紧凑数组
`[edge_version, structure_id, receiver, sender, n1, n2, n3]`，随后计算 SHA-256。边身份包含完整有向端点和整数镜像，不允许按距离或原子对折叠。

`stageD-edge-output-v1` 把 prediction、完整边键、edge ID、block shape、连续 component mask、局部轨道下标、实际合成轨道 ID、unit 和源 graph schema 绑定在同一行对象中；行序可以改变，但完整键必须与原图形成双射，所有边级数组的第一维必须严格等于边数。`stageD-batch-v1` 的 concat 形式携带逐图 cell/cutoff、node/edge count、非负 graph ID 和全局端点，padded 形式携带逐图 cell/cutoff、左连续 node/edge mask、局部端点与完整张量。validator 从 fractional、端点、shift 和 cell 重算 displacement，再重算 distance；边特征契约固定为 `distance-displacement-prefix-zero-pad-v1`，因此特征行也能从同一完整键重建。padding 特征可含 NaN，因为前向函数先按 count/mask 切片；若把 padding 行激活，验证器会在读取前拒绝。

## 5. 复杂度与非规范计时

T-D09 报告节点数 \(N\)、边数 \(E\)、层数 \(L\)、隐藏宽度 \(d\) 和候选镜像数。实现中的缓存激活估计为

\[
B_{\mathrm{act}}=8L(3Nd+2Ed)\ \text{bytes},
\]

它只按明确列出的 float64 数组计数，不包含参数、输出、Python 对象、解释器或进程常驻内存。配置 A 的该估计为 2304 bytes，配置 B 为 4608 bytes。

如需测量当前机器上的实现时间，执行：

```powershell
& $py .\05_code_exercises\stageD_synthetic_mpnn\run_experiments.py --format json --config A --seed 20260806 --benchmark
& $py .\05_code_exercises\stageD_synthetic_mpnn\run_experiments.py --format json --config B --seed 20260817 --benchmark
```

2026-08-04 的一次本机快照中，配置 A 的单次构图/前向时间约为 0.01015 s/0.0000495 s，配置 B 约为 0.01081 s/0.0000860 s。该值只用于说明实现数量级，会随负载与硬件波动；`--benchmark` 输出因此是非规范 JSON，不参加字节确定性门控。

## 6. 失败语义与授权边界

退出码 0 只表示十项合成门控全部达到冻结阈值，并且所有预期失败实际执行且被捕获。以下任一情况均应导致非零退出或测试失败：正例超差、预期失败穿透、JSON 含 NaN/Infinity、周期边身份不唯一、轨道身份无法从端点表反解、padding 参与有效计算、跨图边、错误 schema 版本或病态输入被接受。

这些结果不构成 DeepH 精度、真实材料可迁移性或任何 DFT 后端正确性的证据。M8 前，材料体系、DFT/数据后端和 DeepH 软件对象继续保持 `UNRESOLVED_M8`；M8 冻结后，开始 M9 的安装、正式数据下载或复现实验前仍须取得明确执行授权。
