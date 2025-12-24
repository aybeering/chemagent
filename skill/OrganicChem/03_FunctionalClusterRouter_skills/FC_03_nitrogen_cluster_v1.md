# FC_03_nitrogen_cluster_v1 — 氮簇分析

## Triggers
- 分子中存在含氮官能团
- 需要分析氮原子的类型和反应特性
- 需要为 PhysChem HOMO/LUMO 分析提供含氮位点信息

## Inputs
- 官能团列表：fg_category = "nitrogen" 的官能团
- 杂原子标签：来自 SD_04 的氮原子信息
- 分子表示：SMILES / 结构描述

## Outputs
```yaml
nitrogen_cluster:
  members:
    - fg_id: "<官能团 ID>"
      nitrogen_type: "primary_amine | secondary_amine | tertiary_amine | quaternary_ammonium | amide | lactam | nitrile | nitro | azo | imine | pyridine | pyrrole | imidazole | other_heterocycle"
      nitrogen_atom: <int>             # 氮原子索引
      hybridization: "sp | sp2 | sp3"
      lone_pair_available: true | false
      nucleophilicity: "high | moderate | low | none"
      oxidizability: "high | moderate | low"
      basicity: "high | moderate | low | none"
      modifiers: ["conjugated", "protonated", "EWG_adjacent", "EDG_adjacent"]
      notes: "<说明>"
  
  dominant_nitrogen: "<fg_id>"         # 最活泼的氮
  
  physchem_routing:
    homo_analysis: ["HOMO_02_lonepair_n_v1"]
    lumo_analysis: ["LUMO_02_pi_antibond_v1"]  # 若有可还原氮
    electronic_effect: ["ELEC_03_M_pi_v1"]
  
  cluster_summary: "<氮簇摘要>"
```

## Rules

### 氮类型与特性

| 氮类型 | 亲核性 | 氧化性 | 碱性 | HOMO 贡献 |
|--------|--------|--------|------|----------|
| primary_amine | 高 | 高 | 高 | n 孤对 |
| secondary_amine | 高 | 高 | 高 | n 孤对 |
| tertiary_amine | 中-高 | 中 | 中-高 | n 孤对 |
| amide | 低 | 低 | 低 | n 共轭离域 |
| nitrile | 弱 | 低 | 极低 | π (C≡N) |
| nitro | 无 | 无 | 无 | π* 可被还原 |
| pyridine | 中 | 低 | 中 | n 孤对（不参与芳香） |
| pyrrole | 无 | 中 | 极低 | π（孤对参与芳香） |
| imine | 中 | 中 | 中 | n 孤对 |
| azo | 低 | 低 | 低 | n 孤对 |

### 孤对可用性判定

| 氮类型 | 孤对状态 | 说明 |
|--------|---------|------|
| 胺类 | 可用 | 未共轭的 n 孤对 |
| 酰胺 | 部分可用 | 与羰基共轭 |
| 吡啶 | 可用 | sp² 孤对在环平面外 |
| 吡咯 | 不可用 | 孤对参与芳香性 |
| 硝基 | 不可用 | 氮带正电荷 |

### PhysChem 路由规则

| 氮类型 | HOMO 分析 | LUMO 分析 | 电子效应 |
|--------|----------|----------|---------|
| 胺类 | HOMO_02 | - | +M (供电子) |
| 酰胺 | HOMO_02 | LUMO_02 | 共振体 |
| 腈 | - | LUMO_02 | -I/-M |
| 硝基 | - | LUMO_02 | -I/-M (强吸电子) |
| 吡啶 | HOMO_02 | - | -I (环上) |
| 吡咯 | HOMO_03 | - | +M (供电子) |

## Steps
1. **筛选含氮官能团**
   - 从 functional_groups 获取 nitrogen 类

2. **分类氮类型**
   - 结合杂原子标签细分

3. **评估孤对可用性**
   - 判断是否参与共轭/芳香

4. **评估亲核性/碱性/氧化性**

5. **确定主导氮位点**

6. **生成 PhysChem 路由**

## Examples

**Example 1: 三乙胺**
```yaml
input:
  smiles: "CCN(CC)CC"
  functional_groups: [{ fg_id: "FG_1", fg_type: "tertiary_amine" }]

output:
  nitrogen_cluster:
    members:
      - fg_id: "FG_1"
        nitrogen_type: "tertiary_amine"
        nitrogen_atom: 2
        hybridization: "sp3"
        lone_pair_available: true
        nucleophilicity: "high"
        oxidizability: "moderate"
        basicity: "high"
        notes: "叔胺，强碱性和亲核性"
    
    dominant_nitrogen: "FG_1"
    
    physchem_routing:
      homo_analysis: ["HOMO_02_lonepair_n_v1"]
      electronic_effect: ["ELEC_03_M_pi_v1"]
    
    cluster_summary: "叔胺，氮孤对是主要 HOMO 贡献者"
```

**Example 2: 吡啶**
```yaml
input:
  smiles: "c1ccncc1"
  functional_groups: [{ fg_id: "FG_1", fg_type: "pyridine" }]

output:
  nitrogen_cluster:
    members:
      - fg_id: "FG_1"
        nitrogen_type: "pyridine"
        nitrogen_atom: 3
        hybridization: "sp2"
        lone_pair_available: true
        nucleophilicity: "moderate"
        oxidizability: "low"
        basicity: "moderate"
        notes: "吡啶型 N，孤对在环平面外，不参与芳香性"
    
    dominant_nitrogen: "FG_1"
    
    physchem_routing:
      homo_analysis: ["HOMO_02_lonepair_n_v1"]
    
    cluster_summary: "吡啶，氮孤对可作为配位/亲核位点"
```

**Example 3: 吡咯**
```yaml
input:
  smiles: "c1cc[nH]c1"
  functional_groups: [{ fg_id: "FG_1", fg_type: "pyrrole" }]

output:
  nitrogen_cluster:
    members:
      - fg_id: "FG_1"
        nitrogen_type: "pyrrole"
        nitrogen_atom: 3
        hybridization: "sp2"
        lone_pair_available: false
        nucleophilicity: "none"
        oxidizability: "moderate"
        basicity: "very_low"
        modifiers: ["aromatic_conjugation"]
        notes: "吡咯型 N，孤对参与芳香性 (6π)"
    
    dominant_nitrogen: "FG_1"
    
    physchem_routing:
      homo_analysis: ["HOMO_03_pi_system_v1"]
      electronic_effect: ["ELEC_03_M_pi_v1"]
    
    cluster_summary: "吡咯，富电子芳环，N 孤对参与芳香性"
```

**Example 4: 硝基苯**
```yaml
input:
  smiles: "c1ccc([N+](=O)[O-])cc1"
  functional_groups: [{ fg_id: "FG_1", fg_type: "nitro" }]

output:
  nitrogen_cluster:
    members:
      - fg_id: "FG_1"
        nitrogen_type: "nitro"
        nitrogen_atom: 4
        hybridization: "sp2"
        lone_pair_available: false
        nucleophilicity: "none"
        oxidizability: "none"
        basicity: "none"
        modifiers: ["EWG"]
        notes: "硝基，强吸电子基，可被还原"
    
    dominant_nitrogen: "FG_1"
    
    physchem_routing:
      lumo_analysis: ["LUMO_02_pi_antibond_v1"]
      electronic_effect: ["ELEC_02_I_sigma_v1", "ELEC_03_M_pi_v1"]
    
    cluster_summary: "硝基，强吸电子基，可电化学还原"
```

**Example 5: 乙腈**
```yaml
input:
  smiles: "CC#N"
  functional_groups: [{ fg_id: "FG_1", fg_type: "nitrile" }]

output:
  nitrogen_cluster:
    members:
      - fg_id: "FG_1"
        nitrogen_type: "nitrile"
        nitrogen_atom: 2
        hybridization: "sp"
        lone_pair_available: true
        nucleophilicity: "weak"
        oxidizability: "low"
        basicity: "very_low"
        notes: "腈基，弱 Lewis 碱，可作溶剂"
    
    dominant_nitrogen: "FG_1"
    
    physchem_routing:
      lumo_analysis: ["LUMO_02_pi_antibond_v1"]
      electronic_effect: ["ELEC_02_I_sigma_v1"]
    
    cluster_summary: "腈基，C≡N 的 π* 可被还原"
```

## Guardrails
- 注意区分吡啶型 N（孤对独立）和吡咯型 N（孤对参与芳香）
- 酰胺氮的亲核性因共轭而大幅降低
- 硝基氮不具有亲核性或碱性
- 季铵盐无孤对，不能作为亲核试剂

## Confusable Cases
- 吡啶 vs 吡咯：孤对是否参与芳香性
- 胺 vs 酰胺：后者孤对共轭
- 腈 vs 异腈：CN vs NC 顺序

## Changelog
- 2025-12-24: 初始版本

