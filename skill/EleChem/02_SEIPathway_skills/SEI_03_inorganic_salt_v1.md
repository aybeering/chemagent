# SEI_03_inorganic_salt_v1 — 无机盐膜路径

## Triggers
- 需要评估分子还原后形成无机盐（Li₂CO₃、Li₂O 等）的倾向
- 需要判断无机盐类型和形成机理
- 分析碳酸酯类溶剂的深度分解产物

## Inputs
- 分子表示：SMILES / 官能团列表
- 上游 OrganicChem 输出：官能团、杂原子特征
- 上游 PhysChem 输出：LUMO 排序、还原位点
- 电极条件（可选）：电位深度

## Outputs
- `likelihood`: 无机盐形成可能性（high / medium / low / none）
- `salt_types`: 可能的无机盐类型
- `formation_mechanism`: 形成机理
- `products_hint`: 详细产物提示
- `sei_contribution`: 对 SEI 的贡献描述
- `confidence`: 置信度

## Rules
### 无机盐形成的来源

**碳酸酯类溶剂分解**：
| 溶剂类型 | 主要产物 | 机理 |
|---------|---------|------|
| 环状碳酸酯（EC/PC） | Li₂CO₃, ROCO₂Li | 开环后进一步分解 |
| 线性碳酸酯（DMC/EMC/DEC） | Li₂CO₃, ROLi | 直接还原分解 |

**其他来源**：
| 结构类型 | 可能产物 | 条件 |
|---------|---------|------|
| 含 S 化合物（砜/磺酸酯） | Li₂S, Li₂SO₃ | 深度还原 |
| 含 N 化合物 | Li₃N | 极端条件 |
| 硅酸酯 | Li₂SiO₃ | 深度还原 |

### 分解深度影响
- 浅度还原（>0.5V vs Li）：主要形成有机锂盐（ROCO₂Li）
- 深度还原（<0.5V vs Li）：进一步分解为无机盐（Li₂CO₃, Li₂O）
- 极端条件（Li 金属表面）：更多 Li₂O

### 无机盐特征
| 无机盐 | 离子电导率 | 机械性能 | SEI 贡献 |
|-------|-----------|---------|---------|
| Li₂CO₃ | 低 | 脆性 | 阻隔性好 |
| Li₂O | 极低 | 脆性 | 阻隔性好 |
| LiOH | 低 | 脆性 | 可能水解 |

## Steps
1. **识别无机盐前体**
   - 碳酸酯 → Li₂CO₃ 来源
   - 含 S 化合物 → Li₂S/Li₂SO₃ 来源
   - 含 Si 化合物 → 硅酸锂来源

2. **评估分解倾向**
   - 线性碳酸酯 > 环状碳酸酯（完全分解）
   - 深度还原促进无机盐形成

3. **判断产物类型**
   - 根据分子组成和反应条件

4. **评估 SEI 贡献**
   - 无机盐提供阻隔性但增加脆性

## Examples
**Example 1: EC（中等无机盐形成）**
```yaml
input:
  smiles: "C1COC(=O)O1"
  organic_chem:
    functional_groups: [{ fg_type: "cyclic_carbonate" }]
    
output:
  likelihood: "medium"
  salt_types: ["Li₂CO₃", "Li₂O"]
  formation_mechanism: "开环产物进一步分解"
  products_hint:
    - "ROCO₂Li → Li₂CO₃ + R·（自由基）"
    - "Li₂CO₃ 在极低电位可分解为 Li₂O + CO₂"
  sei_contribution: "Li₂CO₃ 提供 SEI 的无机骨架，阻隔溶剂"
  evidence:
    - "EC 优先开环形成有机锂盐"
    - "部分进一步分解为 Li₂CO₃"
    - "完全分解需要较深还原"
  confidence: "high"
```

**Example 2: DMC（高无机盐形成）**
```yaml
input:
  smiles: "COC(=O)OC"
  organic_chem:
    functional_groups: [{ fg_type: "carbonate" }]
    
output:
  likelihood: "high"
  salt_types: ["Li₂CO₃", "CH₃OLi"]
  formation_mechanism: "直接还原分解"
  products_hint:
    - "DMC + 2e⁻ + 2Li⁺ → Li₂CO₃ + 2CH₃·"
    - "或 DMC + e⁻ + Li⁺ → CH₃OCO₂Li + CH₃·"
  sei_contribution: "主要贡献 Li₂CO₃ 和甲氧锂"
  evidence:
    - "线性碳酸酯易完全分解"
    - "不形成聚合物，主要是无机盐和小分子"
  confidence: "high"
```

**Example 3: Sulfolane（含 S 无机盐）**
```yaml
input:
  smiles: "C1CCS(=O)(=O)C1"
  organic_chem:
    functional_groups: [{ fg_type: "sulfone" }]
    
output:
  likelihood: "medium"
  salt_types: ["Li₂SO₃", "Li₂S"]
  formation_mechanism: "砜基还原"
  products_hint:
    - "砜还原可能生成 Li₂SO₃"
    - "深度还原可能生成 Li₂S"
  sei_contribution: "含 S 无机盐可能改善 SEI 离子电导率"
  evidence:
    - "砜基在深度还原下可分解"
    - "S 元素贡献含 S 无机物"
  confidence: "medium"
```

**Example 4: 氟代溶剂（无机盐少）**
```yaml
input:
  smiles: "FC(F)(F)COCC(F)(F)F"
  name: "BTFE"
  organic_chem:
    functional_groups: [{ fg_type: "ether" }, { fg_type: "C-F" }]
    
output:
  likelihood: "low"
  salt_types: ["少量 LiF"]
  formation_mechanism: "主要 C-F 断裂，非碳酸盐分解"
  products_hint:
    - "无碳酸酯结构，不生成 Li₂CO₃"
    - "C-F 断裂贡献 LiF（见 SEI_04）"
  sei_contribution: "主要贡献 LiF 而非碳酸锂类无机盐"
  evidence:
    - "氟化醚不含 C=O，不产生碳酸锂"
    - "高惰性，分解少"
  confidence: "high"
```

## Guardrails
- 不预测无机盐的具体比例或厚度
- 无机盐形成受电位、温度、时间影响
- 锂盐分解（LiPF₆ → LiF + PF₅）也贡献无机盐，但本卡聚焦溶剂贡献
- Li₂CO₃ 脆性可能导致 SEI 开裂，需与有机组分配合
- 过多 Li₂O 可能增加 SEI 阻抗

## Dependencies
- 上游：OrganicChem 官能团识别
- 上游：PhysChem LUMO 分析
- 关联：SEI_01_pathway_flowmap_v1（整合各路径）

## Changelog
- 2025-12-25: 初始版本

