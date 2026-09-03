# M9 source_build v2 独立安装事实审计

审计日期：2026-08-31。结论：PASS；blocking=0，non_blocking=0。本报告证明正式v2安装及只读消费路径通过，不代表permit已经签发或source_build已经执行。独立审计期间未调用install、permit、run或任何构建动作，未修改正式运行态及冻结来源。

## 实际安装与绑定

独立读取实际root-owned snapshot/readiness，核验严格schema、闭集、内容哈希、身份权限及实施报告绑定。结果与机械安装预期一致。

| 证据 | 实际值或SHA-256 |
| --- | --- |
| 新12-file frozen | `bc80d1d939527818c7eec747a60cd17c6000f9015374ff33192f34c2f3ae7614` |
| 实施报告 | `ba520a61bb95933f02d5768a21f8c0c00a856c8911739c5b72b589106b156cdc` |
| 实施verdict | `1a24cbd113c3ec1b0becfb95daffb9b16f1d35595e4735b00af91cca9a643141` |
| 正式readiness gate | `05bbe471d46408de8beb94594907b6c6371a3663359dbf8ae0540cc51713356b` |
| snapshot_manifest | `d46a6ff5f742a6331267ffef368bab0eb9303ed9f124e2e7db7f5d1349b98f6f` |
| history attestation | `58deab7698c64d446f07a72ed744404f0fcc443370a1e14829267ab99012825a` |

`controls/source-build-v2`为root:1000/0550目录，dev:ino=2096:162491、nlink2。目录内恰17个普通单链接文件，全部root:1000/0440，严格对应12项冻结来源、新frozen、实施report/verdict、派生budget和snapshot_manifest。所有内容与各层manifest绑定一致；派生budget仍为 `94050d73f498b84ab0054f64f1b04ea8667067f86a54ed3f352e6b926a9e691e`。新12项及旧25/16/10闭集全部重新核验通过。

`manifests/source_build_v2_gate.json`为3259 bytes，root:1000/0640、nlink1、dev:ino=2096:167852。scope/action、operation `a237ec1f2b404d898840c643e9ae501b`、nonce、授权记录、实施报告/verdict、snapshot、history attestation及runtime均匹配。gate不是execution permit。

## 正式增量与历史保留

以v1安装后完整baseline `M9_source_build_v1_installation_postexecution_evidence.json`（SHA `0e125e288af8299fb3cf6447ac379e3b946bd042ddd705537dcd9cff11300f00`）逐项比较。实际namespace由147增至166对象，新增恰为新snapshot目录、17文件及新gate，共19项，无删除和未知新增。旧147项除controls/manifests两个父目录规定的元数据变化外全等；controls的nlink从7增至8。旧v1 snapshot/gate、固定8项root:root/0600历史和/root控制证据均未修改。

root在原budget.lock内实际读取全量正式对象，包括固定8项和/root历史；未用UID metadata-only结果替代这些内容证明。原锁dev:ino=2096:50700，uid/gid1000、0644、nlink1、空文件，身份保持。正式166对象canonical SHA为 `7feae3d05aab27e954b02cab06197cbedeaad7286676498c7bd0d9e223ddf662`。

准备树和失败退休树各5319 receipts，与安装前既定哈希及只读验证前后完整字典一致。其canonical SHA分别为 `7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260`、`060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359`。D-017/D-018、source_prepare失败/恢复/成功与v1安装FAIL历史均保留；本次PASS不改写旧FAIL结论。

state/workflow/transaction/ledger原始字节与已保存baseline逐项全等。ledger仍64298 bytes，SHA `0be27e9220b6597d47ee657bbe5169134118340c77a7a0af3722a4eb1ad885c2`；runtime五绑定canonical SHA仍 `e066af35757b5610dbeac189ad36a4cf6a9e1b0f89014e24f4bc573b0a655a29`。workflow为SOURCES_PREPARED，事务`dc75dda112af553377a697f629801782`仍为source_prepare/SUCCESS_COMMITTED，无active transaction或hard stop。v2 staging、permit及其tmp、v1 permit及所有禁止的构建/运行产物均缺席。

## 真实UID1000安装入口

通过`/usr/sbin/runuser -u evan-williams --`启动固定Python3.9.23 `-I -S -B`，直接执行正式root-owned安装路径 `/home/evan-williams/deeph-m9/controls/source-build-v2/m9_source_build_v2_consumer.py`。没有重写入口条件、模拟UID、替换验证函数或使用项目副本替代安装入口。

| 实际动作 | 结果 |
| --- | --- |
| `verify-ready` | rc0，status=PASS，source_build_executed=false；stderr为空，runtime SHA与root一致 |
| `verify-execution` | rc1，stdout为空；明确FileNotFoundError指向 `/home/evan-williams/deeph-m9/manifests/source_build_v2_execution_permit.json` |

缺permit拒绝发生在历史、snapshot、gate和准备树验证之后，未出现v1的PermissionError。每条命令结束后均重新持原锁采集166对象，与命令前字典严格全等；最后两棵完整树及runtime原始字节也全等。因此本次两条正式入口验证均为零写。这里的UID对固定8项仍采用经root封存绑定的元数据检查，不声称UID实际读取root-only内容。

## 预算、持久证据与后续条件

原预算函数对4GiB预测返回violations=[]。overlap_build原始累计7212.901214103001秒，有效12.825903575000666秒，余额7187.174096424999秒；既有抵扣、历史事件及上限未变。GPU compatibility累计54.84820560599999秒，training/physical_validation均0。

采集时总apparent/allocated为31132517105/31458013184 bytes，overlap增量1263037374/1288192000 bytes，VHDX为28064088064 bytes，项目审计apparent/allocated为3439643/3809280 bytes。之后新增本次审计证据和报告仍计入原存储预算，签发与运行前须再次即时核验，不能复用该存储读数作为未来通过证明。

独立证据保存于 `M9_source_build_v2_installation_postexecution_evidence.json`，177974 bytes，SHA `8bd80c401c6ca2b3fa986a6452574644ad1d49de3a08e6befe90f21a8dba3775`。其中包含完整166项receipt、允许父目录变化、四份runtime原始字节Base64、五项runtime绑定、gate原始字节、两树前后哈希、预算与两条真实UID命令的完整argv/stdout/stderr/退出码。保存后通过固定Python重新核对canonical SHA和raw字节哈希，纳秒整数未经过浮点序列化；可作为后续permit与单次执行事实审计基线。完整准备树证据仍由不变的前序baseline引用链保留。

M9缓存扫描为0，未使用py_compile；本报告Pandoc严格Markdown与git diff --check通过。实施报告/verdict及其他已绑定文件保持原SHA。本安装PASS允许主端按冻结loader和本报告/verdict绑定机械签发一次v2 permit；签发后仍须独立核验实际permit及真实UID1000 verify-execution，再由主端执行已批准的一次冻结编译自测。当前尚未执行构建，不关闭M9-DATA-B01，不放行材料结构、smoke/batch、训练或其他动作。
