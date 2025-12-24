# SITE_NU_LONEPAIR_HET_v1 — 杂原子孤对亲核位点映射

| Field | Value |
|---|---|
| Skill ID | `SITE_NU_LONEPAIR_HET_v1` |
| Type | Prompt Skill (Site → Reaction Catalog) |
| Site Type | `NU_LONEPAIR_HET` |
| Site Kind | `ATOM` |
| Category | 亲核类（NU） |
| Schema | `SITE_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Depends On | L0 GroundTruth, L1 SiteMap |

## Purpose
针对中性杂原子孤对（胺/醇/硫醇/硫醚/膦等）亲核位点，输出常见反应族与触发/否决提示。

## Non-goals
- 不把弱亲核位点（如酰胺氮、磺酰胺氮等）强行当作强亲核；需依据 local_env 降权或标注不适用。
- 不替代 L2 的严格匹配与中心选择；只提供候选反应族。

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
        | `RXN_SN2_v1` | 亲核取代（SN2） | 对 E_SP3_C_LG 取代；中性亲核通常要求更好离去基/更强条件。 |
| `RXN_ACYLATION_v1` | 酰化 | 对酸氯/酸酐/活化酯等进行酰化，生成酰胺/酯/硫酯。 |
| `RXN_NUC_ADDITION_CARBONYL_v1` | 羰基加成 | 醇/胺对醛酮加成形成半缩醛/氨醇中间体等（后续由 L2 细化）。 |
| `RXN_IMINE_FORMATION_v1` | 亚胺/缩合 | 胺类与羰基缩合生成亚胺/肟/腙等（可拆分子类）。 |
| `RXN_TRANSESTERIFICATION_v1` | 酯交换/酰基转移 | 在催化/活化条件下发生交换或转移。 |
| `RXN_RING_OPENING_v1` | 张力环开环 | 对环氧/氮丙啶等张力环进行开环。 |
| `RXN_COORDINATION_v1` | 配位/路易斯酸相互作用 | 与金属/路易斯酸配位影响反应性（提示性）。 |
| `RXN_DEPROTONATION_v1` | 去质子化（前序） | 若该位点可去质子化，可先形成 NU_ANION。 |

## Priority Rules
- 芳胺、酰胺、磺酰胺等孤对离域位点：降低 RXN_SN2_v1 与 RXN_IMINE_FORMATION_v1 权重。
- 位阻较小且存在良好离去基：提高 RXN_SN2_v1。
- 若 local_env 显示为醇/胺且同时存在 E_CARBONYL_C：提高 RXN_NUC_ADDITION_CARBONYL_v1 与 RXN_IMINE_FORMATION_v1（胺优先）。

## Common Exclusions / Conflicts
- 强共轭/强吸电子基团导致孤对显著离域（典型：酰胺 N）：通常不作为有效亲核中心。

## Prompt Template
### Prompt Template

**System**
你是“反应位点→反应族映射（Prompt Skill）”专家。你只能使用输入中的 `ground_truth` 与 `site`（来自结构真值层 L0 与位点图谱层 L1），不得猜测结构、不得引入未提供的条件信息。若缺少关键条件，请在 `requirements` 中标注“条件依赖”。

**User**
给定如下 `site`（site_type=NU_LONEPAIR_HET）及其 `local_env` 与 `evidence`，请输出该位点最可能参与的反应族 `reaction_keys`（按优先级排序），并为每个反应族给出：
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
- SMILES: `CN`
- 位点提示: N 原子
- 期望反应族（示例）: `RXN_SN2_v1`, `RXN_ACYLATION_v1`, `RXN_IMINE_FORMATION_v1`
**Example 2**
- SMILES: `CO`
- 位点提示: O 原子
- 期望反应族（示例）: `RXN_SN2_v1`, `RXN_ACYLATION_v1`, `RXN_NUC_ADDITION_CARBONYL_v1`

## Confusable With
- NU_ANION（阴离子亲核）
- BASE_SITE（碱性位点）

## Failure Modes
- 结构解析失败或位点识别不可信：应由上游 L0/L1 直接 FAIL，本技能不得继续推断。
- 条件缺失：必须在 requirements 中标记“条件依赖”，不得给出确定性结论。
- 位点类型误分：应回退检查 L1 规则与 evidence（SMARTS/规则编号）。

## Changelog
- 2025-12-24: initial version
