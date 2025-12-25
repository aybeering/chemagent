# ROLE_04_diluent_hypothesis_v1 — 稀释剂假设

## Triggers
- 需要判断分子是否适合作为 LHCE（局部高浓电解液）稀释剂
- 需要评估分子的低配位性、惰性和与高浓电解液的相容性

## Inputs
- 分子表示：SMILES / 官能团列表
- 上游 OrganicChem 输出：官能团、杂原子特征
- 上游 PhysChem 输出：电子效应、HOMO/LUMO 分析
- 电解液体系（可选）：LiFSI / LiTFSI 基 LHCE

## Outputs
- `suitability`: 适合度（high / medium / low / unsuitable）
- `evidence`: 支持/反对的结构证据
- `coordination_tendency`: Li+ 配位倾向（weak / negligible）
- `inertness`: 化学惰性评估（high / medium / low）
- `miscibility_hint`: 与高浓电解液相容性提示
- `fluorination_level`: 氟化程度提示（high / medium / low / none）

## Rules
### 稀释剂适合性正向指标

- **低/无 Li+ 配位能力**：
  - 稀释剂不应强配位 Li+，否则会破坏高浓电解液的溶剂化结构
  - 氟化醚/酯：配位能力被 -I 效应削弱
  - 氟化烷烃/芳烃：无配位位点
  
- **化学惰性**：
  - 高氟化结构：提高氧化/还原稳定性
  - 无活泼官能团：不参与副反应
  
- **与高浓电解液相容**：
  - 适当的粘度：降低整体粘度
  - 溶解性：与高浓电解液混溶

### 稀释剂适合性负向指标
- 强 Li+ 配位能力：竞争破坏溶剂化结构
- 活泼官能团：参与副反应
- 极高挥发性：安全问题
- 与电解液不混溶

### 典型稀释剂结构模式
| 结构模式 | 配位能力 | 典型代表 |
|---------|---------|---------|
| 氟化醚 | 弱 | BTFE, TTE, TFEE |
| 氟化碳酸酯 | 弱 | FEMC, F-EMC |
| 氟化芳烃 | 无 | 氟苯衍生物 |
| 氟化烷烃 | 无 | 全氟烷烃 |

### 氟化程度影响
- 高度氟化（>50% F 取代）：
  - 极低配位能力
  - 高化学惰性
  - 可能与某些电解液不混溶
  
- 部分氟化：
  - 弱配位能力
  - 良好惰性
  - 通常更好的混溶性

## Steps
1. **评估配位能力**
   - 识别可配位原子（O、N、S）
   - 评估吸电子基（F、CF₃）对配位的削弱
   - 高氟化 → 配位能力弱
   
2. **评估化学惰性**
   - 氟化程度
   - 活泼官能团（不应存在）
   - 结合 PhysChem 的 HOMO/LUMO
   
3. **评估相容性**
   - 分子极性（与电解液匹配）
   - 氟化程度（影响混溶性）
   
4. **综合判定适合度**

## Examples
**Example 1: BTFE (高度适合)**
```yaml
input:
  smiles: "FC(F)(F)COCC(F)(F)F"
  name: "Bis(2,2,2-trifluoroethyl) ether"
  functional_groups: ["ether", "C-F"]
  
output:
  suitability: "high"
  evidence:
    positive:
      - "高度氟化醚，配位能力被 CF₃ 的 -I 效应显著削弱"
      - "化学惰性高，不易参与副反应"
      - "与 LiFSI/LiTFSI 基电解液混溶性好"
      - "降低电解液粘度"
    negative:
      - "完全惰性的稀释剂可能略降低离子电导率"
  coordination_tendency: "weak"
  inertness: "high"
  miscibility_hint: "与高浓 LiFSI 电解液混溶"
  fluorination_level: "high"
```

**Example 2: TTE (适合)**
```yaml
input:
  smiles: "FC(F)(F)C(F)(F)OCC(F)(F)C(F)(F)F"
  name: "1,1,2,2-Tetrafluoroethyl 2,2,3,3-tetrafluoropropyl ether"
  functional_groups: ["ether", "C-F"]
  
output:
  suitability: "high"
  evidence:
    positive:
      - "高度氟化结构"
      - "醚氧配位被 F 极度削弱"
      - "优异的化学惰性"
    negative:
      - "高氟化可能导致与某些电解液相容性降低"
  coordination_tendency: "negligible"
  inertness: "high"
  miscibility_hint: "需验证与具体电解液的混溶性"
  fluorination_level: "high"
```

**Example 3: DME (不适合)**
```yaml
input:
  smiles: "COCCOC"
  name: "1,2-Dimethoxyethane"
  functional_groups: ["ether"]
  
output:
  suitability: "unsuitable"
  evidence:
    positive: []
    negative:
      - "非氟化醚，醚氧有较强 Li+ 配位能力"
      - "会竞争性配位 Li+，破坏高浓电解液结构"
      - "应作为溶剂使用，不适合作为稀释剂"
  coordination_tendency: "strong"
  inertness: "medium"
  miscibility_hint: null
  fluorination_level: "none"
  note: "DME 是锂硫电池常用溶剂，不是 LHCE 稀释剂"
```

## Guardrails
- 稀释剂概念特定于 LHCE 体系
- 常规电解液不使用"稀释剂"概念
- 不预测具体混溶比例
- 高度氟化化合物需注意成本和来源
- 实际相容性需实验验证

## Dependencies
- 上游：OrganicChem 官能团识别
- 上游：PhysChem 电子效应分析

## Changelog
- 2025-12-25: 初始版本

