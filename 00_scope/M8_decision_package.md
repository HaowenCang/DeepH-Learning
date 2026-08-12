# M8 实践方案集中决策包（已冻结）

## 1. 状态与授权边界

- 提交日期：2026-08-11
- 当前状态：`FROZEN/COMPLETED`
- 前置门控：M7-I 定点复核 `PASS`，`BLOCKING=0`、`NON_BLOCKING=0`、新增及剩余问题 0；报告 SHA-256 为 `215C6A4BCB3A054871CBEF55BDEB888B4EA8354994528263510A5A876AEACD7C`。
- 冻结记录：用户于 2026-08-11 明确采用推荐组合 R1 + S1 + D1 + B2；首个材料为 graphene；首轮排除磁性、SOC、杂化泛函、响应性质和跨材料迁移。正式记录见 `decisions.md` 的 D-013。
- 环境补充：WSL 2 发行版及 Linux 虚拟磁盘固定于 `E:\Laptop\WSL`，Linux 用户固定为 `evan-williams`。认证口令不进入本项目或任何复现产物。
- M8 冻结本身不授权 M9。用户随后已通过 D-014 单独授权配置现有 WSL、安装冻结的 DeepH/依赖、下载官方 graphene 数据并执行复现实验；OpenMX/其他 DFT 安装、标签生成、静默换路线和自动重启仍不在授权范围。M9-02 还必须等待 M9-01 独立工作包审计问题清零。

## 2. 证据快照

### 2.1 本机资源

| 项目 | 已核对值 | 对实践路线的含义 |
|---|---|---|
| 操作系统 | Windows 11 Pro for Workstations Insider Preview，64 位，版本 10.0.26220 | 原项目以 Linux 命令和旧版科学计算栈为主，不推荐直接使用 Windows 原生环境 |
| CPU | Intel Core i9-13900HX，32 个逻辑处理器 | 足以承担预处理、数据加载和小规模稀疏后处理 |
| 内存 | 31.73 GiB | 适合首个单元素小体系；不宜预先承诺大超胞或多模型并行 |
| GPU | NVIDIA GeForce RTX 4080 Laptop GPU，12,282 MiB，计算能力 8.9 | 可执行单卡训练，但批量大小必须通过显存实测冻结 |
| 驱动 | 610.88；`nvidia-smi` 报告 CUDA 13.3 | 只说明宿主驱动状态，不证明旧版 PyTorch/CUDA 用户态组合已经兼容 |
| 存储余量 | C: 32.0 GiB；D: 91.9 GiB；E: 369.4 GiB | 工作数据和 Linux 虚拟磁盘应放在 E 盘；C 盘不足以承担默认 WSL 数据增长 |
| Linux 环境 | 当前未发现已初始化的 WSL 发行版 | M9 获授权后才可安装和验证 |

Microsoft 官方说明 Windows 11 可通过 WSL 2 运行 Linux 工具链，并允许指定发行版；NVIDIA 官方说明 WSL 2 复用 Windows 宿主驱动，不应在 WSL 内另装 Linux 显卡驱动。[Microsoft WSL 安装说明](https://learn.microsoft.com/en-us/windows/wsl/install) [NVIDIA CUDA on WSL 指南](https://docs.nvidia.com/cuda/archive/13.0.2/wsl-user-guide/index.html)

### 2.2 软件与数据对象

[DeepH-pack 官方仓库](https://github.com/mzjb/DeepH-pack)将自身定义为 DeepH 的官方实现，支持 OpenMX、SIESTA、ABACUS 和 FHI-aims 数据。其公开依赖仍是 Python 3.9、PyTorch 1.9.1、PyTorch Geometric 1.7.2、e3nn 0.3.5；需要稀疏能带后处理时还涉及 Julia 1.6.6。当前发布页的最新标签为 [`v0.2.2`](https://github.com/mzjb/DeepH-pack/releases/tag/v0.2.2)，对应提交 `66703c532a6f633f4bbc8f94f75c8698a7f89859`。本次只读取了公开元数据，没有克隆或安装仓库。

官方仓库提供 graphene、MoS2、twisted bilayer graphene 和 twisted bilayer bismuthene 的处理后数据入口，并说明 graphene、TBG、TBB 各使用一个 MPNN，MoS2 使用四个 MPNN。公开数据记录 `10.5281/zenodo.6555484` 的元数据显示：graphene 压缩包为 1,833,785,660 字节，约 1.708 GiB，登记 MD5 为 `348c21faacdc62433dd8f01994824916`；MoS2、TBG、TBB 分别约 3.544、2.048、16.756 GiB。[官方数据记录](https://zenodo.org/records/6555484)

DeepH-pack 明确说明上述处理后数据由 OpenMX 产生，并要求推理阶段使用与训练数据相同的 DFT 软件和基组生成 overlap。它明确要求 OpenMX 3.9；虽然 OpenMX 官方已在 2026 年发布 4.0，3.9 仍可从 GPLv3 下载页获得，不能把 4.0 视为无验证的等价替代。[OpenMX 官方下载页](https://openmx-square.org/download.html) [DeepH-pack 推理说明](https://deeph-pack.readthedocs.io/en/stable/keyword/inference.html)

SIESTA 当前稳定版是 5.4.2，采用 GPL-3.0-only；DeepH-pack 要求 SIESTA 不低于 4.1.5。它是可行的后续替代后端，但不能直接复用 OpenMX 数据的 basis/overlap 契约。[SIESTA 官方获取说明](https://siesta-project.org/siesta/CodeAccess/)

DeepH-pack 官方仓库仍警告 ABACUS 接口存在 overlap 稀疏模式问题，可能导致预测错误。因此 ABACUS 不适合作为首个闭环的推荐后端。独立 DeepH-E3 仓库也明确建议新用户优先使用 DeepH-pack；其软件和数据应保留为完成普通 DeepH 基线后的等变扩展对象，而不是首个安装对象。[DeepH-E3 官方仓库](https://github.com/Xiaoxun-Gong/DeepH-E3)

## 3. 候选方案与推荐

### 3.1 计算环境

| 方案 | 内容 | 优点 | 主要风险 | 结论 |
|---|---|---|---|---|
| R1 | 本机 WSL 2，Ubuntu 22.04 LTS，Linux 虚拟磁盘置于 E 盘，单张 RTX 4080 Laptop GPU | 使用现有硬件；接近官方 Linux 工作流；可记录完整环境 | 旧版 PyTorch/PyG 与当前 GPU/驱动需先做兼容性烟雾测试 | **推荐** |
| R2 | 远程 Linux/CUDA 工作站或集群 | 环境和显存可更稳定，可扩展多次训练 | 当前没有账号、配额、GPU 型号或调度信息 | 有现成资源时可替代 R1 |
| R3 | Windows 原生 Python | 无需 WSL | 官方脚本、Julia、编译链和旧版 PyG 兼容风险最高 | 不推荐 |

推荐冻结 R1，但把“CUDA 张量运算、PyG 扩展导入、e3nn 前向/反向、DeepH-pack CLI 启动”设为 M9 的前置兼容性门控。该门控失败时应停止，不得自行切换到主分支、新框架或其他 DFT 后端。

### 3.2 DeepH 软件对象与依赖

| 方案 | 软件对象 | 取舍 | 结论 |
|---|---|---|---|
| S1 | DeepH-pack `v0.2.2`，提交 `66703c532a6f633f4bbc8f94f75c8698a7f89859` | 有明确发布标签，且是官方推荐入口；依赖较旧，需要隔离环境 | **推荐** |
| S2 | DeepH-pack `main`，审计时远程 HEAD 为 `141faaaba1d5e17248283ef939bcd2ead2d8e677` | 可能含发布后修复，但对象会漂移，较难对应论文基线 | 仅作后续兼容性对照 |
| S3 | DeepH-E3，审计时远程 HEAD 为 `036bf95b996052ef778c5c38e3c54c2ac0e2b591` | 直接面向 E(3) 等变与 SOC，但首轮复杂度和数据体量更高 | M9 基线后再议 |

推荐环境主版本为 Python 3.9、PyTorch 1.9.1、PyG 1.7.2、e3nn 0.3.5、Julia 1.6.6，并在 M9 安装前先生成精确的直接依赖与传递依赖锁文件。拟用 CUDA 11.1 用户态运行时作为 PyTorch 1.9.1 的首个兼容候选；这只是待验证候选，不能由宿主 `nvidia-smi` 的 CUDA 13.3 字样推出其必然兼容。

### 3.3 数据、DFT 后端与首个材料体系

| 方案 | 数据与体系 | 优点 | 主要风险 | 结论 |
|---|---|---|---|---|
| D1 | 官方处理后 OpenMX graphene 数据；首轮不自行生成 DFT 标签 | 单元素、无磁、首轮不含 SOC、一个 MPNN、数据最小且官方配置直接支持 | 仍须核查压缩包内部清单、basis/overlap/划分和参考物理量是否足以完成全部验收 | **推荐** |
| D2 | 官方处理后 OpenMX MoS2 数据 | 多元素和轨道块更丰富 | 四个 MPNN，数据和诊断复杂度更高 | graphene 基线后候选 |
| D3 | 自行使用 OpenMX 3.9 生成 graphene 标签 | 能覆盖原始结构到标签全链 | 引入 DFT 收敛、赝势、PAO、k 网格和标签质量审计，已超出最小首轮闭环 | 后续扩展；需重新授权 |
| D4 | SIESTA 5.4.2 自生成数据 | 开源且当前维护 | 与官方 OpenMX 处理数据不共享 basis/overlap 契约，需要独立基准 | 后续替代后端 |
| D5 | ABACUS 或 TBG/TBB | 有官方示例或研究价值 | ABACUS 已知接口警告；扭转体系规模大 | 首轮拒绝 |

推荐冻结 D1。OpenMX 3.9 在 M8 中只冻结为该数据的 provenance、basis 和 overlap 软件身份；首轮 M9 不安装 OpenMX、不生成标签。若下载后发现官方包缺少完成预定矩阵、overlap 或能带验收所需对象，应把它判为“数据契约不满足”并暂停，由用户重新选择 D2、D3 或缩小可声称的复现范围，而不是静默补造数据。

### 3.4 物理范围和表示契约

推荐首轮冻结为：非磁、无 SOC、常规局域或半局域 DFT 来源、单材料内插，不处理杂化泛函、响应性质、跨材料迁移、磁性超结构或拓扑/SOC 结论。其目标是复现 DeepH 原始普通 MPNN 基线，而不是宣称完成 DeepH-E3 或 xDeepH。

单位采用 DeepH-pack 处理约定：长度 Å、能量 eV。轨道基组、轨道排序、相位、局部坐标、截断半径及 overlap 必须从官方 graphene 数据和固定版本配置中原样提取并形成机读清单；在实际归档内容被核查前，本包不猜测具体 PAO 字符串或轨道列表。推理所用 overlap 必须与 OpenMX 数据的 DFT 软件及基组一致。

### 3.5 预算、数据划分、随机种子和失败标准

提供三个预算候选：

| 预算 | 墙钟上限 | GPU 上限 | 工作存储上限 | 适用范围 |
|---|---:|---:|---:|---|
| B1 | 3 天 | 8 GPU 小时 | 60 GiB | 只保证环境、数据契约和最小训练烟雾测试，不保证完整基线 |
| B2 | 7 天 | 24 GPU 小时 | 100 GiB | 完成一个固定配置的 graphene 基线，并保留一次受控复跑或故障诊断余量；**推荐** |
| B3 | 14 天 | 72 GPU 小时 | 180 GiB | 允许多随机种子、有限超参数比较或第二材料预检 |

推荐 B2，并预登记：

- 数据划分优先使用 `v0.2.2` 官方 graphene 配置或数据内显式划分；若不存在，则按结构 ID 排序后使用固定、分组且不可泄漏的 80%/10%/10% 划分，并把所得 ID 清单和 SHA-256 冻结后才训练。
- 规范随机种子为 `20260811`；训练、NumPy、Python 和数据加载器分别显式设置。若算力有余，使用 `20260812` 做非门控的稳健性复跑，不以单次随机改善替换规范结果。
- 兼容性烟雾测试上限为 2 GPU 小时；规范训练和验证上限为 16 GPU 小时；复跑、物理重建及诊断预留 6 GPU 小时。任一上限到达即保存状态并停止，不自动扩大预算。
- 批量大小不在 M8 中臆定；M9 兼容门控从 1 开始，按显存测量提高，并将最终值、峰值显存和 OOM 失败样例写入运行清单。
- 正式通过必须同时满足：环境锁定；数据哈希与清单通过；划分无结构泄漏；训练、验证和测试对象分离；预测矩阵维度、键和 provenance 一致；Hermiticity、逆边、overlap 正定适用条件、实空间到 k 空间重建和广义本征残差通过；物理量与官方参考按预先登记的数值容差比较。
- 不能因训练 loss 下降而单独判定成功。出现 NaN/Inf、OOM、哈希不符、数据泄漏、basis/overlap 不一致、官方参考缺失或关键残差超限均判定为失败并暂停。
- 具体数值容差须在下载后、训练前根据官方配置和数据精度登记；不得在看到测试结果后放宽。

## 4. 推荐冻结组合

推荐一次性冻结以下组合：

1. 资源：R1，本机 WSL 2 + Ubuntu 22.04 LTS，发行版数据置于 E 盘，单卡 RTX 4080 Laptop GPU。
2. 软件：S1，DeepH-pack `v0.2.2` / `66703c532a6f633f4bbc8f94f75c8698a7f89859`，隔离的 Python 3.9 旧版依赖环境；DeepH-E3 不进入首轮。
3. 数据与 DFT：D1，官方处理后 OpenMX graphene 数据；OpenMX 3.9 仅作为来源和 overlap 契约身份，首轮不安装 DFT 软件、不生成标签。
4. 材料：graphene，单材料、非磁、无 SOC。
5. 预算：B2，7 天、24 GPU 小时、100 GiB；规范种子 `20260811`。
6. 高级物理：首轮排除磁性、SOC、杂化泛函、响应性质和跨材料迁移。

该组合最小化首轮的材料、轨道和模型数量，同时保留矩阵级、对称性和物理重建验收。它只能支持“固定官方处理数据上的 DeepH-pack 普通基线复现”；不能外推为“已复现原始 DFT 标签生成”“已验证 OpenMX 4.0/SIESTA/ABACUS 接口”或“已完成 E(3)/SOC 模型”。原始 DeepH 方法的局域非正交基和 Hamiltonian 学习边界见[原始论文](https://www.nature.com/articles/s43588-022-00265-6)，E(3) 等变扩展的额外范围见[DeepH-E3 论文](https://www.nature.com/articles/s41467-023-38468-8)。

## 5. 用户冻结模板

本节保留冻结时使用的确认模板，作为决策来源证据：

> 冻结 M8 推荐组合 R1 + S1 + D1 + B2；首个材料为 graphene；首轮排除磁性、SOC、杂化泛函、响应性质和跨材料迁移。

也可逐项替换，例如：

> 资源改为 R2；软件仍为 S1；数据改为 D3；预算改为 B3；其余按推荐。

用户已按上述模板冻结 M8，最终选择已写入 D-013；其后又以 D-014 完成独立的 M9 执行授权。D-014 不授权 OpenMX/其他 DFT 安装或标签生成，也不允许越过 M9-01 独立审计门控。
