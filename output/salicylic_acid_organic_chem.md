# Salicylic Acid (水杨酸) 完整 OrganicChem 分析

## 分析流程
1. **结构解剖** (SD_01_digest_flowmap_v1)
2. **敏感位点识别** (RH_01_hotspot_flowmap_v1)
3. **官能团簇路由** (FC_01_cluster_router_v1)

---

## 1. 结构解剖 (Structure Digest)

### 分子信息
- **SMILES**: `OC(=O)c1ccccc1O`
- **标准化 SMILES**: `O=C(O)c1ccccc1O`
- **分子式**: C₇H₆O₃
- **原子总数**: 16

### 骨架识别 (SD_02)
- **骨架类型**: `cyclic` (单环)
- **主链长度**: 0 (环为主体)
- **环数量**: 1
- **环标识符**: `RING_1`

### 官能团识别 (SD_03)
识别到 3 个主要官能团：

| fg_id | 官能团类型 | 类别 | 原子索引 | 中心原子 | 子类型 |
|-------|-----------|------|---------|---------|--------|
| FG_1 | carboxylic_acid | carbonyl | [0,1,2] | 1 | benzoic_acid |
| FG_2 | phenol | oxygen | [15] | 15 | ortho_phenol |
| FG_3 | benzene | unsaturated | [3-8] | - | benzene |

**说明**:
- FG_1: 羧酸基团 (C=O + OH)，连接在芳环上形成苯甲酸结构
- FG_2: 酚羟基，位于羧基的邻位 (ortho)
- FG_3: 苯环骨架

### 杂原子标签 (SD_04)
分子中有 3 个氧原子：

| 原子索引 | 元素 | 杂化 | 孤对数 | 形式电荷 | 环境 | 反应性提示 |
|---------|------|------|--------|---------|------|-----------|
| 0 | O | sp3 | 2 | 0 | hydroxyl_oxygen (羧酸) | nucleophilic |
| 1 | O | sp2 | 2 | 0 | carbonyl_oxygen | nucleophilic |
| 15 | O | sp3 | 2 | 0 | phenol_oxygen | nucleophilic |

**说明**:
- 所有氧原子均为 sp³ 杂化 (羰基氧为 sp²)
- 每个氧有 2 个孤对电子
- 羧酸氧 (0) 和酚氧 (15) 均可作为氢键供体和受体

### 环系分析 (SD_05)
- **环 ID**: `RING_1`
- **环大小**: 6
- **原子**: [3,4,5,6,7,8] (苯环碳原子)
- **芳香性**: `true` (芳香环)
- **张力水平**: `none`
- **环类型**: `carbocycle`
- **特殊特征**: 苯环，被羧基和羟基取代

### 共轭网络映射 (SD_06)
- **π 系统 1** (PI_1):
  - 原子: [1,2,3,4,5,6,7,8,15] (羰基 + 苯环 + 酚氧)
  - 范围: `extended`
  - 类型: `extended`
  - π 电子数: 10
  - 离域程度: `partial`
  
**说明**: 水杨酸存在扩展共轭体系：
1. 羧基羰基与苯环共轭
2. 酚羟基氧孤对与苯环共轭 (+M 效应)
3. 形成羧基-苯环-酚羟基的推拉电子体系

---

## 2. 反应敏感位点 (Reactive Hotspots)

### 亲核位点 (RH_02)
识别到 3 个主要亲核位点：

| site_id | 原子索引 | 类型 | 强度 | 元素 | 说明 |
|---------|---------|------|------|------|------|
| NU_1 | 0 | n_lonepair | moderate | O | 羧酸羟基氧，可去质子化 |
| NU_2 | 1 | n_lonepair | weak | O | 羰基氧，因吸电子效应减弱 |
| NU_3 | 15 | n_lonepair | moderate | O | 酚氧，可去质子化形成酚盐 |

**强度排序**: NU_3 ≈ NU_1 > NU_2

### 亲电位点 (RH_03)
识别到 2 个主要亲电位点：

| site_id | 原子索引 | 类型 | 强度 | 说明 |
|---------|---------|------|------|------|
| E_1 | 2 | carbonyl_C | moderate | 羧基羰基碳，受邻位羟基影响 |
| E_2 | 3 | deficient_aromatic | weak | 苯环碳 (羧基邻位) |

**说明**:
- E_1: 羧基羰基碳是典型亲电位点，但酚羟基的邻位效应可能通过分子内氢键影响其反应性
- E_2: 苯环碳因羧基吸电子效应而略显缺电子

### 消除位点 (RH_04)
**无典型消除位点**
- 分子中无 β-H + LG 组合
- 羧基脱羧需高温条件，不属于常温消除

### 其他敏感位点
**分子内氢键位点**:
- 酚羟基 (O15) 与羧基羰基氧 (O1) 可能形成分子内氢键
- 这会影响酚羟基的酸性和反应性

**开环位点**: 无 (苯环稳定，不易开环)

**重排位点**: 无典型重排倾向

---

## 3. 官能团簇路由 (Functional Cluster Routing)

### 识别的官能团簇 (FC_01)

| 簇类型 | 包含的官能团 | 优先级 | 说明 |
|--------|-------------|--------|------|
| carbonyl | FG_1 | 1 | 羧基是主要官能团，决定酸性 |
| oxygen | FG_1, FG_2 | 2 | 含羧酸氧和酚氧 |
| unsaturated | FG_3 | 3 | 苯环 π 系统 |

**主要簇**: `carbonyl`

### 推荐的 PhysChem 分析模块

| 模块 ID | 推荐理由 | 优先级 | 目标位点 |
|---------|---------|--------|---------|
| LUMO_02_pi_antibond_v1 | 羧基羰基 π* 是主要还原位点 | 1 | 原子 2 (羰基碳) |
| HOMO_02_lonepair_n_v1 | 酚氧和羧酸氧孤对是氧化位点 | 2 | 原子 0, 15 |
| ELEC_03_M_pi_v1 | 酚羟基 +M 效应与羧基 -M 效应共存 | 3 | 整个共轭体系 |
| ELEC_04_hyperconj_v1 | 羧基可能存在的超共轭效应 | 4 | 羧基区域 |

### 路由建议摘要
水杨酸是具有双重官能团（羧酸 + 酚）的芳香酸，分析重点应为：
1. **羰基的还原行为** (LUMO_02)：电化学还原可能发生在羰基碳
2. **氧孤对的氧化行为** (HOMO_02)：酚氧和羧酸氧均可被氧化
3. **分子内电子效应** (ELEC_03)：邻位取代导致的特殊电子效应
4. **分子内氢键**：可能影响反应性和光谱性质

---

## 完整 YAML 输出

```yaml
output:
  task_completed: "full_digest"
  molecule_echo:
    smiles: "OC(=O)c1ccccc1O"
    name: "Salicylic Acid"
    canonical_smiles: "O=C(O)c1ccccc1O"
    formula: "C7H6O3"
    atom_count: 16
  
  structure_digest:
    skeleton:
      type: "cyclic"
      ring_count: 1
      ring_ids: ["RING_1"]
    
    functional_groups:
      - fg_id: "FG_1"
        fg_type: "carboxylic_acid"
        fg_category: "carbonyl"
        atoms: [0, 1, 2]
        center_atom: 1
        subtype: "benzoic_acid"
      
      - fg_id: "FG_2"
        fg_type: "phenol"
        fg_category: "oxygen"
        atoms: [15]
        center_atom: 15
        subtype: "ortho_phenol"
      
      - fg_id: "FG_3"
        fg_type: "benzene"
        fg_category: "unsaturated"
        atoms: [3, 4, 5, 6, 7, 8]
    
    heteroatom_labels:
      - atom_index: 0
        element: "O"
        hybridization: "sp3"
        lone_pairs: 2
        formal_charge: 0
        environment: "hydroxyl_oxygen"
        reactivity_hint: "nucleophilic"
      
      - atom_index: 1
        element: "O"
        hybridization: "sp2"
        lone_pairs: 2
        formal_charge: 0
        environment: "carbonyl_oxygen"
        reactivity_hint: "nucleophilic"
      
      - atom_index: 15
        element: "O"
        hybridization: "sp3"
        lone_pairs: 2
        formal_charge: 0
        environment: "phenol_oxygen"
        reactivity_hint: "nucleophilic"
    
    ring_info:
      - ring_id: "RING_1"
        size: 6
        atoms: [3, 4, 5, 6, 7, 8]
        aromatic: true
        strain_level: "none"
        ring_type: "carbocycle"
        saturation: "aromatic"
    
    conjugation_map:
      pi_systems:
        - system_id: "PI_1"
          atoms: [1, 2, 3, 4, 5, 6, 7, 8, 15]
          extent: "extended"
          type: "extended"
          electron_count: 10
          delocalization: "partial"
      cross_conjugated: false
      total_pi_electrons: 10
  
  reactive_hotspots:
    nucleophilic_sites:
      - site_id: "NU_1"
        atom_index: 0
        site_type: "n_lonepair"
        strength: "moderate"
        element: "O"
        lone_pairs: 2
        confidence: 0.9
        notes: "羧酸羟基氧"
      
      - site_id: "NU_2"
        atom_index: 1
        site_type: "n_lonepair"
        strength: "weak"
        element: "O"
        lone_pairs: 2
        confidence: 0.8
        notes: "羰基氧"
      
      - site_id: "NU_3"
        atom_index: 15
        site_type: "n_lonepair"
        strength: "moderate"
        element: "O"
        lone_pairs: 2
        confidence: 0.9
        notes: "酚氧"
    
    electrophilic_sites:
      - site_id: "E_1"
        atom_index: 2
        site_type: "carbonyl_C"
        strength: "moderate"
        confidence: 0.85
        notes: "羧基羰基碳"
      
      - site_id: "E_2"
        atom_index: 3
        site_type: "deficient_aromatic"
        strength: "weak"
        confidence: 0.7
        notes: "羧基邻位苯环碳"
    
    elimination_sites: []
    ring_opening_sites: []
    rearrangement_sites: []
  
  cluster_routing:
    clusters:
      - cluster_type: "carbonyl"
        functional_groups: ["FG_1"]
        priority: 1
        physchem_modules: ["LUMO_02_pi_antibond_v1"]
      
      - cluster_type: "oxygen"
        functional_groups: ["FG_1", "FG_2"]
        priority: 2
        physchem_modules: ["HOMO_02_lonepair_n_v1"]
      
      - cluster_type: "unsaturated"
        functional_groups: ["FG_3"]
        priority: 3
        physchem_modules: ["HOMO_03_pi_system_v1", "LUMO_02_pi_antibond_v1"]
    
    primary_cluster: "carbonyl"
    
    suggested_physchem_modules:
      - module_id: "LUMO_02_pi_antibond_v1"
        reason: "羧基羰基 π* 是主要还原位点"
        priority: 1
        target_sites: [2]
      
      - module_id: "HOMO_02_lonepair_n_v1"
        reason: "酚氧和羧酸氧孤对是主要氧化位点"
        priority: 2