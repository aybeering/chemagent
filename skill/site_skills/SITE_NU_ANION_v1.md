# SITE_NU_ANION_v1 — 阴离子亲核位点映射

| Field | Value |
|---|---|
| Skill ID | `SITE_NU_ANION_v1` |
| Type | Prompt Skill (Site → Reaction Catalog) |
| Site Type | `NU_ANION` |
| Site Kind | `ATOM` |
| Category | 亲核类（NU） |
| Schema | `SITE_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Depends On | L0 GroundTruth, L1 SiteMap |

## Purpose
针对阴离子/强亲核位点（如 RO⁻、RS⁻、NR₂⁻、稳定碳负离子等），输出该位点常参与的反应族（reaction keys），并给出最小触发条件、常见否决条件与竞争路径提示。

## Non-goals
- 不进行分子结构解析或纠错；结构真值必须来自 L0。
- 不直接判定“反应一定发生”；仅输出该位点可触发的反应族与条件提示，供 L2 反应匹配技能严格判定。
- 不推断溶剂/温度/催化剂等未提供条件；缺失条件时需标注“条件依赖”。

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
        | `RXN_SN2_v1` | 亲核取代（SN2） | 对 E_SP3_C_LG 亲电中心进行背面进攻取代；常见于一级/二级卤代烷、磺酸酯等。 |
| `RXN_E2_v1` | β-消除（E2） | 作为强碱夺取 β-H，发生消除；常与 SN2 竞争。 |
| `RXN_ACYL_SUBSTITUTION_v1` | 酰基取代 | 对酸氯/酸酐/活化酯等酰基衍生物进行取代。 |
| `RXN_NUC_ADDITION_CARBONYL_v1` | 羰基亲核加成 | 对醛/酮羰基碳加成；某些软/硬亲核差异需要在 L2 细化。 |
| `RXN_MICHAEL_ADDITION_v1` | 共轭加成（Michael） | 对 α,β-不饱和羰基等共轭体系进行 1,4-加成；软亲核位点更常见。 |
| `RXN_EPOXIDE_OPENING_v1` | 环氧开环 | 对环氧等张力环进行亲核开环；区域选择性/条件依赖。 |
| `RXN_SNA_R_v1` | 亲核芳香取代（SNAr） | 对带强 EWG 且具有离去基的芳环进行取代。 |
| `RXN_DEPROTONATION_v1` | 夺氢/去质子化 | 作为碱夺取 ACID_H，形成新的阴离子亲核位点或驱动后续反应。 |

## Priority Rules
- 若 local_env 显示该阴离子位点靠近强吸电子基团或共轭稳定（稳定碳负离子/硫负离子），提高 RXN_MICHAEL_ADDITION_v1 权重。
- 若存在可匹配的 E_SP3_C_LG 且亲电中心位阻低，优先 RXN_SN2_v1；若 β-H 可用且位点碱性强，提高 RXN_E2_v1。
- 若存在 E_CARBONYL_C 且为酰基衍生物（可离去基），提高 RXN_ACYL_SUBSTITUTION_v1；若为醛/酮，提高 RXN_NUC_ADDITION_CARBONYL_v1。

## Common Exclusions / Conflicts
- 当亲电中心为 sp2（芳基/烯基）且无 SNAr 活化条件时，SN2 通常不适用。
- 当亲电中心为三级碳或位阻极大时，SN2 明显受阻；更可能走 SN1/E2（由 L2 决定）。

## Prompt Template
### Prompt Template

**System**
你是“反应位点→反应族映射（Prompt Skill）”专家。你只能使用输入中的 `ground_truth` 与 `site`（来自结构真值层 L0 与位点图谱层 L1），不得猜测结构、不得引入未提供的条件信息。若缺少关键条件，请在 `requirements` 中标注“条件依赖”。

**User**
给定如下 `site`（site_type=NU_ANION）及其 `local_env` 与 `evidence`，请输出该位点最可能参与的反应族 `reaction_keys`（按优先级排序），并为每个反应族给出：
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
- SMILES: `[O-]CC`
- 位点提示: O 原子
- 期望反应族（示例）: `RXN_SN2_v1`, `RXN_ACYL_SUBSTITUTION_v1`, `RXN_DEPROTONATION_v1`
**Example 2**
- SMILES: `[S-]C`
- 位点提示: S 原子
- 期望反应族（示例）: `RXN_SN2_v1`, `RXN_MICHAEL_ADDITION_v1`

## Confusable With
- NU_LONEPAIR_HET（中性孤对亲核）
- BASE_SITE（碱性位点）

## Failure Modes
- 结构解析失败或位点识别不可信：应由上游 L0/L1 直接 FAIL，本技能不得继续推断。
- 条件缺失：必须在 requirements 中标记“条件依赖”，不得给出确定性结论。
- 位点类型误分：应回退检查 L1 规则与 evidence（SMARTS/规则编号）。

## Changelog
- 2025-12-24: initial version
