# OrganicChem_Schema — 输入/输出数据结构定义

| Field | Value |
|-------|-------|
| Type | Schema Definition |
| Created | 2025-12-24 |
| Version | 1.0 |
| Downstream | PhysChem_Schema |

本文件定义 OrganicChem 技能库的标准输入/输出数据结构，供 Router 和各模块使用。

---

## 1. 输入 Schema

### 1.1 OrganicChemRequest（顶层输入结构）

```yaml
OrganicChemRequest:
  type: object
  required:
    - molecule
    - task_type
  properties:
    molecule:
      $ref: "#/definitions/MoleculeInput"
    task_type:
      $ref: "#/definitions/TaskType"
    options:
      $ref: "#/definitions/RequestOptions"
```

### 1.2 MoleculeInput（分子输入）

```yaml
MoleculeInput:
  type: object
  required:
    - smiles  # 至少提供 smiles 或 structure_description
  properties:
    smiles:
      type: string
      description: "分子的 SMILES 表示"
      example: "C1COC(=O)O1"
    name:
      type: string
      description: "分子名称（可选）"
      example: "Ethylene Carbonate"
    structure_description:
      type: string
      description: "结构的文字描述（当 SMILES 不可用时）"
      example: "五元环状碳酸酯，含有羰基和两个醚氧"
    inchi:
      type: string
      description: "InChI 表示（可选）"
    mol_weight:
      type: number
      description: "分子量（可选）"
```

### 1.3 TaskType（任务类型枚举）

```yaml
TaskType:
  type: string
  enum:
    - structure_digest      # 结构解剖与标签化
    - reactive_hotspots     # 反应敏感位点识别
    - cluster_routing       # 官能团簇路由
    - full_digest           # 完整解析
  description: "指定要执行的分析任务类型"
```

### 1.4 RequestOptions（请求选项）

```yaml
RequestOptions:
  type: object
  properties:
    include_hotspots:
      type: boolean
      default: true
      description: "是否包含敏感位点分析"
    include_clustering:
      type: boolean
      default: true
      description: "是否包含官能团簇路由"
    output_format:
      type: string
      enum: ["yaml", "json"]
      default: "yaml"
      description: "输出格式"
    verbosity:
      type: string
      enum: ["concise", "detailed"]
      default: "concise"
      description: "输出详细程度"
    target_atoms:
      type: array
      items:
        type: integer
      description: "只关注的特定原子索引（可选）"
    skip_modules:
      type: array
      items:
        type: string
      description: "跳过的模块 ID 列表"
```

---

## 2. 输出 Schema

### 2.1 OrganicChemResponse（顶层输出结构）

```yaml
OrganicChemResponse:
  type: object
  required:
    - task_completed
    - molecule_echo
    - overall_confidence
  properties:
    task_completed:
      $ref: "#/definitions/TaskType"
    molecule_echo:
      $ref: "#/definitions/MoleculeEcho"
    structure_digest:
      $ref: "#/definitions/StructureDigestOutput"
    reactive_hotspots:
      $ref: "#/definitions/ReactiveHotspotsOutput"
    cluster_routing:
      $ref: "#/definitions/ClusterRoutingOutput"
    notes:
      type: string
      description: "补充说明"
    warnings:
      type: array
      items:
        type: string
      description: "警告信息"
    overall_confidence:
      $ref: "#/definitions/ConfidenceLevel"
```

### 2.2 MoleculeEcho（分子回显）

```yaml
MoleculeEcho:
  type: object
  properties:
    smiles:
      type: string
    name:
      type: string
    canonical_smiles:
      type: string
      description: "标准化后的 SMILES"
    formula:
      type: string
      description: "分子式"
    atom_count:
      type: integer
      description: "原子总数"
```

---

## 3. 结构解剖输出 Schema

### 3.1 StructureDigestOutput

```yaml
StructureDigestOutput:
  type: object
  properties:
    skeleton:
      $ref: "#/definitions/SkeletonInfo"
    functional_groups:
      type: array
      items:
        $ref: "#/definitions/FunctionalGroupInfo"
    heteroatom_labels:
      type: array
      items:
        $ref: "#/definitions/HeteroatomLabel"
    ring_info:
      type: array
      items:
        $ref: "#/definitions/RingInfo"
    conjugation_map:
      $ref: "#/definitions/ConjugationMap"
```

### 3.2 SkeletonInfo（骨架信息）

```yaml
SkeletonInfo:
  type: object
  properties:
    type:
      type: string
      enum: ["linear", "branched", "cyclic", "polycyclic", "bridged", "spiro"]
      description: "骨架类型"
    main_chain_length:
      type: integer
      description: "主链碳原子数（若适用）"
    ring_count:
      type: integer
      description: "环数量"
    ring_ids:
      type: array
      items:
        type: string
      description: "环的唯一标识符列表"
    bridgehead_atoms:
      type: array
      items:
        type: integer
      description: "桥头原子索引"
    spiro_centers:
      type: array
      items:
        type: integer
      description: "螺原子索引"
```

### 3.3 FunctionalGroupInfo（官能团信息）

```yaml
FunctionalGroupInfo:
  type: object
  required:
    - fg_id
    - fg_type
    - atoms
  properties:
    fg_id:
      type: string
      description: "唯一标识符"
      example: "FG_1"
    fg_type:
      type: string
      description: "官能团类型"
      example: "ester"
    fg_category:
      type: string
      enum: ["carbonyl", "nitrogen", "oxygen", "halogen", "sulfur", "phosphorus", "unsaturated", "other"]
      description: "官能团大类"
    atoms:
      type: array
      items:
        type: integer
      description: "包含的原子索引"
    center_atom:
      type: integer
      description: "中心原子索引"
    subtype:
      type: string
      description: "子类型"
      example: "methyl_ester"
    smarts:
      type: string
      description: "匹配的 SMARTS 模式"
```

### 3.4 HeteroatomLabel（杂原子标签）

```yaml
HeteroatomLabel:
  type: object
  required:
    - atom_index
    - element
  properties:
    atom_index:
      type: integer
      description: "原子索引"
    element:
      type: string
      description: "元素符号"
      example: "O"
    hybridization:
      type: string
      enum: ["sp", "sp2", "sp3"]
      description: "杂化类型"
    lone_pairs:
      type: integer
      description: "孤对电子数"
    formal_charge:
      type: integer
      description: "形式电荷"
    environment:
      type: string
      description: "周围环境描述"
      example: "carbonyl_oxygen"
    coordination:
      type: string
      description: "配位状态（若有）"
```

### 3.5 RingInfo（环信息）

```yaml
RingInfo:
  type: object
  required:
    - ring_id
    - size
    - atoms
  properties:
    ring_id:
      type: string
      description: "唯一标识符"
      example: "RING_1"
    size:
      type: integer
      description: "环大小"
    atoms:
      type: array
      items:
        type: integer
      description: "环上原子索引"
    aromatic:
      type: boolean
      description: "是否芳香"
    strain_level:
      type: string
      enum: ["none", "low", "medium", "high"]
      description: "张力水平"
    ring_type:
      type: string
      enum: ["carbocycle", "heterocycle", "fused", "bridged", "spiro"]
      description: "环类型"
    heteroatoms:
      type: array
      items:
        type: string
      description: "环上的杂原子列表"
    fusion_partner:
      type: string
      description: "稠合环的伙伴 ring_id（若有）"
```

### 3.6 ConjugationMap（共轭映射）

```yaml
ConjugationMap:
  type: object
  properties:
    pi_systems:
      type: array
      items:
        $ref: "#/definitions/PiSystem"
    cross_conjugated:
      type: boolean
      description: "是否存在交叉共轭"
    total_conjugation_length:
      type: integer
      description: "最长共轭链的原子数"
```

### 3.7 PiSystem（π 系统）

```yaml
PiSystem:
  type: object
  properties:
    system_id:
      type: string
      description: "唯一标识符"
    atoms:
      type: array
      items:
        type: integer
      description: "参与共轭的原子索引"
    extent:
      type: string
      enum: ["local", "extended", "aromatic"]
      description: "共轭范围"
    type:
      type: string
      enum: ["alkene", "alkyne", "carbonyl", "aromatic", "heterocyclic", "extended"]
      description: "π 系统类型"
```

---

## 4. 敏感位点输出 Schema

### 4.1 ReactiveHotspotsOutput

```yaml
ReactiveHotspotsOutput:
  type: object
  properties:
    nucleophilic_sites:
      type: array
      items:
        $ref: "#/definitions/NucleophilicSite"
    electrophilic_sites:
      type: array
      items:
        $ref: "#/definitions/ElectrophilicSite"
    elimination_sites:
      type: array
      items:
        $ref: "#/definitions/EliminationSite"
    ring_opening_sites:
      type: array
      items:
        $ref: "#/definitions/RingOpeningSite"
    rearrangement_sites:
      type: array
      items:
        $ref: "#/definitions/RearrangementSite"
```

### 4.2 NucleophilicSite（亲核位点）

```yaml
NucleophilicSite:
  type: object
  required:
    - site_id
    - atom_index
    - site_type
  properties:
    site_id:
      type: string
      description: "唯一标识符"
    atom_index:
      type: integer
      description: "原子索引"
    site_type:
      type: string
      enum: ["n_lonepair", "pi_system", "anion", "enolate", "carbanion", "hydride"]
      description: "亲核类型"
    strength:
      type: string
      enum: ["strong", "moderate", "weak"]
      description: "亲核强度"
    orbital_type:
      type: string
      enum: ["n", "pi", "sigma"]
      description: "轨道类型"
    confidence:
      type: number
      minimum: 0
      maximum: 1
      description: "置信度"
    notes:
      type: string
      description: "补充说明"
```

### 4.3 ElectrophilicSite（亲电位点）

```yaml
ElectrophilicSite:
  type: object
  required:
    - site_id
    - atom_index
    - site_type
  properties:
    site_id:
      type: string
      description: "唯一标识符"
    atom_index:
      type: integer
      description: "原子索引"
    site_type:
      type: string
      enum: ["carbonyl_C", "sp3_with_LG", "deficient_aromatic", "carbocation_potential", "michael_acceptor", "imine_C"]
      description: "亲电类型"
    strength:
      type: string
      enum: ["strong", "moderate", "weak"]
      description: "亲电强度"
    leaving_group:
      type: string
      description: "离去基团类型（若有）"
    confidence:
      type: number
      minimum: 0
      maximum: 1
      description: "置信度"
    notes:
      type: string
      description: "补充说明"
```

### 4.4 EliminationSite（消除位点）

```yaml
EliminationSite:
  type: object
  required:
    - site_id
    - c_alpha
    - c_beta
  properties:
    site_id:
      type: string
      description: "唯一标识符"
    c_alpha:
      type: integer
      description: "α 碳索引（连接离去基团）"
    c_beta:
      type: integer
      description: "β 碳索引（连接 β-H）"
    leaving_group:
      type: string
      description: "离去基团类型"
    beta_h_count:
      type: integer
      description: "β 氢的数量"
    mechanism_preference:
      type: string
      enum: ["E2", "E1cb", "E1", "competing"]
      description: "优选机理"
    antiperiplanar_available:
      type: boolean
      description: "是否有反式共平面构象"
    confidence:
      type: number
      minimum: 0
      maximum: 1
      description: "置信度"
```

### 4.5 RingOpeningSite（开环位点）

```yaml
RingOpeningSite:
  type: object
  required:
    - site_id
    - ring_id
  properties:
    site_id:
      type: string
      description: "唯一标识符"
    ring_id:
      type: string
      description: "对应的环 ID"
    attack_atom:
      type: integer
      description: "被攻击的原子索引"
    ring_type:
      type: string
      enum: ["epoxide", "lactone", "cyclic_carbonate", "aziridine", "lactam", "small_ring", "strained_ring"]
      description: "环类型"
    strain_driven:
      type: boolean
      description: "是否由环张力驱动"
    regioselectivity:
      type: string
      description: "区域选择性说明"
    confidence:
      type: number
      minimum: 0
      maximum: 1
      description: "置信度"
```

### 4.6 RearrangementSite（重排位点）

```yaml
RearrangementSite:
  type: object
  required:
    - site_id
    - rearrangement_type
  properties:
    site_id:
      type: string
      description: "唯一标识符"
    migrating_group:
      type: string
      description: "迁移基团描述"
    origin_atom:
      type: integer
      description: "起始原子索引"
    destination_atom:
      type: integer
      description: "目标原子索引"
    rearrangement_type:
      type: string
      enum: ["1,2-hydride", "1,2-methyl", "1,2-aryl", "Wagner-Meerwein", "pinacol", "Cope", "Claisen", "oxy-Cope", "other"]
      description: "重排类型"
    driving_force:
      type: string
      description: "驱动力说明"
    confidence:
      type: number
      minimum: 0
      maximum: 1
      description: "置信度"
```

---

## 5. 官能团簇路由输出 Schema

### 5.1 ClusterRoutingOutput

```yaml
ClusterRoutingOutput:
  type: object
  properties:
    clusters:
      type: array
      items:
        $ref: "#/definitions/FunctionalCluster"
    primary_cluster:
      type: string
      description: "主要官能团簇类型"
    suggested_physchem_modules:
      type: array
      items:
        $ref: "#/definitions/PhysChemSuggestion"
```

### 5.2 FunctionalCluster（官能团簇）

```yaml
FunctionalCluster:
  type: object
  required:
    - cluster_type
    - functional_groups
  properties:
    cluster_type:
      type: string
      enum: ["carbonyl", "nitrogen", "oxygen", "halogen", "sulfur_phosphorus", "unsaturated"]
      description: "簇类型"
    functional_groups:
      type: array
      items:
        type: string
      description: "属于该簇的官能团 ID 列表"
    priority:
      type: integer
      description: "优先级（1 = 最高）"
    physchem_modules:
      type: array
      items:
        type: string
      description: "推荐的 PhysChem 模块 ID 列表"
    notes:
      type: string
      description: "补充说明"
```

### 5.3 PhysChemSuggestion（PhysChem 建议）

```yaml
PhysChemSuggestion:
  type: object
  required:
    - module_id
    - reason
  properties:
    module_id:
      type: string
      description: "PhysChem 模块 ID"
      example: "HOMO_02_lonepair_n_v1"
    reason:
      type: string
      description: "推荐理由"
    priority:
      type: integer
      description: "优先级（1 = 最高）"
    target_sites:
      type: array
      items:
        type: integer
      description: "相关的原子索引"
```

---

## 6. 通用定义

### 6.1 ConfidenceLevel（置信度）

```yaml
ConfidenceLevel:
  type: string
  enum: ["high", "medium", "low"]
  description: |
    置信度定义：
    - high: 结构明确，解析可靠
    - medium: 结构基本清晰，部分细节存在不确定性
    - low: 结构复杂或信息不足，建议人工复核
```

---

## 7. 示例

### 7.1 完整请求示例

```yaml
input:
  molecule:
    smiles: "C1COC(=O)O1"
    name: "Ethylene Carbonate"
  task_type: "full_digest"
  options:
    include_hotspots: true
    include_clustering: true
    verbosity: "detailed"
```

### 7.2 完整响应示例

```yaml
output:
  task_completed: "full_digest"
  molecule_echo:
    smiles: "C1COC(=O)O1"
    name: "Ethylene Carbonate"
    canonical_smiles: "O=C1OCCO1"
    formula: "C3H4O3"
    atom_count: 10
  
  structure_digest:
    skeleton:
      type: "cyclic"
      ring_count: 1
      ring_ids: ["RING_1"]
    
    functional_groups:
      - fg_id: "FG_1"
        fg_type: "cyclic_carbonate"
        fg_category: "carbonyl"
        atoms: [1, 2, 3, 4, 5]
        center_atom: 1
        subtype: "5-membered_cyclic_carbonate"
    
    heteroatom_labels:
      - atom_index: 2
        element: "O"
        hybridization: "sp3"
        lone_pairs: 2
        formal_charge: 0
        environment: "ether_oxygen"
      - atom_index: 3
        element: "O"
        hybridization: "sp2"
        lone_pairs: 2
        formal_charge: 0
        environment: "carbonyl_oxygen"
      - atom_index: 5
        element: "O"
        hybridization: "sp3"
        lone_pairs: 2
        formal_charge: 0
        environment: "ether_oxygen"
    
    ring_info:
      - ring_id: "RING_1"
        size: 5
        atoms: [1, 2, 4, 5, 6]
        aromatic: false
        strain_level: "low"
        ring_type: "heterocycle"
        heteroatoms: ["O", "O"]
    
    conjugation_map:
      pi_systems:
        - system_id: "PI_1"
          atoms: [1, 3]
          extent: "local"
          type: "carbonyl"
      cross_conjugated: false
  
  reactive_hotspots:
    nucleophilic_sites:
      - site_id: "NU_1"
        atom_index: 2
        site_type: "n_lonepair"
        strength: "moderate"
        confidence: 0.8
        notes: "醚氧孤对"
      - site_id: "NU_2"
        atom_index: 5
        site_type: "n_lonepair"
        strength: "moderate"
        confidence: 0.8
        notes: "醚氧孤对"
    
    electrophilic_sites:
      - site_id: "E_1"
        atom_index: 1
        site_type: "carbonyl_C"
        strength: "strong"
        confidence: 0.95
        notes: "羰基碳，易受亲核攻击"
    
    ring_opening_sites:
      - site_id: "RO_1"
        ring_id: "RING_1"
        attack_atom: 1
        ring_type: "cyclic_carbonate"
        strain_driven: true
        confidence: 0.9
        regioselectivity: "亲核进攻羰基碳，酰氧键断裂"
  
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
        reason: "羰基 π* 反键是主要还原位点"
        priority: 1
        target_sites: [1]
      - module_id: "HOMO_02_lonepair_n_v1"
        reason: "醚氧孤对是主要氧化位点"
        priority: 2
        target_sites: [2, 5]
      - module_id: "LUMO_04_ring_strain_v1"
        reason: "五元环存在一定张力"
        priority: 3
  
  notes: "典型五元环状碳酸酯，羰基为主要反应中心"
  warnings: []
  overall_confidence: "high"
```

---

## 8. 版本兼容性

| Schema 版本 | 兼容的 Router 版本 | 兼容的 PhysChem Schema |
|-------------|-------------------|----------------------|
| 1.0 | 1.0+ | 1.0+ |

---

## 9. Changelog

- 2025-12-24: 初始版本 v1.0

