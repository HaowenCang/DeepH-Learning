# M9 冻结环境复现说明

## 1. 适用范围

本说明只复现 D-013 与 D-014 冻结的 DeepH-pack v0.2.2 直接环境。它不授权安装 OpenMX 或其他 DFT 后端，不生成 DFT 标签，也不改变材料、SOC、磁性或预算范围。正式大体积环境位于 `/home/evan-williams/deeph-m9`；项目侧文件只保存锁、清单、命令和小型测试。

## 2. 固定安装器与制品

Miniconda 安装器为 `Miniconda3-py39_25.9.1-3-Linux-x86_64.sh`，SHA-256 为 `0ac18f10d17ca918247b4606df82be38eba6e23380a7eddb25b47ef6ccdb920e`。Julia 制品为 `julia-1.6.6-linux-x86_64.tar.gz`，SHA-256 为 `c25ff71a4242207ab2681a0fcc5df50014e9d99f814e77cacbc5027e20514945`。

Conda 的常规下载器在大包传输中多次出现 `IncompleteRead`，因此 PyTorch 与 CUDA runtime 应使用 `curl -C -` 续传到 Miniconda 包缓存，并在安装前核验：

```text
pytorch-1.9.1-py3.9_cuda11.1_cudnn8.0.5_0.tar.bz2
bytes 1542096331
md5   00a69e75b48b9fc8bbffc2b67bb2ebef

cudatoolkit-11.1.1-hb139c0e_13.conda
bytes 974708650
md5   9528bea6b0539cf7e5adc6a2e51f7213
sha256 ea3760bed1195a395df228aaa3dfd270bb47fdb367e99db3d956a0d9fc4d9eab
```

## 3. 精确重建命令

以下命令假定 Miniconda 安装在冻结根目录，并且两个大包已按上一节的文件名放入 `pkgs/`。`conda-explicit-linux-64.txt` 中的两个 `file:///` 条目因此能够直接解析。

```bash
ROOT=/home/evan-williams/deeph-m9
CONDA="$ROOT/env/miniconda3/bin/conda"
ENV="$ROOT/env/deeph-v022"

"$CONDA" create -y -p "$ENV" \
  --file /mnt/e/Projects/Codex/DeepH/06_reproduction/environment/conda-explicit-linux-64.txt

"$ENV/bin/pip" install \
  e3nn==0.3.5 opt-einsum==3.4.0 opt-einsum-fx==0.1.4

git clone https://github.com/mzjb/DeepH-pack.git "$ROOT/software/DeepH-pack"
git -C "$ROOT/software/DeepH-pack" checkout --detach \
  66703c532a6f633f4bbc8f94f75c8698a7f89859
"$ENV/bin/pip" install --no-deps "$ROOT/software/DeepH-pack"
"$ENV/bin/pip" check
```

精确显式锁包含全部 Conda 传递依赖；`environment-lock.yml` 与 `pip-freeze.txt` 是已安装 Python 视图的交叉证据。`direct-environment.yml` 记录最终直接规格，不应重新求解后用相邻版本替换显式锁。

## 4. 兼容性修复边界

环境求解后固定了以下非主栈兼容项：

- `pymatgen==2023.5.10`、`mp-api==0.29.8`、`emmet-core==0.57.1`、`pydantic==1.10.13`，用于同时满足 NumPy 1.23.5 和合法 Python 元数据；
- `mkl==2024.0.0`、`blas==2.121=mkl`，避免 MKL 2026 与 Torch 1.9.1 的 `iJIT_NotifyEvent` 符号冲突；
- `setuptools==59.5.0`，保留旧 Torch TensorBoard 适配层所需的 `distutils.version`；
- `rdflib==7.1.4`，关闭 PyG 1.7.2 的缺失依赖。

这些版本均已进入显式锁。不得以当前最新版覆盖它们。

## 5. 正式 smoke test

所有 CUDA 命令均应由 `m9_budget.py` 归入 `compatibility` 桶。cuBLAS 的确定性前提固定为 `CUBLAS_WORKSPACE_CONFIG=:4096:8`：

```bash
python3 /mnt/e/Projects/Codex/DeepH/06_reproduction/scripts/m9_budget.py run \
  --bucket compatibility --forecast-bytes 0 \
  --log /home/evan-williams/deeph-m9/logs/compatibility_smoke.log -- \
  env CUBLAS_WORKSPACE_CONFIG=:4096:8 \
  /home/evan-williams/deeph-m9/env/deeph-v022/bin/python \
  /mnt/e/Projects/Codex/DeepH/06_reproduction/scripts/m9_compatibility_smoke.py \
  --config /home/evan-williams/deeph-m9/software/DeepH-pack/ini/graphene.ini
```

两个新进程的规范 JSON 摘要 SHA-256 均为 `dc3f1e08f9f97715f4e72e35ef572e654b5514fb5270fd62dfc4a87d62a79d83`。该结果证明本机 sm_89 上的冻结 PyTorch、PyG 与 e3nn 最小 CUDA 前后向可运行；它不外推为其他 GPU、驱动或训练任务已经通过。
