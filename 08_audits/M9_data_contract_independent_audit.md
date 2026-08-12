# M9-04 官方 graphene 数据契约独立审计

## 审计结论

审计结论为 `BLOCKED`。稳定阻塞项 `M9-DATA-B01` 经独立复核成立；`BLOCKING=1`，`NON_BLOCKING=0`，未发现新的实施记录缺陷。当前冻结数据足以进入 DeepH-pack v0.2.2 的 `npz` Hamiltonian 监督训练数据加载路径，但不足以满足 D-013 已冻结、M9 工作包不得缩减的非正交矩阵与物理验收。M9-05 不允许启动。

关键缺口不是训练标签缺失，而是 450 个结构全部声明 `isorthogonal=false`，发布包却没有任何 overlap 矩阵。缺少同一 OpenMX basis 下的 overlap 时，无法合法构造 \(H(\mathbf{k})c=E\,S(\mathbf{k})c\)，也无法执行 overlap 的 Hermiticity、正定性与条件数、广义本征残差、H/S 成对对称性及基于同一 H/S 合同的能带比较。单位矩阵或从 Hamiltonian 推测 overlap 均会改变冻结问题，不能作为替代。

## 审计边界与方法

本次审计对被审文件和 WSL 运行时对象只读。唯一新增项目文件为本报告。结论不采信主 agent 的摘要值，而是分别从 Zenodo API、本地 ZIP、解压文件、全部 NPZ 数组、固定提交源码、预算状态和项目记录重新取得证据。

被审主要对象为：

- [`data_manifest.json`](../06_reproduction/manifests/data_manifest.json)；
- [`M9_data_contract_report.md`](../06_reproduction/reports/M9_data_contract_report.md)；
- [`M9_stageF_work_package.md`](M9_stageF_work_package.md)；
- [`master_execution_plan.md`](../00_scope/master_execution_plan.md)；
- [`progress_tracker.md`](progress_tracker.md)；
- [`decisions.md`](../decisions.md)；
- WSL ZIP `/home/evan-williams/deeph-m9/data/raw/graphene_dataset.zip`、解压根 `/home/evan-williams/deeph-m9/data/graphene/processed` 及运行时清单；
- DeepH-pack `v0.2.2` 固定提交 `66703c532a6f633f4bbc8f94f75c8698a7f89859`。

## 官方发布对象、ZIP 与解压清单

2026-08-12（Asia/Shanghai）直接读取 Zenodo record 6555484 API。`graphene_dataset.zip` 的内容 URL 为 `https://zenodo.org/api/records/6555484/files/graphene_dataset.zip/content`，登记字节为 `1833785660`，登记校验为 `md5:348c21faacdc62433dd8f01994824916`。Zenodo 该记录未发布 SHA-256；SHA-256 是对本地对象独立计算所得，不能表述为发布方登记值。

本地对象独立结果如下：

- 字节：`1833785660`；
- MD5：`348c21faacdc62433dd8f01994824916`；
- SHA-256：`f48aee772578510b2acba77665b1adba7ee71e977c48aa7e269f9ab3b98a2ac9`；
- `unzip -t`：退出码 0，4050 个成员全部通过 CRC；
- 成员构成：450 个目录、3600 个文件，压缩成员字节合计 `1833072838`，解压字节合计 `2360825225`；
- 安全成员检查：绝对路径或盘符 0、父目录分量 0、反斜杠路径 0、控制字符 0、规范化重复路径 0、加密成员 0、符号链接 0、特殊文件 0；
- 解压对应检查：3600/3600 个文件均存在，逐文件大小与 ZIP 条目一致，逐文件 CRC 一致，未出现额外或遗漏文件；
- 运行时逐文件 SHA-256 清单：3600/3600 条重新计算一致，总字节 `2360825225`，无未登记或失效路径。

运行时清单的实测 SHA-256 与项目摘要一致：`graphene_archive_inspection.json` 为 `67befebd7b0054c78e7de3be25b963caf9efb4b64a9ec9ddf5ac41ca88006bf9`，`graphene_extraction.json` 为 `4210de860b48ef175a73f80e5243c9cf7d4e28e3d78659dba30b402e335f8989`，`graphene_inventory.json` 为 `048e376ffdf52b3c3a5aba53904a00bda7f55280ed3afd8de55e8515d8247800`，`graphene_data_contract.json` 为 `a23e84db1ac3b3d496b73d3103d307619daac32c80c8c87be35a684ca12b31b0`。被保留的失败部分文件字节 `1426243584`、SHA-256 `841543968db331475b2117cd58b20884f1a792dc291480725b45aff4c0266d89`，块清单 SHA-256 `4ce3ba2ee9aa90abd8609a3b08f7000e8db41536d150819b62ac64397179152c`，也均与项目摘要相符。

## 450 个结构的数据合同

独立扫描确认结构 ID 严格等于 `500..4990`、步长 10。450/450 个目录都只含 `element.dat`、`site_positions.dat`、`orbital_types.dat`、`lat.dat`、`rlat.dat`、`info.json`、`rc.npz` 和 `rh.npz` 八个文件，解压根没有额外文件。

450 个 `info.json` 的键集合均严格等于 `fermi_level,isorthogonal,isspinful,norbits,nsites`，字段分布为：

- `nsites=72`：450/450；
- `norbits=936`：450/450；
- `isorthogonal=false`：450/450；
- `isspinful=false`：450/450。

对全部 450 对 `rc.npz`/`rh.npz` 而非抽样执行了全量数组扫描。每个文件均含 2880 个键，450/450 个结构的 `rc` 与 `rh` 键集合完全一致；1,296,000 个键全部可解析为五整数 `[R1,R2,R3,i,j]`，原子下标落在 `1..72`。1,296,000 个 `rc` 数组全部为 `3×3 float64` 且有限；1,296,000 个 `rh` 数组全部为 `13×13 float64` 且有限。由此确认主报告对结构数、info 字段、键数、shape、dtype 与有限性的摘要准确。

## overlap、`rs.npz`、k 点与能带对象

冻结数据目录的全部 NPZ 文件恰为 450 个 `rc.npz` 和 450 个 `rh.npz`。数据目录及 ZIP 中没有 overlap、`rs.npz`、`s.npz`、参考 k 点、参考能带、DOS 或参考本征值文件。

扩大到 M9 运行时的 `data`、`runs`、`logs`、`manifests` 与固定软件源码范围后，仍没有可用于冻结 graphene 数据的 overlap 或参考物理结果。源码树存在 `deeph/inference/band_config.json`，其中含通用 `k_data` 配置；它是 DeepH-pack 自带的版本控制模板，不与这 450 个结构、同 basis overlap 或参考本征值建立 provenance，因而不是冻结数据的参考 k 点或能带对象，不能关闭数据合同缺口。项目工作区中名称含 band/eigen 的教材与合成练习同样不属于 M9 正式数据对象。

## DeepH-pack v0.2.2 的真实接口合同

固定源码仓库 HEAD 为 `66703c532a6f633f4bbc8f94f75c8698a7f89859`，精确 tag 为 `v0.2.2`，工作树无修改。源码与 README 的相互印证结果如下：

- `README.md:327-341` 把 Zenodo 文件明确称为可直接训练的 processed graphene dataset，并要求 `raw_dir` 指向解压数据；`deeph/graph.py:699-713` 的 `interface=npz` 路径实际读取 `rh.npz` 与 `rc.npz`。因此，现有八文件集合确实足以进入普通 Hamiltonian 监督训练数据加载路径。
- `README.md:157-176` 明确区分构造数据集的 DFT 软件和用于大体系 overlap 的 modified overlap-only OpenMX；OpenMX 路线指定 3.9。
- `README.md:254-272` 明确要求推理前计算 overlap，且 overlap 必须使用与数据集相同的 basis set 和 DFT software；`README.md:340-342` 对该 Zenodo 数据进一步明确要求使用 OpenMX overlap。
- `deeph/scripts/inference.py:78-100` 的 OpenMX 推理步骤要求 overlap 输出并生成 `overlaps.h5`；`deeph/inference/dense_calc.jl:100-194` 读取 `hamiltonians_pred.h5` 与 `overlaps.h5`，构造 `H_R/S_R` 和 `H_k/S_k`，随后调用广义 Hermitian eigensolver。缺失个别 overlap key 时源码虽以零块填充，但整体仍要求合法的 `overlaps.h5`，零块语义不能推导或替代真实非正交 overlap。

因此，主报告关于“训练数据结构可用、冻结的完整物理验收不可用”的区分与源码相符。现有证据不支持把训练成功外推为非正交物理闭环完成。

## 项目记录、哈希、预算与授权边界

[`data_manifest.json`](../06_reproduction/manifests/data_manifest.json) 可解析为 JSON。其三个实施脚本 SHA-256 均与现文件一致：`m9_range_download.py` 为 `6697be45763e4a2b0c4230810a8e4cdcac77681c1e7c28799cbacfa415231db0`，`m9_dataset_archive.py` 为 `2c4a80e54d6ec9c155f6967fa1a5f44e59f0a4f1addd5c7ce562ebca6c5ea060`，`m9_data_contract.py` 为 `253bd3daeefa69dc204263074578c3659d52e26bff111afac67c2ce54ab860f4`。项目摘要、报告、主计划、进度跟踪和 D-016 对 `BLOCKED`、未训练、未冻结容差、未安装 OpenMX 和未生成 DFT 标签的陈述互相一致。

预算状态独立只读复算时，兼容性、训练、物理验证 GPU 秒分别为 `54.848205606`、`0`、`0`；合计表观字节 `29687405984`，合计分配字节 `29987586048`，VHDX 相对基线增长 `24326963200`，项目侧白名单表观字节 `333404`，无预算违规。该值是审计时点快照，会随时间和后续合法记录增加；[`data_manifest.json`](../06_reproduction/manifests/data_manifest.json) 中较早的 `generated_utc=2026-08-11T16:58:20.7560617Z` 快照与其生成时点相容，不构成漂移错误。

WSL 的 `runs` 目录无文件；预算训练与物理桶均为 0；运行时没有检查点、预测 Hamiltonian、`overlaps.h5` 或 `openmx.Band`。`which openmx` 无结果，Debian package database 也没有 `openmx` 包。由此支持“训练/试推理未启动、OpenMX 未安装”的当前陈述。未发现凭据落盘证据。

D-013 明确规定正式归档缺少 overlap 或物理验收对象时判定数据契约失败并暂停；D-014 又明确禁止安装 OpenMX/其他 DFT、生成正式 DFT 标签和静默改变路线。M9 工作包 M9-04 规定关键对象缺失即暂停，统一停止规则也列出“数据契约不能支持冻结验收对象”和“需要安装 OpenMX/其他 DFT”。因此，D-014 对一般 M9 复现实验的授权不能解释为 overlap-only OpenMX 的隐含授权。

## 稳定问题与最小关闭条件

### `M9-DATA-B01`：非正交数据缺少同 basis overlap

- 级别：`BLOCKING`。
- 状态：`OPEN`，独立复核确认。
- 影响：M9-04 不能通过；M9-05 不得启动；M9-06 的 overlap、广义本征、H/S 对称性和物理比较没有合法输入。
- 不是关闭条件的做法：使用单位 overlap、从 H 或 `rc` 推断 overlap、把源码 `band_config.json` 当作参考数据、先训练再决定验收、安装相邻 DFT/DeepH 版本、降低数值或物理验收强度。

在不修改 D-013 验收强度的前提下，最小关闭条件为：

1. 用户明确选择并授权 overlap 路线；不能沿用 D-014 的既有授权推定。
2. 若采用 overlap-only OpenMX，先冻结 OpenMX 3.9 原始对象、overlap-only 修改对象的精确版本或提交、下载 URL 与哈希，冻结 PAO/VPS 文件及哈希、basis 字符串、450 个结构到输入的确定映射、无 SCF 命令、输出 schema，以及新增墙钟/CPU/GPU/存储预算。上述工作包先经独立审计通过，才可安装或计算。
3. 若采用预计算 overlap，必须提供可信发布 URL、字节、SHA-256、生成软件与 basis provenance、450 个结构的一一映射及 H/S 键空间绑定；导入前同样独立审计。
4. 取得 overlap 后，重新生成不可变清单，证明每个适用结构的 overlap 与 H 使用同一原子、轨道、basis、单位、周期键和相位合同；完成 Hermiticity、适用正定性、条件数与失败样例预检。
5. 在任何 M9-05 训练、试推理或模型输出之前，登记参考 k 路径、由真值 H/S 构造参考谱的规则及全部机读容差，再由本审计员定点复核 `M9-DATA-B01` 为 `CLOSED`。

若用户决定正式降低 M9 为仅训练合同复现，则必须新增决策显式取代 D-013 的矩阵与物理验收；这属于改变成功定义，不是以现有数据满足 `M9-DATA-B01`。若维持现有禁令，则 M9 保持已证实阻塞，不能标记完成。

## 当前需要的用户路线决策

推荐选择“受限 overlap-only OpenMX 路线”：只为冻结的 450 个 graphene 结构、同一 OpenMX basis 计算 overlap，不生成 Hamiltonian 标签；同时冻结上述软件、PAO/VPS、basis、结构映射和新增预算，并在安装前进行独立工作包审计。该选择仍属于安装受禁 DFT 对象和扩大 D-014 边界，必须由用户明确授权。

用户也可选择：提供具有完整 provenance 的预计算 overlap；明确降低 M9 为训练合同复现；或维持禁令并停止阶段 F。当前证据不能由审计 agent 代替用户在这些路线之间作决定。

## 门控判定

- `M9-04`：`BLOCKED`。
- `M9-DATA-B01`：`OPEN`。
- `BLOCKING=1`。
- `NON_BLOCKING=0`。
- 是否允许 M9-05：否。
- 下一动作：等待用户路线决策；若选择补齐 overlap，先冻结新增对象、预算与授权并完成独立工作包审计，不得直接安装或计算。

## 报告自身验证约定

本报告最终内容固定后执行 UTF-8 非 CR/LF/TAB 控制字符扫描、活动本地 Markdown 链接存在性检查，以及 Pandoc 3.6.4 使用 `markdown+tex_math_single_backslash`、`--fail-if-warnings` 和 HTML5 MathML 的严格转换；输出必须实际含 MathML 节点。最后计算本报告 SHA-256。为避免自引用改变文件内容，最终计数和 SHA-256 不嵌入正文，由交付消息给出。
