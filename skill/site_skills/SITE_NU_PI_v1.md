# SITE_NU_PI_v1 — π体系亲核位点映射

| Field | Value |
|---|---|
| Skill ID | `SITE_NU_PI_v1` |
| Type | Prompt Skill (Site → Reaction Catalog) |
| Site Type | `NU_PI` |
| Site Kind | `BOND` |
| Category | 亲核类（NU） |
| Schema | `SITE_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Depends On | L0 GroundTruth, L1 SiteMap |

## Purpose
针对 π 体系（芳环/烯烃/烯醇相关）可作为电子丰富位点参与亲电反应的情形，输出常见反应族与条件依赖提示。

## Non-goals
- 不在缺少条件信息时武断给出具体取代定位；仅列出可能的反应族与影响因素（活化/去活化、取代效应等）。

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
        | `RXN_EAS_v1` | 芳香亲电取代（EAS） | 芳环在合适亲电试剂/酸性体系下发生硝化/卤化/磺化/F-C 等（可拆分子类）。 |
| `RXN_ELECTROPHILIC_ADDITION_ALKENE_v1` | 烯烃亲电加成 | HX、卤化、卤代醇化等加成；马氏/反马氏受条件影响。 |
| `RXN_HALOGENATION_PI_v1` | π体系卤化 | 烯烃或芳环卤化（芳环通常归 EAS 分支）。 |
| `RXN_OXIDATION_PI_v1` | π体系氧化 | 如环氧化、二羟化等（条件依赖）。 |
| `RXN_RADICAL_ADDITION_PI_v1` | 自由基加成到π体系 | 在引发条件下自由基对双键/芳环加成（提示性）。 |

## Priority Rules
- 若 local_env 显示芳香且有给电子取代：提高 RXN_EAS_v1；若多强 EWG：降低 RXN_EAS_v1，可能转向 RXN_SNA_R_v1（由离去基与 EWG 决定）。
- 若为非芳香 C=C：优先 RXN_ELECTROPHILIC_ADDITION_ALKENE_v1；若 context 缺失，标注“条件依赖”。

## Common Exclusions / Conflicts
- 强去活芳环（多 EWG）通常不易 EAS；需在输出中降权并说明。

## Prompt Template
### Prompt Template

**System**
你是“反应位点→反应族映射（Prompt Skill）”专家。你只能使用输入中的 `ground_truth` 与 `site`（来自结构真值层 L0 与位点图谱层 L1），不得猜测结构、不得引入未提供的条件信息。若缺少关键条件，请在 `requirements` 中标注“条件依赖”。

**User**
给定如下 `site`（site_type=NU_PI）及其 `local_env` 与 `evidence`，请输出该位点最可能参与的反应族 `reaction_keys`（按优先级排序），并为每个反应族给出：
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
- SMILES: `c1ccccc1`
- 位点提示: 芳环 π 键
- 期望反应族（示例）: `RXN_EAS_v1`
**Example 2**
- SMILES: `C=CC`
- 位点提示: 双键
- 期望反应族（示例）: `RXN_ELECTROPHILIC_ADDITION_ALKENE_v1`, `RXN_HALOGENATION_PI_v1`

## Confusable With
- E_ALLYLIC_C_LG（烯丙位离去基中心）

## Failure Modes
- 结构解析失败或位点识别不可信：应由上游 L0/L1 直接 FAIL，本技能不得继续推断。
- 条件缺失：必须在 requirements 中标记“条件依赖”，不得给出确定性结论。
- 位点类型误分：应回退检查 L1 规则与 evidence（SMARTS/规则编号）。

## Changelog
- 2025-12-24: initial version
