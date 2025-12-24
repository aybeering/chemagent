# SITE_LG_SULFONATE_v1 — 磺酸酯离去基位点映射

| Field | Value |
|---|---|
| Skill ID | `SITE_LG_SULFONATE_v1` |
| Type | Prompt Skill (Site → Reaction Catalog) |
| Site Type | `LG_SULFONATE` |
| Site Kind | `ATOM` |
| Category | 离去基（LG） |
| Schema | `SITE_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Depends On | L0 GroundTruth, L1 SiteMap |

## Purpose
针对磺酸酯类离去基（OTs/OMs/OTf 等抽象），输出其作为优良离去基参与取代/消除等反应族候选。

## Non-goals
- 不在缺少连接碳信息时判断具体机理；需联动 E_SP3_C_LG/E_ALLYLIC_C_LG 等位点。

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
        | `RXN_SN2_v1` | SN2 | 作为优良离去基提升 SN2 可行性。 |
| `RXN_E2_v1` | E2 | 强碱条件下。 |
| `RXN_SN1_v1` | SN1 | 若底物可稳定正离子。 |
| `RXN_E1_v1` | E1 | 与 SN1 竞争。 |
| `RXN_SOLVOLYSIS_v1` | 溶剂解 | 条件依赖。 |

## Priority Rules
- 相较卤素：通常更好的离去基，因此在同等位阻下提高 SN2/E2 倾向。

## Common Exclusions / Conflicts
- （无）

## Prompt Template
### Prompt Template

**System**
你是“反应位点→反应族映射（Prompt Skill）”专家。你只能使用输入中的 `ground_truth` 与 `site`（来自结构真值层 L0 与位点图谱层 L1），不得猜测结构、不得引入未提供的条件信息。若缺少关键条件，请在 `requirements` 中标注“条件依赖”。

**User**
给定如下 `site`（site_type=LG_SULFONATE）及其 `local_env` 与 `evidence`，请输出该位点最可能参与的反应族 `reaction_keys`（按优先级排序），并为每个反应族给出：
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
- SMILES: `CCOS(=O)(=O)C`
- 位点提示: O-SO2R 片段中离去端 O
- 期望反应族（示例）: `RXN_SN2_v1`, `RXN_E2_v1`

## Confusable With
- LG_HALIDE（卤素离去基）

## Failure Modes
- 结构解析失败或位点识别不可信：应由上游 L0/L1 直接 FAIL，本技能不得继续推断。
- 条件缺失：必须在 requirements 中标记“条件依赖”，不得给出确定性结论。
- 位点类型误分：应回退检查 L1 规则与 evidence（SMARTS/规则编号）。

## Changelog
- 2025-12-24: initial version
