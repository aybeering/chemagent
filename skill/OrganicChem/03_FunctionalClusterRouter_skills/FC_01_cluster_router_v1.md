# FC_01_cluster_router_v1 — 官能团簇总路由

## Triggers
- 需要将分子中的官能团归类为化学功能簇
- 需要为 PhysChem 分析推荐目标模块
- 作为 OrganicChem → PhysChem 的桥接入口

## Inputs
- 分子表示：SMILES / 结构描述
- 官能团信息（必需）：来自 SD_03 的 functional_groups
- 敏感位点信息（推荐）：来自 RH_01 的 reactive_hotspots

## Outputs
```yaml
cluster_routing:
  clusters:
    - cluster_type: "carbonyl | nitrogen | oxygen | halogen | sulfur_phosphorus | unsaturated"
      functional_groups: ["<fg_id>"]
      priority: <int>
      physchem_modules: ["<module_id>"]
      notes: "<说明>"
  
  primary_cluster: "<主要簇类型>"
  secondary_clusters: ["<次要簇>"]
  
  suggested_physchem_modules:
    - module_id: "<PhysChem 模块 ID>"
      reason: "<推荐理由>"
      priority: <int>
      target_sites: [<原子索引>]
  
  routing_summary: "<路由摘要>"
  confidence: <0.0-1.0>
```

## Rules

### 簇类型定义

| 簇类型 | 包含的官能团 | 化学特征 |
|--------|-------------|---------|
| carbonyl | 醛、酮、羧酸、酯、酰胺、酸酐、碳酸酯、酰卤 | π* C=O 反键轨道 |
| nitrogen | 胺、酰胺、腈、硝基、偶氮、杂环 N | n 孤对 / π 系统 |
| oxygen | 醇、醚、环氧、过氧化物 | n 孤对（不含羰基氧） |
| halogen | C-F、C-Cl、C-Br、C-I | σ* C-X 反键轨道 |
| sulfur_phosphorus | 硫醇、硫醚、亚砜、磺酰、磷酸酯 | n 孤对 / d 轨道 |
| unsaturated | 烯烃、炔烃、芳环、共轭体系 | π / π* 轨道 |

### 优先级判定规则

1. **反应活性优先**：更活泼的官能团优先
2. **电化学相关优先**：与电极反应相关的官能团优先
3. **数量权重**：相同类型官能团多则优先级提升

### 簇到 PhysChem 模块的映射

| 簇类型 | PhysChem 模块 | 原因 |
|--------|--------------|------|
| carbonyl | LUMO_02_pi_antibond_v1 | 羰基 π* 是主要还原位点 |
| carbonyl (酯/酰胺) | HOMO_02_lonepair_n_v1 | 酯氧/酰胺氧孤对 |
| nitrogen (胺) | HOMO_02_lonepair_n_v1 | 胺氮孤对是主要氧化位点 |
| nitrogen (硝基) | LUMO_02_pi_antibond_v1 | 硝基可被还原 |
| oxygen | HOMO_02_lonepair_n_v1 | 醚/醇氧孤对 |
| halogen | LUMO_03_sigma_antibond_v1 | C-X σ* 可接受电子 |
| halogen (F) | ELEC_02_I_sigma_v1 | 强诱导效应分析 |
| sulfur_phosphorus | HOMO_02_lonepair_n_v1 | S/P 孤对 |
| unsaturated | HOMO_03_pi_system_v1 | π 系统氧化 |
| unsaturated | LUMO_02_pi_antibond_v1 | π* 还原 |

### 交叉效应考虑

| 组合 | 交叉效应 | 推荐附加模块 |
|------|---------|-------------|
| carbonyl + halogen | 卤素 -I 增强羰基亲电性 | ELEC_02 |
| nitrogen + carbonyl | 酰胺共振 | ELEC_03 |
| unsaturated + EWG | 缺电子烯烃/芳环 | LUMO_02 |
| unsaturated + EDG | 富电子烯烃/芳环 | HOMO_03 |

## Steps
1. **收集官能团信息**
   - 从 SD_03 获取 functional_groups

2. **按簇类型分组**
   - 遍历官能团，归入对应簇

3. **调用簇子卡分析**
   - FC_02 ~ FC_07 详细分析每个簇

4. **确定优先级**
   - 综合活性、数量、交叉效应

5. **生成 PhysChem 路由建议**
   - 映射簇到模块
   - 考虑交叉效应

6. **汇总输出**

## Examples

**Example 1: 乙酸乙酯**
```yaml
input:
  smiles: "CCOC(=O)C"
  functional_groups:
    - { fg_id: "FG_1", fg_type: "ester", fg_category: "carbonyl" }

output:
  cluster_routing:
    clusters:
      - cluster_type: "carbonyl"
        functional_groups: ["FG_1"]
        priority: 1
        physchem_modules: ["LUMO_02_pi_antibond_v1"]
      - cluster_type: "oxygen"
        functional_groups: ["FG_1"]
        priority: 2
        physchem_modules: ["HOMO_02_lonepair_n_v1"]
    
    primary_cluster: "carbonyl"
    
    suggested_physchem_modules:
      - module_id: "LUMO_02_pi_antibond_v1"
        reason: "酯羰基 π* 是还原位点"
        priority: 1
      - module_id: "HOMO_02_lonepair_n_v1"
        reason: "酯氧孤对可被氧化"
        priority: 2
    
    routing_summary: "简单酯类，羰基为主要反应中心"
    confidence: 0.9
```

**Example 2: 氟代碳酸乙烯酯 (FEC)**
```yaml
input:
  smiles: "FC1COC(=O)O1"
  functional_groups:
    - { fg_id: "FG_1", fg_type: "cyclic_carbonate", fg_category: "carbonyl" }
    - { fg_id: "FG_2", fg_type: "C-F", fg_category: "halogen" }

output:
  cluster_routing:
    clusters:
      - cluster_type: "carbonyl"
        functional_groups: ["FG_1"]
        priority: 1
        physchem_modules: ["LUMO_02_pi_antibond_v1"]
      - cluster_type: "halogen"
        functional_groups: ["FG_2"]
        priority: 2
        physchem_modules: ["LUMO_03_sigma_antibond_v1", "ELEC_02_I_sigma_v1"]
      - cluster_type: "oxygen"
        functional_groups: ["FG_1"]
        priority: 3
        physchem_modules: ["HOMO_02_lonepair_n_v1"]
    
    primary_cluster: "carbonyl"
    secondary_clusters: ["halogen", "oxygen"]
    
    suggested_physchem_modules:
      - module_id: "LUMO_02_pi_antibond_v1"
        reason: "环状碳酸酯羰基 π*"
        priority: 1
      - module_id: "LUMO_03_sigma_antibond_v1"
        reason: "C-F σ* 可接受电子释放 F⁻"
        priority: 2
      - module_id: "ELEC_02_I_sigma_v1"
        reason: "F 的 -I 效应分析"
        priority: 3
      - module_id: "LUMO_04_ring_strain_v1"
        reason: "五元环存在轻度张力"
        priority: 4
    
    routing_summary: "FEC 为典型电解液添加剂，羰基和 C-F 均为关键位点"
    confidence: 0.95
```

**Example 3: 二甲基亚砜 (DMSO)**
```yaml
input:
  smiles: "CS(=O)C"
  functional_groups:
    - { fg_id: "FG_1", fg_type: "sulfoxide", fg_category: "sulfur" }

output:
  cluster_routing:
    clusters:
      - cluster_type: "sulfur_phosphorus"
        functional_groups: ["FG_1"]
        priority: 1
        physchem_modules: ["HOMO_02_lonepair_n_v1"]
    
    primary_cluster: "sulfur_phosphorus"
    
    suggested_physchem_modules:
      - module_id: "HOMO_02_lonepair_n_v1"
        reason: "亚砜硫原子孤对可被氧化"
        priority: 1
      - module_id: "LUMO_02_pi_antibond_v1"
        reason: "S=O 可被还原"
        priority: 2
    
    routing_summary: "亚砜类化合物，S 原子为主要反应中心"
    confidence: 0.85
```

## Guardrails
- 官能团可能同时属于多个簇（如酯的羰基和氧）
- 交叉效应需在 routing_summary 中说明
- 对于复杂多官能团分子，限制推荐模块数量（≤5）
- 不预测具体反应，只提供分析入口

## Dependencies
- `SD_03_functional_group_v1`
- `FC_02_carbonyl_cluster_v1`
- `FC_03_nitrogen_cluster_v1`
- `FC_04_oxygen_cluster_v1`
- `FC_05_halogen_cluster_v1`
- `FC_06_sulfur_phosphorus_v1`
- `FC_07_unsaturated_cluster_v1`

## Changelog
- 2025-12-24: 初始版本

