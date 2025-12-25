# SEI_02_polymer_film_v1 — 聚合膜路径

## Triggers
- 需要评估分子在负极还原时形成聚合物膜的倾向
- 需要判断聚合机理（开环 / 自由基 / 其他）
- 分子含有可聚合结构（环状酯、不饱和键等）

## Inputs
- 分子表示：SMILES / 官能团列表
- 上游 OrganicChem 输出：官能团、环系、开环位点
- 上游 PhysChem 输出：LUMO 排序、环张力分析
- 电极条件（可选）：电位范围

## Outputs
- `likelihood`: 聚合膜形成可能性（high / medium / low / none）
- `mechanism`: 聚合机理（ring_opening / radical / anionic / cationic / none）
- `polymerization_site`: 聚合起始位点
- `products_hint`: 可能的聚合物类型
- `film_character`: 膜特征提示（flexible / rigid / porous）
- `confidence`: 置信度

## Rules
### 聚合倾向正向指标

**开环聚合（Ring-Opening Polymerization）**：
| 结构类型 | 聚合倾向 | 机理 |
|---------|---------|------|
| 环状碳酸酯（5 元） | 高 | 亲核开环 |
| 内酯（5/6 元） | 中-高 | 亲核开环 |
| 环氧化物 | 高 | 亲核开环 |
| 环状醚（如 DOL） | 中 | 阳离子开环 |

**自由基聚合**：
| 结构类型 | 聚合倾向 | 条件 |
|---------|---------|------|
| 乙烯基（C=C） | 高 | 电子转移引发 |
| 共轭二烯 | 高 | 自由基活性高 |
| 炔基 | 中 | 可能聚合 |

### 聚合倾向负向指标
- 无可聚合官能团
- 高度氟化（聚合活性被抑制）
- 位阻过大
- 链转移剂存在

### 聚合物膜特征
| 聚合物类型 | 膜特征 | SEI 贡献 |
|-----------|--------|---------|
| 聚碳酸酯 | 柔性、可溶 | 改善机械性能 |
| 聚醚 | 柔性、离子传导 | 辅助离子传输 |
| 聚烯烃 | 较刚性 | 阻隔性好 |

## Steps
1. **识别可聚合结构**
   - 环状酯/醚/碳酸酯 → 开环聚合
   - C=C 双键 → 自由基聚合
   - 炔基 → 可能聚合

2. **评估聚合活性**
   - 环张力（3/4/5 元环活性高）
   - 电子效应（活化或钝化）
   - 位阻效应

3. **判断聚合机理**
   - 电子转移引发 → 阴离子/自由基
   - 开环 → 亲核/阳离子

4. **预测产物类型**
   - 根据单体结构推断聚合物结构
   - 评估膜特征

## Examples
**Example 1: EC（高聚合倾向）**
```yaml
input:
  smiles: "C1COC(=O)O1"
  organic_chem:
    functional_groups: [{ fg_type: "cyclic_carbonate" }]
    ring_opening_sites: [{ ring_type: "cyclic_carbonate", strain_driven: true }]
    
output:
  likelihood: "high"
  mechanism: "ring_opening"
  polymerization_site: "羰基碳（亲核进攻）"
  products_hint: ["聚(碳酸乙烯酯)", "低聚碳酸酯"]
  film_character: "flexible"
  evidence:
    - "五元环状碳酸酯，适中环张力促进开环"
    - "还原后羰基碳成为亲电位点"
    - "形成可溶性柔性聚合物"
  confidence: "high"
```

**Example 2: VC（极高聚合倾向）**
```yaml
input:
  smiles: "C=C1OC(=O)O1"
  organic_chem:
    functional_groups: [{ fg_type: "cyclic_carbonate" }, { fg_type: "vinyl" }]
    
output:
  likelihood: "high"
  mechanism: "radical"
  polymerization_site: "乙烯基 C=C"
  products_hint: ["聚(碳酸乙烯酯)", "交联聚合物"]
  film_character: "flexible"
  evidence:
    - "乙烯基高度活化，易接受电子引发聚合"
    - "自由基聚合形成高分子量聚合物"
    - "显著改善 SEI 柔性和稳定性"
  confidence: "high"
```

**Example 3: DMC（低聚合倾向）**
```yaml
input:
  smiles: "COC(=O)OC"
  organic_chem:
    functional_groups: [{ fg_type: "carbonate" }]
    ring_opening_sites: []
    
output:
  likelihood: "low"
  mechanism: "none"
  polymerization_site: null
  products_hint: ["无聚合物，主要形成小分子"]
  film_character: null
  evidence:
    - "线性碳酸酯，无环张力驱动开环"
    - "还原主要产生 Li₂CO₃ 和烷氧锂"
  confidence: "high"
```

**Example 4: DOL（中等聚合倾向）**
```yaml
input:
  smiles: "C1COCO1"
  name: "1,3-Dioxolane"
  organic_chem:
    functional_groups: [{ fg_type: "cyclic_ether" }]
    
output:
  likelihood: "medium"
  mechanism: "ring_opening"
  polymerization_site: "C-O 键"
  products_hint: ["聚(1,3-二氧戊环)", "聚醚"]
  film_character: "flexible"
  evidence:
    - "五元环醚可开环聚合"
    - "聚醚有一定离子传导能力"
    - "常与 DME 配合用于锂硫电池"
  confidence: "medium"
```

## Guardrails
- 不预测聚合度/分子量
- 聚合程度受电位、温度、竞争反应影响
- 受控聚合（形成 SEI）与失控聚合（安全问题）需区分
- 过度聚合可能导致 SEI 过厚、阻抗升高
- 新型单体需实验验证

## Dependencies
- 上游：OrganicChem 环系分析、开环位点识别
- 上游：PhysChem LUMO 分析、环张力评估
- 关联：GAS_03_polymer_risk_v1（评估失控风险）

## Changelog
- 2025-12-25: 初始版本

