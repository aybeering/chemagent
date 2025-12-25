# Query_Catalog — 跨域查询能力目录

| Field | Value |
|-------|-------|
| Type | Capability Registry |
| Created | 2025-12-25 |
| Purpose | 定义所有可用的跨域查询能力 |

本文件定义了所有技能域可以提供的原子查询能力，供其他域调用。

---

## 1. OrganicChem 提供的查询能力

### 1.1 结构查询类

| Query ID | 名称 | 描述 |
|----------|------|------|
| `OC.adjacent_groups` | 邻近基团查询 | 指定原子周围的官能团 |
| `OC.functional_group_at` | 位点官能团 | 指定位置的官能团类型 |
| `OC.ring_membership` | 环成员查询 | 原子是否在环内及环信息 |
| `OC.bond_type` | 键类型查询 | 两原子间的键类型 |
| `OC.skeleton_type` | 骨架类型 | 分子骨架分类 |

#### OC.adjacent_groups

```yaml
query:
  type: "OC.adjacent_groups"
  params:
    smiles: "<SMILES>"
    target_atom: <int>  # 目标原子索引
    radius: <int>       # 搜索半径（键数），默认 2
    
response:
  adjacent_groups:
    - distance: <int>
      atom_index: <int>
      element: "<元素符号>"
      fg_type: "<官能团类型 | null>"
      is_ewg: <bool | null>  # 是否吸电子基
      is_edg: <bool | null>  # 是否推电子基
```

#### OC.functional_group_at

```yaml
query:
  type: "OC.functional_group_at"
  params:
    smiles: "<SMILES>"
    atom_index: <int>
    
response:
  functional_group:
    fg_type: "<官能团类型>"
    fg_category: "carbonyl | nitrogen | oxygen | halogen | sulfur | unsaturated | other"
    center_atom: <int>
    atoms: [<int>]
    confidence: <float>
```

---

### 1.2 反应性查询类

| Query ID | 名称 | 描述 |
|----------|------|------|
| `OC.nucleophilicity` | 亲核性 | 指定位点的亲核能力 |
| `OC.electrophilicity` | 亲电性 | 指定位点的亲电能力 |
| `OC.leaving_group_ability` | 离去基团能力 | 基团的离去能力 |
| `OC.ring_strain` | 环张力 | 环的张力水平 |

#### OC.nucleophilicity

```yaml
query:
  type: "OC.nucleophilicity"
  params:
    smiles: "<SMILES>"
    atom_index: <int>
    
response:
  nucleophilicity:
    strength: "strong | moderate | weak | none"
    orbital_type: "n | pi | sigma"
    modifiers: ["EWG_adjacent", "EDG_adjacent", "conjugated", ...]
    confidence: <float>
```

---

### 1.3 共轭与电子体系查询

| Query ID | 名称 | 描述 |
|----------|------|------|
| `OC.conjugation_check` | 共轭检查 | 原子是否与某体系共轭 |
| `OC.pi_system` | π 体系 | 原子所属的 π 体系 |
| `OC.aromatic_check` | 芳香性检查 | 环是否芳香 |

#### OC.conjugation_check

```yaml
query:
  type: "OC.conjugation_check"
  params:
    smiles: "<SMILES>"
    atom_index: <int>
    system_type: "carbonyl | aromatic | alkene | any"  # 可选
    
response:
  conjugation:
    is_conjugated: <bool>
    conjugation_type: "<描述>"
    extent: "full | partial | none"
    conjugated_with: [<atom_indices>]
```

---

## 2. PhysChem 提供的查询能力

### 2.1 电子效应查询类

| Query ID | 名称 | 描述 |
|----------|------|------|
| `PC.ewg_strength` | 吸电子基强度 | 取代基的 -I/-M 强度 |
| `PC.edg_strength` | 推电子基强度 | 取代基的 +I/+M 强度 |
| `PC.local_electron_density` | 局部电子密度 | 位点的电子密度趋势 |
| `PC.effect_on_bond` | 键的电子效应 | 取代基对特定键的影响 |

#### PC.ewg_strength

```yaml
query:
  type: "PC.ewg_strength"
  params:
    smiles: "<SMILES>"
    substituent_atom: <int>  # 取代基中心原子
    target_atom: <int>       # 效应传递目标（可选）
    
response:
  ewg_strength:
    I_effect:
      sign: "-I"
      strength: "very_strong | strong | medium | weak"
      decay_range: <int>  # 有效键数
    M_effect:
      sign: "-M | none"
      strength: "strong | medium | weak | none"
      requires_conjugation: <bool>
    net_classification: "strong_ewg | moderate_ewg | weak_ewg"
    effect_on_target:  # 若指定了 target_atom
      direction: "electron_withdrawing"
      magnitude: "significant | moderate | weak"
```

#### PC.local_electron_density

```yaml
query:
  type: "PC.local_electron_density"
  params:
    smiles: "<SMILES>"
    atom_index: <int>
    
response:
  electron_density:
    tendency: "electron_rich | neutral | electron_poor"
    contributing_factors:
      - factor: "<因素描述>"
        effect: "+/- electron density"
    confidence: <float>
```

---

### 2.2 轨道查询类

| Query ID | 名称 | 描述 |
|----------|------|------|
| `PC.homo_contributor` | HOMO 贡献者 | 位点对 HOMO 的贡献 |
| `PC.lumo_contributor` | LUMO 贡献者 | 位点对 LUMO 的贡献 |
| `PC.orbital_energy_trend` | 轨道能级趋势 | 取代基对轨道能级的影响 |

#### PC.homo_contributor

```yaml
query:
  type: "PC.homo_contributor"
  params:
    smiles: "<SMILES>"
    atom_index: <int>
    
response:
  homo_contribution:
    is_major_contributor: <bool>
    orbital_type: "n | pi | sigma"
    relative_weight: "primary | secondary | minor | negligible"
    substituent_modulation: "<取代基如何影响该位点的 HOMO 贡献>"
```

#### PC.lumo_contributor

```yaml
query:
  type: "PC.lumo_contributor"
  params:
    smiles: "<SMILES>"
    atom_index: <int>
    bond: [<int>, <int>]  # 可选，查询特定键的 σ*/π*
    
response:
  lumo_contribution:
    is_major_contributor: <bool>
    orbital_type: "pi_star | sigma_star"
    relative_weight: "primary | secondary | minor | negligible"
    activation_by_ewg: "<邻近 EWG 是否降低能量>"
```

---

### 2.3 键活化查询类

| Query ID | 名称 | 描述 |
|----------|------|------|
| `PC.bond_activation` | 键活化程度 | 键被削弱/活化的程度 |
| `PC.bond_polarity` | 键极性 | 键的极化方向 |

#### PC.bond_activation

```yaml
query:
  type: "PC.bond_activation"
  params:
    smiles: "<SMILES>"
    bond_atoms: [<int>, <int>]  # 组成键的两个原子
    activation_type: "reduction | homolytic | heterolytic"
    
response:
  bond_activation:
    activation_level: "high | medium | low"
    sigma_star_energy: "lowered | normal | raised"
    activating_factors:
      - factor: "<因素>"
        effect: "<效应>"
    susceptible_to: ["reduction", "radical_attack", ...]
```

---

## 3. EleChem 提供的查询能力

| Query ID | 名称 | 描述 |
|----------|------|------|
| `EC.reduction_priority` | 还原优先级 | 位点的相对还原顺序 |
| `EC.oxidation_priority` | 氧化优先级 | 位点的相对氧化顺序 |
| `EC.sei_contribution` | SEI 贡献 | 官能团对 SEI 的贡献类型 |
| `EC.film_component` | 膜组分 | 预期生成的 SEI 组分 |

#### EC.reduction_priority

```yaml
query:
  type: "EC.reduction_priority"
  params:
    smiles: "<SMILES>"
    atom_index: <int>  # 或 fg_type
    
response:
  reduction_priority:
    rank: <int>  # 1 = 最先还原
    timing: "early | middle | late | resistant"
    mechanism: "1e | 2e | ring_opening | bond_cleavage"
```

---

## 4. 查询组合模式

### 4.1 常见组合

| 场景 | 查询序列 |
|------|---------|
| 判断 C-F 键活性 | `OC.adjacent_groups` → `PC.ewg_strength` → `PC.bond_activation` |
| 评估氧化风险 | `OC.functional_group_at` → `PC.homo_contributor` → `EC.oxidation_priority` |
| 预测开环路径 | `OC.ring_strain` → `OC.nucleophilicity` → `PC.lumo_contributor` |

### 4.2 SEI_04 完整查询流程示例

```yaml
# 分析 FEC 的 C-F 键活性

# Step 1: 找到 C-F 键邻近的官能团
query_1:
  type: "OC.adjacent_groups"
  params:
    smiles: "FC1COC(=O)O1"
    target_atom: 0  # F
    radius: 2
response_1:
  adjacent_groups:
    - { distance: 1, atom_index: 1, element: "C" }
    - { distance: 2, atom_index: 3, fg_type: "carbonyl", is_ewg: true }

# Step 2: 查询羰基的吸电子强度
query_2:
  type: "PC.ewg_strength"
  params:
    smiles: "FC1COC(=O)O1"
    substituent_atom: 3
    target_atom: 0
response_2:
  ewg_strength:
    I_effect: { sign: "-I", strength: "strong" }
    effect_on_target:
      direction: "electron_withdrawing"
      magnitude: "significant"

# Step 3: 查询 C-F 键的活化程度
query_3:
  type: "PC.bond_activation"
  params:
    smiles: "FC1COC(=O)O1"
    bond_atoms: [0, 1]  # F-C 键
    activation_type: "reduction"
response_3:
  bond_activation:
    activation_level: "high"
    sigma_star_energy: "lowered"
    activating_factors:
      - factor: "邻近羰基 -I 效应"
        effect: "降低 σ*(C-F) 能量"

# 综合结论
conclusion:
  likelihood: "high"
  evidence: "C-F 键被邻近羰基活化，σ* 能量降低，易于还原断裂"
```

---

## 5. 错误处理

| 错误类型 | 响应格式 |
|----------|---------|
| 无效 query_type | `{ error: "unknown_query_type", available: [...] }` |
| 缺少必需参数 | `{ error: "missing_param", param: "<param_name>" }` |
| SMILES 解析失败 | `{ error: "invalid_smiles" }` |
| 原子索引越界 | `{ error: "atom_index_out_of_range", max: <int> }` |
| 查询超时 | `{ error: "timeout", retry_suggested: true }` |

---

## 6. 性能考量

- **缓存策略**：同一 SMILES 的多次查询应缓存基础解析结果
- **批量查询**：支持单次请求多个查询以减少延迟
- **懒加载**：仅在需要时计算特定属性

---

## 7. Changelog

- 2025-12-25: 初始版本，定义核心查询能力


