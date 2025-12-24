# SITE_E_SP3_C_LG_v1 — sp3碳-离去基亲电中心映射

| Field | Value |
|---|---|
| Skill ID | `SITE_E_SP3_C_LG_v1` |
| Type | Prompt Skill (Site → Reaction Catalog) |
| Site Type | `E_SP3_C_LG` |
| Site Kind | `ATOM` |
| Category | 亲电类（E+） |
| Schema | `SITE_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Depends On | L0 GroundTruth, L1 SiteMap |

## Purpose
针对带离去基的 sp3 碳亲电中心，输出取代/消除等反应族候选，并提示 SN2 vs SN1/E2/E1 竞争。

## Non-goals
- 不直接给出机理定论；只输出候选反应族与结构层面倾向（位阻、稳定正离子等）。

## Inputs (Schema)
```json
{
  "ground_truth": {
    "canonical_smiles": "string",
    "inchi": "string (optional)",
    "inchikey": "string (optional)",
    "atom_table": "AtomRecord[]",
    "bond_table": "BondRecord[]",
    "standardization_version": "string"
  },
  "site": {
    "site_id": "string",
    "site_type": "string",
    "site_kind": "ATOM|BOND",
    "atom_index": "int|null",
    "bond_index": "int|null",
    "local_env": "object",
    "evidence": "EvidenceItem[]",
    "confidence": "0..1"
  },
  "context": "object (optional)"
}
```

## Outputs (Schema)
```json
{
  "reaction_keys": ["string"],
  "requirements": { "reaction_key": ["string"] },
  "exclusions": { "reaction_key": ["string"] },
  "notes": ["string"]
}
```

## Reaction Catalog
| Reaction Key | Family | Description |
        |---|---|---|
        | `RXN_SN2_v1` | 亲核取代（SN2） | 位阻小/良好离去基时更优。 |
| `RXN_SN1_v1` | 亲核取代（SN1） | 可形成稳定碳正离子（三级/苄位/烯丙位）时更优。 |
| `RXN_E2_v1` | β-消除（E2） | 强碱/β-H 可用/位阻大时更优。 |
| `RXN_E1_v1` | β-消除（E1） | 与 SN1 竞争（正离子途径）。 |
| `RXN_SOLVOLYSIS_v1` | 溶剂解 | 偏 SN1/E1 条件依赖。 |

## Priority Rules
- 一级中心：提高 RXN_SN2_v1；三级中心：降低 SN2，提高 SN1/E2/E1。
- 若 local_env 显示 β-H 丰富且位阻大：提高 RXN_E2_v1。

## Common Exclusions / Conflicts
- 当中心为 sp2（芳基/烯基）时不属于本位点类型，应归类到其他位点（如 SNAr/偶联等）。

## Prompt Template
### Prompt Template

**System**
你是“反应位点→反应族映射（Prompt Skill）”专家。你只能使用输入中的 `ground_truth` 与 `site`（来自结构真值层 L0 与位点图谱层 L1），不得猜测结构、不得引入未提供的条件信息。若缺少关键条件，请在 `requirements` 中标注“条件依赖”。

**User**
给定如下 `site`（site_type=E_SP3_C_LG）及其 `local_env` 与 `evidence`，请输出该位点最可能参与的反应族 `reaction_keys`（按优先级排序），并为每个反应族给出：
- 最小触发条件（requirements）
- 常见否决/冲突条件（exclusions）
- 竞争路径/注意事项（notes）

**Output (JSON)**
```json
{
  "reaction_keys": ["RXN_..._v1"],
  "requirements": {
    "RXN_..._v1": ["..."]
  },
  "exclusions": {
    "RXN_..._v1": ["..."]
  },
  "notes": ["..."]
}
```

## Examples
**Example 1**
- SMILES: `CCBr`
- 位点提示: 与 Br 相连的 C
- 期望反应族（示例）: `RXN_SN2_v1`, `RXN_E2_v1`
**Example 2**
- SMILES: `CC(C)(C)Br`
- 位点提示: 三级 C
- 期望反应族（示例）: `RXN_SN1_v1`, `RXN_E2_v1`, `RXN_E1_v1`

## Confusable With
- E_BENZYLIC_C_LG（苄位）
- E_ALLYLIC_C_LG（烯丙位）

## Failure Modes
- 结构解析失败或位点识别不可信：应由上游 L0/L1 直接 FAIL，本技能不得继续推断。
- 条件缺失：必须在 requirements 中标记“条件依赖”，不得给出确定性结论。
- 位点类型误分：应回退检查 L1 规则与 evidence（SMARTS/规则编号）。

## Changelog
- 2025-12-24: initial version
