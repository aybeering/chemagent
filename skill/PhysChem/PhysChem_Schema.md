# PhysChem_Schema — 输入/输出数据结构定义

| Field | Value |
|-------|-------|
| Type | Schema Definition |
| Created | 2025-12-24 |
| Version | 1.0 |

本文件定义 PhysChem 技能库的标准输入/输出数据结构，供 Router 和各模块使用。

---

## 1. 输入 Schema

### 1.1 PhysChemRequest（顶层输入结构）

```yaml
PhysChemRequest:
  type: object
  required:
    - molecule
    - task_type
  properties:
    molecule:
      $ref: "#/definitions/MoleculeInput"
    task_type:
      $ref: "#/definitions/TaskType"
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
    structure_description:
      type: string
      description: "结构的文字描述（当 SMILES 不可用时）"
      example: "五元环状碳酸酯，含有羰基和两个醚氧"
```

### 1.3 TaskType（任务类型枚举）

```yaml
TaskType:
  type: string
  enum:
    - electronic_effect      # 电子效应分析
    - oxidation_tendency     # 氧化倾向评估
    - reduction_tendency     # 还原倾向评估
    - interface_ranking      # 界面优先位点排序
    - stability_check        # 稳定性校验
    - full_assessment        # 完整评估
  description: "指定要执行的分析任务类型"
```

### 1.4 TaskContext（任务上下文）

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
    environment:
      type: string
      enum: ["bulk", "interface"]
      default: "bulk"
      description: "分析环境：体相溶液 vs 电极界面"
    temperature:
      type: number
      description: "温度（K），默认 298K"
      default: 298
```

### 1.5 RequestOptions（请求选项）

```yaml
RequestOptions:
  type: object
  properties:
    include_trade_check:
      type: boolean
      default: true
      description: "是否在输出中附加 TRADE 模块的校验警示"
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
    target_sites:
      type: array
      items:
        type: string
      description: "只关注的特定位点（可选，默认全部评估）"
      example: ["C1", "O2", "carbonyl"]
```

---

## 2. 输出 Schema

### 2.1 PhysChemResponse（顶层输出结构）

```yaml
PhysChemResponse:
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
    electronic_effect:
      $ref: "#/definitions/ElecOutput"
    oxidation_tendency:
      $ref: "#/definitions/HomoOutput"
    reduction_tendency:
      $ref: "#/definitions/LumoOutput"
    interface_ranking:
      $ref: "#/definitions/IntfOutput"
    tradeoff_warnings:
      $ref: "#/definitions/TradeOutput"
    notes:
      type: string
      description: "补充说明"
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

### 3.1 ElecOutput（电子效应模块输出）

```yaml
ElecOutput:
  type: object
  properties:
    effect_summary:
      type: string
      description: "净效应的总结描述"
      example: "CF₃ 对邻近位点为强 -I 吸电子，无 π 共振通道"
    channels:
      type: object
      properties:
        I:
          $ref: "#/definitions/IChannelResult"
        M:
          $ref: "#/definitions/MChannelResult"
        hyperconj:
          $ref: "#/definitions/HyperconjResult"
        field:
          $ref: "#/definitions/FieldResult"
        conformation:
          $ref: "#/definitions/ConformationResult"
    dominant_channel:
      type: string
      enum: ["I", "M", "hyperconj", "field", "mixed"]
    transmission_path:
      type: string
      description: "电子效应传播路径描述"
    dominant_sites:
      type: array
      items:
        type: string
      description: "受电子效应影响最显著的位点"
    confidence:
      $ref: "#/definitions/ConfidenceLevel"

IChannelResult:
  type: object
  properties:
    active:
      type: boolean
    direction:
      type: string
      enum: ["+I", "-I"]
    strength:
      $ref: "#/definitions/EffectStrength"
    decay:
      type: string
      description: "衰减描述"
      example: "经 3 键后衰减约 90%"

MChannelResult:
  type: object
  properties:
    active:
      type: boolean
    direction:
      type: string
      enum: ["+M", "-M"]
    strength:
      $ref: "#/definitions/EffectStrength"
    selectivity:
      type: string
      description: "位置选择性（芳环）"
      example: "o/p 位电子密度增加"

HyperconjResult:
  type: object
  properties:
    active:
      type: boolean
    description:
      type: string
      example: "苄位 C-H 的 σ 电子与芳环 π* 耦合"

FieldResult:
  type: object
  properties:
    active:
      type: boolean
    description:
      type: string
      example: "近邻偶极造成空间极化"

ConformationResult:
  type: object
  properties:
    conjugation_status:
      type: string
      enum: ["ON", "OFF", "PARTIAL"]
    description:
      type: string
      example: "扭转角约 45°，共振效应部分降权"
```

### 3.2 HomoOutput（氧化倾向模块输出）

```yaml
HomoOutput:
  type: object
  properties:
    ox_sites_ranked:
      type: array
      items:
        $ref: "#/definitions/RankedSite"
      description: "按氧化倾向排序的位点列表"
    dominant_site:
      type: string
      description: "最易氧化的位点"
    dominant_homo_type:
      type: string
      enum: ["n", "pi", "sigma_CH", "mixed"]
    substituent_effects:
      type: string
      description: "取代基对 HOMO 的调制摘要"
    interface_modifier:
      type: string
      description: "界面环境修正说明"
    confidence:
      $ref: "#/definitions/ConfidenceLevel"
```

### 3.3 LumoOutput（还原倾向模块输出）

```yaml
LumoOutput:
  type: object
  properties:
    red_sites_ranked:
      type: array
      items:
        $ref: "#/definitions/RankedSite"
      description: "按还原倾向排序的位点列表"
    dominant_site:
      type: string
      description: "最易还原的位点"
    dominant_lumo_type:
      type: string
      enum: ["pi_star", "sigma_star", "ring_strain", "mixed"]
    substituent_effects:
      type: string
      description: "取代基对 LUMO 的调制摘要"
    interface_modifier:
      type: string
      description: "界面环境修正说明"
    confidence:
      $ref: "#/definitions/ConfidenceLevel"
```

### 3.4 IntfOutput（界面位点模块输出）

```yaml
IntfOutput:
  type: object
  properties:
    cathode:
      type: array
      items:
        $ref: "#/definitions/RankedSite"
      description: "正极界面优先位点排序"
    anode:
      type: array
      items:
        $ref: "#/definitions/RankedSite"
      description: "负极界面优先位点排序"
    competition_notes:
      type: string
      description: "多位点竞争判定说明"
    film_hint:
      type: string
      description: "SEI/CEI 成膜倾向提示"
    confidence:
      $ref: "#/definitions/ConfidenceLevel"
```

### 3.5 TradeOutput（稳定性权衡模块输出）

```yaml
TradeOutput:
  type: object
  properties:
    triggered_pitfalls:
      type: array
      items:
        $ref: "#/definitions/PitfallWarning"
      description: "触发的误判警示列表"
    confidence_adjustment:
      type: string
      enum: ["none", "lowered", "requires_review"]
      description: "对主结论置信度的调整建议"
    review_notes:
      type: string
      description: "需要人工复核的说明"

PitfallWarning:
  type: object
  properties:
    pitfall_id:
      type: string
      enum: ["TRADE_01", "TRADE_02", "TRADE_03", "TRADE_04", "TRADE_05"]
    warning:
      type: string
      description: "警示内容"
    applies_to:
      type: string
      description: "涉及的结论或位点"
    mechanism:
      type: string
      description: "反例成立的机理（可选）"
```

---

## 4. 通用定义

### 4.1 RankedSite（排序位点）

```yaml
RankedSite:
  type: object
  required:
    - rank
    - site
    - reason
  properties:
    rank:
      type: integer
      minimum: 1
      description: "排序位次（1 = 最优先）"
    site:
      type: string
      description: "位点描述"
      example: "羰基 C=O"
    site_type:
      type: string
      description: "位点类型（HOMO/LUMO 贡献类型）"
      example: "pi_star"
    reason:
      type: string
      description: "排在该位次的理由"
      example: "最低 LUMO，容易接受电子"
    confidence:
      $ref: "#/definitions/ConfidenceLevel"
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

### 4.3 EffectStrength（效应强度）

```yaml
EffectStrength:
  type: string
  enum: ["strong", "moderate", "weak", "negligible"]
  description: |
    效应强度定义：
    - strong: 主导性效应，显著改变目标位点性质
    - moderate: 明显效应，与其他因素竞争
    - weak: 可检测但非主导的效应
    - negligible: 可忽略的效应
```

---

## 5. 示例

### 5.1 完整请求示例

```yaml
# 请求：评估 FEC 在负极界面的行为
input:
  molecule:
    smiles: "C1C(F)OC(=O)O1"
    name: "Fluoroethylene Carbonate"
    functional_groups: ["cyclic_carbonate", "C-F"]
  task_type: "interface_ranking"
  context:
    electrode: "anode"
    electrode_material: "Li"
    voltage_range: "deep_reduction"
    environment: "interface"
  options:
    include_trade_check: true
    verbosity: "detailed"
```

### 5.2 完整响应示例

```yaml
output:
  task_completed: "interface_ranking"
  molecule_echo:
    smiles: "C1C(F)OC(=O)O1"
    name: "Fluoroethylene Carbonate"
    identified_groups: ["cyclic_carbonate", "ester", "ether", "C-F"]
  
  interface_ranking:
    cathode:
      - rank: 1
        site: "酯氧孤对"
        site_type: "n"
        reason: "HOMO 贡献，但被 F 的 -I 略降"
        confidence: "medium"
    anode:
      - rank: 1
        site: "羰基 C=O"
        site_type: "pi_star"
        reason: "最低 LUMO（π* 反键），被 F 进一步降低"
        confidence: "high"
      - rank: 2
        site: "C-F 键"
        site_type: "sigma_star"
        reason: "σ*(C-F) 可接受电子，释放 F⁻"
        confidence: "high"
    competition_notes: "羰基还原与 C-F 断裂可能竞争，羰基优先但 C-F 路径产生 LiF"
    film_hint: "优先还原形成开环产物；F⁻ 释放促进 LiF 富集 SEI"
    confidence: "high"
  
  tradeoff_warnings:
    triggered_pitfalls:
      - pitfall_id: "TRADE_04"
        warning: "FEC 属于牺牲型添加剂，不稳定反而是功能需求"
        applies_to: "整体稳定性评估"
    confidence_adjustment: "none"
    review_notes: "FEC 的'不稳定'是设计特性，不应作为缺点"
  
  notes: "FEC 在负极优先还原，形成含 LiF 的优质 SEI；正极相对稳定"
  overall_confidence: "high"
```

---

## 6. 版本兼容性

| Schema 版本 | 兼容的 Router 版本 | 说明 |
|-------------|-------------------|------|
| 1.0 | 1.0+ | 初始版本 |

---

## 7. Changelog

- 2025-12-24: 初始版本 v1.0

