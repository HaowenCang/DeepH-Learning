# M9 source_build v2 独立执行前复核

审计日期：2026-08-31。结论：PASS；blocking=0，non_blocking=0。正式采集于2026-08-31T07:21:36.762379+00:00完成。实际许可及真实UID1000只读执行验证均通过，可由主端执行已批准的唯一冻结编译自测命令一次。本轮没有执行run、build、permit或其他正式写入。

## 许可与唯一增量

以已封存166对象安装证据SHA `8bd80c401c6ca2b3fa986a6452574644ad1d49de3a08e6befe90f21a8dba3775`逐项比较，当前恰167对象。唯一新增为 `manifests/source_build_v2_execution_permit.json`，仅manifests父目录mtime/ctime变化；其他166对象的身份、权限、大小、时间及文件哈希全等。

permit为447 bytes、root:1000/0640、nlink1，dev:ino=2096:162503，SHA `b00e367be4f06f81a6e8d2e86b72d058c2d6e59e84729637d7f03a8f50594d9e`。实际严格六字段schema、gate SHA `05bbe471d46408de8beb94594907b6c6371a3663359dbf8ae0540cc51713356b`、operation `a237ec1f2b404d898840c643e9ae501b`、固定nonce、安装报告SHA `5be394d6ff7dfb8ea79d2cb3130b29e2cca803dc7111eecab9f81a4460dd2212`及安装verdict SHA `7bc76fcedbc15de4a50a1b7db2765ecd83456188442bace012a33a30e8129a2b`全部匹配。原12/25/16/10来源闭集及snapshot/readiness/实施权威绑定再次通过真实验证函数，未改写旧报告或权限。

root在原budget.lock内全量读取167对象，包括固定8项及/root历史。正式namespace canonical SHA为 `504dfef4ee662954b6755dce850742f2a4dc37f09adfec8e1ca32b9120978460`。准备树、失败退休树各5319 receipts，哈希仍分别为 `7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260`、`060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`。新staging/tmp、v1 permit及禁止的构建/运行产物均缺席。

## 真实消费、预算与零写

实际调用`runuser -u evan-williams --`，使用固定Python3.9.23 `-I -S -B`，从root-owned正式v2路径执行`verify-execution`。退出码0、stderr为空；stdout为status=PASS、action=source_build、source_build_executed=false，runtime SHA `e066af35757b5610dbeac189ad36a4cf6a9e1b0f89014e24f4bc573b0a655a29`。该命令前后167对象、两棵完整树、runtime及state/workflow/transaction/ledger原始字节全等；锁身份保持，缓存扫描为0。

workflow仍为SOURCES_PREPARED，事务`dc75dda112af553377a697f629801782`仍source_prepare/SUCCESS_COMMITTED。ledger仍64298 bytes，SHA `0be27e9220b6597d47ee657bbe5169134118340c77a7a0af3722a4eb1ad885c2`。CPU原始累计7212.901214103001秒、有效12.825903575000666秒、余额7187.174096424999秒，历史抵扣不变；GPU compatibility累计54.84820560599999秒，training/physical_validation为0。

原预算函数即时4GiB预测返回violations=[]。采集时总apparent/allocated为31132702911/31458205696 bytes，overlap增量1263223180/1288384512 bytes，项目审计apparent/allocated为3625002/3997696 bytes，VHDX为28064088064 bytes。新增审计文件仍计入存储，正式入口保留即时预算与首次写前重验，不以本报告替代运行时守卫。

完整167项receipt、四份runtime原始字节Base64（含完整ledger）、五项runtime绑定、许可原字节、前后比较、真实UID命令及完整输出、预算和唯一批准argv保存在 `M9_source_build_v2_preexecution_evidence.json`，169190 bytes，SHA `4efc0337731d39412e312b84998096252600bd4f6ce8b7e22976eda5a226747a`。保存后用固定Python重算namespace canonical及原字节哈希通过，纳秒整数无浮点损失，可用于执行后的ledger前缀与逐项增量审计。报告Pandoc严格Markdown及git diff --check通过。

## 唯一执行与边界

主端应以真实UID1000执行如下完整argv一次，不增删参数，不重试。此后立即以本证据作独立执行事实审计。

```powershell
wsl -d Ubuntu-22.04 -u evan-williams -- /home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9 -I -S -B /home/evan-williams/deeph-m9/controls/source-build-v2/m9_source_build_v2_consumer.py run --build-operation-id a237ec1f2b404d898840c643e9ae501b --bucket none --cpu-bucket overlap_build --forecast-bytes 4294967296 --overlap-operation --overlap-action source_build --config /mnt/e/Projects/Codex/DeepH/06_reproduction/configs/m9_overlap_only_contract.json
```

本PASS不是构建完成或M9科学结果通过。授权仅覆盖冻结编译与构建自测，不下载、不计算材料结构、不训练，不扩展至smoke/batch/GPU或其他正式动作；M9-DATA-B01仍OPEN。任何失败或新漂移应停止并保留证据，不以本次许可自行重放。
