# SITE_BASE_SITE_v1 — 碱性位点映射

| Field | Value |
|---|---|
| Skill ID | `SITE_BASE_SITE_v1` |
| Type | Prompt Skill (Site → Reaction Catalog) |
| Site Type | `BASE_SITE` |
| Site Kind | `ATOM` |
| Category | 酸碱相关 |
| Schema | `SITE_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Depends On | L0 GroundTruth, L1 SiteMap |

## Purpose
针对可受质子化/可作为一般碱的位点（常与杂原子孤对重叠），输出其在酸碱与促进反应中的角色与反应族候选。

## Non-goals
- 不把所有碱性位点都当作强亲核；亲核性需由 NU_* 位点技能表达。

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
        | `RXN_PROTONATION_v1` | 质子化 | 影响反应性/离去基形成/活化。 |
| `RXN_DEPROTONATION_v1` | 作为碱夺氢 | 夺取 ACID_H 触发消除/烯醇化等。 |
| `RXN_E2_v1` | E2（作为碱参与） | 与 E_SP3_C_LG 和 β-H 联动。 |
| `RXN_GENERAL_BASE_CATALYSIS_v1` | 一般碱催化（提示性） | 条件依赖。 |

## Priority Rules
- 若 local_env 显示强碱性且存在 E_SP3_C_LG 与 β-H：提高 RXN_E2_v1。

## Common Exclusions / Conflicts
- （无）

## Prompt Template
### Prompt Template

**System**
你是“反应位点→反应族映射（Prompt Skill）”专家。你只能使用输入中的 `ground_truth` 与 `site`（来自结构真值层 L0 与位点图谱层 L1），不得猜测结构、不得引入未提供的条件信息。若缺少关键条件，请在 `requirements` 中标注“条件依赖”。

**User**
给定如下 `site`（site_type=BASE_SITE）及其 `local_env` 与 `evidence`，请输出该位点最可能参与的反应族 `reaction_keys`（按优先级排序），并为每个反应族给出：
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
- SMILES: `CN(C)C`
- 位点提示: 胺 N
- 期望反应族（示例）: `RXN_PROTONATION_v1`, `RXN_DEPROTONATION_v1`

## Confusable With
- NU_LONEPAIR_HET（亲核）
- NU_ANION（更强亲核/碱）

## Failure Modes
- 结构解析失败或位点识别不可信：应由上游 L0/L1 直接 FAIL，本技能不得继续推断。
- 条件缺失：必须在 requirements 中标记“条件依赖”，不得给出确定性结论。
- 位点类型误分：应回退检查 L1 规则与 evidence（SMARTS/规则编号）。

## Changelog
- 2025-12-24: initial version
