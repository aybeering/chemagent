# GAS_02_gassing_flags_v1 — 产气风险红旗

## Triggers
- 需要识别分子结构中的产气风险特征
- 需要评估可能产生的气体类型
- 进行电解液安全性筛查

## Inputs
- 分子表示：SMILES / 官能团列表
- 上游 OrganicChem 输出：官能团、敏感位点
- 应用场景：溶剂 / 添加剂
- 使用条件（可选）：正极/负极、电压范围

## Outputs
- `gas_flags`: 产气风险红旗列表
  - `gas_type`: 气体类型
  - `source`: 产气来源结构
  - `likelihood`: 产气可能性
  - `trigger`: 触发条件
  - `mechanism_hint`: 机理提示
- `total_gas_risk`: 总体产气风险等级
- `confidence`: 置信度

## Rules
### 产气类型与来源

**CO₂ 产气**：
| 来源结构 | 触发条件 | 可能性 | 说明 |
|---------|---------|-------|------|
| 碳酸酯（环状） | 还原 | 高 | SEI 形成正常产气 |
| 碳酸酯（线性） | 还原 | 高 | 分解产气 |
| 碳酸酯 | 高压氧化 | 中 | 氧化分解 |
| 羧酸/酯 | 脱羧 | 低-中 | 热分解 |

**CO 产气**：
| 来源结构 | 触发条件 | 可能性 | 说明 |
|---------|---------|-------|------|
| 碳酸酯 | 深度还原 | 中 | 进一步分解 |
| 醛/酮 | 还原 | 低-中 | 脱羰 |
| 甲酸酯 | 分解 | 中 | 特定结构 |

**H₂ 产气**（严重警示）：
| 来源结构 | 触发条件 | 可能性 | 说明 |
|---------|---------|-------|------|
| 活泼 O-H（醇/水） | 接触 Li | 极高 | 剧烈反应 |
| 活泼 N-H（胺） | 接触 Li | 高 | 反应产 H₂ |
| 活泼 S-H（硫醇） | 接触 Li | 高 | 反应产 H₂ |

**HF 产气**（腐蚀警示）：
| 来源结构 | 触发条件 | 可能性 | 说明 |
|---------|---------|-------|------|
| C-F + 痕量水 | 水解 | 低-中 | 需控制水分 |
| LiPF₆ + 痕量水 | 水解 | 中 | 盐分解 |
| C-F 断裂 + 水 | 还原 + 水 | 低-中 | 生成 F⁻ + H₂O → HF |

**C₂H₄ 产气**：
| 来源结构 | 触发条件 | 可能性 | 说明 |
|---------|---------|-------|------|
| EC | 还原 | 中 | 特定路径脱羰 |
| 乙烯基化合物 | 热分解 | 低 | 不常见 |

**其他气体**：
| 气体 | 来源 | 触发条件 |
|-----|------|---------|
| N₂ | 叠氮化物 | 分解（危险！） |
| NOₓ | 硝基化合物 | 还原分解 |
| SOₓ | 含 S 化合物 | 氧化分解 |

### 产气风险等级
| 等级 | 条件 |
|-----|------|
| 高 | 存在活泼 H（H₂ 风险）或不稳定基团 |
| 中 | 碳酸酯类正常产气 / C-F + 水分控制不佳 |
| 低 | 惰性结构 / 成熟材料可控产气 |

## Steps
1. **扫描高风险结构**
   - 活泼 H（O-H、N-H、S-H）
   - 不稳定基团（叠氮、硝基等）

2. **扫描中等风险结构**
   - 碳酸酯（正常产气）
   - C-F（HF 风险）
   - 醛/酮（CO 风险）

3. **评估各气体风险**
   - 结合应用条件
   - 确定触发条件

4. **汇总产气风险**

## Examples
**Example 1: EC（正常产气）**
```yaml
input:
  smiles: "C1COC(=O)O1"
  application: "solvent"
  condition: "anode"
    
output:
  gas_flags:
    - gas_type: "CO2"
      source: "环状碳酸酯还原分解"
      likelihood: "high"
      trigger: "首次锂化（SEI 形成）"
      mechanism_hint: "2EC + 2e⁻ + 2Li⁺ → Li₂CO₃ + C₂H₄ 或 CO₂ + ..."
    - gas_type: "C2H4"
      source: "EC 还原"
      likelihood: "medium"
      trigger: "首次锂化"
      mechanism_hint: "特定还原路径"
  total_gas_risk: "low"
  notes: "EC 产气是正常 SEI 形成过程，通过化成工艺排气管理"
  confidence: "high"
```

**Example 2: 甲醇（高风险）**
```yaml
input:
  smiles: "CO"
  application: "solvent_candidate"
  condition: "anode"
    
output:
  gas_flags:
    - gas_type: "H2"
      source: "O-H 活泼氢"
      likelihood: "high"
      trigger: "接触锂金属或低电位负极"
      mechanism_hint: "2CH₃OH + 2Li → 2CH₃OLi + H₂↑"
  total_gas_risk: "high"
  notes: "含活泼 O-H，与锂剧烈反应产 H₂，严重安全隐患"
  confidence: "high"
```

**Example 3: FEC（可控产气）**
```yaml
input:
  smiles: "FC1COC(=O)O1"
  application: "additive"
  condition: "anode"
    
output:
  gas_flags:
    - gas_type: "CO2"
      source: "还原开环分解"
      likelihood: "high"
      trigger: "首次锂化"
      mechanism_hint: "优先于 EC 还原"
    - gas_type: "HF"
      source: "C-F 断裂后 F⁻ + 痕量水"
      likelihood: "low"
      trigger: "电解液含水量高"
      mechanism_hint: "F⁻ + H₂O → HF + OH⁻"
  total_gas_risk: "low"
  notes: "FEC 是成熟添加剂，控制水分即可避免 HF 问题"
  confidence: "high"
```

**Example 4: 硝基甲烷（极高风险）**
```yaml
input:
  smiles: "C[N+](=O)[O-]"
  application: "solvent_candidate"
    
output:
  gas_flags:
    - gas_type: "NOx"
      source: "硝基还原分解"
      likelihood: "high"
      trigger: "还原条件"
      mechanism_hint: "硝基接受电子分解"
    - gas_type: "explosion_risk"
      source: "硝基化合物"
      likelihood: "medium"
      trigger: "冲击/热/还原"
      mechanism_hint: "硝基化合物固有风险"
  total_gas_risk: "high"
  notes: "硝基化合物有爆炸风险，不适合电池应用"
  confidence: "high"
```

## Guardrails
- 不预测具体产气量（mL/g 等）
- 产气是趋势判断，实际受条件影响
- "正常产气"（如 SEI 形成）不等于安全问题
- 高风险结构应直接排除，不建议使用
- 定量产气测试需 DEMS、在线质谱等

## Dependencies
- 上游：OrganicChem 官能团识别
- 关联：ROLE_05_unsuitable_flag_v1（不适合标记）

## Changelog
- 2025-12-25: 初始版本

