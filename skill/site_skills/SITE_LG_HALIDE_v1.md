# SITE_LG_HALIDE_v1 — 卤素离去基位点映射

| Field | Value |
|---|---|
| Skill ID | `SITE_LG_HALIDE_v1` |
| Type | Prompt Skill (Site → Reaction Catalog) |
| Site Type | `LG_HALIDE` |
| Site Kind | `ATOM` |
| Category | 离去基（LG） |
| Schema | `SITE_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Depends On | L0 GroundTruth, L1 SiteMap |

## Purpose
针对卤素离去基（Cl/Br/I 等），输出其作为离去基/偶联位点相关的反应族候选，并提示 sp3 vs sp2 连接差异。

## Non-goals
- 不将所有卤代物都视为可 SN2；必须依据连接碳的杂化与局部环境提示。

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
        | `RXN_SN2_v1` | 卤代烷 SN2 | sp3 碳连接、位阻允许时。 |
| `RXN_SN1_v1` | 卤代烷 SN1 | 稳定正离子条件下。 |
| `RXN_E2_v1` | 卤代烷 E2 | 强碱/β-H 可用。 |
| `RXN_E1_v1` | 卤代烷 E1 | 与 SN1 竞争。 |
| `RXN_SNA_R_v1` | 芳基卤化物 SNAr | 需强 EWG 活化与合适离去基。 |
| `RXN_CROSS_COUPLING_CSP2_v1` | 交叉偶联（sp2-X） | 芳基/烯基卤化物偶联，条件依赖。 |
| `RXN_METAL_HALOGEN_EXCHANGE_v1` | 卤-金属交换 | 条件依赖。 |

## Priority Rules
- 若 halide 连接 sp3 C：提升 RXN_SN2_v1/RXN_E2_v1；若连接 sp2 C：提升 RXN_SNA_R_v1 与 RXN_CROSS_COUPLING_CSP2_v1，并在 notes 中说明 SN2 通常不适用。

## Common Exclusions / Conflicts
- （无）

## Prompt Template
### Prompt Template

**System**
你是“反应位点→反应族映射（Prompt Skill）”专家。你只能使用输入中的 `ground_truth` 与 `site`（来自结构真值层 L0 与位点图谱层 L1），不得猜测结构、不得引入未提供的条件信息。若缺少关键条件，请在 `requirements` 中标注“条件依赖”。

**User**
给定如下 `site`（site_type=LG_HALIDE）及其 `local_env` 与 `evidence`，请输出该位点最可能参与的反应族 `reaction_keys`（按优先级排序），并为每个反应族给出：
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
- 位点提示: Br 原子
- 期望反应族（示例）: `RXN_SN2_v1`, `RXN_E2_v1`
**Example 2**
- SMILES: `c1ccccc1Br`
- 位点提示: Br 原子
- 期望反应族（示例）: `RXN_SNA_R_v1`, `RXN_CROSS_COUPLING_CSP2_v1`

## Confusable With
- E_SP3_C_LG（亲电中心）

## Failure Modes
- 结构解析失败或位点识别不可信：应由上游 L0/L1 直接 FAIL，本技能不得继续推断。
- 条件缺失：必须在 requirements 中标记“条件依赖”，不得给出确定性结论。
- 位点类型误分：应回退检查 L1 规则与 evidence（SMARTS/规则编号）。

## Changelog
- 2025-12-24: initial version
