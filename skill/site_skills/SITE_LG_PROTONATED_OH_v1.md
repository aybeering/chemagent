# SITE_LG_PROTONATED_OH_v1 — 质子化羟基（水离去）位点映射

| Field | Value |
|---|---|
| Skill ID | `SITE_LG_PROTONATED_OH_v1` |
| Type | Prompt Skill (Site → Reaction Catalog) |
| Site Type | `LG_PROTONATED_OH` |
| Site Kind | `ATOM` |
| Category | 离去基（LG） |
| Schema | `SITE_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Depends On | L0 GroundTruth, L1 SiteMap |

## Purpose
针对在酸性条件下可转化为水离去的羟基位点，输出酸催化取代/脱水等反应族候选，并强调条件依赖。

## Non-goals
- 不得在缺少酸性条件信息时断言该位点已质子化；必须在 requirements 标注“需要酸”。

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
        | `RXN_SN1_v1` | 酸催化取代（SN1 倾向） | 二级/三级醇在酸下形成正离子后被亲核进攻。 |
| `RXN_E1_v1` | 酸催化脱水（E1） | 生成烯烃；与 SN1 竞争。 |
| `RXN_SUBSTITUTION_ALCOHOL_v1` | 醇的取代（泛化） | 酸下与卤化物/亲核体取代（SN1/SN2 分支）。 |
| `RXN_ACID_CATALYZED_REARRANGEMENT_v1` | 碳正离子重排 | 条件依赖，提示性。 |

## Priority Rules
- 若连接碳为三级/苄位/烯丙位：提高 SN1/E1 倾向；一级醇多数情况下需要转化为更好离去基（提示）。

## Common Exclusions / Conflicts
- （无）

## Prompt Template
### Prompt Template

**System**
你是“反应位点→反应族映射（Prompt Skill）”专家。你只能使用输入中的 `ground_truth` 与 `site`（来自结构真值层 L0 与位点图谱层 L1），不得猜测结构、不得引入未提供的条件信息。若缺少关键条件，请在 `requirements` 中标注“条件依赖”。

**User**
给定如下 `site`（site_type=LG_PROTONATED_OH）及其 `local_env` 与 `evidence`，请输出该位点最可能参与的反应族 `reaction_keys`（按优先级排序），并为每个反应族给出：
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
- SMILES: `CC(O)C`
- 位点提示: O 原子（酸下可变成离去）
- 期望反应族（示例）: `RXN_SN1_v1`, `RXN_E1_v1`

## Confusable With
- LG_SULFONATE（已活化的 O-离去基）

## Failure Modes
- 结构解析失败或位点识别不可信：应由上游 L0/L1 直接 FAIL，本技能不得继续推断。
- 条件缺失：必须在 requirements 中标记“条件依赖”，不得给出确定性结论。
- 位点类型误分：应回退检查 L1 规则与 evidence（SMARTS/规则编号）。

## Changelog
- 2025-12-24: initial version
