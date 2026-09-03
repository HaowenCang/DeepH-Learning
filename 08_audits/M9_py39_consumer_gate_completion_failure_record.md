# M9 Python 3.9 consumer gate 安装中断事实记录

日期：2026-08-29  
范围：`D-018-PY39-CONSUMER-GATE-COMPLETION`  
状态：`INSTALLER_EXITED_BEFORE_CONSUMER_GATE`

受审 single-FD loader 已成功安装 `uid1000-consumer-py39-v2-bootstrap`。随后从该 root 信任根调用固定 Python 3.9.23、`-I -S -B` 的 trusted installer，进程以退出码 1 和唯一诊断 `Python-3.9 recovery terminal evidence mismatch` 结束。未调用 `source_prepare` 或其他预算动作。

中断后的只读事实如下：

- bootstrap receipt：1,399 bytes，SHA-256 `3107543507a64e2eb7e50227293b278e35a95e87b4815c1674ce70ea14673fea`；
- replacement snapshot manifest：9,746 bytes、28 members，SHA-256 `b9c7358b1f976d85c31f2defec1e06d25338ea3dfbe51b1594eb2e6ca1b3fc7d`；
- refresh journal：`SUCCESS_COMMITTED`，1,733 bytes，SHA-256 `b9d7800e471fe74da00fb78ac911004106db1195326812d098b575f5c25fb292`；
- 新 active gate：SHA-256 `229f0846c3d22917ccb955729a577168880bca6a53ad07f32502b0ae4a4e27ab`，inode `2096:162490`；
- 旧 active gate 退休对象：SHA-256 `78311a978c2472c85b35a745d80e1f33724c1500cf8d7bd244cdbe83c3fa3698`，保留原 inode `2096:153476`；
- replacement consumer gate：缺席；单次 `source_prepare` authorization：缺席；active staging：缺席；
- state SHA-256 `f51960808c7e0c518972cd717ae94fbc2a070be57638862c4b143970f3223e73`；workflow SHA-256 `384a4de85803666e305ca55b38dd6966c40244f789ac887a52b5a282095e2492`；ledger 61,826 bytes，SHA-256 `5253620510f84d1987874c5fa571f6016cedfbdabc6e80a4b126e724839b1ea9`。

只读复现表明，refresh journal 的 `active` receipt 为 `{path, bytes, sha256, uid, gid, mode, nlink, dev, ino}`，而 `consumer_runtime_receipts()["active_overlap_gate_sha256"]` 为同一文件的 `{path, bytes, sha256, uid, gid, mode, nlink}`。两者七个共享字段逐项相等，只有前者额外保存 inode 身份；trusted installer 对两个字典执行整对象不等比较，因而产生确定性假阴性。该错误发生在 consumer gate 写入前，未改变预算、runtime 或历史证据。

后续不得机械重试旧 installer。只允许在新的独立审计 `PASS/BLOCKING=0/NON_BLOCKING=0` 后，通过一次性 completion 控制器在同一 `budget.lock` 下重放全部既有验证，严格证明 receipt 只相差 `dev/ino`，再签发缺失 consumer gate。completion 仍不创建 authorization，也不授权 `source_prepare`。
