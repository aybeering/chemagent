# ROLE_02_solvent_hypothesis_v1 — 溶剂假设

## Triggers
- 需要判断分子是否适合作为电解液主溶剂
- 需要评估分子的溶解锂盐能力和电化学窗口

## Inputs
- 分子表示：SMILES / 官能团列表
- 上游 OrganicChem 输出：官能团类型、杂原子特征
- 上游 PhysChem 输出：电子效应、HOMO/LUMO 分析
- 应用场景（可选）：常规 / 高压 / 低温

## Outputs
- `suitability`: 适合度（high / medium / low / unsuitable）
- `evidence`: 支持/反对的结构证据
- `dielectric_hint`: 介电常数趋势提示（high / medium / low）
- `viscosity_hint`: 粘度趋势提示（low / medium / high）
- `coordination_sites`: Li+ 配位位点描述
- `electrochemical_window_hint`: 电化学窗口提示（wide / medium / narrow）

## Rules
### 溶剂适合性正向指标
- **高介电常数倾向**：
  - 环状碳酸酯（EC、PC）：极高介电常数（80-90）
  - 砜类（sulfolane）：高介电常数（40-50）
  - 内酯（γ-BL）：中高介电常数（40）
  - 线性碳酸酯（DMC、EMC、DEC）：低介电常数（3-5），需与高介电溶剂配合
  
- **Li+ 配位能力**：
  - 羰基氧：强配位位点
  - 醚氧：中等配位位点
  - 砜氧：强配位位点
  - 腈 N：强配位位点
  
- **低粘度倾向**：
  - 线性结构优于环状
  - 小分子优于大分子
  - 烷基取代增加粘度

### 溶剂适合性负向指标
- 极低介电常数（<3）：无法有效溶解锂盐
- 无配位位点：无法溶剂化 Li+
- 极高粘度：降低离子传输
- 极窄电化学窗口：容易氧化/还原分解

### 典型溶剂结构模式
| 结构模式 | 介电常数趋势 | 典型代表 |
|---------|------------|---------|
| 环状碳酸酯 | 极高 | EC, PC |
| 线性碳酸酯 | 低 | DMC, EMC, DEC |
| 内酯 | 中高 | γ-BL |
| 砜 | 高 | Sulfolane |
| 腈 | 高 | Acetonitrile |
| 醚 | 低-中 | DME, DOL |

## Steps
1. **识别配位位点**
   - 从官能团列表提取可配位原子（O、N、S）
   - 评估配位强度（羰基 O > 醚 O > 酯 O）
   
2. **评估介电常数趋势**
   - 根据官能团类型和环状/线性结构判断
   - 环状碳酸酯/砜/内酯 → high
   - 线性碳酸酯/醚 → low
   
3. **评估粘度趋势**
   - 分子量、环状性、支链
   - 小分子线性结构 → low
   - 大分子环状结构 → high
   
4. **评估电化学窗口**
   - 结合 PhysChem 的 HOMO/LUMO 分析
   - HOMO 低 → 氧化稳定
   - LUMO 高 → 还原稳定

5. **综合判定适合度**

## Examples
**Example 1: EC (适合)**
```yaml
input:
  smiles: "C1COC(=O)O1"
  functional_groups: ["cyclic_carbonate"]
  
output:
  suitability: "high"
  evidence:
    positive:
      - "环状碳酸酯结构，高介电常数"
      - "羰基和醚氧提供双配位位点"
      - "成熟的锂离子电池溶剂"
    negative:
      - "较高熔点（36°C），低温流动性差"
  dielectric_hint: "high"
  viscosity_hint: "medium"
  coordination_sites: "羰基 O（主）+ 醚 O（辅）"
  electrochemical_window_hint: "medium"
```

**Example 2: DMC (配合溶剂)**
```yaml
input:
  smiles: "COC(=O)OC"
  functional_groups: ["carbonate"]
  
output:
  suitability: "medium"
  evidence:
    positive:
      - "低粘度，改善离子传输"
      - "羰基提供配位位点"
    negative:
      - "低介电常数（~3），单独无法溶解锂盐"
      - "需与高介电溶剂配合使用"
  dielectric_hint: "low"
  viscosity_hint: "low"
  coordination_sites: "羰基 O"
  electrochemical_window_hint: "medium"
```

**Example 3: Hexane (不适合)**
```yaml
input:
  smiles: "CCCCCC"
  functional_groups: []
  
output:
  suitability: "unsuitable"
  evidence:
    positive: []
    negative:
      - "纯烷烃，无配位位点"
      - "极低介电常数，无法溶解锂盐"
  dielectric_hint: "low"
  viscosity_hint: "low"
  coordination_sites: "无"
  electrochemical_window_hint: "wide"
  note: "可考虑作为 LHCE 稀释剂"
```

## Guardrails
- 不输出具体介电常数数值，只给趋势判断
- 低介电常数溶剂不直接判定为"不适合"，需考虑混合溶剂使用
- 新型溶剂结构需降低置信度
- 实际性能需实验验证

## Dependencies
- 上游：OrganicChem 官能团识别
- 上游：PhysChem HOMO/LUMO 分析

## Changelog
- 2025-12-25: 初始版本

