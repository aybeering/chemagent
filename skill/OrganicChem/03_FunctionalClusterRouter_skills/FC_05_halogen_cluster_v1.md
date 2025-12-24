# FC_05_halogen_cluster_v1 — 卤素簇分析

## Triggers
- 分子中存在卤素取代基
- 需要分析 C-X 键的反应特性
- 需要为 PhysChem LUMO/ELEC 分析提供卤素信息

## Inputs
- 官能团列表：fg_category = "halogen" 的官能团
- 杂原子标签：来自 SD_04 的卤素原子信息
- 分子表示：SMILES / 结构描述

## Outputs
```yaml
halogen_cluster:
  members:
    - fg_id: "<官能团 ID>"
      halogen_type: "C-F | C-Cl | C-Br | C-I | Ar-F | Ar-Cl | Ar-Br | Ar-I | vinyl_halide | acyl_halide"
      halogen_atom: <int>              # 卤素原子索引
      carbon_atom: <int>               # 连接的碳原子索引
      halogen: "F | Cl | Br | I"
      carbon_hybridization: "sp | sp2 | sp3"
      leaving_ability: "excellent | good | moderate | poor"
      bond_strength: "strong | moderate | weak"
      inductive_effect: "-I strength"
      reducibility: "high | moderate | low"
      modifiers: ["benzylic", "allylic", "alpha_carbonyl", "perfluoro"]
      notes: "<说明>"
  
  dominant_halogen: "<fg_id>"          # 最活泼/最重要的卤素
  
  physchem_routing:
    lumo_analysis: ["LUMO_03_sigma_antibond_v1"]
    electronic_effect: ["ELEC_02_I_sigma_v1"]
    field_effect: ["ELEC_05_field_v1"]  # 若有多卤代
  
  cluster_summary: "<卤素簇摘要>"
```

## Rules

### 卤素特性比较

| 卤素 | 电负性 | C-X 键强 (kcal/mol) | 离去能力 | -I 效应 |
|------|--------|---------------------|---------|---------|
| F | 4.0 | ~116 (强) | 差 | 极强 |
| Cl | 3.0 | ~81 (中) | 好 | 强 |
| Br | 2.8 | ~68 (弱) | 好 | 中 |
| I | 2.5 | ~52 (弱) | 极好 | 弱 |

### 碳杂化与反应性

| 碳类型 | 反应性 | 典型反应 |
|--------|--------|---------|
| sp³ (一级) | SN2 易 | 亲核取代 |
| sp³ (二级) | SN2/SN1 竞争 | 取代/消除 |
| sp³ (三级) | SN1/E1 为主 | 取代/消除 |
| sp² (芳基) | SNAr（需活化） | 亲核芳香取代 |
| sp² (乙烯基) | 难取代 | 加成/偶联 |
| sp (炔基) | 难取代 | 偶联 |

### 位置效应

| 位置 | 效应 | 说明 |
|------|------|------|
| 苄基 | ↑ SN1/SN2 增强 | 碳正离子稳定 |
| 烯丙基 | ↑ SN1/SN2 增强 | 碳正离子稳定 |
| α-羰基 | ↑ 活化 | α-卤代酮活泼 |
| 全氟 | ↓ 亲核取代 | 极强 -I，但 C-F 强 |

### 还原性评估

| 卤素 | 电化学还原 | σ*(C-X) 能级 |
|------|-----------|-------------|
| C-F | 困难 | 高 |
| C-Cl | 中等 | 中 |
| C-Br | 较易 | 较低 |
| C-I | 易 | 低 |

### PhysChem 路由规则

| 卤素类型 | 主要模块 | 电子效应 |
|----------|---------|---------|
| 所有卤素 | LUMO_03 (σ*) | ELEC_02 (-I) |
| 芳基卤 | LUMO_03 | ELEC_03 (+M 弱) |
| 多卤代 | LUMO_03 | ELEC_05 (场效应) |
| 全氟 | ELEC_02 | ELEC_05 |

## Steps
1. **筛选卤素官能团**
   - 从 functional_groups 获取 halogen 类

2. **分类卤素类型**
   - 确定卤素种类和碳杂化

3. **评估离去能力和反应性**

4. **分析电子效应**
   - -I 效应强度

5. **确定主导卤素**
   - 最具反应活性或电子效应最强

6. **生成 PhysChem 路由**

## Examples

**Example 1: 溴乙烷**
```yaml
input:
  smiles: "CCBr"
  functional_groups: [{ fg_id: "FG_1", fg_type: "C-Br" }]

output:
  halogen_cluster:
    members:
      - fg_id: "FG_1"
        halogen_type: "C-Br"
        halogen_atom: 2
        carbon_atom: 1
        halogen: "Br"
        carbon_hybridization: "sp3"
        leaving_ability: "good"
        bond_strength: "moderate"
        inductive_effect: "-I moderate"
        reducibility: "moderate"
        notes: "伯溴代烷，典型 SN2 底物"
    
    dominant_halogen: "FG_1"
    
    physchem_routing:
      lumo_analysis: ["LUMO_03_sigma_antibond_v1"]
      electronic_effect: ["ELEC_02_I_sigma_v1"]
    
    cluster_summary: "简单溴代烷，C-Br σ* 是主要 LUMO"
```

**Example 2: 三氟甲苯**
```yaml
input:
  smiles: "FC(F)(F)c1ccccc1"
  functional_groups: [{ fg_id: "FG_1", fg_type: "C-F", atoms: [0,1] }, ...]

output:
  halogen_cluster:
    members:
      - fg_id: "FG_1"
        halogen_type: "C-F"
        halogen_atom: 0
        carbon_atom: 1
        halogen: "F"
        carbon_hybridization: "sp3"
        leaving_ability: "poor"
        bond_strength: "strong"
        inductive_effect: "-I very strong"
        reducibility: "low"
        modifiers: ["perfluoro"]
        notes: "CF₃ 基团，强 -I 吸电子"
    
    dominant_halogen: "FG_1"
    
    physchem_routing:
      electronic_effect: ["ELEC_02_I_sigma_v1", "ELEC_05_field_v1"]
    
    cluster_summary: "三氟甲基，极强 -I 效应，C-F 键强难断裂"
```

**Example 3: 苄基氯**
```yaml
input:
  smiles: "ClCc1ccccc1"
  functional_groups: [{ fg_id: "FG_1", fg_type: "C-Cl" }]

output:
  halogen_cluster:
    members:
      - fg_id: "FG_1"
        halogen_type: "C-Cl"
        halogen_atom: 0
        carbon_atom: 1
        halogen: "Cl"
        carbon_hybridization: "sp3"
        leaving_ability: "good"
        bond_strength: "moderate"
        inductive_effect: "-I moderate"
        reducibility: "moderate"
        modifiers: ["benzylic"]
        notes: "苄基氯，SN1/SN2 均可行"
    
    dominant_halogen: "FG_1"
    
    physchem_routing:
      lumo_analysis: ["LUMO_03_sigma_antibond_v1"]
      electronic_effect: ["ELEC_02_I_sigma_v1"]
    
    cluster_summary: "苄基卤化物，碳正离子可被芳环稳定"
```

**Example 4: 氯苯（芳基卤）**
```yaml
input:
  smiles: "Clc1ccccc1"
  functional_groups: [{ fg_id: "FG_1", fg_type: "Ar-Cl" }]

output:
  halogen_cluster:
    members:
      - fg_id: "FG_1"
        halogen_type: "Ar-Cl"
        halogen_atom: 0
        carbon_atom: 1
        halogen: "Cl"
        carbon_hybridization: "sp2"
        leaving_ability: "poor"
        bond_strength: "strong"
        inductive_effect: "-I moderate"
        reducibility: "low"
        notes: "芳基氯，C-Cl 键强，需活化才能取代"
    
    dominant_halogen: "FG_1"
    
    physchem_routing:
      electronic_effect: ["ELEC_02_I_sigma_v1", "ELEC_03_M_pi_v1"]
    
    cluster_summary: "芳基卤，-I/-M 混合效应，邻对位钝化"
```

**Example 5: 氟代碳酸乙烯酯 (FEC)**
```yaml
input:
  smiles: "FC1COC(=O)O1"
  functional_groups: [{ fg_id: "FG_1", fg_type: "C-F" }]

output:
  halogen_cluster:
    members:
      - fg_id: "FG_1"
        halogen_type: "C-F"
        halogen_atom: 0
        carbon_atom: 1
        halogen: "F"
        carbon_hybridization: "sp3"
        leaving_ability: "poor"
        bond_strength: "strong"
        inductive_effect: "-I strong"
        reducibility: "moderate"
        notes: "C-F 键强，但电化学还原可释放 F⁻"
    
    dominant_halogen: "FG_1"
    
    physchem_routing:
      lumo_analysis: ["LUMO_03_sigma_antibond_v1"]
      electronic_effect: ["ELEC_02_I_sigma_v1"]
    
    cluster_summary: "FEC 的 C-F，电化学还原释放 F⁻ 形成 LiF"
```

## Guardrails
- 酰卤的反应性主要来自羰基，此处仅标记卤素
- 全氟化合物的 C-F 键通常不参与取代
- 芳基卤需特殊活化（SNAr 需 EWG）
- 过渡金属催化可实现芳基卤偶联

## Confusable Cases
- 酰卤 vs 烷基卤：前者反应中心是羰基
- 芳基卤 vs 苄基卤：前者 C(sp²)-X，后者 C(sp³)-X
- 乙烯基卤 vs 烯丙基卤：前者 C(sp²)-X 难取代

## Changelog
- 2025-12-24: 初始版本

