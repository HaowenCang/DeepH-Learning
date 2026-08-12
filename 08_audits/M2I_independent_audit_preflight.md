# M2-I 独立内容审计送审前检查

## 结论

结论为 **送审就绪（`READY`）**。M2I-01、M2I-02 和 M2I-03 的来源定位已经完成，第 1 章提纲具备交给独立上下文审计的证据入口。本记录只属于内部送审前检查，不是独立内容审计，不解除 M2-I 门控，也不授权开始 M3 正文定稿。

## 本次检查范围

- 复核 FND-01—05 的版本、章节、页码、定理位置和证据边界；
- 逐页复核 DH-01 正文第 375—376 页及补充材料印刷页第 2—4 页；
- 检查 `outline.md` 中广义本征问题、正交化接口和一阶扰动式的条件表述；
- 检查来源台账、书目、章节资料包、资料缺口记录和进度台账能否相互追溯。

## 发现与处置

| ID | 发现 | 严重性 | 处置 | 状态 |
|---|---|---|---|---|
| PF-01 | 原提纲把含 \(\delta S\) 的广义本征扰动式置于“标准正交”条件下，条件与公式不一致 | `BLOCKING`（送审前） | 改为可微厄米矩阵族、\(S\succ0\)、简单特征值和 \(S\)-归一化条件 | `CLOSED` |
| PF-02 | FND-02—03 不能单独精确定位对称正交化 | `BLOCKING`（来源） | 新增 FND-04；第 35 页明确给出 \(B^{-1/2}\) 与 Cholesky 两种约化 | `CLOSED` |
| PF-03 | FND-03 不直接给出本章采用的一阶扰动式 | `BLOCKING`（来源归属） | 新增 FND-05 的简单特征值定理；广义 \(H/S\) 形式继续标为直接推导 | `CLOSED` |
| PF-04 | 现代 DeepH-pack 的 Hamiltonian、overlap、density matrix 分工尚未按固定发布物核验 | `NON_BLOCKING`（第 1 章概念审计） | 保留 M2I-04 为 `PLANNED`，禁止把原始 DeepH 分工外推到现代软件 | `OPEN` |

## 送审证据

- `03_textbook/chapters/01_deeph_problem/outline.md`：被审计提纲；
- `03_textbook/chapters/01_deeph_problem/sources.md`：FND-01—05 与 DH-01 页码；
- `03_textbook/chapters/01_deeph_problem/independent_audit_brief.md`：独立审计问题和结论口径；
- `02_source_ledger/source_table.csv` 与 `01_sources/bibliography.bib`：结构化来源和书目；
- `08_audits/M2_source_gap_closure.md`：来源缺口关闭记录；
- `01_sources/README.md`：本地 PDF 来源与 SHA-256。

## 未解除的门控

M2I-05 必须由独立上下文按照审计简报执行，并形成包含结论、逐项结果、可复现证据位置、阻塞修改项和非阻塞建议的正式报告。只有正式报告给出“通过”，或“有条件通过”的全部阻塞项完成修订并复核后，M2-I 才能进入 `COMPLETED`，M3 任务才可转为 `READY`。
