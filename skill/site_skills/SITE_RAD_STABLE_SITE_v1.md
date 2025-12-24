# SITE_RAD_STABLE_SITE_v1 — 自由基稳定中心映射

| Field | Value |
|---|---|
| Skill ID | `SITE_RAD_STABLE_SITE_v1` |
| Type | Prompt Skill (Site → Reaction Catalog) |
| Site Type | `RAD_STABLE_SITE` |
| Site Kind | `ATOM` |
| Category | 自由基/氧化还原 |
| Schema | `SITE_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Depends On | L0 GroundTruth, L1 SiteMap |

## Purpose
针对可能稳定自由基的中心（苄位/烯丙位/α-羰基等），输出自由基相关反应族候选，并强调条件依赖（光/引发剂/过氧化物）。

## Non-goals
- 不在缺少引发条件时断言自由基反应会发生；仅做结构可行性提示。

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
        | `RXN_RADICAL_HALOGENATION_v1` | 自由基卤化 | 苄/烯丙位 C–H 卤化等；条件依赖。 |
| `RXN_RADICAL_ADDITION_PI_v1` | 自由基加成到π体系 | 对双键/芳环等加成；条件依赖。 |
| `RXN_H_ABSTRACTION_v1` | 氢抽提（链反应步骤） | 提示性。 |
| `RXN_OXIDATION_RADICAL_PATHWAY_v1` | 自由基途径氧化 | 提示性。 |

## Priority Rules
- 若 local_env 显示苄位/烯丙位：提高 RXN_RADICAL_HALOGENATION_v1；若存在 π 体系：保留 RXN_RADICAL_ADDITION_PI_v1。

## Common Exclusions / Conflicts
- （无）

## Prompt Template
### Prompt Template

**System**
你是“反应位点→反应族映射（Prompt Skill）”专家。你只能使用输入中的 `ground_truth` 与 `site`（来自结构真值层 L0 与位点图谱层 L1），不得猜测结构、不得引入未提供的条件信息。若缺少关键条件，请在 `requirements` 中标注“条件依赖”。

**User**
给定如下 `site`（site_type=RAD_STABLE_SITE）及其 `local_env` 与 `evidence`，请输出该位点最可能参与的反应族 `reaction_keys`（按优先级排序），并为每个反应族给出：
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
- SMILES: `c1ccccc1CH3`
- 位点提示: 苄位 C
- 期望反应族（示例）: `RXN_RADICAL_HALOGENATION_v1`

## Confusable With
- E_BENZYLIC_C_LG（苄位亲电中心）

## Failure Modes
- 结构解析失败或位点识别不可信：应由上游 L0/L1 直接 FAIL，本技能不得继续推断。
- 条件缺失：必须在 requirements 中标记“条件依赖”，不得给出确定性结论。
- 位点类型误分：应回退检查 L1 规则与 evidence（SMARTS/规则编号）。

## Changelog
- 2025-12-24: initial version
