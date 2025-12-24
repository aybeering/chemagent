# SITE_E_ALLYLIC_C_LG_v1 — 烯丙位-离去基亲电中心映射

| Field | Value |
|---|---|
| Skill ID | `SITE_E_ALLYLIC_C_LG_v1` |
| Type | Prompt Skill (Site → Reaction Catalog) |
| Site Type | `E_ALLYLIC_C_LG` |
| Site Kind | `ATOM` |
| Category | 亲电类（E+） |
| Schema | `SITE_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Depends On | L0 GroundTruth, L1 SiteMap |

## Purpose
针对烯丙位带离去基中心，输出 SN2 / SN2′ / SN1 / 消除等反应族候选，并提示区域选择性与条件依赖。

## Non-goals
- 不在缺少上下文时给出唯一区域选择性结论；应输出 SN2 与 SN2′ 并行候选。

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
        | `RXN_SN2_v1` | 烯丙位 SN2 | 常规取代，区域由亲电中心决定。 |
| `RXN_SN2_PRIME_v1` | SN2′（烯丙位重排取代） | 对共轭体系发生取代伴随双键迁移。 |
| `RXN_SN1_v1` | SN1 | 烯丙正离子稳定；条件依赖。 |
| `RXN_E2_v1` | E2 | 强碱条件下消除。 |
| `RXN_E1_v1` | E1 | 与 SN1 竞争。 |
| `RXN_ALLYLIC_OXIDATION_v1` | 烯丙位氧化 | 结构可行性提示。 |

## Priority Rules
- 若 local_env 显示有共轭 π 体系且离去基位置允许：保留 RXN_SN2_PRIME_v1 并给出区域选择性提示。
- 若位阻较大或正离子稳定性高：提高 RXN_SN1_v1 / RXN_E1_v1。

## Common Exclusions / Conflicts
- （无）

## Prompt Template
### Prompt Template

**System**
你是“反应位点→反应族映射（Prompt Skill）”专家。你只能使用输入中的 `ground_truth` 与 `site`（来自结构真值层 L0 与位点图谱层 L1），不得猜测结构、不得引入未提供的条件信息。若缺少关键条件，请在 `requirements` 中标注“条件依赖”。

**User**
给定如下 `site`（site_type=E_ALLYLIC_C_LG）及其 `local_env` 与 `evidence`，请输出该位点最可能参与的反应族 `reaction_keys`（按优先级排序），并为每个反应族给出：
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
- SMILES: `C=CCBr`
- 位点提示: 烯丙位 C
- 期望反应族（示例）: `RXN_SN2_v1`, `RXN_SN2_PRIME_v1`, `RXN_E2_v1`

## Confusable With
- NU_PI（π体系位点）
- E_SP3_C_LG（一般 sp3）

## Failure Modes
- 结构解析失败或位点识别不可信：应由上游 L0/L1 直接 FAIL，本技能不得继续推断。
- 条件缺失：必须在 requirements 中标记“条件依赖”，不得给出确定性结论。
- 位点类型误分：应回退检查 L1 规则与 evidence（SMARTS/规则编号）。

## Changelog
- 2025-12-24: initial version
