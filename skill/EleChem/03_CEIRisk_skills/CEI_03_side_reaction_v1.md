# CEI_03_side_reaction_v1 — 副反应类别判定

## Triggers
- 需要预测分子氧化后可能发生的副反应类型
- 需要评估副反应对电池性能的影响
- 基于 CEI_02 识别的氧化位点进行分析

## Inputs
- 氧化位点信息：来自 CEI_02 的 oxidation_sites
- 分子表示：SMILES / 官能团列表
- 上游 OrganicChem 输出：官能团、敏感位点
- 正极条件（可选）：电压范围、材料

## Outputs
- `side_reactions`: 副反应列表
  - `reaction_type`: 反应类型
  - `likelihood`: 可能性（high / medium / low）
  - `description`: 反应描述
  - `consequences`: 后果描述
  - `mechanism_hint`: 机理提示
- `overall_severity`: 总体严重程度（high / medium / low）
- `product_hints`: 可能的降解产物
- `confidence`: 置信度

## Rules
### 氧化副反应类型

**脱氢反应（Dehydrogenation）**：
| 触发位点 | 产物趋势 | 条件 |
|---------|---------|------|
| α-醚 C-H | 醛 / 羧酸 | 醚类氧化 |
| 苄位 C-H | 醛 / 酮 | 芳香族氧化 |
| α-酯 C-H | 不饱和酯 | 酯类氧化 |

**开环反应（Ring Opening）**：
| 结构类型 | 产物趋势 | 条件 |
|---------|---------|------|
| 环状碳酸酯 | CO₂ + 二醇 / 醛 | 高压氧化开环 |
| 内酯 | 羧酸 + 醛 | 氧化开环 |

**聚合反应（Polymerization）**：
| 触发条件 | 产物 | 影响 |
|---------|------|------|
| 自由基中间体 | 聚合物沉积 | CEI 增厚 |
| 阳离子中间体 | 阳离子聚合 | 电解液劣化 |

**分解反应（Decomposition）**：
| 结构类型 | 产物趋势 | 条件 |
|---------|---------|------|
| 线性碳酸酯 | CO₂ + 烷氧化物 | 深度氧化 |
| 醚类 | 醛 + 酸 + 碎片 | 链断裂 |

### 副反应后果评估
| 后果类型 | 严重程度 | 描述 |
|---------|---------|------|
| 产气（CO₂, CO） | 中-高 | 电池膨胀、安全风险 |
| CEI 增厚 | 中 | 阻抗上升、容量衰减 |
| 活性物质损失 | 高 | 电解液持续消耗 |
| 过渡金属溶出 | 高 | 正极材料劣化 |
| 酸性产物 | 高 | 腐蚀、进一步分解 |

## Steps
1. **接收氧化位点信息**
   - 获取 CEI_02 识别的氧化位点
   - 获取分子官能团列表

2. **根据位点类型预测反应**
   - n 轨道氧化 → 脱氢/开环/分解
   - π 轨道氧化 → 加成/聚合
   - σ(C-H) 氧化 → 脱氢

3. **评估各反应可能性**
   - 基于结构稳定性
   - 基于反应驱动力

4. **评估后果和严重程度**
   - 产物类型
   - 对电池性能的影响

## Examples
**Example 1: EC 高压氧化**
```yaml
input:
  oxidation_sites:
    - { site: "酯氧孤对", site_type: "n", activity: "medium" }
  smiles: "C1COC(=O)O1"
  context:
    voltage_range: "high"
    
output:
  side_reactions:
    - reaction_type: "ring_opening"
      likelihood: "medium"
      description: "氧化导致环开裂，释放 CO₂"
      consequences: "产气、电解液消耗"
      mechanism_hint: "n 轨道氧化后 C-O 键弱化开裂"
    - reaction_type: "dehydrogenation"
      likelihood: "low"
      description: "环上 C-H 脱氢"
      consequences: "形成不饱和产物"
      mechanism_hint: "自由基机理"
  overall_severity: "medium"
  product_hints: ["CO₂", "乙二醇衍生物", "甲醛"]
  confidence: "medium"
```

**Example 2: DME 高压氧化**
```yaml
input:
  oxidation_sites:
    - { site: "醚氧孤对", site_type: "n", activity: "high" }
    - { site: "α-醚 C-H", site_type: "sigma_CH", activity: "medium" }
  smiles: "COCCOC"
  context:
    voltage_range: "high"
    
output:
  side_reactions:
    - reaction_type: "dehydrogenation"
      likelihood: "high"
      description: "α-醚 C-H 脱氢形成醛"
      consequences: "产生醛类，可能进一步氧化为酸"
      mechanism_hint: "n 氧化产生阳离子自由基，引发 C-H 脱氢"
    - reaction_type: "decomposition"
      likelihood: "high"
      description: "C-O 键断裂，链分解"
      consequences: "电解液严重劣化"
      mechanism_hint: "β-断裂机理"
  overall_severity: "high"
  product_hints: ["甲醛", "甲酸", "甲氧基碎片", "CO"]
  confidence: "high"
```

**Example 3: Sulfolane 高压氧化**
```yaml
input:
  oxidation_sites:
    - { site: "环碳 C-H", site_type: "sigma_CH", activity: "low" }
  smiles: "C1CCS(=O)(=O)C1"
  context:
    voltage_range: "high"
    
output:
  side_reactions:
    - reaction_type: "none_significant"
      likelihood: "low"
      description: "砜基高度稳定，难以发生显著副反应"
      consequences: "轻微"
      mechanism_hint: "砜基吸电子效应抑制氧化"
  overall_severity: "low"
  product_hints: ["少量脱氢产物（若有）"]
  confidence: "high"
```

**Example 4: BTFE 高压氧化**
```yaml
input:
  oxidation_sites:
    - { site: "醚氧孤对", site_type: "n", activity: "low" }
  smiles: "FC(F)(F)COCC(F)(F)F"
  context:
    voltage_range: "high"
    
output:
  side_reactions:
    - reaction_type: "none_significant"
      likelihood: "low"
      description: "高度氟化结构极其稳定"
      consequences: "几乎无副反应"
      mechanism_hint: "CF₃ 强吸电子效应阻止氧化"
  overall_severity: "low"
  product_hints: []
  confidence: "high"
```

## Guardrails
- 不预测反应速率或动力学
- 副反应是趋势预测，非确定性结论
- 正极材料表面可能催化特定反应
- 电解液添加剂可能改变反应路径
- 新型结构需实验验证
- 多个副反应可能同时发生

## Dependencies
- 必需：CEI_02_oxidation_site_v1 输出
- 辅助：OrganicChem 官能团识别

## Changelog
- 2025-12-25: 初始版本

