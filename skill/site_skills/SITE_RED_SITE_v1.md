# SITE_RED_SITE_v1 — 易还原位点映射

| Field | Value |
|---|---|
| Skill ID | `SITE_RED_SITE_v1` |
| Type | Prompt Skill (Site → Reaction Catalog) |
| Site Type | `RED_SITE` |
| Site Kind | `ATOM` |
| Category | 自由基/氧化还原 |
| Schema | `SITE_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Depends On | L0 GroundTruth, L1 SiteMap |

## Purpose
针对结构上可能易被还原的位点（羰基、硝基、腈、C=C 等，需由 local_env/evidence 标识），输出相应还原反应族候选。

## Non-goals
- 不在未定类时泛化输出；必须基于 evidence 限定类别后输出。

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
        | `RXN_REDUCTION_CARBONYL_v1` | 羰基还原 | 醛/酮/某些酯等；条件依赖。 |
| `RXN_REDUCTION_NITRO_v1` | 硝基还原 | 硝基→胺；条件依赖（若 site ontology 标识硝基）。 |
| `RXN_HYDROGENATION_C_C_v1` | 烯烃/炔烃加氢 | 条件依赖。 |
| `RXN_DEHALOGENATION_v1` | 脱卤还原 | 条件依赖。 |
| `RXN_REDUCTION_NITRILE_v1` | 腈还原 | 腈→胺；条件依赖。 |

## Priority Rules
- 若 evidence 标识羰基：优先 RXN_REDUCTION_CARBONYL_v1；若标识 C=C：优先 RXN_HYDROGENATION_C_C_v1。

## Common Exclusions / Conflicts
- （无）

## Prompt Template
### Prompt Template

**System**
你是“反应位点→反应族映射（Prompt Skill）”专家。你只能使用输入中的 `ground_truth` 与 `site`（来自结构真值层 L0 与位点图谱层 L1），不得猜测结构、不得引入未提供的条件信息。若缺少关键条件，请在 `requirements` 中标注“条件依赖”。

**User**
给定如下 `site`（site_type=RED_SITE）及其 `local_env` 与 `evidence`，请输出该位点最可能参与的反应族 `reaction_keys`（按优先级排序），并为每个反应族给出：
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
- SMILES: `CC(=O)C`
- 位点提示: 羰基 C
- 期望反应族（示例）: `RXN_REDUCTION_CARBONYL_v1`

## Confusable With
- OX_SITE（易氧化位点）
- E_CARBONYL_C（亲电中心）

## Failure Modes
- 结构解析失败或位点识别不可信：应由上游 L0/L1 直接 FAIL，本技能不得继续推断。
- 条件缺失：必须在 requirements 中标记“条件依赖”，不得给出确定性结论。
- 位点类型误分：应回退检查 L1 规则与 evidence（SMARTS/规则编号）。

## Changelog
- 2025-12-24: initial version
