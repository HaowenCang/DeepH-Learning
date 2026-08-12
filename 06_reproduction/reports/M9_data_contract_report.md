# M9-04 官方 graphene 数据契约报告

## 结论

M9-04 在下载、压缩包完整性、安全解压和训练数据结构层面通过，但在阶段 F 的完整物理验收合同上失败，稳定阻塞项为 `M9-DATA-B01`。冻结的官方 graphene 发布包包含局部坐标旋转 `rc.npz` 和旋转后的 Hamiltonian 标签 `rh.npz`，不包含 overlap 矩阵；450 个结构的 `info.json` 又全部声明 `isorthogonal=false`。因此，现有对象足以建立普通 MPNN 的 Hamiltonian 监督训练，却不足以定义非正交广义本征问题、overlap 正定性与条件数、广义谱残差和能带比较。按照 D-013 与 M9 工作包的停止规则，M9-05 训练不得启动，M9-04 保持阻塞。2026-08-12 用户已通过 D-017 选择下文推荐的受限 overlap-only 路线；在新增工作包独立审计、实际 overlap 生成及 `M9-DATA-B01` 定点复核完成前，本报告的阻塞结论不变。

## 不可变下载与解压证据

- 发布对象：Zenodo `10.5281/zenodo.6555484` 的 `graphene_dataset.zip`。
- 登记与实测字节：`1833785660`。
- 发布与实测 MD5：`348c21faacdc62433dd8f01994824916`。
- 本地 SHA-256：`f48aee772578510b2acba77665b1adba7ee71e977c48aa7e269f9ab3b98a2ac9`。
- `unzip -t`：4050 个成员全部通过 CRC，退出码 0。
- 安全检查：绝对路径、父目录、重复规范路径、加密成员、链接和特殊文件均为 0。
- 解压对象：450 个结构目录、3600 个文件、`2360825225` 字节；逐文件清单位于 Linux 工作根，清单 SHA-256 为 `048e376ffdf52b3c3a5aba53904a00bda7f55280ed3afd8de55e8515d8247800`。

首次单流下载因 `curl --retry` 在 Range 恢复后复用旧偏移而产生不可信部分文件。该进程被定点终止，部分文件以 `preserved_failure_evidence_not_used` 状态保留；正式对象改由 28 个固定 Range 块下载，每块只在 HTTP 206 和精确字节数同时满足时接受。两个 SSL EOF 临时块均被拒绝并重新获取，最终组装对象通过字节、MD5 和 SHA-256 三重校验。

## 结构与矩阵合同

450 个结构 ID 为 `500` 到 `4990`、步长 10。每个结构均含 72 个碳原子、每原子轨道类型 `[0,0,1,1,2]`、每原子 13 个轨道和每结构 936 个轨道；每个 `rc.npz`/`rh.npz` 具有同一组 2880 个 `[R1,R2,R3,i,j]` 键。所有 Hamiltonian 块均为有限 `float64` 的 `13×13` 数组，所有局部旋转均为有限 `float64` 的 `3×3` 数组；最大旋转正交残差为 `2.17921530070387e-14`，最大行列式偏差为 `9.99200722162641e-16`，最大晶格—倒格关系残差为 `8.88178419700125e-16`。

`rh.npz` 是按各 edge 的 `rc.npz` 局部架旋转后的监督标签，不是统一全局 AO 基下的 Hamiltonian；因此，原始 `rh` 的逆边不能直接以简单转置判定。正式矩阵 Hermiticity 与逆边验收必须先使用冻结的 DeepH `Rotate` 合同回拉到统一 AO 基，并同时绑定 edge key、局部旋转和轨道顺序。该步骤原计划属于 M9-06，当前未因数据合同失败而提前执行。

## 阻塞项 `M9-DATA-B01`

每个结构只含以下八个对象：`element.dat`、`site_positions.dat`、`orbital_types.dat`、`lat.dat`、`rlat.dat`、`info.json`、`rc.npz` 和 `rh.npz`。全量递归检查没有发现 overlap、`rs.npz`、能带、k 点、DOS 或参考本征值对象。DeepH-pack v0.2.2 的官方说明同时明确：使用该训练数据得到模型后，物理推理仍需另行使用相同 OpenMX basis 计算 overlap。

由于 `isorthogonal=false`，不能把单位矩阵静默替代 overlap，也不能从 Hamiltonian、局部旋转或晶格推导出 overlap。这样做会改变广义本征问题和物理谱，违反 D-013 的对象边界。当前 D-014 又明确禁止安装 OpenMX、其他 DFT 后端或生成新标签。因此，以下验收没有合法输入：

- overlap 的 Hermiticity、正定性与条件数；
- `H(k)c=E S(k)c` 的广义本征残差；
- 依赖同一 basis overlap 的能带、简并、带隙、带宽和费米能窗比较；
- `H/S` 成对的反演与无自旋时间反演验证。

训练 loss 或 Hamiltonian 块误差不能替代这些物理验收。继续训练会越过顺序门控，并可能把训练成功误报为阶段 F 完成。

## 路线决策及后续门控

推荐方案已经由用户通过 D-017 明确采用：仅为冻结 graphene 结构和与数据 provenance 完全一致的 OpenMX 3.9 basis 获取 overlap，先冻结 OpenMX 对象、PAO/VPS 版本、basis 字符串、输入结构映射、无 SCF 的 overlap-only 命令和原总预算内的存储/CPU 墙钟子预算，再由独立审计通过后执行。该方案不允许生成 Hamiltonian、SCF 或其他 DFT 标签。正式合同见 [`M9_overlap_only_openmx_work_package.md`](../../08_audits/M9_overlap_only_openmx_work_package.md)。

若已有可信的、与 450 个结构和同一 basis 一一对应的预计算 overlap，可改为提供其发布 URL、字节与哈希；在来源和结构键映射独立审计通过前不得使用。

另一方案是正式降低 M9 为“训练合同复现”，删除 overlap、广义本征和能带验收。该方案会降低 D-013 已冻结的验收强度，不推荐，也不能由执行 agent 自行采用。

最后可以维持现有禁令，把 M9 记录为已证实的数据合同阻塞并停止阶段 F。此选择不构成 M9 完成，M10/M11 仍不能声称建立了完整物理基线。

## 证据位置与边界

项目侧机读摘要为 [`data_manifest.json`](../manifests/data_manifest.json)。完整逐文件清单、数据合同和命令日志保留在 `/home/evan-williams/deeph-m9`，不复制大型数据或运行时对象到项目目录。当前训练 GPU 秒与物理验证 GPU 秒均为 0；未冻结训练后容差，未运行训练或试推理，未安装 OpenMX，未生成 DFT 标签，预算无违规。
