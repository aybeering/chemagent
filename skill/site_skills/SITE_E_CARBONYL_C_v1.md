# SITE_E_CARBONYL_C_v1 — 羰基碳亲电中心映射

| Field | Value |
|---|---|
| Skill ID | `SITE_E_CARBONYL_C_v1` |
| Type | Prompt Skill (Site → Reaction Catalog) |
| Site Type | `E_CARBONYL_C` |
| Site Kind | `ATOM` |
| Category | 亲电类（E+） |
| Schema | `SITE_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Depends On | L0 GroundTruth, L1 SiteMap |

## Purpose
针对羰基碳（醛/酮/酰基衍生物等）作为亲电中心，输出其可能发生的加成、取代、还原、缩合等反应族。

## Non-goals
- 不替代官能团精确定类（醛/酮/酯/酰胺/酸氯等）——必须基于 local_env/evidence 给出分支或标注不确定。

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
        | `RXN_NUC_ADDITION_CARBONYL_v1` | 羰基亲核加成 | 醛/酮典型；硬/软亲核差异由 L2 决定。 |
| `RXN_ACYL_SUBSTITUTION_v1` | 酰基取代 | 酸衍生物（酸氯/酸酐/活化酯等）发生亲核取代。 |
| `RXN_IMINE_FORMATION_v1` | 缩合成亚胺 | 与胺缩合生成亚胺/肟/腙（分支可扩展）。 |
| `RXN_REDUCTION_CARBONYL_v1` | 羰基还原 | 氢化物/催化氢化等；结构层面标记“可还原位点”。 |
| `RXN_ENOLIZATION_v1` | 烯醇化相关 | α-位去质子化/烯醇化（需 ACID_H/BASE_SITE 联动）。 |

## Priority Rules
- 若 evidence/规则表明是酸氯/酸酐：优先 RXN_ACYL_SUBSTITUTION_v1；若为醛/酮：优先 RXN_NUC_ADDITION_CARBONYL_v1。
- 若 local_env 表明为酰胺羰基：降低一般加成反应权重，并在 notes 中说明（共振降低亲电性）。

## Common Exclusions / Conflicts
- 显著共轭/强电子给体共振降低羰基亲电性时，一般亲核加成可能需要强条件（提示性）。

## Prompt Template
### Prompt Template

**System**
你是“反应位点→反应族映射（Prompt Skill）”专家。你只能使用输入中的 `ground_truth` 与 `site`（来自结构真值层 L0 与位点图谱层 L1），不得猜测结构、不得引入未提供的条件信息。若缺少关键条件，请在 `requirements` 中标注“条件依赖”。

**User**
给定如下 `site`（site_type=E_CARBONYL_C）及其 `local_env` 与 `evidence`，请输出该位点最可能参与的反应族 `reaction_keys`（按优先级排序），并为每个反应族给出：
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
- 期望反应族（示例）: `RXN_NUC_ADDITION_CARBONYL_v1`, `RXN_REDUCTION_CARBONYL_v1`
**Example 2**
- SMILES: `CC(=O)Cl`
- 位点提示: 酰氯羰基 C
- 期望反应族（示例）: `RXN_ACYL_SUBSTITUTION_v1`

## Confusable With
- E_SP3_C_LG（sp3 亲电 + 离去基）

## Failure Modes
- 结构解析失败或位点识别不可信：应由上游 L0/L1 直接 FAIL，本技能不得继续推断。
- 条件缺失：必须在 requirements 中标记“条件依赖”，不得给出确定性结论。
- 位点类型误分：应回退检查 L1 规则与 evidence（SMARTS/规则编号）。

## Changelog
- 2025-12-24: initial version
