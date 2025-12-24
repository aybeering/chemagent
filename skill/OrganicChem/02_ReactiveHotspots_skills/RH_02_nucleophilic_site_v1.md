# RH_02_nucleophilic_site_v1 — 亲核位点识别

## Triggers
- 需要识别分子中可作为亲核试剂的位点
- 需要评估亲核位点的强度和类型
- 为 PhysChem 的 HOMO 分析提供目标

## Inputs
- 分子表示：SMILES / 结构描述
- 杂原子标签（推荐）：来自 SD_04 的 heteroatom_labels
- 共轭信息（推荐）：来自 SD_06 的 conjugation_map

## Outputs
```yaml
nucleophilic_sites:
  - site_id: "NU_1"
    atom_index: <int>
    site_type: "n_lonepair | pi_system | anion | enolate | carbanion | hydride"
    orbital_type: "n | pi | sigma"
    strength: "strong | moderate | weak"
    element: "<元素符号>"
    lone_pairs: <int>
    delocalization: "none | partial | full"
    modifiers: ["EWG_adjacent", "EDG_adjacent", "conjugated", "steric_hindered"]
    confidence: <0.0-1.0>
    notes: "<补充说明>"
```

## Rules

### 亲核位点类型

| 类型 | 描述 | 典型 HOMO | 强度范围 |
|------|------|----------|----------|
| n_lonepair | 杂原子孤对电子 | n 轨道 | 中-强 |
| pi_system | π 电子体系 | π 轨道 | 中-强 |
| anion | 负离子 | 高能 n 或 π | 强 |
| enolate | 烯醇负离子 | π 轨道 | 强 |
| carbanion | 碳负离子 | sp³ 孤对 | 强 |
| hydride | 负氢源 | σ (M-H) | 强 |

### 亲核强度判定

| 强度 | 条件 |
|------|------|
| strong | 负离子；未受吸电子基影响的孤对；活化芳环 |
| moderate | 中性杂原子孤对；普通烯烃 π |
| weak | 受吸电子基影响的孤对；缺电子芳环 |

### 调制因素

| 因素 | 对亲核性的影响 |
|------|---------------|
| 共轭稳定 | ↓ 降低（孤对离域） |
| 吸电子基相邻 | ↓ 降低 |
| 推电子基相邻 | ↑ 增强 |
| 位阻 | ↓ 反应性降低，但亲核性本身不变 |
| 极性溶剂 | ↓ 降低（溶剂化稳定） |

### 常见亲核位点识别规则

| 结构特征 | site_type | 强度 | 说明 |
|----------|-----------|------|------|
| R-O⁻ | anion | strong | 醇盐 |
| R-NH₂ | n_lonepair | moderate | 伯胺 |
| R₂NH | n_lonepair | moderate | 仲胺 |
| R₃N | n_lonepair | moderate | 叔胺，位阻可能限制 |
| R-OH | n_lonepair | weak | 醇，需活化 |
| R-O-R | n_lonepair | weak | 醚 |
| RC(=O)O⁻ | anion | moderate | 羧酸盐（共轭降低） |
| ArO⁻ | anion | moderate | 酚盐 |
| RC≡C⁻ | carbanion | strong | 炔负离子 |
| 烯烃 C=C | pi_system | moderate | π 电子 |
| 芳环 | pi_system | weak-moderate | 取决于取代基 |
| 吡啶 N | n_lonepair | moderate | 孤对不参与芳香性 |

## Steps
1. **遍历杂原子**
   - 从 heteroatom_labels 获取杂原子信息
   - 检查孤对可用性

2. **检测负离子**
   - 识别形式电荷为负的原子

3. **识别 π 亲核位点**
   - 从 conjugation_map 获取 π 系统
   - 评估 π 电子的可用性

4. **评估强度**
   - 考虑电子效应（邻近基团）
   - 考虑共轭离域程度

5. **标记调制因素**
   - EWG/EDG 影响
   - 位阻因素

## Examples

**Example 1: 二甲胺**
```yaml
input: "CNC"
output:
  nucleophilic_sites:
    - site_id: "NU_1"
      atom_index: 1
      site_type: "n_lonepair"
      orbital_type: "n"
      strength: "moderate"
      element: "N"
      lone_pairs: 1
      delocalization: "none"
      confidence: 0.9
      notes: "仲胺，典型亲核试剂"
```

**Example 2: 苯酚钠**
```yaml
input: "[O-]c1ccccc1"
output:
  nucleophilic_sites:
    - site_id: "NU_1"
      atom_index: 0
      site_type: "anion"
      orbital_type: "n"
      strength: "moderate"
      element: "O"
      lone_pairs: 3
      delocalization: "partial"
      modifiers: ["conjugated"]
      confidence: 0.85
      notes: "酚氧负离子，与芳环共轭降低亲核性"
```

**Example 3: 乙酸乙酯（酯）**
```yaml
input: "CCOC(=O)C"
output:
  nucleophilic_sites:
    - site_id: "NU_1"
      atom_index: 2
      site_type: "n_lonepair"
      orbital_type: "n"
      strength: "weak"
      element: "O"
      lone_pairs: 2
      delocalization: "partial"
      modifiers: ["EWG_adjacent"]
      confidence: 0.7
      notes: "酯氧孤对，因羰基吸电子效应减弱"
    - site_id: "NU_2"
      atom_index: 4
      site_type: "n_lonepair"
      orbital_type: "n"
      strength: "weak"
      element: "O"
      lone_pairs: 2
      delocalization: "none"
      modifiers: ["EWG_adjacent"]
      confidence: 0.6
      notes: "羰基氧孤对，亲核性较弱"
```

**Example 4: 1,3-丁二烯**
```yaml
input: "C=CC=C"
output:
  nucleophilic_sites:
    - site_id: "NU_1"
      atom_index: 0
      site_type: "pi_system"
      orbital_type: "pi"
      strength: "moderate"
      delocalization: "partial"
      confidence: 0.8
      notes: "共轭二烯，C1/C4 位为亲核中心"
    - site_id: "NU_2"
      atom_index: 3
      site_type: "pi_system"
      orbital_type: "pi"
      strength: "moderate"
      confidence: 0.8
```

**Example 5: 乙酰丙酮烯醇式**
```yaml
input: "CC(=O)C=C(C)O"
output:
  nucleophilic_sites:
    - site_id: "NU_1"
      atom_index: 3
      site_type: "enolate"
      orbital_type: "pi"
      strength: "strong"
      delocalization: "full"
      confidence: 0.9
      notes: "烯醇 β-碳，强亲核位点"
    - site_id: "NU_2"
      atom_index: 5
      site_type: "n_lonepair"
      orbital_type: "n"
      strength: "moderate"
      element: "O"
      confidence: 0.8
```

## Guardrails
- 不预测亲核反应的具体路径
- 溶剂效应需单独考虑（此处假设气相/非极性）
- 对于两可亲核试剂（如 CN⁻），需标注多个可能攻击位点
- 超共轭等弱效应由 PhysChem 进一步分析

## Confusable Cases
- 酰胺 N vs 胺 N：酰胺 N 孤对共轭，亲核性大降
- 吡咯 N vs 吡啶 N：吡咯孤对参与芳香性，不可用作亲核
- 烯醇 O vs C：O 亲核（硬）vs C 亲核（软）

## Changelog
- 2025-12-24: 初始版本

