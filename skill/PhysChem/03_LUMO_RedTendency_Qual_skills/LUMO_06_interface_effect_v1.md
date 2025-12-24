# LUMO_06_interface_effect_v1 — 界面/电场环境对还原行为的修正

## Triggers
- 分析对象为电解液分子，需考虑负极界面环境
- 需要判断"在负极界面，还原行为是否改变"
- 需要评估双电层电场对还原位点优先级的影响

## Inputs
- 界面类型：
  - `anode_interface`: 负极界面（低电位，还原环境）
  - `cathode_interface`: 正极界面（高电位，氧化环境）
  - `bulk_phase`: 体相（无界面效应）
- 电极材料（可选）：Li metal / Graphite / Si / Li₄Ti₅O₁₂
- 电位范围（可选）：深度还原（<0.3V vs Li）/ 中度（0.3-1.0V）/ 浅（>1.0V）
- 分子吸附信息（可选）：可能的吸附构象与暴露官能团

## Outputs
- `interface_modifier`: 界面对还原排序的修正因子
  - `boost`: 某些位点还原倾向增强
  - `suppress`: 某些位点还原倾向降低
  - `reorder`: 位点优先级重排
- `field_effect`: 电场对分子电子结构的影响方向
- `adsorption_exposure`: 因吸附导致特定官能团暴露的效应
- `red_pathway_hint`: 界面可能的还原路径提示（单电子 / 双电子 / 协同）
- `film_formation_relevance`: 与 SEI 成膜的相关性
- `notes`: 环境依赖性说明与警示

## Rules

### 界面类型对还原评估的影响

| 界面类型 | 对还原评估的影响 |
|----------|-----------------|
| 负极界面（深度还原） | 强还原驱动；可活化通常惰性的位点 |
| 负极界面（中度） | 中等还原驱动；按体相 LUMO 排序基本有效 |
| 正极界面 | 还原驱动弱；本模块适用性降低（应使用 HOMO 模块） |
| 体相 | 无界面效应；纯粹基于 LUMO 评估 |

### 电极材料特异性

| 电极材料 | 工作电位 | 还原强度 | 特殊考虑 |
|----------|----------|----------|----------|
| Li metal | ~0V vs Li | 极强 | 可还原几乎所有有机物；Li⁺/e⁻ 协同 |
| 石墨 | 0.05-0.2V | 强 | 层间插入；首周 SEI 形成关键 |
| 硅基 | 0.1-0.4V | 强 | 体积膨胀；SEI 持续形成 |
| LTO | 1.5V | 弱 | "零应变"；还原较温和 |

### 电场效应

| 电场方向 | 效应 |
|----------|------|
| 场指向分子 | 可能稳定阴离子中间体 → 还原增强 |
| 场背离分子 | 可能不利于阴离子 → 还原可能受抑制 |

### 吸附取向效应

| 吸附模式 | 还原影响 |
|----------|---------|
| 极性官能团朝向电极 | 该官能团优先接受电子 |
| 平躺吸附 | 多位点同时暴露 |
| 疏水端朝向电极 | 可能不利于电子转移 |

### SEI 相关性

| 还原产物倾向 | SEI 相关性 |
|--------------|------------|
| 释放 F⁻ / PF₆⁻ 分解 | 有利于 LiF 成膜 |
| 产生有机锂盐 | 有利于有机 SEI |
| 气体产生（CO₂, 烯烃） | 可能造成界面不稳定 |
| 聚合物生成 | 有利于 oligomer/polymer SEI |

## Steps
1. 识别界面类型与电极环境。
2. 评估电位范围：
   - 深度还原 → 可活化更多位点
   - 温和还原 → 按体相 LUMO 排序
3. 评估吸附效应（如有信息）：
   - 识别可能的吸附构象
   - 判断哪些官能团暴露于电极
4. 应用材料特异性规则。
5. 输出修正因子：
   - 哪些位点被增强（boost）
   - 哪些位点被抑制（suppress）
   - 是否需要重排优先级（reorder）
6. 提供 SEI 成膜相关提示。

## Examples

### Example 1: EC 在石墨负极界面
```
输入:
  分子: 碳酸乙烯酯 (EC)
  界面: anode_interface
  电极: Graphite (0.1V vs Li)

分析:
- 体相 LUMO 排序: 羰基 π* > 酯基 C-O σ*
- 界面效应:
  - 羰基可能朝向电极吸附
  - 首周充电时优先还原

输出:
  interface_modifier:
    boost:
      - site: "羰基C=O"
        reason: "低电位优先还原；开环形成 SEI"
  red_pathway_hint: "单电子还原 → 自由基 → 开环"
  film_formation_relevance: "高度相关；EC 还原产物是 SEI 主要成分"
```

### Example 2: FEC 在锂金属负极
```
输入:
  分子: 氟代碳酸乙烯酯 (FEC)
  界面: anode_interface
  电极: Li metal (0V vs Li)

分析:
- 体相 LUMO 排序: 羰基 π* > C-F σ*
- 界面效应:
  - 极强还原驱动
  - C-F 还原释放 F⁻

输出:
  interface_modifier:
    boost:
      - site: "羰基C=O"
        reason: "最低 LUMO，优先还原"
      - site: "C-F"
        reason: "强还原条件下也可断裂"
  reorder:
    original: [羰基, C-F]
    modified: [羰基 ≈ C-F]（极端条件下趋于竞争）
  film_formation_relevance: "极高相关；F⁻ 释放促进 LiF 富集"
```

### Example 3: DME 在 LTO 负极
```
输入:
  分子: 乙二醇二甲醚 (DME)
  界面: anode_interface
  电极: LTO (1.5V vs Li)

分析:
- 体相 LUMO 排序: 无典型低 LUMO（醚键 σ* 高）
- 界面效应:
  - LTO 电位高，还原驱动弱
  - DME 在 LTO 表面较稳定

输出:
  interface_modifier:
    boost: []
    suppress: []
  notes: "LTO 电位较高，DME 基本稳定；无显著界面还原"
  film_formation_relevance: "低相关；DME 在 LTO 表面不易分解"
```

### Example 4: 腈类溶剂在石墨负极
```
输入:
  分子: 乙腈 (ACN)
  界面: anode_interface
  电极: Graphite (0.1V vs Li)

分析:
- 体相 LUMO 排序: 腈基 π*（中-高 LUMO）
- 界面效应:
  - 腈基可配位 Li⁺
  - 低电位可能还原

输出:
  interface_modifier:
    boost:
      - site: "腈基C≡N"
        reason: "低电位可活化腈基还原"
  red_pathway_hint: "可能经历 C≡N 加氢或 C-C 键断裂"
  film_formation_relevance: "中等相关；腈还原产物可能聚合或产气"
  notes: "腈类溶剂在低电位石墨上不如碳酸酯稳定"
```

## Guardrails
- **不在正极界面使用**：正极以氧化为主，本 skill 适用性降低。
- **无界面信息时跳过**：若输入为 `bulk_phase`，直接返回空修正因子。
- **不输出具体电位数值**：只给定性的"深度/中度/浅"还原评估。
- **SEI 成膜为提示性**：具体成膜机理复杂，本 skill 只给方向性提示。
- **电极材料为可选**：无材料信息时使用通用负极假设。

