# LUMO_03_sigma_antibond_v1 — σ* 反键轨道的 LUMO 贡献评估

## Triggers
- 分子含有可断裂的 σ 键（C-卤素/C-O/C-S），需评估其 σ* 对 LUMO 的贡献
- 需要判断"这个 C-Br/C-O 键容易被还原断裂吗"
- 分析离去基还原脱离的可能性

## Inputs
- σ 键类型与化学环境：
  - C-卤素：C-F、C-Cl、C-Br、C-I
  - C-O 键：酯 C-O、醚 C-O、磺酸酯 C-O、碳酸酯 C-O
  - C-S 键：磺酸酯 C-S、硫醚 C-S
  - C-N 键：季铵 C-N、酰胺 C-N
- 碳的杂化与环境（sp³/sp²/sp）
- 离去基稳定性

## Outputs
- `sigma_star_lumo_level`: σ* LUMO 贡献等级（low / medium / high / very_high）
- `bond_cleavage_tendency`: 键断裂倾向（high / medium / low）
- `leaving_group_quality`: 离去基质量评估
- `substituent_effect`: 取代基对 σ* LUMO 的调制
- `red_susceptibility`: 该位点的还原断裂敏感性评估

## Rules

### σ* LUMO 基础排序
```
低 LUMO ──────────────────────────────────────────► 高 LUMO
（易断裂）                                         （难断裂）

C-I < C-Br < C-Cl < C-OTs/OMs < C-OAc < C-OR(酯) < C-F < C-OR(醚) < C-C
```

### σ* 键类型分类

| 键类型 | 典型结构 | σ* LUMO | 断裂倾向 | 离去基 |
|--------|----------|---------|----------|--------|
| C-I | 碘代烃 | very_low | 很高 | I⁻ (优秀) |
| C-Br | 溴代烃 | low | 高 | Br⁻ (优秀) |
| C-Cl | 氯代烃 | low-medium | 中-高 | Cl⁻ (良好) |
| C-OTs | 甲苯磺酸酯 | low-medium | 中-高 | TsO⁻ (优秀) |
| C-OMs | 甲磺酸酯 | low-medium | 中-高 | MsO⁻ (优秀) |
| C-OAc | 乙酸酯 | medium | 中等 | AcO⁻ (中等) |
| C-F | 氟代烃 | medium-high | 中-低 | F⁻ (差) |
| C-OR | 醚 | high | 低 | RO⁻ (差) |

### 碳杂化的影响
- **sp³ 碳**：σ* 最易接近，还原断裂最易
- **sp² 碳**（如乙烯基卤）：σ* 与 π* 混合，机制复杂
- **sp 碳**（如炔基卤）：较少见，需特殊处理

### 取代基调制
- **邻近吸电子基 (-I/-M)** → σ* LUMO ↓ → 更易断裂
- **邻近给电子基 (+I/+M)** → σ* LUMO ↑ → 更难断裂
- **苄位/烯丙位**：可能通过自由基中间体稳定化增强断裂

### 离去基稳定性因素
- **离去后阴离子稳定性**：I⁻ > Br⁻ > Cl⁻ > F⁻
- **共轭稳定化**：TsO⁻、MsO⁻ 因共振稳定而成为好离去基
- **电负性**：高电负性原子形成的阴离子更稳定

## Steps
1. 识别分子中所有可还原断裂的 σ 键。
2. 分类键类型（C-卤素/C-O/C-S 等）。
3. 评估碳的杂化状态。
4. 应用基础排序规则，给出初始 σ* LUMO 等级。
5. 评估离去基质量。
6. 调用 `LUMO_05_substituent_mod_v1` 获取取代基调制（如适用）。
7. 输出各 σ 键位点的断裂倾向与还原敏感性评估。

## Examples

### Example 1: 溴乙烷
```
输入: SMILES = "CCBr"

分析:
- σ 键: C-Br（sp³ 碳）
- 离去基: Br⁻（优秀）

输出:
  sigma_star_lumo_level: "low"
  bond_cleavage_tendency: "high"
  leaving_group_quality: "excellent"
  red_susceptibility: "高敏感；C-Br 键易被还原断裂释放 Br⁻"
```

### Example 2: 氟代碳酸乙烯酯 (FEC)
```
输入: SMILES = "C1C(F)OC(=O)O1"

分析:
- σ 键: C-F（sp³ 碳，五元环）
- 离去基: F⁻（本身差，但 LiF 热力学稳定）
- 竞争: 与羰基 π* 竞争

输出:
  sigma_star_lumo_level: "medium"
  bond_cleavage_tendency: "medium"
  leaving_group_quality: "moderate (but LiF precipitation drives reaction)"
  red_susceptibility: "中等敏感；C-F 断裂释放 F⁻ 有利于 LiF 成膜"
```

### Example 3: 对甲苯磺酸甲酯 (MeOTs)
```
输入: SMILES = "Cc1ccc(cc1)S(=O)(=O)OC"

分析:
- σ 键: C-OTs（sp³ 碳）
- 离去基: TsO⁻（优秀，共振稳定）

输出:
  sigma_star_lumo_level: "low-medium"
  bond_cleavage_tendency: "high"
  leaving_group_quality: "excellent"
  red_susceptibility: "高敏感；磺酸酯是优秀离去基，易还原断裂"
```

### Example 4: 二乙醚
```
输入: SMILES = "CCOCC"

分析:
- σ 键: C-O（醚键，sp³ 碳）
- 离去基: EtO⁻（差）

输出:
  sigma_star_lumo_level: "high"
  bond_cleavage_tendency: "low"
  leaving_group_quality: "poor"
  red_susceptibility: "低敏感；醚键 σ* LUMO 高，通常不易还原断裂"
```

## Guardrails
- **区分酯 C-O 与醚 C-O**：酯中 C-O 比醚更易断裂。
- **考虑竞争位点**：若分子同时有 π* 和 σ*，需与 LUMO_02 结果比较。
- **离去基质量必须评估**：σ* LUMO 低但离去基差时，实际断裂可能受阻。
- **不混淆与 LUMO_04**：环氧的 C-O 断裂在 LUMO_04 处理（应变主导）。
- **不输出还原电位**：只给定性评估。

