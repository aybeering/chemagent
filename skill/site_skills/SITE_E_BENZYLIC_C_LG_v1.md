# SITE_E_BENZYLIC_C_LG_v1 — 苄位-离去基亲电中心映射

| Field | Value |
|---|---|
| Skill ID | `SITE_E_BENZYLIC_C_LG_v1` |
| Type | Prompt Skill (Site → Reaction Catalog) |
| Site Type | `E_BENZYLIC_C_LG` |
| Site Kind | `ATOM` |
| Category | 亲电类（E+） |
| Schema | `SITE_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Depends On | L0 GroundTruth, L1 SiteMap |

## Purpose
针对苄位带离去基的碳中心（正离子/自由基稳定），输出取代/消除/自由基路径等反应族候选。

## Non-goals
- 不在缺少条件时断言自由基/金属催化一定发生；需标注条件依赖。

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
        | `RXN_SN1_v1` | 亲核取代（SN1） | 苄正离子稳定，SN1 相对更可行。 |
| `RXN_SN2_v1` | 亲核取代（SN2） | 位阻允许时仍可能发生。 |
| `RXN_E1_v1` | β-消除（E1） | 与 SN1 竞争。 |
| `RXN_E2_v1` | β-消除（E2） | 强碱条件下可行。 |
| `RXN_RADICAL_SUBSTITUTION_BENZYLIC_v1` | 苄位自由基取代/卤化 | 条件依赖（光/引发剂）。 |
| `RXN_BENZYLIC_OXIDATION_v1` | 苄位氧化 | 结构可行性提示。 |

## Priority Rules
- 相较普通 E_SP3_C_LG：提高 RXN_SN1_v1 与 RXN_E1_v1 权重。
- 若 local_env 显示位阻低且强亲核存在：同时保留 RXN_SN2_v1。

## Common Exclusions / Conflicts
- 若该位点实际为芳基卤化物（卤直接连芳环 sp2 C），不应归类为苄位。需回到 L1 位点识别纠正。

## Prompt Template
### Prompt Template

**System**
你是“反应位点→反应族映射（Prompt Skill）”专家。你只能使用输入中的 `ground_truth` 与 `site`（来自结构真值层 L0 与位点图谱层 L1），不得猜测结构、不得引入未提供的条件信息。若缺少关键条件，请在 `requirements` 中标注“条件依赖”。

**User**
给定如下 `site`（site_type=E_BENZYLIC_C_LG）及其 `local_env` 与 `evidence`，请输出该位点最可能参与的反应族 `reaction_keys`（按优先级排序），并为每个反应族给出：
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
- SMILES: `c1ccccc1CBr`
- 位点提示: 苄位 C
- 期望反应族（示例）: `RXN_SN1_v1`, `RXN_SN2_v1`, `RXN_E1_v1`

## Confusable With
- E_SP3_C_LG（一般 sp3）
- LG_HALIDE（离去基本身）

## Failure Modes
- 结构解析失败或位点识别不可信：应由上游 L0/L1 直接 FAIL，本技能不得继续推断。
- 条件缺失：必须在 requirements 中标记“条件依赖”，不得给出确定性结论。
- 位点类型误分：应回退检查 L1 规则与 evidence（SMARTS/规则编号）。

## Changelog
- 2025-12-24: initial version
