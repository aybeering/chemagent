# FC_06_sulfur_phosphorus_v1 — 硫/磷簇分析

## Triggers
- 分子中存在含硫或含磷官能团
- 需要分析 S/P 原子的类型和反应特性
- 需要为 PhysChem HOMO 分析提供 S/P 位点信息

## Inputs
- 官能团列表：fg_category = "sulfur" 或 "phosphorus" 的官能团
- 杂原子标签：来自 SD_04 的 S/P 原子信息
- 分子表示：SMILES / 结构描述

## Outputs
```yaml
sulfur_phosphorus_cluster:
  members:
    - fg_id: "<官能团 ID>"
      element: "S | P"
      functional_type: "thiol | thioether | disulfide | sulfoxide | sulfone | sulfonate | sulfate | thiocarbonyl | phosphine | phosphate | phosphonate | phosphonium"
      heteroatom_index: <int>
      oxidation_state: <int>           # 氧化态
      lone_pairs: <int>
      nucleophilicity: "high | moderate | low"
      oxidizability: "high | moderate | low"
      reducibility: "high | moderate | low"
      coordination_ability: "high | moderate | low"
      modifiers: ["aromatic", "conjugated"]
      notes: "<说明>"
  
  dominant_site: "<fg_id>"
  
  physchem_routing:
    homo_analysis: ["HOMO_02_lonepair_n_v1"]
    lumo_analysis: ["LUMO_02_pi_antibond_v1"]  # 若有 S=O/P=O
  
  cluster_summary: "<硫/磷簇摘要>"
```

## Rules

### 硫化合物类型与特性

| 类型 | 氧化态 | 亲核性 | 氧化性 | 说明 |
|------|--------|--------|--------|------|
| thiol (-SH) | -2 | 高 | 很高 | 易氧化为二硫化物 |
| thioether (R-S-R) | -2 | 中 | 高 | 可氧化为亚砜 |
| disulfide (R-S-S-R) | -1 | 低 | 中 | S-S 可被还原 |
| sulfoxide (R-S(O)-R) | 0 | 低 | 低 | 可继续氧化 |
| sulfone (R-SO₂-R) | +2 | 极低 | 极低 | 惰性 |
| sulfonate (-SO₃⁻) | +4 | 无 | 无 | 良好离去基 |
| thiocarbonyl (C=S) | -2 | - | 中 | π 系统 |

### 磷化合物类型与特性

| 类型 | 氧化态 | 亲核性 | 配位能力 | 说明 |
|------|--------|--------|---------|------|
| phosphine (R₃P) | -3 | 高 | 高 | 强还原性，配体 |
| phosphite (P(OR)₃) | +3 | 中 | 中 | 可被氧化 |
| phosphate (-PO₄) | +5 | 无 | 低 | 稳定阴离子 |
| phosphonate (-PO₃) | +5 | 无 | 低 | 稳定阴离子 |
| phosphonium (R₄P⁺) | - | 无 | 无 | 正离子 |

### 电化学相关性

| 类型 | 氧化 | 还原 | 电解液相关性 |
|------|------|------|------------|
| 硫醚 | 易 → 亚砜 | 难 | 可能氧化分解 |
| 亚砜 | 可 → 砜 | 可 | DMSO 溶剂 |
| 二硫化物 | 难 | 易 → 硫醇 | 聚硫化物 |
| 磷酸酯 | 难 | 难 | LiPF₆ 分解 |

### PhysChem 路由规则

| 类型 | HOMO 分析 | LUMO 分析 |
|------|----------|----------|
| 硫醇/硫醚 | HOMO_02 (n) | - |
| 亚砜/砜 | HOMO_02 (n) | LUMO_02 (S=O π*) |
| 磷化氢 | HOMO_02 (n) | - |
| 磷酸酯 | - | LUMO_02 (P=O π*) |

## Steps
1. **筛选 S/P 官能团**
   - 从 functional_groups 获取 sulfur/phosphorus 类

2. **确定氧化态**
   - 根据连接的氧原子数判断

3. **评估反应特性**
   - 亲核性、氧化性、配位能力

4. **确定主导位点**

5. **生成 PhysChem 路由**

## Examples

**Example 1: 二甲基硫醚**
```yaml
input:
  smiles: "CSC"
  functional_groups: [{ fg_id: "FG_1", fg_type: "thioether" }]

output:
  sulfur_phosphorus_cluster:
    members:
      - fg_id: "FG_1"
        element: "S"
        functional_type: "thioether"
        heteroatom_index: 1
        oxidation_state: -2
        lone_pairs: 2
        nucleophilicity: "moderate"
        oxidizability: "high"
        reducibility: "low"
        coordination_ability: "moderate"
        notes: "硫醚，易被氧化为亚砜"
    
    dominant_site: "FG_1"
    
    physchem_routing:
      homo_analysis: ["HOMO_02_lonepair_n_v1"]
    
    cluster_summary: "硫醚，S 孤对是主要 HOMO，易氧化"
```

**Example 2: 二甲基亚砜 (DMSO)**
```yaml
input:
  smiles: "CS(=O)C"
  functional_groups: [{ fg_id: "FG_1", fg_type: "sulfoxide" }]

output:
  sulfur_phosphorus_cluster:
    members:
      - fg_id: "FG_1"
        element: "S"
        functional_type: "sulfoxide"
        heteroatom_index: 1
        oxidation_state: 0
        lone_pairs: 1
        nucleophilicity: "low"
        oxidizability: "moderate"
        reducibility: "moderate"
        coordination_ability: "moderate"
        notes: "亚砜，常用溶剂，S=O 可参与配位"
    
    dominant_site: "FG_1"
    
    physchem_routing:
      homo_analysis: ["HOMO_02_lonepair_n_v1"]
      lumo_analysis: ["LUMO_02_pi_antibond_v1"]
    
    cluster_summary: "亚砜，S 孤对和 S=O π* 均可参与反应"
```

**Example 3: 甲磺酸**
```yaml
input:
  smiles: "CS(=O)(=O)O"
  functional_groups: [{ fg_id: "FG_1", fg_type: "sulfonic_acid" }]

output:
  sulfur_phosphorus_cluster:
    members:
      - fg_id: "FG_1"
        element: "S"
        functional_type: "sulfonate"
        heteroatom_index: 1
        oxidation_state: +4
        lone_pairs: 0
        nucleophilicity: "none"
        oxidizability: "none"
        reducibility: "low"
        coordination_ability: "low"
        notes: "磺酸，强酸，磺酸根是优秀离去基"
    
    dominant_site: "FG_1"
    
    physchem_routing:
      # 磺酸/磺酸酯主要作为离去基
    
    cluster_summary: "磺酸，S 已完全氧化，惰性"
```

**Example 4: 三苯基膦**
```yaml
input:
  smiles: "c1ccc(P(c2ccccc2)c3ccccc3)cc1"
  functional_groups: [{ fg_id: "FG_1", fg_type: "phosphine" }]

output:
  sulfur_phosphorus_cluster:
    members:
      - fg_id: "FG_1"
        element: "P"
        functional_type: "phosphine"
        heteroatom_index: 4
        oxidation_state: -3
        lone_pairs: 1
        nucleophilicity: "high"
        oxidizability: "high"
        reducibility: "low"
        coordination_ability: "very_high"
        modifiers: ["aromatic"]
        notes: "三芳基膦，优秀配体，可形成膦氧化物"
    
    dominant_site: "FG_1"
    
    physchem_routing:
      homo_analysis: ["HOMO_02_lonepair_n_v1"]
    
    cluster_summary: "膦配体，P 孤对是主要 HOMO，强还原性"
```

**Example 5: 磷酸三甲酯**
```yaml
input:
  smiles: "COP(=O)(OC)OC"
  functional_groups: [{ fg_id: "FG_1", fg_type: "phosphate_ester" }]

output:
  sulfur_phosphorus_cluster:
    members:
      - fg_id: "FG_1"
        element: "P"
        functional_type: "phosphate"
        heteroatom_index: 2
        oxidation_state: +5
        lone_pairs: 0
        nucleophilicity: "none"
        oxidizability: "none"
        reducibility: "low"
        coordination_ability: "low"
        notes: "磷酸酯，P 已完全氧化"
    
    dominant_site: "FG_1"
    
    physchem_routing:
      lumo_analysis: ["LUMO_02_pi_antibond_v1"]
    
    cluster_summary: "磷酸酯，P=O π* 可接受电子"
```

## Guardrails
- 硫醚在电解液中可能被氧化
- 二硫化物在还原条件下可断裂
- 膦类通常用作配体，而非电解液组分
- 磷酸酯（如 LiPF₆ 分解）需特别关注

## Confusable Cases
- 硫醚 vs 亚砜：氧化态不同
- 磷酸酯 vs 亚磷酸酯：氧化态不同
- 硫醇 vs 硫酚：连接基团不同

## Changelog
- 2025-12-24: 初始版本

