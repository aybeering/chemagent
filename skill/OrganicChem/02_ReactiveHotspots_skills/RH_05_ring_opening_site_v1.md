# RH_05_ring_opening_site_v1 — 开环位点识别

## Triggers
- 需要识别分子中可能发生开环反应的位点
- 需要评估环张力驱动的反应
- 为 PhysChem 的 LUMO（环张力）分析提供目标

## Inputs
- 分子表示：SMILES / 结构描述
- 环系信息（必需）：来自 SD_05 的 ring_info
- 官能团信息（推荐）：来自 SD_03 的 functional_groups

## Outputs
```yaml
ring_opening_sites:
  - site_id: "RO_1"
    ring_id: "<对应 ring_id>"
    ring_size: <int>
    ring_type: "epoxide | lactone | cyclic_carbonate | lactam | aziridine | small_carbocycle | strained_heterocycle"
    attack_atom: <int>                 # 被攻击的原子索引
    breaking_bond: [<int>, <int>]      # 断裂的键
    strain_driven: true | false
    strain_level: "high | medium | low"
    nucleophile_preference: "hard | soft | ambivalent"
    regioselectivity: "<区域选择性说明>"
    opening_mode: "SN2 | addition_elimination | radical | thermal"
    confidence: <0.0-1.0>
    notes: "<补充说明>"
```

## Rules

### 开环反应类型

| 环类型 | 开环驱动力 | 典型机理 | 常用条件 |
|--------|-----------|---------|---------|
| 环氧 (3-ring) | 高张力 | SN2 | 亲核试剂 + 酸/碱 |
| 氮杂环丙烷 | 高张力 | SN2 | 亲核试剂 |
| 环丙烷 | 高张力 | 热/光 | 需活化（取代基） |
| β-内酰胺 (4-ring) | 中等张力 + 酰基活性 | 加成-消除 | 亲核试剂 |
| 内酯 (5-ring) | 酰基活性 | 加成-消除 | 水解/醇解 |
| 环状碳酸酯 | 酰基活性 + 轻度张力 | 加成-消除 | 电化学/亲核 |
| 内酰胺 | 酰基活性 | 加成-消除 | 水解 |

### 环张力等级

| 环大小 | 张力等级 | 开环倾向 |
|--------|---------|---------|
| 3 | high | 极易 |
| 4 | high | 易 |
| 5 | low | 需活化 |
| 6 | none | 需活化 |
| 7+ | low | 取决于结构 |

### 区域选择性规则

#### 环氧开环
| 条件 | 攻击位点 | 原因 |
|------|---------|------|
| 酸催化 | 取代较多的碳 | SN1-like，稳定碳正离子 |
| 碱催化/亲核 | 取代较少的碳 | SN2，位阻控制 |

#### 内酯/碳酸酯开环
- 亲核进攻羰基碳（酰基位置）
- 酰氧键断裂（BAc2 机理）

### 亲核试剂偏好

| 偏好 | 适用亲核试剂 | 说明 |
|------|-------------|------|
| hard | H₂O, OH⁻, RO⁻, F⁻ | 电荷控制 |
| soft | RS⁻, I⁻, RSe⁻ | 轨道控制 |
| ambivalent | 胺类 | 介于两者之间 |

## Steps
1. **遍历所有环**
   - 从 ring_info 获取环信息

2. **筛选可开环的环**
   - 高张力环（3-4 元）
   - 含活化基团的环（内酯、碳酸酯、内酰胺）

3. **确定攻击位点**
   - 环氧/氮杂环丙烷：环上碳
   - 内酯/碳酸酯：羰基碳

4. **确定断键位置**
   - 根据机理预测

5. **评估区域选择性**
   - 考虑取代基效应和反应条件

## Examples

**Example 1: 环氧乙烷**
```yaml
input: "C1OC1"
output:
  ring_opening_sites:
    - site_id: "RO_1"
      ring_id: "RING_1"
      ring_size: 3
      ring_type: "epoxide"
      attack_atom: 0
      breaking_bond: [0, 1]
      strain_driven: true
      strain_level: "high"
      nucleophile_preference: "ambivalent"
      regioselectivity: "对称，无区域选择性问题"
      opening_mode: "SN2"
      confidence: 0.95
    - site_id: "RO_2"
      ring_id: "RING_1"
      ring_size: 3
      ring_type: "epoxide"
      attack_atom: 2
      breaking_bond: [1, 2]
      strain_driven: true
      strain_level: "high"
      opening_mode: "SN2"
      confidence: 0.95
      notes: "两个碳等效"
```

**Example 2: 1,2-环氧丙烷（不对称环氧）**
```yaml
input: "CC1OC1"
output:
  ring_opening_sites:
    - site_id: "RO_1"
      ring_id: "RING_1"
      ring_size: 3
      ring_type: "epoxide"
      attack_atom: 2
      breaking_bond: [1, 2]
      strain_driven: true
      strain_level: "high"
      regioselectivity: "碱性条件：攻击无取代碳（SN2）"
      opening_mode: "SN2"
      confidence: 0.9
    - site_id: "RO_2"
      ring_id: "RING_1"
      ring_size: 3
      ring_type: "epoxide"
      attack_atom: 1
      breaking_bond: [0, 1]
      strain_driven: true
      strain_level: "high"
      regioselectivity: "酸性条件：攻击甲基取代碳（碳正离子稳定）"
      opening_mode: "SN2"
      confidence: 0.85
```

**Example 3: γ-丁内酯**
```yaml
input: "C1CCC(=O)O1"
output:
  ring_opening_sites:
    - site_id: "RO_1"
      ring_id: "RING_1"
      ring_size: 5
      ring_type: "lactone"
      attack_atom: 3
      breaking_bond: [3, 5]
      strain_driven: false
      strain_level: "low"
      nucleophile_preference: "hard"
      regioselectivity: "亲核进攻羰基碳，酰氧键断裂"
      opening_mode: "addition_elimination"
      confidence: 0.85
      notes: "五元内酯，水解开环"
```

**Example 4: 碳酸乙烯酯 (EC)**
```yaml
input: "C1COC(=O)O1"
output:
  ring_opening_sites:
    - site_id: "RO_1"
      ring_id: "RING_1"
      ring_size: 5
      ring_type: "cyclic_carbonate"
      attack_atom: 3
      breaking_bond: [3, 2]
      strain_driven: true
      strain_level: "low"
      nucleophile_preference: "hard"
      regioselectivity: "电化学还原：羰基优先接受电子"
      opening_mode: "addition_elimination"
      confidence: 0.9
      notes: "环状碳酸酯，电化学开环形成 SEI"
```

**Example 5: β-丙内酯**
```yaml
input: "C1CC(=O)O1"
output:
  ring_opening_sites:
    - site_id: "RO_1"
      ring_id: "RING_1"
      ring_size: 4
      ring_type: "lactone"
      attack_atom: 2
      breaking_bond: [2, 3]
      strain_driven: true
      strain_level: "high"
      regioselectivity: "四元内酯高张力，易开环"
      opening_mode: "addition_elimination"
      confidence: 0.95
```

## Guardrails
- 不预测具体开环产物（需完整反应信息）
- 无张力且无活化基团的环，标记"需特殊条件"
- 聚合反应（如环氧开环聚合）需单独分析
- 电化学开环由 PhysChem 进一步分析

## Confusable Cases
- 内酯 vs 酯：内酯是环状酯
- 环氧 vs 醚：环氧是三元环醚
- 碳酸酯 vs 酯：碳酸酯有两个酯氧

## Changelog
- 2025-12-24: 初始版本

