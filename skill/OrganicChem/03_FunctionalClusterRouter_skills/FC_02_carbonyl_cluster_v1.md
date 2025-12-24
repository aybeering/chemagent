# FC_02_carbonyl_cluster_v1 — 羰基簇分析

## Triggers
- 分子中存在羰基类官能团
- 需要分析羰基的类型和反应活性
- 需要为 PhysChem LUMO 分析提供羰基信息

## Inputs
- 官能团列表：fg_category = "carbonyl" 的官能团
- 分子表示：SMILES / 结构描述

## Outputs
```yaml
carbonyl_cluster:
  members:
    - fg_id: "<官能团 ID>"
      carbonyl_type: "aldehyde | ketone | carboxylic_acid | ester | lactone | amide | lactam | anhydride | acyl_halide | carbonate | cyclic_carbonate | imide"
      center_atom: <int>               # 羰基碳索引
      carbonyl_oxygen: <int>           # 羰基氧索引
      electrophilicity: "high | moderate | low"
      reducibility: "high | moderate | low"
      leaving_group: "<离去基团，若有>"
      modifiers: ["EWG_adjacent", "EDG_adjacent", "conjugated", "strained"]
      notes: "<说明>"
  
  dominant_carbonyl: "<fg_id>"         # 最活泼的羰基
  
  physchem_routing:
    primary: "LUMO_02_pi_antibond_v1"
    secondary: ["HOMO_02_lonepair_n_v1"]
    electronic_effect: "ELEC_03_M_pi_v1"  # 若有共轭取代基
  
  cluster_summary: "<羰基簇摘要>"
```

## Rules

### 羰基类型与活性

| 羰基类型 | 亲电性 | 还原性 | 说明 |
|----------|--------|--------|------|
| acyl_halide | 极高 | 高 | 酰卤，优秀离去基 |
| anhydride | 很高 | 高 | 酸酐 |
| aldehyde | 高 | 高 | 醛，无空间位阻 |
| ketone | 中 | 中 | 酮 |
| ester | 中-低 | 中 | 酯，氧共享孤对 |
| lactone | 中 | 中-高 | 内酯，有张力时更活泼 |
| cyclic_carbonate | 中 | 中-高 | 环状碳酸酯 |
| carbonate | 低 | 中 | 链状碳酸酯 |
| amide | 低 | 低 | 酰胺，氮共享孤对 |
| lactam | 低-中 | 低-中 | 内酰胺，有张力时更活泼 |
| imide | 中 | 中 | 亚胺 |
| carboxylic_acid | 低 | 低 | 羧酸（质子化时更活泼） |

### 活性调制因素

| 因素 | 对亲电性的影响 | 说明 |
|------|---------------|------|
| α-EWG | ↑ 增强 | 如 CF₃ 相邻 |
| α-EDG | ↓ 降低 | 如烷基取代 |
| 共轭 | ↓ 略降 | 与芳环共轭 |
| 环张力 | ↑ 增强 | 小环内酯/内酰胺 |

### PhysChem 路由规则

| 羰基类型 | 主要模块 | 次要模块 |
|----------|---------|---------|
| 所有羰基 | LUMO_02 (π*) | HOMO_02 (n) |
| 与芳环共轭 | ELEC_03 (M效应) | - |
| α-卤代羰基 | ELEC_02 (I效应) | LUMO_03 (σ*) |
| 环状 | LUMO_04 (环张力) | - |

## Steps
1. **筛选羰基官能团**
   - 从 functional_groups 获取 carbonyl 类

2. **分类羰基类型**
   - 细分为醛/酮/酯/酰胺等

3. **评估活性**
   - 综合类型和调制因素

4. **确定主导羰基**
   - 活性最高的羰基

5. **生成 PhysChem 路由**

## Examples

**Example 1: 乙醛**
```yaml
input:
  smiles: "CC=O"
  functional_groups: [{ fg_id: "FG_1", fg_type: "aldehyde" }]

output:
  carbonyl_cluster:
    members:
      - fg_id: "FG_1"
        carbonyl_type: "aldehyde"
        center_atom: 1
        carbonyl_oxygen: 2
        electrophilicity: "high"
        reducibility: "high"
        notes: "简单醛，高亲电性"
    
    dominant_carbonyl: "FG_1"
    
    physchem_routing:
      primary: "LUMO_02_pi_antibond_v1"
      secondary: ["HOMO_02_lonepair_n_v1"]
    
    cluster_summary: "单一醛基，典型亲电中心"
```

**Example 2: N,N-二甲基甲酰胺 (DMF)**
```yaml
input:
  smiles: "CN(C)C=O"
  functional_groups: [{ fg_id: "FG_1", fg_type: "amide" }]

output:
  carbonyl_cluster:
    members:
      - fg_id: "FG_1"
        carbonyl_type: "amide"
        center_atom: 3
        carbonyl_oxygen: 4
        electrophilicity: "low"
        reducibility: "low"
        modifiers: ["N_conjugation"]
        notes: "酰胺，N 孤对与羰基共轭降低亲电性"
    
    dominant_carbonyl: "FG_1"
    
    physchem_routing:
      primary: "LUMO_02_pi_antibond_v1"
      secondary: ["HOMO_02_lonepair_n_v1"]
      electronic_effect: "ELEC_03_M_pi_v1"
    
    cluster_summary: "叔酰胺，羰基活性低，氮孤对共轭"
```

**Example 3: 乙酰氯**
```yaml
input:
  smiles: "CC(=O)Cl"
  functional_groups: [{ fg_id: "FG_1", fg_type: "acyl_halide" }]

output:
  carbonyl_cluster:
    members:
      - fg_id: "FG_1"
        carbonyl_type: "acyl_halide"
        center_atom: 1
        carbonyl_oxygen: 2
        electrophilicity: "high"
        reducibility: "high"
        leaving_group: "Cl"
        notes: "酰氯，极强亲电性"
    
    dominant_carbonyl: "FG_1"
    
    physchem_routing:
      primary: "LUMO_02_pi_antibond_v1"
    
    cluster_summary: "酰卤，极活泼羰基衍生物"
```

**Example 4: 碳酸乙烯酯 (EC)**
```yaml
input:
  smiles: "C1COC(=O)O1"
  functional_groups: [{ fg_id: "FG_1", fg_type: "cyclic_carbonate" }]

output:
  carbonyl_cluster:
    members:
      - fg_id: "FG_1"
        carbonyl_type: "cyclic_carbonate"
        center_atom: 3
        carbonyl_oxygen: 4
        electrophilicity: "moderate"
        reducibility: "moderate"
        modifiers: ["strained"]
        notes: "五元环状碳酸酯，有轻度张力"
    
    dominant_carbonyl: "FG_1"
    
    physchem_routing:
      primary: "LUMO_02_pi_antibond_v1"
      secondary: ["HOMO_02_lonepair_n_v1", "LUMO_04_ring_strain_v1"]
    
    cluster_summary: "环状碳酸酯，电化学还原开环的典型底物"
```

## Guardrails
- 同一分子可有多个羰基，需逐一分析
- 羰基活性受邻近基团显著影响
- 不预测具体反应产物
- 对于多羰基分子，标记竞争可能性

## Confusable Cases
- 酯 vs 内酯：后者是环状
- 酰胺 vs 内酰胺：后者是环状
- 碳酸酯 vs 酯：碳酸酯有两个烷氧基

## Changelog
- 2025-12-24: 初始版本

