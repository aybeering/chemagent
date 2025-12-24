# SITE_ACID_H_v1 — 酸性氢位点映射

| Field | Value |
|---|---|
| Skill ID | `SITE_ACID_H_v1` |
| Type | Prompt Skill (Site → Reaction Catalog) |
| Site Type | `ACID_H` |
| Site Kind | `ATOM` |
| Category | 酸碱相关 |
| Schema | `SITE_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Depends On | L0 GroundTruth, L1 SiteMap |

## Purpose
针对可被夺取的酸性氢（羧酸/酚/醇/α-羰基氢/端炔氢等抽象），输出以去质子化为前序的反应族候选。

## Non-goals
- 不直接给出 pKa 数值；仅基于 local_env 的稳定化证据输出相对倾向与可行反应族。

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
        | `RXN_DEPROTONATION_v1` | 去质子化 | 生成对应阴离子（后续反应前序）。 |
| `RXN_ENOLIZATION_v1` | 烯醇化/生成烯醇盐 | α-羰基位点等；与 BASE_SITE 联动。 |
| `RXN_ALKYLATION_AFTER_DEPROTONATION_v1` | 去质子化后烷基化 | 生成阴离子后对 E_SP3_C_LG 等进行烷基化。 |
| `RXN_CONDENSATION_v1` | 缩合（提示性） | 如 aldol/Claisen 等（需更细分 key）。 |
| `RXN_SALT_FORMATION_v1` | 成盐/酸碱平衡 | 结构层面提示。 |

## Priority Rules
- 若 local_env 显示共轭/邻近羰基/多 EWG 稳定负电：提高去质子化与后续碳负离子反应族权重。

## Common Exclusions / Conflicts
- （无）

## Prompt Template
### Prompt Template

**System**
你是“反应位点→反应族映射（Prompt Skill）”专家。你只能使用输入中的 `ground_truth` 与 `site`（来自结构真值层 L0 与位点图谱层 L1），不得猜测结构、不得引入未提供的条件信息。若缺少关键条件，请在 `requirements` 中标注“条件依赖”。

**User**
给定如下 `site`（site_type=ACID_H）及其 `local_env` 与 `evidence`，请输出该位点最可能参与的反应族 `reaction_keys`（按优先级排序），并为每个反应族给出：
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
- SMILES: `CC(=O)CH3`
- 位点提示: α-位 H
- 期望反应族（示例）: `RXN_ENOLIZATION_v1`, `RXN_DEPROTONATION_v1`
**Example 2**
- SMILES: `c1ccccc1O`
- 位点提示: 酚羟基 H
- 期望反应族（示例）: `RXN_DEPROTONATION_v1`, `RXN_SALT_FORMATION_v1`

## Confusable With
- BASE_SITE（碱性位点）

## Failure Modes
- 结构解析失败或位点识别不可信：应由上游 L0/L1 直接 FAIL，本技能不得继续推断。
- 条件缺失：必须在 requirements 中标记“条件依赖”，不得给出确定性结论。
- 位点类型误分：应回退检查 L1 规则与 evidence（SMARTS/规则编号）。

## Changelog
- 2025-12-24: initial version
