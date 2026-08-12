# M9 最小 DeepH 复现

本目录保存 M9 的小型可审计产物；正式软件、数据、环境和大体积运行结果位于 WSL 内的 `/home/evan-williams/deeph-m9`，其 Linux 虚拟磁盘由 Windows 注册在 `E:\Laptop\WSL`。项目侧白名单小型产物合计上限为 1 GiB，并与 Linux 工作根合并计入 100 GiB 总预算；不得在本目录保存数据集、环境或检查点。

M9-01 已由同一独立审计员第二次定点复核为 `PASS`、问题为 0。M9-02/M9-03 固定环境与实机兼容性已通过。M9-04 的冻结 Zenodo ZIP 下载、哈希、CRC、安全解包、逐文件清单和 450 结构全量数据合同已经完成；所有结构均为非正交基且发布包没有 overlap。独立全量审计确认 `M9-DATA-B01` 为唯一开放阻塞，`BLOCKING=1`、`NON_BLOCKING=0`，M9-05 不允许启动。用户已通过 D-017 授权受限 overlap-only OpenMX 路线；新增 [`M9_overlap_only_openmx_work_package.md`](../08_audits/M9_overlap_only_openmx_work_package.md)、[`m9_overlap_only_contract.json`](configs/m9_overlap_only_contract.json)、来源检查器、输入生成器和 overlap 验证器。当前只进入独立工作包审计，尚未安装、编译、生成输入或计算。原阶段工作包见 [`M9_stageF_work_package.md`](../08_audits/M9_stageF_work_package.md)；环境对象见 [`environment_manifest.json`](environment/environment_manifest.json)，数据阻塞证据见 [`data_manifest.json`](manifests/data_manifest.json)、[`M9_data_contract_report.md`](reports/M9_data_contract_report.md) 和 [`M9_data_contract_independent_audit.md`](../08_audits/M9_data_contract_independent_audit.md)。

项目文件不得包含 Linux 认证口令或其他敏感凭据。需要提权时使用宿主 WSL root 入口；不把口令传入命令行或日志。

## 预期产物

```text
06_reproduction/
├── README.md
├── environment/
├── manifests/
├── configs/
├── scripts/
├── tests/
└── reports/
```

所有配置和验证脚本在实际对象核查后形成；不提前猜测官方 graphene 数据的轨道字符串、内部目录、划分或数值容差。
