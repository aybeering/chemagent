# FC_04_oxygen_cluster_v1 — 氧簇分析

## Triggers
- 分子中存在非羰基的含氧官能团
- 需要分析氧原子的类型和反应特性
- 需要为 PhysChem HOMO 分析提供含氧位点信息

## Inputs
- 官能团列表：fg_category = "oxygen" 的官能团（不含羰基氧）
- 杂原子标签：来自 SD_04 的氧原子信息
- 分子表示：SMILES / 结构描述

## Outputs
```yaml
oxygen_cluster:
  members:
    - fg_id: "<官能团 ID>"
      oxygen_type: "primary_alcohol | secondary_alcohol | tertiary_alcohol | phenol | ether | cyclic_ether | epoxide | peroxide | hydroperoxide | furan | other_heterocycle"
      oxygen_atom: <int>               # 氧原子索引
      hybridization: "sp2 | sp3"
      lone_pairs: <int>
      nucleophilicity: "high | moderate | low"
      oxidizability: "high | moderate | low"
      acidity: "high | moderate | low | very_low"
      hydrogen_bonding: "donor | acceptor | both | none"
      modifiers: ["conjugated", "strained", "EWG_adjacent", "EDG_adjacent"]
      notes: "<说明>"
  
  dominant_oxygen: "<fg_id>"           # 最活泼的氧
  
  physchem_routing:
    homo_analysis: ["HOMO_02_lonepair_n_v1"]
    ring_strain: ["LUMO_04_ring_strain_v1"]  # 若有环氧
  
  cluster_summary: "<氧簇摘要>"
```

## Rules

### 氧类型与特性

| 氧类型 | 亲核性 | 氧化性 | 酸性 | 说明 |
|--------|--------|--------|------|------|
| primary_alcohol | 中 | 高 | 低 | 可氧化为醛 |
| secondary_alcohol | 中 | 高 | 低 | 可氧化为酮 |
| tertiary_alcohol | 中 | 低 | 低 | 难氧化 |
| phenol | 低 | 中 | 中 | 芳环共轭 |
| ether | 低 | 中-低 | 极低 | 两孤对 |
| cyclic_ether | 低 | 中 | 极低 | THF 类 |
| epoxide | 低 | 低 | 极低 | 高张力 |
| peroxide | 低 | 高 | 低 | O-O 弱键 |
| hydroperoxide | 低 | 极高 | 中 | 危险！ |
| furan | 低 | 中 | 极低 | 芳香杂环 |

### 氧化敏感性判定

| 氧类型 | 氧化产物 | HOMO 类型 |
|--------|---------|----------|
| 伯醇 | 醛 → 羧酸 | n 孤对 |
| 仲醇 | 酮 | n 孤对 |
| 叔醇 | 难氧化 | n 孤对 |
| 醚 | 过氧化物（慢） | n 孤对 |
| 过氧化物 | 自由基 | σ (O-O) |

### 氢键特性

| 氧类型 | 氢键供体 | 氢键受体 |
|--------|---------|---------|
| 醇 | 是 | 是 |
| 酚 | 是 | 是 |
| 醚 | 否 | 是 |
| 环氧 | 否 | 弱 |

### PhysChem 路由规则

| 氧类型 | 主要模块 | 附加模块 |
|--------|---------|---------|
| 醇/醚 | HOMO_02 | - |
| 酚 | HOMO_02 | ELEC_03 (与芳环共轭) |
| 环氧 | HOMO_02 | LUMO_04 (环张力) |
| 过氧化物 | HOMO_02 | 特别警告 |

## Steps
1. **筛选含氧官能团**
   - 从 functional_groups 获取 oxygen 类
   - 排除已在 carbonyl_cluster 中的羰基氧

2. **分类氧类型**
   - 结合杂原子标签细分

3. **评估各项特性**
   - 亲核性、氧化性、酸性、氢键

4. **确定主导氧位点**

5. **生成 PhysChem 路由**

## Examples

**Example 1: 乙醇**
```yaml
input:
  smiles: "CCO"
  functional_groups: [{ fg_id: "FG_1", fg_type: "primary_alcohol" }]

output:
  oxygen_cluster:
    members:
      - fg_id: "FG_1"
        oxygen_type: "primary_alcohol"
        oxygen_atom: 2
        hybridization: "sp3"
        lone_pairs: 2
        nucleophilicity: "moderate"
        oxidizability: "high"
        acidity: "low"
        hydrogen_bonding: "both"
        notes: "伯醇，可被氧化为醛"
    
    dominant_oxygen: "FG_1"
    
    physchem_routing:
      homo_analysis: ["HOMO_02_lonepair_n_v1"]
    
    cluster_summary: "简单伯醇，氧孤对是主要 HOMO"
```

**Example 2: 四氢呋喃 (THF)**
```yaml
input:
  smiles: "C1CCOC1"
  functional_groups: [{ fg_id: "FG_1", fg_type: "cyclic_ether" }]

output:
  oxygen_cluster:
    members:
      - fg_id: "FG_1"
        oxygen_type: "cyclic_ether"
        oxygen_atom: 3
        hybridization: "sp3"
        lone_pairs: 2
        nucleophilicity: "low"
        oxidizability: "moderate"
        acidity: "very_low"
        hydrogen_bonding: "acceptor"
        notes: "五元环醚，常用溶剂"
    
    dominant_oxygen: "FG_1"
    
    physchem_routing:
      homo_analysis: ["HOMO_02_lonepair_n_v1"]
    
    cluster_summary: "环醚，氧孤对可配位金属或作氢键受体"
```

**Example 3: 环氧乙烷**
```yaml
input:
  smiles: "C1OC1"
  functional_groups: [{ fg_id: "FG_1", fg_type: "epoxide" }]

output:
  oxygen_cluster:
    members:
      - fg_id: "FG_1"
        oxygen_type: "epoxide"
        oxygen_atom: 1
        hybridization: "sp3"
        lone_pairs: 2
        nucleophilicity: "low"
        oxidizability: "low"
        acidity: "very_low"
        hydrogen_bonding: "acceptor"
        modifiers: ["strained"]
        notes: "三元环氧化物，高张力易开环"
    
    dominant_oxygen: "FG_1"
    
    physchem_routing:
      homo_analysis: ["HOMO_02_lonepair_n_v1"]
      ring_strain: ["LUMO_04_ring_strain_v1"]
    
    cluster_summary: "环氧化物，高张力是主要反应驱动力"
```

**Example 4: 苯酚**
```yaml
input:
  smiles: "c1ccc(O)cc1"
  functional_groups: [{ fg_id: "FG_1", fg_type: "phenol" }]

output:
  oxygen_cluster:
    members:
      - fg_id: "FG_1"
        oxygen_type: "phenol"
        oxygen_atom: 4
        hybridization: "sp3"
        lone_pairs: 2
        nucleophilicity: "low"
        oxidizability: "moderate"
        acidity: "moderate"
        hydrogen_bonding: "both"
        modifiers: ["conjugated"]
        notes: "酚，氧孤对与芳环共轭"
    
    dominant_oxygen: "FG_1"
    
    physchem_routing:
      homo_analysis: ["HOMO_02_lonepair_n_v1"]
      electronic_effect: ["ELEC_03_M_pi_v1"]
    
    cluster_summary: "酚，氧孤对对芳环有 +M 效应"
```

**Example 5: 二甲基过氧化物**
```yaml
input:
  smiles: "COOC"
  functional_groups: [{ fg_id: "FG_1", fg_type: "peroxide" }]

output:
  oxygen_cluster:
    members:
      - fg_id: "FG_1"
        oxygen_type: "peroxide"
        oxygen_atom: 1
        hybridization: "sp3"
        lone_pairs: 2
        nucleophilicity: "low"
        oxidizability: "very_high"
        acidity: "low"
        modifiers: ["weak_O-O_bond"]
        notes: "过氧化物，O-O 键弱（~36 kcal/mol），危险品！"
    
    dominant_oxygen: "FG_1"
    
    physchem_routing:
      homo_analysis: ["HOMO_02_lonepair_n_v1"]
    
    cluster_summary: "过氧化物，易均裂产生自由基，需谨慎处理"
    warnings: ["过氧化物不稳定，可能爆炸"]
```

## Guardrails
- 羰基氧已在 FC_02 中处理，此处排除
- 过氧化物需特别警告安全风险
- 醚类氧化缓慢但可能形成过氧化物
- 环氧的反应性主要来自环张力

## Confusable Cases
- 醚 vs 酯：酯含有羰基
- 醇 vs 半缩醛：半缩醛有两个氧
- 环氧 vs 缩醛环：检查是否有两个 C-O

## Changelog
- 2025-12-24: 初始版本

