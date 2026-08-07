# COVER-01 Round 1 Result

## 当前科学问题

当前 MiniMind-V / authoritative source data 是否能唯一固定一个
“互补覆盖 versus 同域冗余”的单因素训练对照和未见 generative-VLM target？

## 假设

若 authoritative controlled coverage 是当前可裁决机制，则 direct generative
primary evidence、source schema、local example lineage、单因素对照和冻结 held-out
prediction 应同时通过，不需要 embedding/LLM cluster、mixture/domain/target sweep
或事后 benchmark 选择。

## 本轮实验

五族冻结 query 共检索 442 raw records、380 unique titles，标记 69 个 prior-search
duplicates 和 75 个 score≥10 records；全文核查 14 篇决定性 primary sources。
同时核查 MiniMind 与 ALLaVA 官方 revision/card/tree/schema，并用可复现脚本对本地
1,274,698-row pretraining parquet 做只读 lineage audit。本轮未运行 checkpoint、
GPU 或训练，也未访问 final confirmation。

## 判定标准

- **支持**：authoritative strata、exact baseline lineage、direct/formal evidence、
  unique single-factor contrast、frozen held-out direction、合法访问及算法出口全部
  通过。
- **否定**：任一关键对象依赖随机/embedding/LLM/manual grouping，或 coverage 与
  source/task/style/quality/difficulty 同变，或必须搜索 mixture/domain/target/metric，
  或只有 CLIP 证据而无 generative bridge。
- **无法判断**：仅限决定性全文、官方 schema/license/version 或本地 exact artifact
  无法取得或核实。

## 执行结果

- **Direct generative evidence 不满足唯一门**：
  - Vision-Flan 的 10/20 versus 187-task fixed-total evidence最接近“更多覆盖”，但
    task identity、source dataset、task/output type、difficulty 与 coverage 同时变化；
  - MM1/MM1.5 的 fixed-step mixture ablations 改变 format、source、context structure
    与 capability，并比较多个 ratio/category；
  - DCVLR 隔离了 fixed model/recipe，但 difficulty filtering、alignment、synthetic
    mixture 与 diversity 同时变化；
  - DMO、DataProphet、MixAtlas 与 DecoupleMix 均依赖 target outcome、mixture search、
    embedding cluster、LLM judge 或 proxy-scale optimization。
- **最干净的 controlled-coverage evidence 仍是 CLIP-only**：
  arXiv:2502.09507 用 DomainNet source-defined domain/class、matched within-target
  sizes 和三 seeds 测未见域/组合；但其对象是 contrastive CLIP zero-shot
  classification，未给出到 autoregressive LVLM token/semantic risk 的 theorem bridge。
- **本地 lineage 比“schema 无 ID”更可恢复**：
  local parquet 的 SHA-256 与官方 MiniMind revision/tree 完全一致，schema 只有
  `conversations` 与 `image_bytes`，source tokens 计数均为 0；然而保存的官方
  169 个 caption rows 的 English assistant text 全部一对一精确匹配本地行
  （76 LAION、93 VFLAN）。因此不能宣称 lineage 整体不可恢复。
- **sample reconstruction 仍不等于 exact factorial lineage**：
  保存样本中 3 个 VFLAN `id` 各重复两次；full-dataset 与中译行 ID 传播尚未证明。
  更重要的是，LAION/VFLAN 标签同时编码 acquisition、natural/document/chart
  content、task origin、caption style、quality 与 difficulty，无法唯一指定
  complementary/redundancy/held-out cells。
- 14/14 decisive sources、official source receipts 与 exact local artifact 均可核查，
  因而不是 `INCONCLUSIVE`。
- Search index 在 fresh temporary directory 中 byte-identical 重建，SHA-256 为
  `064cfe8d4fb61545fd864bc4da35bc9f2a1bdd2f6dcf9d86bafbf3af26b05cc0`。

## 结论

`COVER-01=NO_CANDIDATE`，failure level=`BRIDGE_REJECTED`：当前审计的
authoritative-source/data-lineage → local unique single-factor
complementary-coverage-versus-redundancy bridge 不成立。

**What exactly is rejected**：使用当前审计的 broad source/task labels 和现有
primary protocols，在不搜索 domain/mixture/target 且不引入主要混杂的条件下，
唯一构造本地 coverage intervention 的 bridge。

**What is NOT rejected**：数据覆盖/多样性影响 VLM 泛化、Vision-Flan task
diversity、domain/compositional coverage、source-specific transfer、ALLaVA 全量 ID
恢复可能性，以及未来真正 source-factorial 的 generative-LVLM coverage 实验。
本轮没有达到 `MECHANISM_REJECTED`。

## 下一步

不再从 broad LAION/VFLAN/task-category 标签挑选 mixture；转向一个更窄的
source-defined crossed-cell 问题：检索是否存在“同一 image/acquisition unit × 多个
authoritative text/task factors”的真实 factorial multimodal schema，可在 held-out
crossed cell 上固定 prediction，同时正交控制 source、quality、difficulty 和 output
format。执行前另建并提交 immutable plan。

## 状态

`REJECT_IDEA`
