# FC_07_unsaturated_cluster_v1 — 不饱和簇分析

## Triggers
- 分子中存在不饱和键（烯烃、炔烃、芳环）
- 需要分析 π 系统的类型和反应特性
- 需要为 PhysChem HOMO/LUMO 分析提供 π 系统信息

## Inputs
- 官能团列表：fg_category = "unsaturated" 的官能团
- 共轭信息：来自 SD_06 的 conjugation_map
- 分子表示：SMILES / 结构描述

## Outputs
```yaml
unsaturated_cluster:
  members:
    - fg_id: "<官能团 ID>"
      unsaturated_type: "alkene | alkyne | benzene | naphthalene | heterocyclic_aromatic | conjugated_diene | extended_pi"
      atoms: [<原子索引>]
      pi_electrons: <int>
      aromaticity: "aromatic | antiaromatic | non-aromatic"
      electron_density: "rich | neutral | poor"
      homo_contribution: "high | moderate | low"
      lumo_contribution: "high | moderate | low"
      substituent_effects: ["EWG_attached", "EDG_attached"]
      modifiers: ["strained", "conjugated", "cross-conjugated"]
      notes: "<说明>"
  
  dominant_pi_system: "<fg_id>"
  
  physchem_routing:
    homo_analysis: ["HOMO_03_pi_system_v1"]
    lumo_analysis: ["LUMO_02_pi_antibond_v1"]
    electronic_effect: ["ELEC_03_M_pi_v1"]
  
  cluster_summary: "<不饱和簇摘要>"
```

## Rules

### 不饱和类型与特性

| 类型 | π 电子 | HOMO | LUMO | 典型反应 |
|------|--------|------|------|----------|
| 烯烃 | 2 | π | π* | 加成、氧化 |
| 炔烃 | 4 | π | π* | 加成、氧化 |
| 苯环 | 6 | π | π* | EAS、氧化 |
| 共轭二烯 | 4 | π | π* | 1,4-加成、DA |
| 富电子芳环 | 6 | π (高) | π* | EAS (活化) |
| 缺电子芳环 | 6 | π (低) | π* (低) | SNAr |

### 电子密度评估

| 电子密度 | 取代基 | 反应倾向 |
|----------|--------|---------|
| rich | EDG (OR, NR₂) | 亲电攻击 |
| neutral | 烷基 | 中等 |
| poor | EWG (NO₂, CF₃) | 亲核攻击 |

### 芳香性判定（Hückel 规则）

| π 电子数 | 平面性 | 芳香性 |
|----------|--------|--------|
| 4n+2 | 是 | 芳香 |
| 4n | 是 | 反芳香 |
| 任意 | 否 | 非芳香 |

### PhysChem 路由规则

| 不饱和类型 | HOMO 分析 | LUMO 分析 | 电子效应 |
|-----------|----------|----------|---------|
| 烯烃 | HOMO_03 | LUMO_02 | - |
| 富电子芳环 | HOMO_03 | - | ELEC_03 |
| 缺电子芳环 | - | LUMO_02 | ELEC_03 |
| 共轭体系 | HOMO_03 | LUMO_02 | ELEC_03 |

## Steps
1. **筛选不饱和官能团**
   - 从 functional_groups 获取 unsaturated 类

2. **分析 π 系统**
   - 结合 conjugation_map 确定共轭范围

3. **评估电子密度**
   - 检查取代基的推拉电子效应

4. **判定芳香性**

5. **评估 HOMO/LUMO 贡献**

6. **生成 PhysChem 路由**

## Examples

**Example 1: 1-己烯**
```yaml
input:
  smiles: "CCCCC=C"
  functional_groups: [{ fg_id: "FG_1", fg_type: "alkene" }]

output:
  unsaturated_cluster:
    members:
      - fg_id: "FG_1"
        unsaturated_type: "alkene"
        atoms: [4, 5]
        pi_electrons: 2
        aromaticity: "non-aromatic"
        electron_density: "neutral"
        homo_contribution: "high"
        lumo_contribution: "moderate"
        notes: "端烯，π 电子是主要 HOMO"
    
    dominant_pi_system: "FG_1"
    
    physchem_routing:
      homo_analysis: ["HOMO_03_pi_system_v1"]
      lumo_analysis: ["LUMO_02_pi_antibond_v1"]
    
    cluster_summary: "简单烯烃，π 键是主要反应位点"
```

**Example 2: 甲苯**
```yaml
input:
  smiles: "Cc1ccccc1"
  functional_groups: [{ fg_id: "FG_1", fg_type: "benzene" }]

output:
  unsaturated_cluster:
    members:
      - fg_id: "FG_1"
        unsaturated_type: "benzene"
        atoms: [1, 2, 3, 4, 5, 6]
        pi_electrons: 6
        aromaticity: "aromatic"
        electron_density: "neutral"
        homo_contribution: "moderate"
        lumo_contribution: "low"
        substituent_effects: ["EDG_attached"]
        notes: "甲基略推电子，芳环轻度活化"
    
    dominant_pi_system: "FG_1"
    
    physchem_routing:
      homo_analysis: ["HOMO_03_pi_system_v1"]
      electronic_effect: ["ELEC_03_M_pi_v1", "ELEC_04_hyperconj_v1"]
    
    cluster_summary: "取代苯，甲基通过超共轭轻度活化"
```

**Example 3: 苯胺**
```yaml
input:
  smiles: "Nc1ccccc1"
  functional_groups: [{ fg_id: "FG_1", fg_type: "aniline" }]

output:
  unsaturated_cluster:
    members:
      - fg_id: "FG_1"
        unsaturated_type: "benzene"
        atoms: [1, 2, 3, 4, 5, 6]
        pi_electrons: 6
        aromaticity: "aromatic"
        electron_density: "rich"
        homo_contribution: "high"
        lumo_contribution: "low"
        substituent_effects: ["EDG_attached"]
        modifiers: ["conjugated"]
        notes: "氨基 +M 效应强烈活化芳环"
    
    dominant_pi_system: "FG_1"
    
    physchem_routing:
      homo_analysis: ["HOMO_03_pi_system_v1", "HOMO_02_lonepair_n_v1"]
      electronic_effect: ["ELEC_03_M_pi_v1"]
    
    cluster_summary: "苯胺，富电子芳环，易被氧化"
```

**Example 4: 硝基苯**
```yaml
input:
  smiles: "[O-][N+](=O)c1ccccc1"
  functional_groups: [{ fg_id: "FG_1", fg_type: "nitrobenzene" }]

output:
  unsaturated_cluster:
    members:
      - fg_id: "FG_1"
        unsaturated_type: "benzene"
        atoms: [4, 5, 6, 7, 8, 9]
        pi_electrons: 6
        aromaticity: "aromatic"
        electron_density: "poor"
        homo_contribution: "low"
        lumo_contribution: "high"
        substituent_effects: ["EWG_attached"]
        modifiers: ["conjugated"]
        notes: "硝基 -M 效应使芳环缺电子"
    
    dominant_pi_system: "FG_1"
    
    physchem_routing:
      lumo_analysis: ["LUMO_02_pi_antibond_v1"]
      electronic_effect: ["ELEC_02_I_sigma_v1", "ELEC_03_M_pi_v1"]
    
    cluster_summary: "硝基苯，缺电子芳环，可被还原或 SNAr"
```

**Example 5: 1,3-丁二烯**
```yaml
input:
  smiles: "C=CC=C"
  functional_groups: [{ fg_id: "FG_1", fg_type: "conjugated_diene" }]

output:
  unsaturated_cluster:
    members:
      - fg_id: "FG_1"
        unsaturated_type: "conjugated_diene"
        atoms: [0, 1, 2, 3]
        pi_electrons: 4
        aromaticity: "non-aromatic"
        electron_density: "neutral"
        homo_contribution: "high"
        lumo_contribution: "high"
        modifiers: ["conjugated"]
        notes: "共轭二烯，Diels-Alder 反应的亲二烯体"
    
    dominant_pi_system: "FG_1"
    
    physchem_routing:
      homo_analysis: ["HOMO_03_pi_system_v1"]
      lumo_analysis: ["LUMO_02_pi_antibond_v1"]
    
    cluster_summary: "共轭二烯，HOMO/LUMO 能隙较小"
```

**Example 6: 萘**
```yaml
input:
  smiles: "c1ccc2ccccc2c1"
  functional_groups: [{ fg_id: "FG_1", fg_type: "naphthalene" }]

output:
  unsaturated_cluster:
    members:
      - fg_id: "FG_1"
        unsaturated_type: "naphthalene"
        atoms: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        pi_electrons: 10
        aromaticity: "aromatic"
        electron_density: "neutral"
        homo_contribution: "high"
        lumo_contribution: "moderate"
        notes: "稠合芳环，比苯更易氧化"
    
    dominant_pi_system: "FG_1"
    
    physchem_routing:
      homo_analysis: ["HOMO_03_pi_system_v1"]
      lumo_analysis: ["LUMO_02_pi_antibond_v1"]
    
    cluster_summary: "萘，扩展 π 系统，HOMO 较高"
```

## Guardrails
- 芳香性需严格按 Hückel 规则判定
- 扩展共轭体系需考虑所有参与原子
- 取代基效应需区分 o/m/p 位影响
- 不预测具体反应产物

## Confusable Cases
- 芳香 vs 非芳香环：检查 4n+2 规则
- 共轭 vs 交叉共轭：后者无法完全离域
- 累积双键 vs 共轭双键：累积不是共轭

## Changelog
- 2025-12-24: 初始版本

