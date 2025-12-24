# INTF_05_film_formation_hint_v1 — SEI/CEI 成膜倾向与路径提示

## Triggers
- 需要评估分子分解产物与**界面膜形成**的关系
- 需要判断"这个分子的分解是否有利于成膜"
- 分析 SEI（负极）或 CEI（正极）的可能组成来源

## Inputs
- 分子表示：SMILES / 结构描述
- 优先反应位点：从 INTF_02/03 获取的排序
- 界面类型：
  - `anode`: 负极（SEI）
  - `cathode`: 正极（CEI）
- 电极材料（可选）

## Outputs
- `film_formation_tendency`: 成膜倾向（high / medium / low）
- `film_type_hint`: 可能的膜类型
  - `inorganic_dominant`: 无机为主（LiF, Li₂O, Li₂CO₃）
  - `organic_dominant`: 有机为主（聚合物、烷氧锂）
  - `mixed`: 混合型
- `key_products_hint`: 关键产物提示（不做精确预测）
- `passivation_quality`: 钝化质量预估（good / moderate / poor）
- `notes`: 补充说明

## Rules

### 成膜相关的结构特征

| 结构特征 | SEI 贡献 | CEI 贡献 |
|----------|----------|----------|
| 含 F 基团 | LiF 来源（有利） | 可能有贡献 |
| 碳酸酯基 | Li₂CO₃、烷氧锂 | 可能氧化分解 |
| 硫酸酯/磺酰基 | Li₂S、LiₓSOy | 可能有贡献 |
| 硝基/亚硝基 | LiₓNOy | 少见 |
| 烯烃/双键 | 可能聚合 | 可能交联 |
| 腈基 | 可能聚合 | 稳定性较高 |

### SEI 质量评估因素

| 因素 | 有利于好 SEI | 不利于好 SEI |
|------|--------------|--------------|
| LiF 含量 | 高 LiF → 好 | 低 LiF → 差 |
| 有机/无机比 | 适度混合 → 好 | 过于单一 → 一般 |
| 产气倾向 | 低产气 → 好 | 高产气 → 差 |
| 电子绝缘性 | 绝缘 → 好 | 导电 → 差 |
| Li⁺ 传导 | 高传导 → 好 | 低传导 → 差 |

### 产物类型与膜质量关系

| 产物类型 | 膜质量评估 |
|----------|------------|
| LiF | 优秀（致密、稳定） |
| Li₂CO₃ | 良好（稳定，Li⁺ 传导中等） |
| 烷氧锂（ROLi） | 中等（有机相，柔性） |
| 聚碳酸酯 | 中等（有机相） |
| Li₂O | 良好（稳定） |
| 气体（CO₂, C₂H₄） | 不利（界面不稳定） |

## Steps
1. 接收分子结构与优先反应位点。
2. 识别与成膜相关的结构特征：
   - 含 F → LiF 潜力
   - 碳酸酯 → Li₂CO₃/烷氧锂 潜力
   - 双键 → 聚合潜力
3. 评估成膜倾向：
   - 多个成膜有利特征 → high
   - 部分有利 → medium
   - 无明显贡献 → low
4. 预估膜类型（无机/有机/混合）。
5. 评估钝化质量。
6. 输出提示性结论。

## Examples

### Example 1: FEC (氟代碳酸乙烯酯)
```
输入:
  分子: FEC
  界面: anode (负极)
  优先位点: [羰基C=O, C-F]

分析:
  - 含 F 基团 → LiF 来源
  - 碳酸酯 → Li₂CO₃ 可能
  - C-F 断裂释放 F⁻

输出:
  film_formation_tendency: "high"
  film_type_hint: "mixed (LiF 富集 + 有机)"
  key_products_hint: "LiF（主导）、烷氧锂、可能的聚合物"
  passivation_quality: "good"
  notes: "FEC 是优秀的 SEI 形成剂；LiF 富集型 SEI 稳定性好"
```

### Example 2: EC (碳酸乙烯酯)
```
输入:
  分子: EC
  界面: anode (负极)
  优先位点: [羰基C=O]

分析:
  - 碳酸酯 → Li₂CO₃、烷氧锂
  - 无 F → 无 LiF
  - 可能产气（CO₂）

输出:
  film_formation_tendency: "medium-high"
  film_type_hint: "organic_dominant (+ Li₂CO₃)"
  key_products_hint: "Li₂CO₃、(CH₂OCO₂Li)₂、可能 CO₂ 产气"
  passivation_quality: "moderate"
  notes: "EC 是 SEI 主要组分来源；但首周产气可能造成初期不稳定"
```

### Example 3: LiTFSI 盐
```
输入:
  分子: LiTFSI
  界面: anode (负极)
  优先位点: [S-N, C-F]

分析:
  - 含 F → LiF 来源
  - 含 S → LiₓSOy 可能
  - 阴离子分解

输出:
  film_formation_tendency: "high"
  film_type_hint: "inorganic_dominant (LiF, Li₂S, LiₓSOy)"
  key_products_hint: "LiF、Li₂S、SOₓ 类无机物"
  passivation_quality: "good (if controlled)"
  notes: "TFSI⁻ 分解贡献无机 SEI；需控制程度避免过度消耗"
```

### Example 4: DME (乙二醇二甲醚)
```
输入:
  分子: DME
  界面: anode (石墨负极, 0.1V)

分析:
  - 醚键 σ* 较高
  - 无 F、无碳酸酯基
  - 稳定性相对较好

输出:
  film_formation_tendency: "low"
  film_type_hint: "minimal (可能烷氧锂)"
  key_products_hint: "少量烷氧锂（如有分解）"
  passivation_quality: "N/A (minimal decomposition)"
  notes: "DME 在石墨上相对稳定；主要作为溶剂而非成膜剂"
```

## Guardrails
- **只给提示不做预测**：具体产物复杂，只给方向性提示。
- **区分 SEI 和 CEI**：正负极成膜机理不同。
- **质量评估为定性**：不给具体数值。
- **考虑协同效应**：多组分电解液可能有协同。
- **产气是负面因素**：明确指出产气倾向。

