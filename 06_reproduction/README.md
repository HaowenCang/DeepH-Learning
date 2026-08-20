# M9 最小 DeepH 复现

本目录保存 M9 的小型可审计产物；正式软件、数据、环境和大体积运行结果位于 WSL 内的 `/home/evan-williams/deeph-m9`，其 Linux 虚拟磁盘由 Windows 注册在 `E:\Laptop\WSL`。项目侧白名单小型产物合计上限为 1 GiB，并与 Linux 工作根合并计入 100 GiB 总预算；不得在本目录保存数据集、环境或检查点。

M9-01—03 已通过。M9-04 的冻结 Zenodo ZIP、安全解包、逐文件清单和 450 结构全量数据合同已经完成；所有结构均为非正交基且发布包没有 overlap，`M9-DATA-B01` 保持开放，M9-05 不允许启动。D-017 受限 overlap-only 工作包第四次定点复核确认 `.pth` 主穿透关闭，但 B07 因 `overlap-init` 未核对冻结解释器身份而保持开放。第五轮最小修复已把解释器身份检查移入公共 bootstrap，覆盖 init/run 且先于任何状态读写；系统 Python 3.10 的 init 零写入负例通过，19/19 合成穿透通过，等待同一审计员第五次复核。复核通过前仍禁止安装、解压、编译、生成输入或运行 OpenMX。正式对象见 [`M9_overlap_only_openmx_work_package.md`](../08_audits/M9_overlap_only_openmx_work_package.md)、[`m9_overlap_source_launcher.py`](scripts/m9_overlap_source_launcher.py) 与 [`test_m9_overlap_controls.py`](tests/test_m9_overlap_controls.py)。

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
