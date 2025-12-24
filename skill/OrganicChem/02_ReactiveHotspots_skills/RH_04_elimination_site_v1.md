# RH_04_elimination_site_v1 — 消除位点识别

## Triggers
- 需要识别分子中可能发生消除反应的位点
- 需要评估 β-H + 离去基团的组合
- 需要预测消除机理倾向（E2/E1cb/E1）

## Inputs
- 分子表示：SMILES / 结构描述
- 亲电位点信息（推荐）：来自 RH_03 的 electrophilic_sites
- 骨架信息（推荐）：来自 SD_02 的 skeleton

## Outputs
```yaml
elimination_sites:
  - site_id: "EL_1"
    c_alpha: <int>                    # α 碳索引（连 LG）
    c_beta: <int>                     # β 碳索引（连 β-H）
    leaving_group: "<LG 类型>"
    lg_quality: "excellent | good | moderate | poor"
    beta_h_count: <int>               # β 氢数量
    beta_h_acidity: "high | moderate | low"  # β-H 酸性
    mechanism_preference: "E2 | E1cb | E1 | competing"
    antiperiplanar_available: true | false
    product_alkene: "<预期烯烃描述>"
    zaitsev_vs_hofmann: "Zaitsev | Hofmann | equal"
    confidence: <0.0-1.0>
    notes: "<补充说明>"
```

## Rules

### 消除反应必要条件

1. **α 碳**：连接离去基团的碳
2. **β 碳**：与 α 碳相邻，且连有氢原子
3. **离去基团**：可以离去的基团（卤素、OTs、OH₂⁺ 等）

### 机理判定规则

| 机理 | 条件 | 特征 |
|------|------|------|
| E2 | 强碱 + 好 LG + β-H | 一步协同，需反式共平面 |
| E1cb | 强碱 + 差 LG + 酸性 β-H | 先去 β-H 形成碳负离子 |
| E1 | 弱碱/无碱 + 好 LG + 稳定碳正离子 | 先离去形成碳正离子 |

### β-H 酸性评估

| β-H 酸性 | 条件 | 说明 |
|----------|------|------|
| high | β-C 连接 EWG（如羰基、硝基） | pKa < 20 |
| moderate | 普通烷基 | pKa ~ 45-50 |
| low | β-C 连接 EDG | 更难被碱夺取 |

### Zaitsev vs Hofmann 规则

| 规则 | 条件 | 主产物 |
|------|------|--------|
| Zaitsev | 大多数情况 | 取代基较多的烯烃（更稳定） |
| Hofmann | 大位阻碱；季铵盐消除；β-H 酸性高 | 取代基较少的烯烃 |

### 反式共平面要求

- **E2 机理**：β-H 与 LG 必须反式共平面（180°）
- 环状体系中需检查构象
- 若无法达到反式共平面，E2 不可行

## Steps
1. **识别所有 α-C + LG 组合**
   - 从 electrophilic_sites 获取 sp3_with_LG 类型

2. **对每个 α-C 找出所有 β-C**
   - 与 α-C 相邻的碳原子
   - 统计 β-H 数量

3. **评估 β-H 酸性**
   - 检查 β-C 邻近是否有 EWG

4. **判断反式共平面可能性**
   - 对于开链：通常可行
   - 对于环状：需检查构象

5. **预测机理倾向**
   - 综合 LG 能力、β-H 酸性、碳正离子稳定性

6. **预测产物倾向**
   - Zaitsev vs Hofmann

## Examples

**Example 1: 2-溴丁烷**
```yaml
input: "CCC(Br)C"
output:
  elimination_sites:
    - site_id: "EL_1"
      c_alpha: 2
      c_beta: 1
      leaving_group: "Br"
      lg_quality: "good"
      beta_h_count: 2
      beta_h_acidity: "moderate"
      mechanism_preference: "E2"
      antiperiplanar_available: true
      product_alkene: "2-butene (major)"
      zaitsev_vs_hofmann: "Zaitsev"
      confidence: 0.85
    - site_id: "EL_2"
      c_alpha: 2
      c_beta: 3
      leaving_group: "Br"
      lg_quality: "good"
      beta_h_count: 3
      beta_h_acidity: "moderate"
      mechanism_preference: "E2"
      antiperiplanar_available: true
      product_alkene: "1-butene (minor)"
      zaitsev_vs_hofmann: "Hofmann"
      confidence: 0.85
```

**Example 2: 环己基甲磺酸酯**
```yaml
input: "C1CCC(OC(=O)C(F)(F)F)CC1"  # simplified
output:
  elimination_sites:
    - site_id: "EL_1"
      c_alpha: 3
      c_beta: 2
      leaving_group: "OMs"
      lg_quality: "excellent"
      beta_h_count: 1
      mechanism_preference: "E2"
      antiperiplanar_available: true
      product_alkene: "cyclohexene"
      confidence: 0.9
      notes: "环己烷椅式构象中，反式共平面 β-H 在轴向"
```

**Example 3: 2-溴-2-甲基丙烷（叔丁基溴）**
```yaml
input: "CC(C)(C)Br"
output:
  elimination_sites:
    - site_id: "EL_1"
      c_alpha: 1
      c_beta: 0
      leaving_group: "Br"
      lg_quality: "good"
      beta_h_count: 3
      beta_h_acidity: "moderate"
      mechanism_preference: "E1"
      product_alkene: "isobutylene"
      confidence: 0.8
      notes: "叔碳正离子稳定，倾向 E1；与 SN1 竞争"
```

**Example 4: β-硝基乙醇衍生物**
```yaml
input: "O=[N+]([O-])CCBr"
output:
  elimination_sites:
    - site_id: "EL_1"
      c_alpha: 3
      c_beta: 2
      leaving_group: "Br"
      lg_quality: "good"
      beta_h_count: 2
      beta_h_acidity: "high"
      mechanism_preference: "E1cb"
      product_alkene: "nitroethene"
      confidence: 0.85
      notes: "硝基使 β-H 酸性增强，倾向 E1cb"
```

## Guardrails
- 不预测具体反应条件（碱的类型、溶剂）
- E1 与 SN1 通常竞争，需标注
- 环状体系需特别注意构象
- 若 β-H 为 0，标记"无消除位点"

## Confusable Cases
- E2 vs SN2：取决于碱的强度和位阻
- E1 vs SN1：取决于条件，通常同时发生
- E1cb vs E2：取决于 β-H 酸性

## Changelog
- 2025-12-24: 初始版本

