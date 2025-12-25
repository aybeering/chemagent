# EleChem_Schema — 输入/输出数据结构定义

| Field | Value |
|-------|-------|
| Type | Schema Definition |
| Created | 2025-12-25 |
| Version | 1.0 |
| Upstream | OrganicChem_Schema, PhysChem_Schema |

本文件定义 EleChem 技能库的标准输入/输出数据结构，供 Router 和各模块使用。

---

## 1. 输入 Schema

### 1.1 EleChemRequest（顶层输入结构）

```yaml
EleChemRequest:
  type: object
  required:
    - molecule
    - task_type
    - upstream
  properties:
    molecule:
      $ref: "#/definitions/MoleculeInput"
    task_type:
      $ref: "#/definitions/TaskType"
    upstream:
      $ref: "#/definitions/UpstreamInput"
    context:
      $ref: "#/definitions/TaskContext"
    options:
      $ref: "#/definitions/RequestOptions"
```

### 1.2 MoleculeInput（分子输入）

```yaml
MoleculeInput:
  type: object
  required:
    - smiles
  properties:
    smiles:
      type: string
      description: "分子的 SMILES 表示"
      example: "C1COC(=O)O1"
    name:
      type: string
      description: "分子名称（可选）"
      example: "Ethylene Carbonate"
    functional_groups:
      type: array
      items:
        type: string
      description: "预识别的官能团列表（可选）"
      example: ["cyclic_carbonate", "ester", "ether"]
```

### 1.3 TaskType（任务类型枚举）

```yaml
TaskType:
  type: string
  enum:
    - role_hypothesis        # 角色假设
    - sei_pathway           # SEI 路径分析
    - cei_risk              # CEI 风险评估
    - gassing_polymer_risk  # 产气/聚合风险
    - full_assessment       # 完整评估
  description: "指定要执行的分析任务类型"
```

### 1.4 UpstreamInput（上游输入）

```yaml
UpstreamInput:
  type: object
  required:
    - organic_chem
    - phys_chem
  properties:
    organic_chem:
      $ref: "#/definitions/OrganicChemOutput"
    phys_chem:
      $ref: "#/definitions/PhysChemOutput"
  description: "从 OrganicChem 和 PhysChem 获取的上游输出"

OrganicChemOutput:
  type: object
  properties:
    structure_digest:
      type: object
      properties:
        functional_groups:
          type: array
          items:
            $ref: "#/definitions/FunctionalGroup"
        ring_info:
          type: array
          items:
            type: object
        heteroatom_labels:
          type: array
          items:
            type: object
    reactive_hotspots:
      type: object
      properties:
        electrophilic_sites:
          type: array
        nucleophilic_sites:
          type: array
        ring_opening_sites:
          type: array
    cluster_routing:
      type: object
      properties:
        clusters:
          type: array
        suggested_physchem_modules:
          type: array

PhysChemOutput:
  type: object
  properties:
    oxidation_tendency:
      type: object
      properties:
        ox_sites_ranked:
          type: array
        dominant_site:
          type: string
    reduction_tendency:
      type: object
      properties:
        red_sites_ranked:
          type: array
        dominant_site:
          type: string
    interface_ranking:
      type: object
      properties:
        cathode:
          type: array
        anode:
          type: array
```

### 1.5 TaskContext（任务上下文）

```yaml
TaskContext:
  type: object
  properties:
    electrode:
      type: string
      enum: ["cathode", "anode", "both"]
      default: "both"
      description: "关注的电极类型"
    electrode_material:
      type: string
      enum: ["NCM", "NCA", "LCO", "LFP", "Li", "Graphite", "Si", "other"]
      description: "电极材料"
    voltage_range:
      type: string
      enum: ["high", "normal", "deep_reduction"]
      default: "normal"
      description: |
        电位范围：
        - high: >4.3V vs Li/Li+（高压正极）
        - normal: 2.5-4.3V（常规）
        - deep_reduction: <0.5V（深度还原，如负极首次锂化）
    electrolyte_system:
      type: string
      enum: ["conventional", "LHCE", "solid"]
      default: "conventional"
      description: "电解液体系类型"
    temperature:
      type: number
      description: "温度（K），默认 298K"
      default: 298
```

### 1.6 RequestOptions（请求选项）

```yaml
RequestOptions:
  type: object
  properties:
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
```

---

## 2. 输出 Schema

### 2.1 EleChemResponse（顶层输出结构）

```yaml
EleChemResponse:
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
    role_hypothesis:
      $ref: "#/definitions/RoleOutput"
    sei_pathway:
      $ref: "#/definitions/SEIOutput"
    cei_risk:
      $ref: "#/definitions/CEIOutput"
    gassing_polymer_risk:
      $ref: "#/definitions/GasOutput"
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
    identified_groups:
      type: array
      items:
        type: string
      description: "分析过程中识别的官能团"
```

---

## 3. 模块输出 Schema

### 3.1 RoleOutput（角色假设模块输出）

```yaml
RoleOutput:
  type: object
  properties:
    primary_role:
      type: string
      enum: ["solvent", "film_additive", "diluent", "unsuitable"]
      description: "主要角色假设"
    confidence:
      $ref: "#/definitions/ConfidenceLevel"
    evidence:
      type: array
      items:
        type: string
      description: "支持该角色的结构证据"
    alternatives:
      type: array
      items:
        $ref: "#/definitions/AlternativeRole"
      description: "备选角色"
    unsuitable_flags:
      type: array
      items:
        $ref: "#/definitions/UnsuitableFlag"
      description: "不适合标记"

AlternativeRole:
  type: object
  properties:
    role:
      type: string
      enum: ["solvent", "film_additive", "diluent"]
    confidence:
      $ref: "#/definitions/ConfidenceLevel"
    condition:
      type: string
      description: "适用条件"

UnsuitableFlag:
  type: object
  properties:
    flag_id:
      type: string
    reason:
      type: string
      description: "不适合的原因"
```

### 3.2 SEIOutput（SEI 路径模块输出）

```yaml
SEIOutput:
  type: object
  properties:
    primary_pathway:
      type: string
      enum: ["polymer_film", "inorganic_salt", "lif_rich", "mixed"]
      description: "主要 SEI 路径"
    pathways:
      type: object
      properties:
        polymer_film:
          $ref: "#/definitions/PathwayDetail"
        inorganic_salt:
          $ref: "#/definitions/PathwayDetail"
        lif:
          $ref: "#/definitions/LiFDetail"
    film_composition_hint:
      type: string
      description: "SEI 组成定性描述"
    mechanism_summary:
      type: string
      description: "整体成膜机理摘要"
    confidence:
      $ref: "#/definitions/ConfidenceLevel"

PathwayDetail:
  type: object
  properties:
    likelihood:
      type: string
      enum: ["high", "medium", "low", "none"]
    mechanism:
      type: string
      description: "机理类型"
    products_hint:
      type: array
      items:
        type: string
      description: "可能产物提示"

LiFDetail:
  type: object
  properties:
    likelihood:
      type: string
      enum: ["high", "medium", "low", "none"]
    f_source:
      type: string
      description: "F 来源描述"
```

### 3.3 CEIOutput（CEI 风险模块输出）

```yaml
CEIOutput:
  type: object
  properties:
    risk_level:
      type: string
      enum: ["high", "medium", "low"]
      description: "整体风险等级"
    oxidation_sites:
      type: array
      items:
        $ref: "#/definitions/OxidationSite"
      description: "易氧化位点列表"
    side_reactions:
      type: array
      items:
        $ref: "#/definitions/SideReaction"
      description: "可能的副反应"
    mitigation_hints:
      type: array
      items:
        type: string
      description: "缓解措施建议"
    confidence:
      $ref: "#/definitions/ConfidenceLevel"

OxidationSite:
  type: object
  properties:
    site:
      type: string
      description: "位点描述"
    site_type:
      type: string
      description: "位点类型（n/pi/sigma_CH）"
    reason:
      type: string
      description: "易氧化原因"

SideReaction:
  type: object
  properties:
    reaction_type:
      type: string
      enum: ["dehydrogenation", "ring_opening", "polymerization", "decomposition", "other"]
    likelihood:
      type: string
      enum: ["high", "medium", "low"]
    description:
      type: string
      description: "反应描述"
```

### 3.4 GasOutput（产气/聚合风险模块输出）

```yaml
GasOutput:
  type: object
  properties:
    gas_flags:
      type: array
      items:
        $ref: "#/definitions/GasFlag"
      description: "产气风险红旗"
    polymer_flags:
      type: array
      items:
        $ref: "#/definitions/PolymerFlag"
      description: "聚合风险红旗"
    overall_risk:
      type: string
      enum: ["high", "medium", "low"]
      description: "整体风险等级"
    safety_notes:
      type: string
      description: "安全性说明"

GasFlag:
  type: object
  properties:
    gas_type:
      type: string
      enum: ["CO2", "CO", "H2", "HF", "C2H4", "other"]
      description: "气体类型"
    source:
      type: string
      description: "产气来源"
    likelihood:
      type: string
      enum: ["high", "medium", "low"]
    trigger:
      type: string
      description: "触发条件"

PolymerFlag:
  type: object
  properties:
    risk_type:
      type: string
      enum: ["radical_chain", "crosslinking", "uncontrolled"]
      description: "聚合风险类型"
    source:
      type: string
      description: "聚合源"
    likelihood:
      type: string
      enum: ["high", "medium", "low"]
    trigger:
      type: string
      description: "触发条件"
```

---

## 4. 通用定义

### 4.1 FunctionalGroup（官能团）

```yaml
FunctionalGroup:
  type: object
  properties:
    fg_id:
      type: string
    fg_type:
      type: string
      description: "官能团类型"
    fg_category:
      type: string
      enum: ["carbonyl", "nitrogen", "oxygen", "halogen", "sulfur", "phosphorus", "unsaturated"]
    atoms:
      type: array
      items:
        type: integer
```

### 4.2 ConfidenceLevel（置信度）

```yaml
ConfidenceLevel:
  type: string
  enum: ["high", "medium", "low"]
  description: |
    置信度定义：
    - high: 结论明确，基于清晰的结构特征和成熟规则
    - medium: 结论可能，但存在竞争因素或边界情况
    - low: 结论不确定，建议补充计算或实验验证
```

---

## 5. 示例

### 5.1 完整请求示例

```yaml
# 请求：评估 FEC 的完整电化学机理
input:
  molecule:
    smiles: "FC1COC(=O)O1"
    name: "Fluoroethylene Carbonate"
    functional_groups: ["cyclic_carbonate", "C-F"]
  task_type: "full_assessment"
  upstream:
    organic_chem:
      structure_digest:
        functional_groups:
          - { fg_id: "FG_1", fg_type: "cyclic_carbonate", fg_category: "carbonyl" }
          - { fg_id: "FG_2", fg_type: "C-F", fg_category: "halogen" }
        ring_info:
          - { ring_id: "RING_1", size: 5, aromatic: false, strain_level: "low" }
      reactive_hotspots:
        electrophilic_sites:
          - { atom_index: 3, site_type: "carbonyl_C" }
        ring_opening_sites:
          - { ring_type: "cyclic_carbonate", strain_driven: true }
    phys_chem:
      reduction_tendency:
        red_sites_ranked:
          - { rank: 1, site: "羰基 C=O", lumo_type: "pi_star" }
          - { rank: 2, site: "C-F 键", lumo_type: "sigma_star" }
        dominant_site: "羰基 C=O"
      oxidation_tendency:
        ox_sites_ranked:
          - { rank: 1, site: "酯氧孤对", homo_type: "n" }
  context:
    electrode: "anode"
    electrode_material: "Li"
    voltage_range: "deep_reduction"
  options:
    verbosity: "detailed"
```

### 5.2 完整响应示例

```yaml
output:
  task_completed: "full_assessment"
  molecule_echo:
    smiles: "FC1COC(=O)O1"
    name: "Fluoroethylene Carbonate"
    identified_groups: ["cyclic_carbonate", "C-F"]
  
  role_hypothesis:
    primary_role: "film_additive"
    confidence: "high"
    evidence:
      - "含 C-F 键，可释放 F⁻ 促进 LiF 形成"
      - "环状碳酸酯结构，优先于 EC 还原"
      - "小用量即可显著改善 SEI 质量"
    alternatives:
      - role: "solvent"
        confidence: "low"
        condition: "仅作为共溶剂使用，通常用量 <10%"
    unsuitable_flags: []
  
  sei_pathway:
    primary_pathway: "mixed"
    pathways:
      polymer_film:
        likelihood: "high"
        mechanism: "ring_opening"
        products_hint: ["聚碳酸酯", "烷基锂"]
      inorganic_salt:
        likelihood: "medium"
        products_hint: ["Li2CO3", "Li2O"]
      lif:
        likelihood: "high"
        f_source: "C-F 键还原断裂释放 F⁻"
    film_composition_hint: "LiF 富集 + 有机聚合物混合 SEI"
    mechanism_summary: "FEC 优先还原开环，同时 C-F 断裂释放 F⁻ 形成 LiF，产生柔性且离子导电的 SEI"
    confidence: "high"
  
  cei_risk:
    risk_level: "low"
    oxidation_sites:
      - site: "酯氧孤对"
        site_type: "n"
        reason: "HOMO 贡献，但被 F 的 -I 略降"
    side_reactions:
      - reaction_type: "dehydrogenation"
        likelihood: "low"
        description: "高压下可能脱氢，但 F 取代增加氧化稳定性"
    mitigation_hints:
      - "控制正极电位 <4.5V 可降低氧化风险"
    confidence: "high"
  
  gassing_polymer_risk:
    gas_flags:
      - gas_type: "CO2"
        source: "碳酸酯开环分解"
        likelihood: "medium"
        trigger: "首次锂化时还原开环"
      - gas_type: "HF"
        source: "C-F 断裂后与痕量水反应"
        likelihood: "low"
        trigger: "电解液含水量高时"
    polymer_flags:
      - risk_type: "radical_chain"
        source: "开环中间体"
        likelihood: "low"
        trigger: "通常形成稳定的 SEI 膜，不失控"
    overall_risk: "low"
    safety_notes: "FEC 是成熟添加剂，正常使用下产气风险可控"
  
  notes: "FEC 是典型的成膜添加剂，通过优先还原和 LiF 形成改善 SEI 质量"
  warnings: []
  overall_confidence: "high"
```

---

## 6. 版本兼容性

| Schema 版本 | 兼容的 Router 版本 | 兼容的上游 Schema |
|-------------|-------------------|------------------|
| 1.0 | 1.0+ | OrganicChem 1.0+, PhysChem 1.0+ |

---

## 7. Changelog

- 2025-12-25: 初始版本 v1.0

