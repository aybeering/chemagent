# LUMO_02_pi_antibond_v1 — π* 反键轨道的 LUMO 贡献评估

## Triggers
- 分子含有不饱和体系（羰基/腈/硝基/烯烃/芳环），需评估其 π* 对 LUMO 的贡献
- 需要判断"这个羰基/硝基容易被还原吗"
- 需要比较不同 π* 位点的还原倾向

## Inputs
- π* 体系类型与化学环境：
  - 羰基类：醛、酮、酯、酰胺、碳酸酯、脲
  - 氮氧类：硝基、亚硝基、N-氧化物
  - 腈类：腈、异腈
  - 烯烃类：隔离双键、共轭双键、α,β-不饱和羰基
  - 芳环类：苯、杂环芳烃
- 相邻取代基信息
- 是否有共轭延伸

## Outputs
- `pi_star_lumo_level`: π* LUMO 贡献等级（very_low / low / medium / high / very_high）
- `functional_group_ranking`: 同一分子内多个 π* 位点的 LUMO 排序
- `conjugation_effect`: 共轭对 LUMO 的影响（lowered / neutral / raised）
- `substituent_effect`: 取代基对 LUMO 的调制方向（↓ / → / ↑）
- `red_susceptibility`: 该位点的还原敏感性评估

## Rules

### π* LUMO 基础排序（无取代基调制时）
```
低 LUMO ──────────────────────────────────────────► 高 LUMO
（易还原）                                         （难还原）

硝基 < 醛 < α,β-不饱和醛 < 酮 < α,β-不饱和酮 
     < 酯 < 碳酸酯 < 酰胺 < 脲 < 腈 < 烯烃 < 芳环
```

### 官能团 LUMO 等级分类

| 类别 | 典型结构 | LUMO 水平 | 还原敏感性 |
|------|----------|-----------|------------|
| 硝基 | -NO₂ | very_low | 极高 |
| 醛 | -CHO | very_low | 很高 |
| 酮 | -CO- | low | 高 |
| 酯 | -COO- | low-medium | 中-高 |
| 碳酸酯 | -OCOO- | medium | 中等 |
| 酰胺 | -CONH- | medium | 中等 |
| 腈 | -CN | medium-high | 中-低 |
| 烯烃 | C=C | high | 低 |
| 芳环 | Ar | very_high | 很低 |

### 共轭效应对 π* 的影响
- **与吸电子基共轭 → LUMO 降低**：如 α,β-不饱和羰基
- **与给电子基共轭 → LUMO 略升高**：如烯醇醚
- **共轭延伸 → LUMO 分散，可能略升**：多烯体系

### 取代基调制（需调用 LUMO_05）
- **吸电子基 (-M/-I)** → π* LUMO ↓ → 更易还原
- **给电子基 (+M/+I)** → π* LUMO ↑ → 更难还原
- **典型强影响**：硝基旁的 CF₃ 使 LUMO 更低

## Steps
1. 识别分子中所有 π* 体系（羰基/腈/硝基/烯烃/芳环）。
2. 分类每个 π* 体系的基础类型。
3. 判断共轭状态：
   - 与吸电子基共轭 → 标记 `conjugation_effect: lowered`
   - 与给电子基共轭 → 标记 `conjugation_effect: raised`
4. 应用基础排序规则，给出初始 LUMO 等级。
5. 调用 `LUMO_05_substituent_mod_v1` 获取取代基调制。
6. 输出各 π* 位点的 LUMO 贡献与还原敏感性评估。

## Examples

### Example 1: 碳酸二甲酯 (DMC)
```
输入: SMILES = "COC(=O)OC"

分析:
- π* 体系: 碳酸酯羰基 C=O
- 共轭: 与两个 -OMe 共轭（+M 给电子）
- 取代基: 甲氧基（+M）

输出:
  pi_star_lumo_level: "medium"
  conjugation_effect: "raised"
  substituent_effect: "↑ (+M)"
  red_susceptibility: "中等；碳酸酯羰基因 +M 效应 LUMO 略高于普通酯"
```

### Example 2: 硝基甲烷
```
输入: SMILES = "C[N+](=O)[O-]"

分析:
- π* 体系: 硝基 N=O
- 特性: 硝基是极强 π 受体

输出:
  pi_star_lumo_level: "very_low"
  red_susceptibility: "极高敏感；硝基 LUMO 极低，是最易还原的官能团"
```

### Example 3: 乙腈
```
输入: SMILES = "CC#N"

分析:
- π* 体系: 腈基 C≡N
- 取代基: 甲基（弱 +I）

输出:
  pi_star_lumo_level: "medium-high"
  substituent_effect: "→ (弱)"
  red_susceptibility: "中-低敏感；腈基 LUMO 较高，需较强还原条件"
```

### Example 4: 丙烯醛（α,β-不饱和醛）
```
输入: SMILES = "C=CC=O"

分析:
- π* 体系: 醛 C=O、烯烃 C=C
- 共轭: 烯烃与羰基共轭

输出:
  pi_star_lumo_level: "very_low"
  conjugation_effect: "lowered"（共轭降低 LUMO）
  functional_group_ranking: [醛C=O（主导）, 烯烃C=C（次要）]
  red_susceptibility: "很高敏感；共轭使 LUMO 更低"
```

## Guardrails
- **区分官能团类型**：必须明确是醛/酮/酯/酰胺，不能笼统地说"羰基"。
- **共轭需明确方向**：共轭可能升高或降低 LUMO，需具体分析。
- **不混淆 π* 与 σ***：C-O 单键断裂属于 σ*，在 LUMO_03 处理。
- **不输出还原电位**：只给定性等级，不给数值。
- **多 π* 分子**：必须分别评估并指出主导贡献者。

