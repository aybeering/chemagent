# SD_04_heteroatom_label_v1 — 杂原子标签

## Triggers
- 需要详细标记分子中杂原子的电子特性
- 需要确定杂原子的杂化状态、孤对电子数、形式电荷
- 为 PhysChem 的 HOMO/LUMO 分析提供杂原子信息

## Inputs
- 分子表示：SMILES / 结构描述
- 关注元素（可选）：["N", "O", "S", "P", "F", "Cl", "Br", "I"]

## Outputs
```yaml
heteroatom_labels:
  - atom_index: <int>
    element: "<元素符号>"
    hybridization: "sp | sp2 | sp3"
    lone_pairs: <int>
    formal_charge: <int>
    environment: "<周围环境描述>"
    coordination: "<配位状态>"
    reactivity_hint: "nucleophilic | electrophilic | ambivalent | inert"
```

## Rules

### 杂化判定规则

| 元素 | 连接数 | 形式电荷 | 杂化 | 孤对数 |
|------|--------|----------|------|--------|
| **氧 (O)** |
| O | 2 | 0 | sp3 | 2 |
| O | 1 | 0 (=O) | sp2 | 2 |
| O | 1 | -1 | sp3 | 3 |
| O | 3 | +1 | sp3 | 1 |
| **氮 (N)** |
| N | 3 | 0 | sp3 | 1 |
| N | 2 | 0 (含双键) | sp2 | 1 |
| N | 1 | 0 (≡N) | sp | 1 |
| N | 4 | +1 | sp3 | 0 |
| N (芳环) | 2 | 0 | sp2 | 1 (可共轭) |
| **硫 (S)** |
| S | 2 | 0 | sp3 | 2 |
| S | 1 | 0 (=S) | sp2 | 2 |
| S | 4 | 0 (磺酰) | sp3 | 1 |
| **卤素** |
| F, Cl, Br, I | 1 | 0 | sp3 | 3 |

### 环境分类

| 环境类型 | 描述 | 示例 |
|----------|------|------|
| carbonyl_oxygen | 羰基氧 | C=O 中的 O |
| ether_oxygen | 醚氧 | C-O-C 中的 O |
| hydroxyl_oxygen | 羟基氧 | C-OH 中的 O |
| amine_nitrogen | 胺氮 | R-NH2, R2NH, R3N |
| amide_nitrogen | 酰胺氮 | RC(=O)NH2 |
| nitrile_nitrogen | 腈氮 | R-C≡N |
| pyridine_nitrogen | 吡啶氮 | 六元芳环含 N |
| pyrrole_nitrogen | 吡咯氮 | 五元芳环含 N-H |
| thioether_sulfur | 硫醚硫 | C-S-C |
| thiol_sulfur | 硫醇硫 | C-SH |

### 反应性提示

| reactivity_hint | 条件 | 典型行为 |
|-----------------|------|----------|
| nucleophilic | 孤对可用，无强吸电子基 | 亲核进攻 |
| electrophilic | 正电荷或强缺电子 | 亲电/Lewis 酸 |
| ambivalent | 可作亲核或亲电 | 取决于条件 |
| inert | 孤对被共轭/强拉电，或全卤代 | 低反应性 |

## Steps
1. **遍历所有杂原子**
   - 识别非 C、H 的原子
   
2. **确定杂化状态**
   - 根据连接数和键类型判定
   
3. **计算孤对电子数**
   - 价电子 - 成键电子 - 形式电荷调整
   
4. **判定环境**
   - 检查邻近基团
   
5. **给出反应性提示**
   - 综合孤对可用性和电子环境

## Examples

**Example 1: 二甲醚**
```yaml
input: "COC"
output:
  heteroatom_labels:
    - atom_index: 1
      element: "O"
      hybridization: "sp3"
      lone_pairs: 2
      formal_charge: 0
      environment: "ether_oxygen"
      reactivity_hint: "nucleophilic"
```

**Example 2: 乙酰胺**
```yaml
input: "CC(=O)N"
output:
  heteroatom_labels:
    - atom_index: 2
      element: "O"
      hybridization: "sp2"
      lone_pairs: 2
      formal_charge: 0
      environment: "carbonyl_oxygen"
      reactivity_hint: "nucleophilic"
    - atom_index: 3
      element: "N"
      hybridization: "sp2"
      lone_pairs: 1
      formal_charge: 0
      environment: "amide_nitrogen"
      reactivity_hint: "ambivalent"
      notes: "孤对与羰基共轭，亲核性降低"
```

**Example 3: 吡啶**
```yaml
input: "c1ccncc1"
output:
  heteroatom_labels:
    - atom_index: 3
      element: "N"
      hybridization: "sp2"
      lone_pairs: 1
      formal_charge: 0
      environment: "pyridine_nitrogen"
      reactivity_hint: "nucleophilic"
      notes: "孤对在环平面外，不参与芳香性"
```

**Example 4: 硝基苯**
```yaml
input: "c1ccc([N+](=O)[O-])cc1"
output:
  heteroatom_labels:
    - atom_index: 4
      element: "N"
      hybridization: "sp2"
      lone_pairs: 0
      formal_charge: +1
      environment: "nitro_nitrogen"
      reactivity_hint: "inert"
    - atom_index: 5
      element: "O"
      hybridization: "sp2"
      lone_pairs: 2
      formal_charge: 0
      environment: "nitro_oxygen"
      reactivity_hint: "inert"
    - atom_index: 6
      element: "O"
      hybridization: "sp3"
      lone_pairs: 3
      formal_charge: -1
      environment: "nitro_oxygen"
      reactivity_hint: "nucleophilic"
```

**Example 5: 三氟甲基**
```yaml
input: "FC(F)(F)C"
output:
  heteroatom_labels:
    - atom_index: 0
      element: "F"
      hybridization: "sp3"
      lone_pairs: 3
      formal_charge: 0
      environment: "C-F_bond"
      reactivity_hint: "inert"
      notes: "强电负性，孤对紧密"
    # 同理 F at index 2, 3
```

## Guardrails
- 不处理金属配合物的复杂配位化学
- 对于罕见杂原子（Se, Te, As 等），降低置信度
- 不预测质子化/去质子化状态，除非 SMILES 已明确标记
- 芳环杂原子需区分"孤对参与芳香性"与"孤对独立"

## Confusable Cases
- 酰胺 N vs 胺 N：酰胺 N 孤对共轭，亲核性低
- 吡咯 N vs 吡啶 N：吡咯孤对参与芳香性，吡啶孤对独立
- 硝基 vs 亚硝基：氧化态不同

## Changelog
- 2025-12-24: 初始版本

