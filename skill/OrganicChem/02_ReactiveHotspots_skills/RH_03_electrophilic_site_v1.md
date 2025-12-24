# RH_03_electrophilic_site_v1 — 亲电位点识别

## Triggers
- 需要识别分子中可作为亲电中心的位点
- 需要评估亲电位点的强度和类型
- 为 PhysChem 的 LUMO 分析提供目标

## Inputs
- 分子表示：SMILES / 结构描述
- 官能团信息（推荐）：来自 SD_03 的 functional_groups
- 杂原子标签（推荐）：来自 SD_04 的 heteroatom_labels

## Outputs
```yaml
electrophilic_sites:
  - site_id: "E_1"
    atom_index: <int>
    site_type: "carbonyl_C | sp3_with_LG | michael_acceptor | deficient_aromatic | carbocation_potential | imine_C | nitrile_C"
    orbital_type: "pi_star | sigma_star | vacant_p"
    strength: "strong | moderate | weak"
    leaving_group: "<LG 类型，若有>"
    partial_charge: "delta+ | positive"
    modifiers: ["EWG_adjacent", "EDG_adjacent", "steric_hindered", "activated"]
    confidence: <0.0-1.0>
    notes: "<补充说明>"
```

## Rules

### 亲电位点类型

| 类型 | 描述 | 典型 LUMO | 强度范围 |
|------|------|----------|----------|
| carbonyl_C | 羰基碳 | π* (C=O) | 中-强 |
| sp3_with_LG | sp³ 碳连离去基 | σ* (C-LG) | 中 |
| michael_acceptor | Michael 受体 | π* (共轭体系) | 中-强 |
| deficient_aromatic | 缺电子芳环 | π* (芳环) | 弱-中 |
| carbocation_potential | 潜在碳正离子 | vacant p | 强 |
| imine_C | 亚胺碳 | π* (C=N) | 中 |
| nitrile_C | 腈碳 | π* (C≡N) | 弱-中 |

### 亲电强度判定

| 强度 | 条件 |
|------|------|
| strong | 酰卤、酸酐、活化酯；α,β-不饱和羰基 β-C；碳正离子 |
| moderate | 醛酮；伯/仲卤代烷；硝基芳环 |
| weak | 叔卤代烷（位阻）；酯/酰胺羰基；普通芳环 |

### 离去基团能力排序

| 离去基团 | 能力 | 说明 |
|----------|------|------|
| N₂⁺ | 极强 | 重氮盐 |
| OTs, OMs, OTf | 极强 | 磺酸酯 |
| I⁻ | 强 | 碘代物 |
| Br⁻ | 强 | 溴代物 |
| Cl⁻ | 中 | 氯代物 |
| H₂O | 中 | 质子化羟基 |
| F⁻ | 弱 | 氟代物 |
| OH⁻ | 极弱 | 需活化 |
| RO⁻ | 极弱 | 需活化 |

### 调制因素

| 因素 | 对亲电性的影响 |
|------|---------------|
| 吸电子基相邻 | ↑ 增强 |
| 推电子基相邻 | ↓ 降低 |
| 共轭稳定离去基 | ↑ 增强 |
| 位阻大 | ↓ 反应性降低 |

## Steps
1. **识别羰基碳**
   - 从 functional_groups 获取羰基类官能团
   - 评估羰基活性（取决于邻近基团）

2. **识别 sp³ + LG 位点**
   - 找出连接离去基的 sp³ 碳
   - 评估离去基能力

3. **识别 Michael 受体**
   - 找出 α,β-不饱和羰基
   - 标记 β-碳为亲电位点

4. **识别缺电子芳环**
   - 检查芳环上的吸电子取代基

5. **评估强度**
   - 综合考虑电子效应和离去基能力

## Examples

**Example 1: 乙酰氯**
```yaml
input: "CC(=O)Cl"
output:
  electrophilic_sites:
    - site_id: "E_1"
      atom_index: 1
      site_type: "carbonyl_C"
      orbital_type: "pi_star"
      strength: "strong"
      leaving_group: "Cl"
      partial_charge: "delta+"
      modifiers: ["activated"]
      confidence: 0.95
      notes: "酰卤，极强亲电性"
```

**Example 2: 苯甲醛**
```yaml
input: "c1ccccc1C=O"
output:
  electrophilic_sites:
    - site_id: "E_1"
      atom_index: 6
      site_type: "carbonyl_C"
      orbital_type: "pi_star"
      strength: "strong"
      partial_charge: "delta+"
      confidence: 0.9
      notes: "醛基碳，典型亲电中心"
```

**Example 3: 丙烯醛 (Michael 受体)**
```yaml
input: "C=CC=O"
output:
  electrophilic_sites:
    - site_id: "E_1"
      atom_index: 2
      site_type: "carbonyl_C"
      orbital_type: "pi_star"
      strength: "strong"
      partial_charge: "delta+"
      confidence: 0.9
      notes: "醛基碳，1,2-加成位点"
    - site_id: "E_2"
      atom_index: 0
      site_type: "michael_acceptor"
      orbital_type: "pi_star"
      strength: "strong"
      partial_charge: "delta+"
      modifiers: ["conjugated"]
      confidence: 0.9
      notes: "β-碳，1,4-加成位点"
```

**Example 4: 溴代叔丁烷**
```yaml
input: "CC(C)(C)Br"
output:
  electrophilic_sites:
    - site_id: "E_1"
      atom_index: 1
      site_type: "carbocation_potential"
      orbital_type: "vacant_p"
      strength: "strong"
      leaving_group: "Br"
      modifiers: ["steric_hindered"]
      confidence: 0.85
      notes: "叔卤代烷，倾向 SN1（形成稳定叔碳正离子）"
```

**Example 5: 硝基苯**
```yaml
input: "c1ccc([N+](=O)[O-])cc1"
output:
  electrophilic_sites:
    - site_id: "E_1"
      atom_index: 1
      site_type: "deficient_aromatic"
      orbital_type: "pi_star"
      strength: "weak"
      partial_charge: "delta+"
      modifiers: ["EWG_adjacent"]
      confidence: 0.7
      notes: "硝基邻位碳，缺电子但仍需活化"
    - site_id: "E_2"
      atom_index: 3
      site_type: "deficient_aromatic"
      orbital_type: "pi_star"
      strength: "weak"
      confidence: 0.7
      notes: "硝基对位碳"
```

**Example 6: 溴乙烷**
```yaml
input: "CCBr"
output:
  electrophilic_sites:
    - site_id: "E_1"
      atom_index: 1
      site_type: "sp3_with_LG"
      orbital_type: "sigma_star"
      strength: "moderate"
      leaving_group: "Br"
      partial_charge: "delta+"
      confidence: 0.9
      notes: "伯溴代烷，典型 SN2 底物"
```

## Guardrails
- 不预测反应机理（SN1 vs SN2 需条件信息）
- 碳正离子仅标记"潜在"，实际生成取决于条件
- 对于酰胺羰基，强调其亲电性弱于酯
- 不评估 Lewis 酸中心（金属配位）

## Confusable Cases
- 酯 vs 酰胺：酯羰基更亲电
- Michael β-C vs 烯烃：需区分是否有共轭吸电子基
- SN1 vs SN2 底物：取决于碳的取代程度和条件

## Changelog
- 2025-12-24: 初始版本

