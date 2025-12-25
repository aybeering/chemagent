# CEI_02_oxidation_site_v1 — 易氧化位点识别

## Triggers
- 需要识别分子中容易被电化学氧化的位点
- 需要评估各位点的相对氧化活性
- 依赖 PhysChem 的 HOMO 分析输出

## Inputs
- 分子表示：SMILES / 官能团列表
- 上游 PhysChem 输出：
  - HOMO 排序（ox_sites_ranked）
  - 氧化位点类型（n/pi/sigma_CH）
- 正极条件（可选）：电压范围

## Outputs
- `oxidation_sites`: 易氧化位点列表
  - `site`: 位点描述
  - `site_type`: 位点类型（n / pi / sigma_CH）
  - `homo_contribution`: HOMO 贡献描述
  - `activity`: 氧化活性（high / medium / low）
  - `reason`: 易氧化原因
- `dominant_site`: 最易氧化位点
- `substituent_effect`: 取代基对氧化位点的调制
- `confidence`: 置信度

## Rules
### HOMO 类型与氧化活性

**n 轨道（杂原子孤对）**：
| 原子类型 | 相对 HOMO | 氧化活性 |
|---------|----------|---------|
| 胺 N（脂肪族） | 高 | 高 |
| 醚 O | 中-高 | 中-高 |
| 酯 O | 中 | 中 |
| 砜 O | 低 | 低 |
| 氟代醚 O | 低 | 低 |

**π 轨道（不饱和体系）**：
| 结构类型 | 相对 HOMO | 氧化活性 |
|---------|----------|---------|
| 富电子芳环（-OMe, -NR₂） | 高 | 高 |
| 普通芳环 | 中 | 中 |
| 缺电子芳环（-NO₂, -CF₃） | 低 | 低 |
| 烯烃 | 中 | 中 |

**σ 轨道（C-H 键）**：
| C-H 类型 | 相对活性 | 条件 |
|---------|---------|------|
| 苄位 C-H | 中 | 被芳环活化 |
| α-醚 C-H | 中 | 被 O 活化 |
| 普通烷基 C-H | 低 | 需极高电位 |

### 取代基调制效应
| 取代基 | 对 HOMO 的影响 | 对氧化稳定性的影响 |
|-------|---------------|------------------|
| -F, -CF₃ | 降低 HOMO（-I） | 提高稳定性 |
| -NO₂, -CN | 降低 HOMO（-I/-M） | 提高稳定性 |
| -OMe, -NR₂ | 升高 HOMO（+M） | 降低稳定性 |
| -alkyl | 略升高 HOMO（+I） | 略降低稳定性 |

## Steps
1. **解析 PhysChem HOMO 输出**
   - 获取 ox_sites_ranked 列表
   - 识别各位点的 HOMO 类型

2. **评估各位点氧化活性**
   - 根据 HOMO 类型和相对排序
   - 考虑取代基调制效应

3. **确定主导氧化位点**
   - HOMO 贡献最大的位点
   - 评估置信度

4. **输出结构化结果**

## Examples
**Example 1: EC**
```yaml
input:
  smiles: "C1COC(=O)O1"
  phys_chem:
    oxidation_tendency:
      ox_sites_ranked:
        - { rank: 1, site: "酯氧孤对", homo_type: "n" }
        - { rank: 2, site: "醚氧孤对", homo_type: "n" }
        
output:
  oxidation_sites:
    - site: "酯氧孤对（C=O 中的 O）"
      site_type: "n"
      homo_contribution: "主要 HOMO 贡献"
      activity: "medium"
      reason: "羰基吸电子效应略降低 n 轨道能级"
    - site: "醚氧孤对（环内 O）"
      site_type: "n"
      homo_contribution: "次要 HOMO 贡献"
      activity: "medium"
      reason: "sp³ 氧的 n 孤对"
  dominant_site: "酯氧孤对"
  substituent_effect: "环状结构无额外取代基调制"
  confidence: "high"
```

**Example 2: BTFE**
```yaml
input:
  smiles: "FC(F)(F)COCC(F)(F)F"
  phys_chem:
    oxidation_tendency:
      ox_sites_ranked:
        - { rank: 1, site: "醚氧孤对", homo_type: "n" }
        
output:
  oxidation_sites:
    - site: "醚氧孤对"
      site_type: "n"
      homo_contribution: "唯一 HOMO 贡献，但被大幅降低"
      activity: "low"
      reason: "两个 CF₃ 的强 -I 效应显著降低 O 的 n 轨道能级"
  dominant_site: "醚氧孤对（被抑制）"
  substituent_effect: "CF₃ 的 -I 效应使 HOMO 能级大幅降低，提高氧化稳定性"
  confidence: "high"
```

**Example 3: DME**
```yaml
input:
  smiles: "COCCOC"
  phys_chem:
    oxidation_tendency:
      ox_sites_ranked:
        - { rank: 1, site: "醚氧孤对", homo_type: "n" }
        - { rank: 2, site: "α-醚 C-H", homo_type: "sigma" }
        
output:
  oxidation_sites:
    - site: "醚氧孤对（两个）"
      site_type: "n"
      homo_contribution: "主要 HOMO 贡献"
      activity: "high"
      reason: "醚类 n 轨道能级高，易氧化"
    - site: "α-醚 C-H"
      site_type: "sigma_CH"
      homo_contribution: "次要贡献"
      activity: "medium"
      reason: "被 O 活化的 C-H，可能脱氢"
  dominant_site: "醚氧孤对"
  substituent_effect: "无吸电子基，HOMO 能级未被降低"
  confidence: "high"
```

**Example 4: Sulfolane**
```yaml
input:
  smiles: "C1CCS(=O)(=O)C1"
  phys_chem:
    oxidation_tendency:
      ox_sites_ranked:
        - { rank: 1, site: "环碳 C-H", homo_type: "sigma" }
        
output:
  oxidation_sites:
    - site: "砜氧"
      site_type: "n"
      homo_contribution: "低 HOMO 贡献（砜基强吸电子）"
      activity: "low"
      reason: "砜基的强吸电子效应使 O 的 n 孤对能级很低"
    - site: "环碳 C-H"
      site_type: "sigma_CH"
      homo_contribution: "相对主要"
      activity: "low"
      reason: "被砜基弱活化"
  dominant_site: "无明显易氧化位点"
  substituent_effect: "砜基（-SO₂-）是强吸电子基，大幅降低 HOMO，提高氧化稳定性"
  confidence: "high"
```

## Guardrails
- 依赖 PhysChem HOMO 输出，不独立计算
- 不预测具体氧化电位
- 实际氧化行为受正极材料、电解液配方影响
- 动力学因素可能改变氧化选择性
- 新型结构需实验验证

## Dependencies
- 必需：PhysChem HOMO 分析输出
- 可选：OrganicChem 官能团识别（辅助解释）

## Changelog
- 2025-12-25: 初始版本

