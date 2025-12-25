# CEI_01_risk_flowmap_v1 — CEI 风险总路由

## Triggers
- 需要评估分子在高压正极界面的氧化稳定性
- 需要预测可能的氧化副反应
- 作为 EleChem CEI 风险模块的主入口被调用

## Inputs
- 分子表示：SMILES / 官能团列表
- 上游 OrganicChem 输出：官能团、杂原子特征
- 上游 PhysChem 输出：HOMO 排序、氧化位点、界面排序
- 正极条件：
  - 电极材料：NCM / NCA / LCO / LFP / LNMO
  - 电压范围：normal（<4.3V）/ high（4.3-4.5V）/ ultra-high（>4.5V）

## Outputs
- `risk_level`: 风险等级（high / medium / low）
- `oxidation_sites`: 易氧化位点列表
- `side_reactions`: 可能的副反应列表
- `mitigation_hints`: 缓解措施建议
- `overall_assessment`: 综合评估摘要
- `confidence`: 置信度

## Rules
### CEI 风险评估规则

**风险等级判定**：
| 风险等级 | 条件 |
|---------|------|
| high | HOMO 高 + 多个易氧化位点 + 高压正极 |
| medium | 存在易氧化位点但非主导 / 中等电压 |
| low | HOMO 低 + 结构稳定 + 常规电压 |

**易氧化结构**：
| 结构类型 | HOMO 位置 | 氧化风险 |
|---------|----------|---------|
| 醚氧孤对 | 高 | 高 |
| 胺 N 孤对 | 高 | 高 |
| 芳环 π | 中 | 中 |
| 砜类 | 低 | 低 |
| 高度氟化 | 很低 | 很低 |

**正极材料影响**：
| 正极 | 电压 | 氧化压力 |
|-----|------|---------|
| LFP | 3.4V | 低 |
| LCO | 4.2V | 中 |
| NCM811/NCA | 4.3-4.5V | 高 |
| LNMO | 4.7V | 极高 |

## Steps
1. **接收上游输入**
   - 获取 PhysChem 的 HOMO 排序和氧化位点
   - 获取正极条件（材料、电压）

2. **调用易氧化位点识别** → `CEI_02_oxidation_site_v1`
   - 识别所有易氧化位点
   - 评估各位点的氧化活性

3. **调用副反应类别判定** → `CEI_03_side_reaction_v1`
   - 根据氧化位点预测可能的副反应
   - 评估副反应的可能性和后果

4. **综合风险评估**
   - 结合正极条件评估实际风险
   - 生成缓解措施建议
   - 确定风险等级

## Examples
**Example 1: EC（中等 CEI 风险）**
```yaml
input:
  smiles: "C1COC(=O)O1"
  phys_chem:
    oxidation_tendency:
      ox_sites_ranked:
        - { rank: 1, site: "酯氧孤对", homo_type: "n" }
  context:
    electrode_material: "NCM811"
    voltage_range: "high"
    
output:
  risk_level: "medium"
  oxidation_sites:
    - site: "酯氧孤对"
      site_type: "n"
      reason: "HOMO 贡献，但羰基吸电子略降低"
      activity: "medium"
  side_reactions:
    - reaction_type: "ring_opening"
      likelihood: "medium"
      description: "氧化开环可能产生 CO₂"
  mitigation_hints:
    - "控制正极电位 <4.4V"
    - "使用 CEI 形成添加剂（如 LiBOB）"
  overall_assessment: "EC 在高压 NCM811 体系有中等氧化风险，需配合 CEI 保护策略"
  confidence: "high"
```

**Example 2: DMC（低-中 CEI 风险）**
```yaml
input:
  smiles: "COC(=O)OC"
  phys_chem:
    oxidation_tendency:
      ox_sites_ranked:
        - { rank: 1, site: "酯氧孤对", homo_type: "n" }
  context:
    electrode_material: "NCM622"
    voltage_range: "normal"
    
output:
  risk_level: "low"
  oxidation_sites:
    - site: "酯氧孤对"
      site_type: "n"
      reason: "线性碳酸酯 HOMO 略低于环状"
      activity: "low-medium"
  side_reactions:
    - reaction_type: "decomposition"
      likelihood: "low"
      description: "常规电压下稳定"
  mitigation_hints:
    - "正常使用条件下氧化风险可控"
  overall_assessment: "DMC 在常规电压下氧化稳定性良好"
  confidence: "high"
```

**Example 3: BTFE（低 CEI 风险）**
```yaml
input:
  smiles: "FC(F)(F)COCC(F)(F)F"
  phys_chem:
    oxidation_tendency:
      ox_sites_ranked:
        - { rank: 1, site: "醚氧孤对（被 CF₃ 削弱）", homo_type: "n" }
  context:
    electrode_material: "NCA"
    voltage_range: "high"
    
output:
  risk_level: "low"
  oxidation_sites:
    - site: "醚氧孤对"
      site_type: "n"
      reason: "CF₃ 的强 -I 效应显著降低 HOMO"
      activity: "low"
  side_reactions:
    - reaction_type: "none_significant"
      likelihood: "low"
      description: "高度氟化结构氧化稳定"
  mitigation_hints:
    - "天然高氧化稳定性，无需额外措施"
  overall_assessment: "BTFE 高度氟化，氧化稳定性优异，适合高压体系"
  confidence: "high"
```

**Example 4: DME（高 CEI 风险）**
```yaml
input:
  smiles: "COCCOC"
  phys_chem:
    oxidation_tendency:
      ox_sites_ranked:
        - { rank: 1, site: "醚氧孤对", homo_type: "n" }
  context:
    electrode_material: "NCM811"
    voltage_range: "high"
    
output:
  risk_level: "high"
  oxidation_sites:
    - site: "醚氧孤对（两个）"
      site_type: "n"
      reason: "醚类 HOMO 高，易氧化"
      activity: "high"
  side_reactions:
    - reaction_type: "dehydrogenation"
      likelihood: "high"
      description: "脱氢形成醛/酸"
    - reaction_type: "decomposition"
      likelihood: "high"
      description: "链断裂分解"
  mitigation_hints:
    - "不推荐用于高压正极体系"
    - "仅适用于低压体系（如 Li-S）"
  overall_assessment: "DME 氧化稳定性差，不适合高压正极"
  confidence: "high"
```

## Guardrails
- 不预测具体氧化电位（V）
- CEI 形成是复杂过程，本卡给出趋势而非精确预测
- 正极材料表面催化效应可能改变氧化行为
- 新型正极材料需实验验证
- 电解液配方（锂盐、添加剂）影响实际 CEI 性能

## Dependencies
- `CEI_02_oxidation_site_v1`
- `CEI_03_side_reaction_v1`
- 上游：`PhysChem_Router`（HOMO 分析）

## Changelog
- 2025-12-25: 初始版本

