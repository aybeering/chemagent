# GAS_03_polymer_risk_v1 — 失控聚合风险

## Triggers
- 需要评估分子在电解液应用中失控聚合的风险
- 需要区分受控聚合（SEI 形成）和失控聚合（安全问题）
- 进行新型添加剂安全性筛查

## Inputs
- 分子表示：SMILES / 官能团列表
- 上游 OrganicChem 输出：官能团、不饱和度、环系
- 应用场景：添加剂 / 溶剂
- 使用量估计（可选）：trace / low / moderate / high

## Outputs
- `polymer_flags`: 聚合风险红旗列表
  - `risk_type`: 风险类型
  - `source`: 聚合源结构
  - `likelihood`: 失控可能性
  - `trigger`: 触发条件
  - `consequences`: 后果描述
- `total_polymer_risk`: 总体聚合风险等级
- `mitigation_hints`: 缓解措施
- `confidence`: 置信度

## Rules
### 受控聚合 vs 失控聚合

**受控聚合（SEI 形成，正常）**：
- 环状碳酸酯开环聚合 → 形成 SEI
- VC 自由基聚合 → 形成柔性 SEI
- 小用量、界面局限、自终止

**失控聚合（安全问题）**：
- 大用量单体快速聚合 → 放热失控
- 多官能团交联 → 凝胶化
- 链式反应无终止 → 粘度飙升

### 聚合风险结构特征

**高风险结构**：
| 结构类型 | 风险类型 | 原因 |
|---------|---------|------|
| 丙烯酸酯 | 自由基链式 | 高聚合活性 |
| 多官能团丙烯酸酯 | 交联 | 快速凝胶化 |
| 共轭二烯 | 自由基 | 高活性 |
| 过氧化物 | 引发剂 | 可能引发其他聚合 |

**中等风险结构**：
| 结构类型 | 风险类型 | 条件 |
|---------|---------|------|
| 乙烯基（单官能） | 自由基 | 大用量时 |
| 环氧化物 | 开环 | 阳离子引发时 |
| 异氰酸酯 | 聚合/交联 | 与醇/胺反应 |

**低风险结构**：
| 结构类型 | 说明 |
|---------|------|
| 饱和烷烃 | 无聚合活性 |
| 环状碳酸酯 | 受控开环 |
| 高度氟化 | 聚合抑制 |

### 失控聚合后果
| 后果 | 严重程度 | 描述 |
|-----|---------|------|
| 粘度飙升 | 中 | 电解液失效 |
| 凝胶化 | 高 | 电池失效 |
| 放热失控 | 极高 | 热失控前兆 |
| 局部过热 | 高 | 可能引发热失控 |

## Steps
1. **识别聚合活性结构**
   - 乙烯基、丙烯酸酯、二烯
   - 环氧、异氰酸酯等

2. **评估失控可能性**
   - 官能团数量（多官能 = 交联风险）
   - 聚合活性（丙烯酸酯 > 乙烯基 > 普通烯烃）
   - 使用量

3. **判断触发条件**
   - 电子转移（电化学条件）
   - 热（温升）
   - 杂质（引发剂残留）

4. **评估后果和缓解措施**

## Examples
**Example 1: EC（低风险，受控）**
```yaml
input:
  smiles: "C1COC(=O)O1"
  application: "solvent"
  amount: "high"
    
output:
  polymer_flags:
    - risk_type: "ring_opening"
      source: "环状碳酸酯"
      likelihood: "low"
      trigger: "还原条件"
      consequences: "形成 SEI 聚合物，受控"
  total_polymer_risk: "low"
  notes: "EC 的开环聚合是 SEI 形成的一部分，受控在界面，不是失控风险"
  mitigation_hints:
    - "无需特殊措施"
  confidence: "high"
```

**Example 2: VC（低风险，受控）**
```yaml
input:
  smiles: "C=C1OC(=O)O1"
  application: "additive"
  amount: "low"
    
output:
  polymer_flags:
    - risk_type: "radical"
      source: "乙烯基"
      likelihood: "low"
      trigger: "电子转移"
      consequences: "形成 SEI 聚合物，受控"
  total_polymer_risk: "low"
  notes: "VC 作为添加剂（<5%），聚合受控形成 SEI，不是失控风险"
  mitigation_hints:
    - "控制用量 <5%"
  confidence: "high"
```

**Example 3: 丙烯酸甲酯（中-高风险）**
```yaml
input:
  smiles: "C=CC(=O)OC"
  name: "Methyl Acrylate"
  application: "additive_candidate"
  amount: "moderate"
    
output:
  polymer_flags:
    - risk_type: "radical_chain"
      source: "丙烯酸酯"
      likelihood: "high"
      trigger: "电子转移、热、自由基杂质"
      consequences: "快速聚合、粘度飙升、可能放热失控"
    - risk_type: "thermal_runaway"
      source: "聚合放热累积"
      likelihood: "medium"
      trigger: "大量快速聚合"
      consequences: "局部过热、电池损坏"
  total_polymer_risk: "medium-high"
  notes: "丙烯酸酯类有较高聚合活性，需谨慎"
  mitigation_hints:
    - "添加阻聚剂（如 MEHQ）"
    - "严格控制用量（<2%）"
    - "避免高温存储"
    - "确保无自由基杂质"
  confidence: "high"
```

**Example 4: 多官能丙烯酸酯（高风险）**
```yaml
input:
  smiles: "C=CC(=O)OCC(COC(=O)C=C)(COC(=O)C=C)COC(=O)C=C"
  name: "Pentaerythritol Tetraacrylate"
  application: "additive_candidate"
  amount: "low"
    
output:
  polymer_flags:
    - risk_type: "crosslinking"
      source: "四官能丙烯酸酯"
      likelihood: "high"
      trigger: "任何聚合引发"
      consequences: "快速凝胶化、电解液失效"
    - risk_type: "thermal_runaway"
      source: "交联放热"
      likelihood: "high"
      trigger: "聚合开始"
      consequences: "可能热失控"
  total_polymer_risk: "high"
  notes: "多官能单体极易交联凝胶化，不推荐用于液态电解液"
  mitigation_hints:
    - "不推荐使用"
    - "若必须使用，需极低用量（<0.5%）+ 强阻聚剂"
  confidence: "high"
```

**Example 5: BTFE（极低风险）**
```yaml
input:
  smiles: "FC(F)(F)COCC(F)(F)F"
  application: "diluent"
  amount: "high"
    
output:
  polymer_flags: []
  total_polymer_risk: "low"
  notes: "高度氟化饱和结构，无聚合活性"
  mitigation_hints:
    - "无需特殊措施"
  confidence: "high"
```

## Guardrails
- 区分受控聚合（SEI 形成）和失控聚合（安全问题）
- 用量是关键因素：小用量添加剂风险低，大用量需谨慎
- 不预测聚合速率或分子量
- 工业级产品可能含阻聚剂，需确认
- 新型单体需小规模安全测试
- 与 SEI_02_polymer_film_v1 的区别：SEI_02 分析受控成膜，本卡分析失控风险

## Dependencies
- 上游：OrganicChem 官能团识别、不饱和度
- 关联：SEI_02_polymer_film_v1（受控聚合成膜）
- 关联：ROLE_05_unsuitable_flag_v1（不适合标记）

## Changelog
- 2025-12-25: 初始版本

