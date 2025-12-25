# GAS_01_risk_flowmap_v1 — 产气/聚合风险总路由

## Triggers
- 需要评估分子在电解液应用中的产气和失控聚合风险
- 需要进行安全性结构筛查
- 作为 EleChem 产气/聚合风险模块的主入口被调用

## Inputs
- 分子表示：SMILES / 官能团列表
- 上游 OrganicChem 输出：官能团、敏感位点、环系
- 上游 PhysChem 输出：HOMO/LUMO 分析
- 应用场景：溶剂 / 添加剂 / 稀释剂
- 使用条件（可选）：温度范围、电压范围

## Outputs
- `gas_flags`: 产气风险红旗列表
- `polymer_flags`: 聚合风险红旗列表
- `overall_risk`: 总体风险等级（high / medium / low）
- `safety_notes`: 安全性说明
- `mitigation_hints`: 缓解措施建议
- `confidence`: 置信度

## Rules
### 风险等级判定

**高风险（high）**：
- 存在高产气倾向结构
- 存在失控聚合高风险结构
- 多个中等风险因素叠加

**中等风险（medium）**：
- 存在产气倾向但可控
- 存在聚合倾向但通常受控
- 需要特定条件触发

**低风险（low）**：
- 结构稳定
- 无明显产气/聚合红旗
- 经验证的成熟材料

### 产气风险评估要点
| 结构特征 | 产气类型 | 风险等级 |
|---------|---------|---------|
| 碳酸酯（还原） | CO₂, CO | 中（正常 SEI 形成） |
| 碳酸酯（氧化） | CO₂ | 中 |
| C-F + 水 | HF | 中-高 |
| 活泼 H | H₂ | 高（与 Li 反应） |
| 不稳定基团 | 多种 | 高 |

### 聚合风险评估要点
| 结构特征 | 聚合类型 | 风险等级 |
|---------|---------|---------|
| 单不饱和（烯烃） | 自由基 | 低-中 |
| 多不饱和（二烯） | 自由基 | 中-高 |
| 环氧化物 | 开环 | 中 |
| 丙烯酸酯 | 自由基 | 高 |

## Steps
1. **接收上游输入**
   - 获取官能团列表和敏感位点
   - 获取应用场景信息

2. **调用产气风险分析** → `GAS_02_gassing_flags_v1`
   - 识别产气风险红旗
   - 评估各气体产生可能性

3. **调用聚合风险分析** → `GAS_03_polymer_risk_v1`
   - 识别失控聚合风险红旗
   - 评估聚合失控可能性

4. **综合风险评估**
   - 汇总所有风险因素
   - 确定总体风险等级
   - 生成安全性说明和缓解措施

## Examples
**Example 1: EC（低风险）**
```yaml
input:
  smiles: "C1COC(=O)O1"
  organic_chem:
    functional_groups: [{ fg_type: "cyclic_carbonate" }]
  application: "solvent"
    
output:
  gas_flags:
    - gas_type: "CO2"
      source: "SEI 形成时碳酸酯分解"
      likelihood: "medium"
      trigger: "首次锂化"
      notes: "正常 SEI 形成过程，不是安全问题"
  polymer_flags:
    - risk_type: "ring_opening"
      source: "开环聚合"
      likelihood: "low"
      trigger: "还原条件"
      notes: "形成 SEI 的一部分，受控"
  overall_risk: "low"
  safety_notes: "EC 是成熟溶剂，产气和聚合在正常范围内"
  mitigation_hints:
    - "首次充电使用化成工艺排气"
  confidence: "high"
```

**Example 2: FEC（低风险）**
```yaml
input:
  smiles: "FC1COC(=O)O1"
  organic_chem:
    functional_groups: [{ fg_type: "cyclic_carbonate" }, { fg_type: "C-F" }]
  application: "film_additive"
    
output:
  gas_flags:
    - gas_type: "CO2"
      source: "还原开环"
      likelihood: "medium"
      trigger: "首次锂化"
    - gas_type: "HF"
      source: "C-F 断裂 + 痕量水"
      likelihood: "low"
      trigger: "电解液含水时"
      notes: "控制水分可避免"
  polymer_flags:
    - risk_type: "ring_opening"
      source: "开环聚合"
      likelihood: "low"
      trigger: "还原条件"
      notes: "形成优质 SEI"
  overall_risk: "low"
  safety_notes: "FEC 是成熟添加剂，风险可控"
  mitigation_hints:
    - "控制电解液水分 <20ppm"
    - "首次化成排气"
  confidence: "high"
```

**Example 3: 乙烯基化合物（中等风险）**
```yaml
input:
  smiles: "C=CC(=O)OC"
  name: "Methyl Acrylate"
  organic_chem:
    functional_groups: [{ fg_type: "acrylate" }, { fg_type: "vinyl" }]
  application: "additive"
    
output:
  gas_flags:
    - gas_type: "CO2"
      source: "酯基分解"
      likelihood: "low"
      trigger: "氧化条件"
  polymer_flags:
    - risk_type: "radical_chain"
      source: "丙烯酸酯自由基聚合"
      likelihood: "high"
      trigger: "电子转移、热、光"
      notes: "丙烯酸酯类易聚合"
    - risk_type: "thermal_runaway"
      source: "聚合放热累积"
      likelihood: "medium"
      trigger: "大量快速聚合"
  overall_risk: "medium"
  safety_notes: "丙烯酸酯类有聚合风险，需谨慎使用"
  mitigation_hints:
    - "添加阻聚剂"
    - "控制使用量（<5%）"
    - "避免高温和强还原条件"
  confidence: "high"
```

**Example 4: 含活泼 H 化合物（高风险）**
```yaml
input:
  smiles: "CCO"
  name: "Ethanol"
  organic_chem:
    functional_groups: [{ fg_type: "alcohol" }]
  application: "solvent"
    
output:
  gas_flags:
    - gas_type: "H2"
      source: "O-H 与锂反应"
      likelihood: "high"
      trigger: "接触锂金属/低电位负极"
      notes: "活泼 H 是严重安全隐患"
  polymer_flags: []
  overall_risk: "high"
  safety_notes: "含 O-H 结构不适合锂电池电解液，会产生 H₂ 并与锂反应"
  mitigation_hints:
    - "不推荐使用"
    - "若必须使用，确保远离锂金属和低电位负极"
  confidence: "high"
```

## Guardrails
- 本卡给出结构风险提示，不预测具体产气量
- 实际风险受使用量、温度、电流等影响
- "低风险"不等于"零风险"
- 新型结构需实验安全性验证
- 产气测试（原位 DEMS 等）可提供定量数据

## Dependencies
- `GAS_02_gassing_flags_v1`
- `GAS_03_polymer_risk_v1`
- 上游：`OrganicChem_Router`, `PhysChem_Router`

## Changelog
- 2025-12-25: 初始版本

